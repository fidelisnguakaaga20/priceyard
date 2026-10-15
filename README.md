# PriceYard

PriceYard provides Nigerian agricultural commodity price observations, history,
market intelligence, reporting and subscription access. It uses React/TypeScript,
FastAPI, SQLAlchemy/PostgreSQL, Paystack and optional email/push/WhatsApp providers.

This branch contains the October 2026 hardening work. Repository changes and local
test results do not imply that the deployed application has changed. Production
data, provider transactions, publishing and deployment remain outside the local
verification process.

## Business rules

- A 14-day trial starts at registration.
- Monthly access costs NGN 2,500 for 30 days.
- Seasonal access costs NGN 6,000 for 90 days; it is a rolling period, not a named
  planting/harvest season. Neither plan automatically charges again.
- Renewals preserve unused purchased time and the valid remaining trial.
- Existing inclusive paid end dates and manual grants are preserved.
- Public current summaries retain ranges, previous ranges, movement, measurement,
  confidence and observation time. Full history and deeper intelligence require
  a valid trial, paid access or administrator authority.
- Reporter/Admin authority is separate from subscription expiry.
- Different markets, recorded units, bag sizes, variants and grades remain
  separate. Unknown measurements/averages are never invented.
- Consumer history remains active-reference-only. An outdated latest observation
  does not cause an older price to reappear as current.
- Published price corrections preserve originals and require a reason. Withdrawal
  retains the price and dependent evidence.

## Components

| Location | Purpose |
|---|---|
| [backend](backend/README.md) | Authentication, entitlements, prices, administration and provider integration |
| [frontend](frontend/README.md) | Public/member/Reporter pages and administrator tools |
| [API contracts](docs/api-endpoints.md) | Implemented routes, payload rules and compatibility notes |
| [Access matrix](docs/access-control-matrix.md) | Authoritative backend access and field boundaries |
| [Deployment runbook](docs/deployment-plan.md) | Proposed release, worker and recovery requirements |
| [Isolated verification](audit-prep/p00/README.md) | Synthetic-only tests and transport/configuration guards |
| [Audit status](docs/audit-remediation-status.md) | PY-01 through PY-36 implementation and remaining limits |
| [Progress](PRICEYARD_PROGRESS.md) | Current work and verification record |

## Safe verification

Use the prepared isolated runtime from the repository root. The runners disable
dotenv before application imports and use synthetic configuration/data. Do not
run historical owner smoke scripts against configured developer or live services.

```powershell
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_backend_tests.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\verify_migrations.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\prepare_frontend.py'
& '.\audit-prep\p00\runtime\venv\Scripts\python.exe' -I -B '.\audit-prep\p00\run_browser_checks.py'
```

The PostgreSQL command requires the separately provisioned disposable cluster and
its positive identity marker. Frontend commands require the declared local tools
and a successful secret-free snapshot build. Missing prerequisites cause failure;
the scripts do not fall back to a configured production database or site.

## Security and operational limits

Access tokens are short-lived and server sessions are revocable. Password reset
revokes previous sessions. Google identities are never merged by email matching
alone. **Refresh credentials remain JavaScript-readable browser storage; HttpOnly
cookie sessions and administrator MFA are not implemented.**

Notification producers queue delivery; a separately scheduled worker must process
the outbox. Logical enqueue is deduplicated, but provider delivery is at least once.
The default rate limiter is process-local; scaling to multiple workers requires a
reviewed shared store such as Redis and its deployment dependency.

Local tests do not certify deployed availability, capacity, database privileges,
backup restoration or every mobile/browser interaction. Historic stage reports
under `docs/evidence` are retained evidence, not current release acceptance.
