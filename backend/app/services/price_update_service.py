from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_revision import PriceRevision
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.storage_suitability import StorageSuitability
from app.models.user import User
from app.schemas.price_update_schema import Movement, PriceUpdateCreate, PriceUpdateUpdate
from app.utils.price_measurement import lagos_day_bounds, normalize_label


PRICE_UPDATE_LOAD_OPTIONS = (selectinload(PriceUpdate.commodity), selectinload(PriceUpdate.market))
MAX_PAGE_SIZE = 1000
_SERIES_FIELDS = ("commodity_id", "market_id", "unit", "bag_size", "commodity_type", "grade")


def _validate_reference_records(db: Session, commodity_id: int, market_id: int) -> None:
    for model, record_id, label in ((Commodity, commodity_id, "Commodity"), (Market, market_id, "Market")):
        item = db.get(model, record_id)
        if item is None:
            raise HTTPException(status_code=404, detail=f"{label} not found")
        if not item.is_active:
            raise HTTPException(status_code=422, detail=f"{label} is inactive")


def _validate_final_ranges(item: PriceUpdate, changes: dict) -> None:
    low = Decimal(changes.get("price_low", item.price_low))
    high = Decimal(changes.get("price_high", item.price_high))
    avg_raw = changes.get("average_price", item.average_price)
    avg = Decimal(avg_raw) if avg_raw is not None else None
    if high < low:
        raise HTTPException(status_code=422, detail="price_high must be greater than or equal to price_low")
    if avg is not None and not low <= avg <= high:
        raise HTTPException(status_code=422, detail="average_price must be within the current price range")
    previous_low = changes.get("previous_price_low", item.previous_price_low)
    previous_high = changes.get("previous_price_high", item.previous_price_high)
    if (previous_low is None) != (previous_high is None):
        raise HTTPException(status_code=422, detail="previous price bounds must be provided together")
    if previous_low is not None and Decimal(previous_high) < Decimal(previous_low):
        raise HTTPException(status_code=422, detail="previous_price_high must be greater than or equal to previous_price_low")


def _validate_confidence(values: dict) -> None:
    if values.get("confidence_level") == "Verified by 2 sources":
        sources = [normalize_label(values.get(field)) for field in ("source_1", "source_2")]
        if not all(sources) or sources[0] == sources[1]:
            raise HTTPException(status_code=422, detail="Two-source verification requires two distinct recorded sources")


def _page(statement, page: int, page_size: int):
    if page < 1 or not 1 <= page_size <= MAX_PAGE_SIZE:
        raise HTTPException(status_code=422, detail="Invalid pagination: page >= 1 and page_size between 1 and 1000 required")
    return statement.offset((page - 1) * page_size).limit(page_size)


def _approved_price_statement(*, commodity_search=None, market_search=None, commodity_id=None,
                              market_id=None, selected_date=None, movement=None, time_of_day=None,
                              include_outdated=True, active_only=True):
    statement = (select(PriceUpdate).join(Commodity, PriceUpdate.commodity_id == Commodity.id)
                 .join(Market, PriceUpdate.market_id == Market.id)
                 .options(*PRICE_UPDATE_LOAD_OPTIONS).where(PriceUpdate.status == "approved"))
    if active_only:
        statement = statement.where(Commodity.is_active.is_(True), Market.is_active.is_(True))
    if not include_outdated:
        statement = statement.where(PriceUpdate.is_outdated.is_(False))
    if commodity_id is not None:
        statement = statement.where(PriceUpdate.commodity_id == commodity_id)
    if market_id is not None:
        statement = statement.where(PriceUpdate.market_id == market_id)
    if commodity_search:
        statement = statement.where(Commodity.name.ilike(f"%{commodity_search}%"))
    if market_search:
        statement = statement.where(Market.name.ilike(f"%{market_search}%"))
    if selected_date is not None:
        start, end = lagos_day_bounds(selected_date)
        statement = statement.where(PriceUpdate.update_date_time >= start, PriceUpdate.update_date_time < end)
    if movement is not None:
        statement = statement.where(PriceUpdate.movement == movement)
    if time_of_day is not None:
        statement = statement.where(PriceUpdate.time_of_day == time_of_day)
    return statement


def _series_partition():
    labels = [func.lower(func.trim(func.coalesce(getattr(PriceUpdate, field), "")))
              for field in ("unit", "bag_size", "commodity_type", "grade")]
    # Keep one current unclassified observation per recorded scope. Unspecified
    # bags remain incomparable (and chart keys stay separate), but assigning
    # every old row its own current partition would expose historical IDs.
    return [PriceUpdate.commodity_id, PriceUpdate.market_id, *labels]


def _latest_statement(**filters):
    ranked = (_approved_price_statement(**filters)
              .with_only_columns(PriceUpdate.id,
                                 func.row_number().over(partition_by=_series_partition(),
                                    order_by=(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())).label("position"))
              .subquery())
    return (select(PriceUpdate).join(ranked, PriceUpdate.id == ranked.c.id)
            .options(*PRICE_UPDATE_LOAD_OPTIONS)
            .where(ranked.c.position == 1, PriceUpdate.is_outdated.is_(False)))


def create_price_update(db: Session, payload: PriceUpdateCreate, creator: User) -> PriceUpdate:
    _validate_reference_records(db, payload.commodity_id, payload.market_id)
    values = payload.model_dump()
    if creator.role == "reporter":
        values.update(confidence_level="Reporter submitted", possible_meaning=None, suggested_action="Watch",
                      source_type=None, source_1=None, source_2=None)
    _validate_confidence(values)
    if values["confidence_level"] == "Price outdated":
        values["is_outdated"] = True
    item = PriceUpdate(**values, status="pending", created_by=creator.id, approved_by=None)
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail="Price update could not be saved") from exc
    return get_price_update_for_admin(db, item.id)


def get_price_update_for_admin(db: Session, price_update_id: int) -> PriceUpdate:
    item = db.scalar(select(PriceUpdate).options(*PRICE_UPDATE_LOAD_OPTIONS).where(PriceUpdate.id == price_update_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Price update not found")
    return item


def get_approved_price_update(db: Session, price_update_id: int, *, current_only: bool = False) -> PriceUpdate:
    statement = _latest_statement() if current_only else _approved_price_statement()
    item = db.scalar(statement.where(PriceUpdate.id == price_update_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Eligible approved price update not found")
    return item


def list_latest_approved_price_updates(db: Session, *, commodity_search=None, market_search=None,
                                      commodity_id=None, market_id=None, selected_date=None,
                                      movement: Movement | None = None, page=1, page_size=1000) -> list[PriceUpdate]:
    # Rank first in SQL: outdated/movement filters must never revive an older row.
    statement = _latest_statement(commodity_search=commodity_search, market_search=market_search,
                                  commodity_id=commodity_id, market_id=market_id, selected_date=selected_date)
    if movement is not None:
        statement = statement.where(PriceUpdate.movement == movement)
    statement = statement.order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())
    return list(db.scalars(_page(statement, page, page_size)).all())


def count_latest_approved_price_updates(db: Session) -> int:
    current = _latest_statement().with_only_columns(PriceUpdate.id).subquery()
    return int(db.scalar(select(func.count()).select_from(current)) or 0)


def list_price_history(db: Session, *, commodity_search=None, market_search=None, commodity_id=None,
                       market_id=None, selected_date=None, movement=None, time_of_day=None,
                       page=1, page_size=100) -> list[PriceUpdate]:
    statement = _approved_price_statement(commodity_search=commodity_search, market_search=market_search,
                 commodity_id=commodity_id, market_id=market_id, selected_date=selected_date,
                 movement=movement, time_of_day=time_of_day).order_by(PriceUpdate.update_date_time.asc(), PriceUpdate.id.asc())
    return list(db.scalars(_page(statement, page, page_size)).all())


def get_submission_stats(db: Session, user_id: int) -> dict[str, int]:
    rows = db.execute(select(PriceUpdate.status, func.count()).where(PriceUpdate.created_by == user_id)
                      .group_by(PriceUpdate.status)).all()
    counts = dict(rows)
    return {"submitted": sum(counts.values()), "pending": counts.get("pending", 0),
            "approved": counts.get("approved", 0), "rejected": counts.get("rejected", 0) + counts.get("withdrawn", 0)}


def list_admin_price_updates(db: Session, *, page=1, page_size=100) -> list[PriceUpdate]:
    statement = select(PriceUpdate).options(*PRICE_UPDATE_LOAD_OPTIONS).order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc())
    return list(db.scalars(_page(statement, page, page_size)).all())


def list_market_comparison(db: Session, *, commodity_search=None, commodity_id=None, selected_date=None,
                           page=1, page_size=1000) -> list[PriceUpdate]:
    return list_latest_approved_price_updates(db, commodity_search=commodity_search, commodity_id=commodity_id,
                                             selected_date=selected_date, page=page, page_size=page_size)


def _snapshot_original(item: PriceUpdate) -> dict:
    result = {}
    for column in inspect(item).mapper.column_attrs:
        value = getattr(item, column.key)
        result[column.key] = value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, Decimal) else value
    return result


def _record_revision(db: Session, item: PriceUpdate, actor_id: int, reason: str) -> None:
    # Restricted evidence has no public/general-audit response. Original source
    # identities remain restricted instead of being copied into general logs.
    db.add(PriceRevision(price_update_id=item.id, actor_id=actor_id, reason=reason,
                         original_values=_snapshot_original(item)))


def _lock_price_scope(db: Session, item: PriceUpdate, *, next_commodity_id: int | None = None) -> None:
    # A shared commodity row serializes approval/backfill/correction operations
    # on PostgreSQL, including two pending observations with different IDs.
    # Ordered locks also avoid inverted lock acquisition when scope changes.
    identifiers = {item.commodity_id}
    if next_commodity_id is not None:
        identifiers.add(next_commodity_id)
    db.execute(select(Commodity.id).where(Commodity.id.in_(identifiers)).order_by(Commodity.id).with_for_update()).all()
    db.refresh(item)


def _same_series(item: PriceUpdate):
    criteria = [PriceUpdate.commodity_id == item.commodity_id, PriceUpdate.market_id == item.market_id]
    for field in ("unit", "bag_size", "commodity_type", "grade"):
        criteria.append(func.lower(func.trim(func.coalesce(getattr(PriceUpdate, field), ""))) == normalize_label(getattr(item, field)))
    return criteria


def _derive_comparison(db: Session, item: PriceUpdate) -> None:
    previous = None
    if normalize_label(item.bag_size):
        previous = db.scalar(select(PriceUpdate).where(PriceUpdate.id != item.id, PriceUpdate.status == "approved", *_same_series(item),
                    or_(PriceUpdate.update_date_time < item.update_date_time,
                        and_(PriceUpdate.update_date_time == item.update_date_time, PriceUpdate.id < item.id)))
                    .order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc()).limit(1))
    item.previous_price_update_id = previous.id if previous else None
    item.previous_price_low = previous.price_low if previous else None
    item.previous_price_high = previous.price_high if previous else None
    item.movement = "unknown"
    if previous is not None and previous.average_price is not None and item.average_price is not None:
        item.movement = "up" if item.average_price > previous.average_price else "down" if item.average_price < previous.average_price else "stable"


def _successor(db: Session, item: PriceUpdate):
    if not normalize_label(item.bag_size):
        return None
    return db.scalar(select(PriceUpdate).where(PriceUpdate.status == "approved", *_same_series(item),
                 or_(PriceUpdate.update_date_time > item.update_date_time,
                     and_(PriceUpdate.update_date_time == item.update_date_time, PriceUpdate.id > item.id)))
                 .order_by(PriceUpdate.update_date_time.asc(), PriceUpdate.id.asc()).limit(1))


def _refresh_successor(db: Session, item: PriceUpdate, actor_id: int) -> None:
    db.flush()
    successor = _successor(db, item)
    if successor is not None:
        _record_revision(db, successor, actor_id, "Comparable predecessor changed; recalculated previous range and movement")
        _derive_comparison(db, successor)


def _ensure_unlinked_scope_change(db: Session, item: PriceUpdate, changes: dict) -> None:
    if not any(field in changes and changes[field] != getattr(item, field) for field in _SERIES_FIELDS):
        return
    for model in (MarketSignal, QualitySignal, StorageSuitability):
        if db.scalar(select(model.id).where(model.price_update_id == item.id).limit(1)) is not None:
            raise HTTPException(status_code=409, detail="Price specification cannot change while intelligence is linked; retain the record and submit a corrected specification")


def update_price_update(db: Session, item: PriceUpdate, payload: PriceUpdateUpdate, *, actor: User | None = None) -> PriceUpdate:
    changes = payload.model_dump(exclude_unset=True)
    reason = changes.pop("correction_reason", None)
    if not changes:
        return get_price_update_for_admin(db, item.id)
    _lock_price_scope(db, item, next_commodity_id=changes.get("commodity_id"))
    for field in ("commodity_id", "market_id", "price_low", "price_high", "unit", "bag_size",
                  "movement", "confidence_level", "update_date_time", "is_outdated"):
        if field in changes and changes[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")
    if "commodity_id" in changes or "market_id" in changes:
        _validate_reference_records(db, changes.get("commodity_id", item.commodity_id), changes.get("market_id", item.market_id))
    _ensure_unlinked_scope_change(db, item, changes)
    if item.status == "approved" and not reason:
        raise HTTPException(status_code=422, detail="A correction reason of at least ten characters is required for a published price")
    _validate_final_ranges(item, changes)
    _validate_confidence({field: changes.get(field, getattr(item, field)) for field in ("confidence_level", "source_1", "source_2")})
    if changes.get("confidence_level") == "Price outdated":
        changes["is_outdated"] = True
    if changes.get("is_outdated") is False and changes.get("confidence_level", item.confidence_level) == "Price outdated":
        raise HTTPException(status_code=422, detail="Choose a current confidence label before clearing outdated status")
    actor_id = actor.id if actor else item.approved_by or item.created_by
    approved = item.status == "approved"
    comparison_change = bool(set(changes) & {*_SERIES_FIELDS, "update_date_time", "price_low", "price_high", "average_price"})
    old_successor = _successor(db, item) if approved and comparison_change else None
    if approved:
        _record_revision(db, item, actor_id, reason or "Administrator correction")
    for field, value in changes.items():
        setattr(item, field, value)
    if approved:
        _derive_comparison(db, item)
        if comparison_change:
            _refresh_successor(db, item, actor_id)
            if old_successor is not None:
                _record_revision(db, old_successor, actor_id, "Former comparable predecessor corrected")
                _derive_comparison(db, old_successor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail="Price update could not be updated") from exc
    return get_price_update_for_admin(db, item.id)


def approve_price_update(db: Session, item: PriceUpdate, approver: User) -> PriceUpdate:
    _lock_price_scope(db, item)
    _validate_reference_records(db, item.commodity_id, item.market_id)
    _validate_confidence({field: getattr(item, field) for field in ("confidence_level", "source_1", "source_2")})
    if item.status == "approved":
        return get_price_update_for_admin(db, item.id)
    if item.status == "withdrawn":
        raise HTTPException(status_code=409, detail="Withdrawn evidence cannot be republished; create a reviewed observation")
    item.status = "approved"
    item.approved_by = approver.id
    _derive_comparison(db, item)
    _refresh_successor(db, item, approver.id)
    db.commit()
    return get_price_update_for_admin(db, item.id)


def reject_price_update(db: Session, item: PriceUpdate, *, actor: User | None = None) -> PriceUpdate:
    _lock_price_scope(db, item)
    if item.status == "approved":
        _record_revision(db, item, actor.id if actor else item.approved_by or item.created_by, "Administrator rejected published observation")
    item.status = "rejected"
    item.approved_by = None
    _refresh_successor(db, item, actor.id if actor else item.created_by)
    db.commit()
    return get_price_update_for_admin(db, item.id)


def mark_price_update_outdated(db: Session, item: PriceUpdate, *, actor: User | None = None) -> PriceUpdate:
    _lock_price_scope(db, item)
    if item.status == "approved" and not item.is_outdated:
        _record_revision(db, item, actor.id if actor else item.approved_by or item.created_by, "Administrator marked observation outdated")
    item.is_outdated = True
    db.commit()
    return get_price_update_for_admin(db, item.id)


def delete_price_update(db: Session, item: PriceUpdate, *, actor: User | None = None) -> None:
    _lock_price_scope(db, item)
    # Existing DELETE keeps its 204 contract but withdraws instead of destroying evidence.
    if item.status != "withdrawn":
        actor_id = actor.id if actor else item.approved_by or item.created_by
        _record_revision(db, item, actor_id, "Administrator withdrew observation")
        item.status = "withdrawn"
        item.is_outdated = True
        _refresh_successor(db, item, actor_id)
    db.commit()
