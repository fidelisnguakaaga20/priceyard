"""Negative isolation checks use illustrative targets, never live providers."""
import os
from pathlib import Path
import socket
import subprocess
import unittest


class IsolationGuardTests(unittest.TestCase):
    def test_runner_configuration_has_no_provider_credentials(self):
        self.assertEqual(os.environ["DATABASE_URL"], "sqlite+pysqlite:///:memory:")
        for key in ("PAYSTACK_SECRET_KEY", "BREVO_API_KEY", "SMTP_PASSWORD", "SUPABASE_URL", "AWS_SECRET_ACCESS_KEY"):
            self.assertNotIn(key, os.environ)

    def test_dotenv_and_credential_reads_are_rejected_before_file_access(self):
        for name in (".env", ".env.production", "synthetic.key", "credentials", ".npmrc"):
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, "Secret-bearing"):
                Path(name).read_bytes()

    def test_dns_and_tcp_are_rejected_before_external_transport(self):
        with self.assertRaisesRegex(RuntimeError, "External transport"):
            socket.getaddrinfo("provider.invalid", 443)
        with socket.socket() as connection:
            with self.assertRaisesRegex(RuntimeError, "External transport"):
                connection.connect(("192.0.2.1", 443))
        with self.assertRaisesRegex(RuntimeError, "External transport"):
            socket.create_connection(("127.0.0.1", 55439))

    def test_native_postgres_entry_points_are_denied_without_libpq_execution(self):
        import psycopg
        for connect in (psycopg.connect, psycopg.Connection.connect, psycopg.AsyncConnection.connect):
            with self.subTest(connect=connect), self.assertRaisesRegex(RuntimeError, "External transport"):
                connect("host=192.0.2.1 dbname=synthetic user=synthetic connect_timeout=1")

    def test_all_sqlalchemy_engine_entry_points_reject_non_memory_databases(self):
        import sqlalchemy
        from sqlalchemy.engine import create_engine
        from sqlalchemy.engine.create import create_engine as implementation
        for create in (sqlalchemy.create_engine, create_engine, implementation):
            for url in ("sqlite:///synthetic.db", "postgresql+psycopg://synthetic@192.0.2.1/synthetic"):
                with self.subTest(url=url), self.assertRaisesRegex(RuntimeError, "fresh in-memory"):
                    create(url)

    def test_child_processes_cannot_escape_test_transport_guards(self):
        with self.assertRaisesRegex(RuntimeError, "External transport"):
            subprocess.Popen(["synthetic-unavailable-tool"])
        with self.assertRaisesRegex(RuntimeError, "External transport"):
            os.system("synthetic-unavailable-tool")
