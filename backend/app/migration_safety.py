"""Read-only protection against replaying legacy business-data migrations."""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

REVIEWED_BASELINES = frozenset({"0021_feedback_screenshot", "0022_login_revocation"})


def assert_safe_migration_start(connection: Connection, current_heads: tuple[str, ...]) -> None:
    # The approved additive0022 path starts from the original0021 application.
    # No flag or automatic stamp bypasses review of older/unknown populated data.
    if len(current_heads) == 1 and current_heads[0] in REVIEWED_BASELINES:
        return
    quote = connection.dialect.identifier_preparer.quote
    for table in inspect(connection).get_table_names():
        if table == "alembic_version":
            continue
        if connection.execute(text("SELECT 1 FROM " + quote(table) + " LIMIT 1")).first() is not None:
            raise RuntimeError("Populated legacy or unversioned database requires a reviewed migration; no changes were applied")
