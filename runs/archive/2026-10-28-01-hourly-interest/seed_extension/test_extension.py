"""18次扩种监督器的禁网假进程检查；不启动引擎或对真实PID发信号。"""
from copy import deepcopy
from datetime import timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('extension_test_control', HERE / 'run_extension.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.extension, self.workspace = self.home / 'seed_extension', self.home / 'workspace'
        self.extension.mkdir(); self.workspace.mkdir()
        guard = patch.multiple(control, HERE=self.extension, PLAN=self.extension / 'runtime_plan.json',
                               STATE=self.extension / 'batch_execution.json')
        guard.start(); self.addCleanup(guard.stop)
        for target in ('socket.socket.connect', 'socket.create_connection'):
            guard = patch(target, side_effect=AssertionError('离线检查禁止网络'))
            guard.start(); self.addCleanup(guard.stop)
        for name in ('kill', 'killpg'):
            guard = patch.object(control.os, name, side_effect=AssertionError('离线检查禁止真实信号'))
            guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.subprocess, 'Popen', side_effect=AssertionError('离线检查禁止真实CLI'))
        guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.signal, 'signal')
        guard.start(); self.addCleanup(guard.stop)
        created = control.now() - timedelta(minutes=5)
        env = self.extension / 'fixture.env'
        env.write_text('AGENTSOCIETY_LLM_MODEL=fixture-model\nAGENTSOCIETY_LLM_API_KEY=offline-fixture\nAGENTSOCIETY_LLM_API_BASE=https://offline.invalid/v1\n')
        source = self.workspace / 'guarded.py'; source.write_text('pass\n')
        self.plan = dict(execution_authorized=True, workspace=str(self.workspace), python='offline-python',
                         env_file=str(env), requested_model='fixture-model',
                         expected_returned_model='deepseek-v4-1-flash-261017',
                         api_base_sha256=hashlib.sha256(b'https://offline.invalid/v1').hexdigest(),
                         created_at=created.isoformat(), deadline_at=(created + timedelta(hours=48)).isoformat(),
                         max_wall_hours=48, max_parallel_runs=2,
                         decision_opportunities=19800, extra_requests_limit=1980,
                         body_outer_requests_limit=21780, ledger_path=str(self.extension / 'extra_attempts.count'),
                         source_sha256={str(source): control.digest(source)}, runs=[], reuse_runs=[])
        for seed in range(1, 10):
            for algorithm in ('random', 'interest'):
                run_id = f'hourly_return_v1_{algorithm}_s{seed}'
                configuration = self.extension / 'configs' / f'{run_id}.json'
                steps = self.extension / 'steps.yaml'
                steps.write_text('fixture: true\n')
                save(configuration, dict(env_modules=[dict(kwargs=dict(
                    recommendation_algorithm=algorithm, random_seed=seed, arrival_agent_return_policy='next_batch'))],
                    agents=[dict(kwargs=dict(content_retry_budget=dict(limit=1980,
                        ledger_path=self.plan['ledger_path']))) for _ in range(100)]))
                self.plan['runs'].append(dict(algorithm=algorithm, seed=seed, run_id=run_id,
                                             config=str(configuration), steps=str(steps),
                                             run_dir=str(self.workspace / 'runs' / run_id)))
        for algorithm in ('random', 'interest'):
            directory = self.workspace / 'pilot' / algorithm
            record = directory / 'fixture.json'; save(record, {'completed': True})
            self.plan['reuse_runs'].append(dict(algorithm=algorithm, seed=0, run_id=f'pilot_{algorithm}_s0',
                                               run_dir=str(directory), raw_sha256={'fixture.json': control.digest(record)}))
        save(control.PLAN, self.plan)
        self.summary = dict(agent_files=100, decisions=20, unique_decisions=20, posted=2,
                            requests=20, action_failures=0, service_failures=0,
                            posted_model_failures=0, invalid_publications=0,
                            response_models={'deepseek-v4-1-flash-261017': 2})

    def test_matrix_strictly_covers_seed1_to9_random_interest(self):
        rows = control.matrix(self.plan)
        self.assertEqual([(r['seed'], r['algorithm']) for r in rows],
                         [(seed, arm) for seed in range(1, 10) for arm in ('random', 'interest')])
        for seed, algorithm in ((0, 'random'), (1, 'chronological'), (1, 'no_b')):
            invalid = deepcopy(self.plan)
            invalid['runs'][0].update(seed=seed, algorithm=algorithm)
            with self.assertRaises(RuntimeError): control.matrix(invalid)
        for invalid in (dict(self.plan, runs=self.plan['runs'][:-1]),
                        dict(self.plan, runs=[self.plan['runs'][0]] + self.plan['runs'][:-1])):
            with self.assertRaises(RuntimeError): control.matrix(invalid)

    def test_pending_does_not_repeat_done_or_active_or_reuse(self):
        runs = control.matrix(self.plan)
        pending = control.pending_runs(runs, [runs[0]], [runs[1]])
        self.assertEqual(pending, runs[2:])
        self.assertFalse(any(r['seed'] == 0 or r['algorithm'] == 'chronological' for r in pending))

    def test_shared_budget_counts_both_slots_and_completed(self):
        done, active = [{'requests': 100}], [{'agent_summary': {'requests': 20}}, {'agent_summary': {'requests': 30}}]
        self.assertEqual(control.enforce_budget(self.plan, done, active, 7), 150)
        for body, extra in ((21781, 0), (0, 1981), (0, -1)):
            with self.assertRaises(RuntimeError): control.enforce_budget(self.plan, [{'requests': body}], [], extra)

    def test_command_identity_matches_all_arguments_and_rejects_zombie(self):
        expected = ['/fake/python', '/known/run.py', '--start-authorized']
        good = SimpleNamespace(returncode=0, stdout='Ss /fake/python /known/run.py --start-authorized\n')
        with patch.object(control.subprocess, 'run', return_value=good):
            self.assertTrue(control.command_matches(9001, expected))
            self.assertFalse(control.command_matches(9001, ['/fake/python', '/known/run.py', '--status']))
            self.assertFalse(control.command_matches(9001, ['/fake/python', '/other/run.py', '--start-authorized']))
        zombie = SimpleNamespace(returncode=0, stdout='Z /fake/python /known/run.py --start-authorized\n')
        with patch.object(control.subprocess, 'run', return_value=zombie):
            self.assertFalse(control.command_matches(9001, expected))

    def test_stop_never_signals_foreign_pid(self):
        entry = dict(child_pid=9001, command=['/fake/python', '--run-dir', 'ours'], _process=None)
        with patch.object(control, 'engine_alive', return_value=True), \
                patch.object(control, 'command_matches', return_value=False), \
                patch.object(control.os, 'killpg') as kill:
            control.signal_engines([entry], signal.SIGINT)
        kill.assert_not_called()

    def test_source_and_reused_seed0_hash_changes_are_rejected(self):
        control.frozen_sources(self.plan)
        source = Path(next(iter(self.plan['source_sha256'])))
        source.write_text('changed\n')
        with self.assertRaises(RuntimeError): control.frozen_sources(self.plan)
        final = dict(steps=693, actions=1100, posted=2)
        with patch.object(control, 'final_result', return_value=final):
            self.assertEqual(len(control.validate_reuse(self.plan)), 2)
            reused = Path(self.plan['reuse_runs'][0]['run_dir']) / 'fixture.json'
            reused.write_text('{"completed": false}')
            with self.assertRaises(RuntimeError): control.validate_reuse(self.plan)

    def test_stop_cli_rejects_foreign_controller_without_signal(self):
        save(control.STATE, dict(status='running', supervisor_pid=9001,
                                controller_command=['offline-python', 'ours.py', '--start-authorized']))
        with patch.object(sys, 'argv', ['ours.py', '--stop']), \
                patch.object(control, 'command_matches', return_value=False), \
                patch.object(control.os, 'kill') as kill:
            with self.assertRaises(RuntimeError): control.main()
        kill.assert_not_called()

    def test_stop_cli_signals_only_matching_controller(self):
        expected = ['offline-python', 'ours.py', '--start-authorized']
        save(control.STATE, dict(status='running', supervisor_pid=9001, controller_command=expected))
        with patch.object(sys, 'argv', ['ours.py', '--stop']), \
                patch.object(control, 'command_matches', return_value=True) as matches, \
                patch.object(control.os, 'kill') as kill, patch.object(control.os, 'killpg') as groups:
            control.main()
        matches.assert_called_once_with(9001, expected)
        kill.assert_called_once_with(9001, signal.SIGTERM)
        groups.assert_not_called()

    def run_loop(self, failure=False):
        phase = dict(cycle=0, stopped=False, max_active=0)
        launched, sent = [], []
        original_write = control.write
        def record(path, value):
            if Path(path) == control.STATE:
                phase['max_active'] = max(phase['max_active'], len(value.get('active_runs', [])))
            original_write(path, value)
        def launch(command, **kwargs):
            directory = Path(command[command.index('--run-dir') + 1])
            launched.append(directory.name)
            class Fake:
                pid = 5000 + len(launched)
                returncode = 0
                def poll(self): return None
            return Fake()
        launched_at = {}
        def alive(entry):
            if phase['stopped']: return False
            if failure: return True
            launched_at.setdefault(entry['run_id'], phase['cycle'])
            return phase['cycle'] < launched_at[entry['run_id']] + 1
        def summary(directory, **kwargs):
            row = dict(self.summary)
            if failure and phase['cycle']: row['service_failures'] = 1
            return row, set(), {}
        def stop(entries, sig):
            sent.append(([row['run_id'] for row in entries], sig)); phase['stopped'] = True
        def final(directory, run, expected):
            return dict(run_id=run['run_id'], algorithm=run['algorithm'], seed=run['seed'],
                        run_dir=str(directory), requests=20, posted=2, steps=693, actions=1100, weeks=11,
                        expected_returned_model=expected)
        with patch.object(control, 'preflight', return_value=(self.plan, self.workspace,
                Path(self.plan['ledger_path']), {})), \
                patch.object(control, 'engine_alive', side_effect=alive), \
                patch.object(control, 'agent_summary', side_effect=summary), \
                patch.object(control, 'progress', return_value={}), \
                patch.object(control, 'frozen_sources'), \
                patch.object(control, 'final_result', side_effect=final), \
                patch.object(control, 'signal_engines', side_effect=stop), \
                patch.object(control, 'command_matches', return_value=True), \
                patch.object(control, 'write', side_effect=record), \
                patch.object(control.subprocess, 'Popen', side_effect=launch), \
                patch.object(control.time, 'sleep', side_effect=lambda _: phase.update(cycle=phase['cycle'] + 1)):
            successful = control.supervise(0)
        return successful, phase, launched, sent, control.read(control.STATE)

    def test_two_slots_complete_exact18_without_restarting_or_counting_seed0(self):
        before = control.PLAN.read_bytes()
        successful, phase, launched, sent, state = self.run_loop()
        self.assertTrue(successful)
        self.assertEqual(launched, [Path(r['run_dir']).name for r in self.plan['runs']])
        self.assertEqual(phase['max_active'], 2)
        self.assertEqual(len(state['completed']), 18)
        self.assertEqual({r['run_id'] for r in state['completed']}, {r['run_id'] for r in self.plan['runs']})
        self.assertEqual(state['total_body_requests'], 360)
        self.assertEqual(state['extra_requests_used'], 0)
        self.assertEqual(state['deadline_at'], self.plan['deadline_at'])
        self.assertEqual(control.PLAN.read_bytes(), before)
        self.assertEqual(sent, [])

    def test_failure_stops_two_slots_and_never_starts_next_seed(self):
        successful, phase, launched, sent, state = self.run_loop(failure=True)
        self.assertFalse(successful)
        self.assertEqual(launched, [Path(r['run_dir']).name for r in self.plan['runs'][:2]])
        self.assertEqual(phase['max_active'], 2)
        self.assertEqual(set(sent[0][0]), {r['run_id'] for r in self.plan['runs'][:2]})
        self.assertEqual(state['status'], 'stopped')
        self.assertEqual(state['completed'], [])
        self.assertFalse(Path(self.plan['runs'][2]['run_dir']).exists())

    def test_expired_deadline_blocks_start_before_any_signal(self):
        plan = deepcopy(self.plan)
        plan['deadline_at'] = (control.now() - timedelta(seconds=1)).isoformat()
        with patch.object(control.os, 'kill') as kill, patch.object(control.os, 'killpg') as groups:
            with self.assertRaisesRegex(RuntimeError, '截止|48|时限'):
                control.preflight(plan)
        kill.assert_not_called(); groups.assert_not_called()

    def test_existing_state_ledger_and_run_directory_refuse_duplicate_start(self):
        for target in (control.STATE, Path(self.plan['ledger_path']), Path(self.plan['runs'][0]['run_dir'])):
            with self.subTest(target=target):
                if target == Path(self.plan['runs'][0]['run_dir']): target.mkdir(parents=True)
                else: target.write_text('{}')
                try:
                    with self.assertRaisesRegex(RuntimeError, '已有|存在|重复|账本'):
                        control.preflight(self.plan)
                finally:
                    if target.is_dir(): target.rmdir()
                    else: target.unlink()


if __name__ == '__main__':
    unittest.main(verbosity=2)
