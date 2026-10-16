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
1 and 2 in docs/PURCHASE_VALUE_APPROVAL.md; indefinite-grant payment handling
remains a separate pending decision. Next: implement and verify these calculations;
remaining payment reconciliation/checkout validation follows separately.
Apply small technical batches with automated and browser verification. Reuse
existing local tools from .git/priceyard-local-recovery-20261015; do not reinstall
or read private configuration. Runtime is tools/local-test/runtime (ignored).

## Checklist — do not repeat the audit

| ID | Improvement | Current status |
|---|---|---|
| PY-01 | Consistent historical access checks | Complete in batch 7; date/comparison/ID routes enforce existing history entitlement; current summaries preserved |
| PY-02 | Confidential/restricted market information | Partial: quality list/detail match existing premium screen; broader source/audit response review pending; public basic guidance unchanged |
| PY-03 | Google ownership and safe account linking | Pending; new linking UI requires approval |
| PY-04 | Password reset and login revocation | Complete in batch 5; actual HTTP/browser and PostgreSQL reset/logout races passed |
| PY-05 | Referral abuse protection | Pending; preserve original rewards/qualification; policy changes require approval |
| PY-06 | Safe push notification destinations | Application-side complete in batch 13; known-provider/key validation, bounded TLS transport, no redirects; live provider compatibility remains operational verification |
| PY-07 | Shared-device/session safety | Partial: server logout/reset/disable revocation and stale UI protection; JS token storage/push cleanup/offline limits remain |
| PY-08 | Input/upload/request abuse bounds | Partial: push endpoint/key/query bounds verified; broader input/upload/request bounds pending |
| PY-09 | Concurrent security-action safety | Complete for identified reset/logout/last-Admin cases in batches 5/6; six PostgreSQL cases passed |
| PY-10 | Spreadsheet export safety | Complete in batch 3; text/numeric regressions and original browser download/access checks passed |
| PY-11 | Correct saved administrator price state | Complete in batch 10; actual create/approve/correct/outdated/reject/reload browser regression passed |
| PY-12 | Accurate existing quantity/type/market comparisons | Pending; no grades/new measurement fields |
| PY-13 | Consistent Nigerian dates/times | Partial: legacy naive trial timestamps interpreted as UTC consistently with backend; remaining entry/display/filter handling pending; original paid UTC date policy unchanged |
| PY-14 | Evidence-based movement/confidence | Pending; wording/policy changes require approval |
| PY-15 | Prices recover after failed loading | Complete in batch 1; before/after browser regression passed |
| PY-16 | Correct filters and response ordering | Pending |
| PY-17 | Correct market-detail loading | Pending |
| PY-18 | Accurate account/payment/access messages | Partial: stale profile/401/outage fixes plus batch 11 expiry display/timers verified; callback/payment messaging verification pending |
| PY-19 | Existing FAQ draft/hide/publish management | Complete in batch 12; hidden drafts remain available to Admin across reload, public publication boundary verified |
| PY-20 | Bounded queries with accessible historical records | Pending |
| PY-21 | Reliable independent alerts | Pending; no new delivery promises |
| PY-22 | Efficient loading and accurate dashboard totals | Pending |
| PY-23 | Preserve layout while fixing mobile overflow | Pending |
| PY-24 | Keyboard/focus accessibility | Pending |
| PY-25 | Safe and clearly aged offline prices | Pending; visible additions require approval |
| PY-26 | Complete atomic administrative audit | Partial: payment confirmation/access/audit share one transaction; remaining administrative writes pending |
| PY-27 | Consistent existing editing/password inputs | Pending |
| PY-28 | Historical record preservation | Partial: approved 0022 tested on fresh/populated synthetic PostgreSQL; future migration/history work pending |
| PY-29 | Stable identities and dependent records | Pending; no automatic merge |
| PY-30 | Isolated automated/browser verification | Partial: baseline guards, 12 original tests, six real browser workflows passed; expand with each batch |
| PY-31 | Confirmed payment activation and recovery | Partial: atomic activation, missing-subscription preservation and retry/replay tested; provider verification/reconciliation pending; schema additions require approval |
| PY-32 | Preserve unused purchased/trial time | Owner approved dated renewals and remaining trial preservation on 2026-10-16; implementation next; indefinite-grant payment handling pending |
| PY-33 | Validate payment evidence | Partial: signed evidence and duplicate provider-ID binding verified; checkout/reconciliation checks pending |
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
