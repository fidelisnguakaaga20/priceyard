# Stage 18 Build Report

Status: BUILT / IN PROGRESS — owner runtime proof required.

Implemented:
- React + TypeScript frontend foundation.
- Home, Prices, Commodity Detail, Price History, Market-Day Calendar, FAQ, Feedback, Login, Register, Dashboard, Watchlist.
- Shared JWT auth/subscription state and Guest/Free/Trial/Active Paid/Admin presentation states.
- Existing API integration for approved price intelligence and full-access intelligence.
- Required exact disclaimers.
- Responsive/mobile CSS.
- Vite local `/api` proxy plus deploy-time `VITE_API_URL`.

Not implemented:
- Stage 19 admin management frontend.
- Stage 20 access-control test matrix.
- payment gateway, marketplace, logistics, AI prediction, alerts, native mobile, complex charts or other deferred features.

Database: unchanged; head remains `0005_stage13_watchlists`.
Backend API contracts: unchanged.

Internal proof:
- backend compile: PASS
- static Stage 18 scope/requirements check: PASS
- TypeScript/TSX syntax transpilation check: PASS
- dependency install/production build in assistant container: BLOCKED by unavailable/timed-out npm registry access; no false PASS is recorded.

Owner proof required:
- npm install
- npm run build
- FastAPI health and Vite proxy
- browser render of public routes
- register/login
- dashboard access display
- watchlist add/remove
- feedback submit
- full-access intelligence display for trial/active paid/admin
- 390x844 mobile render + visual usability check


## Owner build attempt and configuration fix — 2026-08-13
- Owner `npm install`: PASS.
- Owner `npm run build`: FAIL with TypeScript TS5096 because `frontend/tsconfig.node.json` enabled `allowImportingTsExtensions` without `noEmit` or `emitDeclarationOnly`.
- Smallest fix: added `"noEmit": true` to `frontend/tsconfig.node.json`; no dependency, backend, API, database, or feature change.
- Assistant config retest via `tsc -p frontend/tsconfig.node.json --showConfig`: PASS; Stage 18 TS/TSX syntax check remains PASS.
- Owner full Stage 18 smoke retest is still required; Stage 19 remains blocked.
- Owner npm also reported 5 dependency vulnerabilities (1 moderate, 4 high). No `npm audit fix --force` was run because that could change approved dependency versions; this is tracked for security review rather than silently changing dependencies.

## Owner browser-verification attempt and approved helper fix — 2026-08-13
- Owner database connectivity retest: PASS.
- Owner `npm install`: PASS.
- Owner `npm run build`: PASS.
- Owner FastAPI `/health`: PASS.
- Owner Vite -> FastAPI proxy: PASS.
- Owner frontend dev server: PASS.
- Remaining failure: Windows Chrome headless `--dump-dom` process timed out after 30 seconds before browser-route proof completed.
- Change Control approval received for test-helper-only correction.
- Smallest fix: `docs/evidence/stage-18-owner-smoke.py` now launches Chrome with an isolated temporary user-data directory, `--headless=new`, safer noninteractive/background flags, and a 45-second browser timeout. The mobile screenshot uses the same isolated-profile approach.
- Product frontend, backend, APIs, database, dependencies, and Stage 19 scope are unchanged.
- Assistant `py_compile` of the helper: PASS.
- Stage 18 static scope check after helper change: PASS.
- Owner full browser/mobile retest is still required; Stage 19 remains blocked.
