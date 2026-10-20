"""Local model of the proposed ordered Render rewrites, not edge certification.

The API target is an in-process ASGI application. No HTTP proxy, Render service,
provider, database server, migration or application configuration is modified.
"""
from datetime import timedelta
import hashlib
import hmac
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, JSONResponse

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app import models as _models
from app.models.audit_log import AuditLog
from app.models.payment import Payment
from app.models.user import User
from app.rate_limit import limiter
from app.security import create_access_token
from app.services.browser_session_service import SECURE_COOKIE
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password


FRONT = "https://priceyard.onrender.com"
BACK = "https://priceyard-api.onrender.com"


class LocalRewriteModel:
    """Fixed API destination first, original SPA fallback second.

    Calling the target directly deliberately avoids claiming anything about
    Render's edge forwarding, cookie handling, caching or deployment behavior.
    """

    def __init__(self, api, frontend=None):
        self.api = api
        self.frontend = frontend

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.api(scope, receive, send)
        path = scope["path"]
        if path.startswith("/api/"):
            forwarded = dict(scope)
            forwarded.update(path=path[4:], raw_path=scope.get("raw_path", path.encode())[4:],
                             root_path="", server=("priceyard-api.onrender.com", 443))
            forwarded["headers"] = [(key, value) for key, value in scope["headers"]
                                    if key.lower() != b"host"] + [(b"host", b"priceyard-api.onrender.com")]
            return await self.api(forwarded, receive, send)
        if self.frontend is not None:
            return await self.frontend(scope, receive, send)
        return await HTMLResponse("<!doctype html><title>Original React fallback fixture</title>")(scope, receive, send)


class RenderRoutingContractTests(unittest.TestCase):
    def test_local_rewrite_model_preserves_original_sessions_payments_and_direct_api(self):
        # One small in-memory database; guard.py rejects all real transports.
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        password = "SyntheticRouting8!"
        with Session(engine) as db:
            user = User(full_name="Synthetic routing tester", email="routing@example.com",
                        password_hash=hash_password(password), role="free_user", is_active=True,
                        referral_code="ROUTING")
            user.subscription = build_trial_subscription(user=user)
            other = User(full_name="Synthetic other routing tester", email="routing-other@example.com",
                         password_hash="unused-synthetic-only", role="free_user", is_active=True,
                         referral_code="ROUTINGOTHER")
            other.subscription = build_trial_subscription(user=other)
            db.add_all([user, other]); db.commit()
            user_id, other_id = user.id, other.id
            trial_end = user.subscription.trial_ends_at

        def sessions():
            with Session(engine, expire_on_commit=False) as db:
                yield db

        original_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = sessions
        settings = get_settings()
        patches = [patch.object(settings, "frontend_url", FRONT),
                   patch.object(settings, "cors_origins", FRONT),
                   patch.object(settings, "app_env", "staging"),
                   patch.object(settings, "paystack_secret_key", "sk_test_routing_synthetic_only"),
                   patch("app.services.payment_service.notify_admins")]
        for item in patches:
            item.start()
        limiter.reset()
        browser = TestClient(LocalRewriteModel(app), base_url=FRONT, raise_server_exceptions=False)
        direct = TestClient(app, base_url=BACK, raise_server_exceptions=False)
        try:
            with self.subTest(contract="method_body_query_status_multiple_cookies"):
                async def probe(scope, receive, send):
                    if scope['type'] == 'lifespan':
                        while True:
                            message = await receive()
                            if message['type'] == 'lifespan.startup':
                                await send({'type': 'lifespan.startup.complete'})
                            elif message['type'] == 'lifespan.shutdown':
                                await send({'type': 'lifespan.shutdown.complete'})
                                return
                    chunks = []
                    while True:
                        message = await receive(); chunks.append(message.get("body", b""))
                        if not message.get("more_body"):
                            break
                    response = JSONResponse({"path": scope["path"], "method": scope["method"],
                                             "query": scope["query_string"].decode(),
                                             "body": b"".join(chunks).decode()}, status_code=207,
                                            headers={"Cache-Control": "private, no-store"})
                    response.set_cookie("synthetic_one", "one", httponly=True, secure=True)
                    response.set_cookie("synthetic_two", "two", httponly=True, secure=True)
                    await response(scope, receive, send)
                with TestClient(LocalRewriteModel(probe), base_url=FRONT) as client:
                    response = client.post("/api/probe?one=a%20b&one=c", content=b"{\n  \"raw\": true\n}")
                    self.assertEqual(response.status_code, 207)
                    self.assertEqual(response.json(), {"path": "/probe", "method": "POST",
                                                      "query": "one=a%20b&one=c", "body": '{\n  "raw": true\n}'})
                    self.assertEqual(len(response.headers.get_list("set-cookie")), 2)
                    self.assertEqual(response.headers["cache-control"], "private, no-store")

            with self.subTest(contract="api_precedes_spa_and_never_selects_an_arbitrary_target"):
                for path in ("/login", "/history", "/payment/callback?reference=synthetic"):
                    self.assertIn("text/html", browser.get(path).headers["content-type"])
                response = browser.get("/api/not-a-real-route?target=https://untrusted.example.invalid")
                self.assertEqual(response.status_code, 404)
                self.assertIn("application/json", response.headers["content-type"])
                self.assertEqual(browser.get("/api/https://untrusted.example.invalid/health").status_code, 404)
                self.assertEqual(browser.get("/api/health?target=https://untrusted.example.invalid").json(),
                                 {"status": "healthy"})

            origin = {"Origin": FRONT}
            with self.subTest(contract="login_secure_cookie_reload_session_and_csrf"):
                response = browser.post("/api/auth/browser/login", json={"email": "routing@example.com",
                                        "password": password, "remember": True}, headers=origin)
                self.assertEqual(response.status_code, 200, response.text)
                metadata = response.json()
                self.assertEqual(set(metadata), {"session_id", "csrf_token"})
                token = browser.cookies.get(SECURE_COOKIE)
                self.assertTrue(token)
                cookie = response.headers["set-cookie"]
                for attribute in ("Secure", "HttpOnly", "SameSite=lax", "Path=/"):
                    self.assertIn(attribute, cookie)
                self.assertNotIn("Domain=", cookie)
                self.assertNotIn(token, response.text)
                self.assertEqual(browser.get("/dashboard").status_code, 200)
                response = browser.get("/api/auth/browser/session")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), metadata)
                self.assertEqual(response.headers["cache-control"], "private, no-store")
                csrf = {**origin, "X-PriceYard-CSRF": metadata["csrf_token"],
                        "X-PriceYard-Session": metadata["session_id"]}
                for headers in (origin, {**csrf, "X-PriceYard-CSRF": "wrong"},
                                {**csrf, "Origin": "https://untrusted.example.invalid"}):
                    self.assertEqual(browser.post("/api/auth/logout", headers=headers).status_code, 403)
                self.assertEqual(browser.get("/api/auth/me").status_code, 200)

            with self.subTest(contract="mocked_TEST_checkout_verification_signature_and_replay"):
                calls = []
                reference = None
                def provider(session, method, url, **kwargs):
                    calls.append((method.upper(), url, kwargs))
                    self.assertFalse(session.trust_env)
                    self.assertFalse(kwargs["allow_redirects"])
                    self.assertTrue(kwargs["verify"])
                    self.assertEqual(kwargs["headers"]["Authorization"], "Bearer sk_test_routing_synthetic_only")
                    if method.upper() == "POST":
                        self.assertEqual(url, "https://api.paystack.co/transaction/initialize")
                        body = kwargs["json"]
                        self.assertEqual((body["amount"], body["currency"], body["callback_url"]),
                                         (250000, "NGN", FRONT + "/payment/callback"))
                        value = {"status": True, "data": {"reference": body["reference"],
                                 "authorization_url": "https://checkout.paystack.com/synthetic-routing-only",
                                 "access_code": "synthetic-routing-only"}}
                    else:
                        self.assertEqual(url, "https://api.paystack.co/transaction/verify/" + reference)
                        value = {"status": True, "data": {"reference": reference, "id": 987654321,
                                 "amount": 250000, "currency": "NGN", "status": "pending"}}
                    response = requests.Response(); response.status_code = 200
                    response._content = json.dumps(value).encode()
                    return response
                with patch("requests.Session.request", autospec=True, side_effect=provider):
                    response = browser.post("/api/payments/initiate", json={"plan": "monthly"}, headers=csrf)
                    self.assertEqual(response.status_code, 200, response.text)
                    reference = response.json()["reference"]
                    response = browser.post(f"/api/payments/{reference}/verify", headers=csrf)
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(response.json()["status"], "pending")
                    self.assertEqual(len(calls), 2)
                    other = {"Authorization": "Bearer " + create_access_token(user_id=other_id)}
                    self.assertEqual(direct.post(f"/payments/{reference}/verify", headers=other).status_code, 404)
                    self.assertEqual(len(calls), 2)
                    raw = json.dumps({"event": "charge.success", "data": {"domain": "test", "reference": reference,
                                     "id": 987654321, "amount": 250000, "currency": "NGN", "status": "success"}},
                                     indent=2).encode()
                    signature = hmac.new(b"sk_test_routing_synthetic_only", raw, hashlib.sha512).hexdigest()
                    webhook_headers = {"Content-Type": "application/json", "x-paystack-signature": signature}
                    # A provider request has no browser cookie or CSRF header.
                    with TestClient(LocalRewriteModel(app), base_url=FRONT) as provider_client:
                        self.assertEqual(provider_client.post("/api/payments/webhook", content=raw + b" ",
                                         headers=webhook_headers).status_code, 401)
                        self.assertEqual(provider_client.post("/api/payments/webhook", content=raw,
                                         headers=webhook_headers).status_code, 200)
                    with Session(engine) as db:
                        paid_end = db.get(User, user_id).subscription.end_date
                        self.assertEqual(paid_end, trial_end.date() + timedelta(days=30))
                    # Existing direct webhook is retained; duplicate delivery must not add days.
                    self.assertEqual(direct.post("/payments/webhook", content=raw, headers=webhook_headers).status_code, 200)
                    self.assertEqual(browser.post(f"/api/payments/{reference}/verify", headers=csrf).status_code, 200)
                    self.assertEqual(len(calls), 2)
                with Session(engine) as db:
                    payment = db.scalar(select(Payment).where(Payment.reference == reference))
                    self.assertEqual((payment.status, payment.paystack_transaction_id), ("success", "987654321"))
                    self.assertEqual(db.get(User, user_id).subscription.end_date, paid_end)
                    self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action == "payment.success")).all()), 1)

            with self.subTest(contract="logout_cookie_deletion_revoked_replay_and_independent_bearer"):
                independent = create_access_token(user_id=user_id)
                self.assertEqual(browser.post("/api/auth/logout", headers=csrf).status_code, 204)
                self.assertIsNone(browser.cookies.get(SECURE_COOKIE))
                self.assertEqual(browser.get("/api/auth/browser/session").status_code, 401)
                self.assertEqual(direct.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code, 401)
                self.assertEqual(direct.get("/auth/me", headers={"Authorization": "Bearer " + independent}).status_code, 200)
        finally:
            browser.close(); direct.close()
            for item in reversed(patches):
                item.stop()
            if original_override is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = original_override
            limiter.reset(); engine.dispose()
