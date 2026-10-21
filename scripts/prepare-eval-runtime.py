#!/usr/bin/env python3
"""Prepare a pinned public npm runtime at a NEW path, separately from replay.
No lifecycle scripts run. Network/package acquisition happens only in this command.
Use a Node version supported by evals/runtime/package.json and the lockfile.
"""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence',ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
if args.output.exists():
    p.error('output must be a new directory')
shutil.copytree(ROOT/'evals/runtime',args.output)
r=e.execute(['npm','ci','--ignore-scripts','--no-audit','--no-fund','--engine-strict'],args.output.resolve(),300)
if r['returncode']!=0 or r.get('error'):
    print('Runtime preparation failed; inspect npm and engine compatibility. No fixture baseline was created.',file=sys.stderr)
    sys.exit(1)
print('Prepared locked runtime: '+str(args.output.resolve()))
