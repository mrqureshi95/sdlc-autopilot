"""Fresh, positive test evidence across native JSON and generic JUnit reports."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence_adapters', ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
e=importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

class ReportAdapters(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='sdlc reports ')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()

    def run_report(self, runner, report, rc=0, write=True):
        # Simulates a runner's documented report interface, never stdout-based evidence.
        script=self.root/'runner.py'
        script.write_text('import pathlib,sys\n'
            'p=next(a.split("=",1)[1] for a in sys.argv if a.startswith("--outputFile="))\n'
            if runner!='junit' else 'import pathlib,sys\np=sys.argv[1]\n')
        with script.open('a') as f:
            if write: f.write('pathlib.Path(p).write_text('+repr(report)+')\n')
            f.write('sys.exit('+str(rc)+')\n')
        argv=[sys.executable,str(script)] + (['{report}'] if runner=='junit' else [])
        return e.run_check({'name':'test','kind':'test','runner':runner,'argv':argv},self.root,5)

    def json_report(self, statuses=('passed',), **overrides):
        data={'success':True,'numPassedTests':statuses.count('passed'),'numFailedTests':statuses.count('failed'),
              'testResults':[{'assertionResults':[{'fullName':'case '+str(i),'status':s} for i,s in enumerate(statuses)]}]}
        data.update(overrides)
        return json.dumps(data)

    def test_json_adapters_count_only_named_actual_passes(self):
        for runner in ('jest-json','vitest-json'):
            with self.subTest(runner=runner):
                r=self.run_report(runner,self.json_report(('passed','pending')))
                self.assertEqual((r['state'],r['count']),('pass',1))

    def test_missing_malformed_or_contradictory_json_never_passes(self):
        reports=['{}','garbage',self.json_report((),numPassedTests=7),self.json_report(success=False),
                 self.json_report(('pending',)),self.json_report(numPassedTests=True)]
        for report in reports:
            with self.subTest(report=report):
                self.assertEqual(self.run_report('jest-json',report)['state'],'inconclusive')
        (self.root/'old-report.json').write_text(self.json_report())
        self.assertEqual(self.run_report('jest-json','',write=False)['state'],'inconclusive')

    def test_test_failure_and_setup_failure_are_distinguished(self):
        self.assertEqual(self.run_report('vitest-json',self.json_report(('failed',),success=False),1)['state'],'fail')
        self.assertEqual(self.run_report('vitest-json','',1,False)['state'],'inconclusive')
        self.assertEqual(self.run_report('jest-json',self.json_report(),1)['state'],'inconclusive')

    def test_junit_counts_testcases_excluding_skips(self):
        report='<testsuites><testsuite tests="2"><testcase name="works"/><testcase name="later"><skipped/></testcase></testsuite></testsuites>'
        r=self.run_report('junit',report)
        self.assertEqual((r['state'],r['count']),('pass',1))
        self.assertEqual(self.run_report('junit','<testsuite><testcase name="bad"><failure/></testcase></testsuite>',1)['state'],'fail')

    def test_junit_rejects_empty_opaque_unsafe_or_failed_suites(self):
        for report in ['<testsuite tests="10"/>','<testsuite><testcase name="later"><skipped/></testcase></testsuite>',
                       '<testsuite><testcase/></testsuite>', '<testsuite errors="1"><testcase name="works"/></testsuite>',
                       '<!DOCTYPE x [<!ENTITY a "value">]><testsuite><testcase name="&a;"/></testsuite>']:
            with self.subTest(report=report):
                self.assertNotEqual(self.run_report('junit',report)['state'],'pass')

    def test_malformed_junit_counters_cannot_cancel_real_failure(self):
        for value in ('-1','1.5','not-a-number'):
            report='<testsuite failures="'+value+'"><testcase name="bad"><failure/></testcase><testcase name="good"/></testsuite>'
            self.assertNotEqual(self.run_report('junit',report)['state'],'pass')

    def test_report_flags_and_placeholder_are_owned_by_adapter(self):
        for runner,argv in [('jest-json',['jest','--outputFile=stale.json']),('vitest-json',['vitest','--reporter=json']),('junit',['tool','stale.xml'])]:
            with self.subTest(runner=runner),self.assertRaises(ValueError):
                e.run_check({'name':'bad','kind':'test','runner':runner,'argv':argv},self.root,5)

    def test_configuration_accepts_new_adapters_only_for_tests(self):
        for runner in ('jest-json','vitest-json','junit'):
            config={'version':1,'checks':[{'name':'unit','kind':'test','runner':runner,'argv':['tool','{report}']}]}
            (self.root/'.sdlc-checks.json').write_text(json.dumps(config))
            self.assertEqual(e.configuration(self.root)[0]['runner'],runner)
            config['checks'][0]['kind']='lint'
            (self.root/'.sdlc-checks.json').write_text(json.dumps(config))
            with self.assertRaises(ValueError): e.configuration(self.root)
