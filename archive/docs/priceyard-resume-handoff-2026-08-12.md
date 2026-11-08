# PriceYard Resume Handoff — 2026-08-12

## Source of truth
Continue using, in authority order:
1. `docs/priceyard-reference-document.md`
2. `docs/architecture-design.md`
3. `docs/ai-project-execution-plan.md`

Always follow one-stage-at-a-time execution and Change Control.

## Current checkpoint
- Latest cumulative repository: Stage 9.
- Stage 9 owner smoke: RETESTED/PASS on 2026-08-12.
- Stage 9 is not yet owner-approved for progression.
- Resume point: owner approves Stage 9, then begin Stage 10 only.

## Completed progression
- Stage 0: owner-approved coding exception; business validation evidence remains partially unresolved for final audit.
- Stage 1: Project Setup — PASS / approved.
- Stage 2: Backend Foundation — RETESTED/PASS / approved.
- Stage 3: Database Foundation — RETESTED/PASS / approved.
- Stage 4: Authentication — RETESTED/PASS / approved.
- Stage 5: Subscription and 14-Day Trial — RETESTED/PASS / approved.
- Stage 6: Admin Core Management — RETESTED/PASS / approved.
- Stage 7: Price Updates — RETESTED/PASS / approved.
- Stage 8: Search, Filters, History, Comparison — RETESTED/PASS / approved.
- Stage 9: Market Signals and Quality Signals — RETESTED/PASS; awaiting owner approval.

## Stage 9 verified scope
- Market signal create/edit/view/list/delete.
- Quality signal create/edit/view/list/delete.
- Admin-only management.
- Active authenticated user viewing at current backend stage.
- Optional validated `price_update_id` links.
- Signal Possible Meaning/Suggested Action kept separate from price-update Possible Meaning/Suggested Action.
- Guaranteed/predictive financial wording rejected.
- Unsupported laboratory claims rejected.
- Required market-signal disclaimer returned.
- No Stage 10 feature, migration, chart, payment, reporter workflow, AI prediction or new dependency added.

## Important outstanding project issue
Stage 0 still has two items that were not independently proven as originally written:
1. full 14-day validation duration;
2. at least two reliable independent price sources.
The owner explicitly allowed coding to proceed despite this business-validation risk. Stage 24 must reconcile it before final acceptance.

## Remaining stages
- Stage 10: Buying Zones and Sell-Watch Windows.
- Stage 11: Storage Suitability.
- Stage 12: Cost Breakdown.
- Stage 13: Watchlist.
- Stage 14: FAQ.
- Stage 15: User Feedback and 1–5 Star Rating.
- Stage 16: Audit Logs.
- Stage 17: Simple CSV Report Export.
- Stage 18: Public and User Frontend MVP.
- Stage 19: Admin Frontend MVP.
- Stage 20: Access Control and Subscription Testing.
- Stage 21: Full MVP Testing and Security Review.
- Stage 22: Deployment.
- Stage 23: Pilot Launch.
- Stage 24: Final Acceptance Audit.

## Exact place to resume
Do not rebuild or rerun Stages 1–8 unless a bug/integration requirement demands it.

First action after resuming:
1. Confirm Stage 9 owner approval.
2. Read Stage 10 requirements from the approved Execution Plan.
3. Build only Stage 10.
4. Stage 10 will require migrations for `buying_zones` and `sell_watch_windows` because those tables were intentionally deferred at Stage 3.
5. Test/prove/fix/retest/update traceability/project status/commit.
6. Stop and request owner approval before Stage 11.

## Stage 10 required scope reminder
Buying zones:
- commodity
- market
- price_low
- price_high
- reason
- valid_from
- valid_to
- confidence
- created_by
- timestamps

Sell-watch windows:
- commodity
- market
- start_period
- end_period
- observation
- confidence
- created_by
- timestamps

Rules:
- not price prediction;
- not guaranteed lowest price;
- not guaranteed profit window;
- required disclaimer behavior must be tested.

## Security / workflow reminders
- `.env` must remain outside Git and ZIP snapshots.
- Never paste real database/JWT secrets into chat.
- Backend authorization remains the authority.
- No deferred feature may be added without approval.
- Fix the smallest affected area; do not rewrite working modules unnecessarily.
