from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import get_settings

try:
    limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"],
                      storage_uri=get_settings().rate_limit_storage_uri)
except Exception:
    raise RuntimeError("Rate-limit storage is unavailable or invalid; review private server configuration") from None
