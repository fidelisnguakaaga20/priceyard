"""add activity_events table

Revision ID: 0016_add_activity_events
Revises: 0015_add_payments
Create Date: 2026-10-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0016_add_activity_events"
down_revision: Union[str, Sequence[str], None] = "0015_add_payments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=30), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("seen", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activity_events_event_type", "activity_events", ["event_type"])
    op.create_index("ix_activity_events_seen", "activity_events", ["seen"])


def downgrade() -> None:
    op.drop_index("ix_activity_events_seen", table_name="activity_events")
    op.drop_index("ix_activity_events_event_type", table_name="activity_events")
    op.drop_table("activity_events")
