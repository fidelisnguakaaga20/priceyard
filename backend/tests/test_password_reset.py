import os
from urllib.parse import parse_qs, urlparse
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

os.environ.setdefault("FRONTEND_URL", "https://priceyard.onrender.com")

from app.database import Base
import app.models  # noqa: F401
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.services import password_reset_service
from app.services.auth_service import authenticate_user
from app.utils.password import hash_password


class PasswordResetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            full_name="Reset Test",
            email="reset@example.com",
            password_hash=hash_password("OldPassword1"),
            role="free_user",
            is_active=True,
            referral_code="RESETTEST",
        )
        self.db.add(self.user)
        self.db.commit()
        self.sent: dict[str, str] = {}
        self.original_sender = password_reset_service.send_password_reset_email
        password_reset_service.send_password_reset_email = (
            lambda *, recipient, reset_url: self.sent.update(recipient=recipient, reset_url=reset_url)
        )

    def tearDown(self) -> None:
        password_reset_service.send_password_reset_email = self.original_sender
        self.db.close()
        self.engine.dispose()

    def test_request_does_not_reveal_account_and_stores_only_hash(self) -> None:
        known = password_reset_service.request_password_reset(self.db, email=self.user.email)
        unknown = password_reset_service.request_password_reset(self.db, email="missing@example.com")
        self.assertEqual(known, unknown)
        raw_token = parse_qs(urlparse(self.sent["reset_url"]).query)["token"][0]
        stored = self.db.scalar(select(PasswordResetToken))
        self.assertIsNotNone(stored)
        self.assertNotEqual(stored.token_hash, raw_token)
        self.assertEqual(len(stored.token_hash), 64)

    def test_token_is_single_use_and_new_password_authenticates(self) -> None:
        password_reset_service.request_password_reset(self.db, email=self.user.email)
        token = parse_qs(urlparse(self.sent["reset_url"]).query)["token"][0]
        password_reset_service.reset_password(self.db, token=token, new_password="NewPassword1")
        self.assertEqual(authenticate_user(self.db, email=self.user.email, password="NewPassword1").id, self.user.id)
        with self.assertRaises(HTTPException) as context:
            password_reset_service.reset_password(self.db, token=token, new_password="AnotherPassword1")
        self.assertEqual(context.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
