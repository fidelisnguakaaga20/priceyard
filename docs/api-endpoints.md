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

Commodity, market, price, signal, quality, FAQ, feedback and broader admin APIs remain unimplemented until their approved stages.

## Stage 5 — Subscription and 14-Day Trial

### GET /subscriptions
Purpose: list subscription records for manual administration.
Authentication: admin bearer JWT required.

### GET /subscriptions/{user_id}
Purpose: return one user's subscription/trial record.
Authentication: bearer JWT required. A normal user may view only their own record; admin may view any user's record.

### PATCH /subscriptions/{user_id}/status
Purpose: manually set an approved subscription status.
Authentication: admin bearer JWT required.

Allowed statuses:
- `free`
- `trial`
- `active`
- `expired`
- `cancelled`

Stage 5 rules:
- normal public registration creates a 14-day trial subscription;
- trial status gives full-access classification only until `trial_ends_at`;
- an expired trial transitions to `expired` and the user remains/returns `free_user`;
- `active` is the paid/full-access status and assigns `paid_user` for a normal user;
- `free`, `expired`, and `cancelled` are limited-access statuses;
- payment gateway integration remains deferred.
