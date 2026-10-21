#!/usr/bin/env python3
"""Local evidence collection. No network, package installation, or automatic fixes.

Exit 0: applicable required checks satisfied; 1: observed failure; 2: missing
required evidence. Neither exit 0 nor a scanner finding proves overall safety.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

VERSION = 1
HERE = Path(__file__).resolve().parent
MAX_FILE = 2 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def execute(argv, cwd, timeout=120, env=None):
    """Bound wall time, process group, and captured output even without GNU timeout."""
    started = time.monotonic()
    result = {'command': argv, 'cwd': str(cwd)}
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            p = subprocess.Popen(argv, cwd=cwd, stdout=out, stderr=err, start_new_session=True,
                                 env=env if env is not None else {**os.environ, 'CI': '1', 'GIT_TERMINAL_PROMPT': '0', 'PYTHONDONTWRITEBYTECODE': '1'})
        except OSError:
            return {**result, 'returncode': None, 'error': 'unavailable', 'stdout': '', 'stderr': ''}
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            result['error'] = 'timeout'
        finally:
            # Do not leave child watchers running after their parent has exited.
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        result.update(returncode=p.returncode, duration_seconds=round(time.monotonic()-started, 3))
        for name, handle in [('stdout', out), ('stderr', err)]:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(0)
            result[name] = handle.read(MAX_FILE).decode('utf-8', 'replace')
            if size > MAX_FILE:
                result['error'] = 'output-limit'
    return result


def git(root, *args):
    r = execute(['git', '--no-optional-locks', *args], root, 30)
    if r['returncode'] != 0 or r.get('error'):
        raise ValueError('Git command failed: ' + ' '.join(args[:2]))
    return r['stdout']


def git_bytes(root, *args):
    # NUL delimited paths must not pass through whitespace parsing or lossy decoding.
    p = subprocess.run(['git', '--no-optional-locks', *args], cwd=root,
                       capture_output=True, timeout=30)
    if p.returncode:
        raise ValueError('Git path collection failed')
    return p.stdout


def repo(cwd):
    try:
        root = Path(git(cwd, 'rev-parse', '--show-toplevel').rstrip('\n')).resolve()
        head = git(root, 'rev-parse', '--verify', 'HEAD').strip()
        branch = git(root, 'branch', '--show-current').strip() or None
        return root, head, branch
    except ValueError:
        return None, None, None


def paths(root):
    raw = git_bytes(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard')
    return sorted(set(os.fsdecode(p) for p in raw.split(b'\0') if p))


def within(root, relative):
    p = (root / relative).resolve()
    if not p.is_relative_to(root):
        raise ValueError('Path escapes project: ' + relative)
    return p



def valid_relative(path):
    return isinstance(path, str) and bool(path) and not Path(path).is_absolute() and '\0' not in path and not any(p in ('.', '..') for p in path.split('/'))


def linked_ancestor(root, path):
    if not valid_relative(path):
        raise ValueError('Invalid repository-relative path')
    cursor = root
    for part in Path(path).parts[:-1]:
        cursor = cursor / part
        if cursor.is_symlink():
            return True
    return False


def file_hash(root, path):
    if linked_ancestor(root, path):
        return 'unscanned:symlink-ancestor'
    p = root / path
    if p.is_symlink():
        return digest(os.fsencode(os.readlink(p)))
    if not p.exists():
        return None
    if not p.is_file():
        return 'non-file'
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()



def file_state(root, path):
    p = root / path
    if linked_ancestor(root, path):
        return {'sha256':None, 'kind':'unscanned-symlink-ancestor', 'executable':False}
    content_hash = file_hash(root, path)
    if content_hash is None:
        return None
    return {'sha256': content_hash, 'kind': 'symlink' if p.is_symlink() else 'regular' if p.is_file() else 'non-file',
            'executable': bool(p.lstat().st_mode & 0o111)}



def index_state(root):
    stages = git_bytes(root, 'ls-files', '--stage', '-z')
    flags = git_bytes(root, 'ls-files', '-v', '-z')
    return digest(stages + b'\0' + flags)


def masked_index_paths(root):
    masked = {}
    for entry in git_bytes(root, 'ls-files', '-v', '-z').split(b'\0'):
        if entry and (entry[:1].islower() or entry[:1].upper() == b'S'):
            masked[os.fsdecode(entry[2:])] = entry[:1].decode()
    return masked


def masked_changes(root):
    masked = masked_index_paths(root)
    if not masked:
        return []
    entries = {}
    for entry in git_bytes(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if entry:
            metadata, path = entry.split(b'\t', 1)
            mode, oid, stage = metadata.split()
            if stage == b'0':
                entries[os.fsdecode(path)] = (mode.decode(), oid.decode())
    changes = []
    for path, flag in masked.items():
        p = root / path
        if linked_ancestor(root, path):
            changes.append({'path':path, 'status':'M', 'old_path':None, 'source':'index-flag-unverified'})
            continue
        if not p.exists() and not p.is_symlink():
            if flag.upper() != 'S':  # Missing sparse-checkout paths are intentional.
                changes.append({'path':path, 'status':'D', 'old_path':None, 'source':'index-flag-comparison'})
            continue
        expected_mode, expected_oid = entries.get(path, ('', ''))
        if p.is_symlink():
            raw = os.fsencode(os.readlink(p))
            algorithm = 'sha256' if len(expected_oid)==64 else 'sha1'
            actual = hashlib.new(algorithm, b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            mode = '120000'
        elif p.is_file():
            actual = git(root, 'hash-object', '--no-filters', '--', path).strip()
            mode = '100755' if p.stat().st_mode & 0o111 else '100644'
        else:
            actual, mode = '', ''
        if (mode, actual) != (expected_mode, expected_oid):
            changes.append({'path':path, 'status':'M', 'old_path':None, 'source':'index-flag-comparison'})
    return changes


def selected_projects(root, requested):
    projects = []
    for relative in requested or ['.']:
        project = within(root, relative)
        if not project.is_dir():
            raise ValueError('Selected project is not an existing directory: '+relative)
        if project not in projects:
            projects.append(project)
    return projects


def change_list(root, base):
    parts = git_bytes(root, 'diff', '--name-status', '-z', '--find-renames', base, '--').split(b'\0')
    items = {}
    i = 0
    while i < len(parts) and parts[i]:
        status = os.fsdecode(parts[i]); i += 1
        path = os.fsdecode(parts[i]); i += 1
        old = None
        if status[0] in ('R', 'C'):
            old = path
            path = os.fsdecode(parts[i]); i += 1
        items[path] = {'path': path, 'status': status, 'old_path': old}
    for p in git_bytes(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
        if p:
            path = os.fsdecode(p)
            items[path] = {'path': path, 'status': '?', 'old_path': None}
    for c in masked_changes(root):
        items.setdefault(c['path'], c)
    return [items[p] for p in sorted(items)]


def choose_base(root, head, branch, explicit):
    if explicit:
        return git(root, 'rev-parse', '--verify', '--end-of-options', explicit + '^{commit}').strip(), 'explicit-ref'
    # Prefer the local remote-default identity; never fetch or guess the newest commit.
    candidates = []
    try:
        candidates.append(git(root, 'symbolic-ref', 'refs/remotes/origin/HEAD').strip())
    except ValueError:
        pass
    candidates += ['refs/heads/main', 'refs/heads/master']
    for candidate in candidates:
        try:
            base = git(root, 'merge-base', head, candidate).strip()
            return base, 'merge-base:' + candidate
        except ValueError:
            continue
    # No reliable branch base: HEAD is explicitly a worktree-only view, not a pass.
    return head, 'HEAD-only:branch-base-unknown'


def check(name, state, reason, required=True, **details):
    return {'name': name, 'state': state, 'required': required, 'reason': reason, **details}


def outcome(checks):
    if any(c['state'] == 'fail' for c in checks):
        return 'fail', 1
    if any(c['state'] == 'inconclusive' and c['required'] for c in checks):
        return 'inconclusive', 2
    if not any(c['state'] == 'pass' for c in checks):
        return 'not-applicable', 0
    return 'pass', 0


def snapshot(args):
    root, head, branch = repo(Path.cwd())
    if root is None:
        raise ValueError('Snapshot requires a Git repository with a HEAD commit')
    target = Path(args.output).resolve()
    if target.is_relative_to(root):
        raise ValueError('Store the baseline outside the target repository')
    data = {'version': VERSION, 'root': str(root), 'head': head, 'branch': branch,
            'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'files': {p: file_state(root, p) for p in paths(root)},
            'preexisting': [c['path'] for c in change_list(root, head)]}
    with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        json.dump(data, f, indent=2)
    return {'status': 'pass', 'baseline': str(target), 'sha256': digest(target.read_bytes())}, 0


def configuration(project, config_path=None):
    config = config_path or project / '.sdlc-checks.json'
    if config.is_symlink():
        raise ValueError('Checks configuration must not be a symlink')
    if not config.exists():
        return []
    data = json.loads(config.read_text())
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('checks'), list):
        raise ValueError('Invalid checks configuration')
    for c in data['checks']:
        if (not isinstance(c, dict) or c.get('kind') not in ['lint','format','type','test','security']
                or not isinstance(c.get('name'), str) or not isinstance(c.get('argv'), list)
                or not c['argv'] or not all(isinstance(x, str) and x for x in c['argv'])):
            raise ValueError('Invalid check entry')
        if not isinstance(c.get('cwd', '.'), str):
            raise ValueError('Invalid command cwd')
        within(project, c.get('cwd', '.'))
        if 'fix_argv' in c and (not isinstance(c['fix_argv'], list) or not c['fix_argv'] or not all(isinstance(x, str) and x for x in c['fix_argv']) or c['fix_argv'].count('{files}') != 1):
            raise ValueError('Invalid scoped fix argv')
        if c.get('runner', 'exit-only') not in ['node-test', 'pytest', 'unittest', 'jest-json', 'vitest-json', 'junit', 'exit-only']:
            raise ValueError('Unsupported test evidence adapter')
        if c.get('runner', 'exit-only') != 'exit-only' and c['kind'] != 'test':
            raise ValueError('Test evidence adapters require kind test')
    return data['checks']


def report_check(c, project, timeout):
    """Read an adapter-owned fresh report, never an existing coverage/result file."""
    runner = c['runner']
    argv = list(c['argv'])
    if runner == 'junit':
        if sum(a.count('{report}') for a in argv) != 1:
            raise ValueError('junit requires exactly one {report} output placeholder')
    elif any(a.startswith(('--outputFile', '--reporter', '--json', '--watch')) or a == '-w' for a in argv):
        raise ValueError('JSON adapter owns output/reporter/watch options')
    with tempfile.TemporaryDirectory(prefix='sdlc-fresh-report-') as temporary:
        report = Path(temporary) / ('results.xml' if runner == 'junit' else 'results.json')
        if runner == 'junit':
            argv = [a.replace('{report}', str(report)) for a in argv]
        elif runner == 'jest-json':
            argv += ['--json', '--outputFile='+str(report), '--watch=false', '--watchAll=false']
        else:
            argv += ['--run', '--reporter=json', '--outputFile='+str(report)]
        r = execute(argv, within(project, c.get('cwd', '.')), timeout)
        info = {k:v for k,v in r.items() if k not in ('stdout','stderr')}
        info['output_sha256'] = digest((r['stdout']+r['stderr']).encode())
        state, reason, count = 'inconclusive', 'missing, invalid, or inconsistent fresh runner report', None
        if r.get('error'):
            reason = r['error']
        elif report.is_file() and not report.is_symlink() and report.stat().st_size <= MAX_FILE:
            raw = report.read_bytes()
            info['report_sha256'] = digest(raw)
            try:
                text = raw.decode('utf-8')
                if runner == 'junit':
                    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
                        raise ValueError('XML declarations are unsupported')
                    root = ET.fromstring(text)
                    if root.tag not in ('testsuite','testsuites'):
                        raise ValueError('Unexpected JUnit root')
                    cases = list(root.iter('testcase'))
                    if not all(t.get('name','').strip() for t in cases):
                        raise ValueError('Unnamed JUnit cases')
                    failed = sum(t.find('failure') is not None or t.find('error') is not None for t in cases)
                    # Suite setup errors may exist without a testcase; never turn these green.
                    for suite in root.iter():
                        if suite.tag in ('testsuite','testsuites'):
                            for field in ('errors','failures','tests','skipped'):
                                value = suite.get(field,'0')
                                if not re.fullmatch(r'[0-9]+', value):
                                    raise ValueError('Invalid JUnit counter')
                                if field in ('errors','failures') and int(value) > 0:
                                    failed = max(failed, 1)
                    count = sum(t.find('skipped') is None and t.find('failure') is None and t.find('error') is None for t in cases)
                    good = True
                else:
                    data = json.loads(text)
                    if not isinstance(data, dict) or not isinstance(data.get('testResults'), list):
                        raise ValueError('Missing JSON test results')
                    cases = []
                    for suite in data['testResults']:
                        if not isinstance(suite, dict) or not isinstance(suite.get('assertionResults'), list):
                            raise ValueError('Missing assertion results')
                        cases += suite['assertionResults']
                    if not all(isinstance(t,dict) and isinstance(t.get('fullName'),str) and t['fullName'].strip() and t.get('status') in ('passed','failed','pending','skipped','todo','disabled') for t in cases):
                        raise ValueError('Invalid test case')
                    count = sum(t['status']=='passed' for t in cases)
                    failed = sum(t['status']=='failed' for t in cases)
                    good = (data.get('success') is True and type(data.get('numPassedTests')) is int
                            and data['numPassedTests']==count and type(data.get('numFailedTests')) is int
                            and data['numFailedTests']==failed)
                    if type(data.get('numFailedTests')) is int and data['numFailedTests'] > 0:
                        failed = max(failed, data['numFailedTests'])
                if failed:
                    state, reason = 'fail', 'fresh runner report observed test/suite failures'
                elif r['returncode']==0 and good and count > 0:
                    state, reason = 'pass', 'fresh report observed executed named cases; quality requires review'
            except (ValueError, TypeError, KeyError, AttributeError, ET.ParseError):
                count = None
        return check(c['name'], state, reason, count=count, kind='test', **info)


def run_check(c, project, timeout):
    if c.get('runner') in ('jest-json', 'vitest-json', 'junit'):
        return report_check(c, project, timeout)
    cwd = within(project, c.get('cwd', '.'))
    argv = list(c['argv'])
    runner = c.get('runner', 'exit-only')
    if runner == 'node-test':
        # Adapter owns the reporter; never accept a repository-written result artifact.
        if argv[:2] != ['node', '--test']:
            raise ValueError('node-test requires argv starting with node --test')
        if any(x.startswith('--test-reporter') for x in argv):
            raise ValueError('node-test reporter is managed by the adapter')
        argv.insert(2, '--test-reporter=' + str(HERE / 'node-test-reporter.mjs'))
    r = execute(argv, cwd, timeout)
    info = {k: v for k, v in r.items() if k not in ['stdout','stderr']}
    info['output_sha256'] = digest((r['stdout'] + r['stderr']).encode())
    # Output may contain secrets or hostile instructions; retain only digest and bounded facts.
    if r.get('error'):
        return check(c['name'], 'inconclusive', r['error'], kind=c['kind'], **info)
    if r['returncode'] != 0:
        return check(c['name'], 'fail', 'command returned nonzero; inspect locally for cause', kind=c['kind'], **info)
    if c['kind'] != 'test':
        return check(c['name'], 'pass', 'configured command exited zero (scope is command-defined)', kind=c['kind'], **info)
    count = None
    if runner == 'node-test':
        reports = re.findall(r'^SDLC_NODE_EVIDENCE (.+)$', r['stdout'], re.M)
        if reports:
            facts = json.loads(reports[-1])
            count = facts.get('passed', 0)
            if facts.get('failed', 0):
                return check(c['name'], 'fail', 'runner observed test failures', kind='test', **info)
    elif runner == 'unittest':
        summary = re.search(r'Ran (\d+) tests? in ', r['stderr'])
        if summary and re.search(r'^OK(?: \(.*\))?$', r['stderr'], re.M):
            not_passed = sum(int(n) for n in re.findall(r'(?:skipped|expected failures)=(\d+)', r['stderr']))
            count = max(0, int(summary[1]) - not_passed)
    elif runner == 'pytest':
        matches = re.findall(r'\b(\d+) passed\b', r['stdout'])
        if matches:
            count = int(matches[-1])
    state = 'pass' if isinstance(count, int) and count > 0 else 'inconclusive'
    return check(c['name'], state, 'observed executed tests; quality requires review' if state=='pass'
                 else 'no positive supported test count; zero/opaque execution is unverified',
                 count=count, kind='test', **info)


def project_checks(project):
    configured = configuration(project)
    if (project / '.sdlc-checks.json').exists():
        return configured
    # Deliberately narrow fallback. Do not infer arbitrary npm scripts, download tools,
    # descend into unrelated packages, or run files such as latest_data.js.
    root, _, _ = repo(project)
    tests = []
    if root:
        for p in paths(root):
            full = root / p
            if not linked_ancestor(root, p) and full.is_relative_to(project) and full.is_file() and not full.is_symlink():
                rel = full.relative_to(project)
                if re.search(r'\.(?:test|spec)\.(?:mjs|cjs|js)$', rel.name):
                    tests.append('./' + str(rel))
    if tests:
        return [{'name':'tests', 'kind':'test', 'argv':['node','--test', *tests], 'runner':'node-test'}]
    return []


# These are review candidates, not a security scanner or a proof of exploitability.
CANDIDATES = [
    ('credential-literal', re.compile(r'''(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*[=:]\s*["'][^"'\n]{8,}["']''')),
    ('private-key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('provider-token', re.compile(r'\b(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,})\b')),
    ('dynamic-evaluation', re.compile(r'\beval\s*\(|\bnew\s+Function\s*\(')),
    ('unsafe-html-sink', re.compile(r'\.innerHTML\s*=|dangerouslySetInnerHTML')),
]


def scan(root, changes, context_digest):
    findings = []
    unscanned = []
    for c in changes:
        if linked_ancestor(root, c['path']):
            unscanned.append(c['path']); continue
        p = root / c['path']
        if not p.exists() and not p.is_symlink():
            continue
        if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_FILE:
            unscanned.append(c['path']); continue
        raw = p.read_bytes()
        if b'\0' in raw:
            unscanned.append(c['path']); continue
        for number, line in enumerate(raw.decode('utf-8', 'replace').splitlines(), 1):
            for name, pattern in CANDIDATES:
                if pattern.search(line):
                    findings.append({'path':c['path'], 'line':number, 'rule':name,
                                     'fingerprint':digest((context_digest+'\0'+c['path']+'\0'+name+'\0'+str(number)+'\0'+digest(raw)+'\0'+line).encode())})
    return findings, unscanned, sum(1 for c in changes if c['path'] not in unscanned and (root/c['path']).is_file())


def verify(args):
    cwd = Path.cwd().resolve()
    root, head, branch = repo(cwd)
    result = {'version': VERSION, 'mode': args.mode, 'task': args.task, 'checks': [], 'changes': [],
              'human_review': 'Task adequacy, regression intent, contracts, security context, suppressions, and residual risk are not proved by this helper.',
              'provenance': {'invocation':sys.argv, 'cwd':str(cwd), 'root':str(root) if root else None, 'head':head, 'branch':branch}}
    checks = result['checks']
    if not root:
        checks.append(check('repository', 'inconclusive', 'No Git HEAD; diff provenance unavailable'))
        return result, 2
    base, method = choose_base(root, head, branch, args.base)
    result['provenance'].update(base=base, base_selection=method,
        diff_command=['git','diff','--name-status','-z','--find-renames',base,'--'],
        untracked_command=['git','ls-files','--others','--exclude-standard','-z'])
    projects = selected_projects(root, args.project)
    changes = change_list(root, base)
    result['provenance']['index_sha256'] = index_state(root)
    result['provenance']['index_masked_paths'] = sorted(masked_index_paths(root))
    if any(c.get('source')=='index-flag-unverified' for c in changes):
        checks.append(check('index-flags', 'inconclusive', 'Masked paths traverse symlinks; inspect without changing user flags'))
    hashes = {p:file_state(root,p) for p in paths(root)}
    result['provenance']['worktree_sha256'] = digest(json.dumps(hashes, sort_keys=True).encode())
    checks.append(check('diff-provenance', 'inconclusive' if method.startswith('HEAD-only') else 'pass', method))
    baseline = None
    if args.baseline:
        raw = Path(args.baseline).read_bytes()
        baseline = json.loads(raw)
        if (not isinstance(baseline, dict) or baseline.get('version') != VERSION or baseline.get('root') != str(root)
                or not isinstance(baseline.get('head'), str) or not re.fullmatch(r'[0-9a-f]{40,64}', baseline['head'])
                or not isinstance(baseline.get('files'), dict) or not isinstance(baseline.get('preexisting'), list)
                or not all(valid_relative(p) for p in baseline['preexisting'])
                or not all(valid_relative(p) and (state is None or isinstance(state, dict) and set(state)=={'sha256','kind','executable'}) for p,state in baseline['files'].items())):
            raise ValueError('Baseline does not match repository or schema')
        git(root, 'merge-base', '--is-ancestor', baseline['head'], head)
        result['provenance']['baseline_sha256'] = digest(raw)
        result['provenance']['baseline_head'] = baseline['head']
        # Include changed-since-snapshot paths even if the net branch diff is empty.
        known = {c['path'] for c in changes}
        for p in sorted(set(hashes) | set(baseline['files'])):
            if hashes.get(p) != baseline['files'].get(p) and p not in known:
                changes.append({'path':p, 'status':'D' if hashes.get(p) is None else 'M', 'old_path':None})
    for c in changes:
        c['file_state'] = hashes.get(c['path'])
        c['sha256'] = c['file_state']['sha256'] if c['file_state'] else None
        if baseline:
            changed = c['file_state'] != baseline['files'].get(c['path'])
            c['attribution'] = ('mixed-preexisting' if c['path'] in baseline['preexisting'] else 'changed-since-snapshot') if changed else 'preexisting'
        else:
            c['attribution'] = 'unknown:no-task-start-snapshot'
    result['changes'] = changes
    checks.append(check('attribution', 'pass' if baseline else 'inconclusive',
                        'Path-level only; mixed files require hunk review' if baseline else 'No task-start baseline; do not assign ownership', required=False))
    findings, unscanned, scanned_count = scan(root, changes, result['provenance']['worktree_sha256'])
    decisions = []
    if args.review_decisions:
        raw = Path(args.review_decisions).read_bytes()
        decisions = json.loads(raw)
        if not isinstance(decisions, list) or any(not isinstance(d, dict) or
            d.get('disposition') not in ['false-positive', 'test-fixture', 'accepted-risk'] or
            not isinstance(d.get('fingerprint'), str) or
            not isinstance(d.get('reason'), str) or len(d['reason'].strip()) < 12 for d in decisions):
            raise ValueError('Invalid contextual review decisions')
        if len({d['fingerprint'] for d in decisions}) != len(decisions):
            raise ValueError('Duplicate review decision fingerprint')
        current = {f['fingerprint'] for f in findings}
        if any(d['fingerprint'] not in current for d in decisions):
            raise ValueError('Stale or unmatched review decision; re-review current candidates')
        result['provenance']['review_decisions_sha256'] = digest(raw)
    by_fingerprint = {d['fingerprint']:d['disposition'] for d in decisions}
    for f in findings:
        f['review_disposition'] = by_fingerprint.get(f['fingerprint'], 'unreviewed')
    unresolved = [f for f in findings if f['review_disposition']=='unreviewed']
    accepted = [f for f in findings if f['review_disposition']=='accepted-risk']
    result['review_candidates'] = findings
    result['unscanned_paths'] = unscanned
    checks.append(check('pattern-review', 'fail' if unresolved else 'inconclusive' if accepted else 'pass' if scanned_count else 'not-applicable',
                        'Unreviewed/risk-accepted candidates; contextual decisions are human/agent claims' if unresolved or accepted else 'Contextual decisions recorded; not independent security evidence' if findings else 'No bundled-pattern matches in readable changed files; not a security clearance',
                        scanned_scope='whole current changed files (not repository audit)', scanned_files=scanned_count, unscanned_count=len(unscanned)))
    # Read-only review inspects evidence but does not demand implementation or run code.
    if args.task == 'review':
        checks.append(check('execution', 'not-applicable', 'Read-only review: no implementation or test execution required'))
    else:
        behavioral = args.task != 'cosmetic' and args.mode != 'quick'
        for project in projects:
            project_name = str(project.relative_to(root))
            project_results = []
            for c in project_checks(project):
                observation = run_check(c, project, args.timeout)
                observation['project'] = project_name
                project_results.append(observation)
            if behavioral and not any(c.get('kind')=='test' for c in project_results):
                project_results.append(check('tests', 'inconclusive', 'No configured or supported test command for this project', kind='test', project=project_name))
            if args.mode == 'full' and behavioral and not any(c.get('kind')=='security' for c in project_results):
                project_results.append(check('security-tooling', 'inconclusive', 'No configured maintained security check for this project; manual review is separate', project=project_name))
            checks.extend(project_results)
        final_root, final_head, final_branch = repo(cwd)
        if final_root != root:
            checks.append(check('worktree-stability', 'inconclusive', 'Repository identity changed during commands'))
        else:
            final_hashes = {p:file_state(root,p) for p in paths(root)}
            final_digest = digest(json.dumps(final_hashes, sort_keys=True).encode())
            final_index = index_state(root)
            result['provenance'].update(final_worktree_sha256=final_digest, final_index_sha256=final_index,
                                        final_head=final_head, final_branch=final_branch)
            drift = sorted(p for p in set(hashes)|set(final_hashes) if hashes.get(p)!=final_hashes.get(p))
            stable = not drift and head==final_head and branch==final_branch and result['provenance']['index_sha256']==final_index
            checks.append(check('worktree-stability', 'pass' if stable else 'inconclusive',
                                'Observed inputs unchanged after commands' if stable else 'Commands changed files or Git state; input evidence does not verify the final state. Inspect drift before rerunning.',
                                changed_paths=drift))
    checks.append(check('coverage', 'not-applicable', 'Existing coverage files are not consumed; use a fresh scoped command and review exact paths', required=False))
    if os.environ.get('SDLC_STRICT_INVERSION') == '1':
        checks.append(check('inversion', 'inconclusive', 'Automatic inversion unsupported; see verify-inversion.sh'))
    result['status'], rc = outcome(checks)
    return result, rc


def detect(args):
    cwd = Path.cwd().resolve()
    root, head, branch = repo(cwd)
    projects = []
    for project in selected_projects(root or cwd, args.project):
        languages = [lang for name,lang in [('package.json','javascript'),('pyproject.toml','python'),('requirements.txt','python'),('go.mod','go'),('Cargo.toml','rust'),('Gemfile','ruby'),('pom.xml','java'),('build.gradle','java'),('build.gradle.kts','java')] if (project/name).exists()]
        checks = configuration(project)
        projects.append({'path':str(project), 'language': languages[0] if languages else None,
                         'languages':sorted(set(languages)), 'checks':[
                             {'name':c['name'], 'kind':c['kind'], 'configured':True,
                              'available':shutil.which(c['argv'][0], path=os.environ.get('PATH')) is not None if '/' not in c['argv'][0] else os.access(within(project,c.get('cwd','.'))/c['argv'][0],os.X_OK),
                              'runnable':'unverified until executed', 'command':c['argv']} for c in checks]})
    return {'version':VERSION, 'status':'pass', 'git':{'root':str(root) if root else None,'head':head,'branch':branch},
            'projects':projects, 'note':'Explicit project scopes; no recursive monorepo discovery or deployment inference'}, 0


def gates(args):
    root, _, _ = repo(Path.cwd())
    root = root or Path.cwd().resolve()
    checks = []
    if args.fix and not args.file:
        raise ValueError('--fix requires explicit --file scope')
    for project in selected_projects(root, args.project):
        for c in configuration(project):
            if args.fix:
                # Fix adapters are explicit argv arrays with a mandatory scope placeholder.
                argv = c.get('fix_argv')
                if not argv or argv.count('{files}') != 1:
                    continue
                if any(linked_ancestor(project,f) or (project/f).is_symlink() for f in args.file):
                    raise ValueError('Fix scope must not traverse symlinks')
                scoped = [within(project,f) for f in args.file]
                if any(not p.is_file() or p.is_symlink() for p in scoped):
                    raise ValueError('Fix scope must contain regular files, not directories or symlinks')
                files = [str(p) for p in scoped]
                c = {**c, 'argv':[part for x in argv for part in (files if x=='{files}' else [x])]}
            checks.append(run_check(c, project, args.timeout))
    if not checks:
        checks.append(check('configured-gates', 'inconclusive', 'No configured runnable checks for selected projects'))
    status, rc = outcome(checks)
    return {'version':VERSION, 'status':status, 'checks':checks}, rc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    snap = sub.add_parser('snapshot'); snap.add_argument('--output', required=True)
    for name in ['verify','detect','gates']:
        p = sub.add_parser(name)
        p.add_argument('--json', action='store_true')
        p.add_argument('--project', action='append')
        p.add_argument('--timeout', type=float, default=120)
        if name == 'verify':
            p.add_argument('mode', choices=['quick','standard','full'])
            p.add_argument('--task', choices=['implementation','cosmetic','review'], default='implementation')
            p.add_argument('--base'); p.add_argument('--baseline'); p.add_argument('--review-decisions')
        if name == 'gates':
            p.add_argument('--fix', action='store_true'); p.add_argument('--file', action='append')
    args = parser.parse_args()
    try:
        if hasattr(args,'timeout') and not 0 < args.timeout <= 3600:
            raise ValueError('timeout must be positive and at most 3600 seconds')
        result, rc = {'snapshot':snapshot,'verify':verify,'detect':detect,'gates':gates}[args.action](args)
        if 'status' not in result:
            result['status'] = 'inconclusive'
        if getattr(args,'json',False) or args.action in ['snapshot','detect']:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        else:
            for c in result.get('checks',[]):
                print(f"[{c['state'].upper()}] {c['name']}: {c['reason']}")
            print('Result: '+result['status']+' (scoped evidence only; no readiness guarantee)')
        return rc
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'version':VERSION,'status':'inconclusive','error':str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
