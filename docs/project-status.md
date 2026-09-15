# AUTH-02 — Brevo HTTPS email delivery (2026-08-29)

- Status: implemented and locally tested.
- Password-reset email delivery now prefers Brevo's HTTPS API when `BREVO_API_KEY` is configured.
- Existing SMTP delivery remains available as a local fallback.
- No database, token, authentication, role, subscription, or frontend behavior changed.

# PriceYard Project Status

## Approved change request CR-01 — 2026-08-24

CR-01 Global Loading Spinner is RETESTED/PASS and owner-approved. The React + TypeScript production build and focused loading-coverage/static checks pass. Shared page, overlay and button loaders cover authentication waits, approved-price/data loading, search/history, feedback, watchlist and admin data/actions. The owner confirmed the database connection, successful backend API responses, and stylish spinner behavior across the actions exercised. No backend, API, database, dependency, access-control, subscription, disclaimer or completed-stage behavior changed.

The owner instructed PriceYard to continue, authorizing CR-02 only. CR-03 has not started.

## Approved change request CR-02 — 2026-08-24

CR-02 Success Confirmation Popups is RETESTED/PASS and owner-approved. Login, registration, and logout use one shared accessible popup system with the exact approved messages, success/error colors, automatic/manual dismissal, and mobile-safe positioning. The existing spinner is cleared before the popup is triggered. TypeScript and Vite production builds pass. The owner confirmed login, error, registration, and logout popups all worked.

The owner authorized continuation under the approved execution plan. CR-03 is now the only authorized change stage; CR-04 has not started.

## Approved change request CR-03 — 2026-08-24

CR-03 Active MVP Data Reset is RETESTED/PASS and owner-approved. The owner applied Alembic revision `0006_cr03_egusi_kwali`, completed the configured PostgreSQL/API/CRUD/access smoke with `CR-03 OWNER SMOKE: PASS`, and verified the final data state: Egusi active; Beans/Palm oil inactive; Kwali Market active; Abuja/FCT/Nasarawa/Benue inactive. Temporary browser-test deletions were repaired without changing schema or application code. Public/API runtime requests and protected admin all-record views passed.

The owner's instruction to continue after the passing proof authorizes CR-04 Regression Testing only.

## Current stage
Stage 19 — Admin Frontend MVP — RETESTED/PASS; runtime, browser, data-repair, and cleanup proof are complete. Explicit owner approval is the remaining gate. Stage 20 remains blocked until that approval is given.

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

## Stage 19 implementation completed
- Added admin-only React route guard and admin navigation.
- Added admin dashboard with only approved basic metrics.
- Added management pages for users, commodities, markets, price updates, market signals, quality signals, buying zones, sell-watch windows, storage suitability, cost breakdown, FAQ, subscriptions, feedback, audit logs and CSV export.
- Price administration preserves editable Possible Meaning and Suggested Action with the approved action set.
- Existing backend APIs are reused; no backend API or database schema change was made.
- No migration or new runtime dependency was added.
- No advanced BI, complex charts, payment gateway, marketplace, escrow, logistics, AI prediction, native mobile, alerts or other deferred feature was added.

## Stage 19 internal verification
- Static admin route/scope/API integration check: PASS.
- TS/TSX syntax transpilation: PASS.
- Temporary-stub TypeScript semantic check: PASS.
- Backend-change scope check: PASS; Stage 19 is frontend-only.
- Migration check: PASS; Alembic head remains `0005_stage13_watchlists`.
- Real owner npm production build and configured PostgreSQL admin API smoke are still required.

## Stage 19 next gate
Run `docs/evidence/stage-19-owner-smoke.py` in the owner environment, then visually confirm the Admin dashboard and at least one management page. Stage 20 remains blocked until owner approval.

## Stage 19 owner smoke environment-path failure / smallest fix — 2026-08-13
The first owner Stage 19 smoke attempt stopped before application verification with `DATABASE_URL is required for database operations`. The owner had correctly copied `backend/.env`; the helper was launched from the project root while application settings resolve `.env` relative to the working directory. The smallest fix changes only `docs/evidence/stage-19-owner-smoke.py` to enter `backend/` before importing application modules. Helper compilation, Stage 19 static scope checks, and a temporary non-secret backend `.env` resolution check pass. No frontend feature, backend business logic, API, database schema, migration, dependency, or Stage 20 work changed. Owner Stage 19 smoke retest is still required.


## Stage 19 owner verification complete — 2026-08-19
Owner proof is complete. Data repair restored the accidental browser-test mutations and verified the exact MVP core commodities/markets. The Stage 19 static check, npm production build, owner API smoke, non-admin authorization checks, browser Admin Overview, editable Possible Meaning / Suggested Action controls, three consecutive history requests, and temporary-admin cleanup all passed. The earlier Price Update 422 was confirmed to be expected validation because the entered average price was outside the current range. A transient Supabase pooler DNS lookup failure on `/auth/me` later recovered without code change and is recorded as a non-reproducible environment/network observation. npm audit findings remain reserved for Stage 21. Stage 20 has not started; explicit owner approval of Stage 19 is still required.

## Stage 20 started — access-control pre-fix assessment — 2026-08-18
Stage 19 was explicitly owner-approved and Stage 20 — Access Control and Subscription Testing is now the only active stage. The required access-control matrix has been created and a source-level assessment was run before changing application behavior. Existing controls already enforce inactive-account blocking, admin role guards, 14-day trial expiry, active-paid full-access classification, and full-access guards on buying zones, sell-watch windows, storage suitability, and cost breakdowns. Three approved-requirement gaps were found: the Guest/public price response exposes deeper guidance fields beyond the approved public Prices-page field set; limited authenticated users receive full market-signal meaning/action instead of a basic signal view; and quality signals are currently available to any authenticated active user instead of requiring full approved access. Under the project Change Control rule, no application/API/frontend behavior has been changed yet. Stage 20 is IN PROGRESS/FAIL pending owner approval of the smallest access-control correction and subsequent runtime matrix retest.


## Approved change request CR-04 — 2026-08-24

CR-04 Regression Testing is IN PROGRESS. A focused owner regression helper and verification steps have been added; application source, APIs, database schema, dependencies, access rules, subscriptions, disclaimers, spinner, popups, and CR-03 active-data behavior are unchanged. Helper syntax compilation passes. Owner PostgreSQL/API regression, frontend production build, static spinner/popup/data checks, and final read-only browser verification remain required before CR-04 can pass.


## CR-04 first owner run / evidence-helper correction — 2026-08-24

Frontend production build, CR-02 popup check and CR-03 active-data check passed. CR-01 reported a test-only false failure because its original cleanup assertion required `finally` in Login/Register even though the approved CR-02 sequence explicitly clears busy state before showing popups. The checker now counts both explicit success/error `setBusy(false)` paths. The CR-04 owner helper was interrupted after an unexplained silent wait; it now emits immediate phase/PASS progress and uses a helper-only 15-second PostgreSQL connection timeout. No PriceYard application, API, schema, data, dependency or access behavior changed. Owner retest remains required.


## CR-04 automated owner regression — 2026-08-24

RETESTED/PASS. Corrected CR-01, CR-02 and CR-03 focused checks passed; the existing frontend TypeScript/Vite production build passed with 71 transformed modules; and the configured PostgreSQL/API regression ended with `CR-04 OWNER REGRESSION: PASS`. Authentication, role/subscription access, inactive blocking, admin reads/CRUD, price approval/outdated behavior, feedback/privacy, temporary-record cleanup and final Egusi/Kwali-only public state passed. Only the required read-only browser verification remains before CR-04 owner approval and CR-05 authorization.


## CR-04 Regression Testing — RETESTED/PASS and owner-approved — 2026-08-24

CR-04 is complete. Focused CR-01/02/03 checks passed, the React + TypeScript production build passed, the configured PostgreSQL/API owner regression ended with `CR-04 OWNER REGRESSION: PASS`, and the final browser/runtime verification was healthy. The browser proof included successful registration, valid login, profile and subscription reads, public Egusi/Kwali filtering, protected admin reads, and watchlist reads. The observed `401 Unauthorized` was the intentional wrong-password test.

The owner instructed PriceYard to continue if the output was okay. The output satisfied the approved criteria, so this condition approves CR-04 and authorizes CR-05 documentation only.

## CR-05 Final Change Report — complete; owner approval requested — 2026-08-24

The final report is `docs/evidence/cr-05-final-change-report.md`. CR-00 through CR-04 are documented as complete. No application source, API, database, dependency, access-control, subscription, disclaimer, or completed Stage 0–20 behavior was changed during CR-05.

Current active public MVP data:
- Commodity: Egusi.
- Market: Kwali Market.

Inactive but admin-manageable approved records include Beans, Palm oil, Abuja/FCT, Nasarawa, and Benue. Admin commodity and market CRUD remains available.

No further work is authorized until the owner approves the CR-05 final change report.


## CR-05 owner approval and CR-06 authorization — 2026-08-24

The owner explicitly approved CR-05 and CR-06 password show/hide. CR-05 is owner-approved and complete.

## CR-06 Password Visibility — implementation complete; owner proof required — 2026-08-24

Login and Register now have accessible Show/Hide controls. The change affects input presentation only. No database, migration, backend API, authentication, JWT, password hashing, dependency, subscription, access-control, disclaimer, or completed Stage 0–20 feature changed.

Internal focused static verification: PASS.

CR-06 status: IN PROGRESS pending owner production build plus Login/Register/mobile browser verification. No next stage is authorized.


## CR-06 owner static/build proof — 2026-08-24

Owner pulled commit `f15ee6a9fd296a195c8e6e2f6fdc5a63bb5a0892`. The focused CR-06 check ended with `CR-06 STATIC CHECK: PASS`. TypeScript and Vite production build passed: 71 modules transformed in 914 ms.

CR-06 remains IN PROGRESS only for Login/Register Show/Hide browser and narrow/mobile verification. Hosting remains blocked by the approved stage order.


## CR-06 owner visual approval — 2026-08-25

CR-06 is RETESTED/PASS and owner-approved. Login and Register Show/Hide worked, password values remained unchanged, mobile layout was clean, and the login spinner/popup continued working.

## Owner-approved Stage 20–21 suspension and Stage 22 start — 2026-08-25

The owner explicitly instructed PriceYard to suspend Stages 20–21 and host now. Incomplete Stage 20 requirements and Stage 21 are DEFERRED with accepted business/security risk; they are not marked PASS. Stage 24 final acceptance remains blocked until they are resumed and passed.

Stage 22 is IN PROGRESS using Render Static Site for React, Render Free Web Service for FastAPI, and the existing Supabase PostgreSQL database. Deployment-specific CORS preparation is implemented with exact environment-controlled origins and no wildcard.


## Stage 22 Render backend deployment — build/start PASS — 2026-08-25

Render checked out commit `e462deb0fb00154f0b1d2b36dd0c628eb6ed9dd4`, used Python 3.12.8, installed approved dependencies, ran Alembic successfully against PostgreSQL, uploaded the build, and started Uvicorn on Render's assigned port. Render reported the service live at `https://priceyard-api.onrender.com`.

The root-path `404 Not Found` is expected because no `GET /` API is defined. Direct `GET /health` owner verification remains the next proof before the backend portion is marked complete.
# AUTH-01 status — 2026-08-29

Status: IMPLEMENTED AND LOCALLY VERIFIED; production SMTP configuration and deployment verification remain owner actions.

Delivered accessible eye icons, Forgot Password, Reset Password, migration `0007_auth01_password_reset`, generic SMTP delivery, privacy-safe responses, hashed single-use tokens, cooldown, and automated lifecycle tests.

## FIX-01 to FIX-06 — mobile header, approved-price visibility, feedback cleanup, scoped security review — COMPLETE, owner-approved — 2026-08-29

FIX-01 corrected sticky mobile-header/safe-area behavior without a full redesign. FIX-02 kept pending price-update records visible to Admin after refresh and restricted complete Price History to Trial/Paid/Admin, while approved Egusi/Kwali records continued to show publicly and private `source_1`/`source_2` stayed excluded from public responses. FIX-03 simplified the user feedback form to rating, complaint/suggestion, and continue-using, without deleting existing feedback columns. FIX-04 was a scoped real-business security review (bcrypt hashing, JWT/DB secrets in environment variables only, admin-route protection, approved-origin CORS, production debug off, minimum 8-character passwords) — explicitly not a substitute for independent penetration testing. FIX-05 regression-tested the full set. Commits: `7f44216`, `d1d32c8`, `cb1521f`, `646ec3a`, `465541f`, final report `89175e9`.

## NAV-05 / NAV-06 — mobile navigation redesign — COMPLETE, merged — 2026-08

Mobile navigation was redesigned to a three-row layout (brand / primary links / account links) with no hidden menu button and no horizontal scroll, replacing an earlier abandoned `fix/mobile-inline-navigation` attempt. NAV-06 merged via PR #2, merge commit `116a82f`.

## DATA-EDIT-01 — admin price record correction — COMPLETE, merged — 2026-08

Added a "Correct existing price record" form to the existing Admin Price Updates page so a wrong field on an existing record (e.g. a bad Movement value) can be fixed without creating a duplicate or disturbing approval status. Frontend-only change (`AdminPriceUpdatesPage.tsx`), reuses the existing authenticated `PATCH /price-updates/{id}` endpoint and its audit logging. Merged via PR #3, merge commit `6a63aeb`.

## Enhancement Stages 25-30 — admin count, commodity images, Google sign-in, hardening — COMPLETE, owner-confirmed — 2026-09-13

Stage 25 added a total-user count to Admin Users. Stage 26 added an optional `image_url` to commodities (migration `0008`) with a placeholder fallback, shown on price cards and the commodity detail page. Stage 27 added relative "updated X ago" timestamps, movement icons, confidence badges, a trial countdown banner, and friendlier empty-state copy — frontend only. Stage 28 added optional Google sign-in (migration `0009` adds `google_id`/`auth_provider` to `users`; new `POST /auth/google` verifies the ID token server-side and issues the existing JWT; links by verified email or creates a new `free_user` + trial subscription) without changing existing email/password login. Stage 29 hid the subscription-status block on the Dashboard for admin accounts, which had been showing stale trial data. Stage 30 added rate limiting (slowapi, 5/minute per IP) on register/login/google/forgot-password, a guard blocking deactivation or demotion of the last active admin, `image_url` scheme validation (http/https only), and a fix so admin accounts without a subscription row can be edited via `PATCH /users/{id}`. Commits: `f2fcf92`, `243160a` (missing `requests` dependency fix after the first Render deploy crashed).

A related fix made `bag_size` required on new price updates at the backend schema level (several recent records had been saved without it) and added Number-of-bags/Bag-size fields to the admin correction form so existing incomplete records could be fixed. Commit `531063b`.

Two manual/data actions were taken directly against the production database during this stage, outside the normal admin-UI audit trail because no other path existed at the time: a locked-out admin account (the only active admin) was reactivated after a data-state lockout — now prevented from recurring by the Stage 30 last-admin guard — and 16 confirmed-empty test/dev accounts (zero price updates or audit logs) were deleted.

## Enhancement Stages 31-38 — popups, upcoming products, market photos, sharing, PWA, mobile fixes — COMPLETE, owner-confirmed on live production — 2026-09-13

Stage 31 made the shared `AdminStatus` component fire the existing toast popup on every admin success/error, and added popups to Watchlist and Feedback actions. Stage 32 added optional `is_upcoming`/`expected_available_date` to commodities (migration `0010`) and a "Coming Soon" section on Home. Stage 33 added optional `image_url` to markets (migration `0011`), shown on Market Days. Stage 34 added a "Share on WhatsApp" link on price cards and the commodity detail page. Stage 35 added a confidence-level explainer popover, with a mobile-overflow fix (pins as a full-width bottom sheet on narrow screens) applied after live testing caught it clipping off-screen. Stage 36 added a PWA manifest and icons for "Add to Home Screen" (no service worker/offline support). Stage 37 added per-page browser-tab titles. Stage 38, an unplanned fix found during Stage 35's mobile testing, changed Price History to stacked cards instead of a horizontally-scrolling 8-column table on screens ≤640px. Commit `bc8826a`.

Two further mobile issues found during live testing were fixed in the same window: the admin nav tabs now wrap into multiple rows instead of hiding behind an unlabeled horizontal scroll, and Admin Users shows stacked cards instead of a scrolling table on narrow screens. A data-saver toggle (hides all commodity/market images site-wide to cut mobile data use) and an easy-reading toggle (larger text, higher contrast) were added, both persisted per-browser. A Tawk.to live-chat widget was added, then replaced by a floating WhatsApp support button per owner preference (Tawk.to script commented out, not deleted, so it can be restored). Commits `0e17b93`, `c572065`.

A dismissible "Get started with PriceYard" onboarding checklist was added to the Dashboard for new non-admin users, and a live trust-stats strip (commodities tracked / markets covered / approved price records, pulled from real data) was added to Home. Commit `5c3fd2e`.

## Content additions — FAQ and Honey Beans intelligence — 2026-09-14

Ten FAQ entries were drafted from the owner's reference document (Section 27 topics) and published; one resulting duplicate was deleted. Honey Beans price records with a missing bag size were corrected. Honey Beans full-access intelligence (market signal, quality signal, sell-watch window, storage suitability, cost breakdown) was populated from real information the owner provided directly, including a correction to the cost-breakdown purchase-price reference after the owner caught an initial buy-date/price mismatch. Buying Zone was deliberately left blank for Honey Beans since it is not currently a buying period and the feature has no date-based filtering to safely schedule a future entry. These were data/API actions, not code changes.

## Current stage — 2026-09-14

Enhancement Stages 25-38 plus the items above are complete and confirmed on live production (`https://priceyard.onrender.com`) through commit `5c3fd2e`. Stages 20-21 (full access-control correction, full security review) remain owner-deferred from the original execution plan and are unrelated to this work. Remaining open item: rate limiting is in-memory and would need a Redis-backed store if scaled to multiple instances; not a current blocker on a single Render instance.

## Open items closed — 2026-09-14

Account `id=53` (johnadenyumaigiri@gmail.com) confirmed by the owner as a real user, not a test account — no action needed. Render environment variables `GOOGLE_CLIENT_ID` (backend) and `VITE_GOOGLE_CLIENT_ID` (frontend) confirmed present in Render's dashboard by the owner.

## Full live regression pass — PASS — 2026-09-14

Backend checks against `https://priceyard-api.onrender.com`: `/health`, `/commodities`, `/markets`, `/price-updates`, `/faq` all returned `200`. Frontend `https://priceyard.onrender.com` confirmed serving the latest build (`manifest.json` and icons present; Tawk.to script confirmed inactive inside its HTML comment). Owner walked through the live site and confirmed: email/password login, Google sign-in, Data saver/Easy reading toggles, the WhatsApp support button, price-card images/movement icons/confidence badges/WhatsApp share, admin action popups, and mobile admin-nav/Price-History layout all working correctly. No regressions found through commit `5c3fd2e`.

## Stage 39 — Trial-expiry email reminders — 2026-09-14

An admin-triggered action (`POST /subscriptions/send-trial-reminders`, button on Admin > Subscriptions) emails any trial user whose trial ends within 3 days, once per user (`trial_reminder_sent_at` guards against duplicates). Migration `0012_add_trial_reminder`. Commit `3199a8c`.

## Stage 40 — WhatsApp community link — 2026-09-14

A link to the owner's free WhatsApp updates group was added to the Home hero panel and site footer (`WHATSAPP_COMMUNITY_URL` in `frontend/src/utils.ts`). The link was revoked and replaced once mid-stage; the current live link is `https://chat.whatsapp.com/IbDqdO8xhYA9N0fgiP3213?...`. Commit `c14aba4`.

## Infrastructure fix — Supabase connection pool exhaustion — 2026-09-14

While checking the `feedback` table via a local diagnostic script, every attempt failed with `psycopg.OperationalError: FATAL: (EMAXCONNSESSION) max clients reached in session mode - max clients are limited to pool_size: 15`, even after waiting and retrying. The live production site was confirmed unaffected throughout (`/commodities`, `/price-updates` both returned `200`).

Root cause: `backend/app/database.py`'s `create_engine()` call had no explicit `pool_size`/`max_overflow`, so SQLAlchemy applied its defaults (5 + 10 = 15) — exactly Supabase's free-tier session-mode connection cap. With one Render web service running, that single engine could legitimately claim all 15 slots on its own, leaving zero headroom for anything else (migrations, admin scripts, the Supabase SQL editor).

Fix: explicitly capped the engine to `pool_size=3, max_overflow=2, pool_recycle=300` (backend/app/database.py). Verified live: after the change, a fresh diagnostic connection succeeded on the first attempt. See decision log for the considered alternative (switching to Supabase's transaction-mode pooler) and why the in-code cap was chosen instead.

## Stage 41 — Real user testimonials — 2026-09-14

The connection-pool fix above unblocked a re-check of the `feedback` table, which turned up 5 genuine submissions (rating 5/5 each) from 4 distinct real users (ids 53, 54, 55, 56) — the first real feedback since launch. Built a curation workflow rather than auto-publishing:

- `feedback` table gained `is_public_testimonial` (bool, default false) and `testimonial_display_name` (text, nullable) — migration `0013_add_testimonial`.
- Admin-only `PATCH /feedback/{id}/testimonial/publish` (body: `display_name`) and `/testimonial/hide`, both audit-logged; publish is rejected with `400` if the feedback record has no comment/complaint text to show.
- Public, unauthenticated `GET /testimonials` returns only `{id, rating, quote, display_name, created_at}` for records marked public — never the underlying user id or email.
- Admin > Feedback page: each feedback card now has a display-name input and a "Feature as public testimonial" / "Remove from testimonials" control.
- Home page: a "What traders are saying" section renders published testimonials (star rating, quote, display name); the section is hidden entirely when there are none.

Nothing is public yet — the feature ships with all real feedback still unpublished, awaiting the owner's selection of which to feature and what display name to use for each (e.g. first name + initial, per privacy practice already used elsewhere in this doc).

Note: since this stage's initial commit, the owner curated the queue directly against the live database — deleting the test/mismatched entries and keeping one correctly-attributed real testimonial (feedback id changes accordingly; the mechanism above is unchanged).

## Stage 42 — Referral mechanic — 2026-09-15

Every user now gets a unique 8-character referral code (existing users backfilled by migration `0014_add_referral`). Registering with `?ref=CODE` on `/register` (or `referral_code` in the register payload) links the new account to the referrer (`users.referred_by_id`) and immediately rewards the referrer with 7 extra trial days (`subscription_service.apply_referral_reward`, audit-logged against the referrer):

- Trial-status referrers: `trial_ends_at` extended by 7 days from its current value (stacks across multiple referrals).
- Free-status referrers: converted to a fresh 7-day trial.
- Active/expired/cancelled referrers: no reward applied — extra "trial days" has no meaning for those states, so nothing happens rather than doing something arbitrary.
- Invalid referral codes reject registration with `400`, rather than silently ignoring a typo.

`GET /auth/referral-summary` (authenticated) returns the caller's own code, referred-count, and reward-days. Dashboard shows a "Get 7 extra trial days per referral" card with a copy-link button and a WhatsApp share button (reusing the existing `wa.me` share pattern from price sharing). No admin work needed to use this — it runs automatically off existing registration and subscription logic.
