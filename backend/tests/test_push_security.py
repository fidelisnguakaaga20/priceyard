import base64
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate
from app.security import create_access_token
from app.services import push_service
from app.utils.push_validation import SafePushSession
import requests


def encoded(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


class PushSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        key = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        # Exactly 16 fabricated bytes, never production subscription material.
        cls.keys = {"p256dh": encoded(key), "auth": encoded(bytes(range(16)))}

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic push user", email="push@example.com", password_hash="not-used", role="free_user", is_active=True, referral_code="PUSHSEC")
            db.add(user);db.commit();self.user_id=user.id
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db: yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)
        self.headers = {"Authorization":"Bearer "+create_access_token(user_id=self.user_id)}

    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def payload(self, endpoint="https://fcm.googleapis.com/fcm/send/synthetic-only"):
        return {"endpoint":endpoint,"keys":dict(self.keys)}

    def test_recognized_browser_provider_endpoints_remain_supported(self):
        for endpoint in ("https://fcm.googleapis.com/fcm/send/synthetic-only", "https://fcm.googleapis.com/wp/synthetic-only", "https://updates.push.services.mozilla.com/wpush/v2/synthetic-only", "https://push.services.mozilla.com/wpush/synthetic-only", "https://web.push.apple.com/synthetic-only", "https://wns-test.notify.windows.com/?token=synthetic-only"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(PushSubscriptionCreate.model_validate(self.payload(endpoint)).endpoint,endpoint)

    def test_unsafe_or_oversized_destinations_are_rejected_before_storage(self):
        for endpoint in ("http://fcm.googleapis.com/fcm/send/fake", "https://127.0.0.1/internal", "https://[::1]/internal", "https://169.254.169.254/latest/meta-data", "https://10.0.0.1/internal", "https://example.invalid/push", "https://fcm.googleapis.com.evil.invalid/push", "https://evilnotify.windows.com/push", "https://user:synthetic-password@fcm.googleapis.com/push", "https://fcm.googleapis.com:444/push", "https://fcm.googleapis.com/push#fragment", "https://fcm.googleapis.com/\r\nheader", "https://fcm.googleapis.com\\@127.0.0.1/push", "https://fcm.googleapis.com/"+"x"*500):
            with self.subTest(endpoint=endpoint):
                response=self.client.post("/push/subscribe",json=self.payload(endpoint),headers=self.headers)
                self.assertEqual(response.status_code,422)
        with Session(self.engine) as db:self.assertEqual(db.scalars(select(PushSubscription)).all(),[])

    def test_malformed_encryption_keys_are_rejected(self):
        for field, values in {"p256dh":["invalid",encoded(b"\x04"+bytes(64)),"x"*301],"auth":["invalid",encoded(bytes(15)),encoded(bytes(17)),"x"*101]}.items():
            for value in values:
                payload=self.payload();payload["keys"][field]=value
                with self.subTest(field=field,value=value):
                    with self.assertRaises(ValidationError):PushSubscriptionCreate.model_validate(payload)

    def test_legacy_unsafe_rows_never_reach_sender_and_are_preserved(self):
        with Session(self.engine) as db:
            db.add(PushSubscription(user_id=self.user_id,endpoint="http://127.0.0.1/internal",**self.keys));db.commit()
            settings=SimpleNamespace(vapid_public_key="synthetic",vapid_private_key="synthetic",vapid_claim_email="synthetic@example.com")
            with patch.object(push_service,"get_settings",return_value=settings),patch.object(push_service,"webpush") as sender:
                self.assertEqual(push_service.send_push_to_user(db,self.user_id,title="Synthetic",body="Synthetic",url="/prices"),0)
                sender.assert_not_called()
            self.assertEqual(len(db.scalars(select(PushSubscription)).all()),1)

    def test_authenticated_valid_subscription_storage_still_works(self):
        self.assertEqual(self.client.post("/push/subscribe",json=self.payload()).status_code,401)
        self.assertEqual(self.client.post("/push/subscribe",json=self.payload(),headers=self.headers).status_code,204)
        self.assertEqual(self.client.get("/push/subscribed",params={"endpoint":self.payload()["endpoint"]},headers=self.headers).json(),{"subscribed":True})
        self.assertEqual(self.client.get("/push/subscribed",params={"endpoint":"x"*501},headers=self.headers).status_code,422)

    def test_delivery_transport_forces_tls_timeouts_and_no_redirects(self):
        response=requests.Response();response.status_code=201
        with SafePushSession() as transport,patch("requests.Session.request",return_value=response) as request:
            self.assertFalse(transport.trust_env)
            self.assertIs(transport.post(self.payload()["endpoint"],allow_redirects=True,verify=False,timeout=None),response)
            self.assertFalse(request.call_args.kwargs["allow_redirects"])
            self.assertTrue(request.call_args.kwargs["verify"])
            self.assertEqual(request.call_args.kwargs["timeout"],(3,7))
            self.assertEqual(request.call_args.kwargs["proxies"],{})
        response.status_code=302;response.headers["Location"]="http://127.0.0.1/private"
        with SafePushSession() as transport,patch("requests.Session.request",return_value=response) as request:
            with self.assertRaises(requests.RequestException):transport.post(self.payload()["endpoint"])
            request.assert_called_once()
        with SafePushSession() as transport,patch("requests.Session.request") as request:
            with self.assertRaises(ValueError):transport.post("https://example.invalid/push")
            request.assert_not_called()

    def test_valid_sender_uses_safe_transport_and_does_not_log_secret_errors(self):
        with Session(self.engine) as db:
            db.add(PushSubscription(user_id=self.user_id,endpoint=self.payload()["endpoint"],**self.keys));db.commit()
            settings=SimpleNamespace(vapid_public_key="synthetic",vapid_private_key="synthetic",vapid_claim_email="synthetic@example.com")
            with patch.object(push_service,"get_settings",return_value=settings),patch.object(push_service,"webpush") as sender:
                self.assertEqual(push_service.send_push_to_user(db,self.user_id,title="Synthetic",body="Synthetic",url="/prices"),1)
                self.assertIsInstance(sender.call_args.kwargs["requests_session"],SafePushSession)
                self.assertEqual(sender.call_args.kwargs["timeout"],7)
            with patch.object(push_service,"get_settings",return_value=settings),patch.object(push_service,"webpush",side_effect=RuntimeError("synthetic-private-auth-material")),self.assertLogs(push_service.logger,level="WARNING") as logs:
                self.assertEqual(push_service.send_push_to_user(db,self.user_id,title="Synthetic",body="Synthetic",url="/prices"),0)
                self.assertNotIn("synthetic-private-auth-material"," ".join(logs.output))
