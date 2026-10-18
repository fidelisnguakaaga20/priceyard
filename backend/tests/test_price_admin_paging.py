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
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import PriceUpdateAdminResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records
from app.services.price_flag_service import flagged_price_page, stream_flagged_prices


def seed_price_pages(engine):
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as db:
        owner = User(full_name="Synthetic Admin", email="price-page-admin@example.com", role="admin", password_hash="unused", referral_code="PPADMIN")
        other = User(full_name="Synthetic Free", email="price-page-free@example.com", role="free_user", password_hash="unused", referral_code="PPFREE")
        commodities = [Commodity(name="Egusi"), Commodity(name="Palm oil")]; market = Market(name="Kwali Market")
        db.add_all([owner, other, *commodities, market]); db.flush()
        for index in range(205):
            item = PriceUpdate(commodity_id=commodities[index != 0].id, market_id=market.id,
                price_low=210000+index, price_high=220000+index, unit="1 bag", bag_size=None,
                movement="unknown", confidence_level="Low confidence", status=('rejected', 'pending', 'approved')[index % 3],
                update_date_time=now-timedelta(days=2) if index == 0 else now,
                created_by=owner.id, source_1="PRIVATE-PAGE-SOURCE", notes="Saved public note")
            db.add(item); db.flush()
            db.add(PriceFlag(price_update_id=item.id, user_id=other.id, reason="Synthetic flag", created_at=now))
            if index in (0, 204):
                db.add(PriceFlag(price_update_id=item.id, user_id=owner.id, reason="Synthetic extra", resolved=index == 0, created_at=now))
        db.commit()
        return owner.id, other.id, commodities[0].id, market.id


def verify_price_admin_pages(check, engine):
    owner, other, commodity, market = seed_price_pages(engine)
    with Session(engine) as db:
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all()
                  for model in (PriceUpdate, PriceFlag, Commodity, Market)}
    ids, flags = [], []
    for offset, count in ((0, 100), (100, 100), (200, 5), (300, 0)):
        for flag_page in (False, True):
            statements = []
            def observe(*args): statements.append(True)
            event.listen(engine, 'before_cursor_execute', observe)
            try:
                with Session(engine) as db:
                    page = flagged_price_page(db, offset=offset) if flag_page else admin_record_page(db, PriceUpdate,
                        PriceUpdateAdminResponse, offset=offset, order=(("update_date_time", True), ("id", True)), related=("commodity", "market"))
                    check.assertLessEqual(len(db.identity_map), 103)
            finally: event.remove(engine, 'before_cursor_execute', observe)
            check.assertEqual(len(statements), 1)
            check.assertEqual((page.total, len(page.items)), (205, count))
            if flag_page: flags.extend(page.items)
            else:
                ids.extend(row.id for row in page.items)
                check.assertTrue(all(row.source_1 == 'PRIVATE-PAGE-SOURCE' and row.market.name == 'Kwali Market' for row in page.items))
    expected = [row.id for row in reversed(before[PriceUpdate])]
    check.assertEqual(ids, expected); check.assertEqual([row.price_update_id for row in flags], expected)
    check.assertEqual([row.flag_count for row in flags], [2] + [1] * 204)
    legacy = json.loads(''.join(stream_admin_records(engine, PriceUpdate, PriceUpdateAdminResponse,
        order=(("update_date_time", True), ("id", True)), related=("commodity", "market"))))
    check.assertEqual([row['id'] for row in legacy], expected)
    check.assertEqual([row['price_update_id'] for row in json.loads(''.join(stream_flagged_prices(engine)))], expected)
    overrides = app.dependency_overrides.copy()
    def sessions():
        with Session(engine) as db: yield db
    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app) as client:
            admin = {'Authorization': 'Bearer ' + create_access_token(user_id=owner)}
            free = {'Authorization': 'Bearer ' + create_access_token(user_id=other)}
            latest = f'/price-updates/admin/latest?commodity_id={commodity}&market_id={market}'
            for path in ('/price-updates/admin/history', '/price-updates/admin/history/page', '/price-updates/admin/flagged', '/price-updates/admin/flagged/page', latest):
                check.assertEqual(client.get(path).status_code, 401)
                check.assertEqual(client.get(path, headers=free).status_code, 403)
            row = client.get(latest, headers=admin).json()
            check.assertEqual((row['id'], row['status'], row['source_1']), (before[PriceUpdate][0].id, 'rejected', 'PRIVATE-PAGE-SOURCE'))
            check.assertEqual(client.get(latest.replace(f'commodity_id={commodity}', 'commodity_id=999999'), headers=admin).json(), None)
            for path in ('history', 'flagged'):
                page = client.get(f'/price-updates/admin/{path}/page?offset=200', headers=admin).json()
                check.assertEqual((page['total'], len(page['items'])), (205, 5))
                check.assertEqual(client.get(f'/price-updates/admin/{path}/page?offset=-1', headers=admin).status_code, 422)
                check.assertEqual(len(client.get('/price-updates/admin/' + path, headers=admin).json()), 205)
            public = client.get('/price-updates').json()
            check.assertNotIn('PRIVATE-PAGE-SOURCE', json.dumps(public))
    finally:
        app.dependency_overrides.clear(); app.dependency_overrides.update(overrides)
    with Session(engine) as db:
        for model in before:
            check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(), before[model])


class PriceAdminPagingTests(unittest.TestCase):
    def test_prices_flags_complete_counts_privacy_latest_pair_and_preserved_records(self):
        engine = create_engine('sqlite+pysqlite:///:memory:')
        try: verify_price_admin_pages(self, engine)
        finally: engine.dispose()
