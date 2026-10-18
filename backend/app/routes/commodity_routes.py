from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commodity import Commodity
from app.models.user import User
from app.schemas.commodity_schema import CommodityCreate, CommodityResponse, CommodityUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.services.commodity_service import (
    create_commodity,
    delete_commodity,
    get_commodity,
    update_commodity,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/commodities", tags=["commodities"])


def _save_catalog_audit(db: Session, admin: User, action: str, record_id: int, *, old_value: dict | None = None, new_value: dict | None = None) -> None:
    try:
        create_audit_log(db, actor=admin, action=action, table_name="commodities", record_id=record_id,
                         old_value=old_value, new_value=new_value, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[CommodityResponse])
def get_commodities(db: Session = Depends(get_db)) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Commodity, CommodityResponse,
        order=(("name", False), ("id", False)), where=(Commodity.is_active.is_(True),)), private=False)


@router.get("/admin/all", response_model=list[CommodityResponse])
def get_all_commodities_for_admin(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Commodity, CommodityResponse,
        order=(("name", False), ("id", False))))


@router.get("/admin/page", response_model=AdminRecordPage[CommodityResponse])
def get_commodities_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> AdminRecordPage[CommodityResponse]:
    return admin_record_page(db, Commodity, CommodityResponse, offset=offset, order=(("name", False), ("id", False)))


@router.get("/{commodity_id}", response_model=CommodityResponse)
def get_commodity_by_id(commodity_id: int, db: Session = Depends(get_db)) -> Commodity:
    item = get_commodity(db, commodity_id)
    if not item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active commodity not found")
    return item


@router.post("", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
def add_commodity(
    payload: CommodityCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Commodity:
    item = create_commodity(db, payload, commit=False)
    _save_catalog_audit(db, admin, "commodity.create", item.id, new_value=snapshot_model(item))
    return item


@router.patch("/{commodity_id}", response_model=CommodityResponse)
def edit_commodity(
    commodity_id: int,
    payload: CommodityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Commodity:
    item = get_commodity(db, commodity_id, lock=True)
    old_value = snapshot_model(item)
    item = update_commodity(db, item, payload, commit=False)
    _save_catalog_audit(db, admin, "commodity.edit", item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.delete("/{commodity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_commodity(
    commodity_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_commodity(db, commodity_id, lock=True)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_commodity(db, item, commit=False)
    _save_catalog_audit(db, admin, "commodity.delete", record_id, old_value=old_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
