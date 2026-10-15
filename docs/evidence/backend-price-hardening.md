# Backend price integrity implementation evidence

Verified on 15 October 2026 in synthetic local environments. No production
database, live payment, email, push or identity provider was contacted.

## Implemented contracts

- Guests and limited accounts receive existing current price summaries without
  premium meaning, suggested action or notes. Date searches, complete history
  and historical record IDs require full entitlement. Basic authenticated market
  signals omit deeper guidance; quality intelligence requires full access.
- Current prices are selected with a SQL window by recorded commodity, market,
  unit, bag specification, variant and grade. Case/outer whitespace normalization
  does not infer physical conversions. Missing legacy bag specifications remain
  unclassified and are never joined into comparable history/chart series.
- Selection ranks the latest observation before outdated/movement filtering;
  an older observation cannot resurface as current. Consumer history remains
  active-reference-only. Stable ID filters supplement legacy name filters.
- History/admin responses use bounded page/page_size arrays (100 by default,
  maximum 1000). Intelligence reads support commodity/market scope and bounds.
- New observation/reference timestamps require an offset, normalize to UTC and
  reject values over five minutes ahead. Date queries use Africa/Lagos days.
- Approval derives previous ranges and direction from an identified comparable
  predecessor and retained recorded averages. Missing averages produce unknown
  direction. No midpoint, grade, conversion or historical timestamp is invented.
- Backfills/corrections recalculate the affected successor with retained evidence.
  Published corrections require a reason of at least ten characters and retain
  original values in a restricted revision table. A linked price specification
  cannot silently move beneath its intelligence. PostgreSQL commodity row locks
  serialize concurrent approvals/corrections.
- Price DELETE withdraws and retains the row/links. Commodity/market DELETE
  deactivates retained identity. Market/quality/cost DELETE archives retained rows.
- New cost observations persist their measurement and reference timestamp;
  historical null metadata remains null. Nullable required PATCH values reject
  cleanly; optional commentary can be cleared.
- Two-source verification requires distinct recorded nonblank sources. Reporter
  claims remain stripped. Sources never enter consumer price schemas. General
  audit snapshots remain separate from the restricted originals.
- CSV textual cells neutralize spreadsheet formulas while monetary Decimal values
  retain their numeric precision. Exports include measurement metadata.
- Buying-zone validity reports either bound without automatically hiding records.
- Only anonymous undated current lists carry X-PriceYard-Public; authenticated
  current results are private/no-store and vary by Authorization.

## Executed verification

Command (fixed paths; no dotenv):

`audit-prep/p00/runtime/venv/Scripts/python.exe -I -B audit-prep/p00/run_backend_tests.py --pattern test_price_integrity.py`

Result: **28 tests passed, zero failures/errors**, 5.126 seconds on the recorded
run. Tests use in-memory synthetic SQLite and deny external TCP/DNS. Sessions
disable autoflush to match the HTTP transaction configuration. Regression cases
include timestamp correction never selecting its own row as predecessor.
Missing or explicitly cleared recorded averages remain null, produce unknown
movement, and retain the previous value in restricted correction evidence.

Actual HTTP middleware verification:

`audit-prep/p00/runtime/venv/Scripts/python.exe -I -B audit-prep/p00/run_backend_tests.py --pattern test_http_workflows.py`

Result: **8 tests passed, zero failures/errors**, 2.347 seconds. These use the
actual main ASGI application, genuine synthetic JWT sessions, AtomicSession and
middleware. They cover entitlement/source visibility, Reporter review boundaries,
administrator mutation/audit atomicity, injected audit failure rollback, final
commit failure returning 503 rather than a false success, hidden FAQ recovery,
query/body limits and a real 20-per-minute write limit. Oversized bodies return
413 before creating a database session; the 21st write returns 429 and does not
persist another activity event.

A 500-row single-series fixture materialized one current row with three SELECTs
(current result and two reference loads). Entitlement is checked once for a list,
rather than once per row. This is a bounded-query check, not a production capacity
or latency claim.

Additional administrative-query verification:

`audit-prep/p00/runtime/venv/Scripts/python.exe -I -B audit-prep/p00/run_backend_tests.py --pattern test_administration_queries.py`

Result: **4 tests passed**, zero failures/errors, 0.279 seconds. Users,
subscriptions and flagged-price summaries are bounded; flag names/counts use one
joined query. Subscription listing processes every expired synthetic row before
returning its requested page and preserves valid purchased/manual time and staff
authority. The existing **27 payment tests also passed**, 1.160 seconds, after
this query change.

PostgreSQL command:

`audit-prep/p00/runtime/venv/Scripts/python.exe -I -B audit-prep/p00/verify_migrations.py`

Result: **10 tests passed, zero failures/errors**, 16.640 seconds on the recorded
run, against the positively identified disposable cluster only. Coverage:

1. Fresh migration chain 0001 through 0025 matches current model columns.
2. Populated 0021 upgrade preserves original price values, sources, timestamps,
   inactive history, purchase amount, Reporter authority and manual access.
3. Legacy inclusive end dates retain their complete UTC day; no old payment is
   guessed to have already applied, and ambiguous historical cost units stay null.
4. Normalized duplicates abort before price DDL, with no automatic merge/deletion.
5. Invalid legacy previous ranges abort without rewriting the original evidence.
6. Automatic downgrade refuses to discard retained evidence.
7. Native/SQLAlchemy connection guards reject unapproved destinations before
   transport; the test uses reserved illustrative names, not real live hosts.
8. Concurrent approval and concurrent distinct/repeated-payment scenarios retain
   the correct predecessor and purchased value exactly once. The two valid 30-day
   synthetic purchases plus ten existing days yield seventy days; staff authority
   remains intact.
9. Concurrent identical notification enqueue creates one job; simultaneous
   PostgreSQL workers claim distinct jobs using synthetic sender callbacks.
10. A worker with a stale lease cannot acknowledge a newer lease acquired through
    a separate PostgreSQL connection.

The fresh-schema test also verifies the 320-character payment customer-email
column matches the existing user-email allowance. Price averages were already
nullable in the original schema; no historical values or nullability conversion
was needed to support missing observed averages.

The initial native-driver guard rejected SQLAlchemy's nontransport adapter
context. Its type is now validated separately; destination restrictions were not
relaxed. A later stopped-cluster connection attempt timed out before tests or
mutations. The recorded passing run followed restart of the same identified test
cluster and did not require elevated test execution.

## Migration and deployment limitations

Migration 0024 is additive, retains business records and rejects ambiguous
historical conflicts before DDL. It does not backfill grade, measurement,
predecessor or revised price values. Automatic downgrade is refused because it
would destroy revision/provenance evidence. Use a compatible application rollback
or a reviewed forward repair; never blindly drop these columns/tables.

This evidence does not establish production migration compatibility, deployed
indexes/query plans, provider behavior, operational backup/restore, browser
rendering or production load capacity. No production migration or deployment has
been performed.

## Superseding root verification (2026-10-15)

Final backend discovery passed 141 tests (zero failures/errors/skips) in 27.289 seconds. Price suite now includes 29 cases, including explicit export-bound rejection without record loss. PostgreSQL suite passed 12 tests in 20.492 seconds, including added concurrent reset-token/session and last-admin protection checks. These synthetic results supersede earlier subset counts and do not imply production/provider verification.
