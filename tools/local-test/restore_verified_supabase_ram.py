"""One reviewed real restore, pinned local Docker RAM only; never connects to source."""
import ast,ctypes,hashlib,json,os,re,subprocess,time,uuid
from pathlib import Path
ROOT=Path(r'C:\Users\HP\AppData\Local\PriceYardPrivateBackup')
IMAGE='supabase/postgres@sha256:5a4314708484bec672de2c09653a5c01fb1c84a998564ac231b0325e2238ed5b'
CLI=r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
OPERATOR='supabase_admin'
SCHEMA_SHA='4a9f97d2e7225ab0f974953043ad931d97ab197f619ba1610e0e805aafc369ff'
ROLES_SHA='71b786e11bc897be1be4980ff386e488f6e2b547e6a0c68e8293bfb37e77e355'
CATALOG = "\nSELECT jsonb_build_object(\n'roles',(SELECT jsonb_agg(jsonb_build_array(rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconfig) ORDER BY rolname) FROM pg_roles WHERE rolname !~ '^pg_'),\n'role_memberships',(SELECT jsonb_agg(jsonb_build_array(r.rolname,m.rolname,a.admin_option,a.inherit_option,a.set_option) ORDER BY r.rolname,m.rolname) FROM pg_auth_members a JOIN pg_roles r ON r.oid=a.roleid JOIN pg_roles m ON m.oid=a.member),\n'database',(SELECT jsonb_build_object('name',datname,'owner',pg_get_userbyid(datdba),'encoding',pg_encoding_to_char(encoding),'collate',datcollate,'ctype',datctype,'acl',datacl::text) FROM pg_database WHERE datname=current_database()),\n'database_role_settings',(SELECT jsonb_agg(jsonb_build_array(COALESCE(d.datname,''),COALESCE(r.rolname,''),s.setconfig) ORDER BY s.setdatabase,s.setrole) FROM pg_db_role_setting s LEFT JOIN pg_database d ON d.oid=s.setdatabase LEFT JOIN pg_roles r ON r.oid=s.setrole WHERE s.setdatabase IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))),\n'tablespaces',(SELECT jsonb_agg(jsonb_build_array(spcname,pg_get_userbyid(spcowner),spcacl::text,spcoptions) ORDER BY spcname) FROM pg_tablespace),\n'extensions',(SELECT jsonb_agg(jsonb_build_object('name',e.extname,'version',e.extversion,'schema',n.nspname) ORDER BY e.extname) FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace),\n'schemas',(SELECT jsonb_agg(jsonb_build_array(nspname,pg_get_userbyid(nspowner),nspacl::text) ORDER BY nspname) FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname <> 'information_schema'),\n'relations',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,c.relkind,c.relrowsecurity,c.relforcerowsecurity,pg_get_userbyid(c.relowner),c.relacl::text) ORDER BY n.nspname,c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'),\n'columns',(SELECT jsonb_agg(jsonb_build_array(table_schema,table_name,column_name,ordinal_position,data_type,udt_name,is_nullable,column_default) ORDER BY table_schema,table_name,ordinal_position) FROM information_schema.columns WHERE table_schema !~ '^pg_' AND table_schema <> 'information_schema'),\n'constraints',(SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,co.conname,co.contype,co.convalidated,pg_get_constraintdef(co.oid)) ORDER BY n.nspname,c.relname,co.conname) FROM pg_constraint co JOIN pg_class c ON c.oid=co.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'),\n'indexes',(SELECT jsonb_agg(jsonb_build_array(schemaname,tablename,indexname,indexdef) ORDER BY schemaname,tablename,indexname) FROM pg_indexes WHERE schemaname !~ '^pg_' AND schemaname <> 'information_schema'),\n'functions',(SELECT jsonb_agg(jsonb_build_array(n.nspname,p.proname,l.lanname,p.prosecdef) ORDER BY n.nspname,p.proname,p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_language l ON l.oid=p.prolang WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'),\n'foreign_servers',(SELECT jsonb_agg(srvname ORDER BY srvname) FROM pg_foreign_server),\n'publications',(SELECT jsonb_agg(pubname ORDER BY pubname) FROM pg_publication),\n'subscriptions',(SELECT jsonb_agg(jsonb_build_array(subname,subenabled) ORDER BY subname) FROM pg_subscription),\n'policies',(SELECT jsonb_agg(to_jsonb(p) ORDER BY schemaname,tablename,policyname) FROM pg_policies p WHERE schemaname !~ '^pg_' AND schemaname <> 'information_schema'))\n"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def protected(p):
 from ctypes import wintypes
 f=ctypes.WinDLL('kernel32',use_last_error=True).GetFileAttributesW
 f.argtypes=[wintypes.LPCWSTR];f.restype=wintypes.DWORD
 a=f(str(p))
 if a==0xffffffff or a&0x400 or not a&0x4000:raise RuntimeError('Missing EFS/no-reparse protection')
def main():
 status=json.loads((ROOT/'latest-production-backup-status.json').read_text())
 if status.get('database_restoration_verified'):raise RuntimeError('Already verified; no repeat restoration')
 run=Path(status['protected_run_path']);bundle=run/'recovered-copy'
 if run.parent!=ROOT/'PrivateRestoreEfs' or run.name!='supabase-backup-20261019T213738Z':raise RuntimeError('Unexpected source bundle path')
 protected(run);protected(bundle)
 expected=json.loads((bundle/'file-digests.json').read_text())
 for filename,sha in expected.items():
  if Path(filename).name!=filename:raise RuntimeError('Invalid bundle filename')
  protected(bundle/filename)
  if digest(bundle/filename)!=sha:raise RuntimeError('Bundle hash differs')
 if expected['schema-review-private.sql']!=SCHEMA_SHA or expected['roles.sql']!=ROLES_SHA:raise RuntimeError('Reviewed SQL hash differs')
 if digest(Path(status['archive_path']))!=status['archive_sha256']:raise RuntimeError('Portable archive differs')
 catalog=json.loads((bundle/'catalog-private.json').read_text());manifest=json.loads((bundle/'manifest-private.json').read_text())
 if manifest['source_host']!='db.lrvpjfbtmftjkzaxbunk.supabase.co' or manifest['source_user']!='postgres' or manifest['revision']!='0021_feedback_screenshot' or manifest['tls']!='verify-full' or manifest['source_transaction_read_only'] is not True:raise RuntimeError('Unexpected source identity')
 required={'plpgsql':'1.0','pgcrypto':'1.3','uuid-ossp':'1.1','pg_stat_statements':'1.11','supabase_vault':'0.3.1'}
 if {e['name']:e['version'] for e in catalog['extensions']}!=required:raise RuntimeError('Unreviewed extensions')
 if any(catalog.get(k) for k in ('foreign_servers','subscriptions')) or any(t[0] not in ('pg_default','pg_global') for t in catalog['tablespaces']):raise RuntimeError('Unreviewed external objects')
 if any(t['rows'] for t in manifest['tables'] if t['schema']=='vault'):raise RuntimeError('Vault key coverage required')
 if not any(r[0]==OPERATOR and r[1] is True for r in catalog['roles']):raise RuntimeError('Reviewed original bootstrap administrator unavailable')
 if {f[2] for f in catalog['functions']}!={'sql','plpgsql','c'}:raise RuntimeError('Unreviewed procedural language')
 for key,value in [('encoding','UTF8'),('collate','en_US.UTF-8'),('ctype','en_US.UTF-8')]:
  if catalog['database'][key]!=value:raise RuntimeError('Unreviewed locale')
 sql_review=json.loads((run/'sql-review-summary-private.json').read_text())
 if sql_review['schema_sha256']!=SCHEMA_SHA or sql_review['roles_sha256']!=ROLES_SHA or any(sql_review['sensitive_command_presence'].values()):raise RuntimeError('Executable SQL review differs')
 fixture=json.loads((ROOT/'ram-fixture-result.json').read_text())
 if fixture['status']!='passed' or fixture['image']!=IMAGE or not all(fixture['checks'].values()):raise RuntimeError('Matching synthetic target proof unavailable')
 query=CATALOG
 env={k:os.environ[k] for k in ('SYSTEMROOT','WINDIR','USERPROFILE','APPDATA','LOCALAPPDATA','TEMP','TMP') if k in os.environ}
 base=[CLI,'--config',str(ROOT/'docker-feasibility-cli'),'--host','npipe:////./pipe/dockerDesktopLinuxEngine']
 def docker(args,input=None,timeout=15):
  p=subprocess.run(base+args,input=input,env=env,capture_output=True,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
  if p.returncode:
   path=run/'ram-restore-command-error-private.log';path.write_bytes(p.stdout+b'\n'+p.stderr);protected(path)
   raise RuntimeError('Local restore command failed; error retained only in EFS')
  return p.stdout
 name='priceyard-private-ram-'+uuid.uuid4().hex[:10]
 image=json.loads(docker(['image','inspect',IMAGE,'--format','{{json .}}']))
 if image['Config'].get('Volumes') or image['Os']!='linux' or image['Architecture']!='amd64':raise RuntimeError('Image isolation profile differs')
 docker(['container','create','--pull=never','--name',name,'--label','purpose=priceyard-approved-private-restore','--network=none','--read-only','--user=postgres','--cap-drop=ALL','--security-opt=no-new-privileges','--log-driver=none','--no-healthcheck','--memory=512m','--memory-swap=512m','--cpus=1','--pids-limit=64','--shm-size=16m','--ulimit=core=0','--stop-signal=SIGTERM','--tmpfs=/work:rw,noexec,nosuid,nodev,size=268435456,mode=1777','--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=8388608,mode=1777','--entrypoint=/bin/sh',IMAGE,'-c','umask 077; exec sleep 900'])
 result={'status':'failed','production_connection':False,'production_changes':False,'migrations_run':0,'image':IMAGE,'real_restore_started':False,'database_restoration_verified':False}
 started=time.monotonic()
 def execute(args,input=None,timeout=15):return docker(['exec','--interactive',name,*args],input,timeout)
 def shell(text,timeout=20):return execute(['/bin/sh','-c',text],timeout=timeout)
 def psql(statement,database='postgres',readonly=True):
  options='-c timezone=UTC -c datestyle=ISO -c extra_float_digits=3 -c bytea_output=hex -c row_security=off -c default_transaction_read_only='+('on' if readonly else 'off')
  return docker(['exec','--interactive','--env','PGOPTIONS='+options,name,'psql','-X','-q','-At','-v','ON_ERROR_STOP=1','-h','/work/socket','-U',('postgres' if readonly and database=='postgres' and result.get('data_restore_finished') else OPERATOR),'-d',database],statement.encode('utf-8'))
 def ident(value):return '"'+value.replace('"','""')+'"'

 def literal(value):return "'"+value.replace("'","''")+"'"
 acl_cache={}
 def acl_rows(owner,value,kind):
  key=(owner,value,kind)
  if key not in acl_cache:
   raw='NULL' if value is None else literal(value)+'::aclitem[]'
   sql="SELECT COALESCE(jsonb_agg(jsonb_build_array(pg_get_userbyid(grantor),CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END,privilege_type,is_grantable) ORDER BY pg_get_userbyid(grantor),grantee,privilege_type,is_grantable),'[]'::jsonb) FROM aclexplode(COALESCE("+raw+",acldefault("+literal(kind)+'::"char",(SELECT oid FROM pg_roles WHERE rolname='+literal(owner)+"))));"
   acl_cache[key]=json.loads(psql(sql))
  return acl_cache[key]
 def acl_objects(data):
  objects={}
  for row in data['schemas']:
   objects[('schema',row[0])]=('SCHEMA '+ident(row[0]),row[1],row[2],'n')
  for row in data['relations']:
   kind=row[2]
   if kind in ('r','p','v','m','f','S'):
    objects[('relation',row[0],row[1])]=(('SEQUENCE ' if kind=='S' else 'TABLE ')+ident(row[0])+'.'+ident(row[1]),row[5],row[6],'S' if kind=='S' else 'r')
  db=data['database'];objects[('database',db['name'])]=('DATABASE '+ident(db['name']),db['owner'],db['acl'],'d')
  return objects

 def restore_recorded_extension_views(observed):
  actual={(row[0],row[1]):row for row in observed['relations']};restored=0
  allowed={('extensions','pg_stat_statements'),('extensions','pg_stat_statements_info')}
  for row in catalog['relations']:
   current=actual.get((row[0],row[1]))
   if current is None or current[5]==row[5]:continue
   if (row[0],row[1]) not in allowed or row[2]!='v' or current[2]!='v' or row[5]!='postgres' or current[5]!='supabase_admin':raise RuntimeError('Unreviewed object ownership difference')
   object_name=ident(row[0])+'.'+ident(row[1])
   belongs=psql("SELECT EXISTS(SELECT 1 FROM pg_depend d JOIN pg_extension e ON e.oid=d.refobjid WHERE d.classid='pg_class'::regclass AND d.refclassid='pg_extension'::regclass AND d.objid="+literal(object_name)+"::regclass AND d.deptype='e' AND e.extname='pg_stat_statements');").strip()
   if belongs!=b't':raise RuntimeError('Object is not a reviewed extension-owned view')
   psql('ALTER VIEW '+object_name+' OWNER TO '+ident(row[5])+';',readonly=False);restored+=1
  return restored
 def restore_recorded_acls(observed):
  expected_objects=acl_objects(catalog);actual_objects=acl_objects(observed);changed=0
  permissions={'CREATE','USAGE','CONNECT','TEMPORARY','SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN'}
  for key,(object_sql,owner,expected_acl,kind) in expected_objects.items():
   if key not in actual_objects or actual_objects[key][1]!=owner:raise RuntimeError('Original ownership differs; no automatic ownership change')
   actual_acl=actual_objects[key][2]
   if expected_acl==actual_acl:continue
   wanted=acl_rows(owner,expected_acl,kind);current=acl_rows(owner,actual_acl,kind)
   if wanted==current:continue
   if any(row[0]!=owner or row[2] not in permissions for row in wanted):raise RuntimeError('Original chained privileges require separate review')
   statements=['BEGIN; SET LOCAL ROLE '+ident(owner)+';']
   grantees={row[1] for row in current}|{'PUBLIC',owner}
   for grantee in sorted(grantees):statements.append('REVOKE ALL PRIVILEGES ON '+object_sql+' FROM '+('PUBLIC' if grantee=='PUBLIC' else ident(grantee))+';')
   for grantor,grantee,privilege,grantable in wanted:
    statements.append('GRANT '+privilege+' ON '+object_sql+' TO '+('PUBLIC' if grantee=='PUBLIC' else ident(grantee))+(' WITH GRANT OPTION' if grantable else '')+';')
   statements.append('COMMIT;');psql('\n'.join(statements),readonly=False);changed+=1
  return changed

 def parse_recorded_check_constraints(expected,actual):
  actual_by_key={tuple(row[:3]):row for row in actual['constraints']};parsed=0
  for row in expected['constraints']:
   observed=actual_by_key.get(tuple(row[:3]))
   if observed is None or row[:5]!=observed[:5] or row[5]==observed[5]:continue
   if row[0]!='public' or row[3]!='c' or row[4] is not True:raise RuntimeError('Unreviewed constraint representation difference')
   probe='py_snapshot_check_'+uuid.uuid4().hex[:10]
   sql='BEGIN; CREATE TEMP TABLE '+ident(probe)+' (LIKE '+ident(row[0])+'.'+ident(row[1])+') ON COMMIT DROP; ALTER TABLE pg_temp.'+ident(probe)+' ADD CONSTRAINT snapshot_check '+row[5]+'; SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='+literal('pg_temp.'+ident(probe))+"::regclass AND conname='snapshot_check'; COMMIT;"
   row[5]=psql(sql,readonly=False).decode('utf-8').strip();parsed+=1
  return parsed
 def comparable(data):
  value=json.loads(json.dumps(data))
  ranks={}
  for row in value['columns']:
   key=(row[0],row[1]);ranks[key]=ranks.get(key,0)+1;row[3]=ranks[key]
  for row in value['schemas']:row[2]=acl_rows(row[1],row[2],'n')
  for row in value['relations']:
   if row[2] in ('r','p','v','m','f','S'):row[6]=acl_rows(row[5],row[6],'S' if row[2]=='S' else 'r')
  db=value['database'];db['acl']=acl_rows(db['owner'],db['acl'],'d')
  value['database_role_settings']=sorted([[db,role,sorted(settings or [])] for db,role,settings in value.get('database_role_settings') or []],key=lambda row:(row[0],row[1]))
  return value
 try:
  info=json.loads(docker(['container','inspect',name,'--format','{{json .}}']));h=info['HostConfig']
  if not (h['NetworkMode']=='none' and h['ReadonlyRootfs'] and h['Memory']==536870912 and h['MemorySwap']==536870912 and h['NanoCpus']==1000000000 and h['PidsLimit']==64 and h['LogConfig']['Type']=='none' and not h['Privileged'] and not h.get('Binds') and not h.get('VolumesFrom') and 'ALL' in h['CapDrop'] and 'no-new-privileges' in h['SecurityOpt'] and info['Config']['User']=='postgres' and {m['Type'] for m in info.get('Mounts',[])}<={'tmpfs'} and set(h['Tmpfs'])=={'/work','/tmp'}):raise RuntimeError('Container isolation differs before execution')
  docker(['container','start',name])
  shell("set -eu; umask 077; test \"$(id -un)\" = postgres || { echo USER_GUARD_FAILED >&2; exit 1; }; test \"$(stat -f -c %T /work)\" = tmpfs || { echo TMPFS_GUARD_FAILED >&2; exit 1; }; test \"$(cat /sys/fs/cgroup/memory.max)\" = 536870912 || { echo MEMORY_GUARD_FAILED >&2; exit 1; }; test \"$(cat /sys/fs/cgroup/memory.swap.max)\" = 0 || { echo CGROUP_SWAP_GUARD_FAILED >&2; exit 1; }; test \"$(awk 'END {print NR}' /proc/swaps)\" = 1 || { echo VM_SWAP_GUARD_FAILED >&2; exit 1; }; test \"$(awk 'END {print NR}' /proc/net/route)\" = 1 || { echo NETWORK_GUARD_FAILED >&2; exit 1; }; mkdir -m 700 /work/input /work/socket")
  shell("set -eu; umask 077; initdb -D /work/cluster -U "+OPERATOR+" -A trust --locale=en_US.UTF-8 --encoding=UTF8 --data-checksums > /work/init.log 2>&1; printf \"\\nlisten_addresses=''\\nunix_socket_directories='/work/socket'\\nshared_buffers='16MB'\\nwork_mem='1MB'\\nmaintenance_work_mem='16MB'\\nmax_connections=8\\nmax_worker_processes=0\\nmax_wal_senders=0\\nmax_replication_slots=0\\nshared_preload_libraries='pg_stat_statements'\\nlog_statement='none'\\nlog_min_messages='fatal'\\ntimezone='UTC'\\n\" >> /work/cluster/postgresql.conf; pg_ctl -D /work/cluster -l /work/server.log -w -t 15 start > /work/control.log 2>&1")
  if psql("LOAD 'supautils'; LOAD 'safeupdate'; SELECT 1;",database='template1',readonly=False).strip()!=b'1':raise RuntimeError('Required server library runtime loading failed before data transfer')
  result['runtime_storage_network_swap_guards']='passed'
  for filename in ('database.dump','roles.sql'):
   execute(['/bin/sh','-c','umask 077; cat > /work/input/'+filename],(bundle/filename).read_bytes())
   observed=shell('sha256sum /work/input/'+filename).decode().split()[0]
   if observed!=expected[filename]:raise RuntimeError('Uploaded file digest differs')
  roles_sql=(bundle/'roles.sql').read_text(encoding='utf-8')
  pattern=r'(?m)^CREATE ROLE (?:supabase_admin|"supabase_admin");\r?\n'
  if len(re.findall(pattern,roles_sql))!=1:raise RuntimeError('Expected one verified existing-bootstrap CREATE statement')
  replay_roles=re.sub(pattern,'-- Original bootstrap role already initialized; all attributes/grants follow unchanged.\n',roles_sql)
  psql(replay_roles,database='template1',readonly=False)
  result['original_bootstrap_identity_preserved']=True
  result['only_existing_bootstrap_create_omitted']=True
  # Only this freshly initialized, source-free container's empty default database.
  if psql("SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='postgres';",database='template1').strip()!=OPERATOR.encode():raise RuntimeError('Empty default database is not controller-owned')
  if psql("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r';").strip()!=b'0':raise RuntimeError('Default database is not empty')
  execute(['dropdb','--no-password','-h','/work/socket','-U',OPERATOR,'postgres'])
  result['real_restore_started']=True
  print('RESTORING_REVIEWED_BACKUP_IN_NETWORK_DISABLED_RAM_ONLY_TARGET',flush=True)
  execute(['pg_restore','--no-password','--exit-on-error','--create','--host=/work/socket','--username='+OPERATOR,'--dbname=template1','/work/input/database.dump'],timeout=75)
  result['data_restore_finished']=True
  after=json.loads(psql(query+';'))
  result['recorded_extension_view_owners_replayed']=restore_recorded_extension_views(after)
  after=json.loads(psql(query+';'))
  result['recorded_acl_objects_replayed']=restore_recorded_acls(after)
  after=json.loads(psql(query+';'))
  after_path=run/'ram-restored-catalog-private.json';after_path.write_text(json.dumps(after,indent=2),encoding='utf-8');protected(after_path)
  compared_after=comparable(after);compared_source=comparable(catalog)
  result['recorded_check_constraints_parser_canonicalized']=parse_recorded_check_constraints(compared_source,compared_after)
  for key in ('schemas','relations','columns','constraints','indexes','functions','extensions','policies','publications','subscriptions','foreign_servers','tablespaces'):
   if compared_after.get(key)!=compared_source.get(key):raise RuntimeError('Restored catalog differs: '+key)
  if compared_after['database']!=compared_source['database']:raise RuntimeError('Restored database attributes/grants differ')
  if compared_after.get('database_role_settings')!=compared_source.get('database_role_settings'):raise RuntimeError('Restored database/role settings differ')
  roles_after={r[0]:r for r in after.get('roles') or []}
  for role in catalog['roles']:
   if roles_after.get(role[0])!=role:raise RuntimeError('Restored role attributes differ')
  members=after.get('role_memberships') or []
  if members!=(catalog.get('role_memberships') or []):raise RuntimeError('Restored role memberships differ')
  checked=0
  for table in manifest['tables']:
   table_sql=ident(table['schema'])+'.'+ident(table['table'])
   if int(psql('SELECT count(*) FROM ONLY '+table_sql+';'))!=table['rows']:raise RuntimeError('Restored row count differs')
   payload=psql('COPY (SELECT to_jsonb(t)::text FROM ONLY '+table_sql+' t ORDER BY to_jsonb(t)::text COLLATE "C") TO STDOUT (FORMAT binary);')
   if hashlib.sha256(payload).hexdigest()!=table['copy_json_sha256']:raise RuntimeError('Restored row digest differs')
   del payload;checked+=1
  sequences=json.loads(psql("SELECT COALESCE(json_agg(row_to_json(t)),'[]'::json) FROM (SELECT schemaname,sequencename,last_value,increment_by,start_value,min_value,max_value,cycle FROM pg_sequences WHERE schemaname !~ '^pg_' ORDER BY schemaname,sequencename) t;"))
  if [list(s.values()) for s in sequences]!=manifest['sequence_observations_non_mvcc']:raise RuntimeError('Sequence observations differ; no automatic adjustment')
  large=json.loads(psql("SELECT COALESCE(json_agg(row_to_json(t)),'[]'::json) FROM (SELECT oid,octet_length(lo_get(oid)) AS bytes,encode(sha256(lo_get(oid)),'hex') AS digest FROM pg_largeobject_metadata ORDER BY oid) t;"))
  if [list(o.values()) for o in large]!=manifest['large_objects']:raise RuntimeError('Large objects differ')
  if psql('SELECT version_num FROM public.alembic_version;').strip()!=b'0021_feedback_screenshot':raise RuntimeError('Restored migration revision differs')
  shell('pg_ctl -D /work/cluster -m fast -w -t 15 stop > /work/control.log 2>&1; pg_checksums --check -D /work/cluster > /work/checksums.log 2>&1')
  result.update(status='passed',database_restoration_verified=True,tables_checked=checked,all_table_counts_and_digests_match=True,catalog_roles_memberships_settings_and_permissions_match=True,sequences_and_large_objects_match=True,native_checksums_passed=True,original_revision_unchanged=True,portable_archive_sha256=status['archive_sha256'],duration_seconds=round(time.monotonic()-started,1))
 except Exception as exc:
  result['failure']=str(exc)
  raise
 finally:
  docker(['container','stop','--time=5',name],timeout=10)
  docker(['container','rm',name])
  result['ram_container_removed']=True
  report=run/'real-ram-restore-result-private.json';report.write_text(json.dumps(result,indent=2),encoding='utf-8');protected(report)
 if result['status']=='passed':
  status.update(status='encrypted_backup_integrity_and_protected_restoration_passed',database_restoration_verified=True,protected_restore_report=str(run/'real-ram-restore-result-private.json'),restored_tables_verified=result['tables_checked'],migrations_run=0,deployment=False)
  (ROOT/'latest-production-backup-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  print('RESTORATION_STOPPED_SAFELY: '+str(exc),flush=True)
  raise SystemExit(1)
