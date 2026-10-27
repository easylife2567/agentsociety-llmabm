"""禁网/假进程验收两路接管：原引擎不收信号、两路上限、故障联停与原预算。

仅在临时目录写合成状态；不启动CLI，不向真实进程发信号，不调用模型。
"""
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import signal
import sys
import tempfile
from unittest.mock import Mock, patch
from contextlib import redirect_stderr

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
sys.path.insert(0, str(EXPERIMENT))
spec = importlib.util.spec_from_file_location('parallel_check_target', EXPERIMENT / 'run_seed_extension_parallel.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def main():
    checks = []
    runs = [dict(run_id=f'test_{i}', config='config.json', steps='steps.yaml', run_dir=f'batch/test_{i}') for i in range(3)]
    pending = control.pending_runs(runs, [dict(run_id='test_0')], [dict(run_id='test_1')])
    assert [r['run_id'] for r in pending] == ['test_2']
    checks.append('已完成与已接管条件不重复启动，按原顺序填补空位')
    original = control.read(control.PLAN)
    frozen_deadline = control.deadline(original)
    assert frozen_deadline == datetime.fromisoformat(original['started_at']) + control.timedelta(hours=48)
    assert frozen_deadline.isoformat() == '2026-10-24T15:40:45.950453+00:00'
    checks.append('截止沿用原2026-10-24T15:40:45.950453+00:00，不从交接重新计时')
    budget = dict(extra_requests_limit=2310, max_agent_body_requests=25410)
    assert control.enforce_budget([dict(requests=10)], [dict(agent_summary=dict(requests=20))], 2310, budget) == 30
    for done, extra in (([dict(requests=25411)], 0), ([], 2311)):
        try:
            control.enforce_budget(done, [], extra, budget)
        except RuntimeError:
            pass
        else:
            raise AssertionError('共享预算越界未拒绝')
    checks.append('跨两路累计正文和共享额外额度守恒，越界拒绝')
    with tempfile.TemporaryDirectory(dir=EXPERIMENT / 'tmp') as folder:
        root = Path(folder)
        state_path = root / 'state.json'
        previous = dict(supervisor_pid=2001, child_pid=2002, status='running',
                        current_run='test_0', command=['fake'], completed=[])
        control.write(state_path, previous)
        sent = []
        def alive(pid, expected):
            return not (pid == 2001 and any(sig == signal.SIGHUP for _, sig in sent))
        with patch.object(control, 'ROOT', root), patch.object(control, 'STATE', state_path), \
             patch.object(control, 'HISTORY', root / 'history'), patch.object(control, 'LEDGER', root / 'ledger'), \
             patch.object(control, 'process_alive', side_effect=alive), \
             patch.object(control, 'agent_summary', return_value=dict(action_failures=0, response_models={})), \
             patch.object(control, 'progress', return_value=dict(step_count=123)), \
             patch.object(control.subprocess, 'check_output', return_value='2002 2001 agentsociety2.society.cli fake\n'), \
             patch.object(control.os, 'kill', side_effect=lambda pid, sig: sent.append((pid, sig))), \
             patch.object(control.time, 'sleep'):
            (root / 'ledger').write_text('7')
            inherited = control.release_serial(dict(runs=runs), original, previous)
        assert inherited['child_pid'] == 2002
        assert sent == [(2001, signal.SIGSTOP), (2001, signal.SIGHUP), (2001, signal.SIGCONT)]
        assert (root / 'ledger').read_text() == '7'
    checks.append('交接信号仅送原父PID，原引擎PID保留且账本不重置')

    with tempfile.TemporaryDirectory(dir=EXPERIMENT / 'tmp') as folder:
        root = Path(folder)
        batch = root / 'batch'
        batch.mkdir()
        ledger = batch / 'ledger'
        ledger.write_text('0')
        phase = dict(stopped=False, advanced=False, max_active=0)
        sent_groups = []
        summary = dict(agent_files=100, decisions=20, unique_decisions=20, posted=2, requests=2,
                       action_failures=0, response_models={control.EXPECTED_MODEL: 2})
        def inspect(_):
            return dict(summary, action_failures=int(phase['advanced']))
        def sleep(_):
            phase['advanced'] = True
        def stop(active, sig):
            sent_groups.append(([item['child_pid'] for item in active], sig))
            phase['stopped'] = True
            phase['max_active'] = max(phase['max_active'], len(active))
        previous = dict(supervisor_pid=2001, child_pid=2002, status='running',
                        current_run='test_0', command=['fake'], completed=[], total_runs=3,
                        started_at=original['started_at'])
        plan = dict(original, runs=runs, source_sha256={})
        proc = Mock(pid=2003, returncode=None)
        fake_controller = root / 'controller.py'
        fake_controller.write_text('offline controller fixture\n')
        with patch.object(control, 'ROOT', root), patch.object(control, 'BATCH', batch), \
             patch.object(control, '__file__', str(fake_controller)), \
             patch.object(control, 'STATE', batch / 'state.json'), patch.object(control, 'PLAN', batch / 'plan.json'), \
             patch.object(control, 'LEDGER', ledger), \
             patch.object(control, 'preflight', return_value=(dict(runs=runs), plan, previous,
                         dict(AGENTSOCIETY_LLM_MODEL=original['model']))), \
             patch.object(control, 'release_serial', return_value=previous), \
             patch.object(control, 'engine_alive', side_effect=lambda _: not phase['stopped']), \
             patch.object(control, 'agent_summary', side_effect=inspect), \
             patch.object(control, 'signal_engines', side_effect=stop), \
             patch.object(control.signal, 'signal'), patch.object(control.time, 'sleep', side_effect=sleep), \
             patch.object(control.subprocess, 'Popen', return_value=proc) as launch, redirect_stderr(io.StringIO()):
            control.supervise()
        state = control.read(batch / 'state.json')
        assert launch.call_count == 1 and phase['max_active'] == 2
        assert sent_groups[0] == ([2002, 2003], signal.SIGINT)
        assert state['status'] == 'stopped' and not state['completed']
        saved_plan = control.read(batch / 'plan.json')
        assert saved_plan['started_at'] == original['started_at']
        assert saved_plan['deadline_at'] == frozen_deadline.isoformat()
        assert saved_plan['extra_requests_limit'] == 2310 and ledger.read_text() == '0'
    checks.append('合成接管后只新增一路，任一路失败联停两路，不启动第三个条件或重置额度')
    result = dict(status='passed', checks=checks, network_calls=0, llm_calls=0, real_cli_calls=0,
                  real_process_signals=0, controller_sha256=control.digest(EXPERIMENT / 'run_seed_extension_parallel.py'),
                  check_script_sha256=control.digest(Path(__file__)), checked_at=datetime.now(timezone.utc).isoformat())
    control.write(HERE / 'offline-check.json', result)
    print(json.dumps(dict(status='passed', checks=len(checks), network_calls=0, llm_calls=0, real_cli_calls=0), ensure_ascii=False))


if __name__ == '__main__':
    main()
