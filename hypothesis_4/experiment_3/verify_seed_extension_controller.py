"""使用假子进程验证两路控制、失败联停与额度边界；不调用CLI/模型。"""
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bdr_extension_controller', HERE / 'run_seed_extension.py')
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def scenario(mode):
    with tempfile.TemporaryDirectory(dir=HERE / 'checks', prefix='.controller_check_') as tmp:
        root = Path(tmp)
        (root / 'records').mkdir()
        (root / 'extra.count').write_text('0')
        start = datetime.now(timezone.utc)
        runs = [dict(run_id=f'offline_no_b_s{i}', condition='no_b', seed=i,
                     run_dir=f'offline_{i}', config='offline.json', steps='offline.yaml') for i in range(4)]
        plan = dict(batch_id='offline-only', budget=dict(max_wall_hours=48,
            max_agent_body_requests=25410, extra_requests_limit=2310, ledger_path='extra.count'),
            runs=runs, started_at=start.isoformat(), deadline_at=(start + timedelta(hours=48)).isoformat(),
            source_sha256={}, live_guard_sha256={})
        made, snapshots, signals = [], [], []
        class FakeProcess:
            def __init__(self, *args, **kwargs):
                self.pid = 990000 + len(made)
                self.returncode = (1 if not made else None) if mode == 'failure' else (None if mode == 'budget' else 0)
                made.append(self)
            def poll(self):
                return self.returncode
        def stop(pid, signum):
            signals.append((pid, signum))
            next(p for p in made if p.pid == pid).returncode = -2
        summary = dict(agent_files=100, decisions=1100, unique_decisions=1100, posted=0,
                       requests=25411 if mode == 'budget' else 0, action_failures=0, response_models={})
        actual_write = controller.write
        def save(path, value):
            snapshots.append(json.loads(json.dumps(value)))
            actual_write(path, value)
        def complete(directory, run):
            return dict(run_id=run['run_id'], run_dir=str(directory), steps=693,
                        actions=1100, weeks=11, **summary)
        with patch.object(controller, 'ROOT', root), patch.object(controller, 'STATE', root/'records/state.json'), \
             patch.object(controller.subprocess, 'Popen', FakeProcess), \
             patch.object(controller, 'agent_summary', return_value=summary), \
             patch.object(controller, 'completed', side_effect=complete), \
             patch.object(controller, 'write', side_effect=save), \
             patch.object(controller.time, 'sleep'), patch.object(controller.signal, 'signal'), \
             patch.object(controller.os, 'killpg', side_effect=stop):
            result = controller.execute(plan, {'PYTHON_PATH': sys.executable})
        assert max(len(s['active_runs']) for s in snapshots) <= 2
        assert all(s['started_at'] == plan['started_at'] and s['deadline_at'] == plan['deadline_at'] for s in snapshots)
        if mode == 'success':
            assert result['status'] == 'completed' and len(result['completed']) == len(made) == 4
            assert not signals
        else:
            assert result['status'] == 'stopped' and len(made) == 2 and not result['completed']
            assert all(p.poll() is not None for p in made)
            assert any(s == signal.SIGINT for _, s in signals)
        return dict(case=mode, passed=True, fake_processes=len(made),
                    max_parallel=max(len(s['active_runs']) for s in snapshots),
                    no_relaunch_after_failure=mode == 'success' or len(made) == 2,
                    deadline_and_start_preserved=True)


if __name__ == '__main__':
    checks = [scenario(mode) for mode in ('success', 'failure', 'budget')]
    report = dict(status='passed', checks=checks, real_subprocesses=0, simulation_calls=0, llm_calls=0,
                  controller_sha256=hashlib.sha256((HERE/'run_seed_extension.py').read_bytes()).hexdigest())
    (HERE/'checks/seed3_9_controller_check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))
