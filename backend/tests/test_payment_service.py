import hashlib
import hmac
import json
import os
import unittest
from datetime import date, timedelta

os.environ.setdefault("FRONTEND_URL", "https://priceyard.onrender.com")

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.payment import Payment
from app.models.user import User
from app.services import payment_service
from app.services.subscription_service import apply_paid_expiry, build_trial_subscription, update_subscription_status
from app.utils.password import hash_password


class FakeSettings:
    paystack_secret_key = "sk_test_fake123"
    frontend_url = "https://priceyard.onrender.com"


class PaymentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            full_name="Payment Test",
            email="payer@example.com",
            password_hash=hash_password("Password1"),
            role="free_user",
            is_active=True,
            referral_code="TESTCODE",
        )
        self.user.subscription = build_trial_subscription(user=self.user)
        self.db.add(self.user)
        self.db.commit()

        self.original_get_settings = payment_service.get_settings
        payment_service.get_settings = lambda: FakeSettings()

    def tearDown(self) -> None:
        payment_service.get_settings = self.original_get_settings
        self.db.close()
        self.engine.dispose()

    def _signed_webhook(self, reference: str, transaction_id: int = 999) -> tuple[bytes, str]:
        payload = {"event": "charge.success", "data": {"reference": reference, "id": transaction_id}}
        raw_body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(b"sk_test_fake123", raw_body, hashlib.sha512).hexdigest()
        return raw_body, signature

    def test_webhook_signature_verification(self) -> None:
        raw_body, signature = self._signed_webhook("py_test_1")
        self.assertTrue(payment_service.verify_webhook_signature(raw_body, signature))
        self.assertFalse(payment_service.verify_webhook_signature(raw_body, "wrong-signature"))
        self.assertFalse(payment_service.verify_webhook_signature(raw_body, None))

    def test_successful_webhook_activates_subscription_with_correct_end_date(self) -> None:
        payment = Payment(user_id=self.user.id, reference="py_test_2", plan="monthly", amount=2500, currency="NGN", status="pending")
        self.db.add(payment)
        self.db.commit()

        _, signature = self._signed_webhook("py_test_2")
        payload = json.loads(self._signed_webhook("py_test_2")[0])
        payment_service.handle_webhook_event(self.db, payload)

        self.db.refresh(payment)
        self.assertEqual(payment.status, "success")
        self.assertEqual(payment.paystack_transaction_id, "999")

        subscription = self.db.scalar(select(self.user.subscription.__class__).where(self.user.subscription.__class__.user_id == self.user.id))
        self.assertEqual(subscription.status, "active")
        self.assertEqual(subscription.plan_name, "paid_monthly")
        self.assertEqual(subscription.end_date, date.today() + timedelta(days=30))
        self.db.refresh(self.user)
        self.assertEqual(self.user.role, "paid_user")

    def test_webhook_is_idempotent_on_replay(self) -> None:
        payment = Payment(user_id=self.user.id, reference="py_test_3", plan="seasonal", amount=6000, currency="NGN", status="pending")
        self.db.add(payment)
        self.db.commit()

        payload = json.loads(self._signed_webhook("py_test_3")[0])
        payment_service.handle_webhook_event(self.db, payload)
        first_end_date = self.user.subscription.end_date

        # Replay the same event - must not re-extend the subscription or error
        payment_service.handle_webhook_event(self.db, payload)
        self.assertEqual(self.user.subscription.end_date, first_end_date)

    def test_unknown_reference_is_ignored_not_an_error(self) -> None:
        payload = json.loads(self._signed_webhook("py_never_existed")[0])
        payment_service.handle_webhook_event(self.db, payload)  # should not raise

    def test_paid_expiry_flips_status_and_role_after_end_date(self) -> None:
        subscription = self.user.subscription
        subscription.status = "active"
        subscription.plan_name = "paid_monthly"
        subscription.end_date = date.today() - timedelta(days=1)
        self.user.role = "paid_user"
        self.db.commit()

        changed = apply_paid_expiry(subscription)
        self.assertTrue(changed)
        self.assertEqual(subscription.status, "expired")
        self.assertEqual(self.user.role, "free_user")

    def test_manual_admin_activation_stays_indefinite(self) -> None:
        # Regression check: the existing admin-manual "active" grant must still
        # set end_date=None (indefinite) - only payment-driven activation should
        # set a real expiry.
        subscription = update_subscription_status(self.db, self.user.subscription, "active")
        self.assertIsNone(subscription.end_date)
        self.assertFalse(apply_paid_expiry(subscription))


if __name__ == "__main__":
    unittest.main()
