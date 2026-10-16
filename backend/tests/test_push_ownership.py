import base64
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.security import create_access_token


def encoded(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


class PushOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            self.users = []
            for index in range(2):
                user = User(full_name="Synthetic device user", email=f"device{index}@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code=f"DEVICE{index}")
                db.add(user);db.flush();self.users.append(user.id)
            db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions
        self.client=TestClient(app,raise_server_exceptions=False)
        self.headers=[{"Authorization":"Bearer "+create_access_token(user_id=user_id)} for user_id in self.users]
        public=ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
        self.payload={"endpoint":"https://fcm.googleapis.com/fcm/send/synthetic-shared-device","keys":{"p256dh":encoded(public),"auth":encoded(bytes(range(16)))}}

    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def save(self,index,payload=None):
        return self.client.post("/push/subscribe",json=payload or self.payload,headers=self.headers[index])

    def owned(self,index):
        return self.client.get("/push/subscribed",params={"endpoint":self.payload["endpoint"]},headers=self.headers[index]).json()["subscribed"]

    def test_endpoint_alone_does_not_allow_another_account_to_take_device(self):
        self.assertEqual(self.save(0).status_code,204)
        changed={**self.payload,"keys":{**self.payload["keys"],"auth":encoded(bytes(16))}}
        self.assertEqual(self.save(1,changed).status_code,409)
        self.assertTrue(self.owned(0));self.assertFalse(self.owned(1))
        with Session(self.engine) as db:
            row=db.scalar(select(PushSubscription))
            self.assertEqual(row.auth,self.payload["keys"]["auth"])

    def test_legitimate_same_browser_handoff_preserves_existing_behavior(self):
        self.assertEqual(self.save(0).status_code,204)
        # Padding is a representation difference, not different device secrets.
        padded={**self.payload,"keys":{field:value+"="*(-len(value)%4) for field,value in self.payload["keys"].items()}}
        self.assertEqual(self.save(1,padded).status_code,204)
        self.assertFalse(self.owned(0));self.assertTrue(self.owned(1))
        with Session(self.engine) as db:self.assertEqual(len(db.scalars(select(PushSubscription)).all()),1)

    def test_current_owner_can_refresh_keys_but_old_secret_cannot_reclaim(self):
        self.assertEqual(self.save(0).status_code,204)
        changed={**self.payload,"keys":{**self.payload["keys"],"auth":encoded(bytes(16))}}
        self.assertEqual(self.save(0,changed).status_code,204)
        self.assertEqual(self.save(1).status_code,409)
        self.assertTrue(self.owned(0));self.assertFalse(self.owned(1))

    def test_other_user_cannot_unsubscribe_owner_and_owner_cleanup_is_idempotent(self):
        self.assertEqual(self.save(0).status_code,204)
        for index in (1,0,0):
            self.assertEqual(self.client.post("/push/unsubscribe",json={"endpoint":self.payload["endpoint"]},headers=self.headers[index]).status_code,204)
            self.assertEqual(self.owned(0),index==1)

    def test_invalid_legacy_keys_are_preserved_and_cannot_be_claimed(self):
        with Session(self.engine) as db:
            db.add(PushSubscription(user_id=self.users[0],endpoint=self.payload["endpoint"],p256dh="legacy-invalid",auth="legacy-invalid"));db.commit()
        self.assertEqual(self.save(1).status_code,409)
        with Session(self.engine) as db:
            row=db.scalar(select(PushSubscription));self.assertEqual(row.user_id,self.users[0]);self.assertEqual(row.auth,"legacy-invalid")
