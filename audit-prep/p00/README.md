# Isolated PriceYard verification

All data is synthetic. Production databases, real transactions/messages, customer
exports, secret files and deployments are excluded. Do not import application
modules from an unguarded test command or reuse historical owner smoke scripts.

This implementation uses disposable environments plus reviewed process/transport
guards. It is not a general-purpose VM/container security policy for arbitrary
untrusted native code. New subprocesses, database drivers or transports require
review; do not assume they inherit every Python/Node guard.

## Prepared runtime

The working environment uses `runtime/venv`, separately acquired declared frontend
tools, secret-free snapshots and a separately initialized local PostgreSQL cluster.
These disposable artifacts are ignored by Git. A clean checkout must provision
compatible tools and cluster identity before execution; the scripts intentionally
fail rather than falling back to developer/production services.

Dependency acquisition is a separate network-enabled activity with no application
credentials. The frontend acquisition helper uses an app-free directory, empty
local npm configuration and --ignore-scripts. It records package-lock and a tooling
manifest. Runtime tests do not install dependencies. The Python verification lock
is platform-specific (Windows/Python 3.14); do not treat it as a universal production
environment.

## Backend: no network, fresh SQLite

From the repository root:

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_backend_tests.py'
```

Optional focused selection:

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_backend_tests.py' --pattern test_http_workflows.py
```

Before application imports, the runner clears inherited application configuration,
disables dotenv, rejects secret-bearing file reads and restricts SQLAlchemy to fresh
in-memory SQLite. TCP/DNS is denied; only Windows asyncio's thread-local internal
socket-pair creation is permitted. Provider calls must be mocked or they fail.

Actual main-ASGI HTTP tests use genuine synthetic JWTs, isolated AtomicSession
overrides and real request/transaction/rate-limit middleware. No HTTP request is
sent to the deployed application.

## PostgreSQL: fixed positively identified disposable cluster

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\verify_migrations.py'
```

The verifier accepts no connection URL/host/database arguments. Required boundary:

- Literal 127.0.0.1:55439; synthetic role priceyard_test_admin.
- Cluster data directory runtime/postgres-test.
- An offline pg_controldata identity marker created during trusted initialization.
- Live data_directory and system_identifier matching that marker before mutation.
- Only marked synthetic priceyard_test database and random current-run namespaces.
- Native Psycopg and SQLAlchemy connection checks; no arbitrary service/passfile/
  hostaddr/URL override. An explicitly empty synthetic passfile prevents reading
  an existing account's PostgreSQL credentials.
- Secret-file/DNS/other socket restrictions before application imports.
- Namespace cleanup only after matching the current run's marker.

The script may create its exact synthetic database if absent, but refuses an
unmarked existing one. It does not select or reset another database. Cleanups remove
only current-run synthetic schemas; old/unrecognized resources are not silently
deleted. Root-level application database guards are not relaxed for these tests.

This suite exercises real PostgreSQL migrations and concurrency. SQLite alone
cannot establish those properties. No Supabase host or live provider is probed;
negative destinations use reserved illustrative names rejected before transport.

## Frontend build and browser checks

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\prepare_frontend.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_browser_checks.py'
```

Preparation creates an allowlisted disposable source snapshot, excludes dotenv and
symlinks, verifies declared tools, sets synthetic inputs and runs Node tests,
TypeScript and Vite under the Node file/transport guard. The real working directory
is not used as a Vite environment-discovery location.

The browser wrapper requires the successful marked snapshot build. It uses a fresh
synthetic profile, routes API requests to fabricated responses and blocks external
browser traffic. It does not sign in to production or reuse a real browser profile.
Browser installation/availability and sandbox permission failures must be reported
as failures/blockers, not as passing visual verification.

## Evidence and limitations

Each runner prints counts and returns a failing exit status when checks fail.
Keep service tests, actual HTTP boundaries, PostgreSQL properties, Node tests,
builds and browser workflows distinct. See the root progress/report and
[backend price evidence](../../docs/evidence/backend-price-hardening.md).

No test proves deployed provider behavior, infrastructure egress, backup retention,
restoration, database privileges, production performance or universal accessibility.
No production migration or release is authorized by running this lab.


## Actual worker/offline lifecycle

After the successful frontend build, run `run_browser_checks.py --pwa` through the same isolated Python invocation. This uses the matching disposable Chromium binary and a synthetic server bound only to `127.0.0.1:55441`. The Node guard resolves that literal without DNS and permits only that exact server bind; other Node connections remain denied. The fixture server is closed before offline reload checks, so worker fallback is tested against an unavailable server rather than browser offline emulation alone. Authenticated/history requests remain uncached and logout purges saved prices. This does not use the real API, provider credentials or a real browser profile.

Browser/tool acquisition helpers run separately from tests. Missing tools/cluster markers fail closed. A clean environment must acquire the pinned toolchain and matching browser before running these commands.
