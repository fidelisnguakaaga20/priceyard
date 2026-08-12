from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.price_update import PriceUpdate


class CostBreakdown(Base):
    __tablename__ = "cost_breakdowns"
    __table_args__ = (
        CheckConstraint("transport >= 0", name="ck_cost_breakdowns_transport_nonnegative"),
        CheckConstraint("warehouse >= 0", name="ck_cost_breakdowns_warehouse_nonnegative"),
        CheckConstraint("security >= 0", name="ck_cost_breakdowns_security_nonnegative"),
        CheckConstraint("market_charges >= 0", name="ck_cost_breakdowns_market_charges_nonnegative"),
        CheckConstraint("loading_offloading >= 0", name="ck_cost_breakdowns_loading_offloading_nonnegative"),
        CheckConstraint("other_costs >= 0", name="ck_cost_breakdowns_other_costs_nonnegative"),
        CheckConstraint("total_additional_cost >= 0", name="ck_cost_breakdowns_total_additional_nonnegative"),
        CheckConstraint("purchase_price_reference >= 0", name="ck_cost_breakdowns_purchase_price_nonnegative"),
        CheckConstraint(
            "total_estimated_landing_storage_cost >= 0",
            name="ck_cost_breakdowns_total_estimated_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    price_update_id: Mapped[int] = mapped_column(
        ForeignKey("price_updates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transport: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    warehouse: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    security: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    market_charges: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    loading_offloading: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    other_costs: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    total_additional_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    purchase_price_reference: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_estimated_landing_storage_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    price_update: Mapped[PriceUpdate] = relationship(back_populates="cost_breakdowns")
