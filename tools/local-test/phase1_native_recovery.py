"""Recheck the retained synthetic restore read-only; no seed/dump/restore repeated."""
import hashlib
import json
import msvcrt
import os
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
for name in list(os.environ):
    if name.upper().startswith('PG'):
        os.environ.pop(name)
import pg_recovery_control as recovery


def main():
    with (LAB / 'runtime/postgres-test-run.lock').open('r+b') as lock:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        manifest = recovery.manifest()
        schema = manifest['schema']
        state = json.loads(recovery.STATE.read_text(encoding='utf-8'))
        if state['purpose'] != recovery.PURPOSE or state['schema'] != schema:
            raise RuntimeError('Invalid retained synthetic recovery state')
        with recovery.connect(recovery.SOURCE) as source, recovery.connect(recovery.TARGET) as target:
            comment = target.execute("SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=%s", (recovery.TARGET,)).fetchone()[0]
            if comment != recovery.COMMENT:
                raise RuntimeError('Unapproved retained restore target')
            original = recovery.fingerprint(source, schema, True)
            restored = recovery.fingerprint(target, schema, True)
            if {key: value for key, value in original.items() if key != 'shape'} != state['baseline']:
                raise RuntimeError('Synthetic source changed since backup')
            if restored['tables'] != state['baseline']['tables']:
                raise RuntimeError('Retained restored rows differ')
            original['shape']['constraints'] = recovery.canonical_constraints(source, schema)
            restored['shape']['constraints'] = recovery.canonical_constraints(target, schema)
            if original['shape'] != restored['shape']:
                raise RuntimeError('Retained restored structure differs')
            archive = LAB / 'runtime/synthetic-business-backup.dump'
            prior = json.loads((LAB / 'evidence/batch-83-recovery.json').read_text(encoding='utf-8'))
            if hashlib.sha256(archive.read_bytes()).hexdigest() != prior['archive_sha256']:
                raise RuntimeError('Synthetic archive changed')
            schemas = source.execute("SELECT count(*) FROM pg_namespace WHERE nspname LIKE 'pyrev_%'").fetchone()[0]
            report = {'passed': True, 'read_only_reverification': True, 'reuses_actual_synthetic_restore_batch': 83,
                      'tables': len(restored['tables']), 'business_rows': sum(row['rows'] for row in restored['tables'].values()),
                      'source_and_restored_data_structure_preserved': True, 'archive_sha256': prior['archive_sha256'],
                      'cluster_identity_verified': True, 'retained_schemas': schemas, 'schema_budget': 80,
                      'new_backup_or_restore_executed': False, 'actual_customer_backup_verified': False,
                      'production_connections': 0}
        (LAB / 'evidence/batch-84-native-recovery.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
