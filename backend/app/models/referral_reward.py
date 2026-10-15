from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReferralReward(Base):
    __tablename__ = "referral_rewards"
    __table_args__ = (CheckConstraint("reward_days = 7", name="ck_referral_rewards_days"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    referred_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    referrer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    qualifying_payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="RESTRICT"), unique=True, nullable=False)
    reward_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
