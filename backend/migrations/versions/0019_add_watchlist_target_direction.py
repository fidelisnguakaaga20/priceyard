"""add target_direction to watchlists for target-price alerts

Revision ID: 0019_add_target_price
Revises: 0018_add_price_flags
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0019_add_target_price"
down_revision: Union[str, Sequence[str], None] = "0018_add_price_flags"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("watchlists", sa.Column("target_direction", sa.String(length=20), nullable=True))
    op.create_check_constraint(
        "ck_watchlists_target_price_direction_paired",
        "watchlists",
        "(target_price IS NULL) = (target_direction IS NULL)",
    )
    op.create_check_constraint(
        "ck_watchlists_target_direction_valid",
        "watchlists",
        "target_direction IS NULL OR target_direction IN ('at_or_below', 'at_or_above')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_watchlists_target_direction_valid", "watchlists", type_="check")
    op.drop_constraint("ck_watchlists_target_price_direction_paired", "watchlists", type_="check")
    op.drop_column("watchlists", "target_direction")
