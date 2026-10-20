# 0022 rehearsal checkpoint — 2026-10-20 WAT

**Blocked before database startup; no migration ran.** Production is unchanged.
The owner approved only the isolated local rehearsal. Backup/export, verified
restoration and retrieved-copy checksum were not repeated.

## Verified preparation

- Exact existing Alembic migration compiles offline from0021 to0022 without
  importing application configuration, reading dotenv files or connecting to a
  database. Migration SHA256:
  `fff52739dc5efec205a1ca809f599fd03fb482d70f0faed1a5f11974620a232f`.
- Its downgrade refuses to delete revocation evidence. Three admission checks
  confirm default duplicate restore, unreviewed callback and unverified-baseline
  rejection before Docker/database work.
- Three existing, focused authentication regressions pass on fresh fabricated
  in-memory SQLite: legacy/reset revocation, idempotent logout and failed-reset
  transaction rollback. External sockets, dotenv and native DB connections are
  blocked. These do **not** prove actual-clone or hosted compatibility.
- Security-aware rollback candidate
  `2cfbfa65447d51b225a0d367433709c25bd6da4a` has the same backend application tree
  as current code: `fcc47f0a0d5a1596d8f3cd5790e61f624c3e04ed`. An original0021 app
  which ignores revocations is not a safe application rollback target.

## Actual local attempt

One startup attempt used the existing Desktop4.96, cached pinned PG17 image,
temporary WSL2GiB/one CPU/swap0 settings and a90second readiness limit. Docker
never became ready and no Linux distribution started. The controller, protected
export transfer, clone creation and migration were therefore **not attempted**.
This is a local environment failure, not a failed0022 migration.

The exact startup cause is unconfirmed. A Docker log WSL-update status was false;
installed WSL2.6.3 alone does not justify an update. No installation or retry was
performed. The unresponsive graceful stop was followed by verified cleanup of
only this attempt's Docker processes. Original stopped Docker and absent
`.wslconfig` states are restored; temporary config was hash-checked/archived
before removal. Original backups and previous recovery result remain intact.
Private resource journal: `0022-resource-run-20261020T102057Z-2c1fb8e8.json` in
the existing private backup root. It contains no customer rows or credentials.

## Resume acceptance criteria

After Docker readiness is resolved, use the prepared helper against a new RAM
clone from the existing EFS export, retaining all previous safety guards:

1. Preserve pristine0021 baseline. Verify transaction ROLLBACK and an injected
   failed upgrade leave original schema,59 table contents and sequences intact.
2. Apply exact0022 locally; verify only expected security additions/revision and
   preserve every original value, excluding only the newly added user counter
   from original-value fingerprints. Check defaults, constraints and indexes.
3. Check inherited PUBLIC/anon/authenticated privileges: new revocations must
   remain private. Investigate actual effective column/RLS rights on the new
   account counter; do not infer provider security from SQLite tests.
4. Check synthetic security constraints and restart recovery while preserving
   original and revocation evidence. Never downgrade/delete security records or
   restore an old snapshot over newer production activity.
5. Approve a compatible release/rollback artifact and hosted checks separately.

**Next owner action:** open Docker Desktop and report whether it shows Engine
running or a startup error. Do not reset Docker, delete volumes or reinstall it.
No production access, migration, push or deployment is authorized by this report.
