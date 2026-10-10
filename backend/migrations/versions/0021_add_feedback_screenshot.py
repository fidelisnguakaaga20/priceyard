"""add optional screenshot to feedback

Revision ID: 0021_feedback_screenshot
Revises: 0020_cost_breakdown_cm
Create Date: 2026-10-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0021_feedback_screenshot"
down_revision: Union[str, Sequence[str], None] = "0020_cost_breakdown_cm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("feedback", sa.Column("screenshot_data", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("feedback", "screenshot_data")
