# API Endpoints

## Stage 2 — Backend Foundation

### GET /health

Purpose: verify that the PriceYard FastAPI backend is running.

Authentication: none.

Expected successful response:

```json
{"status":"healthy"}
```

Owner-verified in Stage 2 with HTTP 200.

## Stage 3 — Database Foundation

No new public/business API endpoint is introduced in Stage 3.

Stage 3 adds only the approved PostgreSQL/SQLAlchemy/Alembic database foundation and model schema.

## Later approved stages

Stage 4 planned auth endpoints:
- POST /auth/register
- POST /auth/login
- GET /auth/me

Commodity, market, price, subscription, signal, quality, FAQ, feedback and admin APIs remain unimplemented until their approved stages.
