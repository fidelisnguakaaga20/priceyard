"""HTTP evidence validation and atomic activation; all provider traffic is fake."""
import hashlib
import hmac
import json
import unittest
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import AtomicSession, Base, get_db
from app.models.entitlement_grant import EntitlementGrant
from app.models.payment import Payment
from app.models.user import User
from app.routes.payment_routes import router
from app.services import payment_service
from app.services.subscription_service import build_trial_subscription, paid_cutoff
from app.transactions import install_transactions
from app.utils.permissions import get_current_user


class SyntheticProviderSettings:
    paystack_secret_key = "sk_test_synthetic_no_live_provider"


class PaymentApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        with Session(self.engine, expire_on_commit=False) as db:
            self.user = User(full_name="Synthetic payer", email="payer@fixture.test", password_hash="unused", role="free_user", email_verified=True, is_active=True, referral_code="HTTPFIXTURE")
            self.user.subscription = build_trial_subscription(user=self.user)
            db.add(self.user); db.flush()
            self.payment = Payment(user_id=self.user.id, reference="py_http_synthetic", plan="monthly", amount=2500,
                                   currency="NGN", status="pending", duration_days=30,
                                   expected_customer_email=self.user.email, provider_environment="test")
            db.add(self.payment); db.commit()
            self.original_cutoff = self.user.subscription.trial_ends_at
        self.current = self.user
        self.app = FastAPI()
        self.app.include_router(router)
        def request_db(request: Request):
            if not hasattr(request.state, "database_session"):
                request.state.database_session = AtomicSession(bind=self.engine, autoflush=False, expire_on_commit=False)
            return request.state.database_session
        self.app.dependency_overrides[get_db] = request_db
        self.app.dependency_overrides[get_current_user] = lambda: self.current
        install_transactions(self.app)
        self.client = TestClient(self.app, raise_server_exceptions=False)
        self.settings = patch.object(payment_service, "get_settings", return_value=SyntheticProviderSettings())
        self.settings.start()

    def tearDown(self):
        self.settings.stop(); self.client.close(); self.engine.dispose()

    def event(self, amount=250000):
        return {"event": "charge.success", "data": {"reference": self.payment.reference, "id": 12345,
                "amount": amount, "currency": "NGN", "status": "success", "domain": "test",
                "customer": {"email": self.user.email}, "metadata": {"priceyard_user_id": self.user.id}}}

    def signed_post(self, event=None, *, signature=None):
        raw = json.dumps(event or self.event()).encode()
        signature = signature or hmac.new(SyntheticProviderSettings.paystack_secret_key.encode(), raw, hashlib.sha512).hexdigest()
        return self.client.post("/payments/webhook", content=raw, headers={"x-paystack-signature": signature, "content-type": "application/json"})

    def test_signed_event_activates_once_and_status_reflects_committed_grant(self):
        self.assertEqual(self.signed_post().json()["outcome"], "applied")
        self.assertEqual(self.signed_post().json()["outcome"], "already_applied")
        status = self.client.get("/payments/status/" + self.payment.reference)
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.json()["access_applied"])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count(EntitlementGrant.id))), 1)

    def test_failure_after_activation_rolls_back_every_business_record_then_retries(self):
        with patch.object(payment_service, "create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            self.assertEqual(self.signed_post().status_code, 500)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count(EntitlementGrant.id))), 0)
            payment = db.get(Payment, self.payment.id)
            self.assertEqual(payment.status, "pending")
            self.assertFalse(payment.access_applied)
            self.assertIsNone(paid_cutoff(payment.user.subscription))
        self.assertEqual(self.signed_post().json()["outcome"], "applied")

    def test_bad_signature_or_amount_never_grants_access(self):
        self.assertEqual(self.signed_post(signature="a" * 128).status_code, 401)
        self.assertEqual(self.signed_post(self.event(amount=1)).json()["outcome"], "evidence_mismatch")
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count(EntitlementGrant.id))), 0)
            self.assertEqual(db.get(Payment, self.payment.id).reconciliation_error, "amount_mismatch")

    def test_other_account_cannot_read_payment_status(self):
        self.current = User(id=self.user.id + 1000, role="free_user")
        self.assertEqual(self.client.get("/payments/status/" + self.payment.reference).status_code, 404)
        self.current = User(id=self.user.id + 1000, role="admin")
        self.assertEqual(self.client.get("/payments/status/" + self.payment.reference).status_code, 200)

    def test_oversized_webhook_rejected_before_parsing(self):
        response = self.client.post("/payments/webhook", content=b" " * 32769)
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
