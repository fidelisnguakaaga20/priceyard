"""Owner-approved: admin-named cost lines on cost breakdowns.

Existing non-zero fixed costs become named lines (e.g. "Transport") and their
fixed columns are zeroed, so every saved total stays exactly the same.

Revision ID: 0023_cost_breakdown_items
Revises: 0022_login_revocation
Create Date: 2026-11-04
"""
import json
from decimal import Decimal

from alembic import op
import sqlalchemy as sa

revision = "0023_cost_breakdown_items"
down_revision = "0022_login_revocation"
branch_labels = None
depends_on = None

FIXED = (
    ("transport", "Transport"),
    ("warehouse", "Warehouse"),
    ("security", "Security"),
    ("market_charges", "Market charges"),
    ("loading_offloading", "Loading/offloading"),
    ("other_costs", "Other costs"),
)


def upgrade():
    op.add_column("cost_breakdowns", sa.Column("cost_items", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    bind = op.get_bind()
    columns = ", ".join(column for column, _ in FIXED)
    for row in bind.execute(sa.text(f"SELECT id, {columns} FROM cost_breakdowns")).mappings().all():
        items = [{"name": label, "amount": f"{Decimal(row[column]):.2f}"}
                 for column, label in FIXED if row[column] and Decimal(row[column]) > 0]
        if not items:
            continue
        zeroed = ", ".join(f"{column} = 0" for column, _ in FIXED)
        bind.execute(sa.text(f"UPDATE cost_breakdowns SET cost_items = :items, {zeroed} WHERE id = :id")
                     .bindparams(sa.bindparam("items", type_=sa.JSON())), {"items": items, "id": row["id"]})


def downgrade():
    bind = op.get_bind()
    labels = {label: column for column, label in FIXED}
    for row in bind.execute(sa.text("SELECT id, cost_items FROM cost_breakdowns")).mappings().all():
        items = row["cost_items"] if not isinstance(row["cost_items"], str) else json.loads(row["cost_items"])
        if not items:
            continue
        values = {column: Decimal("0") for column, _ in FIXED}
        for item in items:
            values[labels.get(item["name"], "other_costs")] += Decimal(item["amount"])
        assignments = ", ".join(f"{column} = {column} + :{column}" for column in values)
        statement = sa.text(f"UPDATE cost_breakdowns SET {assignments} WHERE id = :id").bindparams(
            *(sa.bindparam(column, type_=sa.Numeric(14, 2)) for column in values))
        bind.execute(statement, {**values, "id": row["id"]})
    op.drop_column("cost_breakdowns", "cost_items")
