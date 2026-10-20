# PY-35 final launch result — 2026-10-20 WAT

**Local routing: PASS. Release: NOT READY — required hosted checks are NOT RUN,
not observed failures. 35/36 complete; PY-35 stays partial.**

| Check | Result |
| --- | --- |
| Production TypeScript/Vite build | PASS; existing snapshot/tools, no install |
| Reject incompatible production API configuration | PASS; seven actual Vite configuration cases |
| Original API behind proposed same-origin route | PASS; two guarded tests, including raw POST/query, status, multiple cookies, fixed destination, React fallback, CSRF, cache headers, logout and revoked-token rejection |
| Original React browser workflow against original API | PASS; virtual HTTPS only, synthetic memory database, real login/dashboard/reload/API/CSRF/logout; all page traffic fulfilled locally or blocked |
| Application rollback compatibility | PASS retained; current backend/app tree equals the already-tested security-aware rollback tree fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed; no repeat restoration or migration |
| Actual Render forwarding and candidate runtime/rollback artifact | NOT RUN; requires an explicitly approved hosted change |

No backend application, UI component/style, database schema, measurement,
subscription rule or provider setting changed. Google, Paystack TEST/webhook/replay,
received email, encrypted backup/restoration and migration rehearsal passes remain
valid and were not repeated. Initial uncommitted test-harness import/lifespan bugs
were corrected. A sandbox build-resolution error was resolved using the normal
approval mechanism; isolation guards stayed enabled.

## Exact proposed launch settings

On existing frontend **priceyard**:

1. Change build environment `VITE_API_URL` from the backend URL to `/api`.
2. Add the first Rewrite: `/api/*` → `https://priceyard-api.onrender.com/*`.
3. Keep the existing second Rewrite **`/*` → `/index.html`** unchanged.

The production build now refuses a separate-site API URL, so step1 must precede
the approved frontend build. Settings are recorded in
[RENDER_LAUNCH_SETTINGS.json](RENDER_LAUNCH_SETTINGS.json); they have **not** been
applied. Backend start command, direct API/webhook routes and host-only Secure,
HttpOnly, SameSite=Lax cookies stay unchanged. Existing frontend origin must remain
in FRONTEND_URL/allowed origins; do not expose or overwrite other secrets.

Render documents full-URL rewrite destinations, but does not guarantee authenticated
POST/body/cookie/private-cache forwarding. The local tests establish application
compatibility, **not Render edge certification**. Under a separately approved hosted
window, verify raw POST/query forwarding, Set-Cookie and Cookie, login/session,
CSRF403, logout204/revocation401, private/no-store without cross-user leakage,
JSON API404, and React deep links. Stop if any fails; do not weaken cookies.
[Render rewrite documentation](https://render.com/docs/redirects-rewrites).

## Remaining release boundary

- Both services auto-deploy master and the backend build runs Alembic. No master
  push or saved production settings until the exact controlled release is approved.
- Preserve the already-reviewed additive0022 migration, grants and revocation
  evidence. At approved cutover, confirm target revision/owner and reconcile writes
  since the existing backup. Do not repeat the backup/rehearsal automatically.
- Verify the exact hosted build and retained security-aware application artifact.
  Application rollback must retain0022/security evidence and restore routing/build
  configuration together. The currently live pre-security artifact is not an
  approved fallback; do not downgrade or restore over later payments.
- Confirm the owner/operator for existing payment recovery and alert response;
  do not add a paid scheduler/service or generate another TEST charge.

With only the two production services and no permission to change them, actual
edge/candidate/rollback tests cannot be completed. The next required approval is
a **scoped hosted routing/runtime verification window**, not an unconditional
production launch. No new service, purchase, push, merge, production migration or
deployment was performed.
