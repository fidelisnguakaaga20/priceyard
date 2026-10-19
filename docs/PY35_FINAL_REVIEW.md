# PriceYard final review - batch 87

**35/36 complete; PY-35 partial. Deployment is blocked.** All executed checks
below pass; the nine real-world release gates remain **not run**, not failed.
No production services, credentials, customer data, migrations, provider sends,
push, merge or deployment were used. Conditional deployment approval does not
substitute for the required evidence.

Current101:owner authorizes private reuse of existing Render DATABASE_URL; hidden
local input/extraction mode tested with five fabricated cases, preserving pinned
source and full TLS and requiring a separate archive passphrase. Private prompt
opened; actual credentials not seen/retrieved by Codex. No remote settings/reset,
successful login/export/restore claim or new gate pass. Owner guidance:
[private Render credential step](PY35_ACTUAL_BACKUP_RUN.md).

Current100:latest owner attempt FAILED authentication(server password rejection),
not TLS. No dump/archive; diagnostics preserved. Native PG17.11 client versions
confirmed, same major but never reached by failure. Permissions/actual schema
compatibility remain unchecked. Auth-first prompt flow passes three new mocked
tests; backup deliberately NOT reopened until valid credentials can be verified
privately. No resets, production retry/SQL by Codex, migrations/push/deploy or
new release-gate success. See[actual backup status](PY35_ACTUAL_BACKUP_RUN.md).

Current99:actual owner backup attempt FAILED TLS certificate verification before
SQL/dump, not data corruption. No dump/archive created; protected diagnostics
preserved. Private CA trust corrected from official Supabase dashboard distribution,
no TLS downgrade or system trust changes. Three new certificate guards pass and
credential-free TLS1.3 certificate/hostname handshake passes. Corrected private
prompt reopened; authenticated backup/restoration still unverified. No release
gate newly passed; no migrations/push/deploy. See[execution status](PY35_ACTUAL_BACKUP_RUN.md).

Current97:owner confirmed separately retrieved protected recovery copy; non-secret
report checked. Actual read-only backup/isolated restore now explicitly authorized,
but no password or source connection available to Codex. Owner-only backup helper
prepared outside Git;four new safety guards pass. Owner runs private prompts next:
[actual backup step](PY35_ACTUAL_BACKUP_RUN.md). Database restoration, actual
compatibility and all mandatory live gates remain unverified. No migration/push/
deployment authorized or executed.

Current96:owner-local recovery PFX export succeeded; non-secret validation and
ciphertext metadata independently confirm AES256, matching private key/challenge
and matching saved digest. Earlier absent-key statuses below are superseded.
Separate private off-computer copy/retrieval comparison remains pending; helper
prepared outside Git with syntax check only. No actual production backup, source
connection, upload by Codex or new live gate pass. Next owner action:
[protected recovery copy](PY35_CONNECTION_AND_KEY_CHECK.md).

## Owner-confirmed hosting update - 2026-10-18

These references were supplied by the owner from Render, not independently
queried through production access. Repository: `fidelisnguakaaga20/priceyard`.
Owner subsequently confirmed Supabase project `priceyard`, reference
`lrvpjfbtmftjkzaxbunk`, Free plan and no managed backups. Manual backup preparation:
[PY35_MANUAL_BACKUP.md](PY35_MANUAL_BACKUP.md). Read-only SQL is prepared but NOT
executed by Codex; owner reports execution2026-10-19:PostgreSQL17.6,14 MB,
installed0021_feedback_screenshot. Complete actual schema compatibility remains
unverified. Local22-file migration-chain review confirms only0022_login_revocation
pending, with earlier migration files unchanged against preserved master. No
encrypted export/restoration yet. Match17 recovery tooling rather than treating
an18-only restoration as proof of17 recovery. Secure access, encrypted storage
and isolated customer-data restore target remain prerequisites. No live gate passed.
Windows-local setup91 has an empty private folder outside Git with verified
user/SYSTEM ACL; it is NOT encrypted. Bundled7za23.01/PG18 found, PG17 missing in
standard installation, BitLocker status unverified. No customer export/restore or
upload. Next:[PY35_WINDOWS_BACKUP_SETUP.md](PY35_WINDOWS_BACKUP_SETUP.md).
Stage92 supersedes the missing standalone-encryption-tool status:7-Zip26.04
verified with eight synthetic AES-256/filename/password/restore checks; artifacts
outside Git, no real password. PG17/protected disk and actual backup remain pending.
Stage93:PG17.11 portable tools and five-table/ten-row encrypted fabricated
backup/restoration now pass; roles/ownership/grants/schema/sequences match in a
separate cluster, both stopped. Owner confirms BitLocker OFF. Customer-data
workspace/host protection requires owner-admin setup; real backup remains blocked.
See[PY35_PG17_SETUP_RESULTS.md](PY35_PG17_SETUP_RESULTS.md). No live gate passed.
Current94 supersedes virtual-disk proposals:built-in EFS/new encrypted folder and
focused fabricated PG17 restore pass, all1,302 database/log/temp files encrypted.
GitHub get_repo/search_branches now confirm readable repository/master and caller
permissions; repository access is no longer missing. No remote writes. Actual
backup/key recovery/Supabase access and provider/host release gates still pending.
Minimum owner actions:[PY35_MINIMUM_BACKUP_RELEASE.md](PY35_MINIMUM_BACKUP_RELEASE.md).
Current95:owner supplied Session pooler host aws-0-eu-west-2.pooler.supabase.com,
port5432/database postgres/user postgres.lrvpjfbtmftjkzaxbunk. No password or DB
connection. EFS workspace remains valid; recovery PFX absent. Owner-local helper
prepared for AES256 PFX export/matching-private-key validation; six fabricated
validator tests pass, real helper not executed. Next:[PY35_CONNECTION_AND_KEY_CHECK.md](PY35_CONNECTION_AND_KEY_CHECK.md).

| Setting | Backend | Frontend |
| --- | --- | --- |
| Render service | `priceyard-api` | `priceyard` |
| Service ID | `srv-da6d9gqjnfac73e2sbfg` | `srv-da6ddb2jnfac73e39490` |
| Public address | `https://priceyard-api.onrender.com` | `https://priceyard.onrender.com` |
| Linked branch | `master` | `master` |
| Deployed commit shown | `a9cf1b9` | `76dbd27` |
| Root directory | `backend` | Not supplied; historical notes say `frontend` |
| Auto-Deploy | **On Commit** | Not supplied; do not assume disabled |
| Build command | `pip install -r requirements.txt && alembic upgrade head` | Not supplied |

**Release blocker: backend builds automatically run migrations.** A push/merge to
linked master can start a deployment and database changes before runtime health
checks. Do not publish/merge candidate code or use a deployment/rebuild/rollback
action while this remains unreviewed. No production setting was changed here.
The different deployed commit labels are a compatibility question, not proof of
a defect; obtain exact artifact/full-commit identities before selecting rollback.
Neither label establishes the database's installed Alembic revision.

Separate frontend/backend hosts require exact cookie, Origin/CORS and API routing
verification; public HTTPS addresses alone do not close that gate. The owner has
identified services/repository, but authenticated access, actual settings review,
runtime compatibility, backup and provider verification remain outstanding.

### Next information only: identify Supabase and backup availability

Owner opens the existing project at `https://supabase.com/dashboard`. Provide
only project name, project reference (the non-secret dashboard URL identifier),
current plan and what **Database > Backups** shows:available backup date/time or
unavailable. Do not share Connect strings, passwords, API keys, customer rows or
unredacted settings screenshots. Do not restore/download/create anything yet.
Official reference: https://supabase.com/docs/guides/platform/backups.

After identifying the project, prepare a bounded read-only SQL review for owner
approval: exact target/operator, read-only transaction, short query/lock timeouts,
PostgreSQL version, Alembic revision and application schema/constraint/index/
permission metadata; no customer-row selection, DDL, migration or app startup.
Credentials stay in approved protected storage; no new role or grant without
separate authorization. Metadata-only review cannot prove historical data quality
or substitute for backup restoration. No SQL or production connection run here.

### Required safe migration/backup/rollback sequence - not authorized or run

1. Identify source/project and exact deployed artifacts. Approve and execute only
   the scoped read-only compatibility review. Unknown/older populated revisions
   stop for explicit migration review; never stamp or replay migrations blindly.
2. Approve backup source/scope/operator, encryption and separate storage,
   retention/recovery objectives, and an isolated restore target with sufficient
   resources. A plan's backup listing is not recoverability evidence. Confirm
   provider auth/roles/RLS/extensions/configuration and any Storage files required
   for recovery:database backups do not contain Storage file contents. Free-plan
   availability must be checked; no paid upgrade assumed or approved.
3. Take a consistent real backup via an approved, version-compatible procedure;
   protect temporary output and encrypt durable copies, retain integrity evidence,
   verify retrieval/decryption, then restore to the explicitly approved isolated
   empty target. No overwrite/clean/restore of production. Keep actual records out
   of Git, chat and the synthetic-only test fixture. Disable provider egress,
   notifications and scheduled jobs; verify protected data/constraints/security/
   payment-value equivalence privately and record only redacted results.
4. Using that verified isolated restoration, rehearse the exact reviewed migration
   delta and compatible application rollback. Preserve all business and revocation
   evidence. Do not assume Render code rollback reverses database changes; never
   use a destructive downgrade or old backup to erase intervening transactions.
5. Only after other release gates pass, review an explicit production change
   proposal:control automatic deployment and decouple migrations from ordinary
   builds, define operators/window/write and payment-reconciliation coordination,
   fresh accepted backup, exact migration steps and stop/rollback thresholds.
   Any change to Auto-Deploy/build settings, migration, push or deployment still
   needs owner approval. Failed rehearsal or missing recovery blocks release.

This update supplies requirements, not authorization to access customer records
or run a backup. All nine live gates remain unrun; count stays35/36.

## Recovered state and confirmed fix

Started from actual `5bce117438aae2c77fc735ffb787fb3dc5dd17f8` on
`codex/priceyard-original-preserved-20261016`. The interrupted service fix and
untracked expiry test were preserved byte-for-byte under ignored
`tools/local-test/runtime/batch-87-interrupted-work/` before further work.
No changes were discarded. Original master `76dbd27588de4aa37f3163d8b263d4b72a2cff32`
and backup branch `258991019e5af8b36eff407a8efa2c9fd03dd644` stay intact.

**Confirmed defect:** an account read could load expired access, then overwrite
the active status/ordinary paid role after payment committed a renewal. Payment
evidence and dates could remain while access was incorrectly expired. The old
committed function reproduces six failing scenarios in memory without reverting
the source. The fix reloads due access under the existing User-then-Subscription
locks before expiring anything, and commits/releases or rolls back consistently.
Valid access takes no new expiry locks. No schema, UI or business-rule change.

Preserved:14-day trial; NGN2,500/30 days; NGN6,000/90 days; remaining paid/trial
value; indefinite-grant review; referral cap; staff roles; UTC paid expiry;
original design/measurements, historical records and all14 Admin cards.

## Independently executed regression evidence

| Check | Result |
| --- | --- |
| Defect reproduction against old committed helper | Six expected failing subcases; working fix restored after memory patch |
| Focused expiry unit tests |6 passed,0.249s; real expiry, renewed stale reads, staff/history preservation, rollback and missing row |
| Full isolated backend discovery |307 passed, zero failures/errors/skips,117.546s; includes authentication, payments, subscriptions and notification regressions |
| Native PostgreSQL |5 passed,9.689s; twelve GET/payment interleavings across trial/paid and ordinary/Reporter/Admin, real blocking observed; listing expiry, verify/webhook replay and distinct concurrent purchases |
| Browser purchased value | Paid renewal and trial purchase retain remaining time; replay adds no second credit; original dashboard |
| Browser indefinite grant | Checkout blocked; confirmed receipt held once; original Admin control resolves synthetic grant; purchase credits once |
| Browser access | Eight role/status scenarios preserve current/detail/history boundaries |
| Browser Admin | All14 original labels and exact totals; one summary request; outage/reload recovery |

Evidence:`tools/local-test/evidence/batch-87-*.json`. Native database is stopped,
26/80 retained schemas, max12 connections/32MB buffers, fsync enabled. Heavy
phases were sequential; one browser at a time. Browser requests stayed loopback;
backend sockets/DNS were denied. No new frontend build was needed because frontend
source is unchanged; the local release checker verifies source/build identity.

Retained setup failures:PowerShell redirected a known Starlette/httpx deprecation
warning as a terminating native-command error before discovery; corrected log
launch then completed307 tests. First browser launch lacked the path to the
already-installed isolated browser; setting that path succeeded without downloads.
Two old browser harnesses still supplied `Bearer null`; updated them to the
already-approved protected cookie/CSRF session. No application workaround or
security restriction bypass. No unresolved executed application test failure.

## Authentication, payment and database review

Reviewed current security/session, Google ownership/reset, payment evidence and
locking, subscription and migration-safety paths against the retained final
readiness requirements. No separate newer audit report was recoverable from the
other conversation; no claim that unseen findings were reviewed. The confirmed
new critical finding above is fixed.307 backend tests provide fresh regression
evidence, not a guarantee against every undiscovered defect.

JWT revocation/version, protected cookie/CSRF and stable Google subject boundaries
remain; browser-host routing and real Google consent are still unverified.
Provider evidence and purchased time are protected locally; actual Paystack TEST
checkout/webhook/recovery remains blocked. Production revision/pooler/permissions
are unknown. The reviewed additive0021-to0022 path preserves synthetic records;
unknown populated schemas stop. Revocation evidence cannot safely be removed by
downgrading. An application rollback must preserve compatible schema/evidence.

Historical hosting notes record separate Render static/backend services, backend
Python3.12.8 and Supabase PostgreSQL; these are historical, not inspected current
settings. Actual same-site API routing, cookie/CORS/proxy headers, clean target
runtime installation and current dependency advisory review remain release gates.
Synthetic backup restoration83 is retained evidence, not proof of a customer
backup. Actual encrypted backup retrieval/restoration and agreed retention,
acceptable data-loss window and recovery time must pass before rollout.

## Exact missing access and safe provision

Render/Supabase targets are owner-identified, but authenticated operator access
is not established. GitHub repository/default-master read access and caller
permissions were verified94; candidate publication/full deployed artifact IDs
remain unverified. No Git fetch/push was performed.

| Area | Missing information/access | How the owner can provide it securely |
| --- | --- | --- |
| Render | Owner confirmed services/domains/master and migration-running backend build above. Still need workspace/operator access, frontend Auto-Deploy/build/root, current runtime/start/routing settings and isolated hosted test target | Share only remaining non-secret settings or supported least-privilege operator access. Backend Auto-Deploy is On Commit: no push/merge to master or setting changes now |
| Supabase | Owner supplied exact Session pooler endpoint/username95 and reported17.6/14 MB/0021, Free/no backups. Full schema/permissions/extensions/TLS/auth and actual backup remain unverified | EFS/PG17 already verified; owner runs local recovery-key helper first, then private DB password entry at reviewed backup prompt. Do not request connection details again or secrets in chat; no production/role/grant change performed |
| GitHub | Read-only get_repo/search_branches94 confirm repository/default master and caller pull/push/admin permissions. Full deployed commit identities/candidate remote publication remain unverified | No new repository-access grant needed. Do not push/merge or change settings: linked master automatically builds/migrates production. Candidate stays local |
| Actual backup/rollback | Approved backup source, encrypted off-host destination/retrieval access, isolated restore target, operator, retention and recovery objectives; compatible rollback artifact | Choose the targets/operator and approve actual-backup handling separately. Use host secret storage and private encrypted files; share only storage references and redacted verification results, never a customer dump in chat |
| Provider verification | Paystack TEST credentials and reachable nonproduction callback/webhook; Google test origin/client/accounts; test message sender and consenting recipients | Enter test-only configuration into approved protected storage yourself/operator; share only secure storage references, URLs and approved recipient identities. Never share account passwords, live keys or real cards |

The existing GitHub connector's read-only repository checks now succeed; no new
GitHub login or permission grant is required for those reads. Neither available
write permissions nor sharing access references authorize publishing/deployment.

## All nine gates still open

1. Public HTTPS, reverse-proxy cookies/session/Google return and target browsers.
2. Actual encrypted off-host backup retrieval and isolated restoration.
3. Read-only production schema compatibility, then separately reviewed rollout
   and rollback; no migration until backup acceptance.
4. Actual Paystack TEST success/failure/replay/missed-event recovery and value.
5. Approved scheduler/checkpoint/restart/alert operation on the chosen host.
6. Google test login and approved email/push/WhatsApp delivery.
7. Host monitoring, clock/pool/resource limits and bounded representative load.
8. Clean target-host dependency installation/advisory review and configuration.
9. Approved historical exceptions/public text review and final cutover decision.

See [OPERATIONAL_READINESS.md](OPERATIONAL_READINESS.md),
[RELEASE_GATES.json](RELEASE_GATES.json) and
[STAGING_SETUP_GUIDE.md](STAGING_SETUP_GUIDE.md). Additional services or spending
are not authorized or assumed. Stop before deployment until these blockers close.
