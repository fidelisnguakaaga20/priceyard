$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$pidPath = Join-Path $labPath 'runtime\preview.pid'
$previewPath = Join-Path $labPath 'preview.py'
$basePythonPath = 'C:\Python314\python.exe'
if (Test-Path -LiteralPath $pidPath) {
    $previousId = [int](Get-Content -LiteralPath $pidPath -Raw).Trim()
    $previousProcess = Get-Process -Id $previousId -ErrorAction SilentlyContinue
    if ($previousProcess) {
        if ($previousProcess.Path -ne $pythonPath) { throw 'Preview PID belongs to another executable; refusing to stop it.' }
        $previousMetadata = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $previousId)
        if (-not $previousMetadata.CommandLine -or $previousMetadata.CommandLine.IndexOf($previewPath, [StringComparison]::OrdinalIgnoreCase) -lt 0) { throw 'Preview PID does not match this test script; refusing to stop it.' }
    }
    # Windows venv Python can redirect to a child interpreter. Verify and stop
    # only children running this exact synthetic script, before their launcher.
    $previousWorkers = @(Get-CimInstance Win32_Process -Filter ('ParentProcessId=' + $previousId))
    foreach ($workerMetadata in $previousWorkers) {
        if (($workerMetadata.ExecutablePath -eq $pythonPath -or $workerMetadata.ExecutablePath -eq $basePythonPath) -and $workerMetadata.CommandLine -and $workerMetadata.CommandLine.IndexOf($previewPath, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $workerProcess = Get-Process -Id $workerMetadata.ProcessId -ErrorAction SilentlyContinue
            if ($workerProcess) {
                $workerProcess.Kill()
                if (-not $workerProcess.WaitForExit(3000)) { throw 'Verified synthetic worker did not stop.' }
            }
        }
    }
    if ($previousProcess) {
        # Stop only the verified child; avoid Stop-Process's interactive host path.
        $previousProcess.Refresh()
        if (-not $previousProcess.HasExited) {
            $previousProcess.Kill()
            if (-not $previousProcess.WaitForExit(3000)) { throw 'Previous synthetic preview did not stop; refusing to start another.' }
        }
    }
}
$previewProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-I','-B',$previewPath) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $labPath 'runtime\preview-stdout.log') -RedirectStandardError (Join-Path $labPath 'runtime\preview-stderr.log')
$previewProcess.Id | Set-Content -LiteralPath $pidPath
Add-Type -AssemblyName System.Net.Http
$probeHandler = [System.Net.Http.HttpClientHandler]::new()
$probeHandler.UseProxy = $false
$probeHandler.AllowAutoRedirect = $false
$probeHandler.UseDefaultCredentials = $false
$probeClient = [System.Net.Http.HttpClient]::new($probeHandler)
$probeClient.Timeout = [TimeSpan]::FromSeconds(2)
$previewReady = $false
try {
    for ($probeAttempt = 0; $probeAttempt -lt 20; $probeAttempt++) {
        $previewProcess.Refresh()
        if ($previewProcess.HasExited) { throw 'Synthetic preview exited before readiness.' }
        try {
            $probeText = $probeClient.GetStringAsync('http://127.0.0.1:55446/__test__/status').GetAwaiter().GetResult()
            $probeStatus = $probeText | ConvertFrom-Json
            if ($probeStatus.synthetic_only -eq $true -and $probeStatus.providers -eq 'disabled') {
                $workerMatches = $probeStatus.process_id -eq $previewProcess.Id
                if (-not $workerMatches) {
                    $servingMetadata = Get-CimInstance Win32_Process -Filter ('ProcessId=' + [int]$probeStatus.process_id)
                    $workerMatches = $servingMetadata.ParentProcessId -eq $previewProcess.Id -and ($servingMetadata.ExecutablePath -eq $pythonPath -or $servingMetadata.ExecutablePath -eq $basePythonPath) -and $servingMetadata.CommandLine -and $servingMetadata.CommandLine.IndexOf($previewPath, [StringComparison]::OrdinalIgnoreCase) -ge 0
                }
                if ($workerMatches) {
                    $previewReady = $true
                    @{ launcher_id=$previewProcess.Id; serving_id=$probeStatus.process_id; script=$previewPath; synthetic_only=$true; providers='disabled' } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $labPath 'runtime\preview-instance.json')
                    break
                }
            }
        } catch { }
        [System.Threading.Thread]::Sleep(250)
    }
} finally { $probeClient.Dispose() }
if (-not $previewReady) { throw 'Synthetic preview identity/readiness was not verified.' }
Write-Output ('Verified synthetic-only preview: http://127.0.0.1:55446; launcher ' + $previewProcess.Id + ', serving PID ' + $probeStatus.process_id)
