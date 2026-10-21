# PY-35 controlled release — 2026-10-21 WAT

Current151: **PASS — approved controlled release is LIVE / GO.** Owner confirmed
actual permanent-site Google login, dashboard refresh retaining login, logout and
refresh remaining signed out. Both services are live at approved64a3290; production
0022 was applied once. Real routing/security/cache/static checks passed. No observed
failure required rollback; Auto-Deploy remains Off and routine builds run no migration.

All planned application changes are deployed. Original tracker:35 fully complete,
PY-35 broader operations partial. Automatic payment-recovery scheduling, alert
delivery/on-call/broader load/browser checks, continuing backup targets/coverage
and exceptional historical-payment review are not certified. These are disclosed
operational follow-ups, not newly invented blockers to the approved launch. No
more staging, duplicate tests, migrations or production edits are required now.

Retain secure backend `dep-dbc17ocs728c73dkqn9g`, frontend
`dep-dbc19kvavr4c73egctug`, exact release source, verified encrypted recovery copy
and original code backup. Local security-aware rollback passed; an actual Render
rollback was not triggered. Recovery preserves0022 and all live business/security
records, and must not select the old pre-security backend or restore over newer
payments. `PY35_ACTUAL_RELEASE_GATES.json` preserves individual gate limitations.

## Previous deployment checkpoints

Current150: **Both approved production deployments are LIVE** at
`64a32909d0185d9487d45aa26b47466492a92557`. Owner applied reviewed0022 once and
confirmed `0022_login_revocation`. Auto-Deploy is Off; routine builds no longer
run migrations. Original master backup and verified encrypted DB recovery remain.

- Backend artifact: `dep-dbc17ocs728c73dkqn9g`; frontend: `dep-dbc19kvavr4c73egctug`.
- Real Render API GET/POST routing, private/no-store, guest/invalid-cookie401,
  missing-CSRF403 and API404 JSON checks passed.
- Production login HTML, original React dashboard fallback and built JS passed.
- Existing Google/provider TEST/email/PG17/recovery passes retained, not repeated.
- **Final owner Google login → dashboard refresh → logout → guest refresh is
  pending.** Do not claim authenticated hosted sessions passed before that result.

No observed failure required rollback. The security-aware backend artifact is
live/retained and local PG17 rollback passed; an actual Render rollback was not
triggered. Recovery must preserve0022, grants and live payments/revocations; the
old pre-security backend is not a safe fallback.

35 recommendations are fully complete; PY-35 approved launch acceptance is pending.
Broader operational follow-ups (automatic recovery scheduling, alert delivery/
response ownership, ongoing backup coverage/targets and exceptional historical
payments) remain explicitly unverified. Do not label all nine original gates
Passed or restart staging/audits. Current state: `PY35_ACTUAL_RELEASE_GATES.json`.

## Previous prerelease evidence retained for history

Current143: **FAIL — blocked prerequisites, no new hosted test run.** Owner's
conditional Free API approval requires an isolated test database before creation
and stopping the service within two hours. Read-only Render listing confirms only
the excluded SettleTrack database. Private local PostgreSQL stays private; memory
SQLite loses revocations across restart/rollback and cannot certify that safety.
No suitable permitted hosted database is confirmed. The connected Render tools
also cannot suspend/delete a service; no authenticated alternative stop path is
verified. Created nothing and stopped as instructed. **35/36; NOT READY for
deployment approval.** Existing test passes and previous POST502 evidence remain.

Current142 final hosted result: **FAIL**. Render GET reaches the synthetic API;
the latest POST returns502 before the counted handler. Login/cookie/CSRF/logout
were not attempted. Controller cleanup happened after failure/count collection;
all helpers closed. Worker/tunnel logs do not identify the exact cause; earlier
POST207 prevents concluding that Render cannot forward POST. No application
defect is established. Failed evidence is retained; no automatic retries or new
services were started. Production remains untouched.

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

**Local routing: PASS. Latest hosted verification: FAIL (POST502). Release:
NOT READY. Hosted sessions are unverified;35/36 complete.**

| Check | Result |
| --- | --- |
| Production TypeScript/Vite build | PASS; existing snapshot/tools, no install |
| Reject incompatible production API configuration | PASS; seven actual Vite configuration cases |
| Original API behind proposed same-origin route | PASS; two guarded tests, including raw POST/query, status, multiple cookies, fixed destination, React fallback, CSRF, cache headers, logout and revoked-token rejection |
| Original React browser workflow against original API | PASS; virtual HTTPS only, synthetic memory database, real login/dashboard/reload/API/CSRF/logout; all page traffic fulfilled locally or blocked |
| Application rollback compatibility | PASS retained; current backend/app tree equals the already-tested security-aware rollback tree fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed; no repeat restoration or migration |
| Temporary Render forwarding | Latest GET200/POST502; earlier POST207 retained; exact failure cause unknown |
| Hosted login/cookie/CSRF/logout | NOT RUN; fail-closed before login |
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

## Conditional hosted option — blocked before creation

Owner conditionally approved one temporary **Free Render API**, reusing the
existing static test site. No API has been created. The earlier in-memory proposal
can check forwarding but cannot verify revocation persistence across hosted
rollback. Confirm a separate permitted synthetic database and an actual service
suspension arrangement before creation; do not substitute SettleTrack, production,
an exposed local database, idle sleep or a resetting memory fixture.
Render permits only one Free Postgres per workspace and Free service local files
are lost across restart/redeploy ([official limits](https://render.com/docs/free)).
Render has a [suspend API](https://api-docs.render.com/reference/suspend-service-1),
but this connected toolset does not expose it. No API keys were requested or read.
This is a prerequisite block, not an established application defect. No service,
expense, branch push, production setting, migration or deployment was performed.
