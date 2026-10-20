"""Fabricated-only PG17 migration privacy checks; no backup or provider access."""
import json
import os
import subprocess
import tempfile
import uuid

from rehearse_verified_0022_ram import prepare
from rehearse_0022_checks import USER_ACCESS_SQL

CLI = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
IMAGE = "supabase/postgres@sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b"

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
mkdir /work/socket
export PGHOST=/work/socket PGUSER=fixture_owner PGDATABASE=postgres PGCONNECT_TIMEOUT=2
finish() {
  code=$?
  pg_ctl -D /work/data -m fast -w -t 5 stop >/dev/null 2>&1 || true
  if test "$code" != 0; then
    for file in /work/server.log /work/migration.log /work/rejected.log; do
      if test -f "$file"; then tail -n 6 "$file"; fi
    done
  fi
  exit "$code"
}
trap finish EXIT
case "$(postgres --version)" in *" 17."*) ;; *) exit 21 ;; esac
initdb -D /work/data -U fixture_owner -A trust --no-instructions --encoding=UTF8 --locale=en_US.UTF-8 >/dev/null
printf "\nlisten_addresses=''\nunix_socket_directories='/work/socket'\nshared_buffers='16MB'\nwork_mem='1MB'\nmaintenance_work_mem='16MB'\nmax_connections=8\nmax_worker_processes=0\nmax_wal_senders=0\nmax_replication_slots=0\nlog_statement='none'\nlog_min_messages='fatal'\n" >> /work/data/postgresql.conf
pg_ctl -D /work/data -l /work/server.log -w -t 10 start >/dev/null
cat > /work/upgrade.sql <<'MIGRATION_SQL'
__UPGRADE__
MIGRATION_SQL
cat > /work/access.sql <<'ACCESS_SQL'
SELECT (j->'effective_original_columns')::text FROM (
__ACCESS__
) snapshot(j);
ACCESS_SQL
q() { psql -X -qAt -v ON_ERROR_STOP=1 -c "$1"; }
assert_true() { test "$(q "SELECT ($1)")" = t; }
baseline() {
  createdb "$1"
  export PGDATABASE="$1"
  q "CREATE TABLE public.users(id integer PRIMARY KEY,label text NOT NULL); INSERT INTO public.users VALUES(1,'FABRICATED ONLY'); CREATE TABLE public.alembic_version(version_num varchar(32) PRIMARY KEY); INSERT INTO public.alembic_version VALUES('0021_feedback_screenshot');" >/dev/null
}
upgrade() { psql -X -q -v ON_ERROR_STOP=1 -f /work/upgrade.sql >/work/migration.log 2>&1; }
assert_baseline() {
  assert_true "(SELECT version_num='0021_feedback_screenshot' FROM alembic_version) AND (SELECT count(*)=1 AND min(label)='FABRICATED ONLY' FROM users) AND to_regclass('public.revoked_access_tokens') IS NULL AND NOT EXISTS(SELECT 1 FROM pg_attribute WHERE attrelid='public.users'::regclass AND attname='auth_version')"
}
assert_upgraded() {
  assert_true "(SELECT version_num='0022_login_revocation' FROM alembic_version) AND (SELECT count(*)=1 AND min(label)='FABRICATED ONLY' AND min(auth_version)=0 FROM users) AND (SELECT relrowsecurity FROM pg_class WHERE oid='public.revoked_access_tokens'::regclass)"
  assert_true "EXISTS(SELECT 1 FROM pg_attribute a JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE a.attrelid='public.users'::regclass AND a.attname='auth_version' AND a.atttypid='integer'::regtype AND a.attnotnull AND pg_get_expr(d.adbin,d.adrelid)='0')"
}
baseline fresh
assert_true "NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN('anon','authenticated','service_role'))"
upgrade
assert_upgraded
echo FRESH_MIGRATION_PASSED
q "CREATE ROLE anon NOLOGIN; CREATE ROLE authenticated NOLOGIN; CREATE ROLE service_role NOLOGIN;" >/dev/null
baseline default_acl
q "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon,authenticated,service_role; GRANT ALL ON public.users TO anon,authenticated,service_role; GRANT UPDATE(label) ON public.users TO anon WITH GRANT OPTION;" >/dev/null
psql -X -qAt -v ON_ERROR_STOP=1 -f /work/access.sql > /work/before
upgrade
assert_upgraded
psql -X -qAt -v ON_ERROR_STOP=1 -f /work/access.sql > /work/after
cmp /work/before /work/after
assert_true "NOT EXISTS(SELECT 1 FROM pg_roles r WHERE r.rolname IN('anon','authenticated') AND has_column_privilege(r.oid,'public.users','auth_version','UPDATE'))"
assert_true "NOT EXISTS(SELECT 1 FROM pg_roles r CROSS JOIN (VALUES('SELECT'),('INSERT'),('UPDATE'),('DELETE'),('TRUNCATE'),('REFERENCES'),('TRIGGER'),('MAINTAIN')) p(privilege) WHERE r.rolname IN('anon','authenticated') AND has_table_privilege(r.oid,'public.revoked_access_tokens',p.privilege))"
assert_true "has_column_privilege('anon','public.users','label','UPDATE WITH GRANT OPTION') AND NOT has_column_privilege('anon','public.users','id','UPDATE WITH GRANT OPTION')"
q "UPDATE public.users SET auth_version=auth_version+1 WHERE id=1; INSERT INTO public.revoked_access_tokens VALUES(repeat('a',64),1,now()+interval '1 hour',now());" >/dev/null
assert_true "(SELECT count(*)=1 FROM revoked_access_tokens) AND (SELECT auth_version=1 FROM users WHERE id=1)"
if q "SET ROLE anon; SELECT * FROM public.revoked_access_tokens;" >/work/rejected.log 2>&1; then exit 22; fi
grep -q 'permission denied' /work/rejected.log
echo DEFAULT_ACL_PRIVACY_AND_ORIGINAL_ACCESS_PASSED
baseline inherited_update
q "CREATE ROLE fixture_inherited NOLOGIN; GRANT fixture_inherited TO anon; GRANT UPDATE ON public.users TO fixture_inherited;" >/dev/null
if upgrade; then exit 23; fi
grep -q 'Inherited account security counter UPDATE requires separate review' /work/migration.log
assert_baseline
echo INHERITED_UPDATE_ATOMIC_REFUSAL_PASSED
baseline dependent_grant
q "CREATE ROLE fixture_dependent NOLOGIN; GRANT UPDATE ON public.users TO anon WITH GRANT OPTION; SET ROLE anon; GRANT UPDATE(label) ON public.users TO fixture_dependent; RESET ROLE;" >/dev/null
if upgrade; then exit 24; fi
grep -q 'Dependent account UPDATE grants require separate review' /work/migration.log
assert_baseline
echo DEPENDENT_GRANT_ATOMIC_REFUSAL_PASSED
"""


def main():
    upgrade_sql, migration_sha = prepare()
    script = SCRIPT.replace("__UPGRADE__", upgrade_sql).replace("__ACCESS__", USER_ACCESS_SQL.strip().rstrip(";"))
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP") if key in os.environ}
    name = "priceyard-0022-fabricated-" + uuid.uuid4().hex[:10]
    result = {"status": "failed", "synthetic_only": True, "customer_records_read": 0, "production_connections": 0, "migration_sha256": migration_sha}
    with tempfile.TemporaryDirectory(prefix="priceyard-empty-docker-config-") as config:
        base = [CLI, "--config", config, "--host", "npipe:////./pipe/dockerDesktopLinuxEngine"]

        def docker(args, timeout=8, payload=None):
            completed = subprocess.run(base + args, env=env, input=None if payload is None else payload.encode("utf-8"), capture_output=True, timeout=timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            completed.stdout = completed.stdout.decode("utf-8", errors="replace")
            completed.stderr = completed.stderr.decode("utf-8", errors="replace")
            return completed

        image = docker(["image", "inspect", IMAGE, "--format", "{{json .}}"])
        if image.returncode:
            raise RuntimeError("Pinned cached image unavailable; no image download attempted")
        meta = json.loads(image.stdout)
        if meta["Os"] != "linux" or meta["Architecture"] != "amd64" or meta["Config"].get("Volumes"):
            raise RuntimeError("Pinned image platform or volumes differ")
        created = docker(["container", "create", "--pull=never", "--rm", "--interactive", "--name", name,
                          "--label", "purpose=priceyard-fabricated-0022-privacy", "--network=none", "--read-only", "--user=postgres", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--log-driver=none", "--no-healthcheck", "--memory=512m", "--memory-swap=512m", "--cpus=1", "--pids-limit=64", "--shm-size=16m", "--ulimit=core=0", "--tmpfs=/work:rw,noexec,nosuid,nodev,size=268435456,mode=1777", "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=8388608,mode=1777", "--entrypoint=/bin/sh", IMAGE, "-s"])
        if created.returncode:
            raise RuntimeError("Synthetic container creation failed")
        try:
            inspected = docker(["container", "inspect", name, "--format", "{{json .}}"])
            info = json.loads(inspected.stdout)
            host = info["HostConfig"]
            if not (host["NetworkMode"] == "none" and host["ReadonlyRootfs"] and host["Memory"] == host["MemorySwap"] == 536870912 and host["NanoCpus"] == 1_000_000_000 and host["PidsLimit"] == 64 and host["LogConfig"]["Type"] == "none" and host["AutoRemove"] and not host["Privileged"] and not host.get("Binds") and not host.get("VolumesFrom") and not host.get("PortBindings") and "ALL" in host["CapDrop"] and "no-new-privileges" in host["SecurityOpt"] and info["Config"]["User"] == "postgres" and {m["Type"] for m in info.get("Mounts", [])} <= {"tmpfs"} and set(host["Tmpfs"]) == {"/work", "/tmp"}):
                raise RuntimeError("Synthetic container isolation differs")
            completed = docker(["container", "start", "--attach", "--interactive", name], timeout=30, payload=script)
            markers = ("FRESH_MIGRATION_PASSED", "DEFAULT_ACL_PRIVACY_AND_ORIGINAL_ACCESS_PASSED", "INHERITED_UPDATE_ATOMIC_REFUSAL_PASSED", "DEPENDENT_GRANT_ATOMIC_REFUSAL_PASSED")
            result["checks"] = {marker: marker in completed.stdout for marker in markers}
            if completed.returncode or not all(result["checks"].values()):
                print(completed.stdout + completed.stderr)
                raise RuntimeError("Fabricated migration privacy check failed")
            result["status"] = "passed"
        finally:
            existing = docker(["container", "inspect", name, "--format", "{{.Name}}"])
            if existing.returncode == 0:
                docker(["container", "rm", "--force", name])
            absent = docker(["container", "inspect", name, "--format", "{{.Name}}"])
            result["test_container_removed"] = absent.returncode != 0
        if not result["test_container_removed"]:
            raise RuntimeError("Synthetic container cleanup must be reviewed")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
