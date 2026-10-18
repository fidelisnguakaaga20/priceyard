# Current application API reference

This replaces the old staged-development notes. The local application already
implements authentication, subscriptions, prices, intelligence, moderation,
payments, exports and Admin operations. This document describes existing code;
it does not approve a new access policy or a production rollout.

For request/response fields and validation, use `/docs` or `/openapi.json` on the
isolated local backend. The browser preview proxies API calls through `/api`;
the paths below are backend paths without that proxy prefix. The synthetic
preview's `/__test__/...` controls are not application endpoints.

## Access and security contracts

- Guest has no account role. Trial and paid access are subscription states,
  separate from stored roles `free_user`, `paid_user`, `reporter`, `admin`.
- `get_current_user` checks the bearer JWT, account activation, current account
  security version and revoked token hashes on the server.
- `require_roles(...)` additionally restricts staff operations to the named roles.
  `require_full_access` checks current trial/paid entitlement; Admin bypasses that
  entitlement check. Reporter authority does not itself grant paid entitlement.
- Public price schemas omit private source identities. Existing approved current
  prices remain public. History, history options, historical comparisons and
  historical detail apply entitlement checks, including conditional handler checks.
  Admin history/source access remains separate from public responses.
- Quality list/detail require full access. Other existing basic intelligence
  visibility is unchanged pending the owner's source/access-policy decisions.
- Subscription reads and watchlists enforce account ownership; Admin powers are
  checked separately. The dependency column alone is not an ownership policy.
- Checkout accepts only existing plans: NGN2,500/30 days and NGN6,000/90 days.
  Activation requires strict signed/provider evidence and an atomic save.
  A webhook uses signature verification rather than a user JWT; it is not an
  unprotected payment activation endpoint. Provider success alone is insufficient.
- CSV download is Admin only, includes every matching approved row, excludes
  private sources and neutralizes spreadsheet formulas. It streams100-record
  fetch batches; there is no arbitrary export count cap.
- Cron/webhook/header checks, rate limits and conditional/ownership checks can
  live inside handlers/services. A dash below means no declared non-DB Depends
  argument, **not** that an operation is public or safe to call without review.

The approved business rules and operational limits are recorded in
[application contracts](APPLICATION_CONTRACTS.md),
[local development](LOCAL_DEVELOPMENT.md) and
[the live progress tracker](../PRICEYARD_PROGRESS.md).

## Route index

Generated from router declarations with `tools/local-test/update_api_reference.py`.
Only source AST is read; no settings, credentials, application imports, database
connection or provider request is involved. Dependency expressions are copied
from declarations for traceability; follow the linked handler for all checks.

| Method | Backend path | Declared access dependencies (excluding get_db) | Handler |
| --- | --- | --- | --- |
| POST | `/activity/ping` | `—` | [ping](../backend/app/routes/activity_routes.py#L16) |
| POST | `/activity/seen` | `require_roles('admin')` | [seen](../backend/app/routes/activity_routes.py#L31) |
| GET | `/activity/summary` | `require_roles('admin')` | [summary](../backend/app/routes/activity_routes.py#L23) |
| GET | `/admin/summary` | `require_roles('admin')` | [dashboard_summary](../backend/app/routes/admin_summary_routes.py#L14) |
| GET | `/audit-logs` | `require_roles('admin')` | [get_logs](../backend/app/routes/audit_log_routes.py#L15) |
| GET | `/audit-logs/{audit_log_id}` | `require_roles('admin')` | [get_log](../backend/app/routes/audit_log_routes.py#L23) |
| POST | `/auth/forgot-password` | `—` | [forgot_password](../backend/app/routes/auth_routes.py#L87) |
| POST | `/auth/google` | `—` | [login_with_google](../backend/app/routes/auth_routes.py#L46) |
| POST | `/auth/login` | `—` | [login](../backend/app/routes/auth_routes.py#L39) |
| POST | `/auth/logout` | `bearer_scheme` | [logout](../backend/app/routes/auth_routes.py#L52) |
| GET | `/auth/me` | `get_current_user` | [me](../backend/app/routes/auth_routes.py#L66) |
| GET | `/auth/referral-summary` | `get_current_user` | [referral_summary](../backend/app/routes/auth_routes.py#L71) |
| POST | `/auth/register` | `—` | [register](../backend/app/routes/auth_routes.py#L27) |
| POST | `/auth/reset-password` | `—` | [change_forgotten_password](../backend/app/routes/auth_routes.py#L92) |
| GET | `/buying-zones` | `require_full_access` | [get_zones](../backend/app/routes/buying_zone_routes.py#L23) |
| POST | `/buying-zones` | `require_roles('admin')` | [add_zone](../backend/app/routes/buying_zone_routes.py#L41) |
| GET | `/buying-zones/{zone_id}` | `require_full_access` | [get_zone](../backend/app/routes/buying_zone_routes.py#L32) |
| PATCH | `/buying-zones/{zone_id}` | `require_roles('admin')` | [edit_zone](../backend/app/routes/buying_zone_routes.py#L52) |
| GET | `/commodities` | `—` | [get_commodities](../backend/app/routes/commodity_routes.py#L32) |
| POST | `/commodities` | `require_roles('admin')` | [add_commodity](../backend/app/routes/commodity_routes.py#L53) |
| GET | `/commodities/admin/all` | `require_roles('admin')` | [get_all_commodities_for_admin](../backend/app/routes/commodity_routes.py#L37) |
| DELETE | `/commodities/{commodity_id}` | `require_roles('admin')` | [remove_commodity](../backend/app/routes/commodity_routes.py#L78) |
| GET | `/commodities/{commodity_id}` | `—` | [get_commodity_by_id](../backend/app/routes/commodity_routes.py#L45) |
| PATCH | `/commodities/{commodity_id}` | `require_roles('admin')` | [edit_commodity](../backend/app/routes/commodity_routes.py#L64) |
| GET | `/cost-breakdowns` | `require_full_access` | [get_items](../backend/app/routes/cost_breakdown_routes.py#L28) |
| POST | `/cost-breakdowns` | `require_roles('admin')` | [add_item](../backend/app/routes/cost_breakdown_routes.py#L46) |
| DELETE | `/cost-breakdowns/{item_id}` | `require_roles('admin')` | [remove_item](../backend/app/routes/cost_breakdown_routes.py#L71) |
| GET | `/cost-breakdowns/{item_id}` | `require_full_access` | [get_item](../backend/app/routes/cost_breakdown_routes.py#L37) |
| PATCH | `/cost-breakdowns/{item_id}` | `require_roles('admin')` | [edit_item](../backend/app/routes/cost_breakdown_routes.py#L57) |
| GET | `/faq` | `—` | [get_published_items](../backend/app/routes/faq_routes.py#L37) |
| POST | `/faq` | `require_roles('admin')` | [add_item](../backend/app/routes/faq_routes.py#L55) |
| GET | `/faq/admin` | `require_roles('admin')` | [get_admin_items](../backend/app/routes/faq_routes.py#L42) |
| DELETE | `/faq/{faq_id}` | `require_roles('admin')` | [remove_item](../backend/app/routes/faq_routes.py#L106) |
| GET | `/faq/{faq_id}` | `—` | [get_published_item](../backend/app/routes/faq_routes.py#L50) |
| PATCH | `/faq/{faq_id}` | `require_roles('admin')` | [edit_item](../backend/app/routes/faq_routes.py#L66) |
| PATCH | `/faq/{faq_id}/hide` | `require_roles('admin')` | [hide_item](../backend/app/routes/faq_routes.py#L93) |
| PATCH | `/faq/{faq_id}/publish` | `require_roles('admin')` | [publish_item](../backend/app/routes/faq_routes.py#L80) |
| GET | `/feedback` | `require_roles('admin')` | [get_feedback_list](../backend/app/routes/feedback_routes.py#L70) |
| POST | `/feedback` | `get_current_user` | [submit_feedback](../backend/app/routes/feedback_routes.py#L53) |
| GET | `/feedback/summary` | `require_roles('admin')` | [get_feedback_summary](../backend/app/routes/feedback_routes.py#L62) |
| DELETE | `/feedback/{feedback_id}` | `require_roles('admin')` | [remove_feedback](../backend/app/routes/feedback_routes.py#L115) |
| GET | `/feedback/{feedback_id}` | `require_roles('admin')` | [get_feedback_item](../backend/app/routes/feedback_routes.py#L79) |
| PATCH | `/feedback/{feedback_id}/testimonial/hide` | `require_roles('admin')` | [hide_testimonial](../backend/app/routes/feedback_routes.py#L102) |
| PATCH | `/feedback/{feedback_id}/testimonial/publish` | `require_roles('admin')` | [publish_testimonial](../backend/app/routes/feedback_routes.py#L88) |
| GET | `/health` | `—` | [health_check](../backend/app/main.py#L84) |
| GET | `/market-signals` | `get_current_user` | [get_signals](../backend/app/routes/market_signal_routes.py#L24) |
| POST | `/market-signals` | `require_roles('admin')` | [add_signal](../backend/app/routes/market_signal_routes.py#L42) |
| DELETE | `/market-signals/{signal_id}` | `require_roles('admin')` | [remove_signal](../backend/app/routes/market_signal_routes.py#L67) |
| GET | `/market-signals/{signal_id}` | `get_current_user` | [get_signal](../backend/app/routes/market_signal_routes.py#L33) |
| PATCH | `/market-signals/{signal_id}` | `require_roles('admin')` | [edit_signal](../backend/app/routes/market_signal_routes.py#L53) |
| GET | `/markets` | `—` | [get_markets](../backend/app/routes/market_routes.py#L26) |
| POST | `/markets` | `require_roles('admin')` | [add_market](../backend/app/routes/market_routes.py#L47) |
| GET | `/markets/admin/all` | `require_roles('admin')` | [get_all_markets_for_admin](../backend/app/routes/market_routes.py#L31) |
| DELETE | `/markets/{market_id}` | `require_roles('admin')` | [remove_market](../backend/app/routes/market_routes.py#L72) |
| GET | `/markets/{market_id}` | `—` | [get_market_by_id](../backend/app/routes/market_routes.py#L39) |
| PATCH | `/markets/{market_id}` | `require_roles('admin')` | [edit_market](../backend/app/routes/market_routes.py#L58) |
| GET | `/payments` | `require_roles('admin')` | [get_payments](../backend/app/routes/payment_routes.py#L65) |
| POST | `/payments/initiate` | `get_current_user` | [start_payment](../backend/app/routes/payment_routes.py#L40) |
| GET | `/payments/page` | `require_roles('admin')` | [get_payments_page](../backend/app/routes/payment_routes.py#L74) |
| POST | `/payments/webhook` | `—` | [paystack_webhook](../backend/app/routes/payment_routes.py#L49) |
| POST | `/payments/{reference}/verify` | `_verification_user` | [verify_payment](../backend/app/routes/payment_routes.py#L30) |
| GET | `/price-updates` | `bearer_scheme` | [get_latest_price_updates](../backend/app/routes/price_update_routes.py#L83) |
| POST | `/price-updates` | `require_roles('admin', 'reporter')` | [add_price_update](../backend/app/routes/price_update_routes.py#L190) |
| GET | `/price-updates/admin/flagged` | `require_roles('admin')` | [get_flagged_price_updates](../backend/app/routes/price_update_routes.py#L163) |
| GET | `/price-updates/admin/history` | `require_roles('admin')` | [get_admin_price_history](../backend/app/routes/price_update_routes.py#L155) |
| GET | `/price-updates/comparison` | `bearer_scheme` | [get_market_comparison](../backend/app/routes/price_update_routes.py#L138) |
| GET | `/price-updates/history` | `require_full_access` | [get_price_history](../backend/app/routes/price_update_routes.py#L107) |
| GET | `/price-updates/history/pairs` | `require_full_access` | [get_price_history_pairs](../backend/app/routes/price_update_routes.py#L130) |
| GET | `/price-updates/my-stats` | `get_current_user` | [get_my_submission_stats](../backend/app/routes/price_update_routes.py#L171) |
| DELETE | `/price-updates/{price_update_id}` | `require_roles('admin')` | [remove_price_update](../backend/app/routes/price_update_routes.py#L288) |
| GET | `/price-updates/{price_update_id}` | `bearer_scheme` | [get_price_update](../backend/app/routes/price_update_routes.py#L179) |
| PATCH | `/price-updates/{price_update_id}` | `require_roles('admin')` | [edit_price_update](../backend/app/routes/price_update_routes.py#L201) |
| PATCH | `/price-updates/{price_update_id}/approve` | `require_roles('admin')` | [approve_update](../backend/app/routes/price_update_routes.py#L218) |
| POST | `/price-updates/{price_update_id}/flag` | `get_current_user` | [flag_price](../backend/app/routes/price_update_routes.py#L245) |
| POST | `/price-updates/{price_update_id}/flags/resolve` | `require_roles('admin')` | [resolve_price_flags](../backend/app/routes/price_update_routes.py#L256) |
| PATCH | `/price-updates/{price_update_id}/mark-outdated` | `require_roles('admin')` | [mark_outdated](../backend/app/routes/price_update_routes.py#L275) |
| PATCH | `/price-updates/{price_update_id}/reject` | `require_roles('admin')` | [reject_update](../backend/app/routes/price_update_routes.py#L232) |
| POST | `/push/subscribe` | `get_current_user` | [subscribe](../backend/app/routes/push_routes.py#L35) |
| GET | `/push/subscribed` | `get_current_user` | [check_subscribed](../backend/app/routes/push_routes.py#L16) |
| POST | `/push/unsubscribe` | `get_current_user` | [unsubscribe](../backend/app/routes/push_routes.py#L44) |
| GET | `/quality-signals` | `require_full_access` | [get_signals](../backend/app/routes/quality_signal_routes.py#L24) |
| POST | `/quality-signals` | `require_roles('admin')` | [add_signal](../backend/app/routes/quality_signal_routes.py#L42) |
| DELETE | `/quality-signals/{signal_id}` | `require_roles('admin')` | [remove_signal](../backend/app/routes/quality_signal_routes.py#L67) |
| GET | `/quality-signals/{signal_id}` | `require_full_access` | [get_signal](../backend/app/routes/quality_signal_routes.py#L33) |
| PATCH | `/quality-signals/{signal_id}` | `require_roles('admin')` | [edit_signal](../backend/app/routes/quality_signal_routes.py#L53) |
| GET | `/reports/prices.csv` | `require_roles('admin')` | [export_price_report_csv](../backend/app/routes/report_export_routes.py#L33) |
| GET | `/sell-watch-windows` | `require_full_access` | [get_windows](../backend/app/routes/sell_watch_window_routes.py#L27) |
| POST | `/sell-watch-windows` | `require_roles('admin')` | [add_window](../backend/app/routes/sell_watch_window_routes.py#L45) |
| GET | `/sell-watch-windows/{window_id}` | `require_full_access` | [get_window](../backend/app/routes/sell_watch_window_routes.py#L36) |
| PATCH | `/sell-watch-windows/{window_id}` | `require_roles('admin')` | [edit_window](../backend/app/routes/sell_watch_window_routes.py#L56) |
| GET | `/share/commodities/{commodity_name}` | `—` | [share_commodity_card](../backend/app/routes/share_routes.py#L49) |
| GET | `/storage-suitability` | `require_full_access` | [get_items](../backend/app/routes/storage_suitability_routes.py#L27) |
| POST | `/storage-suitability` | `require_roles('admin')` | [add_item](../backend/app/routes/storage_suitability_routes.py#L45) |
| GET | `/storage-suitability/{item_id}` | `require_full_access` | [get_item](../backend/app/routes/storage_suitability_routes.py#L36) |
| PATCH | `/storage-suitability/{item_id}` | `require_roles('admin')` | [edit_item](../backend/app/routes/storage_suitability_routes.py#L56) |
| GET | `/subscriptions` | `require_roles('admin')` | [get_subscriptions](../backend/app/routes/subscription_routes.py#L31) |
| POST | `/subscriptions/cron/send-trial-reminders` | `verify_cron_secret` | [cron_trigger_trial_reminders](../backend/app/routes/subscription_routes.py#L62) |
| POST | `/subscriptions/send-trial-reminders` | `require_roles('admin')` | [trigger_trial_reminders](../backend/app/routes/subscription_routes.py#L53) |
| GET | `/subscriptions/{user_id}` | `get_current_user` | [get_user_subscription](../backend/app/routes/subscription_routes.py#L39) |
| PATCH | `/subscriptions/{user_id}/status` | `require_roles('admin')` | [set_subscription_status](../backend/app/routes/subscription_routes.py#L74) |
| GET | `/testimonials` | `—` | [get_public_testimonials](../backend/app/routes/feedback_routes.py#L48) |
| GET | `/users` | `require_roles('admin')` | [get_users](../backend/app/routes/user_routes.py#L17) |
| GET | `/users/page` | `require_roles('admin')` | [get_users_page](../backend/app/routes/user_routes.py#L25) |
| GET | `/users/{user_id}` | `require_roles('admin')` | [get_user_by_id](../backend/app/routes/user_routes.py#L34) |
| PATCH | `/users/{user_id}` | `require_roles('admin')` | [edit_user](../backend/app/routes/user_routes.py#L43) |
| GET | `/watchlist` | `get_current_user` | [get_own_watchlist](../backend/app/routes/watchlist_routes.py#L28) |
| POST | `/watchlist` | `get_current_user` | [save_item](../backend/app/routes/watchlist_routes.py#L19) |
| DELETE | `/watchlist/{item_id}` | `get_current_user` | [remove_item](../backend/app/routes/watchlist_routes.py#L36) |
