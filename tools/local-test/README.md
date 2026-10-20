# Local verification only

Owner-approved provider exception,2026-10-20: `provider_tunnel.py` is separate from
the original guard/preview. Its pinned existing fabricated PG17 target, temporary
private HTTPS gateway, TEST-only Paystack key/destination/amount checks, approved
recipient/two-message ceiling and automatic cleanup must remain intact. Only
explicitly selected provider settings are read under the owner's later approval;
application dotenv/config and production DATABASE_URL are never loaded. Runtime
credentials pass in memory/stdin, not command lines or reports. No real backup
contents/customer database is a provider-test fixture. Do not expose preview.py.
The process-only local bootstrap HBA leaves the original cluster HBA unchanged;
it is solely for the positively identified fabricated cluster. Application role
uses SCRAM on literal loopback. No configuration may be applied to another server.

Batch128 real HTTPS/API/reset/email and initialization checks passed; do not
rerun the whole drill. Existing results deliberately prevent automatic repeats.
`provider_rollback.py` completed only the interrupted rollback without another
tunnel/provider request/migration; its result is retained. Browser cache fix has
startup evidence only. Google consent, TEST checkout/provider webhook/replay,
public browser and actual Render deployment-runtime checks remain unfinished.
Check PRICEYARD_PROGRESS.md and docs/PY35_HOSTED_CHECKS.md before any continuation.

This tooling is separate from application startup. Never run the application with
real configuration to test changes. The guard scrubs inherited configuration,
disables dotenv reads, denies external sockets/DNS/native PostgreSQL/children,
and permits only newly created in-memory SQLite engines.

Existing local verification tools are reused from the preserved recovery archive;
no application credentials or new dependency installs are needed. Runtime files,
snapshots and fabricated data are ignored. The preview uses the real API and the
compiled frontend, with a small external testing notice. External links, native
sharing, push permission and service-worker registration are disabled by the
preview wrapper. Production application components are not changed for this.

These process guards do not constitute a virtual machine or certify protection
against malicious native code. Browser verification also blocks external page
requests. Never claim production/provider compatibility from these tests.

The current [coverage map and finite PY-30 criteria](../../docs/TEST_COVERAGE.md)
link executable checks and their evidence. Future regression tests belong with
each remaining improvement; they do not require reopening the testing-foundation
item. The secret-file probe uses a nonexistent sentinel, never an application
dotenv, including when testing a regressed guard.

## Post-restart resource limits (2026-10-17)

2026-10-18: the recovery fixture reached80/80 retained schemas in batch70.
Preserve it stopped, along with the older revocation fixture. New native batches
use `verify_pg_security.py --paging-cluster` against the separately initialized
`runtime/postgres-paging-20261018`, literal127.0.0.1:55449, pinned identifier
7697910732590408300. Same role/database,80-schema cap, exclusive lock and resource
limits below apply. Build reuse refuses this port too. Never raise an exhausted
fixture's budget, delete preserved schemas or change a marker to select a server.

Run heavy phases sequentially. Stop native PostgreSQL before backend/browser
checks; launch one browser check at a time and close it before the next. Reuse a
verified build only after comparing current source hashes. Do not retry full
native suites repeatedly when connection/worker timeouts recur.

The old `runtime/postgres-revocation` fixture is stopped and retained as evidence;
its many accumulated schemas caused excessive file growth. Do not start it on
resume. The recovery fixture at literal127.0.0.1:55448 is also exhausted and must
stay stopped; use the current `--paging-cluster` profile described above. All
profiles keep hard-coded directory/port/system-identifier checks. The ignored
recovery marker records identifier7697651361316763724; no arbitrary cluster is
authorized by editing a marker. Reduced settings used during recovery are
shared_buffers32MB, max_connections12, maintenance_work_mem16MB and
autovacuum_max_workers1. Keep fsync/durability enabled and stop gracefully after
the suite. Never stop the unrelated existing PostgreSQL service.

The native runner rejects overlapping suites via a nonblocking file lock before
database imports. It refuses runs exceeding80 retained synthetic schemas; preserve
that evidence and provision another explicitly pinned empty fixture instead of
deleting schemas or weakening identity/budget guards. Existing tests use at most
two concurrent application operations only where necessary to check races.

For a small batch, select existing relevant cases with repeated `--test NAME`
arguments to `verify_pg_security.py --paging-cluster`. The report lists the
exact cases; do not label a focused run as a full suite. Identity checks, the
exclusive lock and the80-schema budget apply equally. Full40-case baseline last
passed in batch47; batch48 adds only three schemas (40 to43).

Use `build_frontend.py --reuse` to rebuild the marked workspace-only snapshot
without another node_modules copy. It refuses while either test port is active,
checks snapshot identity/location and refuses removed/stale source files. The
valid build marker is moved aside before updating, restored only by a successful
TypeScript/Vite build; preview must not run against an unfinished build. Application
configuration/credentials are never copied. No additional dependency installation.

After restart, stale PID metadata may refer to an unrelated Windows process. Keep
the launcher's refusal intact. Verify that the record predates the reboot and
the test port is free, then archive the stale metadata; never kill a reused PID.

## Completed one-time synthetic recovery rehearsal

Batch83 already ran `run_recovery_drill.ps1` against the pinned small55449 fixture.
It retains one new schema, the marked `priceyard_synthetic_restore_20261018`
database, ignored synthetic archive/state and diagnostic evidence. The runner
refuses existing artifacts rather than reseeding/overwriting. Do not rerun it on
resumption. Read `docs/BACKUP_RECOVERY.md` and the latest progress entry first.
`pg_recovery_control.py` has only fixed preparation/empty-target/diagnosis/read-only
verification phases; no arbitrary target or drop/clean option. Native tools are
single-worker and archive-limited. Production backups/restorations are unauthorized.

The approved dependency exception is documented in `docs/DEPENDENCY_READINESS.md`;
the new marked snapshot retains old trees. It does not authorize other installs.
`check_local_release.py --require-clean` performs read-only local evidence/source/
lock/Git checks and inventories versions; it cannot grant deployment permission.

Batch86 completed `run_local_tls.ps1` once. It owns one short-lived synthetic
certificate pair under ignored `runtime/local-tls-20261018`; do not install it in
any OS/browser trust store or rerun just to refresh evidence. Trusted bootstrap
generates/loads only its own new key before application imports; the unchanged
guard remains active during app execution. A disposable browser pins that public
SPKI, allows only literal HTTPS127.0.0.1:55446, then closes. Only exact-script owned
TLS processes are stopped; the normal HTTP preview is restored. No deployed TLS,
certificate authority, reverse proxy, actual provider or real-device claim follows.
