# Testing

The backend tests, website page checks and style checks run automatically on every
push, and a deploy happens only when every one passes
([operations](operations.md#deploys)). The backup tool tests are run by hand.

## Backend tests

370 tests in [`backend/tests`](../backend/tests), run with:

```bash
python -I -B tools/local-test/guard.py                  # all tests
python -I -B tools/local-test/guard.py --pattern "test_payment*.py"
```

[`guard.py`](../tools/local-test/guard.py) runs the tests inside an isolated
process. Network connections, DNS lookups and child processes are blocked, real
configuration and `.env` files are ignored, and each test gets a fresh in-memory
SQLite database. A test can never reach the live database, Paystack, email or any
other outside service.

What they cover:

| Area | Examples |
|---|---|
| Sign-in and sessions | cookie sessions and CSRF, logout and login revocation, admin login lifetime, login throttling, password reset, Google account linking |
| Access control | full-access boundaries for history and intelligence, admin-only routes, owner protection, private source fields never published |
| Payments | checkout, webhook signature and evidence checks, verification, payment recovery, manual review holds, trial/paid expiry races |
| Data integrity | each change and its audit log saved together, catalogue identity, price claim evidence, Nigeria-time price days, migration safety |
| Lists and exports | paging totals, streaming history and CSV export, spreadsheet-formula protection |
| Notifications | watchlist alerts, push ownership and security, email delivery failures |
| Request limits | body, URL and header size limits, upload limits, rate-limit client address |
| Error reporting | private data removed before anything is sent to Sentry |

## Website page checks

[`frontend/tests/smoke`](../frontend/tests/smoke) opens the built website in a real
browser (Chromium, through Playwright) with a fake API and no network:

- every public page as a visitor, and every public, member and admin page as an
  admin;
- each at phone width (375 px) and desktop width (1280 px): 88 page views in total.

A page fails if it throws a script error, shows a blank main area, or has content
cut off at the screen edge. The menu and back navigation are also checked.

```bash
cd frontend
npx vite preview --host 127.0.0.1 --port 4322 --strictPort &
node tests/smoke/smoke.mjs
```

## Style and build checks

| Check | Command |
|---|---|
| Python layout and common mistakes ([`ruff.toml`](../ruff.toml)) | `ruff format --check . && ruff check .` |
| Website layout ([`.prettierrc.json`](../frontend/.prettierrc.json)) | `npm run format:check` (in `frontend/`) |
| Website types and build | `npm run build` (in `frontend/`) |

## Backup tool tests

The backup and scheduled-safeguard tools have their own tests, run by hand:

```bash
python -B tools/operations/test_backup_runner.py
python -B tools/operations/test_run_operations.py
```
