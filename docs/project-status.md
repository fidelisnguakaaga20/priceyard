# PriceYard Project Status

## Current stage
Stage 15 — User Feedback and 1–5 Star Rating — BUILT/IN PROGRESS; awaiting owner Supabase-backed runtime verification before Stage 16.

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

## Next gate
Stage 15 — User Feedback and 1–5 Star Rating is BUILT/IN PROGRESS and awaits owner Supabase-backed runtime verification. Do not start Stage 16 until Stage 15 passes and the owner explicitly approves.
