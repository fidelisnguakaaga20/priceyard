from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.sell_watch_window import SellWatchWindow
from app.models.user import User
from app.schemas.sell_watch_window_schema import SellWatchWindowCreate, SellWatchWindowUpdate


def _validate_active_market_scope(db: Session, *, commodity_id: int, market_id: int) -> None:
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


def create_sell_watch_window(
    db: Session, payload: SellWatchWindowCreate, admin: User
) -> SellWatchWindow:
    _validate_active_market_scope(db, commodity_id=payload.commodity_id, market_id=payload.market_id)
    window = SellWatchWindow(**payload.model_dump(), created_by=admin.id)
    db.add(window)
    db.commit()
    db.refresh(window)
    return window


def get_sell_watch_window(db: Session, window_id: int) -> SellWatchWindow:
    window = db.get(SellWatchWindow, window_id)
    if window is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sell-watch window not found")
    return window


def list_sell_watch_windows(db: Session) -> list[SellWatchWindow]:
    return list(
        db.scalars(
            select(SellWatchWindow).order_by(SellWatchWindow.created_at.desc(), SellWatchWindow.id.desc())
        ).all()
    )


def update_sell_watch_window(
    db: Session, window: SellWatchWindow, payload: SellWatchWindowUpdate
) -> SellWatchWindow:
    changes = payload.model_dump(exclude_unset=True)
    commodity_id = int(changes.get("commodity_id", window.commodity_id))
    market_id = int(changes.get("market_id", window.market_id))
    _validate_active_market_scope(db, commodity_id=commodity_id, market_id=market_id)

    for field, value in changes.items():
        setattr(window, field, value)
    db.commit()
    db.refresh(window)
    return window
