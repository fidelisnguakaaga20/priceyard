# PriceYard progress — original appearance preserved

## Authority and baseline

2026-10-16: owner authorized progressive technical fixes, starting from restored
master 76dbd27588de4aa37f3163d8b263d4b72a2cff32. New branch:
codex/priceyard-original-preserved-20261016. Preserve backup branch
backup/priceyard-hardening-20261015 at 258991019e5af8b36eff407a8efa2c9fd03dd644;
use it only as reference, without merging its implementation wholesale.

Preserve original design, wording, fields, measurements, features and policies.
Trial stays 14 days; monthly NGN 2,500/30 days; seasonal NGN 6,000/90 days.
Keep original referral qualification/rewards and session policy unless separately
approved. No grade field, grade labels, guessed quantities or additional markets.
No production credentials, dotenv reads, production services/data, migrations,
push, merge or deployment. Local commits of verified batches are authorized.
Schema additions and visible/business changes require specific approval.
Owner approved the specific internal auth_version/revoked_access_tokens scope on
2026-10-16; see docs/LOCAL_SECURITY_STORAGE_PROPOSAL.md. No other schema/business
scope is inferred from that approval. Production migrations remain forbidden.

## Status and next step

Baseline browser/isolation verification passed. Batch 1 (PY-15) verified:
homepage/current prices clear stale errors after normal successful refresh.
Batch 2 (PY-34) verified: subscription transitions preserve staff authority and
subscription listing processes every expired account. Batch 3 (PY-10) verified:
spreadsheet-safe text export. Batch 4 verified existing account refresh/logout
races (part of PY-18). Batch 5 verified approved internal login revocation storage
(PY-04 and parts of PY-07/PY-09/PY-28). Batch 6 verified remaining PY-09 last-Admin
concurrency protection. Batch 7 verified historical URL/access boundaries (PY-01)
and quality-signal access matching the existing full-access screen (part of PY-02).
Batch 8 verifies strict signed payment evidence (part of PY-33). Batch 9 verifies
atomic payment/access/audit writes and concurrent replay/provider-ID protection
(parts of PY-31/PY-33/PY-26). Batch 10 verifies saved Admin price state (PY-11).
Batch 11 verifies account expiry display/timers (further PY-18; legacy UTC parsing
part of PY-13). Batch 12 verifies original FAQ draft/publication persistence
(PY-19). Batch 13 verifies push destination/key validation and safe transport
(PY-06, part of PY-08); all 58 backend tests passed (16.577s).
Browser storage/rejection/cleanup passed without provider delivery. Preview startup
now verifies its launcher/serving-process identity and synthetic-only readiness.
Owner approved PY-32 paid/trial-time preservation on 2026-10-16, exactly rules
1 and 2 in docs/PURCHASE_VALUE_APPROVAL.md; indefinite-grant handling was separately
approved and verified in batch 21. Batch 14 implements and verifies the approved
dated-renewal/trial calculations. Batch 15 verifies checkout validation: 74 backend
tests and original-button fake-provider browser checks passed. Next: commodity
detail loading (PY-17) is verified in batch 16: five before/after browser checks
and TypeScript/build passed; seven baseline browser workflows also passed. Next:
PY-07 push ownership protection is verified in batch 17. Batch 18 verifies
current-device logout cleanup with a one-second maximum cleanup wait before
server revocation. Ten targeted logout/account/reset browser checks passed;
TypeScript/build passed and original CSS remains unchanged. Next: payment
verification/reconciliation (PY-31/PY-33), bounded queries (PY-20), remaining
authorization/source confidentiality, referrals and atomic administrative audits.
Indefinite manual-grant handling was subsequently approved and implemented in
batch 21, preserving grants and held paid days. Do not implement it again.
Continue from the newest batch status without restarting the audit.
Apply small technical batches with automated and browser verification. Reuse
existing local tools from .git/priceyard-local-recovery-20261015; do not reinstall
or read private configuration. Runtime is tools/local-test/runtime (ignored).

Batch 19 verified: owner-only provider verification shares the atomic webhook
confirmation path. Callback recovery refreshes entitlement without changing its
markup/CSS/guidance. All 87 backend tests, eight final verification/quota tests,
eleven marked PostgreSQL cases and payment/account browser checks passed. PY-18
and PY-33 identified application defects complete: twelve IDs complete, 24 remain
partial/pending. Next: atomic referral registration/reward, price query accuracy/
bounded materialization, remaining source confidentiality and administrative audits.

Batch 20 verified registration/referral atomicity. Batch 21 implements the owner's
approved indefinite-grant checkout/held-purchase rules: all 99 backend tests,
fourteen marked PostgreSQL cases and original Admin/browser review/recovery passed.
PY-32 now complete: thirteen IDs complete, 23 partial/pending. Next: correct price
filter refresh/order behavior, bounded current-price queries, source confidentiality
and remaining atomic administrative writes. Preserve all original price units.

Batch 22 verified: current-price requests ignore superseded responses;
automatic refresh uses the last applied filters and skips a pending foreground
request. Four filter checks, both outage/recovery checks and seven original-browser
baseline workflows passed; TypeScript/Vite passed. Original JSX/CSS unchanged.
Batch 23 verified: database-side current-price ranking passes six focused tests,
105 full backend tests, fifteen pinned PostgreSQL cases, seven baseline browser
flows and eight account/access cases. All historical records remain accessible.
Batch 24 verified: notification email failure no longer skips the same user's
push/WhatsApp attempts. Five focused tests, all 107 backend tests and the original
Watch/Admin approval browser workflow passed. Fourteen IDs complete, 22 partial/
pending. Next: atomic price changes/audit and post-commit notification failures.

Batch 25 verified: create/edit/approve/reject/outdated and sanitized audit commit
together, concurrent edits lock the current price row, and a post-commit alert
failure cannot misreport a saved change. Four focused tests, all 111 backend
tests, sixteen pinned PostgreSQL tests, original Admin and notification browser
workflows passed. Fourteen IDs complete, 22 partial/pending. Next unfinished:
remaining administrative audit transactions, bounded feedback screenshot decoding/
requests, Google-claim validation/account-linking decision, and price comparison
semantics requiring owner approval. No redesign or new measurement assumptions.

Batch 26 verified: feedback screenshot bounds before decoding and stale file
selection guards. All 116 backend tests, seventeen pinned PostgreSQL cases and
four before/after browser checks passed; original CSS unchanged. Owner approved
the practical secure Google linking option in docs/GOOGLE_ACCOUNT_LINKING_APPROVAL.md
on 2026-10-16. Implement/verify that next; no further approval required for that
exact scope. Fourteen IDs complete, 22 partial/pending. Native test PG is running.

Batch 27 verified: approved subject-based Google ownership, strict verified claims,
bounded certificate transport/token input, controlled outages and concurrent
first-login recovery. All 126 backend tests, twenty marked PostgreSQL cases and
six browser/API/account checks passed. Fifteen IDs complete, 21 partial/pending.
Next: history/navigation response ordering, existing date-entry consistency,
dashboard query/totals efficiency and remaining administrative transactions.

Batch 28 verified: current URL navigation updates filters; old history requests/
errors and metadata cannot overwrite newer state. Four before/after browser,
four current-filter regressions and eight access-role cases passed; TypeScript/
Vite passed, original CSS unchanged. Backend unchanged (latest 126 backend/20
native PG from batch 27). PY-16 identified scope complete: sixteen complete,
20 partial/pending. Next: bounded dashboard metric aggregation, then remaining
date-entry consistency, administrative audits and history-query efficiency.

Batch 29 verified (2026-10-17): all fourteen original dashboard cards/definitions
use one Admin-only aggregate request and one read-only DB statement. Five focused
tests, all 131 backend tests, twenty-one pinned PG cases and before/after browser
totals/loading/recovery passed. Original CSS unchanged. PY-22 identified dashboard
scope complete: seventeen complete, nineteen partial/pending. Next: atomic Admin
account/subscription/audit changes, date-entry consistency and remaining checklist.

Batch 30 verified: Admin account/subscription/access/revocation/audit updates
commit together using User -> Subscription locks and the existing last-Admin guard.
All 136 backend tests, 23 pinned PostgreSQL cases and original Admin controls /
six sanitized audit records / dashboard regression passed. Seventeen complete,
nineteen partial/pending. Next: existing price date-entry consistency, remaining
administrative audits and bounded history metadata. No policy, field or UI changes.

Batch 31 verified: original Admin create/correction date-time inputs now send UTC
like the existing Reporter form. Lagos/UTC browser before/after, Reporter and
complete original Admin workflow pass; four backend price/audit regressions and
24 pinned PG cases pass. TypeScript/build passes; original CSS unchanged.
Seventeen complete, nineteen partial/pending; date display/day-filter decisions
remain separate. Next: bounded protected history metadata and other Admin audits.

Batch 32 verified: history filter metadata uses a protected DISTINCT name-pair
query instead of downloading every historical price a second time. Four new
tests plus access matrix pass; all 140 backend and 25 pinned PG cases pass.
Browser before/after, navigation ordering and eight role cases pass; original
market options and complete filtered history preserved. TypeScript/build passes,
original CSS unchanged. Seventeen complete, nineteen partial/pending; other
unbounded lists and remaining administrative audits are still open.

Batch 33 verified: FAQ create/edit/publish/hide/delete and sanitized audit commit
together, with row locks for existing records. All 143 backend tests, 26 pinned
PG cases and original FAQ browser controls/publication/reload/audit checks pass.
Frontend unchanged. Seventeen complete, nineteen partial/pending. Next unfinished:
other Admin catalog/editorial/feedback/audit transactions, compatible list bounds,
remaining mobile/accessibility and explicitly pending business/operational cases.

Batch 34 verified: commodity/market create/edit/delete and sanitized audit commit
together; existing-row writes lock before snapshots. Four focused tests, all 147
backend tests, 27 pinned PG cases and original catalog/browser/history/dashboard
regressions pass. No frontend/schema/business-rule changes. Seventeen of 36 IDs
complete; nineteen partial/pending. Native synthetic PG stopped and status verified;
browser preview remains http://127.0.0.1:55446. Resume with other Admin writers,
then remaining compatible performance, mobile/accessibility and pending decisions.

Batch 35 verified: feedback moderation and price deletion commit with audits;
flag resolution is atomically audited once per actual resolution. Future feedback
audits omit private screenshot bytes while original feedback retains them.
All 152 backend tests, 29 pinned PG cases and original moderation browser workflows
pass. Seventeen complete, nineteen partial/pending. Comparison proposal awaits
owner reply in docs/PRICE_COMPARISON_APPROVAL.md; do not infer approval. Next:
flag input/query bounds and missing editorial/resource audits, then usability.

## Checklist — do not repeat the audit

| ID | Improvement | Current status |
|---|---|---|
| PY-01 | Consistent historical access checks | Complete in batch 7; date/comparison/ID routes enforce existing history entitlement; current summaries preserved |
| PY-02 | Confidential/restricted market information | Partial: quality list/detail match existing premium screen; broader source/audit response review pending; public basic guidance unchanged |
| PY-03 | Google ownership and safe account linking | Application-side approved scope complete in batch 27: stable subject ownership, no email-only linking/overwrite, existing password/reset fallback and original trials; cryptographic/HTTP/PG/browser verified. Live Google popup/provider compatibility remains operational PY-35 |
| PY-04 | Password reset and login revocation | Complete in batch 5; actual HTTP/browser and PostgreSQL reset/logout races passed |
| PY-05 | Referral abuse protection | Partial: atomic registration/reward/audit, duplicate-registration safety and concurrent seven-day reward preservation verified in batch 20; qualification/abuse-cap changes require approval and remain unchanged |
| PY-06 | Safe push notification destinations | Application-side complete in batch 13; known-provider/key validation, bounded TLS transport, no redirects; live provider compatibility remains operational verification |
| PY-07 | Shared-device/session safety | Partial: server revocation, stale UI protection, possession-based push ownership/concurrent registration and bounded current-device logout cleanup verified; JS token storage/offline cleanup limits remain |
| PY-08 | Input/upload/request abuse bounds | Partial: push endpoint/key/query bounds and feedback pre-decode 2MB screenshot bound verified; broader request bounds pending |
| PY-09 | Concurrent security-action safety | Complete for identified reset/logout/last-Admin cases in batches 5/6; six PostgreSQL cases passed |
| PY-10 | Spreadsheet export safety | Complete in batch 3; text/numeric regressions and original browser download/access checks passed |
| PY-11 | Correct saved administrator price state | Complete in batch 10; actual create/approve/correct/outdated/reject/reload browser regression passed |
| PY-12 | Accurate existing quantity/type/market comparisons | Pending; no grades/new measurement fields |
| PY-13 | Consistent Nigerian dates/times | Partial: legacy naive trial timestamps treated as UTC; original Admin create/correction inputs now convert local time to UTC like Reporter, with Lagos/UTC browser and PG persistence verified; remaining display/day-filter semantics pending, original paid UTC policy unchanged |
| PY-14 | Evidence-based movement/confidence | Pending; wording/policy changes require approval |
| PY-15 | Prices recover after failed loading | Complete in batch 1; before/after browser regression passed |
| PY-16 | Correct filters and response ordering | Complete for identified current/history/navigation scope in batches 22/28: applied filters, overlap, URL navigation, stale history/error/metadata and access-role browser regressions verified |
| PY-17 | Correct market-detail loading | Complete for identified loading races/combined-failure defect in batch 16; obsolete commodity/account responses ignored and independent successful sections retained |
| PY-18 | Accurate account/payment/access messages | Complete for identified account/expiry/callback defects in batches 4/11/19; verified return refreshes access, unconfirmed return never claims payment received in title |
| PY-19 | Existing FAQ draft/hide/publish management | Complete in batch 12; hidden drafts remain available to Admin across reload, public publication boundary verified |
| PY-20 | Bounded queries with accessible historical records | Partial: current-price DB ranking (batch 23), single-query dashboard summary (batch 29), compact protected DISTINCT history filter metadata (batch 32); complete history and other unbounded lists remain unchanged/pending |
| PY-21 | Reliable independent alerts | Application-side identified channel dependency complete in batch 24: failed email no longer skips push/WhatsApp; per-user/channel failures isolated; existing deduplication/count semantics retained. Delivery/retry operations remain PY-35 |
| PY-22 | Efficient loading and accurate dashboard totals | Complete for identified dashboard scope in batch 29: all 14 original metrics preserved; one Admin-only aggregate API/DB snapshot, zero entity hydration; backend/PG/browser totals and outage recovery verified |
| PY-23 | Preserve layout while fixing mobile overflow | Pending |
| PY-24 | Keyboard/focus accessibility | Pending |
| PY-25 | Safe and clearly aged offline prices | Pending; visible additions require approval |
| PY-26 | Complete atomic administrative audit | Partial: payment, registration/referral, price create/edit/approve/reject/outdated, Admin user/subscription/access, FAQ and commodity/market create/edit/delete share atomic sanitized audits; concurrent price/status/FAQ/catalog trails and rollback verified; other administrative writes pending |
| PY-27 | Consistent existing editing/password inputs | Partial: feedback file replacement/removal/async ordering fixed without form changes in batch 26; remaining editing/password cases pending |
| PY-28 | Historical record preservation | Partial: approved 0022 tested on fresh/populated synthetic PostgreSQL; future migration/history work pending |
| PY-29 | Stable identities and dependent records | Partial: catalog IDs/fields and referenced-price deletion rejection verified with atomic audit writes in batch 34; broader identity/duplicate/rename issues pending, no automatic merge |
| PY-30 | Isolated automated/browser verification | Partial/ongoing: guarded 147 backend tests, 27 identity-pinned synthetic PostgreSQL cases, real original-browser workflows and before/after evidence verified through batch 34; expand with remaining work, live services forbidden |
| PY-31 | Confirmed payment activation and recovery | Partial: atomic confirmation, retry/replay, owner-only callback recovery and approved indefinite-grant holds verified; unattended recovery and operational delivery/reconciliation decisions remain |
| PY-32 | Preserve unused purchased/trial time | Complete for approved rules in batches 14/21: carry forward dated paid/trial time; preserve indefinite grants, block new checkout and hold/recover old purchases without consuming days |
| PY-33 | Validate payment evidence | Complete for application evidence paths in batches 8/9/15/19: signed webhook, checkout/reference/amount/currency/ID verification and concurrent provider-verification/webhook replay; live-provider operational verification separate |
| PY-34 | Expiry without unintended staff-role loss | Complete in batch 2; 18 backend tests and two expired-Reporter browser cases passed |
| PY-35 | Operational readiness and dependency evidence | Pending; production checks outside current scope |
| PY-36 | Accurate progress/documentation/maintainability | Progress record established; ongoing |

## Verified results and batch history

- Starting point: clean master at 76dbd27; backup tip verified unchanged before
  creating the new branch. No comprehensive audit repeated.
- Baseline synthetic database will use existing Egusi/Kwali Market and existing
  `1 bag` fixture, with bag_size left unknown. Fake prices/accounts clearly marked
  by the testing wrapper; no real customers or original database records copied.
- Baseline verified: six negative isolation checks passed (TCP/DNS, credential
  reads, native PostgreSQL, engine alternatives/persistent SQLite, child processes
  and nonlocal listeners; fresh memory DB and empty provider settings allowed).
- Original frontend TypeScript and Vite 5.4.11 build passed (99 modules, 2.01s).
  Original main bundle 315.10kB / 88.84kB gzip; CSS 31.58kB / 7.09kB gzip.
- All 12 original backend tests passed, zero failures/errors/skips, 14.892s.
- Six real-API Chromium browser workflows passed: original homepage/cards, real
  synthetic API/guest boundary/private-source exclusion, original price filters,
  Trial login/plans/history, Admin login/original price form, 375px mobile loading
  with no document overflow. No grade field/input/card label exists. Test harness
  selectors were corrected for existing labels/onboarding/Welcome heading; those
  were checker issues and no application changes were made to resolve them.
- Verified application source matches master before these checks. Fake seed has
  only Egusi and Kwali Market, unit `1 bag` copied from the existing test fixture,
  bag_size=NULL. Source authority: original migration 0006 and watchlist test.
- Browser link: http://127.0.0.1:55446. Fake logins free/trial/paid/reporter/admin
  @example.com, common password PriceYardDemo8!. Preview process ID stored in
  tools/local-test/runtime/preview.pid; server must be alive for link to work.
  Thin notice is testing wrapper only; original application source/CSS unchanged.
- Browser page requests allow only the literal test origin; service workers,
  native sharing/push and external links are disabled in this wrapper. This is
  focused UI/API evidence, not full PWA/provider/VM isolation certification.

### Batch 1 — PY-15

- Two production-source lines changed: successful homepage and Current Prices
  refreshes clear an old error even during automatic refresh. No JSX, CSS,
  wording, fields, units, filtering, prices or subscription/referral rules changed.
- Browser fault/recovery checks reproduced both original defects first, then
  passed after the fix against real local API recovery responses. Timer checks
  invoke the application's registered 60-second callbacks without a minute wait.
- TypeScript/build passed (Vite 2.32s); CSS artifact hash unchanged. Six baseline
  browser workflows passed again. The original 12 backend tests remain the
  unchanged-backend baseline; no backend source changed in this batch.
- Manual check: http://127.0.0.1:55446/__test__/controls — simulate an outage,
  open homepage, restore connection and allow normal refresh with Data saver Off.
  This control page is external test tooling, not a production application feature.
- Harness correction: serialize fixture HTTP requests because a StaticPool memory
  database shares one connection. This avoids test-only concurrent SQLite errors;
  it is not evidence of production concurrency safety. Process guards remain.
- A reused-page Trial/logout/Admin browser check showed a possible existing late
  profile-response race. Independent role fixtures pass; deterministic logout
  verification remains part of PY-18/PY-07. Do not claim logout protection complete.
- Evidence: tools/local-test/evidence/batch-1-*.json. No production/provider access.

### Batch 2 — PY-34

- Subscription expiry/purchase/administration preserves existing Admin/Reporter
  authority. Ordinary paid-user expiry and indefinite manual grants retain their
  existing behavior. Staff authority does not grant paid historical access.
- Replaced short-circuit expiry processing so all applicable accounts are handled,
  not just the first changed subscription. No schema, dates/durations/pricing,
  referral, frontend, wording or design changes in this batch.
- New regression suite reproduced nine failing assertions/subtests across six
  tests before the fix. Afterward all 18 backend tests passed, 17.802s.
- Two real-browser/API workflows passed: expired-trial Reporter and expired-paid
  Reporter both remain Reporter, both have expired subscriptions/history 403,
  and both can open the existing reporting form. Browser assertions use original
  endpoint names and original heading `Report a market price`.
- Manual check: log into http://127.0.0.1:55446 as
  expired-reporter@example.com or expired-paid-reporter@example.com, password
  PriceYardDemo8!. Reporting remains available; full history stays restricted.
- Evidence: tools/local-test/evidence/batch-2-*.json. Restarted only the disposable
  preview to load backend code/new fake account fixtures; no original DB touched.

### Batch 3 — PY-10

- CSV export treats formula-like text as literal text, including leading spacing,
  control characters and BOM. Typed numeric prices, headers, ordinary Unicode,
  CSV quoting and all application screens/fields are preserved. No source record
  is rewritten. No spreadsheet program or external formula was executed.
- Five regression tests reproduced 11 failing assertions/subtests before the
  fix. Current consolidated backend suite has 23 tests; final output recorded in
  tools/local-test/evidence/batch-3-backend-tests.json.
- Real-browser original Admin CSV export/download passed: two synthetic rows,
  original headers and exact numeric prices; private source absent. Guest request
  rejected 401 and Trial rejected 403. No frontend change/build needed.
- Manual check: log into http://127.0.0.1:55446 as admin@example.com with
  PriceYardDemo8!, then open /admin/export and click the existing Download CSV.
- Evidence: tools/local-test/evidence/batch-3-*.json. Existing real spreadsheets
  and customer data were not accessed; real spreadsheet-product compatibility is
  not claimed from string/export checks.

### Batch 4 — part of PY-18

- Ignore superseded account-profile results after logout/account changes. A 401
  from an older token cannot clear a newer login. Keep stored credentials and
  last valid profile/subscription during transient failures; real 401/inactive
  authentication still clears the current account. Background profile refresh
  avoids unmounting existing screens unnecessarily.
- No JSX/CSS/labels/form fields, token lifetime, Remember me defaults, account
  provider flow or subscription/referral policy changed. This is client state
  protection; server revocation still awaits the approved security-storage batch.
- Browser checks reproduced late-profile resurrection and erased login on 503
  before the fix. Three subsequent browser cases passed: logout remains Guest,
  temporary account outage retains the session/reloads without a new password,
  and late old-token 401 preserves a newer Admin login. Delayed responses carry
  real synthetic API data; test-only request tags ensure deterministic ordering.
- TypeScript/build passed (Vite 1.33s, main 315.56kB/89.00kB gzip); CSS artifact
  remains the original index-19youOJ7.css. Original baseline workflows rerun.
- Fixed a second harness-only issue: original PostgreSQL pool_recycle=300 would
  erase a recycled memory database after five minutes. Memory-only guard strips
  those PostgreSQL pool settings; six isolation cases still pass, including a
  new persistence check across connections despite caller-requested recycling.
- Manual: http://127.0.0.1:55446/login — sign into a fake account, log out, then
  sign into another. No saved private account should reappear after logout.
- Owner explicitly approved docs/LOCAL_SECURITY_STORAGE_PROPOSAL.md on 2026-10-16.
  That scope allows internal revocation records only, not new product fields or
  production migration. Evidence: tools/local-test/evidence/batch-4-*.json.
- Follow-up baseline initially hit the existing five-login/minute quota because
  all automated browsers shared localhost. The initially copied batch-4 baseline
  JSON was the earlier passing baseline, not that failed rerun. Replaced with the
  actual current seven-check passing result after separating fabricated client
  identities in the test wrapper. No application rate limit was disabled/changed;
  a new browser check proves five invalid attempts return 401 and the sixth 429.
  All three account regression cases also passed again. Each test context is
  independent; normal browser users retain the real localhost quota.
- Checkpoint 3db1b1d unintentionally included three native browser/Windows cache
  files under a literal %SystemDrive% directory. They are being removed from Git
  tracking without deleting the on-disk files. Browser launch now retains the
  nonsecret SYSTEMDRIVE variable and uses disposable profile/app-data directories;
  the literal cache directory is ignored. Application/business data is unaffected.

### Batch 5 — PY-04; parts of PY-07/PY-09/PY-28

- Implemented only the explicitly approved internal schema: users.auth_version
  and revoked_access_tokens(token_hash, user_id, expires_at, revoked_at). Public
  User response excludes these fields. Original forms, CSS, pricing/referrals,
  14-day trial, Remember me and 90-day access-token lifetime remain unchanged.
- New signed tokens include version and a random identity so logout revokes
  only that credential. Legacy original tokens remain valid at version zero
  until reset/disable/logout; no blanket forced login is introduced.
- Existing logout button clears local state immediately and requests server
  revocation. Password reset atomically claims its link, changes the password,
  increments version and closes outstanding reset links. Disable/re-enable does
  not restore previously issued credentials. Only credential hashes are stored.
- PostgreSQL reset locking always takes user before token rows. Same or distinct
  reset-link races have exactly one winner, without deadlocking. Duplicate
  logout is idempotent. Offline/unreachable backend cannot guarantee revocation;
  JavaScript-readable credential storage remains explicitly unresolved.
- New migration: 0022_login_revocation after original 0021. It adds no market,
  grade, measurement or subscription/referral field. Evidence-losing downgrade
  refuses. It was executed only in fresh marked synthetic PostgreSQL schemas.
- Current backend suite: 29 passed, zero failures/errors/skips, 9.440s. Four
  PostgreSQL cases passed in 5.550s: populated/fresh upgrade with unchanged user,
  subscription/payment/catalog/price/source rows, downgrade refusal, same-link
  and distinct-link reset races, duplicate logout. Wrong hosts/ports rejected;
  every native connection verifies data directory/system identity before writes.
- Test cluster only: tools/local-test/runtime/postgres-revocation, literal
  127.0.0.1:55447, synthetic user priceyard_revocation_test, database
  priceyard_isolated_test. Identity marker is ignored runtime/postgres-marker.json.
  No production URL accepted; TLS key discovery disabled for this loopback fixture.
- Frontend TypeScript/build passed (Vite 1.63s, main 315.67kB/89.04kB gzip; original
  CSS artifact unchanged). Four browser assertions passed using original logout,
  forgot/reset/password-login screens and a separate local-only fake inbox. Seven
  baseline and three account-race checks passed; expired Reporter and Admin CSV
  checks passed again after authorization changes. No real email/provider call.
- Browser reset demo: /forgot-password accepts fabricated @example.com accounts;
  /__test__/inbox shows intercepted local reset links. Fake reset@example.com was
  used by automated tests and now has UpdatedPassword8! until preview restart.
  Other demo account passwords remain PriceYardDemo8!.
- No dependencies installed. Current test environment emits a FastAPI/Starlette
  httpx deprecation warning; it did not fail tests and is operational follow-up.
- Read-only sanitized process check found only guarded local-test Python processes
  for this repository, no original Vite/Uvicorn source watcher using real config.
- Evidence: tools/local-test/evidence/batch-5-*.json. No live DB migration, push,
  merge or deployment. Current completed checklist items: PY-04/PY-10/PY-15/PY-34;
  remaining items include explicitly partial work above, not 36 completed fixes.

### Batch 6 — remaining PY-09; part of transactional user administration

- Serialize privileged user-role/activity changes with a PostgreSQL transaction
  advisory lock. Refresh the target before checking the original last-active-
  Admin rule. Role/subscription changes now use one final commit; avoid expiry
  helper commits that would release the lock before the role change completes.
- Existing standalone subscription administration still commits by default.
  Explicit manual paid/free grants retain their original statuses/dates. No
  schema/field, frontend, business policy or wording change in this batch.
- Six native PostgreSQL cases passed in 7.134s, including concurrent last-Admin
  deactivation and demotion with expired prior trials. Exactly one succeeds and
  one returns 409; one active Admin remains. These validate identified races on
  the marked default-isolation test cluster, not every hosting/isolation setup.
- All 31 backend tests passed, 9.892s, including actual HTTP manual-role behavior
  and sequential last-Admin rejection. Original Users browser screen passed:
  self-deactivation and self-demotion reject, account/role survive reload. Reporter
  expiry browser checks passed again. No frontend rebuild needed.
- Manual: log in as admin@example.com / PriceYardDemo8! at
  http://127.0.0.1:55446/admin/users; attempting to deactivate the sole Test Admin
  must show the existing last-admin error and keep that account active.
- Evidence: tools/local-test/evidence/batch-6-*.json. Five checklist items fully
  verified so far (PY-04, PY-09, PY-10, PY-15, PY-34); other items remain pending
  or explicitly partial. Production still untouched.

### Batch 7 — PY-01; part of PY-02

- Historical date/comparison/direct-ID requests now require the same existing
  history entitlement. Current public records, including their previous-price
  summaries, remain public. A dated request returning the currently public
  record stays public even if its last update is old; no artificial freshness
  policy was added. Outdated records cannot bypass the public-current rule by ID.
- Quality list/detail now use full access, matching the original premium screen.
  Public Possible Meaning/Suggested Action remain unchanged. No frontend, schema,
  wording, prices, fields, measurements, markets or subscription policy changed.
- Six HTTP regression tests reproduced 30 failing assertions/subtests before
  the fix. Initial test fixture had incorrect trial timestamp names, corrected
  to the original model before reproducing those failures. Afterward all 37
  backend tests passed, zero failures/errors/skips, 17.530s.
- Real browser/API checks passed for Guest, Free, Trial, Paid, Reporter, Admin
  and both expired-Reporter fixtures. All alternate historical routes reject
  unauthorized access; original current cards and commodity pages still load;
  entitled accounts see the original history rows and quality section. Corrected
  a checker-only table selector to the existing history-table-view class.
- This reuses the existing latest-record selector so public eligibility cannot
  drift. Its unbounded query cost remains PY-20 work; this batch makes no claim
  of historical pagination/performance completion. No frontend rebuild needed.
- Manual: http://127.0.0.1:55446/history — free@example.com sees the original
  access gate; trial@example.com sees the two fabricated records. Password for
  both: PriceYardDemo8!. Current Prices remains public. Preview restarted with
  fresh fake accounts only. Test-only PostgreSQL remains stopped.
- Evidence: tools/local-test/evidence/batch-7-*.json. Six checklist IDs complete;
  30 remain pending/partial. All commits are local; production is untouched.

### Batch 8 — part of PY-33

- Signed success events must match the recorded integer-kobo amount, NGN,
  success status and valid transaction identity/reference before any credit.
  Invalid shapes return controlled errors; signature format is checked before
  constant-time HMAC comparison. Unknown references/unrelated events stay harmless.
  Recorded purchase amounts remain authoritative; no repricing of old purchases.
- Existing payment tests now use complete fabricated provider payloads, including
  seasonal amount 600000 kobo. Five new HTTP tests reproduced 30 failed assertions
  before this fix. Full suite: 42 passed, 20.168s. After aligning reference/ID
  length bounds to original database columns, all 11 payment tests passed, 5.324s.
- Real browser verified original Dashboard using payment@example.com: wrong
  amount rejects with 422 and remains Free/history 403; valid fabricated event
  grants Active Paid/history 200; replay keeps expiry. Live initiation stays 503
  before and after testing. No money/provider/email connection is involved.
- Separate wrapper controls /__test__/payments invoke the real webhook using
  in-process ASGI transport and a temporary fabricated signing key; ordinary
  provider configuration remains empty. No application UI/schema change/build.
- Paystack public developer documentation consulted read-only, 2026-10-16:
  https://paystack.com/docs/payments/verify-payments/ and
  https://paystack.com/docs/payments/webhooks/ . No account/API service accessed.
- Manual: http://127.0.0.1:55446/__test__/payments explains the fake event buttons
  and original Dashboard login (PriceYardDemo8!). Automated testing already made
  that dedicated fake account Paid; restarting preview restores its Free fixture.
- Activation atomicity, duplicate provider-ID binding, recovery/reconciliation,
  renewal/trial value, and checkout response validation remain explicitly pending.
  Evidence: tools/local-test/evidence/batch-8-*.json. Six IDs complete, 30 partial
  or pending; no production access, push, merge or deployment.

### Batch 9 — parts of PY-31/PY-33/PY-26

- Payment success, subscription activation and sanitized audit now use one
  transaction. Existing standalone subscription/audit helpers still commit by
  default. Activation records the existing subscription.payment_reference field;
  no new schema. Missing subscription preserves the pending purchase for recovery.
- PostgreSQL transaction advisory lock serializes confirmations across workers,
  with refreshed locked payment/user/subscription rows. A provider transaction ID
  cannot credit two local purchases, including different concurrent references.
  No historical payment row is deleted/rewritten by a backfill. This protects
  application confirmation paths; there is no new database uniqueness constraint.
- Ancillary administrator-notification failure cannot undo a saved payment or
  falsely report activation failure. A generic sanitized error is logged; durable
  notification delivery/retry remains PY-21 work, not claimed solved here.
- Five new fault/duplicate tests all failed before the fix. Current full backend
  suite: 47 passed, zero failures/errors/skips, 22.935s. Eight native PostgreSQL
  cases passed, 14.716s, including simultaneous same-payment replay (one success
  audit) and two purchases sharing one provider ID (one 200, one 409).
- Browser payment control now simulates activation failure before valid retry.
  Wrong amount rejects; activation error keeps pending/Free; retry credits; replay
  keeps expiry. Existing Dashboard/history reflect saved access. Live initiation
  stays disabled 503. No frontend layout/build/dependency/schema change.
- Owner approval requested separately for unused paid/trial-time calculations:
  docs/PURCHASE_VALUE_APPROVAL.md. Await response before those dependent changes;
  current prices/durations/trial/referrals/manual-grant behavior remain unchanged.
- Manual: http://127.0.0.1:55446/__test__/payments. Dedicated fake account has
  already been credited by tests; a preview restart reseeds it for another run.
  Evidence: tools/local-test/evidence/batch-9-*.json. Six complete checklist IDs;
  other 30 remain partial/pending. Local-only commits; no production contact.

### Batch 10 — PY-11

- Removed the duplicate created-record cache that overrode newly loaded server
  values. A successful creation updates the existing authoritative list; later
  approvals/corrections/status changes use saved server results after reload.
  Existing forms, labels, selectors, CSS, fields and backend behavior are unchanged.
- Browser reproduced the original bug first: server approved, screen pending.
  After the fix, real API/browser creation, approval, price correction, outdated
  status, rejection and full reload all agree. No record was deleted by this test.
- The original creation schema requires nonempty free-text bag_size; the test
  explicitly supplies "Unknown" for its fabricated record, with existing unit
  "1 bag". No measured weight/grade/new market is invented and no production
  record is touched. Original nullable-size fixture rows remain unchanged.
- TypeScript and Vite build passed (2.51s, main 315.61kB/89.04kB gzip). Original
  CSS stays index-19youOJ7.css, 31.58kB/7.09kB gzip. Backend source unchanged;
  the prior 47-test backend result remains its baseline, not a new rerun claim.
- Checker-only label ambiguity was resolved by selecting the original named
  controls. No product labels were edited to make tests pass.
- Manual: http://127.0.0.1:55446/admin/prices, admin@example.com / PriceYardDemo8!.
  Original record rows should reflect saved approval/correction immediately.
  Synthetic PostgreSQL stopped; browser SQLite preview remains running.
- Evidence: tools/local-test/evidence/batch-10-*.json. Seven IDs complete;
  29 remain pending/partial. Remaining paid/trial-time approval is still pending.

### Batch 11 — further PY-18; part of PY-13

- Existing access labels follow subscription entitlement: an old paid_user role
  alone does not override missing/expired/cancelled access, missing trial end is
  not unlimited access, paid dates stay valid through their existing inclusive
  UTC date. Active end_date=NULL manual grants remain indefinite. No database
  value, price, duration, referral/registration rule or product wording changed.
- Legacy naive trial timestamps are interpreted as UTC, matching the backend's
  existing explicit behavior. Deadline/focus/visibility checks update the access
  gate without page reload. Long timeouts are bounded/rearmed; an effect delayed
  across a deadline rechecks the last active render once instead of looping.
- Eighteen source-level cases reproduced seven original failures, then all 18
  passed. Browser checks verified trial and dated-paid expiry without reload and
  an indefinite manual grant after a simulated year. Browser clock only changes;
  the separate backend expiry tests remain the server-authorization evidence.
- Initial browser expiry checks used Node's Lagos parsing for an offset-less UTC
  timestamp and therefore checked one hour early. This was a checker mistake,
  corrected to explicit UTC. The earlier commentary suspected a timer race;
  the diagnostic mismatch itself was not proof of that product defect. Temporary
  instrumentation removed. Tests run the final seconds near the true deadline.
- TypeScript/Vite passed (3.73s, main 316.55kB/89.31kB gzip, 100 modules). Original
  CSS stays index-19youOJ7.css. Seven baseline browser workflows and three account
  race/outage checks passed during this batch; the final timer safeguard was
  additionally covered by the passing targeted expiry browser checks.
- Testing wrapper adds manual-paid@example.com / PriceYardDemo8! solely to
  demonstrate the existing indefinite-grant behavior. Preview restarted with
  fresh synthetic records; unknown-size administrative test records were reset.
- Manual: http://127.0.0.1:55446/history using trial@example.com, paid@example.com
  or manual-paid@example.com. All retain the original entitlement screens.
  Evidence: tools/local-test/evidence/batch-11-*.json. Seven IDs complete;
  29 remain partial/pending. No production access or deployment.

### Batch 12 — PY-19

- Added an Admin-only FAQ listing for saved hidden and published items. Public
  list/detail still expose only published items. The original Admin screen uses
  that saved data rather than relying on a session-only hidden-record cache.
  Published and hidden items stay in the original sections; no duplicate stale
  row remains after deleting a disposable test draft. All original UI headings,
  text, fields, publication rules and CSS remain unchanged. No schema addition.
- Browser first reproduced hidden draft disappearing from Admin after reload.
  Afterward creation/reload/publish/public-read/hide/reload/delete all passed
  through real synthetic API responses. Only fabricated draft data was deleted;
  no original FAQ or business record was accessed/removed.
- Four new HTTP tests cover saved visibility, public hidden-record exclusion,
  Guest/Free/Paid/Reporter rejection at the Admin route and publication workflow.
  All 51 backend tests passed, zero failures/errors/skips, 27.918s.
- TypeScript/Vite passed (4.26s, main 316.67kB/89.36kB gzip). CSS remains the
  original index-19youOJ7.css. Preview restarted only its in-memory fake database.
  FAQ administrative audit atomicity is separate PY-26 work, not claimed here.
- Manual: http://127.0.0.1:55446/admin/faq, admin@example.com / PriceYardDemo8!.
  Create a hidden fake FAQ and refresh: it remains available. Visitors see it
  only after Publish, and Hide removes it from their public FAQ list.
- Evidence: tools/local-test/evidence/batch-12-*.json. Eight IDs complete;
  28 remain partial/pending. Paid/trial-value business approval still pending.

### Batch 13 — PY-06; part of PY-08

- Validate browser push service destinations and real P-256/authentication-key
  shapes before storage and again before delivery of legacy rows. Unsafe legacy
  rows are preserved and skipped. Requests use TLS, bounded connect/read timeouts,
  no implicit proxy/netrc credentials and no redirects. Logs exclude secret errors.
  No product forms, CSS, notification wording, markets or measurements changed.
- Seven new security tests cover destination/key rejection, recognized browser
  providers, legacy preservation, authenticated storage and mocked transport.
  All 58 backend tests passed, zero failures/errors/skips, 16.577s.
- Browser checks passed: three unsafe destinations rejected with 422, valid fake
  subscription saved and removed with 204, zero external page requests. No real
  notification was delivered; vendor delivery/compatibility remains unverified.
  Known-provider restrictions may require a reviewed update for future providers.
- Fixed test startup only: Windows venv Python launches a child interpreter.
  Verify both exact executable/script/parent identities before stopping the old
  synthetic process; verify literal loopback status and serving PID before success.
  Windows CIM requires local process-metadata permission. Replaced the failing
  Stop-Process host path with verified Process.Kill/WaitForExit. Fresh startup
  passed on resumption (launcher 36836, serving PID 26164); the preview had stopped
  during interruption, so the first resumed browser attempt refused connection.
  Restarted only the synthetic preview and the browser recheck passed.
- Manual: http://127.0.0.1:55446/__test__/push. Separate test controls never
  request native notification permission or contact a delivery provider.
- Evidence: tools/local-test/evidence/batch-13-*.json. Nine application-side IDs
  complete; 27 pending/partial. PY-07 shared-device ownership/cleanup remains open.
- Owner subsequently approved rules 1/2 in docs/PURCHASE_VALUE_APPROVAL.md;
  that approval is recorded for the next batch, not claimed implemented here.

### Batch 14 — approved portion of PY-32

- Active dated renewals append the purchased 30/90 days after the current end
  date. A remaining trial anchors paid expiry after its final UTC date, preserving
  its original timestamps and inclusive paid-date boundary. Expired/free/cancelled
  access starts from today; stale future fields on those states do not grant time.
  Existing start_date remains the confirmation date. Prices, 14-day trial,
  referrals, original frontend and historical successful purchases are unchanged.
- Indefinite manual-grant administration/expiry is unchanged. Payment handling
  for those grants is not fixed by this scope and remains a known pending owner
  decision; do not claim that case or commercial readiness complete.
- Seven new focused tests reproduced seven failed assertions/subtests before
  the fix. Added two real-webhook tests for trial preservation/replay and paid
  renewal audit-failure rollback/retry. Updated the old trial-purchase expectation
  to the approved rule. All 67 backend tests passed, 24.142s, no failures/errors/skips.
- All nine marked native PostgreSQL tests passed, 18.965s, including a new
  simultaneous-two-distinct-purchases case: both successful, two audits and all
  60 paid days retained. Existing replay/duplicate-ID/reset/Admin/migration
  preservation checks passed. Synthetic cluster was stopped afterward.
- Browser original Dashboard verified real local API state for a paid monthly
  renewal (2026-11-15 -> 2026-12-15) and a seasonal trial purchase (trial final
  date 2026-10-30 -> paid final date 2027-01-28). Both keep history access and
  ignore a replay; live payment initiation remains disabled (503). No external
  page requests or provider calls. No frontend change or new build needed.
- Manual: http://127.0.0.1:55446/__test__/purchase-value. Separate fake controls,
  value-paid@example.com / value-trial@example.com, password PriceYardDemo8!.
  Automated checks have already applied those two fake purchases; replay will not
  extend them again. Restarting only the disposable preview reseeds the fixtures.
- Evidence: tools/local-test/evidence/batch-14-*.json. Nine IDs fully complete;
  27 pending/partial, including PY-32's separate indefinite-grant payment decision.

### Batch 15 — further PY-33

- Checkout initialization explicitly requests NGN at unchanged recorded prices.
  Use a fixed Paystack API destination, verified TLS, 3s connect/15s read timeout,
  no implicit environment proxy/netrc credentials and no redirect following.
  Require a 2xx response, a literal boolean success, valid object shape, matching
  locally generated reference and an HTTPS checkout.paystack.com capability URL.
  Unsafe links, malformed bodies, reference mismatches and provider redirects
  return existing controlled errors. Failed purchase rows remain recorded; no
  checkout response grants access. No plan/reference format, UI or schema change.
- Seven new HTTP tests reproduced 24 failed assertions/subtests before the fix.
  All 74 backend tests passed, 43.435s, zero failures/errors/skips. Both plan
  amounts, recorded pending/failed states, provider timeouts and authorization
  boundaries are covered with mocked transport, never an actual provider call.
- Browser used original Dashboard/buttons: both monthly/seasonal unsafe checkout
  replies rejected 502 with existing toast, retaining Dashboard and Free access.
  A valid fake response drives the existing navigation, intercepted and fulfilled
  locally before external connection. Checkout itself still grants no access.
  Disabled the fake provider afterward; normal isolated initiation returns 503.
- Manual: http://127.0.0.1:55446/__test__/checkout. Enable the unsafe-link fixture,
  sign into free@example.com / PriceYardDemo8!, try an original upgrade button,
  then disable the fixture. Valid checkout navigation is automated-only here.
- Paystack API contract consulted read-only on 2026-10-16:
  https://paystack.com/docs/api/transaction/#initialize . No account/API accessed.
  Deployment requiring an outbound proxy or a future checkout host needs separate
  reviewed configuration/compatibility verification. Live-provider delivery and
  reconciliation are not claimed complete. No frontend rebuild needed.
- Evidence: tools/local-test/evidence/batch-15-*.json. Nine IDs fully complete;
  27 pending/partial. Original master/backup remain preserved; commits local only.

### Batch 16 — PY-17

- Commodity results belong to their requested route. Ignore superseded success,
  error and loading callbacks; clear intelligence on commodity/account/access
  changes. One failed intelligence request no longer discards other successful
  sections. Report its existing API error through the existing error box.
  Original component layout, labels, CSS, fields, price units and policies remain.
- Five browser checks reproduce the old behavior and pass afterward: delayed
  prices, delayed errors, independent-section success, visible failure and delayed
  old-commodity intelligence. The nonexistent route used for navigation inserts
  no commodity or market. Delayed prices originate from the real synthetic API;
  outage/intelligence response fixtures are explicitly fabricated in the browser.
- The first checker attempted Playwright route.fetch, which the Node transport
  guard correctly denied before network access. Replaced that with browser-origin
  synthetic API capture; no guard was relaxed. A later checker read empty section
  headings before responses settled; it now waits for the actual success/error
  contents. That checker timing failure was not another application defect.
- TypeScript/Vite passed (5.63s, main 317.31kB/89.61kB gzip). Original CSS remains
  index-19youOJ7.css, 31.58kB/7.09kB gzip. Backend unchanged: prior 74-test result
  remains its baseline, not a new rerun. Seven baseline browser workflows passed,
  including original cards/filters/plans/Admin form, mobile overflow and rate limit.
- Manual: http://127.0.0.1:55446/commodities/Egusi. Original detail layout loads
  for guests; trial@example.com / PriceYardDemo8! retains full-access sections.
- Evidence: tools/local-test/evidence/batch-16-*.json. Ten IDs complete;
  26 remain pending/partial. No production services/data or new dependencies.

### Batch 17 — further PY-07

- An endpoint URL alone no longer transfers another account's notification
  subscription. Require matching device public/authentication keys, comparing
  decoded bytes in constant time so equivalent base64 padding remains compatible.
  Legitimate shared-device transfer and the current owner's key refresh still
  work. Other accounts cannot remove the subscription. Invalid legacy rows are
  preserved and cannot be claimed using replacement keys.
- Lock existing rows while checking ownership. Concurrent first registrations
  recover only the existing unique-endpoint conflict in a savepoint, then apply
  the same ownership check. No ownership overwrite, duplicate row or raw 500.
  No schema, product field, UI, token/session-duration or notification policy change.
- Five new HTTP tests reproduced three original failures. Full backend suite:
  79 passed, 45.238s, zero failures/errors/skips. Ten marked native PostgreSQL
  cases passed, 20.742s, including two simultaneous registrations with different
  secrets: exactly one success, one 409 and the winner's original keys preserved.
- Browser separate notification tool passed real synthetic API storage,
  endpoint-only rejection, legitimate transfer, owner-only removal and cleanup.
  Zero external page requests or real notifications; no native permissions used.
  Original application login/session is unaffected by the helper's fabricated
  temporary API logins. No frontend source change/build in this batch.
- Manual: http://127.0.0.1:55446/__test__/push, click Check device ownership
  protection. Existing login rate limits remain enforced. No keys/tokens printed.
- Evidence: tools/local-test/evidence/batch-17-*.json. Ten IDs complete;
  26 pending/partial. Logout push cleanup and JavaScript token storage remain
  separate PY-07 work; this does not claim complete shared-device safety.

### Batch 18 — further PY-07

- Existing Logout clears account state immediately, then makes a best-effort
  cleanup of only the current browser subscription using the existing unsubscribe
  API before revocation. No VAPID configuration/new permission is needed to find
  an already-existing subscription. Other subscribed devices stay unchanged.
- Worker/native/server cleanup gets at most one second before revocation is
  attempted, even if cleanup hangs or fails. Discard late worker lookups after
  timeout or another login, avoiding changes to a new session's device. Existing
  token lifetime, Remember me, UI/CSS and all business policies remain unchanged.
  No new endpoint, request field, schema/storage or backend source change.
- Three browser scenarios were checked before and after: ordinary cleanup,
  native unsubscribe failure and a hung lookup released after a new login.
  Normal/failure cases remove the current server subscription, preserve another
  device and revoke the old JWT (401). A timed-out lookup still revokes the JWT,
  then leaves the late device/new session alone. Native calls are local mocks;
  real provider unsubscribe/delivery is not claimed verified.
- Four existing logout/reset browser checks passed, including original forms,
  fake inbox, old-login revocation, new password and link single use. All three
  account race/outage checks passed. One older checker initially timed out while
  waiting for a transient Login heading after logout. Original Layout finishes
  on the homepage; fixed the checker to await that stable existing destination.
  No product navigation change was made to satisfy the check.
- TypeScript/Vite passed (5.50s, main 318.04kB/89.79kB gzip). Original CSS remains
  index-19youOJ7.css. Backend unchanged: 79-test backend and ten-case PostgreSQL
  results from batch 17 remain their verified baseline, not new rerun claims.
  The marked PostgreSQL cluster is stopped; synthetic SQLite preview is running.
- Limits: offline/tab termination/browser API failure cannot guarantee server or
  provider cleanup/revocation. A timed-out lookup deliberately preserves that
  subscription. JavaScript-readable tokens remain a separate unresolved concern.
- Manual: http://127.0.0.1:55446/login. Sign into a fabricated account and use
  the original Logout button; account state clears immediately. Provider-native
  cleanup requires the automated mock checks here, not live notification access.
- Evidence: tools/local-test/evidence/batch-18-*.json. Ten IDs complete;
  26 pending/partial. Preview restart in batch 17 reseeded all payment fixtures,
  so /__test__/purchase-value is ready for a fresh manual demonstration. The reset
  test account now uses UpdatedPassword8! until the next disposable restart.

### Batch 19 — PY-18/PY-33; further PY-31/PY-08

- Owner-only POST /payments/{reference}/verify looks up the recorded purchase
  before any provider request; Guest denied and other/unknown references 404.
  Fixed HTTPS Paystack verification destination, no redirects/environment proxy,
  verified TLS and 3s connect/15s read timeouts. Check response shape, reference,
  integer kobo, NGN, transaction ID/status and saved plan; never trust callback
  query parameters as payment evidence. Pending/failed/unconfirmed provider
  states do not remove trial time or alter saved payment/history records.
- Confirmed evidence reuses the webhook transaction/locks/audit/replay protection.
  Can recover a failed-initialization record from a confirmed payment. Already
  credited purchases do not contact the provider or extend access a second time.
  Ten requests/minute per authenticated customer/network, preventing a shared
  carrier NAT from combining different customers into one quota. Original auth
  limits, prices, durations and 14-day trial remain unchanged. No schema change.
- Original callback markup, Thank you heading, conditional guidance and Dashboard
  link remain unchanged. Up to four verification attempts at two-second intervals;
  confirmed payment refreshes the current account, including an in-flight check
  finishing after Go to Dashboard. Superseded credentials cannot start refreshes.
  Browser title uses existing term Payment until confirmed, then Payment received.
- Six isolation checks passed on resumption. Eight new HTTP tests initially
  failed 24 assertions because recovery did not exist. Full backend: 87 passed,
  25.271s. Final customer/network quota refinement: eight focused tests passed,
  1.050s, including independent quotas for customers sharing an address.
- Original-browser before check reproduced no recovery and an unverified success
  title. Afterward: four bounded pending attempts, wrong-amount rejection, recovery
  without webhook, immediate paid Dashboard/history, unchanged expiry on replay,
  and conflicting callback reference rejection all passed. Three account race/
  outage browser regressions passed. Fake provider transport only; zero live calls.
- Eleven marked PostgreSQL cases passed, 12.691s, including simultaneous provider
  verification/webhook: one credit and one audit. Cluster stopped afterward.
  TypeScript/Vite passed (2.05s, main 318.62kB/90.01kB gzip); original CSS artifact
  remains index-19youOJ7.css, 31.58kB/7.09kB gzip.
- Manual: http://127.0.0.1:55446/__test__/verification, verify@example.com /
  PriceYardDemo8!. Automated check already credited this dedicated fabricated
  purchase; replay cannot add time again. Preview restart reseeds it if needed.
  Disable the test fixture afterward. No real money/provider/customer involved.
- Contract source consulted read-only: https://paystack.com/docs/payments/verify-payments/
  and https://paystack.com/docs/api/transaction/#verify (2026-10-16).
  No live-provider compatibility/delivery claim, unattended reconciliation job,
  refund/chargeback rule or indefinite-manual-grant payment decision is introduced.
- Evidence: tools/local-test/evidence/batch-19-*.json. Twelve IDs complete;
  24 pending/partial. Progress and commits stay local; master/backup preserved.

### Batch 20 — further PY-05/PY-26

- New registration, seven-day referral extension and sanitized audit commit
  together. Reward/audit failure rolls back the account and reward, allowing a
  safe retry instead of reporting failure after creating a partial account.
  User uniqueness conflict remains 409 and cannot issue another reward.
- Lock referrer user then subscription before inserting a referred child,
  preventing lost concurrent days and FK key-share lock-upgrade deadlocks. No
  intermediate expiry/reward commit releases those locks. Standalone reward
  helper retains its default commit behavior. Existing qualification, no cap,
  registration-time seven-day reward, 14-day newcomer trial and staff roles remain.
- Four new tests reproduced three original failures. Full backend: 91 passed,
  27.717s, no failures/errors/skips. Thirteen marked PostgreSQL cases passed,
  16.030s: distinct registrations retain both rewards; duplicate concurrent
  registration creates/rewards/audits once, without deadlock. Other security and
  payment-race cases remain passing. Cluster is still isolated for next-batch tests.
- Browser used the original referral URL, registration/password form and Dashboard:
  newcomer gets exactly 14 trial days; referrer gains exactly seven days and one
  referral. Original labels/layout unchanged; no frontend source/build change.
  Only fabricated user data was added. No provider or external page request.
- Manual: http://127.0.0.1:55446/register?ref=TESTREFERRER, use a new fabricated
  @example.com email. Referrer is referrer@example.com / PriceYardDemo8!, and its
  original Dashboard shows the reward. Automated check already added one referral.
- Policy-based abuse caps/verified-email qualification/first-payment rewards were
  not introduced; they require a separate owner decision. Evidence:
  tools/local-test/evidence/batch-20-*.json. Twelve IDs complete, 24 partial/pending.
- Owner explicitly approved the exact indefinite-grant checkout/held-payment scope
  in docs/PURCHASE_VALUE_APPROVAL.md during this batch. Implement it next (batch 21);
  it is not awaiting approval and is not claimed implemented by this checkpoint.

### Batch 21 — approved indefinite-grant scope, PY-32; further PY-31/PY-26

- Checkout is blocked before provider contact/new purchase creation for active
  indefinite grants. Confirmed old purchases retain reference/provider ID and one
  sanitized review audit, remain pending activation and consume no paid days.
  Grant access remains unchanged. Deliberate grant resolution permits exact-once
  retry/activation. Conflicting provider IDs cannot overwrite held evidence.
- Eight HTTP tests reproduced seven failures before implementation. The first
  checkout checker used an incomplete provider stub, then was corrected to a
  complete successful fake checkout response before recording final before-results.
  All 99 backend tests passed, 22.382s; fourteen marked PostgreSQL cases passed,
  14.644s, including concurrent hold/review-once and recovery/credit-once.
- Original-browser workflow passed: checkout 409, confirmed purchase 409/held,
  grant remains active/indefinite with history access, replay preserves one review
  audit/receipt. The original Admin Subscriptions selector deliberately resolves
  only this fabricated grant to Free; retry grants the recorded 30 days once and
  later replay preserves expiry. No provider/email/real-customer contact.
- Manual: http://127.0.0.1:55446/__test__/manual-review, manual-paid@example.com /
  PriceYardDemo8!. The automated test deliberately resolved this fake grant and
  credited the fake purchase; restart the disposable preview to reseed before
  checking the initial indefinite/held state. Existing Audit logs show
  payment.review_required with the recorded reference/provider ID. Those are
  existing database fields; review action is in the existing audit table.
- No new schema, fields, product screen, prices, durations, automatic refund or
  historical backfill. Historical successful payments remain unchanged. Native
  PostgreSQL cluster stopped; SQLite preview remains running. No frontend rebuild
  needed; the last original CSS artifact remains unchanged.
- Evidence: tools/local-test/evidence/batch-21-*.json. Thirteen IDs complete;
  23 pending/partial. All approved purchased-time rules now implemented; unattended
  recovery/operational refund decisions remain separate PY-31/PY-35 work.

### Batch 22 — further PY-16

- An older refresh cannot overwrite applied filters. Background refresh uses the
  last applied selection, leaving draft controls unchanged until Apply, and skips
  a pending foreground request. Superseded/unmounted requests cannot update state.
- Before/after browser checks reproduced and fixed all three defects; foreground
  loading also finishes. Checker corrections: use original select elements (their
  implicit labels include option text), hold both ticker/list requests, and wait
  for new fetches/rendering rather than the one-time networkidle load milestone.
  Those were test corrections, not application features or markup changes.
- Original Home/Prices outage recovery and seven baseline workflows passed,
  including original plans/Admin form, Guest source privacy and 375px overflow.
  TypeScript/Vite passed, 6.41s; JS 318.88kB/90.11kB gzip. Original CSS artifact
  index-19youOJ7.css remains identical, 31.58kB/7.09kB gzip. No backend change.
- Manual: http://127.0.0.1:55446/prices. Select Down, click Apply (the synthetic
  current row is Up, so no match), then Clear to restore Egusi/Kwali Market.
  Automated checks cover delayed response/timer races that are hard to time by hand.
- Evidence: tools/local-test/evidence/batch-22-*.json. Thirteen IDs complete;
  23 partial/pending. Local only; native PostgreSQL remains stopped.

### Batch 23 — further PY-20

- Select the latest approved record per existing commodity/market pair using a
  database window rank, then apply outdated/movement exclusions. Existing date,
  search, active-catalog and timestamp/ID tie rules remain identical. No quantity
  inference, new fields/index/migration, history deletion or response truncation.
- Before: one card hydrated 201 prices. After: one price object, with all 201
  historical records retained and readable. Six focused tests passed, 1.879s;
  full 105 backend tests passed, 121.755s. Concurrent focused notification testing
  overwrote the shared runtime report before copying; the full-suite artifact
  explicitly identifies its source as the completed terminal summary.
- Fifteen pinned PostgreSQL cases passed, 68.981s, including 151 retained rows,
  one hydrated current row, movement/outdated/date rules and all security/payment
  races. Initial new native date assertion compared local-zone hour with UTC;
  corrected the checker to normalize the returned timestamptz. Product unchanged.
- Seven baseline and eight account/access browser cases passed: original cards,
  filters, detail/history boundaries, confidential-source exclusion, plans, Admin
  form and mobile layout. No frontend rebuild/change in this batch.
- Manual: http://127.0.0.1:55446/prices; trial@example.com / PriceYardDemo8!
  can still open original Price History. No new pagination or hidden history cap.
- Evidence: tools/local-test/evidence/batch-23-*.json. Thirteen IDs complete,
  23 partial/pending. Native PostgreSQL shutdown's 20s wait timed out, but a
  subsequent pg_ctl status verified no server running. Preview remains local.

### Batch 24 — PY-21 identified independent-channel defect

- Failed email no longer skips the same customer's existing push/WhatsApp paths.
  Existing watch matching, target conditions, active-user check, per-user
  deduplication, email-count return value and best-effort policy remain unchanged.
  No new delivery channel, subscription rule, queue, schema or delivery guarantee.
- One of five focused tests reproduced the original defect; all five passed
  afterward, 31.291s. All 107 backend tests passed, 89.534s. Email, push and
  WhatsApp failures are independently simulated; later users/channels still run.
- Browser: original trial Watch button creates the watch; original Admin create/
  approve form publishes the fabricated price. A forced email failure still
  records push and WhatsApp attempts, approval returns 200 and survives reload,
  and the current-price API shows it. Original fields/layout unchanged.
- Test wrapper /__test__/alerts explicitly enables fake transports only around
  approval requests, records attempts and rejects unknown fabricated recipients;
  default is disabled. It is separate from the product and was disabled after
  testing. Trial test fixture has a fabricated phone; no real recipient/service.
- Evidence: tools/local-test/evidence/batch-24-*.json. Fourteen IDs complete;
  22 partial/pending. Real delivery, durable retries/provider outages still require
  operational work; no such production capability is claimed by this local test.
- Manual: http://127.0.0.1:55446/prices. Existing appearance is preserved; the
  automated notification evidence covers the invisible channel-failure behavior.

### Batch 25 — further PY-26/PY-28; price-save reliability

- Price create/edit/approve/reject/mark-outdated flush inside one transaction with
  their sanitized audit, then commit together. Audit/commit failures roll back;
  no alert is attempted for failed changes. Existing service default commit
  behavior remains available to other callers. No schema or deletion-rule change.
- Editing/approval/rejection/outdated routes lock and reload the price row before
  taking the old snapshot. Concurrent edits retain an ordered, continuous audit
  trail. Existing private source exclusions apply to every snapshot. Notifications
  remain after commit; a best-effort query/delivery error cannot falsely report
  a saved approval/correction as failed. Log message contains no source/secret.
- Four focused HTTP tests reproduced six failing assertions before implementation;
  all passed afterward, 0.442s. All 111 backend tests passed, 49.894s. Sixteen
  pinned PostgreSQL cases passed, 20.296s, including concurrent price edits and
  all prior security/payment races. Native cluster stopped after verification.
- Original Admin browser create/approve/correct/outdated/reject/reload passed,
  plus five matching audit records and continuous old/new state. Notification
  browser regression also passed through original Watch/Admin controls. Initial
  audit check compared decimal text formatting (209000 vs 209000.00); corrected
  checks to compare numeric values, preserving existing stored snapshot formats.
- Manual: http://127.0.0.1:55446/admin/prices, admin@example.com /
  PriceYardDemo8!. Only fabricated records are present. Original Audit logs show
  the price actions. No design, terminology, prices, durations, measurements,
  historical source records or production data changed.
- Evidence: tools/local-test/evidence/batch-25-*.json. Fourteen IDs complete,
  22 partial/pending; broader Admin writes and operational checks remain open.

### Batch 26 — further PY-08/PY-27

- Preserve the existing 2MB decoded screenshot boundary and accepted formats;
  reject excessive encoded length before slicing/allocating decoded content.
  Boundary-sized original payload remains valid; just-over-limit remains invalid.
- Invalid/replaced/removed selections clear prior attachment state immediately;
  a slower obsolete FileReader cannot overwrite the last selection. Successful
  submission invalidates unfinished reads. Original JSX, labels and CSS unchanged.
- Five focused tests reproduced one pre-decode failure, then passed in 0.079s.
  All 116 backend tests passed, 49.266s; seventeen marked PostgreSQL cases passed,
  36.942s, including feedback image/text preservation and hidden publication state.
  First failing mock assertion printed the fabricated base64 argument; simplified
  the checker to report only the call count. No secret or real screenshot involved.
- Browser before/after: invalid replacement clears attachment, does not submit the
  prior image, last-selected file wins, original form still saves. All four passed.
  TypeScript/Vite passed, 2.01s; JS318.97kB/90.15kB gzip. Original CSS artifact
  index-19youOJ7.css remains identical, 31.58kB/7.09kB gzip.
- Manual: http://127.0.0.1:55446/feedback, trial@example.com / PriceYardDemo8!.
  Attach a small test image, then choose one over 2MB: the old attachment must
  disappear and the original size error appears. No live recipients/providers.
- Evidence: tools/local-test/evidence/batch-26-*.json. Fourteen complete,
  22 partial/pending. No schema, prices, policy or production changes. Synthetic
  PostgreSQL remains running for the next security batch; stop it before final.
- Owner responded to the Google-linking decision during this batch and authorized
  the recommended safe option. Scope/compatibility recorded in the approval doc;
  it remains pending implementation and must not be presented as finished here.

### Batch 27 — PY-03; further PY-08/PY-29

- Owner authorized the recommended secure/friendly Google linking option. An
  unmatched Google subject cannot attach to/replace an existing email account;
  controlled 409 explains the original password/reset route. Already-linked
  subjects continue, including when Google's email changes; no account merge,
  history rewrite or automatic unlink. New users retain the original 14-day trial.
- Require a real verified-email boolean, bounded nonblank subject and valid email
  from verified claims. Token input bounded to 16KiB. Existing Google library still
  verifies signatures/audience/issuer/expiry. Certificate transport uses the fixed
  Google URL, verified TLS, no redirects/proxy inheritance and 3s/10s timeouts.
  Provider outages return sanitized 503; invalid authentication returns 401.
- Concurrent first sign-ins recover a unique-conflict winner by proven subject
  only; different subjects sharing an email cannot claim the existing identity.
  Remove unnecessary post-commit refresh to avoid false failure after account save.
  No new fields, screen, pricing, referral qualification or session policy.
- Ten before tests reproduced sixteen failures/eight errors. Malformed verified
  claims are synthetic robustness cases, not proof of Google issuing such tokens.
  After: ten focused passed, 3.367s; all 126 backend passed, 61.323s. Real installed
  verification library tested against ephemeral RSA-signed tokens/certificate
  responses for bad signature/audience/issuer/expiry; no provider contact.
- Twenty pinned PostgreSQL cases passed, 45.246s: simultaneous same-subject login
  yields one account/trial; different-subject email collision denied; existing paid
  account, binding, password, role and auth version preserved. Other races pass.
- Six browser checks passed: collision/password fallback, linked and new Google
  accounts in original Dashboard/history/plans, unverified denial, controlled
  outage, and live Google disabled. Fake verified responses only. Real Google
  popup/button is intentionally not exercised with a live client/provider.
  Checker corrections used the existing numeric subscription URL and omitted
  private auth_provider from public UserResponse; product API fields unchanged.
- Evidence: tools/local-test/evidence/batch-27-*.json. No frontend change/build.
  Manual original password login: http://127.0.0.1:55446/login. Fabricated Google
  API controls /__test__/google-mode are disabled after automated checks.
- Contract reference (read-only):
  https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
  consulted 2026-10-16. Fifteen IDs complete; 21 partial/pending. Native synthetic
  PG remains running for the next batch; production/master/backup untouched.

### Batch 28 — PY-16 identified navigation/history scope

- Current-price query parameters update the original commodity/market controls
  on native navigation and invalidate the prior request. Apply/Clear behavior,
  existing URL parameter names and filter markup remain unchanged.
- History accepts only the latest request's rows/error/loading result for the
  active entitlement/token. Metadata lookups ignore obsolete/unmounted results;
  no history-pair request is made without the existing full-access entitlement.
  Existing roles, quantity rules and complete historical data remain unchanged.
- Four before/after browser checks reproduced/fixed query navigation, obsolete
  URL errors, old history rows and old history errors. History overlap was forced
  with two native form events; normal disabled buttons already prevent most
  accidental duplicates. No broader ordinary double-click failure is claimed.
- Four previous current-filter checks and eight Guest/Free/Trial/Paid/Reporter/
  Admin/expired-role browser cases also passed. TypeScript/Vite passed, 5.67s;
  JS319.45kB/90.35kB gzip. Original CSS artifact index-19youOJ7.css unchanged.
- Frontend-only batch; latest unchanged backend evidence is 126 tests/twenty
  pinned PG cases from batch 27, not claimed rerun here. PG remains running for
  the next backend batch. Evidence: tools/local-test/evidence/batch-28-*.json.
- Manual: http://127.0.0.1:55446/prices?commodity=Egusi&market=Kwali+Market;
  original controls match the URL. Trial login still opens original Price History.
  Sixteen IDs complete; twenty partial/pending. No production or schema change.

### Batch 29 — PY-22; further PY-20 (2026-10-17)

- Fourteen original cards, labels, rendering and metric definitions preserved.
  Replace nine list downloads with Admin-only GET /admin/summary. One read-only
  aggregate statement uses one PostgreSQL snapshot, hydrates no entities and
  returns no customer/source/screenshot/payment rows. No database columns,
  customer-entry fields, pagination cap, history deletion or migration.
- Reuse the unchanged current-price ranking statement for the latest count.
  Catalog counts still include inactive entries, active users still means the
  existing account-active flag, outdated includes all statuses, revenue remains
  the original successful-payment sum. Seven-day window unchanged, now calculated
  with the server clock. Trial count reflects existing expiry rules without writes;
  ordinary authentication/subscription workflows continue handling expiry.
- Five focused tests passed, 1.161s; all 131 backend passed, 29.098s. Checks cover
  all fourteen values, denied Guest/non-Admin, empty database, exact seven-day
  boundary, one SQL statement, no model hydration and unchanged stored rows.
  Before unit failures reflected an aggregate endpoint not yet implemented; the
  actual before-browser performance finding was nine full-list requests.
- Twenty-one pinned PG cases passed, 24.835s, including the aggregate statement
  over 101 retained historical prices, feedback and original-price purchases.
  Local cluster's startup wait expired during automatic recovery from an earlier
  interrupted session; log then confirmed ready and identity-pinned suite passed.
  No production connection or destructive recovery command was used.
- Browser before/after preserves fourteen labels/values, reduces list requests
  9 -> 0 and uses one summary request. Forced summary outage shows the existing
  error; reload restores all cards. No new UI controls. TypeScript/Vite passed,
  3.08s; JS318.72kB/90.18kB gzip; original CSS index-19youOJ7.css unchanged.
- Manual: http://127.0.0.1:55446/admin, admin@example.com / PriceYardDemo8!.
  Evidence: tools/local-test/evidence/batch-29-*.json. Seventeen IDs complete,
  nineteen partial/pending. Native synthetic PG is running for the next batch.

### Batch 30 — further PY-26/PY-28 (2026-10-17)

- Admin user and subscription changes, linked role/access state, login security
  counter and both sanitized audits now commit together or roll back together.
  Trial/paid cleanup cannot commit ahead of a failed Admin change. Lock User then
  Subscription, matching payment/security writers; preserve the existing global
  last-active-Admin guard. No new schema, field, UI, grant or expiry policy.
- Five focused tests reproduced five before failures (0.566s), then passed (0.426s).
  All 136 backend tests passed, 26.595s. Preserve original inactive-account 403;
  after reactivation an old token remains rejected with 401, while original
  password works and staff authority/indefinite manual grants remain unchanged.
- Twenty-three pinned native PG cases passed, 26.694s: a failed second audit
  rolls back user, subscription, revocation and first audit; simultaneous status
  edits retain continuous old/new snapshots. Prior last-Admin/payment races pass.
  First PG checker run used two fabricated referral codes exceeding the existing
  twelve-character column; fixed the synthetic codes, not the application schema.
- Browser original Users role/deactivate/activate and Subscriptions status controls
  pass, with six sanitized audits and fresh-password recovery. Checker initially
  matched both existing toast and success box; scoped the selector and reseeded
  only the synthetic memory database. Dashboard regression still preserves all
  fourteen cards, one summary request, no list downloads and outage recovery.
- Frontend unchanged; no rebuild needed. Manual: http://127.0.0.1:55446/admin/users,
  admin@example.com / PriceYardDemo8!. Evidence: batch-30-*.json. Seventeen complete,
  nineteen partial/pending; remaining Admin audit transactions are still partial.

### Batch 31 — further PY-13/PY-27 (2026-10-17)

- Original Admin create and optional correction date/time inputs now convert
  browser-local time to UTC ISO, exactly as the existing Reporter form does.
  Lagos 15:30 sends 14:30Z; UTC 15:30 sends 15:30Z. Blank correction stays omitted.
  No timestamp backfill, historical rewrite, day-filter boundary change, new
  measurement, Grade field, form label, styling or database migration.
- Actual before/after browser checks cover both Admin forms in Africa/Lagos and
  UTC, saved values after reload, pending status and unchanged Reporter conversion.
  Original Admin create/approve/correct/outdated/reject/reload regression passes.
  Initial checker used the wrong existing Reporter heading; corrected the checker
  before recording before/after evidence, without changing product wording.
- TypeScript/Vite passes, 1.65s, 100 modules; JS318.84kB/90.20kB gzip. Original
  index-19youOJ7.css unchanged. Four focused backend price/audit tests pass, 1.261s;
  latest full unchanged backend remains 136 tests from batch 30, not rerun here.
- Twenty-four pinned native PG cases pass, 28.308s: UTC create/correction survives
  expiration/reload, keeps both audit records and preserves the complete other
  historical row. Prior security/payment/access races remain passing.
- Manual: http://127.0.0.1:55446/admin/prices, original Update date/time fields;
  admin@example.com / PriceYardDemo8!. Evidence: batch-31-*.json. Seventeen IDs
  complete, nineteen partial/pending. Nigerian calendar-day filter semantics and
  broader legacy price display remain open; no unapproved historical reinterpretation.

### Batch 32 — further PY-20 (2026-10-17)

- Original history filter choices now use a protected name-only DISTINCT query
  instead of a second download of every approved historical price. Same active
  catalogs, approved status and inclusion of outdated/history-only pairs as the
  original full-history query. Original metadata effect cleanup retained.
- Internal /price-updates/history/pairs requires the same full-access entitlement
  as history. It returns only existing commodity/market names, with no private
  sources, prices, new customer-entry fields or schema. Actual filtered history,
  table/chart/card markup, catalog ordering and historical records unchanged.
- Four new backend tests cover exact equivalence, outdated rows, duplicate pairs,
  inactive/empty catalogs, one query/no ORM hydration and unchanged stored history.
  Existing access matrix extended to the metadata URL. All 140 backend tests pass,
  28.268s; twenty-five pinned PG cases pass, 36.378s, including 101 retained old
  outdated prices producing one metadata pair without model hydration or writes.
- Browser before/after: unfiltered history downloads 1 -> 0; one filtered history
  request retained, one compact metadata request added. Original market options
  and all matching rows preserved. Four navigation/overlap regressions and eight
  Guest/Free/Trial/Paid/Reporter/Admin/expired-role cases also pass.
- TypeScript/Vite passes, 3.32s, 100 modules, JS318.84kB/90.21kB gzip. Original
  index-19youOJ7.css unchanged. Manual: http://127.0.0.1:55446/history after logging
  in as trial@example.com / PriceYardDemo8!. Evidence: batch-32-*.json.
- Seventeen IDs complete; nineteen partial/pending. Full history itself remains
  unpaginated to preserve existing complete charts/exports pending a compatible
  implementation; no data is silently capped. Next: other atomic Admin writes.

### Batch 33 — further PY-26/PY-28 (2026-10-17)

- Existing FAQ create/edit/publish/hide/delete now save with their sanitized
  audit in one transaction. Failure rolls back both, including a failed delete
  restoring the FAQ. Existing-row actions lock and refresh the row before taking
  the old snapshot, preserving continuous trails across simultaneous edits.
- Keep original hidden-on-create, public list/detail boundaries, existing action
  permissions, fields, content validation, deletion control and frontend unchanged.
  Service default commits remain compatible; routes explicitly defer until audit.
  Remove unnecessary post-commit refresh that could falsely report a saved failure.
- Three focused before tests reproduced five audit-failure defects (0.405s), then
  all passed (0.460s); all 143 backend tests pass, 34.004s. Coverage includes each
  action's rollback, final-commit failure, public visibility and five audit snapshots.
- Twenty-six pinned native PostgreSQL cases pass, 32.686s: failed FAQ delete loses
  neither record nor history; simultaneous edits keep continuous old/new snapshots.
  Prior password/logout/last-Admin/payment/referral/price/status cases remain passing.
- Browser original create/edit/publish/hide/delete/reload controls pass. Hidden
  content stays private; five audit records match successive saved states. Only
  a newly fabricated FAQ is deleted. No application frontend changes or rebuild.
- Manual: http://127.0.0.1:55446/admin/faq, admin@example.com / PriceYardDemo8!.
  Evidence: batch-33-*.json. Seventeen IDs complete, nineteen partial/pending;
  PY-26 remains partial for other Admin writers. No production/schema changes.

### Batch 34 — further PY-26/PY-28/PY-29 (2026-10-17)

- Original commodity and market create/edit/delete now share a transaction with
  their sanitized audit. Failure rolls back both; row locks refresh existing
  records before snapshots, preserving ordered trails across concurrent edits.
  Service default commits and existing validation/duplicate-name behavior retained.
  No new catalog entries, identity merge, schema, fields, UI or deletion policy.
- Four focused tests reproduced six before audit failures (0.896s), then passed
  (1.366s); all 147 backend tests pass, 85.656s during parallel local verification.
  Original actions/permissions and inactive/public visibility remain unchanged.
- Twenty-seven pinned native PG cases pass, 54.939s: failed catalog audit rolls
  back edits, simultaneous edits keep continuous snapshots, original referenced
  deletion returns 409 and complete historical price rows/IDs remain unchanged.
  Prior security/payment/referral/FAQ/status/time/history cases remain passing.
- Browser original commodity/market Edit/Save/Delete controls pass. Only existing
  synthetic descriptions are temporarily changed then restored. Original names,
  IDs and fields remain; referenced deletion stays denied; all historical price
  values survive; four continuous audits recorded. No new market/commodity added.
  Checker initially matched an exact textarea label that included its saved text;
  switched to its existing name attribute and reseeded only the synthetic preview.
  Product frontend was unchanged. No rebuild needed.
- Dashboard regression still matches all fourteen original labels/totals, zero
  list downloads, one summary request and outage/reload recovery. Manual local
  preview: http://127.0.0.1:55446/login, admin@example.com / PriceYardDemo8!;
  inspect Admin Dashboard, Commodities or Markets using the original navigation.
- Evidence: batch-34-*.json. Seventeen IDs complete, nineteen partial/pending.
  Native synthetic PostgreSQL was stopped cleanly after offline system-identity
  verification; pg_ctl status reports no server running. Browser preview remains
  synthetic-only, launcher 65012 / serving PID 64184 at this checkpoint.
- Master remains 76dbd27588de4aa37f3163d8b263d4b72a2cff32 and previous backup remains
  258991019e5af8b36eff407a8efa2c9fd03dd644. No production access, private configuration
  reads, dependency installations, push, merge or deployment. Resume unfinished
  Admin editorial/feedback/flag/price-delete audits next, preserving current work.

### Batch 35 — further PY-02/PY-26/PY-28 (2026-10-17)

- Feedback publish/hide/delete and price deletion now commit with their audits;
  row locks protect old snapshots. Failed audits restore records and dependent
  flags. Original moderation permissions, publication/deletion controls and public
  testimonial projection are unchanged. No production records or historical logs
  rewritten. Future feedback audits omit screenshot bytes; originals remain private
  in the existing Feedback record. No new fields or schema.
- Flag review locks the parent price, resolves current reports and records one
  count-only audit in the same transaction. Repeated/concurrent review returns
  the existing 204 without duplicate state-change audits; private reasons omitted.
- Five before tests reproduced seven failures (1.871s); all pass after (1.922s).
  All 152 backend tests pass, 87.644s. Twenty-nine pinned PostgreSQL cases pass,
  65.882s: moderation/delete rollback preserves images/prices/dependent flags;
  concurrent review writes one audit; testimonial edits keep continuous snapshots.
- Browser original testimonial publish/hide/delete, price create/approve/delete
  and Mark reviewed controls pass; public testimonials exclude attachments, Admin
  retains the attachment before deliberate deletion of the new synthetic record.
  Every preexisting synthetic price-history row is unchanged. No frontend rebuild.
- Manual: http://127.0.0.1:55446/admin/feedback or /admin/flagged after demo Admin
  login admin@example.com / PriceYardDemo8!. Evidence: batch-35-*.json.
- Seventeen IDs complete; nineteen partial/pending. Missing editorial/resource
  audit coverage remains PY-26 work. A concrete visible price-comparison safeguard
  awaits explicit approval: docs/PRICE_COMPARISON_APPROVAL.md. No proposed chart,
  quantity-selection or message changes implemented from that pending proposal.
