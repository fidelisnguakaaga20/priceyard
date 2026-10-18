"""Fixed synthetic restore controller; never imports app/settings or accepts URLs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

import psycopg
from psycopg import sql

LAB=Path(__file__).resolve().parent
DATA=(LAB/'runtime/postgres-paging-20261018').resolve()
SOURCE='priceyard_isolated_test'
TARGET='priceyard_synthetic_restore_20261018'
IDENTITY='7697910732590408300'
PURPOSE='synthetic-only-backup-recovery-20261018'
COMMENT=PURPOSE+';'+IDENTITY
MANIFEST=LAB/'runtime/synthetic-backup-fixture.json'
STATE=LAB/'runtime/synthetic-backup-state.json'


def manifest():
    value=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if (value.get('purpose')!=PURPOSE or value.get('host')!='127.0.0.1' or value.get('port')!=55449
        or value.get('system_identifier')!=IDENTITY or value.get('source_database')!=SOURCE
        or value.get('target_database')!=TARGET or not re.fullmatch('pyrev_[0-9a-f]{32}',value.get('schema',''))):
        raise RuntimeError('Unapproved recovery manifest')
    return value


def connect(database):
    if database not in {SOURCE,TARGET}:raise RuntimeError('Only the two fixed synthetic databases are permitted')
    connection=psycopg.connect(host='127.0.0.1',port=55449,dbname=database,user='priceyard_revocation_test',
        connect_timeout=3,sslmode='disable',gssencmode='disable',passfile=str(LAB/'runtime/nonexistent-synthetic-passfile'),
        options='-c statement_timeout=10000 -c lock_timeout=3000 -c timezone=UTC',autocommit=True)
    path,identity=connection.execute("SELECT current_setting('data_directory'),system_identifier::text FROM pg_control_system()").fetchone()
    if Path(path).resolve()!=DATA or identity!=IDENTITY:
        connection.close();raise RuntimeError('Live server identity differs; no mutation allowed')
    return connection


def fingerprint(connection,schema,include_shape=False):
    # Read-only consistent snapshot; emit digests/counts, never business values.
    with connection.transaction():
        connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
        names=[row[0] for row in connection.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename",(schema,))]
        tables={}
        for name in names:
            rows=connection.execute(sql.SQL('SELECT to_jsonb(t) FROM {}.{} t').format(sql.Identifier(schema),sql.Identifier(name))).fetchall()
            encoded=sorted(json.dumps(row[0],sort_keys=True,separators=(',',':'),default=str) for row in rows)
            tables[name]={'rows':len(rows),'sha256':hashlib.sha256('\n'.join(encoded).encode()).hexdigest()}
        shape={
            'columns':connection.execute("SELECT table_name,column_name,data_type,is_nullable,column_default,character_maximum_length,numeric_precision,numeric_scale,datetime_precision FROM information_schema.columns WHERE table_schema=%s ORDER BY table_name,ordinal_position",(schema,)).fetchall(),
            'indexes':connection.execute("SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname=%s ORDER BY tablename,indexname",(schema,)).fetchall(),
            'constraints':connection.execute("SELECT r.relname,c.conname,pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace WHERE n.nspname=%s ORDER BY r.relname,c.conname",(schema,)).fetchall(),
            'sequences':connection.execute("SELECT sequencename,last_value FROM pg_sequences WHERE schemaname=%s ORDER BY sequencename",(schema,)).fetchall(),
        }
        result={'tables':tables,'schema_sha256':hashlib.sha256(json.dumps(shape,default=str,sort_keys=True).encode()).hexdigest()}
        if include_shape:result['shape']=shape
        return result


def canonical_constraints(connection,schema):
    # pg_restore can move varchar->text casts from an array to its elements.
    # Compare PostgreSQL's own planned expressions, not a permissive SQL regex.
    rows=connection.execute("SELECT r.relname,c.conname,c.contype,c.convalidated,c.condeferrable,c.condeferred,c.connoinherit,pg_get_constraintdef(c.oid),pg_get_expr(c.conbin,c.conrelid) FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace WHERE n.nspname=%s ORDER BY r.relname,c.conname",(schema,)).fetchall()
    result=[]
    for table,name,kind,validated,deferrable,deferred,noinherit,definition,expression in rows:
        if kind=='c':
            statement=sql.SQL('EXPLAIN (VERBOSE, FORMAT JSON, COSTS OFF) SELECT ({}) FROM {}.{}').format(
                sql.SQL(expression),sql.Identifier(schema),sql.Identifier(table))
            definition=connection.execute(statement).fetchone()[0][0]['Plan']['Output']
        result.append((table,name,kind,validated,deferrable,deferred,noinherit,definition))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare-target','before-restore','verify','diagnose'])
    phase=parser.parse_args().phase
    # No inherited libpq service/password/environment discovery.
    for name in list(os.environ):
        if name.upper().startswith('PG'):os.environ.pop(name)
    value=manifest();schema=value['schema']
    with connect(SOURCE) as source:
        if phase=='prepare-target':
            if STATE.exists():raise RuntimeError('Existing recovery state retained; resume the next phase')
            if source.execute('SELECT 1 FROM pg_database WHERE datname=%s',(TARGET,)).fetchone():
                raise RuntimeError('Target database already exists; refusing to select or overwrite it')
            baseline=fingerprint(source,schema)
            if sum(row['rows'] for row in baseline['tables'].values())!=value['synthetic_business_rows']:
                raise RuntimeError('Unexpected fixture row count')
            source.execute(sql.SQL('CREATE DATABASE {} WITH TEMPLATE template0').format(sql.Identifier(TARGET)))
            source.execute(sql.SQL('COMMENT ON DATABASE {} IS {}').format(sql.Identifier(TARGET),sql.Literal(COMMENT)))
            with STATE.open('x',encoding='utf-8') as output:json.dump({'purpose':PURPOSE,'schema':schema,'baseline':baseline},output,indent=2)
            print(json.dumps({'new_synthetic_restore_database':True,'source_rows':value['synthetic_business_rows']}));return
        state=json.loads(STATE.read_text(encoding='utf-8'))
        if state.get('purpose')!=PURPOSE or state.get('schema')!=schema:raise RuntimeError('Unapproved state')
        with connect(TARGET) as target:
            comment=target.execute('SELECT shobj_description(oid,\'pg_database\') FROM pg_database WHERE datname=%s',(TARGET,)).fetchone()[0]
            if comment!=COMMENT:raise RuntimeError('Target database ownership marker differs')
            if phase=='diagnose':
                original=fingerprint(source,schema,True);restored=fingerprint(target,schema,True)
                keys=set(original['tables'])|set(restored['tables'])
                report={'synthetic_only':True,'source_rows_match_baseline':original['tables']==state['baseline']['tables'],
                    'restored_rows_match_baseline':restored['tables']==state['baseline']['tables'],
                    'different_table_names':[name for name in sorted(keys) if original['tables'].get(name)!=restored['tables'].get(name)],
                    'schema_parts_differ':[name for name in original['shape'] if original['shape'][name]!=restored['shape'][name]],
                    'structural_differences':{name:{'only_source':[row for row in original['shape'][name] if row not in restored['shape'][name]][:12],
                        'only_restored':[row for row in restored['shape'][name] if row not in original['shape'][name]][:12]}
                        for name in original['shape'] if original['shape'][name]!=restored['shape'][name]},'production_contacts':0}
                (LAB/'evidence/batch-83-recovery-diagnosis.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
                print(json.dumps(report,default=str));return
            if phase=='before-restore':
                if target.execute('SELECT 1 FROM pg_namespace WHERE nspname=%s',(schema,)).fetchone():
                    raise RuntimeError('Restore target is populated; no overwrite/clean is allowed')
                print(json.dumps({'restore_target_empty':True,'identity_verified':True}));return
            restored=fingerprint(target,schema,True);unchanged=fingerprint(source,schema,True)
            original_raw={name:item for name,item in unchanged.items() if name!='shape'}
            if original_raw!=state['baseline'] or restored['tables']!=state['baseline']['tables']:
                raise RuntimeError('Original records/schema or restored data differ')
            original_shape=dict(unchanged['shape']);restored_shape=dict(restored['shape'])
            original_shape['constraints']=canonical_constraints(source,schema)
            restored_shape['constraints']=canonical_constraints(target,schema)
            if original_shape!=restored_shape:raise RuntimeError('Restored columns, indexes, sequences or constraint semantics differ')
            dump=LAB/'runtime/synthetic-business-backup.dump'
            if dump.stat().st_size>2*1024*1024:raise RuntimeError('Unexpected archive budget')
            report={'synthetic_only':True,'full_application_tables':len(restored['tables']),
                'business_rows':sum(row['rows'] for row in restored['tables'].values()),'rows_schema_constraints_indexes_sequences_match':True,
                'source_unchanged':True,'paid_trial_payment_private_source_audit_revocation_evidence_preserved':True,
                'raw_check_cast_representation_changed':restored['schema_sha256']!=state['baseline']['schema_sha256'],
                'postgres_planned_constraint_expressions_and_validation_flags_match':True,
                'archive_bytes':dump.stat().st_size,'archive_sha256':hashlib.sha256(dump.read_bytes()).hexdigest(),
                'production_contacts':0,'production_backup_restoration_verified':False,'provider_managed_roles_rls_storage_verified':False}
            (LAB/'evidence/batch-83-recovery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            print(json.dumps(report))

if __name__=='__main__':main()
