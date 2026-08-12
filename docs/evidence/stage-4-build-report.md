# Stage 4 Build Report — Authentication

## Status
IN PROGRESS — implementation built; owner/local runtime verification required before PASS.

## Requirements implemented
- POST /auth/register
- POST /auth/login
- GET /auth/me
- bcrypt password hashing and verification
- JWT creation and verification
- active/inactive user blocking
- current-user authentication dependency
- MVP role-checking dependency for admin/free_user/paid_user
- safe user response without password/password_hash
- public registration fixed to free_user

## Database changes/migrations
None. Stage 4 uses the approved Stage 3 `users` table.

## Dependencies added
- bcrypt
- PyJWT
- email-validator
- httpx in requirements-dev.txt for owner smoke verification

## AI-environment tests
- Python compilation: PASS
- static auth structure/security checks: PASS
- JWT encode/decode: PASS
- git diff check: PASS
- full FastAPI+bcrypt+PostgreSQL smoke: BLOCKED in AI environment because bcrypt and psycopg are unavailable locally and network/DNS prevents dependency download.

## Owner verification prepared
`docs/evidence/stage-4-owner-smoke.py` exercises the approved Stage 4 behaviors against the owner's configured PostgreSQL database and removes the temporary verification user before exit.

## Failed tests/errors
No code failure has been established. Runtime verification is pending due AI-environment dependency availability, not because a Stage 4 behavior failed.

## Outstanding
Owner must install requirements, configure JWT_SECRET, and run the Stage 4 owner smoke test. Stage 5 is blocked until that evidence passes and owner approval is given.

## Unapproved features added
None.
