# PriceYard monitoring and incident checks

This defines the operational signals and local drill. No live agent, external
monitor, scheduler, alert recipient, provider or paid service is enabled.

| Signal | Meaning/check | Response and acceptance |
| --- | --- | --- |
| API /health | Process liveness only; it deliberately does not query the database | Healthy liveness cannot clear a price/database outage. Monitor an actual approved read separately |
| Current-price read | HTTP status, parseable public schema, record count and displayed failure/recovery | Distinguish a failed request from an empty valid market. Never invent replacement prices or treat a saved copy as live |
| Account/history read | Authorized synthetic monitor account on an approved host | Check real entitlement and privacy; do not use an Admin/customer password in public uptime URLs |
| Payment backlog | Pending/failed age, confirmations, review holds, reconciliation outcomes/checkpoints and worker busy/errors | Preserve evidence/value; no blind replay/refund. Operator follows PAYMENT_RECONCILIATION.md; manual-grant holds are expected review outcomes |
| Audit/write failure | Generic error count/action/record ID and transaction outcome | A failed business/audit save must not be reported as success. Alert after durable save cannot undo it |
| Notifications | Per-channel send failures and provider delivery reports | One channel failing must not suppress others. Local mocks do not prove receipt or scheduled retry |
| Price freshness | Latest recorded instant per commodity/market/specification, in WAT for operator display | Report age. Publication/freshness thresholds need the owner's policy; monitoring must not silently relabel history |
| Database/resources | Pool timeouts, connection count, disk, memory, latency, worker overlap, clock offset | Bound workers and investigate before adding retries. Confirm UTC instants/WAT display and stable clocks |
| Backups | Last successful backup and most recent tested restoration, protected checksum/retrieval/access | A successful upload is not a proven restoration. Missed RPO/RTO blocks acceptance |
| Browser/release | JS/API failures, cookie/CSRF rejection rate, redirects, offline-copy age, Android/browser compatibility | Verify original flows and14 cards. Diagnose cookie/host/clock configuration; never weaken origin/CSRF or cookie protection |

Suggested initial alert policy for owner/operator review: check liveness and a
small safe read once a minute, alert after three consecutive failures, and record
recovery. This is a proposal, not an enabled job or an approved service-level
promise. Owner chooses recipients, service costs, retention and response coverage.
Define separate payment-backlog/price-freshness/clock limits after reviewing real
business cadence; do not assume every commodity should be updated hourly/daily.

Local drill must prove that a simulated price503 is detected while /health stays
200; the original page shows its existing error and recovers after the fake outage
is removed. Also verify guest history denial, private source omission, no external
requests and original dashboard monitoring evidence. Existing payment, timeout,
replay, failed-save and notification tests remain evidence; do not rerun entire
suites solely to refresh report dates.

Logs/alerts should contain timestamps, outcome codes and bounded record IDs.
Exclude passwords, bearer/session/reset tokens, cookies, CSRF values, complete
provider bodies, private source contacts, screenshots and raw database URLs.
Use approved access controls and retention; do not send messages from this task.

Incident sequence: acknowledge and scope; preserve evidence; stop the offending
rollout/worker through an approved operator; verify customer access and payment
value; recover using the reviewed runbook; confirm all affected workflows and
monitor sustained recovery. Record root cause and evidence before resuming jobs.
Host-specific dashboards, TLS/cert expiry, alert delivery, distributed throttling,
real provider failures and on-call response remain owner-approved live checks.
