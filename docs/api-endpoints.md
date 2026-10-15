# PriceYard API contracts

Current October 2026 hardening-branch contracts. This document supersedes the
earlier stage-by-stage endpoint descriptions; historical stage evidence remains
under `docs/evidence`. Backend schemas/routes are the final field-level reference.
No deployed API was contacted to prepare this document.

## Common behavior

JSON inputs/outputs unless noted. Monetary observations use Decimal, with at most
14 digits and two decimal places. Pydantic validation errors return 422. Protected
routes use `Authorization: Bearer <access_token>`; invalid/missing authentication
returns 401 and insufficient authority returns 403. Inactive accounts are blocked.
Ownership checks never trust a client-supplied user ID.

A supplied malformed/invalid Authorization header is rejected even on an optionally
authenticated price endpoint. Omitting it requests the public view.

Request bodies are bounded before decoding (default three MiB); oversized bodies
return 413. Authentication/provider/write rate limits may return 429. The HTTP
unit of work commits mutations and audit records before success; commit failure
returns a controlled 503. Provider failures never justify inventing successful
payment or email delivery.

Paginated APIs retain array responses. Most paged lists use `page >= 1` and
`page_size = 1..1000`. Price history/admin history, users, subscriptions,
administrator flagged prices, audit logs and feedback default to 100. Current
prices and scoped intelligence default to 1000. Payments instead use
`offset >= 0` and `limit = 1..500`, default 100. A page is not a total count.

## Authentication

| Route | Input / access | Result |
|---|---|---|
| POST /auth/register | Name, email, password; optional phone/referral_code | Safe user; 14-day trial begins immediately; verification queued |
| POST /auth/login | Email, password, optional remember_me | Session credentials |
| POST /auth/google | id_token, optional remember_me | Known verified identity login or new account; email collisions require explicit recovery/linking |
| POST /auth/refresh | refresh_token | Rotated refresh credential and new access token |
| POST /auth/logout | Current bearer session | Revokes that server session |
| POST /auth/logout-all | Authenticated | Revokes all account sessions |
| POST /auth/request-verification | Email | Generic message; eligible proof queued with cooldown |
| POST /auth/verify-email | token | Consumes valid single-use email proof |
| POST /auth/google/link | Bearer, id_token, current password | Links verified matching identities explicitly |
| POST /auth/forgot-password | Email | Generic message; eligible recovery queued |
| POST /auth/reset-password | token, new_password | Atomic one-use claim; password changed and sessions revoked |
| GET /auth/me | Bearer | Safe current account |
| GET /auth/referral-summary | Bearer | Own attribution summary and reward size |

Session credential response: `access_token`, `token_type`, `refresh_token`,
`expires_in`, `session_expires_at`. Access lifetime defaults to 900 seconds.
Stored refresh tokens are hashed server-side; cookie-based credentials are not
implemented. The legacy API default for omitted remember_me is true; current
frontend login defaults to an explicit unchecked remember choice.

New passwords retain minimum eight characters and maximum 72 UTF-8 bytes. Reset
defaults to 15 minutes and verification to 30 minutes. Old account email ownership
is not fabricated. Valid existing passwords remain valid; old JWTs without server
session identity require login again.

## Users, subscriptions and payments

| Route | Access / behavior |
|---|---|
| GET /users; GET /users/{id}; PATCH /users/{id} | Admin; bounded list, safe fields; role/activity management; last-active-admin protection |
| GET /subscriptions | Admin; page/page_size; all expired rows processed before the requested page |
| GET /subscriptions/{user_id} | Owner or Admin |
| PATCH /subscriptions/{user_id}/status | Admin; cannot erase valid purchased/manual access |
| POST /subscriptions/send-trial-reminders | Admin; eligible reminders accepted for queued delivery |
| POST /subscriptions/cron/send-trial-reminders | Exact secret-protected scheduler route; never a public cron |
| POST /payments/initiate | Authenticated account; plan monthly or seasonal; returns checkout URL/reference |
| POST /payments/webhook | Exact raw-body Paystack signature and validated event evidence |
| GET /payments/status/{reference} | Owner or Admin; distinguishes payment confirmation from access applied |
| GET /payments | Admin; offset/limit |
| POST /payments/reconcile | Admin; signed_payload, signature, reason, optional reviewed legacy_resolution |

Plans: NGN 2,500/30 days and NGN 6,000/90 days. No automatic recurring charges.
Renewals add to unused paid time/valid trial. Server access uses an exclusive UTC
cutoff; legacy inclusive end dates retain their entire date. Manual indefinite
grants survive payments. Cancellation records intent without deleting valid access.

Checkout terms/account binding are retained for reconciliation. Amount, currency,
successful state, customer, environment and provider transaction identity must
match. Callback URLs do not activate access. Duplicate events apply once. Historical
success records lacking proof of applied access require reviewed
`already_applied` or `apply_missing` reconciliation; never blanket replay them.

Pending checkout intent is persisted before provider initialization. This deliberate
transaction boundary grants no access and retains the reconciliation reference if
checkout creation times out. Admin/manual-grant accounts cannot start an unnecessary
subscription checkout.

Referrals qualify prospectively on a verified first successful purchase, once per
referred account. Eligible Trial/Free referrers receive seven days, capped at four
new awards per referrer. Existing earned time is retained.

## Commodities and markets

Public GET list/detail returns active records only. Admin GET
`/commodities/admin/all` and `/markets/admin/all` includes inactive records.
POST/PATCH/DELETE require Admin. DELETE deactivates retained identity instead of
erasing history. Stable IDs distinguish namesake markets. Normalized name/state
uniqueness is protected by database indexes after reviewed migration preflight.

## Prices and history

| Route | Contract |
|---|---|
| GET /price-updates | Current recorded measurement series; optional authentication selects response fields |
| GET /price-updates/comparison | commodity or commodity_id required; current market/specification observations |
| GET /price-updates/history | Full access; chronological approved active-reference history, including outdated rows |
| GET /price-updates/{id} | Public/limited only eligible current ID; full access may read eligible history |
| GET /price-updates/admin/history | Admin; all statuses and inactive references; page/page_size |
| GET /price-updates/admin/flagged | Admin; joined flag aggregates; page/page_size |
| GET /price-updates/my-stats | Own submitted/pending/approved/rejected counts |
| POST /price-updates | Admin/Reporter; starts pending |
| PATCH /price-updates/{id} | Admin; published corrections require correction_reason of 10..500 characters |
| PATCH /price-updates/{id}/approve | Admin; derives comparable predecessor/range/movement |
| PATCH /price-updates/{id}/reject | Admin; retains evidence |
| PATCH /price-updates/{id}/mark-outdated | Admin; does not cause older-current fallback |
| DELETE /price-updates/{id} | Admin; 204 withdrawal, retained row/links/revisions |
| POST /price-updates/{id}/flag | Authenticated account able to read the price |
| POST /price-updates/{id}/flags/resolve | Admin |

Current/history filters: commodity/market names, stable commodity_id/market_id,
date and movement; history also time_of_day. Historical date searches require full
access on every path. Date means Africa/Lagos calendar day. Current selection ranks
latest first, then applies outdated and movement filters.

Create requires commodity_id, market_id, price_low/high, unit, bag_size,
confidence_level, update_date_time and suggested_action. Average is optional.
Optional recorded metadata includes commodity_type, grade, market_day/time_of_day,
previous ranges, confidential sources and editorial commentary. Approval derives
previous ranges/movement rather than accepting contradictory supplied claims.

Public summary retains current/previous ranges, optional recorded average,
measurement, movement, confidence and observation metadata. Full access adds
possible_meaning, suggested_action and notes. Private source_1/source_2 are excluded
from consumer schemas. Reporter submissions cannot self-attest source/confidence
or editorial guidance; source values are stripped.

Recorded series includes commodity, market, unit, bag specification, variant and
grade. No physical conversion or grade is guessed. Missing bag specification is
legacy_unspecified and cannot be joined into a comparable chart. Missing averages
produce unknown direction, never a fabricated midpoint. Responses include
measurement_series, measurement_status and previous_price_update_id.

New timestamps require an offset, normalize to UTC and cannot exceed five minutes
into the future. Corrections preserve originals. A linked observation's specification
cannot silently move beneath intelligence.

Only anonymous undated current lists emit `X-PriceYard-Public: true` and short
public cache lifetime; authenticated lists are private/no-store and vary by
Authorization. History/detail never emit the public-cache marker.

## Intelligence

GET market-signal list/detail requires authentication. Limited accounts receive
basic facts; deeper meaning/action requires full access. GET quality-signals,
buying-zones, sell-watch-windows, storage-suitability and cost-breakdowns requires
full access. Writes require Admin.

Lists support commodity_id/market_id and page/page_size. Consumers require active
references and an approved linked price. Admin management retains inactive-reference
visibility. Archived market/quality/cost records are omitted from normal lists.

Market/quality/storage price links must match commodity and market. Market and
quality DELETE archive retained rows. Buying-zone responses include validity_status
for either date boundary without automatically hiding records. Sell-watch periods
remain editorial strings; they are not authoritative dated forecasts.

New costs require commodity_id, market_id, unit, bag_size, reference_date_time and
purchase_price_reference; optional variant/grade and six nonnegative cost components.
The server calculates totals. Historical missing cost metadata stays null.
Required PATCH fields reject explicit null; nullable commentary may be cleared.

## Other implemented routes

| Group | Access / notable contract |
|---|---|
| GET /faq and /faq/{id} | Published only |
| GET /faq/admin/all | Admin, including hidden drafts |
| FAQ POST/PATCH/publish/hide/DELETE | Admin; content validation and audit |
| POST /feedback | Own authenticated submission; bounded text/screenshot |
| Feedback list/detail/summary/delete/testimonial administration | Admin; list page/page_size |
| GET /testimonials | Public curated safe fields |
| Watchlist GET/POST/DELETE | Own account; paired commodity/market uses AND matching |
| Push subscribe/unsubscribe/status | Own account and verified browser endpoint ownership |
| GET /audit-logs and /{id} | Admin; sanitized snapshots; list page/page_size |
| GET /admin/metrics | Admin; aggregate totals/current/effective-access counts; distinguishes recorded success, provider confirmation and access application; currencies stay separate |
| GET /reports/prices.csv | Admin; optional names/date range; Lagos day boundaries; safe textual spreadsheet cells |
| POST /activity/ping | Rate-limited public count |
| GET /activity/summary; POST /activity/seen | Admin |
| GET /share/commodities/{name} | Public social-preview HTML |
| GET /health | Process liveness only; not a database/provider readiness assertion |
| GET /ready | Required secret, database and exact expected revision check; redacted 503 on failure; not provider/backup readiness |

Targets compare only an explicitly confirmed measurement basis. Legacy numeric
targets are preserved but alerts remain paused until measurement is confirmed.
Notification payloads contain eligible public facts; delivery rechecks account,
watch/measurement, current observation and revision eligibility.

Endpoint schemas/OpenAPI describe the definitive optional fields. Monitoring,
provider compatibility, hosting headers, restore and capacity need separately
authorized environment verification; local route coverage is not live certification.

### Public social-preview identity

GET /share/commodities/{commodity_name} resolves the exact commodity identity. Optional positive `pu` selects only an eligible current observation of that commodity, market and measurement. Historical/wrong-commodity IDs and ambiguous unqualified links show a generic current-selection message; they never quote a guessed series or disclose history. Quantity, bag size, variant and grade accompany a current quote. CSV export rejects more than 10,000 selected observations and asks for narrower filters without removing data.
