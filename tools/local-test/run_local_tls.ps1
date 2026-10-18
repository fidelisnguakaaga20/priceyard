$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$tlsPath = Join-Path $labPath 'local_tls_fixture.py'
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
if (Test-Path -LiteralPath (Join-Path $labPath 'runtime\local-tls-20261018')) { throw 'Synthetic TLS evidence already exists; preserve it, do not rerun' }
if (Get-NetTCPConnection -State Listen -LocalPort 55447,55448,55449 -ErrorAction SilentlyContinue) { throw 'Stop native testing first' }
& (Join-Path $labPath 'stop_preview.ps1')
$tlsProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-I','-B',$tlsPath) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $labPath 'runtime\tls-stdout.log') -RedirectStandardError (Join-Path $labPath 'runtime\tls-stderr.log')
try {
    $identityPath = Join-Path $labPath 'runtime\local-tls-20261018\public-identity.json'
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        $tlsProcess.Refresh()
        if ($tlsProcess.HasExited) { throw 'Synthetic TLS startup failed; retain logs' }
        if (Test-Path -LiteralPath $identityPath) { break }
        [Threading.Thread]::Sleep(200)
    }
    if (-not (Test-Path -LiteralPath $identityPath)) { throw 'Bounded TLS startup timeout' }
    & 'C:\Python314\python.exe' -I -B (Join-Path $labPath 'run_browser.py') local_tls_checks.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Local HTTPS browser verification failed' }
} finally {
    # Stop only the process we launched and exact-script interpreter children.
    $children = @(Get-CimInstance Win32_Process -Filter ('ParentProcessId=' + $tlsProcess.Id))
    foreach ($entry in $children) {
        if ($entry.ExecutablePath -in @($pythonPath,'C:\Python314\python.exe') -and $entry.CommandLine -and $entry.CommandLine.IndexOf($tlsPath,[StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $child = Get-Process -Id $entry.ProcessId -ErrorAction SilentlyContinue
            if ($child) { $child.Kill(); if (-not $child.WaitForExit(3000)) { throw 'Owned TLS worker did not stop' } }
        }
    }
    $tlsProcess.Refresh()
    if (-not $tlsProcess.HasExited) { $tlsProcess.Kill(); if (-not $tlsProcess.WaitForExit(3000)) { throw 'Owned TLS launcher did not stop' } }
    & (Join-Path $labPath 'start_preview.ps1')
}
