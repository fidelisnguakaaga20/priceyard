from datetime import datetime, timedelta, timezone
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import PriceUpdateCreate, PriceUpdateUpdate
from app.services.price_update_service import create_price_update, update_price_update, approve_price_update


def verify_claim_evidence(check, engine):
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as db:
        owner = User(full_name='Synthetic claim editor', email='claims@example.com', role='admin', password_hash='unused', referral_code='CLAIMS')
        reporter = User(full_name='Synthetic claim reporter', email='claims-reporter@example.com', role='reporter', password_hash='unused', referral_code='CLAIMREPORTER')
        commodity, market = Commodity(name='Egusi'), Market(name='Kwali Market')
        db.add_all([owner,reporter,commodity,market]); db.flush()
        common = dict(commodity_id=commodity.id,market_id=market.id,unit='recorded quantity one',
            bag_size='recorded size one',commodity_type='recorded type one',price_low=100,price_high=200,
            average_price=150,confidence_level='Low confidence',movement='unknown',suggested_action='Watch')
        prior = PriceUpdate(**common,status='approved',created_by=owner.id,update_date_time=now-timedelta(days=1))
        # Newer pending/outdated/different-measurement records cannot provide evidence.
        db.add(prior)
        for changes in ({'status':'pending'}, {'status':'approved','is_outdated':True}, {'status':'approved','bag_size':'recorded size two'}):
            db.add(PriceUpdate(**{**common,**changes},created_by=owner.id,update_date_time=now-timedelta(hours=1)))
        legacy = PriceUpdate(**{**common,'movement':'up','bag_size':None,'confidence_level':'Verified by 2 sources'},
            status='pending',created_by=owner.id,update_date_time=now+timedelta(hours=1),source_1='SAME-PRIVATE',source_2='same-private')
        db.add(legacy); db.commit(); owner_id,reporter_id,legacy_id=owner.id,reporter.id,legacy.id
        before=db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
    accepted=0; rejected=0
    for movement,low,high,valid in (('up',110,210,True),('down',90,190,True),('stable',100,200,True),
            ('up',90,210,False),('down',110,190,False),('stable',100,210,False),('up',100,210,False),('unknown',90,210,True)):
        with Session(engine) as db:
            payload=PriceUpdateCreate(**{**common,'movement':movement,'price_low':low,'price_high':high,
                'average_price':(low+high)/2,'update_date_time':now})
            if valid:
                item=create_price_update(db,payload,db.get(User,reporter_id),commit=False)
                check.assertEqual(item.movement,movement); accepted+=1
            else:
                with check.assertRaises(HTTPException) as error:create_price_update(db,payload,db.get(User,reporter_id),commit=False)
                check.assertEqual(error.exception.status_code,422); rejected+=1
            db.rollback()
    for changes in ({'bag_size':'Unknown'},{'commodity_type':None},{'unit':'recorded quantity two'},
                    {'update_date_time':now-timedelta(days=1)}, {'update_date_time':now-timedelta(days=2)},
                    {'previous_price_low':99,'previous_price_high':200}):
        with Session(engine) as db:
            payload=PriceUpdateCreate(**{**common,'movement':'up','price_low':110,'price_high':210,'average_price':160,
                                       'update_date_time':now,**changes})
            with check.assertRaises(HTTPException):create_price_update(db,payload,db.get(User,reporter_id),commit=False)
            db.rollback(); rejected+=1
    for a,b,valid in ((None,None,False),('PRIVATE-ONE',None,False),(' PRIVATE-ONE ','private-one',False),('PRIVATE-ONE','PRIVATE-TWO',True)):
        with Session(engine) as db:
            payload=PriceUpdateCreate(**{**common,'update_date_time':now,'confidence_level':'Verified by 2 sources','source_1':a,'source_2':b})
            if valid:
                item=create_price_update(db,payload,db.get(User,owner_id),commit=False);check.assertEqual(item.source_2,b)
            else:
                with check.assertRaises(HTTPException) as error:create_price_update(db,payload,db.get(User,owner_id),commit=False)
                check.assertNotIn('PRIVATE-ONE',error.exception.detail)
            db.rollback()
    with Session(engine) as db:
        legacy=db.get(PriceUpdate,legacy_id)
        update_price_update(db,legacy,PriceUpdateUpdate(notes='Unrelated historical correction'),commit=False)
        check.assertEqual((legacy.movement,legacy.confidence_level),('up','Verified by 2 sources'))
        db.rollback()
        with check.assertRaises(HTTPException):approve_price_update(db,db.get(PriceUpdate,legacy_id),db.get(User,owner_id),commit=False)
        db.rollback()
        with check.assertRaises(HTTPException):update_price_update(db,db.get(PriceUpdate,legacy_id),PriceUpdateUpdate(price_low=99),commit=False)
        db.rollback()
        check.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(),before)
    check.assertEqual((accepted,rejected),(4,10))


class PriceClaimEvidenceTests(unittest.TestCase):
    def test_new_claims_require_evidence_without_rewriting_history(self):
        engine=create_engine('sqlite+pysqlite:///:memory:')
        try: verify_claim_evidence(self,engine)
        finally: engine.dispose()
