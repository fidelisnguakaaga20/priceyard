from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

SELL_WATCH_DISCLAIMER = (
    "Sell-watch windows are market observations and are not guaranteed profit periods, "
    "guaranteed selling opportunities, predictions, or financial advice."
)

_FORBIDDEN_SELL_CLAIMS = (
    "guaranteed profit",
    "guaranteed profit period",
    "guaranteed selling opportunity",
    "financial advice",
    "must sell",
    "cannot lose",
    "will surely rise",
    "certain to rise",
)


def _validate_observational_text(value: str | None) -> str | None:
    if value is None:
        return value
    lowered = value.lower()
    if any(phrase in lowered for phrase in _FORBIDDEN_SELL_CLAIMS):
        raise ValueError("Sell-watch observation must remain observational and non-guaranteed")
    return value


class SellWatchWindowCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    start_period: str = Field(min_length=1, max_length=100)
    end_period: str | None = Field(default=None, max_length=100)
    observation: str = Field(min_length=1)
    confidence: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("observation")
    @classmethod
    def observation_must_be_non_guaranteed(cls, value: str) -> str:
        return _validate_observational_text(value) or value


class SellWatchWindowUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    start_period: str | None = Field(default=None, min_length=1, max_length=100)
    end_period: str | None = Field(default=None, max_length=100)
    observation: str | None = Field(default=None, min_length=1)
    confidence: str | None = Field(default=None, min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("observation")
    @classmethod
    def observation_must_be_non_guaranteed(cls, value: str | None) -> str | None:
        return _validate_observational_text(value)


class SellWatchWindowResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    start_period: str
    end_period: str | None
    observation: str
    confidence: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    disclaimer: str = SELL_WATCH_DISCLAIMER

    model_config = ConfigDict(from_attributes=True)
