"""Adversarial regressions for the bundled evidence helpers (no network)."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/sdlc-autopilot/scripts'


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='sdlc tests ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_cmd(self, *args, cwd=None, **kwargs):
        return subprocess.run(args, cwd=cwd or self.root, capture_output=True, text=True, **kwargs)

    def git(self, *args):
        p = self.run_cmd('git', *args)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def init(self):
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.write('README.md', '# test\n')
        self.commit()

    def write(self, path, content):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def verify(self, mode='standard', *args, cwd=None):
        p = self.run_cmd('sh', str(SCRIPTS / 'verify-pipeline.sh'), mode, '--json', *args, cwd=cwd)
        return p.returncode, json.loads(p.stdout)

    def test_full_outside_git_is_inconclusive(self):
        rc, r = self.verify('full')
        self.assertEqual(rc, 2)
        self.assertEqual(r['status'], 'inconclusive')

    def test_branch_changes_not_hidden_by_worktree_docs(self):
        self.init()
        self.git('switch', '-qc', 'feature')
        self.write('app.js', 'const password = "real-password-123"; eval(input);\n')
        self.commit()
        self.write('README.md', 'changed docs\n')
        rc, r = self.verify('quick')
        self.assertEqual(rc, 1)
        self.assertIn('app.js', [x['path'] for x in r['changes']])
        self.assertEqual(r['provenance']['base'], self.git('rev-parse', 'main'))
        self.assertNotIn('real-password-123', json.dumps(r))

    def test_spaces_and_failure_are_not_skipped(self):
        self.init()
        self.write('app behavior.test.mjs', 'import {test} from "node:test"; import assert from "node:assert/strict"; test("behavior",()=>assert.equal(1,2));')
        rc, r = self.verify()
        self.assertEqual(rc, 1)
        self.assertTrue(any(c['name'] == 'tests' and c['state'] == 'fail' for c in r['checks']))

    def test_zero_tests_and_production_name_do_not_pass(self):
        for filename in ('latest_data.js', 'empty.test.mjs'):
            with self.subTest(filename=filename):
                self.init_if_needed()
                self.write(filename, 'console.log("no tests");')
                rc, r = self.verify()
                self.assertEqual(rc, 2)
                self.assertFalse(any(c['name'] == 'tests' and c['state'] == 'pass' for c in r['checks']))
                (self.root / filename).unlink()

    def init_if_needed(self):
        if not (self.root / '.git').exists():
            self.init()

    def test_deleted_test_not_execution_evidence(self):
        self.init()
        self.write('old.test.mjs', 'import {test} from "node:test"; test("old",()=>{});')
        self.commit()
        (self.root / 'old.test.mjs').unlink()
        self.write('app.js', 'export const x=2;')
        rc, r = self.verify()
        self.assertEqual(rc, 2)
        self.assertEqual(next(x for x in r['changes'] if x['path']=='old.test.mjs')['status'], 'D')

    def test_real_node_tests_pass_without_test_churn_or_assertion_counts(self):
        self.init()
        self.write('app.test.mjs', 'import {test} from "node:test"; import assert from "node:assert/strict"; test("behavior",()=>assert.equal(1+1,2));')
        self.commit()
        self.write('app.js', 'export const x=2;')
        rc, r = self.verify()
        self.assertEqual(rc, 0, r)
        self.assertEqual(next(c for c in r['checks'] if c['name']=='tests')['count'], 1)

    def test_snapshot_tracks_mixed_user_work_and_subdirectory(self):
        self.init()
        self.write('app.js', 'user work\n')
        baseline = self.root.parent / (self.root.name + '.baseline.json')
        self.addCleanup(lambda: baseline.unlink(missing_ok=True))
        p = self.run_cmd('python3', str(SCRIPTS/'evidence.py'), 'snapshot', '--output', str(baseline))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.write('app.js', 'user work plus task\n')
        self.write('nested/new name.md', 'task\n')
        rc, r = self.verify('quick', '--baseline', str(baseline), cwd=self.root/'nested')
        self.assertEqual(rc, 0, r)
        self.assertEqual(next(x for x in r['changes'] if x['path']=='app.js')['attribution'], 'mixed-preexisting')
        self.assertEqual(next(x for x in r['changes'] if x['path']=='nested/new name.md')['attribution'], 'changed-since-snapshot')

    def test_linked_worktree_and_real_json_null(self):
        self.init()
        other = self.root / 'linked worktree'
        self.git('worktree', 'add', '-qb', 'linked', str(other.resolve()))
        self.addCleanup(lambda: self.run_cmd('git', 'worktree', 'remove', '--force', str(other.resolve())))
        p = self.run_cmd('sh', str(SCRIPTS/'detect-toolchain.sh'), cwd=other)
        r = json.loads(p.stdout)
        self.assertEqual(r['git']['root'], str(other.resolve()))
        self.assertIsNone(r['projects'][0]['language'])

    def test_scan_has_no_blanket_test_or_config_exemption(self):
        self.init()
        self.write('config.test.js', 'const config = { password: "not-a-placeholder-123" }; // example\n')
        rc, r = self.verify('quick')
        self.assertEqual(rc, 1)
        self.assertNotIn('not-a-placeholder-123', json.dumps(r))

    def test_stale_coverage_is_not_evidence(self):
        self.init()
        self.write('src/value.js', 'export const value=1;')
        self.write('coverage/coverage-final.json', '{"elsewhere/value.js":{"s":{"1":1}}}')
        rc, r = self.verify()
        self.assertEqual(rc, 2)
        self.assertFalse(any(c['name']=='coverage' and c['state']=='pass' for c in r['checks']))

    def test_gates_default_does_not_fix_or_fetch(self):
        self.init()
        self.write('package.json', json.dumps({'scripts': {'lint': 'echo do-not-run-implicitly'}}))
        self.write('.sdlc-checks.json', json.dumps({'version':1,'checks':[{'name':'lint','kind':'lint','argv':['python3','-c','print("checked")']}]}))
        p = self.run_cmd('sh', str(SCRIPTS/'run-gates.sh'), '--json')
        r = json.loads(p.stdout)
        self.assertEqual(p.returncode, 0, r)
        self.assertEqual(len(r['checks']), 1)
        self.assertFalse(any('--fix' in x for x in r['checks'][0]['command']))

    def test_timeout_and_missing_tool_are_inconclusive(self):
        self.init()
        for command in (['python3','-c','import time; time.sleep(5)'], ['missing-sdlc-tool']):
            self.write('.sdlc-checks.json', json.dumps({'version':1,'checks':[{'name':'bounded','kind':'lint','argv':command}]}))
            p = self.run_cmd('sh', str(SCRIPTS/'run-gates.sh'), '--json', '--timeout', '0.2')
            self.assertEqual(p.returncode, 2, p.stdout)
            self.assertEqual(json.loads(p.stdout)['checks'][0]['state'], 'inconclusive')

    def test_review_clean_repo_needs_no_implementation_diff(self):
        self.init()
        rc, r = self.verify('full', '--task', 'review')
        self.assertEqual(rc, 0, r)
        self.assertTrue(all(c['state'] != 'fail' for c in r['checks']))
        self.assertIn('human_review', r)

    def test_invalid_config_is_structured_inconclusive(self):
        self.init()
        for value in ([], None, {"version":1,"checks":[None]}, {"version":1,"checks":[{"name":"x","kind":"lint","argv":["echo"],"fix_argv":"echo"}]}):
            self.write('.sdlc-checks.json', json.dumps(value))
            p=self.run_cmd('sh', str(SCRIPTS/'run-gates.sh'), '--json')
            self.assertEqual(p.returncode,2,p.stdout+p.stderr)
            self.assertEqual(json.loads(p.stdout)['status'],'inconclusive')

    def test_empty_review_scan_is_explicitly_not_applicable(self):
        self.init()
        _,r=self.verify('full','--task','review')
        scan=next(c for c in r['checks'] if c['name']=='pattern-review')
        self.assertEqual(scan['state'],'not-applicable')
        self.assertEqual(scan['scanned_files'],0)

    def test_detect_reports_consistent_status(self):
        self.init()
        p=self.run_cmd('sh',str(SCRIPTS/'detect-toolchain.sh'))
        self.assertEqual(json.loads(p.stdout)['status'],'pass')

    def test_rename_and_untracked_symlink_do_not_escape_scan(self):
        self.init()
        self.write('old name.js','export const x=1;')
        self.commit()
        self.git('mv','old name.js','new name.js')
        (self.root/'linked.js').symlink_to('/etc/passwd')
        _,r=self.verify('quick')
        rename=next(c for c in r['changes'] if c['path']=='new name.js')
        self.assertEqual(rename['old_path'],'old name.js')
        self.assertIn('linked.js',r['unscanned_paths'])

    def test_review_decisions_are_exact_and_risk_acceptance_is_unverified(self):
        self.init()
        self.write('fixture.js','const password = "fake-fixture-password";')
        _,r=self.verify('quick')
        fingerprint=r['review_candidates'][0]['fingerprint']
        decisions=self.root.parent/(self.root.name+'.reviews.json')
        self.addCleanup(lambda: decisions.unlink(missing_ok=True))
        decisions.write_text(json.dumps([{'fingerprint':fingerprint,'disposition':'test-fixture','reason':'Intentionally inert fixture used to test literal detection'}]))
        rc,r=self.verify('quick','--review-decisions',str(decisions))
        self.assertEqual(rc,0,r)
        decisions.write_text(json.dumps([{'fingerprint':fingerprint,'disposition':'accepted-risk','reason':'Risk decision for review, still unverified'}]))
        rc,r=self.verify('quick','--review-decisions',str(decisions))
        self.assertEqual(rc,2,r)

    def test_invalid_baseline_is_inconclusive_not_traceback(self):
        self.init()
        baseline=self.root.parent/(self.root.name+'.invalid-baseline.json')
        self.addCleanup(lambda:baseline.unlink(missing_ok=True))
        for value in [[], None, {'version':1,'root':str(self.root.resolve()),'files':{},'preexisting':[]}]:
            baseline.write_text(json.dumps(value))
            rc,r=self.verify('quick','--baseline',str(baseline))
            self.assertEqual(rc,2,r)
            self.assertEqual(r['status'],'inconclusive')

    def test_snapshot_attribution_detects_executable_mode_change(self):
        self.init()
        self.write('run.sh','#!/bin/sh\nexit 0\n')
        self.commit()
        baseline=self.root.parent/(self.root.name+'.mode-baseline.json')
        self.addCleanup(lambda:baseline.unlink(missing_ok=True))
        self.run_cmd('python3',str(SCRIPTS/'evidence.py'),'snapshot','--output',str(baseline))
        (self.root/'run.sh').chmod(0o755)
        rc,r=self.verify('quick','--baseline',str(baseline))
        self.assertEqual(rc,0,r)
        self.assertEqual(next(c for c in r['changes'] if c['path']=='run.sh')['attribution'],'changed-since-snapshot')

    def test_expected_failure_only_is_not_positive_unittest_execution(self):
        self.init()
        self.write('test_expected.py','import unittest\nclass TestExpected(unittest.TestCase):\n @unittest.expectedFailure\n def test_expected(self): self.assertEqual(1,2)\n')
        self.write('.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'tests','kind':'test','runner':'unittest','argv':['python3','-m','unittest','test_expected','-q']}]}))
        rc,r=self.verify()
        self.assertEqual(rc,2,r)

    def test_node_skip_only_is_not_positive_execution(self):
        self.init()
        self.write('skip.test.mjs','import {test} from "node:test"; test.skip("skipped",()=>{}); test.todo("todo");')
        rc,r=self.verify()
        self.assertEqual(rc,2,r)

    def test_fix_mode_requires_regular_file_scope(self):
        self.init()
        self.write('.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'fmt','kind':'format','argv':['python3','-c','print("ok")'],'fix_argv':['python3','-c','print("fix")','{files}']}]}))
        p=self.run_cmd('sh',str(SCRIPTS/'run-gates.sh'),'--fix','--file','.','--json')
        self.assertEqual(p.returncode,2,p.stdout)

    def test_context_edits_invalidate_candidate_decisions(self):
        self.init()
        self.write('calc.js','const expression="1+2";\nexport const result = eval(expression);')
        _,r=self.verify('quick')
        decisions=self.root.parent/(self.root.name+'.context.json')
        self.addCleanup(lambda: decisions.unlink(missing_ok=True))
        decisions.write_text(json.dumps([{'fingerprint':r['review_candidates'][0]['fingerprint'],'disposition':'false-positive','reason':'Expression is a constant owned by source code'}]))
        self.write('calc.js','const expression=process.env.USER_INPUT;\nexport const result = eval(expression);')
        rc,r=self.verify('quick','--review-decisions',str(decisions))
        self.assertEqual(rc,2,r)
        self.assertIn('Stale',r['error'])

    def test_ancestor_symlink_does_not_hash_or_scan_outside_repo(self):
        self.init()
        self.write('data/value.js','export const x=1;')
        self.commit()
        outside=self.root.parent/(self.root.name+'-outside')
        outside.mkdir()
        self.addCleanup(lambda: __import__('shutil').rmtree(outside))
        (outside/'value.js').write_text('eval(input);')
        (self.root/'data/value.js').unlink()
        (self.root/'data').rmdir()
        (self.root/'data').symlink_to(outside,target_is_directory=True)
        _,r=self.verify('quick')
        self.assertFalse(r['review_candidates'],r)
        self.assertIn('data/value.js',r['unscanned_paths'])
        self.assertNotEqual(next(c for c in r['changes'] if c['path']=='data/value.js')['sha256'],__import__('hashlib').sha256((outside/'value.js').read_bytes()).hexdigest())

    def test_fix_mode_rejects_symlink_scope(self):
        self.init()
        self.write('target.js','value')
        (self.root/'link.js').symlink_to(self.root/'target.js')
        self.write('.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'fmt','kind':'format','argv':['echo','ok'],'fix_argv':['echo','{files}']}]}))
        p=self.run_cmd('sh',str(SCRIPTS/'run-gates.sh'),'--fix','--file','link.js','--json')
        self.assertEqual(p.returncode,2,p.stdout)

    def test_snapshot_is_private_even_with_permissive_umask(self):
        self.init()
        baseline=self.root.parent/(self.root.name+'.private.json')
        self.addCleanup(lambda:baseline.unlink(missing_ok=True))
        script='import os,runpy,sys; os.umask(0); sys.argv='+repr([str(SCRIPTS/'evidence.py'),'snapshot','--output',str(baseline)])+'; runpy.run_path(sys.argv[0],run_name="__main__")'
        p=self.run_cmd('python3','-c',script)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(baseline.stat().st_mode & 0o777,0o600)

    def test_commands_cannot_change_verified_state_and_leave_green(self):
        self.init()
        self.write('app.js','export const x=1;')
        self.write('app.test.mjs','import {test} from "node:test"; import {writeFileSync} from "node:fs"; test("behavior",()=>writeFileSync("app.js","export const changed=2;"));')
        self.commit()
        self.write('app.js','export const x=3;')
        rc,r=self.verify()
        self.assertEqual(rc,2,r)
        stability=next(c for c in r['checks'] if c['name']=='worktree-stability')
        self.assertEqual(stability['state'],'inconclusive')
        self.assertIn('app.js',stability['changed_paths'])
        self.assertNotEqual(r['provenance']['worktree_sha256'],r['provenance']['final_worktree_sha256'])

    def test_required_evidence_is_per_selected_project(self):
        self.init()
        self.write('api/unit.test.mjs','import {test} from "node:test"; test("behavior",()=>{});')
        self.write('api/.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'tests','kind':'test','runner':'node-test','argv':['node','--test','unit.test.mjs']},{'name':'security','kind':'security','argv':['echo','configured tool stub']}]}))
        self.write('ui/app.js','export const x=1;')
        rc,r=self.verify('full','--project','api','--project','ui')
        self.assertEqual(rc,2,r)
        missing=[c for c in r['checks'] if c['state']=='inconclusive' and c.get('project')=='ui']
        self.assertEqual({c['name'] for c in missing},{'tests','security-tooling'})

    def test_missing_project_is_rejected_before_executing_any_commands(self):
        self.init()
        self.write('api/.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'sentinel','kind':'lint','argv':['python3','-c','from pathlib import Path; Path("executed").touch()']}]}))
        rc,r=self.verify('quick','--project','api','--project','missing')
        self.assertEqual(rc,2,r)
        self.assertFalse((self.root/'api/executed').exists())
        p=self.run_cmd('sh',str(SCRIPTS/'detect-toolchain.sh'),'--project','missing')
        self.assertEqual(p.returncode,2,p.stdout)

    def test_node_expected_todo_failure_is_not_a_real_failure(self):
        self.init()
        self.write('app.test.mjs','import {test} from "node:test"; import assert from "node:assert/strict"; test("working",()=>assert.equal(1,1)); test("future",{todo:true},()=>assert.fail("not implemented"));')
        rc,r=self.verify()
        self.assertEqual(rc,0,r)
        self.assertEqual(next(c for c in r['checks'] if c.get('kind')=='test')['count'],1)

    def test_failed_todo_only_is_not_positive_test_evidence(self):
        self.init()
        self.write('app.test.mjs','import {test} from "node:test"; import assert from "node:assert/strict"; test("future",{todo:true},()=>assert.fail("not implemented"));')
        rc,r=self.verify()
        self.assertEqual(rc,2,r)

    def test_empty_explicit_configuration_does_not_run_fallback(self):
        self.init()
        self.write('app.test.mjs','import {test} from "node:test"; import {writeFileSync} from "node:fs"; test("sentinel",()=>writeFileSync("executed","yes"));')
        self.write('.sdlc-checks.json',json.dumps({'version':1,'checks':[]}))
        rc,r=self.verify()
        self.assertEqual(rc,2,r)
        self.assertFalse((self.root/'executed').exists())

    def test_git_index_flags_do_not_hide_modified_contents(self):
        self.init()
        self.write('app.js','export const value=1;')
        self.commit()
        for flag in ['--assume-unchanged','--skip-worktree']:
            self.git('update-index',flag,'app.js')
            self.write('app.js','eval(input);')
            rc,r=self.verify('quick')
            self.assertNotEqual(rc,0,r)
            self.assertIn('app.js',[c['path'] for c in r['changes']])
            self.assertTrue(r['review_candidates'])
            self.write('app.js','export const value=1;')
            self.git('update-index','--no-assume-unchanged','--no-skip-worktree','app.js')

    def test_git_flags_are_preserved_and_unchanged_flagged_files_can_pass(self):
        self.init()
        self.write('app.js','export const value=1;')
        self.commit()
        self.git('update-index','--assume-unchanged','app.js')
        self.write('README.md','docs edit')
        rc,r=self.verify('quick')
        self.assertEqual(rc,0,r)
        self.assertEqual(self.git('ls-files','-v','app.js')[0],'h')
        self.assertIn('app.js',r['provenance']['index_masked_paths'])

    def test_command_committing_changes_invalidates_provenance(self):
        self.init()
        self.write('README.md','task edit')
        self.write('.sdlc-checks.json',json.dumps({'version':1,'checks':[{'name':'mutating','kind':'lint','argv':['python3','-c','import subprocess; subprocess.run(["git","add","."],check=True); subprocess.run(["git","commit","-qm","mutation"],check=True)']}]}))
        rc,r=self.verify('quick')
        self.assertEqual(rc,2,r)
        self.assertNotEqual(r['provenance']['head'],r['provenance']['final_head'])

    def test_strict_inversion_is_not_a_false_guarantee(self):
        self.init()
        p = self.run_cmd('sh', str(SCRIPTS/'verify-inversion.sh'))
        self.assertEqual(p.returncode, 2)
        self.assertIn('unsupported', p.stdout.lower())


if __name__ == '__main__':
    unittest.main()
