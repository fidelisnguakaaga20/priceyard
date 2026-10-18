# Safe local development and resumption

Start with [PRICEYARD_PROGRESS.md](../PRICEYARD_PROGRESS.md), the current branch,
working-tree status and recent commits. Continue from the newest verified batch,
not an old audit or a new application rewrite. Master and the20261015 backup are
preservation references. Their exact hashes are in the tracker.

## Browser preview

Use the existing isolated tools; do not install packages or open/copy application
dotenv or provider configuration. The helper scrubs inherited credentials,
denies secret-file/provider access, uses a fresh in-memory synthetic database and
serves the compiled original frontend with a clearly marked test banner.

In PowerShell from the repository root:

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\local-test\start_preview.ps1
```

Open **http://127.0.0.1:55446**. Synthetic demo accounts are
`admin@example.com`, `reporter@example.com`, `free@example.com`,
`trial@example.com`, `paid@example.com`; the demo-only password is
`PriceYardDemo8!`. The banner also lists the credentials. These are not customer
accounts. Payments, email, push and external sharing are disabled/faked.

The preview runs real local application handlers against synthetic SQLite.
It does not prove PostgreSQL concurrency or live-provider delivery. Browser
checks block external routes and native service workers. Do not replace
same-origin browser fetch with Playwright `route.fetch`, which has a separate
native transport. Application `/__test__/...` controls exist only in the preview
harness; never add them to production routes.

Stop only this identity-checked demo:

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\local-test\stop_preview.ps1
```

Do not kill arbitrary Node/Python/PostgreSQL processes. The preview validates
script, executable, parent process and synthetic readiness. After a reboot a PID
can belong to somebody else; preserve its refusal and inspect stale metadata.

## Existing verification tools

Use the Python interpreter and dependency tools already preserved in
`.git/priceyard-local-recovery-20261015/p00/runtime`. Never stage that runtime.

```powershell
$testPython = '.\.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
& $testPython -I -B .\tools\local-test\guard.py --pattern 'test_report_export*.py'
& 'C:\Python314\python.exe' -I -B .\tools\local-test\run_browser.py export_checks.mjs
```

Run one phase at a time. Choose tests relevant to the batch; run a broader suite
when changed behavior warrants it. A focused run is not a full-suite pass. Save
reports from ignored `tools/local-test/runtime` to the current batch's tracked
`tools/local-test/evidence` files before another run overwrites them. Wait for
command exit, including yielded tool sessions, before dependent staging/commits.

If frontend sources change, stop the preview and native fixture first. Reuse the
one marked build snapshot; do not copy another dependency tree:

```powershell
& 'C:\Python314\python.exe' -I -B .\tools\local-test\build_frontend.py --reuse
```

The helper refuses active test ports and invalid snapshot identity, removes the
valid marker during building and restores it only after TypeScript/Vite succeed.
After failure, the same `--reuse` command can resume the preserved in-progress
identity, repeating those checks without declaring the unfinished build ready.
Do not serve a half-built snapshot. No build is needed for unchanged frontend
sources. Keep the original CSS and visible behavior unless specifically approved.

## Smaller native PostgreSQL fixture

Follow [the test harness guide](../tools/local-test/README.md) for exact commands.
The current pinned `postgres-paging-20261018` fixture is literal127.0.0.1:55449
(system identifier7697910732590408300). The old recovery fixture is exhausted80/80
and must remain stopped/intact. The runner verifies the live
directory/system identity on every connection and rejects all other destinations.
Never start the old oversized `postgres-revocation` fixture or touch the unrelated
Windows PostgreSQL service. Do not supply production credentials.

The runner has an exclusive lock and80-schema budget. Select one or two relevant
methods with repeated `--test NAME` arguments plus `--paging-cluster`. Current
usage is in the latest progress entry/report. Each case retains its fresh schema,
including failed setup evidence. Do not drop schemas, raise the budget, repeatedly
run the whole suite or weaken identity checks. Prepare a fresh pinned empty
fixture when necessary. Keep fsync/durability enabled and reduced resource limits;
stop it gracefully before browser/build phases.

This is the only permitted migration target for authorized local migration
tests. Production migrations, repair scripts, provider calls and deployment are
outside local testing permission.

## API/docs maintenance

The [API reference](api-endpoints.md) indexes current router declarations. Regenerate
its table without importing the application or settings:

```powershell
& 'C:\Python314\python.exe' -I -B .\tools\local-test\update_api_reference.py
```

`format_admin_sources.mjs` is a guarded, allowlisted readability helper for the
two legacy files containing six intelligence forms. It requires identical emitted
executable code, including JSX text, before writing; it adds no dependency.
Formatting is not a substitute for TypeScript/build and browser checks.

Read [application contracts](APPLICATION_CONTRACTS.md) before changing access,
pricing, comparisons, account behavior or stored evidence. Keep unfinished owner
decisions visible and separate from production readiness claims.

Browser sessions now use protected HttpOnly cookies. Same-profile tabs share
login/logout; use separate browser profiles/contexts to review independent roles.
New browser JWTs are absent from localStorage/sessionStorage/document.cookie.
Only the isolated55446 fixture permits non-Secure cookies. Production needs
HTTPS/same-site cookie compatibility and supported cross-tab Web Locks; do not
weaken this to make a hosted preview appear to work. Existing API bearer clients
remain supported. Focused browser check:cookie_session_checks.mjs.

## Current dependency and operational evidence

The approved Vite6.4.4/router6.30.6 snapshot is
`tools/local-test/runtime/frontend-security-20261018`; its marker and reviewed
frontend lockfile identify the built version. Older dependency trees remain
preserved. Use the isolated55446 preview; do not run the original root dev server
with application configuration. Additional installs require scoped authorization.

The one-time synthetic recovery drill has already run. Its source schema, marked
restore database and ignored archive/state are retained. Do not reseed, overwrite,
run another restore or delete them on resumption. See [backup/recovery](BACKUP_RECOVERY.md)
and batch83 evidence. The small cluster is stopped,19/80 schemas retained.

After a verified local commit, run the read-only candidate check:

```powershell
& '.\.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe' -I -B .\tools\local-test\check_local_release.py --require-clean
```

Its ignored runtime report inventories installed packages and checks evidence,
build/source/lock identity and preserved Git references. It never connects to a
database/provider, deploys or authorizes production. The [nine live release gates](OPERATIONAL_READINESS.md)
remain separately approved work even when this local command passes.

Phase1 safe staging was subsequently approved; [results and blockers](PY35_PHASE1_REPORT.md)
distinguish the separate ignored source/artifact package from unavailable hosted
HTTPS/provider testing. `run_phase1_backend.py` runs only selected original tests
against that verified source copy with fresh memory data and closed transport.
`run_phase1_native.ps1` uses only the pinned small fixture and stops it afterward;
do not rerun just to refresh results. `verify_phase1_results.py` checks saved
evidence and all nine scoped statuses without contacting any service. The staging
package has no credentials or live URL and is not a production startup shortcut.
