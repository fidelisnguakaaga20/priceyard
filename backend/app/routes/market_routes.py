from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market import Market
from app.models.user import User
from app.schemas.market_schema import MarketCreate, MarketResponse, MarketUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.services.market_service import create_market, delete_market, get_market, update_market
from app.utils.permissions import require_roles

router = APIRouter(prefix="/markets", tags=["markets"])


def _save_catalog_audit(db: Session, admin: User, action: str, record_id: int, *, old_value: dict | None = None, new_value: dict | None = None) -> None:
    try:
        create_audit_log(db, actor=admin, action=action, table_name="markets", record_id=record_id,
                         old_value=old_value, new_value=new_value, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[MarketResponse])
def get_markets(db: Session = Depends(get_db)) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Market, MarketResponse,
        order=(("name", False), ("id", False)), where=(Market.is_active.is_(True),)), private=False)


@router.get("/admin/all", response_model=list[MarketResponse])
def get_all_markets_for_admin(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Market, MarketResponse,
        order=(("name", False), ("id", False))))


@router.get("/admin/page", response_model=AdminRecordPage[MarketResponse])
def get_markets_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> AdminRecordPage[MarketResponse]:
    return admin_record_page(db, Market, MarketResponse, offset=offset, order=(("name", False), ("id", False)))


@router.get("/{market_id}", response_model=MarketResponse)
def get_market_by_id(market_id: int, db: Session = Depends(get_db)) -> Market:
    item = get_market(db, market_id)
    if not item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active market not found")
    return item


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
def add_market(
    payload: MarketCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Market:
    item = create_market(db, payload, commit=False)
    _save_catalog_audit(db, admin, "market.create", item.id, new_value=snapshot_model(item))
    return item


@router.patch("/{market_id}", response_model=MarketResponse)
def edit_market(
    market_id: int,
    payload: MarketUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Market:
    item = get_market(db, market_id, lock=True)
    old_value = snapshot_model(item)
    item = update_market(db, item, payload, commit=False)
    _save_catalog_audit(db, admin, "market.edit", item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_market(
    market_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_market(db, market_id, lock=True)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_market(db, item, commit=False)
    _save_catalog_audit(db, admin, "market.delete", record_id, old_value=old_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
