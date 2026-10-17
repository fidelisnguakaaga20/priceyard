import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.faq_item import FAQItem
from app.models.user import User
from app.security import create_access_token


class FAQAuditAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic FAQ admin",email="faq-audit@example.com",password_hash="unused",role="admin",referral_code="FAQAUDIT")
            db.add(admin);db.flush();self.headers={"Authorization":"Bearer "+create_access_token(user_id=admin.id)}
            self.payload=dict(question="Synthetic saved question",answer="Synthetic saved answer",category="Local testing")
            item=FAQItem(**self.payload,created_by=admin.id,is_published=False);db.add(item);db.commit();self.item_id=item.id
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions;self.client=TestClient(app,raise_server_exceptions=False)

    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return {table:db.execute(select(table)).all() for table in (FAQItem.__table__,AuditLog.__table__)}

    def action(self,action,item_id=None):
        item_id=item_id or self.item_id
        if action=="create":return self.client.post("/faq",headers=self.headers,json=self.payload)
        if action=="delete":return self.client.delete(f"/faq/{item_id}",headers=self.headers)
        return self.client.patch(f"/faq/{item_id}"+("" if action=="edit" else "/"+action),headers=self.headers,json={"answer":"Synthetic corrected answer"} if action=="edit" else None)

    def test_each_faq_write_rolls_back_if_audit_fails(self):
        for action in ("create","edit","publish","hide","delete"):
            with self.subTest(action=action):
                # Exercise a real publication change when testing hide.
                with Session(self.engine) as db:db.get(FAQItem,self.item_id).is_published=action=="hide";db.commit()
                before=self.state()
                with patch("app.routes.faq_routes.create_audit_log",side_effect=RuntimeError("Synthetic FAQ audit failure")):
                    self.assertEqual(self.action(action).status_code,500)
                self.assertEqual(self.state(),before)

    def test_failed_final_commit_cannot_leave_faq_or_audit(self):
        before=self.state()
        with patch.object(Session,"commit",side_effect=RuntimeError("Synthetic commit failure")):
            self.assertEqual(self.action("create").status_code,500)
        self.assertEqual(self.state(),before)

    def test_all_original_actions_have_continuous_audit_and_publication_boundaries(self):
        created=self.action("create");self.assertEqual(created.status_code,201);item_id=created.json()["id"]
        self.assertEqual(self.client.get(f"/faq/{item_id}").status_code,404)
        for action in ("edit","publish","hide","delete"):
            self.assertEqual(self.action(action,item_id).status_code,204 if action=="delete" else 200)
            self.assertEqual(self.client.get(f"/faq/{item_id}").status_code,200 if action=="publish" else 404)
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).where(AuditLog.record_id==item_id).order_by(AuditLog.id)).all()
            self.assertEqual([row.action for row in logs],["faq."+action for action in ("create","edit","publish","hide","delete")])
            self.assertIsNone(logs[0].old_value);self.assertIsNone(logs[-1].new_value)
            for previous,current in zip(logs,logs[1:]):self.assertEqual(previous.new_value,current.old_value)
            self.assertIsNotNone(db.get(FAQItem,self.item_id));self.assertIsNone(db.get(FAQItem,item_id))
