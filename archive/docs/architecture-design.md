# PriceYard Architecture Design — Repository Control Copy

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
