"""Read-only acceptance for Phase 1 evidence; never authorizes a live release."""
import hashlib
import json
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
from check_local_release import ROOT, GATE_IDS, validate_gates, require


def read(name):
    return json.loads((LAB / 'evidence' / name).read_text(encoding='utf-8-sig'))


def main():
    results = json.loads((ROOT / 'docs/PY35_PHASE1_RESULTS.json').read_text(encoding='utf-8'))
    require(results['production_release_authorized'] is False and results['production_checks_run'] is False,
            'Staging cannot authorize or claim production work')
    require(results['hosted_staging_available'] is False and results['provider_credentials_or_recipients_supplied'] is False,
            'Do not claim unavailable infrastructure')
    gates = results['gates']
    require(len(gates) == 9 and {item['id'] for item in gates} == GATE_IDS, 'Missing or repeated Phase 1 gate')
    allowed = {'Passed', 'Failed', 'Awaiting Production Approval'}
    require(all(item['phase1_status'] in allowed and item['production_gate_status'] == 'Awaiting Production Approval'
                for item in gates), 'Incorrect scope or status')
    require({item['id'] for item in gates if item['phase1_status'] == 'Passed'} ==
            {'actual_backup_restoration', 'recovery_scheduler'}, 'Only synthetic sub-scopes have passed')
    validate_gates(json.loads((ROOT / 'docs/RELEASE_GATES.json').read_text(encoding='utf-8')))
    total = 0
    for name, count in (('sessions', 1), ('recovery', 7), ('reset', 2), ('notifications', 5)):
        item = read(f'batch-84-backend-{name}.json')
        require(item['tests'] == count and item['failures'] == item['errors'] == item['skipped'] == 0
                and item['separate_staging_source_verified'] is True, 'Staged backend verification failed')
        total += count
    item = read('batch-84-isolation.json')
    require(item['checks'] == 6 and item['failures'] == item['errors'] == 0, 'Isolation failed')
    for name, checks in {
        'scheduler': {'tests': 1, 'failures': 0, 'errors': 0, 'operating_system_jobs_created': 0},
        'postgres-recovery': {'tests': 2, 'failures': 0, 'errors': 0, 'cluster_identity_verified': True},
        'native-recovery': {'passed': True, 'business_rows': 14, 'tables': 21, 'actual_customer_backup_verified': False},
        'dependencies': {'passed': True, 'new_packages_installed': 0, 'hosted_linux_install_verified': False},
        'browser-performance': {'passed': True, 'tls_verified': False, 'serial_requests': 24, 'concurrency': 1},
        'dashboard-browser': {'fourteen_original_labels_and_values_preserved': True},
        'recovery-browser': {'missed_webhook_recovers_without_callback': True, 'repeated_job_does_not_recredit': True},
        'monitoring-browser': {'local_monitoring_drill_passed': True, 'live_monitor_or_alerts_enabled': False},
        'notifications-browser': {'email_failure_preserves_independent_push_and_whatsapp': True},
        'reset-browser': {'live_emails_sent': 0},
    }.items():
        item = read(f'batch-84-{name}.json')
        require(all(item.get(key) == value for key, value in checks.items()), 'Failed evidence: ' + name)
        require(item.get('production_connections', item.get('production_contacts')) == 0, 'Live access claimed')
    stage = LAB / 'runtime/staging-phase1-20261018'
    manifest = json.loads((stage / 'manifest.json').read_text(encoding='utf-8'))
    build = Path(json.loads((LAB / 'runtime/frontend.json').read_text(encoding='utf-8'))['path'])
    for name, digest in manifest['sha256'].items():
        copied = stage / name
        source = ROOT / name if name.startswith('backend/') else build / name.removeprefix('frontend/')
        require(hashlib.sha256(copied.read_bytes()).hexdigest() == hashlib.sha256(source.read_bytes()).hexdigest() == digest,
                'Staging/source artifact changed')
    report = {'phase1_evidence_verified': True, 'staged_backend_tests': total, 'native_cases': 2,
              'isolation_probes': 6, 'finite_scheduler_tests': 1, 'serial_browser_reads': 24,
              'phase1_gate_counts': {name: sum(item['phase1_status'] == name for item in gates) for name in sorted(allowed)},
              'all_original_live_gates_still_unrun': True, 'production_release_authorized': False,
              'production_connections': 0, 'application_source_and_staging_hashes_match': True}
    (LAB / 'evidence/batch-84-final-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
