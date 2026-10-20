# 0022 protected rehearsal result ? 2026-10-20 WAT

**Passed locally.35/36 complete; PY-35 remains partial.** No production connection,
production migration, push, merge or deployment. Original appearance and business
rules are unchanged. Existing encrypted backup and retrieved Drive copy retain
SHA256 `f26ed1548064ca95666b0459ae5187ab583e13bff566df16fcecf7b4a8d67045`.
No new export, password entry or archive extraction was needed.

## Verified result

Final protected PostgreSQL17 rehearsal completed in54.6seconds; this is not a
promised recovery time. It used the cached pinned Supabase image and existing
EFS-protected recovered export. The pristine0021 database remained intact; a new
RAM-only clone received0022.

- Complete migration transaction ROLLBACK and injected SQL failure preserve0021
  schema, all59 original table counts/content fingerprints and sequences.
- Committed0022 preserves original values, original catalog and sequences. Only
  the approved new security objects/revision and explicitly checked ACL conversion
  differ. Every role's effective rights and grant options on old users columns
  remain identical; expected grantor/grantee chains are checked before ACL
  normalization for the rest of the catalog comparison.
- New counter default/not-null, revocation primary/foreign keys and indexes pass.
  PUBLIC/anon/authenticated cannot access the new revocation table or UPDATE
  the counter. New-table RLS is enabled with no policy; trusted owner access works.
- One collision-checked fabricated account/revocation exercises writes, null,
  foreign-key and duplicate rejection, and cascade inside a rolled-back transaction.
  No original account is edited or deleted.
- Clean PostgreSQL restart preserves all original values and synthetic security
  evidence. Native checksums pass; pristine0021 remains unchanged. The test RAM
  container is removed, and original backup/restoration evidence is preserved.
- Four fabricated-only privacy cases pass: ordinary migration without API roles;
  Supabase-style defaults preserving old-column rights and stronger column grant
  options; unsafe inherited counter rights rejected atomically; dependent grant
  chains rejected atomically. Binary COPY fixtures reject13 malformed streams;
  native fabricated COPY checks agree with independent single-stream digests.

## Security correction found by the rehearsal

The original0022 inherited Supabase defaults exposing its new revocation table
and extending API-role table UPDATE to auth_version. That local attempt stopped;
production was not contacted. The amended migration revokes grants only on the
new private table, enables its RLS, and replaces affected existing users table
UPDATE grants with equivalent grants on every original column. Existing explicit
column grant options are retained. Other existing users privileges/RLS are
unchanged. Unsupported grantors, grant chains or inherited new-object exposure
abort the entire migration; no CASCADE or blanket privilege reduction is used.
This is a safeguard for the already-approved internal security fields, with no
new business fields, UI or subscription change. Existing provider/API security
outside these new objects is not certified by this narrow rehearsal.

Migration SHA256:
`6b7cd540b41982c13091be3805f4660144b8b9b389224cecf7fa5b85d77469fa`.
Compiled raw SQL SHA256:
`221e1ec1a801936d66fe037fa39727ae36e986984eac92147a7cf051d41143f8`.
Independent source/diff review found no material blocker. The target must still
be at0021 and the migration actor must own both tables. An already0022 target
needs separately reviewed follow-up; do not stamp or automatically replay0022.

## Isolation and bounded execution

One non-root target,512MiB/oneCPU/pids64, network none, no ports/host binds or
persistent volumes, read-only root, no container logs, tmpfs data and verified
cgroup swap0. The already-running Docker VM had unused swap; only that swap was
safely disabled after checking zero use and sufficient available memory. Global
VM swap0 was confirmed before private bytes entered Docker. It stays disabled
for this VM session; no persistent WSL config was created and Docker was not
restarted. Existing containers/settings/volumes were not modified. Normal future
VM startup restores boot defaults. EFS protects local files; this is not BitLocker
or protection against a compromised host/Windows memory paging.

Earlier attempts remain recorded privately: clone owner/grants mismatch corrected
by preserving original database owner/settings rather than broadening permissions;
NULL ACL-query handling corrected; actual default-grant exposure corrected above.
Offline Alembic raw SQL now uses named parameter style to avoid pyformat percent
escaping. Batched strict binary COPY reduces Docker process overhead. Private
reports/logs stay outside Git under EFS; only aggregates are recorded here.

## Safe rollback and remaining release requirements

Pre-commit transaction rollback and failed-upgrade recovery are verified.
**Post-commit destructive downgrade is intentionally refused**, because dropping
revocations could reactivate credentials. Restart recovery retains security
records. Never restore the old snapshot over newer production records/payments.

Previously tested security-aware application candidate
`2cfbfa65447d51b225a0d367433709c25bd6da4a`, backend application tree
`fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed`, has three focused synthetic auth
regressions passed. Its exact hosted rollback runtime/artifact still needs
verification. The original application ignoring revocations is not a safe rollback.

Next: approved hosted HTTPS/session/Google tests, Paystack TEST checkout/webhooks/
recovery, approved-recipient delivery, scheduler/monitoring/clock/bounded hosting
checks and runtime/dependency provenance. Confirm non-database backup coverage,
recovery targets and post-snapshot write/payment reconciliation. Render master
still has automatic deployment/migration build behavior: no push, merge or release
until controlled migration/rollback and owner approval are complete.

Evidence: [redacted result](../tools/local-test/evidence/batch-122-0022-rehearsal.json),
[actual gate ledger](PY35_ACTUAL_RELEASE_GATES.json). Original prior-startup blocker
and successful backup/recovery reports are retained as history.
