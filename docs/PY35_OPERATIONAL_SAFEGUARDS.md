# PY-35: the three remaining operational safeguards

2026-10-21: application remains live; **35/36 complete, PY-35 partial**.
Only the requested operational safeguards were implemented. No production change,
new export, repeat restoration, migration, new service or expense was made.

| Safeguard | Verified locally | Still required for completion |
| --- | --- | --- |
| Automatic payment recovery | Strict short-lived GitHub identity; existing purchase verification and PostgreSQL lock; 25-record pages; encrypted resumable position; no new charges | One backend-only deployment, enable public activation flags, successful real workflow run |
| Essential failure alerts | Bounded API/frontend checks; independent GitHub failure notification; controlled failure contacts no production service | Owner saved Actions email settings; actual controlled failure email must still be received |
| Regular encrypted backups | Existing PG17/EFS/AES-256 core preserved; revision0022 guard; Windows-account-encrypted private enrollment; one daily owner task, no overlap, bounded runtime | One hidden private enrollment, task registration and first successful scheduled run |

New tests: **12 backend + 21 scheduler + 10 backup = 43 passed**. Additional
source-only checks accepted0022 and rejected six fabricated identity mismatches;
actual Windows owner/ACL/EFS/key/DPAPI/job-lifetime checks and PowerShell syntax
passed. Existing backup/restoration, payment, Google and release evidence was reused.

## Exact activation change, not yet applied

Publish the reviewed operational commit and deploy **only `priceyard-api`** using
its existing pip-only build. No frontend deployment or database migration. Merge
only `OPS_RECOVERY_ENABLED=true` into existing backend environment; retain all
other variables and secrets. Retain secure64a3290/backend deploy
`dep-dbc17ocs728c73dkqn9g` for rollback; keep production revision0022 and data.

After backend verification, set the public GitHub Actions repository variable
`PRICEYARD_OPERATIONS_ENABLED=true`. Until then scheduled recovery is gated off.
No database, Paystack, email or long-lived application secret goes to GitHub.
Run one real bounded recovery and one controlled alert simulation. Record their
actual outcomes and receipt, rather than calling prepared code operational.

If activation fails, leave the GitHub variable false; pause any running job.
Disable the backend flag and use the retained secure deployment if necessary.
Never downgrade0022, erase payment evidence, reset subscriptions or replay charges.

## Existing Windows and Drive backup arrangement

Copy the reviewed adapter into the existing protected backup folder outside Git.
One visible private enrollment uses the existing Render DATABASE_URL and a separate
archive passphrase, both hidden. Only DPAPI CurrentUser ciphertext is retained
inside EFS. No connection/export occurs during enrollment. Keep the passphrase
and previously verified encrypted EFS recovery copy separately.

Register the daily20:00 local task, starting at the next future occurrence. It
needs this Windows user logged in, the computer powered/online and the existing
direct endpoint's working IPv6 route. Missed runs catch up; two hourly retries,
one worker and a ten-minute limit prevent overlapping runaway work. Observe the
first scheduled result; do not repeat the completed manual backup/restore.

Drive is **browser only**, folder **PriceYard Private Backups**. No new software:
manually upload a checked encrypted archive and checksum there periodically,
for example weekly. Existing protected archives and the verified Drive copy stay.
Automatic off-device copies and always-on backup coverage are not claimed.

The owner's latest instruction says **do not change production**. Production
activation is therefore pending approval; do not publish to master, deploy,
enable the schedule or claim36/36 merely because local tests passed.
