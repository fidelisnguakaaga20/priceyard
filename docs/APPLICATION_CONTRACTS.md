# Existing PriceYard contracts

This is a maintenance reference for approved behavior, not permission to change
the product. [PRICEYARD_PROGRESS.md](../PRICEYARD_PROGRESS.md) records individual
approvals, all36 statuses, commits, test evidence and the next unfinished tasks.

## Original product and purchased value

Keep the original appearance,14 Admin dashboard cards, commodity/market names,
recorded measurements, terminology and features. No invented grades, weights,
markets, defaults or subscription/referral rules. Missing measurements remain
missing. Price comparisons use matching recorded specifications; distinct
market/unit/bag-size/type series stay separate. Preserve all historical rows.
Cost references without a saved unit say “Unit not recorded”; never inherit a
unit from a different record. Market observations are not guaranteed outcomes.

The trial remains14 days. Monthly is NGN2,500 for30 days; seasonal is NGN6,000 for
90 days. Approved renewals add purchased days after remaining paid time. Purchases
during a trial retain remaining trial time before paid days. The existing paid
whole-day UTC expiration and approved rounding of the trial boundary remain.
Indefinite manual grants block new checkout; confirmed existing purchases are
held for review with evidence/access preserved. Never guess a legacy payment's
entitlement or overwrite an indefinite grant. See
[the exact approval](PURCHASE_VALUE_APPROVAL.md) and
[reconciliation operations](PAYMENT_RECONCILIATION.md).

Keep the existing seven-day referral reward and its current registration
qualification. Changing qualification, caps, verification requirements, renewal
pricing or plan duration needs a separate owner decision.

Current/history dropdowns retain their original labels but submit existing catalog
IDs, distinguishing prefix names and same-named markets. Newly generated detail
and share links carry existing identity; renaming does not change the referenced
commodity. Shared-price IDs select a commodity's current public records, never
publish a historical row's amounts or private sources. Legacy text-search API
parameters retain substring semantics. Name-only detail/share links require exact
unambiguous identity; do not invent aliases or guess legacy duplicate ownership.

## Accounts and authorization

Trial/paid are entitlement states, not additional staff roles. Staff authority
and customer entitlement are checked separately. Server-side authorization is
required even when a button/route is hidden in the browser. Private source
identities must not leak through public prices, CSV, audit responses or errors.
Legitimate Admin source access and underlying audit evidence stay available.

Password reset invalidates earlier login versions. Logout revokes the presented
token; disabling/re-enabling an account must not revive previous credentials.
Never save raw login tokens in the revocation table. Google subject ownership
must be verified: matching an existing email alone cannot attach a Google account.
Existing password/reset fallback remains. Session duration and RememberMe policy
remain unchanged; JS token-storage and offline revocation limits are still open
PY-07 work, not a claim of complete protection.

Watchlist/push/account operations enforce ownership. Channel failure must not
skip other alert channels. Notifications occur after durable business writes;
delivery failure cannot imply an already-saved record was lost. Delivery retries
and live-provider monitoring remain operational readiness work.

## Data preservation and maintenance

Business changes and sanitized audit records save atomically. Concurrency checks
must use native PostgreSQL when locks/transactions are material. Never merge
duplicate catalog records or infer deleted source links automatically.

The migration preflight refuses populated unreviewed legacy schemas before old
migration steps. Reviewed local0021-to0022 is additive. Downgrading login
revocation storage is refused to protect sessions. This does not repair old data
or prove a production restore. See [migration preservation](MIGRATION_PRESERVATION.md).

Offline copies visibly identify themselves as saved, not live, with device save
time. Only approved public resources are cached. Private/history/authenticated
resources must not enter the public offline cache.

HTTP input is bounded before parsing, database writes or provider calls:4MiB
body,8KiB encoded request target and64KiB headers. Declared lengths and actual
chunks are checked; malformed lengths/disconnects cannot cause partial writes.
The original decoded2MiB screenshot allowance fits the encoded-body budget.
Existing field/storage rules and stored long records remain; no new per-field
editorial character policy or truncation is inferred from these technical bounds.

Owner-approved Admin paging is recorded in [the exact scope](ADMIN_LIST_PAGING_APPROVAL.md).
Users and Payments currently have100-record pages, Previous/Next, complete totals,
preserved refresh/back/edit behavior and unchanged forms/columns/styles. New
`/users/page` and `/payments/page` are Admin only. Counts and rows share one DB
statement/snapshot. Existing `/users` and `/payments` still return complete schema-
checked JSON arrays using100-record cursor batches, with guaranteed close on
completion/disconnect/cancellation. Other Admin lists/public history remain PY-20
work; never silently truncate an old API or chart to mark paging complete.

## Honest completion boundaries

Completion means the finite identified application requirement and its evidence
are satisfied. Do not keep reopening completed items for hypothetical work, or
mark pending owner policies as implemented. Dates/day-filter display semantics,
movement/confidence rules and remaining list bounds,
session-storage policy retain their tracker statuses. Current catalog/filter/link
identity safeguards are complete in PY-29; legacy repairs remain separate.

PY-35 owns production/provider compatibility, deployment permissions, backups and
restore rehearsal, shared production rate limits, live scheduling/checkpoint
storage, monitoring and reviewed legacy repairs. Local synthetic success proves
local application behavior only. No deployment or production mutation is approved.

For each small batch: inspect existing changes, implement only unfinished scope,
run relevant backend/native/browser checks sequentially, fix failures, record
exact counts/limits/evidence, commit locally and leave resumable progress. Preserve
master and the old backup; never merge the old hardening branch wholesale.
