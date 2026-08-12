from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.user import User
from app.schemas.quality_signal_schema import QualitySignalCreate, QualitySignalUpdate


def _validate_quality_references(
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


def create_quality_signal(db: Session, payload: QualitySignalCreate, admin: User) -> QualitySignal:
    _validate_quality_references(
        db,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
        price_update_id=payload.price_update_id,
    )
    signal = QualitySignal(**payload.model_dump(), created_by=admin.id)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def get_quality_signal(db: Session, signal_id: int) -> QualitySignal:
    signal = db.get(QualitySignal, signal_id)
    if signal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quality signal not found")
    return signal


def list_quality_signals(db: Session) -> list[QualitySignal]:
    return list(db.scalars(select(QualitySignal).order_by(QualitySignal.created_at.desc(), QualitySignal.id.desc())).all())


def update_quality_signal(db: Session, signal: QualitySignal, payload: QualitySignalUpdate) -> QualitySignal:
    changes = payload.model_dump(exclude_unset=True)
    commodity_id = int(changes.get("commodity_id", signal.commodity_id))
    market_id = int(changes.get("market_id", signal.market_id))
    price_update_id = changes.get("price_update_id", signal.price_update_id)

    _validate_quality_references(
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


def delete_quality_signal(db: Session, signal: QualitySignal) -> None:
    db.delete(signal)
    db.commit()
