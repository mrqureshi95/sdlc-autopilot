#!/usr/bin/env python3
"""Structure and referential integrity only; does not evaluate agent behavior."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'evals/evals.json').read_text())
cases=data['evals'];errors=[]
if [c['id'] for c in cases]!=list(range(1,len(cases)+1)):errors.append('non-sequential IDs')
if len({c['name'] for c in cases})!=len(cases):errors.append('duplicate names')
for c in cases:
    fixture=(ROOT/'evals'/c['fixture']).resolve()
    if not fixture.is_relative_to(ROOT/'evals/fixtures') or not fixture.is_dir():errors.append(f"{c['id']}: missing/escaped fixture")
    if c['expected_mode'] not in ['quick','standard','full']:errors.append(f"{c['id']}: invalid mode")
    if not c.get('assertions') or not all(isinstance(x,str) and x.strip() for x in c['assertions']):errors.append(f"{c['id']}: missing human criteria")
    if 'machine_checks' in c:errors.append(f"{c['id']}: obsolete self-report checks")
    for name in c.get('oracles',[]):
        if name not in ['pagination','sql','health','validation','validation-strict']:errors.append(f"{c['id']}: unknown oracle")
    for check in c.get('text_checks',[]):
        if check.get('type') not in ['transcript_not_contains','transcript_contains'] or not isinstance(check.get('value'),str):errors.append(f"{c['id']}: invalid text check")
for p in (ROOT/'evals/fixtures').rglob('package.json'):
    d=json.loads(p.read_text())
    if 'react-scripts' in json.dumps(d):errors.append(str(p)+': undeclared CRA runner')
    for deps in ['dependencies','devDependencies']:
        if any(not k.startswith('@monorepo/') for k in d.get(deps,{})):errors.append(str(p)+': dependencies must use locked central runtime')
lock=json.loads((ROOT/'evals/runtime/package-lock.json').read_text())
package=json.loads((ROOT/'evals/runtime/package.json').read_text())
if lock['packages']['']['dependencies']!=package['dependencies']:errors.append('runtime lock differs from manifest')
for name,version in package['dependencies'].items():
    if not version[0].isdigit() or any(x in version for x in ['^','~','>','*',' ']):errors.append('unpinned runtime dependency '+name)
print(json.dumps({'evidence_type':'structure only','scenarios':len(cases),'with_semantic_oracles':sum(bool(c.get('oracles')) for c in cases),'errors':errors},indent=2))
sys.exit(1 if errors else 0)
