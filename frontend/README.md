# PriceYard Frontend

React + TypeScript single-page app for PriceYard, built with Vite. It covers the public
pages (home, prices, commodity details, price history, market days, FAQ), member pages
(dashboard, watchlist, feedback, price reporting, payments) and the admin area
(prices, commodities, markets, users, subscriptions, payments, feedback, flagged prices,
market intelligence such as signals, buying zones, sell-watch and costs, FAQ, audit logs,
activity and export).

## Local development

1. Start the FastAPI backend on `http://127.0.0.1:8000` (see [backend/README.md](../backend/README.md)).
2. From `frontend/`:

```bash
npm ci
npm run dev
```

The app opens at `http://127.0.0.1:5173`. The Vite dev server forwards `/api/*` to the
backend (set `VITE_DEV_API_TARGET` to use a different address).

Optional settings live in `.env` (copy `.env.example`):

| Variable | Purpose |
|---|---|
| `VITE_GOOGLE_CLIENT_ID` | Google sign-in. Leave blank to hide the Google button. |
| `VITE_VAPID_PUBLIC_KEY` | Push price alerts. Leave blank to hide the "Enable alerts" prompt. |
| `VITE_DEV_API_TARGET` | Backend address for the dev server (default `http://127.0.0.1:8000`). |

## Production build

```bash
npm run build
```

The build type-checks the code and writes static files to `dist/`. In production the
app calls the API on the same site through `/api` (a Render rewrite to the backend), so
sessions use a host-only, Secure, HttpOnly cookie. The build refuses any other
`VITE_API_URL` value.

## Code style

Formatting is enforced with Prettier ([`.prettierrc.json`](.prettierrc.json)) and checked before every deploy.

```bash
npm run format:check   # check
npm run format         # fix
```

## Page checks

[`tests/smoke`](tests/smoke) opens every public, member and admin page in a real browser
at phone and desktop width with fake data and no network, and fails on script errors,
blank pages or content cut off at the screen edge.

```bash
cd tests/smoke && npm ci && npx playwright install chromium && cd ../..
npx vite preview --host 127.0.0.1 --port 4322 --strictPort &
node tests/smoke/smoke.mjs
```

## Structure

```
src/
  pages/        public and member pages
  pages/admin/  admin pages
  components/   shared building blocks (layout, price cards, charts, forms)
  context/      sign-in state, preferences and pop-up messages
  services/     API calls, sessions, push alerts
  hooks/, utils/, types/
public/         app icons, manifest and service worker (installable app)
```
