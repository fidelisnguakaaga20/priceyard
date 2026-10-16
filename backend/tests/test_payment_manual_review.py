from datetime import datetime, timedelta, timezone
import hashlib
import hmac
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
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token
from app.services import payment_service
from app.services.subscription_service import update_subscription_status


class FakeSettings:
    paystack_secret_key="sk_test_manual_review_only"
    frontend_url="http://127.0.0.1:55446"


class PaymentManualReviewTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user=User(full_name="Synthetic manual grant",email="manual-review@example.com",password_hash="not-used",role="paid_user",is_active=True,referral_code="MANUALREVIEW")
            user.subscription=Subscription(plan_name="paid",status="active",start_date=datetime.now(timezone.utc).date(),end_date=None)
            db.add(user);db.flush();self.user_id=user.id
            db.add(Payment(user_id=user.id,reference="py_manual_review",plan="monthly",amount=2500,currency="NGN",status="pending"));db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions
        self.client=TestClient(app,raise_server_exceptions=False,client=("manual-"+uuid.uuid4().hex,50000))
        self.headers={"Authorization":"Bearer "+create_access_token(user_id=self.user_id)}
        self.settings=patch.object(payment_service,"get_settings",return_value=FakeSettings());self.settings.start()

    def tearDown(self):
        self.settings.stop();self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def event(self,*,reference="py_manual_review",transaction=515151,amount=250000):
        return {"event":"charge.success","data":{"reference":reference,"id":transaction,"amount":amount,"currency":"NGN","status":"success"}}

    def send(self,**kwargs):
        body=json.dumps(self.event(**kwargs)).encode();signature=hmac.new(FakeSettings.paystack_secret_key.encode(),body,hashlib.sha512).hexdigest()
        return self.client.post("/payments/webhook",content=body,headers={"x-paystack-signature":signature})

    def verify(self):
        response=requests.Response();response.status_code=200
        response._content=json.dumps({"status":True,"data":self.event()["data"]}).encode()
        with patch("requests.Session.request",return_value=response):return self.client.post("/payments/py_manual_review/verify",headers=self.headers)

    def assert_grant_unchanged(self,*,receipt=None,reviews=0):
        with Session(self.engine) as db:
            user=db.get(User,self.user_id);self.assertEqual(user.role,"paid_user")
            self.assertEqual(user.subscription.status,"active");self.assertEqual(user.subscription.plan_name,"paid");self.assertIsNone(user.subscription.end_date)
            payment=db.scalar(select(Payment).where(Payment.reference=="py_manual_review"))
            self.assertEqual(payment.status,"pending");self.assertEqual(payment.paystack_transaction_id,receipt)
            self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action=="payment.review_required")).all()),reviews)

    def test_new_checkout_blocked_before_provider_and_without_new_purchase(self):
        def accepted(session,method,url,**kwargs):
            response=requests.Response();response.status_code=200
            response._content=json.dumps({"status":True,"data":{"authorization_url":"https://checkout.paystack.com/synthetic-manual","reference":kwargs["json"]["reference"]}}).encode()
            return response
        with patch("requests.Session.request",autospec=True,side_effect=accepted) as provider:
            for plan in ("monthly","seasonal"):
                self.assertEqual(self.client.post("/payments/initiate",json={"plan":plan},headers=self.headers).status_code,409)
            provider.assert_not_called()
        with Session(self.engine) as db:self.assertEqual(len(db.scalars(select(Payment)).all()),1)
        self.assert_grant_unchanged()

    def test_confirmed_purchase_is_held_with_evidence_and_one_review_audit(self):
        self.assertEqual(self.send().status_code,409);self.assert_grant_unchanged(receipt="515151",reviews=1)
        self.assertEqual(self.send().status_code,409);self.assert_grant_unchanged(receipt="515151",reviews=1)

    def test_verification_also_holds_without_consuming_purchased_days(self):
        self.assertEqual(self.verify().status_code,409);self.assert_grant_unchanged(receipt="515151",reviews=1)

    def test_audit_failure_cannot_save_partial_review_evidence(self):
        with patch.object(payment_service,"create_audit_log",side_effect=RuntimeError("Synthetic review audit failure")):
            self.assertEqual(self.send().status_code,500)
        self.assert_grant_unchanged()
        self.assertEqual(self.send().status_code,409);self.assert_grant_unchanged(receipt="515151",reviews=1)

    def test_wrong_amount_never_records_review_or_credit(self):
        self.assertEqual(self.send(amount=249999).status_code,422);self.assert_grant_unchanged()

    def test_conflicting_receipt_never_overwrites_held_transaction(self):
        self.assertEqual(self.send().status_code,409)
        self.assertEqual(self.send(transaction=515152).status_code,409)
        self.assert_grant_unchanged(receipt="515151",reviews=1)

    def test_held_receipt_cannot_credit_another_purchase(self):
        self.assertEqual(self.send().status_code,409)
        with Session(self.engine) as db:
            db.add(Payment(user_id=self.user_id,reference="py_other_manual_purchase",plan="monthly",amount=2500,currency="NGN",status="pending"));db.commit()
        self.assertEqual(self.send(reference="py_other_manual_purchase").status_code,409)
        with Session(self.engine) as db:self.assertIsNone(db.scalar(select(Payment).where(Payment.reference=="py_other_manual_purchase")).paystack_transaction_id)
        self.assert_grant_unchanged(receipt="515151",reviews=1)

    def test_deliberate_grant_resolution_allows_exactly_one_purchased_credit(self):
        self.assertEqual(self.send().status_code,409)
        with Session(self.engine) as db:update_subscription_status(db,db.get(User,self.user_id).subscription,"free")
        self.assertEqual(self.verify().status_code,200)
        self.assertEqual(self.send().status_code,200)
        with Session(self.engine) as db:
            self.assertEqual(db.get(User,self.user_id).subscription.end_date,datetime.now(timezone.utc).date()+timedelta(days=30))
            self.assertEqual(db.scalar(select(Payment)).status,"success")
            actions=[row.action for row in db.scalars(select(AuditLog))]
            self.assertCountEqual(actions,["payment.review_required","payment.success"])
