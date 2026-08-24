"""focus active MVP data on Egusi and Kwali Market

Revision ID: 0006_cr03_egusi_kwali
Revises: 0005_stage13_watchlists
Create Date: 2026-08-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_cr03_egusi_kwali"
down_revision: Union[str, Sequence[str], None] = "0005_stage13_watchlists"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _find_named_id(connection, table, canonical_name: str) -> int | None:
    exact_id = connection.execute(
        sa.select(table.c.id).where(table.c.name == canonical_name).order_by(table.c.id).limit(1)
    ).scalar()
    if exact_id is not None:
        return int(exact_id)
    folded_id = connection.execute(
        sa.select(table.c.id)
        .where(sa.func.lower(sa.func.trim(table.c.name)) == canonical_name.casefold())
        .order_by(table.c.id)
        .limit(1)
    ).scalar()
    return int(folded_id) if folded_id is not None else None


def upgrade() -> None:
    connection = op.get_bind()
    commodities = sa.table(
        "commodities",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )
    markets = sa.table(
        "markets",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("state", sa.String()),
        sa.column("country", sa.String()),
        sa.column("market_day", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )

    egusi_id = _find_named_id(connection, commodities, "Egusi")
    if egusi_id is None:
        connection.execute(
            sa.insert(commodities).values(name="Egusi", description=None, is_active=True)
        )
        egusi_id = _find_named_id(connection, commodities, "Egusi")

    kwali_id = _find_named_id(connection, markets, "Kwali Market")
    if kwali_id is None:
        connection.execute(
            sa.insert(markets).values(
                name="Kwali Market",
                state="FCT",
                country="Nigeria",
                market_day="Tuesday",
                description=None,
                is_active=True,
            )
        )
        kwali_id = _find_named_id(connection, markets, "Kwali Market")

    if egusi_id is None or kwali_id is None:
        raise RuntimeError("CR-03 could not establish the approved Egusi/Kwali focus records")

    connection.execute(sa.update(commodities).values(is_active=False))
    connection.execute(
        sa.update(commodities).where(commodities.c.id == egusi_id).values(name="Egusi", is_active=True)
    )
    connection.execute(sa.update(markets).values(is_active=False))
    connection.execute(
        sa.update(markets).where(markets.c.id == kwali_id).values(name="Kwali Market", is_active=True)
    )


def downgrade() -> None:
    # Previous activity flags are business data and cannot be reconstructed
    # safely. A downgrade therefore preserves records and their current flags.
    pass
