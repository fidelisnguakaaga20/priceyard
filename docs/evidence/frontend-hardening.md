# Frontend hardening implementation evidence

Evidence date: 15 October 2026 (Africa/Lagos).

This record describes implementation and the checks actually performed. It does
not certify mobile rendering, accessibility, installation, live payments or the
deployed application. No production data or provider accounts were used.

## Executed checks

Four allowlisted files were copied into a new disposable directory under
`audit-prep/p00/source-snapshot/frontend-pure-<run-id>/`:

- `frontend/src/lib/priceSeries.mjs`
- `frontend/public/sw.js`
- `frontend/tests/priceSeries.test.mjs`
- `frontend/tests/serviceWorker.test.mjs`

Node ran the copied tests with `audit-prep/p00/node_transport_guard.cjs` loaded
before the test runner, and `--test-timeout=20000`. No environment files or
application configuration were copied. The service-worker tests expose only a
fake transport to the worker. No live API requests were required.

Latest completed result: **14 tests passed, zero failed, zero skipped, exit code
0**. Reported test-runner duration: approximately **223.4 ms**. This is test
execution time, not an application performance benchmark.

The eight price/helper tests cover:

1. Commodity, market, quantity, package, variant and grade separation.
2. Separate observations when historical package sizes are missing.
3. Chronological ordering without mutating the input collection.
4. Authoritative approval responses replacing pending local rows.
5. Africa/Lagos day boundaries and one-sided date windows.
6. Nigeria form timestamps, including rejection of invalid calendar dates.
7. Confirmed target measurements and exact market/specification matching.
8. Preservation of the whole legacy UTC subscription end date.

The six service-worker tests cover:

1. Exclusion of authenticated, historical, external and unknown requests.
2. Explicit server permission before public-price caching.
3. Timestamp-labelled cache fallback after a backend failure.
4. Deletion of expired cached observations instead of replaying them.
5. Bounded public cache entries and the logout purge message.
6. Validation of the root HTML shell before installation caching.

Full frontend preparation uses `audit-prep/p00/prepare_frontend.py`. That runner
copies allowlisted source/tooling to a secret-free snapshot, clears inherited
application configuration, loads the transport guard, and runs Node tests,
TypeScript and Vite from the copy. **Any full-build or browser results belong in
the consolidated execution report; they are not claimed by this 14-test result.**

## Implemented user-visible changes

### Price display and recovery (PY-11–18)

- Home clears a resolved price-fetch error when a later request succeeds.
- Current-price filters synchronize with the URL and use stable IDs. Obsolete
  requests are aborted and cannot replace the selected scope's results.
- Filter choices refresh while polling is enabled; Data saver suppresses polling.
- History starts without a hidden Egusi restriction, supports explicit pages,
  and labels quantities/specifications on both tables and mobile cards.
- Charts separate markets and measurement series. An absent observed average
  produces an explicitly labelled range-midpoint line, never a fabricated mean.
- Commodity identity comes from the commodity catalog independently of whether
  any current price exists. Intelligence reads are scoped by IDs and each
  section exposes its own failure rather than silently hiding successful data.
- Cost records use their retained measurement/reference metadata. Legacy costs
  without measurements remain visible with quantity calculations unavailable.
- Buying-zone warnings handle either date bound and use the Nigerian day.
- Administrator mutation responses update the authoritative record collection;
  created records cannot continue overriding their later approvals/corrections.
- Administrator timestamps use explicit Nigerian input time. Observed averages
  are optional. Measurement labels accommodate bags and other packages.
- Mixed-measurement prefilling requires an explicitly selected source record;
  it does not copy a prior observation's source/confidence claims automatically.
- Corrections collect a reason and offer explicit clearing of nullable average,
  meaning, notes and source type while blank inputs preserve existing values.

### Watchlists and notifications (PY-12, PY-21)

- New price targets require a commodity, market and explicitly recorded unit and
  package. Type/grade participate in matching without inferred conversions.
- A user can copy a recorded specification or enter a known one explicitly.
- Historical targets lacking a confirmed basis remain retained and visibly
  paused until the owner confirms through `PATCH /watchlist/{id}`.
- Ordinary authenticated Free accounts retain their own watchlists and public
  current-price alerts. No new subscription restriction was introduced.
- Broad watches show labelled observations rather than silently treating the
  first market/package as a universal price.

### Administration and commercial wording (PY-19, PY-31–36)

- FAQ administration lists hidden and published entries. Selection is a real
  keyboard-operable button, and selected content can be populated for editing.
- Payments distinguish provider status, access application and legacy review.
  Older records can be loaded through bounded requests.
- The reconciliation form sends exact signed event JSON, provider signature,
  review reason and an explicit historical disposition when applicable. It
  never calls Paystack directly or accepts an unsigned browser success claim.
- Subscription administration shows trial and precise paid cutoffs in Nigeria
  time and identifies indefinite grants/cancellation requests.
- Dashboard prices remain NGN 2,500/30 days and NGN 6,000/90 days. The original
  registration-started 14-day trial remains unchanged; no recurring charge or
  yearly plan was added.
- Dashboard displays Member/Reporter/Administrator separately from current
  entitlement; a legacy paid role is not represented as proof of active access.

### Dashboard aggregation (PY-20, PY-22)

- The administrator dashboard requests `GET /admin/metrics` instead of downloading
  nine complete record collections to calculate counts. Existing activity/badge
  requests remain separate; no new activity polling was added to the dashboard.
- SQL aggregates cover all records rather than the first page of payments or
  history. Current-price counts use the same selection helper as current prices.
- Effective trial/paid counts check actual expiry and active-account state;
  stored subscription-label counts are displayed separately.
- Payment counts distinguish recorded success, provider confirmation, recorded
  access application and historical review. Decimal sums remain separated by
  currency and are labelled recorded amounts, not verified bank settlement.
- `test_admin_metrics_api.py` executed through the guarded backend runner:
  **three HTTP tests passed, zero failed/errors/skipped**. Tests use actual JWT
  dependencies and verify Guest/Free/Trial/Reporter/disabled-Admin rejection.
- Synthetic totals include 129 users, 130 payments and 110 feedback records, so
  assertions protect against first-100-record truncation. The exact NGN amount
  is 313,501.23 while the separate USD amount is excluded from that sum.
- A query-count assertion limits the tested HTTP request to at most 15 SELECT
  statements regardless of fixture size. This is a bounded-query regression
  check, not a production latency or capacity claim.

### Mobile, keyboard access and PWA (PY-23–25)

- Primary navigation has a viewport-bounded scroll area, an identified toggle,
  keyboard Escape handling and focus restoration.
- Mobile administrator sections collapse behind an accessible toggle instead
  of placing every section ahead of the page content.
- Onboarding handles initial focus, Tab containment, Escape, restoration and
  short-viewport scrolling. Explicit selection buttons replace clickable rows.
- The service worker caches only same-origin assets, a validated root shell,
  and exact current-price requests expressly marked public by the server.
- History, account data, authenticated requests, external APIs and arbitrary
  GET routes are excluded. Cache entries are bounded; public prices expire
  after 24 hours and carry saved timestamps on fallback.
- Logout can clear cached public data and outstanding notifications. Push
  notification navigation is restricted to the application's own origin.
- Offline messaging distinguishes a missing connection from known saved prices
  and labels cached observation time instead of claiming prices are live.

## Practical limits and remaining verification

- These tests exercise pure helpers and mocked worker behavior, not React page
  flows or a real browser's service-worker lifecycle.
- Mobile layout, keyboard/screen-reader behavior, 200% zoom, install/update
  behavior and cross-account notification handling still require browser proof.
- Offline public prices require the same-origin `/api/price-updates` deployment
  path and explicit public response header. An external API origin is excluded
  deliberately; no cross-origin offline support is claimed.
- The cache's saved time is when this device received data, not a replacement
  for each agricultural observation's own timestamp.
- Historical chart pagination is explicit: a chart represents the observations
  on the displayed page, not an unbounded complete series.
- Unspecified old measurements cannot be recovered from current prices. They
  remain unconverted and cannot establish a comparable target/series by guess.
- Signed reconciliation still requires retained provider evidence and reviewed
  business records. The form does not manufacture proof or retrieve live data.
- Process-level transport guards protect this test runner; they are not proof
  of a separately enforced VM, firewall or operating-system network boundary.

No source or dependency commits, pushes, merges or deployments were performed
as part of this frontend evidence record.

## Superseding root verification (2026-10-15)

Final source passed 21 guarded Node tests, TypeScript and the Vite build. Ten synthetic Chromium workflows passed, including mobile widths/focus, account and price outages, pending/confirmed payments, Reporter Lagos timestamps and Admin paging beyond 100. A separate actual service-worker lifecycle passed using only a fixed loopback synthetic server, closed before offline checks: shell/assets/public prices reopened, auth/history were excluded and logout cleared saved prices. These results supersede earlier pending browser/build notes; real device installation, provider permissions and full assistive-technology acceptance remain unverified.
