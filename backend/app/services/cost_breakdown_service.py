from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.schemas.cost_breakdown_schema import CostBreakdownCreate, CostBreakdownUpdate

_COST_FIELDS = (
    "transport",
    "warehouse",
    "security",
    "market_charges",
    "loading_offloading",
    "other_costs",
)
_ZERO = Decimal("0.00")


def _validate_commodity(db: Session, commodity_id: int) -> None:
    if db.get(Commodity, commodity_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")


def _validate_market(db: Session, market_id: int) -> None:
    if db.get(Market, market_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")


def _calculate_totals(values: dict[str, Decimal]) -> tuple[Decimal, Decimal]:
    additional = sum((values.get(field, _ZERO) for field in _COST_FIELDS), _ZERO)
    total = values["purchase_price_reference"] + additional
    return additional, total


def create_cost_breakdown(db: Session, payload: CostBreakdownCreate) -> CostBreakdown:
    _validate_commodity(db, payload.commodity_id)
    _validate_market(db, payload.market_id)
    values = payload.model_dump()
    additional, total = _calculate_totals(values)
    item = CostBreakdown(
        **values,
        total_additional_cost=additional,
        total_estimated_landing_storage_cost=total,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_cost_breakdown(db: Session, item_id: int) -> CostBreakdown:
    item = db.get(CostBreakdown, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost breakdown not found")
    return item


def list_cost_breakdowns(db: Session) -> list[CostBreakdown]:
    return list(
        db.scalars(
            select(CostBreakdown).order_by(CostBreakdown.created_at.desc(), CostBreakdown.id.desc())
        ).all()
    )


def update_cost_breakdown(
    db: Session,
    item: CostBreakdown,
    payload: CostBreakdownUpdate,
) -> CostBreakdown:
    changes = payload.model_dump(exclude_unset=True)
    commodity_id = int(changes.get("commodity_id", item.commodity_id))
    market_id = int(changes.get("market_id", item.market_id))
    _validate_commodity(db, commodity_id)
    _validate_market(db, market_id)

    values: dict[str, Decimal] = {
        field: changes.get(field, getattr(item, field)) for field in _COST_FIELDS
    }
    values["purchase_price_reference"] = changes.get(
        "purchase_price_reference", item.purchase_price_reference
    )
    additional, total = _calculate_totals(values)

    for field, value in changes.items():
        setattr(item, field, value)
    item.total_additional_cost = additional
    item.total_estimated_landing_storage_cost = total
    db.commit()
    db.refresh(item)
    return item
