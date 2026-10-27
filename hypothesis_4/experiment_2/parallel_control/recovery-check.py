"""禁网恢复验收：真实检查点只读恢复、假进程两路上限及故障联停。"""
import asyncio
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import signal
import socket
import sys
import tempfile
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_seed_extension_recovery as c


async def restore_check():
    from agentsociety2.registry import scan_and_register_custom_modules, get_registered_env_modules, get_registered_agent_modules
    from agentsociety2.society.society import AgentSociety
    scan_and_register_custom_modules(c.ROOT)
    env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
    directory = c.BATCH / 'timestamp_v1_interest_s6'
    meta, step = AgentSociety._read_checkpoint(directory)
    env = env_cls(**meta['env_kwargs']['CurationDynamicsSpace'])
    assert await env.restore(directory / 'env/CurationDynamicsSpace')
    assert env._arrival.state == c.read(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')['_arrival_state']
    count = 0
    for path in (directory / 'agents').glob('*/AGENT.json'):
        with patch.object(agent_cls, '_bind_services'):
            agent = await agent_cls.from_workspace(path.parent, None)
        assert agent._decision_log == c.read(path)['decision_log']
        count += 1
    assert count == 100 and step['step_count'] == 580


def supervisor_check():
    original = c.read(c.PLAN)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        batch = root / 'batch'; batch.mkdir()
        ledger = batch / 'ledger'; ledger.write_text('5')
        state_path = batch / 'state.json'; state_path.write_text('{}')
        fake_controller = root / 'controller.py'; fake_controller.write_text('offline fixture')
        runs = [dict(run_id=f'fake_{i}', run_dir=f'batch/fake_{i}', config='c', steps='s') for i in range(3)]
        old = dict(completed=[], started_at=original['started_at'])
        plan = dict(original, source_sha256={})
        discarded = [dict(requests=54)]
        phase = dict(advanced=False, stopped=False)
        launched, signals = [], []
        def launch(command, **kwargs):
            launched.append(command)
            return Mock(pid=9900 + len(launched), returncode=None)
        def summary(_):
            return dict(requests=0, action_failures=int(phase['advanced']), response_models={})
        def stop(active, sig):
            signals.append(([a['child_pid'] for a in active], sig))
            phase['stopped'] = True
        with patch.object(c, 'ROOT', root), patch.object(c, 'SELF', fake_controller), patch.object(c, 'BATCH', batch), patch.object(c, 'STATE', state_path), \
             patch.object(c, 'SOURCE_STATE', batch / 'stopped.json'), patch.object(c, 'RECORD', batch / 'recovery.json'), \
             patch.object(c, 'PLAN', state_path), patch.object(c, 'LEDGER', ledger), \
             patch.object(c, 'prepare', return_value=(plan, old, runs, discarded, dict(PYTHON_PATH='fake'))), \
             patch.object(c, 'agent_summary', side_effect=summary), patch.object(c, 'signal_engines', side_effect=stop), \
             patch.object(c, 'engine_alive', side_effect=lambda _: not phase['stopped']), \
             patch.object(c.signal, 'signal'), patch.object(c.subprocess, 'Popen', side_effect=launch), \
             patch.object(c.time, 'sleep', side_effect=lambda _: phase.update(advanced=True)), redirect_stderr(io.StringIO()):
            c.supervise()
        final = c.read(state_path)
        assert len(launched) == 2 and signals[0] == ([9901, 9902], signal.SIGINT)
        assert final['status'] == 'stopped' and final['total_body_requests'] == 54
        assert final['completed'] == [] and ledger.read_text() == '5'
        assert c.deadline(plan) == c.deadline(original)


if __name__ == '__main__':
    from agentsociety2.config.config import Config
    plan, old, runs, discarded, _ = c.prepare()
    assert len(c.pending_runs(runs, old['completed'], [])) == 10
    assert c.budget_total(old['completed'], [dict(agent_summary=dict(requests=175))], discarded, 5, plan) == 2417
    with patch.object(Config, 'get_router', side_effect=AssertionError('禁止模型路由')), \
         patch.object(socket.socket, 'connect', side_effect=AssertionError('禁止联网')):
        asyncio.run(restore_check())
        supervisor_check()
    report = dict(status='passed', checks=['官方检查点读取、完整环境恢复、100份Agent决策逐份恢复',
        '剩余10条件、原截止及失败54请求不归零', '假进程只启两路、失败联停且不启动第三路'],
        llm_calls=0, network_calls=0, real_engine_calls=0, real_process_signals=0,
        controller_sha256=c.digest(c.SELF), check_sha256=c.digest(Path(__file__)), checked_at=c.now(),
        fixture_correction='临时检查修正工作区父目录及假ROOT对应的控制器路径；未调用模型或修改原始文件')
    target = c.BATCH / 'recovery_check_1.json'
    assert not target.exists(), '不覆盖验收证据'
    c.write(target, report)
    print(json.dumps(report, ensure_ascii=False))
