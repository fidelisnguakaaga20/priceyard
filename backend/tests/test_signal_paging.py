from datetime import datetime, timedelta, timezone
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.quality_signal import QualitySignal
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.market_signal_schema import MarketSignalResponse
from app.schemas.quality_signal_schema import QualitySignalResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records

RESOURCES=((MarketSignal,MarketSignalResponse,"market-signals"),(QualitySignal,QualitySignalResponse,"quality-signals"))
ORDER=(("created_at",True),("id",True))


def seed_signals(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner=User(full_name="Synthetic signal Admin",email="signal-page@example.com",role="admin",password_hash="unused",referral_code="SIGNALPAGE")
        free=User(full_name="Synthetic free",email="signal-free@example.com",role="free_user",password_hash="unused",referral_code="SIGNALFREE")
        free.subscription=Subscription(status="free",plan_name="free")
        trial=User(full_name="Synthetic trial",email="signal-trial@example.com",role="free_user",password_hash="unused",referral_code="SIGNALTRIAL")
        trial.subscription=Subscription(status="trial",plan_name="trial",trial_ends_at=datetime.now(timezone.utc)+timedelta(days=14))
        commodities=[Commodity(name="Egusi"),Commodity(name="Palm oil")];market=Market(name="Kwali Market")
        db.add_all([owner,free,trial,*commodities,market]);db.flush()
        moment=datetime(2026,10,18,8,tzinfo=timezone.utc)
        for index in range(205):
            common=dict(commodity_id=commodities[index==204].id,market_id=market.id,created_by=owner.id,created_at=moment)
            db.add(MarketSignal(**common,signal_type="Synthetic observation",signal_description=f"Synthetic market signal {index:03}",possible_meaning="Saved observation",suggested_action="Watch"))
            db.add(QualitySignal(**common,quality_status="Synthetic observation",risk_note=f"Synthetic quality signal {index:03}"))
        db.commit()
        return owner.id,free.id,trial.id,commodities[0].id


def verify_signal_pages(check,engine):
    _,_,_,commodity=seed_signals(engine)
    with Session(engine) as db:
        before={model:db.execute(select(model.__table__).order_by(model.id)).all() for model,_,_ in RESOURCES}
    for model,schema,_ in RESOURCES:
        ids=[]
        for offset,count in ((0,100),(100,100),(200,5),(300,0)):
            statements=[]
            def observe(*args): statements.append(True)
            event.listen(engine,"before_cursor_execute",observe)
            try:
                with Session(engine) as db:
                    page=admin_record_page(db,model,schema,offset=offset,order=ORDER)
                    check.assertLessEqual(len(db.identity_map),100)
            finally: event.remove(engine,"before_cursor_execute",observe)
            check.assertEqual(len(statements),1)
            check.assertEqual((page.total,len(page.items)),(205,count));ids.extend(row.id for row in page.items)
        check.assertEqual(ids,[row.id for row in reversed(before[model])])
        legacy=json.loads("".join(stream_admin_records(engine,model,schema,order=ORDER)))
        check.assertEqual(ids,[row["id"] for row in legacy])
        scoped=json.loads("".join(stream_admin_records(engine,model,schema,order=ORDER,where=(model.commodity_id==commodity,))))
        check.assertEqual(len(scoped),204)
        check.assertTrue(all(row["commodity_id"]==commodity for row in scoped))
    with Session(engine) as db:
        for model in before:check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(),before[model])


class SignalPagingTests(unittest.TestCase):
    def setUp(self): self.engine=create_engine("sqlite+pysqlite:///:memory:")
    def tearDown(self): app.dependency_overrides.clear();self.engine.dispose()
    def test_complete_pages_ties_scoped_legacy_arrays_and_unchanged_records(self):
        verify_signal_pages(self,self.engine)
    def test_original_access_scopes_and_existing_off_page_id_endpoints(self):
        owner,free,trial,commodity=seed_signals(self.engine)
        def sessions():
            with Session(self.engine) as db:yield db
        app.dependency_overrides[get_db]=sessions
        headers={key:{"Authorization":"Bearer "+create_access_token(user_id=value)} for key,value in (("admin",owner),("free",free),("trial",trial))}
        with TestClient(app) as client:
            for _,_,path in RESOURCES:
                self.assertEqual(client.get('/'+path+'/admin/page').status_code,401)
                for role in ("free","trial"):
                    self.assertEqual(client.get('/'+path+'/admin/page',headers=headers[role]).status_code,403)
                for role in headers:
                    old=client.get('/'+path,headers=headers[role])
                    self.assertEqual(old.status_code,403 if role=="free" and path=="quality-signals" else 200)
                    if old.status_code==200:
                        self.assertEqual(len(old.json()),205)
                        scoped=client.get(f'/{path}?commodity_id={commodity}',headers=headers[role])
                        self.assertEqual(len(scoped.json()),204)
                tail=client.get('/'+path+'/admin/page?offset=200',headers=headers['admin']).json()
                self.assertEqual(len(tail['items']),5)
                self.assertEqual(client.get(f'/{path}/{tail["items"][0]["id"]}',headers=headers['admin']).json(),tail['items'][0])
                self.assertEqual(client.get('/'+path+'/admin/page?offset=-1',headers=headers['admin']).status_code,422)
