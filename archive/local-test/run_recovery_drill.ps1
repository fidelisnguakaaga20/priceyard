$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$fixturePath = [IO.Path]::GetFullPath((Join-Path $labPath 'runtime\postgres-paging-20261018'))
$expectedPath = 'C:\Users\HP\Downloads\priceyard-current\tools\local-test\runtime\postgres-paging-20261018'
if ($fixturePath -ne $expectedPath) { throw 'Unexpected recovery fixture path' }
foreach ($name in @('synthetic-backup-fixture.json','synthetic-backup-state.json','synthetic-business-backup.dump')) {
    if (Test-Path -LiteralPath (Join-Path $labPath ('runtime\'+$name))) { throw 'Existing recovery artifacts retained. Resume the recorded phase; do not seed/overwrite again.' }
}
foreach ($port in @(55446,55448,55449)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw 'Stop preview/native testing before the recovery drill' }
}
foreach ($name in @([Environment]::GetEnvironmentVariables().Keys)) {
    if ($name -like 'PG*') { [Environment]::SetEnvironmentVariable($name,$null,'Process') }
}
$env:PGPASSFILE = Join-Path $labPath 'runtime\nonexistent-synthetic-passfile'
$env:PGSERVICEFILE = Join-Path $labPath 'runtime\nonexistent-synthetic-services'
if ((Test-Path -LiteralPath $env:PGPASSFILE) -or (Test-Path -LiteralPath $env:PGSERVICEFILE)) { throw 'Unexpected synthetic credential sentinel' }
$env:PGSSLMODE = 'disable'
$env:PGGSSENCMODE = 'disable'
$env:PGCONNECT_TIMEOUT = '3'
$env:PGOPTIONS = '-c statement_timeout=10000 -c lock_timeout=3000'
$pgPath = 'C:\Program Files\PostgreSQL\18\bin'
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$identity = & (Join-Path $pgPath 'pg_controldata.exe') $fixturePath
if (($identity -join "`n") -notmatch '7697910732590408300') { throw 'Wrong cluster identity' }
& (Join-Path $pgPath 'pg_ctl.exe') -D $fixturePath -l (Join-Path $labPath 'runtime\postgres-paging-20261018.log') -o '-h 127.0.0.1 -p 55449 -c max_connections=12 -c shared_buffers=32MB -c maintenance_work_mem=16MB -c autovacuum_max_workers=1 -c fsync=on' -w -t 15 start
if ($LASTEXITCODE -ne 0) { throw 'Synthetic cluster did not start' }
try {
    & $pythonPath -I -B (Join-Path $labPath 'verify_pg_security.py') --paging-cluster --test test_prepare_tiny_synthetic_backup_fixture
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic source preparation failed' }
    Copy-Item -LiteralPath (Join-Path $labPath 'runtime\postgres-security.json') -Destination (Join-Path $labPath 'evidence\batch-83-postgres-fixture.json')
    & $pythonPath -I -B (Join-Path $labPath 'pg_recovery_control.py') prepare-target
    if ($LASTEXITCODE -ne 0) { throw 'Restore target preparation failed' }
    $manifest = Get-Content -LiteralPath (Join-Path $labPath 'runtime\synthetic-backup-fixture.json') -Raw | ConvertFrom-Json
    if ($manifest.schema -notmatch '^pyrev_[0-9a-f]{32}$' -or $manifest.port -ne 55449 -or $manifest.system_identifier -ne '7697910732590408300') { throw 'Wrong source manifest' }
    $dumpPath = Join-Path $labPath 'runtime\synthetic-business-backup.dump'
    $watch = [Diagnostics.Stopwatch]::StartNew()
    & (Join-Path $pgPath 'pg_dump.exe') --host=127.0.0.1 --port=55449 --username=priceyard_revocation_test --dbname=priceyard_isolated_test --no-password --format=custom --compress=0 --no-owner --no-acl --strict-names --lock-wait-timeout=5s ('--schema='+$manifest.schema) ('--file='+$dumpPath)
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic dump failed' }
    $dumpSeconds = $watch.Elapsed.TotalSeconds
    if ((Get-Item -LiteralPath $dumpPath).Length -gt 2097152) { throw 'Archive budget exceeded' }
    & $pythonPath -I -B (Join-Path $labPath 'pg_recovery_control.py') before-restore
    if ($LASTEXITCODE -ne 0) { throw 'Restore target must be empty and identity-pinned' }
    $watch.Restart()
    & (Join-Path $pgPath 'pg_restore.exe') --host=127.0.0.1 --port=55449 --username=priceyard_revocation_test --dbname=priceyard_synthetic_restore_20261018 --no-password --no-owner --no-acl --single-transaction --exit-on-error --jobs=1 $dumpPath
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic restore failed; preserve source and failure evidence' }
    $restoreSeconds = $watch.Elapsed.TotalSeconds
    @{dump_seconds=[Math]::Round($dumpSeconds,3);restore_seconds=[Math]::Round($restoreSeconds,3);synthetic_only=$true;production_rto_proven=$false;native_tools='PostgreSQL18';parallel_restore_workers=1} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $labPath 'evidence\batch-83-recovery-timing.json')
    & $pythonPath -I -B (Join-Path $labPath 'pg_recovery_control.py') verify
    if ($LASTEXITCODE -ne 0) { throw 'Restored verification failed' }
} finally {
    & (Join-Path $pgPath 'pg_ctl.exe') -D $fixturePath -m fast -w -t 15 stop
}
