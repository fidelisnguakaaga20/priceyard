from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.utils.price_measurement import validate_observation_time


class CostBreakdownCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    unit: str = Field(min_length=1, max_length=100)
    bag_size: str = Field(min_length=1, max_length=100)
    commodity_type: str | None = Field(default=None, max_length=150)
    grade: str | None = Field(default=None, max_length=100)
    reference_date_time: datetime
    transport: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    warehouse: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    security: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    market_charges: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    loading_offloading: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    other_costs: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    purchase_price_reference: Decimal = Field(ge=0, max_digits=14, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("reference_date_time")
    @classmethod
    def reference_must_be_aware(cls, value: datetime) -> datetime:
        return validate_observation_time(value)


class CostBreakdownUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=100)
    bag_size: str | None = Field(default=None, min_length=1, max_length=100)
    commodity_type: str | None = Field(default=None, max_length=150)
    grade: str | None = Field(default=None, max_length=100)
    reference_date_time: datetime | None = None
    transport: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    warehouse: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    security: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    market_charges: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    loading_offloading: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    other_costs: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    purchase_price_reference: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("reference_date_time")
    @classmethod
    def reference_must_be_aware(cls, value: datetime | None) -> datetime | None:
        return validate_observation_time(value) if value is not None else value


class CostBreakdownResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    unit: str | None
    bag_size: str | None
    commodity_type: str | None
    grade: str | None
    reference_date_time: datetime | None
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
