# PY-35 operational readiness — local evidence and release gates

Current checklist:35 of36 complete. PY-35 remains partial until the owner-approved
live gates below pass. A local check returning success never authorizes release.
Phase 1 staging verification was authorized subsequently on2026-10-18. See
[Phase 1 results](PY35_PHASE1_REPORT.md):separate local package and synthetic checks
pass; hosted/provider checks are blocked by missing staging/credentials. Original
live gate statuses remain unrun; no production authorization is implied.
No production configuration, provider account, database or hosting service was
accessed. No migration, live job, push, merge or deployment was performed.

## Completed locally

| Work | Evidence and limits |
| --- | --- |
| Original app and critical workflows | Full286 backend tests and focused native history81; baseline, full251-row history,14 accurate Admin cards and original forms. Later dependency-only checks reuse unchanged backend evidence |
| Approved security dependencies | Vite6.4.4/router6.30.6, reviewed integrity-bearing lockfile, official-registry-only isolated install with lifecycle scripts disabled. Old tools retained. TypeScript/build, computed original styles, sessions/payment/CSV/Google/history/baseline/14 cards pass82. See DEPENDENCY_READINESS.md; not a complete CVE-free certificate |
| Synthetic backup/recovery | Native PostgreSQL18 pg_dump/pg_restore into one new marked empty local database.21 application tables/14 fabricated business rows; data digests, types/defaults/precision, indexes/sequences and constraint semantics match. Source unchanged. Failed raw-text comparison retained: PostgreSQL rewrote equivalent varchar-array casts; its planned expressions/validation flags match. No second restore was needed |
| Recovery isolation | Fixed literal55449, directory/system ID before mutation, no arbitrary database/URL input, marked new target, no clean/drop/overwrite, single transaction/worker,2MiB archive budget, source and failed evidence retained. Four negative guard tests; no native connection in those unit tests |
| Monitoring | Local price outage versus healthy process-liveness, original error/Apply/recovery, privacy and guest boundary drill. No real monitor, recipient or alert enabled. See MONITORING.md |
| Release gate | Source/build/lock hashes, exact test dependency inventory, preserved Git references, evidence and explicit unrun live gates checked by check_local_release.py. Missing/failed evidence and accidental release-authorized flags fail the check |
| Backup/incident/release procedures | BACKUP_RECOVERY.md, MONITORING.md, PAYMENT_RECONCILIATION.md and MIGRATION_PRESERVATION.md preserve historical/payment/security evidence and require reviewed targets/operators |

The archive contains synthetic data only and stays ignored under runtime. The
first restore completed before the strict verification mismatch; its separate
dump/restore durations were not captured. The runner now records timing before
verification for future authorized rehearsals. No production RTO/RPO or actual
customer-backup restoration is inferred. Do not rerun solely to improve a report.

## Separate owner approval and real-world evidence required

| Gate | Concrete approval scope and acceptance |
| --- | --- |
| Hosting/cookies/browser matrix | Approved staging/production domains and operator; HTTPS/same-site proxy, exact credentialed CORS, secure cookies/CSRF, token migration and isolated profiles,90 days/RememberMe, Android/Chrome and other target browsers including Web Locks, logout/reset/Google return/deep links. Never enable an unsafe cookie fallback |
| Actual backup/restore | Approved real source/backup/isolated target, operator, encryption/storage/retention and RPO/RTO. Restore actual backup with egress disabled; include provider auth/storage/RLS/grants/roles/extensions/functions/files and all current payment/security/history evidence; verify retrieval and recovery duration |
| Production schema/rollout | Approved read-only revision/preflight first; reviewed additive migration only after backup/restore acceptance, compatibility and rollback review. Populated legacy/unknown schemas stop. Never downgrade revocation evidence or guess repairs |
| Paystack | Explicit provider test account/mode and bounded scenarios, followed only if approved by a controlled live test. Verify checkout/reference/amount/currency/provider ID, signature, missed callback/webhook recovery, replay/concurrency, carried paid/trial time and manual-grant review. No real customer charge/refund or automatic ambiguous historical correction |
| Recovery scheduler | Operator-approved schedule/checkpoint store/worker permissions and alert ownership. Confirm dry-run preview, exclusive worker, fixed ceiling/continuation checkpoint, bounded retries and error reporting. No job enabled during this work |
| Google/email/push/WhatsApp | Approved test identities/recipients, credentials in platform secret storage, domain/certificate restrictions and delivery evidence. Fabricated verification and mocked sends do not prove actual popup or receipt. No messages sent from this task |
| Monitoring/load/clock | Approved live probes, cost, alert recipients/retention/on-call coverage. Separate liveness from real reads, measure pool/memory/latency under bounded representative load, distributed rate limits, payment backlog and UTC clock alignment. Owner selects freshness/response/RPO/RTO targets; no invented cadence |
| Hosted dependency/environment | Fresh Linux/host install from reviewed frontend lock and exact backend dependency resolution, supported Python/Node/PostgreSQL, provider configuration supplied privately by operator, complete current direct/transitive advisory review and artifact provenance. Local Windows inventory is a reference, not a portable production lock |
| Historical review/cutover | Explicitly scoped review of old public notes, legacy session/reward evidence, unknown migration state and ambiguous payment/manual grants. Preserve records/earned time; decide any repairs individually with evidence. Approve final cutover/deployment separately |

## Operator release sequence — not executed here

1. Review the exact candidate Git commit, approved business contracts, lockfiles,
   evidence and remaining gate list. No automatic deployment on commit.
2. Owner approves named staging targets and external-provider test scope. Start
   with synthetic data and egress disabled; never point test tools at Supabase.
3. Verify host/browser/dependency/provider/monitoring checks and the actual approved
   backup restoration. Record failures without bypassing checks or rewriting data.
4. Obtain separate approval for any production preflight/migration and a controlled
   release window. Pin artifacts, confirm compatible rollback, preserve payment
   evidence, and verify trial/paid/staff access/14 Admin cards/private sources.
5. Owner explicitly approves deployment/cutover only after blockers are closed.
   Monitor recovery and reconciliation; stop on access/payment/privacy errors.

Machine-readable unrun gates:RELEASE_GATES.json. Current progress and approved
decisions:../PRICEYARD_PROGRESS.md. Never interpret historical deployment notes as
current permission to access hosting or deploy.
