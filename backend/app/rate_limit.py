import ipaddress

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def client_address(request: Request) -> str:
    """The visitor's address for attempt limits.

    On Render every request passes through Cloudflare, which sets CF-Connecting-IP to the
    real visitor address and refuses requests that try to supply that header themselves.
    X-Forwarded-For (and therefore request.client.host) can be faked by the visitor, so it
    is only used when CF-Connecting-IP is absent (local development and tests).
    """
    candidate = request.headers.get("cf-connecting-ip", "").strip()
    if candidate:
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=client_address)
