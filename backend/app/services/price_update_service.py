from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import Movement, PriceUpdateCreate, PriceUpdateUpdate, TimeOfDay
from app.services.price_scope_service import lock_price_scope, validate_price_scope_change


PRICE_UPDATE_LOAD_OPTIONS = (
    selectinload(PriceUpdate.commodity),
    selectinload(PriceUpdate.market),
)


def _validate_reference_records(db: Session, commodity_id: int, market_id: int) -> None:
    commodity = db.get(Commodity, commodity_id)
    if commodity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    if not commodity.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Commodity is inactive")

    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    if not market.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Market is inactive")


def _validate_final_ranges(price_update: PriceUpdate, changes: dict[str, object]) -> None:
    price_low = Decimal(changes.get("price_low", price_update.price_low))
    price_high = Decimal(changes.get("price_high", price_update.price_high))
    average_price_raw = changes.get("average_price", price_update.average_price)
    average_price = Decimal(average_price_raw) if average_price_raw is not None else None

    if price_high < price_low:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="price_high must be greater than or equal to price_low",
        )
    if average_price is not None and not (price_low <= average_price <= price_high):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="average_price must be within the current price range",
        )

    previous_low = changes.get("previous_price_low", price_update.previous_price_low)
    previous_high = changes.get("previous_price_high", price_update.previous_price_high)
    if (previous_low is None) != (previous_high is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="previous_price_low and previous_price_high must be provided together",
        )
    if previous_low is not None and previous_high is not None and Decimal(previous_high) < Decimal(previous_low):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="previous_price_high must be greater than or equal to previous_price_low",
        )


def _approved_price_statement(
    *,
    commodity_search: str | None = None,
    market_search: str | None = None,
    selected_date: date | None = None,
    movement: Movement | None = None,
    time_of_day: TimeOfDay | None = None,
    include_outdated: bool = True,
    active_only: bool = True,
):
    statement = (
        select(PriceUpdate)
        .join(Commodity, PriceUpdate.commodity_id == Commodity.id)
        .join(Market, PriceUpdate.market_id == Market.id)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(PriceUpdate.status == "approved")
    )

    if active_only:
        statement = statement.where(Commodity.is_active.is_(True), Market.is_active.is_(True))

    if not include_outdated:
        statement = statement.where(PriceUpdate.is_outdated.is_(False))

    if commodity_search:
        statement = statement.where(Commodity.name.ilike(f"%{commodity_search}%"))

    if market_search:
        statement = statement.where(Market.name.ilike(f"%{market_search}%"))

    if selected_date is not None:
        start = datetime.combine(selected_date, time.min, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        statement = statement.where(
            PriceUpdate.update_date_time >= start,
            PriceUpdate.update_date_time < end,
        )

    if movement is not None:
        statement = statement.where(PriceUpdate.movement == movement)

    if time_of_day is not None:
        statement = statement.where(PriceUpdate.time_of_day == time_of_day)

    return statement


def create_price_update(db: Session, payload: PriceUpdateCreate, creator: User, *, commit: bool = True) -> PriceUpdate:
    _validate_reference_records(db, payload.commodity_id, payload.market_id)
    values = payload.model_dump()
    if creator.role == "reporter":
        # A reporter submits a raw field observation only. Confidence level and any
        # editorial commentary/sourcing are the admin's judgment to add during
        # review, not something an unvetted submission should be able to self-attest.
        values["confidence_level"] = "Reporter submitted"
        values["possible_meaning"] = None
        values["suggested_action"] = "Watch"
        values["source_type"] = None
        values["source_1"] = None
        values["source_2"] = None
    price_update = PriceUpdate(
        **values,
        status="pending",
        created_by=creator.id,
        approved_by=None,
    )
    db.add(price_update)
    try:
        db.commit() if commit else db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Price update could not be saved") from exc
    return get_price_update_for_admin(db, price_update.id)


def get_price_update_for_admin(db: Session, price_update_id: int, *, lock: bool = False) -> PriceUpdate:
    statement = (
        select(PriceUpdate)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(PriceUpdate.id == price_update_id)
    )
    if lock:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    price_update = db.scalar(statement)
    if price_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price update not found")
    return price_update


def get_approved_price_update(db: Session, price_update_id: int) -> PriceUpdate:
    statement = (
        select(PriceUpdate)
        .join(Commodity, PriceUpdate.commodity_id == Commodity.id)
        .join(Market, PriceUpdate.market_id == Market.id)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(
            PriceUpdate.id == price_update_id,
            PriceUpdate.status == "approved",
            Commodity.is_active.is_(True),
            Market.is_active.is_(True),
        )
    )
    price_update = db.scalar(statement)
    if price_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approved price update not found")
    return price_update


def _latest_approved_price_statement(
    *,
    commodity_search: str | None = None,
    market_search: str | None = None,
    selected_date: date | None = None,
    movement: Movement | None = None,
):
    # Owner-approved specification groups: unlike recorded quantities/types must
    # not replace one another. Keep the latest record per group, then exclude
    # outdated records without resurfacing an older same-specification price.
    # This prevents an older non-outdated record from resurfacing as "current".
    # Movement is also applied after selecting the latest record so a movement
    # filter cannot accidentally surface an older historical match.
    ranked = _approved_price_statement(
        commodity_search=commodity_search,
        market_search=market_search,
        selected_date=selected_date,
        movement=None,
        include_outdated=True,
    ).with_only_columns(
        PriceUpdate.id.label("price_update_id"),
        func.row_number().over(
            partition_by=(
                PriceUpdate.commodity_id, PriceUpdate.market_id,
                func.lower(func.trim(func.coalesce(PriceUpdate.unit, ""))),
                func.lower(func.trim(func.coalesce(PriceUpdate.bag_size, ""))),
                func.lower(func.trim(func.coalesce(PriceUpdate.commodity_type, ""))),
            ),
            order_by=(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc()),
        ).label("position"),
    ).subquery()

    # Rank inside the database so retained history is not loaded into Python
    # for every current-price/ticker request. Do not limit or delete history.
    statement = (
        select(PriceUpdate)
        .join(ranked, ranked.c.price_update_id == PriceUpdate.id)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(ranked.c.position == 1, PriceUpdate.is_outdated.is_(False))
        .order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())
    )
    if movement is not None:
        statement = statement.where(PriceUpdate.movement == movement)
    return statement


def list_latest_approved_price_updates(
    db: Session,
    *,
    commodity_search: str | None = None,
    market_search: str | None = None,
    selected_date: date | None = None,
    movement: Movement | None = None,
) -> list[PriceUpdate]:
    return list(db.scalars(_latest_approved_price_statement(
        commodity_search=commodity_search, market_search=market_search,
        selected_date=selected_date, movement=movement,
    )).all())


def list_price_history(
    db: Session,
    *,
    commodity_search: str | None = None,
    market_search: str | None = None,
    selected_date: date | None = None,
    movement: Movement | None = None,
    time_of_day: TimeOfDay | None = None,
) -> list[PriceUpdate]:
    statement = _approved_price_statement(
        commodity_search=commodity_search,
        market_search=market_search,
        selected_date=selected_date,
        movement=movement,
        time_of_day=time_of_day,
        include_outdated=True,
    ).order_by(PriceUpdate.update_date_time.asc(), PriceUpdate.id.asc())
    return list(db.scalars(statement).all())


def list_price_history_pairs(db: Session) -> list[dict[str, dict[str, str]]]:
    """Existing history filter options, without loading every historical price."""
    statement = (
        select(Commodity.name, Market.name)
        .select_from(PriceUpdate)
        .join(Commodity, PriceUpdate.commodity_id == Commodity.id)
        .join(Market, PriceUpdate.market_id == Market.id)
        .where(PriceUpdate.status == "approved", Commodity.is_active.is_(True), Market.is_active.is_(True))
        .distinct()
        .order_by(Commodity.name, Market.name)
    )
    return [{"commodity": {"name": commodity}, "market": {"name": market}} for commodity, market in db.execute(statement)]


def get_submission_stats(db: Session, user_id: int) -> dict[str, int]:
    """Counts of this user's own price-update submissions by status, so reporters
    (who otherwise get no feedback after submitting) can see their contributions."""
    rows = db.execute(
        select(PriceUpdate.status, func.count())
        .where(PriceUpdate.created_by == user_id)
        .group_by(PriceUpdate.status)
    ).all()
    counts = {status_value: count for status_value, count in rows}
    return {
        "submitted": sum(counts.values()),
        "pending": counts.get("pending", 0),
        "approved": counts.get("approved", 0),
        "rejected": counts.get("rejected", 0),
    }


def list_admin_price_updates(db: Session) -> list[PriceUpdate]:
    """Return every price-update status to admins so pending records remain approvable after refresh."""
    statement = (
        select(PriceUpdate)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())
    )
    return list(db.scalars(statement).all())


def list_market_comparison(
    db: Session,
    *,
    commodity_search: str,
    selected_date: date | None = None,
) -> list[PriceUpdate]:
    # Each returned record already carries current range, previous range,
    # movement, confidence, possible meaning and suggested action. Returning
    # the latest approved current record per market makes both previous/current
    # and cross-market comparison possible without creating duplicate data.
    return list_latest_approved_price_updates(
        db,
        commodity_search=commodity_search,
        selected_date=selected_date,
    )


def update_price_update(db: Session, price_update: PriceUpdate, payload: PriceUpdateUpdate, *, commit: bool = True) -> PriceUpdate:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return get_price_update_for_admin(db, price_update.id)

    for non_nullable_field in (
        "commodity_id",
        "market_id",
        "price_low",
        "price_high",
        "average_price",
        "unit",
        "movement",
        "confidence_level",
        "update_date_time",
        "is_outdated",
        "possible_meaning",
        "suggested_action",
    ):
        if non_nullable_field in changes and changes[non_nullable_field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{non_nullable_field} cannot be null",
            )

    if "commodity_id" in changes or "market_id" in changes:
        price_update = lock_price_scope(db, price_update.id)
    final_commodity_id = int(changes.get("commodity_id", price_update.commodity_id))
    final_market_id = int(changes.get("market_id", price_update.market_id))
    if "commodity_id" in changes or "market_id" in changes:
        _validate_reference_records(db, final_commodity_id, final_market_id)
        validate_price_scope_change(db, price_update, commodity_id=final_commodity_id, market_id=final_market_id)

    _validate_final_ranges(price_update, changes)

    for field, value in changes.items():
        setattr(price_update, field, value)

    try:
        db.commit() if commit else db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Price update could not be updated") from exc
    return get_price_update_for_admin(db, price_update.id)


def approve_price_update(db: Session, price_update: PriceUpdate, approver: User, *, commit: bool = True) -> PriceUpdate:
    price_update.status = "approved"
    price_update.approved_by = approver.id
    db.commit() if commit else db.flush()
    return get_price_update_for_admin(db, price_update.id)


def reject_price_update(db: Session, price_update: PriceUpdate, *, commit: bool = True) -> PriceUpdate:
    price_update.status = "rejected"
    price_update.approved_by = None
    db.commit() if commit else db.flush()
    return get_price_update_for_admin(db, price_update.id)


def mark_price_update_outdated(db: Session, price_update: PriceUpdate, *, commit: bool = True) -> PriceUpdate:
    price_update.is_outdated = True
    db.commit() if commit else db.flush()
    return get_price_update_for_admin(db, price_update.id)


def delete_price_update(db: Session, price_update: PriceUpdate, *, commit: bool = True) -> None:
    db.delete(price_update)
    try:
        db.commit() if commit else db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Price update cannot be deleted because it is referenced by existing records",
        ) from exc
