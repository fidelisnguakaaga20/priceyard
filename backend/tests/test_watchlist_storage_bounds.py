"""Targets must survive storage exactly, within the existing NUMERIC(14,2)."""
from decimal import Decimal
import unittest
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.user import User
from app.models.watchlist import Watchlist
from app.security import create_access_token


def exercise_watchlist_storage(check, engine, invalid_values):
    Base.metadata.create_all(engine)
    suffix = uuid.uuid4().hex[:8]
    with Session(engine) as db:
        owner = User(full_name="Synthetic target owner", email=f"target-{suffix}@example.com", password_hash="unused", role="free_user", referral_code="W"+suffix)
        other = User(full_name="Synthetic other owner", email=f"other-{suffix}@example.com", password_hash="unused", role="free_user", referral_code="O"+suffix)
        commodity, market = Commodity(name="Synthetic Egusi "+suffix), Market(name="Synthetic Kwali "+suffix)
        db.add_all([owner, other, commodity, market]); db.commit()
        headers = {"Authorization": "Bearer "+create_access_token(user_id=owner.id)}
        other_headers = {"Authorization": "Bearer "+create_access_token(user_id=other.id)}
        scope = {"commodity_id": commodity.id, "market_id": market.id}

    def sessions():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            for target in (None, "0", "210000", "999999999999.99"):
                payload = {**scope, "target_price": target, "target_direction": None if target is None else "at_or_below"}
                created = client.post("/watchlist", json=payload, headers=headers)
                check.assertEqual(created.status_code, 201, created.text)
                item_id = created.json()["id"]
                with Session(engine) as db:
                    stored = db.get(Watchlist, item_id)
                    check.assertEqual(stored.target_price, None if target is None else Decimal(target))
                    check.assertEqual(stored.target_direction, payload["target_direction"])
                listed = client.get("/watchlist", headers=headers).json()
                row = next(item for item in listed if item["id"] == item_id)
                check.assertEqual(None if row["target_price"] is None else Decimal(str(row["target_price"])), None if target is None else Decimal(target))
                check.assertEqual(client.post("/watchlist", json=payload, headers=headers).status_code, 409)
                check.assertNotIn(item_id, [item["id"] for item in client.get("/watchlist", headers=other_headers).json()])
                check.assertEqual(client.delete(f"/watchlist/{item_id}", headers=other_headers).status_code, 404)
                check.assertEqual(client.delete(f"/watchlist/{item_id}", headers=headers).status_code, 204)

            with Session(engine) as db:
                before = db.execute(select(Watchlist.__table__)).all()
            for value in invalid_values:
                response = client.post("/watchlist", json={**scope, "target_price": value, "target_direction": "at_or_above"}, headers=headers)
                check.assertEqual(response.status_code, 422, response.text)
                check.assertTrue(any(item["loc"][-1] == "target_price" for item in response.json()["detail"]))
            check.assertEqual(client.get("/watchlist").status_code, 401)
            with Session(engine) as db:
                check.assertEqual(db.execute(select(Watchlist.__table__)).all(), before)
    finally:
        app.dependency_overrides.clear()


class WatchlistStorageBoundsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def test_out_of_storage_range_returns_validation_without_writes(self):
        exercise_watchlist_storage(self, self.engine, ("1000000000000", "1e100"))

    def test_sub_kobo_target_is_not_silently_rounded(self):
        exercise_watchlist_storage(self, self.engine, ("210000.001", "0.009"))
