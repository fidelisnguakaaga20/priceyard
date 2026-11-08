# Database schema

PostgreSQL (hosted on Supabase), defined by the SQLAlchemy models in
[`backend/app/models`](../backend/app/models) and created by the Alembic migrations in
[`backend/migrations/versions`](../backend/migrations/versions). Money is stored as
`numeric(14,2)` in naira. Times are stored in UTC and shown in Nigeria time (WAT).

Records that other records depend on (commodities, markets, users) cannot be deleted
while still referenced (`on delete restrict`). A user's own data (subscription,
payments, watchlist, feedback, flags, push subscriptions) is removed with the user
(`on delete cascade`).

## Accounts

### `users`

Everyone with an account. `role` is `free_user`, `paid_user`, `reporter` or `admin`. `auth_version` rises on a password reset or deactivation, ending older logins. `referral_code` is each user's share code; `referred_by_id` records who invited them.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `full_name` | varchar(150) | required |
| `email` | varchar(320) | required, unique |
| `phone` | varchar(30) | unique |
| `password_hash` | varchar(255) | required |
| `google_id` | varchar(255) | unique |
| `auth_provider` | varchar(20) | required |
| `role` | varchar(32) | required |
| `is_active` | boolean | required |
| `auth_version` | integer | required, default 0 |
| `referral_code` | varchar(12) | required, unique |
| `referred_by_id` | integer | → `users` |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `subscriptions`

One per user: free, trial, active (paid), expired or cancelled, with trial and paid-period dates.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, unique, → `users` (on delete cascade) |
| `plan_name` | varchar(50) | required |
| `status` | varchar(20) | required |
| `trial_started_at` | timestamp |  |
| `trial_ends_at` | timestamp |  |
| `trial_reminder_sent_at` | timestamp |  |
| `start_date` | date |  |
| `end_date` | date |  |
| `payment_reference` | varchar(255) |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `status IN ('free', 'trial', 'active', 'expired', 'cancelled')`.

### `payments`

Each Paystack checkout. Access is granted only after the payment is confirmed.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `reference` | varchar(100) | required, unique |
| `plan` | varchar(20) | required |
| `amount` | numeric(14,2) | required |
| `currency` | varchar(10) | required |
| `status` | varchar(20) | required |
| `paystack_transaction_id` | varchar(100) |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `status IN ('pending', 'success', 'failed')`; `plan IN ('monthly', 'seasonal')`.

### `password_reset_tokens`

Single-use reset links, stored only as a hash and valid for 15 minutes.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `token_hash` | varchar(64) | required, unique |
| `expires_at` | timestamp | required |
| `used_at` | timestamp |  |
| `created_at` | timestamp | required, default now |

### `revoked_access_tokens`

Hashes of logged-out tokens until they would have expired anyway; raw tokens are never stored.

| Column | Type | Notes |
|---|---|---|
| `token_hash` | varchar(64) | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `expires_at` | timestamp | required |
| `revoked_at` | timestamp | required |

### `push_subscriptions`

Browser push endpoints for each user's devices.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `endpoint` | varchar(500) | required, unique |
| `p256dh` | varchar(300) | required |
| `auth` | varchar(100) | required |
| `created_at` | timestamp | required, default now |

## Catalogue and prices

### `commodities`

Commodities such as Egusi, Honey Beans and Palm Oil. `is_upcoming` lists a commodity before prices exist.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `name` | varchar(100) | required, unique |
| `description` | text |  |
| `image_url` | varchar(500) |  |
| `is_active` | boolean | required |
| `is_upcoming` | boolean | required |
| `expected_available_date` | date |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `markets`

Markets with their state and market day.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `name` | varchar(150) | required |
| `state` | varchar(100) |  |
| `country` | varchar(100) | required |
| `market_day` | varchar(30) |  |
| `description` | text |  |
| `image_url` | varchar(500) |  |
| `is_active` | boolean | required |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `price_updates`

Price records: a low–high range per commodity, market and specification (unit, bag size, type). `status` is pending → approved or rejected; only approved records are public. `source_1` and `source_2` are private.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `price_low` | numeric(14,2) | required |
| `price_high` | numeric(14,2) | required |
| `average_price` | numeric(14,2) |  |
| `previous_price_low` | numeric(14,2) |  |
| `previous_price_high` | numeric(14,2) |  |
| `unit` | varchar(100) | required |
| `bag_size` | varchar(100) |  |
| `commodity_type` | varchar(150) |  |
| `market_day` | varchar(30) |  |
| `time_of_day` | varchar(20) |  |
| `movement` | varchar(20) | required |
| `confidence_level` | varchar(100) | required |
| `source_type` | varchar(100) |  |
| `source_1` | varchar(255) |  |
| `source_2` | varchar(255) |  |
| `update_date_time` | timestamp | required |
| `is_outdated` | boolean | required |
| `status` | varchar(20) | required |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `approved_by` | integer | → `users` |
| `possible_meaning` | text |  |
| `suggested_action` | varchar(50) |  |
| `notes` | text |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `price_high >= price_low`; `status IN ('pending', 'approved', 'rejected')`; `price_low >= 0`; `average_price IS NULL OR (average_price >= price_low AND average_price <= price_high)`; `movement IN ('up', 'down', 'stable', 'unknown')`.

### `price_flags`

A member's report that a price looks wrong; one per member per price.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `price_update_id` | integer | required, → `price_updates` (on delete cascade) |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `reason` | varchar(50) |  |
| `resolved` | boolean | required, default false |
| `created_at` | timestamp | required, default now |

Rules: unique together `price_update_id`, `user_id`.

## Market intelligence

### `market_signals`

Observations about demand, supply or movement, optionally tied to a price record.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `price_update_id` | integer | → `price_updates` (on delete cascade) |
| `signal_type` | varchar(100) | required |
| `signal_description` | text | required |
| `possible_meaning` | text |  |
| `suggested_action` | varchar(50) |  |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `quality_signals`

Quality, moisture and storage-readiness notes.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `price_update_id` | integer | → `price_updates` (on delete cascade) |
| `quality_status` | varchar(100) |  |
| `moisture_status` | varchar(100) |  |
| `storage_readiness` | varchar(100) |  |
| `risk_note` | text |  |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `buying_zones`

Suggested buying price ranges with a reason, a confidence level and an optional validity period.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `price_low` | numeric(14,2) | required |
| `price_high` | numeric(14,2) | required |
| `reason` | text | required |
| `valid_from` | date |  |
| `valid_to` | date |  |
| `confidence` | varchar(100) | required |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from`; `price_low >= 0`; `price_high >= price_low`.

### `sell_watch_windows`

Periods worth watching for selling.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `start_period` | varchar(100) | required |
| `end_period` | varchar(100) |  |
| `observation` | text | required |
| `confidence` | varchar(100) | required |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `storage_suitability`

Whether storing a commodity at a market is good, watch, risky or not recommended, with the risks behind it.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `price_update_id` | integer | → `price_updates` |
| `suitability_status` | varchar(30) | required |
| `import_risk` | varchar(100) |  |
| `oversupply_risk` | varchar(100) |  |
| `spoilage_risk` | varchar(100) |  |
| `buyer_availability` | varchar(150) |  |
| `quality_storage_notes` | text |  |
| `summary` | text |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `suitability_status IN ('good', 'watch', 'risky', 'not_recommended')`.

### `cost_breakdowns`

Transport, warehouse, security, market and handling costs on top of a purchase price, giving a total landing and storage cost.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `commodity_id` | integer | required, → `commodities` (on delete restrict) |
| `market_id` | integer | required, → `markets` (on delete restrict) |
| `transport` | numeric(14,2) | required |
| `warehouse` | numeric(14,2) | required |
| `security` | numeric(14,2) | required |
| `market_charges` | numeric(14,2) | required |
| `loading_offloading` | numeric(14,2) | required |
| `other_costs` | numeric(14,2) | required |
| `cost_items` | json | required, default '[]' |
| `total_additional_cost` | numeric(14,2) | required |
| `purchase_price_reference` | numeric(14,2) | required |
| `total_estimated_landing_storage_cost` | numeric(14,2) | required |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: every amount must be zero or more.

## Member features

### `watchlists`

What a user watches (a commodity, a market or both), with an optional target price and direction for alerts.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `commodity_id` | integer | → `commodities` (on delete cascade) |
| `market_id` | integer | → `markets` (on delete cascade) |
| `target_price` | numeric(14,2) |  |
| `target_direction` | varchar(20) |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `commodity_id IS NOT NULL OR market_id IS NOT NULL`; `target_price IS NULL OR target_price >= 0`; `target_direction IS NULL OR target_direction IN ('at_or_below', 'at_or_above')`; `(target_price IS NULL) = (target_direction IS NULL)`.

### `feedback`

Ratings and comments, optionally published as a testimonial. The optional screenshot is visible only to admins.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete cascade) |
| `rating` | smallint | required |
| `comment` | text |  |
| `price_usefulness` | text |  |
| `price_accuracy` | text |  |
| `missing_market_request` | text |  |
| `missing_commodity_request` | text |  |
| `complaint_or_suggestion` | text |  |
| `continue_using_feedback` | boolean |  |
| `willingness_to_pay_feedback` | boolean |  |
| `is_public_testimonial` | boolean | required, default false |
| `testimonial_display_name` | text |  |
| `screenshot_data` | text |  |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

Rules: `rating BETWEEN 1 AND 5`.

## Content and administration

### `faq_items`

FAQ entries; only published ones are public.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `question` | text | required |
| `answer` | text | required |
| `category` | varchar(100) | required |
| `is_published` | boolean | required |
| `created_by` | integer | required, → `users` (on delete restrict) |
| `created_at` | timestamp | required, default now |
| `updated_at` | timestamp | required, default now |

### `audit_logs`

Who changed what: every admin change, with old and new values, saved in the same transaction as the change.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `user_id` | integer | required, → `users` (on delete restrict) |
| `action` | varchar(100) | required |
| `table_name` | varchar(100) | required |
| `record_id` | integer |  |
| `old_value` | json |  |
| `new_value` | json |  |
| `created_at` | timestamp | required, default now |

### `activity_events`

Anonymous counts of app opens and shared-link visits for the admin activity feed; no visitor identity is stored.

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `event_type` | varchar(30) | required |
| `label` | varchar(200) |  |
| `seen` | boolean | required, default false |
| `created_at` | timestamp | required, default now |

