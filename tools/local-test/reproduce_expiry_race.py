"""Reproduce the committed defect in memory; preserve current working source."""
import ast
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import guard
guard.isolate()
sys.path.insert(0, str(guard.BACKEND / 'tests'))
from app.services import subscription_service as service
from test_subscription_expiry_race import SubscriptionExpiryRaceTests

source = (LAB / 'runtime/batch-87-interrupted-work/committed-subscription-service.py').read_text(encoding='utf-8-sig')
function = next(item for item in ast.parse(source).body if isinstance(item, ast.FunctionDef) and item.name == 'expire_trial_if_needed')
namespace = dict(vars(service))
exec(compile(ast.Module(body=[function], type_ignores=[]), '<committed expiry helper: memory-only reproduction>', 'exec'), namespace)
case = SubscriptionExpiryRaceTests('test_stale_trial_or_paid_get_cannot_erase_a_committed_renewal_or_staff_role')
result = unittest.TestResult()
with patch.object(service, 'expire_trial_if_needed', namespace['expire_trial_if_needed']):
    case.run(result)
if result.errors or len(result.failures) != 6:
    raise RuntimeError('Expected six stale-renewal failures were not independently reproduced')
report = {'committed_defect_reproduced': True, 'expected_failing_subcases': len(result.failures),
          'source_file_modified_by_reproducer': False, 'working_fix_restored_after_memory_patch': True,
          'database': 'fresh synthetic in-memory SQLite', 'production_connections': 0}
(LAB / 'evidence/batch-87-expiry-before.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
