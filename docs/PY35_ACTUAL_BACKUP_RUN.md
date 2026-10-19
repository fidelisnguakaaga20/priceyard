# Actual encrypted backup - owner-private execution, batch97

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

Use the opened PowerShell window. If it did not appear, open normal Windows
PowerShell and run (do not start another copy while the first is running):

```powershell
& "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Start-PriceYardEncryptedBackup.ps1"
```

Enter the **existing Supabase database password** privately, then a **separate
new archive passphrase** twice. Use at least24 printable English/ASCII characters
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
`8d716edc9dcfc12571cc606a0a9d82c4c528c134735e8c9049c50212525b3c3c`.
This supersedes the initial Windows-root-only helper hash recorded in batch97.

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
