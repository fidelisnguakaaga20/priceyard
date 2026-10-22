"""The owner's manual Admin workflow must save without inferred movement claims."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.security import create_access_token


class AdminManualMovementTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.headers = {"guest": {}}
        now = datetime.now(timezone.utc)
        with Session(self.engine) as db:
            for label, role in (("admin", "admin"), ("reporter", "reporter"), ("free", "free_user")):
                user = User(full_name="Synthetic " + label, email=label + "@example.com",
                            password_hash="unused", role=role, referral_code="MANUAL" + label)
                db.add(user)
                db.flush()
                self.headers[label] = {"Authorization": "Bearer " + create_access_token(user_id=user.id)}
                if label == "admin":
                    admin_id = user.id
            commodity, market = Commodity(name="Palm oil"), Market(name="Owukpa Market")
            db.add_all([commodity, market])
            db.flush()
            self.payload = dict(commodity_id=commodity.id, market_id=market.id,
                price_low=42000, price_high=44000, average_price=43000,
                previous_price_low=40000, previous_price_high=42000,
                unit="1 jericane of 25L", bag_size="25 liter jerican", commodity_type=None,
                movement="up", confidence_level="Admin confirmed", suggested_action="Watch",
                update_date_time=now.isoformat())
            # A different saved range cannot silently replace the Admin's inputs.
            prior = PriceUpdate(**{**self.payload, "commodity_type": "Recorded type",
                "price_low": 100, "price_high": 200, "average_price": 150,
                "update_date_time": now - timedelta(days=1)},
                status="approved", created_by=admin_id, approved_by=admin_id)
            db.add(prior)
            db.flush()
            self.prior_id = prior.id
            db.commit()

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)
        self.notification_patch = patch("app.routes.price_update_routes.notify_watchlist_subscribers", return_value=0)
        self.notification_patch.start()

    def tearDown(self):
        self.notification_patch.stop()
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def create(self, movement="up", **changes):
        return self.client.post("/price-updates", headers=self.headers["admin"],
                                json={**self.payload, "movement": movement, **changes})

    def count(self):
        with Session(self.engine) as db:
            return db.scalar(select(func.count()).select_from(PriceUpdate))

    def test_admin_selected_movements_survive_create_approval_and_correction(self):
        for movement in ("up", "down", "stable", "unknown"):
            with self.subTest(movement=movement):
                created = self.create(movement)
                self.assertEqual(created.status_code, 201, created.text)
                item = created.json()
                self.assertEqual((item["movement"], item["status"]), (movement, "pending"))
                self.assertIsNone(item["commodity_type"])
                self.assertEqual(Decimal(item["previous_price_low"]), Decimal(40000))
                self.assertEqual(item["unit"], self.payload["unit"])
                self.assertEqual(item["bag_size"], self.payload["bag_size"])
                approved = self.client.patch(f"/price-updates/{item['id']}/approve", headers=self.headers["admin"])
                self.assertEqual(approved.status_code, 200, approved.text)
                self.assertEqual((approved.json()["movement"], approved.json()["status"]), (movement, "approved"))
                corrected = self.client.patch(f"/price-updates/{item['id']}", headers=self.headers["admin"],
                    json={"price_low": 41900, "price_high": 43900, "average_price": 42900,
                          "movement": movement, "previous_price_low": 39000, "previous_price_high": 41000})
                self.assertEqual(corrected.status_code, 200, corrected.text)
                self.assertEqual(corrected.json()["movement"], movement)
                self.assertEqual(Decimal(corrected.json()["price_low"]), Decimal(41900))
                self.assertEqual(Decimal(corrected.json()["previous_price_low"]), Decimal(39000))
        with Session(self.engine) as db:
            prior = db.get(PriceUpdate, self.prior_id)
            self.assertEqual((prior.price_low, prior.price_high, prior.movement),
                             (Decimal(100), Decimal(200), "up"))

    def test_admin_can_record_manual_movement_despite_conflicting_comparable_price(self):
        for movement in ("down", "stable", "unknown"):
            with self.subTest(movement=movement):
                response = self.create(movement, commodity_type="Recorded type")
                self.assertEqual(response.status_code, 201, response.text)
                self.assertEqual(response.json()["movement"], movement)

    def test_reporter_cannot_self_attest_unsupported_movement_or_editorial_claims(self):
        response = self.client.post("/price-updates", headers=self.headers["reporter"], json=self.payload)
        self.assertEqual(response.status_code, 422, response.text)
        self.assertIn("preceding comparable", response.json()["detail"])
        self.assertEqual(self.count(), 1)
        response = self.client.post("/price-updates", headers=self.headers["reporter"],
            json={**self.payload, "movement": "unknown", "confidence_level": "Verified by 2 sources",
                  "source_1": "PRIVATE-ONE", "source_2": "PRIVATE-TWO", "suggested_action": "Buy Carefully"})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["confidence_level"], "Reporter submitted")
        self.assertEqual(response.json()["suggested_action"], "Watch")
        self.assertIsNone(response.json()["source_1"])
        self.assertIsNone(response.json()["source_2"])

    def test_only_admin_can_correct_or_approve_manual_prices(self):
        for label, expected in (("guest", 401), ("free", 403), ("reporter", 403)):
            for suffix, body in (("", {"movement": "down"}), ("/approve", None)):
                with self.subTest(role=label, action=suffix or "correct"):
                    response = self.client.patch(f"/price-updates/{self.prior_id}{suffix}",
                        headers=self.headers[label], json=body)
                    self.assertEqual(response.status_code, expected, response.text)
        with Session(self.engine) as db:
            self.assertEqual(db.get(PriceUpdate, self.prior_id).movement, "up")

    def test_manual_entry_preserves_price_range_and_source_reference_safeguards(self):
        for invalid in ({"price_low": -1}, {"price_high": 41000}, {"average_price": 45000},
                        {"previous_price_low": 43000}, {"movement": "invented"},
                        {"confidence_level": "Verified by 2 sources", "source_1": "PRIVATE-ONE", "source_2": "private-one"}):
            with self.subTest(invalid=invalid):
                response = self.create(**invalid)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(self.count(), 1)
        response = self.create(confidence_level="Verified by 2 sources", source_1="PRIVATE-ONE", source_2="PRIVATE-TWO")
        self.assertEqual(response.status_code, 201, response.text)
        record_id = response.json()["id"]
        for changes in ({"price_low": 45000}, {"average_price": 45000},
                        {"source_2": "private-one"}):
            with self.subTest(correction=changes):
                response = self.client.patch(f"/price-updates/{record_id}",
                    headers=self.headers["admin"], json=changes)
                self.assertEqual(response.status_code, 422, response.text)
        with Session(self.engine) as db:
            item = db.get(PriceUpdate, record_id)
            self.assertEqual((item.price_low, item.average_price, item.source_2),
                             (Decimal(42000), Decimal(43000), "PRIVATE-TWO"))
