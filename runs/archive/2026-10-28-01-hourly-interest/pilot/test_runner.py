"""假进程验收单seed控制器；禁止网络与真实引擎启动。"""
from datetime import timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hourly_pilot_runner_test', HERE / 'run_pilot.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve()
        self.pilot = self.home / 'pilot'
        self.workspace = self.home / 'workspace'
        self.pilot.mkdir(); self.workspace.mkdir()
        self.guard = patch.multiple(runner, HERE=self.pilot, PLAN=self.pilot / 'runtime_plan.json',
                                    STATE=self.pilot / 'batch_execution.json')
        self.guard.start(); self.addCleanup(self.guard.stop)
        self.signal_guard = patch.object(runner.signal, 'signal')
        self.signal_guard.start(); self.addCleanup(self.signal_guard.stop)
        self.net_guard = patch('socket.socket.connect', side_effect=AssertionError('测试禁止网络'))
        self.net_guard.start(); self.addCleanup(self.net_guard.stop)
        service = 'https://offline.invalid/v1'
        env = self.pilot / 'test.env'
        env.write_text(f'AGENTSOCIETY_LLM_MODEL=offline-model\nAGENTSOCIETY_LLM_API_KEY=offline-fixture\nAGENTSOCIETY_LLM_API_BASE={service}\n')
        self.plan = dict(execution_authorized=True, workspace=str(self.workspace),
            python='offline-python', env_file=str(env), requested_model='offline-model',
            api_base_sha256=hashlib.sha256(service.encode()).hexdigest(), expected_returned_model=None,
            deadline_at=(runner.now() + timedelta(hours=8)).isoformat(),
            source_sha256={}, decision_opportunities=3300, extra_requests_limit=330,
            body_outer_requests_limit=3630, ledger_path=str(self.pilot / 'extra_attempts.count'), runs=[])
        for algorithm in runner.ALGORITHMS:
            config_path = self.pilot / f'{algorithm}.json'
            save(config_path, dict(env_modules=[dict(kwargs=dict(arrival_agent_return_policy='next_batch',
                random_seed=0, recommendation_algorithm=algorithm))], agents=[dict(kwargs=dict(
                    content_retry_budget=dict(limit=330, ledger_path=self.plan['ledger_path']))) for _ in range(100)]))
            self.plan['runs'].append(dict(algorithm=algorithm, seed=0, run_id=f'pilot_{algorithm}',
                config=str(config_path), steps='steps.yaml', run_dir=f'runs/{algorithm}'))
        save(runner.PLAN, self.plan)

    def process(self, model='returned-v1', failed=False):
        def fake(command, **kwargs):
            directory = Path(command[command.index('--run-dir') + 1])
            rows = []
            for aid in range(1, 101):
                decisions = []
                for week in sorted(runner.WEEKS):
                    published = aid == 1 and week == '2026-W12'
                    row = dict(week=week, reason='published' if published else 'below_threshold',
                               posted=published, generation_attempts=int(published))
                    if published:
                        row.update(content='离线测试正文', post_id=1, response_model=model,
                                   generation_status='service_failed' if failed else 'service_success')
                    decisions.append(row)
                    rows.append(dict(agent_id=str(aid), week=week, candidate_future=0,
                                     acted_at='2026-03-16T10:00:00+08:00', feed=[]))
                save(directory / f'agents/agent_{aid:04d}/AGENT.json', dict(id=aid, decision_log=decisions))
            save(directory / 'pid.json', dict(status='completed'))
            save(directory / 'SOCIETY_STEP.json', dict(step_count=693))
            save(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json', {
                '_arrival_agent_return_policy': 'next_batch', '_arrival_state':dict(actions=rows,
                    weeks=[dict(week=w) for w in sorted(runner.WEEKS)], delayed=[]),
                '_posts':{'1':dict(author_id=1, content='离线测试正文')}})
            class Process:
                pid = 99999999
                returncode = 0
                def poll(self): return 0
            return Process()
        return fake

    def test_serial_success_checks_real_fixture_records(self):
        with patch.object(runner.subprocess, 'Popen', side_effect=self.process()) as launch:
            self.assertTrue(runner.supervise(0))
        state = runner.read(runner.STATE)
        self.assertEqual(launch.call_count, 3)
        self.assertEqual(state['status'], 'completed')
        self.assertEqual(len(state['completed']), 3)
        self.assertEqual(state['total_body_requests'], 3)
        self.assertEqual(state['expected_returned_model'], 'returned-v1')
        self.assertEqual(runner.read(runner.PLAN), self.plan)
        self.assertTrue(all((self.pilot / f'completion_{a}.json').is_file() for a in runner.ALGORITHMS))

    def test_final_service_failure_stops_without_next_condition(self):
        with patch.object(runner.subprocess, 'Popen', side_effect=self.process(failed=True)) as launch:
            self.assertFalse(runner.supervise(0))
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(runner.read(runner.STATE)['status'], 'stopped')
        self.assertFalse((self.workspace / 'runs/chronological').exists())
        with self.assertRaisesRegex(RuntimeError, '已有状态'):
            runner.preflight(self.plan)

    def test_model_drift_stops_and_preserves_first_completion(self):
        models = iter(('returned-v1', 'returned-v2'))
        def fake(*a, **kw): return self.process(next(models))(*a, **kw)
        with patch.object(runner.subprocess, 'Popen', side_effect=fake) as launch:
            self.assertFalse(runner.supervise(0))
        self.assertEqual(launch.call_count, 2)
        state = runner.read(runner.STATE)
        self.assertEqual(len(state['completed']), 1)
        self.assertFalse((self.workspace / 'runs/interest').exists())

    def test_deadline_prevents_start_and_ledger_creation(self):
        self.plan['deadline_at'] = (runner.now() - timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(RuntimeError, '截止'):
            runner.preflight(self.plan)
        self.assertFalse(Path(self.plan['ledger_path']).exists())

    def test_configuration_cannot_escape_workspace_or_change_budget(self):
        self.plan['runs'][0]['run_dir'] = str(self.home / 'outside')
        with self.assertRaisesRegex(RuntimeError, '越出'):
            runner.preflight(self.plan)
        self.plan['runs'][0]['run_dir'] = 'runs/random'
        self.plan['extra_requests_limit'] = 331
        with self.assertRaisesRegex(RuntimeError, '上界'):
            runner.preflight(self.plan)

    def test_stop_refuses_foreign_pid(self):
        save(runner.STATE, dict(status='running', supervisor_pid=99999999))
        with patch.object(runner, 'process_matches', return_value=False), \
                patch.object(runner.os, 'kill') as kill, \
                patch('sys.argv', ['run_pilot.py', '--stop']):
            with self.assertRaisesRegex(RuntimeError, '身份不匹配'):
                runner.main()
            kill.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
