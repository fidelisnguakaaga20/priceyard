from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import save_audited_resource, snapshot_model
from app.models.buying_zone import BuyingZone
from app.models.user import User
from app.schemas.buying_zone_schema import BuyingZoneCreate, BuyingZoneResponse, BuyingZoneUpdate
from app.services.buying_zone_service import (
    create_buying_zone,
    get_buying_zone,
    list_buying_zones,
    update_buying_zone,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/buying-zones", tags=["buying-zones"])


@router.get("", response_model=list[BuyingZoneResponse])
def get_zones(
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
    commodity_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[BuyingZone]:
    return list_buying_zones(db, commodity_id=commodity_id)


@router.get("/{zone_id}", response_model=BuyingZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> BuyingZone:
    return get_buying_zone(db, zone_id)


@router.post("", response_model=BuyingZoneResponse, status_code=status.HTTP_201_CREATED)
def add_zone(
    payload: BuyingZoneCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> BuyingZone:
    item = create_buying_zone(db, payload, current_admin, commit=False)
    save_audited_resource(db, item, current_admin, "buying_zone.create")
    return item


@router.patch("/{zone_id}", response_model=BuyingZoneResponse)
def edit_zone(
    zone_id: int,
    payload: BuyingZoneUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> BuyingZone:
    item = get_buying_zone(db, zone_id, lock=True)
    old_value = snapshot_model(item)
    item = update_buying_zone(db, item, payload, commit=False)
    save_audited_resource(db, item, current_admin, "buying_zone.edit", old_value=old_value)
    return item
