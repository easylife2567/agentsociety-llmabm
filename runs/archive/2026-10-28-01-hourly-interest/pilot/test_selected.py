"""随机/兴趣范围缩减的禁网假进程验收；绝不对真实进程操作。"""
from copy import deepcopy
from datetime import timedelta
import hashlib
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
spec = importlib.util.spec_from_file_location('selected_test_control', HERE / 'run_selected.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


class SelectedTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.pilot, self.workspace = self.home / 'pilot', self.home / 'workspace'
        self.pilot.mkdir(); self.workspace.mkdir()
        guard = patch.multiple(control, HERE=self.pilot, PLAN=self.pilot / 'runtime_plan.json',
                               STATE=self.pilot / 'batch_execution.json', REVISION=self.pilot / 'selected_revision.json',
                               HISTORY=self.pilot / 'scope_handoff')
        guard.start(); self.addCleanup(guard.stop)
        for target in ('socket.socket.connect', 'socket.create_connection'):
            guard = patch(target, side_effect=AssertionError('禁止网络'))
            guard.start(); self.addCleanup(guard.stop)
        for name in ('kill', 'killpg'):
            guard = patch.object(control.os, name, side_effect=AssertionError('禁止真实信号'))
            guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.subprocess, 'Popen', side_effect=AssertionError('禁止真实引擎'))
        guard.start(); self.addCleanup(guard.stop)
        guard = patch.object(control.signal, 'signal')
        guard.start(); self.addCleanup(guard.stop)
        self.summary = dict(agent_files=100, decisions=20, unique_decisions=20, posted=2, requests=20,
                            action_failures=0, service_failures=0, posted_model_failures=0,
                            invalid_publications=0, response_models={'actual-v1': 2})
        start = control.now() - timedelta(minutes=40)
        ledger = self.pilot / 'extra_attempts.count'; ledger.write_text('7')
        env = self.pilot / 'fixture.env'
        env.write_text('AGENTSOCIETY_LLM_MODEL=fixture\nAGENTSOCIETY_LLM_API_KEY=fixture\nAGENTSOCIETY_LLM_API_BASE=https://offline.invalid/v1\n')
        self.plan = dict(execution_authorized=True, workspace=str(self.workspace), python='fake-python',
                         env_file=str(env), requested_model='fixture', api_base_sha256=hashlib.sha256(b'https://offline.invalid/v1').hexdigest(),
                         source_sha256={}, deadline_at=(start + timedelta(hours=8)).isoformat(),
                         decision_opportunities=3300, extra_requests_limit=330, body_outer_requests_limit=3630,
                         ledger_path=str(ledger), runs=[])
        for algorithm in ('random', 'chronological', 'interest'):
            self.plan['runs'].append(dict(algorithm=algorithm, run_id=f'pilot_{algorithm}', seed=0,
                                         config=str(self.pilot / f'{algorithm}.json'), steps='steps.yaml',
                                         run_dir=str(self.workspace / 'runs' / algorithm)))
        random, chronological = self.plan['runs'][:2]
        for run in (random, chronological): Path(run['run_dir']).mkdir(parents=True)
        self.previous = dict(status='running', supervisor_pid=1001, started_at=start.isoformat(),
                             deadline_at=self.plan['deadline_at'], runtime_plan_sha256='', completed=[],
                             expected_returned_model='actual-v1', extra_requests_used=7, total_body_requests=45,
                             active_runs=[dict(random, child_pid=1002), dict(chronological, child_pid=1003)])
        self.withdrawn = dict(chronological, child_pid=1003, status='withdrawn_by_user', consumed_requests=25)
        self.revision = dict(execution_authorized=True, authorization='fixture',
                             selected_algorithms=['random', 'interest'], excluded_algorithms=['chronological'],
                             max_parallel=2, selected_decision_opportunities=2200,
                             runtime_plan_sha256='', parallel_revision_sha256='',
                             controller_sha256=control.digest(Path(control.__file__)),
                             deadline_at=self.plan['deadline_at'], decision_opportunities=3300,
                             extra_requests_limit=330, body_outer_requests_limit=3630,
                             expected_returned_model='actual-v1', withdrawal_record='scope_handoff/withdrawn_chronological.json',
                             withdrawal_sha256='')
        self.freeze()

    def freeze(self):
        save(control.PLAN, self.plan)
        self.revision['runtime_plan_sha256'] = control.digest(control.PLAN)
        self.previous['runtime_plan_sha256'] = self.revision['runtime_plan_sha256']
        save(self.pilot / 'parallel_revision.json', dict(controller_sha256=control.digest(control.PREVIOUS_CONTROLLER)))
        self.revision['parallel_revision_sha256'] = control.digest(self.pilot / 'parallel_revision.json')
        save(control.HISTORY / 'withdrawn_chronological.json', self.withdrawn)
        self.revision['withdrawal_sha256'] = control.digest(control.HISTORY / 'withdrawn_chronological.json')
        save(control.REVISION, self.revision); save(control.STATE, self.previous)

    def test_scope_filters_chronological_from_pending_and_inheritance(self):
        done, active = control.selected_previous(self.previous)
        self.assertEqual([r['algorithm'] for r in active], ['random'])
        self.assertEqual([r['algorithm'] for r in control.pending_runs(self.plan['runs'], done, active)], ['interest'])
        self.assertEqual(control.enforce_budget(self.plan, [], [dict(agent_summary={'requests': 20})], 7, 25), 45)

    def test_budget_counts_withdrawn_and_rejects_overflow(self):
        self.assertEqual(control.enforce_budget(self.plan, [{'requests': 100}], [{'agent_summary': {'requests': 200}}], 7, 25), 325)
        for requests, extra in ((3630, 7), (0, 331), (0, -1)):
            with self.assertRaises(RuntimeError): control.enforce_budget(self.plan, [{'requests': requests}], [], extra, 25)

    def test_parent_handoff_only_preserves_selected_pid_and_ledger(self):
        sent = []
        def matches(pid, text): return pid == 1002 or (pid == 1001 and not any(sig == signal.SIGHUP for _, sig in sent))
        with patch.object(control, 'process_matches', side_effect=matches), \
                patch.object(control, 'agent_summary', return_value=(self.summary, set(), {})), \
                patch.object(control, 'frozen_sources'), \
                patch.object(control.os, 'kill', side_effect=lambda pid, sig: sent.append((pid, sig))), \
                patch.object(control.os, 'killpg') as groups, patch.object(control.time, 'sleep'):
            previous = control.release_parallel(self.plan, self.revision, self.previous)
        self.assertEqual(sent, [(1001, signal.SIGSTOP), (1001, signal.SIGHUP), (1001, signal.SIGCONT)])
        self.assertEqual(control.selected_previous(previous)[1][0]['child_pid'], 1002)
        groups.assert_not_called()
        self.assertEqual(Path(self.plan['ledger_path']).read_text(), '7')

    def test_completed_selected_in_handoff_is_verified_and_absorbed(self):
        sent, verified = [], []
        def matches(pid, text): return pid == 1001 and not any(sig == signal.SIGHUP for _, sig in sent)
        with patch.object(control, 'process_matches', side_effect=matches), \
                patch.object(control, 'agent_summary', return_value=(self.summary, set(), {})), \
                patch.object(control, 'final_result', side_effect=lambda *args: verified.append(args)), \
                patch.object(control, 'frozen_sources'), \
                patch.object(control.os, 'kill', side_effect=lambda pid, sig: sent.append((pid, sig))), patch.object(control.time, 'sleep'):
            control.release_parallel(self.plan, self.revision, self.previous)
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0][1]['algorithm'], 'random')

    def test_foreign_parent_pid_receives_no_signal(self):
        with patch.object(control, 'process_matches', return_value=False), patch.object(control.os, 'kill') as kill:
            with self.assertRaises(RuntimeError): control.release_parallel(self.plan, self.revision, self.previous)
        kill.assert_not_called()

    def run_loop(self, failure=False, already_finished=False):
        phase = dict(cycle=0, stopped=False, max_active=0)
        launched, sent = [], []
        write = control.write
        def record(path, value):
            if Path(path) == control.STATE: phase['max_active'] = max(phase['max_active'], len(value.get('active_runs', [])))
            write(path, value)
        def launch(command, **kwargs):
            directory = Path(command[command.index('--run-dir') + 1]); launched.append(directory.name)
            class Fake:
                pid = 2000 + len(launched)
                returncode = 0
                def poll(self): return None
            return Fake()
        def alive(item):
            if phase['stopped']: return False
            if failure: return True
            if item['algorithm'] == 'random': return not already_finished and phase['cycle'] < 1
            return phase['cycle'] < 2
        def inspect(directory, **kwargs):
            summary = dict(self.summary)
            if failure and phase['cycle']: summary['service_failures'] = 1
            return summary, set(), {}
        def stop(active, sig): sent.append(([item['algorithm'] for item in active], sig)); phase['stopped'] = True
        def final(directory, run, model): return dict(run_id=run['run_id'], algorithm=run['algorithm'], run_dir=str(directory), requests=20, steps=693, actions=1100, weeks=11, posted=2)
        with patch.object(control, 'preflight', return_value=(self.plan, self.revision, self.previous, {}, self.withdrawn)), \
                patch.object(control, 'release_parallel', return_value=deepcopy(self.previous)), \
                patch.object(control, 'engine_alive', side_effect=alive), patch.object(control, 'agent_summary', side_effect=inspect), \
                patch.object(control, 'progress', return_value={}), patch.object(control, 'frozen_sources'), \
                patch.object(control, 'final_result', side_effect=final), patch.object(control, 'signal_engines', side_effect=stop), \
                patch.object(control, 'write', side_effect=record), patch.object(control.subprocess, 'Popen', side_effect=launch), \
                patch.object(control.time, 'sleep', side_effect=lambda _: phase.update(cycle=phase['cycle'] + 1)):
            result = control.supervise(0)
        return result, phase, launched, sent, control.read(control.STATE)

    def test_only_interest_launches_random_continues_and_original_caps_remain(self):
        plan_bytes = control.PLAN.read_bytes()
        ok, phase, launched, sent, state = self.run_loop()
        self.assertTrue(ok); self.assertEqual(launched, ['interest']); self.assertEqual(sent, [])
        self.assertEqual(phase['max_active'], 2)
        self.assertEqual({r['algorithm'] for r in state['completed']}, {'random', 'interest'})
        self.assertEqual(state['excluded_runs'], [self.withdrawn])
        self.assertEqual(state['total_body_requests'], 65)
        self.assertEqual(state['extra_requests_used'], 7)
        self.assertEqual(state['started_at'], self.previous['started_at'])
        self.assertEqual(state['deadline_at'], self.plan['deadline_at'])
        self.assertEqual(control.PLAN.read_bytes(), plan_bytes)

    def test_random_already_completed_not_restarted(self):
        ok, _, launched, _, state = self.run_loop(already_finished=True)
        self.assertTrue(ok); self.assertEqual(launched, ['interest'])
        self.assertEqual(len(state['completed']), 2)

    def test_selected_failure_stops_only_current_selected(self):
        ok, _, launched, sent, state = self.run_loop(failure=True)
        self.assertFalse(ok); self.assertEqual(launched, ['interest'])
        self.assertEqual(sent[0][0], ['random', 'interest'])
        self.assertEqual(state['status'], 'stopped')
        self.assertEqual(state['total_body_requests'], 65)

    def test_original_deadline_prevents_handoff_before_any_signal(self):
        self.plan['deadline_at'] = (control.now() - timedelta(seconds=1)).isoformat()
        self.revision['deadline_at'] = self.plan['deadline_at']; self.freeze()
        with patch.object(control.os, 'kill') as kill, patch.object(control.os, 'killpg') as groups:
            with self.assertRaisesRegex(RuntimeError, '截止'): control.preflight()
        kill.assert_not_called(); groups.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
