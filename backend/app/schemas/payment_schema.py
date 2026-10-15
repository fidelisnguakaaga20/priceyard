from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentPlan = Literal["monthly", "seasonal"]


class PaymentInitiateRequest(BaseModel):
    plan: PaymentPlan


class PaymentInitiateResponse(BaseModel):
    authorization_url: str
    reference: str


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    reference: str
    plan: str
    amount: Decimal
    currency: str
    status: str
    duration_days: int
    confirmed_at: datetime | None = None
    entitlement_applied_at: datetime | None = None
    granted_expires_at: datetime | None = None
    requires_reconciliation: bool = False
    reconciliation_resolution: str | None = None
    reconciliation_error: str | None = None
    access_applied: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentReconcileRequest(BaseModel):
    signed_payload: str = Field(min_length=2, max_length=32768)
    signature: str = Field(pattern=r"^[0-9a-fA-F]{128}$")
    legacy_resolution: Literal["already_applied", "apply_missing"] | None = None
    reason: str = Field(min_length=10, max_length=500)
