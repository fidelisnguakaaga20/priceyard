from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TargetDirection = Literal["at_or_below", "at_or_above"]


class WatchlistCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    target_price: Decimal | None = Field(default=None, ge=0)
    target_direction: TargetDirection | None = None
    target_unit: str | None = Field(default=None, max_length=100)
    target_bag_size: str | None = Field(default=None, max_length=100)
    target_commodity_type: str | None = Field(default=None, max_length=150)
    target_grade: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def require_selection(self) -> "WatchlistCreate":
        if self.commodity_id is None and self.market_id is None:
            raise ValueError("At least one of commodity_id or market_id is required")
        if (self.target_price is None) != (self.target_direction is None):
            raise ValueError("target_price and target_direction must be set together")
        if self.target_price is not None and (
            not self.commodity_id or not self.market_id or not self.target_unit or not self.target_unit.strip()
            or not self.target_bag_size or not self.target_bag_size.strip()
        ):
            raise ValueError("A price target requires a commodity, market, unit and bag/package specification")
        return self


class WatchlistTargetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    target_price: Decimal | None = Field(ge=0)
    target_direction: TargetDirection | None = None
    target_unit: str | None = Field(default=None, max_length=100)
    target_bag_size: str | None = Field(default=None, max_length=100)
    target_commodity_type: str | None = Field(default=None, max_length=150)
    target_grade: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def paired_target(self) -> "WatchlistTargetUpdate":
        if (self.target_price is None) != (self.target_direction is None):
            raise ValueError("target_price and target_direction must be set together")
        if self.target_price is not None and (not self.target_unit or not self.target_unit.strip() or not self.target_bag_size or not self.target_bag_size.strip()):
            raise ValueError("Confirm the unit and bag/package specification for this target")
        return self


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    commodity_id: int | None
    market_id: int | None
    target_price: Decimal | None
    target_direction: TargetDirection | None
    target_unit: str | None = None
    target_bag_size: str | None = None
    target_commodity_type: str | None = None
    target_grade: str | None = None
    target_measurement_confirmed: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
