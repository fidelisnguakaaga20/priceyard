from __future__ import annotations

import sys
from decimal import Decimal
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
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage12-Test-Password!"
admin_email = f"stage12-admin-{run_id}@example.com"
user_email = f"stage12-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_user_id: int | None = None
normal_user_id: int | None = None
price_update_id: int | None = None
cost_breakdown_id: int | None = None


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


def money(value: object) -> Decimal:
    return Decimal(str(value))


try:
    with SessionLocal() as db:
        inspector = inspect(db.get_bind())
        tables = set(inspector.get_table_names())
        check("Stage 12 cost_breakdowns migration applied", "cost_breakdowns" in tables)
        columns = {item["name"] for item in inspector.get_columns("cost_breakdowns")}
        check(
            "cost_breakdowns required fields exist",
            {
                "price_update_id",
                "transport",
                "warehouse",
                "security",
                "market_charges",
                "loading_offloading",
                "other_costs",
                "total_additional_cost",
                "purchase_price_reference",
                "total_estimated_landing_storage_cost",
                "created_at",
                "updated_at",
            }.issubset(columns),
        )

        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        egusi_id = egusi.id
        nasarawa_id = nasarawa.id

        admin = User(
            full_name="Stage 12 Admin",
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
        json={"full_name": "Stage 12 Trial User", "email": user_email, "password": password},
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
        "source_1": "private-stage12-source-1",
        "source_2": "private-stage12-source-2",
        "update_date_time": "2099-05-01T08:00:00+00:00",
        "possible_meaning": "The approved range is below the previous range.",
        "suggested_action": "Investigate",
        "notes": "Stage 12 cost-breakdown linked record.",
    }
    price_create = client.post("/price-updates", json=price_payload, headers=auth(admin_token))
    check("Stage 7 price update create works for cost link", price_create.status_code == 201)
    price_update_id = price_create.json()["id"]
    price_approve = client.patch(f"/price-updates/{price_update_id}/approve", headers=auth(admin_token))
    check("Stage 7 price update approval works for cost link", price_approve.status_code == 200)

    check("unauthenticated cost-breakdown viewing blocked", client.get("/cost-breakdowns").status_code == 401)
    check(
        "active trial can view cost breakdowns",
        client.get("/cost-breakdowns", headers=auth(user_token)).status_code == 200,
    )

    payload = {
        "price_update_id": price_update_id,
        "transport": "3000.00",
        "warehouse": "1500.00",
        "security": "500.00",
        "market_charges": "700.00",
        "loading_offloading": "800.00",
        "other_costs": "500.00",
        "purchase_price_reference": "140000.00",
    }

    check(
        "non-admin cost-breakdown creation blocked",
        client.post("/cost-breakdowns", json=payload, headers=auth(user_token)).status_code == 403,
    )

    negative = dict(payload)
    negative["transport"] = "-1.00"
    check(
        "negative costs rejected",
        client.post("/cost-breakdowns", json=negative, headers=auth(admin_token)).status_code == 422,
    )

    missing_link = dict(payload)
    missing_link["price_update_id"] = 2147483647
    check(
        "missing price-update relationship rejected",
        client.post("/cost-breakdowns", json=missing_link, headers=auth(admin_token)).status_code == 404,
    )

    created = client.post("/cost-breakdowns", json=payload, headers=auth(admin_token))
    check("admin cost-breakdown create works", created.status_code == 201)
    body = created.json()
    cost_breakdown_id = body["id"]
    check("cost breakdown links to price update", body["price_update_id"] == price_update_id)
    check("cost components saved", money(body["transport"]) == Decimal("3000.00") and money(body["warehouse"]) == Decimal("1500.00"))
    check("total additional cost calculated correctly", money(body["total_additional_cost"]) == Decimal("7000.00"))
    check(
        "total landing/storage cost calculated correctly",
        money(body["total_estimated_landing_storage_cost"]) == Decimal("147000.00"),
    )

    fetched = client.get(f"/cost-breakdowns/{cost_breakdown_id}", headers=auth(user_token))
    check("trial user can view cost breakdown record", fetched.status_code == 200)
    check("cost breakdown relationship preserved", fetched.json()["price_update_id"] == price_update_id)

    edited = client.patch(
        f"/cost-breakdowns/{cost_breakdown_id}",
        json={"transport": "4000.00", "warehouse": "2000.00", "other_costs": "0.00"},
        headers=auth(admin_token),
    )
    check("admin cost-breakdown edit works", edited.status_code == 200)
    edited_body = edited.json()
    check("edited costs persisted", money(edited_body["transport"]) == Decimal("4000.00"))
    check("edit recalculates additional total", money(edited_body["total_additional_cost"]) == Decimal("8000.00"))
    check(
        "edit recalculates landing/storage total",
        money(edited_body["total_estimated_landing_storage_cost"]) == Decimal("148000.00"),
    )

    negative_edit = client.patch(
        f"/cost-breakdowns/{cost_breakdown_id}",
        json={"security": "-50.00"},
        headers=auth(admin_token),
    )
    check("negative cost edit rejected", negative_edit.status_code == 422)

    non_admin_edit = client.patch(
        f"/cost-breakdowns/{cost_breakdown_id}",
        json={"security": "600.00"},
        headers=auth(user_token),
    )
    check("non-admin cost-breakdown edit blocked", non_admin_edit.status_code == 403)

    with SessionLocal() as db:
        linked = db.get(PriceUpdate, price_update_id)
        check(
            "SQLAlchemy price-update relationship works",
            linked is not None and any(item.id == cost_breakdown_id for item in linked.cost_breakdowns),
        )

    free_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "free"},
        headers=auth(admin_token),
    )
    check("admin can set test user free", free_status.status_code == 200)
    check(
        "free user cost-breakdown full view blocked",
        client.get("/cost-breakdowns", headers=auth(user_token)).status_code == 403,
    )

    active_status = client.patch(
        f"/subscriptions/{normal_user_id}/status",
        json={"status": "active"},
        headers=auth(admin_token),
    )
    check("admin can set test user active paid", active_status.status_code == 200)
    check(
        "active paid can view cost breakdowns",
        client.get("/cost-breakdowns", headers=auth(user_token)).status_code == 200,
    )

    print(checks)
    print("STAGE 12 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if cost_breakdown_id is not None:
            item = db.get(CostBreakdown, cost_breakdown_id)
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
