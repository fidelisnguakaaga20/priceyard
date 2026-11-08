from __future__ import annotations

import csv
import io
import sys
from datetime import date, datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Commodity, Market, MarketSignal, PriceUpdate, QualitySignal, User
from app.services.report_export_service import build_price_report_csv, list_exportable_price_updates

engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
Base.metadata.create_all(engine)
checks: dict[str, str] = {}


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


with Session(engine) as db:
    admin = User(full_name="Admin", email="stage17-internal@example.com", password_hash="test-hash", role="admin", is_active=True)
    egusi = Commodity(name="Egusi", is_active=True)
    beans = Commodity(name="Beans", is_active=True)
    nasarawa = Market(name="Nasarawa", state="Nasarawa", country="Nigeria", market_day="Monday", is_active=True)
    kwali = Market(name="Kwali Market", state="FCT", country="Nigeria", market_day="Tuesday", is_active=True)
    db.add_all([admin, egusi, beans, nasarawa, kwali])
    db.commit()
    for item in [admin, egusi, beans, nasarawa, kwali]:
        db.refresh(item)

    row1 = PriceUpdate(
        commodity_id=egusi.id,
        market_id=nasarawa.id,
        price_low=135000,
        price_high=145000,
        average_price=140000,
        previous_price_low=150000,
        previous_price_high=160000,
        unit="bag",
        bag_size="250kg",
        commodity_type="unpeeled",
        market_day="Monday",
        time_of_day="morning",
        movement="down",
        confidence_level="Admin confirmed",
        source_type="test",
        source_1="PRIVATE-ONE",
        source_2="PRIVATE-TWO",
        update_date_time=datetime(2099, 6, 15, 8, 0, tzinfo=timezone.utc),
        is_outdated=False,
        status="approved",
        created_by=admin.id,
        approved_by=admin.id,
        possible_meaning="Supply appears stronger than earlier.",
        suggested_action="Watch",
        notes="internal",
    )
    row2 = PriceUpdate(
        commodity_id=beans.id,
        market_id=kwali.id,
        price_low=90000,
        price_high=100000,
        average_price=95000,
        previous_price_low=92000,
        previous_price_high=102000,
        unit="bag",
        movement="stable",
        confidence_level="Verified by 2 sources",
        update_date_time=datetime(2099, 6, 16, 15, 0, tzinfo=timezone.utc),
        is_outdated=False,
        status="approved",
        created_by=admin.id,
        approved_by=admin.id,
        possible_meaning="Market appears broadly stable.",
        suggested_action="Investigate",
    )
    rejected = PriceUpdate(
        commodity_id=egusi.id,
        market_id=kwali.id,
        price_low=120000,
        price_high=125000,
        average_price=122500,
        unit="bag",
        movement="unknown",
        confidence_level="Low confidence",
        update_date_time=datetime(2099, 6, 15, 10, 0, tzinfo=timezone.utc),
        is_outdated=False,
        status="rejected",
        created_by=admin.id,
        approved_by=None,
        possible_meaning="Rejected test row.",
        suggested_action="Watch",
    )
    db.add_all([row1, row2, rejected])
    db.commit()
    for item in [row1, row2, rejected]:
        db.refresh(item)

    db.add(
        MarketSignal(
            commodity_id=egusi.id,
            market_id=nasarawa.id,
            price_update_id=row1.id,
            signal_type="supply",
            signal_description="Supply appears stronger.",
            possible_meaning="More bags observed.",
            suggested_action="Watch",
            created_by=admin.id,
        )
    )
    db.add(
        QualitySignal(
            commodity_id=egusi.id,
            market_id=nasarawa.id,
            price_update_id=row1.id,
            quality_status="Dry appearance",
            moisture_status="No visible wetness observed",
            storage_readiness="Inspect before storage",
            risk_note="Fresh produce may need re-drying.",
            created_by=admin.id,
        )
    )
    db.commit()

    items = list_exportable_price_updates(
        db,
        commodity_search="Egusi",
        market_search="Nasarawa",
        date_from=date(2099, 6, 15),
        date_to=date(2099, 6, 15),
    )
    check("filters isolate approved Egusi/Nasarawa row", len(items) == 1 and items[0].id == row1.id)
    text = build_price_report_csv(items)
    rows = list(csv.DictReader(io.StringIO(text)))
    check("CSV row generated", len(rows) == 1)
    exported = rows[0]
    check("current range exported", exported["price_low"] == "135000.00" and exported["price_high"] == "145000.00")
    check("previous range exported", exported["previous_price_low"] == "150000.00" and exported["previous_price_high"] == "160000.00")
    check("possible meaning preserved", exported["possible_meaning"] == "Supply appears stronger than earlier.")
    check("suggested action preserved", exported["suggested_action"] == "Watch")
    check("market signal included", "Supply appears stronger." in exported["market_signals"])
    check("quality signal included", "Dry appearance" in exported["quality_signals"])
    check("private source identities absent", "PRIVATE-ONE" not in text and "PRIVATE-TWO" not in text)

    date_items = list_exportable_price_updates(db, date_from=date(2099, 6, 15), date_to=date(2099, 6, 16))
    check("date range returns both approved rows only", {item.id for item in date_items} == {row1.id, row2.id})

    invalid_rejected = False
    try:
        list_exportable_price_updates(db, date_from=date(2099, 6, 16), date_to=date(2099, 6, 15))
    except Exception as exc:
        invalid_rejected = getattr(exc, "status_code", None) == 422
    check("invalid date order rejected", invalid_rejected)

print(checks)
print("STAGE 17 INTERNAL CHECK: PASS")
