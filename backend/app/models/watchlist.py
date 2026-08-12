from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.commodity import Commodity
    from app.models.market import Market
    from app.models.user import User


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (
        CheckConstraint(
            "commodity_id IS NOT NULL OR market_id IS NOT NULL",
            name="ck_watchlists_has_selection",
        ),
        CheckConstraint(
            "target_price IS NULL OR target_price >= 0",
            name="ck_watchlists_target_price_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    commodity_id: Mapped[int | None] = mapped_column(
        ForeignKey("commodities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    market_id: Mapped[int | None] = mapped_column(
        ForeignKey("markets.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # Retained from the approved Architecture Design for later target-price work.
    # Stage 13 does not expose or implement target-price alert functionality.
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="watchlist_items")
    commodity: Mapped[Commodity | None] = relationship(back_populates="watchlist_items")
    market: Mapped[Market | None] = relationship(back_populates="watchlist_items")
