"""One bounded synthetic Render-edge drill; no production settings or providers."""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[1]
RUN = LAB / 'runtime/render-hosted-20261020'
ORIGIN = 'https://priceyard-py35-check-20261020.onrender.com'
PORT = 55446
CLOUD = LAB / 'runtime/provider-tunnel-20261020/cloudflared-2026.10.2.exe'
CLOUD_SHA = '12c7c887f8aaab779aef1dfa9b60673530a5adb88ecc55dd6df8f56e0b70f199'


def worker():
    cfg = json.loads(sys.stdin.readline())
    if cfg.get('origin') != ORIGIN or not re.fullmatch('[0-9a-f]{32}', cfg.get('proof', '')):
        raise RuntimeError('Pinned synthetic target required')
    sys.path.insert(0, str(LAB))
    import guard
    guard.isolate()
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from fastapi import Request
    from starlette.responses import JSONResponse
    from app.config import get_settings
    from app.database import Base, get_db
    from app.main import app
    from app.models.user import User
    from app.request_bounds import RequestBoundsMiddleware
    from app.services.subscription_service import build_trial_subscription
    from app.utils.password import hash_password
    settings = get_settings()
    settings.app_env = 'staging'  # Always exercise the real Secure cookie policy.
    settings.frontend_url = settings.cors_origins = ORIGIN
    engine = create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(full_name='Synthetic Routing', email='routing@example.com',
                    password_hash=hash_password('SyntheticRouting8!'), role='free_user',
                    is_active=True, referral_code='ROUTING')
        user.subscription = build_trial_subscription(user=user)
        db.add(user)
        db.commit()

    def sessions():
        with Session(engine, expire_on_commit=False) as db:
            yield db

    app.dependency_overrides[get_db] = sessions
    import asyncio
    lock = asyncio.Lock()
    admitted = {('/auth/browser/login', 'POST'), ('/auth/browser/session', 'GET'),
                ('/auth/me', 'GET'), ('/auth/logout', 'POST')}
    counts = {}

    async def isolated(scope, receive, send):
        if scope['type'] != 'http':
            return await app(scope, receive, send)
        path, method = scope['path'], scope['method']
        async with lock:
            key = method + ' ' + path
            counts[key] = counts.get(key, 0) + 1
            if sum(counts.values()) > 160:
                return await JSONResponse({'detail': 'Synthetic request budget reached'}, status_code=429)(scope, receive, send)
            if (path, method) == ('/health', 'GET'):
                return await JSONResponse({'synthetic_only': True, 'proof': cfg['proof']},
                                          headers={'Cache-Control': 'private, no-store'})(scope, receive, send)
            if (path, method) == ('/__probe_status', 'GET'):
                return await JSONResponse({'synthetic_only': True, 'counts': counts},
                                          headers={'Cache-Control': 'private, no-store'})(scope, receive, send)
            if (path, method) == ('/probe', 'POST'):
                request = Request(scope, receive)
                body = await request.body()
                response = JSONResponse({'proof': cfg['proof'], 'method': method,
                    'query': scope['query_string'].decode('ascii'),
                    'body_sha256': hashlib.sha256(body).hexdigest()}, status_code=207,
                    headers={'Cache-Control': 'private, no-store'})
                for name in ('__Host-py_route_one', '__Host-py_route_two'):
                    response.set_cookie(name, 'synthetic', secure=True, httponly=True,
                                        samesite='lax', path='/', max_age=120)
                return await response(scope, receive, send)
            if (path, method) not in admitted:
                return await JSONResponse({'detail': 'Synthetic route not admitted'}, status_code=404,
                                          headers={'Cache-Control': 'private, no-store'})(scope, receive, send)
            # Do not repair forwarded Origin, Cookie, headers, bodies or cache policy.
            return await app(scope, receive, send)

    import uvicorn
    uvicorn.run(RequestBoundsMiddleware(isolated, max_body_bytes=8192), host='127.0.0.1',
                port=PORT, access_log=False, log_level='warning', proxy_headers=False,
                timeout_keep_alive=5, limit_concurrency=8)


def controller():
    renewal = sys.argv[1:] == ['--renew-expired-window']
    retained_post = None
    if hashlib.sha256(CLOUD.read_bytes()).hexdigest() != CLOUD_SHA:
        raise RuntimeError('Cached tunnel binary hash mismatch')
    with socket.socket() as probe:
        probe.settimeout(1)
        if probe.connect_ex(('127.0.0.1', PORT)) == 0:
            raise RuntimeError('Test port already occupied; no process stopped')
    if RUN.exists():
        if not renewal and sys.argv[1:] != ['--resume-dns-readiness']:
            raise RuntimeError('Existing drill preserved; read its result instead of repeating')
        old = json.loads((RUN / 'result.json').read_text())
        if renewal:
            if (old.get('status') != 'STOPPED' or not old.get('owned_processes_stopped')
                    or old.get('error') != 'Test window expired without rewrite confirmation'
                    or old.get('origin') != ORIGIN or old.get('synthetic_only') is not True
                    or old.get('production_access') is not False or old.get('providers_contacted') != 0
                    or not isinstance(old.get('expires_at_epoch'), (int, float))
                    or old['expires_at_epoch'] > time.time()
                    or old.get('independent_upstream_POST') != 'PASS'
                    or (RUN / 'browser-result.json').exists()
                    or (RUN / 'rewrite-saved.txt').exists() or RUN.is_symlink()):
                raise RuntimeError('Only a stopped, expired and unconfirmed test window may be renewed')
            archive = RUN / ('expired-window-' + str(int(old['expires_at_epoch'])))
            retained_post = old['independent_upstream_POST']
            names = ('result.json', 'state.json', 'worker.log', 'tunnel.log')
            if (RUN / 'saved-route-observation.json').exists():
                names += ('saved-route-observation.json',)
        else:
            if (old.get('status') != 'STOPPED' or not old.get('owned_processes_stopped')
                    or 'NameResolutionError' not in old.get('error', '')
                    or (RUN / 'state.json').exists() or (RUN / 'browser-result.json').exists()
                    or (RUN / 'dns-readiness-stop').exists() or RUN.is_symlink()):
                raise RuntimeError('Only the preserved pre-verification DNS-readiness stop may resume once')
            archive = RUN / 'dns-readiness-stop'
            names = ('result.json', 'worker.log', 'tunnel.log')
        if archive.exists() or archive.resolve().parent != RUN.resolve():
            raise RuntimeError('Refusing to overwrite preserved test-window evidence')
        # Fixed local files only; preserve all previous results without deleting.
        for name in names:
            if (RUN / name).is_symlink() or not (RUN / name).is_file():
                raise RuntimeError('Unexpected synthetic log entry')
        archive.mkdir()
        for name in names:
            item = RUN / name
            item.replace(archive / name)
    elif renewal:
        raise RuntimeError('Renewal requires the existing verified synthetic environment')
    RUN.mkdir(exist_ok=renewal or sys.argv[1:] == ['--resume-dns-readiness'])
    cfg = {'origin': ORIGIN, 'proof': secrets.token_hex(16)}
    env = {key: os.environ[key] for key in ('SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'PATH', 'TEMP', 'TMP') if key in os.environ}
    python = ROOT / '.git/priceyard-local-recovery-20261015/p00/runtime/venv/Scripts/python.exe'
    processes = []
    report = {'status': 'starting', 'synthetic_only': True, 'production_access': False,
              'providers_contacted': 0, 'new_database': False, 'origin': ORIGIN}
    if renewal:
        report['expired_window_renewed'] = True
        report['completed_tests_repeated'] = False
        report['independent_upstream_POST_retained_without_rerun'] = True
    import requests
    http = requests.Session()
    http.trust_env = False
    try:
        with (RUN / 'worker.log').open('w') as log:
            server = subprocess.Popen([str(python), str(Path(__file__).resolve()), '--worker'],
                cwd=RUN, env=env, stdin=subprocess.PIPE, stdout=log, stderr=log,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(server)
        server.stdin.write(json.dumps(cfg) + '\n')
        server.stdin.close()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if server.poll() is not None:
                raise RuntimeError('Isolated API stopped; inspect synthetic worker log')
            try:
                value = http.get(f'http://127.0.0.1:{PORT}/health', timeout=2).json()
                if value.get('proof') == cfg['proof']:
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            raise RuntimeError('Isolated API startup timeout')
        with (RUN / 'tunnel.log').open('w') as log:
            tunnel = subprocess.Popen([str(CLOUD), '--no-autoupdate', 'tunnel', '--url',
                f'http://127.0.0.1:{PORT}', '--protocol', 'http2', '--edge-ip-version', '4'],
                cwd=RUN, env=env, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(tunnel)
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if tunnel.poll() is not None:
                raise RuntimeError('Temporary tunnel stopped')
            match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', (RUN / 'tunnel.log').read_text(errors='replace'))
            if match:
                upstream = match[0]
                break
            time.sleep(1)
        else:
            raise RuntimeError('Temporary tunnel startup timeout')
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if tunnel.poll() is not None:
                raise RuntimeError('Tunnel stopped during readiness checks')
            # A generated URL precedes registration/DNS propagation. Do not
            # mistake that setup interval for a failed application test.
            if 'Registered tunnel connection' in (RUN / 'tunnel.log').read_text(errors='replace'):
                try:
                    verified = http.get(upstream + '/health', timeout=(3, 5), allow_redirects=False)
                    if verified.status_code == 200 and verified.json().get('proof') == cfg['proof']:
                        break
                except (requests.RequestException, ValueError):
                    pass
            time.sleep(1)
        else:
            raise RuntimeError('Public synthetic target identity not verified within readiness budget')
        # Renewal needs only fresh HTTPS identity/liveness. Retain the completed
        # transport control instead of repeating POST/login/browser tests.
        if not renewal:
            raw = b'{\n  "synthetic": true\n}'
            control = http.post(upstream + '/probe?one=a%20b&one=c', data=raw, timeout=(5, 20), allow_redirects=False)
            if control.status_code != 207 or control.json().get('body_sha256') != hashlib.sha256(raw).hexdigest():
                raise RuntimeError('Synthetic POST control failed')
        window_seconds = 1800 if renewal else 900
        report.update(status='awaiting_test_only_rewrite', upstream=upstream,
                      destination=upstream + '/*', proof=cfg['proof'],
                      created_at_epoch=time.time(), expires_at_epoch=time.time() + window_seconds,
                      manual_window_seconds=window_seconds,
                      independent_upstream_POST=retained_post if renewal else 'PASS')
        (RUN / 'state.json').write_text(json.dumps(report, indent=2))
        print(json.dumps({key: report[key] for key in ('status', 'origin', 'destination', 'expires_at_epoch')}), flush=True)
        deadline = time.monotonic() + window_seconds
        route_ready = False
        next_route_check = 0
        while time.monotonic() < deadline and not (RUN / 'rewrite-saved.txt').exists():
            if any(process.poll() is not None for process in processes):
                raise RuntimeError('Owned test process stopped before confirmation')
            if (RUN / 'stop.txt').exists():
                raise RuntimeError('Controlled stop requested')
            if time.monotonic() >= next_route_check:
                next_route_check = time.monotonic() + 15
                try:
                    check = http.get(ORIGIN + '/api/health?py35check=' + cfg['proof'],
                                     timeout=(3, 5), allow_redirects=False)
                    if check.status_code == 200 and check.json().get('proof') == cfg['proof']:
                        # The owner has authorized this drill. Matching the new
                        # identity proves the test-only rewrite was saved; no
                        # login is sent through an old, redirected or wrong route.
                        route_ready = True
                        report['route_confirmation'] = 'fresh_saved_Render_route_identity_verified'
                        break
                except (requests.RequestException, ValueError):
                    pass
            time.sleep(1)
        if not route_ready and not (RUN / 'rewrite-saved.txt').exists():
            raise RuntimeError('Test window expired without rewrite confirmation')
        with (RUN / 'browser.log').open('w') as log:
            checker = subprocess.Popen([str(python), str(LAB / 'run_browser.py'), 'render_hosted_checks.mjs'],
                cwd=ROOT, env=env, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(checker)
        try:
            checker.wait(timeout=120)
        except subprocess.TimeoutExpired:
            # This PID is the still-running process just created above. Stop its
            # descendants too, so an interrupted browser cannot remain running.
            taskkill = Path(env['SYSTEMROOT']) / 'System32/taskkill.exe'
            subprocess.run([str(taskkill), '/PID', str(checker.pid), '/T', '/F'],
                           env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
            checker.wait(timeout=5)
            raise RuntimeError('Bounded browser window expired; owned process tree stopped')
        browser_result = RUN / 'browser-result.json'
        if not browser_result.exists():
            raise RuntimeError('Hosted browser produced no safe report')
        report['browser'] = json.loads(browser_result.read_text())
        report['status'] = report['browser']['status']
        report['upstream_counts'] = http.get(f'http://127.0.0.1:{PORT}/__probe_status', timeout=3).json()['counts']
    except Exception as error:
        report.update(status='STOPPED', error_type=type(error).__name__, error=str(error))
    finally:
        http.close()
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        report['owned_processes_stopped'] = all(process.poll() is not None for process in processes)
        (RUN / 'result.json').write_text(json.dumps(report, indent=2))
        print(json.dumps({'status': report['status'], 'owned_processes_stopped': report['owned_processes_stopped']}), flush=True)


if __name__ == '__main__':
    worker() if sys.argv[1:] == ['--worker'] else controller()
