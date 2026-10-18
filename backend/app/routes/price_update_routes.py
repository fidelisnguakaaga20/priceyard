from datetime import date
import logging

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_flag_schema import FlaggedPriceSummary, PriceFlagCreate
from app.schemas.price_update_schema import (
    Movement,
    PriceUpdateAdminResponse,
    PriceUpdateCreate,
    PriceHistoryPair,
    PriceUpdatePublicResponse,
    PriceUpdateUpdate,
    SubmissionStats,
    TimeOfDay,
)
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.services.price_flag_service import flag_price_update, flagged_price_page, stream_flagged_prices, resolve_flags
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.services.price_update_service import (
    approve_price_update,
    create_price_update,
    delete_price_update,
    get_approved_price_update,
    get_price_update_for_admin,
    get_submission_stats,
    list_latest_approved_price_updates,
    list_market_comparison,
    list_price_history,
    list_price_history_pairs,
    mark_price_update_outdated,
    reject_price_update,
    update_price_update,
)
from app.services.watchlist_alert_service import notify_watchlist_subscribers
from app.utils.permissions import bearer_scheme, get_current_user, require_full_access, require_roles

router = APIRouter(prefix="/price-updates", tags=["price-updates"])
logger = logging.getLogger(__name__)


def _save_audited_price(db: Session, item: PriceUpdate, actor: User, action: str, old_value: dict | None = None, *, deleted: bool = False) -> None:
    try:
        create_audit_log(
            db, actor=actor, action=action, table_name="price_updates",
            record_id=item.id, old_value=old_value, new_value=None if deleted else snapshot_model(item), commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _notify_saved_price(db: Session, item: PriceUpdate) -> None:
    try:
        notify_watchlist_subscribers(db, item)
    except Exception:
        # The business transaction already committed. A best-effort alert/query
        # failure must not make a successful save look like a failed action.
        logger.warning("Price change saved; watchlist notification failed")


def _require_history_access(
    db: Session,
    items: list[PriceUpdate],
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    if not items:
        return
    # Apply the same public-current rule to alternate date/comparison/ID URLs.
    # Keep the previous-price summary of a current record public as before.
    public_ids = {item.id for item in list_latest_approved_price_updates(db)}
    if any(item.id not in public_ids for item in items):
        require_full_access(get_current_user(credentials, db), db)


@router.get("", response_model=list[PriceUpdatePublicResponse])
def get_latest_price_updates(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    commodity_id: int | None = Query(default=None, gt=0, le=2_147_483_647),
    market_id: int | None = Query(default=None, gt=0, le=2_147_483_647),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> list[PriceUpdate]:
    items = list_latest_approved_price_updates(
        db,
        commodity_search=commodity,
        market_search=market,
        commodity_id=commodity_id, market_id=market_id,
        selected_date=selected_date,
        movement=movement,
    )
    if selected_date is not None:
        _require_history_access(db, items, credentials)
    return items


@router.get("/history", response_model=list[PriceUpdatePublicResponse])
def get_price_history(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    commodity_id: int | None = Query(default=None, gt=0, le=2_147_483_647),
    market_id: int | None = Query(default=None, gt=0, le=2_147_483_647),
    selected_date: date | None = Query(default=None, alias="date"),
    movement: Movement | None = Query(default=None),
    time_of_day: TimeOfDay | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_full_access),
) -> list[PriceUpdate]:
    return list_price_history(
        db,
        commodity_search=commodity,
        market_search=market,
        commodity_id=commodity_id, market_id=market_id,
        selected_date=selected_date,
        movement=movement,
        time_of_day=time_of_day,
    )


@router.get("/history/pairs", response_model=list[PriceHistoryPair])
def get_price_history_pairs(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_full_access),
) -> list[dict[str, dict[str, str]]]:
    return list_price_history_pairs(db)


@router.get("/comparison", response_model=list[PriceUpdatePublicResponse])
def get_market_comparison(
    commodity: str = Query(min_length=1, max_length=100),
    selected_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> list[PriceUpdate]:
    items = list_market_comparison(
        db,
        commodity_search=commodity,
        selected_date=selected_date,
    )
    if selected_date is not None:
        _require_history_access(db, items, credentials)
    return items


@router.get("/admin/history", response_model=list[PriceUpdateAdminResponse])
def get_admin_price_history(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), PriceUpdate, PriceUpdateAdminResponse,
        order=(("update_date_time", True), ("id", True)), related=("commodity", "market")))


@router.get("/admin/history/page", response_model=AdminRecordPage[PriceUpdateAdminResponse])
def get_admin_price_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> AdminRecordPage[PriceUpdateAdminResponse]:
    return admin_record_page(db, PriceUpdate, PriceUpdateAdminResponse, offset=offset,
        order=(("update_date_time", True), ("id", True)), related=("commodity", "market"))


@router.get("/admin/latest", response_model=PriceUpdateAdminResponse | None)
def get_admin_latest_pair(
    commodity_id: int = Query(gt=0),
    market_id: int = Query(gt=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> PriceUpdate | None:
    # Match the original all-history prefill, including pending/rejected records.
    return db.scalar(select(PriceUpdate).where(PriceUpdate.commodity_id == commodity_id,
        PriceUpdate.market_id == market_id).options(joinedload(PriceUpdate.commodity), joinedload(PriceUpdate.market))
        .order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc()).limit(1))


@router.get("/admin/flagged", response_model=list[FlaggedPriceSummary])
def get_flagged_price_updates(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Response:
    return AdminJSONResponse(stream_flagged_prices(db.get_bind()))


@router.get("/admin/flagged/page", response_model=AdminRecordPage[FlaggedPriceSummary])
def get_flagged_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> AdminRecordPage[FlaggedPriceSummary]:
    return flagged_price_page(db, offset=offset)


@router.get("/my-stats", response_model=SubmissionStats)
def get_my_submission_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    return get_submission_stats(db, current_user.id)


@router.get("/{price_update_id}", response_model=PriceUpdatePublicResponse)
def get_price_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> PriceUpdate:
    item = get_approved_price_update(db, price_update_id)
    _require_history_access(db, [item], credentials)
    return item


@router.post("", response_model=PriceUpdateAdminResponse, status_code=status.HTTP_201_CREATED)
def add_price_update(
    payload: PriceUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "reporter")),
) -> PriceUpdate:
    item = create_price_update(db, payload, current_user, commit=False)
    _save_audited_price(db, item, current_user, "price_update.create")
    return item


@router.patch("/{price_update_id}", response_model=PriceUpdateAdminResponse)
def edit_price_update(
    price_update_id: int,
    payload: PriceUpdateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id, lock=True)
    old_value = snapshot_model(item)
    price_fields_touched = bool({"price_low", "price_high", "average_price"} & payload.model_dump(exclude_unset=True).keys())
    item = update_price_update(db, item, payload, commit=False)
    _save_audited_price(db, item, current_admin, "price_update.edit", old_value)
    if price_fields_touched and item.status == "approved":
        _notify_saved_price(db, item)
    return item


@router.patch("/{price_update_id}/approve", response_model=PriceUpdateAdminResponse)
def approve_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id, lock=True)
    old_value = snapshot_model(item)
    item = approve_price_update(db, item, current_admin, commit=False)
    _save_audited_price(db, item, current_admin, "price_update.approve", old_value)
    _notify_saved_price(db, item)
    return item


@router.patch("/{price_update_id}/reject", response_model=PriceUpdateAdminResponse)
def reject_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id, lock=True)
    old_value = snapshot_model(item)
    item = reject_price_update(db, item, commit=False)
    _save_audited_price(db, item, current_admin, "price_update.reject", old_value)
    return item


@router.post("/{price_update_id}/flag", status_code=status.HTTP_204_NO_CONTENT)
def flag_price(
    price_update_id: int,
    payload: PriceFlagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = get_approved_price_update(db, price_update_id)
    flag_price_update(db, current_user, item, payload.reason)


@router.post("/{price_update_id}/flags/resolve", status_code=status.HTTP_204_NO_CONTENT)
def resolve_price_flags(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> None:
    get_price_update_for_admin(db, price_update_id, lock=True)
    try:
        count = resolve_flags(db, price_update_id, commit=False)
        if count:
            create_audit_log(db, actor=current_admin, action="price_update.flags_resolve", table_name="price_updates",
                             record_id=price_update_id, old_value={"unresolved_count": count},
                             new_value={"unresolved_count": 0, "resolved_count": count}, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.patch("/{price_update_id}/mark-outdated", response_model=PriceUpdateAdminResponse)
def mark_outdated(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> PriceUpdate:
    item = get_price_update_for_admin(db, price_update_id, lock=True)
    old_value = snapshot_model(item)
    item = mark_price_update_outdated(db, item, commit=False)
    _save_audited_price(db, item, current_admin, "price_update.mark_outdated", old_value)
    return item


@router.delete("/{price_update_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_price_update(
    price_update_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_price_update_for_admin(db, price_update_id, lock=True)
    old_value = snapshot_model(item)
    delete_price_update(db, item, commit=False)
    _save_audited_price(db, item, current_admin, "price_update.delete", old_value, deleted=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
