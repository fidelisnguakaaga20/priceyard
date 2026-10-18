$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$fixturePath = [IO.Path]::GetFullPath((Join-Path $labPath 'runtime\postgres-paging-20261018'))
if ($fixturePath -ne 'C:\Users\HP\Downloads\priceyard-current\tools\local-test\runtime\postgres-paging-20261018') { throw 'Wrong fixed synthetic fixture' }
foreach ($port in @(55446,55447,55448,55449)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw 'Stop isolated preview/native testing before this phase' }
}
foreach ($name in @([Environment]::GetEnvironmentVariables().Keys)) {
    if ($name -like 'PG*') { [Environment]::SetEnvironmentVariable($name,$null,'Process') }
}
$env:PGPASSFILE = Join-Path $labPath 'runtime\nonexistent-synthetic-passfile'
$env:PGSERVICEFILE = Join-Path $labPath 'runtime\nonexistent-synthetic-services'
if ((Test-Path -LiteralPath $env:PGPASSFILE) -or (Test-Path -LiteralPath $env:PGSERVICEFILE)) { throw 'Unexpected credential sentinel' }
$env:PGSSLMODE = 'disable'
$env:PGGSSENCMODE = 'disable'
$env:PGCONNECT_TIMEOUT = '3'
$env:PGOPTIONS = '-c statement_timeout=15000 -c lock_timeout=5000'
$pgPath = 'C:\Program Files\PostgreSQL\18\bin'
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$identity = & (Join-Path $pgPath 'pg_controldata.exe') $fixturePath
if ($LASTEXITCODE -ne 0 -or ($identity -join "`n") -notmatch '7697910732590408300') { throw 'Wrong synthetic cluster identity' }
try {
    & (Join-Path $pgPath 'pg_ctl.exe') -D $fixturePath -l (Join-Path $labPath 'runtime\postgres-paging-20261018.log') -o '-h 127.0.0.1 -p 55449 -c max_connections=12 -c shared_buffers=32MB -c maintenance_work_mem=16MB -c autovacuum_max_workers=1 -c fsync=on' -w -t 15 start
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic database startup failed' }
    & $pythonPath -I -B (Join-Path $labPath 'verify_pg_security.py') --paging-cluster --test test_single_subscription_get_rechecks_committed_paid_and_trial_renewals --test test_single_subscription_expiry_holds_lock_until_payment_can_credit_once --test test_listing_expiry_rechecks_a_renewal_completed_after_candidate_selection --test test_provider_verification_and_webhook_share_one_credit --test test_concurrent_distinct_purchases_preserve_both_durations
    Copy-Item -LiteralPath (Join-Path $labPath 'runtime\postgres-security.json') -Destination (Join-Path $labPath 'evidence\batch-87-postgres.json')
    if ($LASTEXITCODE -ne 0) { throw 'Native final-review regression failed; preserve failure evidence' }
} finally {
    & (Join-Path $pgPath 'pg_ctl.exe') -D $fixturePath -m fast -w -t 15 stop
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic database did not stop normally' }
}
