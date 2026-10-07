"""re-point cost_breakdowns at commodity+market instead of one price_update

Revision ID: 0020_cost_breakdown_cm
Revises: 0019_add_target_price
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0020_cost_breakdown_cm"
down_revision: Union[str, Sequence[str], None] = "0019_add_target_price"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cost_breakdowns", sa.Column("commodity_id", sa.Integer(), nullable=True))
    op.add_column("cost_breakdowns", sa.Column("market_id", sa.Integer(), nullable=True))

    # Backfill from whichever single price_update each row used to be pinned to, so
    # existing cost data is preserved under the new, sturdier commodity+market linkage.
    op.execute(
        """
        UPDATE cost_breakdowns
        SET commodity_id = price_updates.commodity_id,
            market_id = price_updates.market_id
        FROM price_updates
        WHERE cost_breakdowns.price_update_id = price_updates.id
        """
    )

    op.alter_column("cost_breakdowns", "commodity_id", nullable=False)
    op.alter_column("cost_breakdowns", "market_id", nullable=False)

    op.create_foreign_key(
        "fk_cost_breakdowns_commodity_id", "cost_breakdowns", "commodities", ["commodity_id"], ["id"], ondelete="RESTRICT"
    )
    op.create_foreign_key(
        "fk_cost_breakdowns_market_id", "cost_breakdowns", "markets", ["market_id"], ["id"], ondelete="RESTRICT"
    )
    op.create_index("ix_cost_breakdowns_commodity_id", "cost_breakdowns", ["commodity_id"])
    op.create_index("ix_cost_breakdowns_market_id", "cost_breakdowns", ["market_id"])

    op.drop_index("ix_cost_breakdowns_price_update_id", table_name="cost_breakdowns")
    op.drop_constraint("cost_breakdowns_price_update_id_fkey", "cost_breakdowns", type_="foreignkey")
    op.drop_column("cost_breakdowns", "price_update_id")


def downgrade() -> None:
    op.add_column("cost_breakdowns", sa.Column("price_update_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE cost_breakdowns
        SET price_update_id = (
            SELECT id FROM price_updates
            WHERE price_updates.commodity_id = cost_breakdowns.commodity_id
              AND price_updates.market_id = cost_breakdowns.market_id
            ORDER BY price_updates.update_date_time DESC
            LIMIT 1
        )
        """
    )
    op.alter_column("cost_breakdowns", "price_update_id", nullable=False)
    op.create_foreign_key(
        "cost_breakdowns_price_update_id_fkey", "cost_breakdowns", "price_updates", ["price_update_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_cost_breakdowns_price_update_id", "cost_breakdowns", ["price_update_id"])

    op.drop_index("ix_cost_breakdowns_market_id", table_name="cost_breakdowns")
    op.drop_index("ix_cost_breakdowns_commodity_id", table_name="cost_breakdowns")
    op.drop_constraint("fk_cost_breakdowns_market_id", "cost_breakdowns", type_="foreignkey")
    op.drop_constraint("fk_cost_breakdowns_commodity_id", "cost_breakdowns", type_="foreignkey")
    op.drop_column("cost_breakdowns", "market_id")
    op.drop_column("cost_breakdowns", "commodity_id")
