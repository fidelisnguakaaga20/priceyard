"""add Stage 13 watchlists

Revision ID: 0005_stage13_watchlists
Revises: 0004_stage12_cost_breakdowns
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_stage13_watchlists"
down_revision: Union[str, Sequence[str], None] = "0004_stage12_cost_breakdowns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("commodity_id", sa.Integer(), nullable=True),
        sa.Column("market_id", sa.Integer(), nullable=True),
        sa.Column("target_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "commodity_id IS NOT NULL OR market_id IS NOT NULL",
            name="ck_watchlists_has_selection",
        ),
        sa.CheckConstraint(
            "target_price IS NULL OR target_price >= 0",
            name="ck_watchlists_target_price_nonnegative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_watchlists_user_id", "watchlists", ["user_id"], unique=False)
    op.create_index("ix_watchlists_commodity_id", "watchlists", ["commodity_id"], unique=False)
    op.create_index("ix_watchlists_market_id", "watchlists", ["market_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_watchlists_market_id", table_name="watchlists")
    op.drop_index("ix_watchlists_commodity_id", table_name="watchlists")
    op.drop_index("ix_watchlists_user_id", table_name="watchlists")
    op.drop_table("watchlists")
