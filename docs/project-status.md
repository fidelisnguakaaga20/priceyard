# PriceYard Project Status

## Current stage
Stage 6 — Admin Core Management

## Stage 0 disposition
Owner supplied validation metrics: 65 reached, 14 replies, 5 willing to pay, positive usefulness/trust/continuation signals, sample market records and two source types.

Two Stage 0 claims remain not independently proven as written:
1. The owner explicitly stated the 14-day completion entry was used for form testing and that real completion would need later confirmation.
2. The second source is WhatsApp/live-session intelligence and was described as requiring later independent confirmation.

On 2026-08-12, the owner explicitly granted Application Coding Permission: YES. This remains an owner-approved Stage 0 exception/accepted business risk, not fabricated independent proof.

## Completed and owner-approved stages
- Stage 1 — Project Setup: PASS.
- Stage 2 — Backend Foundation: RETESTED/PASS and owner-approved after local verification.
- Stage 3 — Database Foundation: RETESTED/PASS and owner-approved after live Supabase PostgreSQL verification.
- Stage 4 — Authentication: RETESTED/PASS and owner-approved after local authentication smoke verification.
- Stage 5 — Subscription and 14-Day Trial: RETESTED/PASS and owner-approved after corrected local runtime smoke verification.

## Stage 4 status
RETESTED/PASS — owner/local runtime smoke passed against the configured Supabase PostgreSQL database on 2026-08-12. All 17 approved authentication/security checks passed, including registration, duplicate rejection, login, wrong-password rejection, JWT handling, `/auth/me`, bcrypt storage, hash non-disclosure, and inactive-user blocking.

The first owner smoke attempt failed because the verification script used a reserved `.test` email domain. The script was corrected to use a randomized `@example.com` address. A later run failed because the freshly extracted Stage 4 snapshot intentionally contained no `.env`; after the owner restored the approved Stage 3 database URL and a fresh JWT secret locally, the corrected smoke test passed. No authentication implementation or database schema change was required for either verification issue.

## Stage 4 implementation completed
- `POST /auth/register`.
- `POST /auth/login`.
- `GET /auth/me`.
- bcrypt password hashing/verification with no silent >72-byte truncation.
- JWT generation and verification.
- active/inactive user enforcement.
- MVP role-checking dependency for `admin`, `free_user`, `paid_user`.
- public registration fixed to `free_user` to prevent privilege self-escalation.
- safe user response schema that excludes `password_hash`.
- Stage 4 owner smoke test prepared to exercise the real configured PostgreSQL database and clean up its temporary test user.

## AI-environment verification
- Python compilation: PASS.
- JWT encode/decode: PASS.
- Static auth/API/security structure checks: PASS.
- Full auth runtime test: BLOCKED in the AI environment because the `bcrypt` package cannot be downloaded due environment network/DNS restrictions. `bcrypt` is declared in `requirements.txt` and must be installed/verified on the owner's computer.

## Stage 5 status
RETESTED/PASS — owner/local runtime smoke passed against the configured Supabase PostgreSQL database on 2026-08-12. All 31 approved subscription/trial checks passed. An earlier verifier cleanup defect was fixed without changing product code, schema, or API behavior.

## Stage 6 status
IN PROGRESS — implementation is built and static verification passes. Owner/local runtime verification against the configured Supabase PostgreSQL database is required before Stage 6 can become PASS.

## Stage 6 implementation completed
- Admin-only user list/view/update management.
- Admin user activation/deactivation.
- Admin role changes limited to `admin`, `free_user`, `paid_user`; reporter remains deferred.
- Role changes keep normal-user subscription state consistent (`paid_user` -> active, `free_user` -> free).
- Commodity public read plus admin create/edit/delete.
- Market public read plus admin create/edit/delete.
- Existing Stage 5 subscription management remains protected and reused.
- No database migration was required.
- Stage 6 owner verifier ensures approved initial commodities and markets exist, with only Nasarawa Monday and Kwali Tuesday populated as verified market days.

## Stage 6 build verification
- Python compilation: PASS.
- Static route/access/scope checks: PASS.
- Full PostgreSQL runtime smoke: pending owner/local verification because the AI environment does not have the owner's Supabase credentials/bcrypt runtime.

## Outstanding project issue
Stage 0 independent-source/duration evidence remains unresolved and must be reconciled before Stage 24 final acceptance.

## Unapproved features added
None.

## Next gate
Stage 6 implementation and owner/local verification. Stage 7 must not begin until Stage 6 passes and the owner approves.
