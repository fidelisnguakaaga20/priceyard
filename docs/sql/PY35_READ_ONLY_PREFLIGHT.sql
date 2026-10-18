-- PriceYard production metadata review ONLY.
-- Owner must confirm dashboard project: priceyard / lrvpjfbtmftjkzaxbunk.
-- Run the ENTIRE file without selecting a subset in Supabase SQL Editor.
-- No application startup, migrations, customer rows, credentials or data writes.
-- If any statement fails, STOP and report the redacted error; do not repair/stamp.
-- This is not a backup, a migration approval or a complete compatibility verdict.

BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';
SET LOCAL idle_in_transaction_session_timeout = '30s';

-- Server/tool compatibility and approximate space needed; no customer data.
SELECT current_setting('server_version') AS postgres_version,
       current_setting('server_version_num') AS postgres_version_number,
       current_setting('transaction_read_only') AS transaction_read_only,
       pg_database_size(current_database()) AS database_bytes;

-- Confirm Alembic table location before interpreting the next query.
SELECT schemaname, tablename
FROM pg_catalog.pg_tables
WHERE tablename = 'alembic_version'
ORDER BY schemaname;

-- Only migration metadata is read. Expected application schema is public.
-- Missing/unknown/multiple revisions STOP rollout; no automatic correction.
SELECT version_num AS installed_alembic_revision
FROM public.alembic_version
ORDER BY version_num;

-- Inventory tables and security flags, including managed schemas if visible.
SELECT n.nspname AS schema_name, c.relname AS table_name,
       c.relkind AS relation_kind, c.relrowsecurity AS rls_enabled,
       c.relforcerowsecurity AS rls_forced
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'p', 'm', 'f')
  AND n.nspname NOT LIKE 'pg_%'
  AND n.nspname <> 'information_schema'
ORDER BY n.nspname, c.relname;

-- Application column metadata only: defaults and stored values are excluded.
SELECT table_name, column_name, data_type, udt_name, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- Extensions determine whether a plain local PostgreSQL restore is sufficient.
SELECT extname AS extension_name, extversion AS extension_version
FROM pg_catalog.pg_extension
ORDER BY extname;

-- Roles without passwords/hashes; ownership/grant mapping still needs review.
SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb,
       rolcanlogin, rolreplication, rolbypassrls
FROM pg_catalog.pg_roles
ORDER BY rolname;

ROLLBACK;
