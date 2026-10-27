"""禁网核验本次两份接续检查点；不改原目录，不启动Ray或仿真。"""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import socket
from unittest.mock import patch

import run_seed_extension as base

OUTPUT = base.CONTROL / 'recovery_1_offline_check.json'


async def verify(report):
    import yaml
    from agentsociety2.registry import (scan_and_register_custom_modules,
        get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    scan_and_register_custom_modules(base.ROOT)
    agent_cls = dict(get_registered_agent_modules())['CurationDiscourseAgent']
    env_cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    plan, state = base.read(base.PLAN), base.read(base.STATE)
    assert state['status'] == 'stopped' and not base.process_alive(state['supervisor_pid'], 'run_seed_extension')
    assert len(state['completed']) == 10 and len(state['active_runs']) == 2
    assert base.ledger_count(plan) == 4 and state['body_requests_used'] == 3208
    assert datetime.now(timezone.utc) < datetime.fromisoformat(plan['deadline_at'])
    assert all(base.digest(base.ROOT / p) == h for p, h in plan['source_sha256'].items())
    terminal = base.read(base.CONTROL / 'terminal_check.json')
    assert all(base.digest(base.ROOT / p) == h for p, h in terminal['source_sha256'].items())
    report['preserved_sha256'] = dict(terminal['source_sha256'])
    report['completed'] = [base.completed(Path(r['run_dir']), r) for r in state['completed']]
    runner = ExperimentRunner.__new__(ExperimentRunner)
    for item in state['active_runs']:
        d = Path(item['run_dir'])
        assert not base.process_alive(item['child_pid'], str(d))
        run = next(r for r in plan['runs'] if r['run_id'] == item['run_id'])
        meta, step = base.read(d / 'SOCIETY.json'), base.read(d / 'SOCIETY_STEP.json')
        parsed = runner._load_config(base.ROOT / run['config'])
        specs, cls_name = runner._build_agent_specs([r.model_dump() for r in parsed.agents])
        assert meta['agent_specs'] == specs and meta['agent_class_name'] == cls_name
        assert meta['env_kwargs'] == {r['module_type']: r['kwargs'] for r in base.read(base.ROOT / run['config'])['env_modules']}
        assert meta['steps_hash'] == base.digest(base.ROOT / run['steps'])
        steps = yaml.safe_load((base.ROOT / run['steps']).read_text())
        n = step['step_count']
        t = datetime.fromisoformat(steps['start_t'])
        for row in steps['steps'][:n]:
            assert row['type'] == 'run' and row['num_steps'] == 1
            t += timedelta(seconds=row['tick'])
        assert t.isoformat() == step['current_time'] and step['completed_step_count'] == n
        e = env_cls(**meta['env_kwargs']['CurationDynamicsSpace'])
        assert await e.restore(d / 'env/CurationDynamicsSpace')
        saved = base.read(d / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
        assert e._arrival.state == saved['_arrival_state'] and e._chronological_batch_index == n
        assert e._current_event_time.replace(tzinfo=None) == t
        assert not saved['_pending_agent_posts']
        for key in ('_rng_injection', '_rng_feed_random', '_rng_interest_noise', '_rng_interest_sample'):
            assert json.loads(json.dumps(getattr(e, key).getstate())) == saved[key]
        actions = {(str(r['agent_id']), r['week']): r for r in e._arrival.state['actions']}
        assert len(actions) == len(e._arrival.state['actions'])
        decisions, postrows, extras = {}, {}, []
        for f in sorted((d / 'agents').glob('*/AGENT.json')):
            with patch.object(agent_cls, '_bind_services'):
                agent = await agent_cls.from_workspace(f.parent, None)
            raw = base.read(f)
            assert agent._decision_log == raw['decision_log'] and agent._step_count == len(raw['decision_log'])
            for r in raw['decision_log']:
                k = (str(agent._id), r['week'])
                assert k not in decisions and r['reason'] not in ('action_failed', 'publication_failed')
                decisions[k] = r
                if r.get('posted'):
                    assert r.get('content') and r.get('response_model') == base.EXPECTED_MODEL
                    postrows[r['post_id']] = r
                if k not in actions:
                    # 唯一可接受的领先记录：本批已经完成的沉默决策，没有请求或发布副作用。
                    snap = e._arrival.state['snapshots'].get(str(agent._id))
                    assert snap and snap['week'] == r['week'] and snap['acted_at'] == r['acted_at']
                    assert r['speak'] is False and r['reason'] == 'below_threshold'
                    assert not r['posted'] and r['generation_attempts'] == 0 and r.get('post_id') is None
                    feed = e._arrival.get_feed(str(agent._id))
                    u, _ = agent._speak_stimulus(feed)
                    assert abs(u - r['u']) < 1e-12 and u < agent._params['activity']
                    before = json.dumps(agent._decision_log, sort_keys=True)
                    # 实际step命中周去重，任何ask_env/LLM调用由外层禁网闸门阻止。
                    assert await agent.step(int(steps['steps'][n]['tick']), t) == 'arrival decision already recorded'
                    assert json.dumps(agent._decision_log, sort_keys=True) == before
                    extras.append(dict(agent_id=str(agent._id), week=r['week'], reason=r['reason'], replay='skip without request'))
        assert set(actions) <= set(decisions)
        envposts = {int(k): v for k, v in saved['_posts'].items() if v.get('source') == 'agent'}
        envposts.update({r['post_id']: r for r in saved['_arrival_state']['delayed']})
        assert set(postrows) == set(envposts)
        assert all(postrows[k]['content'] == v['content'] for k, v in envposts.items())
        assert len(postrows) == sum(saved['_total_posts_by_agent'].values())
        if run['condition'] == 'no_d':
            assert n == 674 and len(actions) == 1066 and len(decisions) == 1067
            assert extras == [dict(agent_id='25', week='2026-W22', reason='below_threshold', replay='skip without request')]
        else:
            assert run['condition'] == 'no_r' and n == 297 and len(actions) == len(decisions) == 469 and not extras
        # 对所有源文件保存哈希，运行后可核实失败现场完全未动。
        for f in d.rglob('*'):
            if f.is_file():
                report['preserved_sha256'][str(f.relative_to(base.ROOT))] = base.digest(f)
        report['resume_checks'].append(dict(run_id=run['run_id'], source_run_dir=str(d), steps=n,
            environment_actions=len(actions), decisions=len(decisions), posted=len(postrows),
            body_requests=base.agent_summary(d)['requests'], extra_decisions=extras, safe_to_resume=True,
            restored_random_states=4, original_checkpoint_edited=False))
    assert sum(r['requests'] for r in report['completed']) + sum(r['body_requests'] for r in report['resume_checks']) == 3208
    report.update(frozen_files_verified=len(plan['source_sha256']), deadline_at=plan['deadline_at'],
        original_started_at=plan['started_at'], body_requests_before=3208, extra_requests_before=4,
        completed_count=10, remaining_conditions=11, actual_agents_restored=200,
        duplicate_silent_decision_skips_checked=1, environment_steps=0, ray_started=False)


def main():
    assert not OUTPUT.exists(), '验收记录已存在，不覆盖'
    os.chdir(base.ROOT)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    report = dict(status='checking', checked_at=base.stamp(), network_attempts=0, llm_calls=0,
                  resume_checks=[], preserved_sha256={}, script_sha256=base.digest(Path(__file__)))
    def deny(*args, **kwargs):
        report['network_attempts'] += 1
        raise AssertionError('离线核查禁止网络')
    async def deny_llm(*args, **kwargs):
        report['llm_calls'] += 1
        raise AssertionError('离线核查禁止LLM')
    try:
        with patch.object(socket.socket, 'connect', deny), patch.object(socket.socket, 'connect_ex', deny), patch.object(socket, 'create_connection', deny):
            import litellm
            with patch.object(litellm.Router, 'acompletion', deny_llm), patch.object(litellm, 'acompletion', deny_llm):
                asyncio.run(verify(report))
        assert report['network_attempts'] == report['llm_calls'] == 0
        report['status'] = 'passed'
    except Exception as exc:
        import traceback
        report.update(status='failed', error=str(exc), traceback=traceback.format_exc())
    with OUTPUT.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k != 'preserved_sha256'}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1


def check_controller():
    """假进程核对接续预算不重计、最多两路、额度失败联停和原截止。"""
    import signal
    import sys
    import tempfile
    import run_seed_extension_recovery as controller
    results = []
    for mode in ('success', 'quota', 'budget', 'deadline'):
        with tempfile.TemporaryDirectory(dir=base.HERE / 'checks', prefix='.recovery_control_') as tmp:
            root = Path(tmp); (root / 'records').mkdir(); (root / 'extra.count').write_text('4')
            for name in ('source_d', 'source_r'):
                (root / name).mkdir(); (root / name / 'marker').write_text('original checkpoint')
            start = datetime.now(timezone.utc) - timedelta(hours=49 if mode == 'deadline' else 1)
            runs = [dict(run_id='retained', run_dir='retained', requests=100)]
            for i, count in enumerate((262, 208)):
                runs.append(dict(run_id=f'resume{i}', run_dir=f'resume{i}', condition='no_d' if i == 0 else 'no_r',
                    seed=6, config='frozen.json', steps='frozen.yaml', resume=True, prior_requests=count,
                    source_run_dir=str(root / ('source_d' if i == 0 else 'source_r'))))
            runs.append(dict(run_id='new_seed7', run_dir='new_seed7', condition='no_b', seed=7, config='frozen.json', steps='frozen.yaml'))
            plan = dict(runs=runs, started_at=start.isoformat(), deadline_at=(start + timedelta(hours=48)).isoformat(),
                source_sha256={}, budget=dict(max_wall_hours=48, max_agent_body_requests=25410,
                extra_requests_limit=2310, ledger_path='extra.count'))
            old = dict(completed=[dict(runs[0])], started_at=plan['started_at'], deadline_at=plan['deadline_at'])
            made, snapshots, signals = [], [], []
            class Fake:
                def __init__(self, command, **kwargs):
                    self.pid = 990000 + len(made); self.returncode = 0 if mode == 'success' else None
                    made.append(self)
                    if mode == 'quota':
                        (Path(command[command.index('--run-dir') + 1]) / 'recovery-stderr.log').write_text('RateLimitError: usage quota')
                def poll(self):
                    return self.returncode
            def kill(pid, signum):
                signals.append(signum)
                next(p for p in made if p.pid == pid).returncode = -2
            def summary(d):
                count = 263 if d.name == 'resume0' else 209 if d.name == 'resume1' else 1
                return dict(requests=25411 if mode == 'budget' else count, action_failures=0, response_models={})
            def complete(d, r):
                return dict(run_id=r['run_id'], run_dir=str(d), **summary(d))
            write = base.write
            def save(p, v):
                snapshots.append(json.loads(json.dumps(v))); write(p, v)
            with patch.object(base, 'ROOT', root), patch.object(base, 'STATE', root / 'records/state.json'), \
                 patch.object(controller, 'SELF', root / 'controller.py'), patch.object(controller, 'RECORD', root / 'records/recovery.json'), \
                 patch.object(controller.subprocess, 'Popen', Fake), patch.object(base, 'agent_summary', side_effect=summary), \
                 patch.object(base, 'completed', side_effect=complete), patch.object(base, 'write', side_effect=save), \
                 patch.object(controller.time, 'sleep'), patch.object(controller.signal, 'signal'), \
                 patch.object(base.os, 'killpg', side_effect=kill):
                result = controller.execute(plan, old, runs, dict(PYTHON_PATH=sys.executable))
            assert max(len(s['active_runs']) for s in snapshots) <= 2
            assert all(s['started_at'] == plan['started_at'] and s['deadline_at'] == plan['deadline_at'] for s in snapshots)
            assert snapshots[0]['body_requests_used'] == 570  # 完成100 + 接续262 + 接续208，绝不归零或重复。
            if mode == 'success':
                assert result['status'] == 'completed' and len(result['completed']) == 4 and len(made) == 3
                assert result['body_requests_used'] == 573 and not signals
                assert all((root / r / 'marker').read_text() == 'original checkpoint' for r in ('resume0', 'resume1'))
            else:
                assert result['status'] == 'stopped' and len(made) == (0 if mode == 'deadline' else 2)
                assert len(result['completed']) == 1 and all(p.poll() is not None for p in made)
                assert mode == 'deadline' or signal.SIGINT in signals
            results.append(dict(case=mode, status='passed', fake_children=len(made), original_deadline_retained=True))
    report = dict(status='passed', cases=results, real_processes=0, llm_calls=0,
        controller_sha256=base.digest(controller.SELF), verifier_sha256=base.digest(Path(__file__)))
    assert not controller.CHECK.exists(), '不覆盖原检查证据'
    with controller.CHECK.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    if '--controller' in sys.argv:
        check_controller()
    else:
        raise SystemExit(main())
