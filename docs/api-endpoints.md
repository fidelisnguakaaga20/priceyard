# API Endpoints

## Stage 2 — Backend Foundation

### GET /health

Purpose: verify that the PriceYard FastAPI backend is running.

Authentication: none.

Expected successful response:

```json
{"status":"healthy"}
```

Verified in Stage 2 with HTTP 200.

## Later approved stages

Stage 4 planned auth endpoints:
- POST /auth/register
- POST /auth/login
- GET /auth/me

No database, authentication, commodity, market, price, subscription, or other later-stage API has been implemented in Stage 2.
