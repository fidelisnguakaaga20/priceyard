from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.buying_zone import BuyingZone
    from app.models.cost_breakdown import CostBreakdown
    from app.models.market_signal import MarketSignal
    from app.models.price_update import PriceUpdate
    from app.models.quality_signal import QualitySignal
    from app.models.sell_watch_window import SellWatchWindow
    from app.models.storage_suitability import StorageSuitability
    from app.models.watchlist import Watchlist


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Nigeria")
    market_day: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    price_updates: Mapped[list[PriceUpdate]] = relationship(back_populates="market")
    market_signals: Mapped[list[MarketSignal]] = relationship(back_populates="market")
    quality_signals: Mapped[list[QualitySignal]] = relationship(back_populates="market")
    buying_zones: Mapped[list[BuyingZone]] = relationship(back_populates="market")
    sell_watch_windows: Mapped[list[SellWatchWindow]] = relationship(back_populates="market")
    storage_suitability: Mapped[list[StorageSuitability]] = relationship(back_populates="market")
    watchlist_items: Mapped[list[Watchlist]] = relationship(back_populates="market", passive_deletes=True)
    cost_breakdowns: Mapped[list[CostBreakdown]] = relationship(back_populates="market")
