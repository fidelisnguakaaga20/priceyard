"""Generate a source-only route index without importing app/settings or using a DB."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "backend/app/routes"
INTRO = """# Current application API reference

This replaces the old staged-development notes. The local application already
implements authentication, subscriptions, prices, intelligence, moderation,
payments, exports and Admin operations. This document describes existing code;
it does not approve a new access policy or a production rollout.

For request/response fields and validation, use `/docs` or `/openapi.json` on the
isolated local backend. The browser preview proxies API calls through `/api`;
the paths below are backend paths without that proxy prefix. The synthetic
preview's `/__test__/...` controls are not application endpoints.

## Access and security contracts

- Guest has no account role. Trial and paid access are subscription states,
  separate from stored roles `free_user`, `paid_user`, `reporter`, `admin`.
- `get_current_user` checks bearer or protected-cookie JWT, activation, current account
  security version and revoked token hashes on the server.
- Browser login uses HttpOnly/Secure/SameSite=Lax host-only cookies; the test-only
  HTTP exception is literal127.0.0.1:55446 in APP_ENV=test. Browser writes require
  exact approved Origin and session-bound CSRF. RememberMe controls cookie
  persistence; bearer API clients remain supported. Login routes share quotas.
  Session/CSRF metadata is noncredential; no browser JWT is returned by these routes.
- `require_roles(...)` additionally restricts staff operations to the named roles.
  `require_full_access` checks current trial/paid entitlement; Admin bypasses that
  entitlement check. Reporter authority does not itself grant paid entitlement.
- Public price schemas omit private source identities. Existing approved current
  prices remain public. History, history options, historical comparisons and
  historical detail apply entitlement checks, including conditional handler checks.
  Admin history/source access remains separate from public responses.
- Quality list/detail require full access. Other existing basic intelligence
  visibility is unchanged pending the owner's source/access-policy decisions.
- Subscription reads and watchlists enforce account ownership; Admin powers are
  checked separately. The dependency column alone is not an ownership policy.
- Checkout accepts only existing plans: NGN2,500/30 days and NGN6,000/90 days.
  Activation requires strict signed/provider evidence and an atomic save.
  A webhook uses signature verification rather than a user JWT; it is not an
  unprotected payment activation endpoint. Provider success alone is insufficient.
- CSV download is Admin only, includes every matching approved row, excludes
  private sources and neutralizes spreadsheet formulas. It streams100-record
  fetch batches; there is no arbitrary export count cap.
- Cron/webhook/header checks, rate limits and conditional/ownership checks can
  live inside handlers/services. A dash below means no declared non-DB Depends
  argument, **not** that an operation is public or safe to call without review.

The approved business rules and operational limits are recorded in
[application contracts](APPLICATION_CONTRACTS.md),
[local development](LOCAL_DEVELOPMENT.md) and
[the live progress tracker](../PRICEYARD_PROGRESS.md).

## Route index

Generated from router declarations with `tools/local-test/update_api_reference.py`.
Only source AST is read; no settings, credentials, application imports, database
connection or provider request is involved. Dependency expressions are copied
from declarations for traceability; follow the linked handler for all checks.

| Method | Backend path | Declared access dependencies (excluding get_db) | Handler |
| --- | --- | --- | --- |
"""


def declared_dependencies(function):
    args = function.args
    defaults = list(args.defaults) + [value for value in args.kw_defaults if value is not None]
    result = []
    for value in defaults:
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "Depends" and value.args:
            expression = ast.unparse(value.args[0])
            if expression != "get_db":
                result.append(expression)
    return ", ".join(result) or "—"


def render_reference():
    entries = []
    for source in sorted([*ROUTES.glob("*.py"), ROOT / "backend/app/main.py"]):
        tree = ast.parse(source.read_text(encoding="utf-8-sig"))
        prefixes = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id in {"APIRouter", "FastAPI"}:
                prefix = next((ast.literal_eval(value.value) for value in node.value.keywords if value.arg == "prefix"), "")
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        prefixes[target.id] = prefix
        for function in tree.body:
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in function.decorator_list:
                if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                    continue
                owner = decorator.func.value
                method = decorator.func.attr
                if not isinstance(owner, ast.Name) or owner.id not in prefixes or method not in {"get", "post", "patch", "put", "delete", "head", "options"}:
                    continue
                endpoint = prefixes[owner.id] + ast.literal_eval(decorator.args[0])
                dependencies = declared_dependencies(function).replace("|", "\\|")
                link = f"[{function.name}](../{source.relative_to(ROOT).as_posix()}#L{function.lineno})"
                entries.append((endpoint, method.upper(), dependencies, link))
    assert len(entries) > 80, "Refuse to replace the reference with a partial inventory"
    assert len({(path, method) for path, method, _, _ in entries}) == len(entries), "Duplicate operation declaration"
    lines = [f"| {method} | `{path}` | `{dependencies}` | {link} |" for path, method, dependencies, link in sorted(entries)]
    return INTRO + "\n".join(lines) + "\n", len(entries)


if __name__ == "__main__":
    content, count = render_reference()
    (ROOT / "docs/api-endpoints.md").write_text(content, encoding="utf-8")
    print(f"Documented {count} declared backend operations; source-only, no application imports")
