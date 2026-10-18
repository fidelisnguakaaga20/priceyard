from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token

MARKERS=("PRIVATE-PUBLICATION-SOURCE-ONE","PRIVATE-PUBLICATION-SOURCE-TWO")


def verify_source_publication(check,engine):
    Base.metadata.create_all(engine)
    now=datetime.now(timezone.utc);headers={"guest":{}}
    with Session(engine) as db:
        for name,role,status in (("free","free_user","free"),("trial","free_user","trial"),
                ("paid","paid_user","active"),("reporter","reporter","free"),("admin","admin","free")):
            user=User(full_name="Synthetic publication "+name,email=name+"-publication@example.com",password_hash="unused",role=role,referral_code="PUB"+name.upper())
            user.subscription=Subscription(status=status,plan_name="trial" if status=="trial" else "paid_monthly" if status=="active" else "free",
                trial_started_at=now if status=="trial" else None,trial_ends_at=now+timedelta(days=14) if status=="trial" else None,
                end_date=(now+timedelta(days=14)).date() if status=="active" else None)
            db.add(user);db.flush();headers[name]={"Authorization":"Bearer "+create_access_token(user_id=user.id)}
            if name=="admin":owner=user.id
        commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([commodity,market]);db.flush();commodity_id=commodity.id
        ids=[]
        for age in (2,0):
            row=PriceUpdate(commodity_id=commodity.id,market_id=market.id,price_low=210000,price_high=220000,
                unit="1 bag",bag_size=None,movement="unknown",confidence_level="Low confidence",status="approved",created_by=owner,
                update_date_time=now-timedelta(days=age),source_type="Synthetic generic category",source_1=MARKERS[0],source_2=MARKERS[1],
                notes="Existing public market note",possible_meaning="Existing public observation",suggested_action="Watch")
            db.add(row);db.flush();ids.append(row.id)
        legacy=AuditLog(user_id=owner,action="synthetic.publication",table_name="price_updates",record_id=ids[1],
            old_value={"notes":"Retained public audit note","source_1":MARKERS[0]},
            new_value={"nested":[{"SOURCE_2":MARKERS[1],"status":"approved"}]})
        db.add(legacy);db.commit();audit_id=legacy.id
        before={model:db.execute(select(model.__table__).order_by(model.id)).all() for model in (PriceUpdate,AuditLog)}
    def sessions():
        with Session(engine) as db:yield db
    app.dependency_overrides[get_db]=sessions
    try:
        with TestClient(app) as client:
            for role,auth in headers.items():
                for path in ("/price-updates",f"/price-updates/{ids[1]}"):
                    response=client.get(path,headers=auth);check.assertEqual(response.status_code,200)
                    rows=response.json() if isinstance(response.json(),list) else [response.json()]
                    for row in rows:
                        check.assertNotIn("source_1",row);check.assertNotIn("source_2",row)
                        check.assertEqual(row["source_type"],"Synthetic generic category")
                        check.assertEqual(row["notes"],"Existing public market note")
                        check.assertEqual(row["possible_meaning"],"Existing public observation")
                    for marker in MARKERS:check.assertNotIn(marker,response.text)
                for path in ("/price-updates/history",f"/price-updates/{ids[0]}"):
                    response=client.get(path,headers=auth)
                    check.assertEqual(response.status_code,200 if role in ("trial","paid","admin") else 401 if role=="guest" else 403)
                    for marker in MARKERS:check.assertNotIn(marker,response.text)
                admin_history=client.get("/price-updates/admin/history",headers=auth)
                check.assertEqual(admin_history.status_code,200 if role=="admin" else 401 if role=="guest" else 403)
                if role=="admin":
                    for row in admin_history.json():check.assertEqual((row["source_1"],row["source_2"]),MARKERS)
                for path in ("/reports/prices.csv","/audit-logs","/audit-logs/page",f"/audit-logs/{audit_id}"):
                    response=client.get(path,headers=auth)
                    check.assertEqual(response.status_code,200 if role=="admin" else 401 if role=="guest" else 403)
                    for marker in MARKERS:check.assertNotIn(marker,response.text)
            for path in (f"/share/commodities/Egusi?commodity_id={commodity_id}",f"/share/commodities/Egusi?pu={ids[0]}"):
                response=client.get(path);check.assertEqual(response.status_code,200)
                for marker in MARKERS:check.assertNotIn(marker,response.text)
            with Session(engine) as db:
                for model in before:check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(),before[model])
    finally:app.dependency_overrides.clear()


class SourcePublicationTests(unittest.TestCase):
    def test_approved_source_policy_preserves_role_access_public_guidance_and_raw_history(self):
        engine=create_engine("sqlite+pysqlite:///:memory:")
        try:verify_source_publication(self,engine)
        finally:engine.dispose()
