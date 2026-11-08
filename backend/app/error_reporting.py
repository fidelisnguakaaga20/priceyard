"""Error alerts (owner-approved audit item 10).

When SENTRY_DSN is set on the server, unexpected server errors are reported to
Sentry, which emails the owner. When it is not set, nothing happens at all.

Privacy: no passwords, cookies, login tokens, request bodies, visitor IP
addresses or stack variables are ever sent - only where in the code it broke.
"""

import os
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_SAFE_HEADERS = frozenset({"user-agent", "content-type", "content-length", "accept", "origin", "referer", "host"})


def _hide_emails(value):
    if isinstance(value, str):
        return _EMAIL.sub("[email hidden]", value)
    if isinstance(value, dict):
        return {key: _hide_emails(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_hide_emails(item) for item in value]
    return value


def scrub_event(event: dict, hint: dict | None = None) -> dict:
    # Background notes (log lines, outgoing web addresses) can hold personal details.
    event.pop("breadcrumbs", None)
    request = event.get("request")
    if isinstance(request, dict):
        for key in ("data", "cookies", "query_string", "env"):
            request.pop(key, None)
        headers = request.get("headers")
        if isinstance(headers, dict):
            request["headers"] = {name: value for name, value in headers.items() if name.lower() in _SAFE_HEADERS}
    user = event.get("user")
    if isinstance(user, dict):
        # Keep only the numeric account id; never email, name or IP address.
        event["user"] = {"id": user["id"]} if "id" in user else {}
    return _hide_emails(event)


def init_error_reporting(settings) -> bool:
    dsn = (settings.sentry_dsn or "").strip()
    if not dsn:
        return False
    import sentry_sdk
    from sentry_sdk.integrations.stdlib import StdlibIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.app_env,
        release=os.environ.get("RENDER_GIT_COMMIT") or "unknown",
        send_default_pii=False,
        include_local_variables=False,
        max_request_body_size="never",
        traces_sample_rate=0.0,
        before_send=scrub_event,
        # Do not record outgoing web addresses (payment/email links) or started programs.
        disabled_integrations=[StdlibIntegration()],
    )
    return True
