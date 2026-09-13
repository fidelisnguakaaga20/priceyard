"""add optional upcoming-product fields to commodities

Revision ID: 0010_add_commodity_upcoming
Revises: 0009_add_google_sign_in
Create Date: 2026-09-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010_add_commodity_upcoming"
down_revision: Union[str, Sequence[str], None] = "0009_add_google_sign_in"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "commodities",
        sa.Column("is_upcoming", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("commodities", sa.Column("expected_available_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("commodities", "expected_available_date")
    op.drop_column("commodities", "is_upcoming")
