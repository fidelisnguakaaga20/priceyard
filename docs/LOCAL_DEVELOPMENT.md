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
Only the pinned `postgres-recovery-20261017` fixture on literal127.0.0.1:55448
(system identifier7697651361316763724) is permitted. The runner verifies the live
directory/system identity on every connection and rejects all other destinations.
Never start the old oversized `postgres-revocation` fixture or touch the unrelated
Windows PostgreSQL service. Do not supply production credentials.

The runner has an exclusive lock and80-schema budget. Select one or two relevant
methods with repeated `--test NAME` arguments plus `--recovery-cluster`. Current
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
