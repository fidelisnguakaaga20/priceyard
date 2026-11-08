"""Owner-side CR-03 verification against the configured PostgreSQL database."""
from __future__ import annotations

import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if not (BACKEND_DIR / ".env").exists():
    raise SystemExit("FAIL: backend/.env is missing")
os.chdir(BACKEND_DIR)
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select, text  # noqa: E402

from app.database import get_session_factory  # noqa: E402
from app.main import app  # noqa: E402
from app.models.commodity import Commodity  # noqa: E402
from app.models.market import Market  # noqa: E402
from app.models.price_update import PriceUpdate  # noqa: E402
from app.models.subscription import Subscription  # noqa: E402
from app.models.user import User  # noqa: E402

if len(sys.argv) != 2:
    raise SystemExit("Usage: python ../docs/evidence/cr-03-owner-smoke.py YOUR_ADMIN_EMAIL")

admin_email = sys.argv[1].strip().lower()
admin_password = getpass.getpass("Existing PriceYard admin password (not displayed): ")
client = TestClient(app)
SessionLocal = get_session_factory()
results: dict[str, str] = {}
suffix = uuid4().hex
test_user_email = f"cr03-user-{suffix}@example.com"
test_password = "CR03-Temporary-Password-123!"
test_commodity_name = f"CR03 Commodity {suffix[:8]}"
test_market_name = f"CR03 Market {suffix[:8]}"
test_user_id: int | None = None
test_commodity_id: int | None = None
test_market_id: int | None = None
test_price_id: int | None = None


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    results[label] = "PASS"


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def names(response) -> list[str]:
    return sorted(item["name"] for item in response.json())


try:
    with SessionLocal() as db:
        version = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
        expect(version == "0006_cr03_egusi_kwali", "CR-03 migration is current")
        active_commodities = list(db.scalars(select(Commodity).where(Commodity.is_active.is_(True))).all())
        active_markets = list(db.scalars(select(Market).where(Market.is_active.is_(True))).all())
        expect([item.name for item in active_commodities] == ["Egusi"], "database active commodity is exactly Egusi")
        expect([item.name for item in active_markets] == ["Kwali Market"], "database active market is exactly Kwali Market")
        egusi_id = active_commodities[0].id
        kwali_id = active_markets[0].id

    login = client.post("/auth/login", json={"email": admin_email, "password": admin_password})
    expect(login.status_code == 200, "existing admin login works")
    admin_token = login.json()["access_token"]

    public_commodities = client.get("/commodities")
    public_markets = client.get("/markets")
    expect(public_commodities.status_code == 200 and names(public_commodities) == ["Egusi"], "public commodity list shows only Egusi")
    expect(public_markets.status_code == 200 and names(public_markets) == ["Kwali Market"], "public market list shows only Kwali Market")

    latest = client.get("/price-updates")
    history = client.get("/price-updates/history")
    expect(latest.status_code == 200, "public latest prices load")
    expect(history.status_code == 200, "public price history loads")
    expect(all(x["commodity"]["name"] == "Egusi" and x["market"]["name"] == "Kwali Market" for x in latest.json()), "public latest prices are Egusi/Kwali only")
    expect(all(x["commodity"]["name"] == "Egusi" and x["market"]["name"] == "Kwali Market" for x in history.json()), "public history is Egusi/Kwali only")

    register = client.post("/auth/register", json={"full_name": "CR-03 User", "email": test_user_email, "password": test_password})
    expect(register.status_code == 201, "existing registration flow works")
    test_user_id = register.json()["id"]
    user_login = client.post("/auth/login", json={"email": test_user_email, "password": test_password})
    expect(user_login.status_code == 200, "existing normal-user login works")
    user_token = user_login.json()["access_token"]
    subscription = client.get(f"/subscriptions/{test_user_id}", headers=auth(user_token))
    expect(subscription.status_code == 200, "existing trial/subscription self-view works")
    expect(client.get("/commodities/admin/all", headers=auth(user_token)).status_code == 403, "non-admin all-commodity access blocked")
    expect(client.get("/markets/admin/all", headers=auth(user_token)).status_code == 403, "non-admin all-market access blocked")

    all_commodities = client.get("/commodities/admin/all", headers=auth(admin_token))
    all_markets = client.get("/markets/admin/all", headers=auth(admin_token))
    expect(all_commodities.status_code == 200, "admin can view all commodities")
    expect(all_markets.status_code == 200, "admin can view all markets")
    expect(any(item["name"] == "Egusi" for item in all_commodities.json()), "admin all-commodity view contains Egusi")
    expect(any(item["name"] == "Kwali Market" for item in all_markets.json()), "admin all-market view contains Kwali Market")

    commodity_create = client.post("/commodities", headers=auth(admin_token), json={"name": test_commodity_name})
    expect(commodity_create.status_code == 201, "admin can add a new commodity")
    test_commodity_id = commodity_create.json()["id"]
    expect(test_commodity_name in names(client.get("/commodities")), "new active commodity becomes publicly selectable")
    commodity_deactivate = client.patch(f"/commodities/{test_commodity_id}", headers=auth(admin_token), json={"is_active": False})
    expect(commodity_deactivate.status_code == 200, "admin can deactivate a commodity")
    expect(test_commodity_name not in names(client.get("/commodities")), "inactive commodity is hidden publicly")
    expect(any(item["id"] == test_commodity_id and not item["is_active"] for item in client.get("/commodities/admin/all", headers=auth(admin_token)).json()), "admin can still see inactive commodity")
    commodity_reactivate = client.patch(f"/commodities/{test_commodity_id}", headers=auth(admin_token), json={"is_active": True})
    expect(commodity_reactivate.status_code == 200, "admin can reactivate a commodity")

    market_create = client.post("/markets", headers=auth(admin_token), json={"name": test_market_name, "state": "FCT", "country": "Nigeria"})
    expect(market_create.status_code == 201, "admin can add a new market")
    test_market_id = market_create.json()["id"]
    expect(test_market_name in names(client.get("/markets")), "new active market becomes publicly selectable")
    market_deactivate = client.patch(f"/markets/{test_market_id}", headers=auth(admin_token), json={"is_active": False})
    expect(market_deactivate.status_code == 200, "admin can deactivate a market")
    expect(test_market_name not in names(client.get("/markets")), "inactive market is hidden publicly")
    expect(any(item["id"] == test_market_id and not item["is_active"] for item in client.get("/markets/admin/all", headers=auth(admin_token)).json()), "admin can still see inactive market")
    market_reactivate = client.patch(f"/markets/{test_market_id}", headers=auth(admin_token), json={"is_active": True})
    expect(market_reactivate.status_code == 200, "admin can reactivate a market")

    price_payload = {
        "commodity_id": egusi_id,
        "market_id": kwali_id,
        "price_low": "140000.00",
        "price_high": "145000.00",
        "average_price": "142500.00",
        "unit": "bag",
        "bag_size": "verification bag",
        "commodity_type": "Unpeeled Egusi",
        "market_day": "Tuesday",
        "time_of_day": "morning",
        "movement": "unknown",
        "confidence_level": "Admin confirmed",
        "update_date_time": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "is_outdated": False,
        "possible_meaning": "CR-03 verification record; verify current market conditions.",
        "suggested_action": "Watch",
        "notes": "Temporary CR-03 verification record.",
    }
    price_create = client.post("/price-updates", headers=auth(admin_token), json=price_payload)
    expect(price_create.status_code == 201, "admin can create an Egusi/Kwali price update without foreign-key error")
    test_price_id = price_create.json()["id"]
    expect(price_create.json()["status"] == "pending", "verification price update remains pending")
    expect(client.get("/price-updates/admin/history", headers=auth(user_token)).status_code == 403, "non-admin all-history access blocked")
    expect(client.get("/price-updates/admin/history", headers=auth(admin_token)).status_code == 200, "admin all-history access works")

    expect(client.delete(f"/price-updates/{test_price_id}", headers=auth(admin_token)).status_code == 204, "temporary price update cleanup works")
    test_price_id = None
    expect(client.delete(f"/commodities/{test_commodity_id}", headers=auth(admin_token)).status_code == 204, "temporary commodity cleanup works")
    test_commodity_id = None
    expect(client.delete(f"/markets/{test_market_id}", headers=auth(admin_token)).status_code == 204, "temporary market cleanup works")
    test_market_id = None

    expect(names(client.get("/commodities")) == ["Egusi"], "final public commodity state is Egusi only")
    expect(names(client.get("/markets")) == ["Kwali Market"], "final public market state is Kwali Market only")
    print(results)

finally:
    with SessionLocal() as db:
        if test_price_id is not None:
            item = db.get(PriceUpdate, test_price_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if test_commodity_id is not None:
            item = db.get(Commodity, test_commodity_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if test_market_id is not None:
            item = db.get(Market, test_market_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if test_user_id is not None:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == test_user_id))
            if subscription is not None:
                db.delete(subscription)
                db.flush()
            user = db.get(User, test_user_id)
            if user is not None:
                db.delete(user)
        db.commit()

print("CR-03 OWNER SMOKE: PASS")
