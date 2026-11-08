# Architecture

PriceYard is two Render services and one PostgreSQL database.

```
Browser / installed app (PWA)
        │  https://priceyard.onrender.com
        ▼
Render static site ── /*      → React single-page app (frontend/dist)
        │
        └──────────── /api/*  → rewrite (same site, no redirect)
                                   ▼
                     Render web service: FastAPI (priceyard-api)
                                   │
                    ┌──────────────┼──────────────────────────────┐
                    ▼              ▼                              ▼
          PostgreSQL (Supabase)   Paystack (payments)   Brevo email · Web Push · WhatsApp Cloud API
```

## Frontend

- React 18 + TypeScript, built with Vite into static files.
- All API calls go to `/api` on the same site. Render rewrites them to the backend,
  so the session cookie is host-only, and the browser never stores a login token in
  JavaScript.
- A service worker makes the app installable. It caches only approved public
  resources. A saved offline price is always labelled as a saved copy with the time it
  was saved on the device, never shown as live.
- Prices are entered and displayed in Nigeria time (WAT). Instants are stored in UTC.

## Backend

FastAPI with SQLAlchemy 2 and Alembic migrations (`backend/migrations`). Code is split into:

| Folder | Role |
|---|---|
| `app/routes` | HTTP endpoints and access checks ([API reference](api-endpoints.md)) |
| `app/services` | business rules: prices, subscriptions, payments, alerts, audit |
| `app/models` | database tables ([schema](database-schema.md)) |
| `app/schemas` | request/response validation (Pydantic) |
| `app/utils` | shared helpers, including `permissions.py` (sign-in and role checks) |
| `app/jobs` | command-line jobs, e.g. payment recovery |

## Sign-in and sessions

- Email/password (bcrypt hashes) or Google sign-in. A Google account is linked only
  after its verified Google identity is checked, never by matching email alone.
- Login issues a signed JWT. Browsers receive it in an HttpOnly, Secure, SameSite=Lax
  `__Host-` cookie. Every state-changing browser request must also send the
  session's CSRF token from an allowed origin. Bearer tokens remain available for API
  clients.
- Members stay signed in for 90 days. Admin logins expire after 7 days.
- Logout revokes the presented token. A password reset or deactivating an account
  raises the user's `auth_version`, which ends every older login.
- Brute-force protection: per-route rate limits plus a per-account lock after
  5 wrong passwords in 15 minutes.

See [access control](access-control.md) for who can do what.

## Prices and data quality

- Reporters and admins submit price ranges (low–high, never a single fake-precise
  number) for a commodity at a market, with unit, bag size and type.
- New records start as **pending** and appear publicly only after an admin approves
  them. Admins can reject, edit, mark outdated or delete. Members can flag a price
  they think is wrong.
- Reporter submissions are raw observations: confidence is set to "Reporter
  submitted", and a "movement" (up/down/stable) is accepted only when the previous
  approved record has matching recorded specifications, otherwise it is `unknown`.
  Admins set movement manually during review. "Verified by 2 sources" always requires
  two distinct private source references.
- Private source names are never returned by public endpoints, CSV exports or errors.
- Every admin change is written to the audit log in the same database transaction.

## Payments

1. A signed-in user starts a monthly (₦2,500 / 30 days) or seasonal
   (₦6,000 / 90 days) checkout; the backend creates a Paystack transaction.
2. Access is granted only after Paystack confirms the payment, through the signed
   webhook or a server-side verification. The amount, currency and reference must
   all match.
3. Renewals add the purchased days after any remaining paid time. A purchase during
   a trial keeps the remaining trial days.
4. If both the webhook and the customer's return are missed, a scheduled recovery
   job verifies recorded pending payments ([operations](operations.md)). It never
   starts a new charge.

## Notifications

- Watchlist alerts when a watched price changes or reaches a target: email (Brevo),
  Web Push (VAPID) and WhatsApp (Meta Cloud API), each sent independently so one
  failing channel does not stop the others.
- Trial-ending reminders, triggered by a scheduler with a secret header.
- Admin alerts by email. Notifications are sent only after the business change is
  saved.

## Sharing

`/share/commodities/{name}` returns server-rendered HTML with Open Graph tags, so
WhatsApp link previews show the commodity's current price (WhatsApp's crawler does
not run JavaScript).

## Reliability and safety

- Request size limits are enforced before any parsing or database work (4 MiB body,
  8 KiB URL, 64 KiB headers).
- Errors are reported to Sentry with cookies, request bodies, query strings and email
  addresses removed first.
- `/health` reports the running commit; deploys wait for it.
- [Operations](operations.md) covers deploys, scheduled safeguards and backups.
  [Testing](testing.md) covers the automatic checks.
