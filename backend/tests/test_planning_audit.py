"""Existing planning controls must never save without their audit evidence."""
from datetime import datetime, timezone
from decimal import Decimal
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import Numeric, create_engine, select
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
from app.models.storage_suitability import StorageSuitability
from app.models.user import User
from app.security import create_access_token

RESOURCES = (
    ("buying_zone", "buying-zones", BuyingZone,
     {"price_low": 210000, "price_high": 220000, "reason": "Synthetic observation", "confidence": "Low confidence"},
     {"reason": "Synthetic corrected observation"}),
    ("sell_watch_window", "sell-watch-windows", SellWatchWindow,
     {"start_period": "Synthetic recorded period", "observation": "Synthetic observation", "confidence": "Low confidence"},
     {"observation": "Synthetic corrected observation"}),
    ("storage_suitability", "storage-suitability", StorageSuitability,
     {"suitability_status": "watch", "summary": "Synthetic observation"},
     {"summary": "Synthetic corrected observation"}),
)


def audit_values(model, values):
    return {
        key: Decimal(str(value))
        if value is not None and isinstance(model.__table__.columns[key].type, Numeric)
        else value
        for key, value in values.items()
    }


class PlanningAuditTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin = User(full_name="Synthetic planning Admin", email="planning@example.com",
                         password_hash="unused", role="admin", referral_code="PLANADMIN")
            customer = User(full_name="Synthetic customer", email="planning-user@example.com",
                            password_hash="unused", role="free_user", referral_code="PLANUSER")
            commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
            db.add_all([admin, customer, commodity, market])
            db.flush()
            self.admin_id = admin.id
            self.headers = {"Authorization": "Bearer " + create_access_token(user_id=admin.id)}
            self.customer_headers = {"Authorization": "Bearer " + create_access_token(user_id=customer.id)}
            self.scope = {"commodity_id": commodity.id, "market_id": market.id}
            price = PriceUpdate(**self.scope, unit="1 bag", bag_size=None, price_low=210000,
                                price_high=220000, status="approved", movement="unknown",
                                confidence_level="Low confidence", created_by=admin.id,
                                update_date_time=datetime.now(timezone.utc))
            db.add(price)
            db.commit()
            self.price_id = price.id

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def payload(self, resource):
        linked_price = {"price_update_id": self.price_id} if resource[0] == "storage_suitability" else {}
        return {**self.scope, **resource[3], **linked_price}

    def state(self):
        with Session(self.engine) as db:
            return {
                model.__tablename__: db.execute(select(model.__table__)).all()
                for model in (BuyingZone, SellWatchWindow, StorageSuitability, PriceUpdate, AuditLog)
            }

    def create_failure(self, resource):
        before = self.state()
        with patch("app.services.audit_service.create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            response = self.client.post("/" + resource[1], json=self.payload(resource), headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.state(), before)

    def edit_failure(self, resource):
        created = self.client.post("/" + resource[1], json=self.payload(resource), headers=self.headers)
        self.assertEqual(created.status_code, 201)
        before = self.state()
        with patch("app.services.audit_service.create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            response = self.client.patch(f'/{resource[1]}/{created.json()["id"]}', json=resource[4], headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.state(), before)

    def success(self, resource):
        prefix, path, model, _, changes = resource
        self.assertEqual(self.client.post("/" + path, json=self.payload(resource), headers=self.customer_headers).status_code, 403)
        created = self.client.post("/" + path, json=self.payload(resource), headers=self.headers)
        self.assertEqual(created.status_code, 201)
        item_id = created.json()["id"]
        url = f"/{path}/{item_id}"
        self.assertEqual(self.client.patch(url, json=changes, headers=self.customer_headers).status_code, 403)
        updated = self.client.patch(url, json=changes, headers=self.headers)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["id"], item_id)
        for key, value in changes.items():
            self.assertEqual(updated.json()[key], value)
        with Session(self.engine) as db:
            logs = db.scalars(select(AuditLog).where(AuditLog.table_name == model.__tablename__).order_by(AuditLog.id)).all()
            self.assertEqual([row.action for row in logs], [prefix + ".create", prefix + ".edit"])
            self.assertEqual(audit_values(model, logs[0].new_value), audit_values(model, logs[1].old_value))
            self.assertTrue(all(row.user_id == self.admin_id and row.record_id == item_id for row in logs))
            self.assertEqual(len(db.scalars(select(PriceUpdate)).all()), 1)
            self.assertIsNotNone(db.get(model, item_id))


def attach_test(resource, operation):
    def test(self):
        getattr(self, operation)(resource)
    test.__name__ = "test_" + resource[0] + "_" + operation
    setattr(PlanningAuditTests, test.__name__, test)


for resource in RESOURCES:
    for operation in ("create_failure", "edit_failure", "success"):
        attach_test(resource, operation)
