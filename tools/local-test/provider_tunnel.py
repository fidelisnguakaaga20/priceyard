"""Owner-approved, bounded provider drill; never a production startup command."""
from __future__ import annotations

import argparse
import hashlib
import http.server
import io
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
from urllib.parse import quote, urlsplit
import urllib.request

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[1]
RUN = LAB / 'runtime/provider-tunnel-20261020'
PRIVATE = Path(r'C:\Users\HP\AppData\Local\PriceYardPrivateBackup')
BIN = PRIVATE / 'pg17-tools-17.11-5/pgsql/bin'
DATA = PRIVATE / 'PrivateRestoreEfs/pg17-efs-check-20261019/efs-restored-cluster'
PG_ID = '7698190245493700556'
DB = 'priceyard17_efs_synthetic'
EMAIL = 'fidelisnguakaaga20@gmail.com'
PORT = 55453
CLOUDFLARE_SHA = '12c7c887f8aaab779aef1dfa9b60673530a5adb88ecc55dd6df8f56e0b70f199'
CLOUDFLARE_URL = 'https://github.com/cloudflare/cloudflared/releases/download/2026.10.2/cloudflared-windows-amd64.exe'
REPORT = RUN / 'result.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def fields(path, names):
    """Explicit owner-authorized selected-field read; never load application dotenv."""
    found = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
        if match and match[1] in names:
            value = match[2].strip()
            if len(value) > 1 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            found[match[1]] = value
    return found


def clean_environment():
    return {key: os.environ[key] for key in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP') if key in os.environ}


def rollback_source():
    """Only tracked application source; no old migrations/configuration/secrets."""
    import tarfile
    git = r'C:\Program Files\Git\cmd\git.exe'
    tree = subprocess.run([git, 'rev-parse', 'HEAD:backend/app', '2cfbfa6:backend/app'], cwd=ROOT,
                          capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
    require(tree.returncode == 0 and len(tree.stdout.splitlines()) == 2
            and len(set(tree.stdout.splitlines())) == 1, 'Security-aware rollback app tree differs')
    archive = subprocess.run([git, 'archive', '--format=tar', '2cfbfa6', 'backend/app'], cwd=ROOT,
                             capture_output=True, timeout=10)
    require(archive.returncode == 0 and len(archive.stdout) < 3*1024*1024, 'Rollback source budget')
    rollback = RUN / 'rollback'
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as bundle:
        members = bundle.getmembers()
        require(len(members) <= 200 and all((m.isfile() or m.isdir()) and not m.name.startswith('/')
                and '..' not in Path(m.name).parts and (m.name in {'backend', 'backend/app'} or m.name.startswith('backend/app/'))
                for m in members), 'Unexpected rollback source entry')
        if rollback.exists() and any(rollback.iterdir()):
            expected = {m.name for m in members if m.isfile()}
            actual = {p.relative_to(rollback).as_posix() for p in rollback.rglob('*') if p.is_file()}
            require(actual == expected and all(not p.is_symlink() for p in rollback.rglob('*')), 'Rollback source inventory differs')
            for member in members:
                if member.isfile():
                    require((rollback / member.name).read_bytes() == bundle.extractfile(member).read(), 'Rollback source bytes differ')
        else:
            rollback.mkdir(exist_ok=True)
            bundle.extractall(rollback, filter='data')
    return rollback / 'backend'


def worker():
    cfg = json.loads(sys.stdin.readline())
    require(re.fullmatch(r'py_provider_[0-9a-f]{12}', cfg['schema']), 'Unapproved synthetic schema')
    local_google = cfg.get('google_only_local', False)
    require((local_google and cfg['origin'] == 'http://127.0.0.1:5173')
            or (not local_google and re.fullmatch(r'https://[a-z0-9-]+\.trycloudflare\.com', cfg['origin'])), 'Unapproved test origin')
    require(cfg['PAYSTACK_SECRET_KEY'].startswith('sk_test_') and cfg['PAYSTACK_PUBLIC_KEY'].startswith('pk_test_'), 'TEST keys required')
    env = clean_environment()
    os.environ.clear()
    os.environ.update(env)
    os.chdir(RUN)
    application_path = Path(cfg.get('application_path', str(ROOT / 'backend'))).resolve()
    require(application_path in {(ROOT / 'backend').resolve(), (RUN / 'rollback/backend').resolve()}, 'Unapproved application artifact')
    sys.path.insert(0, str(application_path))
    import logging
    logging.disable(logging.CRITICAL)  # No request bodies, reset tokens or provider errors in logs.
    import pydantic_settings
    original_settings = pydantic_settings.BaseSettings.__init__

    def settings_without_files(self, *args, **kwargs):
        kwargs['_env_file'] = None
        original_settings(self, *args, **kwargs)

    pydantic_settings.BaseSettings.__init__ = settings_without_files
    from app.config import Settings
    import app.config
    settings = Settings(_env_file=None, app_env='test' if local_google else 'staging', debug=False,
                        database_url=cfg['database_url'], jwt_secret=cfg['jwt_secret'],
                        frontend_url=cfg['origin'], cors_origins=cfg['origin'],
                        paystack_secret_key=cfg['PAYSTACK_SECRET_KEY'], paystack_public_key=cfg['PAYSTACK_PUBLIC_KEY'],
                        google_client_id=cfg['GOOGLE_CLIENT_ID'], brevo_api_key=cfg['BREVO_API_KEY'],
                        smtp_from_email=cfg['SMTP_FROM_EMAIL'])
    app.config.get_settings = lambda: settings
    import psycopg
    from psycopg.conninfo import conninfo_to_dict
    real_connect = psycopg.Connection.connect

    def pinned_connect(conninfo='', **kwargs):
        values = conninfo_to_dict(conninfo, **{k: v for k, v in kwargs.items() if k not in ('context', 'autocommit', 'row_factory', 'cursor_factory')})
        require(values.get('host') == '127.0.0.1' and str(values.get('port')) == '55452'
                and values.get('dbname') == DB and values.get('user') == cfg['schema'], 'Non-fixture database rejected')
        connection = real_connect(conninfo, **kwargs)
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_setting('server_version_num')::int,current_database(),current_schema()")
            version, database, schema = cursor.fetchone()
        require(170000 <= version < 180000 and database == DB and schema == cfg['schema'], 'Fixture identity changed')
        if not connection.autocommit:
            connection.rollback()
        return connection

    psycopg.connect = pinned_connect
    psycopg.Connection.connect = pinned_connect
    import sqlalchemy
    real_engine = sqlalchemy.create_engine

    def pinned_engine(url, *args, **kwargs):
        require(str(url) == cfg['database_url'] and 'creator' not in kwargs and not kwargs.get('connect_args'), 'Unexpected engine rejected')
        kwargs['connect_args'] = {'connect_timeout': 3, 'sslmode': 'disable', 'options': '-c search_path=' + cfg['schema'] + ' -c statement_timeout=10000 -c lock_timeout=3000'}
        return real_engine(url, *args, **kwargs)

    sqlalchemy.create_engine = pinned_engine
    counts = {'paystack_requests': 0, 'email_messages_accepted': 0, 'google_logins': 0, 'valid_TEST_webhooks': 0}
    import requests
    original_request = requests.Session.request

    def bounded_request(session, method, url, **kwargs):
        require(cfg.get('external_enabled', True), 'External providers disabled for offline rollback')
        parsed = urlsplit(url)
        if local_google:
            require(method.upper() == 'GET' and url == 'https://www.googleapis.com/oauth2/v1/certs', 'Google-only test forbids other providers')
        require(parsed.scheme == 'https' and not parsed.username and not parsed.password and parsed.port in (None, 443), 'Unsafe provider URL')
        allowed = (parsed.hostname == 'api.paystack.co' and (
            (method.upper() == 'POST' and parsed.path == '/transaction/initialize') or
            (method.upper() == 'GET' and parsed.path.startswith('/transaction/verify/py_'))))
        allowed = allowed or (method.upper() == 'GET' and url == 'https://www.googleapis.com/oauth2/v1/certs')
        require(allowed, 'Provider destination rejected')
        if parsed.hostname == 'api.paystack.co':
            require(kwargs.get('headers', {}).get('Authorization') == 'Bearer ' + cfg['PAYSTACK_SECRET_KEY'], 'TEST authorization required')
            if method.upper() == 'POST':
                body = kwargs.get('json', {})
                require(body.get('email') == EMAIL and body.get('currency') == 'NGN'
                        and body.get('amount') in (250000, 600000)
                        and body.get('callback_url') == cfg['origin'] + '/payment/callback', 'Unapproved checkout request')
            counts['paystack_requests'] += 1
            require(counts['paystack_requests'] <= 16, 'Provider request ceiling')
        session.trust_env = False
        kwargs.update(allow_redirects=False, verify=True, timeout=(3, 15))
        return original_request(session, method, url, **kwargs)

    requests.Session.request = bounded_request
    from app.database import Base, get_engine, get_session_factory
    import app.models
    from app.models.user import User
    from app.services.subscription_service import build_trial_subscription
    from app.utils.password import hash_password
    from sqlalchemy.orm import Session
    engine = get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = db.scalar(sqlalchemy.select(User).where(User.email == EMAIL))
        if user is None:
            user = User(full_name='Synthetic provider tester', email=EMAIL,
                        password_hash=hash_password(cfg['synthetic_password']), role='free_user',
                        is_active=True, referral_code='STAGE' + secrets.token_hex(3).upper())
            user.subscription = build_trial_subscription(user=user)
            db.add(user)
            db.commit()
        elif cfg.get('refresh_synthetic_password'):
            require(user.full_name == 'Synthetic provider tester' and user.role == 'free_user'
                    and db.scalar(sqlalchemy.select(sqlalchemy.func.count(User.id))) == 1,
                    'Only the created synthetic tester may be refreshed')
            user.password_hash = hash_password(cfg['synthetic_password'])
            user.auth_version += 1
            db.commit()

    from app.services import email_service
    original_email = email_service.send_email
    private_email_ids = []
    private_reset_urls = []
    private_webhooks = []

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise RuntimeError('Provider redirect rejected')

    def send_only_approved(*, recipient, subject, body):
        require(not cfg.get('email_disabled', False), 'Previously verified email sending disabled')
        require(recipient == EMAIL and cfg['origin'] in body, 'Unapproved email recipient or link')
        require(counts['email_messages_accepted'] < 2, 'Email ceiling reached')
        require('priceyard.onrender.com' not in body and 'priceyard-api.onrender.com' not in body, 'Production link rejected')
        match = re.search(re.escape(cfg['origin']) + r'/reset-password\?token=[A-Za-z0-9_-]+', body)
        if match:
            private_reset_urls.append(match[0])
        return original_email(recipient=recipient, subject=subject, body=body)

    def approved_brevo(request, timeout=15):
        require(cfg.get('external_enabled', True), 'External email disabled for offline rollback')
        require(request.full_url == 'https://api.brevo.com/v3/smtp/email' and request.get_method() == 'POST', 'Unapproved email endpoint')
        body = json.loads(request.data)
        require(body.get('to') == [{'email': EMAIL}] and not any(body.get(k) for k in ('cc', 'bcc')), 'Unapproved email destinations')
        response = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open(request, timeout=15)
        raw = response.read(65536)
        if response.status in (200, 201, 202):
            counts['email_messages_accepted'] += 1
            private_email_ids.append(json.loads(raw).get('messageId'))
        class BufferedResponse(io.BytesIO):
            status = response.status
        response.close()
        return BufferedResponse(raw)

    email_service.send_email = send_only_approved
    email_service.urlopen = approved_brevo
    # Imported by password_reset_service only after the recipient guard is active.
    from app.main import app as api
    from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
    from starlette.staticfiles import StaticFiles
    from starlette.requests import Request
    from app.services.auth_service import authenticate_or_create_google_user as original_google
    import app.routes.auth_routes
    import app.routes.payment_routes
    original_webhook = app.routes.payment_routes.handle_webhook_event

    def approved_webhook(db, payload):
        if payload.get('event') == 'charge.success':
            require(payload.get('data', {}).get('domain') == 'test', 'Only TEST webhook evidence is allowed')
        original_webhook(db, payload)
        if payload.get('event') == 'charge.success':
            counts['valid_TEST_webhooks'] += 1

    app.routes.payment_routes.handle_webhook_event = approved_webhook

    def approved_google(db, token):
        from app.services import auth_service
        with requests.Session() as transport:
            claims = auth_service.google_id_token.verify_oauth2_token(
                token, auth_service._GoogleCertificateRequest(session=transport), cfg['GOOGLE_CLIENT_ID'])
        require(claims.get('email', '').lower() == EMAIL and claims.get('email_verified') is True,
                'Unapproved Google test identity')
        # Prepare an already-linked fixture only from a genuinely verified test
        # token. Production linking logic is neither replaced nor bypassed.
        user = db.scalar(sqlalchemy.select(User).where(User.email == EMAIL))
        require(user is not None and user.google_id in (None, claims['sub']), 'Unexpected synthetic identity')
        user.google_id = claims['sub']
        user.auth_provider = 'google'
        db.commit()
        result = original_google(db, token)
        counts['google_logins'] += 1
        return result

    app.routes.auth_routes.authenticate_or_create_google_user = approved_google
    web = __import__('fastapi').FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @web.middleware('http')
    async def gate(request: Request, call_next):
        if request.url.path == '/__provider_status' and request.client.host == '127.0.0.1' and request.headers.get('x-provider-controller') == cfg['gate']:
            return JSONResponse({'synthetic_only': True, 'postgresql_major': 17, **counts,
                                 'private_email_ids': private_email_ids, 'private_reset_urls': private_reset_urls,
                                 'private_webhooks': private_webhooks})
        if request.url.path == '/' and request.query_params.get('ticket') == cfg['gate']:
            response = RedirectResponse(cfg['origin'] + '/login' if local_google else '/login', status_code=303)
            response.set_cookie('priceyard_google_test_gate' if local_google else '__Host-priceyard_test_gate',
                                cfg['gate'], secure=not local_google, httponly=True, samesite='lax', path='/')
            response.headers['Referrer-Policy'] = 'no-referrer'
            return response
        gate_name = 'priceyard_google_test_gate' if local_google else '__Host-priceyard_test_gate'
        if (local_google or request.url.path != '/api/payments/webhook') and request.cookies.get(gate_name) != cfg['gate']:
            return JSONResponse({'detail': 'Private synthetic test session required'}, status_code=403)
        if local_google and (request.url.path.startswith('/api/payments') or (request.method == 'POST'
                and request.url.path not in ('/api/auth/browser/google', '/api/auth/logout'))):
            return JSONResponse({'detail': 'Google-only check; other writes disabled'}, status_code=403)
        if request.method == 'POST' and request.url.path in ('/api/auth/register', '/api/auth/forgot-password', '/api/auth/browser/login', '/api/auth/login'):
            body = await request.body()
            try:
                require(json.loads(body).get('email', '').lower() == EMAIL, 'Only approved test identity')
            except Exception:
                return JSONResponse({'detail': 'Only approved test identity'}, status_code=403)
        webhook_body = None
        if request.url.path == '/api/payments/webhook' and request.method == 'POST':
            webhook_body = await request.body()
            if len(webhook_body) > 262144:
                return JSONResponse({'detail': 'Test payload ceiling'}, status_code=413)
        response = await call_next(request)
        if webhook_body and response.status_code == 200 and len(private_webhooks) < 3:
            import base64
            private_webhooks.append({'body': base64.b64encode(webhook_body).decode('ascii'),
                                     'signature': request.headers.get('x-paystack-signature', '')})
        response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade' if local_google else 'no-referrer'
        response.headers['Cache-Control'] = 'private, no-store'
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response

    if local_google:
        # Credentialed browser preflights intentionally carry no cookies. Keep
        # CORS outside the private gate, restricted to the already approved
        # loopback UI origin; actual requests still pass the unchanged gate.
        from starlette.middleware.cors import CORSMiddleware
        web.add_middleware(CORSMiddleware, allow_origins=[cfg['origin']], allow_credentials=True,
                           allow_methods=['GET', 'POST'],
                           allow_headers=['Content-Type', 'X-PriceYard-Csrf', 'X-PriceYard-Session'])
    # Serve original compiled appearance; no test UI or local-only debug endpoints.
    web.mount('/api', api)
    web.mount('/assets', StaticFiles(directory=RUN / 'dist/assets'))
    @web.get('/{path:path}')
    def frontend(path: str):
        asset = (RUN / 'dist' / path).resolve()
        if asset.is_relative_to((RUN / 'dist').resolve()) and asset.is_file():
            return FileResponse(asset)
        return FileResponse(RUN / 'dist/index.html')
    import uvicorn
    def block_private_files(event, args):
        if event == 'open' and args and isinstance(args[0], (str, bytes)):
            name = Path(os.fsdecode(args[0])).name.lower()
            require(not name.startswith('.env') and name not in ('credentials', '.pgpass', 'pgpass.conf'), 'Secret file access denied')
        if event in ('subprocess.Popen', 'os.system'):
            raise RuntimeError('Worker child processes denied')
    sys.addaudithook(block_private_files)
    uvicorn.run(web, host='127.0.0.1', port=55446 if local_google else PORT, workers=1, access_log=False,
                log_level='critical', proxy_headers=True, forwarded_allow_ips='127.0.0.1')


def main():
    RUN.mkdir(exist_ok=True)
    require(not REPORT.exists() or '--resume-launcher' in sys.argv, 'Existing provider result retained; review it before any repeat')
    cfg = fields(ROOT / 'backend/.env', {'PAYSTACK_SECRET_KEY', 'PAYSTACK_PUBLIC_KEY', 'GOOGLE_CLIENT_ID', 'BREVO_API_KEY', 'SMTP_FROM_EMAIL'})
    front = fields(ROOT / 'frontend/.env', {'VITE_GOOGLE_CLIENT_ID'})
    require(cfg.get('PAYSTACK_SECRET_KEY', '').startswith('sk_test_') and cfg.get('PAYSTACK_PUBLIC_KEY', '').startswith('pk_test_'), 'TEST keys required')
    require(cfg.get('GOOGLE_CLIENT_ID') == front.get('VITE_GOOGLE_CLIENT_ID') and bool(cfg.get('GOOGLE_CLIENT_ID')), 'Google configuration differs')
    require(cfg.get('BREVO_API_KEY') and cfg.get('SMTP_FROM_EMAIL'), 'Email configuration missing')
    if '--resume-launcher' in sys.argv:
        prior = json.loads(REPORT.read_text())
        require(prior.get('status') == 'stopped' and prior.get('error_type') == 'TimeoutExpired'
                and not prior.get('provider_results') and prior.get('tunnel_closed')
                and prior.get('postgres_stopped') and not (RUN / 'result-initial-launcher-timeout.json').exists(), 'Only the retained pre-tunnel launcher failure can resume')
        REPORT.rename(RUN / 'result-initial-launcher-timeout.json')
    for port in (PORT, 55452, 55454):
        with socket.socket() as test:
            test.settimeout(.2)
            require(test.connect_ex(('127.0.0.1', port)) != 0, 'Owned test port is occupied; no process stopped')
    require(not (Path.home() / '.cloudflared/config.yml').exists() and not (Path.home() / '.cloudflared/config.yaml').exists(), 'Existing Cloudflare configuration requires review')
    report = {'status': 'running', 'synthetic_only': True, 'production_database_connections': 0,
              'production_migrations': 0, 'production_changes': False, 'tunnel_closed': False,
              'postgres_stopped': False, 'provider_results': {}, 'release_authorized': False}
    def save():
        REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    save()
    pg_started = False
    tunnel = server = None
    dummy = None
    environment = clean_environment()
    environment['PGPASSFILE'] = str(RUN / 'absent-passfile')
    environment['PGSERVICEFILE'] = str(RUN / 'absent-servicefile')
    try:
        cloud = RUN / 'cloudflared-2026.10.2.exe'
        if not cloud.exists():
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(CLOUDFLARE_URL, timeout=30) as source, cloud.open('xb') as output:
                total = 0
                while chunk := source.read(1024 * 1024):
                    total += len(chunk)
                    require(total <= 56_000_000, 'Tunnel download size ceiling')
                    output.write(chunk)
        require(hashlib.sha256(cloud.read_bytes()).hexdigest() == CLOUDFLARE_SHA, 'Cloudflare checksum differs')
        report['cloudflared_official_checksum'] = 'passed'
        require(not (DATA / 'postmaster.pid').exists(), 'Original fixture is not confirmed stopped')
        control = subprocess.run([str(BIN / 'pg_controldata.exe'), str(DATA)], env=environment, capture_output=True, text=True, timeout=10)
        require(control.returncode == 0 and PG_ID in control.stdout, 'Fabricated cluster identity differs')
        require((DATA / 'PG_VERSION').read_text().strip() == '17', 'PG17 required')
        schema = 'py_provider_' + secrets.token_hex(6)
        cfg.update(schema=schema, synthetic_password=secrets.token_urlsafe(24), jwt_secret=secrets.token_urlsafe(48), gate=secrets.token_urlsafe(36))
        db_password = secrets.token_urlsafe(32)
        # Temporary process-only HBA: bootstrap is restricted to its existing
        # synthetic admin/database on literal loopback. Original HBA is untouched.
        hba = RUN / 'synthetic-only-pg_hba.conf'
        hba.write_text(f'host postgres,{DB} py17_efs_admin 127.0.0.1/32 trust\n'
                       + f'host {DB} {schema} 127.0.0.1/32 scram-sha-256\n'
                       + 'host all all 0.0.0.0/0 reject\nhost all all ::/0 reject\n', encoding='ascii')
        # Windows server children can retain captured pipe handles after pg_ctl
        # exits. Use a file rather than communicate() on inherited pipes.
        pg_started = True  # The verified stopped fixture is exclusively ours.
        with (RUN / 'pg-control.log').open('ab') as pg_output:
            result = subprocess.run([str(BIN / 'pg_ctl.exe'), '-D', str(DATA), '-l', str(DATA.parent / 'provider-only-server.log'),
                                     '-o', f'-h 127.0.0.1 -p 55452 -c hba_file={hba.as_posix()} -c shared_buffers=32MB -c max_connections=12 -c fsync=on',
                                     '-w', '-t', '15', 'start'], env=environment, stdout=pg_output, stderr=subprocess.STDOUT, timeout=20)
        require(result.returncode == 0, 'Synthetic PG17 startup failed')
        pg_started = True
        import psycopg
        from psycopg import sql
        with psycopg.connect(host='127.0.0.1', port=55452, dbname='postgres', user='py17_efs_admin',
                             connect_timeout=3, sslmode='disable', gssencmode='disable', passfile=str(RUN / 'absent-passfile'), autocommit=True) as db:
            identity, directory, version = db.execute("SELECT system_identifier::text,current_setting('data_directory'),current_setting('server_version_num')::int FROM pg_control_system()").fetchone()
            require(identity == PG_ID and Path(directory).resolve() == DATA.resolve() and 170000 <= version < 180000, 'Live fixture identity differs')
            require(db.execute("SELECT count(*) FROM pg_roles WHERE rolname LIKE 'py_provider_%'").fetchone()[0] < 2, 'Synthetic fixture budget exhausted')
            db.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {}').format(sql.Identifier(schema), sql.Literal(db_password)))
        # Create only a new marked schema, leaving all original fixture tables.
        with psycopg.connect(host='127.0.0.1', port=55452, dbname=DB, user='py17_efs_admin', connect_timeout=3,
                             sslmode='disable', gssencmode='disable', passfile=str(RUN / 'absent-passfile'), autocommit=True) as db:
            db.execute(sql.SQL('CREATE SCHEMA {} AUTHORIZATION {}').format(sql.Identifier(schema), sql.Identifier(schema)))
            db.execute(sql.SQL('COMMENT ON SCHEMA {} IS {}').format(sql.Identifier(schema), sql.Literal('owner-approved synthetic-only HTTPS provider drill')))
        cfg['database_url'] = f'postgresql+psycopg://{schema}:{quote(db_password, safe="")}@127.0.0.1:55452/{DB}'
        report['pg17_identity_and_loopback_binding'] = 'passed'
        manifest = json.loads((LAB / 'runtime/frontend.json').read_text())
        snapshot = Path(manifest['path']).resolve()
        require(manifest.get('purpose') == 'synthetic-only-no-application-credentials' and snapshot.parent == (LAB / 'runtime').resolve(), 'Unapproved frontend snapshot')
        for folder in ('src', 'public'):
            for source in (ROOT / 'frontend' / folder).rglob('*'):
                if source.is_file():
                    copy = snapshot / source.relative_to(ROOT / 'frontend')
                    require(copy.is_file() and source.read_bytes() == copy.read_bytes(), 'Frontend snapshot is stale')
        build_env = dict(environment, VITE_API_URL='/api', VITE_GOOGLE_CLIENT_ID=cfg['GOOGLE_CLIENT_ID'], NODE_ENV='production')
        result = subprocess.run([r'C:\Program Files\nodejs\node.exe', '--require', str(LAB / 'node_guard.cjs'),
                                 str(snapshot / 'node_modules/vite/bin/vite.js'), 'build', '--mode', 'synthetic', '--outDir', str(RUN / 'dist')],
                                cwd=snapshot, env=build_env, capture_output=True, timeout=60)
        require(result.returncode == 0, 'Isolated frontend build failed')
        report['original_frontend_source_reused'] = True
        save()
        class ClosedBootstrap(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(503)
                self.end_headers()
            def log_message(self, *args):
                pass
        dummy = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), ClosedBootstrap)
        threading.Thread(target=dummy.serve_forever, daemon=True).start()
        tunnel_log = (RUN / 'tunnel.log').open('ab')
        tunnel = subprocess.Popen([str(cloud), '--no-autoupdate', 'tunnel', '--url', f'http://127.0.0.1:{PORT}',
                                   '--protocol', 'http2', '--edge-ip-version', '4', '--metrics', '127.0.0.1:55454'],
                                  stdout=tunnel_log, stderr=tunnel_log, env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', (RUN / 'tunnel.log').read_text(errors='replace'))
            if match and match[0] != 'https://api.trycloudflare.com':
                cfg['origin'] = match[0]
                break
            require(tunnel.poll() is None, 'Tunnel process stopped')
            time.sleep(.25)
        require(cfg.get('origin'), 'Temporary tunnel was not ready within budget')
        dummy.shutdown()
        dummy.server_close()
        dummy = None
        server_log = (RUN / 'server.log').open('ab')
        server = subprocess.Popen([sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker'],
                                  stdin=subprocess.PIPE, stdout=server_log, stderr=server_log, env=environment,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        server.stdin.write((json.dumps(cfg) + '\n').encode())
        server.stdin.close()
        import requests
        session = requests.Session()
        session.trust_env = False
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            require(server.poll() is None, 'Provider worker stopped')
            try:
                probe = session.get(f'http://127.0.0.1:{PORT}/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=1)
                if probe.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(.25)
        else:
            raise RuntimeError('Provider worker readiness failed')
        results = report['provider_results']
        origin = cfg['origin']
        response = session.get(origin + '/?ticket=' + quote(cfg['gate']), timeout=(5, 20), allow_redirects=False)
        require(response.status_code == 303, 'HTTPS gateway failed')
        results['https_private_gateway'] = 'passed'
        headers = {'Origin': origin}
        response = session.post(origin + '/api/auth/browser/login', json={'email': EMAIL, 'password': cfg['synthetic_password'], 'remember': True}, headers=headers, timeout=(5, 20))
        require(response.status_code == 200, 'HTTPS browser login failed')
        metadata = response.json()
        cookie = response.headers.get('set-cookie', '').lower()
        require('__host-priceyard_session=' in cookie and all(flag in cookie for flag in ('httponly', 'secure', 'samesite=lax', 'path=/')), 'Protected cookie flags missing')
        require(session.get(origin + '/api/auth/browser/session', timeout=(5, 15)).status_code == 200, 'HTTPS session persistence failed')
        results['https_login_cookie_and_session'] = 'passed'
        require(session.post(origin + '/api/payments/initiate', json={'plan': 'monthly'}, headers=headers, timeout=(5, 15)).status_code == 403, 'CSRF rejection failed')
        results['https_csrf_rejection'] = 'passed'
        headers.update({'x-priceyard-csrf': metadata['csrf_token'], 'x-priceyard-session': metadata['session_id']})
        response = session.post(origin + '/api/payments/initiate', json={'plan': 'monthly'}, headers=headers, timeout=(5, 25))
        results['paystack_initialize_http_status'] = response.status_code
        checkout = None
        if response.status_code == 200:
            checkout = response.json()
            require(urlsplit(checkout['authorization_url']).hostname == 'checkout.paystack.com', 'Checkout destination differs')
            results['paystack_TEST_initialize'] = 'passed'
            # Private runtime state only. TEST checkout contains no production key.
            (RUN / 'checkout.json').write_text(json.dumps({'origin': origin, 'checkout_url': checkout['authorization_url'], 'reference': checkout['reference']}))
        else:
            results['paystack_TEST_initialize'] = 'failed'
        browser_input = {'origin': origin, 'gate': cfg['gate'], 'email': EMAIL,
                         'password': cfg['synthetic_password'], 'checkout_url': checkout['authorization_url'] if checkout else None}
        browser_env = dict(environment, PLAYWRIGHT_BROWSERS_PATH=str(ROOT / '.git/priceyard-local-recovery-20261015/p00/runtime/browser-binaries'))
        for name, suffix in (('LOCALAPPDATA', 'Local'), ('APPDATA', 'Roaming'), ('USERPROFILE', 'Profile')):
            browser_env[name] = str(LAB / 'runtime/browser-support' / suffix)
        browser = subprocess.run([r'C:\Program Files\nodejs\node.exe', str(LAB / 'provider_browser.mjs')],
                                 input=json.dumps(browser_input), env=browser_env, capture_output=True,
                                 text=True, encoding='utf-8', errors='replace', timeout=65)
        if browser.returncode == 0:
            results['browser'] = json.loads(browser.stdout)
        else:
            results['browser'] = {'status': 'not_verified', 'error_type': 'BrowserProcessFailed'}
        response = session.post(origin + '/api/auth/forgot-password', json={'email': EMAIL}, timeout=(5, 25))
        require(response.status_code == 200, 'Reset endpoint failed')
        status = session.get(f'http://127.0.0.1:{PORT}/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=3).json()
        results['email_provider_acceptance'] = 'passed' if status['email_messages_accepted'] == 1 else 'failed'
        if status['email_messages_accepted'] == 1 and status['private_email_ids']:
            for attempt in range(4):
                event = session.get('https://api.brevo.com/v3/smtp/statistics/events',
                                    params={'messageId': status['private_email_ids'][0], 'limit': 5},
                                    headers={'api-key': cfg['BREVO_API_KEY'], 'accept': 'application/json'},
                                    timeout=(3, 12), allow_redirects=False, verify=True)
                if event.status_code == 200:
                    events = event.json().get('events', [])
                    if any(item.get('event') == 'delivered' and item.get('email', '').lower() == EMAIL for item in events):
                        results['email_delivery_provider_evidence'] = 'passed'
                        break
                time.sleep(2)
            else:
                results['email_delivery_provider_evidence'] = 'not_yet_confirmed'
        stale_cookies = session.cookies.copy()
        if status['private_reset_urls']:
            reset_url = status['private_reset_urls'][0]
            require(reset_url.startswith(origin + '/reset-password?token='), 'Reset origin mismatch')
            reset_token = reset_url.split('?token=', 1)[1]
            cfg['synthetic_password'] = secrets.token_urlsafe(24)
            payload = {'token': reset_token, 'new_password': cfg['synthetic_password']}
            require(session.post(origin + '/api/auth/reset-password', json=payload, timeout=(5, 15)).status_code == 200, 'HTTPS reset failed')
            require(session.get(origin + '/api/auth/browser/session', timeout=(5, 15)).status_code == 401, 'Reset did not revoke old session')
            require(session.post(origin + '/api/auth/reset-password', json=payload, timeout=(5, 15)).status_code == 400, 'Reset link replay accepted')
            response = session.post(origin + '/api/auth/browser/login', json={'email': EMAIL, 'password': cfg['synthetic_password'], 'remember': True}, headers={'Origin': origin}, timeout=(5, 15))
            require(response.status_code == 200, 'New password login failed')
            metadata = response.json()
            headers = {'Origin': origin, 'x-priceyard-csrf': metadata['csrf_token'], 'x-priceyard-session': metadata['session_id']}
            results['https_reset_single_use_and_session_revocation'] = 'passed'
        require(session.post(origin + '/api/auth/logout', headers=headers, timeout=(5, 15)).status_code == 204, 'Logout failed')
        require(session.get(origin + '/api/auth/browser/session', timeout=(5, 15)).status_code == 401, 'Logged-out session remains active')
        results['https_logout'] = 'passed'
        # Application-only rollback: exact previously reviewed app tree, current
        # dependencies and current security schema; never run its older migration.
        candidate = rollback_source()
        server.terminate()
        server.wait(timeout=8)
        cfg['application_path'] = str(candidate)
        server = subprocess.Popen([sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker'], stdin=subprocess.PIPE,
                                  stdout=server_log, stderr=server_log, env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
        server.stdin.write((json.dumps(cfg) + '\n').encode())
        server.stdin.close()
        ready_deadline = time.monotonic() + 15
        while time.monotonic() < ready_deadline:
            require(server.poll() is None, 'Rollback application stopped')
            try:
                if session.get(f'http://127.0.0.1:{PORT}/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=1).status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(.2)
        else:
            raise RuntimeError('Rollback readiness failed')
        session.cookies = stale_cookies
        require(session.get(origin + '/api/auth/browser/session', timeout=(5, 15)).status_code == 401, 'Rollback restored revoked session')
        response = session.post(origin + '/api/auth/browser/login', json={'email': EMAIL, 'password': cfg['synthetic_password'], 'remember': True}, headers={'Origin': origin}, timeout=(5, 15))
        require(response.status_code == 200, 'Rollback login failed')
        results['security_aware_application_rollback_over_tunnel'] = 'passed_local_runtime_not_Render_artifact'
        results['google_interactive_login'] = 'not_attempted_requires_browser_identity_and_origin'
        results['paystack_checkout_webhook'] = 'not_attempted_requires_test_checkout_and_TEST_webhook_configuration'
        if '--interactive' in sys.argv:
            report.update(status='awaiting_owner_browser', public_origin=origin,
                          owner_TEST_webhook_url=origin + '/api/payments/webhook',
                          manual_window_seconds=600, tunnel_closed=False)
            save()
            os.startfile(origin + '/?ticket=' + quote(cfg['gate']))
            opened_checkout = False
            manual_deadline = time.monotonic() + 600
            while time.monotonic() < manual_deadline:
                if (RUN / 'TEST_WEBHOOK_CONFIRMED.txt').exists() and not opened_checkout and checkout:
                    confirmation = (RUN / 'TEST_WEBHOOK_CONFIRMED.txt').read_text().strip()
                    require(confirmation == origin + '/api/payments/webhook', 'TEST webhook confirmation differs')
                    os.startfile(checkout['authorization_url'])
                    opened_checkout = True
                stats = session.get(f'http://127.0.0.1:{PORT}/__provider_status', headers={'x-provider-controller': cfg['gate']}, timeout=3).json()
                if stats['google_logins']:
                    results['google_interactive_login'] = 'passed_verified_approved_linked_identity_fixture'
                if stats['valid_TEST_webhooks']:
                    results['paystack_checkout_webhook'] = 'passed_signature_and_original_handler'
                save()
                if stats['google_logins'] and stats['valid_TEST_webhooks']:
                    break
                if (RUN / 'STOP_REQUESTED.txt').exists():
                    break
                time.sleep(3)
        report['status'] = 'partial'
        report['public_origin'] = origin
    except Exception as exc:
        report['status'] = 'stopped'
        report['error_type'] = type(exc).__name__
        # Only our literal assertion messages, never provider or credential errors.
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
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        report['tunnel_closed'] = tunnel is None or tunnel.poll() is not None
        report['worker_stopped'] = server is None or server.poll() is not None
        if pg_started:
            with (RUN / 'pg-control.log').open('ab') as pg_output:
                stopped = subprocess.run([str(BIN / 'pg_ctl.exe'), '-D', str(DATA), '-m', 'fast', '-w', '-t', '15', 'stop'],
                                         env=environment, stdout=pg_output, stderr=subprocess.STDOUT, timeout=20)
            report['postgres_stopped'] = stopped.returncode == 0 or not (DATA / 'postmaster.pid').exists()
        else:
            report['postgres_stopped'] = True
        save()
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    if '--worker' in sys.argv:
        try:
            worker()
        except BaseException as error:
            print(json.dumps({'worker_stopped': True, 'error_type': type(error).__name__}), flush=True)
            raise SystemExit(1)
    else:
        main()
