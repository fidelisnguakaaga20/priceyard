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
from app.models.market import Market
from app.models.user import User
from app.security import create_access_token


class CatalogAuditAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic catalog admin",email="catalog-audit@example.com",password_hash="unused",role="admin",referral_code="CATALOGAUDIT")
            db.add(admin);db.flush();self.headers={"Authorization":"Bearer "+create_access_token(user_id=admin.id)};db.commit()
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions;self.client=TestClient(app,raise_server_exceptions=False)
        self.catalogs=[("commodity","commodities",Commodity,"Egusi"),("market","markets",Market,"Kwali Market")]

    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return {table:db.execute(select(table)).all() for table in (Commodity.__table__,Market.__table__,AuditLog.__table__)}

    def check_rollback(self,action):
        for kind,path,model,name in self.catalogs:
            with self.subTest(kind=kind,action=action):
                item_id=None
                if action!="create":
                    with Session(self.engine) as db:
                        item=model(name=name,description="Synthetic original description");db.add(item);db.commit();item_id=item.id
                before=self.state()
                with patch(f"app.routes.{kind}_routes.create_audit_log",side_effect=RuntimeError("Synthetic catalog audit failure")):
                    if action=="create":response=self.client.post('/'+path,headers=self.headers,json={"name":name})
                    elif action=="edit":response=self.client.patch(f"/{path}/{item_id}",headers=self.headers,json={"description":"Synthetic corrected description","is_active":False})
                    else:response=self.client.delete(f"/{path}/{item_id}",headers=self.headers)
                    self.assertEqual(response.status_code,500)
                self.assertEqual(self.state(),before)

    def test_create_and_audit_roll_back_together(self):self.check_rollback("create")
    def test_edit_and_audit_roll_back_together(self):self.check_rollback("edit")
    def test_delete_and_audit_roll_back_together(self):self.check_rollback("delete")

    def test_original_actions_and_permissions_keep_stable_ids_and_complete_audits(self):
        for kind,path,model,name in self.catalogs:
            created=self.client.post('/'+path,headers=self.headers,json={"name":name});self.assertEqual(created.status_code,201);item_id=created.json()["id"]
            self.assertEqual(self.client.patch(f"/{path}/{item_id}",headers=self.headers,json={"description":"Synthetic corrected description","is_active":False}).status_code,200)
            self.assertEqual(self.client.get(f"/{path}/{item_id}").status_code,404)
            saved=self.client.get('/'+path+'/admin/all',headers=self.headers).json();self.assertEqual(saved[0]["id"],item_id);self.assertEqual(saved[0]["name"],name)
            self.assertEqual(self.client.patch(f"/{path}/{item_id}",json={"description":"Unauthorized"}).status_code,401)
            self.assertEqual(self.client.delete(f"/{path}/{item_id}",headers=self.headers).status_code,204)
            with Session(self.engine) as db:
                logs=db.scalars(select(AuditLog).where(AuditLog.table_name==path).order_by(AuditLog.id)).all()
                self.assertEqual([row.action for row in logs],[kind+'.'+action for action in ('create','edit','delete')])
                self.assertEqual(logs[0].new_value,logs[1].old_value);self.assertEqual(logs[1].new_value,logs[2].old_value)
                self.assertIsNone(logs[0].old_value);self.assertIsNone(logs[-1].new_value)
