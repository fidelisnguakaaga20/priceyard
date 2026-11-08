# Creates ONLY a new empty private folder. No database/keys/network operations.
$ErrorActionPreference = 'Stop'
$privateRoot = 'C:\Users\HP\AppData\Local\PriceYardPrivateBackup'
$projectRoot = 'C:\Users\HP\Downloads\priceyard-current'
if ([IO.Path]::GetFullPath($privateRoot) -ne $privateRoot -or
    $privateRoot.StartsWith($projectRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Unexpected private backup location'
}
foreach ($parent in @('C:\Users', 'C:\Users\HP', 'C:\Users\HP\AppData', 'C:\Users\HP\AppData\Local')) {
    $item = Get-Item -LiteralPath $parent -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Refuse redirected parent; review a private location first'
    }
}
if (Test-Path -LiteralPath $privateRoot) {
    throw 'Private folder already exists; inspect it rather than replacing permissions'
}
$ownerSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
$systemSid = New-Object Security.Principal.SecurityIdentifier('S-1-5-18')
$acl = New-Object Security.AccessControl.DirectorySecurity
$acl.SetOwner($ownerSid)
$acl.SetAccessRuleProtection($true, $false)
foreach ($sid in @($ownerSid, $systemSid)) {
    $rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $sid, [Security.AccessControl.FileSystemRights]::FullControl,
        ([Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit),
        [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
    $acl.AddAccessRule($rule)
}
# Set the private ACL when creating the empty directory, not after writing data.
[IO.Directory]::CreateDirectory($privateRoot, $acl) | Out-Null
$actual = Get-Acl -LiteralPath $privateRoot
$rules = @($actual.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))
$expectedSids = @($ownerSid.Value, $systemSid.Value) | Sort-Object
$actualSids = @($rules | ForEach-Object { $_.IdentityReference.Value }) | Sort-Object
if (-not $actual.AreAccessRulesProtected -or $rules.Count -ne 2 -or
    ($actualSids -join ',') -ne ($expectedSids -join ',') -or
    @($rules | Where-Object { $_.IsInherited -or
        $_.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        $_.FileSystemRights -ne [Security.AccessControl.FileSystemRights]::FullControl }).Count -ne 0) {
    throw 'Private ACL verification failed; do not put data in this folder'
}
[pscustomobject]@{
    path = $privateRoot
    empty = @(Get-ChildItem -LiteralPath $privateRoot -Force).Count -eq 0
    inheritance_disabled = $actual.AreAccessRulesProtected
    explicit_full_control = @('current Windows user', 'SYSTEM')
    encrypted = $false
    customer_data_present = $false
    production_connections = 0
} | ConvertTo-Json -Depth 3
