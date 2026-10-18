"""One bounded loopback TLS rehearsal; no production key or trust-store access."""
import asyncio
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import ssl
import sys

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
# Trusted bootstrap creates and loads ONLY its own new synthetic key before the
# existing guard. The guard is unchanged and precedes every application import.
preserved = {name: os.environ[name] for name in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH') if name in os.environ}
os.environ.clear(); os.environ.update(preserved)
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

fixture = LAB / 'runtime/local-tls-20261018'
fixture.mkdir(exist_ok=False)  # Preserve completed/interrupted evidence; no overwrite.
private = ec.generate_private_key(ec.SECP256R1())
subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'PriceYard synthetic loopback only')])
now = datetime.now(timezone.utc)
certificate = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
    .public_key(private.public_key()).serial_number(x509.random_serial_number())
    .not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(hours=1))
    .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]), critical=False)
    .sign(private, hashes.SHA256()))
cert_bytes = certificate.public_bytes(serialization.Encoding.PEM)
with (fixture / 'synthetic-cert.pem').open('xb') as output: output.write(cert_bytes)
with (fixture / 'synthetic-key.pem').open('xb') as output:
    output.write(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_context.minimum_version = ssl.TLSVersion.TLSv1_2
server_context.load_cert_chain(fixture / 'synthetic-cert.pem', fixture / 'synthetic-key.pem')
pin = base64.b64encode(hashlib.sha256(private.public_key().public_bytes(
    serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).digest()).decode('ascii')


def memory_handshake(hostname, trust):
    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if trust: client_context.load_verify_locations(cadata=cert_bytes.decode('ascii'))
    incoming, outgoing, peer_in, peer_out = (ssl.MemoryBIO() for _ in range(4))
    client = client_context.wrap_bio(incoming, outgoing, server_hostname=hostname)
    server = server_context.wrap_bio(peer_in, peer_out, server_side=True)
    client_done = server_done = False
    for _ in range(12):
        if not client_done:
            try: client.do_handshake(); client_done = True
            except ssl.SSLWantReadError: pass
        if outgoing.pending: peer_in.write(outgoing.read())
        if not server_done:
            try: server.do_handshake(); server_done = True
            except ssl.SSLWantReadError: pass
        if peer_out.pending: incoming.write(peer_out.read())
        if client_done and server_done: return client.version()
    raise RuntimeError('Bounded memory TLS handshake did not finish')


protocol = memory_handshake('127.0.0.1', True)
for hostname, trust in (('wrong.example.invalid', True), ('127.0.0.1', False)):
    try: memory_handshake(hostname, trust)
    except ssl.SSLCertVerificationError: pass
    else: raise RuntimeError('TLS certificate negative verification did not fail')
(LAB / 'evidence/batch-86-tls-handshake.json').write_text(json.dumps({
    'checks': 3, 'failures': 0, 'trusted_matching_name_passed': True,
    'wrong_name_rejected': True, 'untrusted_certificate_rejected': True,
    'tls_protocol': protocol, 'network_used_for_memory_checks': False,
    'system_trust_store_changed': False, 'production_keys_read': False}, indent=2), encoding='utf-8')

import preview  # Applies unchanged guard, synthetic SQLite and credential scrubbing.
from app.config import get_settings
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
import uvicorn

origin = 'https://127.0.0.1:55446'
settings = get_settings()
settings.app_env = 'staging'; settings.frontend_url = origin; settings.cors_origins = origin
for middleware in preview.api.user_middleware:
    if middleware.cls.__name__ == 'CORSMiddleware': middleware.kwargs['allow_origins'] = [origin]


async def status(request):
    return JSONResponse({'synthetic_only': True, 'providers': 'disabled', 'tls_fixture': True})


class LiteralTLSOnly:
    def __init__(self, app): self.app = app; self.lock = asyncio.Lock()
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket': return await send({'type': 'websocket.close', 'code': 1008})
        if scope['type'] == 'http':
            headers = dict(scope.get('headers', []))
            if (scope.get('scheme') != 'https' or headers.get(b'host') != b'127.0.0.1:55446'
                    or headers.get(b'origin', origin.encode()) != origin.encode()):
                return await JSONResponse({'detail': 'Synthetic literal TLS only'}, status_code=403)(scope, receive, send)
            async with self.lock: return await self.app(scope, receive, send)
        await self.app(scope, receive, send)


app = LiteralTLSOnly(Starlette(routes=[Route('/__test__/tls', status), Mount('/api', app=preview.api),
    Mount('/', app=preview.PreviewFiles(directory=str(preview.snapshot / 'dist')))]))
(fixture / 'public-identity.json').write_text(json.dumps({'purpose': 'synthetic-loopback-only-no-system-trust-change',
    'origin': origin, 'spki_sha256': pin, 'providers': 'disabled'}), encoding='utf-8')
config = uvicorn.Config(app, host='127.0.0.1', port=55446, access_log=False, log_level='warning',
                        ssl_context_factory=lambda config, default: server_context)
uvicorn.Server(config).run()
