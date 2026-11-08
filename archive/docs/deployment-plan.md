# Deployment Plan

Current authority (2026-10-18): local development/testing only. Historical hosting
directions below are retained as history; they do not authorize a push, migration,
production connection or deployment. Current release remains blocked by the
owner-approved gates in [OPERATIONAL_READINESS.md](OPERATIONAL_READINESS.md).

Owner-confirmed hosting2026-10-18: repository fidelisnguakaaga20/priceyard;
backend priceyard-api (srv-da6d9gqjnfac73e2sbfg), master/backend, deployed label
a9cf1b9, Auto-Deploy On Commit. Build command runs
`pip install -r requirements.txt && alembic upgrade head`.
Frontend priceyard (srv-da6ddb2jnfac73e39490), master, deployed label76dbd27;
frontend Auto-Deploy/root/build not yet supplied. These are owner-reported facts,
not a production inspection. No push/merge/rebuild/setting change is authorized.
Automatic build-time migrations are an explicit release blocker pending read-only
compatibility evidence, actual encrypted backup/verified isolated restore, migration
rehearsal, compatible rollback and separately approved release controls.
Current details:[PY35_FINAL_REVIEW.md](PY35_FINAL_REVIEW.md).

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
