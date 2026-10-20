"""One remaining-only HTTPS window; no email, backup, migration or deployment."""
import base64
import hashlib
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
    prior = json.loads(d.REPORT.read_text())
    rollback = json.loads((d.RUN / 'rollback-result.json').read_text())
    d.require(prior['tunnel_closed'] and prior['postgres_stopped'] and rollback['status'] == 'passed', 'Prior cleanup/rollback required')
    for port in (55452, 55453, 55454):
        with socket.socket() as check:
            check.settimeout(.2)
            d.require(check.connect_ex(('127.0.0.1', port)) != 0, 'Occupied fixture port; no process stopped')
    output = d.RUN / 'remaining-result.json'
    if '--resume-unconfirmed-window' in sys.argv:
        previous = json.loads(output.read_text())
        safe_startup_stop = previous.get('status') == 'stopped' and previous.get('error_type') == 'ConnectionError'
        d.require((previous.get('status') == 'partial' or safe_startup_stop) and not previous.get('results')
                  and not previous.get('TEST_webhook_change_owner_confirmed')
                  and all(previous.get(key) for key in ('tunnel_closed', 'worker_stopped', 'postgres_stopped'))
                  and not (d.RUN / 'remaining_TEST_webhook_confirmed.txt').exists(),
                  'Only a closed unconfirmed pre-checkout window may resume')
        prefix = 'closed-unconfirmed-' + str(time.time_ns()) + '-'
        for name in ('remaining-result.json', 'remaining-tunnel.log', 'remaining_stop.txt'):
            source = d.RUN / name
            if source.exists():
                source.rename(d.RUN / (prefix + name))
    if '--retry-prepayment' in sys.argv:
        previous = json.loads(output.read_text())
        d.require(previous.get('stop_reason') == 'Owner/controller stop requested'
                  and not previous.get('results') and not previous.get('TEST_webhook_change_owner_confirmed')
                  and all(previous.get(key) for key in ('tunnel_closed', 'worker_stopped', 'postgres_stopped')),
                  'Only the clean pre-payment checker stop may resume')
        for name in ('remaining-result.json', 'remaining-tunnel.log', 'remaining_stop.txt'):
            source = d.RUN / name
            target = d.RUN / ('prepayment-checker-stop-' + name)
            d.require(source.exists() and not target.exists(), 'Retained pre-payment evidence differs')
        for name in ('remaining-result.json', 'remaining-tunnel.log', 'remaining_stop.txt'):
            (d.RUN / name).rename(d.RUN / ('prepayment-checker-stop-' + name))
    d.require(not output.exists(), 'Existing continuation evidence retained')
    for name in ('config.yml', 'config.yaml'):
        d.require(not (Path.home() / '.cloudflared' / name).exists(), 'Existing tunnel configuration requires review')
    cloud = d.RUN / 'cloudflared-2026.10.2.exe'
    d.require(cloud.is_file() and hashlib.sha256(cloud.read_bytes()).hexdigest() == d.CLOUDFLARE_SHA, 'Cached tunnel binary differs')
    d.require((d.RUN / 'dist/index.html').is_file(), 'Previously verified frontend build missing')
    hba = d.RUN / 'synthetic-only-pg_hba.conf'
    content = hba.read_text(encoding='ascii')
    match = re.search(r'^host priceyard17_efs_synthetic (py_provider_[0-9a-f]{12}) 127\.0\.0\.1/32 scram-sha-256$', content, re.M)
    d.require(match, 'Synthetic role missing')
    schema = match[1]
    expected = f'host postgres,{d.DB} py17_efs_admin 127.0.0.1/32 trust\nhost {d.DB} {schema} 127.0.0.1/32 scram-sha-256\nhost all all 0.0.0.0/0 reject\nhost all all ::/0 reject\n'
    d.require(content == expected and not (d.DATA / 'postmaster.pid').exists(), 'Fixture state differs')
    cfg = d.fields(d.ROOT / 'backend/.env', {'PAYSTACK_SECRET_KEY', 'PAYSTACK_PUBLIC_KEY', 'GOOGLE_CLIENT_ID'})
    d.require(cfg.get('PAYSTACK_SECRET_KEY', '').startswith('sk_test_') and cfg.get('PAYSTACK_PUBLIC_KEY', '').startswith('pk_test_'), 'TEST credentials required')
    d.require(cfg.get('GOOGLE_CLIENT_ID') == d.fields(d.ROOT / 'frontend/.env', {'VITE_GOOGLE_CLIENT_ID'}).get('VITE_GOOGLE_CLIENT_ID'), 'Google IDs differ')
    cfg.update(schema=schema, synthetic_password=secrets.token_urlsafe(24), jwt_secret=secrets.token_urlsafe(48),
               gate=secrets.token_urlsafe(36), BREVO_API_KEY='', SMTP_FROM_EMAIL='synthetic@example.com',
               refresh_synthetic_password=True, email_disabled=True)
    env = d.clean_environment()
    env.update(PGPASSFILE=str(d.RUN / 'absent-passfile'), PGSERVICEFILE=str(d.RUN / 'absent-servicefile'))
    report = {'status': 'starting', 'synthetic_only': True, 'production_changes': False,
              'production_database_connections': 0, 'real_money_transactions': 0, 'email_sending_disabled': True,
              'reused_build_and_database': True, 'results': {}, 'release_authorized': False}
    def save():
        output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    server = tunnel = dummy = None
    started = False
    log = (d.RUN / 'remaining-control.log').open('ab')
    tunnel_log = None
    connection = None
    try:
        check = subprocess.run([str(d.BIN / 'pg_controldata.exe'), str(d.DATA)], env=env, capture_output=True, timeout=5)
        d.require(check.returncode == 0 and d.PG_ID.encode() in check.stdout, 'PG17 identity differs')
        started = True
        subprocess.run([str(d.BIN / 'pg_ctl.exe'), '-D', str(d.DATA), '-l', str(d.DATA.parent / 'provider-only-server.log'),
                        '-o', f'-h 127.0.0.1 -p 55452 -c hba_file={hba.as_posix()} -c shared_buffers=32MB -c max_connections=12 -c fsync=on',
                        '-w', '-t', '15', 'start'], env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20, check=True)
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
            d.require(marker == ('owner-approved synthetic-only HTTPS provider drill',) and flags == (False, False, False, False), 'Fixture ownership differs')
            db.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(schema), sql.Literal(password)))
        cfg['database_url'] = f'postgresql+psycopg://{schema}:{quote(password,safe="")}@127.0.0.1:55452/{d.DB}'
        connection = psycopg.connect(host='127.0.0.1', port=55452, user=schema, password=password, dbname=d.DB,
                                     sslmode='disable', gssencmode='disable', connect_timeout=3, autocommit=True,
                                     options=f'-c search_path={schema} -c statement_timeout=3000 -c default_transaction_read_only=on')
        class Closed(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(503)
                self.end_headers()
            def log_message(self, *args):
                pass
        dummy = http.server.ThreadingHTTPServer(('127.0.0.1', d.PORT), Closed)
        threading.Thread(target=dummy.serve_forever, daemon=True).start()
        log_path = d.RUN / 'remaining-tunnel.log'
        d.require(not log_path.exists(), 'Prior tunnel log retained')
        tunnel_log = log_path.open('xb')
        tunnel = subprocess.Popen([str(cloud), '--no-autoupdate', 'tunnel', '--url', 'http://127.0.0.1:55453',
                                   '--protocol', 'http2', '--edge-ip-version', '4', '--metrics', '127.0.0.1:55454'],
                                  stdout=tunnel_log, stderr=tunnel_log, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            origins = re.findall(r'https://[a-z0-9-]+\.trycloudflare\.com', log_path.read_text(errors='replace'))
            origins = [origin for origin in origins if origin != 'https://api.trycloudflare.com']
            if origins:
                cfg['origin'] = origins[0]
                break
            d.require(tunnel.poll() is None, 'Tunnel stopped')
            time.sleep(.25)
        d.require(cfg.get('origin'), 'Tunnel readiness timed out')
        dummy.shutdown()
        dummy.server_close()
        dummy = None
        server = subprocess.Popen([sys.executable, '-I', '-B', str(Path(d.__file__).resolve()), '--worker'], stdin=subprocess.PIPE,
                                  stdout=log, stderr=log, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        server.stdin.write((json.dumps(cfg) + '\n').encode())
        server.stdin.close()
        import requests
        client = requests.Session()
        client.trust_env = False
        local = 'http://127.0.0.1:55453'
        def stats():
            return client.get(local + '/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=3).json()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            d.require(server.poll() is None, 'Provider worker stopped')
            try:
                if stats().get('synthetic_only'):
                    break
            except (requests.RequestException, ValueError):
                pass
            time.sleep(.2)
        else:
            raise RuntimeError('Worker readiness timed out')
        # A newly issued public hostname can precede DNS/edge readiness. Check
        # only this exact generated origin, serially and with a hard bound.
        report['public_origin'] = cfg['origin']
        for attempt in range(8):
            try:
                probe = client.get(cfg['origin'] + '/api/payments/webhook', timeout=(3, 6),
                                   allow_redirects=False, verify=True)
                report['public_probe_status'] = probe.status_code
                if probe.status_code == 405 and 'POST' in probe.headers.get('allow', ''):
                    break
                d.require(probe.status_code in (502, 503, 530), 'Unexpected public backend route')
            except requests.ConnectionError as error:
                # Exception classes only: never log URLs, headers or credentials.
                names, seen, current = [], set(), error
                while current is not None and id(current) not in seen and len(names) < 6:
                    seen.add(id(current))
                    names.append(type(current).__name__)
                    current = current.__cause__ or current.__context__
                report['public_probe_error_classes'] = names
            except requests.Timeout:
                report['public_probe_error_classes'] = ['Timeout']
            time.sleep(2)
        else:
            raise RuntimeError('Bounded public HTTPS readiness failed; no checkout attempted')
        report['public_HTTPS_backend_route_checked'] = True
        report.update(status='awaiting_TEST_webhook_change', public_origin=cfg['origin'],
                      TEST_webhook_url=cfg['origin'] + '/api/payments/webhook', maximum_window_seconds=900)
        save()
        print(json.dumps({'status': report['status'], 'TEST_webhook_url': report['TEST_webhook_url']}), flush=True)
        # The owner must explicitly confirm the exact new TEST URL before any
        # checkout creation/completion. Never infer provider settings from time.
        marker = d.RUN / 'remaining_TEST_webhook_confirmed.txt'
        end = time.monotonic() + 900
        confirmed = False
        handled = False
        while time.monotonic() < end:
            d.require(server.poll() is None and tunnel.poll() is None, 'Test process stopped')
            if (d.RUN / 'remaining_stop.txt').exists():
                report['stop_reason'] = 'Owner/controller stop requested'
                break
            if marker.exists() and not confirmed:
                d.require(marker.read_text().strip() == report['TEST_webhook_url'], 'TEST setting confirmation differs')
                confirmed = True
                report['TEST_webhook_change_owner_confirmed'] = True
                # Credentials/gateway ticket stay private; only the actual owner
                # browser receives the protected synthetic testing entry.
                os.startfile(cfg['origin'] + '/?ticket=' + quote(cfg['gate']))
                browser_env = dict(env, PLAYWRIGHT_BROWSERS_PATH=str(d.ROOT / '.git/priceyard-local-recovery-20261015/p00/runtime/browser-binaries'))
                for name, suffix in (('LOCALAPPDATA', 'Local'), ('APPDATA', 'Roaming'), ('USERPROFILE', 'Profile')):
                    browser_env[name] = str(d.LAB / 'runtime/browser-support' / suffix)
                browser_input = {'origin': cfg['origin'], 'gate': cfg['gate'], 'email': d.EMAIL,
                                 'password': cfg['synthetic_password'], 'checkout_url': None}
                tested = subprocess.run([r'C:\Program Files\nodejs\node.exe', str(d.LAB / 'provider_browser.mjs')],
                                        input=json.dumps(browser_input), env=browser_env, capture_output=True,
                                        text=True, encoding='utf-8', errors='replace', timeout=60)
                report['results']['browser'] = json.loads(tested.stdout) if tested.returncode == 0 else {'status': 'not_verified', 'error_type': 'BrowserProcessFailed'}
                headers = {'Origin': cfg['origin'], 'Cookie': '__Host-priceyard_test_gate=' + cfg['gate'], 'X-Forwarded-Proto': 'https'}
                login = client.post(local + '/api/auth/browser/login', headers=headers,
                                    json={'email': d.EMAIL, 'password': cfg['synthetic_password'], 'remember': True}, timeout=5)
                d.require(login.status_code == 200, 'Test checkout session failed')
                session = login.json()
                headers.update({'Cookie': headers['Cookie'] + '; __Host-priceyard_session=' + login.cookies['__Host-priceyard_session'],
                                'x-priceyard-csrf': session['csrf_token'], 'x-priceyard-session': session['session_id']})
                response = client.post(local + '/api/payments/initiate', json={'plan': 'monthly'}, headers=headers, timeout=25)
                d.require(response.status_code == 200, 'New callback TEST checkout failed')
                checkout = response.json()
                from urllib.parse import urlsplit
                d.require(urlsplit(checkout['authorization_url']).hostname == 'checkout.paystack.com', 'Checkout host differs')
                report['results']['new_callback_TEST_checkout_initialized'] = True
                (d.RUN / 'remaining-checkout.json').write_text(json.dumps(checkout), encoding='utf-8')
                os.startfile(checkout['authorization_url'])
                report['status'] = 'awaiting_approved_TEST_checkout_and_Google_consent'
                print(json.dumps({'status': report['status'], 'browser': report['results']['browser']}), flush=True)
            state = stats()
            if state['google_logins']:
                report['results']['Google_verified_linked_test_identity'] = 'passed'
            if confirmed and state['private_webhooks'] and not handled:
                event = next((event for event in state['private_webhooks']
                              if json.loads(base64.b64decode(event['body'])).get('event') == 'charge.success'), None)
                if event:
                    body = base64.b64decode(event['body'])
                    reference = json.loads(body)['data']['reference']
                    d.require(reference == checkout['reference'], 'Unrelated TEST webhook rejected')
                    def snapshot():
                        return connection.execute('SELECT p.status,p.amount,p.currency,s.status,s.plan_name,s.end_date,s.payment_reference FROM payments p JOIN subscriptions s ON s.user_id=p.user_id WHERE p.reference=%s', (reference,)).fetchone()
                    before = snapshot()
                    d.require(before and before[0] == 'success' and str(before[1]) == '2500.00' and before[2:5] == ('NGN','active','paid_monthly') and before[6] == reference, 'TEST subscription activation differs')
                    report['results']['genuine_signed_TEST_webhook_and_subscription_activation'] = 'passed'
                    for _ in range(2):
                        replay = client.post(cfg['origin'] + '/api/payments/webhook', data=body,
                                             headers={'x-paystack-signature': event['signature'], 'Content-Type': 'application/json'}, timeout=15)
                        d.require(replay.status_code == 200 and snapshot() == before, 'Genuine TEST event replay changed purchased value')
                    report['results']['genuine_event_replay_no_duplicate_days'] = 'passed'
                    handled = True
            save()
            if handled and state['google_logins']:
                report['stop_reason'] = 'Remaining provider checks completed'
                break
            time.sleep(2)
        report['status'] = 'partial' if not (handled and report['results'].get('Google_verified_linked_test_identity')) else 'passed_provider_window'
    except Exception as exc:
        report.update(status='stopped', error_type=type(exc).__name__)
        if type(exc) is RuntimeError:
            report['safe_stop_reason'] = str(exc)
    finally:
        if dummy:
            dummy.shutdown()
            dummy.server_close()
        for process in (tunnel, server):
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        if connection:
            connection.close()
        report['tunnel_closed'] = tunnel is None or tunnel.poll() is not None
        report['worker_stopped'] = server is None or server.poll() is not None
        if started:
            subprocess.run([str(d.BIN / 'pg_ctl.exe'), '-D', str(d.DATA), '-m', 'fast', '-w', '-t', '15', 'stop'],
                           env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20)
        report['postgres_stopped'] = not (d.DATA / 'postmaster.pid').exists()
        if tunnel_log:
            tunnel_log.close()
        log.close()
        save()
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
