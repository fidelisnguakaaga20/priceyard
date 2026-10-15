from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_flag_schema import FlaggedPriceSummary, PriceFlagCreate
from app.schemas.price_update_schema import (
    Movement,
    PriceUpdateAdminResponse,
    PriceUpdateCreate,
    PriceUpdatePublicResponse,
    PriceUpdateSummaryResponse,
    PriceUpdateUpdate,
    SubmissionStats,
    TimeOfDay,
)
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.price_flag_service import flag_price_update, list_flagged_price_updates, resolve_flags
from app.services.price_update_service import (
    approve_price_update,
    create_price_update,
    delete_price_update,
    get_approved_price_update,
    get_price_update_for_admin,
    get_submission_stats,
    list_latest_approved_price_updates,
    list_admin_price_updates,
    list_market_comparison,
    list_price_history,
    mark_price_update_outdated,
    reject_price_update,
    update_price_update,
)
from app.services.watchlist_alert_service import notify_watchlist_subscribers
from app.utils.permissions import get_current_user, optional_current_user, require_full_access, require_roles, user_has_full_access

router = APIRouter(prefix="/price-updates", tags=["price-updates"])


def _price_view(item: PriceUpdate, db: Session, user: User | None, *, full_access: bool | None = None):
    if full_access is None:
        full_access = user_has_full_access(db, user)
    schema = PriceUpdatePublicResponse if full_access else PriceUpdateSummaryResponse
    return schema.model_validate(item)


def _price_views(items: list[PriceUpdate], db: Session, user: User | None):
    full_access = user_has_full_access(db, user)
    return [_price_view(item, db, user, full_access=full_access) for item in items]


def _authorize_date(selected_date: date | None, db: Session, user: User | None) -> None:
    if selected_date is not None and not user_has_full_access(db, user):
        raise HTTPException(status_code=403, detail="Historical date searches require full subscription or active trial")


@router.get("", response_model=list[PriceUpdatePublicResponse | PriceUpdateSummaryResponse])
def get_latest_price_updates(
    response: Response,
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> list[PriceUpdatePublicResponse | PriceUpdateSummaryResponse]:
    _authorize_date(selected_date, db, current_user)
    response.headers["Vary"] = "Authorization"
    if current_user is None and selected_date is None:
        response.headers["X-PriceYard-Public"] = "true"
        response.headers["Cache-Control"] = "public, max-age=30"
    else:
        response.headers["Cache-Control"] = "private, no-store"
    items = list_latest_approved_price_updates(
        db,
        commodity_search=commodity,
        market_search=market,
        selected_date=selected_date,
        movement=movement,
        commodity_id=commodity_id,
        market_id=market_id,
        page=page,
        page_size=page_size,
    )
    return _price_views(items, db, current_user)


@router.get("/history", response_model=list[PriceUpdatePublicResponse])
def get_price_history(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    time_of_day: TimeOfDay | None = Query(default=None),
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_full_access),
) -> list[PriceUpdate]:
    return list_price_history(
        db,
        commodity_search=commodity,
        market_search=market,
        selected_date=selected_date,
        movement=movement,
        time_of_day=time_of_day,
        commodity_id=commodity_id,
        market_id=market_id,
        page=page,
        page_size=page_size,
    )


@router.get("/comparison", response_model=list[PriceUpdatePublicResponse | PriceUpdateSummaryResponse])
def get_market_comparison(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    commodity_id: int | None = Query(default=None, gt=0),
    selected_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> list[PriceUpdatePublicResponse | PriceUpdateSummaryResponse]:
    if commodity is None and commodity_id is None:
        raise HTTPException(status_code=422, detail="commodity or commodity_id is required")
    _authorize_date(selected_date, db, current_user)
    items = list_market_comparison(
        db,
        commodity_search=commodity,
        selected_date=selected_date,
        commodity_id=commodity_id,
    )
    return _price_views(items, db, current_user)


@router.get("/admin/history", response_model=list[PriceUpdateAdminResponse])
def get_admin_price_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> list[PriceUpdate]:
    return list_admin_price_updates(db, page=page, page_size=page_size)


@router.get("/admin/flagged", response_model=list[FlaggedPriceSummary])
def get_flagged_price_updates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> list[FlaggedPriceSummary]:
    return list_flagged_price_updates(db, page=page, page_size=page_size)


@router.get("/my-stats", response_model=SubmissionStats)
def get_my_submission_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    return get_submission_stats(db, current_user.id)


@router.get("/{price_update_id}", response_model=PriceUpdatePublicResponse | PriceUpdateSummaryResponse)
def get_price_update(price_update_id: int, db: Session = Depends(get_db),
                     current_user: User | None = Depends(optional_current_user)):
    full_access = user_has_full_access(db, current_user)
    item = get_approved_price_update(db, price_update_id, current_only=not full_access)
    return _price_view(item, db, current_user, full_access=full_access)


@router.post("", response_model=PriceUpdateAdminResponse, status_code=status.HTTP_201_CREATED)
def add_price_update(
    payload: PriceUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "reporter")),
) -> PriceUpdate:
    item = create_price_update(db, payload, current_user)
    create_audit_log(
        db, actor=current_user, action="price_update.create", table_name="price_updates",
        record_id=item.id, new_value=snapshot_model(item),
    )
    return item


@router.patch("/{price_update_id}", response_model=PriceUpdateAdminResponse)
def edit_price_update(
    price_update_id: int,
    payload: PriceUpdateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id)
    old_value = snapshot_model(item)
    price_fields_touched = bool({"price_low", "price_high", "average_price"} & payload.model_dump(exclude_unset=True).keys())
    item = update_price_update(db, item, payload, actor=current_admin)
    create_audit_log(
        db, actor=current_admin, action="price_update.edit", table_name="price_updates",
        record_id=item.id, old_value=old_value, new_value=snapshot_model(item),
    )
    if price_fields_touched and item.status == "approved":
        notify_watchlist_subscribers(db, item)
    return item


@router.patch("/{price_update_id}/approve", response_model=PriceUpdateAdminResponse)
def approve_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id)
    old_value = snapshot_model(item)
    item = approve_price_update(db, item, current_admin)
    create_audit_log(
        db, actor=current_admin, action="price_update.approve", table_name="price_updates",
        record_id=item.id, old_value=old_value, new_value=snapshot_model(item),
    )
    notify_watchlist_subscribers(db, item)
    return item


@router.patch("/{price_update_id}/reject", response_model=PriceUpdateAdminResponse)
def reject_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id)
    old_value = snapshot_model(item)
    item = reject_price_update(db, item, actor=current_admin)
    create_audit_log(
        db, actor=current_admin, action="price_update.reject", table_name="price_updates",
        record_id=item.id, old_value=old_value, new_value=snapshot_model(item),
    )
    return item


@router.post("/{price_update_id}/flag", status_code=status.HTTP_204_NO_CONTENT)
def flag_price(
    price_update_id: int,
    payload: PriceFlagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = get_approved_price_update(db, price_update_id, current_only=not user_has_full_access(db, current_user))
    flag_price_update(db, current_user, item, payload.reason)


@router.post("/{price_update_id}/flags/resolve", status_code=status.HTTP_204_NO_CONTENT)
def resolve_price_flags(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> None:
    get_price_update_for_admin(db, price_update_id)
    resolve_flags(db, price_update_id)


@router.patch("/{price_update_id}/mark-outdated", response_model=PriceUpdateAdminResponse)
def mark_outdated(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id)
    old_value = snapshot_model(item)
    item = mark_price_update_outdated(db, item, actor=current_admin)
    create_audit_log(
        db, actor=current_admin, action="price_update.mark_outdated", table_name="price_updates",
        record_id=item.id, old_value=old_value, new_value=snapshot_model(item),
    )
    return item


@router.delete("/{price_update_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_price_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_price_update_for_admin(db, price_update_id)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_price_update(db, item, actor=current_admin)
    create_audit_log(
        db, actor=current_admin, action="price_update.withdraw", table_name="price_updates",
        record_id=record_id, old_value=old_value,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
