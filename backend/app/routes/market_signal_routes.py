from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market_signal import MarketSignal
from app.models.user import User
from app.schemas.market_signal_schema import MarketSignalCreate, MarketSignalResponse, MarketSignalUpdate
from app.services.market_signal_service import (
    create_market_signal,
    delete_market_signal,
    get_market_signal,
    list_market_signals,
    update_market_signal,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/market-signals", tags=["market-signals"])


@router.get("", response_model=list[MarketSignalResponse])
def get_signals(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[MarketSignal]:
    return list_market_signals(db)


@router.get("/{signal_id}", response_model=MarketSignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MarketSignal:
    return get_market_signal(db, signal_id)


@router.post("", response_model=MarketSignalResponse, status_code=status.HTTP_201_CREATED)
def add_signal(
    payload: MarketSignalCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> MarketSignal:
    return create_market_signal(db, payload, current_admin)


@router.patch("/{signal_id}", response_model=MarketSignalResponse)
def edit_signal(
    signal_id: int,
    payload: MarketSignalUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> MarketSignal:
    return update_market_signal(db, get_market_signal(db, signal_id), payload)


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_market_signal(db, get_market_signal(db, signal_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
