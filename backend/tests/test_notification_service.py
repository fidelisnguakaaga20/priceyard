"""Durable synthetic notifications; no provider transport is invoked."""
from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from app.database import AtomicSession, Base
import app.models  # noqa: F401
from app.models.notification_job import NotificationJob
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.services.notification_service import delivery_payload, enqueue_notification, enqueue_secure_email, process_notifications


class NotificationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        self.user = User(full_name="Synthetic recipient", email="notice@example.com", password_hash="synthetic-unused-hash",
                         role="free_user", is_active=True, referral_code="NOTICE01")
        self.db.add(self.user)
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def queue(self, channel="email", **changes):
        arguments = dict(channel=channel, recipient="notice@example.com", payload={"subject": "Synthetic", "body": "Public facts"}, event_key="synthetic:event")
        arguments.update(changes)
        return enqueue_notification(self.db, **arguments)

    def test_enqueue_is_deduplicated_and_has_no_provider_side_effect(self) -> None:
        with patch("app.services.email_service.send_email") as sender:
            self.assertTrue(self.queue())
            self.assertFalse(self.queue())
            self.assertTrue(self.queue("push", recipient=str(self.user.id)))
            sender.assert_not_called()
        self.assertEqual(len(self.db.scalars(select(NotificationJob)).all()), 2)

    def test_failed_email_does_not_suppress_other_channels(self) -> None:
        for channel in ("email", "push", "whatsapp"):
            self.queue(channel)
        self.db.commit()
        calls = []
        def email(_job):
            calls.append("email")
            raise RuntimeError("synthetic provider detail must not be persisted")
        counts = process_notifications(self.db, senders={"email": email, "push": lambda _: calls.append("push"), "whatsapp": lambda _: calls.append("whatsapp")})
        self.assertEqual(counts["sent"], 2)
        self.assertEqual(counts["retried"], 1)
        self.assertEqual(set(calls), {"email", "push", "whatsapp"})
        email_job = self.db.scalar(select(NotificationJob).where(NotificationJob.channel == "email"))
        self.assertEqual(email_job.error_code, "RuntimeError")
        self.assertEqual(email_job.attempts, 1)
        self.assertEqual(email_job.status, "pending")

    def test_retry_cap_stops_after_five_attempts(self) -> None:
        self.queue()
        job = self.db.scalar(select(NotificationJob))
        job.attempts = 4
        self.db.commit()
        def fail(_job):
            raise RuntimeError("synthetic failure")
        counts = process_notifications(self.db, senders={"email": fail})
        self.assertEqual(counts["failed"], 1)
        self.assertEqual(job.status, "failed")
        self.assertEqual(job.attempts, 5)
        self.assertEqual(process_notifications(self.db, senders={"email": fail})["failed"], 0)

    def test_expired_worker_lease_can_be_reclaimed(self) -> None:
        self.queue()
        job = self.db.scalar(select(NotificationJob))
        job.status = "processing"
        job.lease_token = "synthetic-old-lease"
        job.attempts = 1
        job.available_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        self.db.commit()
        counts = process_notifications(self.db, senders={"email": lambda _: None})
        self.assertEqual(counts["sent"], 1)
        self.assertEqual(job.attempts, 2)
        self.assertIsNone(job.lease_token)

    def test_stale_worker_cannot_acknowledge_another_lease(self) -> None:
        self.queue()
        self.db.commit()
        def replaced(job):
            self.db.execute(update(NotificationJob).where(NotificationJob.id == job.id).values(lease_token="synthetic-new-owner"))
            self.db.commit()
        counts = process_notifications(self.db, limit=1, senders={"email": replaced})
        job = self.db.scalar(select(NotificationJob))
        self.assertEqual(counts["sent"], 0)
        self.assertEqual(job.status, "processing")
        self.assertEqual(job.lease_token, "synthetic-new-owner")

    def test_sensitive_mail_is_encrypted_until_worker_delivery(self) -> None:
        enqueue_secure_email(self.db, recipient=self.user.email, subject="Synthetic ownership proof",
                             body="http://127.0.0.1/verify-email?token=synthetic-proof",
                             expires_at=datetime.now(timezone.utc) + timedelta(minutes=15), user_id=self.user.id, event_key="proof:1")
        job = self.db.scalar(select(NotificationJob))
        self.assertNotIn("synthetic-proof", json.dumps(job.payload))
        self.db.commit()
        sent = []
        counts = process_notifications(self.db, senders={"email": lambda job: sent.append(delivery_payload(job.payload))})
        self.assertEqual(counts["sent"], 1)
        self.assertIn("synthetic-proof", sent[0]["body"])

    def test_expired_mail_and_disabled_account_are_not_delivered(self) -> None:
        self.queue(payload={"_expires_at": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()}, event_key="expired")
        self.queue(payload={"_user_id": self.user.id}, event_key="inactive")
        self.user.is_active = False
        self.db.commit()
        calls = []
        counts = process_notifications(self.db, senders={"email": lambda job: calls.append(job.id)})
        self.assertEqual(counts["skipped"], 2)
        self.assertFalse(calls)

    def test_premium_payload_is_rechecked_before_delivery(self) -> None:
        self.queue(payload={"_user_id": self.user.id, "_requires_full_access": True})
        self.db.commit()
        calls = []
        counts = process_notifications(self.db, senders={"email": lambda job: calls.append(job.id)})
        self.assertEqual(counts["skipped"], 1)
        self.assertFalse(calls)

    def test_request_session_cannot_run_worker(self) -> None:
        with AtomicSession(bind=self.engine) as request_session:
            with self.assertRaises(RuntimeError):
                process_notifications(request_session, senders={"email": lambda _: None})

    def test_superseded_or_used_proof_is_not_delivered(self) -> None:
        now = datetime.now(timezone.utc)
        proof = PasswordResetToken(user_id=self.user.id, token_hash="a" * 64, expires_at=now + timedelta(minutes=15), used_at=now)
        self.db.add(proof)
        self.db.flush()
        enqueue_secure_email(self.db, recipient=self.user.email, subject="Synthetic reset", body="synthetic old proof",
                             expires_at=proof.expires_at, user_id=self.user.id, event_key="used-proof", proof_type="password_reset", proof_id=proof.id)
        self.db.commit()
        calls = []
        counts = process_notifications(self.db, senders={"email": lambda job: calls.append(job.id)})
        self.assertEqual(counts["skipped"], 1)
        self.assertFalse(calls)

    def test_unsubscribed_push_device_is_skipped_without_provider_calls(self) -> None:
        self.queue("push", recipient=str(self.user.id), payload={"title": "Synthetic", "body": "Public facts", "url": "http://127.0.0.1/prices"})
        self.db.commit()
        with patch("app.services.push_service.webpush") as sender:
            counts = process_notifications(self.db)
            sender.assert_not_called()
        self.assertEqual(counts["skipped"], 1)


if __name__ == "__main__":
    unittest.main()
