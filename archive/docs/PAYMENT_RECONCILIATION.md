# PY-31 recorded-payment recovery — local implementation

The explicit reconciliation job recovers recorded pending/failed purchases when
the webhook and customer return were both missed. It verifies existing references
through the same strict GET verification and atomic activation used by callbacks.
It never initializes a payment, charges a customer, invents evidence or re-credits
a successful legacy record. Amount/currency/reference/provider-ID checks, approved
30/90-day carry-forward and manual-grant review holds remain unchanged.

Application acceptance: default dry run has no provider calls or writes; confirmed
funds recover without customer interaction; unconfirmed/invalid responses never
grant access; one error does not stop the next purchase; retries/concurrent webhook
produce one credit/audit; all purchased/trial time and manual grants survive.

The command is `python -m app.jobs.reconcile_payments` from the backend environment.
It defaults to preview. Only explicit `--apply` enables existing verification and
activation. **Do not execute against live configuration under local authorization.**
No scheduler, startup worker, production configuration or deployment is installed.
Production execution/scheduling/provider verification needs owner approval (PY-35).

Resource contract: serial pages, default25/max100 recorded IDs, soft45-second
budget (max300); an in-flight verification retains its existing3/15-second timeouts.
PostgreSQL session advisory locking permits one applying worker. SQLite is only
for serial synthetic tests. A fixed ceiling excludes new purchases from an ongoing
sweep. Carry `next_after_id` and `ceiling_id` into the next call until `complete`
is true; then start a fresh sweep. Completion means the snapshot was examined,
not that every purchase was confirmed. Persist the returned checkpoint in the
future scheduler so old unconfirmed purchases cannot starve later purchases.

Reports contain record IDs/outcomes only. Failed/mismatched purchases retain their
evidence for retry/review. Existing successful records with ambiguous historical
access are excluded: no automatic compensation, refund, chargeback or data repair.
Those require evidence and explicit reviewed resolution. Scheduling frequency,
checkpoint storage, monitoring and live provider/host testing remain PY-35 gates.
