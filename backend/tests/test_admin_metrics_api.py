"""Real JWT/HTTP aggregate contracts against a fresh synthetic SQLite database."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import AtomicSession, Base, get_db
from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.market import Market
from app.models.payment import Payment
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.routes.admin_metrics_routes import router
from app.services.auth_session_service import issue_session
from app.services.subscription_service import build_trial_subscription
from app.transactions import install_transactions


class AdminMetricsApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.app = FastAPI()
        self.app.include_router(router)
        def database(request: Request):
            if not hasattr(request.state, "database_session"):
                request.state.database_session = AtomicSession(bind=self.engine, autoflush=False, expire_on_commit=False)
            return request.state.database_session
        self.app.dependency_overrides[get_db] = database
        install_transactions(self.app)
        self.client = TestClient(self.app, raise_server_exceptions=False)
        self.headers = {}
        self.now = datetime.now(timezone.utc)
        with Session(self.engine) as db:
            self.user_ids = {}
            for name, role in (("admin", "admin"), ("free", "free_user"), ("reporter", "reporter"), ("trial", "free_user")):
                user = User(full_name=f"Synthetic {name}", email=f"{name}@metrics.test", password_hash="unused",
                            is_active=True, email_verified=True, role=role, referral_code=f"M{name.upper()}")
                user.subscription = build_trial_subscription(user=user) if name == "trial" else Subscription(plan_name="free", status="free")
                db.add(user); db.flush()
                self.user_ids[name] = user.id
                self.headers[name] = {"Authorization": "Bearer " + issue_session(db, user).access_token}
            db.commit()

    def tearDown(self):
        self.client.close()
        self.engine.dispose()

    def test_admin_only_real_authentication_and_private_response(self):
        self.assertEqual(self.client.get("/admin/metrics").status_code, 401)
        for name in ("free", "trial", "reporter"):
            self.assertEqual(self.client.get("/admin/metrics", headers=self.headers[name]).status_code, 403)
        response = self.client.get("/admin/metrics", headers=self.headers["admin"])
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        with Session(self.engine) as db:
            db.get(User, self.user_ids["admin"]).is_active = False
            db.commit()
        self.assertEqual(self.client.get("/admin/metrics", headers=self.headers["admin"]).status_code, 403)

    def test_totals_cover_beyond_one_hundred_records_and_keep_payment_evidence_separate(self):
        with Session(self.engine) as db:
            for index in range(125):
                db.add(User(full_name="Synthetic aggregate member", email=f"member{index}@metrics.test", password_hash="unused",
                            role="free_user", is_active=True, referral_code=f"METRIC{index}"))
            for index in range(123):
                db.add(Payment(user_id=self.user_ids["free"], reference=f"py_metric_{index}", plan="monthly",
                    amount=Decimal("2500.01"), currency="NGN", status="success", duration_days=30,
                    confirmed_at=self.now if index < 101 else None,
                    entitlement_applied_at=self.now if index < 101 else None,
                    paystack_transaction_id=str(50000 + index) if index < 101 else None,
                    requires_reconciliation=index >= 101))
            db.add(Payment(user_id=self.user_ids["free"], reference="py_metric_reviewed", plan="seasonal",
                amount=Decimal("6000.00"), currency="NGN", status="success", duration_days=90,
                reconciliation_resolution="already_applied", requires_reconciliation=False))
            db.add(Payment(user_id=self.user_ids["free"], reference="py_metric_other_currency", plan="monthly",
                amount=Decimal("999.00"), currency="USD", status="success", duration_days=30, requires_reconciliation=True))
            for index, state in enumerate(("pending", "pending", "pending", "failed", "failed")):
                db.add(Payment(user_id=self.user_ids["free"], reference=f"py_metric_other_{index}", plan="monthly",
                               amount=Decimal("2500.00"), currency="NGN", status=state, duration_days=30))
            for index in range(110):
                db.add(Feedback(user_id=self.user_ids["free"], rating=4, is_public_testimonial=index < 105))
            db.commit()
        statements = []
        def recorded(_connection, _cursor, statement, _parameters, _context, _many):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)
        event.listen(self.engine, "before_cursor_execute", recorded)
        try:
            response = self.client.get("/admin/metrics", headers=self.headers["admin"])
        finally:
            event.remove(self.engine, "before_cursor_execute", recorded)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["users_total"], 129)
        self.assertEqual(data["payments_total"], 130)
        self.assertEqual(data["payments_recorded_success"], 125)
        self.assertEqual(data["payments_provider_confirmed"], 101)
        self.assertEqual(data["payments_access_applied"], 102)
        self.assertEqual(data["payments_requires_review"], 23)
        self.assertEqual(data["payments_pending"], 3)
        self.assertEqual(data["payments_failed"], 2)
        self.assertEqual(Decimal(data["recorded_success_amount_ngn"]), Decimal("313501.23"))
        self.assertEqual(Decimal(data["recorded_success_amounts"]["USD"]), Decimal("999.00"))
        self.assertEqual(data["feedback_count"], 110)
        self.assertEqual(data["testimonials_live"], 105)
        self.assertEqual(Decimal(data["feedback_average_rating"]), Decimal("4.00"))
        self.assertLessEqual(len(statements), 15, "Dashboard queries must stay bounded, not one query per record")
        self.assertNotIn("@metrics.test", response.text)
        print(f"Synthetic admin metrics: {len(statements)} SELECT statements; 129 users, 130 payments, 110 feedback records.")

    def test_current_price_and_expiry_counts_follow_access_and_measurement_rules(self):
        with Session(self.engine) as db:
            commodity = Commodity(name="Synthetic metrics crop", is_active=True)
            market = Market(name="Synthetic metrics market", state="Synthetic", is_active=True)
            db.add_all([commodity, market]); db.flush()
            prices = []
            for index, package in enumerate(("50kg", "50kg", "100kg")):
                price = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=90, price_high=110,
                    average_price=None, unit="1 bag", bag_size=package, status="approved", movement="unknown",
                    confidence_level="Admin confirmed", created_by=self.user_ids["admin"],
                    update_date_time=self.now - timedelta(hours=3-index), is_outdated=index == 1)
                db.add(price); prices.append(price)
            db.flush()
            db.add_all([PriceFlag(price_update_id=prices[2].id, user_id=self.user_ids["free"], resolved=False),
                        PriceFlag(price_update_id=prices[2].id, user_id=self.user_ids["reporter"], resolved=False)])
            # A stale stored trial label is not proof of valid access.
            trial = db.get(User, self.user_ids["trial"]).subscription
            trial.trial_ends_at = self.now - timedelta(days=1)
            manual = db.get(User, self.user_ids["reporter"]).subscription
            manual.status = "active"; manual.manual_grant = True
            legacy_paid = db.get(User, self.user_ids["free"]).subscription
            legacy_paid.status = "active"; legacy_paid.end_date = self.now.date()
            db.commit()
        response = self.client.get("/admin/metrics", headers=self.headers["admin"])
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["prices_total"], 3)
        self.assertEqual(data["prices_current"], 1)  # no fallback to the older 50kg price
        self.assertEqual(data["prices_outdated"], 1)
        self.assertEqual(data["open_flags"], 2)
        self.assertEqual(data["flagged_prices"], 1)
        self.assertEqual(data["subscription_statuses"]["trial"], 1)
        self.assertEqual(data["valid_trial_subscriptions"], 0)
        self.assertEqual(data["valid_paid_subscriptions"], 2)


if __name__ == "__main__":
    unittest.main()
