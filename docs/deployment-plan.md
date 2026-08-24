# Deployment Plan

Status: Stage 22 IN PROGRESS by owner-approved change control.

Approved deployment direction as of 2026-08-25:
- Frontend: Render Static Site (free during the controlled pilot).
- Backend: Render Web Service (free during the controlled pilot).
- Database: existing Supabase PostgreSQL Free project.
- HTTPS and environment-based secrets are required.
- Frontend and backend deploy independently from the same GitHub monorepo.
- Backend CORS permits only the exact deployed frontend origin supplied through `CORS_ORIGINS`.
- Render free services are accepted for pilot/testing only; cold starts and free-tier availability limits are accepted.

Owner-approved suspension:
- Stage 20 incomplete access-control corrections are DEFERRED, not passed.
- Stage 21 full MVP/security review is DEFERRED, not passed.
- The owner explicitly instructed PriceYard to suspend Stages 20–21 and host now.
- Stage 24 final acceptance remains blocked until the deferred requirements are resumed and passed.

Render service layout:
- Web Service root directory: `backend`.
- Static Site root directory: `frontend`.
- Supabase remains the persistent PostgreSQL provider.
