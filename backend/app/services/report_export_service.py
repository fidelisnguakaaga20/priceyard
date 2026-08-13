from __future__ import annotations

import csv
from datetime import date, datetime, time, timedelta, timezone
from io import StringIO

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate


CSV_HEADERS = [
    "commodity",
    "market",
    "price_low",
    "price_high",
    "previous_price_low",
    "previous_price_high",
    "movement",
    "update_date_time",
    "confidence_level",
    "possible_meaning",
    "suggested_action",
    "market_signals",
    "quality_signals",
]


def _format_market_signals(item: PriceUpdate) -> str:
    parts: list[str] = []
    for signal in sorted(item.market_signals, key=lambda value: value.id):
        text = f"{signal.signal_type}: {signal.signal_description}"
        if signal.possible_meaning:
            text += f"; possible meaning: {signal.possible_meaning}"
        if signal.suggested_action:
            text += f"; suggested action: {signal.suggested_action}"
        parts.append(text)
    return " || ".join(parts)


def _format_quality_signals(item: PriceUpdate) -> str:
    parts: list[str] = []
    for signal in sorted(item.quality_signals, key=lambda value: value.id):
        fields: list[str] = []
        if signal.quality_status:
            fields.append(f"quality: {signal.quality_status}")
        if signal.moisture_status:
            fields.append(f"moisture: {signal.moisture_status}")
        if signal.storage_readiness:
            fields.append(f"storage readiness: {signal.storage_readiness}")
        if signal.risk_note:
            fields.append(f"risk: {signal.risk_note}")
        parts.append("; ".join(fields))
    return " || ".join(part for part in parts if part)


def list_exportable_price_updates(
    db: Session,
    *,
    commodity_search: str | None = None,
    market_search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[PriceUpdate]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from must be earlier than or equal to date_to",
        )

    statement = (
        select(PriceUpdate)
        .options(
            selectinload(PriceUpdate.commodity),
            selectinload(PriceUpdate.market),
            selectinload(PriceUpdate.market_signals),
            selectinload(PriceUpdate.quality_signals),
        )
        .where(PriceUpdate.status == "approved")
    )

    if commodity_search:
        statement = statement.join(Commodity, PriceUpdate.commodity_id == Commodity.id).where(
            Commodity.name.ilike(f"%{commodity_search}%")
        )

    if market_search:
        statement = statement.join(Market, PriceUpdate.market_id == Market.id).where(
            Market.name.ilike(f"%{market_search}%")
        )

    if date_from is not None:
        start = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        statement = statement.where(PriceUpdate.update_date_time >= start)

    if date_to is not None:
        end = datetime.combine(date_to, time.min, tzinfo=timezone.utc) + timedelta(days=1)
        statement = statement.where(PriceUpdate.update_date_time < end)

    statement = statement.order_by(PriceUpdate.update_date_time.asc(), PriceUpdate.id.asc())
    return list(db.scalars(statement).all())


def build_price_report_csv(items: list[PriceUpdate]) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for item in items:
        writer.writerow(
            [
                item.commodity.name,
                item.market.name,
                item.price_low,
                item.price_high,
                item.previous_price_low if item.previous_price_low is not None else "",
                item.previous_price_high if item.previous_price_high is not None else "",
                item.movement,
                item.update_date_time.isoformat(),
                item.confidence_level,
                item.possible_meaning or "",
                item.suggested_action or "",
                _format_market_signals(item),
                _format_quality_signals(item),
            ]
        )

    return output.getvalue()
