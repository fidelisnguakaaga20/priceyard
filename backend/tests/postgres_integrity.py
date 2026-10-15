"""Run only through audit-prep/p00/verify_migrations.py; synthetic PostgreSQL."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import threading
import unittest

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session

import verify_migrations as guard


class _PostgreSQLTestBase(unittest.TestCase):
    def setUp(self):
        self.schema = guard.create_schema()
        self.engine = create_engine(guard.schema_url(self.schema))
        # Cleanup also runs when a later setUp migration fails.
        self.addCleanup(guard.cleanup_schema, self.schema)
        self.addCleanup(self.engine.dispose)


class PostgreSQLMigrationTests(_PostgreSQLTestBase):

    def seed_legacy(self):
        guard.migrate(self.schema, "0021_feedback_screenshot")
        with self.engine.begin() as connection:
            connection.execute(text("INSERT INTO users (id,full_name,email,password_hash,role,is_active,referral_code) VALUES "
                "(1001,'Synthetic Payer','payer@migration.test','unused-test-hash','paid_user',TRUE,'MIGPAID'),"
                "(1002,'Synthetic Reporter','reporter@migration.test','unused-test-hash','reporter',TRUE,'MIGMANUAL')"))
            connection.execute(text("INSERT INTO subscriptions (user_id,plan_name,status,start_date,end_date) VALUES "
                "(1001,'paid_monthly','active','2026-01-01','2027-01-01'),(1002,'paid','active','2026-01-01',NULL)"))
            connection.execute(text("INSERT INTO commodities (id,name,is_active,is_upcoming) VALUES "
                "(1001,'Synthetic Legacy Commodity',TRUE,FALSE),(1002,'Synthetic Inactive Commodity',FALSE,FALSE)"))
            connection.execute(text("INSERT INTO markets (id,name,state,country,is_active) VALUES "
                "(1001,'Synthetic Legacy Market','Synthetic State','Nigeria',TRUE),"
                "(1002,'Synthetic Inactive Market','Synthetic State','Nigeria',FALSE)"))
            connection.execute(text("INSERT INTO price_updates (id,commodity_id,market_id,price_low,price_high,average_price,unit,bag_size,"
                "commodity_type,movement,confidence_level,source_1,source_2,update_date_time,is_outdated,status,created_by,approved_by) VALUES "
                "(1001,1001,1001,90,110,95,'bag','50 kg','shelled','up','Admin confirmed','Synthetic one','Synthetic two','2026-01-01 23:30:00+00',FALSE,'approved',1002,1001),"
                "(1002,1002,1002,80,100,NULL,'bag',NULL,NULL,'unknown','Low confidence',NULL,NULL,'2025-01-01 12:00:00+00',TRUE,'approved',1002,1001)"))
            connection.execute(text("INSERT INTO payments (user_id,reference,plan,amount,currency,status,paystack_transaction_id) "
                "VALUES (1001,'synthetic-legacy-purchase','monthly',2500,'NGN','success','1234001')"))
            connection.execute(text("INSERT INTO cost_breakdowns (commodity_id,market_id,transport,warehouse,security,market_charges,"
                "loading_offloading,other_costs,total_additional_cost,purchase_price_reference,total_estimated_landing_storage_cost) "
                "VALUES (1001,1001,10,0,0,0,0,0,10,95,105)"))

    def test_fresh_upgrade_builds_current_model_columns(self):
        guard.migrate(self.schema)
        import app.models  # noqa: F401
        from app.database import Base
        metadata = inspect(self.engine)
        for table in Base.metadata.sorted_tables:
            actual = {column["name"] for column in metadata.get_columns(table.name)}
            self.assertTrue({column.name for column in table.columns}.issubset(actual), table.name)
        email_column = next(column for column in metadata.get_columns("payments") if column["name"] == "expected_customer_email")
        self.assertEqual(email_column["type"].length, 320)

    def test_upgrade_preserves_legacy_cutoff_manual_grants_and_price_evidence(self):
        self.seed_legacy()
        with self.engine.connect() as connection:
            before = connection.execute(text("SELECT id,commodity_id,market_id,price_low,price_high,average_price,unit,bag_size,"
                "commodity_type,movement,source_1,source_2,update_date_time,status,is_outdated FROM price_updates ORDER BY id")).all()
        guard.migrate(self.schema)
        with self.engine.connect() as connection:
            after = connection.execute(text("SELECT id,commodity_id,market_id,price_low,price_high,average_price,unit,bag_size,"
                "commodity_type,movement,source_1,source_2,update_date_time,status,is_outdated FROM price_updates ORDER BY id")).all()
            self.assertEqual(before, after)
            payer = connection.execute(text("SELECT end_date,paid_expires_at,manual_grant FROM subscriptions WHERE user_id=1001")).one()
            self.assertEqual(payer.paid_expires_at, datetime(2027, 1, 2, tzinfo=timezone.utc))
            manual = connection.execute(text("SELECT manual_grant,end_date,paid_expires_at FROM subscriptions WHERE user_id=1002")).one()
            self.assertEqual(tuple(manual), (True, None, None))
            self.assertEqual(connection.scalar(text("SELECT role FROM users WHERE id=1002")), "reporter")
            self.assertIsNone(connection.scalar(text("SELECT email_verified FROM users WHERE id=1001")))
            payment = connection.execute(text("SELECT amount,requires_reconciliation,entitlement_applied_at FROM payments")).one()
            self.assertEqual(tuple(payment), (Decimal("2500.00"), True, None))
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM entitlement_grants")), 0)
            self.assertEqual(connection.execute(text("SELECT unit,bag_size,reference_date_time FROM cost_breakdowns")).one(), (None, None, None))
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM price_revisions")), 0)

    def test_normalized_duplicates_abort_before_price_ddl_without_merging(self):
        self.seed_legacy()
        guard.migrate(self.schema, "0023_payment_integrity")
        with self.engine.begin() as connection:
            connection.execute(text("INSERT INTO commodities (name,is_active,is_upcoming) VALUES ('egusi',TRUE,FALSE)"))
        with self.assertRaisesRegex(RuntimeError, "duplicates"):
            guard.migrate(self.schema)
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM commodities WHERE lower(trim(name))='egusi'")), 2)
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM price_updates")), 2)
            self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "0023_payment_integrity")
        self.assertNotIn("grade", {column["name"] for column in inspect(self.engine).get_columns("price_updates")})

    def test_invalid_legacy_previous_bounds_abort_without_rewriting(self):
        self.seed_legacy()
        guard.migrate(self.schema, "0023_payment_integrity")
        with self.engine.begin() as connection:
            connection.execute(text("UPDATE price_updates SET previous_price_low=10,previous_price_high=NULL WHERE id=1001"))
        with self.assertRaisesRegex(RuntimeError, "ranges"):
            guard.migrate(self.schema)
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT previous_price_low,previous_price_high FROM price_updates WHERE id=1001")).one(), (Decimal("10.00"), None))
            self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "0023_payment_integrity")

    def test_connection_guards_reject_other_destinations_before_transport(self):
        import psycopg
        for parameters in ({"host": "production-supabase.invalid", "port": 5432, "dbname": "postgres", "user": guard.USER},
                           {"host": guard.HOST, "port": guard.PORT, "dbname": "postgres", "user": guard.USER},
                           {"host": guard.HOST, "port": guard.PORT, "dbname": guard.DATABASE, "user": guard.USER}):
            with self.assertRaises(RuntimeError):
                psycopg.connect(**parameters)
        with self.assertRaises(RuntimeError):
            create_engine("postgresql+psycopg://unused@production-supabase.invalid/postgres")

    def test_downgrade_refuses_to_discard_business_evidence(self):
        guard.migrate(self.schema)
        from alembic import command
        from alembic.config import Config
        config = Config(str(guard.BACKEND / "alembic.ini"))
        config.set_main_option("script_location", str(guard.BACKEND / "migrations"))
        with self.engine.connect() as connection:
            before = connection.scalar(text("SELECT version_num FROM alembic_version"))
        with self.assertRaisesRegex(RuntimeError, "rollback|downgrade"):
            command.downgrade(config, "0023_payment_integrity")
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), before)


class PostgreSQLConcurrencyTests(_PostgreSQLTestBase):
    def setUp(self):
        super().setUp()
        guard.migrate(self.schema)

    def test_two_approvals_serialize_comparable_predecessor(self):
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.models.user import User
        from app.schemas.price_update_schema import PriceUpdateCreate
        from app.services.price_update_service import approve_price_update, create_price_update, get_price_update_for_admin
        with Session(self.engine) as db:
            user = User(full_name="Synthetic Admin", email="concurrency-admin@postgres.test", password_hash="unused",
                        role="admin", is_active=True, referral_code="PGRACE")
            commodity = Commodity(name="Synthetic Concurrent Commodity", is_active=True)
            market = Market(name="Synthetic Concurrent Market", is_active=True)
            db.add_all([user, commodity, market])
            db.commit()
            ids = []
            for hour, average in ((1, 100), (2, 110)):
                item = create_price_update(db, PriceUpdateCreate(commodity_id=commodity.id, market_id=market.id,
                        price_low=90, price_high=120, average_price=average, unit="bag", bag_size="50 kg", grade="A",
                        confidence_level="Admin confirmed", suggested_action="Watch",
                        update_date_time=datetime(2026, 1, 1, hour, tzinfo=timezone.utc)), user)
                ids.append(item.id)
            actor_id = user.id
        barrier = threading.Barrier(2)

        def approve(item_id):
            with Session(self.engine) as db:
                item = get_price_update_for_admin(db, item_id)
                actor = db.get(User, actor_id)
                barrier.wait(timeout=5)
                approve_price_update(db, item, actor)

        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(approve, identifier) for identifier in ids]
            for future in futures:
                future.result(timeout=10)
        with Session(self.engine) as db:
            latest = db.get(PriceUpdate, ids[1])
            self.assertEqual(latest.previous_price_update_id, ids[0])
            self.assertEqual(latest.movement, "up")

    def test_distinct_and_duplicate_payments_preserve_time_exactly_once(self):
        from app.models.entitlement_grant import EntitlementGrant
        from app.models.payment import Payment
        from app.models.subscription import Subscription
        from app.models.user import User
        from app.services import payment_service, subscription_service
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        old_payment_now, old_subscription_now = payment_service.utc_now, subscription_service.utc_now
        payment_service.utc_now = subscription_service.utc_now = lambda: now
        try:
            with Session(self.engine) as db:
                user = User(full_name="Synthetic Payer", email="concurrency-payer@postgres.test", password_hash="unused",
                            role="reporter", is_active=True, email_verified=True, referral_code="PGPAYER")
                user.subscription = Subscription(plan_name="paid_monthly", status="active", paid_expires_at=now + timedelta(days=10))
                db.add(user)
                db.flush()
                for index in range(2):
                    db.add(Payment(user_id=user.id, reference=f"synthetic-concurrent-{index}", plan="monthly", amount=2500,
                                   currency="NGN", status="pending", duration_days=30, provider_environment="test",
                                   expected_customer_email=user.email))
                db.commit()
                user_id, email = user.id, user.email
            barrier = threading.Barrier(3)

            def deliver(index):
                with Session(self.engine) as db:
                    barrier.wait(timeout=5)
                    outcome = payment_service.handle_webhook_event(db, {"event": "charge.success", "data": {
                        "reference": f"synthetic-concurrent-{index}", "id": 910000 + index, "amount": 250000,
                        "currency": "NGN", "status": "success", "domain": "test", "customer": {"email": email}}})
                    db.commit()
                    return outcome

            with ThreadPoolExecutor(max_workers=3) as workers:
                futures = [workers.submit(deliver, index) for index in (0, 1, 0)]
                results = [future.result(timeout=10) for future in futures]
            self.assertEqual(sorted(results), ["already_applied", "applied", "applied"])
            with Session(self.engine) as db:
                subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
                self.assertEqual(subscription.paid_expires_at, now + timedelta(days=70))
                self.assertEqual(len(list(db.scalars(select(EntitlementGrant)).all())), 2)
                self.assertEqual(db.get(User, user_id).role, "reporter")
        finally:
            payment_service.utc_now, subscription_service.utc_now = old_payment_now, old_subscription_now

    def test_concurrent_enqueue_and_workers_deduplicate_and_claim_distinct_jobs(self):
        from app.models.notification_job import NotificationJob
        from app.services.notification_service import enqueue_notification, process_notifications
        barrier = threading.Barrier(2)

        def enqueue():
            with Session(self.engine) as db:
                barrier.wait(timeout=5)
                added = enqueue_notification(db, channel="email", recipient="synthetic@postgres-notice.test",
                    payload={"subject": "Synthetic", "body": "Synthetic public observation"}, event_key="synthetic-race")
                db.commit()
                return added

        with ThreadPoolExecutor(max_workers=2) as workers:
            results = [future.result(timeout=10) for future in [workers.submit(enqueue), workers.submit(enqueue)]]
        self.assertEqual(sorted(results), [False, True])
        with Session(self.engine) as db:
            enqueue_notification(db, channel="email", recipient="other@postgres-notice.test",
                payload={"subject": "Synthetic", "body": "Synthetic other observation"}, event_key="synthetic-second")
            db.commit()
        sending = threading.Barrier(2)
        delivered = []
        collection_lock = threading.Lock()

        def fake_sender(job):
            with collection_lock:
                delivered.append(job.id)
            sending.wait(timeout=5)

        def deliver():
            with Session(self.engine, expire_on_commit=False) as db:
                return process_notifications(db, limit=1, senders={"email": fake_sender})

        with ThreadPoolExecutor(max_workers=2) as workers:
            results = [future.result(timeout=10) for future in [workers.submit(deliver), workers.submit(deliver)]]
        self.assertEqual(sum(result["sent"] for result in results), 2)
        self.assertEqual(len(set(delivered)), 2)
        with Session(self.engine) as db:
            self.assertTrue(all(job.status == "sent" and job.attempts == 1 for job in db.scalars(select(NotificationJob)).all()))

    def test_stale_notification_worker_cannot_acknowledge_replaced_postgres_lease(self):
        from app.models.notification_job import NotificationJob
        from app.services.notification_service import enqueue_notification, process_notifications
        from sqlalchemy import update
        with Session(self.engine, expire_on_commit=False) as worker:
            enqueue_notification(worker, channel="email", recipient="lease@postgres-notice.test",
                payload={"subject": "Synthetic", "body": "Synthetic lease test"}, event_key="synthetic-lease")
            worker.commit()

            def replacement(job):
                with Session(self.engine) as other:
                    other.execute(update(NotificationJob).where(NotificationJob.id == job.id).values(lease_token="synthetic-new-lease"))
                    other.commit()

            result = process_notifications(worker, limit=1, senders={"email": replacement})
            self.assertEqual(result["sent"], 0)
        with Session(self.engine) as db:
            job = db.scalar(select(NotificationJob))
            self.assertEqual(job.status, "processing")
            self.assertEqual(job.lease_token, "synthetic-new-lease")

    def test_concurrent_password_resets_claim_once_and_revoke_existing_sessions(self):
        from fastapi import HTTPException
        from app.models.auth_session import AuthSession
        from app.models.password_reset_token import PasswordResetToken
        from app.models.user import User
        from app.services.auth_session_service import hash_credential, issue_session
        from app.services.password_reset_service import reset_password
        from app.utils.password import hash_password, verify_password
        proof = "synthetic-postgresql-reset-proof-" + "x" * 32
        with Session(self.engine) as db:
            user = User(full_name="Synthetic reset owner", email="reset-race@postgres.test",
                        password_hash=hash_password("OriginalSynthetic8"), role="free_user", is_active=True,
                        email_verified=True, referral_code="PGRESET")
            db.add(user)
            db.flush()
            owner_id = user.id
            issue_session(db, user)
            issue_session(db, user)
            db.add(PasswordResetToken(user_id=owner_id, token_hash=hash_credential(proof),
                                     expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)))
            db.commit()
        barrier = threading.Barrier(2)
        passwords = ("SyntheticReplacementA8", "SyntheticReplacementB8")

        def reset(password):
            with Session(self.engine) as db:
                barrier.wait(timeout=5)
                try:
                    reset_password(db, token=proof, new_password=password)
                    db.commit()
                    return "reset"
                except HTTPException as error:
                    db.rollback()
                    return error.status_code

        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(reset, password) for password in passwords]
            outcomes = [future.result(timeout=15) for future in futures]
        self.assertEqual(outcomes.count("reset"), 1)
        self.assertEqual(outcomes.count(400), 1)
        with Session(self.engine) as db:
            owner = db.get(User, owner_id)
            self.assertEqual(owner.auth_version, 1)
            self.assertEqual(sum(verify_password(password, owner.password_hash) for password in passwords), 1)
            sessions = db.scalars(select(AuthSession).where(AuthSession.user_id == owner_id)).all()
            self.assertEqual(len(sessions), 2)
            self.assertTrue(all(session.revoked_at is not None for session in sessions))
            self.assertIsNotNone(db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == owner_id)).used_at)

    def test_concurrent_admin_deactivation_preserves_one_active_administrator(self):
        from fastapi import HTTPException
        from app.models.user import User
        from app.schemas.user_schema import AdminUserUpdate
        from app.services.user_service import update_user
        with Session(self.engine) as db:
            admins = [User(full_name=f"Synthetic admin {index}", email=f"admin-race-{index}@postgres.test",
                           password_hash="unused-test-hash", role="admin", is_active=True, referral_code=f"PGADM{index}")
                      for index in range(2)]
            db.add_all(admins)
            db.commit()
            identifiers = [admin.id for admin in admins]
        barrier = threading.Barrier(2)

        def deactivate(identifier):
            with Session(self.engine) as db:
                target = db.get(User, identifier)
                barrier.wait(timeout=5)
                try:
                    update_user(db, target, AdminUserUpdate(is_active=False))
                    db.commit()
                    return "deactivated"
                except HTTPException as error:
                    db.rollback()
                    return error.status_code

        with ThreadPoolExecutor(max_workers=2) as workers:
            outcomes = [future.result(timeout=10) for future in [workers.submit(deactivate, identifier) for identifier in identifiers]]
        self.assertEqual(outcomes.count("deactivated"), 1)
        self.assertEqual(outcomes.count(409), 1)
        with Session(self.engine) as db:
            self.assertEqual(len(db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True))).all()), 1)


if __name__ == "__main__":
    raise SystemExit("Use the fixed-cluster P00 verify_migrations.py guard")
