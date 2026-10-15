# PriceYard architecture: current contracts and historical design

The October 2026 full development authorization supersedes earlier deferred-stage
boundaries. Current contracts are in [API endpoints](api-endpoints.md),
[access control](access-control-matrix.md), [deployment](deployment-plan.md) and
the root [progress record](../PRICEYARD_PROGRESS.md). Historical design text below
is retained for traceability; its manual-payment/Reporter-deferred statements are
not the current implemented behavior.

Current flow: React public/member/Reporter/Admin pages call FastAPI bearer-session
APIs. Database-backed authority/entitlement checks precede service operations.
The HTTP transaction commits mutations and sanitized administrative evidence before
success. Validated payment activation records payment/grant/subscription together;
pending checkout intent has a deliberate earlier durable boundary before provider
initialization. Notifications enqueue transactionally and a separate worker delivers
with leases/retries. PostgreSQL stores retained prices, restricted revisions and
payment evidence. External providers are never part of synthetic test transport.

## Historical stage design

## Approved stack
- Frontend: React + TypeScript
- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: JWT + bcrypt-compatible password hashing
- Hosting: Vercel frontend; one approved backend host (Render/Railway/Fly.io); Supabase/PostgreSQL database
- Payment: manual first
- AI: later, summaries only; no prediction

## MVP roles
- Admin: full administration.
- Free User: limited viewing + FAQ/search/feedback.
- Trial User: full approved viewing for 14 days.
- Paid User: full approved viewing.
- Reporter: deferred until admin flow is stable.

## Main public/user pages
Home; Prices; Commodity Detail; Price History; Market-Day Calendar; FAQ; Login/Register; User Dashboard; Watchlist; Feedback.

## Admin pages
Admin Dashboard; Manage Commodities; Manage Markets; Manage Price Updates; Manage FAQ; Manage Users; Manage Feedback; plus later-stage management pages approved by the execution plan for signals, buying zones, sell-watch windows, storage suitability, costs, subscriptions, audit logs and export.

## Database baseline
Stage 3 creates:
users; subscriptions; commodities; markets; price_updates; market_signals; quality_signals; faq_items; audit_logs; feedback.

Later approved stages create:
buying_zones; sell_watch_windows; storage_suitability; cost_breakdowns; watchlists.

The `price_updates` record must preserve `possible_meaning` and `suggested_action` independently of market signals.

## API baseline
Authentication: POST /auth/register; POST /auth/login; GET /auth/me.
Commodity/market/price/signal/quality/FAQ/subscription/feedback/admin APIs are introduced only in their approved stages.

## Code organization
```
priceyard/
├── backend/
├── frontend/
├── docs/
├── README.md
└── .gitignore
```
Backend separates models, schemas, routes, services and utilities as implementation grows. Frontend separates pages, admin pages, components, services, types, context and utilities. Do not add unnecessary infrastructure.

## Architecture constraints
No microservices, Kubernetes, queues, Redis/cache, GraphQL, Elasticsearch, event-driven architecture, separate auth service, native app, marketplace, escrow, logistics or AI prediction without approved change control.
