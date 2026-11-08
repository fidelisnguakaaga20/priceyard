# PriceYard Backend

FastAPI + SQLAlchemy API for PriceYard, with Alembic migrations and PostgreSQL.
See the [architecture](../docs/architecture.md) and [API reference](../docs/api-endpoints.md).

## Requirements

- Python 3.12
- PostgreSQL (production uses Supabase)

## Setup

```bash
python -m pip install -r requirements-dev.txt   # app + test/style tools
```

`requirements.txt` pins the app's direct libraries; `constraints.txt` pins everything
they pull in, so every install matches the versions the tests passed with.

Copy `.env.example` to `.env` and fill it in. Never commit `.env`.

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection, e.g. `postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE` |
| `JWT_SECRET` | Long random secret for signing logins (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `FRONTEND_URL`, `CORS_ORIGINS` | The website's address and the exact origins allowed to call the API |
| `OWNER_EMAIL` | The protected owner account ([access control](../docs/access-control.md#protected-owner-account)) |
| `GOOGLE_CLIENT_ID` | Google sign-in (blank disables it) |
| `BREVO_API_KEY` or `SMTP_*` | Email delivery (password reset, alerts, trial reminders) |
| `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY` | Payments (blank disables checkout) |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_CLAIM_EMAIL` | Web Push alerts |
| `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN` | WhatsApp alerts (blank disables them) |
| `CRON_SECRET` | Secret header for the trial-reminder scheduler |
| `OPS_RECOVERY_ENABLED` | Allows the scheduled payment-recovery workflow ([operations](../docs/operations.md)) |
| `SENTRY_DSN` | Error alerts (blank disables them) |
| `API_DOCS_ENABLED` | Shows `/docs` and `/openapi.json`; keep `false` in production |

## Database

```bash
python -m alembic upgrade head
```

Migrations live in [`migrations/versions`](migrations/versions); tables are described in
the [database schema](../docs/database-schema.md).

## Run

```bash
python -m uvicorn app.main:app --reload
```

`GET /health` returns `{"status": "healthy", "deployed_commit": "..."}`.

## Tests and style

From the repository root:

```bash
python -I -B tools/local-test/guard.py   # 370 tests, isolated: no network or real database
ruff format --check . && ruff check .
```

See [testing](../docs/testing.md).

## Layout

```
app/
  main.py         app setup, middleware, routers, /health
  config.py       settings from environment variables
  routes/         HTTP endpoints and access checks
  services/       business rules (prices, subscriptions, payments, alerts, audit)
  models/         database tables
  schemas/        request/response validation
  utils/          shared helpers, including sign-in and role checks
  jobs/           command-line jobs (payment recovery)
migrations/       Alembic migrations
tests/            backend tests
```
