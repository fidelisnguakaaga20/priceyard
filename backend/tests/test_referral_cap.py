from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth_schema import RegisterRequest
from app.services import auth_service, subscription_service as service


def utc_instant(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def seed_referrer(db, *, now=None, code='CAPREF'):
    now = now or datetime.now(timezone.utc)
    user = User(full_name='Synthetic capped referrer', email=code.lower()+'@example.com',
                password_hash='unused', role='free_user', referral_code=code)
    user.subscription = service.build_trial_subscription(user=user, now=now)
    db.add(user); db.commit()
    return user


def award_evidence(db, user, when, *, action='referral.reward_granted', table='subscriptions'):
    db.add(AuditLog(user_id=user.id, action=action, table_name=table, record_id=user.subscription.id,
                    created_at=when, old_value={'note':'Retained synthetic evidence'}, new_value={'bonus_days':7}))


def verify_referral_cap_flow(check, engine):
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        parent = seed_referrer(db); parent_id = parent.id
        original_end = parent.subscription.trial_ends_at
        start = parent.subscription.trial_started_at
        for index in range(5):
            payload = RegisterRequest(full_name='Synthetic referral child', email=f'cap-child-{index}@example.com',
                                      password='PriceYardDemo8!', referral_code=parent.referral_code)
            child = auth_service.register_user(db, payload)
            check.assertEqual(child.referred_by_id, parent_id)
            check.assertEqual(child.subscription.trial_ends_at-child.subscription.trial_started_at, timedelta(days=14))
            check.assertEqual(utc_instant(parent.subscription.trial_ends_at),
                              utc_instant(original_end)+timedelta(days=7*min(index+1,3)))
        check.assertEqual(db.scalar(select(func.count()).select_from(User).where(User.referred_by_id == parent_id)), 5)
        check.assertEqual(utc_instant(parent.subscription.trial_started_at), utc_instant(start))
        audits = db.scalars(select(AuditLog).where(AuditLog.action == 'referral.reward_granted').order_by(AuditLog.id)).all()
        check.assertEqual(len(audits), 3)
        check.assertEqual(parent.subscription.status, 'trial')
        check.assertEqual(parent.role, 'free_user')


class ReferralCapTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite+pysqlite:///:memory:'); Base.metadata.create_all(self.engine)
        self.db=Session(self.engine,expire_on_commit=False)
    def tearDown(self): self.db.close(); self.engine.dispose()

    def test_only_three_awards_without_blocking_further_signups_or_removing_days(self):
        verify_referral_cap_flow(self,self.engine)

    def test_elapsed_utc_window_exact_boundary_and_known_reward_scope(self):
        now = datetime(2026,10,18,12,tzinfo=timezone.utc)
        for offset, blocked in ((timedelta(days=30),False),(timedelta(days=30)-timedelta(microseconds=1),True)):
            with self.subTest(offset=offset):
                parent=seed_referrer(self.db,now=now,code='BOUND'+str(int(blocked)))
                other=seed_referrer(self.db,now=now,code='OTHER'+str(int(blocked)))
                for _ in range(3): award_evidence(self.db,parent,now-offset)
                # Other actors/actions/tables and older evidence do not consume slots.
                for _ in range(4):
                    award_evidence(self.db,other,now-timedelta(hours=1))
                    award_evidence(self.db,parent,now-timedelta(hours=1),action='other.action')
                    award_evidence(self.db,parent,now-timedelta(hours=1),table='users')
                    award_evidence(self.db,parent,now-timedelta(days=31))
                self.db.commit()
                before=self.db.execute(select(AuditLog.__table__).order_by(AuditLog.id)).all()
                end=parent.subscription.trial_ends_at
                with patch.object(service,'utc_now',return_value=now):
                    granted=service.apply_referral_reward(self.db,parent,commit=False)
                self.assertEqual(granted,not blocked)
                self.assertEqual(parent.subscription.trial_ends_at.replace(tzinfo=None),end.replace(tzinfo=None)+(timedelta(0) if blocked else timedelta(days=7)))
                self.db.commit()
                self.assertEqual(self.db.execute(select(AuditLog.__table__).order_by(AuditLog.id)).all(),before)

    def test_cap_preserves_free_state_existing_days_and_paid_value(self):
        now=datetime.now(timezone.utc)
        for index,status in enumerate(('free','trial','active','expired','cancelled')):
            parent=seed_referrer(self.db,now=now,code='STATE'+str(index))
            parent.role='reporter'; parent.subscription.status=status
            parent.subscription.end_date=(now+timedelta(days=23)).date()
            parent.subscription.payment_reference='synthetic_saved_payment'
            for _ in range(3): award_evidence(self.db,parent,now-timedelta(hours=1))
            self.db.commit(); before=self.db.execute(select(Subscription.__table__).where(Subscription.user_id==parent.id)).one()
            with patch.object(service,'utc_now',return_value=now): self.assertFalse(service.apply_referral_reward(self.db,parent,commit=False))
            self.db.commit()
            self.assertEqual(self.db.execute(select(Subscription.__table__).where(Subscription.user_id==parent.id)).one(),before)
            self.assertEqual(parent.role,'reporter')

    def test_failed_third_award_leaves_slot_and_all_prior_evidence_intact(self):
        parent=seed_referrer(self.db); now=datetime.now(timezone.utc)
        for _ in range(2): award_evidence(self.db,parent,now-timedelta(hours=1))
        self.db.commit(); end=parent.subscription.trial_ends_at
        payload=RegisterRequest(full_name='Synthetic rollback child',email='cap-rollback@example.com',password='PriceYardDemo8!',referral_code=parent.referral_code)
        with patch.object(auth_service,'create_audit_log',side_effect=RuntimeError('Synthetic cap audit failure')):
            with self.assertRaisesRegex(RuntimeError,'Synthetic cap audit failure'): auth_service.register_user(self.db,payload)
        self.db.expire_all();self.assertIsNone(self.db.scalar(select(User).where(User.email==payload.email)))
        self.assertEqual(parent.subscription.trial_ends_at.replace(tzinfo=None),end.replace(tzinfo=None))
        self.assertEqual(len(self.db.scalars(select(AuditLog)).all()),2)
        auth_service.register_user(self.db,payload);self.assertEqual(len(self.db.scalars(select(AuditLog)).all()),3)
