"""Owner-approved 0022 rehearsal; cached protected export, never a source connection.

The offline Alembic environment deliberately does not import app configuration,
read dotenv files, or create a database connection. The runtime callback receives
only the existing network-disabled, RAM-only PostgreSQL target's SQL interface.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "0021_feedback_screenshot"
TARGET = "0022_login_revocation"
MIGRATION = ROOT / "backend/migrations/versions/0022_login_revocation.py"
OFFLINE_ENV = """from alembic import context
if not context.is_offline_mode():
    raise RuntimeError('This rehearsal compiler never connects to a database')
context.configure(dialect_name='postgresql', literal_binds=True, transactional_ddl=True)
with context.begin_transaction():
    context.run_migrations()
"""


def prepare():
    from alembic import command
    from alembic.config import Config

    migration = runpy.run_path(str(MIGRATION))
    if migration["revision"] != TARGET or migration["down_revision"] != BASELINE:
        raise RuntimeError("Migration chain differs from approved 0021-to-0022 scope")
    try:
        migration["downgrade"]()
    except RuntimeError as exc:
        if str(exc) != "Dropping login revocation records can restore revoked credentials; reviewed recovery is required":
            raise RuntimeError("Downgrade refusal differs") from exc
    else:
        raise RuntimeError("Destructive security downgrade is no longer refused")
    output = io.StringIO()
    with tempfile.TemporaryDirectory(prefix="priceyard-0022-offline-code-") as temporary:
        (Path(temporary) / "env.py").write_text(OFFLINE_ENV, encoding="utf-8")
        config = Config(output_buffer=output)
        config.set_main_option("script_location", temporary)
        config.set_main_option("version_locations", str(MIGRATION.parent))
        command.upgrade(config, BASELINE + ":" + TARGET, sql=True)
    sql = output.getvalue()
    if sql.count("BEGIN;") != 1 or sql.count("COMMIT;") != 1:
        raise RuntimeError("Expected exactly one transactional Alembic upgrade")
    if re.search(r"(?mi)^\s*(DROP|DELETE|TRUNCATE)\s", sql):
        raise RuntimeError("Non-additive migration statement requires review")
    if "UPDATE alembic_version SET version_num='0022_login_revocation'" not in sql:
        raise RuntimeError("Expected exact Alembic version transition")
    return sql, hashlib.sha256(MIGRATION.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    sql, migration_sha = prepare()
    if args.prepare_only:
        print(json.dumps({"offline_compilation": "passed", "downgrade_refusal": "passed",
                          "migration_sha256": migration_sha,
                          "generated_sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
                          "database_connections": 0, "migrations_run": 0}))
        return
    gate = json.loads((ROOT / "docs/PY35_ACTUAL_RELEASE_GATES.json").read_text())
    backup = next(item for item in gate["gates"] if item["id"] == "actual_backup_restoration")
    if backup["off_computer_archive_copy_verified"] is not True:
        raise RuntimeError("Verified independent encrypted backup retrieval is required")
    import rehearse_0022_checks as checks
    from restore_verified_supabase_ram import main as protected_restore

    checks.UPGRADE_SQL = sql
    checks.MIGRATION_SHA256 = migration_sha
    checks.DOWNGRADE_REFUSAL_VERIFIED = True
    checks.run.purpose = "0022_local_only"
    protected_restore(rehearsal=checks.run)


if __name__ == "__main__":
    main()
