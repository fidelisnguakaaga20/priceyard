# Local regression coverage and completion criteria

PY-30 fixes the absence of repeatable isolated regression testing. Its finite
local scope is complete when the requirements below have evidence. This does not
mean100% coverage, completion of the other checklist items, production/provider
certification or permission to run against customer data. Tests for subsequent
fixes remain mandatory within their respective items.

## Verified requirements

1. Automated backend service/API tests exercise the existing critical account,
   access, payment, data-preservation and notification workflows with synthetic
   data. Latest full suite:307 tests, zero failures/errors/skips in batch87.
2. PostgreSQL tests exercise material lock/transaction behavior rather than
   substituting SQLite for concurrency. Last full40-case native baseline is
   batch47. Later recovery/migration/export/catalog changes have focused native
   evidence; batch87 adds five native cases, including twelve single-account
   expiry/payment interleavings. No newly executed full native suite is claimed.
3. Real browser checks use the original compiled application and real local
   handlers with fake providers. Original forms, purchased-value/access flows,
   price screens and all14 Admin dashboard metrics have regression checks.
4. Isolation checks reject TCP/DNS, native PostgreSQL entry points in SQLite
   tests, non-memory engines/databases, child processes and nonlocal listeners.
   Provider configuration is scrubbed; dotenv reads are disabled. Secret-file
   denial is tested against a nonexistent sentinel, never an application dotenv.
5. Native connections are restricted to the pinned synthetic fixture and live
   server identity. Browser checks reject external page requests/native workers.
   Existing TypeScript/Vite checks use credential-free copied sources and guarded
   tools. Failed builds cannot publish a ready marker; safe resumption is tested.
6. Resource controls and evidence make tests resumable: one heavy phase at a time,
   one browser, bounded two-writer race checks, an exclusive native suite lock,
   an80-schema budget and one reused build snapshot. Failed/setup-timeout evidence
   is retained alongside successful retries. Never repeat a whole native suite
   simply to obtain a clean summary or delete its retained schemas.

## Workflow map

This is a representative map to executable checks, not a line-coverage report.
The full backend discovery command includes additional tests beside these files.

| Workflow | Backend checks | Browser checks |
| --- | --- | --- |
| Password/reset/logout and Google ownership | [revocation](../backend/tests/test_login_revocation.py), [Google](../backend/tests/test_google_account_security.py), [password boundaries](../backend/tests/test_password_input_boundaries.py) | [accounts](../tools/local-test/account_checks.mjs), [Google](../tools/local-test/google_checks.mjs), [revocation](../tools/local-test/revocation_checks.mjs) |
| Paid/trial value, provider evidence and recovery | [value](../backend/tests/test_subscription_value.py), [evidence](../backend/tests/test_payment_evidence.py), [reconciliation](../backend/tests/test_payment_reconciliation.py) | [value](../tools/local-test/purchase_value_checks.mjs), [verification](../tools/local-test/verification_checks.mjs), [recovery](../tools/local-test/reconciliation_checks.mjs) |
| Historical access, current records and comparison specifications | [access](../backend/tests/test_price_access_boundaries.py), [current query](../backend/tests/test_current_price_query.py), [specifications](../backend/tests/test_current_price_specifications.py) | [access](../tools/local-test/access_checks.mjs), [comparison](../tools/local-test/comparison_checks.mjs), [history metadata](../tools/local-test/history_metadata_checks.mjs) |
| Atomic business/audit writes and private sources | [price audit](../backend/tests/test_price_audit_atomicity.py), [catalog audit](../backend/tests/test_catalog_audit_atomicity.py), [response privacy](../backend/tests/test_audit_response_privacy.py) | [prices](../tools/local-test/price_admin_checks.mjs), [audit privacy](../tools/local-test/audit_privacy_checks.mjs), [catalog](../tools/local-test/catalog_checks.mjs) |
| Six original intelligence forms and stored costs | [planning](../backend/tests/test_planning_validation.py), [cost limits](../backend/tests/test_cost_validation.py), [SQL scope](../backend/tests/test_intelligence_scope.py) | [saved-value editing](../tools/local-test/admin_edit_prefill_checks.mjs), [honest units](../tools/local-test/cost_unit_checks.mjs) |
| Referrals and independent alerts/push ownership | [referrals](../backend/tests/test_referral_atomicity.py), [alerts](../backend/tests/test_watchlist_alert_service.py), [push](../backend/tests/test_push_ownership.py) | [referrals](../tools/local-test/referral_checks.mjs), [notifications](../tools/local-test/notification_checks.mjs), [push ownership](../tools/local-test/push_ownership_checks.mjs) |
| All14 Admin metrics and full CSV export | [summary](../backend/tests/test_admin_summary.py), [CSV security](../backend/tests/test_report_export_safety.py), [streaming](../backend/tests/test_report_export_streaming.py) | [dashboard](../tools/local-test/dashboard_checks.mjs), [CSV](../tools/local-test/export_checks.mjs) |
| Original UI, mobile, keyboard and honest offline copies | Existing account/access/query tests above | [original smoke tests](../tools/local-test/browser_checks.mjs), [keyboard](../tools/local-test/overlay_keyboard_checks.mjs), [offline](../tools/local-test/offline_ui_checks.mjs) |
| Migration preservation, catalog races and safe test tooling | [migration preflight](../backend/tests/test_migration_safety.py), [catalog identity](../backend/tests/test_catalog_identity.py), [build recovery](../backend/tests/test_local_build_recovery.py), [isolation](../tools/local-test/test_isolation.py) | [native runner](../tools/local-test/verify_pg_security.py), [guarded build](../tools/local-test/build_frontend.py) |

## Evidence and limits

- [Latest full backend suite](../tools/local-test/evidence/batch-81-backend.json).
- [Focused native history check](../tools/local-test/evidence/batch-81-postgres.json).
- Current dependency-update browser/build evidence:batch82. Source/build hashes
  match89 files; original appearance checked at desktop/mobile widths. See
  [dependency readiness](DEPENDENCY_READINESS.md).
- [Synthetic native backup/restore](../tools/local-test/evidence/batch-83-recovery.json),
  [four recovery guard tests](../tools/local-test/evidence/batch-83-recovery-guards.json),
  [three release-gate tests](../tools/local-test/evidence/batch-83-release-gate-tests.json)
  and [monitoring browser drill](../tools/local-test/evidence/batch-83-monitoring-browser.json).
  Reuses unchanged286-test backend evidence; no redundant full-suite run.
- The following batch47/61/62/63 links are historical focused evidence, not current
  fixture usage or latest build/suite counts.
- [Last full native baseline](../tools/local-test/evidence/batch-47-postgres.json).
- Catalog commit races passed in the [initial focused run](../tools/local-test/evidence/batch-62-postgres-initial.json);
  that same run contains a second-case connection setup error. Only that case was
  retried successfully using the [approved runner](../tools/local-test/evidence/batch-62-postgres-rollback-retry.json).
  Do not describe the initial run as wholly passing. Fixture73/80 schemas, stopped.
- [Catalog browser checks](../tools/local-test/evidence/batch-62-browser-catalog.json),
  [14-card dashboard](../tools/local-test/evidence/batch-62-browser-dashboard.json),
  [six-form checks](../tools/local-test/evidence/batch-61-browser-prefill.json).
- [Isolation probes](../tools/local-test/evidence/batch-63-isolation.json) and
  [current original browser smoke checks](../tools/local-test/evidence/batch-63-browser-baseline.json).
- [Current84-file frontend/source preservation](../tools/local-test/evidence/batch-62-frontend-preservation.json)
  reuses the [verified build](../tools/local-test/evidence/batch-61-build.json).

The process guards are not a virtual machine or a certificate against malicious
native code. Test-provider responses are fabricated, not proof of live Paystack,
Google, email/push delivery, production TLS or backup restoration. PY-35 retains
these operational approvals/checks. No live service or CI deployment was run.

Untested future policy changes must not be presented as completed safeguards.
PY-20 is complete locally (batch81); PY-35 retains explicit live approval gates.
Cookie/CSRF/race evidence:batch80; new price-claim evidence:batch79.
Earlier evidence links remain historical, not the newest completion counts.
Use [the progress tracker](../PRICEYARD_PROGRESS.md) for exact current counts and
[the local workflow](LOCAL_DEVELOPMENT.md) for commands, fixture limits and safe
resumption. Do not copy dependencies or rerun expensive phases merely because
this document or a test-only sentinel changed.
