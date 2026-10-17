from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.storage_suitability import StorageSuitability


def lock_price_scope(db: Session, price_update_id: int) -> PriceUpdate:
    price = db.scalar(select(PriceUpdate).where(PriceUpdate.id == price_update_id)
                      .with_for_update().execution_options(populate_existing=True))
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price update not found")
    return price


def validate_linked_price_scope(db: Session, *, price_update_id: int | None, commodity_id: int, market_id: int) -> None:
    if price_update_id is None:
        return
    # Share the parent's edit lock, then re-read its committed identity. A plain
    # SELECT followed by an FK insert can validate a stale pre-correction scope.
    price = lock_price_scope(db, price_update_id)
    if price.commodity_id != commodity_id or price.market_id != market_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Linked price update must use the same commodity and market")


def validate_price_scope_change(db: Session, price: PriceUpdate, *, commodity_id: int, market_id: int) -> None:
    if (commodity_id, market_id) == (price.commodity_id, price.market_id):
        return
    for model in (MarketSignal, QualitySignal, StorageSuitability):
        conflict = db.scalar(select(model.id).where(model.price_update_id == price.id,
            or_(model.commodity_id != commodity_id, model.market_id != market_id)).limit(1))
        if conflict is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail="Price commodity or market cannot change while linked records use a different commodity or market")
