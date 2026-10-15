from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.notification_job import NotificationJob
from app.models.user import User
from app.services.notification_service import process_notifications
from app.services.subscription_service import aware_utc, build_trial_subscription, send_trial_expiry_reminders


class TrialReminderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def add_trial(self, index=1):
        user = User(full_name="Synthetic trial", email=f"trial{index}@example.com", password_hash="synthetic-unused-hash",
                    role="free_user", is_active=True, referral_code=f"TR{index:06}")
        user.subscription = build_trial_subscription(user=user, now=datetime.now(timezone.utc) - timedelta(days=12))
        self.db.add(user)
        self.db.flush()
        return user.subscription

    def test_reminder_is_queued_once_without_changing_trial_or_contacting_provider(self) -> None:
        subscription = self.add_trial()
        started, ended = subscription.trial_started_at, subscription.trial_ends_at
        self.db.commit()
        with patch("app.services.email_service.send_email") as provider:
            self.assertEqual(send_trial_expiry_reminders(self.db), 1)
            self.db.commit()
            self.assertEqual(send_trial_expiry_reminders(self.db), 0)
            provider.assert_not_called()
        jobs = self.db.scalars(select(NotificationJob)).all()
        self.assertEqual(len(jobs), 1)
        self.assertIsNotNone(subscription.trial_reminder_sent_at)
        self.assertEqual(aware_utc(subscription.trial_started_at), aware_utc(started))
        self.assertEqual(aware_utc(subscription.trial_ends_at), aware_utc(ended))
        self.assertIn("WAT", jobs[0].payload["body"])
        self.assertIn("2,500 for 30 days", jobs[0].payload["body"])
        self.assertIn("6,000 for 90 days", jobs[0].payload["body"])

    def test_paid_customer_is_not_sent_an_old_trial_reminder(self) -> None:
        subscription = self.add_trial()
        send_trial_expiry_reminders(self.db)
        subscription.status = "active"
        subscription.plan_name = "paid_monthly"
        subscription.paid_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        self.db.commit()
        calls = []
        counts = process_notifications(self.db, senders={"email": lambda job: calls.append(job.id)})
        self.assertEqual(counts["skipped"], 1)
        self.assertFalse(calls)

    def test_delivery_failure_retries_existing_job_without_requeue_or_trial_change(self) -> None:
        subscription = self.add_trial()
        original_end = subscription.trial_ends_at
        send_trial_expiry_reminders(self.db)
        self.db.commit()
        def failed(_job):
            raise RuntimeError("Synthetic provider unavailable")
        self.assertEqual(process_notifications(self.db, senders={"email": failed})["retried"], 1)
        self.assertEqual(send_trial_expiry_reminders(self.db), 0)
        job = self.db.scalar(select(NotificationJob))
        job.available_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()
        self.assertEqual(process_notifications(self.db, senders={"email": lambda _: None})["sent"], 1)
        self.assertEqual(job.attempts, 2)
        self.assertEqual(aware_utc(subscription.trial_ends_at), aware_utc(original_end))

    def test_reminder_batch_is_bounded_and_next_run_picks_remaining(self) -> None:
        for index in range(1, 202):
            self.add_trial(index)
        self.db.commit()
        self.assertEqual(send_trial_expiry_reminders(self.db), 200)
        self.db.commit()
        self.assertEqual(send_trial_expiry_reminders(self.db), 1)
        self.db.commit()
        self.assertEqual(send_trial_expiry_reminders(self.db), 0)
        self.assertEqual(len(self.db.scalars(select(NotificationJob)).all()), 201)

    def test_changed_trial_end_suppresses_obsolete_reminder(self) -> None:
        subscription = self.add_trial()
        send_trial_expiry_reminders(self.db)
        subscription.trial_ends_at += timedelta(days=7)
        self.db.commit()
        calls = []
        counts = process_notifications(self.db, senders={"email": lambda job: calls.append(job.id)})
        self.assertEqual(counts["skipped"], 1)
        self.assertFalse(calls)


if __name__ == "__main__":
    unittest.main()
