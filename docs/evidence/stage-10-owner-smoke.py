from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select

from app.database import get_session_factory
from app.main import app
from app.models.buying_zone import BuyingZone
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.sell_watch_window import SellWatchWindow
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage10-Test-Password!"
admin_email = f"stage10-admin-{run_id}@example.com"
user_email = f"stage10-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_user_id: int | None = None
normal_user_id: int | None = None
buying_zone_id: int | None = None
sell_watch_window_id: int | None = None

BUYING_DISCLAIMER = (
    "Buying zones are market observations and are not guaranteed lowest prices, "
    "guaranteed buying opportunities, predictions, or financial advice."
)
SELL_WATCH_DISCLAIMER = (
    "Sell-watch windows are market observations and are not guaranteed profit periods, "
    "guaranteed selling opportunities, predictions, or financial advice."
)


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


def login(email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    check(f"login works for {email}", response.status_code == 200)
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


try:
    with SessionLocal() as db:
        inspector = inspect(db.get_bind())
        tables = set(inspector.get_table_names())
        check("Stage 10 buying_zones migration applied", "buying_zones" in tables)
        check("Stage 10 sell_watch_windows migration applied", "sell_watch_windows" in tables)
        buying_columns = {item["name"] for item in inspector.get_columns("buying_zones")}
        sell_columns = {item["name"] for item in inspector.get_columns("sell_watch_windows")}
        check(
            "buying_zones required fields exist",
            {
                "commodity_id",
                "market_id",
                "price_low",
                "price_high",
                "reason",
                "valid_from",
                "valid_to",
                "confidence",
                "created_by",
                "created_at",
                "updated_at",
            }.issubset(buying_columns),
        )
        check(
            "sell_watch_windows required fields exist",
            {
                "commodity_id",
                "market_id",
                "start_period",
                "end_period",
                "observation",
                "confidence",
                "created_by",
                "created_at",
                "updated_at",
            }.issubset(sell_columns),
        )

        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        egusi_id = egusi.id
        nasarawa_id = nasarawa.id

        admin = User(
            full_name="Stage 10 Admin",
            email=admin_email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_user_id = admin.id

    registration = client.post(
        "/auth/register",
        json={"full_name": "Stage 10 Trial User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    normal_user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)

    check("unauthenticated buying-zone viewing blocked", client.get("/buying-zones").status_code == 401)
    check("unauthenticated sell-watch viewing blocked", client.get("/sell-watch-windows").status_code == 401)
    check("active trial can view buying zones", client.get("/buying-zones", headers=auth(user_token)).status_code == 200)
    check("active trial can view sell-watch windows", client.get("/sell-watch-windows", headers=auth(user_token)).status_code == 200)

    buying_payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "price_low": "130000.00",
        "price_high": "145000.00",
        "reason": "Observed price range is within the current buying-zone watch level.",
        "valid_from": "2099-03-01",
        "valid_to": "2099-03-31",
        "confidence": "Admin confirmed",
    }
    check(
        "non-admin buying-zone creation blocked",
        client.post("/buying-zones", json=buying_payload, headers=auth(user_token)).status_code == 403,
    )

    invalid_range = dict(buying_payload)
    invalid_range["price_low"] = "150000.00"
    invalid_range["price_high"] = "140000.00"
    check(
        "invalid buying-zone range rejected",
        client.post("/buying-zones", json=invalid_range, headers=auth(admin_token)).status_code == 422,
    )

    invalid_period = dict(buying_payload)
    invalid_period["valid_from"] = "2099-04-01"
    invalid_period["valid_to"] = "2099-03-01"
    check(
        "invalid buying-zone validity period rejected",
        client.post("/buying-zones", json=invalid_period, headers=auth(admin_token)).status_code == 422,
    )

    guaranteed_buy = dict(buying_payload)
    guaranteed_buy["reason"] = "This is a guaranteed lowest price and you must buy."
    check(
        "guaranteed buying-zone wording rejected",
        client.post("/buying-zones", json=guaranteed_buy, headers=auth(admin_token)).status_code == 422,
    )

    buying_create = client.post("/buying-zones", json=buying_payload, headers=auth(admin_token))
    check("admin buying-zone create works", buying_create.status_code == 201)
    buying_body = buying_create.json()
    buying_zone_id = buying_body["id"]
    check("buying-zone creator is server-controlled admin", buying_body["created_by"] == admin_user_id)
    check("buying-zone range preserved", buying_body["price_low"] == "130000.00" and buying_body["price_high"] == "145000.00")
    check("buying-zone disclaimer works", buying_body["disclaimer"] == BUYING_DISCLAIMER)

    buying_get = client.get(f"/buying-zones/{buying_zone_id}", headers=auth(user_token))
    check("trial user can view buying zone", buying_get.status_code == 200)
    check("buying-zone view preserves reason", buying_get.json()["reason"] == buying_payload["reason"])

    buying_edit = client.patch(
        f"/buying-zones/{buying_zone_id}",
        json={"price_high": "146000.00", "reason": "Observed range widened slightly during monitoring."},
        headers=auth(admin_token),
    )
    check("admin buying-zone edit works", buying_edit.status_code == 200)
    check("buying-zone edit persisted", buying_edit.json()["price_high"] == "146000.00")

    sell_payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "start_period": "December ending",
        "end_period": "January upward",
        "observation": "Monitor approved price movement during this period before making a selling decision.",
        "confidence": "Admin confirmed",
    }
    check(
        "non-admin sell-watch creation blocked",
        client.post("/sell-watch-windows", json=sell_payload, headers=auth(user_token)).status_code == 403,
    )

    guaranteed_sell = dict(sell_payload)
    guaranteed_sell["observation"] = "This is a guaranteed profit period and you must sell."
    check(
        "guaranteed sell-watch wording rejected",
        client.post("/sell-watch-windows", json=guaranteed_sell, headers=auth(admin_token)).status_code == 422,
    )

    sell_create = client.post("/sell-watch-windows", json=sell_payload, headers=auth(admin_token))
    check("admin sell-watch create works", sell_create.status_code == 201)
    sell_body = sell_create.json()
    sell_watch_window_id = sell_body["id"]
    check("sell-watch creator is server-controlled admin", sell_body["created_by"] == admin_user_id)
    check("sell-watch periods preserved", sell_body["start_period"] == "December ending" and sell_body["end_period"] == "January upward")
    check("sell-watch disclaimer works", sell_body["disclaimer"] == SELL_WATCH_DISCLAIMER)

    sell_get = client.get(f"/sell-watch-windows/{sell_watch_window_id}", headers=auth(user_token))
    check("trial user can view sell-watch window", sell_get.status_code == 200)
    check("sell-watch observation preserved", sell_get.json()["observation"] == sell_payload["observation"])

    sell_edit = client.patch(
        f"/sell-watch-windows/{sell_watch_window_id}",
        json={"observation": "Continue monitoring verified price movement and market conditions."},
        headers=auth(admin_token),
    )
    check("admin sell-watch edit works", sell_edit.status_code == 200)
    check("sell-watch edit persisted", "Continue monitoring" in sell_edit.json()["observation"])

    free_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "free"},
        headers=auth(admin_token),
    )
    check("admin can set test user free", free_status.status_code == 200)
    check("free user buying-zone full view blocked", client.get("/buying-zones", headers=auth(user_token)).status_code == 403)
    check("free user sell-watch full view blocked", client.get("/sell-watch-windows", headers=auth(user_token)).status_code == 403)

    active_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "active"},
        headers=auth(admin_token),
    )
    check("admin can set test user active paid", active_status.status_code == 200)
    check("active paid can view buying zones", client.get("/buying-zones", headers=auth(user_token)).status_code == 200)
    check("active paid can view sell-watch windows", client.get("/sell-watch-windows", headers=auth(user_token)).status_code == 200)

    non_admin_edit = client.patch(
        f"/buying-zones/{buying_zone_id}",
        json={"confidence": "Verified by 2 sources"},
        headers=auth(user_token),
    )
    check("non-admin buying-zone edit blocked", non_admin_edit.status_code == 403)
    non_admin_sell_edit = client.patch(
        f"/sell-watch-windows/{sell_watch_window_id}",
        json={"confidence": "Verified by 2 sources"},
        headers=auth(user_token),
    )
    check("non-admin sell-watch edit blocked", non_admin_sell_edit.status_code == 403)

    print(checks)
    print("STAGE 10 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if buying_zone_id is not None:
            item = db.get(BuyingZone, buying_zone_id)
            if item is not None:
                db.delete(item)
        if sell_watch_window_id is not None:
            item = db.get(SellWatchWindow, sell_watch_window_id)
            if item is not None:
                db.delete(item)
        db.commit()

        if normal_user_id is not None:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == normal_user_id))
            if subscription is not None:
                db.delete(subscription)
                db.commit()
            user = db.get(User, normal_user_id)
            if user is not None:
                db.delete(user)
                db.commit()

        if admin_user_id is not None:
            user = db.get(User, admin_user_id)
            if user is not None:
                db.delete(user)
                db.commit()
