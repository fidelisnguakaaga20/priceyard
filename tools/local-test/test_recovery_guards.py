"""No native connections: negative checks for the new recovery controller."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock,patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import guard
guard.isolate()
import pg_recovery_control as recovery


class RecoveryGuards(unittest.TestCase):
    def test_arbitrary_database_rejected_before_driver(self):
        with patch.object(recovery.psycopg,'connect') as connect:
            with self.assertRaises(RuntimeError):recovery.connect('production')
            connect.assert_not_called()

    def test_wrong_live_identity_closes_before_any_mutation(self):
        connection=MagicMock()
        connection.execute.return_value.fetchone.return_value=('C:/unrelated','wrong-system')
        with patch.object(recovery.psycopg,'connect',return_value=connection):
            with self.assertRaises(RuntimeError):recovery.connect(recovery.SOURCE)
        connection.close.assert_called_once();self.assertEqual(connection.execute.call_count,1)
        self.assertIn('pg_control_system',connection.execute.call_args.args[0])

    def test_manifest_cannot_select_external_database_port_or_schema(self):
        baseline={'purpose':recovery.PURPOSE,'host':'127.0.0.1','port':55449,'system_identifier':recovery.IDENTITY,
            'source_database':recovery.SOURCE,'target_database':recovery.TARGET,'schema':'pyrev_'+'a'*32}
        for changes in ({'host':'service.example.invalid'},{'port':5432},{'source_database':'production'},
                        {'target_database':'postgres'},{'system_identifier':'other'},{'schema':'public'},
                        {'schema':'pyrev_;DROP TABLE users'},{'purpose':'unmarked'}):
            with patch.object(recovery,'MANIFEST') as manifest,patch.object(recovery.psycopg,'connect') as connect:
                manifest.read_text.return_value=json.dumps({**baseline,**changes})
                with self.assertRaises(RuntimeError):recovery.manifest()
                connect.assert_not_called()

    def test_fixed_connection_disables_credential_discovery_and_checks_identity(self):
        connection=MagicMock()
        connection.execute.return_value.fetchone.return_value=(str(recovery.DATA),recovery.IDENTITY)
        with patch.object(recovery.psycopg,'connect',return_value=connection) as connect:
            self.assertIs(recovery.connect(recovery.SOURCE),connection)
        arguments=connect.call_args.kwargs
        self.assertEqual((arguments['host'],arguments['port'],arguments['dbname']),('127.0.0.1',55449,recovery.SOURCE))
        self.assertEqual(arguments['sslmode'],'disable');self.assertEqual(arguments['gssencmode'],'disable')
        self.assertTrue(arguments['passfile'].endswith('nonexistent-synthetic-passfile'))
        self.assertEqual(connection.execute.call_count,1)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryGuards))
    report={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'native_connections':0,'production_contacts':0}
    (guard.ROOT/'tools/local-test/evidence/batch-83-recovery-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
