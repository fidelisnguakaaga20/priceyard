import unittest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.notification_job import NotificationJob
from app.models.push_subscription import PushSubscription
from app.services import watchlist_alert_service
from app.services.notification_service import process_notifications
from app.config import get_settings
from app.schemas.watchlist_schema import WatchlistTargetUpdate
from app.services.watchlist_service import update_watchlist_target
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
            bag_size="50 kg",
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

    def deliver_mail(self):
        self.db.commit()
        return process_notifications(self.db, senders={"email": lambda job: self.sent_emails.append({"recipient": job.recipient, **job.payload})})

    def test_watchers_are_notified_once_each_non_watchers_skipped(self) -> None:
        sent = watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        self.assertFalse(self.sent_emails)
        self.deliver_mail()

        recipients = {e["recipient"] for e in self.sent_emails}
        self.assertEqual(sent, 2)
        self.assertIn("watcher@example.com", recipients)
        self.assertIn("marketwatcher@example.com", recipients)
        self.assertNotIn("nonwatcher@example.com", recipients)
        self.assertNotIn("inactive@example.com", recipients)
        # market_watcher matched twice (commodity + market) but must be emailed once
        self.assertEqual(sum(1 for r in recipients if r == "marketwatcher@example.com"), 1)

    def test_email_content_mentions_commodity_and_price(self) -> None:
        self.price_update.source_1 = "Synthetic private market source"
        self.price_update.possible_meaning = "Synthetic premium interpretation"
        self.db.flush()
        watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        self.deliver_mail()

        mail = next(e for e in self.sent_emails if e["recipient"] == "watcher@example.com")
        self.assertIn("Egusi", mail["subject"])
        self.assertIn("210,000", mail["body"])
        self.assertIn("Kwali Market", mail["body"])
        self.assertIn("50 kg", mail["body"])
        self.assertIn(get_settings().frontend_url, mail["body"])
        self.assertNotIn("Synthetic private market source", mail["body"])
        self.assertNotIn("Synthetic premium interpretation", mail["body"])

    def test_one_failed_send_does_not_block_others(self) -> None:
        calls = []
        self.watcher.phone = "08000000000"
        self.db.add(PushSubscription(user_id=self.watcher.id, endpoint="https://fcm.googleapis.com/synthetic-watch", p256dh="synthetic-unused", auth="synthetic-unused"))
        self.db.commit()
        def flaky_send_email(job):
            calls.append(job.recipient)
            if job.recipient == "watcher@example.com":
                raise RuntimeError("simulated provider failure")
        sent = watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        self.db.commit()
        counts = process_notifications(self.db, senders={"email": flaky_send_email, "push": lambda _: calls.append("push"), "whatsapp": lambda _: calls.append("whatsapp")})
        self.assertEqual(sent, 2)  # queued logical email events, not provider success
        self.assertEqual(counts["sent"], 3)
        self.assertEqual(counts["retried"], 1)
        self.assertIn("watcher@example.com", calls)
        self.assertIn("marketwatcher@example.com", calls)
        self.assertIn("push", calls)
        self.assertIn("whatsapp", calls)

    def test_combined_watch_requires_both_dimensions(self) -> None:
        combined = self._make_user("combined@example.com", "BOTHREF")
        self.db.add(Watchlist(user_id=combined.id, commodity_id=self.commodity.id, market_id=self.other_market.id))
        self.db.commit()
        watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        recipients = self.db.scalars(select(NotificationJob.recipient)).all()
        self.assertNotIn(combined.email, recipients)

    def test_legacy_target_is_preserved_but_paused_until_measurement_confirmation(self) -> None:
        watch = self.db.scalar(select(Watchlist).where(Watchlist.user_id == self.watcher.id))
        watch.target_price = 220000
        watch.target_direction = "at_or_below"
        self.db.commit()
        self.assertFalse(watchlist_alert_service._target_condition_met(watch, self.price_update))
        self.assertEqual(watch.target_price, 220000)
        watch.market_id = self.market.id
        watch.target_unit = "1 bag"
        watch.target_bag_size = "50 kg"
        self.db.commit()
        self.assertTrue(watchlist_alert_service._target_condition_met(watch, self.price_update))
        watch.target_bag_size = "100 kg"
        self.assertFalse(watchlist_alert_service._target_condition_met(watch, self.price_update))
        watch.target_bag_size = "50 kg"
        watch.target_grade = "Grade A"
        self.assertFalse(watchlist_alert_service._target_condition_met(watch, self.price_update))

    def test_free_account_can_receive_confirmed_current_price_target(self) -> None:
        watch = self.db.scalar(select(Watchlist).where(Watchlist.user_id == self.watcher.id))
        watch.market_id = self.market.id
        watch.target_price = 220000
        watch.target_direction = "at_or_below"
        watch.target_unit = "1 bag"
        watch.target_bag_size = "50 kg"
        self.db.commit()
        self.assertEqual(self.watcher.role, "free_user")
        watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        self.deliver_mail()
        self.assertIn(self.watcher.email, {mail["recipient"] for mail in self.sent_emails})

    def test_outdated_or_unapproved_price_does_not_enqueue(self) -> None:
        self.price_update.is_outdated = True
        self.db.commit()
        self.assertEqual(watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update), 0)
        self.price_update.is_outdated = False
        self.price_update.status = "pending"
        self.db.commit()
        self.assertEqual(watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update), 0)
        self.assertFalse(self.db.scalars(select(NotificationJob)).all())

    def test_queued_notice_is_skipped_after_watch_is_removed(self) -> None:
        watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        watch = self.db.scalar(select(Watchlist).where(Watchlist.user_id == self.watcher.id))
        self.db.delete(watch)
        self.db.commit()
        counts = self.deliver_mail()
        self.assertEqual(counts["skipped"], 1)
        self.assertEqual(counts["sent"], 1)

    def test_free_owner_can_confirm_existing_target_without_deleting_record(self) -> None:
        watch = self.db.scalar(select(Watchlist).where(Watchlist.user_id == self.watcher.id))
        original_id = watch.id
        watch.target_price = 220000
        watch.target_direction = "at_or_below"
        self.db.commit()
        payload = WatchlistTargetUpdate(target_price=220000, target_direction="at_or_below", market_id=self.market.id,
                                       target_unit="1 bag", target_bag_size="50 kg")
        with self.assertRaises(HTTPException) as caught:
            update_watchlist_target(self.db, self.non_watcher.id, watch.id, payload)
        self.assertEqual(caught.exception.status_code, 404)
        confirmed = update_watchlist_target(self.db, self.watcher.id, watch.id, payload)
        self.assertEqual(confirmed.id, original_id)
        self.assertEqual(confirmed.target_price, 220000)
        self.assertTrue(confirmed.target_measurement_confirmed)

    def test_later_current_observation_suppresses_queued_old_price(self) -> None:
        watchlist_alert_service.notify_watchlist_subscribers(self.db, self.price_update)
        newer = PriceUpdate(commodity_id=self.commodity.id, market_id=self.market.id,
                            price_low=230000, price_high=240000, unit="1 bag", bag_size="50 kg", movement="unknown",
                            confidence_level="Admin confirmed", update_date_time=self.price_update.update_date_time + timedelta(seconds=1),
                            status="approved", created_by=self.admin.id)
        self.db.add(newer)
        self.db.commit()
        counts = self.deliver_mail()
        self.assertEqual(counts["skipped"], 2)
        self.assertFalse(self.sent_emails)


if __name__ == "__main__":
    unittest.main()
