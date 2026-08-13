# PriceYard Database Schema

## Status
Stage 3 foundation is RETESTED/PASS. Stage 10, Stage 11, and Stage 12 tables are owner-verified. Stage 13 is authorized to add only the approved `watchlists` table.

## Approved database stack
- PostgreSQL
- SQLAlchemy 2.x ORM
- Alembic migrations
- Psycopg PostgreSQL driver

## Stage 3 tables
Exactly these MVP foundation tables are implemented:

1. `users`
   - id
   - full_name
   - email
   - phone
   - password_hash
   - role
   - is_active
   - created_at
   - updated_at

2. `subscriptions`
   - id
   - user_id
   - plan_name
   - status
   - trial_started_at
   - trial_ends_at
   - start_date
   - end_date
   - payment_reference
   - created_at
   - updated_at

3. `commodities`
   - id
   - name
   - description
   - is_active
   - created_at
   - updated_at

4. `markets`
   - id
   - name
   - state
   - country
   - market_day
   - description
   - is_active
   - created_at
   - updated_at

5. `price_updates`
   - id
   - commodity_id
   - market_id
   - price_low
   - price_high
   - average_price
   - previous_price_low
   - previous_price_high
   - unit
   - bag_size
   - commodity_type
   - market_day
   - time_of_day
   - movement
   - confidence_level
   - source_type
   - source_1
   - source_2
   - update_date_time
   - is_outdated
   - status
   - created_by
   - approved_by
   - possible_meaning
   - suggested_action
   - notes
   - created_at
   - updated_at

   Important: `possible_meaning` and `suggested_action` are stored directly on `price_updates` and do not depend on a market signal.

6. `market_signals`
   - id
   - commodity_id
   - market_id
   - price_update_id
   - signal_type
   - signal_description
   - possible_meaning
   - suggested_action
   - created_by
   - created_at
   - updated_at

7. `quality_signals`
   - id
   - commodity_id
   - market_id
   - price_update_id
   - quality_status
   - moisture_status
   - storage_readiness
   - risk_note
   - created_by
   - created_at
   - updated_at

8. `faq_items`
   - id
   - question
   - answer
   - category
   - is_published
   - created_by
   - created_at
   - updated_at

9. `audit_logs`
   - id
   - user_id
   - action
   - table_name
   - record_id
   - old_value
   - new_value
   - created_at

10. `feedback`
   - id
   - user_id
   - rating
   - comment
   - price_usefulness
   - price_accuracy
   - missing_market_request
   - missing_commodity_request
   - complaint_or_suggestion
   - continue_using_feedback
   - willingness_to_pay_feedback
   - created_at
   - updated_at

## Main relationships
- User has one subscription.
- User can give feedback.
- Commodity has many price updates.
- Market has many price updates.
- Price update can have market signals.
- Price update can have quality signals.
- Admin/user creator relationships are preserved through foreign keys.
- Audit logs reference the acting user.

## Data-integrity constraints introduced at the schema layer
- Subscription status is limited to approved states: free, trial, active, expired, cancelled.
- Current price low cannot be negative.
- Current price high cannot be below current price low.
- Average price, when provided, must fall inside the current price range.
- Price movement is limited to up, down, stable, unknown.
- Price-update status is limited to pending, approved, rejected.
- Overall feedback ratings are limited to 1–5; price usefulness/accuracy fields remain free-text feedback as described in the architecture.

## Deferred tables — not created in Stage 3
- storage_suitability
- watchlists
- cost_breakdowns
- reporter_submissions
- alerts
- reports

## Stage 6 — Admin Core Management

No database migration is required for Stage 6. The approved Stage 3 tables already contain the fields needed for user, commodity, market, and subscription management.

Stage 6 does not create any Stage 7+ table or column.

## Stage 7 — Price Updates

No migration is required. Stage 7 uses the existing Stage 3 `price_updates` table and its approved fields/constraints.

API-layer validation now additionally enforces the approved suggested-action choices, current/previous range consistency, and observational/non-guaranteed `possible_meaning` wording. Private `source_1`/`source_2` values remain stored in PostgreSQL but are excluded from public price response schemas.

## Stage 9 — Market Signals and Quality Signals

No database migration is required. Stage 9 uses the existing Stage 3 `market_signals` and `quality_signals` tables exactly as approved.

Stage 9 adds API/service validation only:
- referenced commodity and market must exist and be active;
- optional `price_update_id`, when supplied, must point to an existing price update with the same commodity and market;
- market-signal observations reject explicit guarantee/financial-advice wording;
- quality risk notes reject explicit unsupported laboratory-confirmation wording.

`possible_meaning` and `suggested_action` on `market_signals` remain separate from the same-named fields on `price_updates`.

## Stage 10 — Buying Zones and Sell-Watch Windows

Alembic revision `0002_stage10_buy_sell_watch` creates the two Stage 10 tables that were intentionally deferred at Stage 3.

### `buying_zones`
- id
- commodity_id
- market_id
- price_low
- price_high
- reason
- valid_from
- valid_to
- confidence
- created_by
- created_at
- updated_at

Integrity rules:
- `price_low` cannot be negative;
- `price_high` cannot be below `price_low`;
- `valid_to`, when both dates are supplied, cannot be earlier than `valid_from`;
- commodity, market, and creator are relational foreign keys.

### `sell_watch_windows`
- id
- commodity_id
- market_id
- start_period
- end_period
- observation
- confidence
- created_by
- created_at
- updated_at

`start_period` and `end_period` are short text fields rather than forced calendar dates so approved observations such as “December ending” and “January upward” can be stored without inventing false precision.

Stage 10 did not create `storage_suitability`, `cost_breakdowns`, `watchlists`, alerts, reports, or any other later-stage table.


## Stage 11 — Storage Suitability

Alembic revision `0003_stage11_storage_suitability` creates the approved `storage_suitability` table.

Fields:
- id
- commodity_id
- market_id
- price_update_id
- suitability_status
- import_risk
- oversupply_risk
- spoilage_risk
- buyer_availability
- quality_storage_notes
- summary
- created_at
- updated_at

Approved `suitability_status` values:
- `good`
- `watch`
- `risky`
- `not_recommended`

Relationships:
- commodity and market are required foreign keys;
- `price_update_id` is optional and, when used, must match the same commodity and market;
- deleting a linked price update sets the optional storage-suitability link to null rather than deleting the storage observation.

Stage 11 does not create `cost_breakdowns`, `watchlists`, alerts, reports, or other later-stage tables.

## Stage 12 — Cost Breakdown

Alembic revision `0004_stage12_cost_breakdowns` creates the approved `cost_breakdowns` table.

Fields:
- id
- price_update_id
- transport
- warehouse
- security
- market_charges
- loading_offloading
- other_costs
- total_additional_cost
- purchase_price_reference
- total_estimated_landing_storage_cost
- created_at
- updated_at

Integrity/calculation rules:
- `price_update_id` is a required foreign key to `price_updates`;
- each component cost and `purchase_price_reference` must be non-negative;
- `total_additional_cost` is server-calculated as transport + warehouse + security + market charges + loading/offloading + other costs;
- `total_estimated_landing_storage_cost` is server-calculated as purchase-price reference + total additional cost;
- edits recalculate both totals rather than trusting client-supplied totals.

This preserves cost data for a later approved average-cost feature without implementing a full accounting system or complex average-cost calculator in the MVP.

Stage 12 does not create `watchlists`, alerts, reports, or any other Stage 13+ table.

## Stage 13 — Watchlist

Alembic revision `0005_stage13_watchlists` creates the approved `watchlists` table.

Fields:
- id
- user_id
- commodity_id
- market_id
- target_price
- created_at
- updated_at

Integrity/relationship rules:
- `user_id` is required and links each item to its owner;
- at least one of `commodity_id` or `market_id` must be present;
- commodity and market links are optional so a user can save a commodity only, a market only, or both;
- `target_price` is nullable and retained from the approved Architecture Design, but Stage 13 does not expose it through the API or implement target-price alerts;
- deleting the owning user, commodity, or market cascades removal of the affected watchlist row.

Stage 13 does not create FAQ, alert, report, reporter, payment, or other Stage 14+ tables.

## Stage 14 — FAQ schema use
Stage 14 requires no migration. It reuses the `faq_items` table created in the Stage 3 foundation with fields `id`, `question`, `answer`, `category`, `is_published`, `created_by`, `created_at`, and `updated_at`. Publication is controlled by the FAQ publish/hide API flow.


## Stage 15 — Feedback schema use
Stage 15 requires no migration. It reuses the `feedback` table created in Stage 3 with fields `id`, `user_id`, `rating`, `comment`, `price_usefulness`, `price_accuracy`, `missing_market_request`, `missing_commodity_request`, `complaint_or_suggestion`, `continue_using_feedback`, `willingness_to_pay_feedback`, `created_at`, and `updated_at`.

Integrity/access rules:
- rating remains constrained to 1 through 5 at both API and database levels;
- `user_id` is derived from the authenticated user, not client input;
- feedback is linked to the submitting user;
- ordinary users can submit feedback but cannot browse all users' private feedback;
- admin summary is limited to count and average rating, with no advanced analytics.

## Stage 16 — Audit-log schema use
Stage 16 requires no migration. It reuses the `audit_logs` table created in Stage 3 with fields `id`, `user_id`, `action`, `table_name`, `record_id`, `old_value`, `new_value`, and `created_at`.

Stage 16 rules:
- `user_id` identifies the admin who performed the audited action;
- `old_value` and `new_value` contain JSON-safe snapshots where applicable;
- password/password-hash data, JWT/secret/token data, database credentials/URLs, `.env` data, and private price-source identities are excluded from audit snapshots;
- ordinary users cannot view audit history;
- no Stage 17 CSV-report schema or other later-stage schema is introduced.

## Stage 17 — CSV export schema use
Stage 17 requires no migration and creates no report-storage table. The CSV export reads approved `price_updates` and their existing commodity, market, market-signal, and quality-signal relationships. Repository Alembic head remains `0005_stage13_watchlists`.
