# PriceYard development progress

Last updated: 2026-10-15 (Africa/Lagos). Working branch: `codex/priceyard-hardening`.
Latest verified: **144 backend, 12 PostgreSQL, 21 Node and 10 browser workflows passed; actual offline PWA lifecycle passed; TypeScript/Vite build passed**. No production release.

Starting commit: `76dbd27`. **Implementation checkpoint: `13a83e8`** ? 187 files, including source, four migrations, tests, dependencies, progress, findings map and deployment/recovery documentation. This local commit has not been pushed. A following documentation-only commit records final handover details.

## Authority and safety boundaries

The owner approved development across PY-01–PY-36 and P00–P13 in the full-development authorization supplied in the conversation. The 2026-10-15 instruction explicitly requests continuation, preservation of existing work, and this persistent record. Earlier planning-only restrictions were superseded for local development.

- Source changes, dependencies, synthetic local tests, disposable database migrations and local commits are authorized.
- No production database, production Supabase, real provider transaction, customer-data copy, push, merge or deployment is authorized.
- Do not open `.env` files or expose credentials. Test runners scrub inherited application configuration and reject secret-file reads.
- Preserve existing edits and historical records. Do not reset this branch or automatically repair production records.

## Approved business baseline

- Trial: 14 days from registration, without resetting its start after verification.
- Monthly: ₦2,500 for 30 days. Seasonal: ₦6,000 for 90 days. No recurring charge or new annual plan.
- Preserve unused paid/trial time when renewing, existing manual grants, old earned referral rewards and historical business evidence.
- Public current/previous price summaries remain available. Full history and deeper guidance require valid Trial/Paid access or Admin authority. Reporter authority is independent of paid access. Free members retain their own watchlists/preferences and public-price alerts.
- Verify ownership before Google linking and future referral qualification; never merge accounts by matching email alone. Preserve valid existing passwords and the eight-character baseline; reset links expire after 15 minutes.
- Future referrals: one seven-day award for a verified referred account's first successful purchase; conservative implementation cap of four awards (28 days). Previously earned days remain intact.
- Match commodity, market, unit, bag size, type and grade before comparing prices. Do not infer historical measurements, averages, conversions or payment evidence.
- Store clear UTC instants; use Africa/Lagos for display and date searches. Preserve active-only consumer history and latest-outdated/no-fallback behavior.
- Authorized corrections take effect immediately, with reasons and retained evidence; published price records are withdrawn rather than erased.
- Conservative session defaults implemented for isolated review: 15-minute access tokens, 24-hour nonremembered sessions, 90-day explicitly remembered sessions. Cookie/hosting and Admin MFA rollout remain deployment decisions.

## Implemented source changes; verification status

| Package | Existing implementation on branch | Current status |
|---|---|---|
| P00 | Guarded SQLite/native-transport runner; marked disposable PostgreSQL; secret-free build/browser environments | Six negative isolation tests, full guarded suites, and actual loopback PWA lifecycle passed; general VM security is not claimed |
| P01 | Verification, safe Google linking, rotating refresh, server revocation/reset/last-admin protection | Auth/API tests passed in full suite; two real PostgreSQL security races passed; remaining cookie/MFA/replay limits below |
| P02 | Public/full field/history boundaries; DB-backed roles and entitlements | Actual-JWT HTTP and service tests passed |
| P03 | First verified purchase qualification, unique ledger and prospective cap | Referral/payment tests passed; old awards preserved |
| P04 | Pre-response transaction ownership and sanitized complete administrative auditing | Registration, audit and final-commit fault injection passed; no partial success persisted |
| P05 | Signed evidence, reconciliation/grants, expiry/renewal preservation and durable checkout intent | 27 service + five HTTP payment cases and PostgreSQL races passed |
| P06/P07 | Separate measurements, SQL latest/predecessors, Lagos time, retained corrections, costs and identities | 29 price tests and real migration/approval concurrency passed |
| P08 | Recovery/race handling, authoritative admin records, payment confirmation, verification/renewal and older-record paging | TypeScript/build, Node and real synthetic browser workflows passed |
| P09 | Encrypted transactional proof emails; independent leased/retried outbox; safe push and exact targets | Auth/notification/reminder/push/watchlist suites and PostgreSQL worker claims passed; live providers not contacted |
| P10 | Responsive navigation, focus, bounded public-only cache and saved timestamps | Six mock-worker regressions, mobile/focus workflows and actual offline shell/assets/public-price/logout lifecycle passed |
| P11/P12 | Bounds/archives/CSV safety, SQL window and aggregate queries, pagination, lazy chunks, shared reads and timeouts | Query fixtures, full tests and measured build passed; production capacity remains unverified |
| P13 | Current progress/report/findings/API/access/worker/deployment/testing documentation | Local contracts complete; historical evidence retained; release limitations explicit |

## Retained test history (do not mistake for current full verification)

- Guarded payment suite: 22 tests passed before durable checkout-intent change.
- Guarded authentication: 17 unit tests plus 3 HTTP tests passed after transaction middleware fix, before encrypted-email queue work.
- Guarded price suite: grew from 21 to 24 passing tests. A synthetic 500-history fixture returned one current row using three SELECTs (price/commodity/market); no production throughput claim.
- Last captured full backend run: **72 tests, 2 failures, 1 error**. All three were old watchlist tests expecting synchronous email delivery. They must be updated to assert actual queue/worker behavior and rerun; failures are not waived.
- Frontend synthetic Node run: **12 passed** (six price/date/admin helpers and six service-worker cases).
- First secret-free TypeScript check failed on two AuthContext typing errors. Source fixes were applied (Google remember argument and a Promise callback return); build has not yet been rerun successfully.
- PostgreSQL agent reported duplicate/distinct payment races and comparable approval races passing, but no complete final run output was retained. Treat migration verification as pending until rerun.

## Disposable environment and safe commands

All paths below are relative to the repository. Run Python with `-I -B`.

- Python test interpreter: `audit-prep/p00/runtime/venv/Scripts/python.exe` (created using local Python 3.14).
- SQLite tests: interpreter + `audit-prep/p00/run_backend_tests.py`. No arbitrary database URL accepted; only fresh in-memory SQLite. Unexpected TCP/DNS and `.env`/key reads are denied; Windows asyncio's internal socket pair has a narrowly scoped exception.
- Frontend: base Python + `audit-prep/p00/prepare_frontend.py`. Copies allowlisted source/tooling to a unique ignored snapshot, excludes dotenv files, scrubs configuration and uses `node_transport_guard.cjs` before Node tests/TypeScript/Vite.
- PostgreSQL: new native PostgreSQL 18 cluster at `audit-prep/p00/runtime/postgres-test`, bound to `127.0.0.1:55439`, synthetic user `priceyard_test_admin`. Marker generated from offline `pg_controldata`. Verifier must check live data directory and system identifier before mutation and only use run-marked namespaces in `priceyard_test`.
- Docker executable exists, but no Docker daemon was available. No VM/container isolation was established. Python/Node guards are defense in depth; they do not prove immunity to malicious native code.
- Tool acquisition was separate from application tests. No tests may be granted arbitrary provider/network access to make them pass.

## Migrations prepared

`0022_security_sessions` → `0023_payment_integrity` → `0024_price_integrity` → `0025_notification_outbox`, following existing `0021_feedback_screenshot`.

These are local source files, not production execution. Legacy successful payments are flagged for evidence-based reconciliation, not automatically granted twice. Existing unknown measurements remain unknown. Normalized duplicates/invalid price ranges require explicit reviewed remediation before constraints; no automatic merge. Evidence-losing downgrades refuse execution: deployment needs backup/restore and a forward-recovery procedure.

## Remaining work and next resume point

The earlier local implementation/testing backlog and final review are complete at the local checkpoint, subject to the explicit unresolved security and release requirements below. Consult [the implementation report](docs/IMPLEMENTATION_REPORT.md) and [all-36 findings map](docs/audit-remediation-status.md) before interpreting this as production readiness.

1. Completed: reviewed/staged only intended source and documentation, passed cached diff checks and created local implementation checkpoint `13a83e8`. Preserve that checkpoint and the final test results below.
2. Before release, decide the final cookie/hosting/MFA policy; JavaScript-readable refresh tokens and missing refresh-family replay detection remain explicitly open security limitations.
3. Separately authorize/configure staging-provider compatibility checks, scheduled outbox worker, shared limiter if scaling, target-host dependency review, exact proxy/CORS/TLS and database privileges. Current local authorization does not permit contacting live providers/production.
4. Obtain an approved backup and isolated restore proof, review actual migration conflicts/evidence, and agree on recovery/monitoring/load targets. Do not infer actual customer records from synthetic fixtures.
5. Complete real-device installation/push-permission and broader assistive-technology coverage. Local Chromium offline lifecycle and focused viewport/keyboard cases now pass; universal compatibility is not established.
6. Continue incremental legacy component formatting only when needed for maintainability; no rewrite is required to repeat the completed audit work.

Future sessions should read this file, inspect changes since the recorded checkpoint, and resume the specific remaining requirement. Do not rerun the audit or claim that partial security/operational findings are closed.

## Known limitations requiring truthful reporting

- Bearer refresh credentials are currently stored in browser JS-accessible storage; access tokens stay in memory. HttpOnly cookie migration and full refresh-family reuse detection are not implemented. Server-side reset/logout/disable revocation is implemented.
- Notification providers necessarily offer at-least-once delivery after a send/acknowledgement crash. Logical enqueue deduplicates events; do not claim exactly-once external delivery.
- Existing ambiguous target alerts retain their amounts but pause price triggering until the owner confirms measurements; ordinary public-price watching remains available.
- No production record inspection, live provider call, real payment, push, merge or deployment has been performed.

## Session log

- Earlier authorized session: implemented the changes above, established guard runners and disposable PostgreSQL cluster; interrupted before final notification tests, build, complete migration evidence and documentation.
- 2026-10-15 continuation: confirmed branch `codex/priceyard-hardening`, starting commit `76dbd27`, substantial preserved uncommitted changes and no prior progress document. Created this record before resuming implementation. Current verification results will be appended below.
- Continuation verification: first rerun retained **72 tests with 2 failures/8 errors** from unfinished synchronous-email mocks. Completed actual encrypted outbox/worker tests and fixed fixtures; subsequent combined run **118/118 passed**. Later additions still require the final combined run.
- Additional verified continuation checks: **27 payment service tests passed**, **5 payment HTTP tests passed**, **28 price tests passed**, **8 main-app HTTP workflow tests passed**, **10 disposable PostgreSQL tests passed**, **6 negative isolation tests passed**, and **2 readiness tests passed**. Counts overlap with combined discovery; do not add them together as unique tests.
- Compatible frontend dependency patches: React Router DOM `6.30.6`, Vite `5.4.21`; added Playwright `1.56.1` development tooling and recorded `frontend/package-lock.json`. Acquired in a clean app-free directory with lifecycle scripts disabled. Recorded 60 installed Python packages in `backend/requirements-dev.lock`; declared direct cryptography dependency for encrypted proof emails.
- Dependency-patched isolated frontend build succeeded: TypeScript passed, **14 Node tests passed**, Vite completed in **1.41 seconds**, main JS **278.49 kB / 84.86 kB gzip**, CSS **32.37 kB / 7.29 kB gzip**, with separate Admin chunks. These are local bundle measurements, not capacity guarantees. Later frontend/API/pagination changes need another build.
- Browser attempts using installed Chrome/Edge failed before executing checks because both rejected remote debugging in the isolated profile. No browser workflow pass is claimed. Matching disposable Playwright headless browser acquisition is underway; all application page requests will be fulfilled locally or blocked.
- New readiness implementation separates `/health` liveness from `/ready` schema/signing-key readiness and redacts private failures. New checkout validation binds provider-returned reference and restricts checkout URLs; Admin/manual grants cannot start unnecessary purchases. Six negative tests now cover direct native libpq, alternate SQLAlchemy entry points, child processes, TCP/DNS and secret-file reads.
- Current active finishing work: accurate aggregate Admin metrics; bounded administration lists with reachable older pages; shared simultaneous anonymous reads and body-inclusive API timeouts; browser checks; final documentation and combined verification.
- Latest consolidated verification: **141 backend/actual-ASGI tests passed**, zero failures/errors/skips, **27.289 seconds**. This includes the completed queued proof/reminder tests, checkout failures, payment callbacks, access boundaries, isolated-transport negatives, Admin metrics, query pagination and readiness. Earlier failed runs above remain historical evidence and have been corrected.
- Latest PostgreSQL run: **10 tests passed**, zero failures/errors, **15.486 seconds**. Fresh/populated upgrades, preservation/preflight, downgrade refusal and payment/price/outbox concurrency were verified against the fixed disposable cluster. Two additional account-security race tests were requested but are not yet established as executed.
- Latest frontend: **21 Node tests passed**, TypeScript passed, Vite `5.4.21` build passed in **1.65 seconds**; main JS **279.25 kB / 85.11 kB gzip**, CSS **32.37 kB / 7.29 kB gzip**. Admin pages are separate chunks. Exact versions are in package-lock; this build used synthetic `/api` settings.
- Latest browser: **10 synthetic Chromium workflows passed**, including public prices/measurements, 320/375/768px overflow checks, navigation Escape/focus, onboarding focus trap, error recovery, successful/outage login, fixed-duration plan labels, pending and confirmed payment messaging, Lagos Reporter submission without invented average, and older Admin records beyond the first 100. Browser checks caught and fixed an account-refresh loop that unmounted the confirmed-payment screen. All page requests were intercepted locally; service workers were blocked for this suite.
- Admin metrics now aggregate all records (fixture: 129 users, 130 payments, 110 feedback) in **12 SELECTs**, instead of downloading nine lists and presenting first-page counts as totals. Recorded-success amounts remain separate from provider confirmation/access evidence and currencies are not combined.
- Administration pages now expose bounded paging and reject stale responses. Public simultaneous reads are coalesced without persistent caching; API timeouts cover response bodies and CSV downloads share refresh/error handling. CSV exports explicitly reject more than 10,000 selected observations and request narrower filters, retaining all records. The export-bound regression passed.
- Canonical README/API/access/deployment/testing docs and the all-36 findings status map are updated. Remaining active verification: actual isolated service-worker lifecycle; optional additional reset/last-admin PostgreSQL race evidence; final source review, evidence report and recoverable local commit. External provider, hosting, backup-restore, HttpOnly-cookie and MFA limitations remain release decisions, not hidden completed work.
- Final additional verification: **12 PostgreSQL tests passed in 20.492 seconds**, including concurrent reset-token single use with session revocation and concurrent last-admin protection. **Actual PWA lifecycle passed** after closing the literal loopback synthetic server: offline shell, JS/CSS and public prices loaded; authenticated/history fetches failed rather than using cache; logout removed saved prices. The initial PWA attempt exposed a browser offline-emulation limitation; closing the fixture server made the network failure explicit. No production service was involved.
- Reviewed 182 then-current changed files: no ignored runtime/snapshot/node_modules/secret-file artifacts in the change set and no credential-pattern candidates. Full findings/status and deployment/rollback details are in `docs/IMPLEMENTATION_REPORT.md`; a tracked changed-file manifest will accompany the checkpoint.

- Final frontend build after the capped badge clarification: 21 Node tests and TypeScript passed; Vite completed in 1.44 seconds, main JS 279.26 kB / 85.12 kB gzip. Documentation-only changes do not require repeating the passing runtime suites. The changed-file inventory contains 184 paths; runtime, browser binaries, build snapshots and private configuration are excluded.

- Final visual review added missing grade/type labels to public cards/share text and corrected social-preview exact commodity/current measurement selection. Three new share-card HTTP tests passed; full backend now **144/144 passed in 33.352 seconds**. Final Node **21/21**, TypeScript and Vite passed in **1.86 seconds**, main JS **279.60 kB / 85.18 kB gzip**. Current browser tests also assert the grade is visible. No pricing, trial or historical record was changed.

- Checkpoint: **13a83e8**, `Harden PriceYard accounts, payments, prices and isolated verification`; **187 files changed**. Commit hooks were disabled for this local checkpoint to avoid external side effects. Final browser 10/10 and PWA lifecycle both passed against the final grade-labelled build. No code changed after those checks.
- The disposable PostgreSQL cluster is stopped after verification; its synthetic data and identity marker are retained under ignored `audit-prep/p00/runtime/`. Future PostgreSQL runs require starting only that same marked cluster on 127.0.0.1:55439, then using the fixed guarded verifier. Do not initialize or select a configured production database.
- Next work requires a concrete remaining security/operational requirement from the list above. Do not deploy, push, merge, migrate production or contact live providers without the separate authorization those actions require.
