from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session


def lock_catalog_identity(db: Session, kind: Literal["commodity", "market"]) -> None:
    """Serialize existing normalized-name checks until the audited write commits."""
    key = {"commodity": 4, "market": 5}[kind]
    if db.get_bind().dialect.name == "postgresql":
        # Transaction-owned, cross-process and automatically released on rollback.
        # No new columns/indexes or changes to existing naming/market-state rules.
        db.execute(text("SELECT pg_advisory_xact_lock(741523, :catalog_key)"), {"catalog_key": key})
