# PriceYard backup and recovery procedure

Scope: local synthetic rehearsal is authorized. Connecting to production, taking
a customer-data backup, restoring it anywhere, changing retention or performing
a live migration/cutover requires a separately approved target and procedure.
Never paste credentials or backup contents into chat, logs, Git or test evidence.

## Local rehearsal

Use only the existing identity-pinned small PostgreSQL fixture at127.0.0.1:55449,
identifier7697910732590408300. Source is a new synthetic schema in
priceyard_isolated_test; restore target is the new fixed database
priceyard_synthetic_restore_20261018 in that same isolated cluster. No existing
database/schema is dropped, overwritten or cleaned. The controller refuses an
existing unmarked target and a populated restore schema. One tiny fixture/archive
is retained; do not repeatedly create databases or raise the native schema budget.

The native fixture includes current application tables and fabricated accounts,
14-day trial,40 remaining paid days, successful/pending payments, original Egusi/
Kwali prices with unknown measurements, private source, audit and login revocation.
pg_dump creates a custom-format schema archive; pg_restore restores it atomically
into the empty target. Verify row digests/counts, column types/precision/defaults,
constraints, indexes and sequence state against the pre-backup baseline, and
verify the source is unchanged. Archive stays under ignored tools/local-test/runtime.
Successful commands and digests are recorded in batch83 evidence. The first
restore succeeded before raw CHECK-definition comparison failed: PostgreSQL
rewrote equivalent varchar-array casts. Its own planned expressions and all
constraint validation flags match; source raw baseline and restored rows match.
Separate dump/restore timings were not captured for that first run. Do not rerun
solely for timing; the corrected runner records them before verification on a
future authorized drill. A procedure alone is not proof of recovery. No migrations
or provider sends occur.

## Future owner-approved production backup

1. Owner chooses an operator, backup destination/access, retention, acceptable
   data-loss window (RPO) and recovery time (RTO). These targets are currently
   undecided; local rehearsal time is not a production promise.
2. Confirm exact source identity/revision, PostgreSQL/tool compatibility, storage
   size and the provider's supported backup process. Inventory application and
   provider-managed auth/storage objects, extensions, roles/grants/RLS, functions,
   files and separate configuration needed for recovery. A schema-only local
   drill does not prove coverage of these production resources.
3. Use the approved platform secret manager/credential mechanism. Take the
   approved consistent backup; checksum it, encrypt/restrict access, and keep a
   separately controlled copy. Test retrieval and expiry/access revocation. Do
   not write raw connection strings to shell history or upload customer data to
   public tools. Git source backups do not back up customer records.
4. Before calling it a recoverable backup, restore that actual backup into an
   explicitly approved isolated target with all provider egress disabled.
   Validate role/RLS permissions, catalog IDs, raw prices/units/timestamps/private
   sources, historical audits, customer password/security versions, revoked/reset
   tokens, paid/trial value and every payment reference/status/amount/provider ID.
   Also validate indexes/sequences/constraints and application startup. Compare
   protected digests/counts through a reviewed process; expose no personal data.
5. Record evidence, backup age, duration and owner acceptance against RPO/RTO.
   Failed restore/incomplete access evidence blocks release. Keep the source and
   failed evidence intact; investigate rather than stamping/repairing history.

## Incident and rollback

Stop new rollout steps; retain logs/evidence and disable the faulty worker or
payment-recovery scheduler through an approved operator. Distinguish app failure,
provider delay and database corruption before selecting a recovery action.

Prefer reverting to the last compatible application artifact against preserved
data when safe. Do not downgrade revocation storage, delete migration evidence,
reset customer passwords or replay payments as a generic rollback. A restore
can roll back customer activity and payment evidence: reconcile all payments and
writes since the backup using provider evidence before any approved cutover.
Never automatically credit/refund an ambiguous historical purchase.

For an approved disaster restore, use a new target, keep the original read-only,
disable outgoing email/push/WhatsApp/payment jobs in the restore, and verify
identities/value/security before enabling access or external services. Owner
must approve DNS/app/DB switching and return-to-service. Keep both original and
restored evidence until approved retention disposal. No such operation was run
under local authorization.
