"""add testimonial publication fields to feedback

Revision ID: 0013_add_testimonial
Revises: 0012_add_trial_reminder
Create Date: 2026-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0013_add_testimonial"
down_revision: Union[str, Sequence[str], None] = "0012_add_trial_reminder"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "feedback",
        sa.Column("is_public_testimonial", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "feedback",
        sa.Column("testimonial_display_name", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("feedback", "testimonial_display_name")
    op.drop_column("feedback", "is_public_testimonial")
