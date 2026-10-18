from datetime import date, datetime, timedelta, timezone
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.buying_zone import BuyingZone
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.sell_watch_window import SellWatchWindow
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.buying_zone_schema import BuyingZoneResponse
from app.schemas.sell_watch_window_schema import SellWatchWindowResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records

RESOURCES = ((BuyingZone, BuyingZoneResponse, "buying-zones"),
             (SellWatchWindow, SellWatchWindowResponse, "sell-watch-windows"))
ORDER = (("created_at", True), ("id", True))


def seed_windows(engine):
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as db:
        people = {}
        for name, role, status in (("admin", "admin", "free"), ("free", "free_user", "free"),
                ("trial", "free_user", "trial"), ("paid", "paid_user", "active"),
                ("reporter", "reporter", "free")):
            user = User(full_name="Synthetic " + name, email=name + "-windows@example.com",
                        role=role, password_hash="unused", referral_code="WIN" + name.upper())
            user.subscription = Subscription(status=status, plan_name="paid_monthly" if status == "active" else status,
                trial_ends_at=now + timedelta(days=14) if status == "trial" else None,
                end_date=(now + timedelta(days=30)).date() if status == "active" else None)
            db.add(user); db.flush(); people[name] = user.id
        commodities = [Commodity(name="Egusi"), Commodity(name="Palm oil")]
        market = Market(name="Kwali Market")
        db.add_all([*commodities, market]); db.flush()
        for index in range(205):
            common = dict(commodity_id=commodities[index == 204].id, market_id=market.id,
                          created_by=people["admin"], created_at=now)
            db.add(BuyingZone(**common, price_low=210000, price_high=220000,
                reason=f"Synthetic observation {index:03}", confidence="Saved confidence",
                valid_from=date(2026, 10, 1), valid_to=date(2026, 10, 31)))
            db.add(SellWatchWindow(**common, start_period="Existing start", end_period="Existing end",
                observation=f"Synthetic observation {index:03}", confidence="Saved confidence"))
        db.commit()
        return people, commodities[0].id


def verify_window_pages(check, engine):
    _, commodity = seed_windows(engine)
    with Session(engine) as db:
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all()
                  for model, _, _ in RESOURCES}
    for model, schema, _ in RESOURCES:
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
            check.assertTrue(all(row.disclaimer == schema.model_fields["disclaimer"].default for row in page.items))
            ids.extend(row.id for row in page.items)
        check.assertEqual(ids, [row.id for row in reversed(before[model])])
        legacy = json.loads("".join(stream_admin_records(engine, model, schema, order=ORDER)))
        check.assertEqual(ids, [row["id"] for row in legacy])
        scoped = json.loads("".join(stream_admin_records(engine, model, schema, order=ORDER,
                                                       where=(model.commodity_id == commodity,))))
        check.assertEqual(len(scoped), 204)
        check.assertTrue(all(row["commodity_id"] == commodity for row in scoped))
    with Session(engine) as db:
        for model in before:
            check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(), before[model])


class TradeWindowPagingTests(unittest.TestCase):
    def setUp(self): self.engine = create_engine("sqlite+pysqlite:///:memory:")
    def tearDown(self): app.dependency_overrides.clear(); self.engine.dispose()

    def test_complete_tied_pages_streams_disclaimers_and_unchanged_saved_values(self):
        verify_window_pages(self, self.engine)

    def test_original_premium_access_and_existing_off_page_ids(self):
        people, commodity = seed_windows(self.engine)
        def sessions():
            with Session(self.engine) as db: yield db
        app.dependency_overrides[get_db] = sessions
        headers = {name: {"Authorization": "Bearer " + create_access_token(user_id=user_id)}
                   for name, user_id in people.items()}
        with TestClient(app) as client:
            for _, schema, path in RESOURCES:
                self.assertEqual(client.get('/' + path + '/admin/page').status_code, 401)
                self.assertEqual(client.get('/' + path).status_code, 401)
                for role in headers:
                    response = client.get('/' + path + '/admin/page', headers=headers[role])
                    self.assertEqual(response.status_code, 200 if role == "admin" else 403)
                    legacy = client.get('/' + path, headers=headers[role])
                    self.assertEqual(legacy.status_code, 403 if role in {"free", "reporter"} else 200)
                    if legacy.status_code == 200:
                        self.assertEqual(len(legacy.json()), 205)
                        self.assertEqual(len(client.get(f'/{path}?commodity_id={commodity}', headers=headers[role]).json()), 204)
                        self.assertEqual(legacy.headers['cache-control'], 'private, no-store')
                tail = client.get('/' + path + '/admin/page?offset=200', headers=headers['admin']).json()
                self.assertEqual((tail['total'], len(tail['items'])), (205, 5))
                row = tail['items'][0]
                self.assertEqual(row['disclaimer'], schema.model_fields['disclaimer'].default)
                for role in headers:
                    detail = client.get(f'/{path}/{row["id"]}', headers=headers[role])
                    self.assertEqual(detail.status_code, 403 if role in {'free', 'reporter'} else 200)
                    if detail.status_code == 200: self.assertEqual(detail.json(), row)
                for offset in (-1, 2_147_483_648):
                    self.assertEqual(client.get(f'/{path}/admin/page?offset={offset}', headers=headers['admin']).status_code, 422)
