from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.storage_suitability import StorageSuitability
from app.schemas.storage_suitability_schema import StorageSuitabilityCreate, StorageSuitabilityUpdate


def _validate_storage_references(
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


def create_storage_suitability(db: Session, payload: StorageSuitabilityCreate) -> StorageSuitability:
    _validate_storage_references(
        db,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
        price_update_id=payload.price_update_id,
    )
    item = StorageSuitability(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_storage_suitability(db: Session, item_id: int) -> StorageSuitability:
    item = db.get(StorageSuitability, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage suitability not found")
    return item


def list_storage_suitability(db: Session) -> list[StorageSuitability]:
    return list(
        db.scalars(
            select(StorageSuitability).order_by(
                StorageSuitability.created_at.desc(), StorageSuitability.id.desc()
            )
        ).all()
    )


def update_storage_suitability(
    db: Session,
    item: StorageSuitability,
    payload: StorageSuitabilityUpdate,
) -> StorageSuitability:
    changes = payload.model_dump(exclude_unset=True)
    commodity_id = int(changes.get("commodity_id", item.commodity_id))
    market_id = int(changes.get("market_id", item.market_id))
    price_update_id = changes.get("price_update_id", item.price_update_id)

    _validate_storage_references(
        db,
        commodity_id=commodity_id,
        market_id=market_id,
        price_update_id=int(price_update_id) if price_update_id is not None else None,
    )

    for field, value in changes.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item
