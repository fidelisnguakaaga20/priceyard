from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import save_audited_resource, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
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
    update_storage_suitability,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/storage-suitability", tags=["storage-suitability"])


@router.get("", response_model=list[StorageSuitabilityResponse])
def get_items(
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
    commodity_id: Annotated[int | None, Query(gt=0)] = None,
) -> Response:
    conditions = (StorageSuitability.commodity_id == commodity_id,) if commodity_id is not None else ()
    return AdminJSONResponse(stream_admin_records(db.get_bind(), StorageSuitability, StorageSuitabilityResponse,
        order=(("created_at", True), ("id", True)), where=conditions))


@router.get("/admin/page", response_model=AdminRecordPage[StorageSuitabilityResponse])
def get_admin_storage_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AdminRecordPage[StorageSuitabilityResponse]:
    return admin_record_page(db, StorageSuitability, StorageSuitabilityResponse, offset=offset,
        order=(("created_at", True), ("id", True)))


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
    current_admin: User = Depends(require_roles("admin")),
) -> StorageSuitability:
    item = create_storage_suitability(db, payload, commit=False)
    save_audited_resource(db, item, current_admin, "storage_suitability.create")
    return item


@router.patch("/{item_id}", response_model=StorageSuitabilityResponse)
def edit_item(
    item_id: int,
    payload: StorageSuitabilityUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> StorageSuitability:
    item = get_storage_suitability(db, item_id, lock=True)
    old_value = snapshot_model(item)
    item = update_storage_suitability(db, item, payload, commit=False)
    save_audited_resource(db, item, current_admin, "storage_suitability.edit", old_value=old_value)
    return item
