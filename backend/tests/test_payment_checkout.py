import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.payment import Payment
from app.models.user import User
from app.security import create_access_token
from app.services.subscription_service import build_trial_subscription


class FakeSettings:
    paystack_secret_key = "sk_test_checkout_synthetic_only"
    frontend_url = "http://127.0.0.1:55446"


class PaymentCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic checkout", email="checkout@example.com", password_hash="not-used",
                        role="free_user", is_active=True, referral_code="CHECKOUT")
            user.subscription = build_trial_subscription(user=user)
            db.add(user); db.commit(); self.user_id = user.id
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db: yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)
        self.headers = {"Authorization": "Bearer "+create_access_token(user_id=self.user_id)}
        self.settings = patch("app.services.payment_service.get_settings", return_value=FakeSettings())
        self.settings.start()

    def tearDown(self):
        self.settings.stop(); self.client.close(); app.dependency_overrides.clear(); self.engine.dispose()

    def initiate(self, mutate=lambda body: body, *, plan="monthly", http_status=200):
        self.observed = {}
        def provider(session, method, url, **kwargs):
            self.observed = {"url": url, "method": method, "trust_env": session.trust_env, **kwargs}
            body = {"status": True, "data": {"authorization_url": "https://checkout.paystack.com/synthetic-only",
                     "reference": kwargs["json"]["reference"], "access_code": "synthetic-only"}}
            response = requests.Response(); response.status_code = http_status
            response._content = json.dumps(mutate(body)).encode()
            return response
        with patch("requests.Session.request", autospec=True, side_effect=provider):
            return self.client.post("/payments/initiate", json={"plan": plan}, headers=self.headers)

    def test_valid_both_plans_use_recorded_prices_ngn_and_safe_transport(self):
        for plan, kobo in (("monthly", 250000), ("seasonal", 600000)):
            with self.subTest(plan=plan):
                response = self.initiate(plan=plan)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["authorization_url"], "https://checkout.paystack.com/synthetic-only")
                self.assertEqual(self.observed["url"], "https://api.paystack.co/transaction/initialize")
                self.assertEqual(self.observed["json"]["amount"], kobo)
                self.assertEqual(self.observed["json"].get("currency"), "NGN")
                self.assertFalse(self.observed["trust_env"])
                self.assertFalse(self.observed.get("allow_redirects", True))
                self.assertEqual(self.observed["timeout"], (3, 15))
                with Session(self.engine) as db:
                    payment = db.scalar(select(Payment).where(Payment.reference == response.json()["reference"]))
                    self.assertEqual(payment.plan, plan)
                    self.assertEqual(payment.amount*100, kobo)
                    self.assertEqual(payment.status, "pending")
                    self.assertEqual(db.get(User,self.user_id).subscription.status,"trial")

    def test_malformed_shapes_and_nonboolean_success_are_controlled_failures(self):
        for body in (None, [], "ok", {"status": "true", "data": {}}, {"status": 1, "data": {}},
                     {"status": True, "data": []}, {"status": True, "data": "bad"}):
            with self.subTest(body=body):
                self.assertEqual(self.initiate(lambda _: body).status_code, 502)
        with Session(self.engine) as db:
            self.assertTrue(all(item.status == "failed" for item in db.scalars(select(Payment))))
            self.assertEqual(db.get(User,self.user_id).subscription.status,"trial")

    def test_unsafe_checkout_links_never_reach_browser(self):
        for url in ("javascript:alert(1)", "http://checkout.paystack.com/synthetic", "https://example.invalid/synthetic",
                    "https://checkout.paystack.com.evil.invalid/synthetic", "https://checkout.paystack.com@evil.invalid/synthetic",
                    "https://user:password@checkout.paystack.com/synthetic", "https://checkout.paystack.com:444/synthetic",
                    "https://checkout.paystack.com/\r\nheader", "https://checkout.paystack.com\\@evil.invalid/synthetic",
                    "https://checkout.paystack.com/", 123, "x"*2049):
            with self.subTest(url=url):
                def mutate(body): body["data"]["authorization_url"] = url; return body
                self.assertEqual(self.initiate(mutate).status_code, 502)

    def test_mismatched_or_missing_reference_is_rejected(self):
        for value in (None, "py_other_purchase", 123):
            with self.subTest(reference=value):
                def mutate(body): body["data"]["reference"] = value; return body
                self.assertEqual(self.initiate(mutate).status_code, 502)

    def test_provider_redirects_and_failures_never_produce_checkout(self):
        for http_status in (302, 307, 400, 500):
            with self.subTest(http_status=http_status):
                self.assertEqual(self.initiate(http_status=http_status).status_code, 502)

    def test_provider_timeout_preserves_failed_purchase_and_never_grants_access(self):
        with patch("requests.Session.request", side_effect=requests.Timeout("synthetic provider timeout")):
            self.assertEqual(self.client.post("/payments/initiate", json={"plan":"monthly"}, headers=self.headers).status_code, 502)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(Payment)).status,"failed")
            self.assertEqual(db.get(User,self.user_id).subscription.status,"trial")

    def test_unauthenticated_or_invalid_plan_never_contacts_provider(self):
        with patch("requests.Session.request") as sender:
            self.assertEqual(self.client.post("/payments/initiate",json={"plan":"monthly"}).status_code,401)
            self.assertEqual(self.client.post("/payments/initiate",json={"plan":"yearly"},headers=self.headers).status_code,422)
            sender.assert_not_called()
