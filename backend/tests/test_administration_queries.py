"""Bounded administrator reads without lost expiry processing or N+1 queries."""

from datetime import datetime, timedelta, timezone
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.database import Base
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.services.price_flag_service import list_flagged_price_updates
from app.services.subscription_service import list_subscriptions
from app.services.user_service import list_users


class AdministrationQueryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, autoflush=False)
        self.users = []
        now = datetime.now(timezone.utc)
        for index in range(5):
            user = User(full_name=f"Synthetic {index}", email=f"admin-query-{index}@synthetic.test", password_hash="unused",
                        role="reporter", is_active=True, referral_code=f"ADMQ{index}")
            user.subscription = Subscription(status="trial", plan_name="trial", trial_ends_at=now - timedelta(days=1))
            self.db.add(user)
            self.users.append(user)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_pagination_is_bounded_stable_and_validated(self):
        first = list_users(self.db, page=1, page_size=2)
        second = list_users(self.db, page=2, page_size=2)
        self.assertEqual([user.id for user in first + second], [user.id for user in self.users[:4]])
        for page, size in ((0, 100), (1, 1001)):
            with self.assertRaises(HTTPException):
                list_users(self.db, page=page, page_size=size)
            with self.assertRaises(HTTPException):
                list_subscriptions(self.db, page=page, page_size=size)
            with self.assertRaises(HTTPException):
                list_flagged_price_updates(self.db, page=page, page_size=size)

    def test_expiry_updates_every_account_before_returning_one_page(self):
        rows = list_subscriptions(self.db, page=1, page_size=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual({row.status for row in self.db.scalars(select(Subscription)).all()}, {"expired"})
        self.assertEqual({user.role for user in self.users}, {"reporter"})

    def test_bulk_expiry_preserves_future_paid_time_and_indefinite_grants(self):
        now = datetime.now(timezone.utc)
        manual, future, expired = [self.users[index].subscription for index in range(3)]
        manual.status = "active"; manual.manual_grant = True
        future.status = "active"; future.paid_expires_at = now + timedelta(days=10)
        expired.status = "active"; expired.paid_expires_at = now - timedelta(seconds=1)
        self.db.commit()
        list_subscriptions(self.db, page=2, page_size=1)
        self.assertEqual(manual.status, "active")
        self.assertEqual(future.status, "active")
        self.assertEqual(expired.status, "expired")
        self.assertEqual(future.paid_expires_at.replace(tzinfo=timezone.utc), now + timedelta(days=10))

    def test_flag_summary_joins_names_and_counts_in_one_bounded_query(self):
        commodity = Commodity(name="Synthetic flag commodity", is_active=True)
        market = Market(name="Synthetic flag market", is_active=True)
        self.db.add_all([commodity, market])
        self.db.flush()
        price_ids = []
        for index in range(3):
            price = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=90, price_high=110,
                                unit="bag", bag_size="50 kg", status="approved", movement="unknown",
                                confidence_level="Admin confirmed", update_date_time=datetime(2026, 1, 1, index + 1, tzinfo=timezone.utc),
                                created_by=self.users[0].id)
            self.db.add(price)
            self.db.flush()
            price_ids.append(price.id)
            for user in self.users[:2]:
                self.db.add(PriceFlag(price_update_id=price.id, user_id=user.id, reason="Synthetic flag"))
        self.db.commit()
        queries = []
        def collect(connection, cursor, statement, parameters, context, executemany):
            queries.append(statement)
        event.listen(self.engine, "before_cursor_execute", collect)
        try:
            rows = list_flagged_price_updates(self.db, page=1, page_size=2)
        finally:
            event.remove(self.engine, "before_cursor_execute", collect)
        self.assertEqual(len(queries), 1)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row.flag_count == 2 and row.commodity_name == commodity.name and row.market_name == market.name for row in rows))
        self.assertEqual(len(list_flagged_price_updates(self.db, page=2, page_size=2)), 1)


if __name__ == "__main__":
    unittest.main()
