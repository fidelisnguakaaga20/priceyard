"""add optional image_url to commodities

Revision ID: 0008_add_commodity_image_url
Revises: 0007_auth01_password_reset
Create Date: 2026-09-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_add_commodity_image_url"
down_revision: Union[str, Sequence[str], None] = "0007_auth01_password_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("commodities", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("commodities", "image_url")
