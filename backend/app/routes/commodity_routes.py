from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commodity import Commodity
from app.models.user import User
from app.schemas.commodity_schema import CommodityCreate, CommodityResponse, CommodityUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.commodity_service import (
    create_commodity,
    delete_commodity,
    get_commodity,
    list_commodities,
    update_commodity,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/commodities", tags=["commodities"])


@router.get("", response_model=list[CommodityResponse])
def get_commodities(db: Session = Depends(get_db)) -> list[Commodity]:
    return list_commodities(db)


@router.get("/{commodity_id}", response_model=CommodityResponse)
def get_commodity_by_id(commodity_id: int, db: Session = Depends(get_db)) -> Commodity:
    return get_commodity(db, commodity_id)


@router.post("", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
def add_commodity(
    payload: CommodityCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Commodity:
    item = create_commodity(db, payload)
    create_audit_log(
        db, actor=admin, action="commodity.create", table_name="commodities",
        record_id=item.id, new_value=snapshot_model(item),
    )
    return item


@router.patch("/{commodity_id}", response_model=CommodityResponse)
def edit_commodity(
    commodity_id: int,
    payload: CommodityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Commodity:
    item = get_commodity(db, commodity_id)
    old_value = snapshot_model(item)
    item = update_commodity(db, item, payload)
    create_audit_log(
        db, actor=admin, action="commodity.edit", table_name="commodities",
        record_id=item.id, old_value=old_value, new_value=snapshot_model(item),
    )
    return item


@router.delete("/{commodity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_commodity(
    commodity_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_commodity(db, commodity_id)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_commodity(db, item)
    create_audit_log(
        db, actor=admin, action="commodity.delete", table_name="commodities",
        record_id=record_id, old_value=old_value,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
