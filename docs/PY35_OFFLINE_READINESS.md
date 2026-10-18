# PY-35 offline readiness — 2026-10-18

**35/36 complete; PY-35 partial.** Owner chose existing local isolation, without
new Render services/Supabase projects. Batch86 closes the identified remaining
local TLS/browser and email-transport gaps. No application source, design, data,
policy, cloud configuration or external service changed. All original live gates
remain unrun. This is not a production-release certificate.

## Verified locally

New86 evidence (small sequential runs, no repeat of already-passing suites):

- Real TLS1.3 loopback browser request, original login/reload/logout, Secure
  `__Host-`/HttpOnly/SameSite cookies, session-only Remember me behaviour, no
  JavaScript bearer storage, private no-store response, CSRF rejection and revoked
  credential rejection. Disposable Chromium trusts only the generated test SPKI.
  No broad HTTPS-error switch or operating-system trust-store change.
- Three socket-free TLS checks:trusting the generated certificate/matching IP
  succeeds; wrong hostname and untrusted certificate fail certificate validation.
- Six new simulated email checks:missing sender/transport cannot send; provider
  HTTP/network/rejection responses fail safely; SMTP STARTTLS precedes login/send;
  TLS failure sends neither credentials nor mail; SMTPS checks certificates.
  Existing email success and independent-channel coverage is reused.

TLS bootstrapping creates/loads only its own new synthetic key/certificate in a
fixed ignored runtime folder before application imports. Existing isolation guard
then applies unchanged. App sockets/DNS/providers/secrets stay denied; listener is
literal127.0.0.1:55446, requests require HTTPS/exact Host/Origin, only one browser
runs. Server is stopped afterward and the ordinary fresh HTTP preview restored.
One small certificate pair retained; no repeated trees, databases or native suites.

Reused saved evidence:

| Scope | Evidence |
| --- | --- |
| Accounts/roles/private sources/price accuracy/payment value and recovery | Full286 backend baseline81, focused later batches; simulated Paystack/Google verification, replay/mismatch/missed-event/concurrency safeguards |
| Original UI/mobile/keyboard/offline,14 Admin cards | Prior browser evidence; latest notification and14-card checks85 |
| Notification application URLs |9 URL/delivery,5 channel and4 price-audit tests85; known live-host rejection outside production |
| Database integrity and synthetic restore | Focused PostgreSQL cases; actual21-table/14-row synthetic dump/restore83, read-only recheck84 |
| Scheduling/monitoring/performance | Three finite checkpoint ticks and native worker/replay tests84; outage/read recovery and24 serial read samples84 |
| Dependency/release safeguards | Reviewed frontend lock/build82;60 Python packages/74 active requirements without conflicts84; preserved original Git references and explicit release refusal |

These are different scoped runs, not a newly executed full combined suite.
Evidence: `tools/local-test/evidence/batch-86-*.json` and the linked prior batches.
No unresolved failure in the executed checks. Missing real prerequisites are
**Blocked/not attempted**, not failed tests. Historical corrected failures remain.

## Precisely what local simulation cannot establish

| Gate | What still needs external/real evidence, and why |
| --- | --- |
| Hosting/cookies/browsers | Public certificate chain/renewal, DNS, actual Render `/api` routing and forwarded cookie/origin headers; different hosts may behave differently. Current local Chromium/mobile emulation cannot certify real Android/Safari/device settings. Local TLS success closes only the loopback subcheck |
| Actual backup/restoration | Real backup contents, provider auth/storage/RLS/grants/files, encrypted off-host retrieval/retention and measured agreed recovery objectives. Synthetic records cannot prove customer-backup completeness; real-data access remains unauthorized |
| Production schema/rollout | Actual installed revision, permissions/pooler behaviour, migration compatibility and rollback. The production database has not been inspected; guessed schemas are not evidence |
| Paystack | Real TEST checkout, provider IDs/signatures, actual callback/webhook reachability, failures and value/recovery flows. Fabricated responses cannot demonstrate Paystack integration; test credentials and an approved reachable callback endpoint are missing |
| Recovery scheduling | Real process restarts, durable checkpoint location, cron permissions/timing and alert ownership. A finite local rehearsal cannot certify a scheduler that has not been chosen/enabled; no OS/cloud job created |
| Google/email/push/WhatsApp | Real client-origin/consent configuration, Google popup/certificate lookup and message acceptance/delivery to approved recipients. Local mocks do not contact those systems; approved test setup/credentials/recipients remain missing |
| Monitoring/load/clock | Host database-readiness probes, alert receipt, real pool/memory/disk/latency, distributed rate limits and clock alignment.24 tiny local serial reads are not production capacity evidence; heavy load/virtualization was deliberately not started |
| Hosted dependencies | Exact clean target-host installation, runtime compatibility and fresh direct/transitive advisory/provenance review. Available Windows packages/lockfiles do not prove Linux resolution or current online advisory status; no installs/downloads/scans this batch |
| Historical review/cutover | Existing public text, legacy account/reward/payment exceptions and final traffic switching. Those facts exist only in real records/configuration; neither accessible nor authorized in local simulation |

## Minimum additional preparation before a safe launch

1. Approve a precise release commit and an operator. Confirm actual hosting
   HTTPS/same-site cookie routing and target phones/browsers against that candidate.
   Existing hosting may be used only through a separately approved isolated test
   arrangement; no new cloud project is required for more local work, but offline
   success does not substitute for a hosted acceptance test.
2. Supply dedicated provider TEST configuration and consenting recipients through
   protected storage. Approve a reachable nonproduction callback/webhook endpoint
   and restricted recipient/provider transport. No customer keys/cards/accounts.
3. Separately approve read-only production revision/compatibility review and an
   actual encrypted backup restoration into an isolated target. Choose maximum
   acceptable lost-data window/recovery time and retention. Only then review any
   necessary migration, historical exceptions and safe rollback/cutover.
4. Resolve/review dependencies on the target runtime, agree monitoring/alert
   ownership and scheduler/checkpoint operation, and approve final deployment
   separately. No job is enabled and no production request is made here.

Do not use the preserved historical84 staging package as the current release:
it predates85 URL fix. Full setup detail: [STAGING_SETUP_GUIDE.md](STAGING_SETUP_GUIDE.md).
No production access, customer data, real messages/charges, purchase, cloud project,
push, merge or deployment. Stop after reporting.
