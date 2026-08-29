from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.buying_zone import BuyingZone
    from app.models.audit_log import AuditLog
    from app.models.feedback import Feedback
    from app.models.faq_item import FAQItem
    from app.models.market_signal import MarketSignal
    from app.models.price_update import PriceUpdate
    from app.models.password_reset_token import PasswordResetToken
    from app.models.quality_signal import QualitySignal
    from app.models.sell_watch_window import SellWatchWindow
    from app.models.subscription import Subscription
    from app.models.watchlist import Watchlist


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="free_user", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    subscription: Mapped[Subscription | None] = relationship(back_populates="user", uselist=False)
    feedback_entries: Mapped[list[Feedback]] = relationship(back_populates="user")
    created_price_updates: Mapped[list[PriceUpdate]] = relationship(
        back_populates="creator",
        foreign_keys="PriceUpdate.created_by",
    )
    approved_price_updates: Mapped[list[PriceUpdate]] = relationship(
        back_populates="approver",
        foreign_keys="PriceUpdate.approved_by",
    )
    market_signals: Mapped[list[MarketSignal]] = relationship(back_populates="creator")
    quality_signals: Mapped[list[QualitySignal]] = relationship(back_populates="creator")
    buying_zones: Mapped[list[BuyingZone]] = relationship(back_populates="creator")
    sell_watch_windows: Mapped[list[SellWatchWindow]] = relationship(back_populates="creator")
    faq_items: Mapped[list[FAQItem]] = relationship(back_populates="creator")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
    watchlist_items: Mapped[list[Watchlist]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    password_reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
