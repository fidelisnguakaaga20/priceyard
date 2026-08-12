# API Endpoints

## Stage 2 — Backend Foundation

### GET /health

Purpose: verify that the PriceYard FastAPI backend is running.

Authentication: none.

Expected successful response:

```json
{"status":"healthy"}
```

Owner-verified in Stage 2 with HTTP 200.

## Stage 3 — Database Foundation

No new public/business API endpoint is introduced in Stage 3.

Stage 3 adds only the approved PostgreSQL/SQLAlchemy/Alembic database foundation and model schema.

## Stage 4 — Authentication

### POST /auth/register

Purpose: create a normal PriceYard user account.

Authentication: none.

Input:
- `full_name`
- `email`
- optional `phone`
- `password`

Rules:
- email must be unique;
- phone must be unique when supplied;
- password is stored only as a bcrypt hash;
- public registration always assigns `free_user`;
- password/hash is never returned.

### POST /auth/login

Purpose: authenticate an active user and issue a JWT access token.

Authentication: none.

Input:
- `email`
- `password`

Rules:
- invalid credentials return 401;
- inactive users are blocked;
- successful login returns a bearer JWT.

### GET /auth/me

Purpose: return the authenticated user's safe account profile.

Authentication: bearer JWT required.

Rules:
- missing/invalid/expired JWT is rejected;
- inactive users are blocked;
- password/hash is never returned.

## Later approved stages

Commodity, market, price, signal, quality, FAQ, feedback and broader admin APIs remain unimplemented until their approved stages.

## Stage 5 — Subscription and 14-Day Trial

### GET /subscriptions
Purpose: list subscription records for manual administration.
Authentication: admin bearer JWT required.

### GET /subscriptions/{user_id}
Purpose: return one user's subscription/trial record.
Authentication: bearer JWT required. A normal user may view only their own record; admin may view any user's record.

### PATCH /subscriptions/{user_id}/status
Purpose: manually set an approved subscription status.
Authentication: admin bearer JWT required.

Allowed statuses:
- `free`
- `trial`
- `active`
- `expired`
- `cancelled`

Stage 5 rules:
- normal public registration creates a 14-day trial subscription;
- trial status gives full-access classification only until `trial_ends_at`;
- an expired trial transitions to `expired` and the user remains/returns `free_user`;
- `active` is the paid/full-access status and assigns `paid_user` for a normal user;
- `free`, `expired`, and `cancelled` are limited-access statuses;
- payment gateway integration remains deferred.

## Stage 6 — Admin Core Management

### GET /users
Purpose: list PriceYard users for administration.
Authentication: admin bearer JWT required.

### GET /users/{user_id}
Purpose: view one user's safe account details.
Authentication: admin bearer JWT required.
Rule: password hashes are never returned.

### PATCH /users/{user_id}
Purpose: change an approved MVP role and/or activate/deactivate a user.
Authentication: admin bearer JWT required.
Allowed roles: `admin`, `free_user`, `paid_user`.
Reporter remains deferred.
Role/subscription consistency:
- `paid_user` synchronizes to active paid subscription status;
- `free_user` synchronizes to free subscription status;
- `admin` grants administration role directly.

### GET /commodities
Purpose: view commodities.
Authentication: none.

### GET /commodities/{commodity_id}
Purpose: view one commodity.
Authentication: none.

### POST /commodities
Purpose: add a commodity.
Authentication: admin bearer JWT required.

### PATCH /commodities/{commodity_id}
Purpose: edit a commodity.
Authentication: admin bearer JWT required.

### DELETE /commodities/{commodity_id}
Purpose: delete a commodity when it is not referenced by dependent records.
Authentication: admin bearer JWT required.

Initial approved commodities:
- Egusi
- Beans
- Palm oil

### GET /markets
Purpose: view markets.
Authentication: none.

### GET /markets/{market_id}
Purpose: view one market.
Authentication: none.

### POST /markets
Purpose: add a market.
Authentication: admin bearer JWT required.

### PATCH /markets/{market_id}
Purpose: edit a market.
Authentication: admin bearer JWT required.

### DELETE /markets/{market_id}
Purpose: delete a market when it is not referenced by dependent records.
Authentication: admin bearer JWT required.

Initial approved markets:
- Abuja/FCT — market day not set unless independently verified
- Kwali Market — Tuesday
- Nasarawa — Monday
- Benue — market day not set unless independently verified

Stage 6 reuses the Stage 5 subscription management APIs. No new payment behavior is introduced.

## Stage 7 — Price Updates

### GET /price-updates
Purpose: return the latest approved, current price record for each commodity/market pair.
Authentication: none at Stage 7; full access-tier enforcement is tested in the approved later access-control stage.
Public privacy rule: `source_1` and `source_2` are never returned.
Stage boundary: this is a current/latest view, not the Stage 8 chronological history/filter system.

### GET /price-updates/{price_update_id}
Purpose: return one approved price update.
Authentication: none at Stage 7.
Rule: pending/rejected records are not publicly returned; private source identities are excluded.

### POST /price-updates
Purpose: create a price update.
Authentication: admin bearer JWT required.
Rule: created records begin with `pending` status; `created_by` is server-controlled.

### PATCH /price-updates/{price_update_id}
Purpose: edit a price update.
Authentication: admin bearer JWT required.

### PATCH /price-updates/{price_update_id}/approve
Purpose: approve a price update for public retrieval.
Authentication: admin bearer JWT required.
Rule: records the approving admin in `approved_by`.

### PATCH /price-updates/{price_update_id}/reject
Purpose: reject a price update.
Authentication: admin bearer JWT required.

### PATCH /price-updates/{price_update_id}/mark-outdated
Purpose: mark a price update as outdated so it is not presented as current data.
Authentication: admin bearer JWT required.

### DELETE /price-updates/{price_update_id}
Purpose: delete an incorrect price update when no dependent record prevents deletion.
Authentication: admin bearer JWT required.

Stage 7 validation rules:
- current price uses `price_low` and `price_high` and permits equal values only when an exact confirmed value is intentionally supplied;
- `price_high` cannot be below `price_low`;
- `average_price` must be within the current range;
- previous range values are optional when not confirmed, but when supplied they must be supplied as a pair and form a valid range;
- movement is `up`, `down`, `stable`, or `unknown`;
- suggested action is `Watch`, `Investigate`, `Buy Carefully`, `Hold`, or `Sell Carefully`;
- explicit guarantee/financial-advice wording is rejected from `possible_meaning`;
- public responses exclude private `source_1` and `source_2` values.

## Stage 8 — Search, Filters, History, Comparison

### GET /price-updates
Returns latest approved, non-outdated price records (latest per commodity + market). Existing no-query behavior is preserved.

Optional query parameters:
- `commodity` — case-insensitive commodity-name search.
- `market` — case-insensitive market-name filter.
- `date` — exact UTC calendar date (`YYYY-MM-DD`) for the stored update timestamp.
- `movement` — `up`, `down`, `stable`, or `unknown`.

### GET /price-updates/history
Returns approved price records in chronological order. Historical approved records remain available even when marked outdated, because outdated status means the record is no longer current, not that it should disappear from history.

Optional query parameters:
- `commodity`
- `market`
- `date`
- `movement`
- `time_of_day` — `morning`, `afternoon`, `evening`, or `closing`.

### GET /price-updates/comparison
Returns the latest approved, non-outdated record per market for a commodity. Each record contains both current and previous price ranges, movement, confidence, Possible Meaning, and Suggested Action, allowing previous/current and cross-market comparison without duplicating price data.

Required query parameter:
- `commodity`

Optional query parameter:
- `date`

Public source privacy remains unchanged: `source_1` and `source_2` are not returned.

## Stage 9 — Market Signals and Quality Signals

### GET /market-signals
Purpose: list market signals created by PriceYard administration.
Authentication: active bearer JWT required at Stage 9. Full tier-by-tier premium access enforcement remains scheduled for Stage 20.
Response includes the approved market-signal disclaimer.

### GET /market-signals/{signal_id}
Purpose: view one market signal.
Authentication: active bearer JWT required.
Response includes the approved market-signal disclaimer.

### POST /market-signals
Purpose: create a market signal.
Authentication: admin bearer JWT required.
Fields: `commodity_id`, `market_id`, optional `price_update_id`, `signal_type`, `signal_description`, optional `possible_meaning`, optional approved `suggested_action`.
Rules: explicit guarantee/financial-advice wording is rejected; `created_by` is server-controlled.

### PATCH /market-signals/{signal_id}
Purpose: edit a market signal.
Authentication: admin bearer JWT required.

### DELETE /market-signals/{signal_id}
Purpose: delete a market signal.
Authentication: admin bearer JWT required.

Market-signal disclaimer returned by the API:

> Market signals are observations based on available market information. They are not guaranteed predictions or financial advice. Users should verify before making major buying, selling, or storage decisions.

### GET /quality-signals
Purpose: list quality/readiness observations.
Authentication: active bearer JWT required at Stage 9. Full tier-by-tier premium access enforcement remains scheduled for Stage 20.

### GET /quality-signals/{signal_id}
Purpose: view one quality/readiness observation.
Authentication: active bearer JWT required.

### POST /quality-signals
Purpose: create quality/readiness information.
Authentication: admin bearer JWT required.
Fields: `commodity_id`, `market_id`, optional `price_update_id`, optional `quality_status`, `moisture_status`, `storage_readiness`, `risk_note`.
Rule: explicit unsupported laboratory-confirmation wording is rejected; `created_by` is server-controlled.

### PATCH /quality-signals/{signal_id}
Purpose: edit quality/readiness information.
Authentication: admin bearer JWT required.

### DELETE /quality-signals/{signal_id}
Purpose: delete quality/readiness information.
Authentication: admin bearer JWT required.

For both signal types, an optional linked price update must use the same commodity and market. Market-signal meaning/action remains separate from price-update meaning/action.


## Stage 10 — Buying Zones and Sell-Watch Windows

### GET /buying-zones
Purpose: list buying-zone market observations.
Authentication/access: admin, active trial, or active paid access required. Free/expired/cancelled users do not receive this full-intelligence view.
Response includes the buying-zone safety disclaimer.

### GET /buying-zones/{zone_id}
Purpose: view one buying-zone observation.
Authentication/access: admin, active trial, or active paid access required.

### POST /buying-zones
Purpose: create a buying-zone observation.
Authentication: admin bearer JWT required.
Fields: `commodity_id`, `market_id`, `price_low`, `price_high`, `reason`, optional `valid_from`, optional `valid_to`, `confidence`.
Rules: invalid ranges and reversed validity periods are rejected; `created_by` is server-controlled; guarantee/financial-advice wording is rejected.

### PATCH /buying-zones/{zone_id}
Purpose: edit a buying-zone observation.
Authentication: admin bearer JWT required.

Buying-zone API disclaimer:

> Buying zones are market observations and are not guaranteed lowest prices, guaranteed buying opportunities, predictions, or financial advice.

### GET /sell-watch-windows
Purpose: list sell-watch market observations.
Authentication/access: admin, active trial, or active paid access required. Free/expired/cancelled users do not receive this full-intelligence view.
Response includes the sell-watch safety disclaimer.

### GET /sell-watch-windows/{window_id}
Purpose: view one sell-watch observation.
Authentication/access: admin, active trial, or active paid access required.

### POST /sell-watch-windows
Purpose: create a sell-watch observation.
Authentication: admin bearer JWT required.
Fields: `commodity_id`, `market_id`, `start_period`, optional `end_period`, `observation`, `confidence`.
Rules: `created_by` is server-controlled; guaranteed-profit/prediction/financial-advice wording is rejected.

### PATCH /sell-watch-windows/{window_id}
Purpose: edit a sell-watch observation.
Authentication: admin bearer JWT required.

Sell-watch API disclaimer:

> Sell-watch windows are market observations and are not guaranteed profit periods, guaranteed selling opportunities, predictions, or financial advice.

No Stage 11 storage-suitability API is included in Stage 10.
