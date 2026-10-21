"""Small external health/recovery runner; no database or payment credentials.

Only aggregate outcomes and a server-encrypted recovery position leave the API.
All failures have fixed messages: response bodies, URLs and tokens are never logged.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import zipfile


API = "https://priceyard-api.onrender.com"
FRONTEND = "https://priceyard.onrender.com"
RECOVERY = API + "/internal/operations/recover-payments"
REPOSITORY = "fidelisnguakaaga20/priceyard"
WORKFLOW = ".github/workflows/priceyard-operations.yml"
ARTIFACT = "priceyard-payment-checkpoint"
MAX_BODY = 256 * 1024
MAX_CHECKPOINT = 4096
OUTCOMES = {"confirmed", "unconfirmed", "review_required", "error", "missing_record"}


class SafeFailure(Exception):
    """Only fixed, non-sensitive operator messages belong in this exception."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, *, deadline=None, opener=None):
        self.deadline = deadline if deadline is not None else time.monotonic() + 205
        # GitHub/application identity headers must not be relayed through env proxies.
        self.opener = opener or build_opener(ProxyHandler({}), NoRedirect())

    def remaining(self):
        return self.deadline - time.monotonic()

    def request(self, url, *, headers=None, data=None, timeout=20, limit=MAX_BODY,
                allow_redirect=False):
        if self.remaining() <= 0:
            raise SafeFailure("Operational check exceeded its bounded time window.")
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.username or parsed.password
                or parsed.port not in (None, 443) or not parsed.hostname):
            raise SafeFailure("Operational destination validation failed.")
        request = Request(url, data=data, headers=headers or {}, method="POST" if data is not None else "GET")
        try:
            with self.opener.open(request, timeout=min(timeout, self.remaining())) as response:
                body = response.read(limit + 1)
                if response.status != 200 or len(body) > limit:
                    raise SafeFailure("Operational response status or size check failed.")
                return response.status, response.headers, body
        except HTTPError as error:
            if allow_redirect and error.code == 302:
                return error.code, error.headers, b""
            raise SafeFailure("Operational request failed; inspect the service or workflow status.") from None
        except (URLError, TimeoutError, OSError):
            raise SafeFailure("Operational connection failed or timed out.") from None

    def json(self, url, *, headers=None, data=None, timeout=20):
        _, response_headers, body = self.request(url, headers=headers, data=data, timeout=timeout)
        if response_headers.get_content_type() != "application/json":
            raise SafeFailure("Operational JSON content-type check failed.")
        try:
            value = json.loads(body)
        except (ValueError, UnicodeError):
            raise SafeFailure("Operational JSON response is invalid.") from None
        if not isinstance(value, dict):
            raise SafeFailure("Operational JSON response has an invalid shape.")
        return value


def _token(value):
    if value is None:
        return None
    if (not isinstance(value, str) or not 1 <= len(value) <= MAX_CHECKPOINT
            or re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", value) is None):
        raise SafeFailure("Encrypted recovery checkpoint is invalid; no recovery request was sent.")
    return value


def oidc_token(client, environ):
    url = environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    credential = environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith(".actions.githubusercontent.com")
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment or not credential):
        raise SafeFailure("GitHub short-lived identity is unavailable or invalid.")
    query = [(key, value) for key, value in parse_qsl(parsed.query) if key != "audience"]
    query.append(("audience", RECOVERY))
    url = urlunsplit(parsed._replace(query=urlencode(query)))
    value = client.json(url, headers={"Authorization": "Bearer " + credential}, timeout=15)
    token = value.get("value")
    if not isinstance(token, str) or not 64 <= len(token) <= 16384 or token.count(".") != 2:
        raise SafeFailure("GitHub short-lived identity response is invalid.")
    return token


def _github_headers(environ):
    token = environ.get("GITHUB_TOKEN", "")
    if not token or environ.get("GITHUB_REPOSITORY") != REPOSITORY or environ.get("GITHUB_REF") != "refs/heads/master":
        raise SafeFailure("Repository or GitHub checkpoint access is not configured correctly.")
    return {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"}


def load_checkpoint(client, environ):
    headers = _github_headers(environ)
    base = "https://api.github.com/repos/" + REPOSITORY + "/actions/"
    data = client.json(base + "artifacts?" + urlencode({"name": ARTIFACT, "per_page": 10}), headers=headers)
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or type(data.get("total_count")) is not int:
        raise SafeFailure("GitHub checkpoint listing is invalid.")
    candidates = [artifact for artifact in artifacts
                  if isinstance(artifact, dict) and artifact.get("name") == ARTIFACT
                  and not artifact.get("expired")
                  and (artifact.get("workflow_run") or {}).get("head_branch") == "master"]
    if not candidates:
        if data["total_count"] == 0:
            return None  # First run or expired retention: a full new idempotent cycle is safe.
        raise SafeFailure("No usable recovery checkpoint was found; inspect workflow artifacts.")
    artifact = max(candidates, key=lambda value: value.get("id", 0))
    if (type(artifact.get("id")) is not int or type(artifact.get("size_in_bytes")) is not int
            or not 0 < artifact["size_in_bytes"] <= MAX_BODY):
        raise SafeFailure("GitHub checkpoint metadata is invalid.")
    run_id = (artifact.get("workflow_run") or {}).get("id")
    if type(run_id) is not int:
        raise SafeFailure("GitHub checkpoint workflow identity is invalid.")
    run = client.json(base + "runs/" + str(run_id), headers=headers)
    if (run.get("path") != WORKFLOW or run.get("head_branch") != "master"
            or run.get("event") not in ("schedule", "workflow_dispatch")
            or (run.get("head_repository") or {}).get("full_name") != REPOSITORY):
        raise SafeFailure("GitHub checkpoint came from an unexpected workflow.")
    status, download_headers, _ = client.request(base + "artifacts/" + str(artifact["id"]) + "/zip",
                                                headers=headers, allow_redirect=True)
    location = download_headers.get("Location", "")
    parsed = urlsplit(location)
    if (status != 302 or parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith((".blob.core.windows.net", ".actions.githubusercontent.com"))
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise SafeFailure("GitHub checkpoint download destination is invalid.")
    # The signed storage URL receives NO GitHub authorization header.
    _, _, archive = client.request(location)
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            entries = zipped.infolist()
            if (len(entries) != 1 or entries[0].filename != "checkpoint.json"
                    or entries[0].file_size > MAX_CHECKPOINT + 64):
                raise SafeFailure("GitHub checkpoint archive has unexpected contents.")
            checkpoint = json.loads(zipped.read(entries[0]))
    except (zipfile.BadZipFile, ValueError, UnicodeError, RuntimeError):
        raise SafeFailure("GitHub checkpoint archive could not be verified.") from None
    if not isinstance(checkpoint, dict) or set(checkpoint) != {"checkpoint"}:
        raise SafeFailure("GitHub checkpoint file is invalid.")
    return _token(checkpoint["checkpoint"])


def save_checkpoint(path, checkpoint):
    checkpoint = _token(checkpoint)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"checkpoint": checkpoint}), encoding="utf-8")
    temporary.replace(path)


def check_health(client):
    # The first same-origin request also permits a sleeping Free backend to start.
    for origin, timeout in ((FRONTEND + "/api", 65), (API, 20)):
        health = client.json(origin + "/health", timeout=timeout)
        if health != {"status": "healthy"}:
            raise SafeFailure("Application health response did not pass.")
    _, headers, body = client.request(FRONTEND + "/login", timeout=20)
    if headers.get_content_type() != "text/html" or b"priceyard" not in body.lower():
        raise SafeFailure("Application login page did not pass.")


def recover(client, environ, checkpoint, state_path):
    identity = oidc_token(client, environ)
    for _ in range(2):
        if client.remaining() < 75:
            if not Path(state_path).exists():
                raise SafeFailure("Insufficient time remains for a safe recovery request.")
            break
        report = client.json(RECOVERY, headers={"Authorization": "Bearer " + identity,
                                               "Content-Type": "application/json"},
                             data=json.dumps({"checkpoint": checkpoint}).encode("utf-8"), timeout=70)
        if (set(report) != {"busy", "complete", "processed", "outcomes", "checkpoint"}
                or type(report["busy"]) is not bool or type(report["complete"]) is not bool
                or type(report["processed"]) is not int or not 0 <= report["processed"] <= 25
                or not isinstance(report["outcomes"], dict) or set(report["outcomes"]) != OUTCOMES
                or any(type(count) is not int or count < 0 for count in report["outcomes"].values())
                or sum(report["outcomes"].values()) != report["processed"]):
            raise SafeFailure("Recovery aggregate response is invalid; the previous checkpoint is retained.")
        next_checkpoint = _token(report["checkpoint"])
        if (report["busy"] and report["complete"]
                or report["complete"] and next_checkpoint is not None
                or not report["busy"] and not report["complete"] and next_checkpoint is None
                or report["busy"] and (next_checkpoint != checkpoint or report["processed"] != 0)):
            raise SafeFailure("Recovery checkpoint transition is invalid.")
        save_checkpoint(state_path, next_checkpoint)
        checkpoint = next_checkpoint
        if report["busy"]:
            raise SafeFailure("Another recovery worker is active; the next scheduled run will retry.")
        if any(report["outcomes"][key] for key in ("error", "missing_record", "review_required")):
            raise SafeFailure("Payment recovery requires operator attention; progress was preserved.")
        if report["complete"]:
            break


def main(environ=None, client=None):
    environ = os.environ if environ is None else environ
    mode = environ.get("OPS_MODE", "health-only")
    try:
        if mode == "simulate-failure":
            raise SafeFailure("Controlled alert test: application and payment services were not contacted.")
        if mode not in ("recover", "health-only"):
            raise SafeFailure("Unknown operational mode; no request was sent.")
        client = client or Client()
        if mode == "recover":
            checkpoint = load_checkpoint(client, environ)
        health_failure = None
        try:
            check_health(client)
        except SafeFailure as error:
            if mode == "health-only":
                raise
            health_failure = error
        if mode == "recover":
            state_path = environ.get("OPS_STATE_PATH", "")
            if not state_path:
                raise SafeFailure("Encrypted checkpoint storage is not configured.")
            recover(client, environ, checkpoint, state_path)
        if health_failure is not None:
            # A frontend outage must alert without suppressing backend recovery.
            raise health_failure
        print("PASS: bounded application checks" + (" and payment recovery." if mode == "recover" else "."))
        return 0
    except SafeFailure as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    except Exception:
        print("FAIL: unexpected operational error; private details were suppressed.", file=sys.stderr)
        return 1
    finally:
        # Step outputs survive a failing exit so the next step can preserve progress.
        # Write a constant flag only; the opaque checkpoint is never an Actions output.
        path, output = environ.get("OPS_STATE_PATH"), environ.get("GITHUB_OUTPUT")
        if mode == "recover" and path and output and Path(path).is_file():
            with open(output, "a", encoding="utf-8") as stream:
                stream.write("checkpoint-written=true\n")


if __name__ == "__main__":
    sys.exit(main())
