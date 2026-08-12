# PriceYard Database Schema

## Status
Stage 3 — Database Foundation: IN PROGRESS pending live PostgreSQL migration verification.

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
- buying_zones
- sell_watch_windows
- storage_suitability
- watchlists
- cost_breakdowns
- reporter_submissions
- alerts
- reports
