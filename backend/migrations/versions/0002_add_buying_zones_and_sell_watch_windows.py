"""add Stage 10 buying zones and sell-watch windows

Revision ID: 0002_stage10_buy_sell_watch
Revises: 0001_create_mvp_foundation
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_stage10_buy_sell_watch"
down_revision: Union[str, Sequence[str], None] = "0001_create_mvp_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "buying_zones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("price_low", sa.Numeric(14, 2), nullable=False),
        sa.Column("price_high", sa.Numeric(14, 2), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("confidence", sa.String(length=100), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price_low >= 0", name="ck_buying_zones_price_low_nonnegative"),
        sa.CheckConstraint("price_high >= price_low", name="ck_buying_zones_price_range"),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from",
            name="ck_buying_zones_valid_period",
        ),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_buying_zones_commodity_id", "buying_zones", ["commodity_id"], unique=False)
    op.create_index("ix_buying_zones_market_id", "buying_zones", ["market_id"], unique=False)
    op.create_index("ix_buying_zones_created_by", "buying_zones", ["created_by"], unique=False)

    op.create_table(
        "sell_watch_windows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("start_period", sa.String(length=100), nullable=False),
        sa.Column("end_period", sa.String(length=100), nullable=True),
        sa.Column("observation", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=100), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_sell_watch_windows_commodity_id", "sell_watch_windows", ["commodity_id"], unique=False)
    op.create_index("ix_sell_watch_windows_market_id", "sell_watch_windows", ["market_id"], unique=False)
    op.create_index("ix_sell_watch_windows_created_by", "sell_watch_windows", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sell_watch_windows_created_by", table_name="sell_watch_windows")
    op.drop_index("ix_sell_watch_windows_market_id", table_name="sell_watch_windows")
    op.drop_index("ix_sell_watch_windows_commodity_id", table_name="sell_watch_windows")
    op.drop_table("sell_watch_windows")

    op.drop_index("ix_buying_zones_created_by", table_name="buying_zones")
    op.drop_index("ix_buying_zones_market_id", table_name="buying_zones")
    op.drop_index("ix_buying_zones_commodity_id", table_name="buying_zones")
    op.drop_table("buying_zones")
