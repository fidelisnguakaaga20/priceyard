from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.user import User
from app.security import create_access_token
from app.services.audit_service import create_audit_log
from app.services.subscription_service import build_trial_subscription


class AdminAccessAuditTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:"); Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic Admin",email="admin-audit@example.com",password_hash="unused-admin-hash",role="admin",referral_code="ACCESSADMIN")
            target=User(full_name="Synthetic customer",email="target-audit@example.com",password_hash="unchanged-customer-hash",role="free_user",referral_code="ACCESSTARGET")
            target.subscription=build_trial_subscription(user=target)
            db.add_all([admin,target]);db.flush();self.target_id=target.id
            self.admin_headers={"Authorization":"Bearer "+create_access_token(user_id=admin.id)}
            self.target_headers={"Authorization":"Bearer "+create_access_token(user_id=target.id)}
            db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions
        self.client=TestClient(app,raise_server_exceptions=False)

    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            user=db.get(User,self.target_id);sub=user.subscription
            return dict(role=user.role,active=user.is_active,version=user.auth_version,password=user.password_hash,
                        status=sub.status,plan=sub.plan_name,start=sub.start_date,end=sub.end_date,trial_start=sub.trial_started_at,trial_end=sub.trial_ends_at,
                        audits=len(db.scalars(select(AuditLog)).all()))

    def failing_audit(self,number):
        calls=0
        def audit(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==number:raise RuntimeError("Synthetic audit storage failure")
            return create_audit_log(*args,**kwargs)
        return audit

    def test_user_update_rolls_back_role_grant_revocation_and_both_audits(self):
        for number in (1,2):
            before=self.state();paid=before["role"]!="paid_user"
            with self.subTest(audit_number=number),patch("app.routes.user_routes.create_audit_log",side_effect=self.failing_audit(number)):
                response=self.client.patch(f"/users/{self.target_id}",json={"role":"paid_user" if paid else "free_user","is_active":not before["active"]},headers=self.admin_headers)
                self.assertEqual(response.status_code,500)
                self.assertEqual(self.state(),before)
                self.assertEqual(self.client.get("/auth/me",headers=self.target_headers).status_code,200)

    def test_status_update_rolls_back_access_role_and_both_audits(self):
        for number in (1,2):
            before=self.state();status="free" if before["status"]=="active" else "active"
            with self.subTest(audit_number=number),patch("app.routes.subscription_routes.create_audit_log",side_effect=self.failing_audit(number)):
                response=self.client.patch(f"/subscriptions/{self.target_id}/status",json={"status":status},headers=self.admin_headers)
                self.assertEqual(response.status_code,500)
                self.assertEqual(self.state(),before)

    def test_successful_user_change_records_all_state_and_revokes_previous_token(self):
        response=self.client.patch(f"/users/{self.target_id}",json={"role":"paid_user","is_active":False},headers=self.admin_headers)
        self.assertEqual(response.status_code,200)
        state=self.state();self.assertFalse(state["active"]);self.assertEqual(state["version"],1)
        self.assertEqual(state["role"],"paid_user");self.assertEqual(state["status"],"active");self.assertIsNone(state["end"])
        self.assertEqual(state["audits"],2);self.assertEqual(state["password"],"unchanged-customer-hash")
        self.assertEqual(self.client.get("/auth/me",headers=self.target_headers).status_code,403)
        self.assertEqual(self.client.get("/auth/me",headers=self.admin_headers).status_code,200)
        self.assertEqual(self.client.patch(f"/users/{self.target_id}",json={"is_active":True},headers=self.admin_headers).status_code,200)
        self.assertEqual(self.client.get("/auth/me",headers=self.target_headers).status_code,401)
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog)).all()
            self.assertNotIn("unchanged-customer-hash",str([(item.old_value,item.new_value) for item in logs]))

    def test_staff_status_changes_keep_authority_and_existing_indefinite_grant_rule(self):
        with Session(self.engine) as db:db.get(User,self.target_id).role="reporter";db.commit()
        for status in ("active","free"):
            response=self.client.patch(f"/subscriptions/{self.target_id}/status",json={"status":status},headers=self.admin_headers)
            self.assertEqual(response.status_code,200)
            state=self.state();self.assertEqual(state["role"],"reporter");self.assertEqual(state["status"],status);self.assertIsNone(state["end"])
        self.assertEqual(self.state()["audits"],2)

    def test_expiry_cleanup_cannot_commit_before_failed_admin_action(self):
        with Session(self.engine) as db:
            db.get(User,self.target_id).subscription.trial_ends_at=datetime.now(timezone.utc)-timedelta(days=1);db.commit()
        before=self.state()
        with patch("app.routes.user_routes.create_audit_log",side_effect=RuntimeError("Synthetic audit failure")):
            response=self.client.patch(f"/users/{self.target_id}",json={"is_active":False},headers=self.admin_headers)
            self.assertEqual(response.status_code,500)
        self.assertEqual(self.state(),before)
