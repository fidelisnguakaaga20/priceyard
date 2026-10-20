"""Finish only the interrupted application rollback; no tunnel/provider/migration."""
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provider_tunnel as drill

R = drill.RUN
OUT = R / 'rollback-result.json'


def main():
    drill.require(not OUT.exists(), 'Existing rollback result retained')
    prior = json.loads(drill.REPORT.read_text())
    drill.require(prior.get('tunnel_closed') and prior.get('postgres_stopped')
                  and prior.get('safe_stop_reason') == 'Unexpected rollback source entry', 'Wrong resume point')
    # Only the exact HBA produced by this synthetic-only drill is accepted.
    hba = R / 'synthetic-only-pg_hba.conf'
    content = hba.read_text(encoding='ascii')
    match = re.search(r'^host priceyard17_efs_synthetic (py_provider_[0-9a-f]{12}) 127\.0\.0\.1/32 scram-sha-256$', content, re.M)
    drill.require(match, 'Synthetic runner identity missing')
    schema = match[1]
    expected = f'host postgres,{drill.DB} py17_efs_admin 127.0.0.1/32 trust\nhost {drill.DB} {schema} 127.0.0.1/32 scram-sha-256\nhost all all 0.0.0.0/0 reject\nhost all all ::/0 reject\n'
    drill.require(content == expected and not (drill.DATA / 'postmaster.pid').exists(), 'Fixture startup state differs')
    candidate = drill.rollback_source()
    env = drill.clean_environment()
    env.update(PGPASSFILE=str(R / 'absent-passfile'), PGSERVICEFILE=str(R / 'absent-servicefile'))
    cfg = {'schema': schema, 'origin': 'https://offline-rollback-only.trycloudflare.com',
           'synthetic_password': secrets.token_urlsafe(24), 'jwt_secret': secrets.token_urlsafe(48),
           'gate': secrets.token_urlsafe(36), 'PAYSTACK_SECRET_KEY': 'sk_test_OFFLINE_DISABLED',
           'PAYSTACK_PUBLIC_KEY': 'pk_test_OFFLINE_DISABLED', 'GOOGLE_CLIENT_ID': 'synthetic-client',
           'BREVO_API_KEY': '', 'SMTP_FROM_EMAIL': 'synthetic@example.com', 'external_enabled': False,
           'refresh_synthetic_password': True}
    report = {'status': 'running', 'scope': 'local PG17 security-aware application rollback only',
              'production_connections': 0, 'provider_requests': 0, 'tunnels_started': 0, 'migrations_run': 0}
    worker = None
    started = False
    log = (R / 'rollback-control.log').open('ab')
    def boot():
        process = subprocess.Popen([sys.executable, '-I', '-B', str(Path(drill.__file__).resolve()), '--worker'],
                                   stdin=subprocess.PIPE, stdout=log, stderr=log, env=env,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        process.stdin.write((json.dumps(cfg) + '\n').encode())
        process.stdin.close()
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            drill.require(process.poll() is None, 'Rollback fixture worker stopped')
            try:
                response = client.get(base + '/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=1)
                if response.status_code == 200:
                    return process
            except requests.RequestException:
                pass
            time.sleep(.2)
        process.terminate()
        process.wait(timeout=5)
        raise RuntimeError('Rollback fixture readiness timed out')
    try:
        check = subprocess.run([str(drill.BIN / 'pg_controldata.exe'), str(drill.DATA)], env=env, capture_output=True, timeout=5)
        drill.require(check.returncode == 0 and drill.PG_ID.encode() in check.stdout, 'PG17 identity differs')
        started = True
        subprocess.run([str(drill.BIN / 'pg_ctl.exe'), '-D', str(drill.DATA), '-l', str(drill.DATA.parent / 'provider-only-server.log'),
                        '-o', f'-h 127.0.0.1 -p 55452 -c hba_file={hba.as_posix()} -c shared_buffers=32MB -c max_connections=12 -c fsync=on',
                        '-w', '-t', '15', 'start'], env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20, check=True)
        import psycopg
        from psycopg import sql
        password = secrets.token_urlsafe(32)
        with psycopg.connect(host='127.0.0.1', port=55452, user='py17_efs_admin', dbname=drill.DB,
                             sslmode='disable', gssencmode='disable', connect_timeout=3,
                             passfile=str(R / 'absent-passfile'), autocommit=True) as db:
            identity, directory, version = db.execute("SELECT system_identifier::text,current_setting('data_directory'),current_setting('server_version_num')::int FROM pg_control_system()").fetchone()
            drill.require(identity == drill.PG_ID and Path(directory).resolve() == drill.DATA.resolve()
                          and 170000 <= version < 180000, 'Live PG17 fixture identity differs')
            marker = db.execute('SELECT obj_description(oid,\'pg_namespace\') FROM pg_namespace WHERE nspname=%s', (schema,)).fetchone()
            drill.require(marker and marker[0] == 'owner-approved synthetic-only HTTPS provider drill', 'Unapproved schema')
            flags = db.execute('SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication FROM pg_roles WHERE rolname=%s', (schema,)).fetchone()
            drill.require(flags == (False, False, False, False), 'Fixture role privileges differ')
            db.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(schema), sql.Literal(password)))
        cfg['database_url'] = f'postgresql+psycopg://{schema}:{quote(password,safe="")}@127.0.0.1:55452/{drill.DB}'
        import requests
        client = requests.Session()
        client.trust_env = False
        base = 'http://127.0.0.1:55453'
        worker = boot()
        headers = {'Origin': cfg['origin'], 'Cookie': '__Host-priceyard_test_gate=' + cfg['gate'], 'X-Forwarded-Proto': 'https'}
        body = {'email': drill.EMAIL, 'password': cfg['synthetic_password'], 'remember': True}
        response = client.post(base + '/api/auth/browser/login', json=body, headers=headers, timeout=3)
        drill.require(response.status_code == 200, 'Current application login failed')
        token = response.cookies.get('__Host-priceyard_session')
        drill.require(token, 'Synthetic session missing')
        metadata = response.json()
        headers.update({'Cookie': headers['Cookie'] + '; __Host-priceyard_session=' + token,
                        'x-priceyard-csrf': metadata['csrf_token'], 'x-priceyard-session': metadata['session_id']})
        drill.require(client.get(base + '/api/auth/browser/session', headers=headers, timeout=3).status_code == 200, 'Session not usable before logout')
        drill.require(client.post(base + '/api/auth/logout', headers=headers, timeout=3).status_code == 204, 'Fixture logout failed')
        worker.terminate()
        worker.wait(timeout=5)
        cfg.update(application_path=str(candidate), refresh_synthetic_password=False)
        worker = boot()
        drill.require(client.get(base + '/api/auth/browser/session', headers=headers, timeout=3).status_code == 401, 'Rollback reactivated a revoked token')
        headers['Cookie'] = '__Host-priceyard_test_gate=' + cfg['gate']
        response = client.post(base + '/api/auth/browser/login', json=body, headers=headers, timeout=3)
        drill.require(response.status_code == 200, 'Rollback application login failed')
        report.update(status='passed', exact_reviewed_application_source=True,
                      revoked_session_stays_revoked=True, normal_login_works=True,
                      current_security_schema_retained=True, hosted_Render_runtime_verified=False)
    except Exception as exc:
        report.update(status='stopped', error_type=type(exc).__name__)
        if type(exc) is RuntimeError:
            report['safe_reason'] = str(exc)
    finally:
        if worker and worker.poll() is None:
            worker.terminate()
            worker.wait(timeout=5)
        report['worker_stopped'] = worker is None or worker.poll() is not None
        if started:
            subprocess.run([str(drill.BIN / 'pg_ctl.exe'), '-D', str(drill.DATA), '-m', 'fast', '-w', '-t', '15', 'stop'],
                           env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20)
        report['postgres_stopped'] = not (drill.DATA / 'postmaster.pid').exists()
        log.close()
        OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
