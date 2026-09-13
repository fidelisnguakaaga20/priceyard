"""add optional image_url to markets

Revision ID: 0011_add_market_image_url
Revises: 0010_add_commodity_upcoming
Create Date: 2026-09-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011_add_market_image_url"
down_revision: Union[str, Sequence[str], None] = "0010_add_commodity_upcoming"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("markets", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("markets", "image_url")
