from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import save_audited_resource, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.models.market_signal import MarketSignal
from app.models.user import User
from app.schemas.market_signal_schema import MarketSignalCreate, MarketSignalResponse, MarketSignalUpdate
from app.services.market_signal_service import (
    create_market_signal,
    delete_market_signal,
    get_market_signal,
    update_market_signal,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/market-signals", tags=["market-signals"])


@router.get("", response_model=list[MarketSignalResponse])
def get_signals(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    commodity_id: Annotated[int | None, Query(gt=0)] = None,
) -> Response:
    conditions = (MarketSignal.commodity_id == commodity_id,) if commodity_id is not None else ()
    return AdminJSONResponse(stream_admin_records(db.get_bind(), MarketSignal, MarketSignalResponse,
        order=(("created_at", True), ("id", True)), where=conditions))


@router.get("/admin/page", response_model=AdminRecordPage[MarketSignalResponse])
def get_admin_signals_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AdminRecordPage[MarketSignalResponse]:
    return admin_record_page(db, MarketSignal, MarketSignalResponse, offset=offset,
        order=(("created_at", True), ("id", True)))


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
    item = create_market_signal(db, payload, current_admin, commit=False)
    save_audited_resource(db, item, current_admin, "market_signal.create")
    return item


@router.patch("/{signal_id}", response_model=MarketSignalResponse)
def edit_signal(
    signal_id: int,
    payload: MarketSignalUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> MarketSignal:
    item = get_market_signal(db, signal_id, lock=True)
    old_value = snapshot_model(item)
    item = update_market_signal(db, item, payload, commit=False)
    save_audited_resource(db, item, current_admin, "market_signal.edit", old_value=old_value)
    return item


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_market_signal(db, signal_id, lock=True)
    old_value = snapshot_model(item)
    delete_market_signal(db, item, commit=False)
    save_audited_resource(db, item, current_admin, "market_signal.delete", old_value=old_value, deleted=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
