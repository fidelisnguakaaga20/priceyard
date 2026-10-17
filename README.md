# PriceYard

**Live app:** [priceyard.onrender.com](https://priceyard.onrender.com)

PriceYard is an agricultural commodity price intelligence platform built for Nigerian traders. It replaces scattered WhatsApp price updates with structured, verified market data — current prices, price history, confidence levels, and decision-support signals (buying zones, sell-watch windows, storage suitability) for commodities like Egusi, Honey Beans, and Palm Oil across real markets (Kwali Market, Owukpa Market, Beans Market Auta Balefi, and more).

Built and shipped solo, end to end: product design, database schema, backend API, admin tooling, payment integration, and a production deployment with real paying users.

## What it does

- **Price tracking** — current price ranges (not single fake-precise numbers), historical trends with charts, and a confidence level on every price (Reporter submitted → Market visit confirmed).
- **Market intelligence** — buying zones, sell-watch windows, quality/storage readiness, and cost breakdowns, gated behind a free/trial/paid access model.
- **Admin tooling** — full CRUD for commodities, markets, and price records with an approval workflow, audit logging, CSV export, and a "prefill from last entry" shortcut to speed up repetitive data entry.
- **Growth features** — WhatsApp-native sharing with per-commodity Open Graph previews (server-rendered, since WhatsApp's crawler doesn't execute JavaScript), a referral program, and a PWA install flow for Android/iOS.
- **Automated notifications** — email alerts when a watched price changes, and a secret-protected cron endpoint for daily trial-expiry reminders, so the business runs without manual intervention.
- **Payments** — Paystack integration for subscription upgrades, with webhook-verified activation.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL (Supabase), JWT + Google OAuth
- **Frontend:** React, TypeScript, Vite
- **Infra:** Render (frontend + backend as separate services), Paystack, Brevo (transactional email)

## Local development and verified changes

The local development branch preserves the original application design and
approved business rules. Start with [PRICEYARD_PROGRESS.md](PRICEYARD_PROGRESS.md)
for current36-item counts, approvals, exact test results and interrupted work.
Do not treat the live-app link above as a testing target.

- [Safe isolated browser/backend/PostgreSQL workflow](docs/LOCAL_DEVELOPMENT.md)
- [Existing product, security and data-preservation contracts](docs/APPLICATION_CONTRACTS.md)
- [Current API route reference](docs/api-endpoints.md)
- [Local regression coverage and evidence](docs/TEST_COVERAGE.md)
- [Migration preservation](docs/MIGRATION_PRESERVATION.md)
- [Read-only-by-default payment recovery](docs/PAYMENT_RECONCILIATION.md)

Local verification is not production rollout approval. No production connection,
push, merge, deployment or legacy-data repair is part of the local workflow.

## Product notes

This is a live, evolving product — the codebase reflects an iterative build process: real user feedback, data-integrity fixes caught by actual usage, and features added based on what traders in the target market said they needed (not a spec written in isolation).
