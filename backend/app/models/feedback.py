from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_feedback_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_usefulness: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_accuracy: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_market_request: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_commodity_request: Mapped[str | None] = mapped_column(Text, nullable=True)
    complaint_or_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    continue_using_feedback: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    willingness_to_pay_feedback: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_public_testimonial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    testimonial_display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="feedback_entries")
