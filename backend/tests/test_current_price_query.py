"""Current-price selection must not materialize the entire retained history."""
from datetime import datetime, timedelta, timezone
import unittest

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.services.price_update_service import list_latest_approved_price_updates, list_price_history


class CurrentPriceQueryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.now = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic Admin", email="query@example.com", password_hash="unused", role="admin", referral_code="QUERYTEST")
            commodity = Commodity(name="Egusi", is_active=True)
            market = Market(name="Kwali Market", state="FCT", country="Nigeria", is_active=True)
            db.add_all([user, commodity, market])
            db.flush()
            self.user_id, self.commodity_id, self.market_id = user.id, commodity.id, market.id
            for age in range(200, 0, -1):
                db.add(self.row(self.now - timedelta(hours=age), movement="down"))
            current = self.row(self.now, movement="up")
            db.add(current)
            db.flush()
            self.current_id = current.id
            db.commit()

    def tearDown(self):
        self.engine.dispose()

    def row(self, timestamp, **changes):
        return PriceUpdate(commodity_id=self.commodity_id, market_id=self.market_id,
                           price_low=210000, price_high=220000, unit="1 bag", bag_size=None,
                           confidence_level="Low confidence", update_date_time=timestamp,
                           status="approved", created_by=self.user_id, approved_by=self.user_id,
                           **changes)

    def test_current_query_loads_only_winning_records_and_retains_all_history(self):
        loaded = []
        with Session(self.engine) as db:
            def record_load(session, instance):
                if isinstance(instance, PriceUpdate):
                    loaded.append(instance.id)
            event.listen(db, "loaded_as_persistent", record_load)
            result = list_latest_approved_price_updates(db)
            self.assertEqual([item.id for item in result], [self.current_id])
            self.assertEqual(loaded, [self.current_id], "Do not hydrate 201 historical prices for one current card")
            self.assertEqual(db.scalar(select(func.count()).select_from(PriceUpdate)), 201)
            self.assertEqual(len(list_price_history(db)), 201)

    def test_movement_filter_cannot_resurface_an_older_match(self):
        with Session(self.engine) as db:
            self.assertEqual(list_latest_approved_price_updates(db, movement="down"), [])
            self.assertEqual([item.id for item in list_latest_approved_price_updates(db, movement="up")], [self.current_id])

    def test_outdated_winner_does_not_resurface_an_older_price(self):
        with Session(self.engine) as db:
            db.get(PriceUpdate, self.current_id).is_outdated = True
            db.commit()
            self.assertEqual(list_latest_approved_price_updates(db), [])
            self.assertEqual(len(list_price_history(db)), 201)

    def test_timestamp_tie_uses_highest_id_and_ignores_unapproved_newer_row(self):
        with Session(self.engine) as db:
            winner = self.row(self.now, movement="stable")
            pending = self.row(self.now + timedelta(hours=1), movement="down")
            pending.status = "pending"
            db.add_all([winner, pending])
            db.commit()
            self.assertEqual([item.id for item in list_latest_approved_price_updates(db)], [winner.id])

    def test_day_filter_is_before_ranking_with_exclusive_next_day(self):
        with Session(self.engine) as db:
            day = self.now.date() - timedelta(days=1)
            records = list_latest_approved_price_updates(db, selected_date=day)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].update_date_time.date(), day)
            # 23:00 UTC is the next Nigerian day; the last hourly row is 22:00.
            self.assertEqual(records[0].update_date_time.hour, 22)
            self.assertEqual(list_latest_approved_price_updates(db, selected_date=day, movement="up"), [])

    def test_existing_search_active_catalog_and_unknown_quantity_are_preserved(self):
        with Session(self.engine) as db:
            records = list_latest_approved_price_updates(db, commodity_search="gUs", market_search="Kwali")
            self.assertEqual([item.id for item in records], [self.current_id])
            self.assertEqual(records[0].unit, "1 bag")
            self.assertIsNone(records[0].bag_size)
            self.assertEqual(list_latest_approved_price_updates(db, commodity_search="absent"), [])
            db.get(Commodity, self.commodity_id).is_active = False
            db.commit()
            self.assertEqual(list_latest_approved_price_updates(db), [])
            self.assertEqual(db.scalar(select(func.count()).select_from(PriceUpdate)), 201)
