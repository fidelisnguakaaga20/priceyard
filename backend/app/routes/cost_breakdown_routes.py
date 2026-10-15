from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cost_breakdown import CostBreakdown
from app.models.user import User
from app.services.intelligence_query_service import get_visible_intelligence, list_intelligence
from app.schemas.cost_breakdown_schema import (
    CostBreakdownCreate,
    CostBreakdownResponse,
    CostBreakdownUpdate,
)
from app.services.cost_breakdown_service import (
    create_cost_breakdown,
    delete_cost_breakdown,
    get_cost_breakdown,
    list_cost_breakdowns,
    update_cost_breakdown,
)
from app.utils.permissions import require_full_access, require_roles

router = APIRouter(prefix="/cost-breakdowns", tags=["cost-breakdowns"])


@router.get("", response_model=list[CostBreakdownResponse])
def get_items(
    commodity_id: int | None = Query(default=None, gt=0),
    market_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> list[CostBreakdown]:
    return list_intelligence(db, CostBreakdown, commodity_id=commodity_id, market_id=market_id,
                             page=page, page_size=page_size, active_only=current_user.role != "admin")


@router.get("/{item_id}", response_model=CostBreakdownResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_full_access),
) -> CostBreakdown:
    return get_visible_intelligence(db, CostBreakdown, item_id, active_only=current_user.role != "admin")


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


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_cost_breakdown(db, get_cost_breakdown(db, item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
