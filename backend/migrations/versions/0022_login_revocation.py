"""Internal-only login revocation; no business-field or policy change."""
from alembic import op
import sqlalchemy as sa

revision = "0022_login_revocation"
down_revision = "0021_feedback_screenshot"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("auth_version", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.create_table("revoked_access_tokens", sa.Column("token_hash", sa.String(64), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_revoked_access_tokens_user_id", "revoked_access_tokens", ["user_id"])
    op.create_index("ix_revoked_access_tokens_expires_at", "revoked_access_tokens", ["expires_at"])


def downgrade():
    raise RuntimeError("Dropping login revocation records can restore revoked credentials; reviewed recovery is required")
