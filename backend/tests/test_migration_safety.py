import unittest

from sqlalchemy import create_engine, event, inspect, text

from app.migration_safety import assert_safe_migration_start


class MigrationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def seed(self, connection):
        connection.execute(text("CREATE TABLE legacy_records (id INTEGER PRIMARY KEY, original_value TEXT NOT NULL)"))
        connection.execute(text("INSERT INTO legacy_records VALUES (1,'SYNTHETIC-PRIVATE-HISTORY')"))

    def test_empty_initialization_is_allowed_without_creating_or_changing_tables(self):
        with self.engine.begin() as connection:
            assert_safe_migration_start(connection, ())
            self.assertEqual(inspect(connection).get_table_names(), [])
            connection.execute(text("CREATE TABLE empty_legacy (id INTEGER PRIMARY KEY)"))
            assert_safe_migration_start(connection, ("0005_stage13_watchlists",))
            self.assertEqual(connection.execute(text("SELECT count(*) FROM empty_legacy")).scalar_one(), 0)

    def test_populated_legacy_is_rejected_using_read_only_checks(self):
        with self.engine.begin() as connection:
            self.seed(connection)
            writes = []
            def track(conn, cursor, statement, parameters, context, executemany):
                if statement.lstrip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "REPLACE"}:
                    writes.append(statement)
            event.listen(connection, "before_cursor_execute", track)
            with self.assertRaisesRegex(RuntimeError, "reviewed migration") as refused:
                assert_safe_migration_start(connection, ("0005_stage13_watchlists",))
            self.assertNotIn("SYNTHETIC-PRIVATE-HISTORY", str(refused.exception))
            self.assertEqual(writes, [])
            self.assertEqual(connection.execute(text("SELECT * FROM legacy_records")).all(), [(1, "SYNTHETIC-PRIVATE-HISTORY")])

    def test_unversioned_unknown_and_forked_populated_schemas_require_review(self):
        with self.engine.begin() as connection:
            self.seed(connection)
            for heads in ((), ("unknown",), ("0021_feedback_screenshot", "unknown")):
                with self.subTest(heads=heads), self.assertRaises(RuntimeError):
                    assert_safe_migration_start(connection, heads)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM legacy_records")).scalar_one(), 1)

    def test_reviewed_additive_baselines_preserve_original_values(self):
        with self.engine.begin() as connection:
            self.seed(connection)
            before = connection.execute(text("SELECT * FROM legacy_records")).all()
            for revision in ("0021_feedback_screenshot", "0022_login_revocation"):
                assert_safe_migration_start(connection, (revision,))
                self.assertEqual(connection.execute(text("SELECT * FROM legacy_records")).all(), before)
