from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient
from google.auth import exceptions as google_errors
import jwt
import requests
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.subscription import Subscription
from app.models.user import User
from app.services.auth_service import authenticate_or_create_google_user


class GoogleAccountSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public = cls.key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        now = datetime.now(timezone.utc)
        self.claims = {"sub": "synthetic-google-subject", "email": "new-google@example.com", "email_verified": True,
                       "iss": "https://accounts.google.com", "aud": "synthetic-client", "iat": int(now.timestamp()), "exp": int((now+timedelta(minutes=5)).timestamp())}

    def tearDown(self):
        self.db.close(); app.dependency_overrides.clear(); self.engine.dispose()

    def counts(self):
        with Session(self.engine) as db:
            return (db.scalar(select(func.count()).select_from(User)), db.scalar(select(func.count()).select_from(Subscription)))

    def status(self, callable_):
        try:
            callable_()
        except HTTPException as exc:
            return exc.status_code
        return 200

    def seeded(self, *, google_id=None, active=True):
        user = User(full_name="Synthetic existing customer", email=self.claims["email"], password_hash="unchanged-password-hash", google_id=google_id,
                    role="admin", is_active=active, referral_code="GOOGLEFIX", auth_version=3)
        user.subscription = Subscription(status="active", plan_name="paid_monthly", end_date=datetime.now(timezone.utc).date()+timedelta(days=12))
        self.db.add(user); self.db.commit()
        return user

    def certs(self, session, method, url, **kwargs):
        self.assertEqual(method.upper(), "GET")
        self.assertEqual(url, "https://www.googleapis.com/oauth2/v1/certs")
        response = requests.Response(); response.status_code = 200
        response._content = json.dumps({"synthetic-key": self.public}).encode()
        return response

    def signed(self, **changes):
        return jwt.encode({**self.claims, **changes}, self.key, algorithm="RS256", headers={"kid": "synthetic-key"})

    def test_real_verifier_checks_signature_audience_issuer_and_expiry(self):
        bad_signature = jwt.encode(self.claims, rsa.generate_private_key(public_exponent=65537, key_size=2048), algorithm="RS256", headers={"kid":"synthetic-key"})
        invalid = [self.signed(aud="other-app"), self.signed(iss="https://untrusted.example.invalid"), self.signed(exp=self.claims["iat"]-120), bad_signature]
        with patch("requests.Session.request", autospec=True, side_effect=self.certs):
            for token in invalid:
                with self.subTest(token_kind=invalid.index(token)):
                    self.assertEqual(self.status(lambda: authenticate_or_create_google_user(self.db, token)), 401)
                    self.assertEqual(self.counts(), (0, 0))

    def test_valid_new_subject_keeps_original_fourteen_day_trial(self):
        with patch("requests.Session.request", autospec=True, side_effect=self.certs):
            user = authenticate_or_create_google_user(self.db, self.signed())
        self.assertEqual(user.role, "free_user"); self.assertEqual(user.auth_provider, "google")
        self.assertEqual(user.subscription.trial_ends_at-user.subscription.trial_started_at, timedelta(days=14))
        self.assertEqual(self.counts(), (1, 1))

    def test_transport_is_pinned_bounded_tls_and_ignores_environment_proxies(self):
        def provider(session, method, url, **kwargs):
            self.assertFalse(session.trust_env)
            self.assertEqual(kwargs.get("timeout"), (3, 10))
            self.assertIs(kwargs.get("verify"), True)
            self.assertIs(kwargs.get("allow_redirects"), False)
            return self.certs(session, method, url, **kwargs)
        with patch("requests.Session.request", autospec=True, side_effect=provider):
            authenticate_or_create_google_user(self.db, self.signed())

    def test_malformed_verified_claims_never_create_accounts(self):
        invalid = [None, [], "not a claim object"]
        invalid += [{**self.claims, "email_verified": value} for value in (False, "false", "true", 1, None)]
        invalid += [{**self.claims, "sub": value} for value in ({}, [], 123, " ", "x"*256)]
        invalid += [{**self.claims, "email": value} for value in ([], 123, "bad-address", " ")]
        for claims in invalid:
            with self.subTest(claim_type=type(claims).__name__), patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=claims):
                self.assertEqual(self.status(lambda: authenticate_or_create_google_user(self.db, "synthetic-token")), 401)
                self.assertEqual(self.counts(), (0, 0))

    def test_existing_subject_preserves_identity_access_and_password_after_email_change(self):
        user = self.seeded(google_id=self.claims["sub"])
        expected = (user.id, user.password_hash, user.role, user.subscription.end_date, user.auth_version, user.email)
        with patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value={**self.claims, "email":"changed-google@example.com"}):
            actual = authenticate_or_create_google_user(self.db, "synthetic-token")
        self.assertEqual((actual.id, actual.password_hash, actual.role, actual.subscription.end_date, actual.auth_version, actual.email), expected)
        self.assertEqual(self.counts(), (1, 1))

    def test_approved_same_email_rule_never_attaches_or_replaces_google_identity(self):
        for linked in (None, "different-google-owner"):
            if linked is None:
                user = self.seeded()
            else:
                user.google_id = linked; self.db.commit()
            before = (user.id, user.password_hash, user.google_id, user.role, user.subscription.end_date, user.auth_version)
            with self.subTest(linked=linked), patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=self.claims):
                self.assertEqual(self.status(lambda: authenticate_or_create_google_user(self.db, "synthetic-token")), 409)
                self.db.expire_all(); actual = self.db.get(User, user.id)
                self.assertEqual((actual.id, actual.password_hash, actual.google_id, actual.role, actual.subscription.end_date, actual.auth_version), before)
                self.assertEqual(self.counts(), (1, 1))

    def test_inactive_linked_user_remains_denied_without_changes(self):
        user = self.seeded(google_id=self.claims["sub"], active=False)
        with patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=self.claims):
            self.assertEqual(self.status(lambda: authenticate_or_create_google_user(self.db, "synthetic-token")), 403)
        self.assertFalse(user.is_active); self.assertEqual(user.google_id, self.claims["sub"])

    def test_transport_outages_are_controlled_and_create_no_user(self):
        for error in (google_errors.TransportError("synthetic-private-error"), requests.Timeout("synthetic-private-error")):
            with self.subTest(error=type(error).__name__), patch("app.services.auth_service.google_id_token.verify_oauth2_token", side_effect=error):
                with self.assertRaises(HTTPException) as failure:
                    authenticate_or_create_google_user(self.db, "synthetic-token")
                self.assertEqual(failure.exception.status_code, 503)
                self.assertNotIn("synthetic-private-error", failure.exception.detail)
                self.assertEqual(self.counts(), (0, 0))

    def test_success_does_not_require_a_post_commit_refresh(self):
        with patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=self.claims), patch.object(self.db, "refresh", side_effect=RuntimeError("synthetic post-commit outage")):
            user = authenticate_or_create_google_user(self.db, "synthetic-token")
        self.assertIsNotNone(user.id); self.assertEqual(self.counts(), (1, 1))

    def test_oversized_token_is_rejected_by_http_before_verification(self):
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db: yield db
        app.dependency_overrides[get_db] = sessions
        with TestClient(app, raise_server_exceptions=False) as client, patch("app.routes.auth_routes.authenticate_or_create_google_user") as authenticate:
            response = client.post("/auth/google", json={"id_token":"x"*16385})
            self.assertEqual(response.status_code, 422)
            authenticate.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))
