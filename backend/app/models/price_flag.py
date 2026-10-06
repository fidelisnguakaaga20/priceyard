from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.price_update import PriceUpdate
    from app.models.user import User


class PriceFlag(Base):
    __tablename__ = "price_flags"
    __table_args__ = (
        UniqueConstraint("price_update_id", "user_id", name="uq_price_flags_price_update_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    price_update_id: Mapped[int] = mapped_column(ForeignKey("price_updates.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    price_update: Mapped[PriceUpdate] = relationship(back_populates="flags")
    user: Mapped[User] = relationship()
