from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cost_breakdown import CostBreakdown
from app.models.user import User
from app.schemas.cost_breakdown_schema import (
    CostBreakdownCreate,
    CostBreakdownResponse,
    CostBreakdownUpdate,
)
from app.services.cost_breakdown_service import (
    create_cost_breakdown,
    get_cost_breakdown,
    list_cost_breakdowns,
    update_cost_breakdown,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/cost-breakdowns", tags=["cost-breakdowns"])


@router.get("", response_model=list[CostBreakdownResponse])
def get_items(
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> list[CostBreakdown]:
    return list_cost_breakdowns(db)


@router.get("/{item_id}", response_model=CostBreakdownResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
) -> CostBreakdown:
    return get_cost_breakdown(db, item_id)


@router.post("", response_model=CostBreakdownResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: CostBreakdownCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> CostBreakdown:
    return create_cost_breakdown(db, payload)


@router.patch("/{item_id}", response_model=CostBreakdownResponse)
def edit_item(
    item_id: int,
    payload: CostBreakdownUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> CostBreakdown:
    return update_cost_breakdown(db, get_cost_breakdown(db, item_id), payload)
