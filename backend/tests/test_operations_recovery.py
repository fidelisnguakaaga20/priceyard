"""Synthetic-only tests for the narrow operational trigger and GitHub identity boundary."""
import json
import time
import unittest
from unittest.mock import MagicMock, patch

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.main import app
from app.models.payment import Payment
from app.routes import operations_routes as route
from app.services import operations_auth_service as authentication
from test_payment_reconciliation import provider_patches, seed_reconciliation


PATH = "/internal/operations/recover-payments"


class OperationsRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_key = cls.private_key.public_key()

    def setUp(self):
        self.enabled = patch.object(get_settings(), "ops_recovery_enabled", True)
        self.enabled.start()
        self.addCleanup(self.enabled.stop)
        self.original_keys = authentication._jwks_keys
        self.original_expiry = authentication._jwks_expires
        authentication._jwks_keys = {"synthetic-oidc-key": self.public_key}
        authentication._jwks_expires = time.monotonic() + 300
        self.addCleanup(self.restore_cache)
        self.client = TestClient(app, base_url="https://testserver", raise_server_exceptions=False)
        self.addCleanup(self.client.close)

    def restore_cache(self):
        authentication._jwks_keys = self.original_keys
        authentication._jwks_expires = self.original_expiry

    def token(self, *, remove=(), headers=None, **changes):
        now = int(time.time())
        claims = {**authentication.EXPECTED_CLAIMS, "iss": authentication.ISSUER,
                  "sub": authentication.EXPECTED_SUBJECTS[0],
                  "aud": authentication.AUDIENCE, "iat": now - 1, "nbf": now - 1,
                  "exp": now + 300, "jti": "synthetic-unique-identity", "event_name": "schedule"}
        claims.update(changes)
        for name in remove:
            claims.pop(name, None)
        return jwt.encode(claims, self.private_key, algorithm="RS256",
                          headers=headers or {"kid": "synthetic-oidc-key"})

    def send(self, payload=None, token=None, **kwargs):
        return self.client.post(PATH, json={} if payload is None else payload,
                                headers={"Authorization": "Bearer " + (token or self.token())}, **kwargs)

    def assert_private(self, response, status):
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(response.headers.get("cache-control"), "private, no-store")

    def test_disabled_and_cookie_only_requests_cannot_reach_database(self):
        with patch.object(route, "get_engine") as engine:
            with patch.object(get_settings(), "ops_recovery_enabled", False):
                self.assert_private(self.send(), 503)
            for headers in ({}, {"Cookie": "__Host-priceyard_session=synthetic-cookie"},
                            {"Authorization": "Bearer invalid"},
                            [("Authorization", "Bearer " + self.token()), ("Authorization", "Bearer invalid")]):
                self.assert_private(self.client.post(PATH, json={}, headers=headers), 401)
            engine.assert_not_called()
        self.assertNotIn(PATH, app.openapi()["paths"])

    def test_only_exact_repository_workflow_branch_and_runner_are_accepted(self):
        rejected = ({"repository": "attacker/priceyard"}, {"repository_id": "wrong"},
                    {"repository_owner_id": "wrong"}, {"ref": "refs/heads/other"},
                    {"sub": "repo:fidelisnguakaaga20/priceyard:pull_request"},
                    {"workflow_ref": "fidelisnguakaaga20/priceyard/.github/workflows/other.yml@refs/heads/master"},
                    {"runner_environment": "self-hosted"}, {"event_name": "pull_request"},
                    {"aud": "https://untrusted.example.invalid"}, {"aud": [authentication.AUDIENCE]},
                    {"iss": "https://untrusted.example.invalid"}, {"exp": int(time.time()) - 10},
                    {"nbf": int(time.time()) + 300}, {"iat": str(int(time.time()) - 1)}, {"jti": ""})
        with patch.object(route, "get_engine") as engine:
            for claims in rejected:
                with self.subTest(claims=claims):
                    self.assert_private(self.send(token=self.token(**claims)), 401)
            for missing in ("exp", "iat", "nbf", "jti", "iss", "aud", "sub"):
                self.assert_private(self.send(token=self.token(remove=(missing,))), 401)
            engine.assert_not_called()

    def test_exact_immutable_repository_subject_is_also_accepted(self):
        complete = {"dry_run": False, "busy": False, "complete": True, "outcomes": [],
                    "ceiling_id": 0, "next_after_id": 0}
        with patch.object(route, "get_engine"), patch.object(route, "reconcile_payments", return_value=complete) as run:
            self.assert_private(self.send(token=self.token(sub=authentication.EXPECTED_SUBJECTS[1])), 200)
            run.assert_called_once()
            for subject in (authentication.EXPECTED_SUBJECTS[1].replace("220378766", "220378767"),
                            authentication.EXPECTED_SUBJECTS[1].replace("1333398422", "1333398423")):
                self.assert_private(self.send(token=self.token(sub=subject)), 401)
            self.assertEqual(run.call_count, 1)

    def test_bad_signature_or_algorithm_cannot_authenticate(self):
        signed = self.token()
        header, body, signature = signed.split(".")
        changed = ("A" if signature[0] != "A" else "B") + signature[1:]
        unsigned_algorithm = jwt.encode({"sub": "synthetic"}, "synthetic-only-not-a-real-key-" + "x" * 32,
                                        algorithm="HS256", headers={"kid": "synthetic-oidc-key"})
        with patch.object(route, "get_engine") as engine:
            for token in (header + "." + body + "." + changed, unsigned_algorithm):
                self.assert_private(self.send(token=token), 401)
            engine.assert_not_called()

    def test_jwks_is_cached_and_unknown_kids_cannot_force_network_refresh(self):
        authentication._jwks_expires = 0
        report = {"dry_run": False, "busy": False, "complete": True, "outcomes": [],
                  "ceiling_id": 0, "next_after_id": 0}
        with (patch.object(authentication, "_download_keys", return_value={"synthetic-oidc-key": self.public_key}) as download,
              patch.object(route, "get_engine"), patch.object(route, "reconcile_payments", return_value=report)):
            self.assert_private(self.send(), 200)
            self.assert_private(self.send(token=self.token(headers={"kid": "unknown-key"})), 401)
            self.assert_private(self.send(), 200)
            download.assert_called_once_with()

    def test_jwks_outage_is_sanitized_and_backed_off(self):
        authentication._jwks_expires = 0
        with (patch.object(authentication, "_download_keys", side_effect=RuntimeError("SYNTHETIC_PRIVATE_PROVIDER_DIAGNOSTIC")) as download,
              patch.object(route, "get_engine") as engine):
            for _ in range(2):
                response = self.send()
                self.assert_private(response, 503)
                self.assertNotIn("PRIVATE", response.text)
            download.assert_called_once_with()
            engine.assert_not_called()

    def test_jwks_transport_is_fixed_tls_bounded_and_redirects_are_rejected(self):
        key = jwt.algorithms.RSAAlgorithm.to_jwk(self.public_key, as_dict=True)
        key.update(kid="synthetic-oidc-key", alg="RS256", use="sig")
        response = MagicMock()
        response.__enter__.return_value = response
        response.status_code = 200
        response.headers = {}
        response.iter_content.return_value = [json.dumps({"keys": [key]}).encode()]
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.return_value = response
        with patch.object(authentication.requests, "Session", return_value=client):
            self.assertEqual(set(authentication._download_keys()), {"synthetic-oidc-key"})
            self.assertIs(client.trust_env, False)
            client.get.assert_called_once_with(authentication.JWKS_URL, timeout=(3, 5), verify=True,
                                                allow_redirects=False, stream=True)
            response.status_code = 302
            with self.assertRaises(ValueError):
                authentication._download_keys()
            response.status_code = 200
            response.iter_content.return_value = [b"x" * (authentication.MAX_JWKS_BYTES + 1)]
            with self.assertRaises(ValueError):
                authentication._download_keys()

    def test_malformed_or_oversized_input_never_invokes_recovery_or_echoes_body(self):
        auth = {"Authorization": "Bearer " + self.token(), "Content-Type": "application/json"}
        malformed = (b"not-json-private-value", b"[]", b"null", b'{"secret":"SYNTHETIC_PRIVATE"}',
                     b'{"checkpoint":false}', b'{"checkpoint":""}', b'{"checkpoint":null,"checkpoint":null}',
                     json.dumps({"checkpoint": "x" * 4097}).encode())
        with patch.object(route, "get_engine") as engine:
            for body in malformed:
                response = self.client.post(PATH, content=body, headers=auth)
                self.assert_private(response, 400)
                self.assertNotIn("PRIVATE", response.text)
            self.assert_private(self.client.post(PATH, content=b"x" * 8193, headers=auth), 413)
            self.assert_private(self.client.post(PATH, content="{}", headers={"Authorization": auth["Authorization"]}), 415)
            self.assert_private(self.client.post(PATH + "?unexpected=1", json={}, headers=auth), 400)
            engine.assert_not_called()

    def test_tampered_or_out_of_bounds_checkpoint_fails_before_database(self):
        values = ("forged", "\u2603", route._cipher().encrypt(b'{"version":1,"after_id":2,"ceiling_id":1}').decode(),
                  route._cipher().encrypt(b'{"version":true,"after_id":0,"ceiling_id":1}').decode(),
                  route._cipher().encrypt(b'{"version":1,"after_id":0,"ceiling_id":2147483648}').decode())
        with patch.object(route, "get_engine") as engine:
            for value in values:
                self.assert_private(self.send({"checkpoint": value}), 400)
            engine.assert_not_called()

    def test_real_bounded_sweep_resumes_without_exposing_payment_records(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        self.addCleanup(engine.dispose)
        kinds = tuple("unconfirmed" + str(index) for index in range(25)) + ("paid",)
        fixture = seed_reconciliation(engine, kinds)
        for kind in kinds[:-1]:
            fixture[kind]["evidence"]["status"] = "pending"
        observed = []
        with patch.object(route, "get_engine", return_value=engine), provider_patches(fixture, observed):
            first = self.send()
            self.assert_private(first, 200)
            value = first.json()
            self.assertEqual(value["processed"], 25)
            self.assertEqual(value["outcomes"]["unconfirmed"], 25)
            self.assertFalse(value["complete"])
            self.assertIsInstance(value["checkpoint"], str)
            for private in ("payment_id", "after_id", "ceiling_id", fixture["paid"]["evidence"]["reference"]):
                self.assertNotIn(private, first.text)
            self.assertEqual(route._decode_checkpoint(value["checkpoint"]), (25, 26))
            second = self.send({"checkpoint": value["checkpoint"]})
            self.assert_private(second, 200)
            self.assertEqual(second.json()["outcomes"]["confirmed"], 1)
            self.assertTrue(second.json()["complete"])
            self.assertIsNone(second.json()["checkpoint"])
        self.assertEqual(len(observed), 26)
        with Session(engine) as db:
            self.assertEqual(db.scalar(select(Payment).where(Payment.id == fixture["paid"]["payment_id"])).status, "success")

    def test_busy_worker_preserves_checkpoint_and_errors_still_return_resumable_state(self):
        checkpoint = route._cipher().encrypt(b'{"version":1,"after_id":4,"ceiling_id":9}').decode()
        busy = {"dry_run": False, "busy": True, "complete": False, "outcomes": [],
                "ceiling_id": 9, "next_after_id": 4}
        with patch.object(route, "get_engine") as engine, patch.object(route, "reconcile_payments", return_value=busy) as run:
            response = self.send({"checkpoint": checkpoint})
            self.assert_private(response, 200)
            self.assertEqual(response.json()["checkpoint"], checkpoint)
            run.assert_called_once_with(engine.return_value, apply=True, limit=25, after_id=4,
                                        ceiling_id=9, time_budget_seconds=45)
            busy.update(busy=False, outcomes=[{"payment_id": 5, "outcome": "error"}], next_after_id=5)
            failed = self.send({"checkpoint": checkpoint})
            self.assert_private(failed, 200)
            self.assertEqual(failed.json()["outcomes"]["error"], 1)
            self.assertEqual(route._decode_checkpoint(failed.json()["checkpoint"]), (5, 9))
            self.assertNotIn("payment_id", failed.text)

    def test_database_failure_and_unavailable_checkpoint_key_fail_safely(self):
        with patch.object(route, "get_engine", side_effect=RuntimeError("SYNTHETIC_PRIVATE_DATABASE_URL")):
            response = self.send()
            self.assert_private(response, 503)
            self.assertEqual(response.json(), {"detail": "Operational recovery could not complete"})
        with patch.object(get_settings(), "jwt_secret", "short"), patch.object(route, "get_engine") as engine:
            self.assert_private(self.send(), 503)
            engine.assert_not_called()
