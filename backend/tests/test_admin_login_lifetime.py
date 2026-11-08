from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, get_db
import app.models
from app.main import app
from app.models.user import User
from app.security import create_access_token, decode_access_claims
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password


class AdminLoginLifetimeTests(unittest.TestCase):
    """Owner-approved audit item 12: admin logins last 7 days, users keep 90."""

    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("Password123")

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(
                full_name="Synthetic user",
                email="lifetime-user@example.com",
                password_hash=self.password_hash,
                role="free_user",
                is_active=True,
                referral_code="LIFEUSER",
            )
            user.subscription = build_trial_subscription(user=user)
            admin = User(
                full_name="Synthetic admin",
                email="lifetime-admin@example.com",
                password_hash=self.password_hash,
                role="admin",
                is_active=True,
                referral_code="LIFEADMN",
            )
            db.add_all([user, admin])
            db.commit()
            self.user_id, self.admin_id = user.id, admin.id

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def lifetime_days(self, token):
        claims = decode_access_claims(token)
        return (claims["exp"] - claims["iat"]) / 86400

    def old_token(self, user_id, *, days_ago, valid_for_days=90):
        issued = datetime.now(timezone.utc) - timedelta(days=days_ago)
        payload = {
            "sub": str(user_id),
            "iat": issued,
            "exp": issued + timedelta(days=valid_for_days),
            "auth_version": 0,
            "jti": "old",
        }
        settings = get_settings()
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def me(self, token):
        return self.client.get("/auth/me", headers={"Authorization": "Bearer " + token})

    def test_admin_login_lasts_seven_days(self):
        response = self.client.post(
            "/auth/login", json={"email": "lifetime-admin@example.com", "password": "Password123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(self.lifetime_days(response.json()["access_token"]), 7, places=2)

    def test_normal_user_login_still_lasts_ninety_days(self):
        response = self.client.post(
            "/auth/login", json={"email": "lifetime-user@example.com", "password": "Password123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(self.lifetime_days(response.json()["access_token"]), 90, places=2)

    def test_older_admin_login_is_refused_after_seven_days(self):
        self.assertEqual(self.me(self.old_token(self.admin_id, days_ago=6)).status_code, 200)
        self.assertEqual(self.me(self.old_token(self.admin_id, days_ago=8)).status_code, 401)

    def test_older_normal_user_login_is_unaffected(self):
        self.assertEqual(self.me(self.old_token(self.user_id, days_ago=30)).status_code, 200)

    def test_new_admin_token_works(self):
        token = create_access_token(user_id=self.admin_id, role="admin")
        self.assertEqual(self.me(token).status_code, 200)


if __name__ == "__main__":
    unittest.main()
