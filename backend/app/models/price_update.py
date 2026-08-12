from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.commodity import Commodity
    from app.models.market import Market
    from app.models.market_signal import MarketSignal
    from app.models.quality_signal import QualitySignal
    from app.models.storage_suitability import StorageSuitability
    from app.models.user import User


class PriceUpdate(Base):
    __tablename__ = "price_updates"
    __table_args__ = (
        CheckConstraint("price_low >= 0", name="ck_price_updates_price_low_nonnegative"),
        CheckConstraint("price_high >= price_low", name="ck_price_updates_price_range"),
        CheckConstraint(
            "average_price IS NULL OR (average_price >= price_low AND average_price <= price_high)",
            name="ck_price_updates_average_in_range",
        ),
        CheckConstraint(
            "movement IN ('up', 'down', 'stable', 'unknown')",
            name="ck_price_updates_movement",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_price_updates_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False, index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id", ondelete="RESTRICT"), nullable=False, index=True)
    price_low: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    price_high: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    average_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    previous_price_low: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    previous_price_high: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    unit: Mapped[str] = mapped_column(String(100), nullable=False)
    bag_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commodity_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    market_day: Mapped[str | None] = mapped_column(String(30), nullable=True)
    time_of_day: Mapped[str | None] = mapped_column(String(20), nullable=True)
    movement: Mapped[str] = mapped_column(String(20), nullable=False, default="unknown", index=True)
    confidence_level: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    update_date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_outdated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    possible_meaning: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    commodity: Mapped[Commodity] = relationship(back_populates="price_updates")
    market: Mapped[Market] = relationship(back_populates="price_updates")
    creator: Mapped[User] = relationship(back_populates="created_price_updates", foreign_keys=[created_by])
    approver: Mapped[User | None] = relationship(back_populates="approved_price_updates", foreign_keys=[approved_by])
    market_signals: Mapped[list[MarketSignal]] = relationship(back_populates="price_update")
    quality_signals: Mapped[list[QualitySignal]] = relationship(back_populates="price_update")
    storage_suitability: Mapped[list[StorageSuitability]] = relationship(back_populates="price_update")
