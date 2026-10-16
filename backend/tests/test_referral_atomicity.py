from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth_schema import RegisterRequest
from app.services import auth_service
from app.services.subscription_service import build_trial_subscription


class ReferralAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        self.db=Session(self.engine,expire_on_commit=False)
        self.referrer=User(full_name="Synthetic referrer",email="referrer@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code="REFTEST")
        self.referrer.subscription=build_trial_subscription(user=self.referrer)
        self.db.add(self.referrer);self.db.commit()
        self.original_end=self.referrer.subscription.trial_ends_at
        self.payload=RegisterRequest(full_name="Synthetic newcomer",email="newcomer@example.com",password="PriceYardDemo8!",referral_code="REFTEST")

    def tearDown(self):
        self.db.close();self.engine.dispose()

    def assert_unchanged(self):
        self.db.rollback();self.db.expire_all()
        self.assertIsNone(self.db.scalar(select(User).where(User.email=="newcomer@example.com")))
        expected=self.original_end.replace(tzinfo=None)
        self.assertEqual(self.referrer.subscription.trial_ends_at.replace(tzinfo=None),expected)
        self.assertEqual(self.db.scalars(select(AuditLog)).all(),[])

    def test_reward_failure_does_not_leave_a_created_account(self):
        with patch.object(auth_service,"apply_referral_reward",side_effect=RuntimeError("Synthetic reward outage")):
            with self.assertRaises(RuntimeError):auth_service.register_user(self.db,self.payload)
        self.assert_unchanged()

    def test_audit_failure_rolls_back_registration_and_reward(self):
        with patch.object(auth_service,"create_audit_log",side_effect=RuntimeError("Synthetic audit outage")):
            with self.assertRaises(RuntimeError):auth_service.register_user(self.db,self.payload)
        self.assert_unchanged()

    def test_registration_reward_and_audit_commit_once(self):
        with patch.object(self.db,"commit",wraps=self.db.commit) as commit:
            newcomer=auth_service.register_user(self.db,self.payload)
            self.assertEqual(commit.call_count,1)
        self.assertEqual(newcomer.referred_by_id,self.referrer.id)
        self.assertEqual(newcomer.subscription.trial_ends_at-newcomer.subscription.trial_started_at,timedelta(days=14))
        self.assertEqual(self.referrer.subscription.trial_ends_at.replace(tzinfo=None),self.original_end.replace(tzinfo=None)+timedelta(days=7))
        self.assertEqual(len(self.db.scalars(select(AuditLog).where(AuditLog.action=="referral.reward_granted")).all()),1)
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as error:auth_service.register_user(self.db,self.payload)
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.referrer.subscription.trial_ends_at.replace(tzinfo=None),self.original_end.replace(tzinfo=None)+timedelta(days=7))

    def test_existing_reward_qualification_and_staff_roles_remain_unchanged(self):
        for state in ("free","active","expired","cancelled","past_trial"):
            with self.subTest(state=state):
                subscription=self.referrer.subscription
                subscription.status="trial" if state=="past_trial" else state
                subscription.trial_ends_at=datetime(2000,1,1,tzinfo=timezone.utc) if state=="past_trial" else self.original_end
                subscription.end_date=None
                self.referrer.role="reporter"
                self.db.commit()
                payload=self.payload.model_copy(update={"email":f"new-{state}@example.com"})
                auth_service.register_user(self.db,payload)
                self.assertEqual(self.referrer.role,"reporter")
                self.assertEqual(subscription.status,"trial" if state=="free" else "expired" if state=="past_trial" else state)
                if state=="free":
                    end=subscription.trial_ends_at.replace(tzinfo=None);start=subscription.trial_started_at.replace(tzinfo=None)
                    self.assertEqual(end-start,timedelta(days=7))
