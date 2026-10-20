# Verified database recovery — 2026-10-20 WAT

The actual encrypted archive and isolated database recovery passed. PY-35 remains
partial; this is not deployment permission. Original application and production
records were unchanged. No new source connection, password entry or migration
was needed for recovery.

## Evidence and scope

- Existing archive: `PriceYard-20261019T213738Z.7z`, outside Git in the owner-private
  `PriceYardPrivateBackup/EncryptedArchives` directory. SHA256:
  `f26ed1548064ca95666b0459ae5187ab583e13bff566df16fcecf7b4a8d67045`.
- AES-256/encrypted filenames, independent EFS decryption and file hashes passed.
  All59 tables' counts/content digests match; this includes customer accounts,
  prices, payment/subscription evidence and history. Recorded schema/column live
  order/types/defaults/constraints/indexes/RLS, roles/memberships/settings/effective
  schema/relation/database permissions, sequences and large objects match.
- Native checksums pass. Restored Alembic revision remains0021_feedback_screenshot.
  Final restoration/verification37.2 seconds excludes setup/download/earlier
  failed verification attempts; it is not a promised recovery time.
- Private result: EFS run `real-ram-restore-result-private.json`; root
  `latest-production-backup-status.json` confirms database_restoration_verified.
  Neither report nor backup contents belong in Git/chat.

## Protected target and reproducibility

One pinned Supabase Postgres17 Linux image,367203535 compressed layer bytes:
`supabase/postgres@sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b`.
Five source extension versions and en_US.UTF-8 pass. Supautils/SafeUpdate load;
SafeUpdate rejects unbounded UPDATE. No cloud project or paid service created.

Source files remain EFS-protected. Target: non-root, no capabilities/new privileges,
network none, no host binds/ports/persistent volumes/logs, read-only image root,
512MiB memory=memory-swap and actual swap0; database files use bounded tmpfs only.
WSL temporarily capped at2GiB/one CPU/swap0. This protects data files; it is not
full-disk encryption or protection against a compromised logged-in host.

Secret-free [recovery code](../tools/local-test/restore_verified_supabase_ram.py)
retains reviewed bundle/SQL/image pins and the original bootstrap administrator.
Only that already-existing role's duplicate CREATE is skipped. Every original
GRANTED BY/attribute remains. Two recorded pg_stat_statements view owners and
two recorded GraphQL schema ACLs are replayed exactly, including grant options.
Other owner/grant-chain mismatches still stop. Source data/files are never edited.
See the [PostgreSQL bootstrap/grantor issue](https://www.postgresql.org/message-id/671134.1778008247%40sss.pgh.pa.us).

Comparison uses the original read role and effective ACLs rather than grant-array
order. Live column order is checked independently of dropped-attribute gaps.
Seven equivalent CHECK cast renderings are compared using PostgreSQL's parser
on empty temporary LIKE tables; original allowed values/rules remain unchanged.
Nine small synthetic checks verify these cases before the real recovery.

The published helper inlines the identical catalog query; all other executed
restore logic is unchanged. Static equivalence and the already-verified refusal
pass without rerunning the real restoration. It is bound to this reviewed bundle,
not a universal automatic restore command. A future operator must review source,
new target, keys and pins; never clear safeguards to force a new backup through.

All test containers and their RAM data were removed. Docker/WSL stopped. The
test-created resource file was archived/hash-checked/removed, restoring previous
absence. Existing Docker disks/images/containers/settings remain preserved;
Docker auto-started existing EasySpend containers and returned them to stopped
state, without querying their databases or editing their configuration.

## Remaining before release

1. **Verified 2026-10-20 WAT:** owner confirms private Google Drive upload; the
   individually downloaded encrypted7z and original archive both have174448 bytes
   and SHA256 `f26ed1548064ca95666b0459ae5187ab583e13bff566df16fcecf7b4a8d67045`.
   Neither backup was extracted, modified or deleted. The earlier folder-ZIP
   comparison blocker is superseded. Upload/download was owner-performed; no
   Drive access by Codex. Keep archive passphrase and EFS recovery key separate.
2. Confirm non-database file coverage, provider/hosting configuration and server
   role credentials separately. Storage file bytes/provider secrets and settings,
   server-role passwords, Vault root keys and post-snapshot writes are outside
   this logical backup; Vault tables contain no secrets in this snapshot.
   Application account records/password hashes were preserved by data digests.
3. Review0022 migration on the actual-data clone, permissions, rollback and owner
   recovery targets before approving any production migration. No0022 rehearsal
   or migration was run in this batch.
4. Complete [external release gates](PY35_ACTUAL_RELEASE_GATES.json). Reconcile any
   writes/payments since the snapshot at an approved cutover; never overwrite
   newer customer activity with an old backup. No push/merge/deploy authorized.
