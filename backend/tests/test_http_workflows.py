"""Actual ASGI middleware, JWT dependencies and transaction-boundary regressions."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest
from unittest.mock import patch

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import AtomicSession, Base, get_db
from app.main import app, settings
from app.models.activity_event import ActivityEvent
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.rate_limit import limiter
from app.services.auth_session_service import issue_session
from app.services.subscription_service import build_trial_subscription


class HttpWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.previous_overrides = dict(app.dependency_overrides)
        self.sessions = []

        def isolated_database(request: Request):
            if not hasattr(request.state, "database_session"):
                request.state.database_session = AtomicSession(bind=self.engine, autoflush=False, expire_on_commit=False)
                self.sessions.append(request.state.database_session)
            return request.state.database_session

        app.dependency_overrides[get_db] = isolated_database
        self.original_enabled = limiter.enabled
        limiter.enabled = True
        limiter.reset()
        self.client = TestClient(app, raise_server_exceptions=False)
        self.headers = {}
        with Session(self.engine) as db:
            users = {}
            for index, (key, role, commercial) in enumerate((("admin", "admin", "free"), ("free", "free_user", "free"),
                    ("trial", "free_user", "trial"), ("reporter", "reporter", "free"), ("expired", "paid_user", "expired"))):
                user = User(full_name=f"Synthetic {key}", email=f"{key}@http-tests.test", password_hash="unused-test-hash",
                            role=role, is_active=True, email_verified=True, referral_code=f"HTTP{index}")
                user.subscription = build_trial_subscription(user=user) if commercial == "trial" else Subscription(status=commercial, plan_name="synthetic")
                db.add(user)
                db.flush()
                users[key] = user
            commodity = Commodity(name="Synthetic HTTP Commodity", is_active=True)
            market = Market(name="Synthetic HTTP Market", state="Synthetic State", is_active=True)
            db.add_all([commodity, market])
            db.flush()
            self.commodity_id, self.market_id = commodity.id, market.id
            self.price_ids = []
            for hour in (1, 2):
                observation = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=Decimal("90.00"),
                    price_high=Decimal("110.00"), average_price=Decimal("100.00"), unit="bag", bag_size="50 kg",
                    movement="unknown", confidence_level="Admin confirmed", source_1="Synthetic confidential one",
                    source_2="Synthetic confidential two", update_date_time=datetime(2026, 1, 1, hour, tzinfo=timezone.utc),
                    status="approved", created_by=users["admin"].id, approved_by=users["admin"].id,
                    possible_meaning="Synthetic paid meaning", suggested_action="Watch", notes="Synthetic paid note")
                db.add(observation)
                db.flush()
                self.price_ids.append(observation.id)
            for key, user in users.items():
                tokens = issue_session(db, user)
                self.headers[key] = {"Authorization": "Bearer " + tokens.access_token}
            db.commit()

    def tearDown(self):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.previous_overrides)
        limiter.reset()
        limiter.enabled = self.original_enabled
        self.client.close()
        self.engine.dispose()

    def test_real_jwt_boundaries_and_public_cache_contract(self):
        public = self.client.get("/price-updates")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.headers.get("x-priceyard-public"), "true")
        self.assertEqual(self.client.get("/price-updates/history").status_code, 401)
        for key in ("free", "reporter", "expired"):
            limited = self.client.get("/price-updates", headers=self.headers[key])
            self.assertEqual(limited.status_code, 200)
            self.assertNotIn("x-priceyard-public", limited.headers)
            for field in ("possible_meaning", "suggested_action", "notes", "source_1", "source_2"):
                self.assertNotIn(field, limited.json()[0])
            self.assertEqual(self.client.get("/price-updates/history", headers=self.headers[key]).status_code, 403)
            self.assertEqual(self.client.get(f"/price-updates/{self.price_ids[0]}", headers=self.headers[key]).status_code, 404)
        paid = self.client.get("/price-updates/history", headers=self.headers["trial"])
        self.assertEqual(paid.status_code, 200)
        self.assertEqual(len(paid.json()), 2)
        self.assertIn("possible_meaning", paid.json()[0])
        self.assertNotIn("source_1", paid.json()[0])

    def test_reporter_submits_raw_observation_but_cannot_approve(self):
        payload = {"commodity_id": self.commodity_id, "market_id": self.market_id, "price_low": "90.00", "price_high": "110.00",
                   "average_price": None, "unit": "bag", "bag_size": "50 kg", "confidence_level": "Verified by 2 sources",
                   "suggested_action": "Buy Carefully", "possible_meaning": "Synthetic attempted guidance",
                   "source_1": "Synthetic attempted source", "source_2": "Synthetic attempted source",
                   "update_date_time": "2026-01-02T12:00:00+01:00"}
        response = self.client.post("/price-updates", json=payload, headers=self.headers["reporter"])
        self.assertEqual(response.status_code, 201, response.text)
        identifier = response.json()["id"]
        self.assertEqual(response.json()["status"], "pending")
        self.assertEqual(response.json()["confidence_level"], "Reporter submitted")
        self.assertIsNone(response.json()["average_price"])
        self.assertIsNone(response.json()["source_1"])
        self.assertEqual(self.client.patch(f"/price-updates/{identifier}/approve", headers=self.headers["reporter"]).status_code, 403)
        self.assertEqual(self.client.patch(f"/price-updates/{identifier}/approve", headers=self.headers["admin"]).status_code, 200)
        with Session(self.engine) as db:
            self.assertEqual(db.get(PriceUpdate, identifier).status, "approved")
            self.assertIsNotNone(db.scalar(select(AuditLog).where(AuditLog.action == "price_update.approve", AuditLog.record_id == identifier)))

    def test_admin_mutation_is_committed_with_one_explicit_audit(self):
        response = self.client.post("/commodities", json={"name": "Synthetic persisted commodity"}, headers=self.headers["admin"])
        self.assertEqual(response.status_code, 201, response.text)
        identifier = response.json()["id"]
        with Session(self.engine) as db:
            self.assertIsNotNone(db.get(Commodity, identifier))
            self.assertEqual(db.scalar(select(func.count()).select_from(AuditLog).where(
                AuditLog.table_name == "commodities", AuditLog.record_id == identifier)), 1)
        self.assertIsNone(self.sessions[-1].get_transaction())

    def test_audit_failure_rolls_back_already_flushed_business_change(self):
        with patch("app.routes.commodity_routes.create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            response = self.client.post("/commodities", json={"name": "Synthetic must roll back"}, headers=self.headers["admin"])
        self.assertEqual(response.status_code, 500)
        with Session(self.engine) as db:
            self.assertIsNone(db.scalar(select(Commodity).where(Commodity.name == "Synthetic must roll back")))

    def test_final_commit_failure_replaces_success_and_rolls_back(self):
        with patch.object(Session, "commit", side_effect=SQLAlchemyError("Synthetic commit failure")):
            response = self.client.post("/commodities", json={"name": "Synthetic commit must roll back"}, headers=self.headers["admin"])
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Synthetic commit failure", response.text)
        with Session(self.engine) as db:
            self.assertIsNone(db.scalar(select(Commodity).where(Commodity.name == "Synthetic commit must roll back")))

    def test_hidden_faq_remains_manageable_after_separate_requests(self):
        created = self.client.post("/faq", json={"question": "Synthetic question?", "answer": "Synthetic factual answer.",
                                                "category": "Synthetic"}, headers=self.headers["admin"])
        self.assertEqual(created.status_code, 201, created.text)
        identifier = created.json()["id"]
        self.assertEqual(self.client.patch(f"/faq/{identifier}/publish", headers=self.headers["admin"]).status_code, 200)
        self.assertEqual(self.client.patch(f"/faq/{identifier}/hide", headers=self.headers["admin"]).status_code, 200)
        self.assertEqual(self.client.get(f"/faq/{identifier}").status_code, 404)
        management = self.client.get("/faq/admin/all", headers=self.headers["admin"])
        self.assertEqual([item["id"] for item in management.json()], [identifier])
        self.assertEqual(self.client.get("/faq/admin/all", headers=self.headers["free"]).status_code, 403)
        edited = self.client.patch(f"/faq/{identifier}", json={"answer": "Synthetic revised factual answer."}, headers=self.headers["admin"])
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(self.client.patch(f"/faq/{identifier}/publish", headers=self.headers["admin"]).status_code, 200)
        self.assertEqual(self.client.get(f"/faq/{identifier}").json()["answer"], "Synthetic revised factual answer.")

    def test_body_and_query_bounds_are_enforced_by_actual_app(self):
        for query in ("page=0", "page_size=1001", "commodity_id=-1"):
            self.assertEqual(self.client.get("/price-updates?" + query).status_code, 422)
        before = len(self.sessions)
        oversized = self.client.post("/activity/ping", content=b"x" * (settings.max_request_bytes + 1),
                                     headers={"Content-Type": "application/json"})
        self.assertEqual(oversized.status_code, 413)
        self.assertEqual(len(self.sessions), before, "Body limit must reject before opening a database session")

    def test_public_write_rate_limit_rejects_excess_without_persisting(self):
        statuses = [self.client.post("/activity/ping", json={"event_type": "app_visit", "label": "Synthetic"}).status_code
                    for _ in range(21)]
        self.assertEqual(statuses[:20], [204] * 20)
        self.assertEqual(statuses[-1], 429)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(ActivityEvent)), 20)


if __name__ == "__main__":
    unittest.main()
