from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.storage_suitability import StorageSuitability
from app.models.user import User
from app.services.intelligence_query_service import get_visible_intelligence, list_intelligence
from app.schemas.storage_suitability_schema import (
    StorageSuitabilityCreate,
    StorageSuitabilityResponse,
    StorageSuitabilityUpdate,
)
from app.services.storage_suitability_service import (
    create_storage_suitability,
    get_storage_suitability,
    list_storage_suitability,
    update_storage_suitability,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/storage-suitability", tags=["storage-suitability"])


@router.get("", response_model=list[StorageSuitabilityResponse])
def get_items(
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> list[StorageSuitability]:
    return list_intelligence(db, StorageSuitability, commodity_id=commodity_id, market_id=market_id,
                             page=page, page_size=page_size, active_only=current_user.role != "admin")


@router.get("/{item_id}", response_model=StorageSuitabilityResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> StorageSuitability:
    return get_visible_intelligence(db, StorageSuitability, item_id, active_only=current_user.role != "admin")


@router.post("", response_model=StorageSuitabilityResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: StorageSuitabilityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> StorageSuitability:
    return create_storage_suitability(db, payload)


@router.patch("/{item_id}", response_model=StorageSuitabilityResponse)
def edit_item(
    item_id: int,
    payload: StorageSuitabilityUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> StorageSuitability:
    return update_storage_suitability(db, get_storage_suitability(db, item_id), payload)
