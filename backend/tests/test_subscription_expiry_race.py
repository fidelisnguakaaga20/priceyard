"""Protect single-account reads from overwriting concurrently purchased access.

The unittest cases use only an in-memory SQLite database. The explicit helper
accepts an engine from the guarded native PostgreSQL runner; it never discovers
credentials or opens an independently configured database.
"""
from datetime import datetime, timedelta, timezone
import threading
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.subscription import Subscription
from app.models.user import User
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.routes.subscription_routes import get_user_subscription
from app.services import subscription_service as service
from app.services import payment_service

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def seed_account(engine, *, status, role, now):
    tag = uuid4().hex[:10]
    with Session(engine) as db:
        user = User(full_name="Synthetic expiry race", email=f"expiry-{tag}@example.com",
                    password_hash="unused-by-this-test", role=role, referral_code="ER" + tag)
        user.subscription = Subscription(
            status=status, plan_name="trial" if status == "trial" else "paid_monthly",
            trial_started_at=now-timedelta(days=15),
            trial_ends_at=now-timedelta(minutes=1) if status == "trial" else None,
            start_date=(now-timedelta(days=31)).date() if status == "active" else None,
            end_date=(now-timedelta(days=1)).date() if status == "active" else None,
            payment_reference=f"synthetic-original-{tag}",
        )
        db.add(user)
        db.commit()
        return user.id


def renew_account(engine, user_id, *, now):
    with Session(engine) as db:
        _, subscription = service.lock_subscription_state(db, user_id)
        service.activate_paid_subscription(db, subscription, plan="monthly", now=now, commit=False)
        subscription.payment_reference = f"synthetic-renewal-{user_id}"
        db.commit()


def assert_renewal_preserved(check, engine, user_id, *, role, now):
    with Session(engine) as db:
        item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
        check.assertEqual(item.status, "active")
        check.assertEqual(item.plan_name, "paid_monthly")
        check.assertEqual(item.start_date, now.date())
        check.assertEqual(item.end_date, (now+timedelta(days=30)).date())
        check.assertEqual(item.payment_reference, f"synthetic-renewal-{user_id}")
        check.assertEqual(item.user.role, role if role in {"admin", "reporter"} else "paid_user")


def seed_pending_renewal(engine, user_id):
    with Session(engine) as db:
        db.add(Payment(user_id=user_id, reference=f"synthetic-renewal-{user_id}",
                       plan="monthly", amount=2500, currency="NGN", status="pending"))
        db.commit()


def confirm_renewal(db, user_id):
    payment_service.handle_webhook_event(db, {"event": "charge.success", "data": {
        "reference": f"synthetic-renewal-{user_id}", "id": 990000+user_id,
        "amount": 250000, "currency": "NGN", "status": "success"}})


def assert_payment_once(check, engine, user_id):
    with Session(engine) as db:
        payment = db.scalar(select(Payment).where(Payment.user_id == user_id))
        check.assertEqual((payment.status, payment.paystack_transaction_id), ("success", str(990000+user_id)))
        check.assertEqual(len(db.scalars(select(AuditLog).where(
            AuditLog.user_id == user_id, AuditLog.action == "payment.success")).all()), 1)


def verify_subscription_get_renewal_races(check, engine):
    """Native-only, two-session GET/renewal races; invoke through guarded runner.

    Pause the GET after its expired read but before the lock/reload. A separate
    transaction commits a renewal, then the GET must retain the newly paid value.
    Six tiny cases cover expired trial/paid access and ordinary/staff authority.
    """
    check.assertEqual(engine.dialect.name, "postgresql")
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    original_lock = service.lock_subscription_state
    for status in ("trial", "active"):
        for kind in ("ordinary", "reporter", "admin"):
            role = ("free_user" if status == "trial" else "paid_user") if kind == "ordinary" else kind
            user_id = seed_account(engine, status=status, role=role, now=now)
            seed_pending_renewal(engine, user_id)
            selected, release = threading.Event(), threading.Event()
            outcomes = []

            def delayed_lock(db, candidate):
                if threading.current_thread().name == "single-subscription-expiry":
                    check.assertEqual(candidate, user_id)
                    selected.set()
                    if not release.wait(5):
                        raise RuntimeError("Synthetic single-account expiry coordination timed out")
                return original_lock(db, candidate)

            def read_subscription():
                with Session(engine, expire_on_commit=False) as db:
                    try:
                        current_user = db.get(User, user_id)
                        item = get_user_subscription(user_id, db=db, current_user=current_user)
                        outcomes.append((item.status, item.end_date, item.user.role))
                    except BaseException as error:
                        db.rollback()
                        outcomes.append(error)

            with patch.object(service, "lock_subscription_state", side_effect=delayed_lock), \
                    patch.object(service, "utc_now", return_value=now), \
                    patch.object(payment_service, "notify_admins"):
                worker = threading.Thread(target=read_subscription, name="single-subscription-expiry", daemon=True)
                worker.start()
                try:
                    check.assertTrue(selected.wait(5), "GET must recheck expired access under the renewal locks")
                    with Session(engine) as payer:
                        confirm_renewal(payer, user_id)
                finally:
                    release.set()
                    worker.join(8)
            check.assertFalse(worker.is_alive(), "Synthetic expiry reader must finish promptly")
            expected_role = role if role in {"admin", "reporter"} else "paid_user"
            check.assertEqual(outcomes, [("active", (now+timedelta(days=30)).date(), expected_role)])
            assert_renewal_preserved(check, engine, user_id, role=role, now=now)
            assert_payment_once(check, engine, user_id)


def verify_expiry_first_blocks_payment_then_preserves_renewal(check, engine):
    """Prove a real payment waits for expiry's User lock, then credits once."""
    check.assertEqual(engine.dialect.name, "postgresql")
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    original_lock = service.lock_subscription_state
    for status in ("trial", "active"):
        for kind in ("ordinary", "reporter", "admin"):
            role = ("free_user" if status == "trial" else "paid_user") if kind == "ordinary" else kind
            user_id = seed_account(engine, status=status, role=role, now=now)
            seed_pending_renewal(engine, user_id)
            selected, release, payment_attempted = threading.Event(), threading.Event(), threading.Event()
            outcomes, writer_pid = [], []

            def hold_expiry_lock(db, candidate):
                result = original_lock(db, candidate)
                selected.set()
                if not release.wait(5): raise RuntimeError("Synthetic locked-expiry coordination timed out")
                return result

            def observe_user_lock(connection, cursor, statement, parameters, context, many):
                if (threading.current_thread().name == "renewal-writer" and statement.lstrip().startswith("SELECT users.")
                        and "FOR UPDATE" in statement):
                    payment_attempted.set()

            def expire():
                with Session(engine) as db:
                    try:
                        get_user_subscription(user_id, db=db, current_user=db.get(User, user_id))
                        outcomes.append("expired-read-finished")
                    except BaseException as error: outcomes.append(error)

            def pay():
                with Session(engine) as db:
                    try:
                        writer_pid.append(db.scalar(text("SELECT pg_backend_pid()")))
                        confirm_renewal(db, user_id)
                        outcomes.append("payment-finished")
                    except BaseException as error: outcomes.append(error)

            event.listen(engine, "before_cursor_execute", observe_user_lock)
            reader = threading.Thread(target=expire, name="expiry-reader", daemon=True)
            writer = threading.Thread(target=pay, name="renewal-writer", daemon=True)
            with patch.object(service, "lock_subscription_state", side_effect=hold_expiry_lock), \
                    patch.object(service, "utc_now", return_value=now), patch.object(payment_service, "notify_admins"):
                try:
                    reader.start(); check.assertTrue(selected.wait(5))
                    writer.start(); check.assertTrue(payment_attempted.wait(5))
                    blocked = False
                    with engine.connect() as observer:
                        for _ in range(50):
                            if observer.scalar(text("SELECT cardinality(pg_blocking_pids(:pid))"), {"pid": writer_pid[0]}):
                                blocked = True; break
                            time.sleep(0.02)
                    check.assertTrue(blocked, "Native payment must wait on the expiry transaction lock")
                finally:
                    release.set(); reader.join(8)
                    if writer.ident is not None: writer.join(8)
                    event.remove(engine, "before_cursor_execute", observe_user_lock)
            check.assertFalse(reader.is_alive()); check.assertFalse(writer.is_alive())
            check.assertCountEqual(outcomes, ["expired-read-finished", "payment-finished"])
            assert_renewal_preserved(check, engine, user_id, role=role, now=now)
            assert_payment_once(check, engine, user_id)


class SubscriptionExpiryRaceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_stale_trial_or_paid_get_cannot_erase_a_committed_renewal_or_staff_role(self):
        for status in ("trial", "active"):
            for kind in ("ordinary", "reporter", "admin"):
                role = ("free_user" if status == "trial" else "paid_user") if kind == "ordinary" else kind
                with self.subTest(status=status, role=role):
                    user_id = seed_account(self.engine, status=status, role=role, now=NOW)
                    with Session(self.engine, expire_on_commit=False) as stale:
                        user = stale.get(User, user_id)
                        item = stale.scalar(select(Subscription).where(Subscription.user_id == user_id))
                        self.assertEqual(item.status, status)
                        item.user  # Keep the original relationship loaded too.
                        renew_account(self.engine, user_id, now=NOW)
                        with patch.object(service, "utc_now", return_value=NOW):
                            result = get_user_subscription(user_id, db=stale, current_user=user)
                        self.assertEqual(result.status, "active")
                        self.assertEqual(result.user.role, role if kind != "ordinary" else "paid_user")
                    assert_renewal_preserved(self, self.engine, user_id, role=role, now=NOW)

    def test_real_expiry_changes_only_access_state_and_keeps_staff_and_history(self):
        for status in ("trial", "active"):
            for role in ("paid_user", "reporter", "admin"):
                with self.subTest(status=status, role=role):
                    user_id = seed_account(self.engine, status=status, role=role, now=NOW)
                    with Session(self.engine) as db:
                        item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
                        before = {name: getattr(item, name) for name in (
                            "plan_name", "trial_started_at", "trial_ends_at", "start_date", "end_date", "payment_reference")}
                        result = service.expire_trial_if_needed(db, item, now=NOW)
                        self.assertEqual(result.status, "expired")
                        self.assertEqual(result.user.role, role if role in {"admin", "reporter"} else "free_user")
                        self.assertEqual({name: getattr(result, name) for name in before}, before)

    def test_valid_trial_paid_and_indefinite_reads_take_no_expiry_locks_or_commit(self):
        for status in ("trial", "active", "free", "expired", "cancelled"):
            with self.subTest(status=status):
                user_id = seed_account(self.engine, status=status, role="reporter", now=NOW)
                with Session(self.engine) as db:
                    item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
                    if status == "trial":
                        item.trial_ends_at = NOW+timedelta(days=1)
                    elif status == "active":
                        item.end_date = NOW.date()
                    db.commit()
                    with patch.object(service, "lock_subscription_state") as lock, patch.object(db, "commit") as commit:
                        self.assertIs(service.expire_trial_if_needed(db, item, now=NOW), item)
                        lock.assert_not_called()
                        commit.assert_not_called()
                    if status == "active":
                        item.end_date = None
                        db.commit()
                        with patch.object(service, "lock_subscription_state") as lock:
                            self.assertIs(service.expire_trial_if_needed(db, item, now=NOW), item)
                            lock.assert_not_called()

    def test_candidate_renewed_before_lock_still_releases_the_transaction(self):
        user_id = seed_account(self.engine, status="active", role="paid_user", now=NOW)
        with Session(self.engine, expire_on_commit=False) as db:
            item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            renew_account(self.engine, user_id, now=NOW)
            with patch.object(db, "commit", wraps=db.commit) as commit:
                result = service.expire_trial_if_needed(db, item, now=NOW)
                self.assertEqual(result.status, "active")
                commit.assert_called_once()
            assert_renewal_preserved(self, self.engine, user_id, role="paid_user", now=NOW)

    def test_failed_expiry_commit_rolls_back_all_access_changes(self):
        user_id = seed_account(self.engine, status="active", role="paid_user", now=NOW)
        with Session(self.engine) as db:
            item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            with patch.object(db, "commit", side_effect=RuntimeError("synthetic commit failure")), \
                    patch.object(db, "rollback", wraps=db.rollback) as rollback:
                with self.assertRaisesRegex(RuntimeError, "synthetic commit failure"):
                    service.expire_trial_if_needed(db, item, now=NOW)
                rollback.assert_called_once()
        with Session(self.engine) as db:
            item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            self.assertEqual((item.status, item.user.role), ("active", "paid_user"))

    def test_candidate_missing_after_reload_fails_without_mutating_stale_state(self):
        user_id = seed_account(self.engine, status="trial", role="free_user", now=NOW)
        with Session(self.engine) as db:
            item = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            with patch.object(service, "lock_subscription_state", return_value=(item.user, None)), \
                    patch.object(db, "rollback", wraps=db.rollback) as rollback:
                with self.assertRaises(HTTPException) as caught:
                    service.expire_trial_if_needed(db, item, now=NOW)
                self.assertEqual(caught.exception.status_code, 404)
                rollback.assert_called_once()
            self.assertEqual(item.status, "trial")
