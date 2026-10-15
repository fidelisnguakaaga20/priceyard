from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.price_flag import PriceFlag
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_flag_schema import FlaggedPriceSummary


def flag_price_update(db: Session, user: User, price_update: PriceUpdate, reason: str | None) -> bool:
    """Record that a user flagged this price as looking wrong. Returns False instead
    of erroring if they already flagged it -- the unique constraint is there to stop
    duplicate rows, not to punish someone for tapping the button twice."""
    flag = PriceFlag(price_update_id=price_update.id, user_id=user.id, reason=reason)
    db.add(flag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    return True


def list_flagged_price_updates(db: Session, *, page: int = 1, page_size: int = 100) -> list[FlaggedPriceSummary]:
    if page < 1 or not 1 <= page_size <= 1000:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid pagination")
    statement = (
        select(
            PriceFlag.price_update_id,
            Commodity.name.label("commodity_name"),
            Market.name.label("market_name"),
            func.count(PriceFlag.id).label("flag_count"),
            func.max(PriceFlag.created_at).label("latest_flag_at"),
        )
        .join(PriceUpdate, PriceFlag.price_update_id == PriceUpdate.id)
        .join(Commodity, PriceUpdate.commodity_id == Commodity.id)
        .join(Market, PriceUpdate.market_id == Market.id)
        .where(PriceFlag.resolved.is_(False))
        .group_by(PriceFlag.price_update_id, Commodity.name, Market.name)
        .order_by(func.max(PriceFlag.created_at).desc(), PriceFlag.price_update_id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    return [FlaggedPriceSummary(**row) for row in db.execute(statement).mappings().all()]


def resolve_flags(db: Session, price_update_id: int) -> int:
    count = (
        db.query(PriceFlag)
        .filter(PriceFlag.price_update_id == price_update_id, PriceFlag.resolved.is_(False))
        .update({"resolved": True})
    )
    db.commit()
    return count
