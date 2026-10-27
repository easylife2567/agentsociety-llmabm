"""修复副本和两路调度的禁网验收；只写新准备资产，不改原始现场。"""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import sys
import tempfile
from unittest.mock import patch

import run_seed_extension_recovery_2 as controller
base = controller.base


def controller_checks():
    cases = []
    for mode in ('success', 'service_failed', 'missing_model', 'quota', 'budget', 'deadline'):
        with tempfile.TemporaryDirectory(dir=base.HERE / 'checks', prefix='.recovery2_control_') as tmp:
            root = Path(tmp); (root / 'records').mkdir(); (root / 'source').mkdir()
            (root / 'source/marker').write_text('prepared checkpoint')
            (root / 'extra.count').write_text('7')
            fixture = root / 'fixture/agents/agent_1'; fixture.mkdir(parents=True)
            row = dict(week='2026-W12', reason='published', posted=True, generation_attempts=2,
                generation_status='service_failed' if mode == 'service_failed' else 'service_success',
                generation_error='Timeout', response_model=None if mode in ('service_failed', 'missing_model') else base.EXPECTED_MODEL)
            (fixture / 'AGENT.json').write_text(json.dumps(dict(id=1, decision_log=[row])))
            actual = controller.agent_summary(root / 'fixture')
            assert actual['service_failures'] == (mode == 'service_failed')
            assert actual['posted_model_failures'] == (mode in ('service_failed', 'missing_model'))
            if mode == 'success':
                assert not actual['service_failures']  # 成功重试虽保留generation_error，也不误停。
            start = datetime.now(timezone.utc) - timedelta(hours=49 if mode == 'deadline' else 1)
            runs = [dict(run_id='retained', run_dir='retained', requests=100),
                dict(run_id='resume', run_dir='resume', condition='no_r', seed=6, config='cfg', steps='steps',
                     resume=True, prior_requests=465, source_run_dir=str(root / 'source')),
                dict(run_id='retry', run_dir='retry', condition='no_b', seed=7, config='cfg', steps='steps'),
                dict(run_id='pending', run_dir='pending', condition='no_d', seed=7, config='cfg', steps='steps')]
            plan = dict(runs=runs, source_sha256={}, started_at=start.isoformat(), deadline_at=(start + timedelta(hours=48)).isoformat(),
                budget=dict(max_wall_hours=48, max_agent_body_requests=25410, extra_requests_limit=2310, ledger_path='extra.count'))
            old = dict(completed=[dict(runs[0])], started_at=plan['started_at'], deadline_at=plan['deadline_at'])
            made, states, signals = [], [], []
            class Fake:
                def __init__(self, command, **kw):
                    self.pid = 990000 + len(made); self.returncode = 0 if mode == 'success' else None; made.append(self)
                    if mode == 'quota':
                        (Path(command[command.index('--run-dir') + 1]) / 'recovery2-stderr.log').write_text('RateLimitError: usage quota')
                def poll(self):
                    return self.returncode
            def stop(pid, sig):
                signals.append(sig); next(p for p in made if p.pid == pid).returncode = -2
            def summary(d):
                used = 466 if d.name == 'resume' else 1
                return dict(actual, requests=25411 if mode == 'budget' else used)
            def complete(d, run):
                return dict(run_id=run['run_id'], run_dir=str(d), **summary(d))
            original_write = base.write
            def write(path, value):
                states.append(json.loads(json.dumps(value))); original_write(path, value)
            with patch.object(base, 'ROOT', root), patch.object(base, 'STATE', root / 'records/state.json'), \
                 patch.object(controller, 'SELF', root / 'controller.py'), patch.object(controller, 'RECORD', root / 'records/recovery.json'), \
                 patch.object(controller.subprocess, 'Popen', Fake), patch.object(controller, 'agent_summary', side_effect=summary), \
                 patch.object(controller, 'final_result', side_effect=complete), patch.object(base, 'write', side_effect=write), \
                 patch.object(controller.time, 'sleep'), patch.object(controller.signal, 'signal'), patch.object(base.os, 'killpg', side_effect=stop):
                result = controller.execute(plan, old, runs, dict(PYTHON_PATH=sys.executable), [dict(run_id='failed', requests=62)])
            assert max(len(s['active_runs']) for s in states) <= 2
            assert states[0]['body_requests_used'] == 627  # 完成100+R465+B失败62。
            assert all(s['started_at'] == plan['started_at'] and s['deadline_at'] == plan['deadline_at'] for s in states)
            if mode == 'success':
                assert result['status'] == 'completed' and len(result['completed']) == 4 and len(made) == 3
                assert result['body_requests_used'] == 630 and not signals
                assert (root / 'resume/marker').read_text() == 'prepared checkpoint'
            else:
                assert result['status'] == 'stopped' and len(made) == (0 if mode == 'deadline' else 2)
                assert len(result['completed']) == 1 and all(p.poll() is not None for p in made)
                assert mode == 'deadline' or signal.SIGINT in signals
            cases.append(dict(case=mode, passed=True, fake_children=len(made), max_parallel=2))
    # 相对/绝对路径均按脚本名和明确参数匹配；不接受无关进程。
    with patch.object(base.subprocess, 'run') as ps:
        ps.return_value = type('PS', (), dict(returncode=0, stdout='Ss python hypothesis_4/experiment_3/run_seed_extension_recovery_2.py --continue-authorized'))()
        assert base.process_alive(1, controller.SELF.name + ' --continue-authorized')
        assert not base.process_alive(1, 'another_controller --continue-authorized')
    report = dict(status='passed', cases=cases, recovered_retry_not_misclassified=True, process_path_matching=True,
        real_processes=0, llm_calls=0, controller_sha256=base.digest(controller.SELF))
    with controller.CHECK.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


async def verify(report):
    from agentsociety2.registry import scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules
    scan_and_register_custom_modules(base.ROOT)
    agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
    env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    plan, old = base.read(base.PLAN), base.read(base.STATE)
    terminal = base.read(base.CONTROL / 'terminal_check_recovery_1.json')
    assert old['status'] == 'stopped' and len(old['completed']) == 11 and old['body_requests_used'] == 3529
    assert base.ledger_count(plan) == 7 and datetime.now(timezone.utc) < datetime.fromisoformat(plan['deadline_at'])
    assert not base.process_alive(old['supervisor_pid'], 'run_seed_extension')
    assert all(not base.process_alive(a['child_pid'], a['run_dir']) for a in old['active_runs'])
    assert all(base.digest(base.ROOT / f) == h for f, h in plan['source_sha256'].items())
    assert all(base.digest(base.ROOT / f) == h for f, h in terminal['source_sha256'].items())
    preserved = {**base.read(base.CONTROL / 'recovery_1_offline_check.json')['preserved_sha256'], **terminal['source_sha256']}
    preserved.pop(str(base.STATE.relative_to(base.ROOT)), None)  # 动态状态将换代，原字节另存stopped_execution_2。
    report['source_state_sha256'] = base.digest(base.STATE)
    report['completed'] = [controller.final_result(Path(x['run_dir']), x) for x in old['completed']]
    for item in old['completed'] + old['active_runs']:
        for path in Path(item['run_dir']).rglob('*'):
            if path.is_file():
                preserved[str(path.relative_to(base.ROOT))] = base.digest(path)
    assert all(base.digest(base.ROOT / f) == h for f, h in preserved.items())
    source = Path(next(a['run_dir'] for a in old['active_runs'] if a['run_id'] == 'timestamp_bdr_v1_interest_no_r_s6'))
    assert not controller.CHECKPOINT.exists()
    shutil.copytree(source, controller.CHECKPOINT)
    env, pending = await controller.reconstruct_pending(controller.CHECKPOINT)
    before = base.read(source / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    await env.to_workspace(controller.CHECKPOINT / 'env/CurationDynamicsSpace')
    after = base.read(controller.CHECKPOINT / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    changed = {k for k in before if before[k] != after[k]}
    assert changed == set(pending['reconstructed_keys'])
    assert base.read(controller.CHECKPOINT / 'SOCIETY_STEP.json')['step_count'] == 602
    differing = []
    for path in source.rglob('*'):
        if path.is_file() and base.digest(path) != base.digest(controller.CHECKPOINT / path.relative_to(source)):
            differing.append(str(path.relative_to(source)))
    assert differing == ['env/CurationDynamicsSpace/state/ENV_STATE.json']
    report['pending_publication'] = dict(pending, source_run_dir=str(source), prepared_checkpoint=str(controller.CHECKPOINT),
        modified_files=differing, changed_keys=sorted(changed), source_env_sha256=base.digest(source / differing[0]),
        prepared_env_sha256=base.digest(controller.CHECKPOINT / differing[0]))
    decisions, agents = {}, {}
    for path in (controller.CHECKPOINT / 'agents').glob('*/AGENT.json'):
        with patch.object(agent_cls, '_bind_services'):
            agent = await agent_cls.from_workspace(path.parent, None)
        agents[str(agent._id)] = agent
        for row in agent._decision_log:
            decisions[str(agent._id), row['week']] = row
    t = datetime.fromisoformat(base.read(controller.CHECKPOINT / 'SOCIETY_STEP.json')['current_time'])
    tick = decisions['95', '2026-W21']['tick']
    for aid in ('29', '95'):
        original = json.dumps(agents[aid]._decision_log, sort_keys=True)
        assert await agents[aid].step(tick, t) == 'arrival decision already recorded'
        assert json.dumps(agents[aid]._decision_log, sort_keys=True) == original
    trials = []
    for _ in range(2):
        e = env_cls(**base.read(controller.CHECKPOINT / 'SOCIETY.json')['env_kwargs']['CurationDynamicsSpace'])
        assert await e.restore(controller.CHECKPOINT / 'env/CurationDynamicsSpace')
        assert (await e.create_post('95', decisions['95', '2026-W21']['content']))['already_posted']
        await e._arrival.step(tick, t)  # 仅内存单批验证，不运行引擎或模型，不写回。
        actions = {(str(a['agent_id']), a['week']) for a in e._arrival.state['actions']}
        assert len(actions) == len(e._arrival.state['actions']) == 953 and actions == set(decisions)
        posts = {int(k): v for k, v in e._posts.items() if v.get('source') == 'agent'}
        posts.update({v['post_id']: v for v in e._arrival.state['delayed']})
        published = {v['post_id']: v for v in decisions.values() if v.get('posted')}
        assert len(posts) == 463 and set(posts) == set(published)
        assert all(posts[k]['content'] == row['content'] for k, row in published.items())
        assert e._chronological_batch_index == 603 and not e._pending_agent_posts
        trials.append(json.dumps(dict(arrival=e._arrival.state, posts=e._posts, cumulative=e._cumulative_exposures), sort_keys=True))
    assert trials[0] == trials[1]
    assert controller.agent_summary(controller.CHECKPOINT)['requests'] == 465
    assert not controller.agent_summary(controller.CHECKPOINT)['service_failures']
    assert all(base.digest(base.ROOT / f) == h for f, h in preserved.items())
    report.update(preserved_sha256=preserved,
        checkpoint_sha256={str(f.relative_to(controller.CHECKPOINT)): base.digest(f) for f in controller.CHECKPOINT.rglob('*') if f.is_file()},
        frozen_files_verified=len(plan['source_sha256']), retained_completed=11, remaining_conditions=10,
        body_before=3529, extra_before=7, discarded_B_body=62, R_carried_body=465,
        first_attempt_opportunities_remaining=10047, worst_total_body_with_remaining_extra=15879,
        original_started_at=plan['started_at'], original_deadline_at=plan['deadline_at'],
        actual_agents_restored=100, memory_single_batch_replays=2, replay_states_equal=True,
        real_engine_processes=0, ray_started=False, body_regenerations=0)


def main():
    assert not controller.AUDIT.exists() and not controller.CHECK.exists() and not controller.CHECKPOINT.exists(), '不覆盖本次准备证据'
    os.chdir(base.ROOT)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    report = dict(status='checking', started_at=base.stamp(), network_attempts=0, llm_calls=0,
        controller_sha256=base.digest(controller.SELF), verifier_sha256=base.digest(Path(__file__)))
    def deny(*a, **kw):
        report['network_attempts'] += 1
        raise AssertionError('离线验收禁止联网')
    async def deny_llm(*a, **kw):
        report['llm_calls'] += 1
        raise AssertionError('离线验收禁止LLM')
    try:
        report['controller_checks'] = controller_checks()
        with tempfile.TemporaryDirectory(dir=base.HERE / 'checks', prefix='.recovery2_cache_') as cache:
            os.environ['BLACK_CACHE_DIR'] = cache
            with patch.object(socket.socket, 'connect', deny), patch.object(socket.socket, 'connect_ex', deny), patch.object(socket, 'create_connection', deny):
                import litellm
                with patch.object(litellm.Router, 'acompletion', deny_llm), patch.object(litellm, 'acompletion', deny_llm):
                    asyncio.run(verify(report))
        assert report['network_attempts'] == report['llm_calls'] == 0
        report['status'] = 'passed'
    except Exception as exc:
        import traceback
        report.update(status='failed', error=str(exc), traceback=traceback.format_exc())
    report['finished_at'] = base.stamp()
    with controller.AUDIT.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k not in ('preserved_sha256', 'checkpoint_sha256', 'completed')}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
