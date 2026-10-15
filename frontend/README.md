# PriceYard frontend

React 18, TypeScript, React Router and Vite. Includes public/member pages,
Reporter submissions, email verification/recovery, payment status and administrator
management. Administrator routes load lazily; the backend enforces permissions.

## Safe build and tests

Use the prepared P00 runtime from the repository root:

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\prepare_frontend.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_browser_checks.py'
```

The preparation script copies allowlisted source/configuration into a disposable
snapshot, selects declared local tools, excludes dotenv/symlinks, clears inherited
application configuration, runs Node regression tests, TypeScript and Vite.
The browser wrapper requires that snapshot's successful build and a fresh profile
with synthetic routes. Neither command targets the deployed site.

`package-lock.json` records declared dependencies. Tool acquisition is separate
from runtime verification; see [P00](../audit-prep/p00/README.md). A bare
`npm run build` in a configured working directory is not the approved secret-free
verification path.

## API and authentication

`VITE_API_URL` selects the backend base; absent it, requests use `/api`.
Development proxy targets must point to an approved isolated backend, not a live
URL. Frontend variables are public build inputs and must contain no secrets.
Use exact backend CORS origins for a separately hosted frontend.

Access credentials live in memory; refresh credentials use sessionStorage or
localStorage according to remember choice. Requests time out after 20 seconds.
A recoverable 401 rotates credentials once; transient network failures do not
automatically destroy an otherwise recoverable session.

Refresh credentials remain JavaScript-readable. HttpOnly cookie sessions and MFA
are not implemented. Avoid remembered access on shared devices. Logout clears
local state and attempts server revocation/push removal; offline failure is
reported without claiming confirmed server sign-out.

## Product contracts

- Trial: 14 days from registration.
- Monthly: NGN 2,500 for 30 days.
- Seasonal: NGN 6,000 for 90 rolling days, not a calendar farming season.
- No automatic recurring charge. Display exact expiry in Africa/Lagos.
- Payment callback checks authenticated backend status; returning from checkout
  alone never proves activation.
- Public current summaries omit premium guidance. History and deeper intelligence
  require backend-confirmed full access. Staff authority survives commercial expiry.
- Prices/charts separate market, bag size, unit, variant and grade. Missing observed
  averages remain unknown; do not calculate a midpoint to fill the field.
- Forms interpret Nigerian observation times consistently; date search is a Lagos
  calendar day. New costs retain their own measurement and reference time.
- Published corrections require a reason. Withdrawal retains backend evidence.
- Lists respect server pagination; a fetched page is not a total-count metric.

Reference: [API contracts](../docs/api-endpoints.md) and
[access matrix](../docs/access-control-matrix.md).

## PWA and accessibility

The worker caches a validated public shell, same-origin static assets and explicitly
marked anonymous current-price responses. It bypasses authenticated/history/provider
traffic. Current data has bounded retention (24 hours, 30 entries), visible cache
age and recovery behavior for backend failures. It does not provide premium offline
access.

Public-current caching uses the same-origin `/api/price-updates` path and the
backend `X-PriceYard-Public: true` marker. Cross-origin direct API deployments do
not automatically get that cache behavior; do not widen cache rules to compensate.

Navigation is viewport-bounded; onboarding manages keyboard focus and Escape.
Administrator selection controls and labels support keyboard operation. These
changes require browser/assistive-technology acceptance beyond static/unit checks;
do not claim universal accessibility or installation support from a successful build.

## Performance and remaining work

The administrator dashboard uses the protected aggregate metrics endpoint instead
of counting downloaded first pages. Administrator list controls request bounded
pages; identical anonymous public GETs are coalesced, and consumer detail requests
are scoped. These controls do not establish production throughput.

Compressed legacy administrator components remain candidates for incremental
formatting/refactoring. Real device installation, full assistive-technology coverage
and deployed-provider behavior require additional acceptance.
See [audit status](../docs/audit-remediation-status.md) for these limits and
[progress](../PRICEYARD_PROGRESS.md) for actual verification results.
