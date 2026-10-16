"""An editor's saved price state and sanitized audit must succeed together."""
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.security import create_access_token


class PriceAuditAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic Admin", email="audit@example.com", password_hash="unused", role="admin", referral_code="PRICEAUDIT")
            commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
            db.add_all([user, commodity, market]); db.flush()
            self.headers = {"Authorization": "Bearer " + create_access_token(user_id=user.id)}
            self.payload = dict(commodity_id=commodity.id, market_id=market.id, price_low=210000,
                price_high=220000, average_price=215000, unit="1 bag", bag_size="Unknown",
                confidence_level="Low confidence", movement="unknown", suggested_action="Watch",
                update_date_time=datetime.now(timezone.utc).isoformat(), source_1="PRIVATE-FAKE-SOURCE")
            item = PriceUpdate(**{**self.payload, "update_date_time": datetime.now(timezone.utc)}, status="pending", created_by=user.id)
            db.add(item); db.flush(); self.price_id = item.id; db.commit()
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close(); app.dependency_overrides.clear(); self.engine.dispose()

    def request(self, action):
        if action == "create":
            return self.client.post("/price-updates", json=self.payload, headers=self.headers)
        suffix = "" if action == "edit" else "/" + action
        return self.client.patch(f"/price-updates/{self.price_id}" + suffix,
                                 json={"price_low": 209000} if action == "edit" else None, headers=self.headers)

    def state(self):
        with Session(self.engine) as db:
            row = db.get(PriceUpdate, self.price_id)
            return (row.status, row.is_outdated, row.price_low, row.approved_by,
                    db.scalar(select(func.count()).select_from(PriceUpdate)),
                    db.scalar(select(func.count()).select_from(AuditLog)))

    def test_audit_failure_rolls_back_each_price_action_and_does_not_notify(self):
        for action in ("create", "edit", "approve", "reject", "mark-outdated"):
            before = self.state()
            with self.subTest(action=action), \
                    patch("app.routes.price_update_routes.create_audit_log", side_effect=RuntimeError("synthetic audit failure")), \
                    patch("app.routes.price_update_routes.notify_watchlist_subscribers") as notify:
                self.assertEqual(self.request(action).status_code, 500)
                self.assertEqual(self.state(), before)
                notify.assert_not_called()

    def test_successful_actions_preserve_complete_private_source_free_audit(self):
        with patch("app.routes.price_update_routes.notify_watchlist_subscribers", return_value=0):
            for action in ("create", "edit", "approve", "mark-outdated", "reject"):
                with self.subTest(action=action):
                    response = self.request(action)
                    self.assertEqual(response.status_code, 201 if action == "create" else 200)
        with Session(self.engine) as db:
            logs = db.scalars(select(AuditLog).order_by(AuditLog.id)).all()
            self.assertEqual(len(logs), 5)
            self.assertEqual([log.action for log in logs], ["price_update." + action for action in ("create", "edit", "approve", "mark_outdated", "reject")])
            self.assertNotIn("PRIVATE-FAKE-SOURCE", str([(log.old_value, log.new_value) for log in logs]))
            self.assertEqual(logs[2].old_value["status"], "pending")
            self.assertEqual(logs[2].new_value["status"], "approved")

    def test_commit_failure_rolls_back_price_and_audit_without_notifying(self):
        before = self.state()
        with patch.object(Session, "commit", side_effect=RuntimeError("synthetic commit failure")), \
                patch("app.routes.price_update_routes.notify_watchlist_subscribers") as notify:
            self.assertEqual(self.request("approve").status_code, 500)
            notify.assert_not_called()
        self.assertEqual(self.state(), before)

    def test_failed_notification_cannot_misreport_saved_approval_or_correction(self):
        with patch("app.routes.price_update_routes.notify_watchlist_subscribers", side_effect=RuntimeError("synthetic query failure")):
            self.assertEqual(self.request("approve").status_code, 200)
            self.assertEqual(self.request("edit").status_code, 200)
        state = self.state()
        self.assertEqual(state[0], "approved")
        self.assertEqual(state[2], 209000)
        self.assertEqual(state[-1], 2)
