"""Internal-only login revocation; no business-field or policy change."""
from alembic import op
import sqlalchemy as sa

revision = "0022_login_revocation"
down_revision = "0021_feedback_screenshot"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("auth_version", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.create_table("revoked_access_tokens", sa.Column("token_hash", sa.String(64), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_revoked_access_tokens_user_id", "revoked_access_tokens", ["user_id"])
    op.create_index("ix_revoked_access_tokens_expires_at", "revoked_access_tokens", ["expires_at"])
    if op.get_bind().dialect.name == "postgresql":
        # Supabase may grant API roles rights on newly created public objects.
        # Login revocations are server-owned. Preserve every old users-column
        # UPDATE right while excluding the new account-security counter.
        op.execute(sa.text(r"""
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
$login_security$;
"""))


def downgrade():
    raise RuntimeError("Dropping login revocation records can restore revoked credentials; reviewed recovery is required")
