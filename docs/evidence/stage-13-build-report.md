# Stage 13 Build Report — Watchlist

Status: BUILT / IN PROGRESS — owner Supabase migration and runtime smoke verification required.

Implemented:
- `watchlists` model and Alembic revision `0005_stage13_watchlists`.
- `POST /watchlist` to save a commodity, market, or commodity+market combination for the authenticated user.
- `GET /watchlist` to list only the authenticated user's items.
- `DELETE /watchlist/{item_id}` to remove only the authenticated user's item.
- Active commodity/market validation.
- Empty-selection rejection.
- Duplicate-item handling with HTTP 409.
- Cross-user isolation.
- Relationships from user, commodity, and market.

Architecture compatibility:
- The approved architecture listed nullable `target_price` on `watchlists`. The database field is retained for later work, but Stage 13 neither accepts target-price input nor implements target-price alerts.

Internal evidence:
- compileall: PASS.
- migration chain through `0005_stage13_watchlists`: PASS on temporary SQLite.
- required field inspection: PASS.
- service create/list/duplicate/delete checks: PASS.
- scope check: PASS.

No Stage 14 or later feature was implemented.
