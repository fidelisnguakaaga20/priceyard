from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
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
from app.models.subscription import Subscription
from app.models.user import User
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
admin_email = f"stage7-admin-{suffix}@example.com"
user_email = f"stage7-user-{suffix}@example.com"
password = "Stage7-Secure-Password-123!"
private_source_1 = f"PRIVATE-SOURCE-ONE-{suffix}"
private_source_2 = f"PRIVATE-SOURCE-TWO-{suffix}"
created_price_update_ids: list[int] = []
admin_id: int | None = None
user_id: int | None = None

try:
    with SessionLocal() as db:
        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        expect(egusi is not None, "Stage 6 Egusi commodity exists")
        expect(nasarawa is not None, "Stage 6 Nasarawa market exists")
        commodity_id = egusi.id
        market_id = nasarawa.id

        admin = User(
            full_name="Stage 7 Admin",
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
            "full_name": "Stage 7 User",
            "email": user_email,
            "password": password,
        },
    )
    expect(register.status_code == 201, "normal user registration works")
    user_id = register.json()["id"]

    admin_token = login(admin_email, password)
    user_token = login(user_email, password)

    base_time = datetime.now(timezone.utc).replace(microsecond=0)
    payload = {
        "commodity_id": commodity_id,
        "market_id": market_id,
        "price_low": "140000.00",
        "price_high": "160000.00",
        "average_price": "150000.00",
        "previous_price_low": "240000.00",
        "previous_price_high": "240000.00",
        "unit": "bag",
        "bag_size": "250kg bag / about 180 mudu",
        "commodity_type": "Unpeeled Egusi",
        "market_day": "Monday",
        "time_of_day": "morning",
        "movement": "down",
        "confidence_level": "Low confidence",
        "source_type": "Stage 7 verification source type",
        "source_1": private_source_1,
        "source_2": private_source_2,
        "update_date_time": base_time.isoformat(),
        "is_outdated": False,
        "possible_meaning": "Price entered the observed buying zone but may move quickly.",
        "suggested_action": "Investigate",
        "notes": "Stage 7 verification record; no market signal required.",
    }

    blocked_create = client.post("/price-updates", headers=auth(user_token), json=payload)
    expect(blocked_create.status_code == 403, "non-admin price creation blocked")

    invalid_range = client.post(
        "/price-updates",
        headers=auth(admin_token),
        json={**payload, "price_low": "170000.00", "price_high": "160000.00", "average_price": "165000.00"},
    )
    expect(invalid_range.status_code == 422, "invalid current price range rejected")

    invalid_action = client.post(
        "/price-updates",
        headers=auth(admin_token),
        json={**payload, "suggested_action": "Guaranteed Buy"},
    )
    expect(invalid_action.status_code == 422, "invalid suggested action rejected")

    unsafe_meaning = client.post(
        "/price-updates",
        headers=auth(admin_token),
        json={**payload, "possible_meaning": "This is guaranteed profit."},
    )
    expect(unsafe_meaning.status_code == 422, "guaranteed possible meaning rejected")

    created = client.post("/price-updates", headers=auth(admin_token), json=payload)
    expect(created.status_code == 201, "admin price update create works")
    created_body = created.json()
    first_id = created_body["id"]
    created_price_update_ids.append(first_id)
    expect(created_body["status"] == "pending", "new price update starts pending")
    expect(created_body["created_by"] == admin_id, "created_by is server-controlled admin")
    expect(created_body["approved_by"] is None, "pending update has no approver")
    expect(created_body["source_1"] == private_source_1 and created_body["source_2"] == private_source_2, "admin response preserves private sources")
    expect(created_body["possible_meaning"] == payload["possible_meaning"], "possible meaning preserved on create")
    expect(created_body["suggested_action"] == "Investigate", "suggested action preserved on create")

    public_before_approval = client.get("/price-updates")
    expect(public_before_approval.status_code == 200, "public latest price endpoint works")
    expect(all(item["id"] != first_id for item in public_before_approval.json()), "pending update is not publicly published")

    with SessionLocal() as db:
        linked_signal = db.scalar(select(MarketSignal).where(MarketSignal.price_update_id == first_id))
        expect(linked_signal is None, "price update works without market signal")

    edited = client.patch(
        f"/price-updates/{first_id}",
        headers=auth(admin_token),
        json={
            "price_low": "145000.00",
            "price_high": "165000.00",
            "average_price": "155000.00",
            "possible_meaning": "Observed price moved upward within the reported range; verify before buying.",
            "suggested_action": "Buy Carefully",
        },
    )
    expect(edited.status_code == 200, "admin price update edit works")
    expect(edited.json()["price_low"] in ("145000.00", 145000, 145000.0), "edited price persisted")
    expect(edited.json()["possible_meaning"].startswith("Observed price moved upward"), "possible meaning preserved on edit")
    expect(edited.json()["suggested_action"] == "Buy Carefully", "suggested action preserved on edit")

    approved = client.patch(f"/price-updates/{first_id}/approve", headers=auth(admin_token))
    expect(approved.status_code == 200, "admin price update approval works")
    expect(approved.json()["status"] == "approved", "approved status persisted")
    expect(approved.json()["approved_by"] == admin_id, "approver recorded")

    public_detail = client.get(f"/price-updates/{first_id}")
    expect(public_detail.status_code == 200, "approved price update public retrieval works")
    public_body = public_detail.json()
    expect("source_1" not in public_body and "source_2" not in public_body, "private source identity not exposed publicly")
    expect(public_body["possible_meaning"].startswith("Observed price moved upward"), "public possible meaning preserved")
    expect(public_body["suggested_action"] == "Buy Carefully", "public suggested action preserved")

    latest = client.get("/price-updates")
    expect(latest.status_code == 200, "latest approved retrieval works")
    latest_ids = [item["id"] for item in latest.json()]
    expect(first_id in latest_ids, "approved current update appears in latest data")
    for item in latest.json():
        if item["id"] == first_id:
            expect("source_1" not in item and "source_2" not in item, "latest endpoint hides private source identity")

    reject_payload = {
        **payload,
        "update_date_time": (base_time + timedelta(minutes=1)).isoformat(),
        "price_low": "150000.00",
        "price_high": "170000.00",
        "average_price": "160000.00",
        "possible_meaning": "Second verification record for rejection flow.",
        "suggested_action": "Watch",
    }
    second = client.post("/price-updates", headers=auth(admin_token), json=reject_payload)
    expect(second.status_code == 201, "second admin price update create works")
    second_id = second.json()["id"]
    created_price_update_ids.append(second_id)
    rejected = client.patch(f"/price-updates/{second_id}/reject", headers=auth(admin_token))
    expect(rejected.status_code == 200 and rejected.json()["status"] == "rejected", "admin price update rejection works")
    expect(client.get(f"/price-updates/{second_id}").status_code == 404, "rejected update is not publicly retrievable")

    outdated = client.patch(f"/price-updates/{first_id}/mark-outdated", headers=auth(admin_token))
    expect(outdated.status_code == 200 and outdated.json()["is_outdated"] is True, "admin mark-outdated works")
    latest_after_outdated = client.get("/price-updates")
    expect(all(item["id"] != first_id for item in latest_after_outdated.json()), "outdated latest update is excluded from current data")

    blocked_edit = client.patch(f"/price-updates/{first_id}", headers=auth(user_token), json={"notes": "blocked"})
    expect(blocked_edit.status_code == 403, "non-admin price edit blocked")
    blocked_approve = client.patch(f"/price-updates/{first_id}/approve", headers=auth(user_token))
    expect(blocked_approve.status_code == 403, "non-admin price approval blocked")
    blocked_delete = client.delete(f"/price-updates/{first_id}", headers=auth(user_token))
    expect(blocked_delete.status_code == 403, "non-admin price delete blocked")

    delete_second = client.delete(f"/price-updates/{second_id}", headers=auth(admin_token))
    expect(delete_second.status_code == 204, "admin can delete rejected incorrect update")
    created_price_update_ids.remove(second_id)

    delete_first = client.delete(f"/price-updates/{first_id}", headers=auth(admin_token))
    expect(delete_first.status_code == 204, "admin can delete outdated incorrect update")
    created_price_update_ids.remove(first_id)

    print(results)

finally:
    with SessionLocal() as db:
        # Defensive cleanup if verification stopped early.
        for price_update_id in created_price_update_ids:
            item = db.get(PriceUpdate, price_update_id)
            if item is not None:
                db.delete(item)
        db.flush()

        for email in (user_email, admin_email):
            user = db.scalar(select(User).where(User.email == email))
            if user is not None:
                subscription = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
                if subscription is not None:
                    db.delete(subscription)
                    db.flush()
                db.delete(user)
        db.commit()

print("STAGE 7 OWNER SMOKE: PASS")
