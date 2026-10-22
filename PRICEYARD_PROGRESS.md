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
2026-10-17 owner clarified: continue routine authorized local commands, commits,
builds and isolated tests without repeatedly asking; use automatic approval where
eligible. Production/deployment, destructive and security-sensitive actions retain
explicit approval boundaries. This does not bypass platform sandbox restrictions.
Owner approved the specific internal auth_version/revoked_access_tokens scope on
2026-10-16; see docs/LOCAL_SECURITY_STORAGE_PROPOSAL.md. No other schema/business
scope is inferred from that approval. Production migrations remain forbidden.

## Status and next step

Current162 THREE CONVENIENCE CONTROLS LIVE / RELEASE PASS (2026-10-22 WAT):
verified 6c700c5d9e7b67e50a406bb76f594ca725d28216 committed and atomic
fast-forward pushed to master/development. Existing frontend priceyard is LIVE
at that exact commit, deploydep-dbct4rgm7kps73cruge0. Reused Current161 production
build/seven admission cases,11 convenience and9 navigation browser checks.
Read-only live browser PASS: all three control implementations served in
/assets/index-3endh_5T.js; Pause/Resume stops/resumes actual animation while
focused and respects reduced motion, without changing the ticker records.
All public price options/photos, stable View history links, compact mobile Menu,
guest gate and private401 session boundary remain intact. Browser sent no writes
(existing activity ping blocked), no login/customer access. Protected sort and
remembered-search behavior verified with synthetic accounts only. Backend remains
ce0ca70/deploydep-dbc68a5g1s2s7396tnog; no backend deploy, migrations, settings,
records or business-rule changes. Both services Auto-Deploy Off; prior frontend
a0cb706/deploydep-dbckl4vb9u1s73c0l530 retained for compatible artifact rollback.
Local preview stopped. Evidence: batch-154-history-convenience-release.json.
Chrome: hard-refresh the site; Price History > Search history > History order
below the graph; revisit Price History to check remembered selections; use
Pause/Resume scrolling on the green strip. 35/36 complete; unchanged PY-35 backup
transport safeguard awaits the already-sent Supabase support response.

Current161 THREE APPROVED CONVENIENCE CONTROLS / VERIFIED FOR RELEASE
(2026-10-22 WAT): owner approved implementation, commit, push and deployment.
History order offers Oldest first/Newest first for both table and mobile cards;
charts retain chronological input and measurement safeguards. Explicit UTC/WAT
instants determine order; unconfirmed dates remain visible at the end. Successful
history searches remember only commodity/market catalog IDs on this device,
fetch fresh prices on return, respect explicit View history links and survive
renaming; removed IDs, malformed/blocked storage and failed searches fail safely.
The visible Pause/Resume scrolling button controls animation only, preserving
price refresh, hover pause and reduced motion. Resume works while focused.
TypeScript/Vite production build and seven origin admission cases passed;
11 focused convenience checks and nine existing navigation regressions passed
serially with synthetic trial/Admin accounts and no external requests. Reviewed
desktop/mobile screenshots; 320/375px controls fit Easy reading and both themes,
44px targets; existing navigation verified through 1920px and short landscape.
Local preview stopped. No backend, schema, records, policies or dependencies
changed. Both Render services remain Auto-Deploy Off; frontend-only release next,
retaining a0cb706/deploydep-dbckl4vb9u1s73c0l530 for rollback. Evidence:
batch-153-history-convenience.json. 35/36 complete; PY-35 backup transport blocker
remains unchanged. Do not repeat completed backups or provider diagnostics.

Current160 THREE NAVIGATION IMPROVEMENTS LIVE / RELEASE PASS
(2026-10-22 WAT): reviewed a0cb706cd8abfeb2ed3e0c67e1c498629a462a89 committed
and atomic fast-forward pushed to master/development. Existing frontendpriceyard
deploydep-dbckl4vb9u1s73c0l530 is LIVE at exacta0cb706. Both services Auto-Deploy
remain Off; only frontend triggered, with no settings changes. Reused verified
159 build/seven admission cases,14 price/chart regressions and9 focused navigation
checks. Read-only live browser PASS: View history IDs match public price records,
compact mobile header/Menu work, all3 feature code served in
/assets/index-S0KrnKA7.js, all public prices preserved, guest history gate and
private401 session boundary intact. All writes blocked; no account login or
customer access. Protected history selection/Back to filters verified with
synthetic trial/Admin accounts, not production accounts. Backend remainsce0ca70
atdep-dbc68a5g1s2s7396tnog; no backend deploy, migrations, subscriptions/payment/data
changes or new services. Prior frontend13c9e3b/deploydep-dbc886ss728c73eav8ag
retained for rollback. Local synthetic preview stopped after verification.
Evidence: batch-152-navigation-release.json. Owner can hard-refresh /prices,
click View history and verify filters, shrink browser for Menu, then scroll
history and use Back to filters. 35/36 complete; backup transport blocker remains.

Current159 THREE APPROVED NAVIGATION IMPROVEMENTS / VERIFIED FOR RELEASE
(2026-10-22 WAT): resumed the saved changes; owner explicitly approved completing,
committing, pushing and deploying all three frontend improvements. Every price
card now has View history using existing commodity/market IDs; history preselects
them, handles back/forward links and preserves manual choices during session
refresh. Compact header retains all navigation/ticker/preferences, readable Easy
reading and44px navigation/toggle targets; brand/Menu share one mobile row.
Measured header offset bounds the menu in short landscape screens. Back to filters
appears after the form scrolls above the header, avoids WhatsApp, scrolls beneath
the sticky header, focuses Commodity and honors reduced motion. No access or
business-rule changes. TypeScript/Vite production build +seven existing origin
admission cases passed;14 price/chart regressions passed; nine focused navigation
checks passed on final build, including seven widths320–1920/Easy on-off,
844x390 landscape, guest/trial/Admin access, stable renamed IDs and keyboard focus.
Landscape clipping found in the first run was corrected before release. Visual
desktop/mobile/filter screenshots reviewed. Synthetic-only, no DB writes,
production contacts, migrations, dependency changes or new services. Evidence:
batch-151-navigation-ux.json. Release only the existing frontend;35/36 remain
complete, secure automatic backup still paused awaiting Supabase support.

Current158 CHART USABILITY CORRECTION LIVE / RELEASE PASS
(2026-10-21 WAT): approved13c9e3b4ab75cade0ea6d7d68cef1387c48da86c
committed and atomic fast-forward pushed to master/development after157 build,
14 focused checks and visual review. Both Render Auto-Deploy settings remained
Off; only frontendpriceyard triggered. Exact deploydep-dbc886ss728c73eav8ag
is LIVE. Read-only public browser confirmed the new labelled-axis/compact-summary/
interaction code served in /assets/index-C5afWBLR.js, public price grouping and
all options preserved, mobile/desktop fit, history guest gate and private401
session boundary intact. All writes blocked (existing activity/ping intercepted),
no account login/customer access. Private chart rendering and interaction were
verified with synthetic records, not a production account. Backend remains
ce0ca70 atdep-dbc68a5g1s2s7396tnog; no settings change, backend deploy or migration.
Previous frontend5a60e36 deploydep-dbc7ji3rjlhs73b3s3f0 is retained for rollback.
Evidence: batch-150-history-chart-release.json. Original design, records,
measurements and business rules retained. 35/36 complete; only secure automatic
backup verification remains paused awaiting Supabase support.

Current157 OWNER-APPROVED CHART USABILITY FIX / VERIFIED FOR RELEASE
(2026-10-21 WAT): owner rejected the oversized, poorly labelled charts and
explicitly authorized implementation, commit, push and frontend deployment.
History plots now remain250px high with responsive readable naira axes/grid,
WAT date ticks (time ticks for same-day records), commodity/market/specification
headings, and persistent exact-record details selectable by mouse, touch or
keyboard/previous-next arrows. Single records use compact dated price summaries
without an empty SVG. Fully matching records retain lines; incomplete records
stay unconnected; same-time observations do not imply a temporal trend. History,
measurements, current-price grouping, access rules and backend stay unchanged.
Production-mode TypeScript/Vite build and seven existing origin-admission cases
passed;14 focused synthetic browser checks passed, including actual mobile tap,
keyboard/pointer selection, axes/height, flat/tied times, same-dayWAT, retained
actions/filtering and mobile/easy-reading/light-dark themes. Visual review used
fabricated month-spanning histories, incomplete records and a single outlier.
No new dependencies, backend/DB/workflow changes, credentials or migrations.
Evidence: batch-149-history-chart-usability.json. Proceed only with the approved
frontend release;35/36 remain complete pending secure automatic backup success.

Current156 APPROVED PRESENTATION RELEASE LIVE / READ-ONLY CHECKS PASSED
(2026-10-21 WAT): owner explicitly approved commit, push and Render deployment
of the grouped commodity cards and restored history graph. Reused155 build/
browser evidence rather than repeating completed tests. Confirmed both existing
Render services Auto-Deploy Off, frontend root/dist configuration, retained64a3290
rollback artifact, and exact remote masterce0ca70 ancestry. Backend/workflows
are identical across the release. Atomic fast-forward pushed exact5a60e36 to
master/development; only frontendpriceyard manually deployed. Deployment
dep-dbc7ji3rjlhs73b3s3f0 LIVE at exact5a60e3679ebd4b2d758bfa3333941b5fb6f6ed71.
Fresh public read-only browser check passed: every public price preserved under
one photo per commodity, desktop/mobile layout fits, latest graph code served,
guest history gate and private401 session boundary intact. All writes blocked;
normal activity/ping telemetry intercepted before transmission, no login or
customer access attempted. Initial check incorrectly expected no attempted
telemetry; corrected the harness to distinguish blocked attempts from writes
sent, without changing application behavior. Backend remains LIVEce0ca70 at
dep-dbc68a5g1s2s7396tnog; no backend deployment, settings change or migration.
Evidence: batch-148-price-presentation-release.json. MiFi is sufficient for
ordinary application use/deployment. 35/36 still complete; secure automatic
backup remains paused while awaiting Supabase support. Existing backups,
automatic recovery, alerts and production data remain preserved.

Current155 OWNER-APPROVED PRICE PRESENTATION / LOCAL VERIFICATION PASSED
(2026-10-21 WAT): owner approved reducing repeated commodity photographs and
restoring useful history graphs while awaiting Supabase support. Current Prices
now shares one photo/title per commodity ID, retaining every returned record's
market, recorded measurements, status, notes, watch/share/report actions and
filters. Homepage cards remain unchanged. History retains connected trends for
complete matching specifications; older records missing measurement/type details
now appear as separate, explicitly unconnected low/high-range markers. Single
records remain visible. Invalid prices/unconfirmed timestamps stay in the table
with an explanation, without guessed dates, units or cross-measurement trends.
Chart colours follow the original light/dark themes. Production-mode TypeScript/
Vite build passed, including seven existing API-origin admission cases; eight
focused synthetic browser checks passed (identity/actions/filtering, graph
accuracy and desktop/mobile/easy-reading/themes), no external requests/database
changes. Evidence: batch-147-price-presentation.json. Local changes only: no push,
deployment, backend/database change or repeat backup/restore. 35/36 remain
complete: daily encrypted backup is still paused for the documented transport
blocker; live payment recovery/alerts and verified backups remain preserved.

Current154 TWO OPERATIONAL SAFEGUARDS PASS / BACKUP TRANSPORT BLOCKED
(2026-10-21 WAT): approved backendce0ca70 remains LIVE; two-hourly GitHub recovery
and actual delivered failure email passed153. Owner completed private enrollment
and switched to the correct phone hotspot. Both tested local connections still
cannot resolve the pinned Direct host (Windows11001) and have no usable IPv6.
Existing confirmed IPv4 Session pooler is reachable. One pinned verify-full/
same-CA/enrolled-password identity probe passed client TLS, PG17, dbpostgres,
rolepostgres, read-onlyON and revision0022; its distinct pooler-to-database
connection reports PostgreSQL SSL=false. One final own-backend metadata-only
classification confirmed nonlocal transport, not Unix/loopback. GSS encryption
was not checked; do not claim all transport is unencrypted. This fails the
unchanged existing database-TLS guard; verified client TLS does not prove upstream
TLS. No guard weakened, export/dump/new archive/restore/migration or provider
setting change occurred. No more probes, password requests or network-switch
loops. Only the newly registered daily backup task is Disabled; protected
enrollment, task settings, original helpers and verified archives/Drive copy stay.
35/36 complete; PY-35 cannot close until backup can use a transport satisfying
the required security guard and an actual scheduled archive succeeds. A working
IPv6 Direct connection is the unchanged secure path. Any alternative trust-policy
exception needs a separate explicit decision, not a silent relaxation.
Recovery/alerts remain active; production application and data are preserved.
No further development, services, spending or production changes are authorized
merely to force36/36. Evidence: batch-146-operational-activation.json.

Current153 APPROVED OPERATIONAL ACTIVATION / BACKUP VERIFICATION PENDING
(2026-10-21 WAT): owner explicitly approved backend-only deployment, two-hourly
recovery/alerts and existing-tool daily encrypted backups; manual Drive uploads.
Reviewed ce0ca7066e465c19b64498744c805b08e1eed03f was fast-forward published to
master/development with both Auto-Deploy settings verified Off and backend build
pip-only. Only backend OPS_RECOVERY_ENABLED=true merged; deployment
dep-dbc68a5g1s2s7396tnog LIVE at exactce0ca70. Existing frontend remains64a3290;
no migrations/schema/business-rule changes or new services/expenses. Missing and
fabricated operational auth both401 private/no-store; health200. Immutable GitHub
repo/owner identities independently matched before activation. Public repository
variable PRICEYARD_OPERATIONS_ENABLED=true verified, workflow active. Real runs
39559936636 and39560074138 PASSED, including persisted encrypted checkpoint read
on second run. Intentional alert-only run39560232468 failed exactly as designed;
actual matching GitHub email verified in approved owner's Gmail INBOX at
2026-10-21T07:11:41Z. No application/provider call in the alert simulation.
Reviewed backup adapter installed outside Git; owner confirmed hidden enrollment
ENROLLED. Daily20:00WAT original-owner/limited/network/catchup/no-overlap/10min task
registered; first actual task failed safely before any pg_dump/roles export/new
archive. Current network lacks the Direct endpoint's required IPv6 route; exact
native failure not logged, so do not claim an unconfirmed cause. Bounded
credential-free connectivity check pending; preserve enrollment/old archives,
New task now Disabled with registration/enrollment preserved. Credential-free
pinned-host lookup returned Windows DNS11001 and no address; no TCP/auth/export
was attempted by that probe. Current network therefore cannot reach the Direct
backup endpoint. Owner asked to reconnect the previously working phone hotspot;
then verify reachability before enabling/running the already-enrolled task once.
No password re-entry or repeat setup needed. No new
password prompt, restore, migration or upload. 35 complete, PY-35 partial until
the first scheduled backup succeeds; recovery and delivered alerts are verified.

Current152 REQUESTED OPERATIONS VERIFIED LOCALLY / ACTIVATION PENDING
(2026-10-21 WAT): owner reopened only PY-35 automatic payment recovery, essential
failure alerts and regular encrypted backups. Original live application/design,
business rules, revision0022 and all completed evidence preserved. New code:
hidden disabled-by-default GitHub-OIDC recovery endpoint; existing reconciliation
rules/PG lock, encrypted cursor, aggregate-only output; gated two-hour GitHub
schedule with bounded checks and controlled failure test; existing encrypted
backup core adapted narrowly for0022 and DPAPI/EFS enrolled daily Windows task.
43 new targeted tests passed (12 backend,21 scheduler,10 backup), six fabricated
source-identity negatives refused, owner/ACL/EFS/key/DPAPI/child-job/PS syntax
checks passed. No completed audit, real backup, restoration or migration repeated.
Owner confirmed GitHub failure-email settings SAVED and browser-only Drive folder
PriceYard Private Backups. No software/sync client installed; off-device copies
remain manual encrypted uploads. New code is prepared, not falsely called active.
Latest owner instruction forbids production changes: no master push, deployment,
live recovery/alert check, new export, credential enrollment or task registration
has occurred. Need approval for exact backend-only activation and one private
backup enrollment; observe real workflow/alert receipt/first scheduled backup
before claiming completion. 35 fully complete, PY-35 partial, 1 remaining.
See docs/PY35_OPERATIONAL_SAFEGUARDS.md and batch-145 local evidence. No new
features, schema, customer-data edits, provider credentials or paid resources.

Current151 APPROVED CONTROLLED RELEASE PASS / LIVE (2026-10-21 WAT): owner
confirmed PASS for actual permanent-site Google login, dashboard refresh retaining
login, logout and refresh retaining signed-out state. Authenticated hosted cookie
lifecycle now passes in owner's browser; no tokens/passwords shared. Together with
actual Render routing/body/private-cache/negative-CSRF/API404/SPA/JS checks,
protected PG17 recovery/migration/rollback and previously completed genuine TEST
payment/webhook/replay/email/provider evidence, the approved release is GO/LIVE.
Backend dep-dbc17ocs728c73dkqn9g and frontend dep-dbc19kvavr4c73egctug both LIVE
64a32909d0185d9487d45aa26b47466492a92557; production0022 applied once by owner.
Auto-Deploy stays Off, routine backend build pip-only. No rollback was needed or
performed. Retain exact secure artifact IDs/current0022; never downgrade/erase
payments/revocations or choose pre-security backend as fallback. Original master
backup branch and encrypted recoverable DB backup remain preserved.
STOP release implementation/testing: no demonstrated launch blocker remains,
no new staging/services, no repeat checks or migration. Existing operational
follow-ups are explicitly NOT verified: automatic payment recovery schedule,
alert delivery/on-call/broader load/browser checks, ongoing backup targets and
coverage, exceptional ambiguous historical payments. They are separate from
successful approved launch. Original tracker remains35 fully complete + PY-35
partial for these broader operations; do not falsely claim all nine gates passed.
All planned application changes are live. Preserve this handoff and perform no
further production change merely to make the checklist read36/36.

Current150 BOTH PRODUCTION SERVICES LIVE / OWNER SESSION ACCEPTANCE PENDING
(2026-10-21 WAT): frontend dep-dbc19kvavr4c73egctug is LIVE at exact reviewed
64a32909d0185d9487d45aa26b47466492a92557, same as live backend dep-dbc17ocs728c73dkqn9g.
Actual anonymous HTTPS frontend checks PASS: /login200HTML with original React
root, /dashboard200 identical SPA entry (fallback preserved), built JS asset200
JavaScript. Backend routing/security checks from149 remain passed; not repeated.
Owner asked to open permanent /login, hard refresh, Google sign in with approved
owner account, refresh dashboard, log out, refresh and report PASS/visible error.
This is the remaining authenticated hosted acceptance for the approved controlled
release. No passwords/tokens requested. Do not claim valid login/cookies/logout
before owner's result. Do NOT redeploy or rerun0022 on resume: both services are
already live, migrations applied once, Auto-Deploy deliberately Off.
Rollback uses retained secure64a3290 backend artifact/current0022; never select
old pre-securitya9cf1b9, downgrade or overwrite live payments/revocations. Local
PG17 rollback remains passed; actual Render rollback was not triggered because
no observed check failed. Original source backup and protected database recovery
evidence are preserved; new environment changes were public URL keys only.
35 recommendations remain fully complete; PY-35 launch acceptance pending.
Existing broader operational follow-ups (automatic recovery scheduling, alert
delivery/on-call, ongoing backup targets/coverage and exceptional historical
payments) must not be falsely labelled tested or used to restart staging/audits.
Keep release PASS/GO distinct from claiming every original operational gate passed.
Master remains pinned reviewed release64a3290; local progress notes do not deploy.

Current149 BACKEND LIVE / FRONTEND BUILD ACTIVE (2026-10-21 WAT): backend
dep-dbc17ocs728c73dkqn9g is LIVE at exact approved64a3290. Five bounded actual
frontend-origin checks passed: /api/health200; guest /auth/browser/session401 and
forged-cookie /auth/me401 with private/no-store; forged-cookie logout without CSRF
403 with private/no-store; nonexistent /api route404 JSON (not React HTML).
Fabricated invalid cookie only; no owner/customer credentials, business records,
payment or email used. This is real candidate/backend/cache/CSRF forwarding proof,
not a claim of successful authenticated login. Secure backend artifact now exists
at that retained deployment ID; original pre-security backend is not a fallback.
Frontend VITE_API_URL=/api saved by merge only; all other env/secrets preserved.
Save started frontend dep-dbc19kvavr4c73egctug at exact64a3290. No duplicate deploy.
Monitor that ID to terminal state, then bounded HTML/SPA/asset checks and owner's
Google sign-in -> dashboard reload -> logout -> guest refresh acceptance. Do not
mark36/36 or fully validated until actual authenticated workflow passes.
Migration0022 remains applied once; no repeat tests/backups or new services.

Current148 APPROVED MASTER PUBLISHED / BACKEND BUILD ACTIVE (2026-10-21 WAT):
after owner-confirmed0022 and fresh Off/pip-only checks, normal master push
76dbd27->64a32909d0185d9487d45aa26b47466492a92557 succeeded; remote exact SHA verified.
Original backup branch76dbd27 preserved. Backend FRONTEND_URL merged (replace=false)
to https://priceyard.onrender.com, leaving secrets/other environment untouched.
Environment save started Render deployment dep-dbc17ocs728c73dkqn9g of exact
approved64a3290. No duplicate trigger issued. Monitor this ID to terminal state.
Do NOT update/deploy frontend until backend live and bounded health/session-route
readiness passes. Frontend VITE_API_URL then changes to /api (merge only), and its
resulting exact64a3290 deployment must be monitored before hosted session checks.
Both Auto-Deploy remain Off; no migration rerun or data reset. Owner-applied0022
is already successful. Local prior tests/backups retained without repetition.

Current147 OWNER CONFIRMED PRODUCTION0022 (2026-10-21 WAT): owner ran the exact
approved guarded SQL in the existing Supabase project and reported SUCCESS with
installed_revision0022_login_revocation. Record as owner-operated confirmation;
agent did not connect to the database. Do NOT rerun0022, stamp, downgrade or
restore over live data. Fresh Render metadata again verifies Auto-Deploy Off on
both, master branches unchanged, backend build pip-only. Controlled release
approval remains granted. Now publish reviewed release64a3290 by normal master
fast-forward, retain original remote backup, merge only required public URL
configuration without touching secrets, deploy backend first, then frontend/API
configuration and perform missing hosted sessions. No repeated tests or backups.

Current146 PRODUCTION ROUTE VERIFIED / APPROVED SQL STEP PENDING (2026-10-21 WAT):
owner saved backend build-only pip command and ordered frontend rewrites. Fresh
Render metadata verifies backend Auto-Deploy Off, `pip install -r requirements.txt`,
and unchanged correct Uvicorn start. One bounded anonymous actual production
frontend check passed: GET /api/health ->200 application/json; POST /api/auth/login
with deliberately invalid fabricated JSON ->422 json_invalid. No credentials,
accounts, payments or customer records submitted. This verifies real Render
method/body routing to the stable existing backend; cookies/session checks still
pending the candidate release. No Cloudflare/staging tests or prior checks repeated.
Hash-verified guarded SQL40d29dc7...707b1f copied to owner clipboard, not executed
by agent. Owner instructed to open ONLY existing project lrvpjfbtmftjkzaxbunk SQL
Editor, paste ENTIRE script, Run once and report installed_revision0022 or stop on
error. Async result pending. Do NOT execute SQL again if owner reports success.
Next: confirm migration result, publish exact reviewed release64a3290 to master
by normal fast-forward, set required public frontend origin on backend, deploy
backend first and verify/retain its secure artifact. Then VITE_API_URL=/api on
frontend, deploy frontend and complete only missing hosted login/CSRF/logout checks.
Both Auto-Deploy settings must stay Off. On failure retain0022/security/payment
records and use security-compatible application recovery; no DB downgrade/reset.
No master push, application deployment or agent production DB connection yet.
35/36 remains. Release approval already granted; do not ask again.

Current145 AUTO-DEPLOY PAUSE VERIFIED / RELEASE SOURCE PUBLISHED (2026-10-21 WAT):
owner saved Off on both services; fresh Render metadata confirms autoDeploy=no
for priceyard-api and priceyard. Both remain running; no deployment triggered.
Published release source64a32909d0185d9487d45aa26b47466492a92557 to GitHub branch
codex/priceyard-original-preserved-20261016. Preserved remote original master76dbd27
in backup/priceyard-production-pre-release-20261021. Atomic push succeeded; remote
refs verified. Remote master is still76dbd27588de4aa37f3163d8b263d4b72a2cff32.
NEXT owner Dashboard edits pending (connector cannot edit these): backend Build
Command becomes `pip install -r requirements.txt` (remove automatic Alembic);
frontend FIRST Rewrite `/api/*` -> `https://priceyard-api.onrender.com/*`, retain
SECOND Rewrite `/*` -> `/index.html`. Save only, no Manual Deploy. Async SAVED
confirmation requested. Verify settings and bounded anonymous routing after save;
then coordinate the already-prepared guarded Supabase SQL, publish master by
normal fast-forward only, and deploy backend before frontend. Do not run the SQL
before explicit migration-step instructions. No production database connection,
migration, customer-data change, merge, master push or deployment yet. Production
settings changed so far ONLY owner-confirmed Auto-Deploy Off. No tests repeated.
Do not request release approval again; it remains explicitly granted.35/36 remains.

Current144 CONTROLLED PRODUCTION RELEASE APPROVED (2026-10-21 WAT): owner
explicitly approved Render routing changes, migration0022 and deployment, with
rollback on failed checks. This supersedes earlier no-production-change approval
flags for this exact release; no new staging/services/database or repeated tests.
Branch clean at ccef8d4 before release preparation; 35/36 work preserved. Native
Git remote access works (master remains76dbd27588de4aa37f3163d8b263d4b72a2cff32).
Live Render backend remains a9cf1b9/dep-db6214p5efls73b651j0; frontend remains
76dbd27/dep-db62ce0ae00c73a7g9i0. Both auto-deploy yes at this checkpoint.
Required owner Dashboard action pending: set Auto-Deploy Off on BOTH existing
services. Connector cannot edit this setting; no push or deployment before that
change is verified. Existing fallback source/migration/backup passes retained.
Prepared docs/sql/PY35_APPROVED_0022_RELEASE.sql for the exact existing Supabase
project's SQL Editor, avoiding another password prompt. Offline generation only:
reviewed0022 source SHA6b7cd540...69fa and original compiled SQL SHA221e1ec1...43f8
match the successful rehearsal; compiled migration body preserved unchanged.
Added transactional metadata baseline/role/PG17/ownership/absent-object guards,
lock2s/statement30s/idle30s limits and public creation search path. Independent
review corrected an initial search-path draft before use. Source project must be
confirmed in the exact Supabase Dashboard URL; role/database names alone do not
identify a project. SQL SHA40d29dc7bb10981a5bb393e4e5a51a69164bd3933e897f8e3f02ee07a0707b1f.
No production DB connection, SQL execution, migration, application source edit,
push, merge or deployment has occurred. Local compile/hash/transaction checks only;
no previous test/backup/rehearsal repeated. Continue AFTER Auto-Deploy Off verified:
publish exact release source, remove migration from routine backend build, coordinate
guarded Supabase SQL once, then backend and same-origin frontend release. Retain
security-aware candidate artifact and preserve0022/payment/revocation data on any
application rollback; never select old pre-security backend as fallback.
Evidence: batch-144-controlled-release-authorized.json. PY-35 still partial until
actual hosted sessions/runtime/rollback acceptance; do not mark36/36 yet.

Current143 CONDITIONAL HOSTED API BLOCKED (2026-10-20 WAT): owner approved ONE
temporary Free Render API only after confirming a suitable isolated database,
with hosted sessions/rollback tests and service stopped within two hours.
Read-only Render database listing in confirmed My Workspace returns only
settletrack-db; it was not connected to or modified. Existing private synthetic
PostgreSQL remains private. The proposed memory SQLite fixture supports one
process's session tests but loses revocations/account state on restart; it cannot
establish durable hosted rollback safety. No suitable permitted hosted database
has been confirmed. Current Render connector exposes no suspend/delete control;
Render CLI is not available on PATH, and no authenticated alternative stop path
has been verified. Idle sleep or process exit is not a two-hour suspension.
STOPPED before API creation, branch push, tests or deployment, as instructed.
No failed application test is claimed for this blocked attempt. Previous hosted
POST502 and all completed work/evidence remain preserved. 35/36 complete; PY-35
partial, deployment approval NOT READY. Minimum prerequisites: a separate
permitted test database that retains revocations across rollback and a verified
Dashboard/API suspension arrangement before any service is created. No new
database, paid resource, production access/settings, migrations or repeated tests.
Evidence: batch-143-hosted-api-prerequisites.json.

Current142 HOSTED TRANSPORT FAIL (2026-10-20 WAT): after owner saved latest kai
destination, automatic corrected suite ran once. Actual Render GET synthetic
identity PASS; POST/probe returned502, stopping before body/query/cookie/login
checks. Handler counts show GET/health4 and GET/status1, no POST or /auth calls.
Outer RequestBounds/Uvicorn are not counted, so do not assert request never reached
the host. Worker log empty; tunnel log registered successfully with no recorded
error. Browser failed before controller collected counts and closed helpers;
cleanup did not cause the502. Exact failing layer/cause cannot be established
from retained logs: response headers/body were not retained by that run. Earlier
POST207 remains evidence forwarding can work; do not claim Render unsupported,
blame MTN/passwords, loosen checks or automatically repeat tunnels/tests.
All owned browser/API/tunnel processes stopped; failed results/logs preserved.
No production data/settings, provider/backup/migration tests, push or deployment.
35/36 remains, PY-35 partial. Hosted login/cookie/cache/CSRF/logout NOT RUN, not PASS.
Added only future failure diagnostics: whitelisted synthetic-probe response
headers/error excerpt and one direct-upstream health GET before cleanup; no
automatic POST retry or additional attempt launched. Safe next investigation
requires distinguishing Render forwarding from the transient tunnel hop; a stable
isolated backend is an alternative requiring a separately approved resource.
Evidence:batch-142-hosted-transport-failure.json. Release approval still withheld.

Current141 HOSTED POST / QUERY HARNESS CORRECTION (2026-10-20 WAT): automatic
drill did run after owner saved corrected Rewrite. Actual temporary Render GET
verified synthetic identity; POST/probe returned207 with method POST. The harness
then failed before body/cookie/login assertions because Render serialized a query
space as '+' instead of '%20'. Both decode identically for this query; this was
an overly strict test assertion, not an established application defect. Original
FAIL/result/logs retained under runtime/render-hosted-20261020/query-normalization-stop.
All owned helpers closed; upstream counts confirm zero /auth requests.
Corrected only harness: exact decoded duplicate values/order/count and literal
plus (%2B) must survive; independent key ordering/space encoding may normalize.
Raw body SHA,207 status, cookies, private cache, CSRF/logout remain strict. Local
query sanity/syntax checks and narrow independent source review pass. One-time
--resume-query-normalization admits only this exact pre-login stopped failure,
preserves all evidence, and resumes unfinished batch against SAME test site/memory
API. No provider/backup/migration tests repeated, new services or production changes.
New verified tunnel destination is in current state.json; owner instructed to
replace only that destination and Save. Fresh-proof auto-detection starts one
bounded suite, then closes tunnel/API/browser.35/36 remains; hosted login pending.
Evidence:batch-141-hosted-query-check.json. No push/migration/deployment authority.

Current140 CORRECTED ACTION / BOUNDED CONTINUATION (2026-10-20 WAT): owner confirms
the temporary API row was changed from Redirect to Rewrite and saved. Previous
15-minute tunnel expired before this reply; result confirms no browser/login run
and clean helper shutdown. Renew only the same synthetic environment/test target,
preserving all evidence; completed POST/provider/backup/migration tests stay skipped.
Renewed manual window is bounded30minutes so owner can replace only its destination.
Controller polls ONLY pinned temporary Render /api/health at15-second intervals,
without redirects; fresh matching synthetic proof permits the already-approved
single hosted suite automatically after save. No fabricated SAVED marker, login
through old/wrong route, new service, production setting, migration or deployment.
Close tunnel/API/browser immediately after result or timeout. Current active URL
and expiry remain in runtime/render-hosted-20261020/state.json; old URLs are stale.
35/36 unchanged until actual hosted result. Do not repeat earlier completed work.

Current139 SAVED ROUTE OBSERVATION (2026-10-20 WAT): owner confirms SAVED for
renewed reforms-describe-smithsonian-contrast tunnel. Before any login/POST, exact
temporary Render /api/health responds301 Location->current tunnel /health. One
cache-busted GET with no-cache confirms301 again. Independent current tunnel and
loopback health both200 with matching synthetic proof. This is a saved-route
redirect, not failed credentials, TLS, DB or production availability. Owner asked
to check ONLY temporary /api/* row Action: change Redirect to Rewrite if needed;
if already Rewrite, report it without changes. Do not infer platform failure until
saved Action is confirmed. Confirmation marker NOT written, hosted browser/login
not run. Do not follow301 or send auth data to a different origin to hide failure.
Current controller remains bounded by state expiry; check result before resuming.
35/36 unchanged, migration/rollback/provider/backup passes preserved. No production
change, push, migration or deployment. Evidence:batch-139-hosted-route-observation.

Current138 TUNNEL RENEWAL (2026-10-20 WAT): owner explicitly requests renewal of
only the expired test window, retaining the same temporary Render site/environment.
Previous result confirms expiry without SAVED, no hosted browser run and clean
owned-process shutdown. New --renew-expired-window admits exactly that state,
rejects live/confirmed/completed windows, checks cached binary/free test port first,
and preserves prior result/state/logs in an expired-window-* directory. Same
synthetic-only API/settings/guard and same Render target; no new site/DB/service,
production settings, provider credentials or deployment. Skip completed POST/browser
checks; check only renewed tunnel registration and fresh verified HTTPS identity.
New active URL/15-minute expiry must come from current runtime state.json, never
the expired question/old rewrite. Wait for owner to save that exact test-only
rewrite; do not generate SAVED or run browser automatically before confirmation.
35/36 and all previous passes retained. Production release approval still withheld.

Current137 TEMPORARY FREE TARGET (2026-10-20 WAT): owner grants the requested
one-site exception. Created exactly one static-only synthetic Render target:
priceyard-py35-check-20261020, srv-dbbs8omi0phs73e1mtd0,
https://priceyard-py35-check-20261020.onrender.com. Initial non-production deploy
dep-dbbs8oui0phs73e1mu50 is live. Auto-deploy NO, no env vars/credentials/database,
no cloned production environment or migration build. Existing repo/master is read
only for checkout; build merely writes a tiny synthetic HTML page to py35-check.
No code push, dependency install, production setting/migration/deployment or paid
service. Do not create another site on resume. Connector cannot edit rewrite rules
or delete the test target; its Dashboard is the owner action path. Preparing one
bounded synthetic-memory API + hash-verified cached tunnel, no provider keys/PG17.
Setup syntax/isolation review passes. First pre-test hostname lookup raced tunnel
registration; processes stopped cleanly. Source corrected to wait boundedly for
registration and verified HTTPS identity. Exact failed setup logs retained in
runtime/render-hosted-20261020/dns-readiness-stop; one gated setup resume only.
New synthetic HTTPS identity and independent POST/body/query control PASS.
State now awaiting ONLY test-site rewrite: /api/* to active state.destination,
then unchanged SPA /*->/index.html; owner question sent with verified current URL.
One15-minute controller window, then tunnel/API stop automatically. No real keys,
provider calls, production data, copied config or PostgreSQL. Runtime progress under
runtime/render-hosted-20261020; check state/result/expiry before confirming SAVED.
On genuine owner SAVED only, write rewrite-saved.txt to trigger single bounded
hosted browser run. Never confirm for owner, reuse expired URL, rerun completed
checks or create another site. No Render edge result yet.35/36 unchanged.
Final release authority remains withheld. Test-site cleanup requires its Dashboard.

Current136 HOSTED TARGET CHECK (2026-10-20 WAT): owner requests one controlled
safe-target hosted verification, no paid resources or production change. One
approved-workspace Render list_services(includePreviews=true) confirms no isolated
PriceYard test/preview target. Do not reuse unrelated applications. No provider,
database, customer, secret, setting or application endpoint accessed/changed.
Connector create_static_site cannot set routes; no route-update/delete tool is
exposed. A temporary Free static target plus one owner Dashboard test-only rewrite
is the smallest available path. Earlier no-new-services restriction conflicts with
creating that target, so one explicit exception requested; no target created or
branch pushed while pending. Production/parent preview settings stay unchanged.
Unchanged0022 SHA2566b7cd540b41982c13091be3805f4660144b8b9b389224cecf7fa5b85d77469fa
and unchanged backend/app tree fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed confirm
previous rehearsal/secure local rollback evidence still applies; no tests repeated.
Hosted result BLOCKED/NOT RUN, not PASS or observed application failure.35/36
remains. Final deployment approval must wait for actual edge/runtime/rollback
verification and controlled cutover approval; no production migration/deploy.

Current135 SAME-ORIGIN LOCAL PASS (2026-10-20 WAT): owner approves narrow routing
implementation/verification, preserving existing services and React fallback;
production changes/push/merge/migration/deploy still forbidden. Proposed exact
VITE_API_URL=/api and API-first external Rewrite recorded in
docs/RENDER_LAUNCH_SETTINGS.json; unchanged SPA /*->/index.html remains second.
Actual production Vite build now rejects separate-site API destinations. Seven
configuration cases and TypeScript/Vite production build PASS in reused isolated
snapshot, no installs. Normal approval resolved esbuild sandbox directory denial;
network/dotenv guards retained. Pre-existing untracked routing test preserved and
completed, fixing import shadowing and synthetic probe lifespan handling only.
Two guarded in-memory tests PASS: actual API sessions/CSRF/logout/revocation,
raw POST/query/multiple cookies, private cache, fixed route/fallback and mocked
payment/direct-webhook compatibility. No real provider test repeated.
One cached Chromium workflow PASS with rebuilt original React and actual original
API over stdio: virtual HTTPS host-only Secure/HttpOnly/Lax login/dashboard/reload,
API requests, CSRF403, logout204/cookie deletion and revoked replay401. All page
traffic fulfilled locally/blocked; no sockets, real TLS/Render/provider request,
production credential or record. Browser/bridge closed; no persistent DB fixture.
Backend/app tree fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed still matches already
tested rollback2cfbfa6; no repeat backup/restoration/migration/rollback drill.
Render edge POST/cookie/private-cache and hosted candidate/secure rollback artifact
remain NOT RUN, requiring scoped hosted-change approval, not observed failures.
No UI/design/business/backend-application/migration change.35/36 remains; PY-35
partial. Final exact launch changes/approval boundary:
docs/PY35_FINAL_LAUNCH_REPORT.md. Evidence:batch-135-same-origin-release.json.

Current134 RENDER READ-ONLY VERIFICATION (2026-10-20 WAT): owner explicitly
confirms My Workspace, tea-d281vqh5pdvs7383f86g. Pinned service reads and five
recent deploys per service confirm both use master with on-commit auto-deploy.
Actual backend start is uvicorn app.main:app --host 0.0.0.0 --port $PORT:
CORRECT, superseding earlier supplied malformed command/attribute uncertainty.
Backend build still runs pip install then alembic upgrade head; no settings saved.
Frontend is a static site, root frontend, publish dist. Live backend a9cf1b9 and
frontend76dbd27 match previous owner reports. Reviewed secure rollback candidate
2cfbfa6 is not an ancestor of the live backend; limited history does not establish
retained compatible rollback artifact availability. Local rollback pass retained.
One coarse one-hour backend metrics read returns CPU0.001338-0.001425 cores and
memory about120.2-120.7MiB; instance-count series empty. One bounded last24h event
read returns no server_failed/server_restarted events. These describe the old
deployed app, not candidate load/readiness, alert delivery or failure recovery.
Blank health path means default TCP. Notify-on-fail is default; recipient/delivery
not verified. Owner-confirmed API URL/SPA-only rewrite remains the candidate Lax
session blocker; no live request/proxy/cookie configuration change or outage claim.
No app logs, secrets, database/customer reads, repeated provider/backup/migration
tests, app-source edits, production mutation, push, merge, migration or deploy.
35/36 remains. Next: approve/rehearse the smallest compatible same-origin API
release route, then verify candidate hosted runtime/secure rollback and controlled
cutover/operational acceptance. No paid domain/service assumed or created.
Pre-existing untracked backend/tests/test_render_routing_contract.py preserved,
not executed/staged/discarded. Evidence:batch-134-render-readonly.json.

Current133 CONFIRMED RELEASE ROUTING BLOCKER (2026-10-20 WAT): owner verifies
frontend VITE_API_URL=https://priceyard-api.onrender.com and sole rewrite
/* -> /index.html (Rewrite), explicitly no /api rewrite/proxy. These settings
match the already-tested direct/separate-Render-sites topology; do not rerun it.
Current upgraded source sets Secure/HttpOnly/SameSite=Lax, so cross-site browser
login cannot retain/use this session. Exact CORS alone cannot fix the cookie
restriction. This is an upgrade-release incompatibility established from confirmed
settings + source + retained browser test, not a claim of a checked live outage.
No purchased domain is needed; same-origin API transport is the robust target.
Do not assume external static rewrites proxy POST, cookies and private-cache
semantics correctly without platform verification. No proxy/cookie/API setting
changed, no public probe, source change or repeated provider/database test.
User clarifies Start Command already contains app.main but supplies no new exact
attribute value. Retain prior malformed-target evidence; actual saved command is
UNVERIFIED, not a confirmed live startup fault. Exact valid target is app.main:app.
Blank health remains default TCP; /health would improve HTTP liveness and is not
alone evidence of an outage or a separate proven launch defect. Existing hosted
candidate/compatible rollback/migration cutover and operational acceptance remain
unverified; do not declare PY-35 complete or deploy. Record35/36 and preserve all
provider/backup/migration/Google passes. Current production settings preserved.
Evidence:tools/local-test/evidence/batch-133-render-configuration.json. Stop at
confirmed incompatibility before any production modification; resolve transport
in the reviewed release proposal, with separate production approval.

Current132 RENDER RELEASE CONTRACT (2026-10-20 WAT): owner independently reports
priceyard-api Start Command `uvicorn app.main --host 0.0.0.0 --port $PORT` and
Health Check Path blank. Local Uvicorn importer rejects exact
target app.main before any app import: module:attribute required. AST confirms
backend/app/main.py defines FastAPI app; proposed release command is
uvicorn app.main:app --host 0.0.0.0 --port $PORT. As-provided startup defect is
confirmed; no claim made that current live process was started with that setting.
No production read/setting edit/restart/deploy. Blank health path means Render's
default TCP probe, not no checks. Proposed /health is existing HTTP process
liveness only; AST confirms constant response, no database-readiness proof.
Reviewed Render current deployment/health/rollback docs; Free has no paid-only
pre-deploy command. Existing migration-running build still requires approved
release sequencing; do not save settings that may trigger deploy/migrations now.
Reviewed existing PY-07 same-site routing requirement (not reopened feature).
Current candidate uses Secure/HttpOnly/SameSite=Lax. Public Suffix List includes
onrender.com. ONE serial cached-browser virtual test fulfils/aborts every request
before transport: direct separate Render sites login200 then session401/no cookie;
same-origin /api control login200/session200/cookie present. No production request,
database, provider, tunnel, dependency install or repeated prior workflow test.
This confirms the transport contract, not deployed route configuration. Frontend
VITE_API_URL and existing /api rewrite/proxy remain unverified; no live defect
claimed if a compatible same-origin route already exists. No custom domain needed.
Next read-only owner action: Render priceyard frontend's VITE_API_URL public URL
and existing /api Redirects/Rewrites rule or absent; no keys or settings changes.
Render MCP tools absent in this session; do not repeat plugin/billing/Google tests.
Evidence:tools/local-test/evidence/batch-132-render-contract.json.35/36 remains;
production start/routing/health/configuration and existing rollback/operations
gates still block deployment approval. All previous passed work preserved.

Current131 GOOGLE PASS (2026-10-20 WAT): owner Screenshots4216/4217 confirm existing
PriceYard web client already authorises http://127.0.0.1:5173 and permanent
https://priceyard.onrender.com. Its public client ID matches selected existing
frontend/backend configuration. No Google setting, project/domain/credential,
Render service or production record changed. No new tunnel.
Reused original frontend snapshot and existing marked synthetic PG17 schema;
built only local API destination http://127.0.0.1:55446/api, no source edits or
dependency installs. Native DB bound127.0.0.1:55452,32MB shared buffers/12connections.
Three new origin-admission rejection cases passed before DB/provider access.
Initial owner FAILED TO FETCH diagnosed precisely: test wrapper required private
cookie on credential-free CORS OPTIONS, returning403 with no allowed-origin header.
Controlled stop preserved report/build; local-only exact-origin CORS placed outside
the private gate. Six bounded checks passed: allowed preflight, rejected unrelated
origin, actual-request gate retained, payment and email writes blocked, anonymous
session401 readable by the approved frontend. No production/app security change.
Reused build on correction; no repeat payment/email/backup/migration checks.
Actual Google signed ID token verified for approved account/client; an already-
linked synthetic fixture passes original Google authentication, and owner explicitly
confirms YES REACHED DASHBOARD. Tokens/passwords/Google subject ID never requested
in chat or saved in logs/Git. Original HTTP-only local cookie exception stays in
test environment/127.0.0.1:55446; no production cookie policy changes or HTTPS claim.
Final local-Google report PASS; frontend/worker/PG17 all confirmed stopped.
Google local end-to-end, public HTTPS sessions, actual received reset email and
genuine Paystack TEST payment/webhook/replay now pass. Actual Render candidate
artifact/proxy/monitoring/scheduler and release/rollback/cutover approval remain
open existing PY-35 gates;35/36 complete, no push/merge/deploy/production migration.
Evidence:tools/local-test/evidence/batch-131-local-google.json. Do not repeat these
passed checks. Remaining work is final release configuration/operational approval.

Current130 (2026-10-20 WAT): owner confirms CLEARED after removing expired Paystack
TEST webhook; record as owner-confirmed, not an independent provider-settings
inspection. LIVE settings unchanged by Codex. Completed payment tests retained.
Owner explicitly requires no further Cloudflare URLs for Google authentication.
Permanent frontend origin is https://priceyard.onrender.com; backend is
https://priceyard-api.onrender.com. No purchased/custom domain is required.
For Google-only isolated testing, inspect whether an authorised localhost origin
already exists; any needed development origin must be separately authorised.
Next owner action: inspect existing Google web client's Authorized JavaScript
origins read-only, supplying public website addresses only, no secret and no
settings edit. Do not repeat provider payment/email/backup/migration tests or
create a new tunnel.35/36; PY-35 partial; no production change or deployment.

Current129 GOOGLE BLOCKER CONFIRMED: owner Screenshot4211 shows Google's actual
400 origin_mismatch and instruction to register the JavaScript origin, for the
races-son temporary frontend. This confirms an external test-origin configuration
blocker; no Google ID token reached the original backend and actual Google login
has NOT passed. Earlier automated google_origin_rejected:false only means that
runner saw no error before the human popup; it is not an authorization result.
Stopped the completed payment window rather than repeat tests or bypass Google's
origin validation. Final runner result: partial, tunnel_closed/worker_stopped/
postgres_stopped all true; genuine TEST payment and replay PASS retained.
The races-son URL is now CLOSED. Owner should clear the expired TEST-only webhook
(never restore production as a TEST destination; LIVE unchanged). Read-only next
step: inspect existing Google web client's Authorized JavaScript origins, sharing
only public website addresses. No client-secret/key request or production OAuth
setting change authorized. Any new temporary origin or separate test client needs
a bounded owner-approved configuration step; never register an expired tunnel.
Google official setup guidance confirms scheme+hostname-only Authorized JavaScript
origins; not a redirect-URI/password/measurement/UI change.35/36 unchanged.
Verified browser/payment work committed locally a13004d; no push/deploy/migration.

Current129 PAYMENT PASS: while awaiting owner browser action, the real TEST
charge.success event arrived at the confirmed isolated HTTPS endpoint. Original
signature validation/handler passed; exact checkout reference has success2500.00
NGN and active paid_monthly subscription. Reposted the same genuinely received
body/signature twice through public HTTPS; both200 and complete payment/
subscription snapshot unchanged (no duplicate paid days). No fabricated webhook
used as provider proof; raw event/signature stay in worker/controller memory,
not Git/logs. No further payment needed. Google owner consent/sign-in is the only
remaining check in this window. Still35/36, PY-35 partial; actual Render runtime/
operations and separate release approval remain required. Read session11082 and
remaining-result.json for Google result and automatic cleanup. Never restart a
payment window or rerun prior backup/migration checks merely to resume Google.

Current129 OWNER CONFIRMED SAVED: independently rechecked all three loopback
ports and live HTTPS405/Allow:POST before recording exact races-son URL
confirmation. Original application browser login now PASSED with real secure,
HttpOnly/SameSite cookie; browser storage contains no bearer secret. Original
API initialized a fresh TEST monthly checkout for the new callback; default
browser opened original login and Paystack checkout. Actual payment/webhook and
Google consent are still pending. One separate headless checkout inspection
encountered Paystack's human-verification UI (cf-turnstile-response), no TEST
mode proven and no submission; no challenge bypass/retry attempted. Secondary
empty-frame URL TypeError is a harness diagnostic, not an app/payment failure;
safe frame parsing corrected without repeating inspection. Owner asked to
complete only visibly TEST checkout using Paystack's official fabricated card,
then Google sign-in with approved email. Do not use real cards or automate Google
passwords. Email remains disabled; completed checks not repeated. Read session11082
and remaining-result.json for event/expiry/cleanup before continuing.

Current129 RESUME NOTE (2026-10-20 WAT): owner saved the old george-weight TEST
URL and explicitly requested active-backend verification before payment. Both
george-weight and modes-address windows are confirmed closed, all test ports
stopped, no checkout/result/provider event. A fresh startup hit ConnectionError
on immediate public readiness; retained it and added bounded serial HTTPS
startup retries with exception-class-only diagnostics. Fresh replacement now
PASSES verified TLS and GET /api/payments/webhook returns405/Allow:POST from the
original isolated backend; private synthetic worker status also passes.
ACTIVE URL: https://races-son-letting-indication.trycloudflare.com/api/payments/webhook
Session11082 waits for this EXACT TEST-only setting confirmation, maximum900s.
All older URLs are closed; never infer confirmation from the earlier saved URL.
No payment initiated/completed. Runtime remaining-result.json tracks expiry and
cleanup. After actual owner confirmation, write exact new URL to ignored
remaining_TEST_webhook_confirmed.txt to continue; do not repeat completed checks.

Current129 IN PROGRESS (2026-10-20 WAT): owner reports TEST webhook currently
points to production https://priceyard-api.onrender.com/payments/webhook. No TEST
payment may be completed against that destination. Added remaining-only runner,
reusing the cached binary, original frontend build and existing marked synthetic
PG17 schema. Email disabled; no backup/restore/migration/rollback repeat.
Pre-payment checker naming mismatch (monthly versus original paid_monthly) was
caught before checkout; cleanly stopped that window, retained all results/logs,
corrected checker and verified its naming contract statically against the app.
The first remaining-only george-weight URL is CLOSED; no checkout/provider call.
Earlier replacement modes-address-cdna-safe.trycloudflare.com ran at most900s,
one tunnel at a time, with DB/metrics loopback-only and controlled cleanup.
Owner was asked to save ONLY its TEST webhook /api/payments/webhook, leaving LIVE
unchanged. Await explicit confirmation of this exact replacement URL; no elapsed
time/old confirmation authorizes payment. Runner session30041 expired cleanly;
runtime remaining-result.json is authoritative for current cleanup/state.
After owner confirms new URL, write that exact URL into ignored runtime
remaining_TEST_webhook_confirmed.txt; then original browser login and fresh
TEST checkout can continue (old callback host is closed). Real Google consent
requires approved owner identity. No new features/business/source changes,
production access/settings, push, merge or deployment.35/36 remains; PY-35 partial.
Do not mark this active window passed or clean until its final results are read.

Latest128 PARTIAL VERIFIED (2026-10-20 WAT): ONE public free Quick Tunnel was
opened/closed for real-provider testing; no Render/Supabase database/service
created and settletrack-db untouched. Reused fixed fabricated PG17.11 cluster
55452, identifier7698190245493700556; added one private synthetic schema/role.
Original cluster HBA/config unchanged; process-only loopback bootstrap HBA and
SCRAM application role used, new schema retained, cluster stopped afterward.
Actual public HTTPS gateway, login/Secure HttpOnly SameSite cookies/session,
CSRF403, reset-email send, single-use reset/token replay rejection, old-session
revocation and logout401 PASSED. Paystack TEST initialization for approved2500
monthly plan returns200; no payment was completed/charged. Email provider accepted
ONE message; owner explicitly confirms Received. Existing Google IDs match, but
actual Google account consent/sign-in is NOT yet tested.
Harness-only failures preserved/fixed: Windows pg_ctl pipes caused TimeoutExpired
despite ready server; file-backed control output fixes launcher. Initial browser
lacked existing cached-browser environment; corrected cache launch/close passes,
but public browser workflow remains unverified. UTF-8 capture corrected. Git tar
root backend entry rejected; narrow root handling corrected and application-only
rollback then PASSED locally using exact2cfbfa6 app source: revoked token stays401,
normal login works, security schema retained, no migration or provider calls.
No second tunnel, repeated backup/restore/migration suite, app/business/design
edit, real payment, provider setting change, push, purchase or deployment.
All owned workers stopped;55452/55453/55454 closed.35/36 unchanged; PY-35 partial.
Real Google login, completed TEST checkout/signed provider webhook/replay/public
browser and Render operational/artifact checks remain OPEN. Do not rerun passed
email/reset/API checks. Credentials were found securely; never request their
setup again or paste keys. Only current owner input requested: Paystack TEST
webhook URL (or blank), read-only, to avoid sending TEST events to production.
Next public window must continue only remaining checks, preserve prior result,
reinitialize checkout only if its expired tunnel callback makes that necessary.
Evidence:tools/local-test/evidence/batch-128-provider-tunnel.json; local runtime
result/initial-timeout/rollback-result retained. See docs/PY35_HOSTED_CHECKS.md.

Latest127 CONFIGURATION LOCATED (2026-10-20 WAT): owner explicitly requests secure
inspection of existing local configuration before further setup. Narrow read-only
provider-field classification (no application import, provider/network call,
database URL inspection, credential output/copy or file changes) finds Paystack
secret/public keys markedTEST, backend Google client ID, frontend Google client
ID, Brevo credential and configured sender. Do not ask owner to recreate these
settings or paste keys. Owner approves fidelisnguakaaga20@gmail.com as test email.
Presence/mode are verified; validity, matching Google client IDs/test identity/
tunnel origin and actual email/Paystack receipt are NOT yet verified. Credentials
remain in existing files; original synthetic guard still denies dotenv/transports.
Use only a separately guarded provider runner, pinned synthetic PG17 and explicit
recipient/endpoint restrictions; never expose unchanged mocked preview or load
production DATABASE_URL. Tunnel not started;35/36 unchanged, no hosted PASS claim.

Latest126 PROVIDER INPUT BLOCKER (2026-10-20 WAT): owner approves ONE temporary
free Cloudflare Quick Tunnel for essential real provider TEST checks, synthetic
data only, PostgreSQL private, close tunnel afterward, no charges/production
changes. Workspace already has settletrack-db: DO NOT create another Render DB
or use that unrelated database. Existing PG17 synthetic environment remains the
approved database target. No completed audit/backup/restore/tests repeated.
Read-only harness inspection finds current preview uses memory SQLite, denies
external transports, mocks provider calls and includes local-only test endpoints;
do not expose it unchanged or relax its original guard for real providers.
cloudflared is not on PATH. No dedicated TEST credential storage reference,
approved real email recipient or Google test identity/origin is recorded.
Do not open a public tunnel or download/start tools before these essential inputs
are supplied; do not read.env or reuse production credentials as substitutes.
Next owner input: approved test recipient and secure TEST configuration reference,
or confirmation that keys are ready for hidden local entry. Never request keys
in chat.35/36 unchanged; hosted tests BLOCKED/not attempted, no FAIL/PASS claim.
No app changes, credentials opened, database/tunnel started, provider call,
purchase, push, migration or deployment performed.

Latest125 ACCESS BLOCKER (2026-10-20 WAT): owner confirms Render plugin installed
and independently connected in ChatGPT, both production services auto-deploy
master. Accept those confirmations; do not ask to reconnect or repeat Billing.
Owner reports today's usage:451.6/750 free hours,34MB/5GB bandwidth,25/500 build
minutes,charges0. Remaining298.4 hours,475 build minutes. Conservative reserve
288 production hours from Oct20 00:00 WAT to Nov1, assuming only the one known
production Free backend, leaves10.4hours; cap staging backend at2 TOTAL running
hours, leaving8.4hours beyond that reserve. Reassess only if delayed/new usage or
other Free workloads appear. This is a bounded capacity estimate, not a quota
reservation or an automatic stop guarantee. No paid upgrades/keep-alive/load.
Current session still exposes ZERO Render MCP tools despite ChatGPT installation;
cannot inspect/create/stop staging here, configure test recipients/keys or execute
hosted provider tests. No API key requested, new session started, push, resource,
migration, expense or deployment.35/36 unchanged. Genuine next action: use the
existing Render-connected ChatGPT conversation to perform approved bounded
staging work or make that connection available here; never claim hosted PASS.

Latest124 BLOCKED (2026-10-20 WAT): owner conditionally approves zero-cost staging
and development-branch push only after proving no production deployment/resource
impact. Resumed clean at2c2075b; no completed tests/export/restore repeated.
GitHub repository read succeeds, defaultmaster; development branch search returns
no matches. Remote master.github directory returns404; local workflow directory
absent. Workflow-list API is unsupported by the connector, not proof of no
external deployment hooks. Render usage/live branch bindings cannot be verified
with current tools: Render plugin exists but is not installed/connected; secure
connection offered. No push, staging resource, purchase, migration, provider call
or deployment made.35/36 complete; launch remains blocked, not a failed hosted
test. Need owner install/connect Render under existing account; then inspect
quota/branch/autodeploy settings read-only before exercising conditional approval.
Hosted tests/rollback must not be marked passed until actually executed.

Latest123 VERIFIED (2026-10-20 WAT): resumed clean ataf8aa77 on original-preserved
development branch; prior verified recovery is an ancestor. No completed backup,
restore, migration or regression tests repeated. Two bounded TLS-only handshakes
to existing Render frontend/backend pass trusted chain/hostname andTLS1.3; no
HTTP request, account/provider/database access or configuration change. This is
only certificate evidence, not hosted candidate/session verification. Static
backend/app tree equals previously checked security-aware rollback candidate;
only migration privacy safeguard differs. Hosted rollback runtime remains open;
retain current grants/revocations and never run old migration/downgrade. Google,
HTTPS sessions, Paystack TEST/webhooks, delivery and monitoring/scheduler checks
need an approved separate test target/provider setup. No such target is recorded;
do not replace production.35/36 complete, PY-35 partial. Next owner step: report
existing non-production Render service name/URL or none, without secrets/settings
changes. No push, merge, migration, deployment, paid service or unrelated feature.
See docs/PY35_HOSTED_CHECKS.md for bounded evidence and exact remaining scope.

Latest122 VERIFIED (2026-10-20 WAT): owner-started Docker4.96 ready. Protected
local PG17 clone rehearsal PASSED in54.6seconds, using the existing EFS export
and cached image; no repeated production export or archive extraction. Exact0022
upgrade, full transaction ROLLBACK, injected-error atomic recovery, all59 original
table values/counts, original catalog/sequences and old user-column access/grant
options pass. Pristine0021 remains intact. Synthetic counter/revocation constraints
and restart recovery preserve both original records and new security evidence;
native checksums pass and RAM target is removed. Actual provider defaults exposed
the new security objects in the earlier local attempt:0022 now removes only new
security exposure, preserving old user-column rights. Four fabricated privacy
cases pass, including inherited/dependent-grant atomic refusal. Offline SQL uses
named parameter style to avoid raw-psql percent escaping. Helpers preserve clone
owner, DB grants and recorded settings; bounded batched COPY avoids excessive
Docker processes. Independent diff review passed. Original and retrieved encrypted
archive SHA256 remain unchanged; original recovery report retained. Docker remains
owner-running; other container settings/volumes untouched. Unused VM swap was
temporarily disabled before private transfer; no persistent WSL setting changed.
35/36 complete; PY-35 partial. Hosted HTTPS/Google/Paystack TEST/delivery/scheduler/
monitoring/runtime and security-aware application rollback checks remain unverified,
along with non-DB recovery coverage, recovery targets and controlled cutover.
No production connection/change/migration, push, merge or deployment. Evidence:
tools/local-test/evidence/batch-122-0022-rehearsal.json; docs/PY35_0022_REHEARSAL.md.

Latest121 BLOCKED (2026-10-20 WAT): owner explicitly approves0022 on an isolated
restored PG17 clone, including safe rollback/recovery; production remains barred.
Prepared bounded rehearsal using existing protected export/cached image, no new
backup/password/provider connection. Actual offline Alembic0021:0022 compilation
and destructive downgrade refusal pass; three admission guards pass. Three
focused synthetic authentication rollback regressions pass with socket/dotenv/
external DB guards. Candidate2cfbfa65447d51b225a0d367433709c25bd6da4a backend/app
tree matches currentfcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed.
One bounded Docker4.96 startup attempt failed readiness90seconds BEFORE any
Linux target/controller/customer-data load/migration. Exact cause unconfirmed;
installed WSL2.6.3 is not evidence an update is required. No automatic retries.
Graceful Desktop cleanup was unresponsive; only verified own-started Docker
processes stopped, exact hash-archived temporary config removed, original stopped
Docker/no-.wslconfig state restored. Original backups/recovery evidence unchanged.
Actual clone upgrade/transaction rollback/restart/provider-role permission checks
remain NOT RUN. Never claim original0021 application is security-safe rollback.
35/36 unchanged; PY-35 partial. See docs/PY35_0022_REHEARSAL.md. Next owner action:
open Docker Desktop and report its engine/startup message; do not install/reset
or alter settings automatically. No production migration, push, merge or deploy.

Latest120 VERIFIED (2026-10-20 WAT): individual encrypted7z downloaded from
owner-confirmed private Google Drive now matches the original encrypted archive
and recorded recovery SHA256 exactly:
f26ed1548064ca95666b0459ae5187ab583e13bff566df16fcecf7b4a8d67045.
Both files174448 bytes. No extraction, decompression, modification or deletion
of either backup; no repeat backup/restore, production access or migrations.
Off-computer ciphertext retrieval verification PASSED; earlier ZIP-wrapper
blocker superseded. Actual backup gate remains partial for file/provider config
coverage and accepted recovery targets.35/36 unchanged; PY-35 partial, no push,
merge or deployment. Remaining release gates retain their existing status.

Latest119 CHECK (2026-10-20 WAT): original encrypted7z SHA256 rechecked and matches
the verified recovery evidence. Downloads contains a Drive folder ZIP, not the
individual7z. ZIP directory lists exactly one matching-name encrypted archive,
174448 bytes, but Deflate compression prevents direct raw-ciphertext comparison.
No archive contents extracted/decompressed, files modified/deleted, backup/export
repeated or production accessed. Downloaded7z SHA256 is NOT verified or mismatched;
owner must download the individual7z rather than its folder under the current
no-extraction instruction. Wrapper SHA256 recorded in the actual gate ledger.
Narrow next-step review confirms0022 protected-clone rehearsal needs migration
approval; preserve0021 and security evidence rather than running downgrade.
Hosted HTTPS/Google/Paystack TEST/delivery/monitoring gates still need approved
test setup. Render master auto-deploy/build migration remain controlled-release
blockers.35/36 unchanged; no migration, push, merge, deployment or new feature.

Latest118 REVIEW (2026-10-20 WAT): owner confirms encrypted archive uploaded to
private Google Drive; downloaded-copy SHA256 verification is still pending.
Current Git/evidence reviewed; completed recovery/tests were not repeated.
0022 statically follows0021, adds auth_version and revocation storage/indexes;
its downgrade intentionally refuses to delete revocation evidence. Actual-clone
migration and security-compatible application rollback rehearsal remain unrun.
Owner currently prohibits migrations, push and deployment; no such commands run.
No approved hosted test URL/provider setup is recorded, so hosted Google/HTTPS
sessions, Paystack TEST/webhooks/recovery, approved-recipient delivery and hosted
monitoring/scheduler/runtime checks remain blocked/not attempted, not failed.
35/36 complete; PY-35 partial. Preserve all original work; no live service access.

Latest117 COMPLETE (2026-10-20 WAT): actual encrypted database backup AND protected
isolated restoration verified. Final real restore37.2 seconds,59 tables: all row
counts/content SHA256 fingerprints match, recorded schema/columns/types/defaults/
constraints/indexes/RLS/roles/memberships/settings/effective permissions match,
sequence/large-object observations and native checksums pass. Revision remains
0021_feedback_screenshot; NO migrations, source connections this batch, uploads,
push/merge/deploy or application changes. Original archive SHA256 unchanged.
Private latest-production-backup-status.json now confirms restoration; protected
run real-ram-restore-result-private.json is passing. All test containers removed;
Docker/WSL stopped; attempt3 resource config archived/hash-checked/removed and
original no-.wslconfig state restored. Cached public image retained; no original
Docker files/container configuration deleted or edited.
Actual Supabase recovery differences were resolved without removing guards:
runtime LOAD verifies Nix-packaged supautils/safeupdate (not a core-libdir guess),
matching original bootstrap supabase_admin preserves explicit GRANTED BY clauses;
only duplicate CREATE of that existing verified administrator is skipped. Two
recorded extension view owners and two provider-initial GraphQL schema ACLs are
replayed exactly from protected metadata, preserving owners/grant options. ACL
order is canonicalized, live column order retains all fields while excluding
irrelevant dropped-attribute numbering gaps, and seven equivalent CHECK casts
are reparsed by PostgreSQL on empty temporary LIKE tables before comparison.
Nine targeted fabricated checks pass, including rejected unbounded UPDATE,
grantor/permission/view ownership, dropped-column gap and valid/invalid CHECK
values; no user-facing business rule changed. Earlier failed evidence retained.
Versioned secret-free restore helper embeds only the identical catalog query;
static equivalence and duplicate-run refusal pass, no second real restore run.
See docs/PY35_VERIFIED_RECOVERY.md and docs/PY35_ACTUAL_RELEASE_GATES.json.
35/36 complete; PY-35 remains partial. Next owner step is a separately retrieved
encrypted archive copy (the existing Drive PFX is NOT that copy).0022 actual-clone
rehearsal, file/provider configuration coverage and external hosting/Paystack TEST/
Google/delivery/scheduler/monitoring/cutover gates remain open. Baseline local-only
RELEASE_GATES.json stays a fixture; new actual ledger records current evidence.
Do not repeat source backup, passwords, completed tests or restore; no deployment
until remaining approval/setup/compatibility/rollback requirements pass.

Latest116 IN PROGRESS: owner replaced exhausted500MB mobile bundle with17GB;
host RAM now4.16GiB free. Public Docker-registry TLS passes. With2GiB/one CPU/
swap0 temporary WSL cap, existing engine29.2.1 becomes ready; do not assert
network exhaustion caused prior failure (memory limit and connectivity changed).
Docker auto-restarts three unrelated EasySpend containers; do not change their
files/configuration. Attempt2 stopped and its temporary config archived/removed.
Attempt3 remains active with temporary2GiB cap (private attempt3 resource record).
Official Supabase17 image17.6.1.136 selected from official compose; Linux amd64
manifest sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b;
367203535 compressed layer bytes downloaded, no credentials/cloud project/charge.
New verify_supabase_ram_fixture.py verifies Docker configuration and actual
tmpfs/read-only/no-network/no-swap512MiB runtime guards, exact five extension
versions including Vault0.3.1, en_US.UTF-8, and sequential fabricated PG17 dump/
restore with matching digest and checksums. PASS; temporary container removed.
First fixture used removed SHOW lc_collate; changed to pg_database catalog query,
preserved failed evidence and reran only that test. No app defect/change implied.
Private ram-fixture-result.json passed; image-result and public manifest metadata
saved. Real backup SQL reviewed privately: no PROGRAM/ALTER SYSTEM/LOAD/file IO/
untrusted language, no foreign server/subscription/custom tablespace, Vault empty;
preload libraries supautils/safeupdate and six provider event triggers require
the reviewed isolated Supabase profile. Real backup NOT yet loaded/restored.
35/36 unchanged; no production connection, migration, push/merge/deploy. Next
review/prepare protected real restore; preserve old simple helper guards and
source backup. On exit stop test-started Docker and archive/remove only the
owned attempt3 temporary .wslconfig after hash validation, restoring absence.

Latest115: owner READY; host still only2.61GiB free. For one fabricated-only
feasibility attempt, created previously absent .wslconfig limiting the sole WSL
docker-desktop distro to1GiB/one CPU/swap0; original absence recorded. Started
existing Docker Desktop (no image download). Explicit local Linux named-pipe
engine query timed out at15 seconds before cached-image/container inventory.
Guest /proc confirms920068KiB total,30520KiB available,swap0. No kernel OOM
confirmed; available local logs show startup timeout, not an established root
cause. Do NOT claim proven OOM or assume another startup will fix compatibility.
No new test container/image, customer restore, SQL, production connection or app
edit. Stopped attempt rather than raising limits under host memory pressure.
First graceful Docker stop returned125; subsequent normal stop remained pending
during cleanup and eventually returned0. Stopped only test-started Docker PIDs
and its WSL distro. Verified WSL stopped, no Docker/WSL
processes left. Archived new .wslconfig under private backup root, hash checked
before removing only that newly-created file; original no-config state restored.
Private docker-feasibility-result.json records bounded failure/cleanup. Backup
archive preserved;35/36, full recovery still NOT VERIFIED. Before retry, require
adequate host memory and resolve Docker startup readiness; a normal owner reboot
may free memory but is NOT a confirmed Docker fix. Do not repeat source backup,
request passwords, install/download images, raise limits or use unencrypted
Docker volumes automatically. No migration/push/merge/deploy.

Latest114: read-only local Docker feasibility check only; no daemon/container
startup, production connection, image download or customer restoration. Docker
Desktop/CLI are installed; WSL docker-desktop is stopped. Existing Docker data
VHDX is NOT EFS-encrypted; C: BitLocker remains off, so normal Docker volumes are
not an approved plaintext customer-data destination. Host has15.7GiB physical RAM
but only2.3GiB available at inspection; do not start an unconstrained stack given
earlier freezes. Private saved manifest shows Vault tables have NO rows and no
public-schema functions; no Vault root-key request justified by this snapshot.
Candidate next step: synthetic-only single-container RAM/tmpfs feasibility test,
with network disabled, read-only root, no persistent data/logs, one CPU, bounded
memory and verified swap prohibition before considering real data. Docker docs
warn tmpfs can swap; RAM-only protection is NOT yet verified. Do not simply put
the real dump in Docker or claim the restore gate passed. Need free RAM before
runtime testing; no settings/install/partition/service changes in this check.
35/36 remains; backup success preserved and full recovery still unverified.

Latest113: ACTUAL production backup completed through verified direct TLS on
owner's hotspot. Hidden owner credential/passphrase entry; source identity,
read-only and permissions passed. Run20261019T213738Z: full custom dump and roles
without passwords,59 table fingerprints, catalog/schema/sequence/large-object
evidence;7-Zip AES/filename encryption, independent EFS decryption and file
digests passed. Source closed; helper stopped successfully in102.8 seconds.
Independent local archive SHA256 and recovered bundle digests reconfirmed. Root
latest-production-backup-status.json now records integrity passed, restore review
required. This is the first verified REAL archive, not a synthetic result.
Restore safely BLOCKED BEFORE EXECUTION: Supabase Vault0.3.1 missing from local
PG17 extension files; source locale en_US.UTF-8 differs from reviewed C-only
restore path;103 functions and one publication require provider/executable-object
review. No automatic omission, SQL execution, extra server or weakened guard.
Need approved compatible isolated restore target/protected storage and reviewed
provider coverage; actual encrypted archive second off-computer copy also not
verified (existing verified Drive copy is the EFS recovery key, not this archive).
All customer exports remain EFS or AES-encrypted outside Git. No source records
changed, app edits, migrations, uploads, push/merge/deploy.35/36 remains; PY-35
partial and release blocked until actual restoration/remaining live gates pass.
Private evidence:run restore-readiness-private.json and latest backup status.

Latest112: owner's phone hotspot supplies IPv6 (MiFi did not); public/default
DNS and direct TCP5432 succeed. Credential-free PostgreSQL TLS handshake verifies
same-project direct hostname and existing pinned CA, TLS1.3. No login/SQL in
those connectivity checks. Initial sandbox socket denial was resolved through
normal escalation, not interpreted as a provider/network failure.
Prepared separate private Start-PriceYardDirectEncryptedBackup.py/.ps1; original
pooler helper/launcher preserved. Only pinned host/user, credential-only pooler
URL recognition, TLS metadata label and console wording differ. Server-side TLS
must still be true; verify-full, recovery/EFS, read-only identity/permissions,
snapshot/export/encryption/integrity and restore-review guards remain unchanged.
22 focused offline checks and launcher syntax pass; no database server/full drill
rerun. Direct helper SHA256:bcd92f38c3ca888117c6c9cd5488c8ed66e4639ed37f42ebdae4dddf4731d686.
Owner says continue; ONE approved visible hidden-entry direct-backup window opened
(process29332) after hash/no-overlap/no-success checks. Await private owner entry
and real result; no backup or restoration success claimed. No application edits,
provider settings changes, migrations, push/merge/deploy.35/36 unchanged. Stop on
any source, permission, coverage, archive or restore-inventory failure.

Latest111: controlled attempt stopped at the retained upstream TLS safeguard.
Private metadata from run20261019T133223Z confirms authenticated metadata read,
client TLS in use with verify-full, database postgres, role postgres, read-only on,
PostgreSQL170006 and installed revision0021_feedback_screenshot. The only failed
source check is pooler_to_database_ssl=false. Exact error: Source preflight
rejected: pooler_to_database_ssl; no dump created. This describes the pooler to
database hop; client to pooler TLS passed. No password/parsing failure inferred.
Only encrypted private error/metadata and trusted CA files exist in this run;
no dump/archive, real success status or active export process. Backup/restoration
remain unverified;35/36 unchanged. No retry/window, security-policy change,
application edit, migration, push, merge or deploy. Next minimum decision: a
verified end-to-end TLS connection path, such as same-project direct connectivity
if available, before another approved attempt. Direct reachability is unverified;
do not change live SSL settings or remove this guard automatically.

Latest110:owner stops feature work and explicitly approves visible local console
with hidden input for ONE controlled production backup and isolated restoration;
this resolves the earlier review ambiguity/refusal. Initial Git clean atb788160;
backup/restore SHA256 match offline-verified7b422e1. No tests/setup/audit repeated.
No overlapping backup process or real success report. Approved launcher opened
successfully(process37048) in Render-URL mode, no alternate launch/bypass. Await
owner-private input/result; no backup/restoration success claimed. Stop at any
source, permission, coverage, integrity or restore-inventory failure; no automatic
unreviewed Supabase restore or migrations. No new features, credential logging,
push/merge/production migration/deploy.35/36 unchanged until real evidence passes.

Latest109:owner authorizes proactive local interface/security/maintainability
enhancements without routine permission prompts; explicit refusal to open a
credential window remains in force. Completed one dashboard reliability/privacy
batch, preserving all prior work. Original browser reproduces two bugs:late
checkout success redirects after navigation, late failure displays an obsolete
global toast. Fix binds private reads/payment/clipboard completion to the active
account/page, aborts obsolete requests, clears account data before paint, cleans
copy timers and guards duplicate submissions. Current-account retry/redirect stay.
Verified:TypeScript/Vite isolated build;8 targeted browser checks including
cross-account stale error and read cancellation;14 Admin cards/totals/one-summary
request/outage recovery; rendered Dashboard JSX exactly matches prior source.
No external browser requests/page errors/real payments. One preview/browser phase
at a time, existing dependency snapshot reused. Backend/schema unchanged, so no
native PostgreSQL or backend suites rerun. Initial dummy success URL redirected
through app fallback; harness corrected to existing local FAQ route before
baseline reproduction. No guard bypass. Evidence:runtime/enhancement-109-summary
and dashboard-race-before/after.json; docs/LOCAL_DASHBOARD_ENHANCEMENT_109.md.
Preview synthetic-only127.0.0.1:55446.35/36 unchanged; PY35 real backup/restore/
live release gates still pending. No credential window, production, migration,
push/merge/deploy. Verified local commit authorized.

Latest108:owner designates THIS conversation main session and resumes PY35 from
actual latest Git state. Clean branch at0b9dab3285ee19a0a3d61e7fc13726a352c7c3bf;
reported offline7b422e1 and latest0b9dab3 are confirmed ancestors, all changes
preserved. master76dbd27/backup2589910 unchanged. Read saved offline evidence:
whole-procedure and restore-guard reports passed; all four private code hashes
match verified7b422e1 documentation. Watchlist107 evidence/history retained.
No tests/setup/audit repeated, no application changes. No active backup process or
real latest-production-backup-status result.35/36; actual backup/restore and live
release gates unverified. Next ONLY blocker to the previously approved controlled
attempt:explicit clarification that a visible local PowerShell console is allowed
while credential input remains hidden; prior automatic review rejected that
launch before execution. No bypass/alternate launch. No production connection,
credential request, export, migration/push/merge/deploy in this batch. Main-session
handoff persists here; do not revert to outdated helper instructions.

Latest107:owner authorizes useful app/interface/security/maintainability/health
enhancements. Completed one focused LOCAL watchlist reliability/privacy batch;
no new audit, redesign, policy, measurement, dependency or schema changes.
Old compiled source matches3cd973d Watchlist blobd870d2681987263ea46e37e8af2c24ab8b880106.
Browser reproduces3 defects:stale success resurrects a removed item, stale503
replaces a newer success, and an old-account save reloads a disposed view. Fix:
abort superseded reads plus generation/token checks, clear private rows/draft
targets before account-switch paint, ignore obsolete mutation errors/toasts/
finalizers, and forward AbortSignal through existing provenance helper. Original
JSX/styles/labels, measurements, all14 Admin cards and business rules preserved.
Verified:2 watchlist API/storage/ownership tests; TypeScript/Vite build using the
same dependency snapshot;8 browser checks pass after3 expected baseline failures;
14 real-API fake-fetch/provenance/cancellation checks; all14 dashboard totals,
single summary request and outage/reload recovery. External browser requests0,
page errors0; TCP/DNS/providers denied by existing synthetic guards. Initial test
harness used blocked Node route.fetch and assumed login could switch accounts
without logout; corrected browser-only transport/logout, without relaxing guards.
Final independent read-only review passes. Evidence:tools/local-test/runtime/
enhancement-107-summary.json and docs/LOCAL_RELIABILITY_ENHANCEMENT_107.md.
Native PostgreSQL not rerun:backend/schema unchanged. Only one browser/test phase
at a time; existing snapshot reused; preview stays synthetic on127.0.0.1:55446.
35/36 unchanged; PY35 real backup/hosting/provider gates remain unverified.
Blocked production credential-window launch was NOT retried. No production,
credentials, migration/push/merge/deploy. Local verified commit authorized.

Latest106:owner approves ONE controlled read-only production backup and isolated
PG17 restore using verified7b422e1 procedure. Current Git initially clean at that
commit; application/private helper code unchanged. Local reconfirmation PASSES:
owner-only ACL/EFS, current non-exporting private-key sign/verify challenge,
unchanged verified recovery-copy evidence, free space, helper/restore hashes and
no running backup/diagnostic. Automatic approval review REJECTED the combined
preflight/window-launch command BEFORE execution, interpreting a visible
PowerShell window as conflicting with requested hidden credential entry.
The separate local-only reconfirmation was approved and passed. No workaround,
alternate launch, credentials, production connection, export/backup, local real
data restore or migration occurred. No actual backup attempt was consumed.
STOP:explicit clarification/approval for a visible private local console whose
credential input is hidden is needed before another launch review. Do not ask
for secrets in chat or repeat completed setup.35/36; actual backup still unverified.

Latest105:owner authorizes correction/review and complete FABRICATED offline
verification only; no prompt, credentials, production connection or actual backup.
Corrected unsupported psycopg3.3.6 PGconn.ssl_attribute call; supported native
ssl_in_use and verify-full remain mandatory. Also fixed Win32 EFS invalid-handle
signedness, explicit UTF8 connection encoding and passphrase-wait transaction
expiry; refresh identity/catalog/privileges after the wait. Prior helpers retained
outside Git. Added guarded local restore primitives, fuller catalog/role/sequence/
large-object evidence and exact-main offline integration. Full PG17.11 TLS -> dump
-> AES256/header encryption -> independent decrypt -> fresh PG17 restore PASSES:
7 fabricated tables, matching rows/hashes/schema/roles, zero checksum errors.
11 integration/security checks plus12 small restore-guard checks pass; launcher
syntax/pins and independent read-only code/evidence review pass. Wrong passwords,
CA/hostname, unencrypted paths, corruption, unsafe settings/provider objects and
non-fresh/non-local targets fail closed. One server at a time,8 connections/32MiB;
both stopped. Initial Windows inherited-output-pipe timeout fixed in test runner;
failed synthetic fixture retained. No app source, business rules, recovery keys or
real records changed; no migrations/push/deploy.35/36 remains:actual Supabase
inventory, pooler-hop TLS, permissions and recoverable production backup remain
UNVERIFIED. No setup repetition required. STOP for owner approval before any
new live attempt. Evidence/hashes:docs/PY35_OFFLINE_PROCEDURE_VERIFICATION.md.

Latest104:owner explicitly approves ONE targeted read-only pooler diagnostic.
Prepared Inspect-PriceYardPooler.ps1/.py outside Git, reusing owner ACL/EFS/key,
pinned source/CA and hidden Render URL parsing. Three fabricated safety tests pass.
Opened private prompt(process40776). Captures exact metadata/Python types/client
encoding and both TLS hops, no backup/native export tools. If actual SQL_ASCII
bytes observed, tests UTF8 via transaction-local setting in SAME connection only;
no persistent config change or second authentication. As of this update awaiting
owner entry/result; no exact mismatch or successful correction claimed. No extra
SQL Editor request, archive passphrase, migration/push/deploy.35/36 unchanged.
Latest103:owner SQL Editor results170006/postgres/[0021_feedback_screenshot]
match expected major/database/revision. Existing failed pooler run still has NO
source-preflight-private.json; only generic85-byte guard error. Remaining role,
read-only and pooler-to-database SSL observations were discarded. Cannot identify
exact original mismatch from SQL Editor's different connection; earlier metadata
query was insufficient for pooler-session diagnosis. No guess/TLS bypass or
automatic restart. Authentication in last attempt already proved successful.
Current helper would capture exact per-field values on a new privately entered
connection, but owner forbids repeating the same process before diagnosis; such
new observation remains required, not fulfilled by supplied three values. No
credentials retained to reconnect autonomously; no backup/export/restore, new
tests/setup, migrations/push/deploy this batch.35/36 unchanged; resume blocked
by missing session evidence rather than bad supplied SQL results.
Latest102:Render URL attempt20261019T080749Z authenticated successfully and read
source identity/Alembic metadata, then failed helper's generic combined validation
guard. NOT authentication/URL-decoding/network denial. Error85bytes omitted actual
values/failed component; cannot honestly identify exact mismatch from retained
logs. Only encrypted CA/error log, no dump/roles/archive. Permissions checked only
for metadata reached, business-table privileges/backup not run. Identified design
ambiguity:pg_stat_ssl behind pooler reports its database hop, not client TLS;
this is a possibility, NOT confirmed failed field. Preserved helper/logs; added
per-field failure labels and protected metadata before guard, explicit client TLS
check; retained EVERY prior requirement, no weakening. Two new local tests pass,
no production retry/prompt reopened/credentials read. Owner next:bounded read-only
SQL Editor metadata using existing Google/GitHub login, no DB password; prepared
docs/sql/PY35_SOURCE_GUARD_DIAGNOSTIC.sql. Editor cannot prove pooler-hop TLS.
Details/hash:docs/PY35_ACTUAL_BACKUP_RUN.md. No migration/push/deploy;35/36 stays.
Latest101:owner uses Google/GitHub for Supabase and authorizes private reuse of
existing Render backend DATABASE_URL, no reset/settings changes. Prepared explicit
-UseRenderDatabaseUrl hidden-input mode outside Git:SQLAlchemy URL parser matches
app semantics, decodes password once, validates exact project/user/database,
uses ONLY password with existing pinned pooler5432/verify-full. URL never used
as target/options or written to diagnostics. Clears current clipboard after input
(Windows history separate); different archive passphrase enforced. Prior helper
versions retained. Five fabricated URL/secret-safety tests pass, no live calls.
Private URL prompt opened(process70696); owner manually copies from Render
priceyard-api Environment without Edit/Save/Deploy. No credential read by Codex;
auth/export/restore results still unverified. New hash/steps:
docs/PY35_ACTUAL_BACKUP_RUN.md. No migrations/push/deploy;35/36 unchanged.
Latest100:second owner attempt fails with server FATAL password authentication
failed, not TLS. Latest protected run20261019T074829Z has only encrypted CA/error
log; no dump, roles, archive or saved success. No native backup process active.
Source reached but login rejected; SQL permissions remain NOT CHECKED. Verified
native PG17.11 versions, same major as reported17.6; failed login never reached
them. Mocked test confirms password passed unchanged via keywords including
special characters; cannot infer wrong entered password versus credential pairing.
Preserved old helpers/diagnostics. Improved auth-first flow:archive passphrase
only after login/identity/initial privileges; no automatic retries or resets.
Three new mocked auth tests pass. No production retry or backup window reopened:
valid existing DB credentials must be verified privately first; none retained.
Details/hash:docs/PY35_ACTUAL_BACKUP_RUN.md. No migrations/push/deploy;35/36 stays.
Latest99:owner reports BACKUP STOPPED. Private diagnostic identifies TLS
certificate verification failure before authentication/SQL/dump; failed run
supabase-backup-20261019T073609Z has only encrypted public-root PEM/error log,
no database dump/archive. Preserved all files and prior helper/launcher versions.
Cause:Windows public roots do not include Supabase's private CA. Downloaded public
CA from HTTPS URL confirmed in official dashboard source; validated root properties,
self-signature/validity and pinned DER SHA256. Replaced per-run trust only;
verify-full unchanged, Windows trust store untouched. Three new CA guards pass.
An initial credential-free driver probe was inconclusive(CONNECTION_OTHER), not
counted as success; subsequent SSLRequest/TLS-only handshake verifies certificate/
hostname with TLS1.3, no startup/authentication/SQL sent. No credentials retained
or customer data inspected. Corrected launcher reopened(process69520), awaiting
private prompts. New helper hash/docs:docs/PY35_ACTUAL_BACKUP_RUN.md. Backup and
database restore still UNVERIFIED; no migrations/push/deploy.35/36 unchanged.
Latest98:owner closed the private backup window. Process/metadata-only check
confirms no surviving backup/native dump/archive process, no supabase-backup run
folders, no production archive and no saved backup result. No incomplete export
files found. Excluded the inspection shell itself from process matching. Existing
helper hash matches its reviewed launcher; reopened the SAME owner-private
procedure in visible PowerShell(process69720), no setup tests repeated, no files
deleted, no password/customer contents read. Actual export/restore still unverified;
await owner-local prompts/result. No migrations/push/deployment.35/36 unchanged.
Latest97:owner explicitly authorizes actual encrypted Supabase backup and isolated
restoration, no migrations/push/deploy. Owner confirms private Drive recovery copy;
read non-secret second-copy report:retrieval digest matches, privacy owner-confirmed
(not queried). Existing setup/PG17/encryption suites not repeated. Prepared
Start-PriceYardEncryptedBackup.ps1/.py outside Git with pinned source, hidden
owner prompts, verify-full TLS/public Windows CA roots, readonly source/snapshot,
full custom dump/password-free roles, same-snapshot table digests, AES256/header
archive and verified EFS-decrypted copy. Four NEW guard tests pass; visible owner
PowerShell launcher opened (process42268) for private prompts. Actual connection/
export/results NOT observed or verified; owner must enter existing DB password
privately. Launcher preparation path-variable error fixed before
execution. Restore remains NOT RUN; managed-object/extension/isolation review must
precede executing restored SQL. Details:docs/PY35_ACTUAL_BACKUP_RUN.md.35/36 stays.
Latest96:owner reports recovery helper succeeded. Independently checked only
non-secret validation metadata and ciphertext hash/length: AES256 protection,
matching private key and RSA challenge passed;2708-byte PFX matches saved digest.
No key decrypted by Codex. Separate off-computer recovery copy not yet verified.
Prepared owner-operated Confirm-PriceYardRecoveryCopy.ps1 outside Git; syntax
check passes, real retrieval comparison NOT executed. Owner uploads only the
password-encrypted PFX to private My Drive, downloads it and compares ciphertext;
sharing privacy is owner-confirmed, not independently queried. See current step
in docs/PY35_CONNECTION_AND_KEY_CHECK.md. No repeated database/app tests, source
connection, customer export, upload by Codex, migration or deployment.35/36 stays.
Latest95:owner supplied Session pooler aws-0-eu-west-2.pooler.supabase.com:5432,
postgres database, postgres.lrvpjfbtmftjkzaxbunk user. No password, connection or
export. Existing EFS workspace/probe/ACL reverified; no recovery PFX exists at
instructed locations. Owner-local Save-PriceYardRecoveryKey.ps1 prepared outside
Git:SecureString prompts, NoClobber AES256_SHA256 export, matching certificate/
private RSA challenge with ephemeral loading, no cert-store import/deletion.
Six fabricated validator tests pass; real owner key workflow NOT executed. Next:
owner runs helper and replies READY/error; no secret values in chat. Details:
docs/PY35_CONNECTION_AND_KEY_CHECK.md. No redundant native/app tests, production,
customer export, migration, upload, push/merge/deploy.35/36 still/PY-35 partial.
Latest94:owner rejects partitions/disks/unnecessary infrastructure. Built-in EFS
works on new PrivateRestoreEfs folder outside Git. One newly necessary PG17 EFS
restore check passes using existing fabricated dump, no repeat export/crypto/full
suite:5 tables/10 rows/roles/schema/sequences/grants match, all1,302 new data/log/
temp files EFS-encrypted, checksums pass, cluster55452 stopped. EFS recovery key
not exported/verified; actual backup still not done. No production credentials
available; async owner question asks only Session pooler host/port/db/username,
never password/URL. GitHub connector read-only repo/master checks succeed with
caller permissions; no repository-access grant needed or remote writes performed.
docs/PY35_MINIMUM_BACKUP_RELEASE.md contains current shortest sequence/owner steps.
Old Disk Management/VHD proposals superseded.35/36 complete/PY-35 partial; no
production, customer exports, migrations, uploads or deploy. Key/access still gate.
Latest setup93:owner confirms C: BitLocker OFF. Portable PG17.11 bin/share/lib
prepared outside Git from official PostgreSQL-linked EDB source, no services/PATH
changes. Five-table/ten-row fabricated dump/roles/AES-256/header/decrypt/independent
cluster restoration passes; rows/schema/constraints/indexes/sequences/ownership/
roles/grants match. One server at a time,12 connections/32MiB buffers, fsync and
checksums; all new clusters stopped. ExistingPG18 untouched. Native Windows pipe
startup stall corrected to file logging; retained initial stopped fixture.
NO actual customer-data protection/backup readiness:BitLocker off and admin-only
encrypted volume/host protection step pending. These fixtures are SYNTHETIC ONLY.
docs/PY35_PG17_SETUP_RESULTS.md records exact results and owner next step.
35/36 complete; no production, customer export, app migration, upload or deploy.
Latest setup92:owner-installed7-Zip26.04 passes eight synthetic encryption checks:
AES-256/header encryption, missing/wrong password listing/extraction rejection,
correct listing/integrity and exact restore.146 fabricated bytes/401-byte archive,
single worker/1MiB dictionary. All test runners/files/results outside Git in the
private folder; temporary password stdin-only, never saved/displayed or retained.
Initial bare-p read-switch harness error corrected/preserved, no ACL bypass.
Archive encryption ready; overall backup NOT ready:PG17/disk encryption/private
restore storage/source access and actual restoration still pending. No production,
exports, uploads, database/migration commands or deployment. Scope/results:
docs/PY35_WINDOWS_BACKUP_SETUP.md.35/36 complete; no live gate newly passed.
Latest setup91:owner requests free Windows preparation, optional encrypted Drive
copy. Created/verified EMPTY ACL-restricted folder outside Git:
C:\Users\HP\AppData\Local\PriceYardPrivateBackup. NOT encrypted. Found bundled
7za23.01/standardPG18; PG17 absent there. WindowsPro/BitLocker tools present,
protection status unverified. No downloads/installs, production, exports, restores,
uploads or migrations. Next:standalone current7-Zip, then encrypted workspace/PG17
and synthetic setup drill. docs/PY35_WINDOWS_BACKUP_SETUP.md. No live gate passed.
Latest owner evidence2026-10-19/batch90:reported production inspection17.6,
14 MB,0021_feedback_screenshot. Static22-file chain confirms only0022 pending;
earlier migrations unchanged vs master. Full schema compatibility not established.
No repeated inspection, production connection or migration. Next:confirm private
encrypted storage outside repository/cloud sync; then reviewed PG17 tools/restore
target/private access. ExistingPG18 synthetic environment preserved. Details:
docs/PY35_MANUAL_BACKUP.md. No backup/restoration success or new live gate pass.
Latest preparation:batch89 records owner-confirmed Supabase priceyard,
lrvpjfbtmftjkzaxbunk, Free/no managed backups. docs/PY35_MANUAL_BACKUP.md and
docs/sql/PY35_READ_ONLY_PREFLIGHT.sql prepare a metadata-only owner-operated
first step. No production SQL, export, restore or migration has run. Stop before
operator access until secure connection/storage/isolated restore target established.
Latest planning update:batch88 records owner-confirmed Render service IDs,
repository/master links and deployed labels. Backend Auto-Deploy On Commit and
build-time `alembic upgrade head` are explicit release blockers. Do not push/merge,
rebuild, change production settings or run migrations. Next:owner supplies only
Supabase project reference/plan/backup availability, then approves a bounded
read-only compatibility review and separate actual-backup/isolated-restore scope.
docs/PY35_FINAL_REVIEW.md records the sequence; no production gate passed.
Latest verified: batch87,35 complete /1 partial or pending:35.
Resumed actual5bce117 and preserved both interrupted expiry files before editing.
Confirmed/fixed single-account expiry GET overwriting a concurrent renewal;
307 backend tests, five focused native PostgreSQL cases (twelve GET/payment
interleavings), purchased-value/review/eight-role browser checks and14 Admin cards
pass. Details/access blockers:docs/PY35_FINAL_REVIEW.md. No release authorization.
Owner chose existing local isolation with no new cloud resources. Identified
remaining local TLS/browser and simulated email transport gaps verified86; see
docs/PY35_OFFLINE_READINESS.md. Public-host/provider/actual-record gates stay open.
Owner authorized notification URL fix and staging instructions2026-10-18. Exact
setup checklist:docs/STAGING_SETUP_GUIDE.md. External checks are Blocked/not
attempted, not failed product tests; batch84 initial failures remain historical.
Owner approved safe Phase 1 staging/testing2026-10-18, without production access.
Separate staging package and synthetic checks pass; hosted/provider prerequisites
were not supplied. See docs/PY35_PHASE1_REPORT.md and docs/PY35_PHASE1_RESULTS.json.
All currently authorized local PY-35 preparation is verified; nine live approval
gates remain explicit in docs/OPERATIONAL_READINESS.md and docs/RELEASE_GATES.json.
Local success does not authorize production release or establish36/36 completion.
PY-20 committed558f756eea2eb7db727708b9a72f81e5f40fd5a7 successfully before
advancing this count. History uses one ordered query and100-row ORM batches,
without truncation. Browser memory still scales with the selected full result;
this is not an infinite-client or production-load guarantee.
Approved PY-07 protected browser sessions and PY-14 evidence safeguards
are complete in the isolated application scope; operational/browser-hosting gates
remain PY-35. Original designs/forms and all14 dashboard cards preserved.
See docs/PRICE_CLAIM_EVIDENCE_APPROVAL.md and docs/SESSION_COOKIE_APPROVAL.md. PY-02 approved source-publication scope is complete locally:
both original Admin Notes controls explain their public visibility; private
source fields/access and historical evidence stay intact. Six-role backend,
native PostgreSQL and browser checks pass. Owner approved the exact scope in
docs/SOURCE_PUBLICATION_APPROVAL.md on2026-10-18. Arbitrary text classification
and production historical-note review are not claimed or authorized.
PY-13 approved Nigerian price time is complete locally:
WAT input/display/day filters, explicit UTC instants, unchanged stored history,
existing history access and billing/paid-expiry rules. Owner's2026-10-18 reply
"do the best for app that is going to be mostly user friendly" authorizes the
recommended WAT scope in docs/NIGERIAN_PRICE_TIME_APPROVAL.md. No production scope.
All16 approved Admin lists now have100-record pages/full snapshot totals and
complete legacy streaming arrays. Original forms/actions/fields and access remain.
Batch77 finishes Prices/Flagged prices, joined commodity/market loads, all-status
latest-pair prefill beyond a page, and protection against delayed prefill overwriting
new form edits. Full277 backend tests, focused native case,205-record browser
checks, original price/source workflows, seven baseline views and all14 dashboard
cards pass.87 build source hashes match; original CSS byte-identical. No data repair.
Old recovery fixture80/80 remains stopped/intact. Fresh small native fixture
postgres-paging-20261018 at127.0.0.1:55449, identifier7697910732590408300,
uses --paging-cluster:26/80 schemas, stopped after87. Same12 connections/32MB buffers,
fsync enabled/exclusive lock and identity guards. Build refuses its active port.
Review controls: /__test__/admin-paging, /__test__/catalog-paging and
/__test__/faq-audit-paging and /__test__/signal-paging on http://127.0.0.1:55446;
disposable samples only.
Owner approved docs/ADMIN_LIST_PAGING_APPROVAL.md on2026-10-18:100-record Admin
pages with Previous/Next, complete totals/records, original forms/styles/cards.
Approved Admin paging16/16 complete77 (Users/Payments67, catalogs68, FAQs/Audit70,
Market/Quality signals71, Buying/Sell-watch73, Storage/Cost74, Feedback75,
Subscriptions76, Prices/flags77). Public history query materialization completed81;
never truncate charts or historical records to claim completion.
Owner answered "do the best option" to the explicit three-bonus rolling30-day
PY-05 proposal in docs/REFERRAL_ABUSE_DECISION.md. Scope implemented/verified78:
maximum3 new seven-day bonuses per rolling30 elapsed UTC days; existing days,
qualification, further signups/referral counts and14-day child trials preserved.
Full281 backend tests, UTC-boundary/rollback/native last-slot concurrency and real
registration/dashboard browser checks pass. No new identity verification claims.
Session/storage07 and claim evidence14 explicitly approved2026-10-18; verified80/79 respectively.
Live production work35 remains unauthorized; safe Phase1 staging testing was
approved later, but its infrastructure/provider prerequisites remain unavailable.
PY-02 approved safeguards complete72.
Owner policy and production gates stay explicit. Testing foundation PY-30 stays
complete; new regression tests belong with their respective improvements.
Do not reopen completed scope or mistake earlier historical counts for current.

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

Batch 36 verified: flag review uses one aggregate query with no private entity
hydration; reason validation matches the existing 50-character database column.
All 156 backend tests, 30 pinned PG cases and unchanged moderation/browser controls
pass. Seventeen complete, nineteen partial/pending. Owner explicitly approved the
comparison safeguard on 2026-10-17; implement that next from the approved doc.

Batch 37 verified: owner-approved current specification groups and separate
matching history charts implemented using existing fields only. Unknown/incomplete
measurements are not joined; no stored weights, types or history rewritten.
All 159 backend tests, 31 pinned PG cases, 31 comparison-unit cases and original
browser comparison/access/fourteen-card checks pass; TypeScript/build passes.
PY-12 approved comparison scope complete: eighteen complete, eighteen partial/
pending. Cost-reference unit inference is a separate PY-29 decision pending in
docs/COST_REFERENCE_UNIT_APPROVAL.md. Next: missing editorial audits and usability.

Batch 38 verified: owner-approved cost-unit wording removes unsupported inference
from the first market price. Saved amounts, formula, quantity control and original
records stay unchanged. All 159 backend tests, 31 pinned PG cases, TypeScript/build
and actual before/after calculator browser checks pass. Eighteen complete, eighteen
partial/pending. Unit-label approval is recorded in the cost proposal; no unit field
or data backfill. Next: missing intelligence-resource audits (three related writers).

Batch 39 verified original Market/Quality signal and Cost reference writes and
audits commit together: 168 backend/34 pinned PG cases and nine browser audit
records pass. Batch 40 completes the remaining Buying zone, Sell-watch window
and Storage suitability create/edit audit writers: 177 backend/37 pinned PG cases
and all six browser audits pass. PY-26 identified application scope complete.
Nineteen IDs complete; seventeen partial/pending. Next: remaining source/privacy,
mobile and keyboard safeguards, retaining original screens and policies.

Batch 41 verified: legacy audit API responses recursively redact private source,
credential and screenshot fields without rewriting original stored evidence.
All 180 backend/38 pinned PG cases and original audit-screen privacy checks pass.
Nineteen complete; seventeen partial/pending. Next: mobile/keyboard checks.

Batch 42 verified existing Admin selection is now keyboard reachable, Enter/Space
matches the original click action, focused rows/cards have a keyboard-only outline,
and role/subscription selects have accessible names. Twenty browser checks and 78
normal viewport/Easy-reading checks pass; five relevant backend/38 pinned PG
compatibility cases pass. Nineteen complete; seventeen partial/pending. Next:
long-content mobile stress checks and remaining keyboard/offline safeguards.

Batch 43 verified: long price-card names no longer escape their cards; ordinary
card/badge geometry is identical before/after. Twelve long-content and 78 normal
viewport checks, six backend query/38 pinned PG compatibility cases pass. PY-23
identified overflow scope complete: twenty complete, sixteen partial/pending.
Owner approved docs/OFFLINE_PRICE_SAFETY_APPROVAL.md on 2026-10-17; implement that
exact local-only safeguard next, with service workers/providers still isolated.

Batch 44 implements the owner-approved offline safeguard: actual worker source
passes 32 fake-network/cache checks, real API TypeScript passes twelve checks,
and original browser views pass thirteen provenance plus two refresh-race checks.
All 180 backend/38 pinned PG tests pass; original browser/access regressions pass.
PY-25 approved application scope complete: twenty-one complete, fifteen partial/
pending. Native browser service workers remain deliberately disabled in this lab;
real deployment/PWA/provider compatibility remains operational PY-35 work.

Batch 45 resumes the uncommitted keyboard work at df74e55. Sixteen original menu/
help/welcome-tour cases, twenty earlier keyboard regressions, fourteen-card
dashboard regression, six backend boundary tests and 38 pinned PG cases pass.
PY-24 identified keyboard/focus scope complete: twenty-two complete, fourteen
partial/pending. The previous build was not executed because approval review hit
a usage limit. Normal sandbox TypeScript passed but Vite ancestor metadata access
failed; a subsequent explicitly reviewed guarded build succeeded. No bypass.
Next: existing password/input consistency, bounded detail queries and remaining
approved technical safeguards; business-rule and live-operation decisions remain.

Batch 46 verifies password input/reset boundaries without changing existing rules:
UTF-8 values beyond the existing bcrypt72-byte limit return422 instead of500;
the link/access remain usable, and original forms validate the same limits without
altering typed passwords. All184 backend/39 pinned PG,32 browser input and full
reset/retry/login/revocation cases pass. Twenty-two complete, fourteen partial/
pending; PY-27 still includes remaining edit consistency. Preview reseeded only
in memory after tests; reset-request cooldown and real records remain unchanged.

Batch 47 recovered and verified after the owner's forced restart (2026-10-17).
All prior commits and interrupted source/test changes were intact at 0e1e118.
Commodity detail now requests only its commodity's market/quality/cost records;
unfiltered Admin lists, ordering, access, original UI/formulas and history remain.
All190 backend tests and all40 native PostgreSQL tests pass, plus real browser
scope, five detail regressions and all14 dashboard cards. PY-20 remains partial:
other lists/full history still require compatible optimization. Exact total stays
22 complete / 14 partial or pending. Recovery checks only; do not begin batch48
without a subsequent instruction. See batch47 history for resource safeguards.

## Checklist — do not repeat the audit

Latest continuation: owner resumed development from c0bb6eb after recovery.
Batch48 verifies two compatible PY-20 changes: commodity-scoped Buying zone and
Sell-watch queries; original default Admin lists, UI and history remain complete.
All194 backend tests, three focused native cases, actual scope browser, five
detail regressions and all14 dashboard cards pass. Smaller PG stopped before
browser/build; retained schemas40 to43, not another full suite. Existing dependency
snapshot reused rather than copied. Exactly22 complete /14 partial or pending;
next compatible remaining work includes Storage suitability query scope and
remaining editing/input/security items. No production, push, merge or deployment.

Batch49 completes the same optional SQL commodity scope for Storage suitability;
all six original intelligence requests now avoid unrelated commodity records.
Twelve relevant backend tests, two native cases and actual planning/detail/14-card
dashboard browser regressions pass; retained PG schemas43 to45. No new full suite
claim (latest full backend194 in batch48, full native40 in batch47). Existing build
dependencies reused; CSS unchanged. Exactly22 complete /14 partial or pending.
Owner approved docs/ADMIN_EDIT_PREFILL_APPROVAL.md on2026-10-17. Batch50 now loads
saved values in the original Market/Quality edit forms; 18 actual browser checks,
nine backend tests, two focused native cases and all14 dashboard cards pass. Four
approved forms remain for sequential batches. Exactly22 complete /14 partial or
pending; original design, fields and policies retained, native fixture stopped.

Batch51 extends the approved safeguard to Buying zones and Sell-watch windows.
All36 browser editing checks, nine backend and two focused native cases pass;
Storage/Cost remain. Exactly22 complete /14 partial or pending. Native schemas49
of80, cluster stopped; original CSS/fields/measurements/policies unchanged.

Batch52 completes the approved six-form editing safeguard with Storage/Cost.
All196 backend tests, two focused native cases,61 browser editing checks, five
detail regressions and all14 dashboard cards pass. PY-27 identified scope complete:
exactly23 complete /13 partial or pending. Native fixture schemas51 of80, stopped.
Next unfinished IDs02,05,07,08,13,14,20,28,29,30,31,35,36. Preserve existing
policy/visible-change approval boundaries; no production/provider claims or new
full native-suite claim. Resume from these results, not earlier historical status.

Batch53 further PY-08: watchlist target validation now matches the original
NUMERIC(14,2) storage. Before: actual native PostgreSQL500 for overflow and SQLite
silently rounded sub-kobo input. After: two targeted backend tests, five alert
regressions, one native workflow and six browser checks pass; valid/unset/zero/max
targets and owner isolation preserved. Frontend unchanged; snapshot from batch52
reused. Exactly23 complete /13 partial or pending; smaller fixture53/80 schemas,
stopped. Latest full backend196 remains batch52, not a claimed full198 run.

Batch54 further PY-08: Cost breakdown rejects explicit nulls for required stored
values and calculated totals exceeding its existing NUMERIC(14,2) columns before
any write. Two backend validation tests, nine audit regressions, two native cases,
seven cost-browser checks and61 editing regressions pass.84 frontend source/config
hashes match the existing verified build; no frontend changes or dependency copies.
Native fixture56/80 schemas, stopped. Exactly23 complete /13 partial or pending.

Batch55 extends required-value validation to Buying zones/Sell-watch while keeping
optional date/period clearing. Full202 backend tests pass28.253s; three focused
native cases pass2.296s;65 original-form browser checks, five detail regressions
and14-card dashboard pass. Native schemas59/80, stopped; no frontend changes.
Exactly23 complete /13 partial or pending. Next PY-08 remaining signal required
values; do not invent text/body/session/source policies to close tracker items.

Batch56 Market/Quality required-value safeguards verified: four focused backend
validation cases, nine audit regressions, three native cases and69 browser checks
pass. Native schemas62/80, stopped. Full202 backend baseline remains batch55;
no new full204-suite claim. Exactly23 complete /13 partial or pending. Next Storage
required IDs/status, preserving nullable notes and linked-price clearing.

Batch57 completes required-value protection across the six existing intelligence
resources. Full205 backend tests pass35.526s; two Storage native cases pass1.677s;
73 browser/API checks, all14 dashboard cards and five detail regressions pass.
84 frontend hashes match the original verified build; no frontend/policy/schema
changes. Native fixture64/80 schemas, stopped; heavy checks sequential. Exactly23
complete /13 partial or pending. These were further PY-08 protections, not a claim
that broader request/text limits, owner policies or production operations are done.
Resume compatible remaining input/query/history work; do not repeat completed null
guards, cost limits or prior batches. Legacy unbounded text must not be arbitrarily
capped, and source/referral/session/date/movement/business changes need approval.

Batch58 completes PY-31 application recovery: explicit dry-run-by-default, bounded
pending/failed reconciliation command using existing strict verification/activation.
No charging, scheduler or live execution enabled. Seven new backend tests, eight
existing verification tests, two focused native cases and actual recovery/payment/
14-card dashboard browser checks pass. Full211 backend baseline passed before the
final CLI error-redaction case; targeted seven pass afterward. Exactly24 complete /
12 partial or pending. Native66/80 schemas, stopped. Next PY-28 legacy migration
preflight, not more expansion of already completed account/input/UI improvements.

Batch59 completes PY-28 current application/migration-preservation scope: read-only
online preflight refuses populated legacy/unversioned/unknown/forked starts before
migration steps; reviewed0021-to0022 and empty initialization still work. Existing
historic migration files and business data are not rewritten/repaired. Full216
backend tests pass29.966s; two native migration cases pass3.136s; seven original
browser workflows and all14 dashboard cards pass. Exactly25 complete /11 partial
or pending:02,05,07,08,13,14,20,29,30,35,36. Native69/80 schemas, stopped.
Next prioritize finite remaining PY-20 query/history and PY-36 documentation/
maintainability; owner policy choices and production-only PY-35 checks stay gated.
No expansion of completed null-guard/account/UI scopes is needed.

| ID | Improvement | Current status |
|---|---|---|
| PY-01 | Consistent historical access checks | Complete in batch 7; date/comparison/ID routes enforce existing history entitlement; current summaries preserved |
| PY-02 | Confidential/restricted market information | Approved application scope complete72: existing premium boundaries, response allowlists and legacy audit redaction retain private evidence/Admin source access; owner-approved hints beside both original Notes controls explain public visibility and private source fields. Six-role/backend/native/browser checks cover prices/history/CSV/audits/shares and unchanged raw records. Public notes/generic categories/access unchanged; arbitrary confidential-text detection not claimed. Any production historical editorial review requires separate PY-35 authorization |
| PY-03 | Google ownership and safe account linking | Application-side approved scope complete in batch 27: stable subject ownership, no email-only linking/overwrite, existing password/reset fallback and original trials; cryptographic/HTTP/PG/browser verified. Live Google popup/provider compatibility remains operational PY-35 |
| PY-04 | Password reset and login revocation | Complete in batch 5; actual HTTP/browser and PostgreSQL reset/logout races passed |
| PY-05 | Referral abuse protection | Owner-approved application scope complete78: atomic/duplicate-safe registration-reward-audit, maximum3 seven-day bonuses per referrer per rolling30 elapsed UTC days enforced under existing parent lock; exact boundary, failed-award rollback and concurrent last-slot signup verified. Further signups/14-day child trials/referral counts and all earned/purchased value preserved; existing dashboard/share explanation states limit. No inferred legacy awards or new identity verification; broader fraud elimination not claimed. Approval: docs/REFERRAL_ABUSE_DECISION.md; live clock/legacy review stays PY-35 |
| PY-06 | Safe push notification destinations | Application-side complete in batch 13; known-provider/key validation, bounded TLS transport, no redirects; live provider compatibility remains operational verification |
| PY-07 | Shared-device/session safety | Approved local application scope complete80: browser HttpOnly cookies, exact Origin/session-bound CSRF, credentialed allowlisted CORS, no-store private responses, shared login quota, server logout/reset revocation, original RememberMe/90-day ceiling and validated same-expiry legacy conversion. Ten browser scenarios cover shared tabs/offline retry/stale responses/cookie-mutation locking; no weaker unsupported-browser fallback. Original forms/API bearer clients/push cleanup/CSV preserved. Browser-session restore settings, live HTTPS/CORS and supported-device/legacy cutover validation remain PY-35; offline remote revocation and XSS elimination not claimed |
| PY-08 | Input/upload/request abuse bounds | Identified application-side bounds complete66: existing push/query/numeric/required-value/storage rules plus4MiB aggregate HTTP body,8KiB URL,64KiB headers before parsing/DB/provider work; declared/chunked/malformed lengths, disconnects and bounded fragment buffering tested. Global body budget bounds all submitted text; existing2MiB screenshot limit and valid fields unchanged. Share path matches existing100-character catalog storage. No historical rewrite or arbitrary new editorial character limits; production proxy/timeouts/distributed throttling remain PY-35 |
| PY-09 | Concurrent security-action safety | Complete for identified reset/logout/last-Admin cases in batches 5/6; six PostgreSQL cases passed |
| PY-10 | Spreadsheet export safety | Complete in batch 3; text/numeric regressions and original browser download/access checks passed |
| PY-11 | Correct saved administrator price state | Complete in batch 10; actual create/approve/correct/outdated/reject/reload browser regression passed |
| PY-12 | Accurate existing quantity/type/market comparisons | Complete for owner-approved current-record/history-chart safeguards in batch 37: separate recorded specifications, matching commodity/market/unit/size/type only, no inferred missing measurements; all historical rows preserved. Cost-reference quantity linkage remains separate PY-29 work |
| PY-13 | Consistent Nigerian dates/times | Complete for approved local scope69: Nigerian WAT price displays, Admin/Reporter entry/correction and current/history/comparison/CSV day filters. Inclusive WAT midnight/exclusive next midnight, exact UTC instants and unchanged raw history verified backend/PG; Lagos/UTC forms and desktop/mobile displays pass. No guessed zone for ambiguous legacy values; actual historical review remains35. Earlier UTC trial parsing31 and paid UTC expiry unchanged. Approval: docs/NIGERIAN_PRICE_TIME_APPROVAL.md, owner discretion2026-10-18 |
| PY-14 | Evidence-based movement/confidence | Approved application scope complete79: new/changed two-source claims require distinct private references; new movement and pending approval require preceding approved, nonoutdated comparable recorded evidence. Both endpoints determine up/down/stable; unsupported claims require existing unknown. Historical labels/records retained; private evidence stays private. No proof of independent humans or retrospective editorial review claimed. Scope: docs/PRICE_CLAIM_EVIDENCE_APPROVAL.md |
| PY-15 | Prices recover after failed loading | Complete in batch 1; before/after browser regression passed |
| PY-16 | Correct filters and response ordering | Complete for identified current/history/navigation scope in batches 22/28: applied filters, overlap, URL navigation, stale history/error/metadata and access-role browser regressions verified |
| PY-17 | Correct market-detail loading | Complete for identified loading races/combined-failure defect in batch 16; obsolete commodity/account responses ignored and independent successful sections retained |
| PY-18 | Accurate account/payment/access messages | Complete for identified account/expiry/callback defects in batches 4/11/19; verified return refreshes access, unconfirmed return never claims payment received in title |
| PY-19 | Existing FAQ draft/hide/publish management | Complete in batch 12; hidden drafts remain available to Admin across reload, public publication boundary verified |
| PY-20 | Bounded queries with accessible historical records | Identified application query scope complete81, committed558f756:16/16 approved Admin pages/full totals/complete legacy streams; current ranking/dashboard/metadata/CSV/commodity scopes verified earlier. Public full history now uses one ordered query and100-row ORM batches, unchanged filters/access/public allowlist and cursor/session cleanup. All251 approved rows retained in native/browser tests including mobile; raw history unchanged. Browser memory/output still scales with selected history size; no infinite-client or production-load certification. No public pagination or chart truncation |
| PY-21 | Reliable independent alerts | Application-side identified channel dependency complete in batch 24: failed email no longer skips push/WhatsApp; per-user/channel failures isolated; existing deduplication/count semantics retained. Delivery/retry operations remain PY-35 |
| PY-22 | Efficient loading and accurate dashboard totals | Complete for identified dashboard scope in batch 29: all 14 original metrics preserved; one Admin-only aggregate API/DB snapshot, zero entity hydration; backend/PG/browser totals and outage recovery verified |
| PY-23 | Preserve layout while fixing mobile overflow | Complete for identified original critical-layout/price-card overflow scope in batches 42/43: 78 normal and twelve long-name viewport checks, 320–1366px, Easy reading both modes; ordinary card/badge geometry and all fourteen Admin cards preserved |
| PY-24 | Keyboard/focus accessibility | Complete for identified original keyboard/focus scope in batches 42/45: selectable records and named role/status controls, menu/help Escape with trigger focus restoration, welcome-dialog initial/wrapped focus and original Skip/Next/Back behavior; 36 browser keyboard cases and all fourteen dashboard cards verified |
| PY-25 | Safe and clearly aged offline prices | Complete for owner-approved application scope in batch 44: public-only explicit configured-API caching, timestamped saved copies, truthful original-view warnings, legacy/private/history exclusion and fresh-response recovery verified using actual worker source with fake network and actual browser UI with synthetic metadata. Native deployed PWA compatibility remains PY-35; no new age cutoff |
| PY-26 | Complete atomic administrative audit | Complete for identified business-record writers through batch 40: payment/referral, price/moderation/flags, account/subscription, FAQ/catalog and all six intelligence resources save sanitized audits atomically; native concurrent edits and failed-audit rollback verified. External delivery operations remain PY-35 |
| PY-27 | Consistent existing editing/password inputs | Complete for identified scope: feedback selection in batch26, existing Unicode/72-byte password rules and reset validation in batch46, owner-approved six Admin edit forms in batches50–52. Saved values/costs, one-field edits, reload, explicit clearing, switching/unknown/blank IDs and creation verified in61 actual browser checks |
| PY-28 | Historical record preservation | Current application-side scope complete in batch59: read-only legacy/unversioned preflight before migration steps, empty/reviewed0021-to0022 paths, unchanged raw history/catalog IDs/active flags/cost links/sources/audits, preserved paid/payment records and0022 downgrade refusal verified. No guesses to repair already-changed historical data; production backup/restore/rollout and any repairs require owner approval under PY-35 |
| PY-29 | Stable identities and dependent records | Application-side identified scope complete65: catalog IDs/referenced deletion/atomic audits34; duplicate/rename/rollback races62; locked parent-price and same-commodity/market observation links64; exact existing-ID current/history filters and rename-safe detail/share links65. Current shares never publish historical amounts. Original labels, measurements and all records preserved; no automatic merge, legacy alias guesses, rewrites or invented cost units. Historical repairs require separate PY-35 approval |
| PY-30 | Isolated automated/browser verification | Identified testing-foundation scope complete63; full268 backend tests71, earlier full40 native baseline47 plus focused cases through signal paging71; original baseline/14-card/all-six-editor/paging/race/mobile checks71 pass. Fresh pinned postgres-paging-20261018:55449 identifier7697910732590408300 uses1/80 schemas, stopped,12 connections/32MB buffers/fsync enabled. Exhausted recovery80/80 retained stopped. Exclusive native lock/negative connection probes and build port guard kept;87 source hashes match reused build, original CSS identical, no installs. Not production/provider certification; future regression tests stay with remaining items; live operations35 gated |
| PY-31 | Confirmed payment activation and recovery | Application-side approved scope complete in batch58: atomic confirmation, owner callback and explicit bounded/resumable reconciliation for missed webhook/return; dry-run default, strict existing evidence/activation, single PG worker, error isolation, replay safety and purchased-time/manual-grant preservation verified. Live scheduling/checkpoints/monitoring and ambiguous legacy repairs require owner approval under PY-35 |
| PY-32 | Preserve unused purchased/trial time | Complete for approved rules in batches14/21; batch87 closes the confirmed stale single-account GET/renewal race under existing locks. Paid/trial value, indefinite grants/review and payment evidence preserved; full307 backend tests, actual PG blocking/twelve interleavings and value/review browser checks pass |
| PY-33 | Validate payment evidence | Complete for application evidence paths in batches 8/9/15/19: signed webhook, checkout/reference/amount/currency/ID verification and concurrent provider-verification/webhook replay; live-provider operational verification separate |
| PY-34 | Expiry without unintended staff-role loss | Complete in batch2; batch87 additionally verifies locked single-account expiry versus payment for ordinary/Reporter/Admin users, genuine expiry/history/rollback and eight-role browser access |
| PY-35 | Operational readiness and dependency evidence | Application LIVE; reviewed backendce0ca70 operational rollout PASS153. Two-hourly GitHub recovery passed two real runs including encrypted checkpoint retrieval; controlled failure email received in approved inbox. Existing release/provider/backup/restoration/rollback evidence retained. Remaining requested safeguard: daily encrypted backup installed/enrolled but paused154; Direct host unavailable on tested IPv4 networks and Session pooler's nonlocal database hop fails the unchanged PostgreSQL TLS guard. No guard relaxation or export; preserve existing backups. 35/36 complete until secure scheduled backup verification succeeds. No repeat audits/migrations or invented new release tasks. |
| PY-36 | Accurate progress/documentation/maintainability | Current application documentation/identified six-form readability scope complete in61: exact106-operation API index, approved contracts, safe local recovery/resumption guide and README links; six original intelligence forms expanded for maintenance with identical emitted syntax and byte-identical compiled JS/CSS. Progress/approvals/evidence current; future maintenance does not reopen this scope. Production rollout/provider documentation verification remains PY-35 |

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

### Batch 36 — further PY-08/PY-20 (2026-10-17)

- Flag reason length now validates against the existing 50-character storage
  limit before insertion; null/empty/50-character Unicode values remain valid.
  No new form, business limit, quota or database column. Overlong browser/API
  requests return 422 rather than reaching a PostgreSQL storage failure.
- Admin flag overview replaces per-price/catalog lookups with one count/name
  aggregate query and no ORM hydration of private prices/reasons. Preserve open
  counts, original response fields and review of pending/rejected or inactive
  catalog records. Add deterministic price-ID ordering only for equal timestamps.
- Four focused before tests reproduced three failures, including ten statements
  for three flagged records (0.212s); after tests pass (0.265s). All 156 backend
  tests pass, 29.371s; thirty pinned PG cases pass, 30.210s. Native checks retain
  every original price/flag row, validate Unicode storage and prove one query.
- Original browser moderation/flag controls pass, including 51-character denial
  followed by valid flag/review and restored preexisting history. No frontend build.
  Manual: http://127.0.0.1:55446/admin/flagged, demo Admin credentials unchanged.
- Evidence: batch-36-*.json. Seventeen complete, nineteen partial/pending.
  Owner explicitly replied "Approve the comparison safeguard" on 2026-10-17.
  docs/PRICE_COMPARISON_APPROVAL.md now records that approval. Three next-batch
  specification tests reproduce current-selection failures and remain uncommitted
  outside this verified batch until the approved safeguard is implemented.

### Batch 37 — approved PY-12 comparison scope (2026-10-17)

- Owner explicitly approved docs/PRICE_COMPARISON_APPROVAL.md before implementation.
  Latest current records now rank within commodity/market/trimmed lowercase existing
  unit/bag-size/type groups; unlike recorded specifications no longer hide one
  another. Outdated/movement filters still cannot resurface older same-spec records.
  Shared query keeps fourteen dashboard card definitions and correct latest totals.
- Original history chart styling reused for separate matching complete groups;
  unlike markets/commodities/units/sizes/types are never joined. Missing/placeholder
  specifications or invalid numbers/dates are not plotted as comparable. The
  approved "Not enough comparable records." message replaces unsupported lines.
  All rows remain in the original history table/cards. No quantity conversion,
  grades, new fields, historical backfill, recorded movement/confidence/previous
  price edits or new calendar-day policy. Price cards/detail/ticker show existing
  type/quantity text to distinguish records; original CSS remains unchanged.
- Three before specification tests fail (0.140s); all pass after (0.124s). Actual
  before browser reproduces a single mixed-measurement line and hidden variants.
  After: two matching two-point charts, distinct current cards, original history
  retained; temporary synthetic labels/rows removed and starting history restored.
- All 159 backend tests pass, 32.845s. Thirty-one pinned PG cases pass, 31.534s,
  including case/space matching, bounded winning-row hydration, four correct
  current specifications/dashboard count and every retained historical row.
  Thirty-one real TypeScript comparison cases pass; inputs remain unmodified.
- TypeScript/Vite passes, 2.63s, 101 modules, JS320.26kB/90.74kB gzip; original
  index-19youOJ7.css unchanged. Original browser eight-role access and fourteen
  dashboard totals/request/recovery regressions pass. Evidence: batch-37-*.json.
- Manual: http://127.0.0.1:55446/history as trial@example.com / PriceYardDemo8!.
  Existing synthetic unknown measurements correctly show the approved insufficient
  comparison message; full history rows remain. No invented sizes are left there.
- Eighteen IDs complete, eighteen partial/pending. Cost references contain no
  saved unit; existing inference from the first market price remains unmodified
  pending separate visible-label approval in docs/COST_REFERENCE_UNIT_APPROVAL.md.
  Remaining audits for six editorial/intelligence resource writers still open.

### Batch 38 — approved cost-reference label, further PY-29 (2026-10-17)

- Owner explicitly approved "Approve the honest unit label" before implementation.
  Stop borrowing bag size/unit from the first current price for a cost reference
  that has no saved quantity. Existing calculator area now says "Unit not recorded"
  and "Confirm the unit for this cost reference before using this estimate."
  Original quantity input, calculations and saved monetary figures unchanged.
- Before browser reproduces the unsupported "Priced per 1 bag" label. After browser
  verifies approved wording, two reference units still give purchase 420,000,
  additional 400 and total 420,400, unchanged saved record and restored initial
  cost list after deleting only the new synthetic test reference. No new fields,
  business amounts, quantities, schema, price linkage or historical backfill.
- Required compatibility runs: all 159 backend tests pass, 30.987s; 31 pinned PG
  cases pass, 29.744s. Backend unchanged; no backend defect or new backend unit-test
  count claimed. TypeScript/Vite passes, 2.19s, 101 modules, JS320.21kB/90.70kB gzip;
  original index-19youOJ7.css unchanged. Evidence: batch-38-*.json.
- Manual: original Cost breakdown area on http://127.0.0.1:55446/commodities/Egusi
  when an existing synthetic cost reference is present; Trial login unchanged.
  No fabricated monetary reference is left after automated checks.
- Eighteen IDs complete; eighteen partial/pending. Broader stable identity and
  missing intelligence audits remain. New next-batch intelligence audit tests
  are intentionally outside this verified frontend commit until fixed/verified.

### Batch 39 — further PY-26 intelligence audits (2026-10-17)

- Original Market signal, Quality signal and Cost reference create/edit/delete
  controls now save their audit in the same transaction. Failed audit insertion
  rolls back the change; row locks keep concurrent edit snapshots continuous.
  Existing permissions, fields, money, formulas and price history unchanged.
- Nine before tests reproduce twelve failures (0.639s); focused after tests pass
  (0.610s). All 168 backend tests pass, 23.229s; 34 pinned PostgreSQL cases pass,
  33.734s, including real concurrent edits and rollback for these three resources.
  Test comparisons treat equal decimal amounts numerically (120 equals 120.00);
  no stored monetary values or rounding rules were changed to satisfy a test.
- Browser original three create/edit/delete workflows pass; all nine audit records
  are verified, starting price history unchanged and temporary rows removed.
  No frontend rebuild. Evidence: tools/local-test/evidence/batch-39-*.json.
- Manual: http://127.0.0.1:55446/admin/market-signals, /admin/quality-signals or
  /admin/costs with admin@example.com / PriceYardDemo8! in the isolated preview.
- Eighteen IDs complete; eighteen partial/pending. Buying zone, Sell-watch window
  and Storage suitability create/edit audit coverage remains next. No live services,
  production credentials, schema changes, push, merge or deployment.

### Batch 40 — complete identified PY-26 resource writers (2026-10-17)

- Buying zone, Sell-watch window and Storage suitability create/edit now commit
  with sanitized actor/record/old/new audits. Existing row locks protect concurrent
  edits; failed audits preserve both records and logs. Original fields, validation,
  permissions, amounts and price history retained. No deletion endpoints added.
- Nine before tests reproduce nine failures (0.573s); all nine pass after (0.557s).
  All 177 backend tests pass, 31.352s; 37 pinned PostgreSQL cases pass, 36.928s,
  including create/edit rollback and continuous concurrent snapshots for all three.
- Browser uses the original three forms to create/edit and verifies six audits
  and unchanged historical prices. These resources originally have no delete
  control; only the disposable in-memory preview is restarted to remove temporary
  test entries. No database cleanup against disk/production and no frontend changes.
  Evidence: tools/local-test/evidence/batch-40-*.json.
- Manual: http://127.0.0.1:55446/admin/buying-zones, /admin/sell-watch or /admin/storage,
  using admin@example.com / PriceYardDemo8!. Original forms are unchanged.
- Nineteen IDs complete; seventeen partial/pending. PY-26 covers identified
  application business-record writers; live delivery/reconciliation operations
  remain separate. No production access, migrations, pushes, merges or deployment.

### Batch 41 — further PY-02 historical audit privacy (2026-10-17)

- Confirmed legacy audit list/detail returned unfiltered historical JSON despite
  original Audit screen's explicit promise that secrets/private sources never appear.
  Apply the existing recursive redaction when serializing both response fields;
  normalize private-key case/space checks and exclude feedback attachment bytes.
  Database evidence, nonprivate amounts/notes, actor/action/record IDs stay intact.
- Three before tests reproduce three failures (0.177s); all pass after (0.262s).
  All 180 backend tests pass, 33.051s; 38 pinned PostgreSQL cases pass, 42.185s.
  Native fresh-session read verifies original nested historical JSON unchanged.
  Guest/non-Admin denial, null/empty/list handling and input immutability pass.
- Actual original browser Audit screen/list/detail omit fabricated legacy private
  fields while retaining public evidence. Public current/history price responses
  exclude sources, legitimate original Admin price response still contains them.
  One initial browser check used the wrong test URL; corrected to existing /admin/audit,
  with no application routing changes. No frontend rebuild or schema changes.
- Evidence: tools/local-test/evidence/batch-41-*.json. The in-memory preview has one
  clearly fabricated legacy audit fixture solely for regression/manual verification.
  Manual: http://127.0.0.1:55446/admin/audit, admin@example.com / PriceYardDemo8!.
- Nineteen IDs complete; seventeen partial/pending. Remaining source policy review,
  mobile/keyboard issues and operational/business decisions are not claimed complete.

### Batch 42 — further PY-23/PY-24 original Admin usability (2026-10-17)

- Real browser before checks reproduce fifteen keyboard/name failures. Existing
  price rows and published/hidden FAQ cards now offer Tab/Enter/Space selection
  with a keyboard-only focus outline. Selection sets the original Record/FAQ ID;
  it never saves, approves or publishes. Mouse selection remains unchanged.
- Original desktop/mobile role controls and subscription status selects now have
  accessible names identifying their user. Visible wording, option values, form
  fields and account/subscription actions are unchanged. No policy/schema changes.
- Twenty after browser checks pass, including mouse parity, no unintended writes
  and unchanged price history. Seventy-eight normal mobile cases pass across
  thirteen original critical screens, 320/375/768px and both Easy-reading modes;
  no out-of-bounds controls and all fourteen Admin cards retained. No mobile CSS
  redesign was needed for those fixtures; long-content stress tests remain next.
- TypeScript/Vite passes, 1.70s/101 modules; JS320.89kB/90.90kB gzip. CSS changed
  only by the keyboard focus-outline rule (31.72kB/7.13kB gzip). Backend unchanged:
  five targeted Admin access/audit compatibility tests pass, 0.503s; all 38 pinned
  PostgreSQL cases pass, 37.888s. Latest full backend remains 180 passes in batch 41.
- Evidence: tools/local-test/evidence/batch-42-*.json. Manual: /admin/prices or
  /admin/faq at http://127.0.0.1:55446 as demo Admin; Tab to a record, press Enter
  or Space, and confirm its ID is selected without saving. Nineteen IDs complete,
  seventeen partial/pending. No production access, push, merge or deployment.

### Batch 43 — identified PY-23 long-content containment (2026-10-17)

- Browser reproduces clipped price names in all twelve stress cases even though
  document overflow reports false. Existing commodity/market text at its existing
  limits is stubbed only in that disposable browser; no API records/names/amounts
  or measurements are saved or changed. Other original screens are retained.
- Three narrowly scoped CSS rules let a price card and its flex text shrink/wrap
  while keeping the movement badge readable. No truncation, new label, new field,
  palette/typography/layout redesign, hidden content or historical change.
- All twelve cases pass at 320/375/640/768/900/1366px with Easy reading off/on.
  Ordinary mobile/desktop card and badge rectangles exactly match before/after.
  All 78 original critical-screen layout cases pass; fourteen Admin cards retained.
- TypeScript/Vite passes, 1.69s/101 modules; JS unchanged 320.89kB/90.90kB gzip;
  CSS31.84kB/7.16kB gzip. Backend unchanged: six relevant current-query compatibility
  tests pass, 0.509s; all 38 pinned PG cases pass, 33.429s. Latest full backend180.
- Evidence: tools/local-test/evidence/batch-43-*.json. Manual: /prices at
  http://127.0.0.1:55446; original ordinary records still look the same. Browser
  stress text never persists in the preview. Twenty IDs complete, sixteen partial/
  pending. Next approved offline-price safeguard; no production/push/merge/deploy.

### Batch 44 — owner-approved PY-25 offline-price safeguard (2026-10-17)

- Owner explicitly approved docs/OFFLINE_PRICE_SAFETY_APPROVAL.md before this batch.
  Actual service worker now caches only recognized public resources from the
  configured API location (including separate API origins) and same-origin public
  shell/assets. Authenticated, private, Admin, reset/account/payment, historical and
  date-selected requests bypass all cache branches. Non-success/private/no-store
  responses are never used as new public copies; 401/403/private responses remove
  a previous same-key copy. Cache failures cannot break successful live responses.
- Successful public copies store device-save time separately from record timestamps.
  Fallbacks require valid metadata and use only the current named data cache; old
  unmarked copies are not replayed. Activation removes only the two known legacy
  PriceYard stores, retaining unrelated/future caches. No age cutoff or new paid rule.
- Reuse the existing banner styling for approved saved-copy wording/time beside
  Home/current/detail/Watchlist prices and the ticker. Cached Home hero no longer
  says Live now. Fresh responses clear their warning; browser offline wording no
  longer promises a cache exists. Per-request metadata and request sequencing prevent
  late cached results replacing newer fresh Home/current/ticker state. No schema,
  price/measurement/confidence edits, changed money/formulas or new database fields.
- Before actual-source tests reproduce 24 failures in 28 cases. All 32 final worker
  cases pass with an in-memory cache and fake fetch; no native transport is supplied
  to the VM. Twelve tests execute actual API TypeScript, including unchanged 401
  handling and fail-closed invalid cache timestamps. Actual original browser with
  synthetic response metadata passes thirteen cases and two refresh-race cases;
  four existing filter regressions and seven original-browser checks pass.
- All 180 backend tests pass, 32.751s; all 38 pinned PG cases pass, 39.816s. Backend
  source unchanged in this batch. Final registration guard excludes userinfo/query/
  fragment API configuration before constructing a worker URL. TypeScript/Vite
  passes, 2.04s/102 modules; JS322.34kB/91.45kB gzip. CSS remains
  index-BEBH-Ai6.css, unchanged from batch43.
  Built worker/source hashes verified equal. Evidence: batch-44-*.json.
- Isolation remains strict: native service workers deliberately disabled in the
  review browser, all requests restricted to literal loopback, real providers off.
  Worker-source fake-network checks and browser UI checks are separate evidence,
  not a claim that deployed browser/PWA/provider compatibility was tested.
- Manual: open http://127.0.0.1:55446/__test__/offline-prices, click Show simulated
  saved copy, then open/reload Current Prices. Use Restore normal responses and
  reload to clear the notice. This control is outside the app and stamps only
  fabricated unauthenticated current-list responses; it does not enable real cache,
  change stored prices, or remove the testing wrapper's no-store/network guards.
- Twenty-one IDs complete; fifteen partial/pending. Next: remaining keyboard/focus,
  editing/query/security work and separately approved business/operational decisions.
  No production access, dependency installation, push, merge or deployment.

### Batch 45 — finish identified PY-24 keyboard/focus scope (2026-10-17)

- Resume preserved uncommitted component changes and before evidence at df74e55;
  no audit restart. Before browser reproduces twelve failures in sixteen cases.
  Existing help popup now identifies its controlled note, handles Escape and
  returns focus on Close/Escape. Existing mobile menu identifies its navigation
  and Escape closes it while restoring the original toggle's focus.
- Existing welcome dialog takes initial focus, wraps Tab/Shift+Tab within its
  buttons, announces its existing step text, and restores focus on dismissal.
  Escape invokes the original Skip action/seen preference; original Next/Back,
  words, step count, buttons, prices/trial/access policies and appearance retained.
- Previous auto-review attempt never executed the build: usage-limit review failure,
  not an unsafe-action determination. Resumed normal sandbox attempt passed
  TypeScript but esbuild could not read ancestor-directory metadata. Same guarded
  credential-free build then received explicit automatic approval and passed.
  No restriction bypass or dependency installation. Build2.37s/102modules,
  JS323.59kB/91.84kB gzip; original CSS index-BEBH-Ai6.css unchanged.
- All sixteen after cases and twenty prior selection/name/mouse regressions pass.
  Original dashboard all fourteen labels/values, one summary request and recovery
  pass. Six relevant backend boundary tests pass,2.255s (backend unchanged; latest
  full suite180 in batch44). All38 native pinned PG cases pass,30.120s.
- The isolated cluster had been interrupted; ordinary automatic recovery completed
  without reset/WAL/PID deletion or edits. Live directory/system identity is checked
  by the pinned runner before every connection/mutation; no production contacts.
- Evidence: tools/local-test/evidence/batch-45-*.json. Manual: /prices at
  http://127.0.0.1:55446, open the confidence ? then press Escape; at mobile width,
  open Menu, Tab to its first link and press Escape. A fresh private browser opens
  the original tour; Tab remains inside it and Escape performs Skip.
- Twenty-two IDs complete; fourteen partial/pending. Remaining editing/query,
  security/business and operational work is not claimed complete. No production
  data access, push, merge or deployment. Preview remains synthetic-only.

### Batch 46 — further PY-04/PY-08/PY-27 password boundaries (2026-10-17)

- Confirmed reset accepts a schema-valid Unicode string that exceeds the existing
  bcrypt72-byte limit, then raises uncaught ValueError/HTTP500. Return the same422
  and existing “Password is too long” text as registration, before claiming the
  link. No new password policy, storage/hash algorithm, account field or data repair.
- Original Login/Register/Reset/Confirmation controls validate that same existing
  byte limit and Python/Unicode minimum character count before submission. Typed
  values are never trimmed, normalized or truncated; Show/Hide, single-character
  login, eight-character registration/reset and72-byte ASCII/Unicode boundaries
  stay unchanged. Existing server messages reused; no forms/design changes.
- Four before backend cases reproduce one500 failure (1.113s); all pass after
  (1.093s). Thirty-two browser input checks reproduce eleven mismatches before,
  all pass after. All184 backend tests pass,32.865s;39 pinned PG cases pass,41.348s,
  including rejected-reset persistence, paid-access preservation, exact-byte retry,
  old-token revocation and one-use links against native PostgreSQL.
- Actual original browser reset rejects overlong input before POST; direct invalid
  request is422 and leaves old login/link usable. Same link resets to an accepted
  exact-boundary password, invalidates old login, stays single-use and signs in
  through the original Login form, with the original subscription unchanged.
- First browser cleanup incorrectly requested another link during the existing
  reset cooldown. Preserve that rule: revised test requires only a disposable
  in-memory preview reseed afterward, restoring default fabricated passwords.
  The passing workflow never requires changing cooldown or production records.
- TypeScript/Vite passes,1.45s/102modules;JS323.79kB/91.93kB gzip; original CSS
  index-BEBH-Ai6.css unchanged. Evidence: tools/local-test/evidence/batch-46-*.json.
  Manual: /register at http://127.0.0.1:55446; original password form/visibility
  remain. Demo reset requests use only /__test__/inbox; no email is delivered.
- Twenty-two IDs complete; fourteen partial/pending. Remaining edit/query/security
  and owner/operational decisions remain. No production, push, merge or deployment.

### Batch 47 — interrupted query batch and post-restart recovery (2026-10-17)

- Recovery started on codex/priceyard-original-preserved-20261016 at
  0e1e1187c460134d580e2e511b88404009d4a7f3. Keyboard commit6c0efbf, offline
  commitdf74e55 and all previous work remain in ancestry; nine modified tracked
  files and all new batch47 tests/evidence survived. Master remains76dbd27588de4aa37f3163d8b263d4b72a2cff32;
  backup remains258991019e5af8b36eff407a8efa2c9fd03dd644. No discarded changes.
- Preserved interrupted changes: optional positive commodity_id on existing
  market-signal, quality-signal and cost-breakdown GET lists applies SQL filtering
  before materialization. Commodity detail supplies its existing ID. Default Admin
  lists retain every record/order; original permissions, defensive UI filtering,
  independent failure/race handling, cost formula, measurements and markup remain.
  No database/form fields, business rules, prices, history edits or new features.
- Before evidence: six tests reproduced three failures/three errors before the
  optimization; a separate missing fixture import was fixed before interruption.
  Preserve the later failed native report as batch-47-postgres-timeout.json:
  40 tests,1 failure,9 errors,82.598s with local connection timeouts. Do not erase
  that result or describe the original heavy cluster as successfully recovered.
- Confirmed local test-infrastructure problem: retained per-test schemas left
  139,451 files/about1458MiB in its synthetic database directory. Old logs show a
  startup fsync scan reaching160s, checkpoints syncing6060–11128 files, then many
  autovacuum worker-start warnings. Checkpoint write pacing near269s alone is not
  proof of a freeze. Windows41/6008 confirm an unclean restart; available evidence
  does not establish a single OS-level cause or prove pre-restart memory exhaustion.
  Repeated full-suite retries on the growing fixture were an unsafe resource habit.
- Old pinned fixture postgres-revocation (identifier7697280512362447984,port55447)
  is stopped, with its stale PID/control evidence and all synthetic schemas retained.
  Its control state reflects interrupted shutdown; it was not restarted or repaired
  during this recovery because another large fsync scan would add disk pressure.
  The separate pre-existing PostgreSQL service/process tree was left untouched.
- Initialized a separate empty workspace-only postgres-recovery-20261017 fixture:
  identifier7697651361316763724, literal127.0.0.1:55448, same synthetic-only test
  user/database/purpose. Explicit --recovery-cluster selects only this hard-pinned
  profile; arbitrary marker paths/ports/identities still fail. Shared buffers32MB,
  max_connections12, maintenance_work_mem16MB, autovacuum_max_workers1; fsync and
  normal durability stay enabled. No production configurations/credentials used.
- Native runner now acquires one nonblocking exclusive lock before database imports
  and refuses a run that would exceed80 retained synthetic schemas. A real second
  runner was rejected before any database import with the server stopped. No schema
  was dropped. Each connection/mutation still checks live directory/system identity;
  TCP/DNS/provider and negative-destination guards remain enabled. Full native suite
  passes40/40 in27.681s. Graceful shutdown completes8.035s checkpoint; control state
  verified shut down. Never start the old heavy fixture automatically on resume.
- Run heavy phases sequentially: PostgreSQL then stop; full backend190/190 in23.669s;
  then a single in-memory preview and one browser at a time. No dependency install.
  Avoided another build/copy: all73 current frontend source files match the already
  TypeScript/Vite-verified frontend-7cf451c3d7a54985a699a81d503125d4 exactly. Existing
  batch47 build:2.65s/102modules, JS323.84kB/91.95kB gzip; CSS index-BEBH-Ai6.css
  unchanged. Current browser verification uses that exact matching artifact.
- New scope browser checks pass for three scoped responses, complete default Admin
  lists, unchanged Egusi history and calculator totals210200/420400, with temporary
  fixtures removed/catalog restored. Five detail error/navigation races pass; all14
  original Admin labels/totals, one summary request and outage recovery pass. All
  browser requests literal loopback, native service workers blocked, providers off.
- Old preview PID1252 was reused by Windows fontdrvhost.exe after restart. Launcher
  refused to stop it, correctly. Verified PID metadata predates boot and55446 was
  unused; archived only the stale PID record, leaving that Windows process untouched.
  New synthetic preview launcher18556/worker25204 was identity-verified for checks.
  After checks, only those verified processes were stopped; both55446/55448 were
  confirmed unbound. No added test workload remains running (stop-recovery evidence).
- Recovery evidence: tools/local-test/evidence/batch-47-*-recovery.json,
  batch-47-postgres.json, batch-47-run-lock.json and earlier before/after records.
  Current post-restart machine had about2.8GiB available initially/3.3GiB later and
  about214GiB disk free; these snapshots cannot diagnose its earlier memory state.
- Exactly22 IDs complete /14 partial or pending; this extends PY-20 without claiming
  it complete. Remaining IDs02,05,07,08,13,14,20,27,28,29,30,31,35,36. Preserve
  14-day trial, NGN2500/30days, NGN6000/90days and all approved rules. Stop after
  recovery report; no new batch, production access, push, merge or deployment.

### Batch 48 — Buying zone/Sell-watch query scope and bounded verification (2026-10-17)

- Owner resumed authorized development from c0bb6eb. Two existing sections now
  pass the current commodity ID to their existing GET lists. Optional positive
  commodity_id filters SQL before hydration; no filter still returns every record
  in original order for Admin. No changes to forms, wording, calculations, access,
  measurements, subscription/referral policies or stored business records.
- Ten scope tests before reproduce two failures/two unexpected-keyword errors;
  six earlier scope cases remain passing. All194 backend tests pass after,30.705s.
  Existing native scope fixture now checks all five resources with two matching
  rows hydrated from42 and preserves raw history. Scope plus both planning audit/
  concurrency cases pass3/3,2.313s; retained schemas40 to43 of80. Native suite
  explicitly selects existing cases with --test; report lists them, guards unchanged.
  Do not confuse this focused run with the full40 baseline that passed in batch47.
- PostgreSQL on pinned recovery55448 stopped gracefully before build/browser.
  Build --reuse validates the existing synthetic snapshot, copies only approved
  source/public/config files, reuses dependencies and invalidates its serving
  marker until success. Refuses active preview/native test ports and stale removed
  source. Actual refusal with running preview leaves the valid marker unchanged.
  No dependency copies/installations; TypeScript/Vite passes1.47s/102modules,
  JS323.88kB/91.95kB gzip; original CSS index-BEBH-Ai6.css unchanged.
- Actual browser verifies both scoped responses/downloads, unchanged original
  sections, complete default Admin lists and unchanged price history. These two
  resources have no delete endpoint: no new feature added for cleanup. Restarted
  only the disposable memory preview to remove fabricated planning fixtures.
  Five detail failure/race regressions and all14 dashboard labels/totals, one
  summary request and recovery pass. No external browser requests/providers.
- Evidence: tools/local-test/evidence/batch-48-*.json. Manual: local /commodities/Egusi
  while logged in as admin@example.com / PriceYardDemo8!; Buying zone/Sell-watch
  headings/design stay the same. API requests include commodity_id; Admin lists
  remain complete. Any preview fixtures are synthetic only.
- Exactly22 complete /14 partial or pending. PY-20 remains partial for Storage
  suitability, full history and other unbounded lists. Continue approved technical
  work; do not invent new business/source/session policies to inflate completion.
  No production access, push, merge or deployment.

### Batch 49 — Storage suitability query scope (2026-10-17)

- Added optional positive commodity_id filtering to the existing Storage suitability
  GET list/service and current-detail request; original access/order/default complete
  Admin list retained. Existing fields, validation and linked-price checks unchanged.
  No measurements, form fields, business records or appearance changes.
- Twelve scope tests before reproduce one failed HTTP selection and one missing
  service keyword error; all12 pass after,1.758s. Existing native scope case now
  checks all six resource types; it and Storage audit/rollback/concurrency pass2/2,
  1.676s. Small pinned fixture retained schemas43 to45, of80; stopped before build.
  Latest full backend194 passed batch48; latest full native40 passed batch47.
- Credential-free snapshot rebuilt with --reuse, no dependency copy/install.
  TypeScript/Vite1.19s/102modules; JS323.90kB/91.95kB gzip, original CSS
  index-BEBH-Ai6.css unchanged. Actual browser verifies all three planning scopes,
  default Admin lists, excluded unrelated rows and unchanged full price history.
  Reseeded only the disposable memory preview afterward. Five detail regressions
  and all14 Admin cards, one summary request and outage recovery pass.
- Added a local stop_preview.ps1 helper using exact script/executable/parent and
  synthetic marker checks; verified it stops only the disposable preview and checks
  its port unbound. This preserves the launcher safeguards and avoids generic kills.
- Evidence: tools/local-test/evidence/batch-49-*.json. All heavy checks sequential;
  native cluster stopped. Manual local commodity detail keeps the same six section
  headings/design. Exactly22 complete /14 partial or pending; PY-20 broader lists/
  history and remaining policies/operations still open. Local commits only.

### Batch 50 — Approved Market/Quality editing safeguard (2026-10-17)

- Owner explicitly approved the six-form scope in docs/ADMIN_EDIT_PREFILL_APPROVAL.md.
  First two forms only: entering an ID loads saved values from the existing Admin
  list into existing controls; switching/clearing IDs restores approved behavior.
  Pending/unknown IDs cannot save a mismatched record. No new fields, layout,
  database changes, automatic writes or business policies.
- Before build, actual old-browser behavior reproduces four loading/prefill failures.
  After:18 browser checks pass, including changing one field without losing saved
  optional values, reload, explicit clearing, other/unknown/blank IDs and creation.
  Initial check hit ambiguous existing error/toast text; narrowed only the test
  locator and reran successfully. Price history unchanged; zero external requests.
- Nine intelligence audit backend cases pass,0.681s; two existing native Market/
  Quality atomic audit, rollback and concurrency cases pass,1.562s. Small pinned
  fixture schemas45 to47 of80, stopped gracefully before build/browser. Latest
  full backend194 remains batch48; focused runs do not imply a new full-suite run.
- Reused isolated build passes TypeScript/Vite,1.27s/103modules; JS325.17kB,
  92.47kB gzip; original CSS index-BEBH-Ai6.css unchanged. All14 original dashboard
  cards/totals, one summary request and outage recovery pass. Evidence batch-50-*.
- Exactly22 complete /14 partial or pending; PY-27 four approved forms still open.
  Next Buying/Sell-watch, then Storage/Cost in batches of two. Synthetic-only
  preview http://127.0.0.1:55446; existing admin@example.com / PriceYardDemo8!.
  No production access, dependencies installed, push, merge or deployment.

### Batch 51 — Approved Buying/Sell-watch editing safeguard (2026-10-17)

- Applied the approved shared saved-value loader to only Buying zones and Sell-watch
  windows. Existing controls, date/period semantics, full list, layout, validation,
  create/PATCH endpoints and audit behavior retained. No new fields or policies.
- Before build, four browser loading/prefill failures reproduced for these forms;
  previous Market/Quality checks remain passing. After:36 browser checks pass for
  all four forms, one-field preservation/reload, explicit clearing, switching IDs,
  unknown/blank IDs and original creation. Decimal assertions compare numeric
  amounts, respecting existing API decimal strings (100 versus100.00).
- Nine planning audit backend tests pass,0.748s; two existing native Buying/Sell-watch
  audit rollback/concurrency tests pass,1.625s. Pinned small fixture schemas47 to49
  of80, stopped before build. Reused build passes TypeScript/Vite2.17s/103modules,
  JS325.33kB/92.58kB gzip, unchanged original CSS index-BEBH-Ai6.css. No dependency
  copies/installations. Fourteen dashboard cards/totals and outage recovery pass.
- Synthetic planning fixtures have no original delete endpoint; test does not add
  one or issue unsupported deletes. Reseed only the disposable memory preview at
  next restart. Price history unchanged; zero external browser/provider contacts.
  Evidence batch-51-*.json. Exactly22 complete /14 partial or pending; remaining
  approved forms are Storage/Cost. No production, push, merge or deployment.

### Batch 52 — Approved Storage/Cost editing safeguard; PY-27 complete (2026-10-17)

- Last two approved forms now use the same existing-control saved-value loader.
  Storage status/notes/linked-price values and all saved costs load from the
  existing authorized list. Original blank-ID creation defaults, explicit clearing
  (blank cost remains zero), formulas, inputs, layout, access and policies remain.
- Before build: four loading/prefill failures reproduced for Storage/Cost; previous
  four forms remain passing. Final actual browser suite61/61 passes across all six:
  one-field edit preserves other details, reload, explicit clearing, switched IDs
  replace only unsaved changes, unknown IDs block submit, blank IDs restore defaults,
  original creation, saved zero costs and accurate cost totals. Cost assertions were
  corrected for existing decimal string/number formatting; no application amount
  conversion or calculation changed. Price history unchanged; zero external requests.
- Full196 backend tests pass,30.855s, synthetic SQLite with TCP/DNS denied. Two native
  Storage/Cost-reference audit rollback/concurrency cases pass,1.740s. An unknown
  test name was rejected before execution; corrected to the existing case without
  changing any guard. Small pinned fixture schemas49 to51 of80, stopped gracefully.
  Full40 native baseline remains batch47; do not relabel focused tests as full suite.
- Reused snapshot build TypeScript/Vite passes2.02s/103modules, JS325.48kB/92.51kB
  gzip; original CSS index-BEBH-Ai6.css unchanged.14 original dashboard labels/totals,
  one summary request/outage recovery and five detail failure/race regressions pass.
  Browser scenarios/PG/backend/build run sequentially. No new dependency copies or
  installs. Reseed only the disposable memory preview to clear temporary planning
  records; no unsupported deletes or production/database changes.
- Evidence tools/local-test/evidence/batch-52-*.json. PY-27 identified scope complete.
  Exactly23 complete /13 partial or pending:02,05,07,08,13,14,20,28,29,30,31,35,36.
  Those still include owner policy choices, broader compatible bounds/history work
  and operational/live-provider verification; none claimed complete by this batch.
  Local commits only; master and preserved backup stay unchanged. No push/merge/deploy.
- Manual check: http://127.0.0.1:55446, admin@example.com / PriceYardDemo8!. In an
  original Admin section, create a synthetic entry and enter its displayed ID in
  ID to edit: existing saved fields populate. Alter one field, save and re-enter
  the ID after reloading to confirm other fields remain. Do not use real customer
  data. Trial14 days, NGN2500/30 days, NGN6000/90 days and approved policies retained.

### Batch 53 — Existing watchlist storage bounds (2026-10-17)

- PY-08 technical validation only: target_price now matches the existing PostgreSQL
  NUMERIC(14,2) column, like original price/cost amounts. No new field, screen,
  measurement, cap on stored valid values, subscription/referral rule or schema.
  Reject nonrepresentable input before writing instead of overflow500 or silently
  changing the intended target. Original whole-naira UI/step/layout unchanged.
- Before: both backend workflow cases fail; SQLite accepts an out-of-range target
  and silently rounds210000.001 to210000.00. Native PostgreSQL reproduces HTTP500
  on1000000000000 in one pinned synthetic schema (51 to52). Evidence records the
  expected failing baseline; no production contacted or existing data changed.
- After: both backend cases pass,0.394s, and the native workflow passes1/1,1.168s
  (schemas52 to53). Unset/zero/ordinary/max representable targets persist exactly;
  duplicates409, guest401, other-owner listing/deletion protection, valid deletion
  and invalid-request nonmutation all verified. Overflow/excess precision now422.
- Existing five watchlist notification regressions pass,7.792s, with fake delivery;
  independent channels/deduplication remain. Native fixture stopped gracefully
  before backend/browser work. Six actual original-browser checks pass: existing
  form error, no silent rounding, no invalid writes, valid save, reload and unchanged
  original watchlist/prices. A select-label test locator was corrected; no UI
  markup changed. Invalid browser fixtures cleaned using existing own-delete API.
- Frontend source unchanged; reused verified batch52 TypeScript/Vite snapshot,
  original CSS index-BEBH-Ai6.css. No dependency copies/installations. Full196 backend
  baseline remains batch52; do not claim the full198 suite was executed here. New
  native case extends coverage; last full40-case native run remains batch47.
  Evidence tools/local-test/evidence/batch-53-*.json. Exactly23 complete /13 partial
  or pending. Broader body/text limits and remaining owner/operational choices stay
  open. No production, push, merge or deployment.

### Batch 54 — Required cost values and calculated storage limits (2026-10-17)

- Further PY-08/PY-28 protection: reject nulls for non-nullable Cost breakdown
  columns before coercion/calculation; omitted values still retain saved values,
  and explicit zero still clears an individual cost. Validate the sum against
  existing NUMERIC(14,2) total columns before setting any values or saving audits.
  Original formulas, appearance, fields, measurements and policies stay unchanged.
- Before: two HTTP/backend failures (required-value500; SQLite accepts total beyond
  PostgreSQL capacity); native PostgreSQL independently reproduces null-edit500.
  After: two validation workflows pass0.240s and nine intelligence audit regressions
  pass0.725s. New native preservation workflow plus existing Cost audit rollback/
  concurrency case pass2/2,2.539s. Invalid requests leave raw costs, historical
  prices and audit records unchanged; valid corrections/zeros/max total still save.
- Seven actual cost-browser checks and61 existing six-form editing regressions
  pass. Rejected create/edit uses the existing error presentation, saved details
  and audit evidence remain unchanged, original save/zero clearing/reload works.
  Compare fetched records before/after to respect existing POST-versus-GET decimal
  formatting. Zero external requests. Synthetic planning fixtures from the editing
  regression require only disposable-memory preview reseeding at next restart.
-84 frontend source/public/config file hashes match the existing verified build;
  original CSS index-BEBH-Ai6.css retained. No build/dependency copy needed for this
  backend-only change. Small native fixture schemas53 to54 for expected failing
  baseline, then54 to56 for passing cases; cap80 retained, cluster stopped. Heavy
  phases serialized. Runtime Windows sandbox refused process-identity inspection
  and a stop signal; used the required platform approval mechanism without bypassing
  identity checks or touching unrelated processes. Routine work already authorized.
- Evidence batch-54-*.json. Exactly23 complete /13 partial or pending. Next existing
  Buying/Sell-watch required-value validation; no new business/source/session policy.
  No production access, migrations, dependency installs, push, merge or deployment.

### Batch 55 — Required Buying/Sell-watch values (2026-10-17)

- Preserve existing non-nullable database rules for both resources: explicit null
  for mandatory IDs, amounts or text returns422 before coercion/flush instead of500.
  Omitted fields retain saved values. Nullable valid-from/to and end-period still
  clear correctly; no new fields, layout, measurement or subscription/source rules.
- Before: both backend workflows reproduce500. After: full202 backend tests pass,
  28.253s, including new11-field null checks, omitted-value preservation, optional
  clearing, corrections, forbidden non-Admin writes and unchanged raw price/audit
  evidence on rejection. Three focused native tests pass2.296s: same preservation
  workflow and both existing atomic-audit rollback/concurrent-edit cases. Fixture
  schemas56 to59 of80, stopped before browser. Full40 native baseline remains47.
-65 actual original-form browser checks pass, including all61 earlier editing
  checks plus required-null rejection and record/audit preservation for these two
  resources. Optional clearing, create/edit/reload still pass for all six forms.
  Five detail regressions and all14 original dashboard labels/totals, one summary
  request and outage recovery pass. Zero external page/provider requests.
- Frontend source unchanged; reuse the84-file hash-matched build verified in54,
  with original CSS index-BEBH-Ai6.css and no copied/installed dependencies. Heavy
  phases run sequentially. Windows restricted-token startup failed inside sandbox;
  required platform approval allowed only the pinned synthetic PostgreSQL fixture,
  preserving all identity, network, exclusive-run and schema-budget guards.
- Evidence batch-55-*.json. Exactly23 complete /13 partial or pending. Disposable
  memory preview will be reseeded on next restart to clear temporary planning
  records; no unsupported delete endpoints added. Next remaining PY-08 signal
  required values; business/visible/production approval boundaries still apply.
  No production, push, merge or deployment.

### Batch 56 — Required Market/Quality signal values (2026-10-17)

- Further PY-08: required Market commodity/market/type/description and Quality
  commodity/market IDs reject explicit null before coercion/flush. Optional
  meanings, actions, quality/risk notes and linked price remain clearable under
  existing schemas; no new fields, confidence policy, source access or appearance.
- Before: two new HTTP workflows reproduce500; earlier two planning cases pass.
  After all four validation workflows pass0.495s and nine intelligence audit
  regressions pass1.133s. Shared fixture checks omitted fields, optional clearing,
  valid correction/reload, non-Admin denial and unchanged raw history/audits on
  invalid requests. Three focused native cases pass2.839s: same required-value
  workflow plus existing Market and Quality audit rollback/concurrency checks.
-69 actual six-form browser/API checks pass. Required nulls are422 with no record
  or audit mutation; all original creation/editing/optional clearing/reload checks
  still pass. Price history unchanged and zero external requests. Disposable
  planning records are cleared only by the next memory-preview restart.
- Native schemas59 to62 of80, cluster stopped before browser. Terminal polling
  lost its finished start-helper session; verified fresh process marker plus the
  literal loopback synthetic-only status rather than starting a duplicate process.
  Original84-file hash-matched frontend build/CSS reused, no frontend changes,
  copied dependencies or installations. Full202 backend baseline remains55; the
  focused runs do not claim a full204 run. Evidence batch-56-*.json.
- Exactly23 complete /13 partial or pending. Next Storage required IDs/status;
  preserve nullable notes/linked-price clearing. No production, push, merge/deploy.

### Batch 57 — Required Storage values; complete intelligence null guards (2026-10-17)

- Last resource in this PY-08 scope: commodity/market IDs and suitability status
  reject null before coercion/flush, matching their original non-nullable columns.
  Existing linked-price and optional storage/risk/quality notes remain clearable.
  No fields, measurement, grade, status terminology, appearance or policy added.
- Before: Storage HTTP workflow reproduces500, earlier four cases pass. After:
  full205 backend tests pass35.526s, no skips/failures/errors. Raw business history
  and audits remain unchanged on rejection; optional clearing, omitted-value
  preservation, correction/reload and non-Admin write denial are verified.
- Two focused native Storage cases pass1.677s: required-value/history preservation
  and existing audit rollback/concurrent-edit test. Fixture schemas62 to64 of80,
  stopped before browser. Full40 native baseline remains batch47; do not run a full
  current suite against this budget or claim a new full-suite native result.
-73 original-browser/API checks pass across all six forms, including every required
  null field and unchanged records/audits on rejection. All14 original dashboard
  labels/totals, one summary request/outage recovery and five detail failure/race
  regressions pass. Zero external page requests. Existing seven cost overflow/
  correction browser checks passed54 and full backend covers those paths here.
-84 source/public/config hashes match the existing verified frontend snapshot;
  original CSS index-BEBH-Ai6.css retained. No rebuild/copies/install needed for
  these backend-only batches. Heavy checks serialized, one browser at a time,
  retained synthetic schemas below80; old large cluster remains stopped/untouched.
  Reseed only the disposable memory preview after testing to clear fabricated
  planning records; no unsupported deletes or historical-record cleanup.
- Evidence batch-57-*.json. Exactly23 complete /13 partial or pending:
  02,05,07,08,13,14,20,28,29,30,31,35,36. Next compatible remaining request/input/
  query/history work and separately approved business/operational decisions. Do
  not repeat completed required-null guards or cost-total/target validation.
  Unknown legacy text lengths are not permission to invent caps or discard data.
- Master76dbd27588de4aa37f3163d8b263d4b72a2cff32 and backup258991019e5af8b36eff407a8efa2c9fd03dd644
  remain unchanged. Local verified commits only; no credentials read, production
  services/data, production migrations, push, merge or deployment. Routine local
  work remains authorized; Windows/Git sandbox restrictions are still enforced.

### Batch 58 — PY-31 bounded missed-payment recovery complete locally (2026-10-17)

- Focused a remaining item: pending/failed purchases now have an explicitly invoked
  recovery job when webhook and customer return were missed. Reuses existing strict
  provider verification and atomic activation; no charging, guessed evidence,
  successful-legacy re-credit, new subscription/referral policy, schema or UI.
  CLI defaults to read-only preview; --apply is explicit. Nothing auto-starts and
  no scheduler/production config was installed. See docs/PAYMENT_RECONCILIATION.md.
- Serial bounded pages default25/max100, fixed ceiling and resume cursor, soft time
  budget, generic ID/outcome reporting. PostgreSQL session lock permits one applying
  worker, released/invalidated in finally. One failed purchase does not stop others.
  Existing paid/trial carry-forward and manual-grant review holds are unchanged.
  Completed sweep does not mean every purchase was confirmed; the future scheduler
  must retain the cursor so unconfirmed older purchases cannot starve later ones.
- Seven new backend workflows pass0.390s: dry-run immutability, missed success and
  failed-init recovery, paid/trial time, indefinite holds/replay, mismatched evidence,
  missing subscription, bounded pages/snapshot, audit rollback/retry, per-customer
  outage isolation, time budget, safe command default and redacted failure reporting.
  Existing eight HTTP verification tests pass1.065s. Full211 backend baseline passed
  30.107s before final CLI-error test; do not claim a full212 run from that alone.
- Two focused native cases pass1.531s: same recovery/value/evidence workflow and
  overlapping second-worker exclusion plus simultaneous webhook. Exactly one
  activation/audit; job lock released. Schemas64 to66 of80, cluster stopped before
  backend/browser. Full native suite remains historical baseline only.
- Actual isolated browser proves preview never verifies, wrong amount stays Free/
  pending, recovery grants existing original Dashboard/history access without a
  checkout callback, and repeat makes no new verification/extra days. Existing
  wrong-amount/activation-failure/replay payment workflow and all14 dashboard cards,
  one summary request/outage recovery pass. All providers fake; zero external
  requests. New test-harness endpoint is scoped to the existing fabricated verify
  account/purchase, not a production API or product screen.
- Frontend original files/build untouched; existing verified snapshot reused.
  Evidence batch-58-*.json; native tests serialized and no dependencies installed.
  PY-31 application scope complete:24 complete /12 partial or pending:
  02,05,07,08,13,14,20,28,29,30,35,36. PY-35 retains live scheduling/checkpoint,
  provider/host operations and evidence-based legacy repair approval boundaries.
  No production, push, merge or deployment. Next PY-28 migration preservation.

### Batch 59 — PY-28 current migration-preservation scope complete (2026-10-17)

- Added a read-only online Alembic preflight before migration steps: populated
  unversioned, unknown, forked or pre0021 starts require reviewed migration. Empty
  initialization and current reviewed0021/0022 starts remain supported. No bypass
  flag, auto-stamp, auto-merge, activity reset, guessed cost link, new migration or
  application field. Original0006/0020 and0022 files remain unchanged. Existing0022
  downgrade still refuses erasing revocation evidence. Contract:
  docs/MIGRATION_PRESERVATION.md. Offline SQL needs separate review, not live proof.
- Two native cases pass3.136s. A populated0005 fixture is refused before old focus/
  cost-link migrations, with full rows/columns/revision snapshots identical,
  including active Honey Beans, private source, original price/cost association,
  paid subscription and audit JSON. Fresh initialization then populated0021-to0022
  still preserves original users/catalog/prices/sources/payments/purchased access;
  zero initial revocations and downgrade refusal verified by the existing case.
- First native attempt had a fixture error:0005 predates the payments table.
  Removed only that invalid fixture insertion; the separate populated0021 test
  retains real payment-preservation coverage. This is not claimed as an original
  application failure. Failed setup schema retained (66 to67); passing cases67
  to69 of80. Native fixture stopped before remaining tests. No destructive cleanup
  or full native-suite rerun. Evidence includes the setup error transparently.
- Full216 backend tests pass29.966s, no failures/errors/skips: seven recovery tests,
  four new preflight cases plus prior coverage. Preflight tests verify read-only
  behavior, empty/known-baseline acceptance, unknown/forked/unversioned rejection,
  unchanged stored values and generic errors without private content.
- Actual browser: seven original home/Guest/filter/Trial-plan/history/Admin-form/
  mobile/login-quota workflows pass, no Grade labels, no mobile overflow; all14
  original dashboard metrics, one summary request and outage recovery pass. No
  application frontend change. Source hashes/build remain the existing verified
  snapshot; no dependency installation/copy or expensive rebuild needed.
- PY-28 finite current application scope complete;25 complete /11 partial or pending:
  02,05,07,08,13,14,20,29,30,35,36. Do not keep this item open for unspecified future
  migrations, or claim production preservation from local proof. Historical damage
  cannot be reconstructed without evidence. Older populated local migrations now
  intentionally stop for review. PY-35 retains production revision/backup/restore,
  rollout and any repair approvals. Next finite PY-20 history/query bounds and
  PY-36 documentation/maintainability; preserve remaining owner-policy gates.
- Evidence batch-59-*.json. Master/backup retained; no production databases,
  credentials, services, migrations, push, merge or deployment accessed/performed.

### Batch 60 — bounded complete CSV export (2026-10-17)

- Resumed clean from556cf6b on the existing original-preserved branch; no audit,
  resets or previous completed-item expansion. PY-20 export no longer materializes
  every ORM record and the complete CSV string before responding. Server cursor
  fetches100 price records at a time; observed transient handoff at most200 live
  price objects. Related signal collections and individual text sizes remain
  proportional to each record, not a byte-size guarantee. No record-count cap.
- Original Admin-only route, filename,13 columns, numeric values, approved-only
  selection, inclusive UTC date filters, complete chronological/id order,
  inactive-catalog/outdated history and formula neutralization preserved. Private
  sources remain absent. No frontend, design, fields, policies or records changed.
- Stream owns its database session; success, partial close, failed send and
  cancellation cleanup close cursor/session. Invalid date range returns422 before
  response starts. Later database/network errors interrupt the download rather
  than silently truncate a successful complete file.
- Full221 backend tests pass33.824s. Five new tests cover multi-batch completeness,
  ordering, unchanged stored records, filters/empty exports, route permissions,
  validation and connection cleanup. First targeted run exposed the expected
  two-batch handoff; corrected the test's bound instead of claiming one-batch
  peak memory. Existing five spreadsheet-injection tests still pass.
- Focused native PostgreSQL case passes3.405s, all251 approved rows retained,
  all253 stored rows unchanged, bounded hydration and partial-stream connection
  return verified. Initial native attempt had a test-helper import-path error;
  corrected explicit local import, retained failure evidence. Fixture69->70 on
  failed harness setup,70->71 on passing case, of80; stopped before browser work.
- Actual original CSV screen/download and Guest401/Trial403 checks pass; original
  headings, filename/data, source exclusion and no grades verified. Existing
  compiled frontend reused; no build, dependency install or dependency copy.
- Evidence batch-60-*.json.25 complete /11 partial or pending remain:
  02,05,07,08,13,14,20,29,30,35,36. PY-20 is still partial for full JSON history/
  other lists; do not claim all query work complete. Next finite task: PY-36
  current documentation and behavior-preserving readability of existing forms.
- No production contact/data/migration, credential reads, push, merge or deploy.

### Batch 61 — current documentation, readable original forms and build recovery (2026-10-17)

- PY-36 finite current application scope complete. Replaced obsolete staged API
  notes (including claims that implemented resources were unimplemented) with a
  source-derived106-operation reference. Compared exact method/path inventory to
  guarded local OpenAPI:106/106 match;123 relative file links resolve. No database
  connection, credentials or provider access for documentation verification.
- README now links the live tracker, approved behavior contracts, local workflow,
  migration-preservation and payment-recovery guides. APPLICATION_CONTRACTS.md
  distinguishes implemented safeguards from pending owner policies and PY-35
  operations. LOCAL_DEVELOPMENT.md explains safe demo/tests/build resumption,
  evidence retention, pinned small native fixture and resource limits. No new
  audit, application feature, policy or commercial-readiness claim.
- Six original Admin intelligence forms in two legacy compressed source files
  expanded into readable statements/JSX. Allowlisted formatter verifies emitted
  syntax/literal equality against both input and previous verified snapshot;
  no changes to names/fields/defaults/actions/measurements/markup behavior. Initial
  formatter comparison was too sensitive to layout (including SourceFile text);
  corrected structural comparison excludes positions/source layout but retains
  node kinds, operators, declaration scope and all literal/identifier text.
- TypeScript/Vite pass,103 modules,1.43s Vite. Stronger independent proof: built
  JS index-BgXjH4fu.js and CSS index-BEBH-Ai6.css hashes are byte-for-byte identical
  to the previous verified build. Exactly the same compiled original UI.
- Actual Windows restricted-token build failed esbuild directory access, and its
  ready marker correctly stayed absent. Normal approved escalation then exposed
  a real interrupted-build resumption gap: --reuse required that missing marker.
  Fixed only local harness PY-30: resume the preserved in-progress identity,
  revalidate the same port/path/purpose checks, and publish ready marker only
  after both TypeScript/Vite succeed. No manually restored ready marker, weakened
  network/secret guard, new dependency tree or security restriction bypass.
- Four file/process-free mock tests verify failed resume never publishes ready,
  both steps must pass, unapproved purpose stops before copying/building, and an
  active test port stops before marker reads. Targeted4 pass0.019s. Final full225
  backend tests pass32.509s, zero failures/errors/skips. Repeated broader run was
  after new harness/global-mock tests, not repeated native/schema-heavy testing.
- Actual browser: all six existing forms retain saved-value loading, field edits,
  required-null rejection, reload/clearing/ID-switch/creation behavior and unchanged
  original price history. All14 dashboard labels/totals preserved, one summary
  request, outage recovery; seven original home/Guest/filter/Trial/history/Admin/
  mobile/login-quota workflows pass, no grades or mobile overflow. Browser workers
  and external requests disabled; synthetic fixture only. Planning-form test
  entries without original DELETE APIs remain synthetic until preview reseeding.
- No native rerun for pure docs/formatting/harness change. Focused native export
  proof from60 retained, full40 baseline remains47;71/80 schemas retained and
  stopped. Build/browser/backend phases serialized; no dependency installations,
  copied dependency trees or unbounded new fixture/file creation.
- Evidence batch-61-*.json.26 complete /10 partial or pending:
  02,05,07,08,13,14,20,29,30,35. Next finite PY-20 full JSON history/list bounds
  and PY-29 stable identity/concurrent duplicate protection; no automatic catalog
  merges or changes to original filter semantics. Source/referral/session/input/
  calendar/movement policy and production gates remain explicit in their rows.
- Master/backup preserved, verified changes saved only on the existing local
  development branch. No production data/services/migrations, credential reads,
  push, merge or deployment. Preview remains guarded at127.0.0.1:55446.

### Batch 62 — concurrent catalog identity protection (2026-10-17)

- Resumed clean fromaca2585. PY-29 existing case-insensitive commodity and
  name/state market duplicate checks now use transaction-owned PostgreSQL
  advisory locks (separate unused keys4/5 in existing namespace741523). Checks
  serialize across application workers until the existing audited transaction
  commits or rolls back. No schema/index additions, name/state/country policy
  changes, automatic merge, legacy-data rewrite or new form fields.
- Five new catalog tests cover case/whitespace collisions, rename/state conflicts,
  preserved IDs/metadata, allowed distinct market states and untouched legacy
  case-variant rows. Existing atomic catalog audit tests remain passing:
  nine focused tests1.232s. Full230 backend tests pass131.731s, zero failures/
  errors/skips. Run was slower than61; no repeated full-suite runs performed.
- Native create-versus-create and create-versus-rename checks prove contender
  waits through first writer's audited transaction. After commit it returns409;
  after rollback it succeeds once. Four intended audited writes, saved metadata
  and complete original price/source history remain correct. At most two owned
  worker threads, joined before next case; no overlapping suites.
- Initial focused native run: first case passed, second failed in connection
  setup before its application checks. Restricted-runner pg_ctl also incorrectly
  reported no server. Approved runner verified same healthy pinned PID35140 and
  live identity; only failed rollback case retried and passed1.484s. Exact Windows
  cause is unproven; log shows host-software client abort. No application change,
  timeout increase, fixture restart, data deletion or weakened guard to pass.
  Initial report retained. Schemas71->72 first case, no schema for failed setup,
  then72->73 passing retry, of80. Fixture gracefully stopped before browser work.
- Actual original catalog forms: edit/revert preserves IDs/names/fields; referenced
  deletion remains rejected, duplicate case/whitespace creation shows existing409
  message and adds no catalog/audit rows. Complete price history and four intended
  continuous edit audits preserved. Initial browser harness used “Save” in new
  creation mode; corrected to original “Create” control and handled response/click
  promises together. No application screen/button change.
- All14 original dashboard labels/totals, single summary query and outage recovery
  pass.84 frontend source/public/config files and JS/CSS hashes match the existing
  verified build; no rebuild, dependencies installed/copied or design changes.
- Evidence batch-62-*.json.26 complete /10 partial or pending remain:
  02,05,07,08,13,14,20,29,30,35. PY-29 stays partial for filter/link-scope work;
  do not infer completion of all identity issues from duplicate race tests.
- No production services/data/credentials/migrations, push, merge or deployment.

### Batch 63 — close identified local testing-foundation scope (2026-10-17)

- PY-30 now has finite acceptance rather than remaining “ongoing” merely because
  future development will need tests. docs/TEST_COVERAGE.md maps existing executable
  checks to critical workflows and six requirements: service/API automation,
  native concurrency, real original-UI browser coverage, transport/config/secret
  isolation, guarded builds and bounded resumable execution/evidence. Current
  identified infrastructure/coverage requirements are satisfied; new fixes still
  require their own tests. This does not mark unfinished business policies or
  other defects complete, claim100% coverage, run CI/deployment or certify live
  services. Operational/provider acceptance remains PY-35.
- Secret-denial probe now targets an asserted-nonexistent synthetic sentinel;
  it cannot read an application dotenv even if the guard regresses. All six
  probes pass0.018s: TCP/DNS/native PostgreSQL/engine/persistent SQLite/child/
  nonlocal-listener denial, fresh memory persistence and cleared provider config.
  No actual secret contents opened, external connections or child processes launched.
- Current application/backend/DB source unchanged from verified8f364ac. Reused
  full230 backend pass62 and focused native catalog evidence, with original
  setup-timeout report retained; no needless full/backend/native rerun. Full40
  native baseline is still47, not a newly executed suite.73/80 retained schemas,
  fixture stopped. No additional PostgreSQL schemas/queries, builds/dependency
  copies or process overlap for this test-only sentinel/coverage batch.
- Actual final original browser smoke check: seven home/Guest/filter/Trial/history/
  Admin/mobile/login-quota workflows pass, no grades or mobile overflow; external
  requests zero. Catalog/all14 dashboard checks62 and six-form checks61 retained.
  Current84-file frontend/source and compiled asset preservation evidence62 used.
- Coverage/evidence verifier checks70 relative source/report/doc links, full230
  backend and earlier40-case native successful reports, clean isolated/browser
  results and explicit retry/non-production limits. No test totals fabricated by
  combining retries or describing focused cases as a full current native run.
- Evidence batch-63-*.json. Exactly27 complete /9 partial or pending:
  02,05,07,08,13,14,20,29,35. Next finite technical work: full JSON history/list
  query bounds and remaining stable-filter/cross-record scope issues. Current
  source/referral/session/input/day-filter/movement policy gates stay unchanged.
- Existing design,14 cards, fields, names, measurements, pricing/trial/referral
  rules and all business records preserved. Local commits only; no production
  access/data/migrations/credentials, push, merge or deploy. Guarded preview at
  http://127.0.0.1:55446; PostgreSQL stopped.

### Batch 64 — preserve linked price scope during corrections (2026-10-17)

- Resumed clean fromd0f3862. PY-29 identified parent-side gap: child creation/
  editing already required matching commodity/market, but correcting the parent
  price could strand saved observations, including a validate-then-insert race.
- Market/quality/storage reference validators now share the parent's transaction
  lock and refresh its committed identity before checking the same existing
  matching rule. Parent scope corrections use that lock and indexed child-ID
  existence checks, returning409 before any write if saved linked records would
  point to a different commodity/market. No child/link rewrites, migrations,
  fields, market/measurement/policy additions or changes to delete behavior.
- Valid price-value edits and unlinked commodity/market corrections remain;
  unchanged identities on metadata edits do not reject legacy observations.
  Missing/mismatched child links retain existing404/422 behavior. Parent/child
  rejection preserves business rows and audit history; private sources never
  enter validation error text.
- Six focused tests pass0.540s; full236 backend tests pass85.410s, zero failures/
  errors/skips. All three child types cover blocked commodity/market correction,
  unchanged rows, unlinked correction, original value edits and rejected stale
  links. HTTP rejection also preserves stored prices/observations/audits.
- One selected native PostgreSQL case passes2.058s: three child types, both save
  orders, at most two owned threads at once. Child-first saves once and conflicting
  parent gets409; parent-first correction saves once and stale child gets422.
  All saved links match their parent; six intended audits, sources and identities
  correct. No failed setup/retry, full native rerun or new fixture.73->74 schemas
  of80; fixture stopped in finally before browser tests. Durability kept enabled.
- Actual browser verifies all three saved links/history unchanged on rejection,
  existing error responses and original Admin price screen. Original create/
  approve/correct/outdate/reject/reload and complete sanitized audit workflow pass;
  all14 dashboard labels/totals, one summary request and outage recovery pass.
  Temporary synthetic Storage observations require preview reseeding afterward;
  no new DELETE feature added for cleanup. No real customer/business data touched.
-84 frontend source/public/config hashes match existing verified build; no UI,
  terminology, fields, bag weights, grades, CSS/build/dependency changes.
- Evidence batch-64-*.json.27 complete /9 partial or pending remain:
  02,05,07,08,13,14,20,29,35. PY-29 still needs stable-filter identity; do not
  claim complete from linked-record protection alone. Next that finite task.
- Existing trial/prices/referral/session rules preserved. Local commits only;
  no production credentials/services/data/migrations, push, merge or deployment.


### Batch 65 ? PY-29 stable filters and rename-safe links (2026-10-18)

- Resumed preserved uncommitted work from427c670; no audit restart. Current and
  history endpoints accept optional existing commodity_id/market_id INTEGER IDs,
  with positive/storage bounds. Existing text search remains compatible and
  combines with explicit IDs rather than overriding them. No schema additions.
- Original dropdown labels/layout/options remain; values submit existing IDs,
  keeping prefix commodities and same-name markets separate. Detail links carry
  commodity IDs, ignore obsolete path names after rename and show the current
  saved name. Literal percent names are not decoded twice in the browser.
- Existing shared-price pu IDs resolve the commodity only; previews still use
  current approved public prices, never the historical row's values or sources.
  Coming-soon links carry the existing commodity ID. Invalid/conflicting IDs and
  ambiguous legacy names fail closed. No automatic aliases, catalog merges,
  historical edits, new measurements, forms or subscription changes.
- Public-only worker caching supports the exact current-price query IDs and
  commodity navigation ID. History, private/authenticated resources, unknown
  query parameters and cross-origin requests remain excluded.34 worker checks
  passed. No new caching policy, age threshold or visible wording.
- Backend: six focused identity/share tests and full242 tests passed, zero
  failures/errors/skips,117.822s. A literal-percent legacy handler test uses its
  once-decoded ASGI path directly because TestClient double-decodes that escape;
  the actual browser literal-percent navigation is separately verified.
- Native: one selected exact-ID/history/rename case passed4.294s on the pinned
  small recovery fixture.75/80 synthetic schemas retained; native fixture stopped
  in finally. No full native rerun, new cluster or dependency copies.
- TypeScript/Vite passed104 modules/2.19s using the existing snapshot. Restricted
  runner denied esbuild directory traversal; the same guarded build succeeded
  through approved escalation. No security guard/marker bypass.85 source/public/
  config hashes match; original CSS SHA256 remains1cb3438f14a262d4ad7efa4ad11153cf61867917aabf51e88a04c6655cffdb28.
- Browser: seven exact-ID/rename/record-preservation checks, seven original
  baseline workflows, four applied-filter cases, four navigation/history races,
  five detail-loading cases and all14 original dashboard labels/values/one-query/
  outage recovery passed. Initial new fixture missed existing required fields;
  corrected fixture only. Literal-name test awaited loaded rows. Navigation
  regression now checks unchanged visible labels and intercepts actual ID query,
  retaining its original stale-response assertions. All external requests zero.
- Evidence: tools/local-test/evidence/batch-65-*.json. Source-only API reference
  refreshed106 existing operations. Synthetic preview reseeded after temporary
  collision/rename fixtures; current local link http://127.0.0.1:55446/prices.
- Count:28 complete /8 partial or pending:02,05,07,08,13,14,20,35.
  PY-29 finite application-side scope complete. Existing unknown legacy links,
  historical repair decisions and production/provider verification remain PY-35;
  no automatic repair or production readiness claim. Next: PY-08/PY-20 unfinished
  technical bounds, preserving original full results and approved policies.


### Batch 66 ? PY-08 aggregate HTTP input bounds (2026-10-18)

- Started from verified5b60e52. Added pure ASGI input bounds before JSON parsing,
  database dependencies, payment verification or writes:4MiB actual body bytes,
 8KiB encoded URL/query and64KiB headers. These are technical resource budgets,
  not new form fields, plans, measurements or per-field editorial length rules.
- Declared oversize rejects without reading input. Actual chunks are checked
  independently of Content-Length; malformed/conflicting/mismatched lengths,
  early disconnects and overflow never enter application handlers. Buffering
  uses bounded bytearray storage rather than retaining an unbounded chunk list.
  Signed bytes are replayed exactly. Non-HTTP lifecycle and CORS remain intact.
- Existing2MiB decoded screenshot policy remains. Browser saved a fabricated
  maximum-size data URI unchanged. One4MiB+1 request rejected before payment
  verification, with prices/payment/audit rows unchanged. Payloads only in
  memory; no large disk fixture, new snapshot or overlapping heavy processes.
- Shared commodity path validation now uses the existing100-character catalog
  storage boundary, preventing arbitrary long unknown paths reaching activity
  writes. Valid100-character paths remain supported;101 returns422. This final
  source change justified one final full backend rerun, not extra native schemas.
- Nine focused request tests passed0.462s. Final full252 backend tests passed,
  zero failures/errors/skips,28.516s. Native selected rejection/preservation case
  passed3.179s: zero DB queries or provider verification on oversized input;
  original Admin history readable afterward and raw price rows unchanged.
  Pinned small fixture76/80 schemas retained and stopped in finally.
- Browser boundary/max-screenshot checks, seven original baseline workflows,
  four feedback-selection/save cases, both fake-provider checkout rejection/
  success navigation and all14 dashboard totals/one-query/outage checks pass.
  External/provider/production connections zero. Large synthetic screenshot
  fixture reseeded immediately after its check.85 frontend source/config hashes
  match65 build, no frontend/CSS changes or rebuild/dependency copies.
- PY-08 identified local application-bound scope complete. Operational request
  timeouts/proxy limits/distributed throttling remain PY-35. Old stored text,
  image policy, original valid field values and all customer data untouched.
- Owner separately approved docs/ADMIN_LIST_PAGING_APPROVAL.md on2026-10-18.
  This authorizes100-record Admin pages with Previous/Next, original forms/styles,
  full totals/all14 dashboard cards and compatible complete API results. No
  paging code included in66. Start with Users/Payments; public history/charts
  remain separate. Evidence: tools/local-test/evidence/batch-66-*.json.
- Count:29 complete /7 partial or pending:02,05,07,13,14,20,35.


### Batch 67 ? approved PY-20 Users/Payments paging (2026-10-18)

- Started froma512630. Owner approved the exact Admin paging scope recorded in
  docs/ADMIN_LIST_PAGING_APPROVAL.md. First two lists only: Users and Payments.
  Remaining lists/public history are not counted complete.
- New Admin-only /users/page and /payments/page return at most100 original-schema
  records. A single CTE statement returns full count and selected rows from one
  DB snapshot, even for an empty/out-of-range page. Original sort plus ID tie
  breaker; no mutation, new DB field, migrations or hidden100-record total cap.
- Existing full-list APIs still return complete arrays through schema-checked
  100-record native cursor batches. Private password/provider fields excluded;
  raw evidence unchanged. Each stream owns and closes its cursor/session after
  completion, query/send failure or cancellation. CSV implementation untouched.
- Original Users total uses the full count. Existing role/status controls stay;
  edit refresh keeps page, URL retains position on browser refresh/back, old
  responses/errors cannot overwrite a new page, and empty last pages move back.
  Payments remains read-only with original columns. Original CSS unchanged.
  No controls appear for short lists; approved Previous/Next appear above100.
- Six focused paging/stream/lifecycle tests passed1.679s. Full258 backend tests
  passed84.677s, zero failures/errors/skips. One native case covers both205-row
  resources, all pages/ties/full counts, one-query snapshots, bounded ORM loads,
  complete legacy streams and unchanged raw rows. Passed3.331s; small pinned
  fixture77/80 schemas retained, stopped before build/browser. No full native rerun.
- TypeScript/Vite passed105 modules/4.04s using the existing snapshot, no installs
  or dependency copies.86 source/config hashes match build. CSS matches verified
  original asset; a typo in an ad-hoc expected-hash assertion was corrected by
  comparing against the existing verified65 artifact, without rebuilding.
- Browser: seven paging scenarios passed for205 fabricated users/payments,100
  visible records maximum; all IDs reachable, full totals, edit/refresh/back/
  obsolete response+error, out-of-range page and375px original cards/layout.
  Original last-Admin rejection, full role/status/revocation/grant/audit workflow,
  seven baseline workflows and14 dashboard totals/one-query/outage recovery pass.
  Dashboard verified with both205-record and original small fixtures. External/
  production connections zero; phases sequential, one browser at a time.
- Disposable testing wrapper has a fixed-size sample control at
  http://127.0.0.1:55446/__test__/admin-paging. Its Load synthetic sample button
  and original demo login were browser-verified. Only in-memory example.com
  accounts/pending fake payments; no arbitrary fixture sizes, SQL or connections.
  Restarting preview resets sample. Current preview has the205-row sample for
  review; reseed before unrelated tests. No sample fields/markets/measurements
  added to application source or real business data.
- API source reference updated108 operations. Evidence:
  tools/local-test/evidence/batch-67-*.json. Counts remain29 complete /7 partial
  or pending:02,05,07,13,14,20,35. PY-20 next: other approved Admin lists; all
  public history/chart results remain unchanged and separate. Master/backup
  preserved; no production access, push, merge or deployment.


### Batch 68 ? approved PY-20 catalog paging and pending-save race (2026-10-18)

- Started fromb57c749. Extended the approved100-record Admin paging to Commodities
  and Markets. Full count/selected rows use one DB snapshot; original fields,
  forms, name ordering plus ID tie breaker and all record identities remain.
  Admin full-list APIs still return complete arrays through bounded streams.
- Public catalog APIs now stream every active record with unchanged schemas,
  preserving active/upcoming/state metadata. Public responses deliberately keep
  cache eligibility; Admin responses remain private/no-store. No inactive sample
  entries become public or acquire prices. Legacy callers are not truncated.
- During extension, reproduced a new67 hook race: a save held on page100, then
  navigation to200, completed by reloading100 and leaving loading stuck. Before
  browser evidence records actual reload100. Hook reload now reads current refs,
  uses the current navigator and avoids requests after unmount. After browser
  evidence records reload200, five visible records and enabled Previous. No
  business-rule changes; fault injection used a fabricated PATCH response only.
- Two focused catalog tests passed1.101s. Full260 backend tests passed86.934s,
  zero failures/errors/skips. One native case for both205-row catalogs verifies
  all pages/counts/name ties/states/active flags/public streams and unchanged raw
  rows. Passed3.039s; small pinned fixture78/80 retained, stopped before build.
- TypeScript/Vite passed105 modules/4.09s. Same snapshot reused;86 source/config
  hashes match. CSS identical to verified original asset; no installs/dependency
  copies or concurrent heavy phases.
- Five catalog browser checks pass: all205 IDs per catalog reachable, unchanged
  edit fields/inactive flags, saved values on page2, refresh and deleting only
  five disposable unlinked tail samples automatically returns to last page.
  Public catalogs and all saved prices compare unchanged;375px layout fits.
  Initial fixture selectors assumed exact textarea label text and a Market-card
  description display that the original app never had; corrected tests to use
  original textarea names and verify Market description in its existing editor.
  No application layout/fields were added to satisfy these assumptions.
- Original catalog checks pass: four continuous sanitized audits, restored fields,
  referenced-delete and duplicate conflicts, unchanged historical price values.
  Seven original baseline workflows, original account/grant/revocation/six-audit
  workflow and all14 dashboard totals/one-query/outage recovery pass. All browser
  external/production contacts zero. Evidence: tools/local-test/evidence/batch-68-*.json.
- Disposable catalog sample control: http://127.0.0.1:55446/__test__/catalog-paging.
  Additional example entries are inactive, uniquely marked synthetic and created
  only in the memory fixture. No real extra market, commodity, unit or grade.
  Original preview reseeded after mutations. Reseed before unrelated testing;
  optional sample buttons give browser proof without changing app design.
- Source-only API reference now110 operations.4/16 Admin lists paged; remaining12:
  Prices, Flagged, Market signals, Quality, Buying zones, Sell-watch, Storage,
  Costs, FAQ, Subscriptions, Feedback, Audit. Full public history/chart paging
  remains separate; never claim PY-20 complete or truncate charts.
- PY-13 Nigeria price-time proposal is recorded in docs/NIGERIAN_PRICE_TIME_APPROVAL.md
  and submitted for owner approval. No time-rule/input-label changes implemented
  in68; preserve current stored timestamps/access/billing rules pending reply.
- Count unchanged29 complete /7 partial or pending:02,05,07,13,14,20,35.
  Next authorized technical work: remaining Admin paging in small batches.
  Native budget has two schemas left; preserve existing fixture/evidence and
  prepare a separately pinned small fixture when needed, without destructive
  cleanup or repeated full native suites. No production/push/merge/deployment.


### Batch 69 - approved PY-13 Nigerian price time (2026-10-18)

Owner delegated the explicit Nigeria WAT choice: "do the best for app that is
 going to be mostly user friendly". Applied only the recommended local price-time
scope in docs/NIGERIAN_PRICE_TIME_APPROVAL.md. No billing/access-policy change.

- Price-entry and correction fields now mean WAT on every device; Reporter default
  is current WAT. Existing labels/fields/grid arrangement stay, with a separate
  Nigeria time (WAT) caption. New submissions still send explicit UTC instants.
- Original price cards, history, detail, watchlist and chart labels use WAT for
  explicit instants; elapsed age wording remains. Unzoned legacy values stay
  literal; no guessed ages/chart coordinates or rewritten history.
- Shared Nigerian-day bounds feed current/history/comparison and CSV date filters:
  inclusive 23:00 UTC the prior day, exclusive 23:00 UTC the selected day. Original
  ranking, specifications, history permissions, CSV columns/raw instants remain.
- The synthetic SQLite preview alone adapts known UTC price timestamps to native
  TIMESTAMPTZ-shaped responses. It rejects unzoned synthetic writes; no application
  serializer, real database type, schema, migration or production data changed.

Verification (one heavy phase at a time; native fixture stopped before build):
- Full263 backend tests passed in87.180s; focused native boundary/history/export
  case passed in2.960s. Raw price rows unchanged, private sources excluded and
  current/history access retained. Native fixture78->79 of80 schemas, stopped.
- Corrected two new test assumptions: a free fixture needed its existing free
  subscription; the framework accepts midnight datetime strings as dates, so the
  invalid-input case now uses an actually invalid date. Final suite has no
  failures/errors/skips. No product behavior changed to satisfy these assertions.
- Original Admin create/correct and Reporter default/submit/reload verified in
  Lagos and UTC; 00:30 WAT sends23:30 UTC on the preceding day in both contexts.
- Original cards/history show1 January2001 at00:30 WAT for31 December2000 at
  23:30 UTC on both devices, desktop and375px; raw legacy ambiguity not guessed.
  The display case changes response timestamps only; stored originals unchanged.
- Original moderation/audits, separate comparable charts, all seven baseline
  workflows and all14 dashboard labels/totals/outage recovery passed. No external
  or production contacts. Build TypeScript/Vite106 modules4.09s;87 whitelisted
  source/public/config hashes match snapshot, original CSS byte-identical.
- Restricted CIM process inspection was denied; stopped that attempt and used
  the same identity-checking preview helper through approved escalation. No
  weakened checks or unrelated process termination. Dependencies not installed.

Evidence: tools/local-test/evidence/batch-69-*.json; reusable time browser cases
and native case are tracked. Current count:30 complete,6 partial/pending:
02,05,07,14,20,35. Continue approved PY-20 lists in small batches; preserve original
public-history/chart completeness. Source/referral/session/movement policy gates
and all live operations remain explicit. One native schema slot remains; preserve
this fixture and its evidence when preparing any separately pinned replacement.
No production access, push, merge or deployment.


### Batch 70 - approved PY-20 FAQ/audit paging (2026-10-18)

Continued from verified local96a855d (Nigerian time69), without reopening it.
- Added /faq/admin/page and /audit-logs/page:100-record pages/full snapshot counts,
  one SQL statement, unchanged schemas/permissions. Empty/out-of-range pages keep
  complete totals. FAQ visual order is published first, hidden second, then the
  original category/ID order within each group; audit order stays newest/ID first.
- Old /faq/admin and /audit-logs return complete arrays via bounded owned-session
  streams. Public /faq remains complete/published-only and eligible for public
  caching; legacy full FAQ category/ID ordering stays unchanged.
- Existing FAQ forms/actions and audit columns retained with shared Previous/Next
  controls. Saves reload the current page, without injecting off-page records or
  exceeding100 displayed rows. Known-ID editing/publish/hide/delete works beyond
  the current page; removing the final tail moves back safely. No hidden draft
  publication, source disclosure or historical audit rewrite.
- Added fixed205-record /__test__/faq-audit-paging fixture control to the guarded
  in-memory preview only. Extra FAQs stay hidden; fake private markers exercise
  existing audit redaction. No customer/market/price data is copied or invented.

Verification:
- All265 backend tests passed,28.877s, no failures/errors/skips. Full pages/groups,
  stable ties, old complete arrays, public drafts boundary, invalid offsets and
  raw saved FAQ/audit evidence preservation verified.
- One native PostgreSQL case passed0.809s; fixture79->80/80 schemas and stopped.
  This cap is now reached. Do not run further cases in it, raise its cap or delete
  preserved schemas; prepare a new separately pinned small fixture for next work.
- Original FAQ create/edit/publish/hide/reload/delete and five continuous audits
  passed.205-row browser sample verified every FAQ/audit ID reachable, old arrays
  complete, redaction, off-page known-ID edit/publication, safe last-page deletion,
  public FAQ and saved prices unchanged,375px layouts. No external/prod contacts.
- Original seven browser baseline workflows and all14 dashboard cards/totals plus
  outage recovery passed. TypeScript/Vite106 modules1.18s;87 source/public/config
  hashes match reused build, original CSS byte-identical; no dependency copies or
  installations. Source-only API index now112 declared operations.

Evidence: tools/local-test/evidence/batch-70-*.json. Count remains30 complete and
6 partial/pending (02,05,07,14,20,35); PY-20 now6/16 approved Admin lists paged,
10 lists and complete public-history materialization remain. Next small lists
must preserve existing subscription expiry/filter/source/ID-action semantics,
using a new pinned native fixture before tests. No production, push, merge or
 deployment; source/referral/session/movement and live-operation gates remain.


### Batch 71 - approved PY-20 Market/Quality signal paging (2026-10-18)

Resumed clean0b13cec, preserving all earlier work. Added100-record Admin pages
for Market/Quality signals, full snapshot counts and original newest/ID ordering.
Existing full/scoped arrays stream complete results; Market remains signed-in
access and Quality remains full access. New pages are Admin-only. No source
policy, fields, measurements, prices or history changes.

Existing ID edit forms now use their existing detail endpoint if a record is
outside the current page. Saved fields populate before submit; changing IDs
aborts/ignores the old request. Mismatched response IDs cannot fill another
record. Reloads retain the current page; deleting the disposable last tail moves
back safely. Existing optional clearing/defaults and all six forms are preserved.

Verification:
- Full268 backend tests passed29.346s, no failures/errors/skips. Includes current
  permissions, full/scoped legacy arrays, tied ordering, one-query page/count,
  invalid/empty offsets, saved observations unchanged and new build-port guard.
- Exhausted recovery80/80 fixture retained stopped/intact. Initialized exactly
  one fresh empty synthetic fixture under runtime/postgres-paging-20261018,
  no inherited PG/service configuration; literal127.0.0.1:55449 and hard-coded
  identifier7697910732590408300. Same role/DB,12 connections/32MB shared buffers,
  16MB maintenance memory, one autovacuum worker and fsync enabled. Guard verifies
  live directory/system ID before mutation, rejects other hosts/production port,
  retains exclusive run lock and80-schema cap. One relevant native case passed
  0.852s,0->1 schemas; stopped before build. No old fixtures/data were deleted.
- TypeScript caught callback narrowing in the new optional lookup; corrected
  typed captures, then TypeScript/Vite passed106 modules1.04s. Snapshot source
  hashes match87 whitelisted files; original CSS byte-identical. No installs or
  repeated dependency copies.
- All six original edit forms passed73 checks, no failures: prefill, single-field
  edits, saved-value retention, explicit clearing, invalid/changed/unknown IDs,
  creation and original costs. These were relevant because the helper is shared.
- Ten focused205-record signal paging checks passed: all IDs reachable; off-page
  edits retain other fields/page; delayed/wrong-ID responses cannot replace a
  newer selection; final-tail deletion returns to an existing page;375px layouts
  and raw price history preserved. Corrected the test selector to match original
  Quality label 'Signal #ID'; no product wording/design changed for the test.
- Seven baseline browser workflows and all14 dashboard labels/totals/outage
  recovery passed, zero external/production contacts. Source-only API index114.

Evidence: tools/local-test/evidence/batch-71-*.json.30 complete/6 partial-pending:
02,05,07,14,20,35; approved Admin paging8/16. Next: remaining four intelligence
lists, then Feedback/Subscriptions/Prices/flags, preserving existing expiry,
filters, source rules and complete public history. Use --paging-cluster for the
new native fixture; never restart exhausted fixtures or raise their budgets.
PY-02 publication hint proposal recorded in docs/SOURCE_PUBLICATION_APPROVAL.md;
owner question pending, no hint/policy implementation without its answer.
No production, push, merge or deployment.


### Batch 72 - approved PY-02 source publication (2026-10-18)

Preserved497e228 and the interrupted working tree. Owner explicitly answered
"Approve the source safeguard". Both original Admin Notes textareas now have an
accessible hint explaining public visibility and the existing private source
fields. No new fields, source categories, paid-access rules or historical edits.

Verification:
- Focused six-role backend policy case passed0.365s, covering current/history,
  CSV, audit list/page/detail and share paths. Existing public notes/guidance stay;
  private fabricated markers remain absent and Admin source management remains.
- Relevant native case passed1.480s on the pinned small127.0.0.1:55449 fixture;
  schemas1->2/80, stopped before the build. Raw price/audit evidence unchanged.
- Interrupted TypeScript/Vite build passed106 modules4.00s.87 whitelisted source,
  public and config hashes match the reused build; original CSS byte-identical.
  No dependencies installed/copied or overlapping heavy phases.
- Normal approval retry succeeded. Previous command was not executed because
  automatic approval review hit a usage limit, not a finding that it was unsafe.
  No guard/restriction was bypassed. Identity-checked synthetic preview restarted.
- Browser confirms both hints/descriptions, original Notes labels, private-source
  prefill, mobile375px layout, unchanged records and public CSV/share privacy.
  Existing legacy-audit privacy and original create/approve/correct/outdated/
  reject/reload workflows pass. Seven baseline views and all14 Admin labels/
  totals/outage recovery pass. Zero external/production contacts.

Evidence: tools/local-test/evidence/batch-72-*.json. Exactly31 complete and5
partial/pending:05,07,14,20,35. PY-02 complete for this finite approved scope;
free-text editorial discipline is still necessary, and no production historical
text review is authorized. Next approved small batch: Buying zones/Sell-watch
Admin paging under PY-20 (8/16 lists paged). Referral/session/movement decisions
and live operations retain their gates. No production, push, merge or deployment.


### Batch 73 - approved PY-20 Buying zones/Sell-watch paging (2026-10-18)

Started from verified1c41f93. Two existing Admin lists now use approved100-record
pages/full snapshot totals, existing buttons and original forms/cards. Their old
full/scoped APIs stream complete arrays in100-row batches, retaining original
premium access, disclaimers, newest/ID ordering and saved values. Existing ID
endpoints load off-page records; no delete feature added to either resource.

Verification:
- Two focused backend cases passed0.773s; full271 backend tests passed31.240s,
  zero failures/errors/skips. One-query page/count,205 tied rows/all pages/empty
  tail, complete scoped streams, original roles and unchanged stored rows pass.
- Native run caught an overlong fabricated referral code; shortened only that
  fixture to the existing12-character limit. Failed evidence retained; no app
  rule/schema change. Re-run passed0.934s on pinned55449. Schemas2->3 failed
  fixture,3->4 successful; stopped before build. README now clearly forbids
  restarting either exhausted fixture and names the current --paging-cluster.
- TypeScript/Vite passed106 modules1.92s.87 current source/public/config hashes
  match reused snapshot; original CSS byte-identical; no dependency installation
  or copying. API source reference now116 operations.
- Ten focused browser checks pass across205 entries per list: all IDs/totals,
  reload/Previous/Next/browser Back, off-page saved-value editing, dates/amounts/
  confidence/disclaimers retained, late lookup isolation, unknown-ID submit block
  and375px layout. Raw prices unchanged; no new delete controls.
- All six original editing workflows pass73 checks, including optional clearing,
  create/edit/reload/invalid values and original cost totals. Fresh tiny fixture
  baseline passes seven workflows and all14 dashboard totals/outage recovery.
  Single browser at a time; no external requests/production contacts.

Evidence: tools/local-test/evidence/batch-73-*.json.31 complete /5 partial-pending:
05,07,14,20,35. Approved Admin paging10/16; next small batch Storage/Cost lists,
then Feedback/Subscriptions/Prices/flags. Public history remains complete/separate.
No production, historical rewrite, policy/measurement change, push/merge/deploy.


### Batch 74 - approved PY-20 Storage/Cost paging (2026-10-18)

Continued c22f819 without reopening completed checklist items. Storage suitability
and Cost breakdown now use approved100-record Admin pages/full snapshot counts.
Original complete/scoped premium arrays stream100-row batches, original
newest/ID ordering/access/disclaimers remain. Existing ID endpoints retain saved
off-page values; original optional clearing and cost-delete capability remain.
No unit, measurement, formula, form, pricing or historical-record changes.

Verification:
- New relevant backend contract case passed0.718s. Native same case passed1.814s
  on pinned small55449; schemas4->5/80, stopped before build. Both205-row lists,
  ties/pages/full counts/empty tails, single-statement snapshots, scoped complete
  results, actual permissions, decimal costs/zero values and saved price links
  pass; raw costs/storage/prices unchanged. Full271 baseline passed batch73;
  this is a focused additional case, not a claim of another full suite.
- TypeScript/Vite passed106 modules0.993s.87 source/public/config hashes match
  reused snapshot; original CSS byte-identical; no installations/dependency copies.
  Source-only API index now118 operations.
- Eleven205-row browser checks pass: all IDs/totals, reload/Previous/Next/Back,
  off-page edits retain links/other values and recalculate original cost totals,
  delayed/unknown-ID safety, original cost tail deletion/page recovery and375px
  layout. Storage still has no delete control; raw price history unchanged.
- All six original form workflows pass73 checks. Existing calculator browser
  test found a test-only assumption that POST decimal text ("120") equals a
  persisted NUMERIC response ("120.00"). Test now verifies every amount and
  compares the persisted record exactly before/after calculator use; passed.
  Product serialization/calculations untouched; original honest unit label stays.
- Fresh tiny-preview seven baseline workflows and all14 dashboard labels/full
  totals/outage recovery pass. Sequential heavy phases, one browser at a time;
  zero external requests/production contacts.

Evidence: tools/local-test/evidence/batch-74-*.json.31 complete /5 partial-pending:
05,07,14,20,35. Admin paging12/16; remaining Feedback/Subscriptions/Prices/flags.
Subscription listing must still process every expired account, with staff and
purchased-time preservation; do not page away those side effects. Full public
history/chart materialization stays separate and must not be truncated.
Referral/session/movement decisions and live operations retain their gates.
No production, push, merge or deployment.


### Batch 75 - approved PY-20 filtered Feedback paging (2026-10-18)

Continued verified ecf133a. Original Feedback view now uses100-record Admin pages
and the existing rating filter; filter changes start at page1, and reload/back
retain rating/page. Shared snapshot helper accepts explicit SQL conditions for
both count and rows. Default callers keep identical unfiltered behavior. Old
full/rating-filtered Feedback arrays stream complete100-row batches.

The original summary remains global count/average, independent of page/rating.
Summary requests abort/ignore obsolete responses after navigation/account change;
record actions reload the current page and global summary. Existing private
screenshots, testimonial display-name field, publish/hide/delete controls and
public testimonial allowlist remain. No new fields, policies or product design.

Verification:
- New focused contract case passed0.238s. Full273 backend tests passed32.414s,
  no failures/errors/skips; broad run justified by the shared filtered-page helper.
 205 tied records,1/204/empty rating scopes, full/global counts/averages, complete
  legacy streams, private attachments/Admin rights and public allowlists pass.
- Focused native case passed1.030s; pinned55449 schemas5->6/80, stopped before
  build. Original feedback rows unchanged; no production/schema migration.
- TypeScript/Vite passed106 modules0.982s.87 whitelisted source/public/config
  hashes match reused snapshot; original CSS byte-identical. Zero installations
  or dependency copies. Source-only API index now119 declared operations.
- Six205-record browser checks pass: all IDs/full totals/private screenshots;
  Previous/reload/browser Back; rating reset/retention/empty results and unchanged
  global summary; original testimonial feature/hide with private evidence intact;
 375px layout; filtered-tail deletion moves back while retaining rating and
  refreshing global/filtered totals. Corrected only the test selector for the
  original wrapped rating select; no product label/accessibility rule changed.
- Existing customer feedback attachment/last-file-wins/submit checks pass.
  Fresh tiny-preview seven baseline workflows and all14 dashboard labels/full
  totals/outage recovery pass. Raw prices unchanged; one heavy phase/browser
  at a time, zero external requests/production contacts.

Evidence: tools/local-test/evidence/batch-75-*.json. Exactly31 complete /5 partial
or pending:05,07,14,20,35. Approved Admin paging13/16; next Subscriptions, Prices
and flags. Subscription paging must preserve the original all-account expiry
sweep, original User->Subscription writer lock order, staff authority and all
purchased/trial value; never process just the visible page. Full public history
materialization is still separate, with no approval to truncate chart/history.
Referral/session/movement owner decisions remain unchanged; live operational
PY-35 work remains forbidden. No production, push, merge or deployment.


### Batch 76 - approved PY-20 Subscription paging/whole-list expiry (2026-10-18)

Resumed clean2d9cf35. Original Subscriptions view now uses100-record Admin pages
and full snapshot counts, same ascending ID ordering, status controls, columns,
reminder control and existing styles. Complete legacy arrays stream100-row
batches. No price, trial duration, manual-grant or purchase rule changes.

Preserved the original listing's whole-account expiry side effect: select at
most100 due account IDs at a time up to the initial highest user ID, then recheck
under the existing User->Subscription locks. Flush bounded entities and commit
all expiries atomically before generating a response; roll back everything on
failure. A concurrent renewal that makes a selected candidate valid is retained.
Original UTC paid whole-day boundary, trial instants, manual grants, stored dates,
payment references and staff authority remain. No scheduler or migration added.

Verification:
- Three focused cases passed0.400s; full276 backend tests passed31.293s, zero
  failures/errors/skips.205 accounts across expired trials/paid dates, valid
  dates, final paid day and indefinite grants; all account expiry, bounded
  hydration, complete pages/legacy results, Admin-only access and failed-sweep
  rollback pass. Fresh-session ORM hydration stayed below10 entities.
- Two focused native cases passed1.535s on pinned small55449; schemas6->8/80,
  stopped before build. Forced real confirmed renewal after candidate selection
  remains active with all purchased30 days, payment reference/success and one
  atomic payment audit. Expiry does not overwrite the fresh locked state.
- TypeScript/Vite passed106 modules1.00s.87 whitelisted hashes match reused
  snapshot; original CSS byte-identical; no dependencies installed/copied.
  Source-only API index now120 operations.
- Four205-row browser checks pass: all IDs/full totals/page boundaries; reload/
  Previous/browser Back; original status action retains page and14-day trial,
  other records unchanged; original columns/reminder control and375px layout.
  Raw prices unchanged. Fresh tiny baseline seven workflows and all14 dashboard
  labels/full totals/outage recovery pass. Sequential heavy phases and no
  external requests/production contacts.

Evidence: tools/local-test/evidence/batch-76-*.json.31 complete /5 partial-pending:
05,07,14,20,35. Approved Admin paging14/16; next Prices/Flagged prices. Preserve
latest-pair prefill across all price pages and full flag counts when finishing.
Public history must remain complete; owner referral/session/movement decisions
and production readiness retain their gates. No production, push/merge/deploy.


### Batch 77 - approved PY-20 Prices/Flagged prices paging (2026-10-18)

Continued586b621. Final two Admin lists use100-record pages/full snapshot totals.
Price pages join existing commodity/market relationships within the single count/
page statement; complete legacy Admin arrays stream100-row batches. Every price
status remains reachable. Flag pages count all unresolved reports per price before
paging grouped prices, keeping newest flag/ID ordering and original review action.
Full flag arrays stream; no flags, prices, catalog records or audit evidence removed.

Original price prefill now queries the latest matching commodity/market globally,
including pending/rejected records as before, sorted by date/ID. It retains private
Admin source fields/unknown measurements. Delayed prefill cannot overwrite form
values changed since its request or a different account/form. Creating a pending
record reloads the current page rather than adding an unbounded optimistic row;
existing Record ID actions/corrections still work beyond the displayed page.

Verification:
- Focused backend case passed0.435s. Full277 backend tests passed31.796s with no
  failures/errors/skips.205 prices/grouped flags, all statuses/ties/pages/empty
  tails, one-query snapshot/related loads, full streams, exact aggregate counts,
  original permissions/private sources/global latest-pair lookup and raw records
  pass. No invented grades, weights, markets or additional product fields.
- Focused native case passed1.742s; pinned55449 schemas8->9/80, stopped before
  build. TypeScript/Vite passed106 modules1.16s.87 whitelisted hashes match reused
  snapshot; CSS byte-identical; no installs/copies. API source reference123 ops.
- Seven205-row browser checks pass: complete prices/statuses/flag groups; original
  correction retains page/status/sources/measurements; off-page latest-pair prefill;
  delayed response preserves newer form input; flag review empties last page and
  moves back without altering prices; original mobile layout/no grades. Test-only
  expectation corrected to original flag review204 response; rerun on fresh fixture.
- Original source/Notes checks and create/approve/correct/outdated/reject/reload
  price workflows pass. Their request assertions now follow the paged reload and
  await the existing prefill's async result. Seven baseline views and all14 dashboard
  labels/full totals/outage recovery pass; zero external/production contacts.

Evidence: tools/local-test/evidence/batch-77-*.json.31 complete /5 partial-pending:
05,07,14,20,35. Admin paging16/16 complete. PY-20 public-history materialization
remains explicitly separate. Owner's "do the best option" reply approves the
recommended local three-bonus/rolling30-day PY-05 scope; documented exact decision
in docs/REFERRAL_ABUSE_DECISION.md, not yet implemented. Next batch implements and
tests it without reducing historical bonuses, purchased days or signup access.
Other policy/production gates remain. No production, push, merge or deployment.


### Batch 78 - approved PY-05 rolling referral cap (2026-10-18)

Continued6f0b14c. Owner answered "do the best option" to the explicit recommended
three-bonus rolling30-day proposal; approval recorded before implementation in
docs/REFERRAL_ABUSE_DECISION.md. Existing seven-day reward and registration/free-
or-live-trial eligibility remain. Under the parent-account lock, count only known
successful reward audits within30 elapsed UTC days (strictly after the lower
boundary, through now); grant at most3. Current registration/reward/audit stays
atomic. Beyond the cap, new people still register/get14-day trials and referral
counts increase. No old award/days/purchased time removed or legacy history guessed.
Existing dashboard/share explanation states cap and eligibility; forms/layout,
summary fields, all14 Admin cards, prices and subscription plan rules stay.

Verification:
- Four focused cases passed1.838s after correcting test UTC normalization. Full281
  backend tests passed37.270s, zero failures/errors/skips, before that test-only
  correction. Exact30-day boundary/microsecond, actor/action/table scope, existing
  free/trial/paid/expired/cancelled value/staff roles and failed-third-award rollback
  pass. Five signups produce only3 bonuses with all child trials/referrals intact.
- First native flow assertion incorrectly stripped WAT/UTC offsets, comparing the
  same instant as different wall times. Preserved failed evidence and corrected
  only the test to compare UTC instants. Concurrent last-slot test already passed.
  Re-run both cases passed2.845s: two simultaneous children both register/get14-day
  trials; only one consumes the final available slot, preserving all prior days.
  Pinned55449 schemas9->11 retained correction run,11->13 successful; stopped before
  build. No application timestamp conversion, historical rewrite or migration.
- TypeScript/Vite passed106 modules1.11s.87 source/public/config hashes match reused
  snapshot; original CSS byte-identical; no dependencies installed/copied.
- Original referral-link UI signup plus four total browser referrals pass: first
  three add21 days; fourth succeeds, counts as a referral and retains14-day trial
  without another bonus. Dashboard/share text state limit; mobile375px preserved.
  No message sent. Seven baseline views and all14 dashboard full totals/outage
  recovery pass. Heavy phases/browser runs sequential, no external/production access.

Evidence: tools/local-test/evidence/batch-78-*.json. Exactly32 complete /4 partial-
pending:07,14,20,35. Approved Admin pagination16/16 complete. PY-07 storage/session
and PY-14 movement/confidence policy choices need concrete owner approvals before
behavior changes. PY-20 full public-history/query materialization remains, with
no chart/history truncation approval. PY-35 production/provider/restore/rollout,
application/database clock alignment and legacy reward evidence review remain
unauthorized. Local cap does not prove unique human identities/eliminate all fraud.
No production, push, merge or deployment. Resume these unfinished scopes only.


### Batch 79 - approved PY-14 claim evidence (2026-10-18)

Owner explicitly approved both docs/PRICE_CLAIM_EVIDENCE_APPROVAL.md and
docs/SESSION_COOKIE_APPROVAL.md. This batch implements only14;07 remains open.
New/changed Verified by2 sources requires distinct nonblank existing private
references. New movement/approval checks latest strictly preceding approved,
nonoutdated price with same catalog IDs and complete normalized recorded
quantity/bag size/type. Both range endpoints must rise/fall/equal; supplied
previous ranges must match that evidence. Otherwise existing unknown is required,
with422 before mutation/audit. No guessed units, grades, source identity claims,
fields, forms, historical rewriting or automatic relabeling. Unrelated historical
notes corrections and idempotent approval remain possible. Evidence is checked
at write time; later editorial corrections do not silently rewrite old claims.

Verification:282 backend tests passed35.365s (zero failures/errors/skips); focused
claim case and24 existing price cases pass. Native pinned55449 case passed1.864s;
schemas13->14/80, stopped. Accepted up/down/stable/unknown, mixed endpoints,
time/measurement mismatch, missing/duplicate references and failed approval/
correction preservation covered. Guarded original-form browser checks reject
unsupported claims, save/approve explicit unknown and hide private evidence.
Original source/Notes, price create/approve/correct/outdated/reject/reload, seven
baseline workflows and all14 dashboard cards pass; mobile375px unchanged, zero
external/production contacts. Frontend unchanged:87 hashes and compiled assets
match last validated78 build (reused, not a fresh build). Heavy tests sequential.

Evidence:tools/local-test/evidence/batch-79-*.json. Exactly33 complete /3 partial-
pending:07,20,35. Next protected browser sessions, remaining full-history query
bounds and local operational readiness evidence; live/provider/restore gates
remain unauthorized. No production, push, merge or deployment.


### Batch 80 - approved PY-07 protected browser sessions (2026-10-18)

Continuede60cdc7. Explicit owner approval:docs/SESSION_COOKIE_APPROVAL.md. New
browser-only login/Google/bootstrap/upgrade endpoints return noncredential
CSRF/session metadata, never JWT. Host-only HttpOnly/Secure/SameSite=Lax cookies
keep original90-day token maximum and RememberMe; unremembered is a browser-
session cookie. Only literal127.0.0.1:55446 under APP_ENV=test permits HTTP.
Existing bearer API routes/clients stay. Valid legacy JS tokens convert only after
server validation, retaining the identical signed expiry, then are removed.

Cookie writes require exact configured Origin and token-bound CSRF. Session IDs
reject old-account requests after a cookie switch. Private/auth responses are
no-store, including mounted API errors. Old/new login endpoints share5/min quota.
Logout revokes server token and expires cookie; reset/version revocation still
applies. Device view clears immediately offline, with a nonsecret pending marker
that prevents automatic return and retries after reconnection. Existing bounded
current-device push cleanup/other devices remain. Cross-tab Web Locks serialize
cookie-changing requests so delayed logout responses cannot erase a new login.
Unsupported browsers fail before sign-in with the existing error display rather
than using an unsafe tab-only lock. Verify the target phone/browser matrix and
HTTPS/same-site hosting under35 before release. Browser restore settings can retain
session cookies; shared-device users should explicitly log out. No new DB fields.

Browser races found/fixed:old bootstrap401 could acknowledge a newer logout
marker; an older logout broadcast could cancel an explicit queued new sign-in.
Deterministic regressions cover both. Test navigation now waits for the original
logout-home transition and clicks the existing Log in link, preserving one document.
The offline harness explicitly aborts API requests because routing can override
Playwright offline emulation. Node APIRequest transport stayed forbidden; the
negative replay uses the already-approved guarded page transport. New Google route
was connected to the existing synthetic verifier after the guard blocked its first
certificate lookup before DNS/network; no provider contacted/guard weakened.
Original CSV download had a separate bearer fetch; now uses shared authenticated
blob transport, preserving form/filename/content and Admin-only access.

Verification:283 full backend tests pass35.342s (zero failures/errors/skips),
versus124.786s verbose run. Reused stdout/stderr logs avoid console backpressure;
no overlapping heavy test suites. Focused final native case2.172s covers cookie
CSRF, reset/logout/replacement hashes, exact legacy expiry, shared quota, mounted
no-store and production Secure behavior; fixture14->15 first run,15->16 final,
stopped. Full suite preceded tiny mounted-cache fix; that fix and its added test
pass in the final native case. TypeScript/Vite107 modules1.32s;88 source hashes
match, original CSS byte-identical, no installs/dependency copies. Ten cookie
browser scenarios pass, including delayed200/401, cross-tab queued sign-in,
unsupported-lock refusal and offline retry. Original payment failure/recovery/
replay, fabricated Google/password fallback/new14-day trial, reset/single-use,
three push-cleanup cases, source privacy, price editing, CSV, seven baseline
views and all14 full-total dashboard cards pass. External/production contacts0.
Evidence:tools/local-test/evidence/batch-80-*.json. Exactly34 complete /2 partial-
pending:20,35. Live cookie/provider/device/cutover/backup/rollout gates remain.
No production, push, merge or deployment.

### Batch 81 - PY-20 complete history streaming (2026-10-18)

Continued08c9e38. Complete JSON history uses one ordered query, scalar catalog
joins and100-row ORM fetch batches. Existing active/approved/outdated rules,
catalog IDs/text/WAT-date/movement/time filters, chronological time/ID order,
entitlement and public response schema remain. Owned cursor/session closes on
completion, query failure, disconnect and cancellation. No history/chart cap,
public pagination, design change, new measurement or record rewrite.

Previously verified:6 existing access tests and3 new history cases; full286
backend tests35.733s with0 failures/errors/skips. Full251-row preservation,
one SQL query, first batch<=100, peak hydrated prices<=200 during batch turnover,
privacy, WAT filtering, missing measurements and failure cleanup pass. Native
first run rejected a test-only13-character referral code against VARCHAR12;
corrected only the fixture code, retained failed evidence/schema16->17. Focused
rerun passes1.191s,17->18/80 schemas, cluster stopped. No schema changes.

Browser:251 desktop rows/mobile cards, full ordered response, original market/
time filters, no-store/source privacy and unchanged current prices pass. Fixed
249-record add-on uses original Egusi/Kwali/1bag/null size/type, older timestamps.
Fresh original seven-workflow baseline, all14 dashboard totals/outage recovery
and CSV pass; external/production contacts0. No frontend change or redundant
build; last validated80 snapshot remains. Browser still renders the complete
selected result and scales with its size; this is not unlimited-load evidence.

The next commit attempt was not executed because automatic approval review hit
the usage limit; no unsafe-action determination. On resume, inspected actual diff,
clean whitespace and saved reports without repeating passed tests. Source/tests/
evidence committed558f756eea2eb7db727708b9a72f81e5f40fd5a7, then confirmed clean
Git status and unchanged master76dbd275/backup25899101 before advancing35/36.
Evidence:tools/local-test/evidence/batch-81-*.json. PY-35 remains the only partial
item. No production, push, merge or deployment.

### Batch 82 - PY-35 approved dependency security updates (2026-10-18)

Continued3e523ad after confirming PY-20 commit558f756. Targeted maintainer
advisories include declared Vite5.4.11/router6.28.0; package presence is not proof
of exploitation. Vite dev-server exposure differs from the compiled Python
preview; router advisories have mode/untrusted-navigation conditions. Exact
links and limits:docs/DEPENDENCY_READINESS.md. Owner answered "do best option"
to the explicit isolated Vite6.4.4/router6.30.6 install exception. Approval
recorded before fetching. Only official npm registry, integrity-bearing lockfile,
no inherited user/npm credentials, no lifecycle scripts, no production services.

New fixed runtime/frontend-security-20261018 retains old snapshot/dependencies.
Lock123 entries;73 applicable packages installed. React18.3.1/plugin4.3.4/TS5.6.3
unchanged; plugin peer range supports Vite6. Source declarations plus reviewed
package-lock updated only after guarded TypeScript/Vite build104 modules4.65s.
No application TSX/CSS/public source change. Compiler CSS bytes differ; computed
layout/font/padding/colors/borders match the old build at1366/375px. Existing
commodity-ID deep link, ten protected-session cases, seven original baseline
workflows, all14 accurate dashboard cards/outage recovery, payment failure/retry/
replay, CSV, original price editing, fabricated Google and full251-row history
pass. Five build-recovery tests0.098s pass after optional lockfile snapshot copy.
Backend application code unchanged; reused286-test/native81 evidence, not a new
full suite. All browser/provider tests isolated, external page/production contacts0.
Authorized registry downloads/public advisory reads are separate from app tests.

Evidence:tools/local-test/evidence/batch-82-*.json. Counts remain35/36;35 partial
for remaining operational work. Do not claim all dependencies/CVEs or Linux/live
hosting certified. Old root node_modules is retained; use marked55446 preview.
Next tiny synthetic backup/restore, monitoring and release gate/runbooks. No
production, push, merge or deployment.

### Batch 83 - PY-35 local recovery, monitoring and release gates (2026-10-18)

Continued449475e. All currently authorized local operational preparation verified;
35/36 complete, PY-35 partial for nine explicitly unrun live approval gates.
See docs/OPERATIONAL_READINESS.md and docs/RELEASE_GATES.json. No production or
provider access, deployment, migration, live monitor or scheduler enabled.

Tiny native fixture prepared0.738s,18->19/80 retained schemas,21 application
tables/14 fabricated business rows. Actual pg_dump/pg_restore into one new marked
empty database on the pinned55449 cluster preserved paid/trial/payment/private
source/audit/revocation evidence.124437-byte archive and originals stay ignored
and retained. No drop/clean/overwrite or repeat restoration. Source raw baseline
unchanged. Initial verification found seven equivalent CHECK array-cast text
rewrites; retained diagnosis and verified PostgreSQL's own planned expressions
and validation flags, with all other columns/indexes/sequences/row digests equal.
Separate first dump/restore times were not captured; this is not production RTO.
Cluster stopped before browser checks. Four negative recovery guard tests pass
0.005s with no native connections; three release-gate tests pass0.001s.

Browser monitoring drill passes:process /health200 cannot conceal price503,
original Current Prices error and existing Apply recovery work, Guest history
remains401/private fields absent, external requests0. Harness initially expected
a Retry control absent from the original app; corrected only the check to Apply.
No application design/source behavior change. Fresh original synthetic preview
remains http://127.0.0.1:55446, outage disabled.

Read-only release checker validates required evidence, complete36-item tracker,
89 current build/source hashes, approved lock and installed versions, exact local
Python inventory, unchanged master/backup references and explicit release refusal.
New backup/incident/monitoring/release procedures distinguish local evidence from
actual customer-backup restoration, hosted security/browser/load checks, provider
delivery/payment tests and approved rollout. No portable dependency/CVE-free or
production readiness certificate claimed. Reused unchanged286-backend/native81
and dependency/browser82 results; no unnecessary whole-suite rerun.

Evidence:tools/local-test/evidence/batch-83-*.json. Precommit release inventory
records parent449475e and expected dirty tree; final --require-clean result stays
ignored in runtime/local-release-check.json to avoid rewriting committed evidence.
Only verified source/docs/test evidence is committed; archives/dependency trees/
runtime stay untracked. PY-35 remains partial until separately approved live gates
pass. No push, merge or deployment.

### Batch 84 - PY-35 approved Phase 1 staging verification (2026-10-18)

Continuedc797db8. Owner authorized separate staging, provider TEST mode and
approved recipients only; no production. No staging URL/host, TEST credentials,
Google test identities or recipient list were supplied. Reply "do best option for
the app" supplies no credentials or production permission. Documented blockers;
no provider contact, external changes, purchases, messages or production fallback.
Full nine-gate statuses:docs/PY35_PHASE1_REPORT.md/PY35_PHASE1_RESULTS.json.

Separate ignored source/artifact package125 files/740043 bytes verified,300-file/
5MiB cap, no dotenv/config/secrets/customer data/dependency-tree copy. Not hosted
staging.15 focused existing tests actually import the copied staged backend with
fresh synthetic SQLite:session1,recovery7,reset2,notification5; zero failures/
errors/skips. Six isolation probes pass. One finite three-tick scheduler test
checks persisted/reloaded checkpoint/fixed ceiling and no duplicate credit; no OS
job enabled. Native recovery/single-worker/webhook cases2 pass1.435s,19->21/80
schemas retained, pinned cluster stopped. Existing batch83 actual synthetic
restore reverified read-only:21 tables/14 rows, archive/source/restored evidence
unchanged; no new restore/archive/customer-backup claim.

Browser14-card exact totals,375px layout, cookie/no-JS-bearer, reset/logout,
recovery/replay and independent mocked notifications pass; process200/price503
and original Apply recovery pass.24 serial read samples180ms total,concurrency1;
max/p95 health13.1ms/prices8.8ms/Admin10.4ms. Not hosted load/TLS/capacity evidence.
Offline60 Python packages/74 active requirements including requested extras have
no conflicts;123 resolved npm
entries source/integrity valid.89 source hashes match existing build; no new
installs, redundant build or fresh advisory/Linux certification. Local constraints
inventory is not a portable backend lock.

Retained three test-only setup/assertion failures:Python-I local import path;
obsolete Bearer-null header overriding approved cookies; UTC timestamp in WAT
notification form. Fixed invocation and only two browser harnesses, fresh fake
data reruns pass; no application edits. Confirmed staging-send issue:watchlist
email body hard-codes deployed-site link. Left product content unchanged; actual
test sends blocked until staging-safe handling/credentials/recipients reviewed.
Starlette/httpx test deprecation warning remains without installing replacements.

Phase1 statuses:2 Passed(synthetic backup/recovery and finite scheduler),5 Failed
because missing staging/provider prerequisites,2 Awaiting Production Approval.
Passed subchecks never close original live gates;35/36 complete,PY-35 partial.
All application backend/TSX/CSS files and approved policies unchanged. Evidence:
tools/local-test/evidence/batch-84-*.json. Fresh local HTTP preview55446 only;
runtime package/checkpoints/constraints remain ignored. Stop after reporting;
no production approval requested, push, merge, deployment or live job.

### Batch 85 - PY-35 safe notification origins and owner setup guide (2026-10-18)

Continuedd3f7aad. Owner explicitly approved replacing the hard-coded live email
URL, configuration validation/tests and concise staging instructions. Watchlist
email/push/WhatsApp share an explicit validated FRONTEND_URL origin plus/prices.
HTTPS outside test/development loopback; no missing/default fallback, userinfo,
query/fragment/path/control/encoded/private staging destination. Nonproduction
rejects the original known production hostname. Additional live aliases require
review before any provider test. No new settings fields/database fields/forms.
Bad configuration returns0 before watcher queries/provider sends; saved approval
is not undone. Correctly configured original production destination/content,
deduplication, targets and independent-channel behaviour preserved. Actual
production settings were not read; explicit FRONTEND_URL is a release prerequisite.

Passed:9 focused URL/delivery/configuration tests2.399s;5 existing notification
channel tests6.545s;4 price approval/audit tests1.037s. No failures/errors/skips.
Original watchlist/Admin approval, three independent mocked channel attempts,
latest price/reload and all14 correct Admin cards/outage recovery pass in browser;
external requests0, no actual emails/push/WhatsApp sent. No frontend source change
or redundant build/native suite. Restarted only verified disposable preview.

docs/STAGING_SETUP_GUIDE.md lists hostname/HTTPS host, synthetic PostgreSQL and
new staging secret, Paystack TEST keys, Google client/test identities, message
credentials/approved recipients and exact existing configuration names. Seven
plain-language steps; secure storage references only, no provider changes/purchases
performed or keys requested. No new global recipient restriction is falsely
claimed:restricted provider harness/sandbox still required before actual sends.

Report/JSON now distinguish2 Passed synthetic scopes,5 Blocked/not attempted
external checks,2 Awaiting Production Approval. Earlier84 "Failed—blocked" counts
remain historical; actual three test failures were resolved and retained. No
unresolved executed check is failing. Existing84 source package/evidence is
preserved at its historical revision and does not contain85; do not overwrite or
use its checker to claim the updated source was staged. Refresh only under a
reviewed next staging batch. Original live gates remain unrun;35/36 complete,
PY-35 partial. Evidence:tools/local-test/evidence/batch-85-*.json.

Only authorized watchlist URL handling changes in application code; original
design,14 cards,prices/measurements/history/trial/subscription/referral/access
rules preserved. No production credentials/data, provider contacts, real charges,
purchase, migration, push, merge or deploy. Stop after providing setup instructions.

### Batch 86 - PY-35 remaining identified offline checks (2026-10-18)

Continued8dd9d1c. Owner prefers existing local isolation, no new Render service or
Supabase project. Reused passed baseline/native/browser/value/recovery/backup/
dependency evidence instead of repeating it. New6 simulated email transport tests
pass0.341s:missing configuration, API rejection/error privacy, verified STARTTLS/
SMTPS context/order and failed TLS cannot send credentials/message. No provider
traffic or message. No application source changes or dependency installs.

Closed real local TLS gap:one generated synthetic loopback certificate/key,
memory handshakes3 pass(trusted matching IP, wrong name denied, untrusted denied),
actual TLS1.3 Chromium browser login/reload/logout with Secure __Host-/HttpOnly/
SameSite cookies, session-only RememberMe, CSRF403, private no-store, no JS bearer
and server-revoked token401 pass. Only this generated SPKI trusted in disposable
browser; no broad HTTPS ignore flag, OS trust-store edit or production key read.
Original isolation guard unchanged. Literal HTTPS127.0.0.1:55446/Host/Origin gate,
serial SQLite requests, external requests0. The original compiled UI/API reused;
transient fixture uses staging cookie mode. No production configuration touched.

TLS bootstrap creates/loads only its own new certificate files before app imports;
then original guard applies. New file tree bounded to one small ignored pair and
public identity; no copied dependencies/databases. Exact-script owned TLS worker
stopped and fresh ordinary HTTP preview restored. Native PostgreSQL stays stopped
at21/80; no schema/file growth from repeating native suites. TLS evidence is not
public CA/DNS/reverse-proxy/Android/Safari or actual-host compatibility proof.

docs/PY35_OFFLINE_READINESS.md maps every remaining live gate to its unavailable
evidence and explains minimum launch prerequisites. Existing provider TEST access/
consenting recipients, reachable isolated callback host, target-runtime install/
advisory review, actual-backup restoration/read-only revision review, monitoring/
scheduler ownership and separate release approval remain. No claim that all
possible offline tests or real-world operations are certified. Known identified
local gaps now covered;35/36 complete,PY-35 partial. Evidence86 retained; no failed
new check, heavy load, virtualization or repeated prior full suite. No production,
customer records, actual charges/messages, purchase, cloud creation, push, merge,
deployment or jobs enabled. Stop after reporting; no credentials requested.

### Batch 87 - final review and single-account expiry/renewal race (2026-10-18)

Resumed actual5bce117 on the existing branch, preserving interrupted modified
subscription_service.py and untracked test_subscription_expiry_race.py byte-for-byte
under ignored runtime/batch-87-interrupted-work. Initial SHA256 respectively:
F4CC326F9CE8352FBD45755E7BC915AEE11C54B99EE345BC87AE42C85A901675 and
A35434D68004E99BFB8880B6B5F4273AD217F2D241521FD44D1C7B628E8FDC85.
No branch reset, discarded work or backup/master changes. Existing uncommitted
service fix retained; strengthened its native regression evidence independently.

Confirmed old committed helper overwrote concurrent renewed access/ordinary paid
role after reading expired trial/paid state. Reproduced six expected failing
subcases by compiling only the old function in memory; source never reverted.
Fixed helper reloads under existing User->Subscription locks before mutation,
releases locks even after renewed candidate, rolls back failures. Valid/indefinite
reads avoid expiry writes/locks. Same approved pricing/trial/value/staff/history.

Fresh full backend307 pass117.546s, zero failures/errors/skips. Focused expiry6
pass0.249s. Five native PostgreSQL cases pass9.689s:two new cases cover twelve
actual webhook/GET interleavings across trial/paid and ordinary/Reporter/Admin;
pg_blocking_pids proves payment waits when expiry holds the lock. Listing expiry,
verification/webhook replay and distinct concurrent purchase durations also pass.
Actual payment.success audit/receipt once and preserved access/authority checked.
Pinned small cluster stopped normally,21->26/80 schemas,12 connections/32MB
buffers/fsync; preview stopped during heavy phases. No overlapping heavy suites.

Browser paid renewal/trial purchase/replay, indefinite grant held/resolved/credited
once, eight access scenarios and all14 exact Admin metrics/outage recovery pass.
Two older value/review harnesses updated from Bearer-null to approved cookie/CSRF
session. No frontend source/CSS change or redundant build. Read-only local release
checker now requires87 evidence;89 source/build files match, original Git refs
preserved and all nine live gates remain unrun/release refused. Evidence87 saved.

Retained launcher issues, not application failures:PowerShell stderr redirection
treated existing Starlette/httpx warning as terminating error before discovery;
Start-Process direct log redirection then completed the suite. Initial browser
launch lacked existing isolated browser path; explicit path fixed it without
installing/downloading anything. No auto-review rejection/bypass occurred this
batch. Full backend used bounded sequential execution; PostgreSQL test waits are
bounded, no high-load loop or broad new database tree.

Scoped current auth/session/reset/Google, payment/expiry and migration-safety
review completed against existing readiness requirements. Separate unseen other
conversation audit findings are not claimed reviewed. No new confirmed critical
issue beyond the verified fix; no promise of exhaustive vulnerability discovery.
docs/PY35_FINAL_REVIEW.md distinguishes proved local fixes from unverified actual
Render/Supabase/provider/backup compatibility and lists exact secure access needs.
GitHub connector available but repo permissions/publication unverified; no remote
fetch, service access, credentials/production data, migration, push, merge or deploy.
35/36 complete, PY-35 partial; mandatory external release checks have NOT passed.
Stop before deployment until approved evidence/backup/rollback prerequisites close.

### Batch 88 - confirmed hosting references and migration release block

Owner supplied Render backend priceyard-api/srv-da6d9gqjnfac73e2sbfg,
https://priceyard-api.onrender.com, master/backend, deployed labela9cf1b9;
Auto-Deploy On Commit; build invokes pip install and alembic upgrade head.
Frontend priceyard/srv-da6ddb2jnfac73e39490,
https://priceyard.onrender.com, master, deployed label76dbd27. Frontend
Auto-Deploy/root/build remain unconfirmed. Repository confirmed by owner:
fidelisnguakaaga20/priceyard. These are owner-reported, not independently fetched
production facts; labels do not establish installed database revision.

Updated final review/deployment plan with exact references, the risk that master
push/merge triggers migrations during build, and remaining requirements. No
production settings, connections, credentials, records or provider actions touched.
Next information-only step:Supabase project name/reference, plan, backup listing.
Read-only revision/schema/permissions review needs bounded target/operator approval;
actual encrypted backup handling/isolated restoration need separate approval.
Rehearse exact migration and compatible rollback against verified restoration
before any proposed live change. Never treat code rollback as database rollback.
Official Supabase backup guidance reviewed; database backup excludes Storage file
contents, plan availability unconfirmed, no upgrade/purchase assumed.

Documentation-only batch; diff/link/reference checks, no redundant application
tests or build. Previous307 backend/five native/browser evidence retained;35/36
complete, PY-35 partial and all nine live gates still unrun. No cloud project,
production access, migration, settings changes, push, merge or deployment.

### Batch 89 - manual backup preparation; stopped before production access

Owner confirmed project priceyard/lrvpjfbtmftjkzaxbunk, Free, no managed backups;
requested read-only compatibility review, encrypted manual backup and verified
isolated local restoration, with explicit stop before production access if access
or approval is needed. No authenticated production connection is available.
Prepared docs/sql/PY35_READ_ONLY_PREFLIGHT.sql:whole read-only transaction,
5s statement/1s lock timeouts, server/size/Alembic/catalog/extension/role metadata,
rollback, no customer row/password/default/function-body reads or writes. Not run.

docs/PY35_MANUAL_BACKUP.md records existing native PG18 tool preference over new
CLI/Docker, version/TLS/source checks, secure operator credential entry, encrypted
storage outside Git and independently retrievable copy, role/grant/snapshot
coverage, actual empty private restore target and bounded single-worker verification.
Real records must never enter the synthetic-only cluster/harness. Same-snapshot
digests/records/permissions/integrity, migration rehearsal and compatible rollback
acceptance required. Local migration rehearsal remains separately approval-gated.
Official Supabase/PostgreSQL guidance reviewed; file bytes, external service/key/
extension/role-password coverage and later payment writes explicitly excluded or
require separate recovery. Missing encryption/access/setup is not successful backup.

Documentation/SQL preparation only; no database connection, secret/.env read,
tool installation, dump, restore, migration, production change, push/merge/deploy.
No redundant regression tests.35/36 complete, PY-35 partial, live gates unrun.

### Batch 90 - reported production revision and exact migration delta (2026-10-19)

Owner reports approved read-only inspection completed:PostgreSQL17.6,database14 MB,
revision0021_feedback_screenshot, projectpriceyard/lrvpjfbtmftjkzaxbunk Free/no
managed backups. Preserve this evidence as owner-reported, not a Codex connection
or independently verified full schema review. Do not repeat completed first checks.

Static Python AST review of22 local migration files (no imports of app/Alembic,
database or application startup) confirms sole head0022_login_revocation directly
after0021. Git diff against preserved master shows only0022 added; earlier migration
files unchanged. Upgrade adds users.auth_version integer NOT NULL default0, new
revoked_access_tokens table/FK/PK/timestamps/two indexes. No business-record rewrite
or delete in upgrade. Drift/permissions/locks/extensions still need actual review;
0022 downgrade refuses and an old app rollback cannot be assumed security-safe.

Only standardPG18 installation found; pg_dump18 can export17, but its output is
not guaranteed to restore on17. Official version compatibility reviewed; recommend
PG17 client tools/separate17 restore target to match production, no tool install
or source version change performed/authorized. Existing smallPG18 tests preserved.
No prior regression repeated, cluster started, production connection, secret read,
backup/export/restore, migration, production setting change, push/merge/deploy.

Manual backup/final readiness documents updated. Next owner stage is identifying
existing encrypted backup/restore storage outside Git/cloud sync; encryption keys
must stay private and separate. Then review version-matched tools, private access
and exact commands. Backup gate remains blocked until actual encrypted-copy
retrieval and isolated verified restoration;35/36 complete/PY-35 partial.
