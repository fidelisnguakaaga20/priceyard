"""add Stage 11 storage suitability

Revision ID: 0003_stage11_storage_suitability
Revises: 0002_stage10_buy_sell_watch
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_stage11_storage_suitability"
down_revision: Union[str, Sequence[str], None] = "0002_stage10_buy_sell_watch"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "storage_suitability",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("price_update_id", sa.Integer(), nullable=True),
        sa.Column("suitability_status", sa.String(length=30), nullable=False),
        sa.Column("import_risk", sa.String(length=100), nullable=True),
        sa.Column("oversupply_risk", sa.String(length=100), nullable=True),
        sa.Column("spoilage_risk", sa.String(length=100), nullable=True),
        sa.Column("buyer_availability", sa.String(length=150), nullable=True),
        sa.Column("quality_storage_notes", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "suitability_status IN ('good', 'watch', 'risky', 'not_recommended')",
            name="ck_storage_suitability_status",
        ),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["price_update_id"], ["price_updates.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_storage_suitability_commodity_id", "storage_suitability", ["commodity_id"], unique=False)
    op.create_index("ix_storage_suitability_market_id", "storage_suitability", ["market_id"], unique=False)
    op.create_index("ix_storage_suitability_price_update_id", "storage_suitability", ["price_update_id"], unique=False)
    op.create_index("ix_storage_suitability_suitability_status", "storage_suitability", ["suitability_status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_storage_suitability_suitability_status", table_name="storage_suitability")
    op.drop_index("ix_storage_suitability_price_update_id", table_name="storage_suitability")
    op.drop_index("ix_storage_suitability_market_id", table_name="storage_suitability")
    op.drop_index("ix_storage_suitability_commodity_id", table_name="storage_suitability")
    op.drop_table("storage_suitability")
