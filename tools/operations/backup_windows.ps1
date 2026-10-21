# Install/enroll only when explicitly invoked by the owner; no action on dot-source.
[CmdletBinding()]
param(
    [ValidateSet('Enroll','RegisterTask','Run','Verify')][string]$Action,
    [ValidatePattern('^([01][0-9]|2[0-3]):[0-5][0-9]$')][string]$DailyAt='20:00'
)
$ErrorActionPreference='Stop'
$purpose='priceyard-recurring-backup-0022-v1'
$root='C:\Users\HP\AppData\Local\PriceYardPrivateBackup'
$efs=Join-Path $root 'PrivateRestoreEfs'
$sid='S-1-5-21-459339568-2436947701-3458135915-1001'
$enrollment=Join-Path $efs 'recurring-backup-0022.dpapi'
$python='C:\Users\HP\Downloads\priceyard-current\.git\priceyard-local-recovery-20261015\p00\runtime\venv\Scripts\python.exe'
$runner=Join-Path $PSScriptRoot 'backup_runner.py'
if(-not $Action){Write-Host 'Choose Enroll, RegisterTask or Run only after reviewing this procedure.';return}
if([Security.Principal.WindowsIdentity]::GetCurrent().User.Value -ne $sid){throw 'Run as the original backup owner'}
foreach($path in @('C:\Users\HP','C:\Users\HP\AppData','C:\Users\HP\AppData\Local',$root,$efs)){
    if((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Redirected backup path refused'}
}
$acl=Get-Acl -LiteralPath $root
$rules=@($acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
if(-not $acl.AreAccessRulesProtected -or $rules.Count -ne 2 -or @($rules | Where-Object {
    $_.IdentityReference.Value -notin @($sid,'S-1-5-18') -or $_.AccessControlType -ne 'Allow'
}).Count -ne 0){throw 'Owner-only backup permissions changed'}
foreach($path in @($efs,(Join-Path $efs 'FABRICATED_ONLY_encryption_probe.txt'))){
    if(-not ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::Encrypted)){throw 'EFS protection unavailable'}
}
if(-not (Get-Item -LiteralPath 'Cert:\CurrentUser\My\C53486EF563407FB8D37D03440A55E2DABDF3F56').HasPrivateKey){throw 'EFS recovery key unavailable'}
if((Get-FileHash -LiteralPath (Join-Path $root 'Start-PriceYardDirectEncryptedBackup.py') -Algorithm SHA256).Hash -ne 'BCD92F38C3CA888117C6C9CD5488C8ED66E4639ED37F42EBDAE4DDDF4731D686'){
    throw 'Reviewed backup core changed'
}
if(Test-Path -LiteralPath $enrollment){
    $secretAcl=Get-Acl -LiteralPath $enrollment
    $secretRules=@($secretAcl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
    if($secretRules.Count -ne 2 -or @($secretRules | Where-Object {
        $_.IdentityReference.Value -notin @($sid,'S-1-5-18') -or $_.AccessControlType -ne 'Allow'
    }).Count -ne 0){throw 'Protected enrollment permissions changed'}
}
if($Action -eq 'Verify'){return}
if($Action -eq 'Enroll'){
    if(Test-Path -LiteralPath $enrollment){throw 'Existing enrollment preserved; no overwrite'}
    & $python -I -B $runner --enroll-private
    if($LASTEXITCODE -ne 0){throw 'Private enrollment did not pass; no backup was started'}
    return
}
if(-not (Test-Path -LiteralPath $enrollment)){throw 'Private one-time enrollment is required first'}
if($Action -eq 'RegisterTask'){
    if(Get-ScheduledTask -TaskName 'PriceYard encrypted daily backup 0022' -ErrorAction SilentlyContinue){throw 'Existing scheduled task preserved'}
    if($PSScriptRoot.StartsWith('C:\Users\HP\Downloads\priceyard-current',[StringComparison]::OrdinalIgnoreCase)){
        throw 'Install the reviewed scripts together outside Git in the existing private backup folder first'
    }
    $scriptPath=Join-Path $PSScriptRoot 'backup_windows.ps1'
    $arguments='-NoProfile -NonInteractive -File "'+$scriptPath+'" -Action Run'
    $taskAction=New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $arguments -WorkingDirectory $root
    $nextRun=[DateTime]::Today.Add([TimeSpan]::Parse($DailyAt))
    if($nextRun -le (Get-Date)){$nextRun=$nextRun.AddDays(1)}
    $trigger=New-ScheduledTaskTrigger -Daily -At $nextRun
    $settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable -RunOnlyIfNetworkAvailable -RestartCount 2 -RestartInterval (New-TimeSpan -Hours 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    # No saved Windows password and no SYSTEM account: EFS/DPAPI need this owner.
    $principal=New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName 'PriceYard encrypted daily backup 0022' -Action $taskAction -Trigger $trigger -Settings $settings -Principal $principal -Description 'Owner-approved EFS/PG17/AES256 backup. Requires this user logged in, PC online. No migrations, restore, deletion or upload.'|Out-Null
    Write-Host 'Daily task registered. It runs only while this Windows account is logged in and online.'
    return
}
$env:PRICEYARD_BACKUP_APPROVED_SCHEDULE=$purpose
try{
    & $python -I -B $runner --run-approved
    $code=$LASTEXITCODE
}finally{Remove-Item Env:\PRICEYARD_BACKUP_APPROVED_SCHEDULE -ErrorAction SilentlyContinue}
exit $code
