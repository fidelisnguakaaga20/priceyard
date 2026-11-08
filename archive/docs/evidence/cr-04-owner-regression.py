"""Owner-side CR-04 regression verification against configured PostgreSQL."""
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
from sqlalchemy.engine import make_url  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.database import get_session_factory  # noqa: E402
from app.main import app  # noqa: E402
from app.models.commodity import Commodity  # noqa: E402
from app.models.feedback import Feedback  # noqa: E402
from app.models.market import Market  # noqa: E402
from app.models.price_update import PriceUpdate  # noqa: E402
from app.models.subscription import Subscription  # noqa: E402
from app.models.user import User  # noqa: E402

if len(sys.argv) != 2:
    raise SystemExit("Usage: python ../docs/evidence/cr-04-owner-regression.py YOUR_ADMIN_EMAIL")

admin_email = sys.argv[1].strip().lower()
admin_password = getpass.getpass("Existing PriceYard admin password (not displayed): ")
settings = get_settings()
if settings.database_url:
    settings.database_url = make_url(settings.database_url).update_query_dict(
        {"connect_timeout": "15"}
    ).render_as_string(hide_password=False)
client = TestClient(app)
SessionLocal = get_session_factory()
results: dict[str, str] = {}
suffix = uuid4().hex
test_email = f"cr04-user-{suffix}@example.com"
test_password = "CR04-Temporary-Password-123!"
commodity_name = f"CR04 Commodity {suffix[:8]}"
market_name = f"CR04 Market {suffix[:8]}"
test_user_id: int | None = None
commodity_id: int | None = None
market_id: int | None = None
price_id: int | None = None
feedback_id: int | None = None


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    results[label] = "PASS"
    print(f"PASS: {label}", flush=True)


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def names(response) -> list[str]:
    return sorted(item["name"] for item in response.json())


try:
    print("CHECK: database preflight", flush=True)
    with SessionLocal() as db:
        version = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
        expect(version == "0006_cr03_egusi_kwali", "database migration remains at CR-03 head")
        active_commodities = list(db.scalars(select(Commodity).where(Commodity.is_active.is_(True))).all())
        active_markets = list(db.scalars(select(Market).where(Market.is_active.is_(True))).all())
        expect([x.name for x in active_commodities] == ["Egusi"], "only Egusi is active")
        expect([x.name for x in active_markets] == ["Kwali Market"], "only Kwali Market is active")
        egusi_id = active_commodities[0].id
        kwali_id = active_markets[0].id

    expect(client.get("/health").status_code == 200, "backend health works")
    expect(client.get("/auth/me").status_code == 401, "missing JWT is rejected")
    expect(client.get("/buying-zones").status_code == 401, "guest is blocked from full-access intelligence")
    expect(names(client.get("/commodities")) == ["Egusi"], "public commodities remain Egusi only")
    expect(names(client.get("/markets")) == ["Kwali Market"], "public markets remain Kwali Market only")
    latest = client.get("/price-updates")
    expect(latest.status_code == 200, "public prices load")
    expect(all(x["commodity"]["name"] == "Egusi" and x["market"]["name"] == "Kwali Market" for x in latest.json()), "public prices do not leak inactive data")

    print("CHECK: admin login and protected reads", flush=True)
    admin_login = client.post("/auth/login", json={"email": admin_email, "password": admin_password})
    expect(admin_login.status_code == 200, "admin login works")
    admin_token = admin_login.json()["access_token"]
    admin_headers = auth(admin_token)
    admin_me = client.get("/auth/me", headers=admin_headers)
    expect(admin_me.status_code == 200 and admin_me.json()["role"] == "admin", "admin profile and role work")
    expect("password_hash" not in admin_me.json(), "password hash is not returned")
    expect(client.get("/users", headers=admin_headers).status_code == 200, "admin users API works")
    expect(client.get("/subscriptions", headers=admin_headers).status_code == 200, "admin subscriptions API works")
    expect(client.get("/commodities/admin/all", headers=admin_headers).status_code == 200, "admin commodity data loads")
    expect(client.get("/markets/admin/all", headers=admin_headers).status_code == 200, "admin market data loads")
    expect(client.get("/price-updates/admin/history", headers=admin_headers).status_code == 200, "admin price history loads")
    expect(client.get("/feedback/summary", headers=admin_headers).status_code == 200, "admin feedback summary loads")
    expect(client.get("/buying-zones", headers=admin_headers).status_code == 200, "admin full access works")

    print("CHECK: registration and subscription access matrix", flush=True)
    register_payload = {"full_name": "CR-04 Regression User", "email": test_email, "password": test_password}
    register = client.post("/auth/register", json=register_payload)
    expect(register.status_code == 201, "registration works")
    test_user_id = register.json()["id"]
    expect(client.post("/auth/register", json=register_payload).status_code == 409, "duplicate registration is rejected")
    expect(client.post("/auth/login", json={"email": test_email, "password": "wrong-password"}).status_code == 401, "wrong login is rejected")
    user_login = client.post("/auth/login", json={"email": test_email, "password": test_password})
    expect(user_login.status_code == 200, "normal-user login works")
    user_token = user_login.json()["access_token"]
    user_headers = auth(user_token)
    user_me = client.get("/auth/me", headers=user_headers)
    expect(user_me.status_code == 200 and "password_hash" not in user_me.json(), "normal-user profile works safely")
    subscription = client.get(f"/subscriptions/{test_user_id}", headers=user_headers)
    expect(subscription.status_code == 200 and subscription.json()["status"] == "trial", "new user receives trial status")
    trial_start = datetime.fromisoformat(subscription.json()["trial_started_at"])
    trial_end = datetime.fromisoformat(subscription.json()["trial_ends_at"])
    expect((trial_end - trial_start).days == 14, "trial lasts 14 days")
    expect(client.get("/buying-zones", headers=user_headers).status_code == 200, "trial user has full access")
    expect(client.get("/users", headers=user_headers).status_code == 403, "non-admin user management is blocked")
    expect(client.get("/commodities/admin/all", headers=user_headers).status_code == 403, "non-admin commodity administration is blocked")

    status_expectations = [("active", 200), ("free", 403), ("expired", 403), ("cancelled", 403), ("trial", 200)]
    for subscription_status, access_status in status_expectations:
        changed = client.patch(f"/subscriptions/{test_user_id}/status", headers=admin_headers, json={"status": subscription_status})
        expect(changed.status_code == 200 and changed.json()["status"] == subscription_status, f"admin can set {subscription_status} status")
        expect(client.get("/buying-zones", headers=user_headers).status_code == access_status, f"{subscription_status} access rule works")
    expect(client.patch(f"/subscriptions/{test_user_id}/status", headers=admin_headers, json={"status": "invalid"}).status_code == 422, "invalid subscription status is rejected")

    deactivated = client.patch(f"/users/{test_user_id}", headers=admin_headers, json={"is_active": False})
    expect(deactivated.status_code == 200, "admin can deactivate a user")
    expect(client.get("/auth/me", headers=user_headers).status_code == 403, "inactive user is blocked")
    expect(client.patch(f"/users/{test_user_id}", headers=admin_headers, json={"is_active": True}).status_code == 200, "admin can reactivate a user")

    print("CHECK: admin CRUD and public active-data filtering", flush=True)
    commodity_create = client.post("/commodities", headers=admin_headers, json={"name": commodity_name})
    expect(commodity_create.status_code == 201, "admin commodity create works")
    commodity_id = commodity_create.json()["id"]
    expect(client.patch(f"/commodities/{commodity_id}", headers=admin_headers, json={"is_active": False}).status_code == 200, "admin commodity deactivate works")
    expect(commodity_name not in names(client.get("/commodities")), "inactive commodity stays hidden publicly")
    expect(client.patch(f"/commodities/{commodity_id}", headers=admin_headers, json={"is_active": True}).status_code == 200, "admin commodity reactivate works")

    market_create = client.post("/markets", headers=admin_headers, json={"name": market_name, "state": "FCT", "country": "Nigeria"})
    expect(market_create.status_code == 201, "admin market create works")
    market_id = market_create.json()["id"]
    expect(client.patch(f"/markets/{market_id}", headers=admin_headers, json={"is_active": False}).status_code == 200, "admin market deactivate works")
    expect(market_name not in names(client.get("/markets")), "inactive market stays hidden publicly")
    expect(client.patch(f"/markets/{market_id}", headers=admin_headers, json={"is_active": True}).status_code == 200, "admin market reactivate works")

    price_payload = {
        "commodity_id": egusi_id,
        "market_id": kwali_id,
        "price_low": "140000.00",
        "price_high": "145000.00",
        "average_price": "142500.00",
        "unit": "bag",
        "bag_size": "CR-04 verification bag",
        "commodity_type": "Unpeeled Egusi",
        "market_day": "Tuesday",
        "time_of_day": "morning",
        "movement": "unknown",
        "confidence_level": "Admin confirmed",
        "update_date_time": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "is_outdated": False,
        "possible_meaning": "Regression verification observation only.",
        "suggested_action": "Watch",
        "notes": "Temporary CR-04 record.",
    }
    price_create = client.post("/price-updates", headers=admin_headers, json=price_payload)
    expect(price_create.status_code == 201, "admin price update create works")
    price_id = price_create.json()["id"]
    approved = client.patch(f"/price-updates/{price_id}/approve", headers=admin_headers)
    expect(approved.status_code == 200 and approved.json()["status"] == "approved", "admin price approval works")
    expect(client.get(f"/price-updates/{price_id}").status_code == 200, "approved price is publicly retrievable")
    expect(client.patch(f"/price-updates/{price_id}/mark-outdated", headers=admin_headers).status_code == 200, "admin outdated action works")

    print("CHECK: feedback and cleanup", flush=True)
    expect(client.post("/feedback", headers=user_headers, json={"rating": 0}).status_code == 422, "feedback rating 0 is rejected")
    expect(client.post("/feedback", headers=user_headers, json={"rating": 6}).status_code == 422, "feedback rating 6 is rejected")
    feedback_create = client.post("/feedback", headers=user_headers, json={"rating": 5, "comment": "CR-04 regression feedback", "continue_using_feedback": True})
    expect(feedback_create.status_code == 201, "feedback submission works")
    feedback_id = feedback_create.json()["id"]
    expect(client.get("/feedback", headers=user_headers).status_code == 403, "ordinary user cannot browse private feedback")
    expect(client.get("/feedback?rating=5", headers=admin_headers).status_code == 200, "admin feedback filter works")
    expect(client.get("/feedback/summary", headers=admin_headers).status_code == 200, "admin feedback summary still works")

    expect(client.delete(f"/feedback/{feedback_id}", headers=admin_headers).status_code == 204, "temporary feedback cleanup works")
    feedback_id = None
    expect(client.delete(f"/price-updates/{price_id}", headers=admin_headers).status_code == 204, "temporary price cleanup works")
    price_id = None
    expect(client.delete(f"/commodities/{commodity_id}", headers=admin_headers).status_code == 204, "temporary commodity cleanup works")
    commodity_id = None
    expect(client.delete(f"/markets/{market_id}", headers=admin_headers).status_code == 204, "temporary market cleanup works")
    market_id = None
    expect(names(client.get("/commodities")) == ["Egusi"], "final public commodity state remains Egusi only")
    expect(names(client.get("/markets")) == ["Kwali Market"], "final public market state remains Kwali Market only")
    print(results)

finally:
    print("CHECK: fallback cleanup", flush=True)
    with SessionLocal() as db:
        if feedback_id is not None:
            item = db.get(Feedback, feedback_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if price_id is not None:
            item = db.get(PriceUpdate, price_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if commodity_id is not None:
            item = db.get(Commodity, commodity_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if market_id is not None:
            item = db.get(Market, market_id)
            if item is not None:
                db.delete(item)
                db.flush()
        if test_user_id is not None:
            subscription_item = db.scalar(select(Subscription).where(Subscription.user_id == test_user_id))
            if subscription_item is not None:
                db.delete(subscription_item)
                db.flush()
            user_item = db.get(User, test_user_id)
            if user_item is not None:
                db.delete(user_item)
        db.commit()

print("CR-04 OWNER REGRESSION: PASS")
