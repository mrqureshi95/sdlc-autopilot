#!/usr/bin/env python3
"""Smoke-test a standalone package with a pinned local skills CLI. No installs of dependencies.
Uses disposable project-local destinations and an isolated child HOME; no global skills change.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence',ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-dir',type=Path,required=True);args=p.parse_args()
runtime=args.runtime_dir.resolve()
cli=runtime/'node_modules/skills/bin/cli.mjs'
metadata=json.loads((runtime/'node_modules/skills/package.json').read_text())
if metadata['version']!='1.7.4': p.error('expected locked skills CLI 1.7.4')
with tempfile.TemporaryDirectory(prefix='sdlc install smoke ') as temp:
    root=Path(temp).resolve(); source=root/'export'; source.mkdir()
    prefix='skills/sdlc-autopilot/'
    expected={}
    for name in e.paths(ROOT):
        if name.startswith(prefix):
            original=ROOT/name
            if original.is_symlink() or not original.is_file(): raise SystemExit('Invalid package file: '+name)
            relative=Path(name).relative_to('skills')
            target=source/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,target)
            expected[str(Path(name).relative_to(prefix))]=e.digest(original.read_bytes())
    for agent,folder in [('codex','.agents/skills'),('claude-code','.claude/skills'),('opencode','.agents/skills')]:
        project=root/agent;project.mkdir();home=root/(agent+'-home');home.mkdir()
        env={k:os.environ[k] for k in ('PATH','LANG','TMPDIR') if k in os.environ}
        env.update(HOME=str(home),CI='1',DISABLE_TELEMETRY='1',DO_NOT_TRACK='1',GIT_TERMINAL_PROMPT='0',NODE_DISABLE_COMPILE_CACHE='1',PYTHONDONTWRITEBYTECODE='1')
        r=e.execute(['node',str(cli),'add',str(source),'--skill','sdlc-autopilot','--agent',agent,'--copy','--yes'],project,60,env)
        if r['returncode']!=0 or r.get('error'): raise SystemExit('Installer failed for '+agent+'; output SHA256 '+e.digest((r['stdout']+r['stderr']).encode()))
        installed=project/folder/'sdlc-autopilot'
        actual={str(f.relative_to(installed)):e.digest(f.read_bytes()) for f in installed.rglob('*') if f.is_file()}
        if actual!=expected: raise SystemExit('Package contents differ for '+agent+': '+str(sorted(set(expected)^set(actual))))
        for command in [['git','init','-q'],['git','config','user.email','smoke@example.invalid'],['git','config','user.name','Installer smoke']]:
            if e.execute(command,project,10,env)['returncode']: raise SystemExit('Git setup failed')
        (project/'.gitignore').write_text('.agents/\n.claude/\nskills-lock.json\n')
        (project/'smoke.test.mjs').write_text('import {test} from "node:test"; import assert from "node:assert/strict"; test("installed reporter runs",()=>assert.equal(2+2,4));\n')
        e.execute(['git','add','.'],project,10,env);e.execute(['git','commit','-qm','smoke fixture'],project,10,env)
        r=e.execute(['sh',str(installed/'scripts/verify-pipeline.sh'),'standard','--base','HEAD','--json'],project,30,env)
        if r['returncode'] or json.loads(r['stdout'])['status']!='pass': raise SystemExit('Installed verifier failed for '+agent)
        print(agent+': copied '+str(len(actual))+' identical package files; standalone verifier and reporter passed')
print('skills@1.7.4 project-local installation smoke passed; no live agent behavior was measured.')
