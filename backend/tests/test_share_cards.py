"""Public share cards keep exact identity, measurement and current-only scope."""
from datetime import datetime, timedelta, timezone
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
import app.models  # noqa: F401
from app.database import Base, get_db
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.routes.share_routes import router

class ShareCardTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(full_name="Synthetic admin", email="share@fixture.test", password_hash="unused", role="admin", referral_code="SHARE")
        self.beans = Commodity(name="Beans", is_active=True)
        self.honey = Commodity(name="Honey Beans", is_active=True)
        self.market = Market(name="Synthetic market", state="Synthetic state", is_active=True)
        self.db.add_all([self.user, self.beans, self.honey, self.market]); self.db.flush()
        self.when = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.first = self.price(self.beans, 100, "50kg", "A")
        self.second = self.price(self.beans, 200, "25kg", "B")
        self.price(self.honey, 999, "50kg", "A")
        self.db.commit()
        app = FastAPI(); app.include_router(router)
        def db_override(): yield self.db
        app.dependency_overrides[get_db] = db_override
        self.client = TestClient(app)
    def tearDown(self):
        self.client.close(); self.db.close(); self.engine.dispose()
    def price(self, commodity, value, size, grade, when=None):
        record = PriceUpdate(commodity_id=commodity.id, market_id=self.market.id, price_low=value, price_high=value,
            average_price=None, unit="2 bags", bag_size=size, grade=grade, movement="unknown", confidence_level="Admin confirmed",
            update_date_time=when or self.when, status="approved", created_by=self.user.id, approved_by=self.user.id)
        self.db.add(record); self.db.flush(); return record
    def test_exact_current_id_includes_quantity_bag_and_grade(self):
        response = self.client.get(f"/share/commodities/Beans?pu={self.second.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("2 bags · 25kg · grade B", response.text)
        self.assertIn("200", response.text)
        self.assertNotIn("999", response.text)
    def test_ambiguous_or_other_commodity_id_never_quotes_arbitrary_price(self):
        response = self.client.get("/share/commodities/Beans")
        self.assertIn("select a current market and measurement", response.text)
        response = self.client.get(f"/share/commodities/Honey?pu={self.first.id}")
        self.assertNotIn("100", response.text)
        self.assertNotIn("999", response.text)
    def test_historical_shared_id_is_generic_and_never_replays_old_price(self):
        self.price(self.beans, 150, "50kg", "A", self.when + timedelta(days=1)); self.db.commit()
        response = self.client.get(f"/share/commodities/Beans?pu={self.first.id}")
        self.assertIn("shared observation may have changed", response.text)
        self.assertNotIn("2 bags", response.text)
