import base64
from urllib.parse import urlsplit
from pydantic import BaseModel, Field, field_validator
from cryptography.hazmat.primitives.asymmetric import ec

PUSH_HOSTS = {"fcm.googleapis.com", "updates.push.services.mozilla.com", "web.push.apple.com", "wns.windows.com"}

def validate_push_endpoint(value: str) -> str:
    if any(char.isspace() or ord(char) < 32 for char in value):
        raise ValueError("Invalid push endpoint characters")
    parts = urlsplit(value)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or parts.username or parts.password or parts.fragment or parts.port not in (None, 443) or not parts.path or parts.path == "/":
        raise ValueError("Only supported secure push endpoints are accepted")
    if host not in PUSH_HOSTS and not host.endswith(".wns.windows.com"):
        raise ValueError("Unsupported push provider")
    return value


class PushSubscriptionKeys(BaseModel):
    p256dh: str = Field(max_length=128)
    auth: str = Field(max_length=64)

    @field_validator("p256dh", "auth")
    @classmethod
    def validate_key(cls, value, info):
        try:
            raw = base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
        except Exception:
            raise ValueError("Invalid push key") from None
        if len(raw) != (65 if info.field_name == "p256dh" else 16):
            raise ValueError("Invalid push key length")
        if info.field_name == "p256dh":
            try:
                ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), raw)
            except ValueError:
                raise ValueError("Invalid P-256 public key") from None
        return value


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(min_length=10, max_length=500)
    keys: PushSubscriptionKeys

    @field_validator("endpoint")
    @classmethod
    def endpoint_supported(cls, value):
        return validate_push_endpoint(value)


class PushUnsubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=10, max_length=500)
