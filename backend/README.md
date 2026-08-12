# PriceYard Backend

FastAPI backend for the PriceYard MVP.

## Requirements
- Python 3.11+
- PostgreSQL

## Setup

```bash
python -m pip install -r requirements.txt
```

For owner/local verification tooling:

```bash
python -m pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` and set the real PostgreSQL connection and a private JWT secret.

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
JWT_SECRET=REPLACE_WITH_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secret locally if needed:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Never commit `.env` or expose `JWT_SECRET`/database credentials.

## Run migrations

```bash
python -m alembic upgrade head
```

## Verify database connection

```bash
python -c "from app.database import verify_database_connection; verify_database_connection(); print('database connection: PASS')"
```

## Run API

```bash
python -m uvicorn app.main:app --reload
```

Health endpoint:

```text
GET /health
```

Expected response:

```json
{"status":"healthy"}
```

## Stage 4 authentication endpoints

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Registration creates an active `free_user` account and, from Stage 5 onward, an associated 14-day `trial` subscription. Clients cannot self-register as admin or paid users.

Protected requests use:

```text
Authorization: Bearer <access_token>
```

## Stage 4 owner smoke test

With the real PostgreSQL `DATABASE_URL` and `JWT_SECRET` configured in `.env`:

```bash
python ../docs/evidence/stage-4-owner-smoke.py
```

Expected final line:

```text
STAGE 4 OWNER SMOKE: PASS
```


## Stage 5 subscription/trial endpoints

```text
GET   /subscriptions
GET   /subscriptions/{user_id}
PATCH /subscriptions/{user_id}/status
```

Approved statuses: `free`, `trial`, `active`, `expired`, `cancelled`. Payment gateway integration remains deferred.

## Stage 5 owner smoke test

With the real PostgreSQL `DATABASE_URL` and `JWT_SECRET` configured in `.env`:

```bash
python ../docs/evidence/stage-5-owner-smoke.py
```

Expected final line:

```text
STAGE 5 OWNER SMOKE: PASS
```
