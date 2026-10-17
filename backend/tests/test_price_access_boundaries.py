from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token


class PriceAccessBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        now = datetime.now(timezone.utc)
        self.old_date = (now - timedelta(days=2)).date().isoformat()
        self.current_date = now.date().isoformat()
        self.headers = {"guest": {}}
        with Session(self.engine) as db:
            for name, role, access in (
                ("free", "free_user", "free"), ("trial", "free_user", "trial"),
                ("paid", "paid_user", "active"), ("reporter", "reporter", "free"),
                ("admin", "admin", "free"), ("expired_trial", "free_user", "expired_trial"),
                ("expired_paid", "paid_user", "expired_paid"),
            ):
                user = User(full_name="Synthetic " + name, email=name + "@example.com", password_hash="not-a-real-password", role=role, is_active=True, referral_code="ACCESS" + name)
                trial = access in {"trial", "expired_trial"}
                expired = access.startswith("expired")
                user.subscription = Subscription(status="trial" if trial else "active" if access in {"active", "expired_paid"} else "free", plan_name="trial" if trial else "paid_monthly" if access in {"active", "expired_paid"} else "free", start_date=(now - timedelta(days=31)).date(), end_date=(now - timedelta(days=1)).date() if expired else (now + timedelta(days=14)).date(), trial_started_at=now - timedelta(days=15) if expired and trial else now if trial else None, trial_ends_at=now - timedelta(days=1) if expired and trial else now + timedelta(days=14) if trial else None)
                db.add(user)
                db.flush()
                self.headers[name] = {"Authorization": "Bearer " + create_access_token(user_id=user.id)}
                if name == "admin":
                    admin = user
            commodity = Commodity(name="Egusi", is_active=True)
            market = Market(name="Kwali Market", state="FCT", country="Nigeria", is_active=True)
            db.add_all([commodity, market])
            db.flush()
            rows = []
            for age, low, state in ((2, 210000, "approved"), (0, 211000, "approved"), (-1, 212000, "pending")):
                item = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=low, price_high=low+10000, previous_price_low=210000 if age == 0 else None, previous_price_high=220000 if age == 0 else None, unit="1 bag", bag_size=None, confidence_level="Low confidence", movement="unknown", update_date_time=now-timedelta(days=age), status=state, created_by=admin.id, approved_by=admin.id if state == "approved" else None, source_1="CONFIDENTIAL-SYNTHETIC-SOURCE")
                db.add(item)
                db.flush()
                rows.append(item.id)
            self.old_id, self.current_id, self.pending_id = rows
            quality = QualitySignal(commodity_id=commodity.id, market_id=market.id, price_update_id=self.current_id, risk_note="Synthetic private quality observation", created_by=admin.id)
            db.add(quality)
            db.commit()
            self.quality_id = quality.id
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def historical_urls(self):
        return ["/price-updates/history", "/price-updates/history/pairs", "/price-updates?date=" + self.old_date, "/price-updates/comparison?commodity=Egusi&date=" + self.old_date, "/price-updates/" + str(self.old_id)]

    def test_history_routes_enforce_existing_access_matrix(self):
        for name, headers in self.headers.items():
            expected = 200 if name in {"trial", "paid", "admin"} else 401 if name == "guest" else 403
            for url in self.historical_urls():
                with self.subTest(user=name, url=url):
                    self.assertEqual(self.client.get(url, headers=headers).status_code, expected)

    def test_quality_routes_match_existing_full_access_screen(self):
        for name, headers in self.headers.items():
            expected = 200 if name in {"trial", "paid", "admin"} else 401 if name == "guest" else 403
            for url in ("/quality-signals", f"/quality-signals/{self.quality_id}"):
                with self.subTest(user=name, url=url):
                    self.assertEqual(self.client.get(url, headers=headers).status_code, expected)

    def test_public_current_prices_keep_original_fields_and_previous_summary(self):
        for headers in ({}, {"Authorization": "Bearer invalid-test-token"}, self.headers["free"]):
            for url in ("/price-updates", "/price-updates?date=" + self.current_date, "/price-updates/comparison?commodity=Egusi", f"/price-updates/{self.current_id}"):
                with self.subTest(url=url, headers=headers):
                    response = self.client.get(url, headers=headers)
                    self.assertEqual(response.status_code, 200)
                    payload = response.json()
                    row = payload[0] if isinstance(payload, list) else payload
                    self.assertEqual(row["id"], self.current_id)
                    self.assertEqual(float(row["previous_price_low"]), 210000)
                    self.assertIsNone(row["bag_size"])
                    self.assertNotIn("grade", row)
                    self.assertNotIn("source_1", row)
                    self.assertNotIn("CONFIDENTIAL-SYNTHETIC-SOURCE", response.text)

    def test_stale_current_record_is_still_public_but_outdated_is_not(self):
        with Session(self.engine) as db:
            current = db.get(PriceUpdate, self.current_id)
            current.update_date_time -= timedelta(days=1)
            db.commit()
        self.assertEqual(self.client.get(f"/price-updates/{self.current_id}").status_code, 200)
        with Session(self.engine) as db:
            db.get(PriceUpdate, self.current_id).is_outdated = True
            db.commit()
        self.assertEqual(self.client.get("/price-updates").json(), [])
        self.assertEqual(self.client.get(f"/price-updates/{self.current_id}").status_code, 401)
        self.assertEqual(self.client.get(f"/price-updates/{self.old_id}").status_code, 401)
        self.assertEqual(self.client.get(f"/price-updates/{self.current_id}", headers=self.headers["trial"]).status_code, 200)

    def test_unapproved_or_missing_records_remain_unavailable(self):
        for headers in ({}, self.headers["trial"], self.headers["admin"]):
            for item_id in (self.pending_id, 99999):
                self.assertEqual(self.client.get(f"/price-updates/{item_id}", headers=headers).status_code, 404)
        self.assertEqual(self.client.get("/price-updates?date=2000-01-01").json(), [])

    def test_invalid_or_revoked_credentials_cannot_read_history(self):
        for headers in ({"Authorization": "Bearer invalid-test-token"}, self.headers["trial"]):
            if headers == self.headers["trial"]:
                self.assertEqual(self.client.post("/auth/logout", headers=headers).status_code, 204)
            for url in self.historical_urls():
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url, headers=headers).status_code, 401)
