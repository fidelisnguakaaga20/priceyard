"""add Stage 12 cost breakdowns

Revision ID: 0004_stage12_cost_breakdowns
Revises: 0003_stage11_storage_suitability
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_stage12_cost_breakdowns"
down_revision: Union[str, Sequence[str], None] = "0003_stage11_storage_suitability"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cost_breakdowns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_update_id", sa.Integer(), nullable=False),
        sa.Column("transport", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("warehouse", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("security", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("market_charges", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("loading_offloading", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("other_costs", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("total_additional_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("purchase_price_reference", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_estimated_landing_storage_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("transport >= 0", name="ck_cost_breakdowns_transport_nonnegative"),
        sa.CheckConstraint("warehouse >= 0", name="ck_cost_breakdowns_warehouse_nonnegative"),
        sa.CheckConstraint("security >= 0", name="ck_cost_breakdowns_security_nonnegative"),
        sa.CheckConstraint("market_charges >= 0", name="ck_cost_breakdowns_market_charges_nonnegative"),
        sa.CheckConstraint("loading_offloading >= 0", name="ck_cost_breakdowns_loading_offloading_nonnegative"),
        sa.CheckConstraint("other_costs >= 0", name="ck_cost_breakdowns_other_costs_nonnegative"),
        sa.CheckConstraint("total_additional_cost >= 0", name="ck_cost_breakdowns_total_additional_nonnegative"),
        sa.CheckConstraint("purchase_price_reference >= 0", name="ck_cost_breakdowns_purchase_price_nonnegative"),
        sa.CheckConstraint(
            "total_estimated_landing_storage_cost >= 0",
            name="ck_cost_breakdowns_total_estimated_nonnegative",
        ),
        sa.ForeignKeyConstraint(["price_update_id"], ["price_updates.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_cost_breakdowns_price_update_id", "cost_breakdowns", ["price_update_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cost_breakdowns_price_update_id", table_name="cost_breakdowns")
    op.drop_table("cost_breakdowns")
