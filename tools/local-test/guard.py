"""Fail-closed, synthetic-only backend verification; never load real dotenv files."""
from __future__ import annotations

import argparse
import importlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import threading
import time
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"


def isolate() -> None:
    if any(name.startswith("app.") for name in sys.modules):
        raise RuntimeError("Isolation must precede application imports")
    preserved = {name: os.environ[name] for name in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if name in os.environ}
    os.environ.clear()
    os.environ.update(preserved)
    os.environ.update({
        "PRICEYARD_TEST_MODE": "isolated", "APP_ENV": "test", "DEBUG": "false",
        "FRONTEND_URL": "http://127.0.0.1:5173", "CORS_ORIGINS": "http://127.0.0.1:5173",
        "JWT_SECRET": "synthetic-only-not-a-production-credential-" + "x" * 32,
        "GOOGLE_CLIENT_ID": "synthetic-client", "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    })
    os.chdir(Path(__file__).resolve().parent)
    sys.path.insert(0, str(BACKEND))

    def denied(*args, **kwargs):
        raise RuntimeError("External transport is forbidden in the synthetic test runner")

    # No TCP/DNS is required by in-process API and SQLite tests. PostgreSQL and
    # browser verification use a separately isolated runtime, never this guard.
    original_connect = socket.socket.connect
    original_socketpair = socket.socketpair
    pair_context = threading.local()

    def pair_connect(connection, address):
        if getattr(pair_context, "creating", False) and isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(connection, address)
        return denied()

    def internal_pair(*args, **kwargs):
        # Windows asyncio uses a loopback pair as its internal wake-up channel.
        # Permit only pair creation in this thread, never arbitrary loopback/API traffic.
        pair_context.creating = True
        try:
            return original_socketpair(*args, **kwargs)
        finally:
            pair_context.creating = False

    socket.socketpair = internal_pair
    socket.socket.connect = pair_connect
    socket.socket.connect_ex = denied
    socket.create_connection = denied
    socket.getaddrinfo = denied
    socket.socket.sendto = denied
    original_bind = socket.socket.bind
    original_listen = socket.socket.listen

    def local_bind(connection, address):
        if getattr(pair_context, "creating", False) and isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_bind(connection, address)
        if address == ("127.0.0.1", 55446):
            return original_bind(connection, address)
        return denied()

    def local_listen(connection, *args):
        if getattr(pair_context, "creating", False) or connection.getsockname()[:2] == ("127.0.0.1", 55446):
            return original_listen(connection, *args)
        return denied()

    socket.socket.bind = local_bind
    socket.socket.listen = local_listen
    import sqlite3
    original_sqlite_connect = sqlite3.connect

    def memory_connect(database, *args, **kwargs):
        if str(database) != ":memory:":
            return denied()
        return original_sqlite_connect(database, *args, **kwargs)

    sqlite3.connect = memory_connect
    import sqlalchemy
    original_create_engine = sqlalchemy.create_engine

    def safe_engine(url, *args, **kwargs):
        if str(url) != "sqlite+pysqlite:///:memory:":
            raise RuntimeError("Only a fresh in-memory synthetic database is allowed")
        # Share one fresh memory database across API worker threads. Original
        # application's PostgreSQL pool options do not apply to SQLite.
        from sqlalchemy.pool import StaticPool
        for option in ("pool_size", "max_overflow"):
            kwargs.pop(option, None)
        kwargs.update(poolclass=StaticPool, connect_args={"check_same_thread": False})
        return original_create_engine(url, *args, **kwargs)

    sqlalchemy.create_engine = safe_engine
    sqlalchemy.engine.create_engine = safe_engine
    importlib.import_module("sqlalchemy.engine.create").create_engine = safe_engine
    # Native libpq bypasses Python's socket hooks. SQLite verification must
    # reject it before driver code can resolve or connect to any address.
    import psycopg
    psycopg.connect = denied
    psycopg.Connection.connect = denied
    psycopg.AsyncConnection.connect = denied
    import subprocess
    subprocess.Popen = denied
    os.system = denied
    import pydantic_settings
    original_init = pydantic_settings.BaseSettings.__init__

    def settings_without_dotenv(self, *args, **kwargs):
        kwargs["_env_file"] = None
        original_init(self, *args, **kwargs)

    pydantic_settings.BaseSettings.__init__ = settings_without_dotenv

    # Auditable defense against application/file-reader attempts to open dotenv,
    # credentials or application-owned database files during test discovery.
    def audit(event, args):
        if event == "open" and args and isinstance(args[0], (str, bytes)):
            value = Path(os.fsdecode(args[0]))
            if (value.name.startswith(".env") or value.suffix.lower() in {".pem", ".key"}
                or value.name.lower() in {"credentials", ".npmrc", ".pgpass", "pgpass.conf"}
                or any(part.lower() in {".aws", ".ssh", ".azure"} for part in value.parts)):
                raise RuntimeError("Secret-bearing file access is forbidden in tests")
    sys.addaudithook(audit)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="test_*.py")
    options = parser.parse_args()
    isolate()
    suite = unittest.defaultTestLoader.discover(str(BACKEND / "tests"), pattern=options.pattern)
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {"tests_run": result.testsRun, "failures": len(result.failures),
                      "errors": len(result.errors), "skipped": len(result.skipped),
                      "duration_seconds": round(time.perf_counter() - started, 3), "pattern": options.pattern,
                      "runtime": "in-process synthetic SQLite; TCP and DNS denied"}
    artifacts = ROOT / "tools/local-test/runtime"
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "backend-tests.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
