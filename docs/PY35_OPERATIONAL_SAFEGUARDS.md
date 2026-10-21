# PY-35: the three remaining operational safeguards

2026-10-21: application remains live; **35/36 complete, PY-35 partial**.
Owner approved activation after the prepared commit. Backend-only rollout,
automatic recovery and delivered failure alerts passed. Daily backup is installed
and privately enrolled, but its first execution failed before export; it is
paused pending a working network. No repeat restoration, migration, new service
or expense was made. Exact results: batch-146 operational evidence.

| Safeguard | Verified locally | Still required for completion |
| --- | --- | --- |
| Automatic payment recovery | Backend live atce0ca70; GitHub gate enabled and workflow active; two real runs passed, including persisted checkpoint retrieval | PASS; maintain the existing schedule |
| Essential failure alerts | Controlled failure run39560232468 and its exact matching GitHub email confirmed in approved owner's inbox | PASS; test failure was intentional and contacted no production service |
| Regular encrypted backups | Protected enrollment complete; daily20:00WAT limited-owner task registered with guards, no overlap and bounded runtime | First execution failed before export; task paused until current Direct-host DNS/IPv6 network blocker is corrected |

New tests: **12 backend + 21 scheduler + 10 backup = 43 passed**. Additional
source-only checks accepted0022 and rejected six fabricated identity mismatches;
actual Windows owner/ACL/EFS/key/DPAPI/job-lifetime checks and PowerShell syntax
passed. Existing backup/restoration, payment, Google and release evidence was reused.

## Exact activation change, applied with owner approval

Reviewedce0ca70 was published and **only `priceyard-api`** deployed using its
existing pip-only build. Deployment `dep-dbc68a5g1s2s7396tnog` is live. No frontend
deployment or database migration. Only `OPS_RECOVERY_ENABLED=true` was merged
into existing backend environment; other variables/secrets retained. Secure64a3290/backend deploy
`dep-dbc17ocs728c73dkqn9g` for rollback; keep production revision0022 and data.

After backend verification, the public GitHub Actions repository variable
`PRICEYARD_OPERATIONS_ENABLED=true` was verified. Workflow state is active.
No database, Paystack, email or long-lived application secret goes to GitHub.
Real bounded runs39559936636 and39560074138 passed, including persisted checkpoint
retrieval. Controlled failure39560232468 produced the expected email, independently
verified in the approved owner's inbox at2026-10-21T07:11:41Z.

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

The owner explicitly approved these operational changes. The backup's first run
failed before source export and created no new archive. Both tested connections,
including the owner's correctly selected phone hotspot, lack usable IPv6; Direct
host lookups confirmed Windows DNS11001/no address. The earlier suppressed native
exception is unavailable, so its exact cause is not invented.

The already confirmed IPv4 Session pooler resolves and accepts the enrolled
credentials with pinned verified client TLS, read-onlyON, expected project role,
database, PG17 and revision0022. Its distinct database connection reports
PostgreSQL SSL=false and nonlocal transport. GSS encryption was not checked;
this is not proof all transport is unencrypted. Verified client TLS does not
prove the separate upstream TLS requirement. The existing guard was **not**
weakened and no export was attempted through this route. No provider settings,
credentials or database records were changed by these read-only metadata checks.

Only the new backup task is disabled. Existing archives/Drive copy, protected
enrollment and working recovery/alerts remain. Stop probes and password/network
retry loops. A working IPv6 Direct connection is the unchanged secure path; an
alternative provider-transport trust exception requires a separate explicit
decision. Do not claim36/36 before secure scheduled backup verification succeeds.

Transport references: [Supavisor's separate client and upstream TLS settings](https://supabase.github.io/supavisor/configuration/tenants/),
[PostgreSQL17 per-backend SSL definitions](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-SSL-VIEW).
