"""Owner-approved future paid/trial value, without historical backfills."""
from datetime import datetime, timedelta, timezone
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import activate_paid_subscription, has_full_access

NOW = datetime(2026, 10, 16, 23, 30, tzinfo=timezone.utc)


class SubscriptionValueTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.count = 0

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def subscription(self, status, *, end=None, trial_end=None, role="free_user"):
        self.count += 1
        user = User(full_name="Synthetic value", email=f"value{self.count}@example.com",
                    password_hash="not-used", role=role, is_active=True, referral_code=f"VALUE{self.count}")
        user.subscription = Subscription(status=status, plan_name="trial" if status == "trial" else "paid_monthly",
                                         end_date=end, trial_started_at=NOW-timedelta(days=4), trial_ends_at=trial_end)
        self.db.add(user)
        self.db.commit()
        return user.subscription

    def test_both_renewal_plans_preserve_remaining_paid_days(self):
        for plan, days in (("monthly", 30), ("seasonal", 90)):
            with self.subTest(plan=plan):
                old_end = NOW.date()+timedelta(days=10)
                subscription = self.subscription("active", end=old_end)
                activate_paid_subscription(self.db, subscription, plan=plan, now=NOW)
                self.assertEqual(subscription.end_date, old_end+timedelta(days=days))
                self.assertEqual(subscription.plan_name, "paid_"+plan)

    def test_trial_purchase_preserves_timestamp_and_full_remaining_trial(self):
        for plan, days in (("monthly", 30), ("seasonal", 90)):
            with self.subTest(plan=plan):
                trial_end = NOW+timedelta(days=10, minutes=15)
                subscription = self.subscription("trial", trial_end=trial_end)
                before = (subscription.trial_started_at, subscription.trial_ends_at)
                activate_paid_subscription(self.db, subscription, plan=plan, now=NOW)
                self.assertEqual(subscription.end_date, trial_end.date()+timedelta(days=days))
                self.assertEqual((subscription.trial_started_at, subscription.trial_ends_at), before)
                # Existing paid dates are inclusive, including the final day.
                final = datetime.combine(subscription.end_date, datetime.max.time(), tzinfo=timezone.utc)
                self.assertTrue(has_full_access(subscription, now=final))
                self.assertFalse(has_full_access(subscription, now=final+timedelta(microseconds=1)))

    def test_legacy_naive_trial_end_is_utc(self):
        trial_end = (NOW+timedelta(days=3)).replace(tzinfo=None)
        subscription = self.subscription("trial", trial_end=trial_end)
        activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
        self.assertEqual(subscription.end_date, trial_end.date()+timedelta(days=30))

    def test_trial_final_minutes_and_exact_expiry_keep_original_date_boundary(self):
        for offset in (timedelta(minutes=15), timedelta(0), timedelta(minutes=-15)):
            with self.subTest(offset=offset):
                subscription = self.subscription("trial", trial_end=NOW+offset)
                activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
                self.assertEqual(subscription.end_date, NOW.date()+timedelta(days=30))

    def test_expired_free_cancelled_do_not_reactivate_stale_future_fields(self):
        for status in ("free", "expired", "cancelled"):
            with self.subTest(status=status):
                subscription = self.subscription(status, end=NOW.date()+timedelta(days=100), trial_end=NOW+timedelta(days=100))
                activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
                self.assertEqual(subscription.end_date, NOW.date()+timedelta(days=30))
        subscription = self.subscription("active", end=NOW.date()-timedelta(days=1))
        activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
        self.assertEqual(subscription.end_date, NOW.date()+timedelta(days=30))

    def test_cross_plan_purchases_accumulate_and_keep_staff_authority(self):
        subscription = self.subscription("active", end=NOW.date()+timedelta(days=10), role="reporter")
        activate_paid_subscription(self.db, subscription, plan="seasonal", now=NOW)
        activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW)
        self.assertEqual(subscription.end_date, NOW.date()+timedelta(days=130))
        self.assertEqual(subscription.user.role, "reporter")

    def test_uncommitted_activation_can_roll_back_without_losing_prior_days(self):
        old_end = NOW.date()+timedelta(days=10)
        subscription = self.subscription("active", end=old_end)
        activate_paid_subscription(self.db, subscription, plan="monthly", now=NOW, commit=False)
        self.assertEqual(subscription.end_date, old_end+timedelta(days=30))
        self.db.rollback()
        self.db.refresh(subscription)
        self.assertEqual(subscription.end_date, old_end)
