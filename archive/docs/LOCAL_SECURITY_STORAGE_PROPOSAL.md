# Approved scope: internal login revocation storage

Owner explicitly approved these internal security fields on 2026-10-16 through
the approval question. Local implementation/testing only; production excluded.

Purpose: finish PY-04/PY-07/PY-09 password-reset/logout protection without changing
the existing forms, appearance, passwords, 90-day token lifetime or Remember me.

Proposed local-only schema additions, not yet implemented:

- `users.auth_version`: integer, initial value zero. Password reset/account-wide
  revocation increments it so previously issued login tokens become invalid.
- `revoked_access_tokens`: token_hash (SHA-256 primary key), user_id (foreign key),
  expires_at and revoked_at. Normal logout records a hash rather than the token.
- New JWTs carry the version. Legacy tokens default to zero, preserving existing
  valid logins until a real revocation event. Authentication checks version and
  revocation. Existing logout button calls a backend logout endpoint.
- Additive migration after original 0021, executed only against positively marked
  synthetic test databases. No production schema/configuration/data access.

No customer-facing field, grade, verification screen, linking screen, new staff
role, subscription/referral policy, login-duration change or MFA is included.
Offline logout cannot guarantee server revocation until the backend is reached.
Production rollout, schema execution and customer communications remain separate
approval steps. Safer cookie storage and full session management remain separate.

Approval is requested because the owner explicitly requires approval for new
fields. Existing technical work that does not need these fields continues.
