# Source details and local recovery-key step - batch95

## Current step - batch96: separate protected recovery copy

Owner completed the original helper successfully. Non-secret result and
ciphertext metadata independently agree: AES256 protection, matching private key,
RSA challenge passed;2708-byte PFX matches recorded SHA256. No private key opened
by Codex. The earlier missing-PFX/helper-not-run statements below are history.
Do not rerun the original export.

1. Sign in to your own Google Drive. In **My Drive**, choose **New > File upload**.
   Select only `C:\Users\HP\AppData\Local\PriceYardPrivateBackup\RecoveryKeys\PriceYard-EFS-Recovery.pfx`.
   This is already password-encrypted; never upload its password, the workspace,
   or unencrypted exports. Use an unshared location, not a shared drive/folder.
2. Open the uploaded file's **Share** settings: only your account may have access;
   **General access: Restricted**. Restricted alone does not remove named users
   or inherited folder access. Keep the passphrase separately in a trusted
   password manager/safe paper, with Google two-step verification enabled.
3. Download that uploaded file into Downloads. In normal Windows PowerShell run:

   ```powershell
   & "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Confirm-PriceYardRecoveryCopy.ps1"
   ```

   Press Enter if the default downloaded path is correct; otherwise enter its
   local path. Type `PRIVATE COPY` only after checking the sharing settings.
   Reply **COPY VERIFIED**, or error text without secrets. Never send the file,
   password or sharing link. Do not bypass execution-policy restrictions.

The helper only compares ciphertext size/hash against the validated original
and records the owner's remote/privacy confirmation. It does not upload,
decrypt, request passwords, query Drive permissions or contact Supabase. Syntax
validation passed; actual downloaded-copy comparison is still pending. No
fresh-Windows certificate recovery or production-backup success is claimed.

After copy verification, next scope is the source-pinned, privately prompted
read-only backup: PG17 tools, validated TLS, exports/logs/TEMP inside EFS,
AES256/header-encrypted portable archive, then a new protected local17 restore.
Review managed-object/extension coverage and isolation before restore; stop on
unsupported objects. No migration or deployment before verified recovery and
separate release authorization. No production access has occurred.

Official instructions: [Drive upload](https://support.google.com/drive/answer/2424368?co=GENIE.Platform%3DDesktop&hl=en)
and [Drive sharing](https://support.google.com/drive/answer/7166529?hl=en).

Owner-confirmed production Session pooler, project lrvpjfbtmftjkzaxbunk:

| Setting | Value |
| --- | --- |
| Host | aws-0-eu-west-2.pooler.supabase.com |
| Port |5432 |
| Database |postgres |
| Username |postgres.lrvpjfbtmftjkzaxbunk |
| Reported server/revision |17.6 /0021_feedback_screenshot |

Non-secret settings only, not authentication or independent TLS/database identity
verification. No password requested/provided, connection, export or migration.

## Verified before access

EFS folder/probe still encrypted; no redirected paths; root ACL restricted to
owning Windows account/SYSTEM. Public cipher metadata reports AES256 encryption
and expected per-user certificate. No .pfx present at the instructed root or
RecoveryKeys locations. Recovery remains UNVERIFIED; actual key not exported/read
by Codex. Earlier PG17-on-EFS restore reused; no application/native/7z suite rerun.

Prepared owner-only helper outside Git:
`C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Save-PriceYardRecoveryKey.ps1`.
It checks pinned workspace/account/ACL/certificate, prompts twice privately,
exports AES256_SHA256-protected PFX with NoClobber, loads it ephemerally and
verifies matching private key/random RSA challenge. No certificate-store import/
deletion, network/database, migrations, uploads or password display/storage.
Existing PFX is validated, not replaced. Main workflow has NOT been executed.

Six validator tests pass with a fabricated in-memory certificate:correct recovery,
wrong password/certificate/public-only key rejected, matching/different secure
inputs handled. All tests/results outside Git in recovery-helper-synthetic-test.
Initial test's read-only RSA KeySize setter corrected to explicit in-memory
RSACng; real EFS key/certificate store untouched.

## One owner action

Open normal **Windows PowerShell**, paste this and press Enter:

```powershell
& "C:\Users\HP\AppData\Local\PriceYardPrivateBackup\Save-PriceYardRecoveryKey.ps1"
```

Choose a unique long random passphrase (at least24 characters or six random
words), save it in a trusted password manager/safe paper away from the PC, and
enter it in the two hidden local prompts. This protects the recovery file, not
the database. Never send passwords/key/PFX in chat. If Windows refuses execution,
report the error; do not bypass policy. Current account policy is RemoteSigned.

Success saves RecoveryKeys/PriceYard-EFS-Recovery.pfx and non-secret
recovery-validation.json under the private root. Reply only **READY** or error
text. Keep passphrase separate; an independent controlled recovery copy remains
to be arranged. Do not upload anything under this step. This proves a matching
usable exported key, not full fresh-Windows recovery or production-backup success.

After success, review file/result integrity without reading secrets, then prepare
the exact source-pinned owner backup command with private DB password prompt.
Keep temporary exports/data/logs in EFS and portable7z ciphertext separately.
TLS validation, source scope/snapshot and actual restore still required. No new
disk, reset, production access, migration, push or deploy authorized by this step.

Reference:[Export-PfxCertificate](https://learn.microsoft.com/en-us/powershell/module/pki/export-pfxcertificate).
35/36 complete; actual backup/release still blocked pending required evidence.
