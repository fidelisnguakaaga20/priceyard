"""create MVP database foundation

Revision ID: 0001_create_mvp_foundation
Revises:
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_mvp_foundation"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)

    op.create_table(
        "commodities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_commodities_name"),
    )
    op.create_index("ix_commodities_name", "commodities", ["name"], unique=False)
    op.create_index("ix_commodities_is_active", "commodities", ["is_active"], unique=False)

    op.create_table(
        "markets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("market_day", sa.String(length=30), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_markets_name", "markets", ["name"], unique=False)
    op.create_index("ix_markets_is_active", "markets", ["is_active"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_name", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("payment_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('free', 'trial', 'active', 'expired', 'cancelled')", name="ck_subscriptions_status"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_subscriptions_user_id"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=False)
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"], unique=False)

    op.create_table(
        "price_updates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("price_low", sa.Numeric(14, 2), nullable=False),
        sa.Column("price_high", sa.Numeric(14, 2), nullable=False),
        sa.Column("average_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("previous_price_low", sa.Numeric(14, 2), nullable=True),
        sa.Column("previous_price_high", sa.Numeric(14, 2), nullable=True),
        sa.Column("unit", sa.String(length=100), nullable=False),
        sa.Column("bag_size", sa.String(length=100), nullable=True),
        sa.Column("commodity_type", sa.String(length=150), nullable=True),
        sa.Column("market_day", sa.String(length=30), nullable=True),
        sa.Column("time_of_day", sa.String(length=20), nullable=True),
        sa.Column("movement", sa.String(length=20), nullable=False),
        sa.Column("confidence_level", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_1", sa.String(length=255), nullable=True),
        sa.Column("source_2", sa.String(length=255), nullable=True),
        sa.Column("update_date_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_outdated", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("possible_meaning", sa.Text(), nullable=True),
        sa.Column("suggested_action", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price_low >= 0", name="ck_price_updates_price_low_nonnegative"),
        sa.CheckConstraint("price_high >= price_low", name="ck_price_updates_price_range"),
        sa.CheckConstraint("average_price IS NULL OR (average_price >= price_low AND average_price <= price_high)", name="ck_price_updates_average_in_range"),
        sa.CheckConstraint("movement IN ('up', 'down', 'stable', 'unknown')", name="ck_price_updates_movement"),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_price_updates_status"),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
    )
    for column in ("commodity_id", "market_id", "movement", "update_date_time", "is_outdated", "status", "created_by", "approved_by"):
        op.create_index(f"ix_price_updates_{column}", "price_updates", [column], unique=False)

    op.create_table(
        "market_signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("price_update_id", sa.Integer(), nullable=True),
        sa.Column("signal_type", sa.String(length=100), nullable=False),
        sa.Column("signal_description", sa.Text(), nullable=False),
        sa.Column("possible_meaning", sa.Text(), nullable=True),
        sa.Column("suggested_action", sa.String(length=50), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["price_update_id"], ["price_updates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    for column in ("commodity_id", "market_id", "price_update_id", "signal_type", "created_by"):
        op.create_index(f"ix_market_signals_{column}", "market_signals", [column], unique=False)

    op.create_table(
        "quality_signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commodity_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("price_update_id", sa.Integer(), nullable=True),
        sa.Column("quality_status", sa.String(length=100), nullable=True),
        sa.Column("moisture_status", sa.String(length=100), nullable=True),
        sa.Column("storage_readiness", sa.String(length=100), nullable=True),
        sa.Column("risk_note", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["commodity_id"], ["commodities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["price_update_id"], ["price_updates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    for column in ("commodity_id", "market_id", "price_update_id", "created_by"):
        op.create_index(f"ix_quality_signals_{column}", "quality_signals", [column], unique=False)

    op.create_table(
        "faq_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    for column in ("category", "is_published", "created_by"):
        op.create_index(f"ix_faq_items_{column}", "faq_items", [column], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("table_name", sa.String(length=100), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    for column in ("user_id", "action", "table_name", "record_id"):
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("price_usefulness", sa.Text(), nullable=True),
        sa.Column("price_accuracy", sa.Text(), nullable=True),
        sa.Column("missing_market_request", sa.Text(), nullable=True),
        sa.Column("missing_commodity_request", sa.Text(), nullable=True),
        sa.Column("complaint_or_suggestion", sa.Text(), nullable=True),
        sa.Column("continue_using_feedback", sa.Boolean(), nullable=True),
        sa.Column("willingness_to_pay_feedback", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_feedback_rating"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"], unique=False)
    op.create_index("ix_feedback_rating", "feedback", ["rating"], unique=False)


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("audit_logs")
    op.drop_table("faq_items")
    op.drop_table("quality_signals")
    op.drop_table("market_signals")
    op.drop_table("price_updates")
    op.drop_table("subscriptions")
    op.drop_table("markets")
    op.drop_table("commodities")
    op.drop_table("users")
