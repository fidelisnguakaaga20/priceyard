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

## Stage 4 — Authentication

### POST /auth/register

Purpose: create a normal PriceYard user account.

Authentication: none.

Input:
- `full_name`
- `email`
- optional `phone`
- `password`

Rules:
- email must be unique;
- phone must be unique when supplied;
- password is stored only as a bcrypt hash;
- public registration always assigns `free_user`;
- password/hash is never returned.

### POST /auth/login

Purpose: authenticate an active user and issue a JWT access token.

Authentication: none.

Input:
- `email`
- `password`

Rules:
- invalid credentials return 401;
- inactive users are blocked;
- successful login returns a bearer JWT.

### GET /auth/me

Purpose: return the authenticated user's safe account profile.

Authentication: bearer JWT required.

Rules:
- missing/invalid/expired JWT is rejected;
- inactive users are blocked;
- password/hash is never returned.

## Later approved stages

Subscription/trial behavior is Stage 5. Commodity, market, price, signal, quality, FAQ, feedback and admin APIs remain unimplemented until their approved stages.
