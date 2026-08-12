from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sell_watch_window import SellWatchWindow
from app.models.user import User
from app.schemas.sell_watch_window_schema import (
    SellWatchWindowCreate,
    SellWatchWindowResponse,
    SellWatchWindowUpdate,
)
from app.services.sell_watch_window_service import (
    create_sell_watch_window,
    get_sell_watch_window,
    list_sell_watch_windows,
    update_sell_watch_window,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/sell-watch-windows", tags=["sell-watch-windows"])


@router.get("", response_model=list[SellWatchWindowResponse])
def get_windows(
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> list[SellWatchWindow]:
    return list_sell_watch_windows(db)


@router.get("/{window_id}", response_model=SellWatchWindowResponse)
def get_window(
    window_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> SellWatchWindow:
    return get_sell_watch_window(db, window_id)


@router.post("", response_model=SellWatchWindowResponse, status_code=status.HTTP_201_CREATED)
def add_window(
    payload: SellWatchWindowCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> SellWatchWindow:
    return create_sell_watch_window(db, payload, current_admin)


@router.patch("/{window_id}", response_model=SellWatchWindowResponse)
def edit_window(
    window_id: int,
    payload: SellWatchWindowUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> SellWatchWindow:
    return update_sell_watch_window(db, get_sell_watch_window(db, window_id), payload)
