"""Finite synthetic schedule/restart rehearsal. No OS job or provider connection."""
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import guard
guard.isolate()
sys.path.insert(0, str(guard.BACKEND / 'tests'))
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.jobs.reconcile_payments import main as command
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from test_payment_reconciliation import seed_reconciliation, provider_patches


class SyntheticSchedule(unittest.TestCase):
    def test_three_finite_ticks_resume_checkpoint_without_recredit(self):
        engine = create_engine('sqlite+pysqlite:///:memory:')
        fixtures = seed_reconciliation(engine, ('unconfirmed', 'paid', 'trial'))
        observed = []
        checkpoint = {'after_id': 0, 'ceiling_id': None}
        reports = []
        try:
            for _ in range(3):
                output = io.StringIO()
                args = ['--apply', '--limit', '1', '--time-budget-seconds', '5',
                        '--after-id', str(checkpoint['after_id'])]
                if checkpoint['ceiling_id'] is not None:
                    args += ['--ceiling-id', str(checkpoint['ceiling_id'])]
                with patch('app.database.get_engine', return_value=engine), provider_patches(fixtures, observed), patch('sys.stdout', output):
                    self.assertEqual(command(args), 0)
                report = json.loads(output.getvalue())
                reports.append(report)
                self.assertEqual(len(report['outcomes']), 1)
                checkpoint = {'after_id': report['next_after_id'], 'ceiling_id': report['ceiling_id']}
                # A tiny local checkpoint stands in for a future scheduler store.
                saved = LAB / 'runtime/staging-phase1-20261018/synthetic-scheduler-checkpoint.json'
                saved.write_text(json.dumps({'synthetic_only': True, **checkpoint}), encoding='utf-8')
                checkpoint = json.loads(saved.read_text(encoding='utf-8'))
                self.assertIs(checkpoint.pop('synthetic_only'), True)
            self.assertEqual([item['complete'] for item in reports], [False, False, True])
            self.assertEqual(len({item['ceiling_id'] for item in reports}), 1)
            self.assertEqual([item['outcomes'][0]['outcome'] for item in reports], ['unconfirmed', 'confirmed', 'confirmed'])
            # Fresh sweep retries the unconfirmed record, not successful purchases.
            output = io.StringIO()
            with patch('app.database.get_engine', return_value=engine), provider_patches(fixtures, observed), patch('sys.stdout', output):
                self.assertEqual(command(['--apply', '--limit', '1', '--time-budget-seconds', '5']), 0)
            with Session(engine) as db:
                self.assertEqual(len(db.scalars(select(Payment).where(Payment.status == 'success')).all()), 2)
                self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action == 'payment.success')).all()), 2)
            for kind in ('paid', 'trial'):
                self.assertEqual(observed.count(fixtures[kind]['evidence']['reference']), 1)
        finally:
            engine.dispose()


if __name__ == '__main__':
    started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticSchedule))
    value = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
             'seconds': round(time.monotonic()-started, 3), 'finite_tick_count': 3, 'restart_checkpoint_readback': True,
             'synthetic_provider_only': True, 'operating_system_jobs_created': 0, 'production_connections': 0,
             'hosted_scheduler_verified': False}
    (LAB / 'evidence/batch-84-scheduler.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(value))
    raise SystemExit(not result.wasSuccessful())
