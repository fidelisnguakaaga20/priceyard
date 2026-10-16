import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import (
    activate_paid_subscription, apply_paid_expiry, apply_trial_expiry,
    list_subscriptions, update_subscription_status,
)

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


class SubscriptionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.counter = 0

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def make_subscription(self, role="reporter", status="trial", *, expired=True):
        self.counter += 1
        user = User(full_name="Synthetic staff", email=f"staff{self.counter}@example.com", password_hash="not-used-by-this-test", role=role, referral_code=f"STAFF{self.counter}", is_active=True)
        delta = timedelta(days=-1 if expired else 30)
        subscription = Subscription(user=user, status=status, plan_name="trial" if status == "trial" else "paid_monthly", trial_started_at=NOW-timedelta(days=15) if status == "trial" else None, trial_ends_at=NOW+delta if status == "trial" else None, start_date=(NOW-timedelta(days=31)).date() if status == "active" else None, end_date=(NOW+delta).date() if status == "active" else None)
        self.db.add(user)
        self.db.commit()
        return subscription

    def test_trial_expiry_preserves_reporter_authority(self):
        subscription = self.make_subscription()
        self.assertTrue(apply_trial_expiry(subscription, now=NOW))
        self.assertEqual(subscription.status, "expired")
        self.assertEqual(subscription.user.role, "reporter")

    def test_paid_expiry_preserves_reporter_authority(self):
        subscription = self.make_subscription(status="active")
        self.assertTrue(apply_paid_expiry(subscription, now=NOW))
        self.assertEqual(subscription.status, "expired")
        self.assertEqual(subscription.user.role, "reporter")

    def test_listing_processes_every_expired_account(self):
        # Use unambiguously past/future dates independent of machine clock.
        expired = [self.make_subscription(role="free_user"), self.make_subscription(role="paid_user", status="active"), self.make_subscription()]
        for subscription in expired:
            subscription.trial_ends_at = datetime(2000, 1, 1, tzinfo=timezone.utc) if subscription.status == "trial" else None
            subscription.end_date = datetime(2000, 1, 1).date() if subscription.status == "active" else None
        valid = self.make_subscription(status="active", expired=False)
        valid.end_date = datetime(2099, 1, 1).date()
        self.db.commit()
        result = list_subscriptions(self.db)
        self.assertEqual(len(result), 4)
        self.assertEqual([item.status for item in expired], ["expired"] * 3)
        self.assertEqual(expired[-1].user.role, "reporter")
        self.assertEqual(valid.status, "active")
        self.assertEqual(valid.end_date, datetime(2099, 1, 1).date())

    def test_subscription_administration_keeps_staff_roles(self):
        for role in ("reporter", "admin"):
            subscription = self.make_subscription(role=role)
            for status in ("active", "free", "expired", "cancelled", "trial"):
                with self.subTest(role=role, status=status):
                    update_subscription_status(self.db, subscription, status)
                    self.assertEqual(subscription.user.role, role)
                    self.assertEqual(subscription.status, status)

    def test_purchase_keeps_reporter_authority(self):
        subscription = self.make_subscription()
        activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
        self.assertEqual(subscription.user.role, "reporter")
        self.assertEqual(subscription.end_date, (NOW+timedelta(days=30)).date())

    def test_ordinary_expiry_and_indefinite_manual_grants_unchanged(self):
        ordinary = self.make_subscription(role="paid_user", status="active")
        self.assertTrue(apply_paid_expiry(ordinary, now=NOW))
        self.assertEqual(ordinary.user.role, "free_user")
        manual = self.make_subscription(role="paid_user", status="active")
        manual.end_date = None
        self.assertFalse(apply_paid_expiry(manual, now=NOW))
        self.assertEqual(manual.status, "active")
