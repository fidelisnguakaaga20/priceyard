from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.storage_suitability import StorageSuitability
from app.models.user import User
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
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> list[StorageSuitability]:
    return list_storage_suitability(db)


@router.get("/{item_id}", response_model=StorageSuitabilityResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> StorageSuitability:
    return get_storage_suitability(db, item_id)


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
