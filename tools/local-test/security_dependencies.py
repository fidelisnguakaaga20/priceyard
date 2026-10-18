"""Owner-approved exact npm updates; fixed workspace snapshot, no lifecycle scripts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import socket
from urllib.parse import urlsplit

LAB=Path(__file__).resolve().parent
ROOT=LAB.parents[1]
TARGET=LAB/'runtime/frontend-security-20261018'
NODE=Path('C:/Program Files/nodejs/node.exe')
NPM=Path('C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js')


def checked_target():
    if TARGET.resolve().parent != (LAB/'runtime').resolve() or TARGET.is_symlink():
        raise RuntimeError('Only the fixed isolated dependency snapshot is allowed')
    return TARGET


def npm(arguments):
    # No inherited npm tokens, provider credentials, user config or application env.
    env={name:os.environ[name] for name in ('SYSTEMROOT','WINDIR','TEMP','TMP') if name in os.environ}
    env['PATH']=str(NODE.parent)+';'+str(Path(env.get('SYSTEMROOT','C:/Windows'))/'System32')
    env['NPM_CONFIG_UPDATE_NOTIFIER']='false'
    result=subprocess.run([str(NODE),str(NPM),*arguments,'--ignore-scripts','--no-audit','--no-fund',
        '--registry=https://registry.npmjs.org/','--userconfig='+str(TARGET/'empty-user.npmrc'),
        '--globalconfig='+str(TARGET/'empty-global.npmrc'),'--cache='+str(LAB/'runtime/npm-security-cache')],
        cwd=TARGET,env=env,timeout=180)
    if result.returncode:raise RuntimeError('Isolated npm phase failed')


def check_lock():
    lock=json.loads((TARGET/'package-lock.json').read_text(encoding='utf-8'))
    packages=lock['packages']
    if len(packages)>180:raise RuntimeError('Unexpected dependency/file budget')
    for name,item in packages.items():
        if not name:continue
        address=urlsplit(item.get('resolved',''))
        if address.scheme!='https' or address.netloc!='registry.npmjs.org' or address.username or address.password:
            raise RuntimeError('Non-registry dependency refused')
        if not item.get('integrity','').startswith('sha512-'):raise RuntimeError('Missing package integrity')
    for name,version in {'vite':'6.4.4','react-router-dom':'6.30.6','react':'18.3.1','react-dom':'18.3.1'}.items():
        if packages['node_modules/'+name]['version']!=version:raise RuntimeError('Unexpected resolved direct version')
    return lock


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','lock','install','verify','build','activate'])
    phase=parser.parse_args().phase;checked_target()
    if phase=='prepare':
        if TARGET.exists():raise RuntimeError('Existing snapshot preserved; choose the next reviewed phase')
        TARGET.mkdir()
        manifest=json.loads((ROOT/'frontend/package.json').read_text(encoding='utf-8'))
        manifest['devDependencies']['vite']='6.4.4';manifest['dependencies']['react-router-dom']='6.30.6'
        (TARGET/'package.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        for name in ('index.html','tsconfig.json','tsconfig.app.json','tsconfig.node.json','vite.config.ts'):
            shutil.copyfile(ROOT/'frontend'/name,TARGET/name)
        for name in ('src','public'):
            shutil.copytree(ROOT/'frontend'/name,TARGET/name,
                ignore=lambda directory,names:[name for name in names if name.startswith('.env') or Path(directory,name).is_symlink()])
        for name in ('empty-user.npmrc','empty-global.npmrc'):(TARGET/name).write_text('',encoding='utf-8')
    elif phase=='lock':
        if (TARGET/'node_modules').exists():raise RuntimeError('Do not resolve over an installed snapshot')
        npm(['install','--package-lock-only']);lock=check_lock()
        print(json.dumps({'registry_only':True,'integrity_checked':True,'resolved_packages':len(lock['packages'])-1,'scripts_executed':0}))
    elif phase=='install':
        check_lock()
        if (TARGET/'node_modules').exists():raise RuntimeError('Installed files preserved; inspect before any retry')
        npm(['ci']);check_lock()
    elif phase=='build':
        check_lock()
        for port in (55446,55448,55449):
            with socket.socket() as probe:
                probe.settimeout(1)
                if probe.connect_ex(('127.0.0.1',port))==0:raise RuntimeError('Stop preview/native tests before building')
        env={name:os.environ[name] for name in ('SYSTEMROOT','WINDIR','TEMP','TMP') if name in os.environ}
        env.update(VITE_API_URL='/api',VITE_GOOGLE_CLIENT_ID='',NODE_ENV='production')
        for arguments in ([str(TARGET/'node_modules/typescript/bin/tsc'),'-b'],[str(TARGET/'node_modules/vite/bin/vite.js'),'build','--mode','synthetic']):
            result=subprocess.run([str(NODE),'--require',str(LAB/'node_guard.cjs'),*arguments],cwd=TARGET,env=env,timeout=60)
            if result.returncode:raise RuntimeError('Isolated security dependency build failed')
        marker={'purpose':'synthetic-only-no-application-credentials','path':str(TARGET),
            'lock_sha256':hashlib.sha256((TARGET/'package-lock.json').read_bytes()).hexdigest()}
        (TARGET/'security-build-ready.json').write_text(json.dumps(marker),encoding='utf-8')
    elif phase=='activate':
        check_lock()
        marker=json.loads((TARGET/'security-build-ready.json').read_text(encoding='utf-8'))
        if marker['path']!=str(TARGET) or marker['purpose']!='synthetic-only-no-application-credentials':raise RuntimeError('Build identity mismatch')
        if marker['lock_sha256']!=hashlib.sha256((TARGET/'package-lock.json').read_bytes()).hexdigest():raise RuntimeError('Build lock changed')
        for folder in ('src','public'):
            source=ROOT/'frontend'/folder
            for item in source.rglob('*'):
                if item.is_file() and item.read_bytes()!=(TARGET/folder/item.relative_to(source)).read_bytes():raise RuntimeError('Source changed after snapshot preparation')
        for name in ('package.json','package-lock.json'):shutil.copyfile(TARGET/name,ROOT/'frontend'/name)
        ready={'path':str(TARGET),'purpose':'synthetic-only-no-application-credentials'}
        (LAB/'runtime/frontend.next.json').write_text(json.dumps(ready),encoding='utf-8')
        (LAB/'runtime/frontend.next.json').replace(LAB/'runtime/frontend.json')
        print(json.dumps({'new_build_active_locally':True,'old_snapshot_retained':True}))
    else:
        lock=check_lock();versions={}
        for name in lock['packages']['']['dependencies']|lock['packages']['']['devDependencies']:
            installed=json.loads((TARGET/'node_modules'/name/'package.json').read_text(encoding='utf-8'))
            if installed['version']!=lock['packages']['node_modules/'+name]['version']:raise RuntimeError('Installed/lock version mismatch')
            versions[name]=installed['version']
        report={'direct_versions':versions,'lock_sha256':hashlib.sha256((TARGET/'package-lock.json').read_bytes()).hexdigest(),
            'resolved_packages':len(lock['packages'])-1,'registry':'https://registry.npmjs.org/',
            'lifecycle_scripts_executed':0,'previous_snapshot_retained':True,'production_contacts':0}
        (LAB/'evidence/batch-82-dependencies.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report))

if __name__=='__main__':main()
