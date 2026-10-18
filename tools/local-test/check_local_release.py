"""Read-only local evidence/build gate. Never connects or authorizes deployment."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess

from packaging.requirements import Requirement

LAB=Path(__file__).resolve().parent
ROOT=LAB.parents[1]
GIT='C:/Program Files/Git/cmd/git.exe'
GATE_IDS={'hosting_cookies_browsers','actual_backup_restoration','production_schema_rollout',
    'paystack_provider','recovery_scheduler','google_notification_delivery','monitoring_load_clock',
    'hosted_dependencies_environment','historical_review_cutover'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def validate_gates(value):
    require(value.get('scope')=='local-only-priceyard-py35','Unknown gate scope')
    require(value.get('release_authorized') is False and value.get('production_checks_run') is False,
            'Local evidence cannot authorize or claim production work')
    gates=value.get('gates',[])
    require({gate.get('id') for gate in gates}==GATE_IDS and len(gates)==len(GATE_IDS),'Missing or duplicated live gate')
    require(all(gate.get('status')=='not_run' and gate.get('owner_approval_required') is True for gate in gates),
            'Live checks require a separately reviewed scope')
    return sorted(GATE_IDS)


def report(name,check):
    path=LAB/'evidence'/name
    require(path.stat().st_size<1024*1024,'Unexpected evidence size')
    value=json.loads(path.read_text(encoding='utf-8-sig'))
    require(check(value),'Missing/failed evidence: '+name)
    return value


def git(*args):
    env={name:os.environ[name] for name in ('SYSTEMROOT','WINDIR','TEMP','TMP') if name in os.environ}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=str(LAB/'runtime/nonexistent-git-config'))
    result=subprocess.run([GIT,'--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=ROOT,env=env,
        capture_output=True,text=True,timeout=8,check=True)
    return result.stdout.strip()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--require-clean',action='store_true')
    options=parser.parse_args()
    gates=validate_gates(json.loads((ROOT/'docs/RELEASE_GATES.json').read_text(encoding='utf-8')))
    rows=re.findall(r'^\| (PY-\d{2}) \|[^\n]+', (ROOT/'PRICEYARD_PROGRESS.md').read_text(encoding='utf-8'),re.M)
    require(set(rows)=={f'PY-{number:02}' for number in range(1,37)} and len(rows)==36,'Tracker IDs must remain complete')
    backend=report('batch-81-backend.json',lambda x:x.get('tests_run')==286 and x.get('failures')==0 and x.get('errors')==0 and x.get('skipped')==0)
    report('batch-81-postgres.json',lambda x:x.get('tests')==1 and x.get('failures')==0 and x.get('errors')==0 and x.get('cluster_identity_verified') is True)
    dependencies=report('batch-82-dependencies.json',lambda x:x.get('lifecycle_scripts_executed')==0 and x.get('production_contacts')==0)
    report('batch-82-sessions-browser.json',lambda x:x.get('delayed_logout_response_cannot_clear_new_cross_tab_signin') is True and x.get('external_requests')==0)
    report('batch-82-dashboard-browser.json',lambda x:x.get('fourteen_original_labels_and_values_preserved') is True and x.get('outage_reload_recovers') is True)
    report('batch-83-recovery.json',lambda x:x.get('synthetic_only') is True and x.get('business_rows')==14 and x.get('source_unchanged') is True
        and x.get('rows_schema_constraints_indexes_sequences_match') is True and x.get('production_backup_restoration_verified') is False)
    report('batch-83-recovery-guards.json',lambda x:x.get('tests')==4 and x.get('failures')==0 and x.get('errors')==0 and x.get('native_connections')==0)
    report('batch-83-release-gate-tests.json',lambda x:x.get('tests')==3 and x.get('failures')==0 and x.get('errors')==0)
    report('batch-83-monitoring-browser.json',lambda x:x.get('local_monitoring_drill_passed') is True and x.get('failed',{}).get('health')==200
        and x.get('failed',{}).get('prices')==503 and x.get('recovered',{}).get('prices')==200 and x.get('live_monitor_or_alerts_enabled') is False)
    source=ROOT/'frontend';marker=json.loads((LAB/'runtime/frontend.json').read_text(encoding='utf-8'))
    snapshot=Path(marker['path']).resolve()
    require(marker.get('purpose')=='synthetic-only-no-application-credentials' and snapshot.parent==(LAB/'runtime').resolve(),'Invalid build identity')
    files=[source/name for name in ('package.json','package-lock.json','index.html','tsconfig.json','tsconfig.app.json','tsconfig.node.json','vite.config.ts')]
    files.extend(item for folder in ('src','public') for item in (source/folder).rglob('*') if item.is_file())
    require(all(item.read_bytes()==(snapshot/item.relative_to(source)).read_bytes() for item in files),'Build/source mismatch')
    require(hashlib.sha256((source/'package-lock.json').read_bytes()).hexdigest()==dependencies['lock_sha256'],'Lock/evidence mismatch')
    manifest=json.loads((source/'package.json').read_text(encoding='utf-8'))
    for name,version in (manifest['dependencies']|manifest['devDependencies']).items():
        installed=json.loads((snapshot/'node_modules'/name/'package.json').read_text(encoding='utf-8'))
        require(installed['version']==version==dependencies['direct_versions'][name],'Installed dependency mismatch')
    installed_python={distribution.metadata['Name']:distribution.version for distribution in importlib.metadata.distributions()}
    for line in (ROOT/'backend/requirements.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):continue
        requirement=Requirement(line)
        require(importlib.metadata.version(requirement.name) in requirement.specifier,'Local backend requirement mismatch')
    references=git('rev-parse','HEAD','master','backup/priceyard-hardening-20261015').splitlines()
    require(references[1:] == ['76dbd27588de4aa37f3163d8b263d4b72a2cff32','258991019e5af8b36eff407a8efa2c9fd03dd644'],'Preservation references changed')
    require(git('branch','--show-current')=='codex/priceyard-original-preserved-20261016','Wrong development branch')
    clean=not git('status','--porcelain')
    if options.require_clean:require(clean,'Commit verified local work before final candidate review')
    require(not git('ls-files','--','tools/local-test/runtime/'),'Runtime/archive must never be tracked')
    value={'local_evidence_checks_passed':True,'working_tree_clean':clean,'git_head':references[0],
        'original_master_and_backup_preserved':True,'matched_build_files':len(files),'backend_tests_reused':backend['tests_run'],
        'installed_local_python':dict(sorted(installed_python.items())),'frontend_direct_versions':dependencies['direct_versions'],
        'inventory_is_not_a_portable_production_lock_or_cve_certificate':True,'unrun_owner_approval_gates':gates,
        'production_release_authorized':False,'production_connections':0}
    (LAB/'runtime/local-release-check.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
    print(json.dumps({key:item for key,item in value.items() if key!='installed_local_python'}))

if __name__=='__main__':main()
