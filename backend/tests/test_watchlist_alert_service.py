import os
import unittest
from datetime import datetime, timezone

os.environ.setdefault("FRONTEND_URL", "https://priceyard.onrender.com")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist
from app.services import watchlist_alert_service
from app.utils.password import hash_password


class WatchlistAlertServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.admin = self._make_user("admin@example.com", "ADMINREF")
        self.watcher = self._make_user("watcher@example.com", "WATCHREF")
        self.market_watcher = self._make_user("marketwatcher@example.com", "MKTREF")
        self.non_watcher = self._make_user("nonwatcher@example.com", "NONEREF")
        self.inactive_watcher = self._make_user("inactive@example.com", "INACTREF", is_active=False)

        self.commodity = Commodity(name="Egusi")
        self.other_commodity = Commodity(name="Honey Beans")
        self.market = Market(name="Kwali Market")
        self.other_market = Market(name="Other Market")
        self.db.add_all([self.commodity, self.other_commodity, self.market, self.other_market])
        self.db.commit()

        # watcher: watches the commodity directly
        self.db.add(Watchlist(user_id=self.watcher.id, commodity_id=self.commodity.id))
        # market_watcher: watches the market, AND (deliberately) also the commodity,
        # to prove a user matching on two rows only gets emailed once
        self.db.add(Watchlist(user_id=self.market_watcher.id, market_id=self.market.id))
        self.db.add(Watchlist(user_id=self.market_watcher.id, commodity_id=self.commodity.id))
        # non_watcher watches something unrelated
        self.db.add(Watchlist(user_id=self.non_watcher.id, commodity_id=self.other_commodity.id))
        self.db.add(Watchlist(user_id=self.inactive_watcher.id, commodity_id=self.commodity.id))
        self.db.commit()

        self.price_update = PriceUpdate(
            commodity_id=self.commodity.id,
            market_id=self.market.id,
            price_low=210000,
            price_high=220000,
            unit="1 bag",
            movement="up",
            confidence_level="Admin confirmed",
            update_date_time=datetime.now(timezone.utc),
            status="approved",
            created_by=self.admin.id,
        )
        self.db.add(self.price_update)
        self.db.commit()
        self.db.refresh(self.price_update)

        self.sent_emails: list[dict] = []
        self.original_send_email = watchlist_alert_service.send_email if hasattr(watchlist_alert_service, "send_email") else None

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _make_user(self, email: str, referral_code: str, *, is_active: bool = True) -> User:
        user = User(
            full_name=email.split("@")[0],
            email=email,
            password_hash=hash_password("Password1"),
            role="free_user",
            is_active=is_active,
            referral_code=referral_code,
        )
        self.db.add(user)
        self.db.commit()
        return user

    def _patch_send_email(self):
        import app.services.email_service as email_service_module

        original = email_service_module.send_email

        def fake_send_email(*, recipient, subject, body):
            self.sent_emails.append({"recipient": recipient, "subject": subject, "body": body})

        email_service_module.send_email = fake_send_email
        return original, email_service_module

    def test_watchers_are_notified_once_each_non_watchers_skipped(self) -> None:
        original, module = self._patch_send_email()
        try:
            sent = watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        finally:
            module.send_email = original

        recipients = {e["recipient"] for e in self.sent_emails}
        self.assertEqual(sent, 2)
        self.assertIn("watcher@example.com", recipients)
        self.assertIn("marketwatcher@example.com", recipients)
        self.assertNotIn("nonwatcher@example.com", recipients)
        self.assertNotIn("inactive@example.com", recipients)
        # market_watcher matched twice (commodity + market) but must be emailed once
        self.assertEqual(sum(1 for r in recipients if r == "marketwatcher@example.com"), 1)

    def test_email_content_mentions_commodity_and_price(self) -> None:
        original, module = self._patch_send_email()
        try:
            watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        finally:
            module.send_email = original

        mail = next(e for e in self.sent_emails if e["recipient"] == "watcher@example.com")
        self.assertIn("Egusi", mail["subject"])
        self.assertIn("210,000", mail["body"])
        self.assertIn("Kwali Market", mail["body"])

    def test_one_failed_send_does_not_block_others(self) -> None:
        import app.services.email_service as email_service_module

        original = email_service_module.send_email
        calls = []

        def flaky_send_email(*, recipient, subject, body):
            calls.append(recipient)
            if recipient == "watcher@example.com":
                raise RuntimeError("simulated provider failure")

        email_service_module.send_email = flaky_send_email
        try:
            sent = watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        finally:
            email_service_module.send_email = original

        self.assertEqual(sent, 1)  # only the non-failing recipient counted
        self.assertIn("watcher@example.com", calls)
        self.assertIn("marketwatcher@example.com", calls)


if __name__ == "__main__":
    unittest.main()
