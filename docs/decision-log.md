# AUTH-02 — Use Brevo HTTPS API in hosted environments (2026-08-29)

- Decision: prefer Brevo's transactional email HTTPS API for password-reset delivery on Render.
- Reason: production logs showed `OSError: [Errno 101] Network is unreachable` before Gmail SMTP authentication, while local SMTP delivery passed.
- Scope: email transport only; secure reset-token behavior remains unchanged.
- Fallback: retain the existing SMTP implementation for local or compatible environments.

# Decision Log

## DEC-001 — Stage 0 coding override
- Date: 2026-08-12
- Current requirement: Stage 0 must pass all validation criteria before coding.
- Source: PriceYard Reference Document + AI Project Execution Plan.
- Owner evidence: 65 reached; 14 replies; 5 willing to pay; positive feedback; two source types.
- Exception: Owner stated the 14-day validation completion was mock/form-testing evidence and that independent source confirmation remained later work, while explicitly setting `Application Coding Permission: YES`.
- Decision: Permit Stage 1 to begin under owner-approved business-risk exception.
- Database effect: None.
- API effect: None.
- Frontend effect: None.
- Test effect: Stage 0 final acceptance remains unresolved and must be reconciled before Stage 24.
- Completed-stage effect: None.
- Approval: Owner-approved in conversation.

## DEC-002 — Stage 1 approval and Stage 2 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 1 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: After receiving the Stage 1 PASS report and repository, the owner instructed the AI to continue based on the approved execution plan.
- Decision: Treat the instruction to continue as owner approval of Stage 1 and authorization to execute Stage 2 only.
- Database effect: None.
- API effect: Authorizes only the Stage 2 health endpoint.
- Frontend effect: None.
- Test effect: Stage 2 proof must be completed before Stage 3.
- Completed-stage effect: Stage 1 becomes completed/approved.
- Approval: Owner instruction in conversation.

## DEC-003 — Stage 2 owner approval and Stage 3 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 2 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: `approved` after local dependency installation, Uvicorn startup, and `GET /health` returned HTTP 200 on the owner's computer.
- Decision: Stage 2 is owner-verified and approved. Stage 3 — Database Foundation is authorized.
- Database effect: Authorizes only the approved Stage 3 database foundation.
- API effect: None; no new business API is authorized in Stage 3.
- Frontend effect: None.
- Test effect: Stage 3 requires PostgreSQL connection, migration, table, relationship, and required-field proof before completion.
- Completed-stage effect: Stage 2 becomes completed and owner-approved.
- Approval: Owner-approved in conversation.

## DEC-004 — Stage 3 approval and Stage 4 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 3 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: `approved` after the owner's live Supabase PostgreSQL connection, Alembic migration, table inspection, and `price_updates` field inspection passed.
- Decision: Stage 3 is owner-verified and approved. Stage 4 — Authentication is authorized.
- Database effect: No Stage 4 schema change required; the approved `users` table already contains the required authentication fields.
- API effect: Authorizes only `POST /auth/register`, `POST /auth/login`, and `GET /auth/me` for Stage 4.
- Frontend effect: None.
- Test effect: Stage 4 must prove registration, duplicate rejection, login, wrong-password rejection, inactive-user blocking, JWT handling, `/auth/me`, bcrypt storage, and password-hash non-disclosure.
- Completed-stage effect: Stage 3 becomes completed and owner-approved.
- Approval: Owner-approved in conversation.

## DEC-005 — Stage 4 approval and Stage 5 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 4 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: `STAGE 4 OWNER SMOKE: PASS` with all 17 approved authentication checks passing on the owner's configured Supabase PostgreSQL environment.
- Owner instruction: `continue base on this execution plan here` after the successful Stage 4 smoke proof.
- Decision: Treat the instruction to continue as owner approval of Stage 4 and authorization to execute Stage 5 — Subscription and 14-Day Trial only.
- Database effect: Stage 5 uses the existing `subscriptions` table; no schema change is required unless testing reveals an approved requirement cannot be met.
- API effect: Authorizes only the approved subscription/trial APIs and access-status logic for Stage 5.
- Frontend effect: None.
- Test effect: Stage 5 must prove 14-day trial timing, full/limited access classification, active paid access, invalid-status rejection, and admin subscription update.
- Completed-stage effect: Stage 4 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.

## DEC-006 — Stage 5 approval and Stage 6 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 5 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Corrected `STAGE 5 OWNER SMOKE: PASS` with all 31 approved subscription/trial checks passing on the owner's configured Supabase PostgreSQL environment.
- Owner instruction: `approved`.
- Decision: Stage 5 is RETESTED/PASS and owner-approved. Stage 6 — Admin Core Management is authorized.
- Database effect: No schema change is expected; Stage 6 uses existing `users`, `commodities`, `markets`, and `subscriptions` tables.
- API effect: Authorizes only admin authorization, user management, commodity management, market management, and approved subscription management.
- Frontend effect: None.
- Test effect: Stage 6 must prove non-admin blocking, admin commodity CRUD, admin market CRUD, user management, and subscription management.
- Completed-stage effect: Stage 5 becomes RETESTED/PASS and owner-approved.
- Approval: Owner-approved in conversation.

## 2026-08-12 — Stage 8 query design
Stage 8 extends the existing public `GET /price-updates` endpoint with optional commodity/market/date/movement filters while preserving the no-query Stage 7 behavior. Dedicated `/price-updates/history` and `/price-updates/comparison` endpoints were added because the approved Stage 8 explicitly requires chronological history and comparison. No schema change or new dependency was required.

## DEC-007 — Stage 8 approval and Stage 9 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 8 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: `STAGE 8 OWNER SMOKE: PASS` with commodity search, market/date/movement filters, chronological history, same-day time-of-day records, market comparison, previous/current comparison, Possible Meaning/Suggested Action preservation, and private-source hiding passing on the owner's Supabase-backed environment.
- Owner instruction: `continue base on this execution plan here` after the successful Stage 8 smoke proof.
- Decision: Treat the instruction to continue as owner approval of Stage 8 and authorization to execute Stage 9 — Market Signals and Quality Signals only.
- Database effect: No migration is required; Stage 9 uses the existing `market_signals` and `quality_signals` tables created in Stage 3.
- API effect: Authorizes only the approved market-signal and quality-signal CRUD/view flows.
- Frontend effect: None.
- Test effect: Stage 9 must prove create/edit/view/link validation, access control, observational wording, quality-claim safety, and market-signal disclaimer behavior.
- Completed-stage effect: Stage 8 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.


## DEC-008 — Stage 9 approval and Stage 10 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 9 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: `STAGE 9 OWNER SMOKE: PASS` with market/quality CRUD, link validation, access control, observational wording, quality-claim safety, disclaimer behavior, and separation from price-update meaning/action passing on the owner's Supabase-backed environment.
- Owner instruction: `continue base on this execution plan here`.
- Decision: Treat the instruction to continue as owner approval of Stage 9 and authorization to execute Stage 10 — Buying Zones and Sell-Watch Windows only.
- Database effect: Authorizes the approved Stage 10 migration creating only `buying_zones` and `sell_watch_windows`.
- API effect: Authorizes only the approved Stage 10 create/edit/view flows and their access/safety rules.
- Frontend effect: None.
- Test effect: Stage 10 must prove migration, create/edit/view, invalid-range rejection, access control, and disclaimer behavior.
- Completed-stage effect: Stage 9 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.

## 2026-08-12 — Stage 10 period representation
The approved execution plan defines `start_period` and `end_period` but does not require exact calendar dates. They are stored as short text so observations such as “December ending” and “January upward” can be represented without inventing false date precision. This is an implementation choice within the approved Stage 10 fields, not a product-scope change.

## DEC-009 — Stage 10 approval and Stage 11 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 10 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Alembic upgrade to `0002_stage10_buy_sell_watch` succeeded and `STAGE 10 OWNER SMOKE: PASS` showed migration, required fields, create/edit/view, access control, invalid-range/period rejection, disclaimer behavior, and anti-guarantee wording all passing on the owner's Supabase-backed environment.
- Owner instruction: `if this output is okay, then next`.
- Decision: Stage 10 is RETESTED/PASS and owner-approved. Stage 11 — Storage Suitability only is authorized.
- Database effect: Authorizes one approved migration creating only `storage_suitability`.
- API effect: Authorizes only Stage 11 storage-suitability create/edit/view flows and approved access/safety rules.
- Frontend effect: None.
- Test effect: Stage 11 must prove migration, required fields, create/edit/view, relationships, validation, access control, approved statuses, and storage disclaimer behavior.
- Completed-stage effect: Stage 10 becomes RETESTED/PASS and owner-approved.
- Approval: Conditional owner instruction satisfied by the passing Stage 10 output.

## DEC-010 — Stage 11 approval and Stage 12 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 11 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Database connection PASS, Alembic head `0003_stage11_storage_suitability`, and `STAGE 11 OWNER SMOKE: PASS` after one transient database connection interruption that required no code/schema change.
- Owner instruction: `approved`.
- Decision: Stage 11 is RETESTED/PASS and owner-approved. Stage 12 — Cost Breakdown only is authorized.
- Database effect: Authorizes one approved migration creating only `cost_breakdowns`.
- API effect: Authorizes only Stage 12 cost-breakdown create/edit/view flows needed for the approved MVP.
- Frontend effect: None in Stage 12.
- Test effect: Stage 12 must prove costs save, totals calculate, edits recalculate, negative costs reject, and price-update relationship works.
- Completed-stage effect: Stage 11 becomes RETESTED/PASS and owner-approved.
- Approval: Owner-approved in conversation.

## 2026-08-12 — Stage 12 calculated totals
The approved Stage 12 fields include both component costs and totals. To avoid inconsistent client-supplied totals, `total_additional_cost` and `total_estimated_landing_storage_cost` are calculated by the backend on create and recalculated on edit. This is an implementation choice within the approved Stage 12 scope, not a new accounting feature.


## DEC-011 — Stage 12 approval and Stage 13 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 12 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Alembic upgrade to `0004_stage12_cost_breakdowns` succeeded and `STAGE 12 OWNER SMOKE: PASS` showed migration, required fields, cost saving, total calculation/recalculation, negative-cost rejection, relationship behavior, and access control all passing on the owner's Supabase-backed environment.
- Owner instruction: `see if output okay then next`.
- Decision: The passing output satisfies the owner's condition. Stage 12 is RETESTED/PASS and owner-approved. Stage 13 — Watchlist only is authorized.
- Database effect: Authorizes one approved migration creating only `watchlists`.
- API effect: Authorizes only save/list/remove own watchlist flows. Target-price alerts remain deferred.
- Frontend effect: None in Stage 13.
- Test effect: Stage 13 must prove commodity/market saves, own-list behavior, duplicate handling, cross-user isolation, and removal.
- Completed-stage effect: Stage 12 becomes RETESTED/PASS and owner-approved.
- Approval: Conditional owner instruction satisfied by the passing Stage 12 output.

## 2026-08-12 — Stage 13 target-price field boundary
The approved Architecture Design includes nullable `target_price` in the `watchlists` table, while the Execution Plan explicitly defers target-price alerts. Stage 13 therefore retains the architecture-approved database column for compatibility but does not accept target-price API input and does not implement any alert behavior. This preserves both approved documents without expanding MVP functionality.

## DEC-012 — Stage 13 approval and Stage 14 authorization
- Date: 2026-08-13
- Current requirement: Do not proceed from Stage 13 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Alembic upgrade to `0005_stage13_watchlists` succeeded and `STAGE 13 OWNER SMOKE: PASS` showed commodity/market saves, duplicate handling, own-list isolation, cross-user protection, removal, target-price deferral, and SQLAlchemy relationships all passing on the owner's Supabase-backed environment.
- Owner instruction: `continue base on this execution plan here` after returning from the documented Stage 13 checkpoint.
- Decision: Treat the instruction to continue as owner approval of Stage 13 and authorization to execute Stage 14 — FAQ only.
- Database effect: No migration; Stage 14 reuses the approved `faq_items` table created in Stage 3.
- API effect: Authorizes FAQ create/edit/publish/hide plus the Architecture-approved delete operation, and public viewing of published FAQ items.
- Frontend effect: None in Stage 14.
- Test effect: Stage 14 must prove create/edit/publish/hide/delete, public visibility rules, unauthorized management blocking, content-safety behavior, and disclaimer preservation.
- Completed-stage effect: Stage 13 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.

## 2026-08-13 — Stage 14 publication boundary
New FAQ records start hidden and publication state is changed only through the approved publish/hide actions. This keeps accidental drafts out of public FAQ responses. Public FAQ responses omit creator and publication-control fields. The paid-group word-for-word rule remains a human/editorial source-check because no paid-source corpus is stored for automated comparison.


## DEC-013 — Stage 14 approval and Stage 15 authorization
- Date: 2026-08-13
- Current requirement: Do not proceed from Stage 14 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Alembic remained at `0005_stage13_watchlists` as expected and `STAGE 14 OWNER SMOKE: PASS` showed FAQ create/edit/publish/hide/delete, public visibility, unauthorized management blocking, safety validation, disclaimer preservation, and relationships passing on the owner's Supabase-backed environment.
- Owner instruction: `continue 15`.
- Decision: Treat the instruction as explicit approval of Stage 14 and authorization to execute Stage 15 — User Feedback and 1–5 Star Rating only.
- Database effect: No migration; Stage 15 reuses the approved `feedback` table created in Stage 3.
- API effect: Authorizes authenticated user feedback submission plus admin list/filter/detail/basic summary. The Architecture-approved feedback delete endpoint is included.
- Frontend effect: None in Stage 15.
- Test effect: Stage 15 must prove ratings 1 and 5 work, 0 and 6 fail, user linkage works, admin view/filter/basic summary work, and ordinary users cannot browse all private feedback.
- Completed-stage effect: Stage 14 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.

## 2026-08-13 — Stage 15 summary boundary
The Execution Plan permits only basic feedback count/average and explicitly forbids advanced analytics. Stage 15 therefore exposes only total count and average rating in the admin summary.

## 2026-08-13 — Stage 18 local frontend/backend integration
- Decision: use Vite's local `/api` development proxy for Stage 18 instead of changing backend production CORS behavior early.
- Reason: Stage 18 requires local React/FastAPI integration; production allowed-origin configuration is explicitly part of the later security/deployment stages.
- Scope: frontend development only. `VITE_API_URL` is reserved for the deployed FastAPI base URL.
- No database/API contract change results from this decision.

## 2026-08-13 — Stage 18 Chrome verification-helper correction
- Current requirement: Stage 18 requires browser/mobile verification before approval.
- Source: PriceYard AI Project Execution Plan, Stage 18 and Change Control Rule.
- Owner proof before change: frontend production build, FastAPI health, Vite proxy, and frontend dev server passed; Windows Chrome headless `--dump-dom` timed out.
- Proposed/approved change: modify only `docs/evidence/stage-18-owner-smoke.py` to use isolated temporary Chrome profiles, `--headless=new`, noninteractive/background-reduction flags, and a 45-second browser timeout.
- Reason: remove Windows Chrome profile/process interference from the verification helper without changing PriceYard product code.
- Database effect: None.
- API effect: None.
- Frontend effect: None.
- Test effect: Stage 18 browser/mobile verification helper only.
- Completed-stage effect: None.
- Approval: Owner explicitly said `approved chrome test fix`.

## 2026-08-18 — Stage 20 access-control assessment before correction
- Decision: Start Stage 20 only after explicit owner approval of Stage 19.
- Decision: Create the access-control matrix and run a no-behavior-change assessment before editing routes/schemas.
- Finding: Existing full-access and admin/inactive controls pass static inspection, but Guest public-price payload depth, limited market-signal payload depth, and quality-signal access do not yet meet the approved Stage 20 limited/full separation.
- Decision: Stop under Change Control and request owner approval before changing those existing API response/access behaviors.

## 2026-08-24 — CR-01 global loading spinner authorization and boundary

- Owner instruction: `approve CR-01`.
- Decision: Implement only the approved shared loading spinner and waiting-state coverage; stop before CR-02 popup work.
- Implementation: Add one shared lightweight spinner module and reuse existing `loading`/`busy` state patterns across public, authenticated and admin frontend flows.
- Database effect: None.
- API effect: None.
- Frontend effect: Page/data loaders, optional full-page overlays and disabled button spinners using the approved PriceYard colors.
- Test effect: Require a passing TypeScript/Vite production build and focused static coverage check. Owner-side browser verification remains required because the cloud browser cannot access the local Vite address.
- Completed-stage effect: None; existing Stage 0–20 implementation is preserved.
- Scope boundary: No success popup, active-data reset, dependency, theme redesign or future feature is included.

## 2026-08-24 — CR-01 owner verification and CR-02 authorization

- Owner proof: `DATABASE_URL loaded: True`, `JWT_SECRET loaded: True`, `database connection: PASS`, and successful `200 OK` requests for price updates, markets, price history, and FAQ.
- Owner visual result: `all i clicked spined stylishly`.
- Decision: CR-01 is RETESTED/PASS and owner-approved.
- Owner instruction: `CONFIRM if okay, continue`.
- Authorization: Begin CR-02 Success Confirmation Popups only. CR-03 remains blocked until CR-02 implementation, testing, proof, owner verification, and approval.

## 2026-08-24 — CR-02 shared popup boundary

- Search finding: No existing toast, notification, or popup system exists; only page-local status boxes are present.
- Decision: Add one small shared `Toast` component/context without installing a UI library.
- Behavior: Clear the existing busy/spinner state, yield a browser paint, trigger the success/error popup, then preserve the approved redirect flow.
- Database/API/dependency effect: None.
- Scope boundary: Only login, registration, and logout authentication feedback is changed. CR-03 data reset remains blocked pending CR-02 owner verification and approval.

## 2026-08-24 — CR-02 owner verification and CR-03 authorization

- Owner proof: successful login/account/subscription API responses, wrong-login `401`, duplicate-registration `409`, and the explicit statement `CR-02 visual verification PASS — login, error, registration and logout popups all worked.`
- Decision: CR-02 is RETESTED/PASS and owner-approved.
- Owner instruction: Continue under the approved PriceYard Change Execution Plan.
- Authorization: Begin CR-03 Active MVP Data Reset only. CR-04 remains blocked until CR-03 implementation, testing, proof, owner verification, and approval.

## 2026-08-24 — CR-03 active-data implementation boundary

- Audit finding: Commodity and Market already contain indexed `is_active` fields and existing admin CRUD supports their update; no new column is required.
- Decision: Use one Alembic data revision to ensure canonical Egusi/Kwali records, deactivate other records without deleting them, and preserve all relationships/history.
- Public behavior: Active-only catalog and approved-price queries; Prices filters use those active catalogs.
- Admin preservation: Add protected all-record catalog/history reads so inactive records remain manageable/reactivatable and completed admin work is not removed.
- Database effect: Activity-flag data only; no table/column/record deletion and no user/subscription/auth/audit mutation.
- API effect: Add three admin-protected reads and narrow public reads to active references.
- Frontend effect: Active catalog selects and protected admin all-record paths only.
- Test effect: Static/build checks pass; real owner PostgreSQL migration/runtime/browser proof is required.
- Scope boundary: CR-04 regression testing and CR-05 final reporting remain blocked.


## 2026-08-24 — CR-03 approval and CR-04 authorization

- Owner proof: Alembic reached `0006_cr03_egusi_kwali`; `CR-03 OWNER SMOKE: PASS`; final database query showed Egusi active, Beans/Palm oil inactive, Kwali Market active, and the other approved markets inactive.
- Repair note: Temporary browser-test deletions of inactive commodity rows and the Kwali row were detected from runtime logs and repaired. Final state was reverified before approval.
- Decision: CR-03 is RETESTED/PASS and owner-approved.
- Owner instruction: Continue if the corrected output is okay.
- Authorization: Start CR-04 Regression Testing only.
- Database effect: No new database change is authorized in CR-04.
- API/frontend effect: Verification only; no behavior change is authorized unless a regression is proven and separately approved.
- Test effect: Run existing CR-01/02/03 checks, production build, focused PostgreSQL/API regression, and owner browser checklist.
- Scope boundary: CR-05 remains blocked until CR-04 proof and owner approval.


## 2026-08-24 — CR-04 evidence-helper correction

- Failure: CR-01 checker falsely required `finally` in Login/Register; CR-04 helper gave no progress during a prolonged PostgreSQL/API wait.
- Current implementation: Login/Register explicitly clear busy state in success and error paths before popup display, as required and already proven by CR-02.
- Decision: Change evidence utilities only. Count the two explicit cleanup paths, print each regression phase/result immediately, and add a helper-only 15-second PostgreSQL connection timeout.
- Database/API/frontend product effect: None.
- Test effect: False failure removed and future stalls become bounded/locatable.
- Completed-stage effect: None; CR-01/02/03 product implementations remain unchanged.
- Approval basis: Owner reported the stuck verification run and requested continuation under CR-04 fix/retest rules.


## 2026-08-24 — CR-04 browser proof accepted and CR-05 authorized

- Current requirement: finish CR-04 regression proof before moving to CR-05.
- Evidence reviewed: successful backend startup; registration `201`; valid login `200`; intentional wrong login `401`; profile/subscription, public catalog/price, protected admin, feedback-summary, and watchlist reads `200`.
- Decision: CR-04 is RETESTED/PASS. The owner's conditional instruction to continue when the output was okay authorizes CR-05 documentation.
- Scope: verification and governance only; no application, API, schema, dependency, access, subscription, disclaimer, or product-scope change.

## 2026-08-24 — CR-05 final change report

- Decision: record CR-00 through CR-04 results in one final evidence report and request owner approval.
- Active public data remains Egusi and Kwali Market only.
- Admin can still view/manage inactive records and add/reactivate commodities and markets.
- No unapproved feature was added and no completed Stage 0–20 work was removed.
- Next gate: owner approval of CR-05 before any other work.


## 2026-08-24 — CR-05 approval and CR-06 password visibility authorization

- Owner instruction: `Approve CR-05 and approve CR-06 password show/hide`.
- Decision: CR-05 is owner-approved and complete. CR-06 only is authorized.
- Current requirement: Login and Register currently hide passwords with no visibility control.
- Source: owner-approved change under the Execution Plan Change Control Rule.
- Proposed change: accessible Show/Hide controls on Login and Register.
- Reason: let users verify typed passwords without changing authentication security.
- Database effect: none.
- API/backend effect: none.
- Frontend effect: local visibility state and shared CSS only.
- Test effect: hidden default, show/hide, value preservation, non-submit behavior, accessibility, build, auth regression, and mobile verification.
- Completed-stage effect: none; CR-01 spinner and CR-02 popup flows remain intact.
- Scope boundary: no password reset, strength meter, confirm-password field, icon package, auth policy, Stage 20 correction, Stage 21, or deployment work.


## 2026-08-24 — CR-06 owner static/build proof

- Focused password-visibility check: PASS.
- TypeScript/Vite production build: PASS; 71 modules transformed in 914 ms.
- Decision: implementation and compiled proof pass.
- Remaining gate: owner Login/Register/mobile browser verification.
- Stage effect: CR-06 is not yet owner-approved; Stage 20 reconciliation, Stage 21 and Stage 22 remain blocked.


## 2026-08-25 — CR-06 approval

- Owner proof: Login/Register Show/Hide worked, values remained unchanged, mobile layout was clean, and login spinner/popup still worked.
- Decision: CR-06 is RETESTED/PASS and owner-approved.
- Database/API/dependency/security-policy effect: none.

## 2026-08-25 — Owner suspension of Stages 20–21 and Stage 22 authorization

1. Current requirement: complete Stage 20 access control and Stage 21 full security testing before Stage 22; frontend host was Vercel.
2. Source: PriceYard AI Project Execution Plan, Stages 20–22 and Change Control Rule.
3. Approved change: suspend incomplete Stages 20–21, begin Stage 22 now, and use Render for both frontend and backend with Supabase PostgreSQL.
4. Database effect: no schema/data change; existing Supabase database remains.
5. API effect: add exact-origin, environment-controlled CORS required for the separately hosted frontend.
6. Frontend effect: deploy existing React build with `VITE_API_URL` set to the Render backend URL.
7. Test effect: deployment-specific health, database, auth, admin, price, FAQ, subscription, feedback, mobile and HTTPS checks remain required; full Stage 21 remains deferred.
8. Completed-stage effect: none; incomplete Stage 20 is not relabeled as passed.
9. Risk accepted: public pilot deployment occurs before unresolved access-depth corrections and the full security review; Render/Supabase free-tier cold-start/pause limitations apply.
10. Approval: owner explicitly stated `suspend the stage 20-21 and host now`.

Scope boundary: no marketplace, payment, AI prediction, alert, logistics, or other future feature is authorized. Stage 24 cannot pass while Stages 20–21 remain deferred.


## 2026-08-25 — Stage 22 Render backend build/start result

- Build command completed and Alembic connected to PostgreSQL successfully.
- Uvicorn application startup completed on Render.
- Primary URL: `https://priceyard-api.onrender.com`.
- Root `404`: expected; no root endpoint exists.
- Next proof: owner opens `/health`, then deploys the React Static Site.
# AUTH-01 — Secure password recovery (2026-08-29)

- Replaced password visibility text controls with accessible eye icons.
- Added generic SMTP configuration through environment variables; no provider secret is stored in Git.
- Reset tokens are random, stored only as SHA-256 hashes, expire after 15 minutes, and are single-use.
- Responses do not disclose whether an email address is registered.
- Existing login, registration, JWT, roles, subscriptions, and admin features remain unchanged.

## 2026-08-29 — FIX-02 pending-visibility and history-access split

- Problem found: Admin's price-update history query was dropping pending records on refresh, so newly submitted updates could be lost before approval; complete Price History also needed stronger enforcement than "logged in."
- Decision: keep all statuses (pending/approved/rejected) in the admin history read so nothing is lost, while gating the separate complete-history endpoint behind Trial/Paid/Admin access specifically — two different fixes for two different problems, not one combined change.
- Reason: conflating "admin needs to see everything" with "public needs to see less" would have either hidden pending work from admin or over-exposed history to free/guest users.
- Scope: backend query/authorization only; no schema change.

## 2026-08 — NAV-06 three-row mobile navigation (replacing a hidden menu button)

- An earlier attempt (`fix/mobile-inline-navigation`, abandoned) tried to expose icons inline and hit CSS cascade problems.
- Decision: replace the hidden hamburger-menu pattern entirely with three always-visible rows (brand / primary links / account links) rather than fixing the hidden menu.
- Reason: a menu the user has to discover and tap costs an extra step on every visit; showing links directly costs vertical space but removes that friction, which matters more on a page people check daily for prices.

## 2026-08 — DATA-EDIT-01: correction vs new record as two distinct workflows

- Decision: a price-history record with a genuine data-entry mistake (e.g. wrong Movement value) gets corrected in place via a new "Correct existing price record" form; a genuinely new market price gets a brand-new record, never an edit of an old one.
- Reason: PriceYard's price history is only trustworthy if past records reflect what the market actually did at that time. Silently editing an old price to match a new market reality would erase real history; not being able to fix a typo at all would leave permanent noise in the data. Both needed a distinct, clearly-labeled path so an admin (or a future AI) doesn't reach for the wrong one.

## 2026-09-13 — Stage 30: guard the last active admin instead of just warning

- Trigger: mid-session, the only active admin account was found deactivated with no other active admin able to reactivate it through the UI — required a direct one-off database fix to recover.
- Decision: add a hard backend guard (`409`) that refuses to deactivate or demote the last active admin, rather than just documenting "don't do this."
- Reason: a warning doesn't prevent an accidental click, a bad bulk edit, or a future AI session doing it unknowingly. A structural guard makes the lockout scenario unreachable through the normal app, which is cheaper than ever needing the manual DB recovery again.

## 2026-09-13 — Stage 30/32: `bag_size` required, but `is_upcoming` display not date-filtered

- `bag_size` was optional and several real price records had been saved without it, leaving users unable to see how much a bag actually weighs. Made required at the backend schema level (not just the form) going forward, and added it to the correction form so existing gaps could be fixed retroactively.
- Separately, the "Coming Soon" (upcoming-product) feature was built to display immediately regardless of `valid_from`/`valid_to` — there is no date-based filtering on it. This was a deliberate scope cut for Stage 32 (out of scope: "notifications, ranking/ordering logic"), not an oversight, but it has a consequence: a Buying Zone entry has the same lack of date filtering, so a future/anticipated buying zone must never be entered before its window actually opens — it would display as active immediately. Documented here so a future AI doesn't "helpfully" schedule one early.

## 2026-09-13 — Tawk.to replaced with a WhatsApp support button

- Tawk.to (free live-chat widget) was built and shipped first, per owner request.
- Owner then asked to switch to a WhatsApp-based support button instead, and asked whether running both together was wise.
- Decision/reasoning given: recommended against running both. The real risk of two support channels isn't UI clutter, it's staffing — PriceYard is currently a one-person operation, and an unanswered second inbox looks worse to users than not offering it at all. WhatsApp was already the channel being reliably staffed, so it became the sole channel.
- Implementation choice: the Tawk.to `<script>` block was commented out in `index.html`, not deleted, specifically so it can be restored in one line if the calculus changes later (e.g. a support hire).

## 2026-09-13/14 — Commodity/market intelligence: real data only, verified before publishing

- When asked to fill in blank "Market signals / Quality readiness / Buying zone / Sell-watch window / Storage suitability" sections for Honey Beans, the request was to enter real, owner-supplied observations transcribed into the correct admin forms — not to fabricate plausible-sounding content to make the page look complete.
- Reason: PriceYard's reference document explicitly treats fabricated or unverified market intelligence as a core product risk ("Do not publish paid group content... without independent verification"). An AI assistant filling gaps with invented numbers would violate that rule as surely as a human reporter would.
- Applied consequence: a cost-breakdown entry was initially created referencing the current (September) market price alongside a packaging cost that only applies at the November-December buying time; the owner caught the mismatch and it was corrected to reference the actual buy-time price. Recorded here because it's a useful pattern: cost/price fields must stay internally time-consistent, not just individually plausible.

## 2026-09-13 — Google OAuth: existing Cloud project reused, not a dedicated one

- The Google OAuth Client ID for Sign-in with Google was created under the owner's existing `stripe-revenue-copilot` Google Cloud project, not a new dedicated PriceYard project.
- Reason: no functional requirement for a separate project at MVP scale; OAuth Client IDs are project-scoped credentials, not data-scoped, so this carries no data-mixing risk. Noted here only so a future cleanup pass isn't surprised by the project name.
