# PriceYard

**Live app:** [priceyard.onrender.com](https://priceyard.onrender.com)

PriceYard is an agricultural commodity price intelligence platform built for Nigerian traders. It replaces scattered WhatsApp price updates with structured, verified market data — current prices, price history, confidence levels, and decision-support signals (buying zones, sell-watch windows, storage suitability) for commodities like Egusi, Honey Beans, and Palm Oil across real markets (Kwali Market, Owukpa Market, Beans Market Auta Balefi, and more).

Built and shipped solo, end to end, using AI coding tools under my direction: product design, database schema, backend API, admin tooling, payment integration, and a production deployment with real paying users.

## What it does

- **Price tracking** — current price ranges (not single fake-precise numbers), historical trends with charts, and a confidence level on every price (Reporter submitted → Market visit confirmed).
- **Market intelligence** — buying zones, sell-watch windows, quality/storage readiness, and cost breakdowns, gated behind a free/trial/paid access model.
- **Admin tooling** — full CRUD for commodities, markets, and price records with an approval workflow, audit logging, CSV export, and a "prefill from last entry" shortcut to speed up repetitive data entry.
- **Growth features** — WhatsApp-native sharing with per-commodity Open Graph previews (server-rendered, since WhatsApp's crawler doesn't execute JavaScript), a referral program, and a PWA install flow for Android/iOS.
- **Automated notifications** — email alerts when a watched price changes, and a secret-protected cron endpoint for daily trial-expiry reminders, so the business runs without manual intervention.
- **Payments** — Paystack integration for subscription upgrades, with webhook-verified activation.

## Tech stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL (Supabase), JWT + Google OAuth
- **Frontend:** React, TypeScript, Vite
- **Infra:** Render (frontend + backend as separate services), Paystack, Brevo (transactional email), Sentry (error alerts), GitHub Actions (tests and deploys)

## Engineering quality

- **370 automated backend tests**, run in an isolated harness ([`tools/local-test/guard.py`](tools/local-test/guard.py)) that blocks network, DNS, child processes and real configuration, and gives each test a fresh in-memory database.
- **Website page checks** ([`frontend/tests/smoke`](frontend/tests/smoke)): every public, member and admin page is opened in a real browser at phone and desktop width, using fake data and no network. The check fails on script errors, blank pages or content cut off at the screen edge.
- **Consistent code style, enforced automatically:** Ruff for Python ([`ruff.toml`](ruff.toml)) and Prettier for the website ([`frontend/.prettierrc.json`](frontend/.prettierrc.json)).
- **Deploys only after all checks pass** ([`.github/workflows/backend-tests.yml`](.github/workflows/backend-tests.yml)): every push runs the style checks, backend tests, website build and page checks. Only `master` deploys, and the backend deploy waits until `/health` reports the new commit.
- **Security:** HttpOnly `__Host-` session cookie with a CSRF token, login throttling and rate limiting, sign-out-everywhere (login revocation), protected owner account, webhook-verified payments, and API docs hidden in production.
- **Operations:** error alerts with personal data removed before sending, scheduled operational safeguards ([`tools/operations`](tools/operations)), and encrypted database backups with a verified restore ([operations](docs/operations.md)).

## Project structure

```
backend/
  app/            FastAPI app: routes, services, models, schemas
  migrations/     Alembic database migrations
  tests/          backend tests
frontend/
  src/            React app: public, member and admin pages
  tests/smoke/    browser page checks
tools/
  local-test/     isolated test harness
  operations/     scheduled operational safeguards and backup adapter
docs/             architecture, rules, access control, database, API, operations, testing
archive/          earlier build notes, one-off scripts and records, kept for the record
```

## Running locally

Backend (needs PostgreSQL; copy `backend/.env.example` to `backend/.env` and fill it in):

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Frontend (proxies `/api/*` to the local backend):

```bash
cd frontend
npm ci
npm run dev
```

## Running the checks

```bash
# Backend tests (isolated, no database or network needed)
python -I -B tools/local-test/guard.py

# Python style
ruff format --check . && ruff check .

# Website style and build
cd frontend && npm run format:check && npm run build

# Website page checks (from frontend/, after npm ci in tests/smoke)
npx vite preview --host 127.0.0.1 --port 4322 --strictPort &
node tests/smoke/smoke.mjs
```

## Documentation

- [Architecture](docs/architecture.md): how the pieces fit, sign-in, prices, payments, notifications
- [Business rules](docs/business-rules.md): price, plan, referral and offline rules
- [Access control](docs/access-control.md): roles, plans and who can do what
- [Database schema](docs/database-schema.md): every table, column and rule
- [API reference](docs/api-endpoints.md): every endpoint and who can call it
- [Operations](docs/operations.md): hosting, deploys, alerts, scheduled safeguards, backups
- [Testing](docs/testing.md): backend tests, page checks, style checks

Earlier build notes, approvals and test records are kept in [`archive/`](archive).

## Product notes

This is a live, evolving product — the codebase reflects an iterative build process: real user feedback, data-integrity fixes caught by actual usage, and features added based on what traders in the target market said they needed (not a spec written in isolation).
