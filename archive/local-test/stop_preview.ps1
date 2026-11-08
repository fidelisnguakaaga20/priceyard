$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$previewPath = Join-Path $labPath 'preview.py'
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$instance = Get-Content -LiteralPath (Join-Path $labPath 'runtime\preview-instance.json') -Raw | ConvertFrom-Json
if ($instance.script -ne $previewPath -or $instance.synthetic_only -ne $true -or $instance.providers -ne 'disabled') { throw 'Unexpected preview identity marker.' }
foreach ($testProcessId in (@([int]$instance.serving_id, [int]$instance.launcher_id) | Select-Object -Unique)) {
    $metadata = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $testProcessId)
    if ($metadata) {
        if ($metadata.ExecutablePath -notin @($pythonPath, 'C:\Python314\python.exe') -or -not $metadata.CommandLine -or $metadata.CommandLine.IndexOf($previewPath, [StringComparison]::OrdinalIgnoreCase) -lt 0) { throw 'PID does not match exact synthetic preview; refusing to stop it.' }
        if ($testProcessId -eq [int]$instance.serving_id -and $testProcessId -ne [int]$instance.launcher_id -and $metadata.ParentProcessId -ne [int]$instance.launcher_id) { throw 'Synthetic worker parent differs.' }
        $process = Get-Process -Id $testProcessId -ErrorAction SilentlyContinue
        if ($process) {
            $process.Kill()
            if (-not $process.WaitForExit(3000)) { throw 'Verified synthetic process did not stop.' }
        }
    }
}
if ([System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object { $_.Port -eq 55446 }) { throw 'Preview port remains in use; do not stop unknown processes.' }
@{synthetic_preview_stopped=$true;test_port_unbound=$true;unrelated_processes_untouched=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $labPath 'runtime\preview-stopped.json') -Encoding UTF8
Write-Output 'Verified synthetic preview stopped; unrelated processes untouched.'
