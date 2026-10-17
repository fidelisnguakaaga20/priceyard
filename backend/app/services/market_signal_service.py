from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.price_scope_service import validate_linked_price_scope

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.user import User
from app.schemas.market_signal_schema import MarketSignalCreate, MarketSignalUpdate


def _validate_signal_references(
    db: Session,
    *,
    commodity_id: int,
    market_id: int,
    price_update_id: int | None,
) -> None:
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

    validate_linked_price_scope(db, price_update_id=price_update_id,
                                commodity_id=commodity_id, market_id=market_id)


def create_market_signal(db: Session, payload: MarketSignalCreate, admin: User, *, commit: bool = True) -> MarketSignal:
    _validate_signal_references(
        db,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
        price_update_id=payload.price_update_id,
    )
    signal = MarketSignal(**payload.model_dump(), created_by=admin.id)
    db.add(signal)
    db.commit() if commit else db.flush()
    return signal


def get_market_signal(db: Session, signal_id: int, *, lock: bool = False) -> MarketSignal:
    statement = select(MarketSignal).where(MarketSignal.id == signal_id)
    if lock:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    signal = db.scalar(statement)
    if signal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market signal not found")
    return signal


def list_market_signals(db: Session, *, commodity_id: int | None = None) -> list[MarketSignal]:
    statement = select(MarketSignal)
    if commodity_id is not None:
        statement = statement.where(MarketSignal.commodity_id == commodity_id)
    return list(db.scalars(statement.order_by(MarketSignal.created_at.desc(), MarketSignal.id.desc())).all())


def update_market_signal(db: Session, signal: MarketSignal, payload: MarketSignalUpdate, *, commit: bool = True) -> MarketSignal:
    changes = payload.model_dump(exclude_unset=True)
    required = ("commodity_id", "market_id", "signal_type", "signal_description")
    if any(field in changes and changes[field] is None for field in required):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Required market-signal values cannot be null")
    commodity_id = int(changes.get("commodity_id", signal.commodity_id))
    market_id = int(changes.get("market_id", signal.market_id))
    price_update_id = changes.get("price_update_id", signal.price_update_id)

    _validate_signal_references(
        db,
        commodity_id=commodity_id,
        market_id=market_id,
        price_update_id=int(price_update_id) if price_update_id is not None else None,
    )

    for field, value in changes.items():
        setattr(signal, field, value)
    db.commit() if commit else db.flush()
    return signal


def delete_market_signal(db: Session, signal: MarketSignal, *, commit: bool = True) -> None:
    db.delete(signal)
    db.commit() if commit else db.flush()
