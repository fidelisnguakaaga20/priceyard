from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.price_update_schema import SuggestedAction

MARKET_SIGNAL_DISCLAIMER = (
    "Market signals are observations based on available market information. "
    "They are not guaranteed predictions or financial advice. Users should verify "
    "before making major buying, selling, or storage decisions."
)

_FORBIDDEN_CLAIM_PHRASES = (
    "guaranteed profit",
    "guaranteed prediction",
    "financial advice",
    "cannot lose",
    "never fails",
    "will surely rise",
    "will surely fall",
    "certain to rise",
    "certain to fall",
    "must buy",
    "must sell",
)


def _validate_observational_text(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return value
    lowered = value.lower()
    if any(phrase in lowered for phrase in _FORBIDDEN_CLAIM_PHRASES):
        raise ValueError(f"{field_name} must remain observational and non-guaranteed")
    return value


class MarketSignalCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    signal_type: str = Field(min_length=1, max_length=100)
    signal_description: str = Field(min_length=1)
    possible_meaning: str | None = None
    suggested_action: SuggestedAction | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("signal_description", "possible_meaning")
    @classmethod
    def keep_signal_observational(cls, value: str | None, info) -> str | None:
        return _validate_observational_text(value, field_name=info.field_name)


class MarketSignalUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    signal_type: str | None = Field(default=None, min_length=1, max_length=100)
    signal_description: str | None = Field(default=None, min_length=1)
    possible_meaning: str | None = None
    suggested_action: SuggestedAction | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("signal_description", "possible_meaning")
    @classmethod
    def keep_signal_observational(cls, value: str | None, info) -> str | None:
        return _validate_observational_text(value, field_name=info.field_name)


class MarketSignalResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    price_update_id: int | None
    signal_type: str
    signal_description: str
    possible_meaning: str | None
    suggested_action: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    disclaimer: str = MARKET_SIGNAL_DISCLAIMER

    model_config = ConfigDict(from_attributes=True)
