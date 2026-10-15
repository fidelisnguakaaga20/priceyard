"""Synthetic regression cases; execute only through the isolated test runner."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
import unittest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.auth_session import AuthSession
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User
from app.models.notification_job import NotificationJob
from app.schemas.auth_schema import RegisterRequest, ResetPasswordRequest
from app.schemas.user_schema import AdminUserUpdate
from app.security import create_access_token, decode_access_claims
import app.security as token_security
from app.services import auth_service, email_verification_service, password_reset_service
from app.services.auth_session_service import issue_session, logout_all_sessions, logout_session, refresh_session, utc_aware
from app.services.subscription_service import build_trial_subscription
from app.services.user_service import update_user
from app.services.notification_service import delivery_payload, process_notifications
from app.utils.password import hash_password, verify_password
from app.utils.permissions import get_current_user, optional_current_user, user_has_full_access


class AuthSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        self.user = self.add_user("MEMBER01", "member@example.com")

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def add_user(self, code: str, email: str, *, role: str = "free_user", verified: bool | None = False) -> User:
        user = User(full_name="Synthetic member", email=email, password_hash=hash_password("ExistingPass8"),
                    role=role, is_active=True, referral_code=code, email_verified=verified)
        user.subscription = build_trial_subscription(user=user)
        self.db.add(user)
        self.db.flush()
        return user

    def credentials(self, token: str) -> HTTPAuthorizationCredentials:
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    def google_claims(self, **changes) -> dict:
        claims = {"iss": "https://accounts.google.com", "aud": "synthetic-google-client",
                  "sub": "synthetic-google-sub", "email": self.user.email, "email_verified": True}
        claims.update(changes)
        return claims

    def deliver_account_email(self) -> dict:
        sent = {}
        self.db.commit()
        process_notifications(self.db, senders={"email": lambda job: sent.update(recipient=job.recipient, **delivery_payload(job.payload))})
        return sent

    def google_mocks(self, claims: dict):
        return (
            patch.object(auth_service, "get_settings", return_value=SimpleNamespace(google_client_id="synthetic-google-client")),
            patch.object(auth_service.google_id_token, "verify_oauth2_token", return_value=claims),
        )

    def test_registration_keeps_trial_and_defers_referral_reward(self) -> None:
        prior_end = self.user.subscription.trial_ends_at
        created = auth_service.register_user(self.db, RegisterRequest(
            full_name="Synthetic referral", email="referred@example.com", password="ExistingPass8",
            referral_code=self.user.referral_code,
        ))
        self.assertFalse(created.email_verified)
        self.assertEqual(created.referred_by_id, self.user.id)
        self.assertEqual(created.subscription.trial_ends_at - created.subscription.trial_started_at, timedelta(days=14))
        self.assertEqual(self.user.subscription.trial_ends_at, prior_end)

    def test_google_email_collision_never_links_pre_registered_account(self) -> None:
        original_hash = self.user.password_hash
        settings, verifier = self.google_mocks(self.google_claims())
        with settings, verifier, self.assertRaises(HTTPException) as caught:
            auth_service.authenticate_or_create_google_user(self.db, "synthetic-id-token")
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIsNone(self.user.google_id)
        self.assertEqual(self.user.password_hash, original_hash)

    def test_google_claims_require_verified_issuer_audience_and_email(self) -> None:
        for changes in ({"iss": "https://untrusted.invalid"}, {"aud": "wrong-client"}, {"email_verified": "true"}, {"sub": ""}):
            with self.subTest(changes=changes):
                settings, verifier = self.google_mocks(self.google_claims(**changes))
                with settings, verifier, self.assertRaises(HTTPException) as caught:
                    auth_service.verify_google_claims("synthetic-id-token")
                self.assertEqual(caught.exception.status_code, 401)

    def test_new_google_account_has_verified_ownership_and_same_trial(self) -> None:
        settings, verifier = self.google_mocks(self.google_claims(email="google-new@example.com"))
        with settings, verifier:
            user = auth_service.authenticate_or_create_google_user(self.db, "synthetic-id-token")
        self.assertTrue(user.email_verified)
        self.assertEqual(user.google_id, "synthetic-google-sub")
        self.assertEqual(user.subscription.trial_ends_at - user.subscription.trial_started_at, timedelta(days=14))

    def test_existing_google_subject_proves_matching_email_without_merging(self) -> None:
        self.user.google_id = "synthetic-google-sub"
        self.db.flush()
        settings, verifier = self.google_mocks(self.google_claims())
        with settings, verifier:
            authenticated = auth_service.authenticate_or_create_google_user(self.db, "synthetic-id-token")
        self.assertEqual(authenticated.id, self.user.id)
        self.assertTrue(authenticated.email_verified)

    def test_weak_jwt_configuration_is_rejected(self) -> None:
        with patch.object(token_security, "get_settings", return_value=SimpleNamespace(jwt_secret="synthetic-short")):
            with self.assertRaises(RuntimeError):
                token_security._jwt_secret()

    def test_deliberate_google_link_requires_ownership_and_password(self) -> None:
        settings, verifier = self.google_mocks(self.google_claims())
        with settings, verifier:
            with self.assertRaises(HTTPException) as caught:
                auth_service.link_google_identity(self.db, self.user, token="synthetic-id-token", password="ExistingPass8")
            self.assertEqual(caught.exception.status_code, 403)
            self.user.email_verified = True
            self.db.flush()
            with self.assertRaises(HTTPException) as caught:
                auth_service.link_google_identity(self.db, self.user, token="synthetic-id-token", password="IncorrectPass8")
            self.assertEqual(caught.exception.status_code, 401)
            linked = auth_service.link_google_identity(self.db, self.user, token="synthetic-id-token", password="ExistingPass8")
        self.assertEqual(linked.google_id, "synthetic-google-sub")
        self.assertTrue(verify_password("ExistingPass8", linked.password_hash))

    def test_existing_legacy_password_is_not_locked_out(self) -> None:
        self.user.email_verified = None
        self.db.flush()
        self.assertEqual(auth_service.authenticate_user(self.db, email=self.user.email, password="ExistingPass8").id, self.user.id)

    def test_sessions_are_short_access_with_hashed_rotating_refresh(self) -> None:
        tokens = issue_session(self.db, self.user)
        claims = decode_access_claims(tokens.access_token)
        self.assertLessEqual(claims["exp"] - claims["iat"], 900)
        stored = self.db.get(AuthSession, claims["sid"])
        self.assertEqual(len(stored.refresh_token_hash), 64)
        self.assertNotEqual(stored.refresh_token_hash, tokens.refresh_token)
        renewed = refresh_session(self.db, refresh_token=tokens.refresh_token)
        self.assertNotEqual(renewed.refresh_token, tokens.refresh_token)
        with self.assertRaises(HTTPException):
            refresh_session(self.db, refresh_token=tokens.refresh_token)
        self.assertEqual(get_current_user(self.credentials(renewed.access_token), self.db).id, self.user.id)

    def test_logout_revokes_only_own_current_session(self) -> None:
        first = issue_session(self.db, self.user)
        second = issue_session(self.db, self.user)
        logout_session(self.db, user_id=self.user.id, session_id=decode_access_claims(first.access_token)["sid"])
        with self.assertRaises(HTTPException):
            get_current_user(self.credentials(first.access_token), self.db)
        self.assertEqual(get_current_user(self.credentials(second.access_token), self.db).id, self.user.id)
        logout_all_sessions(self.db, self.user)
        with self.assertRaises(HTTPException):
            refresh_session(self.db, refresh_token=second.refresh_token)

    def test_session_absolute_expiry_rejects_valid_access_and_refresh(self) -> None:
        tokens = issue_session(self.db, self.user)
        stored = self.db.get(AuthSession, decode_access_claims(tokens.access_token)["sid"])
        stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.flush()
        with self.assertRaises(HTTPException):
            get_current_user(self.credentials(tokens.access_token), self.db)
        with self.assertRaises(HTTPException):
            refresh_session(self.db, refresh_token=tokens.refresh_token)

    def test_password_reset_revokes_existing_sessions_and_proves_email(self) -> None:
        tokens = issue_session(self.db, self.user)
        password_reset_service.request_password_reset(self.db, email=self.user.email)
        sent = self.deliver_account_email()
        url = next(line for line in sent["body"].splitlines() if "/reset-password?" in line)
        raw = parse_qs(urlparse(url).query)["token"][0]
        password_reset_service.reset_password(self.db, token=raw, new_password="Replacement8")
        self.assertTrue(self.user.email_verified)
        self.assertTrue(verify_password("Replacement8", self.user.password_hash))
        with self.assertRaises(HTTPException):
            get_current_user(self.credentials(tokens.access_token), self.db)
        with self.assertRaises(HTTPException):
            refresh_session(self.db, refresh_token=tokens.refresh_token)
        with self.assertRaises(HTTPException):
            password_reset_service.reset_password(self.db, token=raw, new_password="Replacement9")

    def test_verification_is_generic_single_use_and_does_not_change_trial(self) -> None:
        original_trial = self.user.subscription.trial_ends_at
        known = email_verification_service.request_email_verification(self.db, email=self.user.email)
        unknown = email_verification_service.request_email_verification(self.db, email="not-registered@example.com")
        self.assertEqual(known, unknown)
        email_verification_service.request_email_verification(self.db, email=self.user.email)
        self.assertEqual(len(self.db.scalars(select(NotificationJob)).all()), 1)
        sent = self.deliver_account_email()
        url = next(line for line in sent["body"].splitlines() if "/verify-email?" in line)
        token = parse_qs(urlparse(url).query)["token"][0]
        stored = self.db.scalar(select(EmailVerificationToken))
        self.assertNotEqual(stored.token_hash, token)
        email_verification_service.verify_email(self.db, token=token)
        self.assertTrue(self.user.email_verified)
        self.assertEqual(utc_aware(self.user.subscription.trial_ends_at), utc_aware(original_trial))
        with self.assertRaises(HTTPException):
            email_verification_service.verify_email(self.db, token=token)

    def test_deactivate_and_reactivate_cannot_restore_old_sessions(self) -> None:
        tokens = issue_session(self.db, self.user)
        update_user(self.db, self.user, AdminUserUpdate(is_active=False))
        update_user(self.db, self.user, AdminUserUpdate(is_active=True))
        with self.assertRaises(HTTPException):
            get_current_user(self.credentials(tokens.access_token), self.db)
        with self.assertRaises(HTTPException):
            refresh_session(self.db, refresh_token=tokens.refresh_token)

    def test_last_admin_cannot_be_disabled_or_demoted(self) -> None:
        admin = self.add_user("ADMIN001", "admin@example.com", role="admin")
        for payload in (AdminUserUpdate(is_active=False), AdminUserUpdate(role="reporter")):
            with self.assertRaises(HTTPException) as caught:
                update_user(self.db, admin, payload)
            self.assertEqual(caught.exception.status_code, 409)
        self.assertTrue(admin.is_active)
        self.assertEqual(admin.role, "admin")

    def test_unknown_roles_and_legacy_tokens_never_authorize(self) -> None:
        legacy = create_access_token(user_id=self.user.id)
        with self.assertRaises(HTTPException):
            get_current_user(self.credentials(legacy), self.db)
        self.assertIsNone(optional_current_user(None, self.db))
        tokens = issue_session(self.db, self.user)
        self.user.role = "unrecognized"
        self.db.flush()
        with self.assertRaises(HTTPException) as caught:
            optional_current_user(self.credentials(tokens.access_token), self.db)
        self.assertEqual(caught.exception.status_code, 403)
        self.assertFalse(user_has_full_access(self.db, self.user))

    def test_password_byte_validation_does_not_silently_truncate(self) -> None:
        for schema, fields in (
            (RegisterRequest, {"full_name": "Synthetic", "email": "bytes@example.com", "password": "é" * 40}),
            (ResetPasswordRequest, {"token": "a" * 64, "new_password": "é" * 40}),
        ):
            with self.assertRaises(ValidationError):
                schema(**fields)


if __name__ == "__main__":
    unittest.main()
