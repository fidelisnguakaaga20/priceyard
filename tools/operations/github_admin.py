"""Bounded Actions administration using the existing Git Credential Manager login.

Credentials remain in memory, never in command arguments, files or output.
This helper cannot edit production services or retrieve database credentials.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPOSITORY = "fidelisnguakaaga20/priceyard"
WORKFLOW = "priceyard-operations.yml"
API = "https://api.github.com"


class SafeError(Exception):
    pass


class HTTPFailure(SafeError):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"GitHub returned HTTP {code}; private response omitted")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SafeError("Unexpected GitHub redirect; stopped")


def credential() -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    result = subprocess.run(
        [r"C:\Program Files\Git\cmd\git.exe", "credential", "fill"],
        input=f"protocol=https\nhost=github.com\npath={REPOSITORY}.git\n\n",
        text=True, capture_output=True, timeout=30, env=env,
    )
    if result.returncode:
        raise SafeError("Existing GitHub login is unavailable; no credential was displayed")
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if fields.get("host") != "github.com" or not fields.get("password"):
        raise SafeError("GitHub credential identity could not be checked")
    return fields["password"]


def request(token: str, path: str, *, payload=None, method=None):
    if not path.startswith(f"/repos/{REPOSITORY}/") and path not in (f"/repos/{REPOSITORY}", "/user"):
        raise SafeError("Request outside the approved repository")
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PriceYard-Operations-Setup",
        **({"Content-Type": "application/json"} if data is not None else {}),
    })
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=25) as response:
            raw = response.read(1_048_577)
            if len(raw) > 1_048_576:
                raise SafeError("GitHub response exceeded the safety bound")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raise HTTPFailure(error.code) from None
    except (urllib.error.URLError, TimeoutError):
        raise SafeError("GitHub could not be reached; private diagnostics omitted") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "runs", "jobs", "enable-schedule", "disable-schedule",
                                         "dispatch-health", "dispatch-alert-test", "dispatch-recovery"))
    parser.add_argument("--run-id", type=int)
    args = parser.parse_args()
    token = credential()
    identity = request(token, "/user")
    if str(identity.get("id")) != "220378766" or identity.get("login") != "fidelisnguakaaga20":
        raise SafeError("GitHub account does not match the approved owner")
    repo_path = f"/repos/{REPOSITORY}"
    if args.action == "status":
        repo = request(token, repo_path)
        permissions = request(token, repo_path + "/actions/permissions")
        print(json.dumps({"owner_verified": True, "repository": REPOSITORY,
                          "visibility": repo.get("visibility"), "default_branch": repo.get("default_branch"),
                          "actions_enabled": permissions.get("enabled"),
                          "allowed_actions": permissions.get("allowed_actions")}))
    elif args.action == "runs":
        result = request(token, repo_path + f"/actions/workflows/{WORKFLOW}/runs?per_page=5")
        print(json.dumps({"runs": [{key: row.get(key) for key in (
            "id", "event", "status", "conclusion", "head_sha", "html_url", "created_at",
        )} for row in result.get("workflow_runs", [])]}))
    elif args.action == "jobs":
        if args.run_id is None or args.run_id <= 0:
            raise SafeError("A valid workflow run ID is required")
        result = request(token, repo_path + f"/actions/runs/{args.run_id}/jobs?per_page=10")
        print(json.dumps({"jobs": [{"id": job.get("id"), "name": job.get("name"),
                                   "status": job.get("status"), "conclusion": job.get("conclusion"),
                                   "steps": [{"name": step.get("name"), "conclusion": step.get("conclusion")}
                                             for step in job.get("steps", [])]}
                                  for job in result.get("jobs", [])]}))
    elif args.action in ("enable-schedule", "disable-schedule"):
        name = "PRICEYARD_OPERATIONS_ENABLED"
        path = repo_path + "/actions/variables/" + name
        try:
            request(token, path)
            exists = True
        except HTTPFailure as error:
            if error.code != 404:
                raise
            exists = False
        value = "true" if args.action == "enable-schedule" else "false"
        request(token, path if exists else repo_path + "/actions/variables",
                payload={"name": name, "value": value}, method="PATCH" if exists else "POST")
        verified = request(token, path)
        if verified.get("value") != value:
            raise SafeError("Scheduled operations activation could not be verified")
        print(json.dumps({"schedule_enabled": value == "true", "repository": REPOSITORY}))
    else:
        inputs = {"mode": {"dispatch-health": "health-only", "dispatch-alert-test": "simulate-failure",
                            "dispatch-recovery": "recover"}[args.action]}
        request(token, repo_path + f"/actions/workflows/{WORKFLOW}/dispatches",
                payload={"ref": "master", "inputs": inputs})
        print(json.dumps({"dispatched": True, "mode": inputs["mode"], "branch": "master"}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SafeError as error:
        print("STOPPED: " + str(error), file=sys.stderr)
        sys.exit(1)
    except (subprocess.SubprocessError, ValueError):
        # Never print response bodies, credential-helper stderr or network errors.
        print("STOPPED: bounded GitHub operation failed; credentials were not displayed", file=sys.stderr)
        sys.exit(1)
