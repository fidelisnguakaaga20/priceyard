"""Streamed lists must not hold the request's pooled connection while streaming.

Before the fix each request held two connections (authentication + stream), so
the six parallel Market insights requests exhausted production's 5-connection
pool and most sections failed to load. A one-connection pool proves the fix.
"""
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.sell_watch_window import SellWatchWindow
from app.models.user import User
from app.security import create_access_token

STREAMED_PATHS = ("/market-signals", "/quality-signals", "/buying-zones", "/sell-watch-windows",
                  "/storage-suitability", "/cost-breakdowns", "/commodities", "/markets")


class StreamConnectionReleaseTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        # The synthetic runner shares one in-memory connection; allow only one
        # checkout of it at a time, as a deliberately exhausted production pool would.
        shared = self.engine.raw_connection().dbapi_connection
        self.engine.pool = QueuePool(lambda: shared, pool_size=1, max_overflow=0, timeout=2,
                                     reset_on_return=None, dialect=self.engine.dialect)
        with Session(self.engine) as db:
            admin = User(full_name="Synthetic Admin", email="pool@example.com", password_hash="unused",
                         role="admin", referral_code="POOLADMIN")
            commodity, market = Commodity(name="Soybeans"), Market(name="Kwali Market")
            db.add_all([admin, commodity, market])
            db.flush()
            db.add(SellWatchWindow(commodity_id=commodity.id, market_id=market.id, start_period="May",
                                   end_period="June", observation="Synthetic observation",
                                   confidence="Low confidence", created_by=admin.id))
            db.commit()
            self.headers = {"Authorization": "Bearer " + create_access_token(user_id=admin.id)}

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_streamed_lists_complete_with_a_single_pooled_connection(self):
        for path in STREAMED_PATHS:
            with self.subTest(path=path):
                response = self.client.get(path, headers=self.headers)
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(json.loads(response.text), list)
        windows = json.loads(self.client.get("/sell-watch-windows", headers=self.headers).text)
        self.assertEqual([item["observation"] for item in windows], ["Synthetic observation"])


if __name__ == "__main__":
    unittest.main()
