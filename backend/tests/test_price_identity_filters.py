from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.security import create_access_token
from app.services.price_update_service import list_latest_approved_price_updates, list_price_history


def seed_identity(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic identity Admin", email="identity-filter@example.com", password_hash="unused", role="admin", referral_code="FILTERID")
        commodities = [Commodity(name="Egusi"), Commodity(name="Egusi synthetic %20")]
        markets = [Market(name="Kwali Market", state="FCT"), Market(name="Kwali Market", state="Benue")]
        db.add_all([owner, *commodities, *markets])
        db.flush()
        moment = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
        for commodity in commodities:
            for market in markets:
                for offset in range(2):
                    db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id, unit="1 bag", bag_size=None,
                        price_low=210000 + commodity.id * 100 + market.id * 10 + offset, price_high=220000,
                        update_date_time=moment + timedelta(hours=offset), confidence_level="Low confidence",
                        movement="unknown", status="approved", created_by=owner.id, source_1="PRIVATE-IDENTITY-SOURCE"))
        db.commit()
        return owner.id, [row.id for row in commodities], [row.id for row in markets]


def verify_identity_filters(check, engine):
    _, commodities, markets = seed_identity(engine)
    with Session(engine) as db:
        before = db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
        check.assertEqual(len(list_latest_approved_price_updates(db, commodity_search="Egusi", market_search="Kwali")), 4)
        for commodity in commodities:
            for market in markets:
                current = list_latest_approved_price_updates(db, commodity_id=commodity, market_id=market)
                history = list_price_history(db, commodity_id=commodity, market_id=market)
                check.assertEqual(len(current), 1)
                check.assertEqual(len(history), 2)
                check.assertTrue(all((row.commodity_id, row.market_id) == (commodity, market) for row in [*current, *history]))
                check.assertEqual(current[0].id, history[-1].id)
        original_ids = [row.id for row in list_price_history(db, commodity_id=commodities[0])]
        item = db.get(Commodity, commodities[0])
        item.name = "Egusi renamed synthetic"
        db.commit()
        check.assertEqual([row.id for row in list_price_history(db, commodity_id=commodities[0])], original_ids)
        item.name = "Egusi"
        db.commit()
        check.assertEqual(list_price_history(db, commodity_id=commodities[0], commodity_search="%20"), [])
        check.assertEqual(list_latest_approved_price_updates(db, commodity_id=2147483647), [])
        check.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(), before)


class PriceIdentityFilterTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_exact_ids_distinguish_prefix_names_and_same_named_markets_after_rename(self):
        verify_identity_filters(self, self.engine)

    def prepare_client(self):
        owner_id, commodities, markets = seed_identity(self.engine)
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        return TestClient(app), {"Authorization": "Bearer " + create_access_token(user_id=owner_id)}, commodities, markets

    def test_http_current_history_forward_existing_ids_without_exposing_sources(self):
        client, headers, commodities, markets = self.prepare_client()
        with client:
            query = f"?commodity_id={commodities[0]}&market_id={markets[1]}"
            for path, count, credentials in (("/price-updates", 1, {}), ("/price-updates/history", 2, headers)):
                response = client.get(path + query, headers=credentials)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), count)
                self.assertTrue(all(row["commodity_id"] == commodities[0] and row["market_id"] == markets[1] for row in response.json()))
                self.assertNotIn("PRIVATE-IDENTITY", response.text)
            self.assertEqual(client.get("/price-updates/history" + query).status_code, 401)
            self.assertEqual(len(client.get("/price-updates?commodity=Egusi&market=Kwali").json()), 4)

    def test_http_id_storage_bounds_and_conflicting_name_filters(self):
        client, headers, commodities, _ = self.prepare_client()
        with client:
            for path in ("/price-updates", "/price-updates/history"):
                for key in ("commodity_id", "market_id"):
                    for value in ("0", "-1", "2147483648", "not-an-id"):
                        self.assertEqual(client.get(f"{path}?{key}={value}", headers=headers).status_code, 422)
            self.assertEqual(client.get(f"/price-updates?commodity_id={commodities[0]}&commodity=%2520").json(), [])

    def test_share_uses_existing_price_identity_after_rename_but_only_current_amounts(self):
        client, _, commodities, _ = self.prepare_client()
        with Session(self.engine) as db:
            historical = db.scalars(select(PriceUpdate).where(PriceUpdate.commodity_id == commodities[0]).order_by(PriceUpdate.id)).first()
            historical.price_low = 12345
            historical.price_high = 23456
            historical_id = historical.id
            db.get(Commodity, commodities[0]).name = "Renamed synthetic Egusi"
            db.commit()
        with client:
            response = client.get(f"/share/commodities/Egusi?pu={historical_id}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Renamed synthetic Egusi", response.text)
            self.assertIn(f"commodity_id={commodities[0]}", response.text)
            for forbidden in ("12,345", "23,456", "PRIVATE-IDENTITY"):
                self.assertNotIn(forbidden, response.text)
            self.assertIn("220,000", response.text)

    def test_share_exact_legacy_literal_name_and_coming_soon_identity(self):
        client, _, commodities, _ = self.prepare_client()
        # Pass the already-decoded ASGI path value directly: TestClient's
        # synthetic transport decodes a literal percent escape a second time.
        from app.routes.share_routes import share_commodity_card
        with Session(self.engine) as db:
            response = share_commodity_card("Egusi synthetic %20", pu=None, commodity_id=None, db=db)
            self.assertIn(f"commodity_id={commodities[1]}", response.body.decode())
        with client:
            response = client.get("/share/commodities/Egusi")
            self.assertIn(f"commodity_id={commodities[0]}", response.text)
            self.assertNotIn(f"commodity_id={commodities[1]}", response.text)
        with Session(self.engine) as db:
            future = Commodity(name="Future renamed synthetic", is_upcoming=True)
            db.add(future); db.commit(); future_id = future.id
        with client:
            response = client.get(f"/share/commodities/Old%20future?commodity_id={future_id}&v=synthetic")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Future renamed synthetic", response.text)
            self.assertIn("Coming Soon", response.text)
            self.assertIn(f"commodity_id={future_id}", response.text)

    def test_share_invalid_unapproved_or_conflicting_identity_never_falls_back_to_name(self):
        client, _, commodities, _ = self.prepare_client()
        with Session(self.engine) as db:
            price = db.scalars(select(PriceUpdate).order_by(PriceUpdate.id)).first()
            price.status = "pending"; price_id = price.id; db.commit()
        with client:
            for query in ("pu=2147483647", f"pu={price_id}", "commodity_id=2147483647", f"pu={price_id + 1}&commodity_id={commodities[1]}"):
                self.assertEqual(client.get("/share/commodities/Egusi?" + query).status_code, 404)
            for value in ("0", "2147483648", "not-an-id"):
                self.assertEqual(client.get("/share/commodities/Egusi?pu=" + value).status_code, 422)

    def test_share_name_boundary_matches_existing_catalog_storage(self):
        client, _, _, _ = self.prepare_client()
        with client:
            self.assertEqual(client.get("/share/commodities/" + "n"*100).status_code, 200)
            self.assertEqual(client.get("/share/commodities/" + "n"*101).status_code, 422)
