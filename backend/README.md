# PriceYard backend

FastAPI, SQLAlchemy 2, PostgreSQL/Psycopg and Alembic. Application dependencies are
declared in `requirements.txt`; test additions are in `requirements-dev.txt`.
`requirements-dev.lock` records the exact Windows/Python 3.14 verification
environment, not a universal Linux production lock.

## Start with isolated verification

Run from the repository root using the prepared P00 virtual environment:

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_backend_tests.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\verify_migrations.py'
```

A focused test selection uses `--pattern test_price_integrity.py` or
`--pattern test_http_workflows.py` on the SQLite runner. PostgreSQL tests use the
second, dedicated runner; do not run them through ordinary unittest discovery.

See [P00 instructions](../audit-prep/p00/README.md). No existing dotenv files,
customer exports or live provider credentials belong in the test environment.
Dependencies are acquired separately in disposable environments. Never use the
historical owner smoke scripts as the current safe test command.

## Authentication and ownership

| Operation | Behavior |
|---|---|
| Register | Local active account, unverified email, unchanged registration-started 14-day trial |
| Login | Existing bcrypt password remains valid; active account required |
| Google login | Verified provider subject/audience/issuer; matching local email returns a conflict instead of auto-linking |
| Link Google | Authenticated account, verified matching email, current password and verified Google identity required |
| Verification | Hashed, expiring, single-use token; generic request response and resend cooldown |
| Password recovery | Generic request response; atomic single-use token claim; changes password and revokes sessions |
| Refresh | Rotates hashed refresh credential in a server-recorded session |
| Logout / logout all | Revokes current/all server sessions |
| Disable account | Revokes sessions; reactivation does not revive them |

Default access JWT lifetime is 15 minutes. Remembered server sessions default to
90 days; nonremembered sessions default to 24 hours. Verification links default to
30 minutes and reset links to 15 minutes. Limits are configurable; these are source
defaults, not inspected production settings. Passwords retain the existing minimum
eight characters and maximum 72 UTF-8 bytes; no truncation occurs.

JWTs require the current server session and user authentication version. Previously
issued legacy JWTs without a session identifier require a fresh login after rollout.
Existing account/password/payment/history data is retained. Email verification does
not restart the trial. A valid email reset proves ownership and signs out predecessor
sessions; Google email collisions are not automatically merged.

The frontend holds access tokens in memory and stores refresh credentials in
sessionStorage/localStorage according to the remember choice. HttpOnly cookies,
administrator MFA and a session-device management screen are not implemented.
An offline local logout cannot promise that the server received revocation.

## Commercial and authorization contracts

NGN 2,500 buys 30 days; NGN 6,000 buys 90 days. There are no recurring charges.
Purchased terms are recorded with checkout. Activation uses validated provider
evidence, never the browser callback. Payment, entitlement, referral qualification
and audit changes commit together. Replays apply once; distinct renewals add time.

Paid time starts after the latest of usable activation, existing paid cutoff and
valid remaining trial. Indefinite manual grants are preserved. Legacy end dates
retain the complete UTC date. Access checks enforce expiry without relying on a
scheduled status job. Cancellation intent does not erase purchased/manual access.

Referral registration records attribution only. A verified referred account's first
successful purchase may award an eligible Trial/Free referrer seven days. The
prospective campaign cap is four awards (28 days) per referrer. Previously earned
days remain intact.

See [access matrix](../docs/access-control-matrix.md) for public/basic/full response
fields, staff authority, ownership and inactive-account rules.

## Price integrity

Current SQL selection partitions recorded commodity/market/unit/bag/variant/grade,
then removes an outdated latest row. No fallback resurrects an older observation.
Unknown legacy measurements are labelled; no conversions or grades are fabricated.

New timestamps require offsets and normalize to UTC. Search dates use Africa/Lagos
boundaries; future tolerance is five minutes. Recorded averages are optional;
missing averages remain null and movement is unknown. Approval derives previous
ranges from a comparable predecessor. Backfill/correction adjusts its successor.

Published corrections require a reason of at least ten characters and retain
restricted original-value evidence. Moving a linked price's specification is
rejected. Consumer schemas and general audit snapshots exclude private sources.
DELETE withdraws a price, deactivates commodity/market identity, or archives
market/quality/cost intelligence as applicable; it does not physically erase those
business records.

## Transactions and notifications

One HTTP AtomicSession owns the complete request transaction. Service commit calls
flush; the HTTP boundary performs the final commit before returning success.
Validation/provider/audit failures roll back the request. Notification enqueue
shares the transaction; actual delivery uses a separate worker.

Checkout preparation is a deliberate exception: its new pending purchase intent is
durable before contacting Paystack, so a timeout cannot erase the reference needed
for reconciliation. This commits no access grant. Actual successful-payment
activation still commits payment/grant/subscription/audit changes together.

The explicit operational command, **for an approved configured environment only**:

```text
python -m app.notification_worker --limit 50
```

Run from `backend` with the correct operator-managed configuration. This command
sends real messages when real providers are configured; it is not an isolated test.
No scheduler is installed automatically. Use synthetic senders in tests.

Workers claim jobs with PostgreSQL SKIP LOCKED, use five-minute leases and
compare-and-set acknowledgement, retry channels independently, and stop after five
attempts by default. Provider delivery is at least once: a crash after provider
acceptance but before acknowledgement may duplicate a message.

Account-proof email payloads are encrypted at rest in the temporary outbox and
rechecked for expiry/consumption before delivery. Preserve the configured encryption
key derivation secret while pending proof emails exist, or expire/reissue the proofs
through a reviewed process; do not copy pending payloads to logs.

Push endpoints are limited to supported HTTPS providers; keys are validated,
redirects disabled, public DNS addresses checked and the checked address pinned
while retaining TLS hostname validation. New push providers require reviewed
allowlist/transport changes. Default per-account device cap is ten.

## Schema and operational preparation

Prepared revisions:

- 0022: ownership proof and revocable sessions; legacy verification stays unknown.
- 0023: payment/grant/referral evidence and preserved legacy paid cutoffs.
- 0024: price revisions, predecessor/grade/cost provenance, archived intelligence,
  normalized identity constraints and indexes.
- 0025: durable notification jobs/leases and explicit target-alert measurement.

Migration 0024 aborts on normalized duplicates or invalid historical previous-price
bounds before its DDL. It never automatically merges, deletes, guesses units or
repairs historic timezone values. Legacy successful payments require reviewed
reconciliation, not blanket reapplication.

Migrations 0023–0025 refuse destructive automatic downgrade. Keep a compatible
application rollback or use reviewed forward repair and verified backup recovery.
No production migration is authorized by these instructions.

The default limiter uses `memory://`; multiple processes need a shared store
through `RATE_LIMIT_STORAGE_URI`, its reviewed Redis client/dependency and
connection/availability testing. Shared-store deployment has not been validated.
Use exact CORS origins and HTTPS; keep secrets in the hosting secret store.

`GET /health` is process liveness only. `GET /ready` checks required secret validity,
database connectivity and exact expected schema revision; failure returns a redacted
503. It does not prove provider readiness. `GET /admin/metrics` returns authorized
SQL aggregates without computing totals from downloaded pages. Deployed monitoring,
restoration and capacity remain acceptance tasks.
