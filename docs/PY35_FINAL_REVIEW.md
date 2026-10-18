# PriceYard final review - batch 87

**35/36 complete; PY-35 partial. Deployment is blocked.** All executed checks
below pass; the nine real-world release gates remain **not run**, not failed.
No production services, credentials, customer data, migrations, provider sends,
push, merge or deployment were used. Conditional deployment approval does not
substitute for the required evidence.

## Recovered state and confirmed fix

Started from actual `5bce117438aae2c77fc735ffb787fb3dc5dd17f8` on
`codex/priceyard-original-preserved-20261016`. The interrupted service fix and
untracked expiry test were preserved byte-for-byte under ignored
`tools/local-test/runtime/batch-87-interrupted-work/` before further work.
No changes were discarded. Original master `76dbd27588de4aa37f3163d8b263d4b72a2cff32`
and backup branch `258991019e5af8b36eff407a8efa2c9fd03dd644` stay intact.

**Confirmed defect:** an account read could load expired access, then overwrite
the active status/ordinary paid role after payment committed a renewal. Payment
evidence and dates could remain while access was incorrectly expired. The old
committed function reproduces six failing scenarios in memory without reverting
the source. The fix reloads due access under the existing User-then-Subscription
locks before expiring anything, and commits/releases or rolls back consistently.
Valid access takes no new expiry locks. No schema, UI or business-rule change.

Preserved:14-day trial; NGN2,500/30 days; NGN6,000/90 days; remaining paid/trial
value; indefinite-grant review; referral cap; staff roles; UTC paid expiry;
original design/measurements, historical records and all14 Admin cards.

## Independently executed regression evidence

| Check | Result |
| --- | --- |
| Defect reproduction against old committed helper | Six expected failing subcases; working fix restored after memory patch |
| Focused expiry unit tests |6 passed,0.249s; real expiry, renewed stale reads, staff/history preservation, rollback and missing row |
| Full isolated backend discovery |307 passed, zero failures/errors/skips,117.546s; includes authentication, payments, subscriptions and notification regressions |
| Native PostgreSQL |5 passed,9.689s; twelve GET/payment interleavings across trial/paid and ordinary/Reporter/Admin, real blocking observed; listing expiry, verify/webhook replay and distinct concurrent purchases |
| Browser purchased value | Paid renewal and trial purchase retain remaining time; replay adds no second credit; original dashboard |
| Browser indefinite grant | Checkout blocked; confirmed receipt held once; original Admin control resolves synthetic grant; purchase credits once |
| Browser access | Eight role/status scenarios preserve current/detail/history boundaries |
| Browser Admin | All14 original labels and exact totals; one summary request; outage/reload recovery |

Evidence:`tools/local-test/evidence/batch-87-*.json`. Native database is stopped,
26/80 retained schemas, max12 connections/32MB buffers, fsync enabled. Heavy
phases were sequential; one browser at a time. Browser requests stayed loopback;
backend sockets/DNS were denied. No new frontend build was needed because frontend
source is unchanged; the local release checker verifies source/build identity.

Retained setup failures:PowerShell redirected a known Starlette/httpx deprecation
warning as a terminating native-command error before discovery; corrected log
launch then completed307 tests. First browser launch lacked the path to the
already-installed isolated browser; setting that path succeeded without downloads.
Two old browser harnesses still supplied `Bearer null`; updated them to the
already-approved protected cookie/CSRF session. No application workaround or
security restriction bypass. No unresolved executed application test failure.

## Authentication, payment and database review

Reviewed current security/session, Google ownership/reset, payment evidence and
locking, subscription and migration-safety paths against the retained final
readiness requirements. No separate newer audit report was recoverable from the
other conversation; no claim that unseen findings were reviewed. The confirmed
new critical finding above is fixed.307 backend tests provide fresh regression
evidence, not a guarantee against every undiscovered defect.

JWT revocation/version, protected cookie/CSRF and stable Google subject boundaries
remain; browser-host routing and real Google consent are still unverified.
Provider evidence and purchased time are protected locally; actual Paystack TEST
checkout/webhook/recovery remains blocked. Production revision/pooler/permissions
are unknown. The reviewed additive0021-to0022 path preserves synthetic records;
unknown populated schemas stop. Revocation evidence cannot safely be removed by
downgrading. An application rollback must preserve compatible schema/evidence.

Historical hosting notes record separate Render static/backend services, backend
Python3.12.8 and Supabase PostgreSQL; these are historical, not inspected current
settings. Actual same-site API routing, cookie/CORS/proxy headers, clean target
runtime installation and current dependency advisory review remain release gates.
Synthetic backup restoration83 is retained evidence, not proof of a customer
backup. Actual encrypted backup retrieval/restoration and agreed retention,
acceptable data-loss window and recovery time must pass before rollout.

## Exact missing access and safe provision

No Render/Supabase authenticated tooling or approved targets are established in
this session. A GitHub connector is available; this repository's permissions and
remote candidate publication are unverified. No remote fetch/push was performed.

| Area | Missing information/access | How the owner can provide it securely |
| --- | --- | --- |
| Render | Workspace, exact frontend/backend service IDs/domains, linked branch, current runtime/build/start/proxy settings; authorized isolated hosted test target/operator | Log into Render yourself; share service names/IDs and redacted settings, or grant a supported least-privilege operator connection. Confirm auto-deploy cannot publish this branch. Do not alter live settings yet |
| Supabase | Exact project reference, approved read-only revision/schema/permission/pooler preflight and operator; current compatibility unknown | Share project reference and approve a bounded metadata-only review separately. Keep any dedicated read-only connection in approved secret storage accessible only to the approved tool/operator; never paste its URL/password here |
| GitHub | Access to the historically recorded repository `fidelisnguakaaga20/priceyard`; candidate branch is local and repository permissions/current remote state are unverified | Confirm the repository name; authorize the existing GitHub connection for only that repository if necessary. Publishing the reviewed branch requires separate approval; do not enable production auto-deploy |
| Actual backup/rollback | Approved backup source, encrypted off-host destination/retrieval access, isolated restore target, operator, retention and recovery objectives; compatible rollback artifact | Choose the targets/operator and approve actual-backup handling separately. Use host secret storage and private encrypted files; share only storage references and redacted verification results, never a customer dump in chat |
| Provider verification | Paystack TEST credentials and reachable nonproduction callback/webhook; Google test origin/client/accounts; test message sender and consenting recipients | Enter test-only configuration into approved protected storage yourself/operator; share only secure storage references, URLs and approved recipient identities. Never share account passwords, live keys or real cards |

The existing GitHub connector has not been tested for repository access. No claim
of a missing login or denied permission is made without a failed access check.
Sharing an access reference does not authorize production writes or deployment.

## All nine gates still open

1. Public HTTPS, reverse-proxy cookies/session/Google return and target browsers.
2. Actual encrypted off-host backup retrieval and isolated restoration.
3. Read-only production schema compatibility, then separately reviewed rollout
   and rollback; no migration until backup acceptance.
4. Actual Paystack TEST success/failure/replay/missed-event recovery and value.
5. Approved scheduler/checkpoint/restart/alert operation on the chosen host.
6. Google test login and approved email/push/WhatsApp delivery.
7. Host monitoring, clock/pool/resource limits and bounded representative load.
8. Clean target-host dependency installation/advisory review and configuration.
9. Approved historical exceptions/public text review and final cutover decision.

See [OPERATIONAL_READINESS.md](OPERATIONAL_READINESS.md),
[RELEASE_GATES.json](RELEASE_GATES.json) and
[STAGING_SETUP_GUIDE.md](STAGING_SETUP_GUIDE.md). Additional services or spending
are not authorized or assumed. Stop before deployment until these blockers close.
