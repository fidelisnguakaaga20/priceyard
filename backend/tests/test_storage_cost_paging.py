from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.storage_suitability import StorageSuitability
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.cost_breakdown_schema import CostBreakdownResponse
from app.schemas.storage_suitability_schema import StorageSuitabilityResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records

RESOURCES = ((StorageSuitability, StorageSuitabilityResponse, "storage-suitability"),
             (CostBreakdown, CostBreakdownResponse, "cost-breakdowns"))
ORDER = (("created_at", True), ("id", True))


def verify_storage_cost_pages(check, engine):
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as db:
        people = {}
        for name, role, status in (("admin", "admin", "free"), ("free", "free_user", "free"),
                ("trial", "free_user", "trial"), ("paid", "paid_user", "active"), ("reporter", "reporter", "free")):
            user = User(full_name="Synthetic " + name, email=name + "-cost-page@example.com",
                        role=role, password_hash="unused", referral_code="SC" + name.upper())
            user.subscription = Subscription(status=status, plan_name="paid_monthly" if status == "active" else status,
                trial_ends_at=now + timedelta(days=14) if status == "trial" else None,
                end_date=(now + timedelta(days=30)).date() if status == "active" else None)
            db.add(user); db.flush(); people[name] = user.id
        commodities = [Commodity(name="Egusi"), Commodity(name="Palm oil")]
        market = Market(name="Kwali Market")
        db.add_all([*commodities, market]); db.flush()
        commodity = commodities[0].id
        for index in range(205):
            common = dict(commodity_id=commodities[index == 204].id, market_id=market.id, created_at=now)
            price = PriceUpdate(commodity_id=common['commodity_id'], market_id=market.id, price_low=210000,
                price_high=220000, unit="1 bag", bag_size=None, movement="unknown", confidence_level="Low confidence",
                status="approved", update_date_time=now, created_by=people['admin'])
            db.add(price); db.flush()
            db.add(StorageSuitability(**common, price_update_id=price.id, suitability_status="watch",
                quality_storage_notes=f"Synthetic saved storage note {index:03}", summary="Saved summary"))
            db.add(CostBreakdown(**common, transport=Decimal('120.50'), warehouse=Decimal('80.25'), security=0,
                market_charges=Decimal('20.75'), loading_offloading=30, other_costs=Decimal('10.10'),
                total_additional_cost=Decimal('261.60'), purchase_price_reference=210000,
                total_estimated_landing_storage_cost=Decimal('210261.60')))
        db.commit()
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all()
                  for model in (StorageSuitability, CostBreakdown, PriceUpdate)}
    for model, schema, path in RESOURCES:
        ids = []
        for offset, count in ((0, 100), (100, 100), (200, 5), (300, 0)):
            statements = []
            def observe(*args): statements.append(True)
            event.listen(engine, "before_cursor_execute", observe)
            try:
                with Session(engine) as db:
                    page = admin_record_page(db, model, schema, offset=offset, order=ORDER)
                    check.assertLessEqual(len(db.identity_map), 100)
            finally:
                event.remove(engine, "before_cursor_execute", observe)
            check.assertEqual(len(statements), 1)
            check.assertEqual((page.total, len(page.items)), (205, count))
            for row in page.items:
                if model is CostBreakdown:
                    check.assertEqual(row.total_additional_cost, Decimal('261.60'))
                    check.assertEqual(row.total_estimated_landing_storage_cost, row.purchase_price_reference + row.total_additional_cost)
                    check.assertEqual(row.security, 0)
                else:
                    check.assertEqual(row.disclaimer, schema.model_fields['disclaimer'].default)
                    check.assertIsNotNone(row.price_update_id)
            ids.extend(row.id for row in page.items)
        check.assertEqual(ids, [row.id for row in reversed(before[model])])
        check.assertEqual(ids, [row['id'] for row in json.loads(''.join(stream_admin_records(engine, model, schema, order=ORDER)))])
        scoped = json.loads(''.join(stream_admin_records(engine, model, schema, order=ORDER, where=(model.commodity_id == commodity,))))
        check.assertEqual(len(scoped), 204)
        check.assertTrue(all(row['commodity_id'] == commodity for row in scoped))
    overrides = app.dependency_overrides.copy()
    def sessions():
        with Session(engine) as db: yield db
    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app) as client:
            for model, _, path in RESOURCES:
                check.assertEqual(client.get('/' + path + '/admin/page').status_code, 401)
                for name, user_id in people.items():
                    headers = {'Authorization': 'Bearer ' + create_access_token(user_id=user_id)}
                    check.assertEqual(client.get('/' + path + '/admin/page', headers=headers).status_code, 200 if name == 'admin' else 403)
                    response = client.get(f'/{path}?commodity_id={commodity}', headers=headers)
                    check.assertEqual(response.status_code, 403 if name in {'free', 'reporter'} else 200)
                    if response.status_code == 200:
                        check.assertEqual(len(response.json()), 204)
                        check.assertEqual(response.headers['cache-control'], 'private, no-store')
                    detail = client.get(f'/{path}/{before[model][0].id}', headers=headers)
                    check.assertEqual(detail.status_code, 403 if name in {'free', 'reporter'} else 200)
                admin = {'Authorization': 'Bearer ' + create_access_token(user_id=people['admin'])}
                check.assertEqual(len(client.get('/' + path, headers=admin).json()), 205)
                check.assertEqual(len(client.get('/' + path + '/admin/page?offset=200', headers=admin).json()['items']), 5)
                check.assertEqual(client.get('/' + path + '/admin/page?offset=-1', headers=admin).status_code, 422)
    finally:
        app.dependency_overrides.clear(); app.dependency_overrides.update(overrides)
    with Session(engine) as db:
        for model in before:
            check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(), before[model])


class StorageCostPagingTests(unittest.TestCase):
    def test_pages_preserve_original_costs_links_values_and_premium_access(self):
        engine = create_engine('sqlite+pysqlite:///:memory:')
        try: verify_storage_cost_pages(self, engine)
        finally: engine.dispose()
