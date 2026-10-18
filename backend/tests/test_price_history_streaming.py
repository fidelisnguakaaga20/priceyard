from datetime import date, datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch

import anyio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.price_update_schema import PriceUpdatePublicResponse
from app.security import create_access_token
from app.services.admin_list_service import AdminJSONResponse
from app.services.price_update_service import list_price_history, stream_price_history


def seed_history(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner=User(full_name='Synthetic history Admin',email='history-stream@example.com',role='admin',password_hash='unused',referral_code='HISTSTREAM')
        free=User(full_name='Synthetic history Free',email='history-free@example.com',role='free_user',password_hash='unused',referral_code='HISTORYFREE')
        free.subscription=Subscription(plan_name='free',status='free')
        commodity=Commodity(name='Egusi');hidden=Commodity(name='Palm oil',is_active=False)
        market=Market(name='Kwali Market');hidden_market=Market(name='Inactive synthetic market',is_active=False)
        db.add_all([owner,free,commodity,hidden,market,hidden_market]);db.flush()
        now=datetime(2026,10,1,23,tzinfo=timezone.utc)
        for index in range(255):
            db.add(PriceUpdate(commodity_id=hidden.id if index==253 else commodity.id,
                market_id=hidden_market.id if index==254 else market.id,
                price_low=100+index,price_high=200+index,unit='1 bag',bag_size=None,commodity_type=None,
                confidence_level='Low confidence',movement='unknown' if index%2 else 'stable',
                time_of_day='morning' if index%2 else 'evening',is_outdated=index==0,
                update_date_time=now+timedelta(days=index//100),created_by=owner.id,
                status='pending' if index==251 else 'rejected' if index==252 else 'approved',
                source_1='PRIVATE-HISTORY-REFERENCE',notes='Saved public history note'))
        db.commit();return owner.id,free.id,commodity.id,market.id


def verify_history_stream(check,engine):
    owner,free,commodity,market=seed_history(engine)
    with Session(engine) as db:
        before=db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
        expected=[PriceUpdatePublicResponse.model_validate(row).model_dump(mode='json') for row in list_price_history(db)]
    loaded=[];counts=[];queries=[]
    def observe(db,instance):
        if isinstance(instance,PriceUpdate):
            loaded.append(instance.id);counts.append(sum(isinstance(value,PriceUpdate) for value in db.identity_map.values()))
    def query(*args):queries.append(True)
    event.listen(Session,'loaded_as_persistent',observe);event.listen(engine,'before_cursor_execute',query)
    try:
        stream=stream_price_history(engine)
        check.assertEqual(next(stream),'[');check.assertEqual(loaded,[])
        first=next(stream);check.assertLessEqual(len(loaded),100)
        content='['+first+''.join(stream)
    finally:
        event.remove(Session,'loaded_as_persistent',observe);event.remove(engine,'before_cursor_execute',query)
    rows=json.loads(content)
    check.assertEqual(rows,expected);check.assertEqual(len(rows),251)
    check.assertEqual(len(queries),1);check.assertLessEqual(max(counts),200)
    check.assertEqual(len(loaded),251);check.assertTrue(rows[0]['is_outdated'])
    check.assertTrue(all(row['bag_size'] is None and row['commodity_type'] is None for row in rows))
    check.assertNotIn('PRIVATE-HISTORY',content);check.assertNotIn('source_1',content)
    filters={'commodity_search':'gusi','market_search':'wali','commodity_id':commodity,'market_id':market,
             'selected_date':date(2026,10,2),'movement':'unknown','time_of_day':'morning'}
    selected=json.loads(''.join(stream_price_history(engine,**filters)))
    check.assertEqual([row['id'] for row in selected],[row['id'] for row in rows[:100] if row['movement']=='unknown'])
    for filters in ({'commodity_search':'No match'},{'commodity_id':commodity+999},{'market_id':market+999}):
        check.assertEqual(json.loads(''.join(stream_price_history(engine,**filters))),[])
    stream=stream_price_history(engine);next(stream);next(stream);stream.close()
    if hasattr(engine.pool,'checkedout'):check.assertEqual(engine.pool.checkedout(),0)
    def sessions():
        with Session(engine) as db:yield db
    app.dependency_overrides[get_db]=sessions
    try:
        with TestClient(app) as client:
            check.assertEqual(client.get('/price-updates/history').status_code,401)
            headers={'Authorization':'Bearer '+create_access_token(user_id=free)}
            check.assertEqual(client.get('/price-updates/history',headers=headers).status_code,403)
            headers={'Authorization':'Bearer '+create_access_token(user_id=owner)}
            response=client.get('/price-updates/history',headers=headers)
            check.assertEqual(response.status_code,200,response.text);check.assertEqual(response.json(),rows)
            check.assertNotIn('content-length',response.headers);check.assertIn('no-store',response.headers['cache-control'])
            check.assertEqual(client.get('/price-updates/history?date=not-a-date',headers=headers).status_code,422)
    finally:app.dependency_overrides.clear()
    with Session(engine) as db:check.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(),before)


class PriceHistoryStreamingTests(unittest.TestCase):
    def setUp(self):self.engine=create_engine('sqlite+pysqlite:///:memory:')
    def tearDown(self):app.dependency_overrides.clear();self.engine.dispose()

    def test_complete_history_filters_privacy_bounded_hydration_and_permissions(self):
        verify_history_stream(self,self.engine)

    def test_database_failure_closes_owned_session(self):
        with patch('app.services.admin_list_service.Session') as sessions:
            sessions.return_value.__enter__.return_value.scalars.side_effect=RuntimeError('Synthetic history query failure')
            with self.assertRaises(RuntimeError):next(stream_price_history(self.engine))
            sessions.return_value.__exit__.assert_called_once()

    def test_disconnected_history_response_closes_real_cursor_and_session(self):
        seed_history(self.engine)
        opened=[]
        class ObservedSession(Session):
            def close(self):opened.append('closed');super().close()
        async def send(message):
            if message['type']=='http.response.body':raise OSError('Synthetic history disconnect')
        async def receive():return {'type':'http.disconnect'}
        async def run():
            with self.assertRaises(Exception):
                await AdminJSONResponse(stream_price_history(self.engine))({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
        with patch('app.services.admin_list_service.Session',ObservedSession):anyio.run(run)
        self.assertEqual(opened,['closed'])
