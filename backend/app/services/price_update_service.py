from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import PriceUpdateCreate, PriceUpdateUpdate


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


def create_price_update(db: Session, payload: PriceUpdateCreate, creator: User) -> PriceUpdate:
    _validate_reference_records(db, payload.commodity_id, payload.market_id)
    price_update = PriceUpdate(
        **payload.model_dump(),
        status="pending",
        created_by=creator.id,
        approved_by=None,
    )
    db.add(price_update)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Price update could not be saved") from exc
    return get_price_update_for_admin(db, price_update.id)


def get_price_update_for_admin(db: Session, price_update_id: int) -> PriceUpdate:
    statement = (
        select(PriceUpdate)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(PriceUpdate.id == price_update_id)
    )
    price_update = db.scalar(statement)
    if price_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price update not found")
    return price_update


def get_approved_price_update(db: Session, price_update_id: int) -> PriceUpdate:
    statement = (
        select(PriceUpdate)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(PriceUpdate.id == price_update_id, PriceUpdate.status == "approved")
    )
    price_update = db.scalar(statement)
    if price_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approved price update not found")
    return price_update


def list_latest_approved_price_updates(db: Session) -> list[PriceUpdate]:
    statement = (
        select(PriceUpdate)
        .options(*PRICE_UPDATE_LOAD_OPTIONS)
        .where(PriceUpdate.status == "approved")
        .order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())
    )
    latest_by_market_commodity: dict[tuple[int, int], PriceUpdate] = {}
    for item in db.scalars(statement).all():
        key = (item.commodity_id, item.market_id)
        if key not in latest_by_market_commodity:
            latest_by_market_commodity[key] = item
    return [item for item in latest_by_market_commodity.values() if not item.is_outdated]


def update_price_update(db: Session, price_update: PriceUpdate, payload: PriceUpdateUpdate) -> PriceUpdate:
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

    final_commodity_id = int(changes.get("commodity_id", price_update.commodity_id))
    final_market_id = int(changes.get("market_id", price_update.market_id))
    if "commodity_id" in changes or "market_id" in changes:
        _validate_reference_records(db, final_commodity_id, final_market_id)

    _validate_final_ranges(price_update, changes)

    for field, value in changes.items():
        setattr(price_update, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Price update could not be updated") from exc
    return get_price_update_for_admin(db, price_update.id)


def approve_price_update(db: Session, price_update: PriceUpdate, approver: User) -> PriceUpdate:
    price_update.status = "approved"
    price_update.approved_by = approver.id
    db.commit()
    return get_price_update_for_admin(db, price_update.id)


def reject_price_update(db: Session, price_update: PriceUpdate) -> PriceUpdate:
    price_update.status = "rejected"
    price_update.approved_by = None
    db.commit()
    return get_price_update_for_admin(db, price_update.id)


def mark_price_update_outdated(db: Session, price_update: PriceUpdate) -> PriceUpdate:
    price_update.is_outdated = True
    db.commit()
    return get_price_update_for_admin(db, price_update.id)


def delete_price_update(db: Session, price_update: PriceUpdate) -> None:
    db.delete(price_update)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Price update cannot be deleted because it is referenced by existing records",
        ) from exc
