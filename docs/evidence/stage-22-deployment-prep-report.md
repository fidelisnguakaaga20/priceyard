# Stage 22 Deployment Preparation Report

Date: 2026-08-25  
Status: IN PROGRESS

## Audit result

- React already supports a deployed API base through `VITE_API_URL`.
- Vite local proxy remains development-only.
- FastAPI had no CORS middleware; a separate Render frontend would therefore be browser-blocked.
- Debug already defaults to false.
- Secrets are environment-driven and `.env` remains ignored.
- Existing Supabase PostgreSQL and Alembic configuration are reusable.

## Smallest implementation

- Add `CORS_ORIGINS` configuration.
- Parse comma-separated exact origins.
- Enable FastAPI CORS only when at least one origin is configured.
- Do not permit wildcard origins.
- Add no dependency, database migration, or API contract change.

## Remaining proof

- Owner static/compile check.
- Render backend deployment and `GET /health`.
- Render frontend deployment and SPA rewrite.
- Exact production CORS origin.
- Production database/auth/admin/price/FAQ/subscription/feedback/mobile/HTTPS verification.
