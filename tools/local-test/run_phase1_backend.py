"""Run selected existing tests against the separate synthetic staging source copy."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import guard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('batch', choices=['sessions', 'recovery', 'notifications', 'reset'])
    options = parser.parse_args()
    stage = LAB / 'runtime/staging-phase1-20261018'
    manifest = json.loads((stage / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['purpose'] != 'synthetic-only-phase1-staging-preparation' or manifest['live_services_enabled'] is not False:
        raise RuntimeError('Unapproved staging package')
    for name, digest in manifest['sha256'].items():
        candidate = stage / name
        if not candidate.resolve().is_relative_to(stage.resolve()) or candidate.is_symlink():
            raise RuntimeError('Staging file escaped package')
        if hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Staging source changed')
    original_tests = guard.BACKEND / 'tests'
    guard.BACKEND = stage / 'backend'
    guard.isolate()
    pattern = {'sessions': 'test_browser_sessions.py', 'recovery': 'test_payment_reconciliation.py',
               'notifications': 'test_watchlist_alert_service.py', 'reset': 'test_password_reset.py'}[options.batch]
    suite = unittest.defaultTestLoader.discover(str(original_tests), pattern=pattern)
    started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    import app
    if Path(app.__file__).resolve() != (stage / 'backend/app/__init__.py').resolve():
        raise RuntimeError('Tests did not load separate staging source')
    value = {'batch': options.batch, 'pattern': pattern, 'tests': result.testsRun,
             'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
             'seconds': round(time.monotonic()-started, 3), 'separate_staging_source_verified': True,
             'database': 'fresh synthetic in-memory SQLite', 'tcp_dns_and_native_postgres_denied': True,
             'provider_delivery_verified': False, 'production_connections': 0}
    (LAB / f'evidence/batch-84-backend-{options.batch}.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(value))
    return not result.wasSuccessful()


if __name__ == '__main__':
    raise SystemExit(main())
