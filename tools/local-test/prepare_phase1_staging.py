"""Prepare one small credential-free staging package; never starts or deploys it."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
from check_local_release import ROOT, git

TARGET = LAB / 'runtime/staging-phase1-20261018'


def main():
    marker = json.loads((LAB / 'runtime/frontend.json').read_text(encoding='utf-8'))
    snapshot = Path(marker['path']).resolve()
    if (marker.get('purpose') != 'synthetic-only-no-application-credentials'
            or snapshot.parent != (LAB / 'runtime').resolve()):
        raise RuntimeError('Unapproved compiled frontend identity')
    # Fixed source allowlist, no dotenv, provider configuration or dependency trees.
    names = git('ls-files', '--', 'backend/app', 'backend/alembic', 'backend/requirements.txt').splitlines()
    sources = [(ROOT / name, name) for name in names
               if name.endswith('.py') or name == 'backend/requirements.txt']
    sources += [(item, 'frontend/dist/' + item.relative_to(snapshot / 'dist').as_posix())
                for item in (snapshot / 'dist').rglob('*') if item.is_file()]
    if not sources or len(sources) > 300:
        raise RuntimeError('Unexpected staging file budget')
    inventory = {}
    total = 0
    for source, name in sources:
        if source.is_symlink() or any(part.startswith('.env') for part in source.parts):
            raise RuntimeError('Secret or linked file refused')
        data = source.read_bytes()
        total += len(data)
        inventory[name] = hashlib.sha256(data).hexdigest()
    if total > 5 * 1024 * 1024:
        raise RuntimeError('Staging package exceeds 5MiB budget')
    value = {'purpose': 'synthetic-only-phase1-staging-preparation', 'source_commit': git('rev-parse', 'HEAD'),
             'file_count': len(inventory), 'bytes': total, 'sha256': inventory,
             'production_credentials_copied': False, 'provider_credentials_available': False,
             'hosted_staging_available': False, 'deployed': False, 'application_started': False,
             'database': 'No connection configured; only pinned synthetic fixtures may be used',
             'live_services_enabled': False, 'package_is_not_a_hosted_environment': True}
    manifest = TARGET / 'manifest.json'
    if TARGET.exists():
        previous = json.loads(manifest.read_text(encoding='utf-8'))
        if previous['sha256'] != inventory:
            raise RuntimeError('Existing staging package differs; preserve it for review')
    else:
        TARGET.mkdir()
        for source, name in sources:
            destination = TARGET / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        manifest.write_text(json.dumps(value, indent=2), encoding='utf-8')
    for name, digest in inventory.items():
        if hashlib.sha256((TARGET / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Staging copy verification failed')
    report = {key: item for key, item in value.items() if key != 'sha256'}
    report.update(copied_files_verified=True, maximum_files=300, maximum_bytes=5*1024*1024,
                  production_connections=0, network_requests=0)
    (LAB / 'evidence/batch-84-staging-package.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
