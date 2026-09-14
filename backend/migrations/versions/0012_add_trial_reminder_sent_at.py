"""add trial_reminder_sent_at to subscriptions

Revision ID: 0012_add_trial_reminder
Revises: 0011_add_market_image_url
Create Date: 2026-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0012_add_trial_reminder"
down_revision: Union[str, Sequence[str], None] = "0011_add_market_image_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("trial_reminder_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "trial_reminder_sent_at")
