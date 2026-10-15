"""Bounded, owner-scoped catalogs with active-reference consumer visibility."""

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate


def _statement(model, *, commodity_id=None, market_id=None, active_only=True):
    statement = select(model)
    if hasattr(model, "is_archived"):
        statement = statement.where(model.is_archived.is_(False))
    if commodity_id is not None:
        statement = statement.where(model.commodity_id == commodity_id)
    if market_id is not None:
        statement = statement.where(model.market_id == market_id)
    if active_only:
        statement = statement.join(Commodity, model.commodity_id == Commodity.id).join(Market, model.market_id == Market.id)
        statement = statement.where(Commodity.is_active.is_(True), Market.is_active.is_(True))
        if hasattr(model, "price_update_id"):
            statement = statement.outerjoin(PriceUpdate, model.price_update_id == PriceUpdate.id)
            statement = statement.where(or_(model.price_update_id.is_(None), PriceUpdate.status == "approved"))
    return statement


def list_intelligence(db: Session, model, *, commodity_id=None, market_id=None, active_only=True,
                      page=1, page_size=1000):
    if page < 1 or not 1 <= page_size <= 1000:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    statement = _statement(model, commodity_id=commodity_id, market_id=market_id, active_only=active_only)
    return list(db.scalars(statement.order_by(model.created_at.desc(), model.id.desc())
                           .offset((page - 1) * page_size).limit(page_size)).all())


def get_visible_intelligence(db: Session, model, item_id: int, *, active_only=True):
    item = db.scalar(_statement(model, active_only=active_only).where(model.id == item_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Eligible intelligence record not found")
    return item


def reject_null_required(changes: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        if field in changes and changes[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")
