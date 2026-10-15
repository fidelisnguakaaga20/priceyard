"""Add price/cost provenance and safe identity constraints without rewriting history.

Revision ID: 0024_price_integrity
Revises: 0023_payment_integrity
"""

from alembic import op
import sqlalchemy as sa


revision = "0024_price_integrity"
down_revision = "0023_payment_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    # No automatic merge, relabelling, deletion or timezone repair of legacy data.
    # Abort before DDL if identity/range conflicts require a reviewed data decision.
    for query, message in (
        ("SELECT 1 FROM commodities GROUP BY lower(trim(name)) HAVING count(*) > 1 LIMIT 1",
         "Commodity normalized-name duplicates require a reviewed resolution before migration"),
        ("SELECT 1 FROM markets GROUP BY lower(trim(name)), lower(trim(coalesce(state, ''))) HAVING count(*) > 1 LIMIT 1",
         "Market normalized-name/state duplicates require a reviewed resolution before migration"),
        ("SELECT 1 FROM price_updates WHERE (previous_price_low IS NULL) <> (previous_price_high IS NULL) "
         "OR previous_price_low < 0 OR previous_price_high < previous_price_low LIMIT 1",
         "Historical previous-price ranges require review before adding the constraint"),
    ):
        if connection.execute(sa.text(query)).first() is not None:
            raise RuntimeError(message)

    op.add_column("price_updates", sa.Column("grade", sa.String(100), nullable=True))
    op.add_column("price_updates", sa.Column("previous_price_update_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_price_updates_predecessor", "price_updates", "price_updates",
                          ["previous_price_update_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_price_updates_previous_price_update_id", "price_updates", ["previous_price_update_id"])
    op.drop_constraint("ck_price_updates_status", "price_updates", type_="check")
    op.create_check_constraint("ck_price_updates_status", "price_updates", "status IN ('pending', 'approved', 'rejected', 'withdrawn')")
    op.create_check_constraint("ck_price_updates_previous_range", "price_updates",
        "(previous_price_low IS NULL AND previous_price_high IS NULL) OR "
        "(previous_price_low IS NOT NULL AND previous_price_high IS NOT NULL "
        "AND previous_price_low >= 0 AND previous_price_high >= previous_price_low)")
    op.create_index("ix_price_updates_current_series", "price_updates",
                    ["status", "commodity_id", "market_id", "update_date_time", "id"])
    op.create_index("ix_price_updates_approved_measurement_series", "price_updates",
        ["commodity_id", "market_id", sa.text("lower(trim(coalesce(unit, '')))"),
         sa.text("lower(trim(coalesce(bag_size, '')))"), sa.text("lower(trim(coalesce(commodity_type, '')))"),
         sa.text("lower(trim(coalesce(grade, '')))"), sa.text("update_date_time DESC"), sa.text("id DESC")],
        postgresql_where=sa.text("status = 'approved'"))
    op.create_table("price_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_update_id", sa.Integer(), sa.ForeignKey("price_updates.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("original_values", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_price_revisions_price_update_id", "price_revisions", ["price_update_id"])
    for field, length in (("unit", 100), ("bag_size", 100), ("commodity_type", 150), ("grade", 100)):
        op.add_column("cost_breakdowns", sa.Column(field, sa.String(length), nullable=True))
    op.add_column("cost_breakdowns", sa.Column("reference_date_time", sa.DateTime(timezone=True), nullable=True))
    for table in ("cost_breakdowns", "market_signals", "quality_signals"):
        op.add_column(table, sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("uq_commodities_normalized_name", "commodities", [sa.text("lower(trim(name))")], unique=True)
    op.create_index("uq_markets_normalized_scope", "markets",
                    [sa.text("lower(trim(name))"), sa.text("lower(trim(coalesce(state, '')))" )], unique=True)


def downgrade() -> None:
    # Dropping revisions, measurement provenance, or withdrawn states would
    # destroy evidence. Roll back application code only to a compatible version;
    # a schema rollback requires a separately reviewed preservation procedure.
    raise RuntimeError("Automatic downgrade refused: retain price revisions and measurement provenance")
