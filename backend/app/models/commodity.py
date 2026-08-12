from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.market_signal import MarketSignal
    from app.models.price_update import PriceUpdate
    from app.models.quality_signal import QualitySignal


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    price_updates: Mapped[list[PriceUpdate]] = relationship(back_populates="commodity")
    market_signals: Mapped[list[MarketSignal]] = relationship(back_populates="commodity")
    quality_signals: Mapped[list[QualitySignal]] = relationship(back_populates="commodity")
