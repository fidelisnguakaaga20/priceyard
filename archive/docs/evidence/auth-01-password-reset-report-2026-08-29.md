# PriceYard AUTH-01 Evidence Report — 2026-08-29

## Outcome

AUTH-01 was implemented without replacing existing authentication, role, subscription, admin, or business-intelligence flows.

## Changes

- Reusable accessible password field with eye/eye-off SVG icons.
- Forgot Password and Reset Password pages.
- `POST /auth/forgot-password` and `POST /auth/reset-password`.
- `password_reset_tokens` table through migration `0007_auth01_password_reset`.
- Generic SMTP sender configured only through environment variables.
- 48-byte URL-safe random tokens; only SHA-256 hashes are stored.
- 15-minute expiry, single use, prior-token invalidation, and 60-second request cooldown.
- Generic forgot-password response for known, unknown, and inactive accounts.

## Verification

- `python -m compileall app migrations`: PASS.
- `python -m unittest discover -s tests -v`: 2 tests, PASS.
- Password reset OpenAPI endpoints and 8–72 character validation: PASS.
- PostgreSQL migration SQL generation from revision 0006 to head: PASS.
- `npm run build`: PASS; 74 modules transformed.
- Built assets contain Forgot Password, Reset Password, eye icon accessibility labels, and new styling: PASS.

## Security

- Passwords continue to use bcrypt.
- Raw reset tokens are never stored.
- Reset links are not returned by the API.
- Account existence is not disclosed.
- SMTP username/password remain environment variables.
- Used or expired reset tokens are rejected.
- No payment, prediction, marketplace, or other unapproved feature was introduced.

## Production owner actions

Before the live reset email can work, configure `FRONTEND_URL` and the `SMTP_*` variables in the Render backend environment, run `python -m alembic upgrade head`, then redeploy and test one real email.
