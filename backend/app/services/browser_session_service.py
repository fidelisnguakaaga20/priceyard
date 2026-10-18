"""Browser-only cookie transport; existing bearer API credentials stay supported."""
from datetime import datetime, timezone
import hashlib
import hmac
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, Response

from app.config import get_settings
from app.security import decode_access_claims

SECURE_COOKIE = '__Host-priceyard_session'
LOCAL_COOKIE = 'priceyard_local_session'


def allowed_browser_origins() -> set[str]:
    settings = get_settings()
    values = [settings.frontend_url, *settings.cors_origins.split(',')]
    return {value.strip().rstrip('/') for value in values
            if value.strip() and value.strip() != '*' and urlsplit(value.strip()).scheme in {'http', 'https'}}


def require_browser_origin(request: Request) -> None:
    if request.headers.get('origin') not in allowed_browser_origins():
        raise HTTPException(status_code=403, detail='Browser request origin is not allowed')


def local_test_cookie(request: Request) -> bool:
    # This exception is deliberately limited to the already isolated preview.
    return (get_settings().app_env == 'test' and request.url.hostname == '127.0.0.1'
            and request.url.port == 55446)


def cookie_name(request: Request) -> str:
    return LOCAL_COOKIE if local_test_cookie(request) else SECURE_COOKIE


def browser_token(request: Request) -> str | None:
    return request.cookies.get(cookie_name(request))


def session_metadata(token: str) -> dict[str, str]:
    secret = get_settings().jwt_secret
    return {'session_id': hashlib.sha256(token.encode()).hexdigest(),
            'csrf_token': hmac.new(secret.encode(), b'priceyard-browser-csrf\0' + token.encode(), hashlib.sha256).hexdigest()}


def validate_browser_request(request: Request, token: str) -> None:
    # Authentication validates the JWT next. CSRF remains usable for idempotent
    # logout so an expired credential can still be removed from this browser.
    metadata = session_metadata(token)
    expected = request.headers.get('x-priceyard-session')
    if expected and not hmac.compare_digest(expected.encode(), metadata['session_id'].encode()):
        raise HTTPException(status_code=401, detail='Browser session changed')
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        require_browser_origin(request)
        if not hmac.compare_digest(request.headers.get('x-priceyard-csrf', '').encode(), metadata['csrf_token'].encode()):
            raise HTTPException(status_code=403, detail='Browser request verification failed')


def set_browser_session(response: Response, request: Request, token: str, *, remember: bool) -> dict[str, str]:
    claims = decode_access_claims(token)
    remaining = max(0, int(claims['exp'] - datetime.now(timezone.utc).timestamp()))
    response.set_cookie(cookie_name(request), token, httponly=True, secure=not local_test_cookie(request),
                        samesite='lax', path='/', max_age=remaining if remember else None)
    response.headers['Cache-Control'] = 'private, no-store'
    return session_metadata(token)


def clear_browser_session(response: Response, request: Request) -> None:
    response.delete_cookie(cookie_name(request), path='/', secure=not local_test_cookie(request), httponly=True, samesite='lax')
    response.headers['Cache-Control'] = 'private, no-store'


class BrowserSessionCacheMiddleware:
    def __init__(self, app): self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        request = Request(scope)
        route_path = request.url.path.removeprefix(scope.get('root_path', ''))
        private = bool(request.headers.get('authorization') or browser_token(request)
                       or route_path.startswith('/auth/'))

        async def guarded_send(message):
            if private and message['type'] == 'http.response.start':
                message = {**message, 'headers': [(k, v) for k, v in message['headers'] if k.lower() != b'cache-control']
                           + [(b'cache-control', b'private, no-store')]}
            await send(message)
        await self.app(scope, receive, guarded_send)
