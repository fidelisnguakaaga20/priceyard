from datetime import datetime, timedelta, timezone
import hashlib
from unittest.mock import patch
import unittest

from fastapi.testclient import TestClient
import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, get_db
import app.models
from app.main import app
from app.models.password_reset_token import PasswordResetToken
from app.models.revoked_access_token import RevokedAccessToken
from app.models.user import User
from app.security import create_access_token
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password, verify_password


class LoginRevocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("OldPassword1")

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic user", email="security@example.com", password_hash=self.password_hash, role="free_user", is_active=True, referral_code="SECURITY")
            user.subscription = build_trial_subscription(user=user)
            admin = User(full_name="Synthetic admin", email="security-admin@example.com", password_hash=self.password_hash, role="admin", is_active=True, referral_code="SECADMIN")
            db.add_all([user, admin])
            db.commit()
            self.user_id, self.admin_id = user.id, admin.id
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)
        self.token = create_access_token(user_id=self.user_id)
        self.headers = {"Authorization": "Bearer " + self.token}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def reset_link(self):
        raw = "synthetic-only-reset-link-" + "x" * 32
        with Session(self.engine) as db:
            db.add(PasswordResetToken(user_id=self.user_id, token_hash=hashlib.sha256(raw.encode()).hexdigest(), expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)))
            db.commit()
        return raw

    def legacy_token(self, **changes):
        now = datetime.now(timezone.utc)
        payload = {"sub": str(self.user_id), "iat": now, "exp": now+timedelta(days=90)}
        payload.update(changes)
        return jwt.encode(payload, get_settings().jwt_secret, algorithm=get_settings().jwt_algorithm)

    def test_logout_revokes_only_this_token_and_is_idempotent(self):
        other = create_access_token(user_id=self.user_id)
        self.assertNotEqual(other, self.token)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers).status_code, 200)
        self.assertEqual(self.client.post("/auth/logout", headers=self.headers).status_code, 204)
        self.assertEqual(self.client.post("/auth/logout", headers=self.headers).status_code, 204)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers).status_code, 401)
        self.assertEqual(self.client.get("/auth/me", headers={"Authorization": "Bearer "+other}).status_code, 200)
        with Session(self.engine) as db:
            stored = db.scalar(select(RevokedAccessToken))
            self.assertEqual(stored.token_hash, hashlib.sha256(self.token.encode()).hexdigest())
            self.assertNotEqual(stored.token_hash, self.token)

    def test_legacy_login_preserved_until_password_reset_revokes_all(self):
        legacy = self.legacy_token()
        self.assertEqual(self.client.get("/auth/me", headers={"Authorization": "Bearer "+legacy}).status_code, 200)
        link = self.reset_link()
        response = self.client.post("/auth/reset-password", json={"token": link, "new_password": "NewPassword1"})
        self.assertEqual(response.status_code, 200, response.text)
        for token in (legacy, self.token):
            self.assertEqual(self.client.get("/auth/me", headers={"Authorization": "Bearer "+token}).status_code, 401)
        login = self.client.post("/auth/login", json={"email": "security@example.com", "password": "NewPassword1"})
        self.assertEqual(login.status_code, 200, login.text)
        profile = self.client.get("/auth/me", headers={"Authorization": "Bearer "+login.json()["access_token"]})
        self.assertEqual(profile.status_code, 200)
        self.assertNotIn("auth_version", profile.json())
        with Session(self.engine) as db:
            self.assertEqual(db.get(User, self.user_id).auth_version, 1)

    def test_reset_link_single_use_and_rejected_retry_has_no_effect(self):
        link = self.reset_link()
        self.assertEqual(self.client.post("/auth/reset-password", json={"token": link, "new_password": "NewPassword1"}).status_code, 200)
        self.assertEqual(self.client.post("/auth/reset-password", json={"token": link, "new_password": "DifferentPassword1"}).status_code, 400)
        with Session(self.engine) as db:
            user = db.get(User, self.user_id)
            self.assertEqual(user.auth_version, 1)
            self.assertTrue(verify_password("NewPassword1", user.password_hash))

    def test_failed_reset_commit_rolls_back_claim_password_and_version(self):
        link = self.reset_link()
        with patch.object(Session, "commit", side_effect=RuntimeError("synthetic commit failure")):
            response = self.client.post("/auth/reset-password", json={"token": link, "new_password": "NewPassword1"})
        self.assertEqual(response.status_code, 500)
        with Session(self.engine) as db:
            self.assertEqual(db.get(User, self.user_id).auth_version, 0)
            self.assertTrue(verify_password("OldPassword1", db.get(User, self.user_id).password_hash))
            self.assertIsNone(db.scalar(select(PasswordResetToken)).used_at)

    def test_disabling_then_reenabling_does_not_restore_old_login(self):
        admin_headers = {"Authorization": "Bearer "+create_access_token(user_id=self.admin_id)}
        for enabled in (False, True):
            response = self.client.patch(f"/users/{self.user_id}", headers=admin_headers, json={"is_active": enabled})
            self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers).status_code, 401)
        with Session(self.engine) as db:
            self.assertTrue(db.get(User, self.user_id).is_active)
            self.assertEqual(db.get(User, self.user_id).auth_version, 1)

    def test_invalid_version_and_unauthenticated_logout_rejected(self):
        for version in (True, "0", -1):
            token = self.legacy_token(auth_version=version)
            self.assertEqual(self.client.get("/auth/me", headers={"Authorization": "Bearer "+token}).status_code, 401)
        self.assertEqual(self.client.post("/auth/logout").status_code, 401)
