import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('harness', ROOT/'scripts/run-agent-evals.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class HarnessTests(unittest.TestCase):
    def test_empty_transcript_cannot_satisfy_negative_evidence(self):
        state, _ = h.transcript_check({'value':'secret','type':'transcript_not_contains'}, None)
        self.assertEqual(state, 'inconclusive')

    def test_schema_rejects_untyped_and_unknown_self_report(self):
        case={'id':1,'expected_mode':'quick'}
        self.assertTrue(h.validate_meta(case, {'eval_id':1,'mode':'quick','summary':'ok','agent_name':3}))
        self.assertTrue(h.validate_meta(case, {'eval_id':True,'mode':'quick','summary':'ok','flags':['passed']}))
        self.assertFalse(h.validate_meta(case, {'eval_id':1,'mode':'quick','summary':'ok','agent_name':'local'}))

    def test_noop_patch_fails_hidden_pagination_oracle(self):
        with tempfile.TemporaryDirectory() as temp:
            work=Path(temp)/'fixture'
            h.shutil.copytree(ROOT/'evals/fixtures/15-python', work)
            result=h.run_oracle(ROOT, work, 'pagination', None, 10)
            self.assertEqual(result['state'], 'fail', result)
            p=work/'pagination.py'
            p.write_text(p.read_text().replace('page * per_page', '(page - 1) * per_page'))
            result=h.run_oracle(ROOT, work, 'pagination', None, 10)
            self.assertEqual(result['state'], 'pass', result)

    def test_provenance_is_harness_generated_and_workspace_is_cleaned(self):
        with tempfile.TemporaryDirectory() as temp:
            runs=Path(temp)
            (runs/'meta.json').write_text(json.dumps({'eval_id':15,'mode':'standard','summary':'claimed fixed','agent_name':'test'}))
            (runs/'patch.diff').write_text('')
            case=next(c for c in json.loads((ROOT/'evals/evals.json').read_text())['evals'] if c['id']==15)
            result=h.evaluate_case(ROOT, case, runs, execute=True, runtime=None, timeout=10)
            self.assertEqual(result['semantic'][0]['state'], 'fail')
            self.assertEqual(len(result['provenance']['patch_sha256']),64)
            self.assertFalse(Path(result['provenance']['workspace']).exists())
            self.assertEqual(result['human_judgment']['state'], 'pending')

    def test_rejects_patch_symlink_escape_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            work=Path(temp)
            (work/'outside').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                h.validate_workspace(work)

    def test_source_tree_digest_ignores_generated_bytecode(self):
        with tempfile.TemporaryDirectory() as temp:
            work=Path(temp)
            (work/'app.py').write_text('value=1')
            before=h.tree_sha(work)
            (work/'__pycache__').mkdir()
            (work/'__pycache__/app.pyc').write_bytes(b'generated')
            self.assertEqual(before,h.tree_sha(work))

    def test_missing_module_is_inconclusive_semantic_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            r=h.run_oracle(ROOT,Path(temp),'pagination',None,5)
            self.assertEqual(r['state'],'inconclusive')

    def test_early_exit_cannot_impersonate_oracle_success(self):
        with tempfile.TemporaryDirectory() as temp:
            work=Path(temp)
            for termination in ['sys.exit(0)','os._exit(0)']:
                (work/'pagination.py').write_text('import sys,os\nprint("ORACLE_PASS pagination",flush=True)\n'+termination+'\n')
                result=h.run_oracle(ROOT,work,'pagination',None,5)
                self.assertEqual(result['state'],'inconclusive',result)

    def test_replay_lists_new_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            runs=Path(temp)
            (runs/'meta.json').write_text(json.dumps({'eval_id':15,'mode':'standard','summary':'new file','agent_name':'test'}))
            (runs/'patch.diff').write_text('diff --git a/new helper.py b/new helper.py\nnew file mode 100644\n--- /dev/null\n+++ b/new helper.py\n@@ -0,0 +1 @@\n+value = 42\n')
            case=next(c for c in json.loads((ROOT/'evals/evals.json').read_text())['evals'] if c['id']==15)
            result=h.evaluate_case(ROOT,case,runs,execute=True,timeout=5)
            self.assertIn('new helper.py',result['provenance']['changed_paths'])

    def test_unknown_oracle_is_not_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            r=h.run_oracle(ROOT,Path(temp),'unknown',None,1)
            self.assertEqual(r['state'],'inconclusive')


if __name__=='__main__':
    unittest.main()
