from datetime import datetime, timezone
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.faq_item import FAQItem
from app.models.user import User
from app.schemas.audit_log_schema import AuditLogResponse
from app.schemas.faq_schema import FAQAdminResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records


FAQ_ORDER = (("is_published", True), ("category", False), ("id", False))
AUDIT_ORDER = (("created_at", True), ("id", True))


def seed_faq_audit(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic FAQ Admin", email="faq-page@example.com", password_hash="unused", role="admin", referral_code="FAQPAGE")
        customer = User(full_name="Synthetic FAQ customer", email="faq-customer@example.com", password_hash="unused", role="free_user", referral_code="FAQFREE")
        db.add_all([owner, customer]); db.flush()
        for index in range(205):
            db.add(FAQItem(question=f"Synthetic FAQ {index:03}", answer="Saved synthetic answer", category="Synthetic",
                           is_published=index % 2 == 0, created_by=owner.id))
            db.add(AuditLog(user_id=owner.id, action="synthetic.paging", table_name="faq_items", record_id=None,
                           old_value={"notes":"Retained audit evidence", "source_1":"PRIVATE-PAGING-SOURCE"},
                           new_value={"nested":[{"SOURCE_2":"PRIVATE-PAGING-SOURCE", "password_hash":"PRIVATE-PAGING-HASH"}]},
                           created_at=datetime(2026,10,18,8,tzinfo=timezone.utc)))
        db.commit()
        return owner.id, customer.id


def verify_faq_audit_pages(check, engine):
    seed_faq_audit(engine)
    with Session(engine) as db:
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all() for model in (FAQItem,AuditLog)}
    resources = ((FAQItem,FAQAdminResponse,FAQ_ORDER,sorted(before[FAQItem],key=lambda row:(not row.is_published,row.category,row.id))),
                 (AuditLog,AuditLogResponse,AUDIT_ORDER,sorted(before[AuditLog],key=lambda row:(row.created_at,row.id),reverse=True)))
    for model,schema,order,expected in resources:
        ids=[]
        for offset,count in ((0,100),(100,100),(200,5),(300,0)):
            statements=[]
            def observe(*args): statements.append(True)
            event.listen(engine,"before_cursor_execute",observe)
            try:
                with Session(engine) as db:
                    page=admin_record_page(db,model,schema,offset=offset,order=order)
                    check.assertLessEqual(len(db.identity_map),100)
            finally: event.remove(engine,"before_cursor_execute",observe)
            check.assertEqual(len(statements),1)
            check.assertEqual((page.total,len(page.items)),(205,count))
            ids.extend(row.id for row in page.items)
            check.assertNotIn("PRIVATE-PAGING",page.model_dump_json())
        check.assertEqual(ids,[row.id for row in expected])
        legacy_order=(("category",False),("id",False)) if model is FAQItem else order
        stream=stream_admin_records(engine,model,schema,order=legacy_order)
        full=json.loads("".join(stream))
        expected_legacy=sorted(before[FAQItem],key=lambda row:(row.category,row.id)) if model is FAQItem else expected
        check.assertEqual([row["id"] for row in full],[row.id for row in expected_legacy])
        check.assertNotIn("PRIVATE-PAGING",str(full))
    with Session(engine) as db:
        for model in before:
            check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(),before[model])


class FAQAuditPagingTests(unittest.TestCase):
    def setUp(self): self.engine=create_engine("sqlite+pysqlite:///:memory:")
    def tearDown(self): app.dependency_overrides.clear();self.engine.dispose()

    def test_complete_faq_groups_redacted_audit_pages_and_unchanged_records(self):
        verify_faq_audit_pages(self,self.engine)

    def test_page_and_legacy_access_publication_and_source_redaction(self):
        owner,customer=seed_faq_audit(self.engine)
        def sessions():
            with Session(self.engine) as db: yield db
        app.dependency_overrides[get_db]=sessions
        admin={"Authorization":"Bearer "+create_access_token(user_id=owner)}
        free={"Authorization":"Bearer "+create_access_token(user_id=customer)}
        with TestClient(app) as client:
            for path in ("/faq/admin/page","/audit-logs/page","/faq/admin","/audit-logs"):
                self.assertEqual(client.get(path).status_code,401)
                self.assertEqual(client.get(path,headers=free).status_code,403)
                response=client.get(path,headers=admin)
                self.assertEqual(response.status_code,200)
                self.assertNotIn("PRIVATE-PAGING",response.text)
            for page in ("/faq/admin/page","/audit-logs/page"):
                self.assertEqual(client.get(page+"?offset=-1",headers=admin).status_code,422)
                self.assertEqual(client.get(page+"?offset=2147483648",headers=admin).status_code,422)
                self.assertEqual(client.get(page+"?offset=300",headers=admin).json()["total"],205)
            public=client.get("/faq")
            self.assertEqual(len(public.json()),103)
            self.assertNotIn("private",public.headers.get("cache-control",""))
            self.assertEqual(client.get("/faq/2").status_code,404)
            known=client.patch("/faq/204",headers=admin,json={"answer":"Changed beyond first page"})
            self.assertEqual(known.status_code,200)
            self.assertFalse(known.json()["is_published"])
            self.assertEqual(client.get("/faq/204").status_code,404)
            self.assertEqual(len(client.get("/faq/admin",headers=admin).json()),205)
