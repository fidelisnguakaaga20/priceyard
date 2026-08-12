from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BUYING_ZONE_DISCLAIMER = (
    "Buying zones are market observations and are not guaranteed lowest prices, "
    "guaranteed buying opportunities, predictions, or financial advice."
)

_FORBIDDEN_BUYING_CLAIMS = (
    "guaranteed lowest",
    "guaranteed buying opportunity",
    "guaranteed profit",
    "financial advice",
    "must buy",
    "cannot lose",
    "will surely rise",
    "certain to rise",
)


def _validate_observational_reason(value: str | None) -> str | None:
    if value is None:
        return value
    lowered = value.lower()
    if any(phrase in lowered for phrase in _FORBIDDEN_BUYING_CLAIMS):
        raise ValueError("Buying-zone reason must remain observational and non-guaranteed")
    return value


class BuyingZoneCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    price_low: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    price_high: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    reason: str = Field(min_length=1)
    valid_from: date | None = None
    valid_to: date | None = None
    confidence: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("reason")
    @classmethod
    def reason_must_be_observational(cls, value: str) -> str:
        return _validate_observational_reason(value) or value

    @model_validator(mode="after")
    def validate_range_and_period(self) -> "BuyingZoneCreate":
        if self.price_high < self.price_low:
            raise ValueError("price_high must be greater than or equal to price_low")
        if self.valid_from is not None and self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be on or after valid_from")
        return self


class BuyingZoneUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    price_low: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    price_high: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    reason: str | None = Field(default=None, min_length=1)
    valid_from: date | None = None
    valid_to: date | None = None
    confidence: str | None = Field(default=None, min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("reason")
    @classmethod
    def reason_must_be_observational(cls, value: str | None) -> str | None:
        return _validate_observational_reason(value)


class BuyingZoneResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    price_low: Decimal
    price_high: Decimal
    reason: str
    valid_from: date | None
    valid_to: date | None
    confidence: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    disclaimer: str = BUYING_ZONE_DISCLAIMER

    model_config = ConfigDict(from_attributes=True)
