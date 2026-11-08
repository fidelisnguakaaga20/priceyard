"""Admin-named cost lines add up exactly, and the migration keeps saved totals."""

from decimal import Decimal
import importlib.util
from pathlib import Path
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.user import User
from app.security import create_access_token

MIGRATION = Path(__file__).resolve().parents[1] / "migrations/versions/0023_cost_breakdown_items.py"


class CostItemTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin = User(
                full_name="Synthetic cost Admin",
                email="cost-items@example.com",
                password_hash="unused",
                role="admin",
                referral_code="COSTITEMS",
            )
            commodity, market = Commodity(name="Honey Beans"), Market(name="Kwali Market")
            db.add_all([admin, commodity, market])
            db.commit()
            self.headers = {"Authorization": "Bearer " + create_access_token(user_id=admin.id)}
            self.scope = {"commodity_id": commodity.id, "market_id": market.id}

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_named_items_are_saved_and_totalled(self):
        items = [{"name": " Sack ", "amount": "500"}, {"name": "Chemical", "amount": "2000.50"}]
        created = self.client.post(
            "/cost-breakdowns",
            json={**self.scope, "purchase_price_reference": "35000", "cost_items": items},
            headers=self.headers,
        )
        self.assertEqual(created.status_code, 201, created.text)
        body = created.json()
        self.assertEqual(
            [(x["name"], Decimal(x["amount"])) for x in body["cost_items"]],
            [("Sack", Decimal("500")), ("Chemical", Decimal("2000.50"))],
        )
        self.assertEqual(Decimal(body["total_additional_cost"]), Decimal("2500.50"))
        self.assertEqual(Decimal(body["total_estimated_landing_storage_cost"]), Decimal("37500.50"))

        edited = self.client.patch(
            f"/cost-breakdowns/{body['id']}",
            json={"cost_items": [{"name": "Transport", "amount": "1500"}]},
            headers=self.headers,
        )
        self.assertEqual(edited.status_code, 200, edited.text)
        self.assertEqual(Decimal(edited.json()["total_estimated_landing_storage_cost"]), Decimal("36500"))
        # Editing only the purchase price keeps the saved lines.
        price_only = self.client.patch(
            f"/cost-breakdowns/{body['id']}", json={"purchase_price_reference": "40000"}, headers=self.headers
        )
        self.assertEqual([x["name"] for x in price_only.json()["cost_items"]], ["Transport"])
        self.assertEqual(Decimal(price_only.json()["total_estimated_landing_storage_cost"]), Decimal("41500"))

    def test_invalid_items_are_rejected(self):
        for items in (
            [{"name": "", "amount": "1"}],
            [{"name": "Sack", "amount": "-1"}],
            [{"name": "Sack", "amount": "0.001"}],
            [{"name": "x" * 101, "amount": "1"}],
        ):
            with self.subTest(items=items):
                response = self.client.post(
                    "/cost-breakdowns",
                    json={**self.scope, "purchase_price_reference": "1", "cost_items": items},
                    headers=self.headers,
                )
                self.assertEqual(response.status_code, 422, response.text)

    def test_migration_moves_fixed_costs_into_named_lines_without_changing_totals(self):
        spec = importlib.util.spec_from_file_location("migration_0023", MIGRATION)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        engine = create_engine("sqlite+pysqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE cost_breakdowns (id INTEGER PRIMARY KEY, transport NUMERIC(14,2), warehouse NUMERIC(14,2), security NUMERIC(14,2), market_charges NUMERIC(14,2), loading_offloading NUMERIC(14,2), other_costs NUMERIC(14,2), total_additional_cost NUMERIC(14,2))"
                )
            )
            connection.execute(
                text("INSERT INTO cost_breakdowns VALUES (1, 120, 80, 0, 0, 0, 0, 200), (2, 0, 0, 0, 0, 0, 0, 0)")
            )
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
            rows = {row.id: row for row in connection.execute(text("SELECT * FROM cost_breakdowns"))}
            self.assertIn('"Transport"', rows[1].cost_items)
            self.assertIn('"120.00"', rows[1].cost_items)
            self.assertIn('"Warehouse"', rows[1].cost_items)
            self.assertEqual(Decimal(str(rows[1].transport)), 0)
            self.assertEqual(Decimal(str(rows[1].total_additional_cost)), Decimal("200"))
            self.assertEqual(rows[2].cost_items, "[]")
            with Operations.context(MigrationContext.configure(connection)):
                migration.downgrade()
            row = connection.execute(text("SELECT transport, warehouse FROM cost_breakdowns WHERE id = 1")).one()
            self.assertEqual(
                (Decimal(str(row.transport)), Decimal(str(row.warehouse))), (Decimal("120"), Decimal("80"))
            )
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
