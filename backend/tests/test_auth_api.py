"""In-process HTTP auth/transaction tests with a new synthetic database."""
from datetime import timedelta
from unittest.mock import patch
import unittest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import AtomicSession, Base, get_db
import app.models  # noqa: F401
from app.models.auth_session import AuthSession
from app.models.user import User
from app.models.notification_job import NotificationJob
from app.models.email_verification_token import EmailVerificationToken
from app.rate_limit import limiter
from app.routes.auth_routes import router
from app.security import decode_access_claims
from app.transactions import install_transactions
from app.utils.permissions import optional_current_user


class AuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.app = FastAPI()
        self.app.state.limiter = limiter
        self.app.include_router(router)
        @self.app.get("/public-probe")
        def public_probe(user=Depends(optional_current_user)):
            return {"authenticated": user is not None}
        self.sessions = []
        def isolated_db(request):
            if not hasattr(request.state, "database_session"):
                request.state.database_session = AtomicSession(bind=self.engine, autoflush=False, expire_on_commit=False)
                self.sessions.append(request.state.database_session)
            return request.state.database_session
        # FastAPI must recognize Request as a request dependency, not a query.
        from fastapi import Request
        isolated_db.__annotations__["request"] = Request
        self.app.dependency_overrides[get_db] = isolated_db
        install_transactions(self.app)
        self.client = TestClient(self.app, raise_server_exceptions=False)
        self.email_patch = patch("app.services.email_service.send_email")
        self.alert_patch = patch("app.routes.auth_routes.notify_admins")
        self.email_sender = self.email_patch.start()
        self.alert_patch.start()
        # Rate-limit behavior has independent tests. This suite exercises the
        # same decorated handlers without sharing quotas across synthetic cases.
        self.original_enabled = limiter.enabled
        limiter.enabled = False

    def tearDown(self) -> None:
        limiter.enabled = self.original_enabled
        self.email_patch.stop()
        self.alert_patch.stop()
        self.client.close()
        self.engine.dispose()

    def register(self) -> None:
        response = self.client.post("/auth/register", json={"full_name": "Synthetic API member", "email": "api@example.com", "password": "ExistingPass8"})
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["email_verified"])
        self.assertNotIn("password_hash", response.json())
        self.email_sender.assert_not_called()
        self.assertIsNone(self.sessions[-1].get_transaction(), "HTTP transaction must finalize before returning the response")

    def login(self, *, remember: bool = True) -> dict:
        response = self.client.post("/auth/login", json={"email": "api@example.com", "password": "ExistingPass8", "remember_me": remember})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("refresh_token" in response.json())
        self.assertIsNone(self.sessions[-1].get_transaction(), "HTTP transaction must finalize before returning the response")
        return response.json()

    def test_register_login_refresh_logout_persist_across_requests(self) -> None:
        self.register()
        tokens = self.login()
        first_headers = {"Authorization": "Bearer " + tokens["access_token"]}
        self.assertEqual(self.client.get("/auth/me", headers=first_headers).status_code, 200)
        refreshed = self.client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        self.assertEqual(refreshed.status_code, 200)
        self.assertEqual(self.client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code, 401)
        headers = {"Authorization": "Bearer " + refreshed.json()["access_token"]}
        self.assertEqual(self.client.post("/auth/logout", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/auth/me", headers=headers).status_code, 401)
        self.assertEqual(self.client.post("/auth/refresh", json={"refresh_token": refreshed.json()["refresh_token"]}).status_code, 401)
        with Session(self.engine) as db:
            self.assertIsNotNone(db.scalar(select(AuthSession)).revoked_at)

    def test_failed_response_rolls_back_session_issuance(self) -> None:
        self.register()
        # Failure after INSERT but before HTTP response must not leave a usable
        # session. The real issue_session implementation runs before injection.
        from app.services.auth_session_service import issue_session
        def fail_after_issue(db, user, **kwargs):
            issue_session(db, user, **kwargs)
            raise RuntimeError("Synthetic response failure")
        with patch("app.routes.auth_routes.issue_session", side_effect=fail_after_issue):
            response = self.client.post("/auth/login", json={"email": "api@example.com", "password": "ExistingPass8"})
        self.assertEqual(response.status_code, 500)
        with Session(self.engine) as db:
            self.assertIsNone(db.scalar(select(AuthSession)))
            self.assertIsNotNone(db.scalar(select(User)))

    def test_nonremembered_session_is_bounded_to_one_day(self) -> None:
        self.register()
        tokens = self.login(remember=False)
        claims = decode_access_claims(tokens["access_token"])
        with Session(self.engine) as db:
            session = db.get(AuthSession, claims["sid"])
            self.assertEqual(session.expires_at - session.last_refreshed_at, timedelta(hours=24))

    def test_registration_failure_rolls_back_account_and_queued_proof(self) -> None:
        with patch("app.routes.auth_routes.notify_admins", side_effect=RuntimeError("Synthetic failure after queueing")):
            response = self.client.post("/auth/register", json={"full_name": "Synthetic API member", "email": "rollback@example.com", "password": "ExistingPass8"})
        self.assertEqual(response.status_code, 500)
        with Session(self.engine) as db:
            self.assertIsNone(db.scalar(select(User)))
            self.assertIsNone(db.scalar(select(EmailVerificationToken)))
            self.assertIsNone(db.scalar(select(NotificationJob)))
        self.email_sender.assert_not_called()

    def test_optional_auth_rejects_present_malformed_headers(self) -> None:
        self.assertEqual(self.client.get("/public-probe").status_code, 200)
        for header in ("Basic synthetic", "Bearer", ""):
            with self.subTest(header=header):
                self.assertEqual(self.client.get("/public-probe", headers={"Authorization": header}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
