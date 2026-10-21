"""Opt-in source-only verification of the private reviewed core; never imports it."""
import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import backup_runner as backup


def review():
    source=backup.load_core()
    tree=ast.parse(source)
    identity=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='source_identity')
    namespace={'REVISION':backup.REVISION}
    exec(compile(ast.Module(body=[identity],type_ignores=[]),'reviewed-identity-only','exec'),namespace)
    verify=namespace['source_identity']
    good=(170006,'postgres','postgres','on',True)
    verify(good,backup.REVISION)
    cases=[(good,'0021_feedback_screenshot'),((180000,*good[1:]),backup.REVISION),
           ((good[0],'other',*good[2:]),backup.REVISION),
           ((*good[:2],'other',*good[3:]),backup.REVISION),
           ((*good[:3],'off',True),backup.REVISION),((*good[:4],False),backup.REVISION)]
    for row,revision in cases:
        try:
            verify(row,revision)
        except RuntimeError:
            continue
        raise AssertionError('Source identity guard unexpectedly accepted a mismatch')
    assert all(value in source for value in ('row_security=off','--roles-only','--no-role-passwords',
               '--snapshot=','sslmode=\'verify-full\'','require_efs(bundle / \'schema-review-private.sql\')'))
    assert '--exclude-schema' not in source and '--exclude-table' not in source
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='input' for n in ast.walk(main))
    choose=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='choose_archive_password')
    assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='input' for n in ast.walk(choose))
    return {'status':'passed','core_sha256':backup.CORE_SHA,'accepted_revision':backup.REVISION,
            'identity_negative_cases':len(cases),'source_connections':0,'exports':0,'restorations':0,
            'private_data_or_credentials_read':False,'existing_helper_modified':False,
            'owner_confirmation_only_inside_replaced_prompt_function':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-approved-source',action='store_true')
    args=parser.parse_args()
    if not args.review_approved_source:
        parser.print_help()
    else:
        print(json.dumps(review(),indent=2))
