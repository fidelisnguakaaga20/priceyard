# Stage 12 Build Report — Cost Breakdown

Status: BUILT/IN PROGRESS pending owner Supabase-backed verification.

Implemented:
- `cost_breakdowns` SQLAlchemy model.
- Alembic revision `0004_stage12_cost_breakdowns`.
- Required Stage 12 fields.
- Required relationship to `price_updates`.
- Admin create/edit routes and full-access view routes.
- Backend-calculated `total_additional_cost`.
- Backend-calculated `total_estimated_landing_storage_cost`.
- Recalculation after edits.
- API and database rejection of negative amounts.
- ORM/database cascade keeps the existing Stage 7 incorrect-price deletion flow compatible when a linked cost breakdown exists.
- Owner smoke script.

Not implemented:
- full accounting system;
- complex average-cost calculator;
- Stage 13 watchlist;
- any later/deferred feature.

Internal evidence:
- compilation PASS;
- migration PASS on temporary SQLite;
- required column inspection PASS;
- save/totals/edit/recalculation/relationship service checks PASS;
- negative-input validation PASS;
- linked price-update deletion integration check PASS.

Owner proof still required:
1. copy existing `.env` into Stage 12 backend;
2. `python -m alembic upgrade head`;
3. `python ../docs/evidence/stage-12-owner-smoke.py`;
4. final expected line: `STAGE 12 OWNER SMOKE: PASS`.
