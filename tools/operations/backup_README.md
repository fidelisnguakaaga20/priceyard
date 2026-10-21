# Existing Windows encrypted backup: recurring adapter

2026-10-21 activation: adapter installed outside Git, owner privately enrolled and
daily task registered. The task is **paused** after failing safely before export.
Tested networks lack usable Direct IPv6; existing Session pooler passes client
TLS but fails the unchanged separate database-TLS guard on a nonlocal hop. Do
not weaken that guard or claim a successful daily backup. Enrollment and the
verified original archive/recovery evidence are preserved; no upload occurred.

The immutable existing Direct helper is reused by SHA256. Exactly three entry
changes are reviewed: installed revision0022, explicit enrolled-context guard,
and no credential-bearing command arguments. Its full schema/data/roles inventory,
RLS/private-object coverage, read-only repeatable snapshot, PG17, verify-full,
EFS-only plaintext, one worker, AES256/header encryption and independently
decrypted file checks are unchanged. Old interactive0021 helpers stay untouched.

`backup_windows.ps1 -Action Enroll` is a one-time **visible private console**:
existing Render DATABASE_URL is entered hidden and parsed by the original pinned
helper (same project/percent-decoding rules); clipboard is cleared. The separate
archive passphrase is entered twice. Only DPAPI CurrentUser ciphertext is saved
inside existing owner-only EFS outside Git. Never paste either value into chat.
Keep the archive passphrase and EFS recovery copy separately as already arranged.
Secrets exist temporarily in the signed-in owner's process memory; EFS/DPAPI do
not protect against a compromised account or encrypt the whole disk/pagefile.

After explicit owner enrollment and reviewed installation together **outside Git**,
`-Action RegisterTask -DailyAt 20:00` installs one same-owner daily task. It needs
the owner logged in, computer powered and connected, and the Direct endpoint's
usable IPv6 route. Missed runs catch up; failures retry twice at hourly intervals.
One-instance scheduling plus an EFS lock prevent overlapping recurring runs.
Each task has a ten-minute limit; the Python worker's Windows job kills native
backup children if its process ends. No saved Windows password/admin task/service.
Do not run the old manual helper while the recurring task is active.

Every run rechecks actual owner SID, root/enrollment ACL, EFS/private key, source
hash, purpose-bound DPAPI and the unchanged live read-only source guards. The
environment flag alone grants no access. Missing/wrong protection stops safely.
No cleanup/deletion, database restore, migration or provider-setting change occurs.
All native exports, private diagnostics and verification copies remain EFS-only.
New archives remain in existing `EncryptedArchives` outside Git; a checked archive
is not falsely labelled a newly verified database restoration.

`recurring-backup-status.json` records only aggregate state/check time/last success,
no credentials, customer identifiers, row data, raw errors or private archive paths.
Task Scheduler's nonzero exit reports a failed job; a missing/stale success is a
backup failure even if the PC did not run. This local file is **not** an externally
delivered alert, nor proof of a second off-device copy. No ongoing24/7/RPO promise
is made when the computer is unavailable.

The owner confirmed browser-only Google Drive and the existing private folder
**PriceYard Private Backups**. No desktop software or automatic upload is needed
or configured. After a successful scheduled backup, use Chrome to upload its
checked `.7z` archive to that folder; keep a recent off-device copy, for example
weekly. Upload only checked encrypted archives and their checksum, never EFS
workspaces, plaintext exports, DPAPI enrollment or recovery keys. The existing
verified Drive copy is preserved; setup does not repeat that completed backup.
Existing archives/recovery evidence are retained; retention/deletion is not
silently imposed. Host storage must be monitored (the core refuses <2GiB free).

New scope verification only:

```
python -B tools/operations/test_backup_runner.py
python -B tools/operations/backup_review_source.py --review-approved-source
```

The second command reads **only source**, verifies its fixed hash, compiles only
the identity guard and uses fabricated metadata. No network/database is opened.
Do not repeat the already completed customer-data restore or old crypto suites.
