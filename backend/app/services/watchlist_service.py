from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.watchlist import Watchlist
from app.schemas.watchlist_schema import WatchlistCreate


def _validate_commodity(db: Session, commodity_id: int | None) -> None:
    if commodity_id is None:
        return
    commodity = db.get(Commodity, commodity_id)
    if commodity is None or not commodity.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")


def _validate_market(db: Session, market_id: int | None) -> None:
    if market_id is None:
        return
    market = db.get(Market, market_id)
    if market is None or not market.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")


def _find_duplicate(
    db: Session,
    *,
    user_id: int,
    commodity_id: int | None,
    market_id: int | None,
) -> Watchlist | None:
    statement = select(Watchlist).where(Watchlist.user_id == user_id)
    if commodity_id is None:
        statement = statement.where(Watchlist.commodity_id.is_(None))
    else:
        statement = statement.where(Watchlist.commodity_id == commodity_id)
    if market_id is None:
        statement = statement.where(Watchlist.market_id.is_(None))
    else:
        statement = statement.where(Watchlist.market_id == market_id)
    return db.scalar(statement)


def create_watchlist_item(db: Session, user_id: int, payload: WatchlistCreate) -> Watchlist:
    _validate_commodity(db, payload.commodity_id)
    _validate_market(db, payload.market_id)

    duplicate = _find_duplicate(
        db,
        user_id=user_id,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Watchlist item already exists",
        )

    item = Watchlist(
        user_id=user_id,
        commodity_id=payload.commodity_id,
        market_id=payload.market_id,
        target_price=payload.target_price,
        target_direction=payload.target_direction,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_watchlist_items(db: Session, user_id: int) -> list[Watchlist]:
    return list(
        db.scalars(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .order_by(Watchlist.created_at.desc(), Watchlist.id.desc())
        ).all()
    )


def delete_watchlist_item(db: Session, user_id: int, item_id: int) -> None:
    item = db.scalar(
        select(Watchlist).where(
            Watchlist.id == item_id,
            Watchlist.user_id == user_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found")
    db.delete(item)
    db.commit()
