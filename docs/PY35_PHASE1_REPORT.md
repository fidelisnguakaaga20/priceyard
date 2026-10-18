# PY-35 Phase 1 results — 2026-10-18

**35/36 complete; PY-35 partial.** Phase 1 permits safe staging and provider TEST
verification, not production. No staging URL, provider TEST credentials, test
identities or approved recipients were supplied. "Do best option for the app"
did not supply these prerequisites or authorize production as a substitute.
No external settings, accounts, paid services, live jobs or messages were changed.
Follow the [owner staging setup guide](STAGING_SETUP_GUIDE.md) for the exact
prerequisites and simple steps. Batch85 fixes notification destinations locally;
batch84 package/test results below remain historical evidence for its source
revision. The preserved package must be reviewed/refreshed before testing a newer
hosted candidate; do not overwrite it or claim it contains this later fix.

## Prepared and verified

- Separate ignored package:`tools/local-test/runtime/staging-phase1-20261018`.
 125 verified files/740043 bytes; cap300 files/5MiB. Contains backend source and
 verified compiled frontend, no dotenv/provider configuration/customer data or
 copied dependency tree. **Not hosted staging**; no migration or deployment.
- Tests actually imported that separate backend under transport/secret guards:
 sessions1, recovery7, reset2, notifications5: **15 passed**, zero failures/errors/
 skips. Each group used fresh synthetic SQLite. Secure-cookie/CSRF/CORS tests
 are in-process, **not an HTTPS handshake**. Six isolation probes also passed.
- Three finite scheduler ticks with checkpoint save/reload and no duplicate
 credit passed. No OS scheduler installed. Two focused native PostgreSQL recovery/
 worker/webhook cases passed1.435s,19->21/80 retained schemas; cluster stopped.
- Batch83 actual synthetic dump/restore reverified read-only:21 tables/14 fabricated
 records, matching archive/data/structure evidence. No repeated restore, new
 archive, cleanup or actual customer-backup access; production recovery time unknown.
- Browser:original14-card totals, mobile375px, HttpOnly login/no JavaScript bearer,
 reset/logout, synthetic payment recovery and independent mocked notifications
 pass. Price503 with healthy process200 and existing Apply recovery pass.
- 24 serial read samples, concurrency1,180ms total. Observed max/p95 per eight
 samples:health13.1ms, prices8.8ms, Admin summary10.4ms. Tiny-fixture timings are
 not hosted capacity/SLO evidence. Loopback `isSecureContext` does not prove TLS.
- Offline consistency:60 Python packages/74 active requirements including requested
 extras, no conflicts;
123 frontend resolved entries have official sources/integrity.89 source hashes
 match prior build. Local exact constraints retained as a Windows reference, not
 a portable lock. No installs or new online advisory/host certification claimed.

## Nine operational gates

These statuses describe **Phase 1 only**. Blocked means missing prerequisites;
the external checks were not attempted. Failed means an executed check produced
the wrong result. No executed check remains failing after the documented test
corrections and batch85 fix. Passed applies only to the stated synthetic sub-scope. All original live
gates in `RELEASE_GATES.json` remain unrun; release is unauthorized.

| Gate | Phase 1 status | Remaining evidence / risk |
| --- | --- | --- |
| Hosting/cookies/browsers | Blocked; not attempted | No staging HTTPS/domain. Hosted cookies/proxy/CORS, Android/browser/Web Locks, session conversion and Google return unverified; hosted login could fail |
| Backup/restoration | Passed, synthetic only | Real backup retrieval/provider objects, encrypted off-host copy, retention and recovery objectives require customer-data/production approval |
| Production schema/rollout | Awaiting Production Approval | Actual revision/preflight and reviewed migration/rollback untouched; incompatible schema could prevent safe release |
| Paystack TEST | Blocked; not attempted | No TEST credentials/setup; no Paystack request/charge. Provider checkout, callbacks, failures/abandonment, value preservation and review holds unverified |
| Recovery scheduling | Passed, finite rehearsal only | Checkpoint ticks/native single-worker/replay pass. Hosted durable scheduling/alerts still need staging infrastructure; no actual job enabled |
| Google/email/notifications | Blocked; not attempted | Missing identities/credentials/recipients. Mocked channels/reset pass; actual popup/delivery unverified. Environment-based link safeguard verified locally85 |
| Monitoring/load/clock | Blocked; not attempted | Local outage/bounded reads pass; hosted resources, clock, load, distributed limits and alert receipt unverified |
| Hosted dependencies | Blocked; not attempted | Windows consistency passes; target-host clean install, exact backend resolution and fresh complete advisory review unverified |
| Historical review/cutover | Awaiting Production Approval | Actual notes/accounts/legacy evidence/payment exceptions and cutover untouched; unresolved historical risks remain |

Machine-readable detail:[PY35_PHASE1_RESULTS.json](PY35_PHASE1_RESULTS.json).

## Failures investigated and notification fix

Retained `batch-84-initial-check-failures.json` records three test-only failures:
isolated Python launcher lacked its explicit local import path; an old browser
test injected `Bearer null` instead of using approved cookies; another entered
UTC wall time into the approved WAT form, producing an older price. Corrected
only invocation/harness, reset disposable preview, and reran affected checks.
No application authentication, dates or price rules changed.

The confirmed hard-coded watchlist email URL was fixed under explicit owner
authorization in batch85. Email/push/WhatsApp now share a validated explicit
`FRONTEND_URL` origin plus `/prices`. HTTPS is required outside local development/
test loopback. Missing/default-only, malformed, credential-bearing, path/query/
fragment/control/encoded URLs fail closed before any watcher query or send.
Outside production mode the original known live hostname is rejected. Additional
live aliases need review before staging provider tests. All channels skip unsafe
configuration without reversing saved prices. With the original production URL
explicitly configured, the original destination/content and recipient logic stay.
Production settings were not read; correct configuration must be confirmed before
any separately approved release. Real sends remain disabled pending prerequisites.
Verification85:9 URL/delivery tests,5 existing channel tests and4 price-approval/
audit tests pass. Original approval/notification browser and all14 accurate Admin
card checks pass. All sends are mocks, external requests0. No frontend edit/build,
database migration or native concurrency rerun was needed for this URL-only fix.

A test-runtime Starlette/
httpx deprecation warning also remains; tests pass, no replacement was installed.

## Missing staging prerequisites and stop boundary

A dedicated staging hostname/host and secure configuration reference, separate
synthetic database, Paystack TEST setup, Google test identities/allowed return
domains, messaging test credentials and explicitly approved recipients are needed.
Never paste keys into chat or reuse production database credentials. External
setting changes or paid services need separate approval. Existing synthetic
guards remain closed; no generic live-service bypass was added. Future provider
verification needs a narrow reviewed allowlist, mode/recipient restrictions and
disabled background jobs. Hosted monitoring also needs an approved alert target.

Batch84 preserved application files; batch85 changes only the authorized watchlist
URL handling. Application TSX/CSS, terminology, measurements,14 cards,14-day
trial,NGN2500 monthly/NGN6000 seasonal and approved reward/access/value rules stay
unchanged. Fresh synthetic HTTP preview:`http://127.0.0.1:55446`; not HTTPS staging.
No production access, customer records, real payments, push, merge or deployment.
Stop after reporting; no production approval is requested here.
