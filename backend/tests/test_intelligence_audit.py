from datetime import datetime, timezone
from decimal import Decimal
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import Numeric, create_engine, select
from sqlalchemy.orm import Session

from app.database import Base,get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.user import User
from app.security import create_access_token

RESOURCES=(
    ("market_signal","market-signals",MarketSignal,{"signal_type":"Synthetic observation","signal_description":"Synthetic description"},{"signal_description":"Synthetic corrected description"}),
    ("quality_signal","quality-signals",QualitySignal,{"quality_status":"Synthetic observation","risk_note":"Synthetic risk note"},{"risk_note":"Synthetic corrected risk note"}),
    ("cost_breakdown","cost-breakdowns",CostBreakdown,{"purchase_price_reference":210000,"transport":120,"warehouse":80},{"purchase_price_reference":211000}),
)

def audit_values(model,values):
    return {key:Decimal(str(value)) if value is not None and isinstance(model.__table__.columns[key].type,Numeric) else value for key,value in values.items()}

class IntelligenceAuditTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic intelligence Admin",email="intelligence@example.com",password_hash="unused",role="admin",referral_code="INTELADMIN")
            customer=User(full_name="Synthetic customer",email="intelligence-user@example.com",password_hash="unused",role="free_user",referral_code="INTELUSER")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([admin,customer,commodity,market]);db.flush()
            self.headers={"Authorization":"Bearer "+create_access_token(user_id=admin.id)};self.customer_headers={"Authorization":"Bearer "+create_access_token(user_id=customer.id)}
            self.scope={"commodity_id":commodity.id,"market_id":market.id}
            price=PriceUpdate(**self.scope,unit="1 bag",bag_size=None,price_low=210000,price_high=220000,status="approved",movement="unknown",confidence_level="Low confidence",created_by=admin.id,update_date_time=datetime.now(timezone.utc))
            db.add(price);db.commit();self.price_id=price.id
        def sessions():
            with Session(self.engine,expire_on_commit=False) as db:yield db
        app.dependency_overrides[get_db]=sessions;self.client=TestClient(app,raise_server_exceptions=False)

    def tearDown(self):self.client.close();app.dependency_overrides.clear();self.engine.dispose()

    def payload(self,resource):
        return {**self.scope,**resource[3],**({"price_update_id":self.price_id} if resource[0]!="cost_breakdown" else {})}

    def state(self):
        with Session(self.engine) as db:return {table.name:db.execute(select(table)).all() for table in (MarketSignal.__table__,QualitySignal.__table__,CostBreakdown.__table__,PriceUpdate.__table__,AuditLog.__table__)}

    def create_failure(self,resource):
        before=self.state()
        with patch("app.services.audit_service.create_audit_log",side_effect=RuntimeError("Synthetic resource audit failure")):
            self.assertEqual(self.client.post('/'+resource[1],json=self.payload(resource),headers=self.headers).status_code,500)
        self.assertEqual(self.state(),before)

    def edit_delete_failure(self,resource):
        for action in ("edit","delete"):
            response=self.client.post('/'+resource[1],json=self.payload(resource),headers=self.headers);self.assertEqual(response.status_code,201);item_id=response.json()["id"];before=self.state()
            with self.subTest(action=action),patch("app.services.audit_service.create_audit_log",side_effect=RuntimeError("Synthetic resource audit failure")):
                url=f'/{resource[1]}/{item_id}'
                response=self.client.patch(url,json=resource[4],headers=self.headers) if action=="edit" else self.client.delete(url,headers=self.headers)
                self.assertEqual(response.status_code,500);self.assertEqual(self.state(),before)

    def success(self,resource):
        prefix,path,model,_,changes=resource
        response=self.client.post('/'+path,json=self.payload(resource),headers=self.headers);self.assertEqual(response.status_code,201);item_id=response.json()["id"];url=f'/{path}/{item_id}'
        self.assertEqual(self.client.patch(url,json=changes,headers=self.customer_headers).status_code,403)
        updated=self.client.patch(url,json=changes,headers=self.headers);self.assertEqual(updated.status_code,200);self.assertEqual(updated.json()["id"],item_id)
        if prefix=="cost_breakdown":self.assertEqual(Decimal(str(updated.json()["total_estimated_landing_storage_cost"])),Decimal("211200"))
        self.assertEqual(self.client.delete(url,headers=self.headers).status_code,204)
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).where(AuditLog.table_name==model.__tablename__).order_by(AuditLog.id)).all()
            self.assertEqual([row.action for row in logs],[prefix+'.'+action for action in ('create','edit','delete')])
            for first,second in zip(logs,logs[1:]):self.assertEqual(audit_values(model,first.new_value),audit_values(model,second.old_value))
            self.assertEqual(len(db.scalars(select(PriceUpdate)).all()),1);self.assertIsNone(db.get(model,item_id))

def attach_test(resource,operation):
    def test(self):getattr(self,operation)(resource)
    test.__name__='test_'+resource[0]+'_'+operation
    setattr(IntelligenceAuditTests,test.__name__,test)
for resource in RESOURCES:
    for operation in ('create_failure','edit_delete_failure','success'):attach_test(resource,operation)
