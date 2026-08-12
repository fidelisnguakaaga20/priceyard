from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.commodity import Commodity
    from app.models.market import Market
    from app.models.price_update import PriceUpdate
    from app.models.user import User


class QualitySignal(Base):
    __tablename__ = "quality_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False, index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id", ondelete="RESTRICT"), nullable=False, index=True)
    price_update_id: Mapped[int | None] = mapped_column(ForeignKey("price_updates.id", ondelete="CASCADE"), nullable=True, index=True)
    quality_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    moisture_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    storage_readiness: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    commodity: Mapped[Commodity] = relationship(back_populates="quality_signals")
    market: Mapped[Market] = relationship(back_populates="quality_signals")
    price_update: Mapped[PriceUpdate | None] = relationship(back_populates="quality_signals")
    creator: Mapped[User] = relationship(back_populates="quality_signals")
