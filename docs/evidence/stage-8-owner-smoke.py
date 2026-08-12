from __future__ import annotations

import sys
from datetime import datetime, timezone
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
admin_email = f"stage8-admin-{suffix}@example.com"
password = "Stage8-Secure-Password-123!"
private_source = f"PRIVATE-STAGE8-{suffix}"
created_price_update_ids: list[int] = []
admin_id: int | None = None

try:
    with SessionLocal() as db:
        egusi = db.scalar(select(Commodity).where(Commodity.name == "Egusi"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        kwali = db.scalar(select(Market).where(Market.name == "Kwali Market"))
        expect(egusi is not None, "Stage 6 Egusi commodity exists")
        expect(nasarawa is not None, "Stage 6 Nasarawa market exists")
        expect(kwali is not None, "Stage 6 Kwali Market exists")
        commodity_id = egusi.id
        nasarawa_id = nasarawa.id
        kwali_id = kwali.id

        admin = User(
            full_name="Stage 8 Admin",
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

    admin_token = login(admin_email, password)

    def create_and_approve(*, market_id: int, at: str, low: str, high: str, average: str, movement: str, time_of_day: str, previous_low: str, previous_high: str, meaning: str, action: str) -> int:
        payload = {
            "commodity_id": commodity_id,
            "market_id": market_id,
            "price_low": low,
            "price_high": high,
            "average_price": average,
            "previous_price_low": previous_low,
            "previous_price_high": previous_high,
            "unit": "bag",
            "bag_size": "250kg bag",
            "commodity_type": "Unpeeled Egusi",
            "market_day": "Monday" if market_id == nasarawa_id else "Tuesday",
            "time_of_day": time_of_day,
            "movement": movement,
            "confidence_level": "Admin confirmed",
            "source_type": "Stage 8 verification",
            "source_1": private_source,
            "source_2": None,
            "update_date_time": at,
            "is_outdated": False,
            "possible_meaning": meaning,
            "suggested_action": action,
            "notes": "Temporary Stage 8 verification record",
        }
        created = client.post("/price-updates", headers=auth(admin_token), json=payload)
        expect(created.status_code == 201, f"price update create works at {at}")
        price_update_id = created.json()["id"]
        created_price_update_ids.append(price_update_id)
        approved = client.patch(f"/price-updates/{price_update_id}/approve", headers=auth(admin_token))
        expect(approved.status_code == 200 and approved.json()["status"] == "approved", f"price update approval works at {at}")
        return price_update_id

    morning_id = create_and_approve(
        market_id=nasarawa_id,
        at="2099-01-15T08:00:00+00:00",
        low="140000.00",
        high="150000.00",
        average="145000.00",
        movement="down",
        time_of_day="morning",
        previous_low="155000.00",
        previous_high="165000.00",
        meaning="Morning price was below the previous reported range.",
        action="Investigate",
    )
    kwali_id_record = create_and_approve(
        market_id=kwali_id,
        at="2099-01-15T10:00:00+00:00",
        low="148000.00",
        high="158000.00",
        average="153000.00",
        movement="stable",
        time_of_day="morning",
        previous_low="148000.00",
        previous_high="158000.00",
        meaning="Kwali price remained within the previously observed range.",
        action="Watch",
    )
    afternoon_id = create_and_approve(
        market_id=nasarawa_id,
        at="2099-01-15T14:00:00+00:00",
        low="150000.00",
        high="160000.00",
        average="155000.00",
        movement="up",
        time_of_day="afternoon",
        previous_low="140000.00",
        previous_high="150000.00",
        meaning="Buyer activity coincided with a higher afternoon reported range.",
        action="Buy Carefully",
    )
    next_day_id = create_and_approve(
        market_id=nasarawa_id,
        at="2099-01-16T09:00:00+00:00",
        low="145000.00",
        high="155000.00",
        average="150000.00",
        movement="down",
        time_of_day="morning",
        previous_low="150000.00",
        previous_high="160000.00",
        meaning="The following day opened below the prior afternoon range.",
        action="Watch",
    )

    commodity_search = client.get("/price-updates", params={"commodity": "gUs", "date": "2099-01-15"})
    expect(commodity_search.status_code == 200, "commodity search request works")
    commodity_ids = {item["id"] for item in commodity_search.json()}
    expect(afternoon_id in commodity_ids and kwali_id_record in commodity_ids, "Egusi commodity search works case-insensitively")
    expect(morning_id not in commodity_ids, "latest search returns latest same-day record per market")

    market_filter = client.get("/price-updates", params={"market": "nasara", "date": "2099-01-15"})
    expect(market_filter.status_code == 200, "market filter request works")
    market_ids = {item["id"] for item in market_filter.json()}
    expect(afternoon_id in market_ids and kwali_id_record not in market_ids, "market filter works")

    date_filter = client.get("/price-updates", params={"commodity": "Egusi", "date": "2099-01-15"})
    expect(date_filter.status_code == 200, "date filter request works")
    expect(next_day_id not in {item["id"] for item in date_filter.json()}, "date filter excludes other dates")

    movement_filter = client.get("/price-updates", params={"commodity": "Egusi", "date": "2099-01-15", "movement": "stable"})
    expect(movement_filter.status_code == 200, "movement filter request works")
    expect(kwali_id_record in {item["id"] for item in movement_filter.json()}, "movement filter works")
    expect(client.get("/price-updates", params={"movement": "sideways"}).status_code == 422, "invalid movement filter rejected")

    history = client.get(
        "/price-updates/history",
        params={"commodity": "Egusi", "market": "Nasarawa", "date": "2099-01-15"},
    )
    expect(history.status_code == 200, "chronological history request works")
    history_rows = [item for item in history.json() if item["id"] in {morning_id, afternoon_id}]
    expect([item["id"] for item in history_rows] == [morning_id, afternoon_id], "history is chronological")
    expect([item["time_of_day"] for item in history_rows] == ["morning", "afternoon"], "same-day time-of-day records work")

    afternoon_history = client.get(
        "/price-updates/history",
        params={"commodity": "Egusi", "market": "Nasarawa", "date": "2099-01-15", "time_of_day": "afternoon"},
    )
    expect(afternoon_history.status_code == 200, "time-of-day history filter works")
    expect(afternoon_id in {item["id"] for item in afternoon_history.json()} and morning_id not in {item["id"] for item in afternoon_history.json()}, "time-of-day filter selects afternoon record")

    comparison = client.get("/price-updates/comparison", params={"commodity": "Egusi", "date": "2099-01-15"})
    expect(comparison.status_code == 200, "market comparison request works")
    comparison_rows = {item["market"]["name"]: item for item in comparison.json() if item["id"] in {afternoon_id, kwali_id_record}}
    expect("Nasarawa" in comparison_rows and "Kwali Market" in comparison_rows, "market comparison returns both markets")
    expect(comparison_rows["Nasarawa"]["id"] == afternoon_id, "market comparison uses latest current record per market")
    expect(comparison_rows["Nasarawa"]["previous_price_low"] is not None and comparison_rows["Nasarawa"]["previous_price_high"] is not None, "previous/current comparison fields preserved")
    expect(comparison_rows["Nasarawa"]["possible_meaning"].startswith("Buyer activity"), "possible meaning preserved through comparison")
    expect(comparison_rows["Nasarawa"]["suggested_action"] == "Buy Carefully", "suggested action preserved through comparison")

    for response in (commodity_search, market_filter, date_filter, movement_filter, history, afternoon_history, comparison):
        expect(all("source_1" not in item and "source_2" not in item for item in response.json()), f"private sources hidden for {response.request.url.path}")

    print(results)

finally:
    with SessionLocal() as db:
        for price_update_id in created_price_update_ids:
            item = db.get(PriceUpdate, price_update_id)
            if item is not None:
                db.delete(item)
        db.flush()

        admin = db.scalar(select(User).where(User.email == admin_email))
        if admin is not None:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == admin.id))
            if subscription is not None:
                db.delete(subscription)
                db.flush()
            db.delete(admin)
        db.commit()

print("STAGE 8 OWNER SMOKE: PASS")
