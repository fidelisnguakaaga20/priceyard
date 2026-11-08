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
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage9-Test-Password!"
admin_email = f"stage9-admin-{run_id}@example.com"
user_email = f"stage9-user-{run_id}@example.com"
checks: dict[str, str] = {}
created_market_signal_id: int | None = None
created_quality_signal_id: int | None = None
created_price_update_id: int | None = None
normal_user_id: int | None = None
admin_user_id: int | None = None


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
        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        kwali = db.scalar(select(Market).where(Market.name == "Kwali Market"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        check("Stage 6 Kwali Market exists", kwali is not None)

        admin = User(
            full_name="Stage 9 Admin",
            email=admin_email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_user_id = admin.id
        egusi_id = egusi.id
        nasarawa_id = nasarawa.id
        kwali_id = kwali.id

    registration = client.post(
        "/auth/register",
        json={"full_name": "Stage 9 User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    normal_user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)

    price_payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "price_low": "135000.00",
        "price_high": "145000.00",
        "average_price": "140000.00",
        "previous_price_low": "150000.00",
        "previous_price_high": "160000.00",
        "unit": "bag",
        "bag_size": "250kg",
        "commodity_type": "unpeeled",
        "market_day": "Monday",
        "time_of_day": "morning",
        "movement": "down",
        "confidence_level": "Admin confirmed",
        "source_type": "market note",
        "source_1": "private-stage9-source-1",
        "source_2": "private-stage9-source-2",
        "update_date_time": "2099-02-01T08:00:00+00:00",
        "possible_meaning": "The current range is lower than the previous approved range.",
        "suggested_action": "Investigate",
        "notes": "Stage 9 linked-price test record.",
    }
    price_create = client.post("/price-updates", json=price_payload, headers=auth(admin_token))
    check("Stage 7 price update create works for signal link", price_create.status_code == 201)
    created_price_update_id = price_create.json()["id"]
    price_approve = client.patch(
        f"/price-updates/{created_price_update_id}/approve", headers=auth(admin_token)
    )
    check("Stage 7 price update approval works for signal link", price_approve.status_code == 200)

    no_auth_market_view = client.get("/market-signals")
    check("unauthenticated market-signal viewing blocked", no_auth_market_view.status_code == 401)
    no_auth_quality_view = client.get("/quality-signals")
    check("unauthenticated quality-signal viewing blocked", no_auth_quality_view.status_code == 401)

    market_payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "price_update_id": created_price_update_id,
        "signal_type": "fresh_harvest",
        "signal_description": "Fresh harvest is entering the market.",
        "possible_meaning": "Supply may increase during the market day.",
        "suggested_action": "Watch",
    }
    non_admin_market_create = client.post("/market-signals", json=market_payload, headers=auth(user_token))
    check("non-admin market-signal creation blocked", non_admin_market_create.status_code == 403)

    guaranteed_market = dict(market_payload)
    guaranteed_market["possible_meaning"] = "This is guaranteed profit and price will surely rise."
    invalid_market = client.post("/market-signals", json=guaranteed_market, headers=auth(admin_token))
    check("guaranteed market-signal wording rejected", invalid_market.status_code == 422)

    mismatched_market = dict(market_payload)
    mismatched_market["market_id"] = kwali_id
    mismatch_response = client.post("/market-signals", json=mismatched_market, headers=auth(admin_token))
    check("mismatched price-update link rejected for market signal", mismatch_response.status_code == 422)

    market_create = client.post("/market-signals", json=market_payload, headers=auth(admin_token))
    check("admin market-signal create works", market_create.status_code == 201)
    market_body = market_create.json()
    created_market_signal_id = market_body["id"]
    check("market signal links to price update", market_body["price_update_id"] == created_price_update_id)
    check("market signal creator is server-controlled admin", market_body["created_by"] == admin_user_id)
    check("market signal possible meaning preserved", market_body["possible_meaning"] == market_payload["possible_meaning"])
    check("market signal suggested action preserved", market_body["suggested_action"] == "Watch")
    check(
        "required market-signal disclaimer returned",
        market_body["disclaimer"]
        == "Market signals are observations based on available market information. They are not guaranteed predictions or financial advice. Users should verify before making major buying, selling, or storage decisions.",
    )

    market_get = client.get(f"/market-signals/{created_market_signal_id}", headers=auth(user_token))
    check("authenticated user can view market signal", market_get.status_code == 200)
    market_list = client.get("/market-signals", headers=auth(user_token))
    check("authenticated user can list market signals", market_list.status_code == 200)
    check(
        "created market signal appears in list",
        any(item["id"] == created_market_signal_id for item in market_list.json()),
    )

    market_edit = client.patch(
        f"/market-signals/{created_market_signal_id}",
        json={
            "signal_description": "Fresh harvest is entering while buyer activity is being observed.",
            "possible_meaning": "Negotiation pressure may change during the day.",
            "suggested_action": "Investigate",
        },
        headers=auth(admin_token),
    )
    check("admin market-signal edit works", market_edit.status_code == 200)
    check("market-signal edit persisted", market_edit.json()["suggested_action"] == "Investigate")

    quality_payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "price_update_id": created_price_update_id,
        "quality_status": "fresh_harvest",
        "moisture_status": "needs_inspection",
        "storage_readiness": "watch",
        "risk_note": "Fresh produce should be inspected for dryness before storage.",
    }
    non_admin_quality_create = client.post("/quality-signals", json=quality_payload, headers=auth(user_token))
    check("non-admin quality-signal creation blocked", non_admin_quality_create.status_code == 403)

    lab_claim = dict(quality_payload)
    lab_claim["risk_note"] = "Laboratory confirmed moisture at 5 percent."
    invalid_quality = client.post("/quality-signals", json=lab_claim, headers=auth(admin_token))
    check("unsupported laboratory claim rejected", invalid_quality.status_code == 422)

    mismatched_quality = dict(quality_payload)
    mismatched_quality["market_id"] = kwali_id
    quality_mismatch = client.post("/quality-signals", json=mismatched_quality, headers=auth(admin_token))
    check("mismatched price-update link rejected for quality signal", quality_mismatch.status_code == 422)

    quality_create = client.post("/quality-signals", json=quality_payload, headers=auth(admin_token))
    check("admin quality-signal create works", quality_create.status_code == 201)
    quality_body = quality_create.json()
    created_quality_signal_id = quality_body["id"]
    check("quality signal links to price update", quality_body["price_update_id"] == created_price_update_id)
    check("quality signal creator is server-controlled admin", quality_body["created_by"] == admin_user_id)
    check("quality risk note preserved", quality_body["risk_note"] == quality_payload["risk_note"])

    quality_get = client.get(f"/quality-signals/{created_quality_signal_id}", headers=auth(user_token))
    check("authenticated user can view quality signal", quality_get.status_code == 200)
    quality_list = client.get("/quality-signals", headers=auth(user_token))
    check("authenticated user can list quality signals", quality_list.status_code == 200)
    check(
        "created quality signal appears in list",
        any(item["id"] == created_quality_signal_id for item in quality_list.json()),
    )

    quality_edit = client.patch(
        f"/quality-signals/{created_quality_signal_id}",
        json={"risk_note": "Dryness should be checked again before storage."},
        headers=auth(admin_token),
    )
    check("admin quality-signal edit works", quality_edit.status_code == 200)
    check("quality-signal edit persisted", quality_edit.json()["risk_note"] == "Dryness should be checked again before storage.")

    price_after_signals = client.get(f"/price-updates/{created_price_update_id}")
    check("linked price update remains publicly retrievable", price_after_signals.status_code == 200)
    check(
        "price-update possible meaning remains separate from market-signal meaning",
        price_after_signals.json()["possible_meaning"] == price_payload["possible_meaning"],
    )
    check(
        "price-update suggested action remains separate from market-signal action",
        price_after_signals.json()["suggested_action"] == price_payload["suggested_action"],
    )

    non_admin_market_edit = client.patch(
        f"/market-signals/{created_market_signal_id}",
        json={"signal_type": "scarcity"},
        headers=auth(user_token),
    )
    check("non-admin market-signal edit blocked", non_admin_market_edit.status_code == 403)
    non_admin_quality_edit = client.patch(
        f"/quality-signals/{created_quality_signal_id}",
        json={"quality_status": "watch"},
        headers=auth(user_token),
    )
    check("non-admin quality-signal edit blocked", non_admin_quality_edit.status_code == 403)

    delete_market = client.delete(f"/market-signals/{created_market_signal_id}", headers=auth(admin_token))
    check("admin market-signal delete works", delete_market.status_code == 204)
    created_market_signal_id = None
    delete_quality = client.delete(f"/quality-signals/{created_quality_signal_id}", headers=auth(admin_token))
    check("admin quality-signal delete works", delete_quality.status_code == 204)
    created_quality_signal_id = None

    print(checks)
    print("STAGE 9 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if created_market_signal_id is not None:
            item = db.get(MarketSignal, created_market_signal_id)
            if item is not None:
                db.delete(item)
        if created_quality_signal_id is not None:
            item = db.get(QualitySignal, created_quality_signal_id)
            if item is not None:
                db.delete(item)
        if created_price_update_id is not None:
            item = db.get(PriceUpdate, created_price_update_id)
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
