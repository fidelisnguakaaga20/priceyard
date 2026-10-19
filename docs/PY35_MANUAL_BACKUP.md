# PY-35 manual backup preparation - production not accessed

Current batch97 supersedes historical setup blockers below. Owner completed
encrypted key export and separate private Drive retrieval/hash comparison, then
explicitly authorized the actual read-only backup/isolated restoration. Tools and
EFS setup already verified. Prepared owner-only command uses private prompts;
has NOT connected/exported yet. See [current execution step](PY35_ACTUAL_BACKUP_RUN.md).
No new approval for migrations, pushes or deployment. No recoverable-backup claim.

Owner-confirmed source:Supabase `priceyard`, reference
`lrvpjfbtmftjkzaxbunk`, Free plan, no managed backups. No successful backup,
restore or complete production compatibility check is claimed. All nine live release
gates stay open;35/36 checklist items complete. Latest request authorizes preparing
the manual backup/recovery workflow, with an explicit stop before production
access if access/approval is required. No authenticated database access is set up.

Owner chose free Windows-local storage with optional encrypted Google Drive copy.
Initial tool/folder inspection completed2026-10-19; empty ACL-protected folder
created outside Git, NOT yet encrypted. PostgreSQL17/encryption/restore setup
remain incomplete. Next:[PY35_WINDOWS_BACKUP_SETUP.md](PY35_WINDOWS_BACKUP_SETUP.md).
No actual export/upload/restoration approved before setup verification.
Stage92:owner-installed7-Zip26.04 starts; eight invented-file AES-256/header/
missing-and-wrong-password/correct-restore checks pass. All artifacts and test
password handling stay outside Git; no real password used. Archive encryption
ready, but PG17 and encrypted local restore storage remain unverified.
Stage93 supersedes PG17-tool absence:portable17.11 version checks and fabricated
encrypted backup/independent local restore pass. C: BitLocker OFF, so actual
customer-data storage/restore remains blocked; synthetic fixtures cannot be reused
for customer data. See[PY35_PG17_SETUP_RESULTS.md](PY35_PG17_SETUP_RESULTS.md).
Current94:owner rejects new disks/partitions. Existing Windows EFS now protects
a new private folder; a focused PG17 fabricated restore verifies encryption of
all database/log/temp files. EFS certificate recovery and secure Supabase access
remain pending, so actual customer backup is not yet performed. Current concise
scope:[PY35_MINIMUM_BACKUP_RELEASE.md](PY35_MINIMUM_BACKUP_RELEASE.md).
Current95:source endpoint/user now supplied without password. EFS encryption/ACL
rechecked; no PFX found at instructed locations. Prepared owner-local recovery-key
helper and six fabricated validator checks; owner must run it privately before
any production access. No new installations/tests of already-passed DB workflows.
Next:[PY35_CONNECTION_AND_KEY_CHECK.md](PY35_CONNECTION_AND_KEY_CHECK.md).

## Owner-reported inspection results - 2026-10-19

Owner reports successful execution of the prepared inspection:PostgreSQL17.6,
database14 MB, installed revision0021_feedback_screenshot. Exact project reference
and Free/no-managed-backup status reconfirmed. Codex has not connected or received
the complete schema/extension/grant inventory. Do NOT repeat the completed first
inspection just to obtain the same three values. Retain the remaining metadata
privately; request only the missing details needed for the next compatibility step.

Static AST review of22 local migration files confirms a single head,
0022_login_revocation, directly following0021_feedback_screenshot. Compared with
preserved master,0022 is the only added migration; earlier migrations are unchanged.
The exact upgrade adds:

- `public.users.auth_version`:integer, NOT NULL, server default0.
- `public.revoked_access_tokens`:token_hash varchar64 primary key, required user_id
  referencing users.id with ON DELETE CASCADE, required timezone-aware expires_at
  and revoked_at, indexes on user_id and expires_at.

No upgrade step deletes/replaces customer rows or rewrites prices, plans, paid/
trial dates, payment evidence or historical records. This is source inspection,
not proof that production's actual columns/types/constraints match its revision.
Check for drift, existing duplicate objects, privileges and extension dependencies
before migration. ALTER operations can wait on locks; a reviewed bounded change
window and transaction/timeout policy still need to be established. Do not rerun
0001-0021, reset, stamp or edit installed revision metadata.0022 downgrade refuses
because dropping revocation evidence can re-enable revoked credentials. Application
rollback must be a tested security-compatible artifact, not assumed old-master.

The machine's standard PostgreSQL installation is18. Version18 pg_dump can read17,
but its output is NOT guaranteed to restore into17. Prefer current PostgreSQL17
client tools and a separate17 local restore server for a recovery target matching
production; obtaining these tools is pending, not authorized installation. Keep
existing18 synthetic tests intact. A successful18-only restore is not evidence
that17 recovery/migration compatibility has passed. No database version upgrade
is proposed. Reference:[pg_dump version compatibility](https://www.postgresql.org/docs/18/app-pgdump.html#APP-PGDUMP-NOTES).

### Next stage only: establish protected backup storage

Owner confirms whether an existing encrypted drive/volume is available OUTSIDE
the repository and cloud-synced folders, and provides only its non-secret folder
path/encryption type. Do not create plaintext database dumps or a customer-data
restore cluster on an unprotected volume. Keep encryption recovery credentials
separately and private; plan a separately stored encrypted copy. If no encrypted
location exists, report that first so a portable encryption method and any tool
installation can be reviewed. No purchase, install, backup or outside-workspace
file creation is authorized by this preparation.

Once storage is approved, arrange17 tools, reviewed restore location and private
password entry, then supply exact source-pinned export commands with failure
checks/encryption and local-only restore controls. No placeholder command is
being executed or presented as a completed backup. Final migration rehearsal
requires its own local-only approval; no production migration is authorized.

## Earlier owner-operated read-only instructions (completed initial stage)

Open the existing Supabase project, confirm the reference above, choose SQL
Editor > New query, paste ALL of [the prepared SQL](sql/PY35_READ_ONLY_PREFLIGHT.sql)
and run it without highlighting a subset. This is for the owner to execute; Codex
has not run it. The transaction is read-only, statement timeout5s/lock timeout1s,
and ends with rollback. Outputs contain database/migration/catalog metadata only;
no customer rows, secrets, function bodies or column defaults are selected.
If the version table is missing/elsewhere or any query fails, stop and share only
the redacted error. Do not create a table, stamp a revision, reset or migrate.

Those three values were provided2026-10-19; the following requirements remain.
Keep the remaining metadata private for reviewed comparison; do not send a full
dashboard screenshot or connection string. The local reviewed baseline is
`0021_feedback_screenshot`; candidate head is `0022_login_revocation`.0022 adds
users.auth_version and revoked_access_tokens/indexes. It refuses downgrade to
preserve revocation evidence. Neither Render's commit labels nor this prepared
SQL proves production matches those baselines. Read-only constraints/indexes/
grants/RLS/function/dependency review must follow using exact target metadata;
this first inventory is not a final schema compatibility certificate.

## Preferred method after metadata/access and destination review

Use native pg_dump/pg_restore rather than adding CLI/Docker on this resource-limited
machine. Match PostgreSQL17 client/restore tooling as described above; currently
only the standard18 installation was found. No new tools installed.
Choose direct or Session pooler access from the project's Connect panel; not a
transaction-pooler endpoint. Verify host/project identity and TLS certificate
before connecting. Do not reset the production password or change grants.

The approved operator enters the existing database password privately at a local
prompt or approved credential mechanism; never in chat, command arguments, shell
history, environment dumps, source files or a URL logged by tools. If no suitable
access exists, stop for an explicit least-privilege access proposal. Do not reuse
synthetic test harnesses:they must never connect to this project.

Before dumping, owner must identify a private location OUTSIDE this repository,
an encryption/key-recovery method, a separately controlled encrypted copy location,
retention and recovery objectives, plus a separate empty local restore target.
No backup data may be written before protected storage is ready. Use vetted
encryption with portable recovery credentials kept separately; compression and
pg_dump's custom format are not encryption. Any tool installation, outside-workspace
write or additional service requires the normal approval process. Confirm space
and memory budgets before export/restore; no parallel dump or restore workers.

Create one consistent custom-format database archive including reviewed schema,
data, sequence state, functions/triggers, constraints/indexes, ownership and ACLs.
Capture accessible required roles/memberships separately using reviewed
pg_dumpall --roles-only --no-role-passwords or the official CLI role-only export.
Do not silently drop roles/grants, ignore permissions, exclude managed schemas or
claim a complete backup if provider permissions prevent required coverage. Catalog
global state is separate from the database snapshot; avoid concurrent DDL/grant
changes and record any consistency limitation. Preserve source Alembic and any
Supabase migration history. Protect all output with encrypted storage/streams,
check every process exit status and retain private errors without credentials.

## Verification required before saying "recoverable"

1. Record source identity, version, snapshot/time and coverage manifest privately;
   derive bounded row counts/digests from the SAME snapshot for source comparisons.
   Later live reads can legitimately differ:never label new customer activity as
   corruption or overwrite it. Capture ciphertext checksum and source tool version.
2. Retrieve and decrypt the independently stored copy, and validate its archive.
   Restore into the explicitly approved empty isolated LOCAL target only. Actual
   customer data requires private encrypted disk/access controls, no cloud sync,
   no Git/runtime evidence upload, provider egress denied and no scheduled jobs.
   The existing synthetic cluster is not an approved customer-data restore target.
3. Recreate/map required roles and extensions using a reviewed plan. Review dump
   executable objects first; no blind activation of cron/webhook/network extensions.
   Use fail-on-error, one worker and bounded resources. Do not use clean/drop flags
   against existing objects or suppress restore errors. Missing Supabase extensions
   or service dependencies block full restoration acceptance until resolved.
4. Verify protected snapshot counts/digests and all customer/password/security,
   price/unit/source/history, subscription/trial/paid value, payment identifiers/
   amounts/status and audit records. Check sequences/constraints/indexes/grants/
   RLS, detect orphan references and confirm zero ignored restore errors. A plain
   PostgreSQL clone cannot certify Supabase Auth/Storage service behavior.
5. Preserve an unchanged restored baseline. Rehearse ONLY the exact approved
   additive migration on an explicitly approved disposable local copy, never
   production. Verify unchanged business records and compatible application
   rollback without dropping0022 security evidence. This local rehearsal needs
   explicit approval because the owner currently prohibits running migrations.
6. Record private verification results, encrypted-copy retrieval, measured restore
   duration, remaining exclusions and owner acceptance. No raw customer rows or
   password hashes in public evidence. A completed dump alone does not pass.

## Coverage requiring separate handling

- Supabase Storage file bytes (database has metadata only); other uploaded files.
- Provider service configuration, Google OAuth, email/Paystack settings, Render
  environment/secrets, DNS and API/JWT keys. GitHub source is a separate artifact.
- Edge Function source/dependencies/secrets, webhooks, schedules/Realtime setup,
  inaccessible platform-owned roles/objects, and external extension dependencies.
- Vault/column encryption root keys if used:encrypted rows alone may not decrypt;
  inventory key recovery privately before claiming completeness. Never expose keys.
- Database role passwords intentionally excluded; document secure reprovisioning.
- Writes/payments after the snapshot require reconciliation, not blind restoration.

Stop on any coverage/encryption/restore incompatibility. Never restore over live
records, reset production, change Render settings, push/merge or deploy. See
[BACKUP_RECOVERY.md](BACKUP_RECOVERY.md) and [final review](PY35_FINAL_REVIEW.md).

Official references reviewed for this preparation:
- [Supabase logical backup/restore](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore)
- [Supabase backup limitations](https://supabase.com/docs/guides/platform/backups)
- [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)

Results:initial metadata inspection completed by OWNER, with the three results
above; complete schema/grant/extension compatibility NOT VERIFIED. Codex production
connections0. Encrypted export BLOCKED by secure access/storage/tool setup;
restoration NOT RUN; migration rehearsal NOT RUN. No test failure or backup success
is inferred from blocked/not-attempted statuses.
