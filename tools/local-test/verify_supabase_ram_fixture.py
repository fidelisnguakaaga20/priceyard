"""Synthetic-only PG17 compatibility/restore check; never opens a real backup."""
import json
import os
from pathlib import Path
import subprocess
import uuid

ROOT = Path(r"C:\Users\HP\AppData\Local\PriceYardPrivateBackup")
CLI = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
IMAGE = "supabase/postgres@sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b"
MEMORY = 512 * 1024 * 1024

SCRIPT = r"""
set -eu
umask 077
test "$(id -un)" = postgres
test "$(stat -f -c %T /work)" = tmpfs
test "$(cat /sys/fs/cgroup/memory.max)" = 536870912
test "$(cat /sys/fs/cgroup/memory.swap.max)" = 0
test "$(awk 'END {print NR}' /proc/swaps)" = 1
awk '$2 == "/" && $4 ~ /(^|,)ro(,|$)/ {ok=1} END {exit !ok}' /proc/mounts
test "$(awk 'END {print NR}' /proc/net/route)" = 1
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 393216
echo RAM_SWAP_ROOT_AND_NETWORK_GUARDS_PASSED
case "$(postgres --version)" in *" 17."*) ;; *) exit 21 ;; esac
mkdir /work/socket
export PGHOST=/work/socket PGUSER=priceyard_fixture_owner PGDATABASE=postgres PGCONNECT_TIMEOUT=3
cleanup_fixture() {
  status=$?
  for data in /work/source /work/restore; do
    if test -f "$data/postmaster.pid"; then pg_ctl -D "$data" -m fast -w -t 10 stop >/dev/null 2>&1 || true; fi
  done
  if test "$status" != 0; then
    for log in /work/init.log /work/server.log /work/control.log /work/restore.log; do
      if test -f "$log"; then tail -n 12 "$log"; fi
    done
  fi
  exit "$status"
}
trap cleanup_fixture EXIT
start_fixture() {
  initdb -D "$1" -U priceyard_fixture_owner -A trust --locale=en_US.UTF-8 --encoding=UTF8 --data-checksums > /work/init.log 2>&1
  printf "\nlisten_addresses=''\nunix_socket_directories='/work/socket'\nshared_buffers='16MB'\nwork_mem='1MB'\nmaintenance_work_mem='16MB'\nmax_connections=8\nmax_worker_processes=0\nmax_wal_senders=0\nmax_replication_slots=0\nshared_preload_libraries='pg_stat_statements'\nlog_statement='none'\nlog_min_messages='fatal'\ntimezone='UTC'\n" >> "$1/postgresql.conf"
  pg_ctl -D "$1" -l /work/server.log -w -t 15 start > /work/control.log 2>&1
}
start_fixture /work/source
test "$(psql -X -At -v ON_ERROR_STOP=1 -c 'SELECT datcollate FROM pg_database WHERE datname=current_database()')" = en_US.UTF-8
test "$(psql -X -At -v ON_ERROR_STOP=1 -c "WITH expected(name,version) AS (VALUES ('plpgsql','1.0'),('pgcrypto','1.3'),('uuid-ossp','1.1'),('pg_stat_statements','1.11'),('supabase_vault','0.3.1')) SELECT count(*) FROM expected e JOIN pg_available_extension_versions v USING(name,version)")" = 5
psql -X -q -v ON_ERROR_STOP=1 <<'SQL'
CREATE SCHEMA extensions;
CREATE SCHEMA vault;
CREATE EXTENSION pgcrypto WITH SCHEMA extensions VERSION '1.3';
CREATE EXTENSION "uuid-ossp" WITH SCHEMA extensions VERSION '1.1';
CREATE EXTENSION pg_stat_statements WITH SCHEMA extensions VERSION '1.11';
CREATE EXTENSION supabase_vault WITH SCHEMA vault VERSION '0.3.1';
CREATE TABLE public.fabricated_fixture(id integer PRIMARY KEY, retired_fixture text, label text NOT NULL, observed_at timestamptz);
ALTER TABLE public.fabricated_fixture DROP COLUMN retired_fixture;
INSERT INTO public.fabricated_fixture VALUES (1,'FABRICATED ONLY', '2026-01-01T12:00:00Z'), (2,chr(8358)||' SYNTHETIC',NULL),(3,'NO CUSTOMER DATA','2026-01-02T12:00:00Z');
CREATE ROLE fixture_group NOLOGIN;
CREATE ROLE fixture_reader NOLOGIN;
GRANT fixture_group TO fixture_reader WITH INHERIT FALSE GRANTED BY priceyard_fixture_owner;
CREATE SCHEMA fixture_initial_acl;
GRANT USAGE ON SCHEMA fixture_initial_acl TO fixture_reader WITH GRANT OPTION;
CREATE ROLE fixture_extension_owner NOLOGIN;
GRANT USAGE,CREATE ON SCHEMA extensions TO fixture_extension_owner;
ALTER VIEW extensions.pg_stat_statements OWNER TO fixture_extension_owner;
BEGIN;
CREATE TEMP TABLE fixture_cast_probe(value varchar) ON COMMIT DROP;
ALTER TABLE fixture_cast_probe ADD CONSTRAINT allowed_values CHECK ((value)::text = ANY ((ARRAY['one'::varchar,'two'::varchar])::text[]));
INSERT INTO fixture_cast_probe VALUES ('one'),('two');
DO $test$ BEGIN BEGIN INSERT INTO fixture_cast_probe VALUES ('three'); RAISE EXCEPTION 'Unexpected allowed value'; EXCEPTION WHEN check_violation THEN NULL; END; END $test$;
COMMIT;
SQL
echo NATIVE_CHECK_CONSTRAINT_CAST_PARSER_AND_ENFORCEMENT_PASSED
psql -X -q -v ON_ERROR_STOP=1 -c "LOAD 'supautils'; LOAD 'safeupdate';"
if psql -X -q -v ON_ERROR_STOP=1 -c "LOAD 'safeupdate'; UPDATE public.fabricated_fixture SET label='MUST BE REJECTED';" > /work/safeupdate.log 2>&1; then exit 22; fi
grep -qi 'WHERE' /work/safeupdate.log
echo RECORDED_PRELOAD_LIBRARIES_AND_SAFEUPDATE_GUARD_PASSED
echo EXACT_EXTENSION_VERSIONS_AND_LOCALE_PASSED
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT count(*)||':'||md5(string_agg(row_to_json(t)::text,'|' ORDER BY id)) FROM public.fabricated_fixture t" > /work/source-digest
pg_dump --no-password --format=custom --file=/work/fabricated.dump > /work/dump.log 2>&1
pg_dumpall --no-password --roles-only --no-role-passwords --file=/work/fabricated-roles.sql
test "$(grep -c '^CREATE ROLE priceyard_fixture_owner;$' /work/fabricated-roles.sql)" = 1
awk '$0 != "CREATE ROLE priceyard_fixture_owner;"' /work/fabricated-roles.sql > /work/restore-roles.sql
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT r.rolname,m.rolname,g.rolname,a.admin_option,a.inherit_option,a.set_option FROM pg_auth_members a JOIN pg_roles r ON r.oid=a.roleid JOIN pg_roles m ON m.oid=a.member JOIN pg_roles g ON g.oid=a.grantor WHERE r.rolname='fixture_group' ORDER BY r.rolname,m.rolname,g.rolname" > /work/source-membership
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(x::text ORDER BY x::text) FROM pg_namespace n,unnest(n.nspacl) x WHERE n.nspname='fixture_initial_acl'" > /work/source-acl
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(column_name ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='fabricated_fixture'" > /work/source-column-order
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(ordinal_position ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='fabricated_fixture'" > /work/source-column-numbers
pg_ctl -D /work/source -m fast -w -t 10 stop > /work/control.log 2>&1
start_fixture /work/restore
psql -X -q -v ON_ERROR_STOP=1 -f /work/restore-roles.sql
pg_restore --no-password --exit-on-error --single-transaction --dbname=postgres /work/fabricated.dump > /work/restore.log 2>&1
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT r.rolname,m.rolname,g.rolname,a.admin_option,a.inherit_option,a.set_option FROM pg_auth_members a JOIN pg_roles r ON r.oid=a.roleid JOIN pg_roles m ON m.oid=a.member JOIN pg_roles g ON g.oid=a.grantor WHERE r.rolname='fixture_group' ORDER BY r.rolname,m.rolname,g.rolname" > /work/restored-membership
cmp /work/source-membership /work/restored-membership
echo BOOTSTRAP_AND_EXPLICIT_GRANTOR_RESTORE_PASSED
psql -X -q -v ON_ERROR_STOP=1 -c 'REVOKE ALL PRIVILEGES ON SCHEMA fixture_initial_acl FROM fixture_reader; GRANT USAGE ON SCHEMA fixture_initial_acl TO fixture_reader WITH GRANT OPTION;'
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(x::text ORDER BY x::text) FROM pg_namespace n,unnest(n.nspacl) x WHERE n.nspname='fixture_initial_acl'" > /work/restored-acl
cmp /work/source-acl /work/restored-acl
echo RECORDED_SCHEMA_PRIVILEGES_AND_GRANT_OPTION_PASSED
psql -X -q -v ON_ERROR_STOP=1 -c 'ALTER VIEW extensions.pg_stat_statements OWNER TO fixture_extension_owner;'
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT pg_get_userbyid(c.relowner) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='extensions' AND c.relname='pg_stat_statements'" > /work/restored-view-owner
test "$(cat /work/restored-view-owner)" = fixture_extension_owner
echo RECORDED_EXTENSION_VIEW_OWNERSHIP_PASSED
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(column_name ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='fabricated_fixture'" > /work/restored-column-order
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT array_agg(ordinal_position ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='fabricated_fixture'" > /work/restored-column-numbers
cmp /work/source-column-order /work/restored-column-order
if cmp -s /work/source-column-numbers /work/restored-column-numbers; then exit 23; fi
echo LIVE_COLUMN_ORDER_WITH_DROPPED_ATTRIBUTE_GAPS_PASSED
psql -X -At -v ON_ERROR_STOP=1 -c "SELECT count(*)||':'||md5(string_agg(row_to_json(t)::text,'|' ORDER BY id)) FROM public.fabricated_fixture t" > /work/restored-digest
cmp /work/source-digest /work/restored-digest
test "$(psql -X -At -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM pg_extension WHERE (extname,extversion) IN (('plpgsql','1.0'),('pgcrypto','1.3'),('uuid-ossp','1.1'),('pg_stat_statements','1.11'),('supabase_vault','0.3.1'))")" = 5
test "$(psql -X -At -v ON_ERROR_STOP=1 -c 'SELECT count(*) FROM vault.secrets')" = 0
pg_ctl -D /work/restore -m fast -w -t 10 stop > /work/control.log 2>&1
pg_checksums --check -D /work/restore > /work/checksums.log 2>&1
echo SYNTHETIC_RESTORE_DIGEST_EXTENSIONS_AND_CHECKSUMS_PASSED
"""


def main():
    env = {k: os.environ[k] for k in (
        "SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP"
    ) if k in os.environ}
    base = [CLI, "--config", str(ROOT / "docker-feasibility-cli"),
            "--host", "npipe:////./pipe/dockerDesktopLinuxEngine"]

    def docker(args, timeout=10):
        return subprocess.run(base + args, env=env, capture_output=True, text=True,
                              timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)

    image = docker(["image", "inspect", IMAGE, "--format", "{{json .}}"])
    if image.returncode:
        raise RuntimeError("Pinned image unavailable; this checker never pulls images")
    metadata = json.loads(image.stdout)
    if metadata["Os"] != "linux" or metadata["Architecture"] != "amd64":
        raise RuntimeError("Unexpected image platform")
    if metadata["Config"].get("Volumes"):
        raise RuntimeError("Declared persistent image volumes require separate review")
    name = "priceyard-fabricated-ram-" + uuid.uuid4().hex[:10]
    create = docker([
        "container", "create", "--pull=never", "--name", name,
        "--label", "purpose=priceyard-synthetic-ram-fixture", "--network=none",
        "--read-only", "--user=postgres", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--log-driver=none", "--no-healthcheck",
        "--memory=512m", "--memory-swap=512m", "--cpus=1", "--pids-limit=64",
        "--shm-size=16m", "--ulimit=core=0", "--stop-signal=SIGTERM",
        "--tmpfs=/work:rw,noexec,nosuid,nodev,size=268435456,mode=1777",
        "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=8388608,mode=1777",
        "--entrypoint=/bin/sh", IMAGE, "-c", SCRIPT,
    ])
    if create.returncode:
        (ROOT / "ram-fixture-create-private.log").write_text(create.stderr, encoding="utf-8")
        raise RuntimeError("Fabricated container creation failed; no backup was opened")
    result = {"synthetic_only": True, "production_access": False,
              "real_backup_opened": False, "image": IMAGE, "status": "failed"}
    try:
        inspection = docker(["container", "inspect", name, "--format", "{{json .}}"])
        if inspection.returncode:
            raise RuntimeError("Container inspection unavailable; no execution")
        info = json.loads(inspection.stdout)
        host = info["HostConfig"]
        expected = (
            host["NetworkMode"] == "none" and host["ReadonlyRootfs"]
            and host["Memory"] == MEMORY and host["MemorySwap"] == MEMORY
            and host["NanoCpus"] == 1_000_000_000 and host["PidsLimit"] == 64
            and host["LogConfig"]["Type"] == "none" and not host["Privileged"]
            and not host.get("Binds") and not host.get("VolumesFrom")
            and "ALL" in host["CapDrop"]
            and "no-new-privileges" in host["SecurityOpt"]
            and info["Config"]["User"] == "postgres"
            and {m["Type"] for m in info.get("Mounts", [])} <= {"tmpfs"}
            and set(host["Tmpfs"]) == {"/work", "/tmp"}
        )
        if not expected:
            raise RuntimeError("Container isolation guards differ; no execution")
        result["docker_configuration_guards"] = "passed"
        completed = docker(["container", "start", "--attach", name], timeout=100)
        (ROOT / "ram-fixture-execution-private.log").write_text(
            completed.stdout + "\n" + completed.stderr, encoding="utf-8")
        expected_markers = ["RAM_SWAP_ROOT_AND_NETWORK_GUARDS_PASSED",
                            "NATIVE_CHECK_CONSTRAINT_CAST_PARSER_AND_ENFORCEMENT_PASSED",
                            "RECORDED_PRELOAD_LIBRARIES_AND_SAFEUPDATE_GUARD_PASSED",
                            "EXACT_EXTENSION_VERSIONS_AND_LOCALE_PASSED",
                            "BOOTSTRAP_AND_EXPLICIT_GRANTOR_RESTORE_PASSED",
                            "RECORDED_SCHEMA_PRIVILEGES_AND_GRANT_OPTION_PASSED",
                            "RECORDED_EXTENSION_VIEW_OWNERSHIP_PASSED",
                            "LIVE_COLUMN_ORDER_WITH_DROPPED_ATTRIBUTE_GAPS_PASSED",
                            "SYNTHETIC_RESTORE_DIGEST_EXTENSIONS_AND_CHECKSUMS_PASSED"]
        result["checks"] = {marker: marker in completed.stdout for marker in expected_markers}
        if completed.returncode or not all(result["checks"].values()):
            raise RuntimeError("Synthetic target check failed; protected actual restore remains forbidden")
        result["status"] = "passed"
    finally:
        docker(["container", "stop", "--time=5", name], timeout=10)
        removed = docker(["container", "rm", name])
        result["test_container_removed"] = removed.returncode == 0
        (ROOT / "ram-fixture-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
