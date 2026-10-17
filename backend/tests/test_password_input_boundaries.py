"""Existing bcrypt byte limit must not turn a valid reset link into HTTP 500."""
from datetime import datetime, timedelta, timezone
import hashlib
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.password_reset_token import PasswordResetToken
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password, verify_password


class PasswordInputBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_hash = hash_password("SyntheticOldPassword8!")

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.raw_token = "synthetic-password-boundary-token-0123456789"
        now = datetime.now(timezone.utc)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic password boundary", email="boundary@example.com",
                        password_hash=self.original_hash, role="paid_user", referral_code="PWBOUNDARY")
            db.add(user)
            db.flush()
            self.user_id = user.id
            db.add(Subscription(user_id=user.id, status="active", plan_name="paid_monthly",
                                start_date=now.date(), end_date=(now + timedelta(days=30)).date()))
            db.add(PasswordResetToken(user_id=user.id, token_hash=hashlib.sha256(self.raw_token.encode()).hexdigest(),
                                      expires_at=now + timedelta(minutes=20)))
            db.commit()

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return {model.__tablename__: db.execute(select(model.__table__)).all()
                    for model in (User, Subscription, PasswordResetToken)}

    def test_overlong_utf8_reset_is_422_without_consuming_link_or_paid_access(self):
        before = self.state()
        response = self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": "好" * 25})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Password is too long")
        self.assertEqual(self.state(), before)

    def test_same_link_accepts_exact_byte_boundary_after_rejected_attempt(self):
        self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": "好" * 25})
        before_subscription = self.state()["subscriptions"]
        response = self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": "好" * 24})
        self.assertEqual(response.status_code, 200)
        with Session(self.engine) as db:
            user = db.get(User, self.user_id)
            self.assertTrue(verify_password("好" * 24, user.password_hash))
            self.assertFalse(verify_password("好" * 25, user.password_hash))
            self.assertEqual(user.auth_version, 1)
            self.assertEqual(user.role, "paid_user")
        self.assertEqual(self.state()["subscriptions"], before_subscription)
        self.assertEqual(self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": "AnotherSynthetic8!"}).status_code, 400)

    def test_existing_minimum_characters_and_ascii_maximum_are_unchanged(self):
        for password in ("😀" * 4, "x" * 73):
            with self.subTest(characters=len(password)):
                self.assertEqual(self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": password}).status_code, 422)
        self.assertEqual(self.client.post("/auth/reset-password", json={"token": self.raw_token, "new_password": "x" * 72}).status_code, 200)

    def test_registration_and_login_keep_existing_byte_limit_behavior(self):
        response = self.client.post("/auth/register", json={"full_name": "Synthetic rejected registration", "email": "rejected-boundary@example.com", "password": "好" * 25})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post("/auth/login", json={"email": "boundary@example.com", "password": "好" * 25}).status_code, 401)
        with Session(self.engine) as db:
            self.assertEqual(len(db.scalars(select(User)).all()), 1)
