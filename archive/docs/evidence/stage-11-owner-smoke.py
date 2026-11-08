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
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.storage_suitability import StorageSuitability
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage11-Test-Password!"
admin_email = f"stage11-admin-{run_id}@example.com"
user_email = f"stage11-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_user_id: int | None = None
normal_user_id: int | None = None
price_update_id: int | None = None
storage_item_id: int | None = None

DISCLAIMER = (
    "Storage suitability is based on available market and quality information. "
    "It does not guarantee profit, preservation, or future price increase."
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
        check("Stage 11 storage_suitability migration applied", "storage_suitability" in tables)
        columns = {item["name"] for item in inspector.get_columns("storage_suitability")}
        check(
            "storage_suitability required fields exist",
            {
                "commodity_id",
                "market_id",
                "price_update_id",
                "suitability_status",
                "import_risk",
                "oversupply_risk",
                "spoilage_risk",
                "buyer_availability",
                "quality_storage_notes",
                "summary",
                "created_at",
                "updated_at",
            }.issubset(columns),
        )

        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        kwali = db.scalar(select(Market).where(Market.name == "Kwali Market"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        check("Stage 6 Kwali Market exists", kwali is not None)
        egusi_id = egusi.id
        nasarawa_id = nasarawa.id
        kwali_id = kwali.id

        admin = User(
            full_name="Stage 11 Admin",
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
        json={"full_name": "Stage 11 Trial User", "email": user_email, "password": password},
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
        "source_1": "private-stage11-source-1",
        "source_2": "private-stage11-source-2",
        "update_date_time": "2099-04-01T08:00:00+00:00",
        "possible_meaning": "The current approved range is lower than the previous range.",
        "suggested_action": "Investigate",
        "notes": "Stage 11 storage-suitability linked record.",
    }
    price_create = client.post("/price-updates", json=price_payload, headers=auth(admin_token))
    check("Stage 7 price update create works for storage link", price_create.status_code == 201)
    price_update_id = price_create.json()["id"]
    price_approve = client.patch(f"/price-updates/{price_update_id}/approve", headers=auth(admin_token))
    check("Stage 7 price update approval works for storage link", price_approve.status_code == 200)

    check(
        "unauthenticated storage-suitability viewing blocked",
        client.get("/storage-suitability").status_code == 401,
    )
    check(
        "active trial can view storage suitability",
        client.get("/storage-suitability", headers=auth(user_token)).status_code == 200,
    )

    payload = {
        "commodity_id": egusi_id,
        "market_id": nasarawa_id,
        "price_update_id": price_update_id,
        "suitability_status": "good",
        "import_risk": "low observed import pressure",
        "oversupply_risk": "watch seasonal supply",
        "spoilage_risk": "watch moisture and drying quality",
        "buyer_availability": "buyer activity observed in the market",
        "quality_storage_notes": "Inspect dryness and moisture before storage.",
        "summary": "Storage interest is positive, but quality and moisture should still be checked.",
    }

    check(
        "non-admin storage-suitability creation blocked",
        client.post("/storage-suitability", json=payload, headers=auth(user_token)).status_code == 403,
    )

    invalid_status = dict(payload)
    invalid_status["suitability_status"] = "excellent"
    check(
        "invalid storage suitability status rejected",
        client.post("/storage-suitability", json=invalid_status, headers=auth(admin_token)).status_code == 422,
    )

    mismatched = dict(payload)
    mismatched["market_id"] = kwali_id
    check(
        "mismatched price-update link rejected for storage suitability",
        client.post("/storage-suitability", json=mismatched, headers=auth(admin_token)).status_code == 422,
    )

    guaranteed = dict(payload)
    guaranteed["summary"] = "This guarantees profit and the commodity will not spoil."
    check(
        "guaranteed storage claim rejected",
        client.post("/storage-suitability", json=guaranteed, headers=auth(admin_token)).status_code == 422,
    )

    created = client.post("/storage-suitability", json=payload, headers=auth(admin_token))
    check("admin storage-suitability create works", created.status_code == 201)
    body = created.json()
    storage_item_id = body["id"]
    check("storage suitability links to price update", body["price_update_id"] == price_update_id)
    check("approved suitability status preserved", body["suitability_status"] == "good")
    check("storage summary preserved", body["summary"] == payload["summary"])
    check("storage disclaimer works", body["disclaimer"] == DISCLAIMER)

    fetched = client.get(f"/storage-suitability/{storage_item_id}", headers=auth(user_token))
    check("trial user can view storage suitability record", fetched.status_code == 200)
    check("storage relationship fields preserved", fetched.json()["commodity_id"] == egusi_id and fetched.json()["market_id"] == nasarawa_id)

    edited = client.patch(
        f"/storage-suitability/{storage_item_id}",
        json={
            "suitability_status": "watch",
            "spoilage_risk": "fresh produce needs careful moisture monitoring",
            "summary": "Continue monitoring quality before longer storage.",
        },
        headers=auth(admin_token),
    )
    check("admin storage-suitability edit works", edited.status_code == 200)
    check("storage-suitability edit persisted", edited.json()["suitability_status"] == "watch")

    non_admin_edit = client.patch(
        f"/storage-suitability/{storage_item_id}",
        json={"suitability_status": "risky"},
        headers=auth(user_token),
    )
    check("non-admin storage-suitability edit blocked", non_admin_edit.status_code == 403)

    free_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "free"},
        headers=auth(admin_token),
    )
    check("admin can set test user free", free_status.status_code == 200)
    check(
        "free user storage-suitability full view blocked",
        client.get("/storage-suitability", headers=auth(user_token)).status_code == 403,
    )

    active_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "active"},
        headers=auth(admin_token),
    )
    check("admin can set test user active paid", active_status.status_code == 200)
    check(
        "active paid can view storage suitability",
        client.get("/storage-suitability", headers=auth(user_token)).status_code == 200,
    )

    print(checks)
    print("STAGE 11 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if storage_item_id is not None:
            item = db.get(StorageSuitability, storage_item_id)
            if item is not None:
                db.delete(item)
                db.commit()
        if price_update_id is not None:
            item = db.get(PriceUpdate, price_update_id)
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
