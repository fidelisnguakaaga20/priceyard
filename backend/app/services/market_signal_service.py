from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
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

    if price_update_id is None:
        return

    price_update = db.get(PriceUpdate, price_update_id)
    if price_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price update not found")
    if price_update.commodity_id != commodity_id or price_update.market_id != market_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Linked price update must use the same commodity and market",
        )


def create_market_signal(db: Session, payload: MarketSignalCreate, admin: User) -> MarketSignal:
    _validate_signal_references(
        db,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
        price_update_id=payload.price_update_id,
    )
    signal = MarketSignal(**payload.model_dump(), created_by=admin.id)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def get_market_signal(db: Session, signal_id: int) -> MarketSignal:
    signal = db.get(MarketSignal, signal_id)
    if signal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market signal not found")
    return signal


def list_market_signals(db: Session) -> list[MarketSignal]:
    return list(db.scalars(select(MarketSignal).order_by(MarketSignal.created_at.desc(), MarketSignal.id.desc())).all())


def update_market_signal(db: Session, signal: MarketSignal, payload: MarketSignalUpdate) -> MarketSignal:
    changes = payload.model_dump(exclude_unset=True)
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
    db.commit()
    db.refresh(signal)
    return signal


def delete_market_signal(db: Session, signal: MarketSignal) -> None:
    db.delete(signal)
    db.commit()
