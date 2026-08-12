from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import (
    Movement,
    PriceUpdateAdminResponse,
    PriceUpdateCreate,
    PriceUpdatePublicResponse,
    PriceUpdateUpdate,
    TimeOfDay,
)
from app.services.price_update_service import (
    approve_price_update,
    create_price_update,
    delete_price_update,
    get_approved_price_update,
    get_price_update_for_admin,
    list_latest_approved_price_updates,
    list_market_comparison,
    list_price_history,
    mark_price_update_outdated,
    reject_price_update,
    update_price_update,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/price-updates", tags=["price-updates"])


@router.get("", response_model=list[PriceUpdatePublicResponse])
def get_latest_price_updates(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PriceUpdate]:
    return list_latest_approved_price_updates(
        db,
        commodity_search=commodity,
        market_search=market,
        selected_date=selected_date,
        movement=movement,
    )


@router.get("/history", response_model=list[PriceUpdatePublicResponse])
def get_price_history(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    time_of_day: TimeOfDay | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PriceUpdate]:
    return list_price_history(
        db,
        commodity_search=commodity,
        market_search=market,
        selected_date=selected_date,
        movement=movement,
        time_of_day=time_of_day,
    )


@router.get("/comparison", response_model=list[PriceUpdatePublicResponse])
def get_market_comparison(
    commodity: str = Query(min_length=1, max_length=100),
    selected_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> list[PriceUpdate]:
    return list_market_comparison(
        db,
        commodity_search=commodity,
        selected_date=selected_date,
    )


@router.get("/{price_update_id}", response_model=PriceUpdatePublicResponse)
def get_price_update(price_update_id: int, db: Session = Depends(get_db)) -> PriceUpdate:
    return get_approved_price_update(db, price_update_id)


@router.post("", response_model=PriceUpdateAdminResponse, status_code=status.HTTP_201_CREATED)
def add_price_update(
    payload: PriceUpdateCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    return create_price_update(db, payload, current_admin)


@router.patch("/{price_update_id}", response_model=PriceUpdateAdminResponse)
def edit_price_update(
    price_update_id: int,
    payload: PriceUpdateUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    return update_price_update(db, get_price_update_for_admin(db, price_update_id), payload)


@router.patch("/{price_update_id}/approve", response_model=PriceUpdateAdminResponse)
def approve_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    return approve_price_update(db, get_price_update_for_admin(db, price_update_id), current_admin)


@router.patch("/{price_update_id}/reject", response_model=PriceUpdateAdminResponse)
def reject_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    return reject_price_update(db, get_price_update_for_admin(db, price_update_id))


@router.patch("/{price_update_id}/mark-outdated", response_model=PriceUpdateAdminResponse)
def mark_outdated(
    price_update_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    return mark_price_update_outdated(db, get_price_update_for_admin(db, price_update_id))


@router.delete("/{price_update_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_price_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_price_update(db, get_price_update_for_admin(db, price_update_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
