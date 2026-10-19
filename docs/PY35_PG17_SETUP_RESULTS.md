# PostgreSQL17 setup and fabricated recovery results - 2026-10-19

**PG17 tools and fabricated round trip pass. Real customer restoration remains
blocked by encrypted workspace setup.** Owner confirmed C: BitLocker OFF.
No Supabase connection, customer export, application migration, upload or deployment.

## Tools obtained and verified

Official PostgreSQL Windows page links to EDB's portable binary archives.
EDB's17.11 Windows link resolved to:
https://get.enterprisedb.com/postgresql/postgresql-17.11-5-windows-x64-binaries.zip

Installed outside Git under
`C:\Users\HP\AppData\Local\PriceYardPrivateBackup\pg17-tools-17.11-5\pgsql`.
postgres/initdb/pg_dump/pg_restore/pg_dumpall/psql all report17.11. Same major17 as
production17.6; production version unchanged. No Windows service/PATH change,
Docker, pgAdmin install or alteration of existing18. Tools are free.

Vendor archive381,531,864 bytes. Full download was stopped deliberately after
83,886,080 bytes to avoid unnecessary transfer. Reused that prefix plus12,433,112
bytes of validated HTTPS vendor range requests, extracting only bin/share/lib:
1,591 entries/140,784,906 uncompressed bytes. Member traversal/link/size guards and
all selected ZIP CRC checks pass. Partial ZIP retained, clearly incomplete:do not
treat it as an installable complete archive. Local executable SHA256 inventory
and download metadata stay private. Executables are unsigned; TLS vendor source,
CRC and local hashes are not an independent vendor-signature certification.

## Verified fabricated-only rehearsal

All scripts, fixtures, archives, logs and JSON results are OUTSIDE Git under the
private folder. Successful report:
`pg17-synthetic-recovery-20261019-verified\recovery-results.json`.

- Two NEW independent clusters, run sequentially:source55450/system identifier
  7698187604558926520; restored55451/7698187654120614004. Paths pinned in report;
  server version/data-directory/listener identity checked before fixture actions.
- Literal127.0.0.1 listeners, generated synthetic SCRAM credentials,12 connections,
 32MiB shared buffers/16MiB maintenance/1MiB work memory, fsync enabled, data checksums.
- Five fixture tables,10 fabricated records covering accounts/security version,
  historical prices with unknown measurement, trial/paid dates, successful/pending
  payment references/amounts and audits. No live/customer records or app migrations.
- Custom-format fixture schema/data dump and role-only export without passwords.
  Source snapshot unchanged. Dump stage0.903s; later restore0.403s (not full RTO).
- Verified7-Zip encrypts roles, dump and snapshot manifest with AES-256/header
  encryption. Missing password cannot list contents. Correct decrypt/integrity
  checks pass; all three decrypted artifacts match their originals byte-for-byte.
- Restored roles into the SECOND cluster, then schema/data into its empty database
  with fail-on-error/single transaction. All rows/types/defaults/constraints/indexes/
  sequences/ownership/role attributes/grants match. Reader has SELECT, not INSERT.
- Both clusters stopped normally; offline pg_checksums validation passes on both.
  Independent pg_ctl status confirms stopped, including the retained failed fixture.
  No active new native server remains. Original18 instances were not stopped/touched.

This is a five-table fabricated fixture, not an actual21-table application restore,
Supabase-managed-service validation, live schema compatibility or migration proof.
No firewall/OS egress policy was changed; no claim that an untrusted future dump
would be safe to execute without additional isolation review. Real source schema,
extensions, provider objects and backup scope still require approved review.

Temporary synthetic archive/database passwords generated in memory, no real
passphrase requested. Archive password stdin-only; synthetic DB password provided
only to child libpq environment and a temporary private initdb input file removed
immediately after initialization. Not saved in reports/command arguments/history.
These disposable credentials are not a real backup recovery mechanism.

## Corrected setup issue retained

Initial pg_ctl startup successfully launched the synthetic source, but inherited
Windows output pipe handles kept Python communicate waiting past its timeout.
Verified exact executable/data directory/PID before stopping only that source.
Retained its empty source fixture. Corrected pg_ctl output to private file logging
and registered cleanup even after startup errors. One bounded retry above passes;
no overlapping native servers, application regression repetition or mass cleanup.

The private root contains PG17_SYNTHETIC_ONLY.txt:all these clusters are on
unencrypted C: and must NEVER receive customer data. No original files deleted.

## Remaining protection step - owner-operated Windows administration

The session is not Windows-administrator, so it cannot safely create/mount and
BitLocker-encrypt a new virtual volume here. Do not weaken existing folder ACLs
or put actual exports/data on C: then encrypt/delete them afterward.

Proposed free built-in option:one NEW1GiB VHDX file under the private folder,
encrypted with BitLocker before any real data, separately labelled for PriceYard.
Do not repartition/format C: or any existing physical disk, or enable whole-C:
encryption automatically. Exact disk identity, new filename/drive letter and
encryption/recovery-key handling must be reviewed in the owner-admin session.
Until then this is a proposal, not a created encrypted environment.

Next owner action only:open Start, type **Computer Management**, choose
**Run as administrator**, then **Storage > Disk Management**. Report that it is
open. Do not initialize/format anything or create a virtual disk yet. Any Windows
administrator credential stays in Windows' prompt; never send it in chat.
References:[Microsoft virtual disks](https://learn.microsoft.com/en-us/windows-server/storage/disk-management/manage-virtual-hard-disks),
[BitLocker](https://support.microsoft.com/en-us/windows/security/encryption/bitlocker-drive-encryption).

Before real use, verify encrypted-volume identity/unlock/lock/recovery, place ALL
data/log/temp/export/restore paths there, and review host temporary/pagefile/crash
storage. A volume container alone does not prove absence of sensitive remnants on
an unencrypted host. If the owner requires strict no-plaintext-anywhere-at-rest,
resolve host protections or select a suitably encrypted restore machine before
customer data is processed. No such OS reconfiguration is authorized/performed.

## Real passphrase

Generate a unique long random backup passphrase in a trusted password manager,
or record random words safely on paper away from this PC. Enter only in native
7-Zip UI/private prompt. Never give it to Codex or put it in scripts/arguments/
Git/cloud folders. Keep the encrypted-drive recovery key separately recoverable
and private; do not rely solely on a file inside that same locked drive. Verify
decryption/recovery locally before backup acceptance. Google Drive second copy
remains optional and requires upload approval; only encrypted archives may go.

Progress35/36 unchanged; PY-35 partial. Tools verified, real-data workspace and
actual encrypted backup/restoration NOT ready. No production approval inferred.
