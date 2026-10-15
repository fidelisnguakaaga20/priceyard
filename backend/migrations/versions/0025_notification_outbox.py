"""Durable delivery without changes to existing business records."""
from alembic import op
import sqlalchemy as sa
revision = "0025_notification_outbox"
down_revision = "0024_price_integrity"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("notification_jobs", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("deduplication_key", sa.String(160), nullable=False, unique=True),
        sa.Column("channel", sa.String(20), nullable=False), sa.Column("recipient", sa.String(320), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False), sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False), sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("error_code", sa.String(80)),
        sa.Column("lease_token", sa.String(36)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_notification_jobs_status", "notification_jobs", ["status"])
    op.create_index("ix_notification_jobs_available_at", "notification_jobs", ["available_at"])
    # Existing monetary targets are preserved. NULL measurement fields keep
    # ambiguous alerts paused until their owner explicitly confirms the basis.
    op.add_column("watchlists", sa.Column("target_unit", sa.String(100), nullable=True))
    op.add_column("watchlists", sa.Column("target_bag_size", sa.String(100), nullable=True))
    op.add_column("watchlists", sa.Column("target_commodity_type", sa.String(150), nullable=True))
    op.add_column("watchlists", sa.Column("target_grade", sa.String(100), nullable=True))

def downgrade():
    raise RuntimeError("Outbox rollback requires preserving pending delivery evidence; use the documented forward recovery procedure")
