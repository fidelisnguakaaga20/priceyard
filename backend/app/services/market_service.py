from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.market import Market
from app.schemas.market_schema import MarketCreate, MarketUpdate
from app.services.catalog_identity_service import lock_catalog_identity


def list_markets(db: Session, *, active_only: bool = False) -> list[Market]:
    statement = select(Market)
    if active_only:
        statement = statement.where(Market.is_active.is_(True))
    return list(db.scalars(statement.order_by(Market.name)).all())


def get_market(db: Session, market_id: int, *, lock: bool = False) -> Market:
    statement = select(Market).where(Market.id == market_id)
    if lock:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    market = db.scalar(statement)
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return market


def _normalized_state(value: str | None) -> str | None:
    return value.strip().lower() if value else None


def _ensure_unique_market(db: Session, name: str, state_value: str | None, *, exclude_id: int | None = None) -> None:
    statement = select(Market).where(func.lower(Market.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Market.id != exclude_id)

    requested_state = _normalized_state(state_value)
    for market in db.scalars(statement).all():
        if _normalized_state(market.state) == requested_state:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Market already exists")


def create_market(db: Session, payload: MarketCreate, *, commit: bool = True) -> Market:
    lock_catalog_identity(db, "market")
    _ensure_unique_market(db, payload.name, payload.state)
    market = Market(**payload.model_dump())
    db.add(market)
    db.commit() if commit else db.flush()
    return market


def update_market(db: Session, market: Market, payload: MarketUpdate, *, commit: bool = True) -> Market:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Market name cannot be null")
    if "country" in changes and changes["country"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Market country cannot be null")
    if "is_active" in changes and changes["is_active"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Market active status cannot be null")

    final_name = changes.get("name", market.name)
    final_state = changes.get("state", market.state)
    if "name" in changes or "state" in changes:
        lock_catalog_identity(db, "market")
        _ensure_unique_market(db, final_name, final_state, exclude_id=market.id)

    for field, value in changes.items():
        setattr(market, field, value)

    db.commit() if commit else db.flush()
    return market


def delete_market(db: Session, market: Market, *, commit: bool = True) -> None:
    db.delete(market)
    try:
        db.commit() if commit else db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Market cannot be deleted because it is referenced by existing records",
        ) from exc
