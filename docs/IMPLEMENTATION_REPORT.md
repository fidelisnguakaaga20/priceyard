# PriceYard hardening implementation report

Date: 2026-10-15, Africa/Lagos. Branch: `codex/priceyard-hardening`; baseline `76dbd27`.

## Outcome and scope

The approved local P00–P13 work has produced implemented source changes and passing synthetic acceptance checks across accounts, access, payments, referrals, prices, administration, notifications, mobile behavior and offline caching. This is a development acceptance report, not a production release certificate. [The complete PY-01–PY-36 map](audit-remediation-status.md) distinguishes implemented fixes from partial mitigation and operational requirements. [The changed-file inventory](evidence/hardening-changed-files.txt) lists every source/document path. [The progress record](../PRICEYARD_PROGRESS.md) preserves history and the next resume point.

No production database/Supabase service was accessed. No customer data was copied, real payment or provider message sent, `.env` opened, push/merge/deployment performed. Tool downloads came from package/browser distributions in separately scrubbed acquisition processes.

## Accepted business behavior

The trial remains 14 days from registration. Purchases remain ₦2,500/30 days and ₦6,000/90 days, with no recurring charge. Renewals stack after unused paid/trial access; legacy inclusive UTC end dates and manual grants remain intact. Future referral awards require a verified first successful purchase, once per referred account, seven days each, capped prospectively at four awards. Previously earned days remain preserved.

Public current/previous summaries remain public. Trial/Paid entitlements govern complete history and deeper guidance; Reporter/Admin authority does not expire with a subscription. Free members retain their own watchlists and confirmed-measurement public-price alerts. Account collisions never silently transfer identity or purchases.

Different markets, units, bags, variants and grades remain independent. Missing recorded averages remain null and comparisons become unknown; chart midpoints are explicitly labelled. UTC instants and Lagos display/search agree. Inactive consumer history and latest-outdated/no-fallback remain unchanged. Published corrections preserve original evidence; withdrawal/archive preserves dependent records.

## Changes delivered

| Packages | Main result | Acceptance evidence |
|---|---|---|
| P00 | Scrubbed configuration, dotenv/native-transport/child-process guards, fresh SQLite, positively identified PostgreSQL, secret-free frontend snapshots, separate tool acquisition | Six negative isolation cases; all tests through guarded entry points |
| P01/P02 | Verification, explicit Google linking, revocable sessions, reset/logout/disable revocation, DB-backed roles, consistent public/full fields | Account and actual-JWT HTTP suites; simultaneous reset and last-admin PostgreSQL cases |
| P03/P05 | Referral/grant ledgers, validated signed events, evidence-based reconciliation, renewal/expiry preservation, durable pending checkout intent | 27 payment service cases; five payment HTTP cases; PostgreSQL duplicate/distinct payment race |
| P04 | HTTP transaction finalizes business data plus sanitized audits before response; failed audit/commit returns failure and rolls back | Main-ASGI fault injection; registration/token/outbox rollback; payment retry proof |
| P06/P07/P11 | Measurement separation, comparable predecessors, revision evidence, active/outdated policy, bounds/constraints, cost provenance, formula-safe bounded exports | 29 price cases; migration preservation/conflict refusal; concurrent approvals |
| P08 | Recoverable errors, ID filters, stale-response protection, authoritative Admin updates, accurate payment callback, verification/renewal UI, older-record paging | Browser workflows, Node paging/helper cases and successful TypeScript build |
| P09 | Transactional encrypted account emails, independent-channel outbox, eligibility rechecks, retries/leases, push validation/public-IP pinning, paired watch matching | Notification/push/reminder/watchlist suites; PostgreSQL deduplication/worker/stale-lease cases |
| P10 | Viewport navigation, Escape/focus handling, validated bounded public cache, saved-data indication and logout purge | Six mock-worker cases, mobile/focus browser cases, actual isolated worker/offline lifecycle |
| P12 | SQL latest/window queries, aggregate dashboard metrics, bounded lists, joined flag summaries, shared simultaneous anonymous reads, lazy Admin chunks and body-inclusive timeouts | Query-count fixtures, 21 Node tests, build sizes, older-record browser scenario |
| P13 | Current README/API/access/schema/status/deployment/worker/testing contracts; historic stage evidence retained | This report, progress record, findings map and focused evidence documents |

## Final executed checks

| Check | Result | Boundary |
|---|---|---|
| Full backend + actual in-process ASGI | **144 passed; 0 failed/error/skipped; 33.352 s** | Synthetic SQLite; TCP/DNS/native libpq/child processes denied |
| PostgreSQL migration/concurrency | **12 passed; 0 failed/error; 20.492 s** | Verified cluster data directory/system identifier; fixed localhost/marked synthetic namespaces |
| Node regressions | **21 passed; 0 failed/skipped** | Secret-free source copy; fake transports; no provider calls |
| TypeScript and Vite | **Passed**, Vite 5.4.21, **1.86 s** | Synthetic build settings; disposable snapshot |
| Browser workflows | **10 passed** | Fresh matching Chromium profile; locally fulfilled requests; workers blocked in workflow suite |
| Actual PWA lifecycle | **Passed** | Fixed 127.0.0.1:55441 synthetic server, then server closed and browser offline; real worker cache/shell/assets/price/history/auth/logout checks |

Counts are distinct suites, not a claimed coverage percentage. Earlier failed runs, their causes and corrections remain in the progress record. The browser suite caught an actual payment-callback unmount loop; the corrected account refresh now preserves mounted screens and the regression passes.

Local main JS is **279.60 kB / 85.18 kB gzip**, CSS **32.37 kB / 7.29 kB gzip**, with separate Admin route chunks. A 500-history fixture returns one current observation using three SELECTs; flag names/counts use one joined query. Dashboard metrics for 129 users, 130 payments and 110 feedback records use **12 SELECTs** and include every record rather than the first page. These are measured local sizes/query counts, not a commercial capacity promise. CSV requests over 10,000 selected observations fail explicitly and request narrower filters; no data is truncated or removed.

## Prepared migrations and dependencies

Prepared and exercised against disposable data: `0022_security_sessions`, `0023_payment_integrity`, `0024_price_integrity`, `0025_notification_outbox`. Existing `0021` history, purchased dates, amounts, source evidence and manual grants survive the populated synthetic upgrade. Normalized duplicates/invalid ranges abort preflight; no automatic merge or invented correction. Evidence-losing downgrades refuse execution.

Frontend patch updates retain the existing major versions: React Router DOM 6.30.6 and Vite 5.4.21. Rationale: [React Router advisory](https://github.com/remix-run/react-router/security/advisories/GHSA-jjmj-jmhj-qwj2) and [Vite Windows advisory](https://github.com/vitejs/vite/security/advisories/GHSA-93m4-6634-74q7). Package-lock records the full tree; Playwright 1.56.1 is development-only. `backend/requirements-dev.lock` records the exact 60-package Windows/Python 3.14 verification environment. Cryptography is now declared directly for proof-email encryption. Linux/target-host resolution and ongoing advisory monitoring remain required; this is not a universal vulnerability clearance.

## Remaining limitations and release requirements

- **PY-07 remains partially mitigated:** refresh credentials are JavaScript-readable; HttpOnly cookie/hosting design, administrator MFA and full refresh-family replay detection are not implemented. Access is short-lived and server-revocable. Do not advertise these remaining protections as completed.
- Providers were mocked. Paystack signature/payload compatibility, email delivery, Google credentials, push transport and WhatsApp permissions must be verified in a separately approved sandbox/staging environment. Historical reconciliation needs trustworthy signed evidence and a reviewed disposition; old access is not guessed.
- A scheduled notification worker is required. Monitor oldest pending age, expiry and failures; proof-email key rotation needs pending-job expiry/drain or reissue. Provider delivery is at least once after send/acknowledgement crashes.
- Default rate limiting is process-local. Use one API worker with that default; multiple workers require a reviewed shared store/dependency, proxy/NAT behavior and tested failure policy.
- Process guards do not certify a general VM boundary against malicious native code. The worker lifecycle test allows exactly one literal local fixture bind; normal tool transport remains denied. Browser page traffic is controlled; arbitrary native background traffic was not comprehensively packet-audited.
- The PWA lifecycle passed in the matching local Chromium. Android/iOS install prompts, push permissions, real shared devices, full screen-reader use, zoom/landscape combinations and every browser version remain acceptance coverage.
- Backup restoration, target schema conflict review, least-privilege DB roles, TLS/security headers, monitoring, host capacity and production readiness remain unverified. Production inspection and deployment were excluded by authorization.
- Some legacy Admin components retain compressed formatting. Their relevant behavior was repaired; a wholesale rewrite was not performed.

## Release and recovery boundary

The repository is ready for technical review and controlled staging preparation. It is **not approved for production deployment**. Follow [the deployment/recovery runbook](deployment-plan.md): preserve the previous artifact, obtain an approved backup and isolated restore proof, assess real migration preconditions, release compatible frontend/backend versions, arrange a fresh-login communication plan, and verify worker/provider operation. Prefer reviewed forward repair; do not discard entitlement/revision/outbox evidence to downgrade. Restoring a backup requires reconciliation of intervening transactions.

Local checkpoint commit references and any final review findings are recorded in `PRICEYARD_PROGRESS.md`. No remote publication is implied by a local commit.
