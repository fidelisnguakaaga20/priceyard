"""Invalid cost edits must not crash, round, or alter historical/audit records."""
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
from app.models.commodity import Commodity
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.security import create_access_token

COSTS = ("transport", "warehouse", "security", "market_charges", "loading_offloading", "other_costs")
MAXIMUM = "999999999999.99"


def exercise_cost_validation(check, engine, scenario):
    Base.metadata.create_all(engine)
    suffix = uuid.uuid4().hex[:8]
    with Session(engine) as db:
        admin = User(full_name="Synthetic cost Admin", email=f"cost-{suffix}@example.com", password_hash="unused", role="admin", referral_code="C"+suffix)
        commodity, market = Commodity(name="Synthetic Egusi "+suffix), Market(name="Synthetic Kwali "+suffix)
        db.add_all([admin, commodity, market]); db.flush()
        scope = {"commodity_id": commodity.id, "market_id": market.id}
        db.add(PriceUpdate(**scope, unit="1 bag", bag_size=None, price_low=210000, price_high=220000, status="approved", movement="unknown", confidence_level="Low confidence", created_by=admin.id, update_date_time=datetime.now(timezone.utc)))
        db.commit()
        headers = {"Authorization": "Bearer "+create_access_token(user_id=admin.id)}

    def sessions():
        with Session(engine) as db:
            yield db

    def state():
        with Session(engine) as db:
            return {model.__tablename__: db.execute(select(model.__table__).order_by(model.id)).all() for model in (CostBreakdown, AuditLog, PriceUpdate)}

    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            payload = {**scope, **{field: "0" for field in COSTS}, "transport": "120", "warehouse": "80", "purchase_price_reference": "210000"}
            response = client.post("/cost-breakdowns", json=payload, headers=headers)
            check.assertEqual(response.status_code, 201, response.text)
            item_id = response.json()["id"]
            before = state()
            if scenario == "nulls":
                requests = [("PATCH", f"/cost-breakdowns/{item_id}", {field: None}) for field in (*scope, *COSTS, "purchase_price_reference")]
            else:
                zeroes = {**scope, **{field: "0" for field in COSTS}, "purchase_price_reference": "0"}
                requests = [
                    ("POST", "/cost-breakdowns", {**zeroes, "transport": MAXIMUM, "warehouse": "0.01"}),
                    ("POST", "/cost-breakdowns", {**zeroes, "transport": MAXIMUM, "purchase_price_reference": "0.01"}),
                    ("PATCH", f"/cost-breakdowns/{item_id}", {"transport": MAXIMUM}),
                ]
            for method, path, changes in requests:
                invalid = client.request(method, path, json=changes, headers=headers)
                check.assertEqual(invalid.status_code, 422, invalid.text)
                check.assertEqual(state(), before)
            saved = client.get(f"/cost-breakdowns/{item_id}", headers=headers).json()
            check.assertEqual(Decimal(saved["total_additional_cost"]), Decimal("200"))
            check.assertEqual(Decimal(saved["total_estimated_landing_storage_cost"]), Decimal("210200"))
            edited = client.patch(f"/cost-breakdowns/{item_id}", json={"transport": "121.50"}, headers=headers)
            check.assertEqual(edited.status_code, 200, edited.text)
            check.assertEqual(Decimal(edited.json()["warehouse"]), Decimal("80"))
            check.assertEqual(Decimal(edited.json()["total_estimated_landing_storage_cost"]), Decimal("210201.50"))
            # The largest existing representable total remains valid, with zero costs.
            maximum = {**scope, **{field: "0" for field in COSTS}, "purchase_price_reference": MAXIMUM}
            boundary = client.post("/cost-breakdowns", json=maximum, headers=headers)
            check.assertEqual(boundary.status_code, 201, boundary.text)
            check.assertEqual(Decimal(boundary.json()["total_estimated_landing_storage_cost"]), Decimal(MAXIMUM))
    finally:
        app.dependency_overrides.clear()


class CostValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def test_required_cost_values_cannot_be_cleared_to_null(self):
        exercise_cost_validation(self, self.engine, "nulls")

    def test_calculated_cost_totals_fit_existing_storage(self):
        exercise_cost_validation(self, self.engine, "totals")
