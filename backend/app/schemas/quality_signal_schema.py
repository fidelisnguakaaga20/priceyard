from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_UNSUPPORTED_LAB_CLAIMS = (
    "lab confirmed",
    "laboratory confirmed",
    "scientifically proven",
    "certified moisture",
    "laboratory verified",
)


def _reject_unsupported_lab_claim(value: str | None) -> str | None:
    if value is None:
        return value
    lowered = value.lower()
    if any(phrase in lowered for phrase in _UNSUPPORTED_LAB_CLAIMS):
        raise ValueError("Quality observations must not make unsupported laboratory claims")
    return value


class QualitySignalCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    quality_status: str | None = Field(default=None, max_length=100)
    moisture_status: str | None = Field(default=None, max_length=100)
    storage_readiness: str | None = Field(default=None, max_length=100)
    risk_note: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("quality_status", "moisture_status", "storage_readiness", "risk_note")
    @classmethod
    def quality_text_must_remain_observational(cls, value: str | None) -> str | None:
        return _reject_unsupported_lab_claim(value)


class QualitySignalUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    quality_status: str | None = Field(default=None, max_length=100)
    moisture_status: str | None = Field(default=None, max_length=100)
    storage_readiness: str | None = Field(default=None, max_length=100)
    risk_note: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("quality_status", "moisture_status", "storage_readiness", "risk_note")
    @classmethod
    def quality_text_must_remain_observational(cls, value: str | None) -> str | None:
        return _reject_unsupported_lab_claim(value)


class QualitySignalResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    price_update_id: int | None
    quality_status: str | None
    moisture_status: str | None
    storage_readiness: str | None
    risk_note: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
