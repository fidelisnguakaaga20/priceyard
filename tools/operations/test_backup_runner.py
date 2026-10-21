"""Only new adapter guards; no credentials, Windows crypto, network or exports."""
import ast
import importlib.util
import os
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('backup_runner',Path(__file__).with_name('backup_runner.py'))
backup=importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupAdapterTests(unittest.TestCase):
    def good(self):
        return {'purpose':backup.PURPOSE,'project':'lrvpjfbtmftjkzaxbunk','revision':'0022_login_revocation',
                'database_password':'fabricated-database-only','archive_passphrase':'fabricated-archive-only-123456789'}

    def test_target_and_secret_guards(self):
        for changes in ({'project':'other'},{'revision':'0021_feedback_screenshot'},{'purpose':'other'},
                        {'database_password':''},{'archive_passphrase':'short'},
                        {'archive_passphrase':'non-ascii-\u20a6'*24},{'extra':'refused'},
                        {'archive_passphrase':'fabricated-database-only'}):
            with self.subTest(changes=changes),self.assertRaises(RuntimeError):
                backup.validate_enrollment({**self.good(),**changes})
        self.assertEqual(backup.validate_enrollment(self.good()),self.good())

    def test_reviewed_source_required_before_adaptation(self):
        with patch.object(Path,'read_bytes',return_value=b'print("unreviewed")'):
            with self.assertRaisesRegex(RuntimeError,'hash differs'):
                backup.load_core()

    def fixture(self):
        return """REVISION = '0021_feedback_screenshot'
def main():
    global RUN, PASSWORD, ARCHIVE_PASSWORD, ENV
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError('Interactive owner console required; production was not contacted')
    arguments = sys.argv[1:]
    preserve_all_export_guards()
"""

    def test_only_scheduled_entry_and_exact_revision_change(self):
        value=backup.adapt_core(self.fixture())
        ast.parse(value)
        self.assertIn("REVISION = '0022_login_revocation'",value)
        self.assertIn('_verify_scheduled_context()',value)
        self.assertIn('preserve_all_export_guards()',value)
        self.assertNotIn('sys.argv[1:]',value)

    def test_source_changes_and_duplicate_adaptations_stop(self):
        for value in (self.fixture().replace('    arguments = sys.argv[1:]','    arguments = unknown'),
                      self.fixture()+"\nREVISION = '0021_feedback_screenshot'\n"):
            with self.assertRaisesRegex(RuntimeError,'structure changed'):
                backup.adapt_core(value)

    def test_explicit_approved_context_required_before_any_secret_read(self):
        with patch.dict(backup.os.environ,{},clear=True),patch.object(backup,'protected_file') as protected:
            with self.assertRaisesRegex(RuntimeError,'reviewed same-owner'):
                backup.run()
            protected.assert_not_called()

    def test_import_and_help_are_inert(self):
        with patch('sys.argv',['backup_runner.py']),patch.object(backup,'run') as run:
            self.assertEqual(backup.main(),0)
            run.assert_not_called()

    def test_task_has_explicit_bounds_and_no_saved_windows_password(self):
        text=Path(__file__).with_name('backup_windows.ps1').read_text(encoding='utf-8')
        for value in ('-MultipleInstances IgnoreNew','-Minutes 10','-StartWhenAvailable',
                      '-RunOnlyIfNetworkAvailable','-RestartCount 2','-Hours 1','-LogonType Interactive',
                      '-Action',"if($Action -eq 'Verify'){return}","'Protected enrollment permissions changed'"):
            self.assertIn(value,text)
        self.assertNotIn('-ExecutionPolicy Bypass',text)
        self.assertNotIn('Remove-Item -LiteralPath',text)

    def test_direct_invocation_rechecks_real_windows_guards(self):
        with patch.object(backup.subprocess,'run') as run:
            run.return_value.returncode=1
            with self.assertRaisesRegex(RuntimeError,'owner, ACL, EFS'):
                backup.verify_owner_context()
            self.assertIn('Verify',run.call_args.args[0])
            self.assertEqual(run.call_args.kwargs['timeout'],30)

    @unittest.skipUnless(os.name=='nt','Windows DPAPI only')
    def test_new_enrollment_envelope_is_purpose_bound(self):
        value=b'FABRICATED new enrollment envelope only'
        sealed=backup.protect(value)
        self.assertNotIn(value,sealed)
        self.assertEqual(backup.unprotect(sealed),value)
        with patch.object(backup,'ENTROPY',b'other-fabricated-purpose'):
            with self.assertRaisesRegex(RuntimeError,'unavailable'):
                backup.unprotect(sealed)

    @unittest.skipUnless(os.name=='nt','Windows file lock only')
    def test_scheduled_orchestration_uses_enrollment_without_console_prompts(self):
        core="""
def main():
    global ENV
    _verify_scheduled_context()
    assert hidden('Existing Supabase database password (hidden): ') == 'fabricated-database-only'
    assert choose_archive_password() == 'fabricated-archive-only-123456789'
    ENV = {'PGPASSWORD':'fabricated-database-only'}
"""
        # Fabricated lock only, in system TEMP outside the project; no secret file.
        with tempfile.TemporaryDirectory(prefix='priceyard-new-adapter-only-') as folder:
            root=Path(folder);(root/'PrivateRestoreEfs').mkdir()
            with patch.object(backup,'ROOT',root),patch.object(backup,'ENROLLMENT') as enrollment,\
                 patch.object(backup,'verify_owner_context') as verify,\
                 patch.object(backup,'protect_child_lifetime'),patch.object(backup,'protected_file'),\
                 patch.object(backup,'load_core',return_value=core),\
                 patch.object(backup,'unprotect',return_value=json.dumps(self.good()).encode()),\
                 patch.object(backup,'write_status') as status,\
                 patch.dict(backup.os.environ,{'PRICEYARD_BACKUP_APPROVED_SCHEDULE':backup.PURPOSE}),\
                 patch('builtins.input',side_effect=AssertionError('Console input forbidden')),\
                 patch.object(backup.getpass,'getpass',side_effect=AssertionError('Console input forbidden')):
                enrollment.stat.return_value.st_size=100
                enrollment.read_bytes.return_value=b'fabricated-envelope'
                self.assertEqual(backup.run(),0)
                verify.assert_called_once()
                status.assert_any_call('running')
                status.assert_called_with('passed',encrypted_archive_checked=True)


if __name__=='__main__':
    unittest.main(verbosity=2)
