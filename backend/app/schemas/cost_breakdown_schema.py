from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CostBreakdownCreate(BaseModel):
    price_update_id: int = Field(gt=0)
    transport: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    warehouse: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    security: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    market_charges: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    loading_offloading: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    other_costs: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    purchase_price_reference: Decimal = Field(ge=0, max_digits=14, decimal_places=2)


class CostBreakdownUpdate(BaseModel):
    price_update_id: int | None = Field(default=None, gt=0)
    transport: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    warehouse: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    security: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    market_charges: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    loading_offloading: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    other_costs: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    purchase_price_reference: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)


class CostBreakdownResponse(BaseModel):
    id: int
    price_update_id: int
    transport: Decimal
    warehouse: Decimal
    security: Decimal
    market_charges: Decimal
    loading_offloading: Decimal
    other_costs: Decimal
    total_additional_cost: Decimal
    purchase_price_reference: Decimal
    total_estimated_landing_storage_cost: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
