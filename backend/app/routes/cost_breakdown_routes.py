from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import save_audited_resource, snapshot_model
from app.models.cost_breakdown import CostBreakdown
from app.models.user import User
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
    db: Session = Depends(get_db),
    _: User = Depends(require_full_access),
    commodity_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[CostBreakdown]:
    return list_cost_breakdowns(db, commodity_id=commodity_id)


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
    current_admin: User = Depends(require_roles("admin")),
) -> CostBreakdown:
    item = create_cost_breakdown(db, payload, commit=False)
    save_audited_resource(db, item, current_admin, "cost_breakdown.create")
    return item


@router.patch("/{item_id}", response_model=CostBreakdownResponse)
def edit_item(
    item_id: int,
    payload: CostBreakdownUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> CostBreakdown:
    item = get_cost_breakdown(db, item_id, lock=True)
    old_value = snapshot_model(item)
    item = update_cost_breakdown(db, item, payload, commit=False)
    save_audited_resource(db, item, current_admin, "cost_breakdown.edit", old_value=old_value)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_cost_breakdown(db, item_id, lock=True)
    old_value = snapshot_model(item)
    delete_cost_breakdown(db, item, commit=False)
    save_audited_resource(db, item, current_admin, "cost_breakdown.delete", old_value=old_value, deleted=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
