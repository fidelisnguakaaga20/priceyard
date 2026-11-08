from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import get_session_factory
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
results: dict[str, str] = {}


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    results[label] = "PASS"


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    expect(response.status_code == 200, f"login works for {email}")
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


suffix = uuid4().hex
admin_email = f"stage6-admin-{suffix}@example.com"
user_email = f"stage6-user-{suffix}@example.com"
password = "Stage6-Secure-Password-123!"
temp_commodity_name = f"Stage6 Temp Commodity {suffix[:8]}"
temp_market_name = f"Stage6 Temp Market {suffix[:8]}"
admin_id: int | None = None
user_id: int | None = None

CORE_COMMODITIES = ["Egusi", "Beans", "Palm oil"]
CORE_MARKETS = {
    "Abuja/FCT": {"state": "FCT", "market_day": None},
    "Kwali Market": {"state": "FCT", "market_day": "Tuesday"},
    "Nasarawa": {"state": "Nasarawa", "market_day": "Monday"},
    "Benue": {"state": "Benue", "market_day": None},
}

try:
    with SessionLocal() as db:
        admin = User(
            full_name="Stage 6 Admin",
            email=admin_email,
            phone=None,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        admin.subscription = Subscription(plan_name="free", status="free")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_id = admin.id

    register = client.post(
        "/auth/register",
        json={
            "full_name": "Stage 6 User",
            "email": user_email,
            "password": password,
        },
    )
    expect(register.status_code == 201, "normal user registration works")
    user_id = register.json()["id"]

    admin_token = login(admin_email, password)
    user_token = login(user_email, password)

    # Admin authorization proof.
    blocked_users = client.get("/users", headers=auth(user_token))
    expect(blocked_users.status_code == 403, "non-admin user list blocked")

    blocked_commodity = client.post(
        "/commodities",
        headers=auth(user_token),
        json={"name": temp_commodity_name},
    )
    expect(blocked_commodity.status_code == 403, "non-admin commodity create blocked")

    blocked_market = client.post(
        "/markets",
        headers=auth(user_token),
        json={"name": temp_market_name, "country": "Nigeria"},
    )
    expect(blocked_market.status_code == 403, "non-admin market create blocked")

    blocked_subscription = client.patch(
        f"/subscriptions/{user_id}/status",
        headers=auth(user_token),
        json={"status": "active"},
    )
    expect(blocked_subscription.status_code == 403, "non-admin subscription management blocked")

    # Ensure only approved initial commodity reference records are present/active as core data.
    commodity_list = client.get("/commodities")
    expect(commodity_list.status_code == 200, "commodity list is viewable")
    commodity_by_name = {item["name"]: item for item in commodity_list.json()}
    for name in CORE_COMMODITIES:
        item = commodity_by_name.get(name)
        if item is None:
            created = client.post(
                "/commodities",
                headers=auth(admin_token),
                json={"name": name, "is_active": True},
            )
            expect(created.status_code == 201, f"admin can create core commodity {name}")
        elif not item["is_active"]:
            updated = client.patch(
                f"/commodities/{item['id']}",
                headers=auth(admin_token),
                json={"is_active": True},
            )
            expect(updated.status_code == 200, f"admin can reactivate core commodity {name}")

    commodity_list = client.get("/commodities")
    commodity_names = {item["name"] for item in commodity_list.json()}
    expect(set(CORE_COMMODITIES).issubset(commodity_names), "approved initial commodities exist")

    # Full commodity CRUD using a temporary record.
    commodity_create = client.post(
        "/commodities",
        headers=auth(admin_token),
        json={"name": temp_commodity_name, "description": "Stage 6 CRUD proof"},
    )
    expect(commodity_create.status_code == 201, "admin commodity create works")
    temp_commodity_id = commodity_create.json()["id"]

    commodity_get = client.get(f"/commodities/{temp_commodity_id}")
    expect(commodity_get.status_code == 200, "commodity get works")

    commodity_patch = client.patch(
        f"/commodities/{temp_commodity_id}",
        headers=auth(admin_token),
        json={"description": "Stage 6 CRUD proof updated", "is_active": False},
    )
    expect(commodity_patch.status_code == 200, "admin commodity edit works")
    expect(commodity_patch.json()["is_active"] is False, "commodity edit persisted")

    commodity_delete = client.delete(f"/commodities/{temp_commodity_id}", headers=auth(admin_token))
    expect(commodity_delete.status_code == 204, "admin commodity delete works")
    expect(client.get(f"/commodities/{temp_commodity_id}").status_code == 404, "deleted commodity no longer exists")

    # Ensure approved initial markets and only verified market days are seeded.
    market_list = client.get("/markets")
    expect(market_list.status_code == 200, "market list is viewable")
    market_by_name = {item["name"]: item for item in market_list.json()}
    for name, expected in CORE_MARKETS.items():
        item = market_by_name.get(name)
        payload = {
            "name": name,
            "state": expected["state"],
            "country": "Nigeria",
            "market_day": expected["market_day"],
            "is_active": True,
        }
        if item is None:
            created = client.post("/markets", headers=auth(admin_token), json=payload)
            expect(created.status_code == 201, f"admin can create core market {name}")
        else:
            update_payload = {
                "state": expected["state"],
                "country": "Nigeria",
                "market_day": expected["market_day"],
                "is_active": True,
            }
            updated = client.patch(f"/markets/{item['id']}", headers=auth(admin_token), json=update_payload)
            expect(updated.status_code == 200, f"admin can align core market {name}")

    market_list = client.get("/markets")
    market_by_name = {item["name"]: item for item in market_list.json()}
    expect(set(CORE_MARKETS).issubset(market_by_name), "approved initial markets exist")
    expect(market_by_name["Nasarawa"]["market_day"] == "Monday", "Nasarawa market day is Monday")
    expect(market_by_name["Kwali Market"]["market_day"] == "Tuesday", "Kwali market day is Tuesday")
    expect(market_by_name["Abuja/FCT"]["market_day"] is None, "unverified Abuja/FCT market day not invented")
    expect(market_by_name["Benue"]["market_day"] is None, "unverified Benue market day not invented")

    # Full market CRUD using a temporary record.
    market_create = client.post(
        "/markets",
        headers=auth(admin_token),
        json={
            "name": temp_market_name,
            "state": "FCT",
            "country": "Nigeria",
            "description": "Stage 6 CRUD proof",
        },
    )
    expect(market_create.status_code == 201, "admin market create works")
    temp_market_id = market_create.json()["id"]

    market_get = client.get(f"/markets/{temp_market_id}")
    expect(market_get.status_code == 200, "market get works")

    market_patch = client.patch(
        f"/markets/{temp_market_id}",
        headers=auth(admin_token),
        json={"description": "Stage 6 CRUD proof updated", "is_active": False},
    )
    expect(market_patch.status_code == 200, "admin market edit works")
    expect(market_patch.json()["is_active"] is False, "market edit persisted")

    market_delete = client.delete(f"/markets/{temp_market_id}", headers=auth(admin_token))
    expect(market_delete.status_code == 204, "admin market delete works")
    expect(client.get(f"/markets/{temp_market_id}").status_code == 404, "deleted market no longer exists")

    # User management proof.
    users = client.get("/users", headers=auth(admin_token))
    expect(users.status_code == 200, "admin can list users")
    expect(any(item["id"] == user_id for item in users.json()), "admin user list contains target user")

    user_detail = client.get(f"/users/{user_id}", headers=auth(admin_token))
    expect(user_detail.status_code == 200, "admin can view user")
    expect("password_hash" not in user_detail.json(), "user management never exposes password hash")

    deactivate = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"is_active": False})
    expect(deactivate.status_code == 200 and deactivate.json()["is_active"] is False, "admin can deactivate user")
    blocked_login = client.post("/auth/login", json={"email": user_email, "password": password})
    expect(blocked_login.status_code == 403, "deactivated user is blocked")

    reactivate = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"is_active": True})
    expect(reactivate.status_code == 200 and reactivate.json()["is_active"] is True, "admin can reactivate user")

    make_paid = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"role": "paid_user"})
    expect(make_paid.status_code == 200 and make_paid.json()["role"] == "paid_user", "admin can set paid_user role")
    paid_subscription = client.get(f"/subscriptions/{user_id}", headers=auth(admin_token))
    expect(paid_subscription.status_code == 200 and paid_subscription.json()["status"] == "active", "paid_user role keeps subscription active")

    make_admin = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"role": "admin"})
    expect(make_admin.status_code == 200 and make_admin.json()["role"] == "admin", "admin can change user role to admin")

    deferred_reporter = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"role": "reporter"})
    expect(deferred_reporter.status_code == 422, "deferred reporter role is rejected")

    make_free = client.patch(f"/users/{user_id}", headers=auth(admin_token), json={"role": "free_user"})
    expect(make_free.status_code == 200 and make_free.json()["role"] == "free_user", "admin can set free_user role")
    free_subscription = client.get(f"/subscriptions/{user_id}", headers=auth(admin_token))
    expect(free_subscription.status_code == 200 and free_subscription.json()["status"] == "free", "free_user role keeps subscription limited")

    # Stage 6 subscription management regression proof.
    subscription_trial = client.patch(
        f"/subscriptions/{user_id}/status",
        headers=auth(admin_token),
        json={"status": "trial"},
    )
    expect(subscription_trial.status_code == 200 and subscription_trial.json()["status"] == "trial", "admin subscription management works")
    expect(subscription_trial.json()["trial_started_at"] is not None and subscription_trial.json()["trial_ends_at"] is not None, "admin trial reset records dates")

    print(results)

finally:
    # Remove only temporary users created by this verification. Approved core commodity/market records remain.
    with SessionLocal() as db:
        for email in (user_email, admin_email):
            user = db.scalar(select(User).where(User.email == email))
            if user is not None:
                subscription = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
                if subscription is not None:
                    db.delete(subscription)
                    db.flush()
                db.delete(user)
        # Defensive cleanup only if a temporary CRUD record survived a failed test run.
        for commodity in db.scalars(select(Commodity).where(Commodity.name == temp_commodity_name)).all():
            db.delete(commodity)
        for market in db.scalars(select(Market).where(Market.name == temp_market_name)).all():
            db.delete(market)
        db.commit()

print("STAGE 6 OWNER SMOKE: PASS")
