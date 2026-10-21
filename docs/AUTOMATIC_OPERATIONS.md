# Automatic payment recovery and failure alerts

The existing public GitHub repository runs `.github/workflows/priceyard-operations.yml`
at minute 17 every two hours (UTC), only after the repository variable
`PRICEYARD_OPERATIONS_ENABLED` is explicitly set to `true`. Publishing the workflow
alone does not start recovery. This is fallback recovery; Paystack webhooks and
the payment callback continue handling purchases immediately. No new service or
database is created. The runner needs no database, Paystack, email or long-lived
application credentials.

GitHub supplies a short-lived OIDC identity to the existing API. The API accepts
only this repository's approved workflow on `master`, when explicitly enabled.
It reuses the existing idempotent reconciliation service, purchase verification,
subscription rules and PostgreSQL single-worker lock. Each run processes at most
two serial pages of 25 recorded pending/failed purchases, within a four-minute
job limit; it never initiates a new charge.

The API encrypts the bounded recovery position. Only that opaque value is saved
in a small GitHub artifact for 14 days, including before reporting individual
recovery failures. No payment IDs, customer records, response bodies or tokens
are written to Actions logs. A failed download never silently resets progress.
An initial run without artifacts starts an idempotent full cycle.

The same job checks frontend `/api/health`, backend `/health` and the login HTML.
Database/provider failures during recovery also fail the job. GitHub's native
Actions failure notifications are independent of Render and the owner's PC.
The approved owner must enable **GitHub Settings → Notifications → Actions →
Send notifications for failed workflows only → Email**, and select **Watch →
Custom → Actions** for the repository. Confirm an actual failure email arrives
using **Actions → PriceYard operational safeguards → Run workflow →
simulate-failure**; this mode contacts neither the application nor Paystack.
`health-only` makes only the three read-only application requests.

## Limits and recovery

- Every-two-hours is the intended fallback/alert detection interval, not a
  real-time guarantee. GitHub scheduled jobs can be delayed; the Actions page
  shows the last run. Public inactive repositories can have scheduling disabled
  after 60 days without repository activity; check the workflow remains enabled.
- Two-hour checks avoid continuous keep-alive requests to sleeping Free Render
  instances. Continue watching the shared Render Free-hours allowance; another
  application in the workspace also consumes it.
- `error`, `missing_record`, `review_required`, HTTP failure, malformed response
  or an unexpected concurrent worker raises a failure notification. Review the
  existing private Admin/payment audit evidence; do not retry a charge manually.
- Set GitHub **Settings → Secrets and variables → Actions → Variables →
  PRICEYARD_OPERATIONS_ENABLED** to `true` only after the backend rollout and
  negative authorization checks pass. Missing/`false` skips scheduled recovery
  and manual `recover`; manual `health-only` and `simulate-failure` remain
  available on `master` while this gate is off.
- To pause recovery, set that variable to `false`, or disable this workflow in
  GitHub Actions. This blocks subsequent runs; an already-running bounded job
  must be cancelled separately if immediate interruption is needed.
  To remove API access,
  disable `OPS_RECOVERY_ENABLED` in the backend's existing environment, observing
  the normal controlled deployment procedure. No database migration is needed.
- Rotating the application's existing signing secret invalidates old encrypted
  checkpoints. Stop the workflow and deliberately remove only its checkpoint
  artifacts before resuming a full idempotent scan; never alter payment records.
- The workflow is prepared locally until the release evidence records its
  production activation, a successful run, and confirmed failure-email receipt.

Sources: [GitHub OIDC](https://docs.github.com/en/actions/concepts/security/openid-connect),
[workflow notifications](https://docs.github.com/en/account-and-profile/managing-subscriptions-and-notifications-on-github/setting-up-notifications/configuring-notifications),
[scheduled events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule),
[Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
