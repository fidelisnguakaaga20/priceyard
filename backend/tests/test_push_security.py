import base64
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from pydantic import ValidationError
from fastapi import HTTPException
from requests import Response
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate, validate_push_endpoint
from app.services import push_service


class PushSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(full_name="Synthetic push", email="push@example.com", password_hash="synthetic-unused-hash",
                         role="free_user", is_active=True, referral_code="PUSH0001")
        self.db.add(self.user)
        self.db.commit()
        raw = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
        self.keys = {"p256dh": encode(raw), "auth": encode(bytes(range(16)))}

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_only_explicit_https_push_hosts_are_accepted(self) -> None:
        valid = ["https://fcm.googleapis.com/fcm/send/synthetic", "https://updates.push.services.mozilla.com/wpush/v2/synthetic",
                 "https://web.push.apple.com/synthetic", "https://example.wns.windows.com/synthetic"]
        for endpoint in valid:
            self.assertEqual(validate_push_endpoint(endpoint), endpoint)
        invalid = ["http://fcm.googleapis.com/synthetic", "https://127.0.0.1/synthetic", "https://169.254.169.254/synthetic",
                   "https://fcm.googleapis.com.untrusted.invalid/synthetic", "https://user:pass@fcm.googleapis.com/synthetic",
                   "https://fcm.googleapis.com:8443/synthetic", "https://fcm.googleapis.com/synthetic#fragment",
                   "https://fcm.googleapis.com\n/synthetic", "https://fcm.googleapis.com/"]
        for endpoint in invalid:
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                validate_push_endpoint(endpoint)

    def test_invalid_keys_are_rejected_before_storage(self) -> None:
        payload = {"endpoint": "https://fcm.googleapis.com/synthetic", "keys": self.keys}
        self.assertIsNotNone(PushSubscriptionCreate(**payload))
        for key, value in (("auth", "YQ"), ("p256dh", "a" * 87)):
            invalid = {**self.keys, key: value}
            with self.assertRaises(ValidationError):
                PushSubscriptionCreate(endpoint=payload["endpoint"], keys=invalid)

    def test_private_and_mixed_dns_answers_are_rejected(self) -> None:
        for addresses in (["127.0.0.1"], ["169.254.169.254"], ["::1"], ["93.184.216.34", "10.0.0.1"]):
            results = [(2, 1, 6, "", (address, 443)) for address in addresses]
            with patch.object(push_service.socket, "getaddrinfo", return_value=results):
                with self.assertRaises(ValueError):
                    push_service.public_push_addresses("fcm.googleapis.com")

    def test_transport_disables_redirects_proxies_and_pins_checked_address(self) -> None:
        response = Response()
        response.status_code = 307
        with push_service.SafePushSession() as session:
            with patch.object(push_service, "public_push_addresses", return_value=["93.184.216.34"]), \
                 patch("requests.Session.request", return_value=response) as request:
                result = session.post("https://fcm.googleapis.com/synthetic", data=b"synthetic")
            self.assertEqual(result.status_code, 307)
            self.assertFalse(session.trust_env)
            self.assertFalse(request.call_args.kwargs["allow_redirects"])
            self.assertEqual(request.call_args.kwargs["timeout"], (3.05, 10))
            self.assertEqual(request.call_args.kwargs["proxies"], {})
            connection_class = session.get_adapter("https://fcm.googleapis.com/").poolmanager.pool_classes_by_scheme["https"].ConnectionCls
            connection = connection_class("fcm.googleapis.com", port=443, timeout=3)
            with patch.object(push_service, "create_connection", return_value=object()) as connect:
                connection._new_conn()
            self.assertEqual(connect.call_args.args[0], ("93.184.216.34", 443))
            self.assertEqual(connection.host, "fcm.googleapis.com")

    def test_unsafe_stored_endpoint_never_reaches_transport(self) -> None:
        self.db.add(PushSubscription(user_id=self.user.id, endpoint="https://127.0.0.1/private", **self.keys))
        self.db.commit()
        settings = SimpleNamespace(vapid_public_key="synthetic", vapid_private_key="synthetic", vapid_claim_email="push@example.com")
        with patch.object(push_service, "get_settings", return_value=settings), patch.object(push_service, "webpush") as send:
            with self.assertRaises(RuntimeError):
                push_service.send_push_to_user(self.db, self.user.id, title="Synthetic", body="Public price", url="http://127.0.0.1/prices")
            send.assert_not_called()

    def test_device_quota_and_owner_scoped_unsubscribe(self) -> None:
        for number in range(push_service.MAX_PUSH_DEVICES):
            push_service.save_subscription(self.db, self.user, PushSubscriptionCreate(endpoint=f"https://fcm.googleapis.com/synthetic-{number}", keys=self.keys))
        with self.assertRaises(HTTPException) as caught:
            push_service.save_subscription(self.db, self.user, PushSubscriptionCreate(endpoint="https://fcm.googleapis.com/overflow", keys=self.keys))
        self.assertEqual(caught.exception.status_code, 409)
        other = User(full_name="Other synthetic", email="other-push@example.com", password_hash="synthetic-unused-hash", role="free_user", is_active=True, referral_code="PUSH0002")
        self.db.add(other)
        self.db.flush()
        push_service.remove_subscription(self.db, other, "https://fcm.googleapis.com/synthetic-0")
        self.assertEqual(len(self.db.scalars(select(PushSubscription)).all()), push_service.MAX_PUSH_DEVICES)


if __name__ == "__main__":
    unittest.main()
