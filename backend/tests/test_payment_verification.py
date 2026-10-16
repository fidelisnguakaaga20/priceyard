from copy import deepcopy
from datetime import timedelta
import json
import unittest
from unittest.mock import patch
import uuid

from fastapi.testclient import TestClient
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.payment import Payment
from app.models.user import User
from app.security import create_access_token
from app.services import payment_service
from app.services.subscription_service import build_trial_subscription


class FakeSettings:
    paystack_secret_key = "sk_test_verify_synthetic_only"
    frontend_url = "http://127.0.0.1:55446"


class PaymentVerificationTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            self.headers=[]
            for index in range(2):
                user=User(full_name="Synthetic verifier",email=f"verify{index}@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code=f"VERIFY{index}")
                user.subscription=build_trial_subscription(user=user);db.add(user);db.flush()
                self.headers.append({"Authorization":"Bearer "+create_access_token(user_id=user.id)})
                if index==0:self.user_id=user.id
            db.add(Payment(user_id=self.user_id,reference="py_verify_synthetic",plan="monthly",amount=2500,currency="NGN",status="pending"));db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions
        self.client=TestClient(app,raise_server_exceptions=False,client=("verify-"+uuid.uuid4().hex,50000))
        self.settings=patch.object(payment_service,"get_settings",return_value=FakeSettings());self.settings.start()
        self.body={"status":True,"data":{"reference":"py_verify_synthetic","id":909090,"amount":250000,"currency":"NGN","status":"success"}}

    def tearDown(self):
        self.settings.stop();self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def verify(self,body=None,*,http_status=200,headers=None,reference="py_verify_synthetic"):
        self.observed={}
        def provider(session,method,url,**kwargs):
            self.observed={"method":method,"url":url,"trust_env":session.trust_env,**kwargs}
            response=requests.Response();response.status_code=http_status
            response._content=json.dumps(self.body if body is None else body).encode();return response
        with patch("requests.Session.request",autospec=True,side_effect=provider):
            return self.client.post(f"/payments/{reference}/verify",headers=self.headers[0] if headers is None else headers)

    def assert_pending(self):
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(Payment)).status,"pending")
            self.assertEqual(db.get(User,self.user_id).subscription.status,"trial")
            self.assertEqual(db.scalars(select(AuditLog)).all(),[])

    def test_verified_purchase_recovers_without_webhook_and_does_not_recredit(self):
        with Session(self.engine) as db:trial_end=db.get(User,self.user_id).subscription.trial_ends_at
        response=self.verify();self.assertEqual(response.status_code,200);self.assertEqual(response.json()["status"],"success")
        self.assertEqual(self.observed["method"].upper(),"GET")
        self.assertEqual(self.observed["url"],"https://api.paystack.co/transaction/verify/py_verify_synthetic")
        self.assertFalse(self.observed["trust_env"]);self.assertFalse(self.observed["allow_redirects"])
        self.assertEqual(self.observed["timeout"],(3,15));self.assertTrue(self.observed["verify"])
        with patch("requests.Session.request") as provider:
            self.assertEqual(self.client.post("/payments/py_verify_synthetic/verify",headers=self.headers[0]).status_code,200)
            provider.assert_not_called()
        with Session(self.engine) as db,patch.object(payment_service,"notify_admins"):
            payment_service.handle_webhook_event(db,{"event":"charge.success","data":self.body["data"]})
            self.assertEqual(db.get(User,self.user_id).subscription.end_date,trial_end.date()+timedelta(days=30))
            self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action=="payment.success")).all()),1)

    def test_guest_other_account_and_unknown_reference_never_query_provider(self):
        for headers,reference,expected in (({},"py_verify_synthetic",401),(self.headers[1],"py_verify_synthetic",404),(self.headers[0],"py_unknown_synthetic",404)):
            with self.subTest(expected=expected):
                self.assertEqual(self.verify(headers=headers,reference=reference).status_code,expected)
                self.assertEqual(self.observed,{})
        self.assert_pending()

    def test_wrong_reference_amount_currency_or_id_never_credits(self):
        for field,value in (("reference","py_other"),("amount",249999),("amount","250000"),("currency","USD"),("id",None),("id",True)):
            body=deepcopy(self.body);body["data"][field]=value
            with self.subTest(field=field):
                self.assertEqual(self.verify(body).status_code,422);self.assert_pending()

    def test_pending_or_failed_provider_status_does_not_grant_or_destroy_trial(self):
        for state in ("pending","failed","abandoned","ongoing","processing","queued","reversed"):
            body=deepcopy(self.body);body["data"]["status"]=state
            with self.subTest(state=state):
                self.assertEqual(self.verify(body).status_code,200);self.assert_pending()

    def test_malformed_response_and_redirect_fail_safely(self):
        for body in ([],"ok",{"status":"true","data":{}},{"status":True,"data":[]},{"status":True,"data":{} }):
            with self.subTest(body=body):self.assertIn(self.verify(body).status_code,(422,502));self.assert_pending()
        self.assertEqual(self.verify(http_status=302).status_code,502);self.assert_pending()

    def test_provider_timeout_and_atomic_failure_leave_purchase_recoverable(self):
        with patch("requests.Session.request",side_effect=requests.Timeout("Synthetic timeout")):
            self.assertEqual(self.client.post("/payments/py_verify_synthetic/verify",headers=self.headers[0]).status_code,502)
        self.assert_pending()
        with patch.object(payment_service,"create_audit_log",side_effect=RuntimeError("Synthetic audit failure")):
            self.assertEqual(self.verify().status_code,500)
        self.assert_pending();self.assertEqual(self.verify().status_code,200)

    def test_failed_initialization_record_can_be_recovered_from_confirmed_evidence(self):
        with Session(self.engine) as db:db.scalar(select(Payment)).status="failed";db.commit()
        self.assertEqual(self.verify().status_code,200)
        with Session(self.engine) as db:self.assertEqual(db.scalar(select(Payment)).status,"success")

    def test_verification_rate_bound_is_enforced(self):
        with patch("requests.Session.request") as provider:
            statuses=[self.client.post("/payments/py_missing/verify",headers=self.headers[0]).status_code for _ in range(11)]
            self.assertEqual(statuses,[404]*10+[429]);provider.assert_not_called()
            self.assertEqual(self.client.post("/payments/py_missing/verify",headers=self.headers[1]).status_code,404)
