from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import hmac
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.payment import Payment
from app.models.user import User
from app.services.subscription_service import build_trial_subscription


class FakeSettings:
    paystack_secret_key = "sk_test_synthetic_evidence_only"
    frontend_url = "http://127.0.0.1:55446"


class PaymentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic payer", email="evidence@example.com", password_hash="not-a-real-password", role="free_user", is_active=True, referral_code="EVIDENCE")
            user.subscription = build_trial_subscription(user=user, now=datetime.now(timezone.utc))
            db.add(user)
            db.flush()
            self.user_id = user.id
            db.add(Payment(user_id=user.id, reference="py_evidence_only", plan="monthly", amount=2500, currency="NGN", status="pending"))
            db.commit()
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.settings_patch = patch("app.services.payment_service.get_settings", return_value=FakeSettings())
        self.settings_patch.start()
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        self.settings_patch.stop()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def payload(self):
        return {"event": "charge.success", "data": {"reference": "py_evidence_only", "id": 123456, "amount": 250000, "currency": "NGN", "status": "success"}}

    def send(self, payload, signature=None):
        raw = json.dumps(payload).encode()
        if signature is None:
            signature = hmac.new(FakeSettings.paystack_secret_key.encode(), raw, hashlib.sha512).hexdigest()
        return self.client.post("/payments/webhook", content=raw, headers={"x-paystack-signature": signature, "Content-Type": "application/json"})

    def assert_not_credited(self):
        with Session(self.engine) as db:
            payment = db.scalar(select(Payment))
            self.assertEqual(payment.status, "pending")
            self.assertIsNone(payment.paystack_transaction_id)
            user = db.get(User, self.user_id)
            self.assertEqual(user.role, "free_user")
            self.assertEqual(user.subscription.status, "trial")

    def test_signed_wrong_or_incomplete_evidence_does_not_credit(self):
        cases = {"amount": [None, 0, -250000, 249999, 250001, 250000.0, "250000", True], "currency": [None, "USD", "ngn"], "status": [None, "pending", "failed"], "id": [None, False, 0, -1, "123456"]}
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    payload = self.payload()
                    payload["data"][field] = value
                    response = self.send(payload)
                    self.assertEqual(response.status_code, 422)
                    self.assert_not_credited()
        for field in ("amount", "currency", "status", "id"):
            with self.subTest(missing=field):
                payload = self.payload()
                del payload["data"][field]
                self.assertEqual(self.send(payload).status_code, 422)
                self.assert_not_credited()

    def test_malformed_signed_shapes_fail_without_server_error_or_credit(self):
        for payload in (None, [], 1, "charge.success", {"event": "charge.success", "data": []}, {"event": "charge.success", "data": "bad"}, {"event": "charge.success", "data": {"reference": ["py_evidence_only"]}}):
            with self.subTest(payload=payload):
                self.assertIn(self.send(payload).status_code, (400, 422))
                self.assert_not_credited()

    def test_valid_evidence_credits_original_record_once(self):
        payload = self.payload()
        self.assertEqual(self.send(payload).status_code, 200)
        with Session(self.engine) as db:
            payment = db.scalar(select(Payment))
            self.assertEqual(payment.status, "success")
            self.assertEqual(payment.paystack_transaction_id, "123456")
            self.assertEqual(payment.amount, Decimal("2500.00"))
            self.assertEqual(payment.currency, "NGN")
            self.assertEqual(payment.plan, "monthly")
            self.assertEqual(db.get(User, self.user_id).subscription.status, "active")
        self.assertEqual(self.send(deepcopy(payload)).status_code, 200)

    def test_unknown_reference_and_unrelated_events_stay_harmless(self):
        payload = self.payload()
        payload["data"]["reference"] = "py_unknown_synthetic_only"
        self.assertEqual(self.send(payload).status_code, 200)
        self.assertEqual(self.send({"event": "transfer.success", "data": {}}).status_code, 200)
        self.assert_not_credited()

    def test_invalid_signature_never_reaches_activation(self):
        for signature in ("invalid", "a" * 128, "x" * 128):
            self.assertEqual(self.send(self.payload(), signature=signature).status_code, 401)
            self.assert_not_credited()
