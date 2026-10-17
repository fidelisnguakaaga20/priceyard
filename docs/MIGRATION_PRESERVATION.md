# PY-28 current migration-preservation contract

The original0021 application can take the owner-approved additive0022 login
revocation migration. Existing users, paid/trial access, payment evidence,
commodities, markets, recorded prices, confidential sources and audits must remain.
The0022 downgrade refuses because deleting revocation evidence can restore revoked
credentials. No new migration or application field is introduced by this guard.

Online Alembic execution now checks its starting revision and whether the database
contains rows **before running migration steps**. Populated unversioned, unknown,
forked or pre0021 databases stop with a generic reviewed-migration error. No
automatic stamp, cleanup, merge, activity-flag reset or guessed cost linkage occurs.
The preflight reads only metadata and existence checks; it exposes no record values.
Empty initialization and the reviewed0021/0022 baselines remain supported.

This closes the missing application-side protection against replaying historic
0006 focus changes and0020 cost-link changes on existing business data. Those old
migration files are retained unchanged. It cannot reconstruct flags or links
already changed in the past: any such repair requires original evidence, a
specific reviewed procedure and owner approval. Offline generated SQL also needs
independent review; it cannot inspect a live database's revision or records.

Acceptance verified only on positively pinned synthetic databases:

- Empty initialization succeeds; populated0021 upgrades to0022 without changing
  original records, prices, sources, payments, purchased access or catalog IDs.
- Populated0005 migration stops before0006 or0020; complete row, column and
  revision snapshots stay identical, including activity flags and original cost
  references/audit JSON.
- Unversioned/unknown/forked populated schemas require review without writes or
  leaking stored values. Current0022 downgrade refuses and retains evidence.

This is a compatibility boundary: older populated local installations now stop
for reviewed migration rather than silently proceeding. Production revision,
backup/restore, hosting permissions, migration rollout and any historical data
repair remain explicit owner-approved PY-35 operations. No production connection,
preflight, migration, backup or data repair was executed during this work.
