"""两路交接的禁网假进程验收；不向真实进程发信号，不启动CLI。"""
from copy import deepcopy
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('hourly_parallel_test', HERE / 'run_parallel.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class ParallelTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.pilot, self.workspace = self.home / 'pilot', self.home / 'workspace'
        self.pilot.mkdir(); self.workspace.mkdir()
        self.guard = patch.multiple(control, HERE=self.pilot, PLAN=self.pilot / 'runtime_plan.json',
                                    STATE=self.pilot / 'batch_execution.json',
                                    REVISION=self.pilot / 'parallel_revision.json',
                                    HISTORY=self.pilot / 'parallel_handoff')
        self.guard.start(); self.addCleanup(self.guard.stop)
        for target in ('socket.socket.connect', 'socket.create_connection'):
            guard = patch(target, side_effect=AssertionError('测试禁止网络'))
            guard.start(); self.addCleanup(guard.stop)
        for name in ('kill', 'killpg'):
            guard = patch.object(control.os, name, side_effect=AssertionError('禁止真实进程信号'))
            guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.subprocess, 'Popen', side_effect=AssertionError('禁止真实CLI启动'))
        guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.signal, 'signal')
        guard.start(); self.addCleanup(guard.stop)
        self.summary = dict(agent_files=100, decisions=20, unique_decisions=20, posted=2,
                            requests=20, action_failures=0, service_failures=0,
                            posted_model_failures=0, invalid_publications=0,
                            response_models={'returned-v1': 2})
        ledger = self.pilot / 'extra_attempts.count'
        ledger.write_text('7')
        start = control.now() - timedelta(minutes=30)
        env_file = self.pilot / 'fixture.env'
        env_file.write_text('AGENTSOCIETY_LLM_MODEL=offline-model\nAGENTSOCIETY_LLM_API_KEY=offline-fixture\nAGENTSOCIETY_LLM_API_BASE=https://offline.invalid/v1\n')
        self.plan = dict(execution_authorized=True, workspace=str(self.workspace),
                         python='offline-python', env_file=str(env_file), requested_model='offline-model',
                         api_base_sha256=control.digest(env_file),
                         expected_returned_model=None, source_sha256={},
                         deadline_at=(start + timedelta(hours=8)).isoformat(), max_wall_hours=8,
                         decision_opportunities=3300, extra_requests_limit=330,
                         body_outer_requests_limit=3630, ledger_path=str(ledger), runs=[])
        import hashlib
        self.plan['api_base_sha256'] = hashlib.sha256(b'https://offline.invalid/v1').hexdigest()
        for algorithm in ('random', 'chronological', 'interest'):
            configuration = self.pilot / f'{algorithm}.json'
            save(configuration, dict(env_modules=[dict(kwargs=dict(
                recommendation_algorithm=algorithm, random_seed=0, arrival_agent_return_policy='next_batch'))],
                agents=[dict(kwargs=dict(content_retry_budget=dict(limit=330, ledger_path=str(ledger))))
                        for _ in range(100)]))
            self.plan['runs'].append(dict(algorithm=algorithm, seed=0, run_id=f'pilot_{algorithm}',
                                         config=str(configuration), steps='steps.yaml',
                                         run_dir=str(self.workspace / 'runs' / algorithm)))
        random = self.plan['runs'][0]
        Path(random['run_dir']).mkdir(parents=True)
        self.previous = dict(status='running', supervisor_pid=2001, started_at=start.isoformat(),
                             updated_at=start.isoformat(), deadline_at=self.plan['deadline_at'],
                             completed=[], expected_returned_model='returned-v1',
                             extra_requests_used=7, total_body_requests=20,
                             active_run=dict(random, child_pid=2002, command=['fake', random['run_dir']]))
        self.revision = dict(execution_authorized=True, authorization='offline fixture', max_parallel=2,
                             runtime_plan_sha256='', controller_sha256=control.digest(Path(control.__file__)),
                             deadline_at=self.plan['deadline_at'], decision_opportunities=3300,
                             extra_requests_limit=330, body_outer_requests_limit=3630,
                             expected_returned_model='returned-v1')
        self.freeze()

    def freeze(self):
        save(control.PLAN, self.plan)
        self.revision['runtime_plan_sha256'] = control.digest(control.PLAN)
        self.previous['runtime_plan_sha256'] = self.revision['runtime_plan_sha256']
        save(control.REVISION, self.revision)
        save(control.STATE, self.previous)

    def test_parent_only_handoff_keeps_engine_and_ledger(self):
        sent = []
        def alive(pid, expected):
            return not (pid == 2001 and any(sig == signal.SIGHUP for _, sig in sent))
        with patch.object(control, 'process_matches', side_effect=alive), \
                patch.object(control, 'agent_summary', return_value=(self.summary, set(), {})), \
                patch.object(control, 'progress', return_value={'SOCIETY_STEP.json': {'step_count': 450}}), \
                patch.object(control.subprocess, 'check_output', return_value='2002 2001 agentsociety2.society.cli fake\n'), \
                patch.object(control.os, 'kill', side_effect=lambda pid, sig: sent.append((pid, sig))), \
                patch.object(control.os, 'killpg') as groups, patch.object(control.time, 'sleep'):
            previous = control.release_serial(self.plan, self.previous)
        self.assertEqual(previous['active_run']['child_pid'], 2002)
        self.assertEqual(sent, [(2001, signal.SIGSTOP), (2001, signal.SIGHUP), (2001, signal.SIGCONT)])
        groups.assert_not_called()
        self.assertEqual(Path(self.plan['ledger_path']).read_text(), '7')
        self.assertEqual(control.read(control.PLAN), self.plan)

    def test_foreign_parent_pid_is_not_signalled(self):
        with patch.object(control, 'process_matches', return_value=False), \
                patch.object(control.os, 'kill') as kill, patch.object(control.os, 'killpg') as groups:
            with self.assertRaises(RuntimeError):
                control.release_serial(self.plan, self.previous)
        kill.assert_not_called(); groups.assert_not_called()

    def test_foreign_engine_pid_is_not_signalled(self):
        item = dict(run_id='pilot_random', child_pid=2002, run_dir=self.plan['runs'][0]['run_dir'],
                    _process=None)
        with patch.object(control, 'process_matches', return_value=False), \
                patch.object(control.os, 'killpg') as groups:
            control.signal_engines([item], signal.SIGINT)
        groups.assert_not_called()

    def run_loop(self, failure=False):
        phase = dict(cycle=0, stopped=False, max_active=0)
        launched, sent = [], []
        real_write = control.write
        def record(path, value):
            if Path(path) == control.STATE:
                phase['max_active'] = max(phase['max_active'], len(value.get('active_runs', [])))
            real_write(path, value)
        def launch(command, **kwargs):
            directory = Path(command[command.index('--run-dir') + 1])
            launched.append(directory.name)
            class Process:
                pid = 2002 + len(launched)
                returncode = 0
                def poll(self): return None
            return Process()
        def alive(item):
            if phase['stopped']:
                return False
            if failure:
                return True
            finish = {'pilot_random': 1, 'pilot_chronological': 2, 'pilot_interest': 3}[item['run_id']]
            return phase['cycle'] < finish
        def inspect(directory, **kwargs):
            summary = dict(self.summary)
            if failure and phase['cycle']:
                summary['service_failures'] = 1
            return summary, set(), {}
        def stop(active, sig):
            sent.append(([item['child_pid'] for item in active], sig))
            phase['stopped'] = True
        def final(directory, run, expected):
            return dict(run_id=run['run_id'], algorithm=run['algorithm'], run_dir=str(directory),
                        requests=20, steps=693, actions=1100, weeks=11, posted=2,
                        expected_returned_model=expected)
        with patch.object(control, 'preflight', return_value=(self.plan, self.revision, self.previous, {})), \
                patch.object(control, 'release_serial', return_value=deepcopy(self.previous)), \
                patch.object(control, 'engine_alive', side_effect=alive), \
                patch.object(control, 'agent_summary', side_effect=inspect), \
                patch.object(control, 'progress', return_value={}), \
                patch.object(control, 'frozen_sources'), \
                patch.object(control, 'final_result', side_effect=final), \
                patch.object(control, 'signal_engines', side_effect=stop), \
                patch.object(control, 'write', side_effect=record), \
                patch.object(control.subprocess, 'Popen', side_effect=launch), \
                patch.object(control.time, 'sleep', side_effect=lambda _: phase.update(cycle=phase['cycle'] + 1)):
            completed = control.supervise(0)
        return completed, phase, launched, sent, control.read(control.STATE)

    def test_two_slots_adopt_without_duplicate_and_preserve_deadline(self):
        plan_bytes = control.PLAN.read_bytes()
        completed, phase, launched, sent, state = self.run_loop()
        self.assertTrue(completed)
        self.assertEqual(launched, ['chronological', 'interest'])
        self.assertEqual(phase['max_active'], 2)
        self.assertEqual({row['run_id'] for row in state['completed']},
                         {row['run_id'] for row in self.plan['runs']})
        self.assertEqual(len(state['completed']), 3)
        self.assertEqual(state['started_at'], self.previous['started_at'])
        self.assertEqual(state['deadline_at'], self.plan['deadline_at'])
        self.assertEqual(state['total_body_requests'], 60)
        self.assertEqual(state['extra_requests_used'], 7)
        self.assertEqual(Path(self.plan['ledger_path']).read_text(), '7')
        self.assertEqual(control.PLAN.read_bytes(), plan_bytes)
        self.assertEqual(sent, [])

    def test_failure_stops_two_slots_and_does_not_start_third(self):
        completed, phase, launched, sent, state = self.run_loop(failure=True)
        self.assertFalse(completed)
        self.assertEqual(launched, ['chronological'])
        self.assertEqual(phase['max_active'], 2)
        self.assertEqual(sent[0], ([2002, 2003], signal.SIGINT))
        self.assertEqual(state['status'], 'stopped')
        self.assertEqual(state['completed'], [])
        self.assertFalse(Path(self.plan['runs'][2]['run_dir']).exists())
        self.assertEqual(Path(self.plan['ledger_path']).read_text(), '7')

    def test_budget_includes_done_and_both_active_and_rejects_overflow(self):
        done = [dict(requests=40)]
        active = [dict(agent_summary=dict(requests=20)), dict(agent_summary=dict(requests=30))]
        self.assertEqual(control.enforce_budget(self.plan, done, active, 7), 90)
        for requests, extra in ((3631, 7), (0, 331), (0, -1)):
            with self.assertRaises(RuntimeError):
                control.enforce_budget(self.plan, [dict(requests=requests)], [], extra)

    def test_expired_original_deadline_blocks_handoff_without_signals(self):
        self.plan['deadline_at'] = (control.now() - timedelta(seconds=1)).isoformat()
        self.revision['deadline_at'] = self.plan['deadline_at']
        self.freeze()
        with patch.object(control.os, 'kill') as kill, patch.object(control.os, 'killpg') as groups:
            with self.assertRaisesRegex(RuntimeError, '截止'):
                control.preflight()
        kill.assert_not_called(); groups.assert_not_called()
        self.assertEqual(Path(self.plan['ledger_path']).read_text(), '7')


if __name__ == '__main__':
    unittest.main(verbosity=2)
