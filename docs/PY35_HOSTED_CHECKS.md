# PY-35 hosted verification — 2026-10-20 WAT

35/36 recommendations remain complete; PY-35 is partial. Resume point verified:
`af8aa77b99bc1be4925f436f8becb3105a0eb989`, clean working tree on
`codex/priceyard-original-preserved-20261016`. Verified recovery commit8c7ea61 is
an ancestor. Completed backup, retrieval, restoration, migration and regression
tests were not repeated.

## Checks completed now

At2026-10-20T12:30:16Z, two bounded standard-library TLS handshakes passed:

| Existing hostname | Certificate chain/hostname | Protocol | Certificate expiry |
| --- | --- | --- | --- |
| priceyard.onrender.com | Passed | TLS1.3 | 2026-12-20T23:04:28Z |
| priceyard-api.onrender.com | Passed | TLS1.3 | 2026-12-20T23:04:28Z |

No HTTP requests, sign-ins, account records, provider transactions or database
connections were made. These handshakes do not prove application routing,
certificate renewal, cookie/session behavior or the unreleased candidate.

Static rollback artifact comparison: current backend/app and candidate2cfbfa6
both have treefcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed. Their only backend/frontend
source difference is the reviewed0022 migration privacy safeguard. This confirms
application source identity, not hosted startup/dependency/session compatibility.
Any eventual rollback must retain the current reviewed database security grants
and revocation evidence; do not execute the older migration or destructive
downgrade. Existing focused authentication regression evidence is retained.

## Still blocked or not attempted

- No separate approved hosted candidate URL/operator or test-service configuration
  is recorded. The two known services serve production. Do not use real customer
  accounts or replace production for testing.
- Google: exact test origin/client and consenting test identities, then popup,
  session persistence, logout/reset and supported-browser checks.
- Paystack: TEST-only credentials and approved callback/webhook destination,
  then test checkout, signed delivery/replay and missed-event recovery. Never use
  live keys, real charges or change existing production webhook settings.
- Delivery: approved test sender/credentials and recipient allowlist, then actual
  reset/notification receipt. Simulated delivery is not provider evidence.
- Operations: approved non-production monitoring/alert recipient and scheduler,
  bounded runtime/clock checks, pinned artifact/dependencies and hosted rollback
  with security evidence retained. No jobs or alerts enabled here.
- Release: non-database file/configuration recovery, owner recovery targets,
  current target permissions/revision and post-snapshot payment/write reconciliation
  remain separately controlled requirements. Existing local migration rehearsal
  passed; no repeat is needed merely for a report.

These checks are blocked/not attempted, not failed application tests. No new
cloud resource, purchase, push, merge, migration or deployment was performed.

Next owner step: open Render Dashboard and check whether an existing separate
non-production test service is available. Provide only its service name/URL, or
say none. Do not create services, change settings or share environment values.
If none exists, candidate hosting requires a separately approved staging
deployment; the current no-deploy instruction prevents that step.
