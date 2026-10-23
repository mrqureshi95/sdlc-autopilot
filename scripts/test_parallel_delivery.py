"""Behavioral tests with temporary real Git worktrees; no network or dependencies."""
import hashlib
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get('PARALLEL_DELIVERY_SCRIPT', ROOT / 'skills/sdlc-autopilot/scripts/parallel_delivery.py'))


class ParallelDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='parallel delivery ')
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name).resolve()
        self.repo = self.directory / 'repository'
        self.repo.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.write(self.repo, '.gitignore', '.agent-output/\n')
        self.write(self.repo, 'src/a/start.txt', 'base A\n')
        self.write(self.repo, 'src/b/start.txt', 'base B\n')
        self.write(self.repo, 'shared/schema.txt', 'base contract\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'base fixture')
        self.base = self.git('rev-parse', 'HEAD')
        self.workers = [self.directory / 'worker a', self.directory / 'worker b']
        for index, worker in enumerate(self.workers):
            self.git('worktree', 'add', '-q', '-b', 'codex/worker-' + str(index), str(worker), self.base)
        self.plan = {
            'version': 1, 'base': self.base, 'gate': 'D08', 'shared_paths': ['shared'],
            'tasks': [dict(id='builder-' + str(i), owned_paths=['src/' + letter],
                           worktree=str(self.workers[i]), branch='codex/worker-' + str(i),
                           ports=[5100 + i], database='fixture_' + letter,
                           output_dir=str(self.workers[i] / '.agent-output'),
                           required_checks=[{'name': 'behavior', 'kind': 'test'}, {'name': 'build', 'kind': 'build'}]) for i, letter in enumerate(('a', 'b'))]
        }
        self.plan_file = self.directory / 'plan.json'
        self.report_file = self.directory / 'handoff.json'

    def git(self, *args, cwd=None):
        result = subprocess.run(['git', *args], cwd=cwd or self.repo, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def write(self, root, name, content):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def check(self, command='check-plan', report=None, live=False, raw=None):
        self.plan_file.write_text(raw if raw is not None else json.dumps(self.plan))
        args = [sys.executable, str(SCRIPT), command, '--plan', str(self.plan_file), '--repo', str(self.repo)]
        if live:
            args.append('--live')
        if command == 'check-handoff':
            self.report_file.write_text(json.dumps(report))
            args.extend(['--report', str(self.report_file)])
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        return result.returncode, output

    def denied(self, **kwargs):
        code, output = self.check(**kwargs)
        self.assertNotEqual(code, 0, output)
        self.assertEqual(output['status'], 'fail')
        return output

    def ready(self):
        worker = self.workers[0]
        self.write(worker, 'src/a/feature.txt', 'implemented behavior\n')
        self.git('add', '.', cwd=worker)
        self.git('commit', '-qm', 'feature fixture', cwd=worker)
        candidate = self.git('rev-parse', 'HEAD', cwd=worker)
        output = Path(self.plan['tasks'][0]['output_dir'])
        for name in ('behavior.log', 'build.log'):
            self.write(output, name, 'fixture evidence ' + name)
        return {
            'version': 1, 'task': 'builder-0', 'base': self.base, 'candidate': candidate, 'status': 'ready',
            'checks': [dict(name=name, kind=kind, status='passed', exit_code=0,
                            evidence=name + '.log', sha256=hashlib.sha256((output / (name + '.log')).read_bytes()).hexdigest(),
                            **({'tests': 2} if kind == 'test' else {})) for name, kind in [('behavior', 'test'), ('build', 'build')]],
            'blockers': [], 'risks': ['Fixture declaration; not an executed product test.']
        }

    def test_valid_plan_and_live_dispatch_with_real_worktrees(self):
        for live in (False, True):
            code, output = self.check(live=live)
            self.assertEqual(code, 0, output)
            self.assertEqual(output['status'], 'pass')
        self.assertIn('declaration', json.dumps(output).lower())

    def test_one_worker_and_no_ports_is_valid(self):
        self.plan['tasks'] = self.plan['tasks'][:1]
        self.plan['tasks'][0]['ports'] = []
        self.assertEqual(self.check(live=True)[0], 0)

    def test_plan_rejects_wrong_types_empty_values_and_invalid_commit(self):
        cases = [('version', True), ('version', 2), ('base', 'HEAD'), ('base', 'f' * 40),
                 ('gate', ''), ('gate', 'bad\nvalue'), ('shared_paths', 'shared'), ('tasks', []),
                 ('tasks', self.plan['tasks'] * 2)]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                original = self.plan[key]
                self.plan[key] = value
                self.denied()
                self.plan[key] = original

    def test_plan_rejects_unsafe_and_conflicting_ownership(self):
        for paths in (['/src/a'], ['src/../a'], ['src\\a'], ['.'], ['src//a'], ['src/a/'],
                      ['src/a\nsecret'], ['C:/src'], ['src/a\u0085secret'], ['.git/config'], [], ['src/a', 'src/a/child'], ['src/b'], ['shared/sub']):
            with self.subTest(paths=paths):
                self.plan['tasks'][0]['owned_paths'] = paths
                self.denied()
        self.plan['tasks'][0]['owned_paths'] = ['src']
        self.denied()
        self.plan['tasks'][0]['owned_paths'] = ['src/ab']
        self.assertEqual(self.check()[0], 0)

    def test_plan_rejects_shared_parent_and_overlapping_shared_paths(self):
        self.plan['shared_paths'] = ['src/a/contract']
        self.denied()
        self.plan['shared_paths'] = ['shared', 'shared/child']
        self.denied()

    def test_plan_rejects_duplicate_names_and_resources(self):
        for key in ('id', 'branch', 'ports', 'database', 'worktree', 'output_dir'):
            with self.subTest(key=key):
                previous = self.plan['tasks'][1][key]
                self.plan['tasks'][1][key] = self.plan['tasks'][0][key]
                self.denied()
                self.plan['tasks'][1][key] = previous
        for value in ([True], [0], [65536], [5100, 5100], ['5100']):
            self.plan['tasks'][0]['ports'] = value
            self.denied()
        self.plan['tasks'][0]['ports'] = []
        for key, value in [('database', ''), ('worktree', 'relative'), ('output_dir', str(self.directory)),
                           ('output_dir', str(self.workers[0])), ('required_checks', []),
                           ('required_checks', [{'name': 'build', 'kind': 'build'}, {'name': 'build', 'kind': 'test'}]),
                           ('required_checks', ['build']), ('required_checks', [{'name': 'behavior', 'kind': 'tests'}]), ('required_checks', [True]), ('branch', '-option')]:
            with self.subTest(key=key):
                previous = self.plan['tasks'][0][key]
                self.plan['tasks'][0][key] = value
                self.denied()
                self.plan['tasks'][0][key] = previous

    def test_live_rejects_dirty_missing_wrong_branch_or_moved_head(self):
        worker = self.workers[0]
        stray = self.write(worker, 'untracked.txt', 'not clean')
        self.denied(live=True)
        stray.unlink()
        self.git('switch', '-qc', 'different', cwd=worker)
        self.denied(live=True)
        self.git('switch', '-q', 'codex/worker-0', cwd=worker)
        self.ready()
        self.denied(live=True)
        self.plan['tasks'][0]['worktree'] = str(self.directory / 'missing')
        self.plan['tasks'][0]['output_dir'] = str(self.directory / 'missing' / '.agent-output')
        self.denied(live=True)

    def test_live_rejects_separate_repository_even_at_same_named_branch(self):
        worker = self.directory / 'foreign'
        subprocess.run(['git', 'clone', '-q', str(self.repo), str(worker)], check=True, capture_output=True)
        self.git('switch', '-qc', 'codex/worker-0', cwd=worker)
        self.plan['tasks'][0]['worktree'] = str(worker)
        self.plan['tasks'][0]['output_dir'] = str(worker / '.agent-output')
        self.denied(live=True)

    def test_valid_handoff_binds_actual_commit_changes_and_evidence(self):
        report = self.ready()
        code, output = self.check('check-handoff', report)
        self.assertEqual(code, 0, output)
        self.assertEqual(output['status'], 'pass')
        self.assertIn('declaration', json.dumps(output).lower())
        self.assertNotIn('fixture evidence behavior.log', json.dumps(output))

    def test_handoff_rejects_missing_failed_duplicate_or_zero_test_checks(self):
        report = self.ready()
        for mutation in ('missing', 'duplicate', 'failed', 'exit', 'bool_exit', 'zero', 'bool_tests', 'missing_count', 'inconclusive', 'unknown_kind'):
            with self.subTest(mutation=mutation):
                bad = json.loads(json.dumps(report))
                if mutation == 'missing': bad['checks'].pop()
                if mutation == 'duplicate': bad['checks'].append(bad['checks'][0])
                if mutation == 'failed': bad['checks'][0]['status'] = 'failed'
                if mutation == 'unknown_kind': bad['checks'][0]['kind'] = 'tests'
                if mutation == 'inconclusive': bad['checks'][0]['status'] = 'inconclusive'
                if mutation == 'exit': bad['checks'][0]['exit_code'] = 1
                if mutation == 'bool_exit': bad['checks'][0]['exit_code'] = False
                if mutation == 'zero': bad['checks'][0]['tests'] = 0
                if mutation == 'bool_tests': bad['checks'][0]['tests'] = True
                if mutation == 'missing_count': bad['checks'][0].pop('tests')
                self.denied(command='check-handoff', report=bad)

    def test_handoff_rejects_bad_identity_blockers_and_stale_head(self):
        report = self.ready()
        for key, value in [('version', True), ('task', 'unknown'), ('base', '0' * 40),
                           ('candidate', self.base), ('candidate', 'HEAD'), ('status', 'blocked'),
                           ('blockers', ['incomplete']), ('blockers', ''), ('risks', 'not a list')]:
            with self.subTest(key=key):
                bad = dict(report)
                bad[key] = value
                self.denied(command='check-handoff', report=bad)
        self.write(self.workers[0], 'src/a/later.txt', 'new revision')
        self.git('add', '.', cwd=self.workers[0])
        self.git('commit', '-qm', 'later', cwd=self.workers[0])
        self.denied(command='check-handoff', report=report)

    def test_handoff_rejects_dirty_checkout_and_committed_unowned_change(self):
        report = self.ready()
        self.write(self.workers[0], 'shared/schema.txt', 'unowned change')
        self.denied(command='check-handoff', report=report)
        self.git('add', '.', cwd=self.workers[0])
        self.git('commit', '-qm', 'unowned', cwd=self.workers[0])
        report['candidate'] = self.git('rev-parse', 'HEAD', cwd=self.workers[0])
        self.denied(command='check-handoff', report=report)

    def test_handoff_detects_unowned_source_of_rename(self):
        report = self.ready()
        self.git('mv', 'shared/schema.txt', 'src/a/moved.txt', cwd=self.workers[0])
        self.git('commit', '-qm', 'rename unowned', cwd=self.workers[0])
        report['candidate'] = self.git('rev-parse', 'HEAD', cwd=self.workers[0])
        self.denied(command='check-handoff', report=report)

    def test_handoff_rejects_evidence_tamper_missing_symlinks_and_escape(self):
        report = self.ready()
        output = Path(self.plan['tasks'][0]['output_dir'])
        evidence = output / 'behavior.log'
        evidence.write_text('changed evidence')
        self.denied(command='check-handoff', report=report)
        evidence.unlink()
        self.denied(command='check-handoff', report=report)
        outside = self.write(self.directory, 'outside.log', 'fixture evidence behavior.log')
        evidence.symlink_to(outside)
        self.denied(command='check-handoff', report=report)
        evidence.unlink()
        linked = output / 'linked'
        linked.symlink_to(self.directory, target_is_directory=True)
        for path in ('linked/outside.log', '../outside.log', str(outside)):
            report['checks'][0]['evidence'] = path
            self.denied(command='check-handoff', report=report)

    def test_handoff_rejects_output_directory_symlink(self):
        report = self.ready()
        output = Path(self.plan['tasks'][0]['output_dir'])
        relocated = self.directory / 'relocated'
        output.rename(relocated)
        output.symlink_to(relocated, target_is_directory=True)
        self.denied(command='check-handoff', report=report)

    def test_absolute_output_evidence_is_supported(self):
        report = self.ready()
        for record in report['checks']:
            record['evidence'] = str(Path(self.plan['tasks'][0]['output_dir']) / record['evidence'])
        self.assertEqual(self.check('check-handoff', report)[0], 0)

    def test_handoff_rejects_candidate_not_descended_from_plan_base(self):
        report = self.ready()
        worker = self.workers[0]
        tree = self.git('rev-parse', 'HEAD^{tree}', cwd=worker)
        unrelated = self.git('commit-tree', tree, '-m', 'unrelated root', cwd=worker)
        self.git('update-ref', 'HEAD', unrelated, cwd=worker)
        report['candidate'] = unrelated
        self.denied(command='check-handoff', report=report)

    def test_plan_rejects_dynamic_branch_expressions(self):
        self.git('switch', '-qc', 'another')
        self.git('switch', '-q', 'main')
        self.plan['tasks'][0]['branch'] = '@{-1}'
        self.denied()

    def test_invalid_cli_returns_json_without_untrusted_arguments(self):
        result = subprocess.run([sys.executable, str(SCRIPT), 'check-plan', '--bad=SECRET_ARGUMENT'], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip(), result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'fail')
        self.assertNotIn('SECRET_ARGUMENT', result.stdout)

    def test_live_rejects_filters_before_git_status_can_execute_them(self):
        marker = self.directory / 'filter executed'
        script = self.write(self.directory, 'clean filter.py',
                            'import pathlib,sys\npathlib.Path(' + repr(str(marker)) + ').write_text("ran")\nsys.stdout.write(sys.stdin.read())\n')
        self.git('config', 'filter.fixture.clean', shlex.quote(sys.executable) + ' ' + shlex.quote(str(script)))
        self.write(self.repo, '.git/info/attributes', 'src/a/start.txt filter=fixture\n')
        self.write(self.workers[0], 'src/a/start.txt', 'evil A\n')
        self.denied(live=True)
        self.assertFalse(marker.exists(), 'Read-only validation executed the configured filter')

    def test_attribute_sentinel_names_cannot_hide_active_filter_drivers(self):
        marker = self.directory / 'sentinel filter executed'
        script = self.write(self.directory, 'sentinel filter.py',
                            'import pathlib,sys\npathlib.Path(' + repr(str(marker)) + ').write_text("ran")\nsys.stdout.write(sys.stdin.read())\n')
        for driver in ('unset', 'unspecified'):
            with self.subTest(driver=driver):
                marker.unlink(missing_ok=True)
                self.git('config', 'filter.' + driver + '.clean', shlex.quote(sys.executable) + ' ' + shlex.quote(str(script)))
                self.write(self.repo, '.git/info/attributes', 'src/a/start.txt filter=' + driver + '\n')
                self.write(self.workers[0], 'src/a/start.txt', 'evil A\n')
                self.denied(live=True)
                self.assertFalse(marker.exists(), 'Attribute sentinel string hid executable filter')

    def test_inactive_configured_filter_does_not_block_clean_workers(self):
        marker = self.directory / 'inactive filter executed'
        self.git('config', 'filter.inactive.clean', 'touch ' + shlex.quote(str(marker)))
        self.assertEqual(self.check(live=True)[0], 0)
        self.assertFalse(marker.exists())

    def test_handoff_rejects_assume_unchanged_and_skip_worktree(self):
        report = self.ready()
        worker = self.workers[0]
        for flag in ('assume-unchanged', 'skip-worktree'):
            with self.subTest(flag=flag):
                self.git('update-index', '--' + flag, 'src/a/start.txt', cwd=worker)
                self.write(worker, 'src/a/start.txt', 'evil A\n')
                try:
                    self.denied(command='check-handoff', report=report)
                finally:
                    self.write(worker, 'src/a/start.txt', 'base A\n')
                    self.git('update-index', '--no-' + flag, 'src/a/start.txt', cwd=worker)

    def test_handoff_cannot_downgrade_required_test_to_lint(self):
        report = self.ready()
        report['checks'][0]['kind'] = 'lint'
        report['checks'][0]['tests'] = 0
        self.denied(command='check-handoff', report=report)

    def test_plan_binds_required_names_to_kinds(self):
        for task in self.plan['tasks']:
            task['required_checks'] = [{'name': 'behavior', 'kind': 'test'}, {'name': 'build', 'kind': 'build'}]
        self.assertEqual(self.check(live=True)[0], 0)

    def test_symlink_alias_of_worker_root_supports_relative_and_absolute_evidence(self):
        report = self.ready()
        alias = self.directory / 'worker alias'
        alias.symlink_to(self.workers[0], target_is_directory=True)
        task = self.plan['tasks'][0]
        task['worktree'] = str(alias)
        task['output_dir'] = str(alias / '.agent-output')
        self.assertEqual(self.check('check-handoff', report)[0], 0)
        for check in report['checks']:
            check['evidence'] = str(alias / '.agent-output' / check['evidence'])
        self.assertEqual(self.check('check-handoff', report)[0], 0)
        task['worktree'] = str(self.workers[0])
        self.assertEqual(self.check('check-handoff', report)[0], 0)

    def test_duplicate_json_keys_and_invalid_json_rejected_without_echoing_payload(self):
        self.denied(raw='{"version":1,"version":1}')
        secret = 'DO_NOT_ECHO_PAYLOAD_8736'
        result = self.denied(raw='{' + secret)
        self.assertNotIn(secret, json.dumps(result))


if __name__ == '__main__':
    unittest.main()
