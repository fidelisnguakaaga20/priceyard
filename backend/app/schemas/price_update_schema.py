from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

Movement = Literal["up", "down", "stable", "unknown"]
SuggestedAction = Literal["Watch", "Investigate", "Buy Carefully", "Hold", "Sell Carefully"]
TimeOfDay = Literal["morning", "afternoon", "evening", "closing"]
MarketDay = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ConfidenceLevel = Literal[
    "Reporter submitted",
    "Verified by 2 sources",
    "Admin confirmed",
    "Market visit confirmed",
    "Low confidence",
    "Price outdated",
]

_FORBIDDEN_CLAIM_PHRASES = (
    "guaranteed profit",
    "guaranteed prediction",
    "financial advice",
    "cannot lose",
    "never fails",
    "will surely rise",
    "must buy",
    "must sell",
)


class PriceUpdateWriteBase(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    price_low: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    price_high: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    average_price: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    previous_price_low: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    previous_price_high: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    unit: str = Field(min_length=1, max_length=100)
    bag_size: str | None = Field(default=None, max_length=100)
    commodity_type: str | None = Field(default=None, max_length=150)
    market_day: MarketDay | None = None
    time_of_day: TimeOfDay | None = None
    movement: Movement = "unknown"
    confidence_level: ConfidenceLevel
    source_type: str | None = Field(default=None, max_length=100)
    source_1: str | None = Field(default=None, max_length=255)
    source_2: str | None = Field(default=None, max_length=255)
    update_date_time: datetime
    is_outdated: bool = False
    possible_meaning: str = Field(min_length=1)
    suggested_action: SuggestedAction
    notes: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("possible_meaning")
    @classmethod
    def possible_meaning_must_remain_observational(cls, value: str) -> str:
        lowered = value.lower()
        if any(phrase in lowered for phrase in _FORBIDDEN_CLAIM_PHRASES):
            raise ValueError("Possible meaning must remain observational and non-guaranteed")
        return value

    @model_validator(mode="after")
    def validate_ranges(self) -> "PriceUpdateWriteBase":
        if self.price_high < self.price_low:
            raise ValueError("price_high must be greater than or equal to price_low")
        if not (self.price_low <= self.average_price <= self.price_high):
            raise ValueError("average_price must be within the current price range")

        previous_pair = (self.previous_price_low, self.previous_price_high)
        if (previous_pair[0] is None) != (previous_pair[1] is None):
            raise ValueError("previous_price_low and previous_price_high must be provided together")
        if previous_pair[0] is not None and previous_pair[1] is not None and previous_pair[1] < previous_pair[0]:
            raise ValueError("previous_price_high must be greater than or equal to previous_price_low")
        return self


class PriceUpdateCreate(PriceUpdateWriteBase):
    pass


class PriceUpdateUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    price_low: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    price_high: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    average_price: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    previous_price_low: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    previous_price_high: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    unit: str | None = Field(default=None, min_length=1, max_length=100)
    bag_size: str | None = Field(default=None, max_length=100)
    commodity_type: str | None = Field(default=None, max_length=150)
    market_day: MarketDay | None = None
    time_of_day: TimeOfDay | None = None
    movement: Movement | None = None
    confidence_level: ConfidenceLevel | None = None
    source_type: str | None = Field(default=None, max_length=100)
    source_1: str | None = Field(default=None, max_length=255)
    source_2: str | None = Field(default=None, max_length=255)
    update_date_time: datetime | None = None
    is_outdated: bool | None = None
    possible_meaning: str | None = Field(default=None, min_length=1)
    suggested_action: SuggestedAction | None = None
    notes: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("possible_meaning")
    @classmethod
    def possible_meaning_must_remain_observational(cls, value: str | None) -> str | None:
        if value is None:
            return value
        lowered = value.lower()
        if any(phrase in lowered for phrase in _FORBIDDEN_CLAIM_PHRASES):
            raise ValueError("Possible meaning must remain observational and non-guaranteed")
        return value


class CommoditySummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MarketSummary(BaseModel):
    id: int
    name: str
    state: str | None
    market_day: str | None

    model_config = ConfigDict(from_attributes=True)


class PriceUpdatePublicResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    commodity: CommoditySummary
    market: MarketSummary
    price_low: Decimal
    price_high: Decimal
    average_price: Decimal | None
    previous_price_low: Decimal | None
    previous_price_high: Decimal | None
    unit: str
    bag_size: str | None
    commodity_type: str | None
    market_day: str | None
    time_of_day: str | None
    movement: str
    confidence_level: str
    source_type: str | None
    update_date_time: datetime
    is_outdated: bool
    status: str
    possible_meaning: str | None
    suggested_action: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceUpdateAdminResponse(PriceUpdatePublicResponse):
    source_1: str | None
    source_2: str | None
    created_by: int
    approved_by: int | None
