# PriceYard Project Status

## Current stage
Stage 19 — Admin Frontend MVP — IN PROGRESS. Stage 18 Public/User Frontend has RETESTED/PASS owner proof covering production build, API integration, registration/login, feedback, watchlist add/remove, narrow-screen usability, and the Egusi commodity-detail route. Stage 20 remains blocked until Stage 19 owner proof passes.

## Stage 0 disposition
Owner supplied validation metrics: 65 reached, 14 replies, 5 willing to pay, positive usefulness/trust/continuation signals, sample market records and two source types.

Two Stage 0 claims remain not independently proven as written:
1. The owner explicitly stated the 14-day completion entry was used for form testing and that real completion would need later confirmation.
2. The second source is WhatsApp/live-session intelligence and was described as requiring later independent confirmation.

On 2026-08-12, the owner explicitly granted Application Coding Permission: YES. This remains an owner-approved Stage 0 exception/accepted business risk, not fabricated independent proof.

## Completed and owner-approved stages
- Stage 1 — Project Setup: PASS.
- Stage 2 — Backend Foundation: RETESTED/PASS and owner-approved after local verification.
- Stage 3 — Database Foundation: RETESTED/PASS and owner-approved after live Supabase PostgreSQL verification.
- Stage 4 — Authentication: RETESTED/PASS and owner-approved after local authentication smoke verification.
- Stage 5 — Subscription and 14-Day Trial: RETESTED/PASS and owner-approved after corrected local runtime smoke verification.
- Stage 6 — Admin Core Management: RETESTED/PASS and owner-approved after corrected local Supabase-backed smoke verification.
- Stage 7 — Price Updates: RETESTED/PASS and owner-approved after local Supabase-backed smoke verification.
- Stage 8 — Search, Filters, History, Comparison: RETESTED/PASS and owner-approved after local Supabase-backed smoke verification and the owner's instruction to continue.
- Stage 9 — Market Signals and Quality Signals: RETESTED/PASS and owner-approved after local Supabase-backed smoke verification and the owner's instruction to continue.
- Stage 10 — Buying Zones and Sell-Watch Windows: RETESTED/PASS and owner-approved after Alembic migration plus local Supabase-backed owner smoke verification.
- Stage 11 — Storage Suitability: RETESTED/PASS and owner-approved after owner Supabase migration and a successful retest following one transient database connection interruption.
- Stage 12 — Cost Breakdown: RETESTED/PASS and owner-approved after Alembic migration plus local Supabase-backed owner smoke verification.
- Stage 13 — Watchlist: RETESTED/PASS and owner-approved after Alembic migration plus local Supabase-backed owner smoke verification and the owner instruction to continue.
- Stage 14 — FAQ: RETESTED/PASS and owner-approved after local Supabase-backed owner smoke verification and the owner instruction `continue 15`.

## Stage 10 implementation completed
- Added `buying_zones` and `sell_watch_windows` models and approved relationships.
- Added Alembic revision `0002_stage10_buy_sell_watch`.
- Added admin create/edit APIs and full-access view APIs for buying zones and sell-watch windows.
- Buying zones validate price ranges and optional validity dates.
- Buying-zone reason and sell-watch observation reject explicit guarantee/prediction/financial-advice wording.
- Trial and active-paid users can view the full Stage 10 intelligence; free/expired/cancelled users are limited; admin retains full access.
- Feature responses include safety disclaimers that implement the approved “not guaranteed lowest price / not guaranteed profit window” rules.
- No Stage 11 table/API, payment, alert, chart, AI prediction, marketplace, or other future feature was added.

## Stage 10 AI-environment verification
- Python compilation/static schema work: PASS.
- Temporary Alembic migration from the Stage 3 foundation through Stage 10 head: PASS.
- Stage 10 table and required-column inspection: PASS.
- Stage 10 schema/service create/edit/validation checks: PASS.
- Stage 10 FastAPI/API flow against temporary SQLite with a temporary bcrypt test stub: PASS; this is build evidence only.
- Full real-bcrypt/Supabase owner runtime proof is still required on the owner environment.

## Stage 10 owner verification
PASS. Owner applied Alembic revision `0002_stage10_buy_sell_watch` against Supabase PostgreSQL and `docs/evidence/stage-10-owner-smoke.py` ended with `STAGE 10 OWNER SMOKE: PASS`.

## Stage 11 implementation completed
- Added `storage_suitability` model and Alembic revision `0003_stage11_storage_suitability`.
- Added approved create/edit/view API flow.
- Approved statuses are `good`, `watch`, `risky`, and `not_recommended`.
- Optional price-update links are validated against the same commodity and market.
- Trial and active-paid users have full storage-suitability view; free/expired/cancelled users remain limited; admin manages records.
- Explicit guaranteed profit/preservation/scarcity/future-price wording is rejected.
- Exact approved storage-suitability disclaimer is returned.
- No Stage 12 cost-breakdown table/API or other future feature was added.

## Stage 11 internal verification
- Python compilation: PASS.
- Static scope/contract check: PASS.
- Temporary migration to `0003_stage11_storage_suitability`: PASS.
- Required table/field inspection: PASS.
- Internal API flow on temporary SQLite with an internal bcrypt compatibility stub: PASS; this is build evidence only.

## Stage 11 owner verification
RETESTED/PASS. The Stage 11 migration reached `0003_stage11_storage_suitability`. The first runtime smoke was interrupted when the PostgreSQL/Supabase connection closed unexpectedly during SQLAlchemy refresh. No code/schema change was made. The owner then verified the database connection, confirmed Alembic head `0003_stage11_storage_suitability`, reran the smoke, and received `STAGE 11 OWNER SMOKE: PASS` with migration, fields, relationships, validation, access control, anti-guarantee wording, and disclaimer checks passing.

## Stage 12 implementation completed
- Added `cost_breakdowns` model and Alembic revision `0004_stage12_cost_breakdowns`.
- Added approved create/edit/view API flow linked to `price_updates`.
- Component costs: transport, warehouse, security, market charges, loading/offloading, and other costs.
- `total_additional_cost` is calculated by the backend from the component costs.
- `total_estimated_landing_storage_cost` is calculated as `purchase_price_reference + total_additional_cost`.
- Negative component costs and negative purchase-price references are rejected at API and database levels.
- Editing any cost component or purchase-price reference recalculates both totals.
- Trial and active-paid users can view full cost breakdowns; admin manages records; free/expired/cancelled users remain limited under the existing access model.
- No full accounting system, average-cost calculator, Stage 13 watchlist, payment, alert, AI prediction, marketplace, or other future feature was added.

## Stage 12 internal verification
- Python compilation: PASS.
- Temporary Alembic migration through `0004_stage12_cost_breakdowns`: PASS.
- Required table/field inspection: PASS.
- Service-level save/total/recalculation/relationship checks on temporary SQLite: PASS.
- Negative-cost schema validation: PASS.
- Real Supabase owner runtime proof is still required.

## Stage 12 owner verification
RETESTED/PASS. Owner applied Alembic revision `0004_stage12_cost_breakdowns` against Supabase PostgreSQL and `docs/evidence/stage-12-owner-smoke.py` ended with `STAGE 12 OWNER SMOKE: PASS`. Migration/fields, cost saving, total calculations, edit recalculation, negative-cost rejection, relationship behavior, and access control all passed.

## Stage 13 implementation completed
- Added `watchlists` model and Alembic revision `0005_stage13_watchlists`.
- Added authenticated save/list/remove-own watchlist API flow.
- Users can save a commodity only, a market only, or a commodity+market combination.
- Empty selections are rejected.
- Referenced commodities/markets must exist and be active.
- Exact duplicates for the same user are rejected with HTTP 409.
- Ownership is derived from the JWT/current user; clients cannot assign `user_id`.
- Cross-user removal is blocked without exposing another user's watchlist record.
- Architecture-approved nullable `target_price` exists only in the database; Stage 13 does not accept target-price input or implement alerts.
- No Stage 14 FAQ work, alerts, payment, AI prediction, marketplace, or other future feature was added.

## Stage 13 internal verification
- Python compilation: PASS.
- Temporary Alembic migration through `0005_stage13_watchlists`: PASS.
- Required table/field inspection: PASS.
- Service-level save/list/duplicate/delete behavior on temporary SQLite: PASS.
- Full FastAPI app runtime in the AI container was unavailable because bcrypt is not installed; this is not counted as runtime proof.

## Stage 13 owner verification
RETESTED/PASS. Owner applied Alembic revision `0005_stage13_watchlists` against Supabase PostgreSQL and `docs/evidence/stage-13-owner-smoke.py` ended with `STAGE 13 OWNER SMOKE: PASS`. Commodity/market saves, duplicate handling, own-list isolation, cross-user removal protection, removal, target-price deferral, and SQLAlchemy relationships all passed.

## Stage 14 implementation completed
- Reused the existing Stage 3 `faq_items` table; no migration is required.
- Added FAQ schemas, service, routes, and FastAPI router registration.
- Admin can create FAQ items, edit them, publish them, hide them, and delete incorrect FAQ items as approved by the Architecture Design.
- New FAQ items start hidden; publication state is controlled only by the dedicated publish/hide endpoints.
- Public users can list and view published FAQ items without authentication; hidden FAQ items return not found and are omitted from public lists.
- Public FAQ responses do not expose `created_by` or publication-control fields.
- FAQ content validation rejects explicit guaranteed-profit/forced-trading claims and private phone/account/vendor instructions.
- Approved disclaimer wording is accepted and preserved.
- The “do not copy paid-group content word-for-word” rule remains an editorial/source-verification responsibility because PriceYard does not store the paid-source corpus for automated text comparison.
- No Stage 15 feedback API, migration, dependency, payment, alert, AI prediction, marketplace, or other future feature was added.

## Stage 14 internal verification
- Python source compilation: PASS.
- FAQ schema safety checks: PASS.
- Static route/scope review: PASS.
- Existing `faq_items` schema confirmed from the approved Stage 3 model/migration; no new migration is introduced.
- Internal FastAPI/API flow against temporary SQLite with a temporary bcrypt compatibility stub: PASS; this is build evidence only and not owner/runtime proof.

## Stage 14 owner verification
RETESTED/PASS. Owner confirmed Alembic remains at `0005_stage13_watchlists` because Stage 14 requires no migration, then ran `docs/evidence/stage-14-owner-smoke.py` against the configured Supabase PostgreSQL environment and received `STAGE 14 OWNER SMOKE: PASS`. Create/edit/publish/hide/delete, public visibility, unauthorized-management blocking, content-safety validation, disclaimer preservation, and FAQ relationships all passed.

## Outstanding project issue
Stage 0 independent-source/duration evidence remains unresolved and must be reconciled before Stage 24 final acceptance.

## Unapproved features added
None.

## Stage 15 implementation completed
- Reused the existing Stage 3 `feedback` table; no migration is required.
- Added feedback schemas, service, routes, and FastAPI router registration.
- Authenticated users can submit 1–5 star feedback with comment, usefulness, accuracy, missing-market/commodity requests, complaint/suggestion, continue-using feedback, and willingness-to-pay feedback.
- `user_id` is server-controlled from the authenticated user and cannot be supplied by clients.
- Admin can list feedback, filter by rating, view one feedback record, and see a basic count/average summary.
- Ordinary users cannot browse all private feedback, view admin summaries/details, or delete feedback.
- Included the Architecture-approved admin delete endpoint.
- No advanced analytics, Stage 16 audit behavior, migration, dependency, payment, alert, AI prediction, marketplace, or other future feature was added.

## Stage 15 internal verification
- Python compilation: PASS.
- Existing feedback model/table field review: PASS.
- Rating 0/6 schema rejection: PASS.
- Rating 1/5 service save, user linkage, filter, summary count/average, and relationship checks on temporary SQLite: PASS.
- Static scope review: PASS.
- Real Supabase owner runtime proof is still required.

## Stage 15 owner verification
RETESTED/PASS. Owner confirmed Alembic remains at `0005_stage13_watchlists` because Stage 15 requires no migration, then ran `docs/evidence/stage-15-owner-smoke.py` against the configured Supabase PostgreSQL environment and received `STAGE 15 OWNER SMOKE: PASS`. Rating boundaries, authenticated user linkage, private-feedback protection, admin listing/filter/detail/summary/delete, complaint/suggestion preservation, and SQLAlchemy relationship checks all passed. The owner explicitly instructed that if the output was okay, continue to the next stage, which approves Stage 15 and Stage 16 start.

## Stage 16 implementation completed
- Reused the existing Stage 3 `audit_logs` table; no migration is required.
- Added audit schema/service and admin-only `GET /audit-logs` plus `GET /audit-logs/{id}`.
- Added audit recording for price create/edit/approve/reject/mark-outdated/delete, commodity changes, market changes, FAQ changes, subscription changes, user status/role changes, and feedback admin delete.
- Price edit audit snapshots preserve changes to Possible Meaning and Suggested Action.
- Audit sanitization excludes password/hash fields, token/secret/database credential fields, `.env` values, and private price-source identities.
- No Stage 17 CSV export, migration, new dependency, payment, alert, AI prediction, marketplace, or other future feature was added.

## Stage 16 internal verification
- Python compilation: PASS.
- Full temporary SQLite FastAPI flow with a temporary bcrypt compatibility stub: PASS.
- Required admin-action audit coverage: PASS.
- Admin audit-history access / ordinary-user blocking: PASS.
- Possible Meaning and Suggested Action change capture: PASS.
- Sensitive/private-source absence checks: PASS.
- Real Supabase owner runtime proof is still required.

## Stage 16 owner verification
RETESTED/PASS. Owner confirmed Alembic remains at `0005_stage13_watchlists`, then ran `docs/evidence/stage-16-owner-smoke.py` against the configured Supabase PostgreSQL environment and received `STAGE 16 OWNER SMOKE: PASS`. Required audit actions, admin-only access, Possible Meaning/Suggested Action change capture, and sensitive/private-source exclusion all passed. The owner instructed that if the output was okay, continue to the next stage, which approves Stage 16 and Stage 17 start.

## Stage 17 implementation completed
- Added admin-only simple CSV export at `GET /reports/prices.csv`.
- Added optional commodity, market, `date_from`, and `date_to` filters with inclusive date-range handling.
- Export includes approved price-update commodity/market, current range, previous range, movement, update date/time, confidence, Possible Meaning, Suggested Action, and linked market/quality signals.
- Only approved price updates are exported; rejected/pending records are excluded.
- Private `source_1`/`source_2`, password/hash fields, JWT/secrets, and unnecessary personal data are not CSV columns.
- Existing Stage 9 signals have no separate approval-status field; linked admin-managed signals are included only when attached to an approved price update.
- No migration or dependency was added; repository Alembic head remains `0005_stage13_watchlists`.
- No PDF reporting, report-storage table, advanced analytics, Stage 18 frontend, payment, alert, AI prediction, marketplace, or other future feature was added.

## Stage 17 internal verification
- Python compilation: PASS.
- Static route/field/privacy/scope check: PASS.
- Temporary SQLite filter/CSV-content test: PASS.
- Temporary SQLite full FastAPI/API smoke with an internal bcrypt compatibility stub: PASS; this is build evidence only.
- Current/previous ranges, Possible Meaning, Suggested Action, linked market/quality signals, and private-source exclusion: PASS.
- Repository Alembic head unchanged at `0005_stage13_watchlists`: PASS.
- Real Supabase owner runtime proof: PASS.

## Stage 17 owner verification
RETESTED/PASS. Owner confirmed Alembic remains at `0005_stage13_watchlists` and ran `docs/evidence/stage-17-owner-smoke.py` against the configured Supabase PostgreSQL environment. Final output: `STAGE 17 OWNER SMOKE: PASS`. CSV authorization, filtering, field accuracy, linked signals, privacy exclusions, and rejected-record exclusion all passed. The owner instructed that if the output was okay, continue to the next stage; that condition was satisfied, approving Stage 17 and Stage 18 start.

## Next gate
Stage 17 — Simple CSV Report Export is RETESTED/PASS and owner-approved. Stage 18 — Public and User Frontend MVP may start; Stage 19 remains blocked until Stage 18 owner approval.

## Stage 18 implementation completed
- Added the approved React + TypeScript public/user frontend under `frontend/`.
- Added Home, Prices, Commodity Detail, Price History, Market-Day Calendar, FAQ, Feedback, Login, Register, User Dashboard, and Watchlist routes/pages.
- Added a small shared API client and authentication context using the existing JWT APIs and subscription endpoint.
- Added display states for Guest, Free, Trial, Active Paid, and Admin. Backend authorization remains the security authority; frontend hiding is only presentation.
- Added current-price cards, filters, chronological history, market-day view, and commodity-detail full-intelligence panels for market signals, quality readiness, buying zones, sell-watch, storage suitability and cost breakdown.
- Preserved Possible Meaning and Suggested Action and labels them as observational/non-guaranteed guidance.
- Added the exact approved price, market-signal and storage-suitability disclaimers.
- Added authenticated watchlist and feedback UI using the already approved Stage 13/15 APIs. Target-price alerts remain deferred.
- Added responsive CSS and mobile navigation; no complex chart library was added.
- Added Vite local `/api` proxy for Stage 18 local integration and `VITE_API_URL` for later deployed backend configuration. Production CORS remains a Stage 21/22 security/deployment concern.
- No database migration or backend API-contract change was introduced; Alembic head remains `0005_stage13_watchlists`.
- No admin management frontend, payment gateway, marketplace, logistics, AI prediction, native mobile, alerts, complex charting or other deferred feature was added.

## Stage 18 internal verification
- Backend Python compilation after frontend addition: PASS.
- Stage 18 source/static scope check: PASS.
- TypeScript/TSX syntax transpilation check using the container's global TypeScript compiler: PASS.
- Assistant-container `npm install` could not complete because package-registry access was unavailable/timed out in that container, so a real production `npm run build` and browser runtime are intentionally not claimed as internally verified.
- Owner verification helper `docs/evidence/stage-18-owner-smoke.py` installs frontend dependencies in the owner's environment, runs the production build, starts FastAPI + Vite, verifies the API proxy, renders key routes with local Chrome, and creates a 390x844 mobile screenshot.
- Register/login/watchlist/feedback interaction and visual mobile usability still require owner confirmation before Stage 18 can pass.

## Next gate
Stage 18 — Public and User Frontend MVP is BUILT/IN PROGRESS. Stage 19 — Admin Frontend MVP must not start until the owner sends the Stage 18 build/browser proof and explicitly approves Stage 18.


## Stage 18 owner build attempt / fix — 2026-08-13
Owner dependency installation completed, but the production build stopped on TypeScript TS5096 in `frontend/tsconfig.node.json`. The defect was isolated to compiler configuration: `allowImportingTsExtensions` required `noEmit` or `emitDeclarationOnly`. The smallest fix added `noEmit: true`; no dependency, API, database, backend, or Stage 19 change was made. Assistant configuration validation and TS/TSX syntax checks pass. Owner full Stage 18 smoke retest and manual browser interactions are still required before Stage 18 can be RETESTED/PASS. Stage 19 remains blocked. npm reported 5 dependency vulnerabilities (1 moderate, 4 high); no force-upgrade was applied and this remains tracked for the approved security review.


## Stage 18 second owner build failure / approved fix — 2026-08-13
The owner retest passed dependency installation and progressed beyond TS5096, then production build stopped on TypeScript TS2580 because `frontend/vite.config.ts` used `process.cwd()` without Node type definitions. Under Change Control, the owner explicitly approved the smallest fix. `loadEnv(mode, process.cwd(), "")` was changed to `loadEnv(mode, ".", "")`, avoiding a new `@types/node` dependency. No backend, API, database, access rule, deferred feature, or Stage 19 work was changed. Full owner Stage 18 smoke retest and manual browser checks remain required before Stage 18 can be RETESTED/PASS.


## Stage 18 automated browser PASS + manual integration findings / approved fixes — 2026-08-13
The corrected Stage 18 owner smoke passed the production build, FastAPI health, Vite proxy, public browser routes, and 390x844 automated mobile render, ending with `STAGE 18 OWNER SMOKE: PASS`. During the required manual interaction/visual check, feedback submission returned 201, watchlist add returned 201, watchlist delete returned 204, and login later returned 200. Two Stage 18 issues prevented owner approval: (1) registration returned a false 500 after its successful commit because the post-commit `db.refresh(user)` encountered a transient Supabase/pooler disconnect; the later successful login showed the account existed, and (2) the owner iPhone-SE-width screenshot showed horizontal clipping on the Watchlist introduction. Under approved Change Control, the smallest fixes remove only the unnecessary post-commit registration refresh and tighten mobile sizing/wrapping with `min-width: 0`, `max-width: 100%`, `minmax(0, 1fr)`, and explicit mobile page width rules. Internal registration fault-injection test, backend compile, Stage 18 syntax/static checks, and CSS parse/static checks pass. No migration, API-contract change, dependency, or Stage 19 work was added. Owner registration/mobile retest remains required; Stage 19 remains blocked.

## Stage 18 second mobile visual failure / smallest CSS fix — 2026-08-13
The owner reran `stage-18-owner-smoke.py`; production build, health, API proxy, route screenshots and 390x844 automated render all passed and the script ended `STAGE 18 OWNER SMOKE: PASS`. Manual integration evidence then confirmed unique registration 201, login 200, watchlist create 201 and watchlist delete 204. The frontend used port 5174 only because an older Vite process still occupied 5173; this is not an application defect. However, the owner iPhone SE 375x667 screenshots still showed horizontal panning/clipping of the Watchlist/header/footer, so Stage 18 cannot yet be approved. The smallest second mobile fix changes only responsive CSS to constrain root/app/main/header/page/card/footer widths and wrapping. Stage 19 remains blocked until the owner visually retests the latest fix and confirms the Commodity Detail route renders.

## Stage 18 deterministic smoke-helper correction — 2026-08-13
Owner retest of the latest mobile fix passed npm installation, production build, FastAPI health, Vite proxy and `/price-updates` 200, but Windows Chrome intermittently failed to create the first automated headless screenshot. Because prior interactive owner browser evidence already proves the frontend can render and the execution plan separately requires manual visual/mobile approval, the Stage 18 smoke helper was narrowed to deterministic automated proof: build, backend health, proxy, and SPA route availability including `/commodities/Egusi`. Headless screenshot generation is no longer a gate. Manual 375px browser inspection remains mandatory before Stage 18 can be RETESTED/PASS. No application code, API, database, dependency, migration or Stage 19 scope changed.

## Stage 18 owner verification
RETESTED/PASS and owner-approved. Owner evidence included a successful TypeScript/Vite production build, FastAPI health and proxy checks, public/user route rendering, registration 201, login 200, feedback 201, watchlist create 201/remove 204, iPhone SE 375px visual verification after the overflow fix, and normal rendering of `/commodities/Egusi` including the approved price disclaimer and Guest access lock. Intermittent Supabase/DNS connection failures and Windows headless-Chrome helper failures were isolated during retests and corrected or removed from the proof path without expanding product scope. The npm audit finding (1 moderate, 4 high) remains explicitly deferred to Stage 21 security review; `npm audit fix --force` was not run.

## Next gate
Stage 18 is RETESTED/PASS and owner-approved. Stage 19 — Admin Frontend MVP is now active. Stage 20 remains blocked pending Stage 19 completion and owner approval.
