# Actual encrypted backup - owner-private execution, batch97

## Current117: real backup AND isolated database restoration PASSED

Verified2026-10-20 (WAT), using the existing20261019T213738Z archive; no new source
connection/export/password entry. Final recovery37.2 seconds:59 tables' counts
and content SHA256 digests match, as do recorded schema/column/type/default/live
order, constraints/indexes/RLS, roles/memberships/settings/effective permissions,
sequences and large objects. Native checksums pass; Alembic remains0021. No actual
or production migrations. Original portable ciphertext checksum unchanged.

Actual provider details required reviewed recovery adaptations: load the Nix
libraries at runtime; preserve original supabase_admin bootstrap/grantors; skip
only its duplicate CREATE, keeping every attribute/grant clause; restore exactly
two extension-view owners and two GraphQL schema ACLs from the protected snapshot.
No source record/history/security policy rewritten. Canonical comparison preserves
ACL meaning, live column order despite dropped-attribute holes, and uses native
parser checks on empty temporary tables for seven equivalent varchar-array casts.
Failure reports and original helper variants remain protected for audit.

Nine fabricated checks now cover these cases plus RAM/swap/network/readonly
isolation, exact five extension versions/locale and restore/checksum integrity.
SafeUpdate still rejects unbounded UPDATE. Real customer rows never displayed.
Ordinary Docker volumes/binds/ports and persistent container logs are prohibited;
source exports/recovered files stay EFS, database files only in bounded tmpfs.

The real container was removed; Docker/WSL are stopped and the test-created WSL
configuration was archived/hash-checked/removed, restoring its previous absence.
Existing Docker images/data/configs preserved. Public image download367203535
compressed bytes; no paid service/project or customer upload. App source/design
and production unchanged. Secret-free recovery code is versioned, inlining only
the identical reviewed catalog query; static equivalence and duplicate-run guard
pass without repeating restoration. See [verified recovery](PY35_VERIFIED_RECOVERY.md).

Private evidence: latest-production-backup-status.json; EFS run
real-ram-restore-result-private.json. Actual database restoration is verified;
off-computer archive copy, source0022 clone rehearsal and other live gates are NOT.
35/36 remains. Current gate ledger:[actual gates](PY35_ACTUAL_RELEASE_GATES.json).
All earlier Current entries below are retained chronological history.

## Current116: compatible RAM-only target passes fabricated restoration

New mobile data and4.16GiB free host RAM permit a bounded retry. Public registry
TLS and local Docker29.2.1 readiness pass under2GiB/one CPU/swap0. Prior1GiB
failure cause is not retrospectively established. Docker auto-starts three local
EasySpend containers; their files/settings must not be altered for PriceYard.

Downloaded only public official Supabase Postgres17.6.1.136, selected from
[official compose](https://github.com/supabase/supabase/blob/master/docker/docker-compose.yml).
Pinned Linux amd64 manifest:
`sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b`.
Compressed layers367203535 bytes. No account credential, cloud project or real
backup export involved. No declared image volumes.

New synthetic-only checker passes: non-root/no capabilities/read-only root,
network none/no host mounts/no persisted logs,512MiB memory=memory-swap, actual
cgroup swap0 and guest swap0, tmpfs data. Exact source extension versions and
en_US.UTF-8 locale pass, including Vault0.3.1. Sequential fabricated PG17 dump/
restore matches data digest, five extensions and native checksums; container
removed. Initial SHOW lc_collate incompatibility corrected to catalog query;
first failure retained, only affected test repeated. Actual backup not opened by
this checker. Evidence: private ram-fixture-result.json and pinned-image result.

Actual saved SQL review: hashes match; no PROGRAM/ALTER SYSTEM/LOAD/server-file IO
or untrusted procedural language; no foreign server/subscription/custom tablespace.
Vault tables empty. Source has six provider event triggers,103 functions, and
supautils/safeupdate role preloads, so do not reuse the old simple-inventory
restorer by disabling its guards. A separate reviewed isolated Supabase profile
is needed before any real restoration. Database recovery remains unverified.

Attempt3 Docker runtime currently active with owned temporary WSL cap; record
path docker-feasibility-resource-config-attempt3.json. Stop Docker after work and
archive/hash-check/remove only that new config to restore prior absence. No new
source connection, app changes, migration, push/merge/deploy.35/36 unchanged.

## Current115: bounded Docker startup failed; real backup untouched

After owner READY, host free RAM was2.61GiB. Docker was the only installed WSL
distro and was stopped. Created a new temporary .wslconfig with1GiB/one CPU/swap0,
recording original file absence and SHA256. Started existing Docker Desktop; no
image pulled, test container created or real archive loaded. Explicit local-only
named-pipe engine readiness query timed out after15 seconds. Guest memory probe
showed920068KiB total,30520KiB available,swap0. No confirmed kernel OOM; classified
local logs show timeout. Exact startup root cause remains UNCONFIRMED.

Stopped rather than increasing limits on a pressured host. Initial graceful-stop
command returned125; next normal stop remained pending during cleanup, eventually
returning0. Terminated only the test-started
Docker process IDs and their WSL distro, then confirmed WSL stopped and no related
processes. Original Docker disk/images/containers and backup files not deleted.
Archived the newly-created settings under private root, checked its recorded
hash, removed only that new file and restored the previous no-.wslconfig state.

Evidence: private docker-feasibility-result.json and resource-config record.
This is an infrastructure readiness failure BEFORE synthetic-container tests,
not a failed customer restoration or failed backup. Adequate host memory and
resolved Docker startup are needed before another attempt; owner normal reboot
may free RAM but is not a confirmed fix. No automatic retry/limit increase/image
download/cloud project or plaintext Docker restore. No source backup repetition,
credentials, production connection, SQL/migration, app changes, push or deploy.
35/36 unchanged; actual encrypted archive passed, full recovery still unverified.

## Current114: existing Docker inspected; no restoration started

Docker Desktop/CLI exist, but WSL docker-desktop and Docker processes are stopped.
Normal Docker data lives in an unencrypted VHDX; it must not receive plaintext
customer records. Host has15.7GiB physical RAM, only2.3GiB currently available.
Avoid startup of an unconstrained full stack or assumptions that free disk equals
free memory. No daemon, container, download, new service or production connection
was started by this inspection. No existing Docker settings/storage were changed.

Saved manifest confirms Vault tables contain no rows, so this snapshot does not
justify obtaining the provider's encryption root key. Vault extension/locale and
provider SQL compatibility still require verification; no objects may be omitted.

Potential no-new-cloud path is a small fabricated-only RAM/tmpfs container test,
before any real restore: disabled networking, read-only root, no persistent
volumes/customer logs, bounded CPU/memory and verified swap prohibition. This is
a candidate, NOT proven protected storage. [Docker tmpfs documentation](https://docs.docker.com/engine/storage/tmpfs/)
warns tmpfs can reach swap; [Docker memory controls](https://docs.docker.com/engine/containers/resource_constraints/)
describe equal positive memory/memory-swap limits preventing container swap.
Runtime/kernel enforcement and host-memory limitations still need verification.
Free sufficient RAM before runtime testing. No full restore or new gate passed.

## Current113: real encrypted backup PASSED; full restoration BLOCKED

Owner entered credentials and a separate archive passphrase privately and typed
BACKUP. Direct verified TLS, role/source/revision/read-only and table permissions
passed. Run20261019T213738Z completed in102.8 seconds: full custom database dump,
password-free roles,59 table fingerprints and catalog/schema/sequence/large-object
evidence. AES-encrypted archive and filenames, independent EFS-only decryption
and matching file digests passed. Source connection closed; backup helper stopped.
Independent local archive SHA256 and recovered bundle hashes passed again.
No production mutation, reset, migration or new provider connection for review.

Encrypted archive is outside Git under owner-private EncryptedArchives:
`PriceYard-20261019T213738Z.7z`. Protected run, exports and recovered copy are under
PrivateRestoreEfs. Actual status is encrypted_backup_integrity_passed_restore_review_required;
database_restoration_verified=false. No archive upload or second-copy claim:
the already verified Google Drive recovery PFX is a separate object.

Actual inventory review blocks the current restoration path BEFORE EXECUTION:

- Supabase Vault0.3.1 is absent from installed local PG17 extension files.
- Source en_US.UTF-8 locale differs from the reviewed C-only restore path.
-103 functions and one publication need provider/executable-object review before
  loading untrusted dump SQL or enabling anything that could contact providers.

No server started, SQL loaded, extensions omitted or safety guard relaxed. A
reviewed Supabase-compatible isolated restore target with protected storage is
required; preserve all managed/customer/history objects and do not substitute
production. Private protected restore-readiness-private.json records blockers.
This is a successful encrypted backup/integrity check, NOT a verified recovery.
35/36 remains; no migration/push/merge/deploy until recovery and other gates pass.

## Current112: direct TLS verified; separate guarded backup prompt opened

Phone hotspot provides an IPv6 default route; the prior MiFi did not. Direct
same-project hostname resolves, TCP5432 connects and a credential-free PostgreSQL
TLS handshake verifies hostname and existing pinned CA with TLS1.3. No database
authentication or SQL occurred in these checks. Sandbox socket restrictions were
handled through normal approved escalation, not a security bypass.

New private direct-route helper and launcher preserve original pooler files.
Host is pinned to the same-project direct endpoint; user is postgres. Render URL
still accepts only that project's direct or original pooler credentials and
extracts the password only, never accepting URL-supplied connection options.
The server-reported TLS guard remains mandatory (now database_connection_ssl).
No read-only, identity, recovery, EFS, export, archive or restore guard removed.

22 focused offline checks pass: accepted direct/pooler URLs, single decoding,
wrong project/user/database/port/missing password rejection, source identity and
TLS/revision rejection, both native/Python connection pinning/read-only behavior,
and unchanged other backup functions. Launcher parses successfully. Existing
full synthetic backup/restore results are reused; no database processes started.
Evidence: private direct-route-safety-results.json. Direct helper SHA256:
`bcd92f38c3ca888117c6c9cd5488c8ed66e4639ed37f42ebdae4dddf4731d686`.

Owner instructed continuation. ONE approved visible PowerShell console opened
(process29332), hidden Render URL/passphrase input, after hash/no-overlap/no-real-
success-report checks. Await private entry/result; do not open another prompt or
retry. Actual backup and restoration remain unverified. Preserve stop-on-failure
and protected restore-inventory review. No application/provider changes,
migrations, push, merge or deployment;35/36 local improvements unchanged.

## Current111: actual source preflight failed; no export started

Protected diagnostics for run20261019T133223Z identify the exact rejected check:
`pooler_to_database_ssl=false`. Login and authenticated metadata read succeeded;
client TLS was active with `verify-full`. Database/role `postgres`, read-only `on`,
version `170006` and revision `0021_feedback_screenshot` matched expectations.
The server-side SSL value describes the pooler-to-database connection, separately
from the successfully verified client-to-pooler TLS connection.

Error: `Source preflight rejected: pooler_to_database_ssl; no dump created`.
This run contains only EFS-encrypted error/metadata files and its trusted CA file;
no dump, roles export or archive. No real success report or running export process.
No credentials or private data are copied into this report. Application unchanged.

STOP at this safety failure. No automatic retry, new credential prompt, reduced
TLS requirements, production settings change, migration or deployment. A verified
end-to-end TLS route is needed before another attempt; same-project direct
connectivity is a candidate, not yet verified. Backup and restoration remain
unverified; the release gate is blocked before export, not a failed restoration.

## Current110: visible hidden-entry window explicitly approved and opened

Owner now explicitly approves a visible PowerShell window with hidden input for
ONE controlled read-only source backup and protected isolated restoration.
Earlier refusal/review ambiguity is resolved by that explicit instruction.
Git clean atb788160; private backup/restore code hashes match offline7b422e1;
no overlapping backup process or successful real status report existed. Reused
all preparation without rerunning the offline suite or changing application code.

Approved existing launcher opened successfully(process37048), Render DATABASE_URL
mode. Owner enters URL and separate archive passphrase privately; no secret in
tool arguments/chat/logs. No backup result yet at this update. Do not open another
window/retry if waiting for input. Stop on safety failure; review real inventory
and SQL before any fresh EFS/local17 restore. Current restore gate accepts only
its reviewed simple inventory; do not claim general Supabase restoration support.
No automatic role/provider enablement, migration, push, merge or deployment.
Only after successful archive/restore evidence may the actual-backup gate change.

## Current108: main session reconciled; no redundant setup

Confirmed current0b9dab3 contains verified offline7b422e1 and watchlist work.
Private helper hashes and saved passing offline reports match; master/backup
branches and all completed changes preserved. No tests or setup repeated.
No real backup result or active backup process. The previously approved controlled
attempt remains unstarted after the recorded automatic-review rejection106.
Next clarify permission for a **visible local window with hidden credential input**;
no secrets in chat. Do not reinterpret general resume as resolving the specific
review ambiguity or launch by another route. No production/push/migration/deploy.

## Current106: protection reconfirmed; launch blocked before production access

Owner now approves ONE controlled read-only backup and protected PG17 restore.
Existing owner ACL, EFS encryption, private-key sign/verify challenge, unchanged
recovery/second-copy evidence, available space, verified helper hashes and absence
of active backup processes pass local checks. No setup was recreated.

Automatic approval review rejected the combined preflight/interactive-window
command before execution:it interpreted a visible PowerShell window as conflicting
with requested hidden credential entry. The approved helper uses getpass in a
private TTY and hides typed secrets; it does not capture them in tool output.
A separate local-only reconfirmation passed. No indirect/alternative launch was
attempted, and no credentials or production connection occurred. Thus no new
production backup or restoration succeeded or failed; they have NOT STARTED.

Stop for explicit clarification/approval of the visible local console with hidden
credential entry before another launch review. No passwords in chat, repeated
preparation, TLS weakening, migrations, push, merge or deployment.

## Current105: offline procedure verified; actual backup remains unverified

Owner authorizes offline correction and fabricated full-procedure verification,
then STOP. No private prompt/window, real credentials, production connection or
actual backup this batch. The last diagnostic's unsupported `ssl_attribute` call
is removed; native `ssl_in_use`, pinned CA/hostname verification and original
source/read-only/upstream TLS requirements remain. Explicit UTF8, correct Win32
EFS return handling and rollback before passphrase input fix additional defects.
New snapshot/identity/privilege checks run after the passphrase wait.

The exact backup main and diagnostic run with genuine installed psycopg3.3.6,
PostgreSQL17.11 TLS and7-Zip against fabricated loopback data; console input and
source/CA constants are overridden in test memory only. Source is stopped before
a fresh isolated PG17 restoration. Encryption, filename secrecy, decryption,
record/schema/role comparisons and native checksums pass. Additional restore
guards fail closed. Existing EFS/recovery setup is reused, not recreated.

Both test servers are stopped. All plaintext fixture/export files remain in EFS;
failed first fixture is preserved. Actual Supabase object/role/locale compatibility,
pooler-hop TLS and source privileges still require real inventory/evidence. The
restore helper deliberately refuses unknown provider/executable objects/settings;
it must not automatically restore an unreviewed real dump. The older source-guard
mismatch is not retrospectively diagnosed by synthetic success. No production
backup/restoration or release gate is newly claimed. Await owner approval before
any live attempt. Current code hashes and evidence:
[offline verification](PY35_OFFLINE_PROCEDURE_VERIFICATION.md).

All earlier helper hashes and open-window instructions below are historical.
No window is currently opened by this batch; do not follow an old command merely
because it appears in the retained development history.

## Current104: one specifically approved metadata-only diagnostic

Owner authorizes one read-only pooler connection with private DATABASE_URL entry.
Inspect-PriceYardPooler.ps1/.py prepared outside Git, prior backup helper unchanged.
Reuses existing ACL/EFS/key checks, exact source pin and verify-full CA, hidden
URL parser and clipboard clearing. Three fabricated tests pass:typed mismatch
capture, expected baseline, exactly one connect call/no export calls. Private
PowerShell opened(process40776); waiting for input/result at this update.

Only identity/version/revision/read-only/encoding/types/client TLS/server TLS
metadata is queried and saved under PrivateRestoreEfs/pooler-diagnostic-*.
No raw exception text, credentials or URL saved. No customer records, backup tools,
archive password or migrations. If actual ASCII byte strings are observed, a
transaction-local UTF8 setting and metadata recheck use the SAME connection;
no persistent server setting change or second authentication. Connection is
rolled back/closed. A diagnostic result does not authorize automatic backup.
Owner replies DIAGNOSTIC COMPLETE only; Codex inspects protected report afterward.
No exact mismatch or verified correction yet; no extra SQL Editor request.

## Current103: supplied metadata matches; original session evidence unavailable

Owner successfully ran the metadata-only query and reports server_version_num
170006, database postgres, installed_revisions[0021_feedback_screenshot]. These
match the expected guard values. They do NOT establish the remaining observed
pooler session role, read-only text/type or pooler-to-database SSL flag. The old
failed run contains no per-field report; its85-byte error cannot identify which
remaining condition failed. Reinspection confirms no dump/roles/archive.

The earlier SQL Editor query was insufficient to finish pooler-specific diagnosis;
do not treat matching results as a reason to weaken any guard or assume upstream
TLS failed. Last owner attempt already proves successful authentication and
metadata SELECTs, not stale Render credentials. No passwords/URL retained.

Exact diagnosis requires a new bounded authenticated **pooler-session metadata**
observation with client TLS, encoding/types, role, transaction state and upstream
SSL recorded before the guard. Current helper captures most such values, but
source encoding/types should also be included if a focused diagnostic is prepared.
This is not a repeated setup test or a database migration; it requires private
credential input because secrets were deliberately discarded. Owner instructed
no repeated attempt before diagnosis, so no prompt/connection/retry launched in
this batch. Actual backup/restoration remains unverified. Do not claim the exact
mismatch or successful correction without runtime evidence.

## Current102: successful login; source-validation mismatch not yet identified

Latest owner run20261019T080749Z fails with
`Source identity/version/TLS/read-only/revision differs; no dump created`.
The exact code path proves authenticated connection and SELECT of identity and
Alembic metadata completed. Render credential works for the approved pooler;
there is no evidence of stale credentials or password-encoding failure in this
attempt. Do not reset/retrieve/paste the same credential again merely to retry.

The helper's combined error discarded which of six checks disagreed, and did
not retain observed values. Exact failed component CANNOT be recovered from
the85-byte error. Do not claim it was TLS, permissions or a database upgrade.
Only encrypted CA/error files exist; no dump, role export or encrypted archive.
All files retained. No source connection or password request in this batch.

One confirmed design ambiguity:server pg_stat_ssl describes the PostgreSQL
backend connection. Through Supavisor this is the pooler-to-database hop; it
does not measure the client's verified TLS connection. A false upstream flag
is a possible cause, not an observed fact. Sources:
[PostgreSQL SSL statistics](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-SSL-VIEW),
[Supabase upstream/client TLS distinction](https://github.com/supabase/supavisor/blob/main/docs/configuration/tenants.md).

Corrected diagnostics, not the unknown underlying mismatch:record only protected
version/database/role/read-only/revision/client TLS/upstream TLS metadata before
the guard and label each failing requirement individually. Keep all original
checks, including upstream SSL, and add explicit native client TLS check. No
silent requirement removal or TLS downgrade. Previous versions retained outside
Git as `.before-preflight-diagnostics`. Two new tests pass, including each
individual mismatch remaining blocked; no repeated setup/native/DB test suites.

**No backup prompt reopened.** Simplest next step is the prepared metadata-only
query in [PY35_SOURCE_GUARD_DIAGNOSTIC.sql](sql/PY35_SOURCE_GUARD_DIAGNOSTIC.sql):
Supabase project priceyard > SQL Editor > New query, paste and run the entire
script using existing Google/GitHub dashboard login. No database password needed.
Share only version/database/revision result values, never screenshots/secrets.
This rules out persistent schema/version drift; SQL Editor uses a different
connection and CANNOT establish pooler-hop SSL or pooler session settings. Further
evidence may still be needed; do not assume this alone certifies backup/release.
No migrations, reset, provider changes, production retry by Codex or deploy.

## Current101: private use of existing Render DATABASE_URL

Owner confirms Supabase website login is Google/GitHub; existing Render backend
has DATABASE_URL. Website OAuth is separate from PostgreSQL password. Owner now
authorizes privately using that existing credential, without resetting it or
editing production settings. No Render API/credential retrieval by Codex.

1. Sign into [Render Dashboard](https://dashboard.render.com), select
   **priceyard-api > Environment**. Reveal/copy the existing **DATABASE_URL value**.
   Do not click Edit, Save or Deploy; do not copy it into chat or a text file.
2. Paste it only into the opened PowerShell **hidden DATABASE_URL prompt** and
   press Enter. Nothing will appear while pasting. Do not paste into a command
   line. Current clipboard is cleared after input; remove the copied item from
   Windows clipboard history separately if that feature is enabled.
3. Login/identity/initial read permissions must pass first. Then choose a separate
   new backup passphrase, save it privately, enter twice and type BACKUP.
   The helper rejects reusing the database password as the backup passphrase.
4. Reply BACKUP CHECKED or BACKUP STOPPED only. No URL/password/logs in chat.

Private input window opened(process70696). If unavailable, the approved mode is:

```powershell
& "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Start-PriceYardEncryptedBackup.ps1" -UseRenderDatabaseUrl
```

Do not start a second copy while one is running. Credentials exist only in local
process memory and the dump client's private environment, not arguments/history/
logs/files. Python cannot guarantee forensic memory erasure; clipboard history
is not erased by clearing its current value. No Windows/Render settings changed.

New mode uses the existing installed SQLAlchemy parser, matching app semantics.
It validates direct project host/user5432 or the confirmed project-qualified
pooler5432/6543 URL and postgres database. Only password is recovered, decoded
once; URL host/query/TLS options are never used to connect. Existing approved
pooler5432/verify-full remains pinned. Parser errors are generic and never include
the URL. No dotenv reads, installation, password reset or remote setting changes.
Prior helpers preserved as `.before-render-url` copies. Five new fabricated tests
pass:decoding, target/TLS pinning, wrong project/input rejection without secret
leakage, unsupported provider/port rejection, different archive password.
Authentication and actual export/restoration are still unverified pending owner
private input. No migrations/push/deployment. Earlier100 stop is superseded only
by this owner-authorized private credential-entry step, not a successful login.

Reference:[Render environment-variable navigation](https://render.com/docs/configure-environment-variables).

## Current100: authentication rejected; do not blindly reopen

Second owner attempt20261019T074829Z reports **password authentication failed**.
The endpoint was reached; this is not a certificate or dump-version failure.
Code passes the raw password as a driver keyword without shell/URL encoding,
trimming or substitution. Tests confirm exact preservation of special characters.
The log cannot distinguish a wrong entered password from a mismatched credential/
account pair. No valid credential was retained. Do not reset credentials or
change provider settings.

| Check | Result |
| --- | --- |
| Connectivity/TLS | Prior TLS1.3 certificate/hostname check passed; latest attempt reached server authentication |
| Authentication | FAILED:server rejected login |
| Permissions/schema compatibility | NOT CHECKED:authentication blocked SQL |
| Backup tools | Native dump/dumpall/restore17.11 verified; same major as reported17.6, not reached by failure |
| Incomplete export | None:only encrypted CA/error log, no dump/roles/archive or success status |
| Preservation | All failed runs and previous helper/launcher versions retained |

Corrected prompt flow:one private DB password attempt; login, identity and initial
read-privilege checks first; only then request the archive passphrase. No automatic
retries or resets. Three new mocked tests pass:raw credential preservation, failed
login skips archive prompts/exports, prompt order. No production retry or repeated
setup tests. Previous helpers remain as `.before-auth-fix` copies outside Git.

**Backup not reopened**, respecting the instruction to confirm the fix first.
Essential next step:owner locates the existing database password privately in
their password manager or existing backend connection configuration. This is not
the Supabase website password or an API key. Never paste credentials, full URLs
or logs into chat; do not read dotenv files or reset passwords. Successful private
authentication is still required to check permissions and run the backup.

## Current99: TLS trust failure corrected; owner retry pending

Owner's failed run20261019T073609Z stopped at certificate verification before
authentication or SQL/export. Metadata shows only the encrypted public CA bundle
and protected error log; no dump/roles/archive. All files preserved. The initial
metadata-inspection command had a local PowerShell parse error; corrected before
reading diagnostics, with no file or database changes.

The helper trusted only Windows public roots. Supabase publishes its own CA;
official dashboard configuration independently confirms its HTTPS distribution:
[official source](https://github.com/supabase/supabase/blob/master/apps/studio/hooks/custom-content/custom-content.json).
Downloaded only that public certificate outside Git. Verified CA constraints,
signing usage, self-signature, validity(until2031-04-26) and DER SHA256
`807025ad50d4ed219d2c9c7d299c004f824eb00cf7f65afef607d07b72e6cafa`.
No Windows trust-store/provider setting change. Prior helper/launcher retained
as `.before-ca-fix` copies. New code trusts the pinned official CA per run,
keeps `verify-full` for psycopg and native dump clients, and rejects missing,
malformed/private-key or mismatched CA inputs before asking for credentials.

Three new CA regression tests pass; no repeated setup/PG/7z suites. One
credential-free driver probe was inconclusive(CONNECTION_OTHER), not a successful
database connection. A subsequent PostgreSQL SSLRequest-only probe passed
TLS1.3/certificate/hostname verification with the official CA. No database startup
packet, credential or SQL was sent in that handshake. Actual authenticated
backup still awaits owner execution. Corrected private prompt reopened(process69520).
No customer records read by Codex, deletions, migrations, push or deployment.

Follow-up98:owner accidentally closed the prompt. Metadata-only inspection found
no surviving backup process, run folder, archive or saved result. No incomplete
export files found or deleted. Reviewed helper hash unchanged; same launcher
reopened in visible PowerShell(process69720), awaiting private input. No repeated
setup tests or verified actual backup/restore result.

## Current evidence

Owner explicitly approved the actual Supabase read-only backup and protected
isolated restoration after confirming the second recovery copy. Its saved report
confirms matching retrieved ciphertext and owner-confirmed restricted Drive
sharing; remote permissions were not independently queried. No repeated setup
tests, real source connection, customer export, upload, migration or deploy by
Codex. Visible owner PowerShell launcher opened (process42268) for private input;
actual connection/export results are not yet observed. Database restoration NOT RUN.

## Owner action

Current100:do not restart until the correct existing DB credentials are located
privately. The command below remains the approved owner procedure for that step;
no new window has been opened. Never run overlapping copies.

```powershell
& "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Start-PriceYardEncryptedBackup.ps1"
```

Enter the **existing Supabase database password** privately. Only after successful
login/identity/initial permission checks enter a **separate archive passphrase**
twice. Use at least24 printable English/ASCII characters
from your password manager (for portable 7-Zip recovery); keep it separately from
the archive/Drive account. Type `BACKUP` when asked to start. Hidden prompts show
no characters; this is normal. Never paste passwords or private logs into chat.
Do not reset credentials or bypass execution policy if the command is refused.

Reply **BACKUP CHECKED** on success or **BACKUP STOPPED** on failure. This is an
execution handoff for private credential entry, not another setup/approval request.

## Scope and safeguards

The launcher and Python helper are outside Git in the private backup root, as are
their four new guard-test results. The launcher pins the owning SID, private root
ACL, existing EFS folder/key and the exact reviewed Python SHA256:
`022c422185575bfbb1fafcc38a59f6641668e4041fffc9830e999b2f25cc792b`.
This supersedes the earlier hashes; previous helper versions remain preserved.

- Reuses PG17.11/7-Zip26.04 and existing installed psycopg3.3.6; no installs or app
  imports/dotenv reads. The driver's existing libpq18 is only a connection client;
  dump/restore tooling remains17. Four fabricated guard tests pass:noninteractive
  run cannot connect; wrong identity/version/TLS/read-only/revision rejected;
  inherited libpq settings excluded; no shell/password interpolation.
- Source pinned to supplied Session pooler5432, project-qualified user and postgres
  database. Validates TLS with `verify-full` against the pinned official Supabase CA;
  stops on certificate/trust failures, never downgrades TLS. Ignores inherited PG
  service/host settings. Password only in local memory/child environment, never
  arguments/history/files; same-account process memory remains a host risk.
- Read-only repeatable-read transaction; expected17 server and0021 revision.
  Bounded statements/locks/connect/process timeouts, no parallel workers. Shared
  table locks can briefly delay DDL, never block normal customer row writes.
- Full custom-format dump, roles without passwords, private object inventory and
  same-snapshot table counts/SHA256 fingerprints. Foreign tables/materialized
  views stop for coverage review. Permission errors stop; no silent schema skip.
  Roles/global state and sequences are not MVCC-atomic; post-snapshot writes must
  be reconciled. No database backup can include external Storage file bytes,
  provider settings/secrets or external encryption root keys automatically.
- All plaintext exports/logs/TEMP/decrypted copies remain in a fresh EFS folder.
  Portable AES256/header-encrypted archive goes into private EncryptedArchives
  outside EFS so certificate loss does not prevent archive recovery. Checks 7z
  integrity and byte digests after independent decryption inside EFS. No upload.
  EFS is not whole-disk/pagefile/crash protection; earlier limitations still apply.
- Errors retain protected files and private diagnostics, print only a safe status.
  No deletion, migration, role alteration or production settings change. Initial
  launcher preparation path-variable error was corrected before any execution.

## Restoration follows the real inventory

After owner execution, inspect only non-secret status and necessary protected
schema/extension metadata; do not read customer rows/password hashes. A successful
archive check is **not** a verified database restoration. Do not execute arbitrary
dump SQL, restored network functions/subscriptions/jobs or role grants blindly.

Prepare a NEW local17 target inside EFS, isolated from source/providers, with one
bounded worker and no application startup/scheduler. Review Supabase-managed
extension dependencies, required roles and dump coverage first. Stop and report
unavailable dependencies or isolation controls rather than omit records or claim
full recovery. Restore with fail-on-error; compare same-snapshot row digests,
schema/constraints/indexes/roles/grants and sequence state. Keep the baseline
unchanged. Database restoration and0022 clone compatibility are still unverified;
no migration may run under this instruction.

References: [PG17 pg_dump](https://www.postgresql.org/docs/17/app-pgdump.html),
[libpq TLS verification](https://www.postgresql.org/docs/17/libpq-ssl.html),
[Supabase logical recovery and managed-object limitations](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore).
