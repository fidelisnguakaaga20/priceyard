# Windows-only backup setup - 2026-10-19

Owner requests free local setup with optional encrypted Google Drive copy.
Production access, export, upload and migrations stay forbidden until setup
verification and explicit approval. No services purchased/accounts accessed.

## Verified stage 1

- Windows Professional; approximately209.87 GiB free on C: at inspection.
- VMware bundles7za.exe23.01. No standalone current7-Zip/GPG/age found in checked
  locations/PATH. Do not replace VMware's executable or treat it as a verified
  backup tool. Standard PostgreSQL installation is18, not17.
- BitLocker tools exist, but C: protection status was unavailable with current
  privileges. No recovery keys requested or encryption settings changed.
- Created empty `C:\Users\HP\AppData\Local\PriceYardPrivateBackup` outside Git:
  current user/SYSTEM FullControl only, inheritance disabled, ACL verified.
  It is NOT encrypted; no customer data or password/key saved. ACLs do not prevent
  an administrator taking ownership or replace encryption.
- No downloads, installs, database processes, exports, restores or uploads.

[Creation script](../tools/local-test/prepare_private_backup_folder.ps1) creates
the fixed folder with its private ACL at creation. Existing targets/redirected
parents cause refusal; do not rerun/reset its permissions. Successful execution
used the owner-authorized outside-workspace location. Evidence:batch-91-private-folder.json.

## Stage 2 verified: archive encryption - 2026-10-19

Owner installed standalone7-Zip26.04 x64. Executable/DLL version and hashes
recorded privately; startup works. Authenticode reports NotSigned, so these hashes
are local inventory, not independent publisher attestation. Official7-Zip site
lists the same version; no execution policy or signature restriction changed.

Eight sequential synthetic checks PASS with installed7z.exe:archive creation,
missing/wrong password listing denied, missing/wrong extraction denied, correct
listing, correct archive integrity and correct extraction.7z reports7zAES and
Encrypted=+; headers/names stay unreadable without the password, and the literal
test filename is absent from archive bytes.146 fabricated bytes restore exactly;
archive401 bytes. One worker/1MiB dictionary/15s per-command timeout.

All runners, fabricated source, archives, failed/successful extraction folders
and JSON evidence stay OUTSIDE Git under
`C:\Users\HP\AppData\Local\PriceYardPrivateBackup`.
Successful result:`encryption-check-20261019-verified\encryption-results.json`.
Temporary random test password generated in memory, supplied on redirected stdin,
never in process arguments/logs/files, never requested from the owner and not
retained. Thus this disposable archive is a test artifact, not a reusable backup.

Initial harness incorrectly supplied bare `-p` on read operations:7-Zip treated
that as an explicit empty password instead of prompting, so the correct-password
stage failed. Preserved the original fixture/runner and one tiny diagnostic probe.
Corrected read invocation uses the private password prompt; all eight checks pass.
No security restriction bypass or ACL weakening. Initial sandbox read denial for
the private folder was handled through normal authorized outside-workspace access.

Archive encryption functionality is READY for the scoped setup. Full real-data
backup setup is NOT ready:PG17 missing, disk encryption/protected restore storage
unverified, source access/scope and actual restoration still pending. No Supabase,
customer export, upload, database commands, migration or deployment occurred.

## Earlier installation instruction (completed)

Open https://www.7-zip.org/download.html and install the current64-bit x64 Windows
version (official site currently lists26.04). It is free. Tell Codex when installed;
do not send any password/key. No tool was downloaded/installed by this stage.
Source:[official7-Zip](https://www.7-zip.org/).

The tiny invented-file encryption/decryption drill above is complete. Archives
must use7z/AES-256/encrypted filenames, with the
password entered privately in the native UI/prompt, never chat/scripts/process
arguments. Use low compression, one worker and bounded memory. Compression or
pg_dump custom format alone is not encryption.

## Remaining setup before actual data

Stage93 update:owner confirmed C: BitLocker OFF. Portable PostgreSQL17.11 tools
and a five-table/ten-row encrypted fabricated backup/independent restoration pass.
Both sequential local17 clusters are stopped. Existing18 untouched. Actual
customer data remains prohibited on these unencrypted fixtures; an owner-admin
encrypted workspace/host protection step is still required. Results/next click:
[PY35_PG17_SETUP_RESULTS.md](PY35_PG17_SETUP_RESULTS.md). Do not repeat setup tests.

1. Owner checks **Control Panel > System and Security > BitLocker Drive Encryption**;
   report only On/Off/Unavailable, never recovery keys. Do not automatically enable
   or reconfigure whole-drive encryption. If off, review a small encrypted local
   workspace/container separately. Decrypted exports/restored data require protected
   storage; an ACL directory alone is insufficient. Do not assume deleting SSD
   plaintext establishes secure erasure.
2. Obtain PostgreSQL17 binaries through the
   [official Windows route](https://www.postgresql.org/download/windows/).
   Review download targets/provenance; prefer separate binaries if practical, no
   auto-start service, preserve18. No Docker needed. Tools are not installed yet.
3. Prepare a NEW local17 cluster on approved encrypted/private storage, separate
   from production/synthetic18:loopback-only, unique checked port, egress/jobs
   disabled,12 connections/32MiB buffers, fsync, one phase at a time, stopped afterward.
   Never cloud-sync/track its data directory. Verify setup with synthetic inputs
   only:encryption/wrong-password handling, decrypt/integrity and17 dump/restore.
4. Obtain explicit approval before source-pinned read-only export and actual
   isolated restoration. Private local password entry; no production password
   reset or secrets in history/chat, and no synthetic-only harness pointed at
   production. Scope:[PY35_MANUAL_BACKUP.md](PY35_MANUAL_BACKUP.md).

## Password and second copy

Use a unique long random passphrase kept in a trusted password manager, or on
paper stored safely away from the computer. Confirm it with a local decryption
test. Keep recovery access separate; never put it in Git/chat/the backup folder
or beside the archive in Drive. Machine-bound encryption alone is not portable
disaster recovery.

After upload approval, manually upload ONLY the verified encrypted archive to
existing Google Drive, within available free quota. Enable two-step verification;
sharing stays Restricted. Do not sync the whole workspace, plaintext, keys or
database clusters. Confirm custom sync rules exclude private local data first.
Download the second encrypted copy into protected storage, compare ciphertext
digest and verify decrypt/retrieval. No Drive access/upload/quota checked; no paid
upgrade assumed. Actual backup acceptance still requires consistent snapshot,
roles/permission coverage and verified restoration.35/36 complete/PY-35 partial.
