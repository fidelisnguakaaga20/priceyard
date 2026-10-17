from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import save_audited_resource, snapshot_model
from app.models.quality_signal import QualitySignal
from app.models.user import User
from app.schemas.quality_signal_schema import QualitySignalCreate, QualitySignalResponse, QualitySignalUpdate
from app.services.quality_signal_service import (
    create_quality_signal,
    delete_quality_signal,
    get_quality_signal,
    list_quality_signals,
    update_quality_signal,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/quality-signals", tags=["quality-signals"])


@router.get("", response_model=list[QualitySignalResponse])
def get_signals(
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
    commodity_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[QualitySignal]:
    return list_quality_signals(db, commodity_id=commodity_id)


@router.get("/{signal_id}", response_model=QualitySignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> QualitySignal:
    return get_quality_signal(db, signal_id)


@router.post("", response_model=QualitySignalResponse, status_code=status.HTTP_201_CREATED)
def add_signal(
    payload: QualitySignalCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> QualitySignal:
    item = create_quality_signal(db, payload, current_admin, commit=False)
    save_audited_resource(db, item, current_admin, "quality_signal.create")
    return item


@router.patch("/{signal_id}", response_model=QualitySignalResponse)
def edit_signal(
    signal_id: int,
    payload: QualitySignalUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> QualitySignal:
    item = get_quality_signal(db, signal_id, lock=True)
    old_value = snapshot_model(item)
    item = update_quality_signal(db, item, payload, commit=False)
    save_audited_resource(db, item, current_admin, "quality_signal.edit", old_value=old_value)
    return item


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_quality_signal(db, signal_id, lock=True)
    old_value = snapshot_model(item)
    delete_quality_signal(db, item, commit=False)
    save_audited_resource(db, item, current_admin, "quality_signal.delete", old_value=old_value, deleted=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
