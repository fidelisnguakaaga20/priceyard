import csv
from datetime import date, datetime, timedelta, timezone
from io import StringIO
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token
from app.services.price_time_service import price_day_bounds
from app.services.price_update_service import list_latest_approved_price_updates, list_market_comparison, list_price_history
from app.services.report_export_service import stream_price_report_csv


DAY = date(2026, 10, 18)
START = datetime(2026, 10, 17, 23, tzinfo=timezone.utc)
END = datetime(2026, 10, 18, 23, tzinfo=timezone.utc)


def seed_time_boundaries(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic time Admin", email="wat-boundary@example.com",
                     role="admin", password_hash="unused", referral_code="WATBOUNDARY")
        free = User(full_name="Synthetic free", email="wat-free@example.com",
                    role="free_user", password_hash="unused", referral_code="WATFREE")
        free.subscription = Subscription(status="free", plan_name="free")
        commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
        db.add_all([owner, free, commodity, market])
        db.flush()
        ids = []
        # Includes both sides of WAT midnight and the UTC/Nigerian date overlap.
        for index, stamp in enumerate((START-timedelta(microseconds=1), START,
                START+timedelta(minutes=30), END-timedelta(microseconds=1), END)):
            row = PriceUpdate(commodity_id=commodity.id, market_id=market.id,
                price_low=210000+index, price_high=220000, unit="1 bag", bag_size=None,
                status="approved", movement="unknown", confidence_level="Low confidence",
                created_by=owner.id, update_date_time=stamp, source_1="PRIVATE-TIME-SOURCE")
            db.add(row)
            db.flush()
            ids.append(row.id)
        db.commit()
        return owner.id, free.id, ids


def verify_price_day(check, engine):
    _, _, ids = seed_time_boundaries(engine)
    check.assertEqual(price_day_bounds(DAY), (START, END))
    with Session(engine) as db:
        before = db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
        history = list_price_history(db, selected_date=DAY)
        check.assertEqual([row.id for row in history], ids[1:4])
        check.assertEqual([row.id for row in list_latest_approved_price_updates(db, selected_date=DAY)], [ids[3]])
        check.assertEqual([row.id for row in list_market_comparison(db, commodity_search="Egusi", selected_date=DAY)], [ids[3]])
        check.assertEqual([row.id for row in list_latest_approved_price_updates(db)], [ids[4]])
        check.assertEqual(len(list_price_history(db)), 5)
    rows = list(csv.DictReader(StringIO("".join(stream_price_report_csv(engine, date_from=DAY, date_to=DAY)))))
    check.assertEqual([row["price_low"] for row in rows], ["210001.00", "210002.00", "210003.00"])
    check.assertNotIn("PRIVATE-TIME-SOURCE", str(rows))
    with Session(engine) as db:
        check.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(), before)
        # Native TIMESTAMPTZ round-trip retains the exact instants, not WAT wall clocks.
        if engine.dialect.name == "postgresql":
            check.assertEqual(db.get(PriceUpdate, ids[1]).update_date_time, START)
            check.assertEqual(db.get(PriceUpdate, ids[4]).update_date_time, END)


class NigeriaPriceTimeTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_midnight_bounds_selection_export_and_unchanged_history(self):
        verify_price_day(self, self.engine)

    def test_nigerian_day_urls_keep_current_and_history_access_boundaries(self):
        admin, free, ids = seed_time_boundaries(self.engine)
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        admin_headers = {"Authorization": "Bearer "+create_access_token(user_id=admin)}
        free_headers = {"Authorization": "Bearer "+create_access_token(user_id=free)}
        with TestClient(app) as client:
            for path in ("/price-updates?date=2026-10-18", "/price-updates/comparison?commodity=Egusi&date=2026-10-18"):
                self.assertEqual(client.get(path).status_code, 401)
                self.assertEqual(client.get(path, headers=free_headers).status_code, 403)
                response = client.get(path, headers=admin_headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual([row["id"] for row in response.json()], [ids[3]])
                self.assertNotIn("PRIVATE-TIME-SOURCE", response.text)
            response = client.get("/price-updates/history?date=2026-10-18", headers=admin_headers)
            self.assertEqual([row["id"] for row in response.json()], ids[1:4])
            self.assertEqual([row["id"] for row in client.get("/price-updates?date=2026-10-19").json()], [ids[4]])
            self.assertEqual(client.get("/price-updates/history?date=2026-10-18").status_code, 401)
            self.assertEqual(client.get("/price-updates?date=not-a-date").status_code, 422)

    def test_year_and_leap_day_boundaries(self):
        self.assertEqual(price_day_bounds(date(2027, 1, 1))[0], datetime(2026, 12, 31, 23, tzinfo=timezone.utc))
        self.assertEqual(price_day_bounds(date(2028, 2, 29))[1], datetime(2028, 2, 29, 23, tzinfo=timezone.utc))
