import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.user import User
from app.schemas.commodity_schema import CommodityResponse
from app.schemas.market_schema import MarketResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records

RESOURCES = ((Commodity, CommodityResponse, "/commodities"), (Market, MarketResponse, "/markets"))
ORDER = (("name", False), ("id", False))


def seed_catalog(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = User(full_name="Synthetic catalog Admin", email="catalog-page@example.com", password_hash="unused", role="admin", referral_code="CATPAGE")
        customer = User(full_name="Synthetic catalog customer", email="catalog-customer@example.com", password_hash="unused", role="free_user", referral_code="CATFREE")
        db.add_all([admin, customer])
        for index in range(205):
            db.add(Commodity(name=f"Synthetic catalog {index:03}", description="Saved synthetic description", is_active=index<3, is_upcoming=index==1))
            market_index = 100 if index == 101 else index
            db.add(Market(name=f"Synthetic market {market_index:03}", state="FCT" if index==100 else "Benue" if index==101 else None,
                          is_active=index<3, description="Saved synthetic market description"))
        db.commit()
        return admin.id, customer.id


def verify_catalog_pages(check, engine):
    seed_catalog(engine)
    with Session(engine) as db:
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all() for model, *_ in RESOURCES}
    for model, schema, _ in RESOURCES:
        expected = [row.id for row in sorted(before[model], key=lambda row: (row.name, row.id))]
        actual = []
        for offset, count in ((0,100),(100,100),(200,5),(300,0)):
            statements = []
            def query(*args):
                statements.append(True)
            event.listen(engine, "before_cursor_execute", query)
            try:
                with Session(engine) as db:
                    page = admin_record_page(db, model, schema, offset=offset, order=ORDER)
                    check.assertLessEqual(len(db.identity_map), 100)
            finally:
                event.remove(engine, "before_cursor_execute", query)
            check.assertEqual(len(statements), 1)
            check.assertEqual((page.total,len(page.items)), (205,count))
            check.assertEqual([row.id for row in page.items], expected[offset:offset+100])
            actual.extend(row.id for row in page.items)
        check.assertEqual(actual, expected)
        full = json.loads("".join(stream_admin_records(engine, model, schema, order=ORDER)))
        check.assertEqual([row["id"] for row in full], expected)
        public = json.loads("".join(stream_admin_records(engine, model, schema, order=ORDER, where=(model.is_active.is_(True),))))
        check.assertEqual([row["id"] for row in public], [row.id for row in before[model] if row.is_active])
    with Session(engine) as db:
        for model, *_ in RESOURCES:
            check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(), before[model])


class CatalogPagingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        app.dependency_overrides.clear(); self.engine.dispose()

    def test_catalog_pages_keep_all_names_states_active_flags_and_identity(self):
        verify_catalog_pages(self, self.engine)

    def test_public_complete_metadata_and_private_admin_pages_preserve_contracts(self):
        owner, customer = seed_catalog(self.engine)
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        admin = {"Authorization": "Bearer " + create_access_token(user_id=owner)}
        free = {"Authorization": "Bearer " + create_access_token(user_id=customer)}
        with TestClient(app) as client:
            for _, _, path in RESOURCES:
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 3)
                self.assertTrue(all(row["is_active"] for row in response.json()))
                self.assertNotIn("private", response.headers.get("cache-control", ""))
                self.assertNotIn("no-store", response.headers.get("cache-control", ""))
                for endpoint in (path+"/admin/all", path+"/admin/page"):
                    self.assertEqual(client.get(endpoint).status_code,401)
                    self.assertEqual(client.get(endpoint,headers=free).status_code,403)
                legacy = client.get(path+"/admin/all", headers=admin)
                self.assertEqual(len(legacy.json()),205)
                collected=[]
                for offset in (0,100,200):
                    response = client.get(f"{path}/admin/page?offset={offset}",headers=admin)
                    self.assertEqual(response.status_code,200)
                    self.assertEqual(response.json()["total"],205)
                    collected.extend(response.json()["items"])
                self.assertEqual(collected,legacy.json())
                self.assertEqual(client.get(path+"/admin/page?offset=-1",headers=admin).status_code,422)
