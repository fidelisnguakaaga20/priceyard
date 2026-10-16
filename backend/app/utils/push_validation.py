import base64
import binascii
import re
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.asymmetric import ec
import requests

# Browser push services documented by Chromium/Google, Mozilla, Apple and WNS.
# Endpoint paths remain opaque: never rewrite a browser's capability URL.
PUSH_HOSTS = frozenset({"fcm.googleapis.com", "updates.push.services.mozilla.com", "push.services.mozilla.com", "web.push.apple.com"})
WNS_HOST = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+notify\.windows\.com\Z")


def validate_push_endpoint(value: str) -> str:
    if (not isinstance(value, str) or not 1 <= len(value) <= 500
            or any(ord(char) <= 32 or ord(char) >= 127 for char in value)
            or "\\" in value or "#" in value):
        raise ValueError("Invalid push destination")
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or parsed.username is not None or parsed.password is not None
                or parsed.port not in {None, 443} or not parsed.hostname
                or (parsed.hostname not in PUSH_HOSTS and not WNS_HOST.fullmatch(parsed.hostname))
                or not parsed.path or (parsed.path == "/" and not parsed.query)):
            raise ValueError("Invalid push destination")
    except ValueError as error:
        raise ValueError("Invalid push destination") from error
    return value


def validate_push_key(value: str, *, public: bool) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", value):
        raise ValueError("Invalid push encryption key")
    try:
        decoded = base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
        if public:
            if len(decoded) != 65 or decoded[0] != 4:
                raise ValueError("Invalid public key")
            ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), decoded)
        elif len(decoded) != 16:
            raise ValueError("Invalid authentication secret")
    except (ValueError, binascii.Error) as error:
        raise ValueError("Invalid push encryption key") from error
    return value


class SafePushSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.trust_env = False  # No implicit proxies or netrc credentials.

    def request(self, method, url, *args, **kwargs):
        validate_push_endpoint(url)
        if method.upper() != "POST":
            raise ValueError("Only push delivery requests are permitted")
        kwargs.update(allow_redirects=False, timeout=(3, 7), verify=True, proxies={})
        response = super().request(method, url, *args, **kwargs)
        if response.is_redirect or response.is_permanent_redirect:
            raise requests.RequestException("Push service redirect refused")
        return response
