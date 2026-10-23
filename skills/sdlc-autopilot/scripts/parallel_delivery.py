#!/usr/bin/env python3
"""Read-only plan/handoff checks. Never starts agents, runs tests, or grants assurance."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

KINDS = {'test', 'type', 'build', 'security', 'reference', 'tracker', 'review', 'lint', 'format'}
LIMITATION = 'Check statuses and test counts are declarations; file hashes do not prove execution, quality, security, or independent review.'


class Rejected(Exception):
    pass


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        raise Rejected('Invalid command arguments.')


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def text(value):
    return isinstance(value, str) and bool(value.strip()) and not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in value)


def integer(value):
    return type(value) is int


def sha(value):
    return isinstance(value, str) and re.fullmatch(r'(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})', value) is not None


def prefix(value):
    require(text(value) and '\\' not in value and not re.match(r'^[A-Za-z]:', value), 'Invalid repository-relative path.')
    path = PurePosixPath(value)
    require(bool(path.parts) and not path.is_absolute() and str(path) == value and not any(p in {'.', '..', '.git'} for p in path.parts),
            'Paths must be canonical relative prefixes without traversal or Git internals.')
    return value


def overlaps(a, b):
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')


def inside(child, parent):
    return child != parent and parent in child.parents


def absolute(value):
    require(text(value) and '\\' not in value and Path(value).is_absolute() and '..' not in Path(value).parts,
            'Resource paths must be absolute without traversal.')
    return Path(value)


def strings(value, label, allow_empty=False):
    require(isinstance(value, list) and (allow_empty or bool(value)) and all(text(item) for item in value), 'Invalid ' + label + '.')
    require(len(set(value)) == len(value), 'Duplicate ' + label + '.')
    return value


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON object key.')
            result[key] = value
        return result
    try:
        result = json.loads(Path(path).read_text(), object_pairs_hook=unique)
    except (ValueError, OSError, UnicodeError):
        raise Rejected('Cannot read valid JSON input.') from None
    require(isinstance(result, dict), 'JSON root must be an object.')
    return result


def git(root, *args, input_bytes=None):
    # Disable hooks/fsmonitor/external diff; do not run project code or expose Git stderr.
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1')
    try:
        result = subprocess.run(['git', '-C', str(root), '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null',
                                 *args], input=input_bytes, capture_output=True, env=env, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        raise Rejected('Git verification unavailable or timed out.') from None
    require(result.returncode == 0, 'Git verification failed.')
    return result.stdout.decode('utf-8', errors='strict').strip('\n')


def repository(root):
    root = Path(root).resolve()
    require(Path(git(root, 'rev-parse', '--show-toplevel')).resolve() == root, 'Expected a Git checkout root.')
    common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    return root, common


def commit(root, value):
    require(sha(value), 'Expected a full hexadecimal commit ID.')
    require(git(root, 'rev-parse', '--verify', value + '^{commit}').lower() == value.lower(), 'Expected an existing commit.')


def required_checks(task):
    checks = task.get('required_checks')
    require(isinstance(checks, list) and bool(checks), 'Task requires named and typed checks.')
    result = {}
    for check in checks:
        require(isinstance(check, dict) and text(check.get('name')) and isinstance(check.get('kind'), str) and
                check['kind'] in KINDS, 'Required checks must bind names to supported kinds.')
        require(check['name'] not in result, 'Duplicate required check name.')
        result[check['name']] = check['kind']
    return result


def worker_local(task, value):
    # Resolve aliases above the checkout (/tmp on macOS), preserving every
    # component below the checkout so evidence symlinks can still be rejected.
    path = absolute(value)
    worker = absolute(task['worktree']).resolve()
    for ancestor in reversed(path.parents):
        if ancestor.resolve() == worker:
            return worker / path.relative_to(ancestor)
    raise Rejected('Resource must be within its worker checkout.')


def worker_state(task, common, expected):
    worker, worker_common = repository(task['worktree'])
    require(worker_common == common, 'Worker must share the repository Git common directory.')
    require(git(worker, 'symbolic-ref', '--quiet', '--short', 'HEAD') == task['branch'], 'Worker is not on its assigned branch.')
    require(git(worker, 'rev-parse', 'HEAD').lower() == expected.lower(), 'Worker HEAD does not match the required commit.')
    index = git(worker, 'ls-files', '-v', '--stage', '-z').split('\0')
    require(all(row.startswith('H ') and not row.startswith('H 160000 ') for row in index if row),
            'Hidden index flags, sparse checkouts and submodules are unsupported.')
    paths = [row.split('\t', 1)[1] for row in index if row]
    attributes = git(worker, 'check-attr', '-z', '--stdin', 'filter',
                     input_bytes=('\0'.join(paths) + '\0').encode()).split('\0')
    filter_keys = git(worker, 'config', '--null', '--name-only', '--list').lower().split('\0')
    # A driver literally named 'unset'/'unspecified' is executable too; Git's
    # attribute display uses the same strings for absent/disabled attributes.
    require(all(value in {'unspecified', 'unset'} and not any(key.startswith('filter.' + value + '.') for key in filter_keys)
                for value in attributes[2::3]),
            'Active Git filters are unsupported: status could execute project code.')
    require(not git(worker, 'status', '--porcelain=v1', '--untracked-files=all', '--ignore-submodules=none'), 'Worker checkout must be clean.')
    return worker


def check_plan(plan, repo, live=False):
    require(integer(plan.get('version')) and plan['version'] == 1, 'Unsupported plan version.')
    root, common = repository(repo)
    commit(root, plan.get('base'))
    require(text(plan.get('gate')), 'Plan requires a gate.')
    shared = strings(plan.get('shared_paths'), 'shared paths', allow_empty=True)
    for item in shared:
        prefix(item)
    for index, item in enumerate(shared):
        require(not any(overlaps(item, other) for other in shared[:index]), 'Shared paths overlap.')
    tasks = plan.get('tasks')
    require(isinstance(tasks, list) and 1 <= len(tasks) <= 2, 'Plan requires one or two tasks.')
    ids, branches, ports, databases, worktrees, outputs, owners = set(), set(), set(), set(), [], [], []
    for task in tasks:
        require(isinstance(task, dict), 'Task must be an object.')
        for field, seen in [('id', ids), ('branch', branches), ('database', databases)]:
            value = task.get(field)
            require(text(value) and value == value.strip() and value not in seen, 'Invalid or duplicate task ' + field + '.')
            seen.add(value)
        require(git(root, 'check-ref-format', '--branch', task['branch']) == task['branch'], 'Branch must be a literal branch name.')
        owned = strings(task.get('owned_paths'), 'owned paths')
        for value in owned:
            prefix(value)
            require(not any(overlaps(value, other) for other in shared + owners), 'Ownership overlaps another task or shared path.')
            owners.append(value)
        allocated = task.get('ports')
        require(isinstance(allocated, list) and all(integer(p) and 1 <= p <= 65535 for p in allocated), 'Invalid worker ports.')
        require(len(set(allocated)) == len(allocated) and not ports.intersection(allocated), 'Worker ports overlap.')
        ports.update(allocated)
        worker = absolute(task.get('worktree')).resolve()
        require(worker != root and not inside(worker, root) and not inside(root, worker), 'Worker requires a separate checkout.')
        require(not any(worker == other or inside(worker, other) or inside(other, worker) for other in worktrees), 'Worker checkouts overlap.')
        worktrees.append(worker)
        output = worker_local(task, task.get('output_dir')).resolve()
        require(inside(output, worker) and '.git' not in output.relative_to(worker).parts, 'Output must be inside its worker checkout.')
        require(not any(output == other or inside(output, other) or inside(other, output) for other in outputs), 'Worker outputs overlap.')
        outputs.append(output)
        required_checks(task)
        if live:
            worker_state(task, common, plan['base'])
    return root, common


def evidence(task, record):
    declared = record.get('evidence')
    require(text(declared) and '\\' not in declared and '..' not in Path(declared).parts, 'Invalid evidence path.')
    worker = Path(task['worktree']).resolve()
    output = worker_local(task, task['output_dir'])
    target = worker_local(task, declared) if Path(declared).is_absolute() else output / declared
    require(inside(output, worker) and inside(target, output), 'Evidence must be within worker output.')
    # Check each component, not only the final file: intermediate symlinks also escape.
    current = worker
    for part in target.relative_to(worker).parts:
        current = current / part
        info = current.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'Evidence path contains a symlink.')
    require(stat.S_ISREG(target.lstat().st_mode), 'Evidence must be a regular file.')
    require(inside(target.resolve(), output.resolve()), 'Evidence escapes its output directory.')
    digest = record.get('sha256')
    require(isinstance(digest, str) and re.fullmatch(r'[0-9a-fA-F]{64}', digest), 'Invalid evidence SHA256.')
    value = hashlib.sha256()
    with target.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    require(value.hexdigest() == digest.lower(), 'Evidence SHA256 does not match.')


def check_handoff(plan, report, repo):
    root, common = check_plan(plan, repo)
    require(integer(report.get('version')) and report['version'] == 1, 'Unsupported handoff version.')
    require(text(report.get('task')), 'Handoff requires a task.')
    task = next((task for task in plan['tasks'] if task['id'] == report['task']), None)
    require(task is not None, 'Handoff task is not in the plan.')
    require(report.get('base') == plan['base'], 'Handoff base does not match the plan.')
    require(report.get('status') == 'ready' and report.get('blockers') == [], 'Handoff must be ready with no blockers.')
    if 'risks' in report:
        strings(report['risks'], 'risks', allow_empty=True)
    candidate = report.get('candidate')
    commit(root, candidate)
    worker = worker_state(task, common, candidate)
    git(worker, 'merge-base', '--is-ancestor', plan['base'], candidate)
    changed = git(worker, 'diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--name-only', '-z', plan['base'], candidate).split('\0')
    changed = [name for name in changed if name]
    require(bool(changed), 'Handoff has no committed task changes.')
    for name in changed:
        prefix(name)
        require(any(overlaps(name, owned) and (name == owned or name.startswith(owned + '/')) for owned in task['owned_paths']) and
                not any(overlaps(name, shared) for shared in plan['shared_paths']), 'Committed changes exceed task ownership.')
    checks = report.get('checks')
    require(isinstance(checks, list) and bool(checks), 'Handoff requires checks.')
    required = required_checks(task)
    names = set()
    for record in checks:
        require(isinstance(record, dict) and text(record.get('name')), 'Invalid handoff check.')
        require(record['name'] not in names, 'Duplicate handoff check.')
        names.add(record['name'])
        require(isinstance(record.get('kind'), str) and record['kind'] in KINDS, 'Unsupported check kind.')
        require(record.get('status') == 'passed' and integer(record.get('exit_code')) and record['exit_code'] == 0,
                'All checks must declare passed with exit code zero.')
        require(record['name'] not in required or record['kind'] == required[record['name']], 'Required check kind does not match the plan.')
        if record['kind'] == 'test':
            require(integer(record.get('tests')) and record['tests'] > 0, 'Test evidence requires a positive test count.')
        evidence(task, record)
    require(set(required).issubset(names), 'Required checks are missing.')
    return {'task': task['id'], 'candidate': candidate, 'changed_paths': len(changed), 'checks': len(names)}


def main():
    parser = JsonParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('check-plan', 'check-handoff'):
        child = commands.add_parser(command)
        child.add_argument('--plan', required=True)
        child.add_argument('--repo', required=True)
        if command == 'check-plan':
            child.add_argument('--live', action='store_true')
        else:
            child.add_argument('--report', required=True)
    try:
        args = parser.parse_args()
        plan = load(args.plan)
        if args.command == 'check-plan':
            check_plan(plan, args.repo, args.live)
            details = {'tasks': len(plan['tasks']), 'live': args.live}
        else:
            details = check_handoff(plan, load(args.report), args.repo)
        result, code = {'status': 'pass', **details, 'limitation': LIMITATION}, 0
    except (Rejected, OSError, ValueError, UnicodeError):
        # Reasons are controlled strings; never print untrusted JSON/Git output or file contents.
        reason = str(sys.exc_info()[1]) if isinstance(sys.exc_info()[1], Rejected) else 'Verification could not complete.'
        result, code = {'status': 'fail', 'reason': reason, 'limitation': LIMITATION}, 1
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
