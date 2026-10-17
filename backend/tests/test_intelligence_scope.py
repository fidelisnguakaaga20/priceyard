"""Commodity pages must not hydrate every unrelated intelligence record."""
from datetime import datetime, timedelta, timezone
import importlib
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.buying_zone import BuyingZone
from app.models.sell_watch_window import SellWatchWindow
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token

RESOURCES = (
    ("buying_zone", "buying-zones", BuyingZone,
     {"price_low": 210000, "price_high": 220000, "reason": "Synthetic scope observation", "confidence": "Low confidence"}, {}),
    ("sell_watch_window", "sell-watch-windows", SellWatchWindow,
     {"start_period": "Synthetic recorded period", "observation": "Synthetic scope observation", "confidence": "Low confidence"}, {}),
    ("market_signal", "market-signals", MarketSignal,
     {"signal_type": "Synthetic scope", "signal_description": "Synthetic scope observation"}, {}),
    ("quality_signal", "quality-signals", QualitySignal,
     {"quality_status": "Synthetic scope", "risk_note": "Synthetic scope observation"}, {}),
    ("cost_breakdown", "cost-breakdowns", CostBreakdown,
     {"purchase_price_reference": 210000, "transport": 120, "warehouse": 80}, {}),
)


def seed_scope_records(db):
    now = datetime.now(timezone.utc)
    admin = User(full_name="Synthetic scope Admin", email="scope-admin@example.com", password_hash="unused", role="admin", referral_code="SCOPEADMIN")
    free = User(full_name="Synthetic scope user", email="scope-user@example.com", password_hash="unused", role="free_user", referral_code="SCOPEUSER")
    egusi, palm, market = Commodity(name="Egusi"), Commodity(name="Palm oil"), Market(name="Kwali Market")
    db.add_all([admin, free, egusi, palm, market])
    db.flush()
    db.add(Subscription(user_id=free.id, status="free", plan_name="free"))
    price = PriceUpdate(commodity_id=egusi.id, market_id=market.id, unit="1 bag", bag_size=None, price_low=210000, price_high=220000,
                        status="approved", movement="unknown", confidence_level="Low confidence", created_by=admin.id, update_date_time=now)
    db.add(price)
    expected = {}
    for kind, _, model, values, _ in RESOURCES:
        expected[kind] = []
        for index in range(42):
            target = index in (0, 41)
            fields = {**values, "commodity_id": egusi.id if target else palm.id, "market_id": market.id,
                      "created_at": now + timedelta(seconds=index)}
            if kind == "cost_breakdown":
                fields.update(total_additional_cost=200, total_estimated_landing_storage_cost=210200)
            else:
                fields["created_by"] = admin.id
            item = model(**fields)
            db.add(item)
            db.flush()
            if target:
                expected[kind].insert(0, item.id)
    db.commit()
    return {"admin": admin.id, "free": free.id, "commodity": egusi.id, "expected": expected}


class IntelligenceScopeTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            self.fixture = seed_scope_records(db)
        self.headers = {"Authorization": "Bearer " + create_access_token(user_id=self.fixture["admin"])}
        self.free_headers = {"Authorization": "Bearer " + create_access_token(user_id=self.fixture["free"])}

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return {model.__tablename__: db.execute(select(model.__table__)).all()
                    for model in [PriceUpdate, *(row[2] for row in RESOURCES)]}

    def http_scope(self, resource):
        kind, endpoint, _, _, _ = resource
        before = self.state()
        url = "/" + endpoint
        response = self.client.get(url, params={"commodity_id": self.fixture["commodity"]}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], self.fixture["expected"][kind])
        self.assertEqual(len(self.client.get(url, headers=self.headers).json()), 42)
        self.assertEqual(self.client.get(url, params={"commodity_id": 999999}, headers=self.headers).json(), [])
        self.assertEqual(self.client.get(url, params={"commodity_id": 0}, headers=self.headers).status_code, 422)
        self.assertEqual(self.client.get(url, params={"commodity_id": self.fixture["commodity"]}).status_code, 401)
        self.assertEqual(self.client.get(url, params={"commodity_id": self.fixture["commodity"]}, headers=self.free_headers).status_code,
                         200 if kind == "market_signal" else 403)
        self.assertEqual(self.state(), before)

    def bounded_hydration(self, resource):
        kind, _, model, _, _ = resource
        service = importlib.import_module("app.services." + kind + "_service")
        name = {"market_signal": "list_market_signals", "quality_signal": "list_quality_signals", "cost_breakdown": "list_cost_breakdowns", "buying_zone": "list_buying_zones", "sell_watch_window": "list_sell_watch_windows"}[kind]
        with Session(self.engine) as db:
            loaded = []
            event.listen(db, "loaded_as_persistent", lambda session, item: loaded.append(item.id) if isinstance(item, model) else None)
            rows = getattr(service, name)(db, commodity_id=self.fixture["commodity"])
            self.assertEqual([item.id for item in rows], self.fixture["expected"][kind])
            self.assertEqual(loaded, self.fixture["expected"][kind])


def attach(resource, operation):
    def test(self):
        getattr(self, operation)(resource)
    test.__name__ = "test_" + resource[0] + "_" + operation
    setattr(IntelligenceScopeTests, test.__name__, test)


for resource in RESOURCES:
    for operation in ("http_scope", "bounded_hydration"):
        attach(resource, operation)
