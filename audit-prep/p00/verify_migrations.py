"""Disposable PostgreSQL verification with a fixed, positively identified cluster.

No URL/host/database arguments are accepted. Must be invoked with -I -B from
the P00 virtual environment. Never reads dotenv or production credentials.
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import re
import socket
import sys
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
CLUSTER = ROOT / "audit-prep" / "p00" / "runtime" / "postgres-test"
MARKER = CLUSTER.parent / "postgres-test-marker.json"
EMPTY_PASSFILE = CLUSTER.parent / "synthetic-empty-passfile.txt"
HOST, PORT, USER, DATABASE = "127.0.0.1", 55439, "priceyard_test_admin", "priceyard_test"
PURPOSE = "synthetic-only-disposable-priceyard-tests"
_schemas: dict[str, str] = {}
_native_connect = None
_cluster_id = None


def _same_path(value: str, expected: Path) -> bool:
    return os.path.normcase(os.path.abspath(value)) == os.path.normcase(str(expected.resolve()))


def _assert_cluster(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('data_directory'), system_identifier::text FROM pg_control_system()")
        directory, identifier = cursor.fetchone()
    if not _same_path(directory, CLUSTER) or identifier != _cluster_id:
        connection.close()
        raise RuntimeError("Disposable PostgreSQL cluster identity mismatch; no mutations authorized")
    connection.rollback()


def _checked_connection(database: str, schema: str | None = None):
    if database not in {"postgres", DATABASE} or (schema is not None and schema not in _schemas):
        raise RuntimeError("Unapproved test connection")
    arguments = dict(host=HOST, port=PORT, user=USER, dbname=database, connect_timeout=3, sslmode="disable",
                     gssencmode="disable", passfile=str(EMPTY_PASSFILE))
    if schema is not None:
        arguments["options"] = f"-csearch_path={schema}"
    connection = _native_connect(**arguments)
    _assert_cluster(connection)
    return connection


def isolate() -> None:
    global _native_connect, _cluster_id
    if any(name.startswith("app.") for name in sys.modules):
        raise RuntimeError("Guard must precede application imports")
    # This marker was created from offline pg_controldata of the new cluster.
    marker = json.loads(MARKER.read_text(encoding="utf-8-sig"))
    if marker.get("purpose") != PURPOSE or marker.get("port") != PORT or not _same_path(marker.get("data_directory", ""), CLUSTER):
        raise RuntimeError("Missing or invalid disposable-cluster marker")
    _cluster_id = str(marker["system_identifier"])
    if EMPTY_PASSFILE.exists() and EMPTY_PASSFILE.stat().st_size != 0:
        raise RuntimeError("Synthetic empty passfile path is not empty")
    EMPTY_PASSFILE.touch(exist_ok=True)
    retained = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    os.environ.clear()
    os.environ.update(retained)
    os.environ.update(PRICEYARD_TEST_MODE="isolated", APP_ENV="test", DEBUG="false",
                      JWT_SECRET="synthetic-only-testing-credential-" + "x" * 40,
                      FRONTEND_URL="http://127.0.0.1:5173", GOOGLE_CLIENT_ID="synthetic-client")
    os.chdir(MARKER.parent)
    sys.path.insert(0, str(BACKEND))

    def denied(*args, **kwargs):
        raise RuntimeError("External transport is forbidden during PostgreSQL verification")

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_resolver = socket.getaddrinfo

    def permitted(address):
        return isinstance(address, tuple) and address[0] == HOST and address[1] == PORT

    def guarded_connect(connection, address):
        return original_connect(connection, address) if permitted(address) else denied()

    def guarded_connect_ex(connection, address):
        return original_connect_ex(connection, address) if permitted(address) else denied()

    def numeric_resolver(host, port, family=0, type=0, proto=0, flags=0):
        if host != HOST or str(port) != str(PORT):
            return denied()
        return original_resolver(host, port, family, type, proto, flags | socket.AI_NUMERICHOST | socket.AI_NUMERICSERV)

    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex
    socket.getaddrinfo = numeric_resolver

    def audit(event, args):
        if event == "open" and args and isinstance(args[0], (str, bytes)):
            path = Path(os.fsdecode(args[0]))
            if path.name.startswith(".env") or path.suffix.lower() in {".pem", ".key"}:
                raise RuntimeError("Secret-bearing file access forbidden")
    sys.addaudithook(audit)
    import pydantic_settings
    original_settings = pydantic_settings.BaseSettings.__init__

    def without_dotenv(self, *args, **kwargs):
        kwargs["_env_file"] = None
        original_settings(self, *args, **kwargs)
    pydantic_settings.BaseSettings.__init__ = without_dotenv

    import psycopg
    from psycopg.conninfo import conninfo_to_dict
    _native_connect = psycopg.connect

    def restricted_native(conninfo="", **kwargs):
        from psycopg.adapt import AdaptersMap
        adapter_context = kwargs.get("context")
        if adapter_context is not None and not isinstance(adapter_context, AdaptersMap):
            raise RuntimeError("Unsupported PostgreSQL adapter context")
        arguments = conninfo_to_dict(conninfo, **{key: value for key, value in kwargs.items() if key != "context"})
        options = arguments.get("options", "")
        schema = options.removeprefix("-csearch_path=")
        allowed_keys = {"host", "port", "user", "dbname", "connect_timeout", "sslmode", "gssencmode", "passfile", "options"}
        if (set(arguments) - allowed_keys or arguments.get("host") != HOST or str(arguments.get("port")) != str(PORT)
            or arguments.get("user") != USER or arguments.get("dbname") != DATABASE
            or arguments.get("sslmode") != "disable" or str(arguments.get("connect_timeout")) != "3"
            or arguments.get("gssencmode") != "disable" or arguments.get("passfile") != str(EMPTY_PASSFILE)
            or options != f"-csearch_path={schema}" or schema not in _schemas):
            raise RuntimeError("Native PostgreSQL transport rejected outside approved synthetic namespace")
        connection = _native_connect(conninfo, **kwargs)
        _assert_cluster(connection)
        return connection

    psycopg.connect = restricted_native
    import sqlalchemy
    from sqlalchemy.engine import make_url
    engine_module = importlib.import_module("sqlalchemy.engine.create")
    original_engine = engine_module.create_engine

    def safe_engine(url, *args, **kwargs):
        target = make_url(url)
        schema = target.query.get("options", "").removeprefix("-csearch_path=")
        if (set(target.query) != {"options", "connect_timeout", "sslmode"} or target.query.get("sslmode") != "disable"
            or target.query.get("connect_timeout") != "3" or target.drivername != "postgresql+psycopg" or target.host != HOST or target.port != PORT
            or target.database != DATABASE or target.username != USER or target.password
            or target.query.get("options") != f"-csearch_path={schema}" or schema not in _schemas):
            raise RuntimeError("Only the positively identified disposable PostgreSQL namespace is allowed")
        if "connect_args" in kwargs or "creator" in kwargs:
            raise RuntimeError("Custom native transport overrides are forbidden")
        kwargs["connect_args"] = {"passfile": str(EMPTY_PASSFILE), "gssencmode": "disable"}
        return original_engine(url, *args, **kwargs)

    sqlalchemy.create_engine = safe_engine
    sqlalchemy.engine.create_engine = safe_engine
    engine_module.create_engine = safe_engine


def provision_database() -> None:
    with _checked_connection("postgres") as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = %s", (DATABASE,))
            existing = cursor.fetchone()
            expected = f"{PURPOSE}:{_cluster_id}"
            if existing is None:
                cursor.execute('CREATE DATABASE "priceyard_test"')
                from psycopg import sql
                cursor.execute(sql.SQL('COMMENT ON DATABASE "priceyard_test" IS {}').format(sql.Literal(expected)))
            elif existing[0] != expected:
                raise RuntimeError("Existing database lacks this disposable cluster's test marker")


def create_schema() -> str:
    schema, token = "py_test_" + uuid.uuid4().hex, uuid.uuid4().hex
    _schemas[schema] = token
    from psycopg import sql
    with _checked_connection(DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
            cursor.execute(sql.SQL("CREATE TABLE {}.p00_run_marker (token text PRIMARY KEY)").format(sql.Identifier(schema)))
            cursor.execute(sql.SQL("INSERT INTO {}.p00_run_marker VALUES (%s)").format(sql.Identifier(schema)), (token,))
    return schema


def schema_url(schema: str):
    if schema not in _schemas:
        raise RuntimeError("Unknown disposable namespace")
    from sqlalchemy.engine import URL
    return URL.create("postgresql+psycopg", username=USER, host=HOST, port=PORT, database=DATABASE,
                      query={"options": f"-csearch_path={schema}", "connect_timeout": "3", "sslmode": "disable"})


def migrate(schema: str, revision="head") -> None:
    from alembic import command
    from alembic.config import Config
    from app.config import get_settings
    os.environ["DATABASE_URL"] = str(schema_url(schema))
    get_settings.cache_clear()
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    command.upgrade(config, revision)


def cleanup_schema(schema: str) -> None:
    if not re.fullmatch(r"py_test_[0-9a-f]{32}", schema) or schema not in _schemas:
        raise RuntimeError("Cleanup denied outside this run")
    from psycopg import sql
    with _checked_connection(DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT token FROM {}.p00_run_marker").format(sql.Identifier(schema)))
            if cursor.fetchone() != (_schemas[schema],):
                raise RuntimeError("Cleanup marker mismatch")
            cursor.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    del _schemas[schema]


def main() -> int:
    isolate()
    provision_database()
    # Import only after all transport/settings/native-driver guards exist.
    suite = unittest.defaultTestLoader.discover(str(BACKEND / "tests"), pattern="postgres_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                      "runtime": "positively identified disposable PostgreSQL; no external service access"}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Tests import this module name; share the exact guard/namespace state.
    sys.modules["verify_migrations"] = sys.modules[__name__]
    raise SystemExit(main())
