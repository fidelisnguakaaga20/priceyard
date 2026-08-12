from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market import Market
from app.models.user import User
from app.schemas.market_schema import MarketCreate, MarketResponse, MarketUpdate
from app.services.market_service import create_market, delete_market, get_market, list_markets, update_market
from app.utils.permissions import require_roles

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=list[MarketResponse])
def get_markets(db: Session = Depends(get_db)) -> list[Market]:
    return list_markets(db)


@router.get("/{market_id}", response_model=MarketResponse)
def get_market_by_id(market_id: int, db: Session = Depends(get_db)) -> Market:
    return get_market(db, market_id)


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
def add_market(
    payload: MarketCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Market:
    return create_market(db, payload)


@router.patch("/{market_id}", response_model=MarketResponse)
def edit_market(
    market_id: int,
    payload: MarketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Market:
    return update_market(db, get_market(db, market_id), payload)


@router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_market(
    market_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_market(db, get_market(db, market_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
