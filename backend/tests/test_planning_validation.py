"""Reject clearing required planning fields, retaining optional clearing/history."""
from datetime import datetime, timezone
from decimal import Decimal
import unittest
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.buying_zone import BuyingZone
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.sell_watch_window import SellWatchWindow
from app.models.user import User
from app.security import create_access_token

RESOURCES = {
    "buying": ("buying-zones", {"price_low": "210000", "price_high": "220000", "reason": "Synthetic saved reason", "confidence": "Low confidence", "valid_from": "2026-10-01", "valid_to": "2026-10-31"}, ("commodity_id", "market_id", "price_low", "price_high", "reason", "confidence"), "valid_to", "reason"),
    "sell": ("sell-watch-windows", {"start_period": "Synthetic recorded start", "end_period": "Synthetic recorded end", "observation": "Synthetic saved observation", "confidence": "Low confidence"}, ("commodity_id", "market_id", "start_period", "observation", "confidence"), "end_period", "observation"),
}


def exercise_planning_validation(check, engine, kind):
    Base.metadata.create_all(engine)
    suffix = uuid.uuid4().hex[:8]
    with Session(engine) as db:
        admin = User(full_name="Synthetic planning Admin", email=f"plan-{suffix}@example.com", password_hash="unused", role="admin", referral_code="P"+suffix)
        free = User(full_name="Synthetic other user", email=f"plan-other-{suffix}@example.com", password_hash="unused", role="free_user", referral_code="F"+suffix)
        commodity, market = Commodity(name="Synthetic Egusi "+suffix), Market(name="Synthetic Kwali "+suffix)
        db.add_all([admin, free, commodity, market]); db.flush()
        scope = {"commodity_id": commodity.id, "market_id": market.id}
        db.add(PriceUpdate(**scope, unit="1 bag", bag_size=None, price_low=210000, price_high=220000, status="approved", movement="unknown", confidence_level="Low confidence", created_by=admin.id, update_date_time=datetime.now(timezone.utc)))
        db.commit()
        headers = {"Authorization": "Bearer "+create_access_token(user_id=admin.id)}
        free_headers = {"Authorization": "Bearer "+create_access_token(user_id=free.id)}

    def sessions():
        with Session(engine) as db:
            yield db

    def state():
        with Session(engine) as db:
            return {model.__tablename__: db.execute(select(model.__table__).order_by(model.id)).all() for model in (BuyingZone, SellWatchWindow, AuditLog, PriceUpdate)}

    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            endpoint, values, required, nullable, text_field = RESOURCES[kind]
            response = client.post("/"+endpoint, json={**scope, **values}, headers=headers)
            check.assertEqual(response.status_code, 201, response.text)
            item_id = response.json()["id"]
            path = f"/{endpoint}/{item_id}"
            before = state()
            for field in required:
                invalid = client.patch(path, json={field: None}, headers=headers)
                check.assertEqual(invalid.status_code, 422, invalid.text)
                check.assertEqual(state(), before)
            check.assertEqual(client.patch(path, json={text_field: "Synthetic unauthorized change"}, headers=free_headers).status_code, 403)
            check.assertEqual(client.patch(path, json={text_field: "Synthetic unauthorized change"}).status_code, 401)
            check.assertEqual(state(), before)
            cleared = client.patch(path, json={nullable: None}, headers=headers)
            check.assertEqual(cleared.status_code, 200, cleared.text)
            check.assertIsNone(cleared.json()[nullable])
            for field in required:
                expected = scope[field] if field in scope else values[field]
                # Existing numeric values serialize with their saved decimal scale.
                if field in ("price_low", "price_high"):
                    check.assertEqual(Decimal(cleared.json()[field]), Decimal(expected))
                else:
                    check.assertEqual(cleared.json()[field], expected)
            corrected = "Synthetic corrected observation"
            changed = client.patch(path, json={text_field: corrected}, headers=headers)
            check.assertEqual(changed.status_code, 200, changed.text)
            reloaded = client.get(path, headers=headers).json()
            check.assertEqual(reloaded[text_field], corrected)
            check.assertIsNone(reloaded[nullable])
            after = state()
            check.assertEqual(after["price_updates"], before["price_updates"])
            check.assertEqual(len(after["audit_logs"]), len(before["audit_logs"])+2)
    finally:
        app.dependency_overrides.clear()


class PlanningValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def test_buying_required_values_reject_null_without_mutation(self):
        exercise_planning_validation(self, self.engine, "buying")

    def test_sell_watch_required_values_reject_null_without_mutation(self):
        exercise_planning_validation(self, self.engine, "sell")
