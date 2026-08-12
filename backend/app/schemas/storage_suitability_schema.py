from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

StorageSuitabilityStatus = Literal["good", "watch", "risky", "not_recommended"]

STORAGE_SUITABILITY_DISCLAIMER = (
    "Storage suitability is based on available market and quality information. "
    "It does not guarantee profit, preservation, or future price increase."
)

_FORBIDDEN_STORAGE_CLAIMS = (
    "guaranteed profit",
    "profit guaranteed",
    "cannot lose",
    "guaranteed preservation",
    "guaranteed preserved",
    "will not spoil",
    "cannot spoil",
    "guaranteed scarcity",
    "scarcity guaranteed",
    "guaranteed price increase",
    "guaranteed future price increase",
    "will surely rise",
    "certain to rise",
    "financial advice",
)


def _validate_storage_observation(value: str | None) -> str | None:
    if value is None:
        return value
    lowered = value.lower()
    if any(phrase in lowered for phrase in _FORBIDDEN_STORAGE_CLAIMS):
        raise ValueError(
            "Storage suitability must not guarantee profit, preservation, scarcity, or future price increase"
        )
    return value


class StorageSuitabilityCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    suitability_status: StorageSuitabilityStatus
    import_risk: str | None = Field(default=None, max_length=100)
    oversupply_risk: str | None = Field(default=None, max_length=100)
    spoilage_risk: str | None = Field(default=None, max_length=100)
    buyer_availability: str | None = Field(default=None, max_length=150)
    quality_storage_notes: str | None = None
    summary: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator(
        "import_risk",
        "oversupply_risk",
        "spoilage_risk",
        "buyer_availability",
        "quality_storage_notes",
        "summary",
    )
    @classmethod
    def text_must_remain_observational(cls, value: str | None) -> str | None:
        return _validate_storage_observation(value)


class StorageSuitabilityUpdate(BaseModel):
    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)
    price_update_id: int | None = Field(default=None, gt=0)
    suitability_status: StorageSuitabilityStatus | None = None
    import_risk: str | None = Field(default=None, max_length=100)
    oversupply_risk: str | None = Field(default=None, max_length=100)
    spoilage_risk: str | None = Field(default=None, max_length=100)
    buyer_availability: str | None = Field(default=None, max_length=150)
    quality_storage_notes: str | None = None
    summary: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator(
        "import_risk",
        "oversupply_risk",
        "spoilage_risk",
        "buyer_availability",
        "quality_storage_notes",
        "summary",
    )
    @classmethod
    def text_must_remain_observational(cls, value: str | None) -> str | None:
        return _validate_storage_observation(value)


class StorageSuitabilityResponse(BaseModel):
    id: int
    commodity_id: int
    market_id: int
    price_update_id: int | None
    suitability_status: StorageSuitabilityStatus
    import_risk: str | None
    oversupply_risk: str | None
    spoilage_risk: str | None
    buyer_availability: str | None
    quality_storage_notes: str | None
    summary: str | None
    created_at: datetime
    updated_at: datetime
    disclaimer: str = STORAGE_SUITABILITY_DISCLAIMER

    model_config = ConfigDict(from_attributes=True)
