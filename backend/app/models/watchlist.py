from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
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
        CheckConstraint(
            "(target_price IS NULL) = (target_direction IS NULL)",
            name="ck_watchlists_target_price_direction_paired",
        ),
        CheckConstraint(
            "target_direction IS NULL OR target_direction IN ('at_or_below', 'at_or_above')",
            name="ck_watchlists_target_direction_valid",
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
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    # 'at_or_below' (buy-side: alert when the range's low reaches this or lower) or
    # 'at_or_above' (sell-side: alert when the range's high reaches this or higher).
    # Always set together with target_price, always null otherwise.
    target_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="watchlist_items")
    commodity: Mapped[Commodity | None] = relationship(back_populates="watchlist_items")
    market: Mapped[Market | None] = relationship(back_populates="watchlist_items")
