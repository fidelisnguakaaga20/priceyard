from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.audit_log import AuditLog
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.user import User
from app.services import payment_service
from app.services import payment_reconciliation_service as recovery
from app.services.subscription_service import build_trial_subscription

KINDS = ("paid", "trial", "manual", "unconfirmed", "bad", "legacy", "missing")


def seed_reconciliation(engine, kinds=KINDS):
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    prefix = uuid.uuid4().hex[:6]
    fixtures = {}
    with Session(engine) as db:
        for index, kind in enumerate(kinds):
            user = User(full_name="Synthetic recovery customer", email=f"rec-{prefix}-{kind}@example.com", password_hash="unused", role="paid_user" if kind in ("paid", "manual") else "free_user", referral_code=prefix+str(index))
            if kind == "trial":
                user.subscription = build_trial_subscription(user=user, now=now-timedelta(days=5))
            elif kind != "missing":
                user.subscription = Subscription(status="active" if kind in ("paid", "manual") else "free", plan_name="paid_monthly" if kind in ("paid", "manual") else "free", end_date=now.date()+timedelta(days=12) if kind == "paid" else None)
            db.add(user); db.flush()
            payment = Payment(user_id=user.id, reference=f"py_rec_{prefix}_{kind}", plan="seasonal" if kind == "trial" else "monthly", amount=6000 if kind == "trial" else 2500, currency="NGN", status="success" if kind == "legacy" else "failed" if kind == "trial" else "pending")
            db.add(payment); db.flush()
            fixtures[kind] = {"user_id": user.id, "payment_id": payment.id,
                              "paid_end": user.subscription.end_date if user.subscription else None,
                              "trial_end": user.subscription.trial_ends_at if user.subscription else None,
                              "evidence": {"reference": payment.reference, "id": 800000+index, "amount": int(payment.amount*100), "currency": "NGN", "status": "pending" if kind == "unconfirmed" else "success"}}
        db.commit()
    fixtures.get("bad", {}).get("evidence", {}).update(amount=249999)
    return fixtures


def fake_provider(fixtures, observed):
    by_reference = {row["evidence"]["reference"]: row["evidence"] for row in fixtures.values()}

    def send(session, method, url, **kwargs):
        reference = url.removeprefix("https://api.paystack.co/transaction/verify/")
        assert method.upper() == "GET" and reference in by_reference
        assert session.trust_env is False and kwargs["allow_redirects"] is False
        assert kwargs["verify"] is True and kwargs["timeout"] == (3, 15)
        observed.append(reference)
        response = requests.Response(); response.status_code = 200
        response._content = json.dumps({"status": True, "data": by_reference[reference]}).encode()
        return response

    return send


def provider_patches(fixtures, observed, provider=None):
    stack = ExitStack()
    stack.enter_context(patch.object(payment_service, "get_settings", return_value=SimpleNamespace(paystack_secret_key="sk_test_recovery_synthetic_only", frontend_url="http://127.0.0.1:55446")))
    stack.enter_context(patch.object(payment_service, "notify_admins"))
    stack.enter_context(patch("requests.Session.request", autospec=True, side_effect=provider or fake_provider(fixtures, observed)))
    return stack


def rows(engine):
    with Session(engine) as db:
        return {model.__tablename__: db.execute(select(model.__table__).order_by(model.id)).all() for model in (User, Subscription, Payment, AuditLog)}


def verify_reconciliation_workflow(check, engine):
    fixture = seed_reconciliation(engine)
    before = rows(engine)
    with patch("requests.Session.request") as transport:
        dry = recovery.reconcile_payments(engine, limit=3)
        transport.assert_not_called()
    check.assertEqual(rows(engine), before)
    check.assertTrue(dry["dry_run"])
    check.assertFalse(dry["complete"])
    check.assertEqual(len(dry["outcomes"]), 3)
    observed = []
    with provider_patches(fixture, observed):
        report = recovery.reconcile_payments(engine, apply=True)
        first_calls = list(observed)
        repeated = recovery.reconcile_payments(engine, apply=True)
    outcomes = {row["payment_id"]: row["outcome"] for row in report["outcomes"]}
    check.assertEqual(outcomes, {fixture[kind]["payment_id"]: expected for kind, expected in (("paid", "confirmed"), ("trial", "confirmed"), ("manual", "review_required"), ("unconfirmed", "unconfirmed"), ("bad", "error"), ("missing", "error"))})
    check.assertTrue(report["complete"])
    check.assertNotIn(fixture["legacy"]["evidence"]["reference"], observed)
    for kind in ("paid", "trial"):
        check.assertEqual(observed.count(fixture[kind]["evidence"]["reference"]), 1)
    check.assertEqual(len(first_calls), 6)  # Missing subscription still verifies evidence before safely rejecting.
    check.assertEqual(len(repeated["outcomes"]), 4)
    with Session(engine) as db:
        for kind, expected_end in (("paid", fixture["paid"]["paid_end"]+timedelta(days=30)), ("trial", fixture["trial"]["trial_end"].date()+timedelta(days=90))):
            check.assertEqual(db.get(User, fixture[kind]["user_id"]).subscription.end_date, expected_end)
            check.assertEqual(db.get(Payment, fixture[kind]["payment_id"]).status, "success")
        manual = db.get(User, fixture["manual"]["user_id"]).subscription
        check.assertEqual(manual.status, "active"); check.assertIsNone(manual.end_date)
        for kind in ("unconfirmed", "bad", "legacy"):
            check.assertEqual(db.get(User, fixture[kind]["user_id"]).subscription.status, "free")
        check.assertIsNone(db.get(User, fixture["missing"]["user_id"]).subscription)
        check.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action == "payment.success")).all()), 2)
        check.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action == "payment.review_required")).all()), 1)


class PaymentReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def test_missed_webhook_recovery_preserves_value_and_isolates_errors(self):
        verify_reconciliation_workflow(self, self.engine)

    def test_resumable_pages_do_not_starve_later_payments_or_admit_new_rows(self):
        fixture = seed_reconciliation(self.engine, ("unconfirmed", "paid", "trial"))
        observed = []
        with provider_patches(fixture, observed):
            first = recovery.reconcile_payments(self.engine, apply=True, limit=1)
        self.assertFalse(first["complete"])
        later = seed_reconciliation(self.engine, ("paid",))
        with provider_patches(fixture, observed):
            second = recovery.reconcile_payments(self.engine, apply=True, after_id=first["next_after_id"], ceiling_id=first["ceiling_id"])
        self.assertTrue(second["complete"])
        self.assertEqual({item["payment_id"] for item in second["outcomes"]}, {fixture[kind]["payment_id"] for kind in ("paid", "trial")})
        with Session(self.engine) as db:
            self.assertEqual(db.get(Payment, later["paid"]["payment_id"]).status, "pending")

    def test_audit_failure_rolls_back_and_retry_recovers(self):
        fixture = seed_reconciliation(self.engine, ("paid",))
        before = rows(self.engine)
        with provider_patches(fixture, []), patch.object(payment_service, "create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            report = recovery.reconcile_payments(self.engine, apply=True)
        self.assertEqual(report["outcomes"][0]["outcome"], "error")
        self.assertEqual(rows(self.engine), before)
        with provider_patches(fixture, []):
            self.assertEqual(recovery.reconcile_payments(self.engine, apply=True)["outcomes"][0]["outcome"], "confirmed")

    def test_timeout_does_not_block_next_customer(self):
        fixture = seed_reconciliation(self.engine, ("paid", "trial"))
        observed = []; send = fake_provider(fixture, observed)
        def provider(session, method, url, **kwargs):
            if url.endswith(fixture["paid"]["evidence"]["reference"]):
                raise requests.Timeout("Synthetic outage")
            return send(session, method, url, **kwargs)
        with provider_patches(fixture, observed, provider):
            report = recovery.reconcile_payments(self.engine, apply=True)
        self.assertEqual([item["outcome"] for item in report["outcomes"]], ["error", "confirmed"])

    def test_bounds_and_time_budget_prevent_unbounded_processing(self):
        fixture = seed_reconciliation(self.engine, ("paid",))
        for args in ({"limit": 0}, {"limit": 101}, {"after_id": -1}, {"ceiling_id": -1}, {"time_budget_seconds": float("inf")}, {"time_budget_seconds": 301}, {"apply": "yes"}):
            with self.assertRaises(ValueError): recovery.reconcile_payments(self.engine, **args)
        with patch.object(recovery.time, "monotonic", side_effect=(0, 50)), patch("requests.Session.request") as transport:
            report = recovery.reconcile_payments(self.engine, apply=True)
            transport.assert_not_called()
        self.assertFalse(report["complete"]); self.assertEqual(report["outcomes"], [])
        self.assertEqual(report["next_after_id"], 0)

    def test_command_defaults_to_read_only_and_reports_no_personal_or_provider_data(self):
        from app.jobs.reconcile_payments import main
        fixture = seed_reconciliation(self.engine, ("paid",))
        before = rows(self.engine); output = io.StringIO()
        with patch("app.database.get_engine", return_value=self.engine), patch("requests.Session.request") as transport, patch("sys.stdout", output):
            self.assertEqual(main([]), 0); transport.assert_not_called()
        report = json.loads(output.getvalue())
        self.assertTrue(report["dry_run"]); self.assertEqual(rows(self.engine), before)
        self.assertNotIn(fixture["paid"]["evidence"]["reference"], output.getvalue())
        self.assertNotIn("@", output.getvalue()); self.assertNotIn("sk_test", output.getvalue())

    def test_command_failure_does_not_expose_connection_details(self):
        from app.jobs.reconcile_payments import main
        output = io.StringIO()
        with patch("app.database.get_engine", side_effect=RuntimeError("SYNTHETIC-PRIVATE-CONNECTION-DETAIL")), patch("sys.stdout", output):
            self.assertEqual(main([]), 2)
        self.assertEqual(json.loads(output.getvalue()), {"error": "Payment reconciliation could not complete"})
