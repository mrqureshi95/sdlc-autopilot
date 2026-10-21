#!/usr/bin/env python3
"""Controlled verifier comparisons with the audited original commit.
This measures specific helper behavior, never agent quality or productivity.
No package installs or external services; all target repositories are disposable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BASE='6c1e8d1d8ea004a7398377005c71c09c516d14e7'


def run(argv,cwd):
    return subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=45)


def git(work,*args):
    p=run(['git',*args],work)
    if p.returncode:raise RuntimeError('Comparison Git operation failed')
    return p.stdout.strip()


def write(work,path,text):
    p=work/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)


def initialize(work):
    git(work,'init','-qb','main');git(work,'config','user.name','Comparison')
    git(work,'config','user.email','comparison@example.invalid')
    write(work,'README.md','# fixture\n')
    git(work,'add','.');git(work,'commit','-qm','base')


def compare(base):
    old=run(['git','show',base+':skills/sdlc-autopilot/scripts/verify-pipeline.sh'],ROOT)
    if old.returncode:raise RuntimeError('Original verifier revision unavailable')
    cases=[
        ('cosmetic-docs','quick',[],True,True),
        ('named-regression','standard',[],True,True),
        ('existing-tests-no-churn','standard',[],False,True),
        ('clean-read-only-review','full',['--task','review'],False,True),
        ('full-outside-git','full',[],True,False),
        ('committed-source-under-doc-edit','quick',[],True,False),
        ('no-named-tests','standard',[],True,False),
        ('failing-test-path-with-spaces','standard',[],True,False),
    ]
    results=[]
    with tempfile.TemporaryDirectory(prefix='sdlc comparisons ') as temp:
        script=Path(temp)/'original.sh';script.write_text(old.stdout)
        for name,mode,extra,expected_old,expected_new in cases:
            work=Path(temp)/name;work.mkdir()
            if name!='full-outside-git':initialize(work)
            if name=='cosmetic-docs':write(work,'README.md','copy edit\n')
            if name in ['named-regression','existing-tests-no-churn']:
                write(work,'app.test.mjs','import {test} from "node:test"; import assert from "node:assert/strict"; test("behavior",()=>{assert.equal(2+2,4); assert.notEqual(1,2);});\n')
                if name=='existing-tests-no-churn':
                    git(work,'add','.');git(work,'commit','-qm','existing tests')
                    write(work,'app.mjs','export function value(){return 42;}\n')
            if name=='committed-source-under-doc-edit':
                git(work,'switch','-qc','feature')
                write(work,'app.js','const password="synthetic-password-123"; eval(input);\n')
                git(work,'add','.');git(work,'commit','-qm','feature')
                write(work,'README.md','docs edit\n')
            if name=='no-named-tests':write(work,'latest_data.js','export const value=42;\n')
            if name=='failing-test-path-with-spaces':write(work,'app behavior.test.mjs','import {test} from "node:test"; import assert from "node:assert/strict"; test("broken",()=>{assert.equal(1,2);assert.equal(2,3);});\n')
            before=run(['sh',str(script),mode],work)
            after=run(['sh',str(ROOT/'skills/sdlc-autopilot/scripts/verify-pipeline.sh'),mode,'--json',*extra],work)
            parsed=json.loads(after.stdout)
            observed_old=before.returncode==0;observed_new=after.returncode==0
            results.append({'case':name,'original_exit':before.returncode,'revised_exit':after.returncode,
                            'revised_state':parsed['status'],'expected_original_green':expected_old,
                            'expected_revised_green':expected_new,
                            'expectations_met':observed_old==expected_old and observed_new==expected_new,
                            'original_output_sha256':hashlib.sha256(before.stdout.encode()).hexdigest()})
    return {'evidence_type':'controlled helper comparison; not a live-agent campaign',
            'original_ref':base,'original_script_sha256':hashlib.sha256(old.stdout.encode()).hexdigest(),
            'revised_script_sha256':hashlib.sha256((ROOT/'skills/sdlc-autopilot/scripts/evidence.py').read_bytes()).hexdigest(),
            'results':results}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',default=DEFAULT_BASE)
    args=p.parse_args();report=compare(args.base)
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if all(r['expectations_met'] for r in report['results']) else 1)
