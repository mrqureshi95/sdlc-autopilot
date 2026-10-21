#!/usr/bin/env python3
"""Replay supplied patches, not an autonomous agent campaign.

Default is read-only artifact validation. --execute opts into running supplied code
in disposable directories; that is NOT an OS sandbox. Use trusted local patches
or an external no-network/no-credentials sandbox for adversarial code.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('sdlc_evidence', ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
evidence = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(evidence)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_sha(root):
    return hashlib.sha256(json.dumps({str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*'))
                                    if p.is_file() and not p.is_symlink() and not any(part in ['__pycache__','.git','node_modules'] for part in p.relative_to(root).parts) and p.suffix != '.pyc'},sort_keys=True).encode()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_schema(data, schema):
    """Enforce the small closed metadata schema; fail on unsupported constraints."""
    supported={'$schema','title','type','required','properties','additionalProperties','minimum','minLength','enum'}
    if set(schema)-supported:
        return ['unsupported schema constraint']
    types={'object':dict,'string':str,'integer':int}
    if schema.get('type') not in types or type(data) is not types[schema['type']]:
        return ['invalid field type']
    errors=[]
    if isinstance(data,dict):
        errors += ['missing '+k for k in schema.get('required',[]) if k not in data]
        properties=schema.get('properties',{})
        if schema.get('additionalProperties') is False:
            errors += ['unexpected '+k for k in data if k not in properties]
        for k in data.keys() & properties.keys():
            errors += [k+': '+e for e in validate_schema(data[k],properties[k])]
    if 'enum' in schema and data not in schema['enum']:
        errors.append('not in enum')
    if 'minimum' in schema and data<schema['minimum']:
        errors.append('below minimum')
    if 'minLength' in schema and len(data.strip())<schema['minLength']:
        errors.append('empty string')
    return errors


def validate_meta(case, meta):
    errors=validate_schema(meta, load_json(ROOT/'evals/agent-run.schema.json'))
    if isinstance(meta,dict):
        if meta.get('eval_id')!=case['id']:
            errors.append('eval_id mismatch')
        if meta.get('mode')!=case['expected_mode']:
            errors.append('mode differs from scenario expectation; human review may assess rationale')
    return errors


def transcript_check(check, transcript):
    if not transcript or not transcript.strip():
        return 'inconclusive','Transcript absent; absence of forbidden text is not evidence'
    present=check['value'].casefold() in transcript.casefold()
    passes=not present if check['type']=='transcript_not_contains' else present
    return ('pass' if passes else 'fail'), 'Text-presence check only, not behavioral evidence'


def command(argv,cwd,timeout):
    # Remove provider/cloud credentials and isolate HOME. This is hygiene, not a sandbox.
    safe_env={k:v for k,v in os.environ.items() if k in ['PATH','SYSTEMROOT','TMPDIR','LANG']}
    safe_env.update(HOME=str(cwd), CI='1', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                    GIT_TERMINAL_PROMPT='0', PYTHONDONTWRITEBYTECODE='1')
    return evidence.execute(argv,cwd,timeout,env=safe_env)


def observed(r):
    return {k:v for k,v in r.items() if k not in ['stdout','stderr']} | {
        'output_sha256':hashlib.sha256((r['stdout']+r['stderr']).encode()).hexdigest()}


def validate_workspace(work):
    for p in work.rglob('*'):
        if p.is_symlink():
            raise ValueError('Symlinks in supplied workspace are not accepted')
        if p.name=='.git' and p!=work/'.git':
            raise ValueError('Nested repositories are not accepted')


def git(work,*args):
    r=command(['git',*args],work,30)
    if r['returncode']!=0 or r.get('error'):
        raise ValueError('Git operation failed: '+' '.join(args[:2]))
    return r['stdout'].rstrip('\n')


def validate_runtime(runtime):
    if runtime is None:
        return False
    try:
        return (runtime/'node_modules/vitest/vitest.mjs').is_file() and sha(runtime/'package-lock.json')==sha(ROOT/'evals/runtime/package-lock.json')
    except OSError:
        return False


def run_oracle(repo_root, work, name, runtime, timeout):
    if name not in ['pagination','sql','health','validation','validation-strict']:
        return {'name':name,'state':'inconclusive','reason':'No semantic oracle implemented'}
    if name!='pagination' and not validate_runtime(runtime):
        return {'name':name,'state':'inconclusive','reason':'Prepared locked runtime required'}
    oracle=repo_root/'evals/oracles'/('pagination.py' if name=='pagination' else 'api.cjs')
    with tempfile.TemporaryDirectory(prefix='sdlc completion ') as temp:
        completion=Path(temp)/'completion.json'
        nonce=secrets.token_hex(24)
        argv=([sys.executable,str(oracle),str(work),str(completion),nonce] if name=='pagination'
              else ['node',str(oracle),str(work),name,str(completion),nonce])
        r=command(argv,work,timeout)
        state='inconclusive'
        completion_hash=None
        if not r.get('error') and completion.is_file() and not completion.is_symlink() and completion.stat().st_size<4096:
            try:
                facts=load_json(completion)
                claimed=facts.get('state')
                if (facts.get('version')==1 and facts.get('oracle')==name and facts.get('nonce')==nonce
                        and claimed in ['pass','fail','inconclusive']
                        and r['returncode']=={'pass':0,'fail':1,'inconclusive':2}[claimed]):
                    state=claimed
                    completion_hash=sha(completion)
            except (ValueError,AttributeError):
                pass
        return {'name':name,'state':state,'oracle_sha256':sha(oracle),
                'completion_sha256':completion_hash,
                'trust':'Trusted-patch replay only; completion shares the evaluated process and is not malicious-code attestation',
                **observed(r)}


def evaluate_case(repo_root, case, run_dir, execute=False, runtime=None, timeout=60):
    result={'id':case['id'],'name':case['name'],'status':'inconclusive','errors':[],
            'semantic':[],'text_checks':[], 'human_judgment':{'state':'pending','criteria':case.get('assertions',[])}}
    meta_path=run_dir/'meta.json'; patch=run_dir/'patch.diff'; transcript=run_dir/'transcript.md'
    result['provenance']={'generated_by':'sdlc replay harness v2','started_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                          'python':platform.python_version(),'platform':platform.platform(),
                          'skill_tree_sha256':tree_sha(repo_root/'skills/sdlc-autopilot'),
                          'harness_sha256':sha(Path(__file__)), 'schema_sha256':sha(repo_root/'evals/agent-run.schema.json')}
    try:
        if not meta_path.is_file() or not patch.is_file():
            raise ValueError('meta.json and patch.diff are required')
        if max(meta_path.stat().st_size,patch.stat().st_size)>2*1024*1024:
            raise ValueError('Artifact size limit exceeded')
        result['errors']+=validate_meta(case,load_json(meta_path))
        result['provenance'].update(patch_sha256=sha(patch),metadata_sha256=sha(meta_path),
                                    transcript_sha256=sha(transcript) if transcript.is_file() else None)
        if result['errors']:
            result['status']='fail';return result
        for c in case.get('text_checks',[]):
            state,reason=transcript_check(c,transcript.read_text() if transcript.is_file() else None)
            result['text_checks'].append({'state':state,'reason':reason})
        fixture=repo_root/'evals'/case['fixture']
        result['provenance']['fixture_sha256']=tree_sha(fixture)
        if not execute:
            result['reason']='Artifact structure only; --execute required for semantic replay'
            return result
        with tempfile.TemporaryDirectory(prefix='sdlc replay ') as temp:
            work=Path(temp)/'workspace'
            shutil.copytree(fixture,work)
            validate_workspace(work)
            # Infrastructure is installed/ignored before the baseline. No npm install here.
            (work/'.gitignore').write_text('node_modules/\n.eval-runtime/\n*.db\n__pycache__/\n')
            git(work,'init','-q','-b','main');git(work,'config','user.email','eval@example.invalid')
            git(work,'config','user.name','SDLC Harness');git(work,'add','.')
            git(work,'commit','-qm','fixture baseline')
            base=git(work,'rev-parse','HEAD')
            result['provenance'].update(workspace=str(work),base=base)
            if patch.stat().st_size:
                git(work,'apply','--check',str(patch.resolve()))
                git(work,'apply','--whitespace=nowarn',str(patch.resolve()))
            validate_workspace(work)
            # Link trusted runtime only after rejecting patch-created symlinks.
            if validate_runtime(runtime):
                (work/'node_modules').symlink_to(runtime/'node_modules',target_is_directory=True)
                (work/'.eval-runtime').symlink_to(runtime,target_is_directory=True)
                # Workspace dependency for the planted monorepo import defect.
                shared=work/'packages/shared'
                if shared.is_dir():
                    scope=work/'packages/dashboard/node_modules/@monorepo'
                    scope.mkdir(parents=True)
                    (scope/'shared').symlink_to(shared,target_is_directory=True)
                result['provenance']['runtime_lock_sha256']=sha(runtime/'package-lock.json')
            result['provenance']['changed_paths']=[c['path'] for c in evidence.change_list(work,base)]
            result['provenance']['node_version']=command(['node','--version'],work,10)['stdout'].strip()
            for name in case.get('oracles',[]):
                result['semantic'].append(run_oracle(repo_root,work,name,runtime,timeout))
            if not result['semantic']:
                result['semantic'].append({'state':'inconclusive','reason':'Scenario requires human evaluation; no semantic oracle'})
            states=[c['state'] for c in result['semantic']+result['text_checks']]
            result['status']='fail' if 'fail' in states else 'inconclusive' if 'inconclusive' in states else 'executable-pass'
            # This status never clears the separate pending human judgments.
        return result
    except (ValueError,OSError,KeyError,TypeError) as exc:
        result['errors'].append(str(exc));result['status']='fail';return result
    finally:
        result['provenance']['finished_at']=dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs-dir',type=Path,required=True);p.add_argument('--eval-id',type=int)
    p.add_argument('--execute',action='store_true');p.add_argument('--runtime-dir',type=Path)
    p.add_argument('--timeout',type=float,default=60)
    args=p.parse_args()
    if not 0<args.timeout<=3600:
        p.error('timeout must be positive and at most 3600 seconds')
    cases=[c for c in load_json(ROOT/'evals/evals.json')['evals'] if args.eval_id is None or c['id']==args.eval_id]
    if not cases:p.error('No matching evals')
    results=[]
    for case in cases:
        candidates=[args.runs_dir/f"{case['id']}-{case['name']}",args.runs_dir/str(case['id']),args.runs_dir/case['name']]
        run_dir=next((x for x in candidates if x.is_dir()),candidates[0])
        results.append(evaluate_case(ROOT,case,run_dir,args.execute,args.runtime_dir,args.timeout))
    print(json.dumps({'evidence_type':'artifact replay; no agent behavior pass rate','results':results},indent=2))
    return 1 if any(r['status']=='fail' for r in results) else 2 if any(r['status']=='inconclusive' for r in results) else 0


if __name__=='__main__':
    sys.exit(main())
