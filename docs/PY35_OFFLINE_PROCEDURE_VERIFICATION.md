# Offline backup procedure verification — 2026-10-19

**Offline procedure passed. Actual Supabase backup/recovery remains unverified.**
Owner authorized corrections, whole-procedure fabricated testing and a stop before
any new credentials, live connection or actual backup. Application source and
business rules are unchanged. Checklist stays **35/36**; PY-35 remains partial.

## Corrections reviewed independently

- Replace unsupported psycopg3.3.6 `PGconn.ssl_attribute` with supported native
  `ssl_in_use`; do not invent protocol metadata. Preserve `verify-full`, pinned
  CA/hostname, source identity, upstream TLS and read-only requirements.
- Explicit UTF8 connection encoding, tested against a SQL_ASCII role default.
- Correct unsigned Win32 file-attribute return handling; nonexistent, unencrypted
  or reparse locations fail closed. Archive destinations also reject junctions.
- Roll back the initial read-only transaction before waiting for the owner's
  archive passphrase. Start a fresh read-only snapshot afterward and refresh
  identity, inventory, special-object and privilege checks before exporting.
- Capture fuller database/role/settings, sequence and large-object evidence.
  Sequence observations are explicitly non-MVCC and must be reconciled if
  concurrent activity causes a difference; they are not silently ignored.
- Add guarded restoration primitives: reviewed SQL hashes and inventory first;
  new isolated loopback target only; stop on unreviewed provider objects/settings.
  No automatic production target or application migrations.

## Executed evidence

Exact diagnostic and backup `main()` functions used genuine PostgreSQL17.11 TLS,
installed psycopg3.3.6, `pg_dump`, `pg_dumpall --no-role-passwords`,7-Zip AES256
with encrypted filenames, independent decryption and `pg_restore`. Only test
configuration/module loading and fabricated console inputs were substituted.
Python connections and native database environments were restricted to loopback.
No real credential, recovery PFX or production endpoint was used.

| Verification | Result |
| --- | --- |
| Correct login, source identity, read-only transaction and actual driver API | Passed |
| Wrong login, wrong CA/hostname and read-only INSERT attempt rejected | Passed |
| Missing/unencrypted paths rejected by actual Win32 checks | Passed |
| Exact backup main, encryption, independent decryption and file digests | Passed |
| No/wrong password cannot list encrypted filenames or extract data | Passed |
| Tampered bundle rejected before restore | Passed |
| Fresh PG17 restore: 7 fabricated tables, 12 rows, matching row digests | Passed |
| Schema, constraints, indexes, policies, owners/grants, roles/settings | Passed |
| Sequences, large-object contents and unchanged0021 migration history | Passed |
| Native database checksums; both test clusters stopped | Passed; zero bad checksums |
| All2,346 whole-drill plaintext artifacts EFS-encrypted | Passed |
|12 extra checks: provider/executable/settings/target guards and valid bundle | Passed |
| Both launcher syntax checks, hash pins and independent read-only review | Passed |

The11 whole-drill checks and12 additional guard checks passed. Additional cases
reject unknown extensions, functions, foreign servers, subscriptions, publications,
custom tablespaces, unsafe role settings, unreviewed SQL and remote/existing/running
restore targets; a valid reviewed bundle still passes. They create no database
process or network connection.

One source server ran at a time, followed by one restore server:8 connections,
32MiB shared buffers, no parallel restore workers. Initial Windows output-pipe
timeout occurred before the first fabricated source was ready; native control
output now goes to private files. That failed fixture is retained. Successful
evidence is `offline-whole-procedure-20261019T090348Z`, outside Git under the
existing `PriceYardPrivateBackup` folder. Plaintext data is under its EFS folder;
portable fixture output is ciphertext or non-sensitive test summaries only.
Existing keys/recovery copies were reused; no repeated setup or upload.

## Verified private code (SHA256)

These owner-local files and their retained previous versions are outside Git.
They contain no owner credentials. Launcher/helper pins match the verified code.

| File | SHA256 |
| --- | --- |
| Start-PriceYardEncryptedBackup.py | `0c02ac54f42c1f62a47eecbb4d11d6d6315103abddff14c063f77fd68077c2d2` |
| Inspect-PriceYardPooler.py | `15dd3fe79f0ef2496ca107c1817106d3e6195bca8527c8f3de3ca6d10144dd2c` |
| PriceYardRestoreOffline.py | `2f2f568d6fad2969e4389fa99a1faf9e4e1d5b56e7c93dacbb87cdb9080b4ccb` |
| verify_exact_backup_offline.py | `6303c58aa6e2d5db2184b04a6ac264af4c878962cdc24c49f6c2bb16ef9c4484` |

## Remaining boundary

The driver error is corrected and the offline workflow is ready for an explicitly
approved real backup attempt. Fabricated success does not resolve the older
unrecorded pooler source-validation mismatch or prove actual Supabase privileges,
both TLS hops, managed extensions/roles, locale, functions, storage or restore
compatibility. All original guards remain; a real mismatch must stop the process.
Unfamiliar real objects require protected inventory/SQL review before restoration.
The restore helper currently accepts only the reviewed simple offline inventory;
it is deliberately not a universal Supabase restore script.

No real backup, production access, production export, credentials prompt, visible
window, application migration, provider change, push, merge or deployment occurred.
Do not repeat EFS/key/7-Zip/PG17 preparation. **Stop for owner approval.**
