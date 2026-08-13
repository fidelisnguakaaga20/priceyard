from __future__ import annotations

import json
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
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.faq_item import FAQItem
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage16-Test-Password!"
admin_email = f"stage16-admin-{run_id}@example.com"
user_email = f"stage16-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_id: int | None = None
user_id: int | None = None
feedback_id: int | None = None
price_update_id: int | None = None
faq_id: int | None = None
commodity_id: int | None = None
market_id: int | None = None


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
        check("Stage 3 audit_logs table still exists", "audit_logs" in inspector.get_table_names())
        columns = {item["name"] for item in inspector.get_columns("audit_logs")}
        check(
            "audit_logs approved fields exist",
            {"id", "user_id", "action", "table_name", "record_id", "old_value", "new_value", "created_at"}.issubset(columns),
        )
        admin = User(
            full_name="Stage 16 Admin",
            email=admin_email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_id = admin.id

        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        egusi_id = egusi.id
        nasarawa_id = nasarawa.id

    registration = client.post(
        "/auth/register",
        json={"full_name": "Stage 16 User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)

    check("unauthenticated audit history blocked", client.get("/audit-logs").status_code == 401)
    check("ordinary user audit history blocked", client.get("/audit-logs", headers=auth(user_token)).status_code == 403)

    # Commodity create/edit/delete audit.
    commodity_name = f"Stage16 Commodity {run_id[:8]}"
    response = client.post(
        "/commodities",
        json={"name": commodity_name, "description": "Temporary audit test commodity"},
        headers=auth(admin_token),
    )
    check("admin commodity create works during audit test", response.status_code == 201)
    commodity_id = response.json()["id"]
    response = client.patch(
        f"/commodities/{commodity_id}",
        json={"description": "Edited audit test commodity"},
        headers=auth(admin_token),
    )
    check("admin commodity edit works during audit test", response.status_code == 200)
    response = client.delete(f"/commodities/{commodity_id}", headers=auth(admin_token))
    check("admin commodity delete works during audit test", response.status_code == 204)
    commodity_id = None

    # Market create/edit/delete audit.
    market_name = f"Stage16 Market {run_id[:8]}"
    response = client.post(
        "/markets",
        json={"name": market_name, "state": "FCT", "country": "Nigeria"},
        headers=auth(admin_token),
    )
    check("admin market create works during audit test", response.status_code == 201)
    market_id = response.json()["id"]
    response = client.patch(
        f"/markets/{market_id}",
        json={"description": "Edited audit test market"},
        headers=auth(admin_token),
    )
    check("admin market edit works during audit test", response.status_code == 200)
    response = client.delete(f"/markets/{market_id}", headers=auth(admin_token))
    check("admin market delete works during audit test", response.status_code == 204)
    market_id = None

    # Price create/edit/approve/outdated/delete, including Possible Meaning and Suggested Action changes.
    private_source_1 = f"PRIVATE-SOURCE-ONE-{run_id}"
    private_source_2 = f"PRIVATE-SOURCE-TWO-{run_id}"
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
        "source_type": "owner-test",
        "source_1": private_source_1,
        "source_2": private_source_2,
        "update_date_time": "2099-04-01T08:00:00+00:00",
        "is_outdated": False,
        "possible_meaning": "Supply appears stronger than the previous observation.",
        "suggested_action": "Watch",
        "notes": "Stage 16 audit test",
    }
    response = client.post("/price-updates", json=price_payload, headers=auth(admin_token))
    check("price creation works during audit test", response.status_code == 201)
    price_update_id = response.json()["id"]

    edited_meaning = "Buyer activity appears stronger than the earlier observation."
    response = client.patch(
        f"/price-updates/{price_update_id}",
        json={"possible_meaning": edited_meaning, "suggested_action": "Investigate"},
        headers=auth(admin_token),
    )
    check("price edit works during audit test", response.status_code == 200)
    response = client.patch(f"/price-updates/{price_update_id}/approve", headers=auth(admin_token))
    check("price approval works during audit test", response.status_code == 200)
    response = client.patch(f"/price-updates/{price_update_id}/mark-outdated", headers=auth(admin_token))
    check("price mark-outdated works during audit test", response.status_code == 200)
    response = client.delete(f"/price-updates/{price_update_id}", headers=auth(admin_token))
    check("price delete works during audit test", response.status_code == 204)
    price_update_id = None

    # FAQ change audit.
    response = client.post(
        "/faq",
        json={
            "question": f"How fresh is a Stage 16 test price {run_id[:8]}?",
            "answer": "Check the update timestamp and confidence label before using the information.",
            "category": "prices",
        },
        headers=auth(admin_token),
    )
    check("FAQ create works during audit test", response.status_code == 201)
    faq_id = response.json()["id"]
    response = client.patch(
        f"/faq/{faq_id}",
        json={"answer": "Check the timestamp, confidence label, and market context before using the information."},
        headers=auth(admin_token),
    )
    check("FAQ edit works during audit test", response.status_code == 200)
    check("FAQ publish works during audit test", client.patch(f"/faq/{faq_id}/publish", headers=auth(admin_token)).status_code == 200)
    check("FAQ hide works during audit test", client.patch(f"/faq/{faq_id}/hide", headers=auth(admin_token)).status_code == 200)
    check("FAQ delete works during audit test", client.delete(f"/faq/{faq_id}", headers=auth(admin_token)).status_code == 204)
    faq_id = None

    # User status and subscription changes.
    response = client.patch(f"/users/{user_id}", json={"is_active": False}, headers=auth(admin_token))
    check("admin user status change works", response.status_code == 200 and response.json()["is_active"] is False)
    response = client.patch(f"/users/{user_id}", json={"is_active": True}, headers=auth(admin_token))
    check("admin user reactivation works", response.status_code == 200 and response.json()["is_active"] is True)
    response = client.patch(f"/subscriptions/{user_id}/status", json={"status": "active"}, headers=auth(admin_token))
    check("admin subscription change works", response.status_code == 200 and response.json()["status"] == "active")
    response = client.patch(f"/subscriptions/{user_id}/status", json={"status": "free"}, headers=auth(admin_token))
    check("admin subscription reset works", response.status_code == 200 and response.json()["status"] == "free")

    # Feedback admin action audit.
    response = client.post(
        "/feedback",
        json={"rating": 4, "comment": "Stage 16 audit feedback", "complaint_or_suggestion": "Keep audit history admin-only."},
        headers=auth(user_token),
    )
    check("user feedback create works for audit delete test", response.status_code == 201)
    feedback_id = response.json()["id"]
    response = client.delete(f"/feedback/{feedback_id}", headers=auth(admin_token))
    check("admin feedback delete works during audit test", response.status_code == 204)
    feedback_id = None

    logs_response = client.get("/audit-logs", headers=auth(admin_token))
    check("admin can view audit history", logs_response.status_code == 200)
    own_logs = [item for item in logs_response.json() if item["user_id"] == admin_id]
    actions = {item["action"] for item in own_logs}
    required_actions = {
        "price_update.create",
        "price_update.edit",
        "price_update.approve",
        "price_update.mark_outdated",
        "price_update.delete",
        "commodity.create",
        "commodity.edit",
        "commodity.delete",
        "market.create",
        "market.edit",
        "market.delete",
        "faq.create",
        "faq.edit",
        "faq.publish",
        "faq.hide",
        "faq.delete",
        "subscription.status_update",
        "user.update",
        "feedback.delete",
    }
    check("required Stage 16 admin actions are logged", required_actions.issubset(actions))

    price_edit_logs = [item for item in own_logs if item["action"] == "price_update.edit"]
    check("price edit audit log exists", bool(price_edit_logs))
    edit_log = price_edit_logs[0]
    check(
        "possible meaning change is audited",
        edit_log["old_value"]["possible_meaning"] == price_payload["possible_meaning"]
        and edit_log["new_value"]["possible_meaning"] == edited_meaning,
    )
    check(
        "suggested action change is audited",
        edit_log["old_value"]["suggested_action"] == "Watch"
        and edit_log["new_value"]["suggested_action"] == "Investigate",
    )

    serialized_logs = json.dumps(own_logs, sort_keys=True)
    check("plaintext password absent from audit logs", password not in serialized_logs)
    check("password hash field absent from audit logs", "password_hash" not in serialized_logs)
    check("JWT/token secrets absent from audit logs", "jwt_secret" not in serialized_logs.lower() and "authorization" not in serialized_logs.lower())
    check("database secrets absent from audit logs", "database_url" not in serialized_logs.lower() and "database_password" not in serialized_logs.lower())
    check(".env absent from audit logs", ".env" not in serialized_logs.lower())
    check("private source 1 absent from audit logs", private_source_1 not in serialized_logs)
    check("private source 2 absent from audit logs", private_source_2 not in serialized_logs)

    one_log = own_logs[0]
    detail_response = client.get(f"/audit-logs/{one_log['id']}", headers=auth(admin_token))
    check("admin can view one audit record", detail_response.status_code == 200 and detail_response.json()["id"] == one_log["id"])
    check("ordinary user cannot view one audit record", client.get(f"/audit-logs/{one_log['id']}", headers=auth(user_token)).status_code == 403)

    print(checks)
    print("STAGE 16 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if feedback_id is not None:
            item = db.get(Feedback, feedback_id)
            if item is not None:
                db.delete(item)
        if price_update_id is not None:
            item = db.get(PriceUpdate, price_update_id)
            if item is not None:
                db.delete(item)
        if faq_id is not None:
            item = db.get(FAQItem, faq_id)
            if item is not None:
                db.delete(item)
        if commodity_id is not None:
            item = db.get(Commodity, commodity_id)
            if item is not None:
                db.delete(item)
        if market_id is not None:
            item = db.get(Market, market_id)
            if item is not None:
                db.delete(item)
        db.commit()

        if admin_id is not None:
            for item in list(db.scalars(select(AuditLog).where(AuditLog.user_id == admin_id)).all()):
                db.delete(item)
            db.commit()

        if user_id is not None:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            if subscription is not None:
                db.delete(subscription)
            user = db.get(User, user_id)
            if user is not None:
                db.delete(user)
            db.commit()

        if admin_id is not None:
            admin = db.get(User, admin_id)
            if admin is not None:
                db.delete(admin)
            db.commit()
