# Minimal backup/release status - 2026-10-19, batch94

Owner rejects partitions, resizing, virtual disks and unrelated infrastructure.
Those proposals are superseded. Keep existing PG17/7-Zip/GitHub/Render/Supabase.
No production backup or release success claimed.35/36 complete; PY-35 partial.

## New work actually verified

Existing Windows Pro/NTFS supports EFS (NtfsDisableEncryption=0). Used built-in
cipher /e on ONE NEW empty folder outside Git:
`C:\Users\HP\AppData\Local\PriceYardPrivateBackup\PrivateRestoreEfs`.
Windows manages a per-user EFS key/certificate. No key read/exported or recovery
password requested; no existing folder re-encrypted or disk setting changed.
New fabricated file inherits encryption and reads back correctly. Source:
[Microsoft cipher](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cipher).

Verified ONLY the newly relevant encrypted-filesystem restore compatibility.
Reused previously passed fabricated17 dump/roles/snapshot; did not rerun export,
7-Zip suite or full application tests. One new fixed local17 cluster55452,
system identifier7698190245493700556, inside EFS, SCRAM,12 connections/32MiB buffers,
fsync/checksums. Five tables/10 rows/schema/constraints/indexes/sequences/roles/
grants match. All1,302 generated database/log/temp files have Windows EFS encrypted
attributes; TEMP/TMP are inside encrypted workspace. Checksum check passes;
cluster stopped. Only fabricated data was used. All scripts/results outside Git:
`PrivateRestoreEfs\pg17-efs-check-20261019\efs-restore-results.json`.

EFS protects file contents at rest, not the whole host/pagefile/crash storage or
an already signed-in compromised account. Do not claim full-disk protection or
zero possible host-memory remnants. No customer data processed; actual source
coverage and encrypted workspace/key-recovery acceptance still required.

GitHub connector read-only get_repo/search_branches succeeded:
fidelisnguakaaga20/priceyard, public, default master; caller permissions include
pull/push/admin. This removes the unverified repository-access prerequisite; it
does NOT authorize writes. No push/fetch/merge/deployment or repository settings
change. Render service references/config remain owner-reported, not independently
queried. No Render/Supabase operator connection established.

## Minimum immediate owner actions

1. Back up the EFS certificate/key privately. Open PowerShell as your normal
   Windows account and run the command below. Confirm the Windows prompt and
   choose its protection password locally; never send password/key/PFX here.
   If the target exists, cancel rather than overwrite it.

   ```powershell
   cipher /x:"C:\Users\HP\AppData\Local\PriceYardPrivateBackup\PrivateRestoreEfs\FABRICATED_ONLY_encryption_probe.txt" "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\EFS-Recovery"
   ```

   Report success/error text only. Keep the password-protected PFX privately;
   keep its password separately in a trusted password manager or on safe paper.
   Recovery file needs a separately controlled copy, not only this PC, before
   disaster-recovery acceptance. Do not upload/share it under current authority.
   Its private-key/password validation must be operator-local, no secret chat.
2. In Supabase priceyard > Connect > Session pooler, provide ONLY host, port,
   database name and username. Never paste the full connection URL/password/API
   key. Do not reset credentials. Existing password and real backup passphrase
   must be entered only at the reviewed owner-operated local native prompt.
   No .env or production credential store was opened. Actual DB access absent.

These are genuine access/recovery prerequisites, not another tool installation.
No additional project, service, purchase, partition or disk-format task is needed.

## Shortest safe actual backup sequence once prerequisites are supplied

- Pin project lrvpjfbtmftjkzaxbunk, connection endpoint/TLS trust, role and17.6
  source; perform bounded read-only metadata/privilege review. Use17.11 tools.
  Choose consistent snapshot and verify full applicable schema/data/roles/grants/
  extension coverage; no silent exclusion of required provider-owned objects.
- Write any export, role file, manifests and temporary logs ONLY within verified
  EFS directory. Build7z AES-256/header-encrypted archive with the owner's native
  private password prompt. Do not use plaintext password arguments or chat.
  Copy only ciphertext to separate restricted archive storage outside EFS so its
  portability does not depend solely on the Windows certificate. Confirm archive
  integrity/decryption and independently retrievable recovery copy. No upload now.
- Restore actual backup to NEW pinned isolated local17 target entirely inside
  EFS, not the existing synthetic fixtures. Review dump SQL/extensions first;
  block outgoing providers/jobs and preserve source. Compare same-snapshot
  protected row digests, payment/trial/value/security evidence, roles/constraints/
  sequences and raw history; record redacted results only. Stop on any error.
- Only then rehearse0022 on a separate restored local copy, preserve pristine
  baseline and all records, verify security-compatible app rollback. Do not
  downgrade/delete revocation evidence or restore over production. No migration
  has run in this batch and production migration remains unauthorized.

## Genuine remaining release checks

| Requirement | What is missing, without repeating completed local work |
| --- | --- |
| Real backup/recovery | Secure source access, EFS recovery/ciphertext retrieval and actual restored-data equivalence; no real export yet |
|0022 compatibility | Static chain0021->0022 and earlier synthetic preservation pass; actual schema drift/privileges and cloned-backup rehearsal not verified |
| Actual hosted sessions/runtime | Existing Render static/backend origins, API proxy/CORS/Secure cookies, target browser/Google return, clean supported-runtime install and fresh advisory evidence; no authenticated host review/test target yet |
| Provider workflows | Actual Paystack TEST checkout/webhook/recovery, Google test login, reset/notification receipt to approved recipients; test credentials/accounts/recipients and approved reachable test endpoint absent |
| Operations/rollout | Accepted backup age/retention/recovery target, scheduler/monitor/alert operator, historical exceptions and compatible rollback artifact; no live job or repair enabled |
| Deployment control | Backend master Auto-Deploy On Commit and build-time alembic upgrade head remain enabled per owner. Before eventual release, approve separating build from explicit migration and controlling auto-deploy; do not change settings or publish now |

Existing repository access and completed307 backend/five PostgreSQL/focused browser
evidence are reused, not blockers requiring repeat. Existing providers can be used;
no new cloud resources are automatically required/authorized. Provider/host tests
still cannot be replaced by local mocks. RELEASE_GATES.json stays unrun/release
false until actual gate evidence exists; no production access/backup/migration,
customer data, upload, push, merge or deploy in this batch.
