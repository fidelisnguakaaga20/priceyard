"""add price_flags table

Revision ID: 0018_add_price_flags
Revises: 0017_add_push_subscriptions
Create Date: 2026-10-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0018_add_price_flags"
down_revision: Union[str, Sequence[str], None] = "0017_add_push_subscriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_update_id", sa.Integer(), sa.ForeignKey("price_updates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=50), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("price_update_id", "user_id", name="uq_price_flags_price_update_user"),
    )
    op.create_index("ix_price_flags_price_update_id", "price_flags", ["price_update_id"])
    op.create_index("ix_price_flags_user_id", "price_flags", ["user_id"])
    op.create_index("ix_price_flags_resolved", "price_flags", ["resolved"])


def downgrade() -> None:
    op.drop_index("ix_price_flags_resolved", table_name="price_flags")
    op.drop_index("ix_price_flags_user_id", table_name="price_flags")
    op.drop_index("ix_price_flags_price_update_id", table_name="price_flags")
    op.drop_table("price_flags")
