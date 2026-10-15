from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'success', 'failed')", name="ck_payments_status"),
        CheckConstraint("plan IN ('monthly', 'seasonal')", name="ck_payments_plan"),
        CheckConstraint("duration_days > 0", name="ck_payments_duration"),
        Index(
            "uq_payments_applied_provider_id", "paystack_transaction_id", unique=True,
            postgresql_where=text("entitlement_applied_at IS NOT NULL"),
            sqlite_where=text("entitlement_applied_at IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="NGN")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    paystack_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda context: 90 if context.get_current_parameters().get("plan") == "seasonal" else 30)
    expected_customer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    provider_environment: Mapped[str | None] = mapped_column(String(10), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    entitlement_applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    granted_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_reconciliation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reconciliation_resolution: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reconciliation_error: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship()

    @property
    def access_applied(self) -> bool:
        return self.entitlement_applied_at is not None or self.reconciliation_resolution == "already_applied"
