# Operations

## Hosting

| Part | Where |
|---|---|
| Website | Render static site `priceyard` (https://priceyard.onrender.com) |
| API | Render web service `priceyard-api` (https://priceyard-api.onrender.com) |
| Database | Supabase PostgreSQL |
| Payments / email | Paystack / Brevo |
| Error alerts | Sentry |

The website rewrites `/api/*` to the API, so the browser talks to one site only.
Both services run on Render's free plan, so the API sleeps when idle and the first
request after a pause is slower.

## Deploys

Every push runs [`.github/workflows/backend-tests.yml`](../.github/workflows/backend-tests.yml):

1. Python style checks (`ruff format --check`, `ruff check`) and all backend tests.
2. Website style check, type check and build, then the browser page checks.
3. Only on `master`, and only if every check passed: trigger the Render deploy hooks.
   The backend job then waits until `/health` reports the new commit.

Pushing to any other branch runs the checks without deploying.

## Health and error alerts

- `GET /health` returns `{"status": "healthy", "deployed_commit": "<sha>"}`. It
  checks only that the process is running, not the database.
- Unhandled server errors go to Sentry ([`error_reporting.py`](../backend/app/error_reporting.py))
  and high-priority issues trigger an email alert. Before sending, cookies, request bodies, query strings,
  environment values and email addresses are removed, and only the user's ID is kept.

## Scheduled safeguards

[`.github/workflows/priceyard-operations.yml`](../.github/workflows/priceyard-operations.yml)
runs at minute 17 of every second hour (UTC):

- **Health checks:** the website's `/api/health`, the API's `/health` and the login page.
- **Payment recovery:** finds recorded purchases that are still pending because both
  the Paystack webhook and the customer's return were missed, and verifies them with
  Paystack. It handles at most two pages of 25 purchases per run, within a four-minute
  limit, and never starts a new charge. The API accepts this call only with a
  short-lived GitHub OIDC token from this workflow on `master`. Progress is saved as
  an encrypted checkpoint.
- Any failure (an unhealthy check, a recovery error, or a payment needing review)
  fails the run, and GitHub emails the owner.

Manual runs (**Actions → PriceYard operational safeguards → Run workflow**):

| Mode | What it does |
|---|---|
| `health-only` | Only the three read-only checks |
| `simulate-failure` | Fails on purpose to test the alert email; contacts nothing |
| `recover` | Health checks plus payment recovery |

Recovery runs only while the repository variable `PRICEYARD_OPERATIONS_ENABLED` is
`true`. To pause it, set that variable to `false` or disable the workflow. To turn
off the API side, set `OPS_RECOVERY_ENABLED=false` on the backend.

Payment recovery can also be run by hand from `backend/`. It only previews unless
`--apply` is given:

```bash
python -m app.jobs.reconcile_payments          # preview
python -m app.jobs.reconcile_payments --apply  # verify and activate confirmed payments
```

## Trial reminders

`POST /subscriptions/cron/send-trial-reminders`, called by a scheduler with the
`X-Cron-Secret` header, emails users whose 14-day trial is ending. Admins can also
trigger it from the API.

## Backups

- [`tools/operations`](../tools/operations) runs encrypted database backups from the
  owner's Windows PC: a read-only `pg_dump` snapshot packed into an AES-256 encrypted
  archive. The archives and the credentials they need are kept outside Git. An
  off-device copy goes to a private Google Drive folder.
- An actual encrypted backup was restored into a separate, isolated database and
  checked table by table (October 2026). That is the proof the backup can be
  recovered.
- Backup tool tests: `python -B tools/operations/test_backup_runner.py` and
  `python -B tools/operations/test_run_operations.py`.
- Code is in Git; customer data is only in the database and its backups.

## If something goes wrong

1. Check the latest GitHub Actions runs, Sentry, and `/health` (which commit is live).
2. If a deploy caused it, revert the commit on `master`. The checks run again and
   redeploy the previous version.
3. Never replay or refund payments by hand without Paystack evidence; use payment
   recovery and the admin payment records.
4. To restore data, restore a backup into a new database first and check it, keeping
   the original untouched. Disable outgoing email, push, WhatsApp and payment jobs
   on the restored copy until it has been verified.
