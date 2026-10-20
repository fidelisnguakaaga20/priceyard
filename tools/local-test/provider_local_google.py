"""Existing authorised loopback origin; Google only, no tunnel or other provider."""
import http.server
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provider_tunnel as d


def main():
    out = d.RUN / 'localhost-google-result.json'
    resume = '--resume-preflight-fix' in sys.argv
    if resume:
        previous = json.loads(out.read_text())
        d.require(previous.get('status') == 'stopped_by_controller' and not previous.get('Google_verified_linked_test_identity')
                  and previous.get('original_frontend_local_API_build') == 'passed_no_source_edits_no_dependency_install'
                  and all(previous.get(k) for k in ('worker_stopped','postgres_stopped','frontend_stopped')),
                  'Only the verified preflight stop can resume')
        for name in ('localhost-google-result.json','localhost-google-stop.txt'):
            d.require((d.RUN/name).exists() and not (d.RUN/('preflight-stop-'+name)).exists(), 'Retained preflight evidence differs')
        for name in ('localhost-google-result.json','localhost-google-stop.txt'):
            (d.RUN/name).rename(d.RUN/('preflight-stop-'+name))
    d.require(not out.exists(), 'Existing Google test result retained; inspect before resuming')
    prior = json.loads((d.RUN / 'remaining-result.json').read_text())
    d.require(all(prior.get(k) for k in ('tunnel_closed', 'worker_stopped', 'postgres_stopped')), 'Previous window not closed')
    for port in (5173, 55446, 55452, 55453, 55454):
        with socket.socket() as probe:
            probe.settimeout(.2)
            d.require(probe.connect_ex(('127.0.0.1', port)) != 0, 'Occupied test port; no process stopped')
    origin = 'http://127.0.0.1:5173'
    cid = d.fields(d.ROOT / 'backend/.env', {'GOOGLE_CLIENT_ID'}).get('GOOGLE_CLIENT_ID')
    d.require(cid == d.fields(d.ROOT / 'frontend/.env', {'VITE_GOOGLE_CLIENT_ID'}).get('VITE_GOOGLE_CLIENT_ID')
              and cid == '664659422573-nua5sbvbcqqq9d64th3hlddjhd41kso9.apps.googleusercontent.com',
              'Local Google client does not match owner screenshot')
    hba = d.RUN / 'synthetic-only-pg_hba.conf'
    content = hba.read_text(encoding='ascii')
    match = re.search(r'^host priceyard17_efs_synthetic (py_provider_[0-9a-f]{12}) 127\.0\.0\.1/32 scram-sha-256$', content, re.M)
    d.require(match, 'Marked synthetic role missing')
    schema = match[1]
    expected = f'host postgres,{d.DB} py17_efs_admin 127.0.0.1/32 trust\nhost {d.DB} {schema} 127.0.0.1/32 scram-sha-256\nhost all all 0.0.0.0/0 reject\nhost all all ::/0 reject\n'
    d.require(content == expected and not (d.DATA / 'postmaster.pid').exists(), 'Synthetic fixture state differs')
    env = d.clean_environment()
    env.update(PGPASSFILE=str(d.RUN / 'absent-passfile'), PGSERVICEFILE=str(d.RUN / 'absent-servicefile'))
    report = {'status': 'preparing', 'synthetic_only': True, 'origin': origin, 'no_tunnel': True,
              'payments_and_email_disabled': True, 'production_changes': False, 'release_authorized': False}
    def save():
        out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    log = (d.RUN / 'localhost-google-control.log').open('ab')
    server = static = None
    started = False
    try:
        manifest = json.loads((d.LAB / 'runtime/frontend.json').read_text())
        snapshot = Path(manifest['path']).resolve()
        d.require(manifest.get('purpose') == 'synthetic-only-no-application-credentials'
                  and snapshot.parent == (d.LAB / 'runtime').resolve(), 'Unapproved frontend snapshot')
        for folder in ('src', 'public'):
            for source in (d.ROOT / 'frontend' / folder).rglob('*'):
                if source.is_file():
                    d.require(source.read_bytes() == (snapshot / source.relative_to(d.ROOT / 'frontend')).read_bytes(), 'Original frontend snapshot stale')
        dist = d.RUN / 'localhost-google-dist'
        if resume:
            bundles = list((dist/'assets').glob('*.js'))
            d.require((dist/'index.html').is_file() and bundles
                      and any(cid in b.read_text(encoding='utf-8') and 'http://127.0.0.1:55446/api' in b.read_text(encoding='utf-8') for b in bundles),
                      'Retained original local build differs')
            report['existing_local_build_reused'] = True
        else:
            d.require(not dist.exists(), 'Existing localhost build retained')
            build_env = dict(env, VITE_API_URL='http://127.0.0.1:55446/api', VITE_GOOGLE_CLIENT_ID=cid, NODE_ENV='production')
            build = subprocess.run([r'C:\Program Files\nodejs\node.exe', '--require', str(d.LAB / 'node_guard.cjs'),
                                    str(snapshot / 'node_modules/vite/bin/vite.js'), 'build', '--mode', 'synthetic', '--outDir', str(dist)],
                                   cwd=snapshot, env=build_env, stdout=log, stderr=log, timeout=60)
            d.require(build.returncode == 0 and (dist / 'index.html').is_file(), 'Local-only frontend build failed')
        report['original_frontend_local_API_build'] = 'passed_no_source_edits_no_dependency_install'
        check = subprocess.run([str(d.BIN / 'pg_controldata.exe'), str(d.DATA)], env=env, capture_output=True, timeout=5)
        d.require(check.returncode == 0 and d.PG_ID.encode() in check.stdout, 'PG17 identity differs')
        started = True
        subprocess.run([str(d.BIN / 'pg_ctl.exe'), '-D', str(d.DATA), '-l', str(d.DATA.parent / 'provider-only-server.log'),
                        '-o', f'-h 127.0.0.1 -p 55452 -c hba_file={hba.as_posix()} -c shared_buffers=32MB -c max_connections=12 -c fsync=on',
                        '-w', '-t', '15', 'start'], env=env, stdout=log, stderr=log, timeout=20, check=True)
        import psycopg
        from psycopg import sql
        password = secrets.token_urlsafe(32)
        with psycopg.connect(host='127.0.0.1', port=55452, user='py17_efs_admin', dbname=d.DB,
                             sslmode='disable', gssencmode='disable', connect_timeout=3,
                             passfile=str(d.RUN / 'absent-passfile'), autocommit=True) as db:
            identity, directory, version = db.execute("SELECT system_identifier::text,current_setting('data_directory'),current_setting('server_version_num')::int FROM pg_control_system()").fetchone()
            d.require(identity == d.PG_ID and Path(directory).resolve() == d.DATA.resolve() and 170000 <= version < 180000, 'Live fixture identity differs')
            marker = db.execute("SELECT obj_description(oid,'pg_namespace') FROM pg_namespace WHERE nspname=%s", (schema,)).fetchone()
            flags = db.execute('SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication FROM pg_roles WHERE rolname=%s', (schema,)).fetchone()
            d.require(marker == ('owner-approved synthetic-only HTTPS provider drill',) and flags == (False,False,False,False), 'Synthetic ownership differs')
            db.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(schema), sql.Literal(password)))
        cfg = dict(schema=schema, origin=origin, google_only_local=True, email_disabled=True,
                   synthetic_password=secrets.token_urlsafe(24), jwt_secret=secrets.token_urlsafe(48), gate=secrets.token_urlsafe(36),
                   GOOGLE_CLIENT_ID=cid, PAYSTACK_SECRET_KEY='sk_test_DISABLED', PAYSTACK_PUBLIC_KEY='pk_test_DISABLED',
                   BREVO_API_KEY='', SMTP_FROM_EMAIL='synthetic@example.com',
                   database_url=f'postgresql+psycopg://{schema}:{quote(password,safe="")}@127.0.0.1:55452/{d.DB}')
        server = subprocess.Popen([sys.executable, '-I', '-B', str(Path(d.__file__).resolve()), '--worker'], stdin=subprocess.PIPE,
                                  stdout=log, stderr=log, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        server.stdin.write((json.dumps(cfg)+'\n').encode())
        server.stdin.close()
        import requests
        client = requests.Session();client.trust_env=False
        base='http://127.0.0.1:55446'
        def stats():
            return client.get(base+'/__provider_status',headers={'x-provider-controller':cfg['gate']},timeout=3).json()
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            d.require(server.poll() is None,'Google fixture worker stopped')
            try:
                if stats().get('synthetic_only'):break
            except (requests.RequestException,ValueError):pass
            time.sleep(.2)
        else:raise RuntimeError('Google fixture startup timed out')
        preflight_headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'}
        allowed=client.options(base+'/api/auth/browser/google',headers=preflight_headers,timeout=3)
        d.require(allowed.status_code==200 and allowed.headers.get('access-control-allow-origin')==origin
                  and allowed.headers.get('access-control-allow-credentials')=='true','Approved loopback preflight failed')
        denied=client.options(base+'/api/auth/browser/google',headers=dict(preflight_headers,Origin='https://priceyard.onrender.com'),timeout=3)
        d.require(denied.status_code==400 and not denied.headers.get('access-control-allow-origin'),'Unexpected origin allowed')
        gated=client.post(base+'/api/auth/browser/google',headers={'Origin':origin},json={'id_token':'not-a-Google-token'},timeout=3)
        d.require(gated.status_code==403 and gated.headers.get('access-control-allow-origin')==origin,'Private gate lost or unreadable rejection')
        entry=client.get(base+'/?ticket='+quote(cfg['gate']),allow_redirects=False,timeout=3)
        d.require(entry.status_code==303,'Local entry failed')
        for path in ('/api/payments/initiate','/api/auth/forgot-password'):
            blocked=client.post(base+path,headers={'Origin':origin},json={'email':d.EMAIL,'plan':'monthly'},timeout=3)
            d.require(blocked.status_code==403,'Non-Google write allowed')
        anon=client.get(base+'/api/auth/browser/session',headers={'Origin':origin},timeout=3)
        d.require(anon.status_code==401 and anon.headers.get('access-control-allow-origin')==origin,'Anonymous session CORS failed')
        d.require(stats()['paystack_requests']==0 and stats()['email_messages_accepted']==0 and stats()['google_logins']==0,'Preflight checks touched provider')
        report['local_CORS_and_isolation_checks_passed']=6
        class OriginalUI(http.server.SimpleHTTPRequestHandler):
            def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(dist),**kwargs)
            def do_GET(self):
                from urllib.parse import urlsplit
                target=(dist/urlsplit(self.path).path.lstrip('/')).resolve()
                if not target.is_relative_to(dist.resolve()):
                    self.send_error(403);return
                if not target.is_file():self.path='/index.html'
                super().do_GET()
            def end_headers(self):
                self.send_header('Referrer-Policy','no-referrer-when-downgrade')
                self.send_header('Cross-Origin-Opener-Policy','same-origin-allow-popups')
                self.send_header('Cache-Control','no-store')
                super().end_headers()
            def log_message(self,*args):pass
        static=http.server.ThreadingHTTPServer(('127.0.0.1',5173),OriginalUI)
        threading.Thread(target=static.serve_forever,daemon=True).start()
        d.require(client.get(origin+'/login',timeout=3).status_code==200,'Original local frontend unavailable')
        report.update(status='awaiting_owner_Google_sign_in',Google_client_matches_owner_screenshot=True,
                      maximum_window_seconds=1200,backend='http://127.0.0.1:55446/api')
        save()
        os.startfile(base+'/?ticket='+quote(cfg['gate']))
        print(json.dumps(report),flush=True)
        end=time.monotonic()+1200
        while time.monotonic()<end:
            d.require(server.poll() is None,'Google fixture stopped')
            state=stats()
            d.require(state['paystack_requests']==0 and state['email_messages_accepted']==0,'Other provider unexpectedly used')
            if state['google_logins']:
                report.update(status='passed_Google_ID_token_and_original_authentication',Google_verified_linked_test_identity=True,
                              HTTP_local_development_only=True,production_Render_session_runtime_verified=False)
                break
            if (d.RUN/'localhost-google-stop.txt').exists():
                report['status']='stopped_by_controller';break
            time.sleep(2)
        else:report['status']='Google_sign_in_not_completed_within_bounded_window'
    except Exception as error:
        report.update(status='stopped',error_type=type(error).__name__)
        if type(error) is RuntimeError:report['safe_stop_reason']=str(error)
    finally:
        if static:static.shutdown();static.server_close()
        if server and server.poll() is None:
            server.terminate();server.wait(timeout=5)
        if started:
            subprocess.run([str(d.BIN/'pg_ctl.exe'),'-D',str(d.DATA),'-m','fast','-w','-t','15','stop'],
                           env=env,stdout=log,stderr=log,timeout=20)
        report.update(worker_stopped=server is None or server.poll() is not None,
                      postgres_stopped=not (d.DATA/'postmaster.pid').exists(),frontend_stopped=True)
        log.close();save()
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
