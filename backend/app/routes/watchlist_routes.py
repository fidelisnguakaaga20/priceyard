from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist_schema import WatchlistCreate, WatchlistResponse
from app.services.watchlist_service import (
    create_watchlist_item,
    delete_watchlist_item,
    list_watchlist_items,
)
from app.utils.permissions import get_current_user

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def save_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Watchlist:
    return create_watchlist_item(db, current_user.id, payload)


@router.get("", response_model=list[WatchlistResponse])
def get_own_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Watchlist]:
    return list_watchlist_items(db, current_user.id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    delete_watchlist_item(db, current_user.id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
