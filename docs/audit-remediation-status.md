# Audit remediation status: PY-01 through PY-36

October 2026 hardening branch. Implementation statements describe repository
behavior, not production state. Findings originally classified as potential risks
remain distinguishable from defects proven in source. No production access,
provider transaction or release was used for verification.

Evidence sources: synthetic backend/service tests, actual main-ASGI HTTP tests,
positively identified disposable PostgreSQL migration/concurrency tests, Node
regressions, isolated TypeScript/Vite build and synthetic browser workflows. The
root [progress record](../PRICEYARD_PROGRESS.md) owns the final combined counts.

| Finding | Repository response | Remaining qualification |
|---|---|---|
| PY-01 historical alternate-path bypass | Historical date/detail/list boundaries enforced; limited direct IDs require eligible current record; negative HTTP/field tests | Public previous-range summaries intentionally preserved; no live entitlement inspection |
| PY-02 premium intelligence exposure | Public/basic/full allowlists; quality/deeper intelligence guarded on list and detail | Consumer schemas continue excluding private sources |
| PY-03 unsafe Google linking | Subject/issuer/audience proof; email collision rejects automatic merge; explicit verified/password-confirmed linking | Legacy ownership remains unknown until proved; existing passwords/records retained |
| PY-04 reset leaves bearer sessions valid | Atomic reset claim, authentication version and revocable sessions; logout-all/reset/disable revoke credentials | Legacy JWTs require fresh login; deployment communication required |
| PY-05 fabricated referral rewards | Verified first successful purchase, unique qualification ledger, seven-day reward and prospective four-award cap | Prior earned access retained; campaign effectiveness not established by synthetic tests |
| PY-06 potential push SSRF | Supported HTTPS destinations, validated keys, public DNS check/address pinning, TLS validation and redirects disabled; synthetic hostile inputs | Original exploitability was not demonstrated; hosting egress/provider compatibility remains operational verification |
| PY-07 stored sessions/shared devices | Access tokens in memory; remember choice; revocation and push/logout cleanup attempts | **Partial:** refresh credentials remain JavaScript-readable; no HttpOnly cookie migration or MFA; offline revocation cannot be confirmed |
| PY-08 abuse/input bounds | Early body limit, bounded text/image processing, authentication/write/default quotas and device bounds; HTTP 413/429 tests | **Operational remainder:** default memory limiter is per-process; Redis/shared-store dependency and failure policy require target-host verification |
| PY-09 potential security races | Conditional reset claims, ordered locks and PostgreSQL last-admin serialization | PostgreSQL concurrent reset single-use/session revocation and last-active-admin protection passed; this does not imply every possible race is covered |
| PY-10 potential spreadsheet formulas | Textual CSV cells neutralized; monetary Decimal values retained | Tests verify generated values; no live spreadsheet exploit was attempted |
| PY-11 stale created admin price row | Authoritative server reconciliation, published correction reason, withdrawal retention | Node/browser evidence is limited to covered interactions; manual source changes remain confidential |
| PY-12 incompatible price/cost series | Recorded market/unit/bag/variant/grade separation; independent persisted cost measurement; legacy ambiguity explicit | No guessed historic conversion, grade, average or bag size; owner review needed for genuinely ambiguous old records |
| PY-13 timestamp/date inconsistency | Aware new UTC timestamps; Lagos forms/search boundaries; five-minute future tolerance | Existing ambiguous timestamps are preserved, not bulk-shifted |
| PY-14 unreconciled movement/confidence | Comparable predecessor provenance and derived direction; null observed average means unknown; distinct source evidence required; freshness separate | Confidence labels still require editorial truthfulness; no automatic physical/laboratory attestation or price prediction |
| PY-15 hidden prices after recovery | Successful refresh clears resolved errors and retains recoverable UI states | No claim that real networks/providers never fail |
| PY-16 stale filters/response ordering | Stable IDs/master references, URL synchronization, obsolete-request protection and bounded page state | Additional data/viewport combinations remain acceptance coverage, not invented proof |
| PY-17 false empty intelligence | Commodity resolved independently from latest price; scoped sections handle partial failure | Production data completeness is not inferred from source behavior |
| PY-18 misleading auth/access/payment UI | Transient failures separated from invalid sessions; entitlement timing and backend payment status refresh; profile-loading lifecycle corrected | Offline server revocation warning remains necessary; browser state is not backend authorization |
| PY-19 hidden FAQ management | Authorized all-status list and hidden/edit/publish workflow | Actual ASGI roundtrip passed; public drafts remain hidden |
| PY-20 accumulating data/query costs | SQL-window latest selection; bounded history/admin/users/subscriptions/flag lists; flag names/counts in one joined query; all-row expiry uses SQL | **Performance remainder:** CSV materialization is bounded at 10,000 observations with explicit rejection above the limit; production plans/load/connection budgets not measured |
| PY-21 blocking/channel-dependent alerts | Approval/proof/reminder enqueue, independent channel retries, paired-watch AND matching, worker leases/CAS and stale eligibility checks | Worker scheduling/monitoring required; at-least-once provider delivery can duplicate after a crash |
| PY-22 overlapping frontend datasets | Lazy admin routes, aggregate dashboard metrics, scoped intelligence, anonymous read coalescing, cancellation/timeouts | Real mobile data/latency and production bundle/network measurements remain separate acceptance |
| PY-23 potential mobile overflow | Viewport-bounded navigation and admin layout; synthetic browser checks at narrow/tablet viewports | No universal claim for all devices, 200% zoom or every landscape combination |
| PY-24 keyboard/modal gaps | Focus management/restoration, Escape and keyboard controls/labels; focused synthetic browser coverage | Full screen-reader/assistive-technology audit remains outstanding |
| PY-25 untrustworthy offline cache | Validated shell, explicit anonymous-current allowlist/header, retention/entry bounds and visible stale age; Node worker regressions | Actual synthetic Chromium worker/offline shell/assets/public-price/auth-history-exclusion/logout lifecycle passed; real device installation and push permission remain acceptance |
| PY-26 non-atomic/incomplete audit | HTTP unit-of-work commits business change and sanitized audit together; generic administrative coverage; injected audit/commit rollback tests | Checkout pending intent deliberately persists before external initialization; no grant is committed at that step |
| PY-27 inconsistent PATCH/password inputs | Required nulls reject, optional commentary/observed averages clear, Unicode byte limits consistent, cost totals stay controlled | Legacy optional measurement remains unresolved rather than silently filled |
| PY-28 history/migration preservation | Preserve active-only consumer policy; retained admin evidence; additive migration/preflight and downgrade refusal | Historic 0006/0020 behavior cannot be undone by guessing; no production migration executed |
| PY-29 identity/dependent invariants | Stable ID filters, normalized unique indexes and conflict handling, linked-scope mutation rejection | Existing duplicates abort migration and require reviewed resolution; no auto-merge |
| PY-30 test gaps | Guarded synthetic service/API/HTTP/PostgreSQL/Node/build/browser suites added | Synthetic coverage is not exhaustive and does not validate production/provider state |
| PY-31 payment success without access | Validated atomic activation, unique application evidence, retry/reconciliation and durable checkout intent | Ambiguous prior successful records require signed evidence and explicit reviewed resolution |
| PY-32 renewal loses time | Accumulate purchased duration after valid unused paid/trial cutoff; preserve manual grants | Existing past lost time is not fabricated/compensated without evidence |
| PY-33 transaction mismatches | Amount/currency/customer/environment/state/reference/provider ID checks and signed reconciliation | No live Paystack transaction, refund or dispute was performed; automated refund policy not introduced |
| PY-34 expiry/Reporter coupling | All applicable expiry transitions processed; commercial access independent of staff role; bounded lists and preserved grants | Intentional administrator role edits remain distinct from automatic subscription expiry |
| PY-35 operational assurance | Dependency records, guarded migrations, readiness check and measured synthetic query/build checks | **Partial:** target-host dependency/security review, TLS/headers/privileges, monitoring, shared limiter, backup restore and production capacity remain operational acceptance |
| PY-36 stale documentation/conventions | Updated current README/API/access/deployment/testing contracts; historical evidence retained and labelled | **Partial maintainability remainder:** compressed legacy admin components still need incremental formatting/refactoring; no rewrite claimed |

## Measurements that are actually established

- The price fixture with 500 observations in one series returns one current record
  using three SELECTs (current result plus two reference loads).
- Flag summary aggregates names/counts in one query rather than per-record reads.
- Entitlement is checked once for a current-price list, not once per row.
- A one-record subscription page still processes all expired synthetic accounts;
  valid paid/manual access and Reporter authority remain unchanged.
- PostgreSQL tests exercise fresh and populated migrations, preservation/preflight,
  payment/price races and independent notification worker claims/stale leases.

These are correctness/query-bound checks, not a commercial user-capacity guarantee.

## Release boundary

No push, merge, deployment, production preflight/migration, live provider test or
production data repair has occurred under this local work. The accepted 14-day
trial, NGN 2,500/30 days, NGN 6,000/90 days, manual grants and original business
records remain protected. Readiness must retain the explicit remaining limits
above; do not convert "implemented" into "production-certified."
