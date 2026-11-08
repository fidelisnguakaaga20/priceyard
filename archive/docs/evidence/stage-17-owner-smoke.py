from __future__ import annotations

import csv
import io
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
from app.models.audit_log import AuditLog
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
password = "Stage17-Test-Password!"
admin_email = f"stage17-admin-{run_id}@example.com"
user_email = f"stage17-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_id: int | None = None
user_id: int | None = None
price_ids: list[int] = []
signal_ids: list[int] = []
quality_ids: list[int] = []


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    check(f"login works for {email}", response.status_code == 200)
    return response.json()["access_token"]


def price_payload(*, commodity_id: int, market_id: int, dt: str, source_1: str, source_2: str, note: str) -> dict:
    return {
        "commodity_id": commodity_id,
        "market_id": market_id,
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
        "source_1": source_1,
        "source_2": source_2,
        "update_date_time": dt,
        "is_outdated": False,
        "possible_meaning": "Supply appears stronger than the previous observation.",
        "suggested_action": "Watch",
        "notes": note,
    }


try:
    with SessionLocal() as db:
        admin = User(
            full_name="Stage 17 Admin",
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
        beans = db.scalar(select(Commodity).where(Commodity.name == "Beans"))
        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        kwali = db.scalar(select(Market).where(Market.name == "Kwali Market"))
        check("Stage 6 Egusi commodity exists", egusi is not None)
        check("Stage 6 Beans commodity exists", beans is not None)
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        check("Stage 6 Kwali Market exists", kwali is not None)
        egusi_id, beans_id = egusi.id, beans.id
        nasarawa_id, kwali_id = nasarawa.id, kwali.id

    registration = client.post(
        "/auth/register",
        json={"full_name": "Stage 17 User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)
    check("unauthenticated CSV export blocked", client.get("/reports/prices.csv").status_code == 401)
    check("ordinary user CSV export blocked", client.get("/reports/prices.csv", headers=auth(user_token)).status_code == 403)

    private_source_1 = f"PRIVATE-SOURCE-ONE-{run_id}"
    private_source_2 = f"PRIVATE-SOURCE-TWO-{run_id}"
    response = client.post(
        "/price-updates",
        json=price_payload(
            commodity_id=egusi_id,
            market_id=nasarawa_id,
            dt="2099-06-15T08:00:00+00:00",
            source_1=private_source_1,
            source_2=private_source_2,
            note="Stage 17 Egusi export row",
        ),
        headers=auth(admin_token),
    )
    check("Egusi price update create works for CSV export", response.status_code == 201)
    egusi_price_id = response.json()["id"]
    price_ids.append(egusi_price_id)
    check("Egusi price approval works for CSV export", client.patch(f"/price-updates/{egusi_price_id}/approve", headers=auth(admin_token)).status_code == 200)

    response = client.post(
        "/market-signals",
        json={
            "commodity_id": egusi_id,
            "market_id": nasarawa_id,
            "price_update_id": egusi_price_id,
            "signal_type": "supply",
            "signal_description": "Supply appears stronger during the observed market period.",
            "possible_meaning": "More bags were observed than earlier.",
            "suggested_action": "Watch",
        },
        headers=auth(admin_token),
    )
    check("linked market signal create works for CSV export", response.status_code == 201)
    signal_ids.append(response.json()["id"])

    response = client.post(
        "/quality-signals",
        json={
            "commodity_id": egusi_id,
            "market_id": nasarawa_id,
            "price_update_id": egusi_price_id,
            "quality_status": "Dry appearance",
            "moisture_status": "No visible wetness observed",
            "storage_readiness": "Inspect before storage",
            "risk_note": "Fresh produce may still require re-drying.",
        },
        headers=auth(admin_token),
    )
    check("linked quality signal create works for CSV export", response.status_code == 201)
    quality_ids.append(response.json()["id"])

    response = client.post(
        "/price-updates",
        json=price_payload(
            commodity_id=beans_id,
            market_id=kwali_id,
            dt="2099-06-16T15:00:00+00:00",
            source_1=f"BEANS-PRIVATE-ONE-{run_id}",
            source_2=f"BEANS-PRIVATE-TWO-{run_id}",
            note="Stage 17 Beans export row",
        ),
        headers=auth(admin_token),
    )
    check("Beans price update create works for CSV export", response.status_code == 201)
    beans_price_id = response.json()["id"]
    price_ids.append(beans_price_id)
    check("Beans price approval works for CSV export", client.patch(f"/price-updates/{beans_price_id}/approve", headers=auth(admin_token)).status_code == 200)

    response = client.post(
        "/price-updates",
        json=price_payload(
            commodity_id=egusi_id,
            market_id=kwali_id,
            dt="2099-06-15T11:00:00+00:00",
            source_1=f"REJECTED-PRIVATE-ONE-{run_id}",
            source_2=f"REJECTED-PRIVATE-TWO-{run_id}",
            note="Stage 17 rejected row",
        ),
        headers=auth(admin_token),
    )
    check("rejected-row price create works", response.status_code == 201)
    rejected_price_id = response.json()["id"]
    price_ids.append(rejected_price_id)
    check("rejected price can be rejected", client.patch(f"/price-updates/{rejected_price_id}/reject", headers=auth(admin_token)).status_code == 200)

    invalid_range = client.get(
        "/reports/prices.csv?date_from=2099-06-16&date_to=2099-06-15",
        headers=auth(admin_token),
    )
    check("invalid CSV date range rejected", invalid_range.status_code == 422)

    response = client.get(
        "/reports/prices.csv?commodity=Egusi&market=Nasarawa&date_from=2099-06-15&date_to=2099-06-15",
        headers=auth(admin_token),
    )
    check("CSV downloads", response.status_code == 200)
    check("CSV response content type works", response.headers.get("content-type", "").startswith("text/csv"))
    check("CSV attachment filename works", "priceyard-price-report.csv" in response.headers.get("content-disposition", ""))
    rows = list(csv.DictReader(io.StringIO(response.text)))
    check("commodity market and date filters isolate one row", len(rows) == 1)
    row = rows[0]
    check("exported commodity matches database record", row["commodity"] == "Egusi")
    check("exported market matches database record", row["market"] == "Nasarawa")
    check("exported current range matches database record", row["price_low"] == "135000.00" and row["price_high"] == "145000.00")
    check("exported previous range matches database record", row["previous_price_low"] == "150000.00" and row["previous_price_high"] == "160000.00")
    check("exported movement matches database record", row["movement"] == "down")
    check("exported confidence matches database record", row["confidence_level"] == "Admin confirmed")
    check("possible meaning exported", row["possible_meaning"] == "Supply appears stronger than the previous observation.")
    check("suggested action exported", row["suggested_action"] == "Watch")
    check("linked market signal exported", "Supply appears stronger during the observed market period." in row["market_signals"])
    check("linked quality signal exported", "Dry appearance" in row["quality_signals"])

    serialized_csv = response.text
    check("private source 1 absent from CSV", private_source_1 not in serialized_csv)
    check("private source 2 absent from CSV", private_source_2 not in serialized_csv)
    check("password absent from CSV", password not in serialized_csv)
    check("password hash field absent from CSV", "password_hash" not in serialized_csv)
    check("JWT/token fields absent from CSV", "access_token" not in serialized_csv and "jwt" not in serialized_csv.lower())

    beans_response = client.get(
        "/reports/prices.csv?commodity=Beans&market=Kwali&date_from=2099-06-16&date_to=2099-06-16",
        headers=auth(admin_token),
    )
    beans_rows = list(csv.DictReader(io.StringIO(beans_response.text)))
    check("Beans commodity filter works", beans_response.status_code == 200 and len(beans_rows) == 1 and beans_rows[0]["commodity"] == "Beans")
    check("Kwali market filter works", beans_rows[0]["market"] == "Kwali Market")

    all_date_response = client.get(
        "/reports/prices.csv?date_from=2099-06-15&date_to=2099-06-16",
        headers=auth(admin_token),
    )
    all_rows = list(csv.DictReader(io.StringIO(all_date_response.text)))
    ids_by_signature = {(r["commodity"], r["market"], r["update_date_time"]) for r in all_rows}
    check("inclusive date-range filter contains approved test rows", any(x[0] == "Egusi" and x[1] == "Nasarawa" for x in ids_by_signature) and any(x[0] == "Beans" and x[1] == "Kwali Market" for x in ids_by_signature))
    check("rejected price update excluded from CSV", not any(r["commodity"] == "Egusi" and r["market"] == "Kwali Market" and r["update_date_time"].startswith("2099-06-15T11:00:00") for r in all_rows))

    print(checks)
    print("STAGE 17 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        for item_id in quality_ids:
            item = db.get(QualitySignal, item_id)
            if item is not None:
                db.delete(item)
        for item_id in signal_ids:
            item = db.get(MarketSignal, item_id)
            if item is not None:
                db.delete(item)
        db.commit()

        for item_id in price_ids:
            item = db.get(PriceUpdate, item_id)
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
