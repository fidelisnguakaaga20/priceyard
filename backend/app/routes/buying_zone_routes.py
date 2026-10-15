from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.buying_zone import BuyingZone
from app.models.user import User
from app.services.intelligence_query_service import get_visible_intelligence, list_intelligence
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
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> list[BuyingZone]:
    return list_intelligence(db, BuyingZone, commodity_id=commodity_id, market_id=market_id,
                             page=page, page_size=page_size, active_only=current_user.role != "admin")


@router.get("/{zone_id}", response_model=BuyingZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> BuyingZone:
    return get_visible_intelligence(db, BuyingZone, zone_id, active_only=current_user.role != "admin")


@router.post("", response_model=BuyingZoneResponse, status_code=status.HTTP_201_CREATED)
def add_zone(
    payload: BuyingZoneCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> BuyingZone:
    return create_buying_zone(db, payload, current_admin)


@router.patch("/{zone_id}", response_model=BuyingZoneResponse)
def edit_zone(
    zone_id: int,
    payload: BuyingZoneUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> BuyingZone:
    return update_buying_zone(db, get_buying_zone(db, zone_id), payload)
