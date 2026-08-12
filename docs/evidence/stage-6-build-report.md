# Stage 6 Build Report — Admin Core Management

Status: BUILT / AWAITING OWNER LOCAL VERIFICATION

## Requirements implemented
- admin authorization on management mutations and user administration;
- user list/view/role/active-state management;
- commodity CRUD;
- market CRUD;
- reuse of approved subscription management;
- approved initial commodity/market verification in owner smoke;
- only verified market days are populated by the Stage 6 owner verifier.

## Database changes
None. No migration was created.

## APIs added
- GET /users
- GET /users/{user_id}
- PATCH /users/{user_id}
- GET/POST /commodities
- GET/PATCH/DELETE /commodities/{commodity_id}
- GET/POST /markets
- GET/PATCH/DELETE /markets/{market_id}

Stage 5 subscription APIs remain in place.

## Build tests
- Python compileall: PASS
- static admin protection/route/scope checks: PASS

## Runtime proof still required
Run `docs/evidence/stage-6-owner-smoke.py` on the owner's machine against the configured Supabase PostgreSQL database. Stage 6 must not be marked PASS until that script completes with `STAGE 6 OWNER SMOKE: PASS`.

## Scope confirmation
No price-update API, signal API, buying-zone API, storage-suitability API, cost API, watchlist, FAQ management, feedback management, audit implementation, CSV export, frontend, payment gateway, reporter workflow, AI feature, marketplace, Redis, GraphQL, or other unapproved future feature was added.
