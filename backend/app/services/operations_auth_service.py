"""Authenticate only the repository's scheduled operational workflow via GitHub OIDC."""
import json
import re
import threading
import time

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException, Request
import jwt
import requests

from app.config import get_settings


ISSUER = "https://token.actions.githubusercontent.com"
AUDIENCE = "https://priceyard-api.onrender.com/internal/operations/recover-payments"
JWKS_URL = ISSUER + "/.well-known/jwks"
MAX_JWKS_BYTES = 128 * 1024
MAX_TOKEN_CHARACTERS = 8192
EXPECTED_CLAIMS = {
    "repository": "fidelisnguakaaga20/priceyard",
    "repository_id": "1333398422",
    "repository_owner_id": "220378766",
    "ref": "refs/heads/master",
    "workflow_ref": "fidelisnguakaaga20/priceyard/.github/workflows/priceyard-operations.yml@refs/heads/master",
    "runner_environment": "github-hosted",
}
EXPECTED_SUBJECTS = (
    "repo:fidelisnguakaaga20/priceyard:ref:refs/heads/master",
    "repo:fidelisnguakaaga20@220378766/priceyard@1333398422:ref:refs/heads/master",
)
_KID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
_jwks_lock = threading.Lock()
_jwks_keys: dict[str, RSAPublicKey] = {}
_jwks_expires = 0.0


def _reject(status: int, detail: str) -> None:
    raise HTTPException(status_code=status, detail=detail, headers={"Cache-Control": "private, no-store"})


def _download_keys() -> dict[str, RSAPublicKey]:
    # Never follow a token-provided URL, redirects or proxy environment settings.
    with requests.Session() as client:
        client.trust_env = False
        with client.get(JWKS_URL, timeout=(3, 5), verify=True, allow_redirects=False, stream=True) as response:
            if response.status_code != 200:
                raise ValueError("OIDC keys unavailable")
            declared = response.headers.get("content-length")
            if declared is not None and (not declared.isdigit() or int(declared) > MAX_JWKS_BYTES):
                raise ValueError("Invalid OIDC key response")
            body = bytearray()
            for chunk in response.iter_content(chunk_size=8192):
                if len(body) + len(chunk) > MAX_JWKS_BYTES:
                    raise ValueError("OIDC key response is too large")
                body.extend(chunk)
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list) or not 1 <= len(payload["keys"]) <= 32:
        raise ValueError("Invalid OIDC key set")
    keys = {}
    for value in payload["keys"]:
        if (not isinstance(value, dict) or value.get("kty") != "RSA"
                or value.get("use", "sig") != "sig" or value.get("alg", "RS256") != "RS256"
                or not isinstance(value.get("kid"), str) or not _KID.fullmatch(value["kid"])):
            continue
        if value["kid"] in keys:
            raise ValueError("Duplicate OIDC key")
        key = jwt.PyJWK.from_dict(value, algorithm="RS256").key
        if not isinstance(key, RSAPublicKey) or not 2048 <= key.key_size <= 8192:
            raise ValueError("Invalid OIDC signing key")
        keys[value["kid"]] = key
    if not keys:
        raise ValueError("No suitable OIDC signing keys")
    return keys


def _verification_key(kid: str) -> RSAPublicKey:
    global _jwks_keys, _jwks_expires
    with _jwks_lock:
        now = time.monotonic()
        if now >= _jwks_expires:
            try:
                _jwks_keys = _download_keys()
                _jwks_expires = time.monotonic() + 300
            except Exception:
                _jwks_keys = {}
                _jwks_expires = time.monotonic() + 30
                _reject(503, "Operational authentication is temporarily unavailable")
        if not _jwks_keys:
            _reject(503, "Operational authentication is temporarily unavailable")
        # Unknown kids do not force refreshes: untrusted requests cannot flood GitHub.
        key = _jwks_keys.get(kid)
        if key is None:
            _reject(401, "Operational authentication failed")
        return key


def authorize_operation(request: Request) -> None:
    if not get_settings().ops_recovery_enabled:
        _reject(503, "Operational recovery is not enabled")
    values = request.headers.getlist("authorization")
    scheme, _, token = values[0].partition(" ") if len(values) == 1 else ("", "", "")
    if scheme.lower() != "bearer" or not 1 <= len(token) <= MAX_TOKEN_CHARACTERS:
        _reject(401, "Operational authentication failed")
    try:
        header = jwt.get_unverified_header(token)
        if (header.get("alg") != "RS256" or not isinstance(header.get("kid"), str)
                or not _KID.fullmatch(header["kid"])):
            raise ValueError("Invalid OIDC header")
        key = _verification_key(header["kid"])
        claims = jwt.decode(token, key, algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER,
                            options={"require": ["exp", "iat", "nbf", "jti", "sub", "aud", "iss"], "strict_aud": True})
        if (any(claims.get(name) != expected for name, expected in EXPECTED_CLAIMS.items())
                or claims.get("sub") not in EXPECTED_SUBJECTS
                or any(type(claims[name]) is not int for name in ("exp", "iat", "nbf"))
                or claims.get("event_name") not in {"schedule", "workflow_dispatch"}
                or not isinstance(claims["jti"], str) or not 1 <= len(claims["jti"]) <= 128):
            raise ValueError("Unapproved OIDC workflow")
    except (jwt.PyJWTError, ValueError, TypeError, UnicodeError):
        _reject(401, "Operational authentication failed")
