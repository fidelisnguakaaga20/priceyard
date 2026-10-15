"""Add payment/entitlement evidence without guessing prior activation outcomes.

Revision ID: 0023_payment_integrity
Revises: 0022_security_sessions
"""

from alembic import op
import sqlalchemy as sa

revision = "0023_payment_integrity"
down_revision = "0022_security_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("paid_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("manual_grant", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("subscriptions", sa.Column("cancellation_requested_at", sa.DateTime(timezone=True), nullable=True))
    # Legacy access included the complete UTC end_date. Preserve that exact cutoff.
    op.execute("UPDATE subscriptions SET paid_expires_at = ((end_date + 1)::timestamp AT TIME ZONE 'UTC') WHERE end_date IS NOT NULL")
    op.execute("UPDATE subscriptions SET manual_grant = TRUE WHERE status = 'active' AND end_date IS NULL")

    op.add_column("payments", sa.Column("duration_days", sa.Integer(), nullable=True))
    op.execute("UPDATE payments SET duration_days = CASE WHEN plan = 'seasonal' THEN 90 ELSE 30 END")
    op.alter_column("payments", "duration_days", nullable=False)
    op.create_check_constraint("ck_payments_duration", "payments", "duration_days > 0")
    op.add_column("payments", sa.Column("expected_customer_email", sa.String(320), nullable=True))
    op.add_column("payments", sa.Column("provider_environment", sa.String(10), nullable=True))
    for name in ("confirmed_at", "entitlement_applied_at", "granted_expires_at"):
        op.add_column("payments", sa.Column(name, sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("requires_reconciliation", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("payments", sa.Column("reconciliation_resolution", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("reconciliation_error", sa.String(100), nullable=True))
    # Old code committed success before activation. Neither infer application nor
    # reapply all historical purchases; explicit review is necessary.
    op.execute("UPDATE payments SET requires_reconciliation = TRUE WHERE status = 'success'")
    op.create_index(
        "uq_payments_applied_provider_id", "payments", ["paystack_transaction_id"], unique=True,
        postgresql_where=sa.text("entitlement_applied_at IS NOT NULL"),
    )
    op.create_table(
        "entitlement_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disposition", sa.String(30), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("duration_days > 0", name="ck_entitlement_grants_duration"),
    )
    op.create_index("ix_entitlement_grants_user_id", "entitlement_grants", ["user_id"])
    op.create_table(
        "referral_rewards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referred_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("referrer_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qualifying_payment_id", sa.Integer(), sa.ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("reward_days", sa.Integer(), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("reward_days = 7", name="ck_referral_rewards_days"),
    )
    op.create_index("ix_referral_rewards_referrer_user_id", "referral_rewards", ["referrer_user_id"])


def downgrade() -> None:
    raise RuntimeError(
        "Automatic downgrade would discard payment/referral evidence and shorten "
        "precise entitlements. Restore a verified backup or use a reviewed forward repair."
    )
