#!/usr/bin/env python3
"""Run baseline fixture tests with the prepared locked runtime, without agent code.
A planted defect may be an expected semantic failure, never an import/setup pass.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/run-agent-evals.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--runtime-dir',type=Path,required=True)
args=p.parse_args()
if not h.validate_runtime(args.runtime_dir):p.error('Locked runtime not prepared')
results=[]
for fixture in sorted((ROOT/'evals/fixtures').iterdir()):
    if not (fixture/'package.json').exists() or not list(fixture.rglob('*test.*')):
        continue
    with tempfile.TemporaryDirectory(prefix='sdlc baseline ') as temp:
        work=Path(temp)/'workspace';shutil.copytree(fixture,work)
        (work/'node_modules').symlink_to(args.runtime_dir.resolve()/'node_modules',target_is_directory=True)
        (work/'.eval-runtime').symlink_to(args.runtime_dir.resolve(),target_is_directory=True)
        if (work/'packages/shared').is_dir():
            scope=work/'packages/dashboard/node_modules/@monorepo';scope.mkdir(parents=True)
            (scope/'shared').symlink_to(work/'packages/shared',target_is_directory=True)
        r=h.command(['node',str(args.runtime_dir.resolve()/'node_modules/vitest/vitest.mjs'),'run','--config',str(args.runtime_dir.resolve()/'vitest.config.mjs'),'--reporter=json','--outputFile='+str(Path(temp)/'report.json')],work,60)
        try:
            report=json.loads((Path(temp)/'report.json').read_text())
            tests=report.get('numTotalTests',0)
            passed=report.get('numPassedTests',0)
        except (ValueError,KeyError,OSError):
            report={};tests=passed=0
        expected=fixture.name=='13-monorepo'
        # The monorepo intentionally has one broken SOURCE import, not a broken test import.
        matched=expected and 'shared/src/indx' in json.dumps(report)
        ok=matched or r['returncode']==0 and passed>0
        results.append({'fixture':fixture.name,'status':'expected-source-import-defect' if matched else 'pass' if ok else 'fail','tests':tests,'passed':passed,'observation':h.observed(r)})
        if not ok:
            print(fixture.name+': '+r['stderr'][-1500:]+r['stdout'][-1500:]+json.dumps(report)[-3000:],file=sys.stderr)
print(json.dumps(results,indent=2))
sys.exit(0 if all(r['status']!='fail' for r in results) else 1)
