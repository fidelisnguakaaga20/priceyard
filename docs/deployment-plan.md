# PriceYard deployment and recovery runbook

This is a proposed operator runbook for the October 2026 hardening branch.
**No push, merge, production migration or deployment is authorized by this file.**
Development changes and local synthetic evidence do not establish deployed state.

## Preserved hosting history

The earlier controlled pilot selected a Render static frontend, Render backend and
Supabase PostgreSQL, with exact frontend CORS origins and HTTPS. Free hosting was
accepted for the pilot, not established as a commercial availability guarantee.
Those historical choices are not a new hosting purchase or a claim about current
production settings.

## Before a separately approved release

1. Review the final source diff, prepared revisions 0022–0025, actual test results
   and remaining audit limitations. Preserve the current release artifact.
2. Obtain an authorized backup and prove restoration into an isolated destination.
   Never test restoration by overwriting production or copying customer records
   into the synthetic development lab.
3. Have an authorized operator assess schema/data preconditions without logging
   credentials or private sources. Do not automatically resolve duplicates,
   invalid previous ranges or ambiguous historic payments.
4. Review the target platform's dependency resolution. The checked-in Python lock
   describes Windows/Python 3.14 tests; Linux production needs compatible reviewed
   resolution. Frontend package-lock is retained.
5. Configure exact CORS origins, HTTPS, JWT/provider settings and protected scheduler
   credentials through operator-managed secret storage. Do not commit or print them.
6. Plan a compatible frontend/backend release: old JWTs without session identity
   require login again, old clients must refresh new credentials, and published
   corrections now require a reason. Paid time and existing passwords stay intact.
7. Provide a supervised migration/release window and an approved recovery plan.
   Actual release commands must be chosen for the authorized target environment;
   no generic command here may select a configured production URL implicitly.

## Migration behavior

| Revision | Important behavior |
|---|---|
| 0022 | Adds sessions and verification proof; legacy email ownership remains unknown |
| 0023 | Preserves complete UTC legacy end dates and manual grants; flags old successful payments for review instead of guessing access |
| 0024 | Adds restricted revisions, grade/predecessor/cost provenance and indexes; archives retain records; duplicate/previous-range preflight aborts before its DDL |
| 0025 | Adds leased notification outbox and target measurement; legacy targets stay preserved but paused until explicitly confirmed |

New price/cost metadata is nullable for historical records. No migration invents
historic grade, quantity, average, timestamp correction or payment application.
Consumer active-only history and no-outdated-fallback remain unchanged.

Revisions 0023–0025 refuse destructive automatic downgrade. An old application
version must first be assessed for compatibility with retained fields/statuses and
security boundaries. Prefer reviewed forward repair; restoring a prior backup can
lose intervening transactions and requires an explicit reconciliation plan. Never
drop revisions, grants, outbox work or paid cutoffs merely to make old code start.

## Notifications and identity recovery

A separate bounded worker is required for queued email, push and WhatsApp delivery:

```text
python -m app.notification_worker --limit 50
```

This is an **operational sending command**, run from backend only in an explicitly
approved configured environment. It is not a safe test command. It is not installed
or scheduled automatically by the repository.

Run frequently enough for 15-minute password recovery links to remain useful.
Monitor oldest pending age, retry/failed counts, provider failures and proof expiry.
Trial-reminder producers enqueue at most 200 eligible accounts per request;
`sent` and the legacy reminder timestamp mean accepted/enqueued, not provider
delivery confirmation.

Jobs use five-minute leases, independent channel retries and a default five-attempt
cap. Expired leases can recover; stale workers cannot acknowledge a replacement
lease. Logical enqueue is deduplicated, but provider delivery is at least once.
Do not promise exactly-once messages after worker crashes.

Proof-email contents are encrypted in the temporary outbox using the application's
secret derivation. Preserve required key material while pending proof jobs exist,
or use reviewed expiry/reissue recovery. Do not log decrypted proof links.

The application restricts push destinations and pins verified public addresses.
Hosting egress policy remains an additional operator control; allow only required
provider destinations. Never test real transactions/messages during development.

## Authentication and entitlements

Users may need one fresh login after the session-security rollout. Do not reset valid
passwords or purchases to accomplish this. Communicate verification/recovery paths.
Google email collisions require explicit ownership recovery/linking.

Access JWTs default to 15 minutes; sessions remain revocable. Refresh credentials
are still JavaScript-readable. HttpOnly cookie sessions and administrator MFA are
not part of this release and must not be advertised as implemented.

Preserve prices (NGN 2,500/30 days, NGN 6,000/90 days), 14-day registration-started
trial and manual grants. No recurring charges are introduced. Historical payment
reconciliation requires trustworthy signed evidence and a reason; uncertain
already-paid customers require reviewed resolution rather than automatic replay.

## Monitoring and scaling gates

- `GET /health` is process liveness. `GET /ready` checks required secret validity,
  database connectivity and the expected schema revision; failures return a generic
  503. It does not prove payment, email, push, backup or overall provider readiness.
- Monitor HTTP errors, latency, database pool pressure, payment confirmation versus
  entitlement application, reconciliation queues and notification backlog.
- Default rate limiting uses process-local `memory://`. Before multiple workers,
  configure a reviewed shared store using RATE_LIMIT_STORAGE_URI, its Redis client
  dependency and failure behavior. Shared-store hosting is not verified locally.
- Each backend process has its own database pool. Size worker/pool totals against
  actual database connection limits and measured workloads.
- Agree on availability, recovery and performance targets from a measured baseline.
  A 500-row synthetic query check is not a user-capacity guarantee.
- Verify proxy/security headers, TLS, exact CORS and least-privilege database access.
  None was inspected in production during development.

## Local acceptance versus release acceptance

Use [P00 guarded commands](../audit-prep/p00/README.md) for synthetic tests.
Production-provider compatibility, actual migration preflight, restoration, mobile
installation, assistive-technology coverage and target-host load need their own
authorized acceptance. Retain known limitations in the release report.
