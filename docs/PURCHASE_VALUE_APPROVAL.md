# Purchased-time rules awaiting owner approval

No change to NGN 2,500 monthly / 30 days, NGN 6,000 seasonal / 90 days,
or the original 14-day trial is proposed. No production change is authorized.

The current activation replaces the end date with today plus the purchased
duration. Paying early can therefore remove remaining paid days or trial time.

Proposed local-development rules for PY-32:

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
   decision; implementation of that case stays pending.

Only rules 1 and 2 are requested for approval now. They change activation
calculations and tests; no new product fields, forms, plan, price, referral rule,
production migration or historical backfill. Successful payment/audit rows remain
preserved. Existing already-processed purchases are not automatically recalculated.
