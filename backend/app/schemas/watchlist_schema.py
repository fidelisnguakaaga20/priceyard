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

    @model_validator(mode="after")
    def require_selection(self) -> "WatchlistCreate":
        if self.commodity_id is None and self.market_id is None:
            raise ValueError("At least one of commodity_id or market_id is required")
        if (self.target_price is None) != (self.target_direction is None):
            raise ValueError("target_price and target_direction must be set together")
        return self


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    commodity_id: int | None
    market_id: int | None
    target_price: Decimal | None
    target_direction: TargetDirection | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
