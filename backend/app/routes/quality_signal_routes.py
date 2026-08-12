from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
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
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/quality-signals", tags=["quality-signals"])


@router.get("", response_model=list[QualitySignalResponse])
def get_signals(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[QualitySignal]:
    return list_quality_signals(db)


@router.get("/{signal_id}", response_model=QualitySignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> QualitySignal:
    return get_quality_signal(db, signal_id)


@router.post("", response_model=QualitySignalResponse, status_code=status.HTTP_201_CREATED)
def add_signal(
    payload: QualitySignalCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> QualitySignal:
    return create_quality_signal(db, payload, current_admin)


@router.patch("/{signal_id}", response_model=QualitySignalResponse)
def edit_signal(
    signal_id: int,
    payload: QualitySignalUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> QualitySignal:
    return update_quality_signal(db, get_quality_signal(db, signal_id), payload)


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_quality_signal(db, get_quality_signal(db, signal_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
