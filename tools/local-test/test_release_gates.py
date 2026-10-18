import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_local_release import ROOT,validate_gates


class LocalReleaseGates(unittest.TestCase):
    def setUp(self):
        self.gates=json.loads((ROOT/'docs/RELEASE_GATES.json').read_text(encoding='utf-8'))

    def test_local_success_keeps_every_live_gate_unrun(self):
        self.assertEqual(len(validate_gates(self.gates)),9)
        self.assertIs(self.gates['release_authorized'],False)

    def test_cannot_turn_local_evidence_into_deployment_permission(self):
        for key in ('release_authorized','production_checks_run'):
            value=copy.deepcopy(self.gates);value[key]=True
            with self.assertRaises(RuntimeError):validate_gates(value)

    def test_missing_duplicate_or_unapproved_gate_fails_closed(self):
        for kind in ('missing','duplicate','passed','approval_removed'):
            value=copy.deepcopy(self.gates)
            if kind=='missing':value['gates'].pop()
            elif kind=='duplicate':value['gates'].append(value['gates'][0])
            elif kind=='passed':value['gates'][0]['status']='passed'
            else:value['gates'][0]['owner_approval_required']=False
            with self.assertRaises(RuntimeError):validate_gates(value)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LocalReleaseGates))
    value={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'production_contacts':0}
    (ROOT/'tools/local-test/evidence/batch-83-release-gate-tests.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
