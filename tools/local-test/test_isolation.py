"""Negative checks run before preview/application imports; no actual network."""
import importlib
import json
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import unittest

import guard
guard.isolate()


class IsolationTests(unittest.TestCase):
    def test_tcp_and_dns_denied(self):
        with socket.socket() as connection:
            with self.assertRaises(RuntimeError):
                connection.connect(("203.0.113.1", 443))
        with self.assertRaises(RuntimeError):
            socket.getaddrinfo("service.example.invalid", 443)

    def test_secret_file_denied_before_open(self):
        with self.assertRaises(RuntimeError):
            (guard.ROOT / "backend/.env").read_text()

    def test_postgresql_native_connections_denied(self):
        import psycopg
        for connect in (psycopg.connect, psycopg.Connection.connect, psycopg.AsyncConnection.connect):
            with self.assertRaises(RuntimeError):
                connect("host=service.example.invalid dbname=synthetic")

    def test_engine_entry_points_and_persistent_sqlite_denied(self):
        import sqlalchemy
        for create in (sqlalchemy.create_engine, sqlalchemy.engine.create_engine, importlib.import_module("sqlalchemy.engine.create").create_engine):
            with self.assertRaises(RuntimeError):
                create("postgresql+psycopg://service.example.invalid/synthetic")
        with self.assertRaises(RuntimeError):
            sqlite3.connect("existing.db")

    def test_children_and_nonlocal_listeners_denied(self):
        with self.assertRaises(RuntimeError):
            subprocess.Popen(["unneeded-child"])
        with socket.socket() as listener:
            with self.assertRaises(RuntimeError):
                listener.bind(("0.0.0.0", 55446))

    def test_only_fresh_memory_database_works(self):
        import sqlalchemy
        with sqlalchemy.create_engine("sqlite+pysqlite:///:memory:").connect() as connection:
            self.assertEqual(connection.execute(sqlalchemy.text("SELECT 1")).scalar(), 1)
        from app.config import get_settings
        settings = get_settings()
        self.assertEqual(settings.database_url, "sqlite+pysqlite:///:memory:")
        self.assertIsNone(settings.paystack_secret_key)
        self.assertIsNone(settings.brevo_api_key)
        self.assertIsNone(settings.smtp_host)
        self.assertIsNone(settings.whatsapp_access_token)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IsolationTests))
    report = {"checks": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "dotenv_contents_opened": False, "production_contacts": 0}
    (guard.ROOT / "tools/local-test/runtime/isolation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    raise SystemExit(not result.wasSuccessful())
