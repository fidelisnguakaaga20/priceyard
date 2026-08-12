from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.commodity import Commodity
    from app.models.market import Market
    from app.models.price_update import PriceUpdate


class StorageSuitability(Base):
    __tablename__ = "storage_suitability"
    __table_args__ = (
        CheckConstraint(
            "suitability_status IN ('good', 'watch', 'risky', 'not_recommended')",
            name="ck_storage_suitability_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    price_update_id: Mapped[int | None] = mapped_column(
        ForeignKey("price_updates.id", ondelete="SET NULL"), nullable=True, index=True
    )
    suitability_status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    import_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    oversupply_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spoilage_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    buyer_availability: Mapped[str | None] = mapped_column(String(150), nullable=True)
    quality_storage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    commodity: Mapped[Commodity] = relationship(back_populates="storage_suitability")
    market: Mapped[Market] = relationship(back_populates="storage_suitability")
    price_update: Mapped[PriceUpdate | None] = relationship(back_populates="storage_suitability")
