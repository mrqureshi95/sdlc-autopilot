#!/usr/bin/env python3
"""Controlled before/after checks for evaluator-owned semantic oracles.
These hand-written patches test the harness, not an agent's success rate.
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
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-dir',type=Path,required=True)
args=p.parse_args()
if not h.validate_runtime(args.runtime_dir):p.error('Prepared locked runtime required')
results=[]
for fixture,oracle in [('15-python','pagination'),('14-deployment','health'),('16-self-verification','validation-strict'),('05-security','sql'),('11-high-risk-never-quick','sql')]:
    with tempfile.TemporaryDirectory(prefix='sdlc oracle controls ') as temp:
        work=Path(temp)/fixture;shutil.copytree(ROOT/'evals/fixtures'/fixture,work)
        (work/'node_modules').symlink_to(args.runtime_dir.resolve()/'node_modules',target_is_directory=True)
        before=h.run_oracle(ROOT,work,oracle,args.runtime_dir.resolve(),20)
        if oracle=='pagination':
            source=work/'pagination.py';source.write_text(source.read_text().replace('start = page * per_page','start = (page - 1) * per_page'))
        elif oracle=='health':
            source=work/'src/server.js';source.write_text(source.read_text().replace('res.status(201)','res.status(200)'))
        elif oracle=='validation-strict':
            source=work/'src/app.js';source.write_text(source.read_text().replace('  const result = req.body.text.toUpperCase();','  if (typeof req.body.text !== "string" || !req.body.text.trim() || req.body.text.length > 2000) return res.status(400).json({error:"Invalid text"});\n  const result = req.body.text.toUpperCase();'))
        elif oracle=='sql':
            source=work/'src/routes/auth.js';s=source.read_text()
            start=s.index('    const query =')
            end=s.index('    if (!user)',start)
            select='SELECT id, username, email, role FROM users WHERE username = ? AND password = ?' if fixture=='05-security' else 'SELECT id, username FROM users WHERE username = ? AND password = ?'
            s=s[:start]+'    const user = db.prepare('+json.dumps(select)+').get(username, password);\n\n'+s[end:]
            source.write_text(s)
        after=h.run_oracle(ROOT,work,oracle,args.runtime_dir.resolve(),20)
        results.append({'fixture':fixture,'oracle':oracle,'before':before,'after':after,'control_pass':before['state']=='fail' and after['state']=='pass'})
print(json.dumps({'evidence_type':'hand-written harness controls; not agent outcomes','results':results},indent=2))
sys.exit(0 if all(r['control_pass'] for r in results) else 1)
