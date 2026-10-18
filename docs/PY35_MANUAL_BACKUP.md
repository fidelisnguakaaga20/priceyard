# PY-35 manual backup preparation - production not accessed

Owner-confirmed source:Supabase `priceyard`, reference
`lrvpjfbtmftjkzaxbunk`, Free plan, no managed backups. No successful backup,
restore or production compatibility check is claimed. All nine live release
gates stay open;35/36 checklist items complete. Latest request authorizes preparing
the manual backup/recovery workflow, with an explicit stop before production
access if access/approval is required. No authenticated database access is set up.

## Immediate owner-operated read-only step

Open the existing Supabase project, confirm the reference above, choose SQL
Editor > New query, paste ALL of [the prepared SQL](sql/PY35_READ_ONLY_PREFLIGHT.sql)
and run it without highlighting a subset. This is for the owner to execute; Codex
has not run it. The transaction is read-only, statement timeout5s/lock timeout1s,
and ends with rollback. Outputs contain database/migration/catalog metadata only;
no customer rows, secrets, function bodies or column defaults are selected.
If the version table is missing/elsewhere or any query fails, stop and share only
the redacted error. Do not create a table, stamp a revision, reset or migrate.

Provide PostgreSQL version, database size and installed Alembic revision first.
Keep the remaining metadata private for reviewed comparison; do not send a full
dashboard screenshot or connection string. The local reviewed baseline is
`0021_feedback_screenshot`; candidate head is `0022_login_revocation`.0022 adds
users.auth_version and revoked_access_tokens/indexes. It refuses downgrade to
preserve revocation evidence. Neither Render's commit labels nor this prepared
SQL proves production matches those baselines. Read-only constraints/indexes/
grants/RLS/function/dependency review must follow using exact target metadata;
this first inventory is not a final schema compatibility certificate.

## Preferred method after metadata/access and destination review

Use native pg_dump/pg_restore, already present under PostgreSQL18 locally, subject
to actual source version/extension compatibility. This avoids installing the
Supabase CLI and Docker on this resource-limited machine. No new tools installed.
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

Results:read-only production checks NOT RUN; encrypted export BLOCKED by secure
access/storage setup; restoration NOT RUN; migration rehearsal NOT RUN. No test
failure or backup success is inferred from these blocked/not-attempted statuses.
