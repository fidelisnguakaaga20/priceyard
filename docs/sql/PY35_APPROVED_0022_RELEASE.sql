-- OWNER-APPROVED CONTROLLED PRICEYARD RELEASE: 2026-10-21 WAT.
-- RUN ONLY in Supabase SQL Editor for project priceyard / lrvpjfbtmftjkzaxbunk.
-- https://supabase.com/dashboard/project/lrvpjfbtmftjkzaxbunk/sql/new
-- Wait for release coordination: do not run before Render auto-deploy is Off.
-- Run this ENTIRE file without selecting a subset, once only.
-- Any error/timeout: STOP. Do not retry, stamp, downgrade or repair automatically.
-- No customer/business records are deleted, reset or updated by this script.
-- Exact existing Alembic 0021-to-0022 SQL is retained unchanged after the preflight.
-- Reviewed migration SHA256: 6b7cd540b41982c13091be3805f4660144b8b9b389224cecf7fa5b85d77469fa
-- Original compiled SQL SHA256: 221e1ec1a801936d66fe037fa39727ae36e986984eac92147a7cf051d41143f8

BEGIN;

SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '30s';
SET LOCAL idle_in_transaction_session_timeout = '30s';
-- public is the creation schema; pg_catalog remains implicitly searched first.
SET LOCAL search_path = public, pg_temp;

SELECT version_num AS starting_revision FROM public.alembic_version FOR UPDATE;
DO $py35_preflight$
DECLARE
    revisions text[];
BEGIN
    IF current_database() <> 'postgres' OR current_user <> 'postgres' THEN
        RAISE EXCEPTION 'STOP: unexpected database or migration role';
    END IF;
    IF current_setting('server_version_num')::integer NOT BETWEEN 170000 AND 179999 THEN
        RAISE EXCEPTION 'STOP: PostgreSQL major version differs from reviewed version';
    END IF;
    SELECT array_agg(version_num ORDER BY version_num) INTO revisions FROM public.alembic_version;
    IF revisions IS DISTINCT FROM ARRAY['0021_feedback_screenshot']::text[] THEN
        RAISE EXCEPTION 'STOP: expected exactly the reviewed 0021 baseline';
    END IF;
    IF (SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid = 'public.users'::regclass)
       IS DISTINCT FROM current_user::text THEN
        RAISE EXCEPTION 'STOP: current role must own original users table';
    END IF;
    IF to_regclass('public.revoked_access_tokens') IS NOT NULL OR EXISTS (
        SELECT 1 FROM pg_attribute WHERE attrelid = 'public.users'::regclass
        AND attname = 'auth_version' AND attnum > 0 AND NOT attisdropped
    ) THEN
        RAISE EXCEPTION 'STOP: unexpected existing login-security objects';
    END IF;
END
$py35_preflight$;


-- Running upgrade 0021_feedback_screenshot -> 0022_login_revocation

ALTER TABLE users ADD COLUMN auth_version INTEGER DEFAULT 0 NOT NULL;

CREATE TABLE revoked_access_tokens (
    token_hash VARCHAR(64) NOT NULL, 
    user_id INTEGER NOT NULL, 
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    revoked_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    PRIMARY KEY (token_hash), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_revoked_access_tokens_user_id ON revoked_access_tokens (user_id);

CREATE INDEX ix_revoked_access_tokens_expires_at ON revoked_access_tokens (expires_at);

DO $login_security$
DECLARE
    users_table oid := 'public.users'::regclass;
    tokens_table oid := 'public.revoked_access_tokens'::regclass;
    users_owner oid;
    actor oid;
    old_columns text;
    affected record;
    api_role record;
    prior_column record;
    old_column_updates jsonb;
    privilege_name text;
    table_privileges text[] := ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER'];
BEGIN
    SELECT oid INTO actor FROM pg_roles WHERE rolname = current_user;
    SELECT relowner INTO users_owner FROM pg_class WHERE oid = users_table;
    IF users_owner IS DISTINCT FROM actor OR
       (SELECT relowner FROM pg_class WHERE oid = tokens_table) IS DISTINCT FROM actor THEN
        RAISE EXCEPTION 'Login security migration requires the original table owner';
    END IF;
    SELECT string_agg(format('%I', attname), ', ' ORDER BY attnum)
      INTO old_columns FROM pg_attribute
      WHERE attrelid = users_table AND attnum > 0 AND NOT attisdropped
        AND attname <> 'auth_version';
    IF old_columns IS NULL THEN
        RAISE EXCEPTION 'Original account columns are required';
    END IF;

    FOR affected IN
        SELECT a.grantor, a.grantee, a.is_grantable,
               CASE WHEN a.grantee = 0 THEN 'PUBLIC'
                    ELSE format('%I', r.rolname) END AS target
        FROM pg_class c
        CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) a
        LEFT JOIN pg_roles r ON r.oid = a.grantee
        WHERE c.oid = users_table AND a.privilege_type = 'UPDATE'
          AND (a.grantee = 0 OR r.rolname IN ('anon', 'authenticated'))
    LOOP
        IF affected.grantor <> users_owner OR EXISTS (
            SELECT 1 FROM pg_attribute c
            CROSS JOIN LATERAL aclexplode(c.attacl) a
            WHERE c.attrelid = users_table AND c.attnum > 0 AND NOT c.attisdropped
              AND a.privilege_type = 'UPDATE' AND a.grantee = affected.grantee
              AND a.grantor <> users_owner
        ) THEN
            RAISE EXCEPTION 'Account UPDATE grantors require separate review';
        END IF;
        IF EXISTS (
            SELECT 1 FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a
            WHERE c.oid = users_table AND a.privilege_type = 'UPDATE'
              AND a.grantor = affected.grantee
        ) OR EXISTS (
            SELECT 1 FROM pg_attribute c CROSS JOIN LATERAL aclexplode(c.attacl) a
            WHERE c.attrelid = users_table AND c.attnum > 0 AND NOT c.attisdropped
              AND a.privilege_type = 'UPDATE' AND a.grantor = affected.grantee
        ) THEN
            RAISE EXCEPTION 'Dependent account UPDATE grants require separate review';
        END IF;
        -- Table REVOKE also removes corresponding column grants. Save their
        -- grant options, then restore their union with the old table grant.
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                   'column', c.attname, 'grantable', a.is_grantable)
                   ORDER BY c.attnum), '[]'::jsonb)
          INTO old_column_updates
          FROM pg_attribute c CROSS JOIN LATERAL aclexplode(c.attacl) a
          WHERE c.attrelid = users_table AND c.attnum > 0 AND NOT c.attisdropped
            AND c.attname <> 'auth_version' AND a.grantee = affected.grantee
            AND a.privilege_type = 'UPDATE';
        EXECUTE format('REVOKE UPDATE ON TABLE public.users FROM %s RESTRICT', affected.target);
        EXECUTE format('GRANT UPDATE (%s) ON TABLE public.users TO %s%s',
                       old_columns, affected.target,
                       CASE WHEN affected.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
        FOR prior_column IN SELECT value FROM jsonb_array_elements(old_column_updates)
        LOOP
            IF (prior_column.value->>'grantable')::boolean THEN
                EXECUTE format('GRANT UPDATE (%I) ON TABLE public.users TO %s WITH GRANT OPTION',
                               prior_column.value->>'column', affected.target);
            END IF;
        END LOOP;
    END LOOP;

    REVOKE ALL PRIVILEGES ON TABLE public.revoked_access_tokens FROM PUBLIC RESTRICT;
    FOR api_role IN SELECT oid, rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')
    LOOP
        EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE public.revoked_access_tokens FROM %I RESTRICT', api_role.rolname);
    END LOOP;
    ALTER TABLE public.revoked_access_tokens ENABLE ROW LEVEL SECURITY;
    IF EXISTS (SELECT 1 FROM pg_policy WHERE polrelid = tokens_table) THEN
        RAISE EXCEPTION 'Unexpected login revocation publication policy';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_class c
        CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) a
        WHERE c.oid = tokens_table AND a.grantee = 0
    ) OR EXISTS (
        SELECT 1 FROM pg_attribute c CROSS JOIN LATERAL aclexplode(c.attacl) a
        WHERE c.attrelid = tokens_table AND c.attnum > 0 AND NOT c.attisdropped
          AND a.grantee = 0
    ) THEN
        RAISE EXCEPTION 'Public login revocation privileges remain';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_class c
        CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) a
        WHERE c.oid = users_table AND a.grantee = 0 AND a.privilege_type = 'UPDATE'
    ) OR EXISTS (
        SELECT 1 FROM pg_attribute c CROSS JOIN LATERAL aclexplode(c.attacl) a
        WHERE c.attrelid = users_table AND c.attname = 'auth_version'
          AND a.grantee = 0 AND a.privilege_type = 'UPDATE'
    ) THEN
        RAISE EXCEPTION 'Public account security counter UPDATE remains';
    END IF;
    IF current_setting('server_version_num')::integer >= 170000 THEN
        table_privileges := array_append(table_privileges, 'MAINTAIN');
    END IF;
    FOR api_role IN SELECT oid, rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')
    LOOP
        IF has_column_privilege(api_role.oid, users_table, 'auth_version', 'UPDATE') THEN
            RAISE EXCEPTION 'Inherited account security counter UPDATE requires separate review';
        END IF;
        FOREACH privilege_name IN ARRAY table_privileges LOOP
            IF has_table_privilege(api_role.oid, tokens_table, privilege_name) THEN
                RAISE EXCEPTION 'Inherited login revocation privileges require separate review';
            END IF;
        END LOOP;
        FOREACH privilege_name IN ARRAY ARRAY['SELECT','INSERT','UPDATE','REFERENCES'] LOOP
            IF has_any_column_privilege(api_role.oid, tokens_table, privilege_name) THEN
                RAISE EXCEPTION 'Inherited login revocation column privileges require separate review';
            END IF;
        END LOOP;
    END LOOP;
END
$login_security$;;

UPDATE alembic_version SET version_num='0022_login_revocation' WHERE alembic_version.version_num = '0021_feedback_screenshot';

COMMIT;


SELECT version_num AS installed_revision FROM public.alembic_version;
