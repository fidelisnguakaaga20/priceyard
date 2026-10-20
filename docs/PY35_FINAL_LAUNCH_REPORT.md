# PY-35 final launch result — 2026-10-20 WAT

Current141 supersedes the initial redirect observation: corrected Rewrite reaches
the synthetic API through Render (GET identity200, POST method/status207). The
browser stopped before login on an overly strict raw query-encoding assertion:
'+' versus '%20' for the same decoded space. Failed evidence is preserved. The
test now compares exact decoded values, duplicate values/order/count and a literal
plus, keeping body bytes/cookies/cache/CSRF/logout strict. Resume only this
unfinished batch; no prior provider/backup/migration tests repeated or production
changes. Full hosted session result remains pending.

Current139 hosted observation: owner saved the temporary route. Both a plain
and cache-busted GET to its /api/health return301 to the exact current tunnel;
the tunnel and loopback health themselves return200 with matching synthetic
identity. Login/browser tests stopped before sending credentials. The owner is
checking whether the test-only row Action is Redirect or Rewrite; platform
support is not judged until that is known. Current saved transport fails the
same-origin requirement. Production remains unchanged; no deployment approval.

**Local routing: PASS. Release: NOT READY — actual Render GET/POST reaches the
synthetic API; hosted session checks are pending the corrected test.35/36 complete.**

| Check | Result |
| --- | --- |
| Production TypeScript/Vite build | PASS; existing snapshot/tools, no install |
| Reject incompatible production API configuration | PASS; seven actual Vite configuration cases |
| Original API behind proposed same-origin route | PASS; two guarded tests, including raw POST/query, status, multiple cookies, fixed destination, React fallback, CSRF, cache headers, logout and revoked-token rejection |
| Original React browser workflow against original API | PASS; virtual HTTPS only, synthetic memory database, real login/dashboard/reload/API/CSRF/logout; all page traffic fulfilled locally or blocked |
| Application rollback compatibility | PASS retained; current backend/app tree equals the already-tested security-aware rollback tree fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed; no repeat restoration or migration |
| Temporary Render forwarding | Corrected Rewrite GET200/POST207; query-format harness corrected, full session result pending |
| Candidate runtime/rollback artifact | NOT RUN; production remains unchanged |

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
