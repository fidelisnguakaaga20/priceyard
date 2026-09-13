"""add optional google sign-in fields to users

Revision ID: 0009_add_google_sign_in
Revises: 0008_add_commodity_image_url
Create Date: 2026-09-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009_add_google_sign_in"
down_revision: Union[str, Sequence[str], None] = "0008_add_commodity_image_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(length=20), nullable=False, server_default="local"),
    )
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "google_id")
