"""Restricted evidence of corrections; never included in consumer schemas."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceRevision(Base):
    __tablename__ = "price_revisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    price_update_id: Mapped[int] = mapped_column(ForeignKey("price_updates.id", ondelete="RESTRICT"), nullable=False, index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    original_values: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
