from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.schemas.commodity_schema import CommodityCreate, CommodityUpdate


def list_commodities(db: Session, *, active_only: bool = False) -> list[Commodity]:
    statement = select(Commodity)
    if active_only:
        statement = statement.where(Commodity.is_active.is_(True))
    return list(db.scalars(statement.order_by(Commodity.name)).all())


def get_commodity(db: Session, commodity_id: int) -> Commodity:
    commodity = db.get(Commodity, commodity_id)
    if commodity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    return commodity


def _ensure_unique_name(db: Session, name: str, *, exclude_id: int | None = None) -> None:
    statement = select(Commodity).where(func.lower(Commodity.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Commodity.id != exclude_id)
    if db.scalar(statement) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Commodity already exists")


def create_commodity(db: Session, payload: CommodityCreate) -> Commodity:
    _ensure_unique_name(db, payload.name)
    commodity = Commodity(**payload.model_dump())
    db.add(commodity)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Commodity already exists") from exc
    db.refresh(commodity)
    return commodity


def update_commodity(db: Session, commodity: Commodity, payload: CommodityUpdate) -> Commodity:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Commodity name cannot be null")
    if "is_active" in changes and changes["is_active"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Commodity active status cannot be null")
    if "name" in changes:
        _ensure_unique_name(db, changes["name"], exclude_id=commodity.id)

    for field, value in changes.items():
        setattr(commodity, field, value)

    db.commit()
    db.refresh(commodity)
    return commodity


def delete_commodity(db: Session, commodity: Commodity) -> None:
    db.delete(commodity)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Commodity cannot be deleted because it is referenced by existing records",
        ) from exc
