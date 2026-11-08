# API reference

The backend is a FastAPI app. In production the website reaches it through `/api` on
the same site (for example `/api/price-updates` → `/price-updates`); the paths below are the
backend paths. Interactive docs (`/docs`) are switched off in production and can be
enabled locally with `API_DOCS_ENABLED=true`.

## Who can call it

| Label | Meaning |
|---|---|
| Public | No sign-in needed |
| Signed in | Any active account |
| Full access | Active trial, paid plan, or admin ([access control](access-control.md)) |
| Admin or reporter / Admin | Only those roles |

Browser requests that change data must also carry the session's CSRF token from an
allowed origin. Ownership rules (for example, only your own watchlist) are enforced
inside the handlers. Sign-in, password reset, activity and payment-verification routes
are rate limited.

## Health

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/health` | Public | [health_check](../backend/app/main.py#L92) |

## Endpoints

### Accounts and sign-in

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| POST | `/auth/register` | Public | [register](../backend/app/routes/auth_routes.py#L49) |
| POST | `/auth/login` | Public | [login](../backend/app/routes/auth_routes.py#L61) |
| POST | `/auth/google` | Public | [login_with_google](../backend/app/routes/auth_routes.py#L70) |
| POST | `/auth/logout` | Signed in | [logout](../backend/app/routes/auth_routes.py#L78) |
| POST | `/auth/browser/login` | Public | [browser_login](../backend/app/routes/auth_routes.py#L116) |
| POST | `/auth/browser/google` | Public | [browser_google](../backend/app/routes/auth_routes.py#L130) |
| GET | `/auth/browser/session` | Public | [browser_session](../backend/app/routes/auth_routes.py#L145) |
| POST | `/auth/browser/upgrade` | Signed in | [browser_upgrade](../backend/app/routes/auth_routes.py#L155) |
| GET | `/auth/me` | Signed in | [me](../backend/app/routes/auth_routes.py#L173) |
| GET | `/auth/referral-summary` | Signed in | [referral_summary](../backend/app/routes/auth_routes.py#L178) |
| POST | `/auth/forgot-password` | Public | [forgot_password](../backend/app/routes/auth_routes.py#L192) |
| POST | `/auth/reset-password` | Public | [change_forgotten_password](../backend/app/routes/auth_routes.py#L197) |

### Prices

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/price-updates` | Public (a past `date` needs full access) | [get_latest_price_updates](../backend/app/routes/price_update_routes.py#L99) |
| GET | `/price-updates/history` | Full access | [get_price_history](../backend/app/routes/price_update_routes.py#L124) |
| GET | `/price-updates/history/pairs` | Full access | [get_price_history_pairs](../backend/app/routes/price_update_routes.py#L150) |
| GET | `/price-updates/comparison` | Public (a past `date` needs full access) | [get_market_comparison](../backend/app/routes/price_update_routes.py#L158) |
| GET | `/price-updates/admin/history` | Admin | [get_admin_price_history](../backend/app/routes/price_update_routes.py#L175) |
| GET | `/price-updates/admin/history/page` | Admin | [get_admin_price_page](../backend/app/routes/price_update_routes.py#L191) |
| GET | `/price-updates/admin/latest` | Admin | [get_admin_latest_pair](../backend/app/routes/price_update_routes.py#L207) |
| GET | `/price-updates/admin/flagged` | Admin | [get_flagged_price_updates](../backend/app/routes/price_update_routes.py#L224) |
| GET | `/price-updates/admin/flagged/page` | Admin | [get_flagged_page](../backend/app/routes/price_update_routes.py#L232) |
| GET | `/price-updates/my-stats` | Signed in | [get_my_submission_stats](../backend/app/routes/price_update_routes.py#L241) |
| GET | `/price-updates/{price_update_id}` | Public for current prices; older records need full access | [get_price_update](../backend/app/routes/price_update_routes.py#L249) |
| POST | `/price-updates` | Admin or reporter | [add_price_update](../backend/app/routes/price_update_routes.py#L260) |
| PATCH | `/price-updates/{price_update_id}` | Admin | [edit_price_update](../backend/app/routes/price_update_routes.py#L271) |
| PATCH | `/price-updates/{price_update_id}/approve` | Admin | [approve_update](../backend/app/routes/price_update_routes.py#L290) |
| PATCH | `/price-updates/{price_update_id}/reject` | Admin | [reject_update](../backend/app/routes/price_update_routes.py#L304) |
| POST | `/price-updates/{price_update_id}/flag` | Signed in | [flag_price](../backend/app/routes/price_update_routes.py#L317) |
| POST | `/price-updates/{price_update_id}/flags/resolve` | Admin | [resolve_price_flags](../backend/app/routes/price_update_routes.py#L328) |
| PATCH | `/price-updates/{price_update_id}/mark-outdated` | Admin | [mark_outdated](../backend/app/routes/price_update_routes.py#L354) |
| DELETE | `/price-updates/{price_update_id}` | Admin | [remove_price_update](../backend/app/routes/price_update_routes.py#L367) |
| GET | `/reports/prices.csv` | Admin | [export_price_report_csv](../backend/app/routes/report_export_routes.py#L34) |
| GET | `/share/commodities/{commodity_name}` | Public | [share_commodity_card](../backend/app/routes/share_routes.py#L49) |

### Catalogue

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/commodities` | Public | [get_commodities](../backend/app/routes/commodity_routes.py#L54) |
| GET | `/commodities/admin/all` | Admin | [get_all_commodities_for_admin](../backend/app/routes/commodity_routes.py#L68) |
| GET | `/commodities/admin/page` | Admin | [get_commodities_page](../backend/app/routes/commodity_routes.py#L80) |
| GET | `/commodities/{commodity_id}` | Public | [get_commodity_by_id](../backend/app/routes/commodity_routes.py#L89) |
| POST | `/commodities` | Admin | [add_commodity](../backend/app/routes/commodity_routes.py#L97) |
| PATCH | `/commodities/{commodity_id}` | Admin | [edit_commodity](../backend/app/routes/commodity_routes.py#L108) |
| DELETE | `/commodities/{commodity_id}` | Admin | [remove_commodity](../backend/app/routes/commodity_routes.py#L122) |
| GET | `/markets` | Public | [get_markets](../backend/app/routes/market_routes.py#L49) |
| GET | `/markets/admin/all` | Admin | [get_all_markets_for_admin](../backend/app/routes/market_routes.py#L63) |
| GET | `/markets/admin/page` | Admin | [get_markets_page](../backend/app/routes/market_routes.py#L73) |
| GET | `/markets/{market_id}` | Public | [get_market_by_id](../backend/app/routes/market_routes.py#L82) |
| POST | `/markets` | Admin | [add_market](../backend/app/routes/market_routes.py#L90) |
| PATCH | `/markets/{market_id}` | Admin | [edit_market](../backend/app/routes/market_routes.py#L101) |
| DELETE | `/markets/{market_id}` | Admin | [remove_market](../backend/app/routes/market_routes.py#L115) |

### Market intelligence

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/market-signals` | Signed in | [get_signals](../backend/app/routes/market_signal_routes.py#L30) |
| GET | `/market-signals/admin/page` | Admin | [get_admin_signals_page](../backend/app/routes/market_signal_routes.py#L48) |
| GET | `/market-signals/{signal_id}` | Signed in | [get_signal](../backend/app/routes/market_signal_routes.py#L59) |
| POST | `/market-signals` | Admin | [add_signal](../backend/app/routes/market_signal_routes.py#L68) |
| PATCH | `/market-signals/{signal_id}` | Admin | [edit_signal](../backend/app/routes/market_signal_routes.py#L79) |
| DELETE | `/market-signals/{signal_id}` | Admin | [remove_signal](../backend/app/routes/market_signal_routes.py#L93) |
| GET | `/quality-signals` | Full access | [get_signals](../backend/app/routes/quality_signal_routes.py#L30) |
| GET | `/quality-signals/admin/page` | Admin | [get_admin_signals_page](../backend/app/routes/quality_signal_routes.py#L48) |
| GET | `/quality-signals/{signal_id}` | Full access | [get_signal](../backend/app/routes/quality_signal_routes.py#L59) |
| POST | `/quality-signals` | Admin | [add_signal](../backend/app/routes/quality_signal_routes.py#L68) |
| PATCH | `/quality-signals/{signal_id}` | Admin | [edit_signal](../backend/app/routes/quality_signal_routes.py#L79) |
| DELETE | `/quality-signals/{signal_id}` | Admin | [remove_signal](../backend/app/routes/quality_signal_routes.py#L93) |
| GET | `/buying-zones` | Full access | [get_zones](../backend/app/routes/buying_zone_routes.py#L30) |
| GET | `/buying-zones/admin/page` | Admin | [get_admin_zones_page](../backend/app/routes/buying_zone_routes.py#L48) |
| GET | `/buying-zones/{zone_id}` | Full access | [get_zone](../backend/app/routes/buying_zone_routes.py#L59) |
| POST | `/buying-zones` | Admin | [add_zone](../backend/app/routes/buying_zone_routes.py#L68) |
| PATCH | `/buying-zones/{zone_id}` | Admin | [edit_zone](../backend/app/routes/buying_zone_routes.py#L79) |
| DELETE | `/buying-zones/{zone_id}` | Admin | [remove_zone](../backend/app/routes/buying_zone_routes.py#L93) |
| GET | `/sell-watch-windows` | Full access | [get_windows](../backend/app/routes/sell_watch_window_routes.py#L34) |
| GET | `/sell-watch-windows/admin/page` | Admin | [get_admin_windows_page](../backend/app/routes/sell_watch_window_routes.py#L52) |
| GET | `/sell-watch-windows/{window_id}` | Full access | [get_window](../backend/app/routes/sell_watch_window_routes.py#L63) |
| POST | `/sell-watch-windows` | Admin | [add_window](../backend/app/routes/sell_watch_window_routes.py#L72) |
| PATCH | `/sell-watch-windows/{window_id}` | Admin | [edit_window](../backend/app/routes/sell_watch_window_routes.py#L83) |
| DELETE | `/sell-watch-windows/{window_id}` | Admin | [remove_window](../backend/app/routes/sell_watch_window_routes.py#L97) |
| GET | `/storage-suitability` | Full access | [get_items](../backend/app/routes/storage_suitability_routes.py#L34) |
| GET | `/storage-suitability/admin/page` | Admin | [get_admin_storage_page](../backend/app/routes/storage_suitability_routes.py#L52) |
| GET | `/storage-suitability/{item_id}` | Full access | [get_item](../backend/app/routes/storage_suitability_routes.py#L63) |
| POST | `/storage-suitability` | Admin | [add_item](../backend/app/routes/storage_suitability_routes.py#L72) |
| PATCH | `/storage-suitability/{item_id}` | Admin | [edit_item](../backend/app/routes/storage_suitability_routes.py#L83) |
| DELETE | `/storage-suitability/{item_id}` | Admin | [remove_item](../backend/app/routes/storage_suitability_routes.py#L97) |
| GET | `/cost-breakdowns` | Full access | [get_items](../backend/app/routes/cost_breakdown_routes.py#L34) |
| GET | `/cost-breakdowns/admin/page` | Admin | [get_admin_costs_page](../backend/app/routes/cost_breakdown_routes.py#L52) |
| GET | `/cost-breakdowns/{item_id}` | Full access | [get_item](../backend/app/routes/cost_breakdown_routes.py#L63) |
| POST | `/cost-breakdowns` | Admin | [add_item](../backend/app/routes/cost_breakdown_routes.py#L72) |
| PATCH | `/cost-breakdowns/{item_id}` | Admin | [edit_item](../backend/app/routes/cost_breakdown_routes.py#L83) |
| DELETE | `/cost-breakdowns/{item_id}` | Admin | [remove_item](../backend/app/routes/cost_breakdown_routes.py#L97) |

### Member features

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| POST | `/watchlist` | Signed in | [save_item](../backend/app/routes/watchlist_routes.py#L19) |
| GET | `/watchlist` | Signed in | [get_own_watchlist](../backend/app/routes/watchlist_routes.py#L28) |
| DELETE | `/watchlist/{item_id}` | Signed in | [remove_item](../backend/app/routes/watchlist_routes.py#L36) |
| GET | `/testimonials` | Public | [get_public_testimonials](../backend/app/routes/feedback_routes.py#L64) |
| POST | `/feedback` | Signed in | [submit_feedback](../backend/app/routes/feedback_routes.py#L69) |
| GET | `/feedback/summary` | Admin | [get_feedback_summary](../backend/app/routes/feedback_routes.py#L78) |
| GET | `/feedback` | Admin | [get_feedback_list](../backend/app/routes/feedback_routes.py#L86) |
| GET | `/feedback/admin/page` | Admin | [get_feedback_page](../backend/app/routes/feedback_routes.py#L104) |
| GET | `/feedback/{feedback_id}` | Admin | [get_feedback_item](../backend/app/routes/feedback_routes.py#L117) |
| PATCH | `/feedback/{feedback_id}/testimonial/publish` | Admin | [publish_testimonial](../backend/app/routes/feedback_routes.py#L126) |
| PATCH | `/feedback/{feedback_id}/testimonial/hide` | Admin | [hide_testimonial](../backend/app/routes/feedback_routes.py#L142) |
| DELETE | `/feedback/{feedback_id}` | Admin | [remove_feedback](../backend/app/routes/feedback_routes.py#L159) |
| GET | `/push/subscribed` | Signed in | [check_subscribed](../backend/app/routes/push_routes.py#L16) |
| POST | `/push/subscribe` | Signed in | [subscribe](../backend/app/routes/push_routes.py#L35) |
| POST | `/push/unsubscribe` | Signed in | [unsubscribe](../backend/app/routes/push_routes.py#L44) |

### Subscriptions and payments

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/subscriptions` | Admin | [get_subscriptions](../backend/app/routes/subscription_routes.py#L38) |
| GET | `/subscriptions/admin/page` | Admin | [get_subscriptions_page](../backend/app/routes/subscription_routes.py#L49) |
| GET | `/subscriptions/{user_id}` | Signed in | [get_user_subscription](../backend/app/routes/subscription_routes.py#L59) |
| POST | `/subscriptions/send-trial-reminders` | Admin | [trigger_trial_reminders](../backend/app/routes/subscription_routes.py#L73) |
| POST | `/subscriptions/cron/send-trial-reminders` | Cron secret header | [cron_trigger_trial_reminders](../backend/app/routes/subscription_routes.py#L82) |
| PATCH | `/subscriptions/{user_id}/status` | Admin | [set_subscription_status](../backend/app/routes/subscription_routes.py#L94) |
| POST | `/payments/{reference}/verify` | Signed in | [verify_payment](../backend/app/routes/payment_routes.py#L41) |
| POST | `/payments/initiate` | Signed in | [start_payment](../backend/app/routes/payment_routes.py#L51) |
| POST | `/payments/webhook` | Paystack signature | [paystack_webhook](../backend/app/routes/payment_routes.py#L60) |
| GET | `/payments` | Admin | [get_payments](../backend/app/routes/payment_routes.py#L76) |
| GET | `/payments/page` | Admin | [get_payments_page](../backend/app/routes/payment_routes.py#L88) |

### Admin and operations

| Method | Path | Who can call it | Handler |
| --- | --- | --- | --- |
| GET | `/users` | Admin | [get_users](../backend/app/routes/user_routes.py#L22) |
| GET | `/users/page` | Admin | [get_users_page](../backend/app/routes/user_routes.py#L30) |
| GET | `/users/{user_id}` | Admin | [get_user_by_id](../backend/app/routes/user_routes.py#L39) |
| PATCH | `/users/{user_id}` | Admin | [edit_user](../backend/app/routes/user_routes.py#L48) |
| GET | `/admin/summary` | Admin | [dashboard_summary](../backend/app/routes/admin_summary_routes.py#L14) |
| POST | `/activity/ping` | Public | [ping](../backend/app/routes/activity_routes.py#L16) |
| GET | `/activity/summary` | Admin | [summary](../backend/app/routes/activity_routes.py#L23) |
| POST | `/activity/seen` | Admin | [seen](../backend/app/routes/activity_routes.py#L31) |
| GET | `/audit-logs` | Admin | [get_logs](../backend/app/routes/audit_log_routes.py#L22) |
| GET | `/audit-logs/page` | Admin | [get_logs_page](../backend/app/routes/audit_log_routes.py#L34) |
| GET | `/audit-logs/{audit_log_id}` | Admin | [get_log](../backend/app/routes/audit_log_routes.py#L43) |
| GET | `/faq` | Public | [get_published_items](../backend/app/routes/faq_routes.py#L58) |
| GET | `/faq/admin` | Admin | [get_admin_items](../backend/app/routes/faq_routes.py#L72) |
| GET | `/faq/admin/page` | Admin | [get_admin_faq_page](../backend/app/routes/faq_routes.py#L84) |
| GET | `/faq/{faq_id}` | Public | [get_published_item](../backend/app/routes/faq_routes.py#L95) |
| POST | `/faq` | Admin | [add_item](../backend/app/routes/faq_routes.py#L100) |
| PATCH | `/faq/{faq_id}` | Admin | [edit_item](../backend/app/routes/faq_routes.py#L111) |
| PATCH | `/faq/{faq_id}/publish` | Admin | [publish_item](../backend/app/routes/faq_routes.py#L125) |
| PATCH | `/faq/{faq_id}/hide` | Admin | [hide_item](../backend/app/routes/faq_routes.py#L138) |
| DELETE | `/faq/{faq_id}` | Admin | [remove_item](../backend/app/routes/faq_routes.py#L151) |
| POST | `/internal/operations/recover-payments` | GitHub OIDC token from the scheduled workflow | [recover_payments](../backend/app/routes/operations_routes.py#L135) |
