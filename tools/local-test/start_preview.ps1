$ErrorActionPreference = 'Stop'
$labPath = $PSScriptRoot
$repoPath = [IO.Path]::GetFullPath((Join-Path $labPath '..\..'))
$pythonPath = Join-Path $repoPath '.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$pidPath = Join-Path $labPath 'runtime\preview.pid'
if (Test-Path -LiteralPath $pidPath) {
    $previousId = [int](Get-Content -LiteralPath $pidPath -Raw).Trim()
    $previousProcess = Get-Process -Id $previousId -ErrorAction SilentlyContinue
    if ($previousProcess) {
        if ($previousProcess.Path -ne $pythonPath) { throw 'Preview PID belongs to another executable; refusing to stop it.' }
        Stop-Process -Id $previousId -ErrorAction Stop
    }
}
$previewPath = Join-Path $labPath 'preview.py'
$previewProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-I','-B',$previewPath) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $labPath 'runtime\preview-stdout.log') -RedirectStandardError (Join-Path $labPath 'runtime\preview-stderr.log')
$previewProcess.Id | Set-Content -LiteralPath $pidPath
Write-Output ('Synthetic-only preview: http://127.0.0.1:55446; PID ' + $previewProcess.Id)
