"""Owner-approved 0022 rehearsal callback; only an already verified RAM clone.

The operator supplies exact offline Alembic SQL and its reviewed migration hash.
This module imports no application/environment configuration and opens no sockets.
It emits aggregate evidence only; rows briefly enter memory for hashing and are
never printed or written to disk by this callback.
"""
import hashlib
import json
import re


UPGRADE_SQL = None
MIGRATION_SHA256 = None
DOWNGRADE_REFUSAL_VERIFIED = False
CLONE = "py0022_rehearsal"
FIXTURE_ID = 2147483646
MISSING_ID = 2147483645
TOKEN_HASH = hashlib.sha256(b"PY35 fabricated revoked token only").hexdigest()

# No stored values or function bodies are included in the catalog evidence.
CATALOG_SQL = r"""
SELECT jsonb_build_object(
 'schemas',(SELECT jsonb_agg(jsonb_build_array(nspname,pg_get_userbyid(nspowner),nspacl::text) ORDER BY nspname) FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname<>'information_schema'),
 'relations',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,c.relkind,c.relrowsecurity,c.relforcerowsecurity,pg_get_userbyid(c.relowner),c.relacl::text,c.reloptions) ORDER BY n.nspname,c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema'),
 'columns',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod),a.attnotnull,pg_get_expr(d.adbin,d.adrelid),a.attidentity,a.attgenerated,a.attacl::text) ORDER BY n.nspname,c.relname,a.attnum) FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE a.attnum>0 AND NOT a.attisdropped AND n.nspname !~ '^pg_' AND n.nspname<>'information_schema'),
 'constraints',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,k.conname,k.contype,k.convalidated,pg_get_constraintdef(k.oid)) ORDER BY n.nspname,c.relname,k.conname) FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema'),
 'indexes',(SELECT jsonb_agg(jsonb_build_array(schemaname,tablename,indexname,indexdef) ORDER BY schemaname,tablename,indexname) FROM pg_indexes WHERE schemaname !~ '^pg_' AND schemaname<>'information_schema'),
 'policies',(SELECT jsonb_agg(to_jsonb(p) ORDER BY schemaname,tablename,policyname) FROM pg_policies p WHERE schemaname !~ '^pg_'),
 'triggers',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid)) ORDER BY n.nspname,c.relname,t.tgname) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT t.tgisinternal AND n.nspname !~ '^pg_'),
 'functions',(SELECT jsonb_agg(jsonb_build_array(n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),pg_get_userbyid(p.proowner),p.proacl::text,p.prosecdef,p.proconfig,md5(p.prosrc)) ORDER BY n.nspname,p.proname,p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema'),
 'default_acls',(SELECT jsonb_agg(jsonb_build_array(pg_get_userbyid(d.defaclrole),COALESCE(n.nspname,''),d.defaclobjtype,d.defaclacl::text) ORDER BY d.defaclrole,d.defaclnamespace,d.defaclobjtype) FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace),
 'extensions',(SELECT jsonb_agg(jsonb_build_array(e.extname,e.extversion,n.nspname) ORDER BY e.extname) FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace))
"""
SEQUENCES_SQL = """SELECT COALESCE(jsonb_agg(to_jsonb(s) ORDER BY schemaname,sequencename),'[]'::jsonb)
FROM (SELECT schemaname,sequencename,last_value,increment_by,start_value,min_value,max_value,cycle
FROM pg_sequences WHERE schemaname !~ '^pg_') s;"""


def run(psql, execute, shell, manifest, catalog, result):
    """Called after the original 0021 restoration's complete verification."""
    if not isinstance(UPGRADE_SQL, str) or not re.fullmatch(r"[a-f0-9]{64}", MIGRATION_SHA256 or ""):
        raise RuntimeError("Exact reviewed offline migration SQL/hash required")
    if not DOWNGRADE_REFUSAL_VERIFIED:
        raise RuntimeError("Exact migration downgrade refusal must be verified first")
    if not re.match(r"\s*BEGIN;", UPGRADE_SQL) or not re.search(r"COMMIT;\s*$", UPGRADE_SQL):
        raise RuntimeError("Migration must retain its PostgreSQL transaction")
    checks = {"status": "running", "migration_sha256": MIGRATION_SHA256,
              "production_connections": 0, "production_changes": False,
              "original_application_rollback_security_safe": False,
              "security_aware_application_artifact_runtime_verified": False}
    result["migration_0022_rehearsal"] = checks
    result["migration_rehearsal"] = checks

    def sql(statement, database=CLONE, readonly=True):
        return psql("SET statement_timeout='12s'; SET lock_timeout='2s';\n" + statement,
                    database=database, readonly=readonly, role="postgres")

    def obj(statement, database=CLONE):
        return json.loads(sql(statement, database=database))

    def assert_true(statement, message):
        if sql("SELECT (" + statement + ");").strip() != b"t":
            raise RuntimeError(message)

    def snapshot(database):
        return obj(CATALOG_SQL + ";", database), obj(SEQUENCES_SQL, database)

    def verify_data(database, upgraded=False, fixture=False):
        checked = 0
        for table in manifest["tables"]:
            schema, name = table["schema"], table["table"]
            if not re.fullmatch(r"[a-z_][a-z_0-9]*", schema + "") or not re.fullmatch(r"[a-z_][a-z_0-9]*", name):
                raise RuntimeError("Unexpected source table identifier")
            reference = '"' + schema + '"."' + name + '"'
            where = " WHERE t.id<>" + str(FIXTURE_ID) if fixture and (schema, name) == ("public", "users") else ""
            if int(sql("SELECT count(*) FROM ONLY " + reference + " t" + where + ";", database)) != table["rows"]:
                raise RuntimeError("Original table count differs during rehearsal")
            if upgraded and (schema, name) == ("public", "alembic_version"):
                if sql("SELECT version_num FROM public.alembic_version;", database).strip() != b"0022_login_revocation":
                    raise RuntimeError("Expected exact upgraded revision")
            else:
                expression = "to_jsonb(t)" + (" - 'auth_version'" if upgraded and (schema, name) == ("public", "users") else "")
                payload = sql("COPY (SELECT (" + expression + ")::text FROM ONLY " + reference + " t" + where +
                              " ORDER BY (" + expression + ')::text COLLATE "C") TO STDOUT (FORMAT binary);', database)
                if hashlib.sha256(payload).hexdigest() != table["copy_json_sha256"]:
                    raise RuntimeError("Original table digest differs during rehearsal")
            checked += 1
        return checked

    if sql("SELECT version_num FROM public.alembic_version;", "postgres").strip() != b"0021_feedback_screenshot":
        raise RuntimeError("Original verified baseline must remain 0021")
    before, sequences = snapshot("postgres")
    if psql("SELECT count(*) FROM pg_database WHERE datname='" + CLONE + "';").strip() != b"0":
        raise RuntimeError("Rehearsal clone already exists; preserve it")
    psql("CREATE DATABASE " + CLONE + " WITH TEMPLATE postgres;", readonly=False)
    # CREATE DATABASE TEMPLATE does not copy database-scoped role settings.
    # Replay only the recorded baseline DB's settings onto this new local clone.
    original_roles = {row[0] for row in catalog["roles"]}
    for database, role, settings in catalog.get("database_role_settings") or []:
        if database != "postgres":
            continue
        if role and role not in original_roles:
            raise RuntimeError("Unrecorded clone settings role")
        for setting in settings or []:
            key, separator, value = setting.partition("=")
            if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9.]*", key):
                raise RuntimeError("Unreviewed clone database setting")
            key_sql = '"' + key.replace('"', '""') + '"'
            value_sql = "'" + value.replace("'", "''") + "'"
            prefix = ("ALTER ROLE \"" + role.replace('"', '""') + "\" IN DATABASE " + CLONE
                      if role else "ALTER DATABASE " + CLONE)
            psql(prefix + " SET " + key_sql + " TO " + value_sql + ";", readonly=False)
    checks["source_role_login_and_clone_database_settings_selected"] = True
    if snapshot(CLONE) != (before, sequences):
        raise RuntimeError("Clone metadata or sequences differ before rehearsal")
    checks["baseline_clone_tables_verified"] = verify_data(CLONE)

    # A complete dry run proves all DDL reaches the final rollback successfully.
    rolled_back = re.sub(r"COMMIT;\s*$", "ROLLBACK;", UPGRADE_SQL)
    sql(rolled_back, readonly=False)
    if snapshot(CLONE) != (before, sequences):
        raise RuntimeError("Migration transaction rollback changed metadata")
    verify_data(CLONE)
    checks["complete_upgrade_transaction_rollback"] = True
    # Then a deterministic database exception exercises abort-on-error recovery.
    failed = re.sub(r"COMMIT;\s*$", "SELECT 1 / 0;\nCOMMIT;", UPGRADE_SQL)
    try:
        sql(failed, readonly=False)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("Injected migration failure unexpectedly committed")
    if snapshot(CLONE) != (before, sequences):
        raise RuntimeError("Failed migration changed original metadata")
    verify_data(CLONE)
    checks["injected_failure_preserves_0021_data_and_schema"] = True

    sql(UPGRADE_SQL, readonly=False)
    result.update(migrations_run=1, production_migrations_run=0)
    checks["migration_applied_to_isolated_clone_only"] = True
    checks["preserved_original_tables"] = verify_data(CLONE, upgraded=True)
    after, observed_sequences = snapshot(CLONE)
    allowed_names = {"revoked_access_tokens", "revoked_access_tokens_pkey",
                     "ix_revoked_access_tokens_user_id", "ix_revoked_access_tokens_expires_at"}
    filtered = json.loads(json.dumps(after))
    for key in ("relations", "columns", "constraints", "indexes"):
        filtered[key] = [row for row in filtered[key] or [] if not
                         (row[0] == "public" and row[1] in allowed_names)]
    filtered["columns"] = [row for row in filtered["columns"] if row[:3] != ["public", "users", "auth_version"]]
    if filtered != before or observed_sequences != sequences:
        raise RuntimeError("Unexpected original catalog or sequence change")
    checks["original_catalog_and_sequences_preserved"] = True
    columns = [row for row in after["columns"] if row[:2] == ["public", "revoked_access_tokens"]]
    expected = [("token_hash", "character varying(64)"), ("user_id", "integer"),
                ("expires_at", "timestamp with time zone"), ("revoked_at", "timestamp with time zone")]
    if [(row[2], row[4]) for row in columns] != expected or not all(row[5] for row in columns):
        raise RuntimeError("Revocation table fields differ from reviewed migration")
    version = [row for row in after["columns"] if row[:3] == ["public", "users", "auth_version"]]
    if len(version) != 1 or version[0][4:7] != ["integer", True, "0"]:
        raise RuntimeError("Account security counter definition differs")
    assert_true("NOT EXISTS (SELECT 1 FROM public.users WHERE auth_version<>0 OR auth_version IS NULL)", "Existing account defaults differ")
    assert_true("(SELECT count(*) FROM public.revoked_access_tokens)=0", "Revocation table must start empty")
    assert_true("EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='public.revoked_access_tokens'::regclass AND contype='p' AND conkey=ARRAY[1]::smallint[])", "Revocation primary key differs")
    assert_true("EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='public.revoked_access_tokens'::regclass AND contype='f' AND confrelid='public.users'::regclass AND confdeltype='c' AND conkey=ARRAY[2]::smallint[])", "Revocation user constraint differs")
    assert_true("(SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND tablename='revoked_access_tokens' AND indexname IN ('ix_revoked_access_tokens_user_id','ix_revoked_access_tokens_expires_at'))=2", "Security indexes missing")
    checks["expected_schema_defaults_constraints_and_indexes"] = True

    # Provider defaults must never publish or permit forgery/deletion of tokens.
    exposure = obj("""SELECT jsonb_build_object(
      'public',EXISTS(SELECT 1 FROM pg_class c CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a WHERE c.oid='public.revoked_access_tokens'::regclass AND a.grantee=0),
      'api_roles',EXISTS(SELECT 1 FROM pg_roles r CROSS JOIN (VALUES ('SELECT'),('INSERT'),('UPDATE'),('DELETE'),('TRUNCATE'),('REFERENCES'),('TRIGGER')) p(privilege) WHERE r.rolname IN ('anon','authenticated') AND has_table_privilege(r.oid,'public.revoked_access_tokens',p.privilege)));""")
    checks["private_table_provider_role_exposure"] = exposure
    if any(exposure.values()):
        checks.update(status="failed", failure="Provider default grants expose login revocation table")
        raise RuntimeError("Provider default grants expose login revocation table; release blocked")
    checks["new_security_table_private"] = True
    assert_true("NOT EXISTS (SELECT 1 FROM public.users WHERE id IN (2147483646,2147483645) OR email='py35-rehearsal@example.invalid' OR referral_code='PY35RAMONLY')", "Synthetic identity conflicts; existing records preserved")
    fixture = """INSERT INTO public.users(id,full_name,email,password_hash,auth_provider,role,is_active,referral_code)
      VALUES (2147483646,'PY35 synthetic rehearsal','py35-rehearsal@example.invalid','fabricated-unusable-password-hash','local','free_user',true,'PY35RAMONLY');
      UPDATE public.users SET auth_version=1 WHERE id=2147483646;
      INSERT INTO public.revoked_access_tokens(token_hash,user_id,expires_at,revoked_at)
      VALUES ('TOKEN',2147483646,now()+interval '1 day',now());""".replace("TOKEN", TOKEN_HASH)
    sql("BEGIN;\n" + fixture + "\nCOMMIT;", readonly=False)
    rejection_sql = """BEGIN;
    DO $probe$ DECLARE rejected boolean; BEGIN
      rejected:=false; BEGIN UPDATE public.users SET auth_version=NULL WHERE id=2147483646; EXCEPTION WHEN not_null_violation THEN rejected:=true; END;
      IF NOT rejected THEN RAISE EXCEPTION 'Counter accepted null'; END IF;
      rejected:=false; BEGIN INSERT INTO public.revoked_access_tokens VALUES(repeat('a',64),2147483645,now(),now()); EXCEPTION WHEN foreign_key_violation THEN rejected:=true; END;
      IF NOT rejected THEN RAISE EXCEPTION 'Unknown account accepted'; END IF;
      rejected:=false; BEGIN INSERT INTO public.revoked_access_tokens VALUES(repeat('b',64),2147483646,NULL,now()); EXCEPTION WHEN not_null_violation THEN rejected:=true; END;
      IF NOT rejected THEN RAISE EXCEPTION 'Null expiry accepted'; END IF;
      rejected:=false; BEGIN INSERT INTO public.revoked_access_tokens VALUES('TOKEN',2147483646,now(),now()); EXCEPTION WHEN unique_violation THEN rejected:=true; END;
      IF NOT rejected THEN RAISE EXCEPTION 'Duplicate revocation accepted'; END IF;
      DELETE FROM public.users WHERE id=2147483646;
      IF EXISTS(SELECT 1 FROM public.revoked_access_tokens WHERE user_id=2147483646) THEN RAISE EXCEPTION 'Cascade failed'; END IF;
    END $probe$; ROLLBACK;""".replace("TOKEN", TOKEN_HASH)
    sql(rejection_sql, readonly=False)
    checks["synthetic_constraints_and_cascade_rollback"] = True
    checks["downgrade_refusal_verified"] = True
    security_sql = "SELECT jsonb_build_array((SELECT to_jsonb(u) FROM public.users u WHERE id=2147483646),(SELECT jsonb_agg(to_jsonb(r) ORDER BY token_hash) FROM public.revoked_access_tokens r));"
    protected_security = hashlib.sha256(sql(security_sql)).hexdigest()
    verify_data(CLONE, upgraded=True, fixture=True)
    shell("pg_ctl -D /work/cluster -m fast -w -t 15 stop > /work/control.log 2>&1; pg_ctl -D /work/cluster -l /work/server.log -w -t 15 start > /work/control.log 2>&1")
    if hashlib.sha256(sql(security_sql)).hexdigest() != protected_security:
        raise RuntimeError("Security evidence changed after recovery restart")
    if snapshot(CLONE) != (after, sequences):
        raise RuntimeError("Upgraded schema or sequences changed after recovery")
    verify_data(CLONE, upgraded=True, fixture=True)
    verify_data("postgres")
    if snapshot("postgres") != (before, sequences):
        raise RuntimeError("Preserved 0021 baseline changed")
    checks.update(status="passed", original_0021_baseline_preserved=True,
                  restart_recovery_preserves_original_and_security_records=True,
                  security_evidence_not_downgraded_or_deleted=True,
                  synthetic_security_accounts=1, synthetic_revocation_records=1,
                  remaining="Approved hosted checks and security-aware rollback artifact runtime verification")
    return checks


run.purpose = "0022_local_only"
