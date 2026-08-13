# Stage 17 Build Report — Simple CSV Report Export

## Requirement
Build one simple CSV export filtered by commodity, market, and date range. Export approved price intelligence fields including current/previous ranges, movement, date/time, confidence, Possible Meaning, Suggested Action, and approved/linked signals. Do not export secrets, password hashes, JWT data, private source identities, or unnecessary personal data. PDF reporting remains deferred.

## Implementation
- Added `backend/app/services/report_export_service.py`.
- Added `backend/app/routes/report_export_routes.py`.
- Registered the Stage 17 router in `backend/app/main.py`.
- Added admin-only `GET /reports/prices.csv`.
- Added optional commodity, market, `date_from`, and `date_to` filters.
- CSV rows come only from approved price updates.
- CSV includes current/previous ranges, movement, update date/time, confidence, Possible Meaning, Suggested Action, linked market signals, and linked quality signals.
- Private `source_1`/`source_2` values and user/security data are excluded.
- No database schema change or new dependency is required; Python standard-library `csv` is used.

## Internal proof
- Python compile check: PASS.
- Static contract/scope check: PASS.
- Temporary SQLite service/filter/CSV-content check: PASS.
- Temporary SQLite full FastAPI/API smoke with an internal bcrypt compatibility stub: PASS; build evidence only, not owner/Supabase proof.
- Alembic repository head remains `0005_stage13_watchlists`.

## Internal command correction
One restricted-header verification command was first invoked from the repository root without `PYTHONPATH=backend`, causing an import-path-only `ModuleNotFoundError: app`. No application code failed and no code change was required. The command was rerun with the correct import path and passed.

## Owner proof required
Run `docs/evidence/stage-17-owner-smoke.py` against the configured Supabase PostgreSQL environment. Stage 17 is not complete until the owner smoke ends with `STAGE 17 OWNER SMOKE: PASS` and the owner approves continuation.

## Scope guard
No migration, PDF export, report-storage table, advanced analytics, frontend, payment, alert, AI prediction, marketplace, or other later-stage feature was added.
