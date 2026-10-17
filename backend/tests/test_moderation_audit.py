from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.market import Market
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.security import create_access_token


class ModerationAuditTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        self.screenshot="data:image/png;base64,c3ludGhldGljLXByaXZhdGU="
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic moderation Admin",email="moderation@example.com",password_hash="unused",role="admin",referral_code="MODERATION")
            customer=User(full_name="Synthetic customer",email="moderation-user@example.com",password_hash="unused",role="free_user",referral_code="MODCUSTOMER")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market")
            db.add_all([admin,customer,commodity,market]);db.flush()
            self.headers={"Authorization":"Bearer "+create_access_token(user_id=admin.id)}
            self.customer_headers={"Authorization":"Bearer "+create_access_token(user_id=customer.id)}
            feedback=Feedback(user_id=customer.id,rating=4,comment="Synthetic original feedback",screenshot_data=self.screenshot)
            price=PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit="1 bag",bag_size=None,
                price_low=210000,price_high=220000,status="approved",movement="unknown",confidence_level="Low confidence",
                update_date_time=datetime.now(timezone.utc),created_by=admin.id,source_1="PRIVATE-MODERATION-SOURCE")
            db.add_all([feedback,price]);db.flush();self.feedback_id,self.price_id=feedback.id,price.id
            db.add(PriceFlag(price_update_id=price.id,user_id=customer.id,reason="Synthetic private report"));db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions;self.client=TestClient(app,raise_server_exceptions=False)

    def tearDown(self):self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return {table.name:db.execute(select(table)).all() for table in (Feedback.__table__,PriceUpdate.__table__,PriceFlag.__table__,AuditLog.__table__)}

    def feedback_action(self,action):
        if action=="delete":return self.client.delete(f"/feedback/{self.feedback_id}",headers=self.headers)
        return self.client.patch(f"/feedback/{self.feedback_id}/testimonial/{action}",json={"display_name":"Synthetic customer"} if action=="publish" else None,headers=self.headers)

    def test_feedback_changes_and_private_evidence_roll_back_on_audit_failure(self):
        for action in ("publish","hide","delete"):
            with self.subTest(action=action):
                with Session(self.engine) as db:db.get(Feedback,self.feedback_id).is_public_testimonial=action=="hide";db.commit()
                before=self.state()
                with patch("app.routes.feedback_routes.create_audit_log",side_effect=RuntimeError("Synthetic audit failure")):
                    self.assertEqual(self.feedback_action(action).status_code,500)
                self.assertEqual(self.state(),before)

    def test_price_delete_failure_preserves_price_flags_and_existing_history(self):
        before=self.state()
        with patch("app.routes.price_update_routes.create_audit_log",side_effect=RuntimeError("Synthetic audit failure")):
            self.assertEqual(self.client.delete(f"/price-updates/{self.price_id}",headers=self.headers).status_code,500)
        self.assertEqual(self.state(),before)

    def test_flag_resolution_failure_preserves_open_reports(self):
        before=self.state()
        with patch("app.routes.price_update_routes.create_audit_log",side_effect=RuntimeError("Synthetic audit failure")):
            self.assertEqual(self.client.post(f"/price-updates/{self.price_id}/flags/resolve",headers=self.headers).status_code,500)
        self.assertEqual(self.state(),before)

    def test_feedback_audits_omit_image_but_keep_original_record_and_public_projection(self):
        self.assertEqual(self.feedback_action("publish").status_code,200)
        public=self.client.get("/testimonials");self.assertEqual(public.status_code,200)
        self.assertNotIn("screenshot",public.text);self.assertNotIn("moderation-user@example.com",public.text)
        self.assertEqual(self.feedback_action("hide").status_code,200);self.assertEqual(self.client.get("/testimonials").json(),[])
        with Session(self.engine) as db:
            self.assertEqual(db.get(Feedback,self.feedback_id).screenshot_data,self.screenshot)
        self.assertEqual(self.feedback_action("delete").status_code,204)
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).order_by(AuditLog.id)).all()
            self.assertEqual([row.action for row in logs],["feedback.testimonial_publish","feedback.testimonial_hide","feedback.delete"])
            for first,second in zip(logs,logs[1:]):self.assertEqual(first.new_value,second.old_value)
            self.assertNotIn("screenshot_data",str([(row.old_value,row.new_value) for row in logs]))

    def test_resolution_is_once_audited_and_customer_cannot_moderate(self):
        url=f"/price-updates/{self.price_id}/flags/resolve"
        self.assertEqual(self.client.post(url,headers=self.customer_headers).status_code,403)
        for _ in range(2):self.assertEqual(self.client.post(url,headers=self.headers).status_code,204)
        with Session(self.engine) as db:
            self.assertTrue(db.scalar(select(PriceFlag)).resolved)
            logs=db.scalars(select(AuditLog).where(AuditLog.action=="price_update.flags_resolve")).all()
            self.assertEqual(len(logs),1);self.assertEqual(logs[0].old_value,{"unresolved_count":1})
            self.assertEqual(logs[0].new_value,{"unresolved_count":0,"resolved_count":1})
            self.assertNotIn("Synthetic private report",str(logs[0].new_value))
