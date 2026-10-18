# PY-35 Phase 1 results — 2026-10-18

**35/36 complete; PY-35 partial.** Phase 1 permits safe staging and provider TEST
verification, not production. No staging URL, provider TEST credentials, test
identities or approved recipients were supplied. "Do best option for the app"
did not supply these prerequisites or authorize production as a substitute.
No external settings, accounts, paid services, live jobs or messages were changed.

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

These statuses describe **Phase 1 only**. Failed—blocked means acceptance could
not be demonstrated because prerequisites are missing, not a confirmed product
defect. Passed applies only to the stated synthetic sub-scope. All original live
gates in `RELEASE_GATES.json` remain unrun; release is unauthorized.

| Gate | Phase 1 status | Remaining evidence / risk |
| --- | --- | --- |
| Hosting/cookies/browsers | Failed—blocked | No staging HTTPS/domain. Hosted cookies/proxy/CORS, Android/browser/Web Locks, session conversion and Google return unverified; hosted login could fail |
| Backup/restoration | Passed, synthetic only | Real backup retrieval/provider objects, encrypted off-host copy, retention and recovery objectives require customer-data/production approval |
| Production schema/rollout | Awaiting Production Approval | Actual revision/preflight and reviewed migration/rollback untouched; incompatible schema could prevent safe release |
| Paystack TEST | Failed—blocked | No TEST credentials/setup; no Paystack request/charge. Provider checkout, callbacks, failures/abandonment, value preservation and review holds unverified |
| Recovery scheduling | Passed, finite rehearsal only | Checkpoint ticks/native single-worker/replay pass. Hosted durable scheduling/alerts still need staging infrastructure; no actual job enabled |
| Google/email/notifications | Failed—blocked | Missing identities/credentials/recipients. Mocked channels/reset pass; actual popup/delivery unverified. Live-site email link needs staging-safe handling |
| Monitoring/load/clock | Failed—blocked | Local outage/bounded reads pass; hosted resources, clock, load, distributed limits and alert receipt unverified |
| Hosted dependencies | Failed—blocked | Windows consistency passes; target-host clean install, exact backend resolution and fresh complete advisory review unverified |
| Historical review/cutover | Awaiting Production Approval | Actual notes/accounts/legacy evidence/payment exceptions and cutover untouched; unresolved historical risks remain |

Machine-readable detail:[PY35_PHASE1_RESULTS.json](PY35_PHASE1_RESULTS.json).

## Failures investigated and remaining compatibility issue

Retained `batch-84-initial-check-failures.json` records three test-only failures:
isolated Python launcher lacked its explicit local import path; an old browser
test injected `Bearer null` instead of using approved cookies; another entered
UTC wall time into the approved WAT form, producing an older price. Corrected
only invocation/harness, reset disposable preview, and reran affected checks.
No application authentication, dates or price rules changed.

Confirmed remaining issue:watchlist email content in
`backend/app/services/watchlist_alert_service.py` hard-codes the deployed-site
price link. Staging emails could direct testers to production. Keep actual sends
disabled until reviewed staging-safe handling is agreed. Application code was
preserved; no silent change to visible message content. A test-runtime Starlette/
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

All application TSX/CSS/backend files, terminology, measurements,14 cards,14-day
trial,NGN2500 monthly/NGN6000 seasonal and approved reward/access/value rules stay
unchanged. Fresh synthetic HTTP preview:`http://127.0.0.1:55446`; not HTTPS staging.
No production access, customer records, real payments, push, merge or deployment.
Stop after reporting; no production approval is requested here.
