from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quality_signal import QualitySignal
from app.models.user import User
from app.services.intelligence_query_service import get_visible_intelligence, list_intelligence
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
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> list[QualitySignal]:
    return list_intelligence(db, QualitySignal, commodity_id=commodity_id, market_id=market_id,
                             page=page, page_size=page_size, active_only=current_user.role != "admin")


@router.get("/{signal_id}", response_model=QualitySignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> QualitySignal:
    return get_visible_intelligence(db, QualitySignal, signal_id, active_only=current_user.role != "admin")


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
