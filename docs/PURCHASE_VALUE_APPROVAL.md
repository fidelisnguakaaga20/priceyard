# Purchased-time rules: time preservation and indefinite-grant handling approved

Owner approved both time-preservation rules on 2026-10-16, then separately
approved the indefinite-grant checkout/held-purchase scope recorded below.

No change to NGN 2,500 monthly / 30 days, NGN 6,000 seasonal / 90 days,
or the original 14-day trial is proposed. No production change is authorized.

The current activation replaces the end date with today plus the purchased
duration. Paying early can therefore remove remaining paid days or trial time.

Approved local-development rules for PY-32 (1 and 2):

1. On an active dated paid subscription, append the purchased 30/90 days to
   its future end date. Example: 10 days remaining plus monthly purchase gives
   40 days remaining. Expired/free accounts retain today as the starting anchor.
2. On a valid remaining trial, append purchased days after the trial end date.
   Preserve original trial timestamps. Because paid access currently uses whole
   dates, keep access through the resulting end date, matching its existing
   inclusive-date rule. This rounds the final boundary up within that day and
   does not remove any trial time; no exact-hour billing field is introduced.
3. Indefinite manual grants remain indefinite. Do not silently convert them to
   expiring access. Their checkout/pending-payment handling is a separate owner
   decision, now approved in the specific scope below; implementation follows
   verification of the current referral batch.

Rules 1 and 2 change activation
calculations and tests; no new product fields, forms, plan, price, referral rule,
production migration or historical backfill. Successful payment/audit rows remain
preserved. Existing already-processed purchases are not automatically recalculated.

## Approved: payments during an indefinite Admin grant

Owner approved this exact local-only scope on 2026-10-16:

- Block new checkout while an active subscription has no end date. Do not send
  a provider request or create another purchase in that state. Explain through
  the existing checkout error that the account already has indefinite access.
- If an existing pending purchase is confirmed during such a grant, preserve
  the grant and leave purchased days unused for manual review. Preserve the
  payment reference and verified provider transaction ID; save one sanitized
  review audit in the existing audit table. Keep payment pending activation.
- Return a controlled conflict rather than reporting completed activation.
  A retry after the grant is deliberately resolved can apply the purchased days
  exactly once. Never silently replace indefinite access with a dated plan.
- No automatic refund, forfeiture, new status/database field, product screen,
  production change or historical backfill. Refund/grant-resolution decisions
  remain with the business owner.

Affected existing files if approved: payment_service.py and its HTTP/native
PostgreSQL/browser tests. Existing manual grant administration remains unchanged.
