"""Offline installed dependency consistency, not an advisory scan or hosted build."""
import importlib.metadata
import json
from pathlib import Path
import sys
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
from check_local_release import ROOT


def main():
    installed = {canonicalize_name(item.metadata['Name']): item for item in importlib.metadata.distributions()}
    extras = {}
    for line in (ROOT / 'backend/requirements.txt').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            requirement = Requirement(line)
            extras.setdefault(canonicalize_name(requirement.name), set()).update(requirement.extras)
    # Include extras explicitly requested by the app (uvicorn[standard],
    # psycopg[binary]) and extras propagated by active transitive requirements.
    changed = True
    while changed:
        changed = False
        for name, distribution in installed.items():
            for declaration in distribution.requires or []:
                requirement = Requirement(declaration)
                if requirement.marker is not None and not any(requirement.marker.evaluate({'extra': extra}) for extra in {''} | extras.get(name, set())):
                    continue
                destination = extras.setdefault(canonicalize_name(requirement.name), set())
                if not requirement.extras.issubset(destination):
                    destination.update(requirement.extras)
                    changed = True
    problems = []
    checked = 0
    for name, distribution in installed.items():
        for declaration in distribution.requires or []:
            requirement = Requirement(declaration)
            if requirement.marker is not None and not any(requirement.marker.evaluate({'extra': extra}) for extra in {''} | extras.get(name, set())):
                continue
            checked += 1
            dependency = installed.get(canonicalize_name(requirement.name))
            if dependency is None or dependency.version not in requirement.specifier:
                problems.append({'package': name, 'dependency': requirement.name, 'required': str(requirement.specifier),
                                 'installed': dependency.version if dependency else None})
    lock = json.loads((ROOT / 'frontend/package-lock.json').read_text(encoding='utf-8'))
    for name, package in lock['packages'].items():
        if not name:
            continue
        if not package.get('resolved', '').startswith('https://registry.npmjs.org/') or not package.get('integrity', '').startswith('sha512-'):
            raise RuntimeError('Unapproved lockfile source or missing package integrity')
    constraints = '\n'.join(f'{name}=={distribution.version}' for name, distribution in sorted(installed.items()))+'\n'
    (LAB / 'runtime/staging-phase1-20261018/local-windows-reference-constraints.txt').write_text(constraints, encoding='utf-8')
    value = {'passed': not problems, 'installed_python_packages': len(installed), 'active_requirements_checked': checked,
             'application_requested_extras_included': True,
             'dependency_conflicts': problems, 'frontend_resolved_entries': len(lock['packages'])-1,
             'official_registry_integrity_checks_passed': True, 'new_packages_installed': 0,
             'network_requests': 0, 'hosted_linux_install_verified': False, 'fresh_advisory_scan_performed': False,
             'local_constraints_are_not_a_portable_production_lock': True, 'production_connections': 0}
    (LAB / 'evidence/batch-84-dependencies.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(value))
    return not value['passed']


if __name__ == '__main__':
    raise SystemExit(main())
