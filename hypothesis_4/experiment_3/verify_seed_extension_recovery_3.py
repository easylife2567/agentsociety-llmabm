"""本次恢复禁网验收：16次完成、两份同步检查点、预算和两路失败联停。"""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import signal
import socket
import sys
import tempfile
from unittest.mock import patch

import run_seed_extension_recovery_3 as controller
base = controller.base


def controller_checks():
    cases = []
    for mode in ('success', 'service_failed', 'missing_model', 'quota', 'budget', 'deadline'):
        with tempfile.TemporaryDirectory(dir=base.HERE / 'checks', prefix='.recovery3_control_') as tmp:
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
                        (Path(command[command.index('--run-dir') + 1]) / 'recovery3-stderr.log').write_text('RateLimitError: usage quota')
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
        ps.return_value = type('PS', (), dict(returncode=0, stdout='Ss python hypothesis_4/experiment_3/run_seed_extension_recovery_3.py --continue-authorized'))()
        assert base.process_alive(1, controller.SELF.name + ' --continue-authorized')
        assert not base.process_alive(1, 'another_controller --continue-authorized')
    report = dict(status='passed', cases=cases, recovered_retry_not_misclassified=True, process_path_matching=True,
        real_processes=0, llm_calls=0, controller_sha256=base.digest(controller.SELF))
    with controller.CHECK.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


async def verify(report):
    import yaml
    from agentsociety2.registry import scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules
    from agentsociety2.society.cli import ExperimentRunner
    scan_and_register_custom_modules(base.ROOT)
    A=dict(get_registered_agent_modules())['CurationDiscourseAgent']
    E=dict(get_registered_env_modules())['CurationDynamicsSpace']
    runner=ExperimentRunner.__new__(ExperimentRunner)
    plan,old=base.read(base.PLAN),base.read(base.STATE)
    assert old['status']=='stopped' and len(old['completed'])==16 and old['body_requests_used']==4876
    assert base.ledger_count(plan)==8 and datetime.now(timezone.utc)<datetime.fromisoformat(plan['deadline_at'])
    assert not base.process_alive(old['supervisor_pid'],'run_seed_extension')
    assert all(not base.process_alive(a['child_pid'],a['run_dir']) for a in old['active_runs'])
    terminal=base.read(base.CONTROL/'terminal_check_recovery_2.json')
    assert all(base.digest(base.ROOT/f)==h for f,h in terminal['source_sha256'].items())
    assert all(base.digest(base.ROOT/f)==h for f,h in plan['source_sha256'].items())
    assert all(base.digest(base.ROOT/f)==h for f,h in base.read(base.CONTROL/'recovery_2.json')['recovery_source_sha256'].items())
    preserved={**base.read(base.CONTROL/'recovery_2_offline_check.json')['preserved_sha256'],**terminal['source_sha256']}
    preserved.pop(str(base.STATE.relative_to(base.ROOT)),None)
    report['source_state_sha256']=base.digest(base.STATE)
    report['completed']=[controller.final_result(Path(x['run_dir']),x) for x in old['completed']]
    report['resume_checks']=[]
    for item in old['active_runs']:
        d=Path(item['run_dir']);run=next(r for r in plan['runs'] if r['run_id']==item['run_id'])
        meta,step=base.read(d/'SOCIETY.json'),base.read(d/'SOCIETY_STEP.json')
        raw=base.read(d/'env/CurationDynamicsSpace/state/ENV_STATE.json');ar=raw['_arrival_state']
        parsed=runner._load_config(base.ROOT/run['config'])
        specs,name=runner._build_agent_specs([r.model_dump() for r in parsed.agents])
        assert meta['agent_specs']==specs and meta['agent_class_name']==name
        assert meta['env_kwargs']=={r['module_type']:r['kwargs'] for r in base.read(base.ROOT/run['config'])['env_modules']}
        assert meta['steps_hash']==base.digest(base.ROOT/run['steps'])
        n=step['step_count'];assert n==step['completed_step_count']==raw['_chronological_batch_index']
        steps=yaml.safe_load((base.ROOT/run['steps']).read_text())
        t=datetime.fromisoformat(steps['start_t']);processed=set()
        for row in steps['steps'][:n]:
            assert row['type']=='run' and row['num_steps']==1
            processed.add((f'{t.isocalendar().year}-W{t.isocalendar().week:02d}',t.weekday()*24+t.hour))
            t+=timedelta(seconds=row['tick'])
        assert t.isoformat()==step['current_time']
        env=E(**meta['env_kwargs']['CurationDynamicsSpace']);assert await env.restore(d/'env/CurationDynamicsSpace')
        assert env._arrival.state==ar and env._current_event_time.replace(tzinfo=None)==t
        assert not env._pending_agent_posts and not env._posted_this_step
        for key in ('_rng_injection','_rng_feed_random','_rng_interest_noise','_rng_interest_sample'):
            assert json.loads(json.dumps(getattr(env,key).getstate()))==raw[key]
        decisions,expected={},set()
        for path in (d/'agents').glob('*/AGENT.json'):
            with patch.object(A,'_bind_services'):agent=await A.from_workspace(path.parent,None)
            data=base.read(path);assert agent._decision_log==data['decision_log']
            assert agent._step_count==len(data['decision_log'])
            overrides=agent._profile.get('chronological_action_hour_overrides',{})
            for week in {w for w,h in processed}:
                h=overrides.get(week,agent._chronological_action_hour)
                if (week,h) in processed:expected.add((str(agent._id),week))
            for row in agent._decision_log:
                key=(str(agent._id),row['week']);assert key not in decisions;decisions[key]=row
        actions={(str(a['agent_id']),a['week']) for a in ar['actions']}
        assert actions==set(decisions)==expected and len(actions)==len(ar['actions'])
        assert not {(str(a),raw['_current_week']) for a in raw['_chronological_active_agents']} & set(decisions)
        posts={int(k):v for k,v in raw['_posts'].items() if v.get('source')=='agent'}
        posts.update({x['post_id']:x for x in ar['delayed']})
        published={x['post_id']:x for x in decisions.values() if x.get('posted')}
        assert set(posts)==set(published) and all(posts[k]['content']==v['content'] for k,v in published.items())
        assert len(posts)==sum(raw['_total_posts_by_agent'].values())
        summary=controller.agent_summary(d)
        assert summary['agent_files']==100 and not summary['service_failures'] and not summary['posted_model_failures'] and not summary['action_failures']
        assert summary['decisions']==summary['unique_decisions']==len(actions)
        with tempfile.TemporaryDirectory(dir=base.HERE/'checks',prefix='.recovery3_roundtrip_') as tmp:
            await env.to_workspace(Path(tmp))
            assert base.read(Path(tmp)/'state/ENV_STATE.json')==raw
        assert (n,len(actions),summary['requests']) in ((249,396,183),(174,274,112))
        report['resume_checks'].append(dict(run_id=run['run_id'],run_dir=str(d),steps=n,actions=len(actions),decisions=len(decisions),
            requests=summary['requests'],posted=summary['posted'],safe_to_resume=True,checkpoint_edit_required=False,
            random_states_restored=4,env_roundtrip_equal=True,prefix_schedule_matrix_complete=True))
    for item in old['completed']+old['active_runs']:
        for path in Path(item['run_dir']).rglob('*'):
            if path.is_file():preserved[str(path.relative_to(base.ROOT))]=base.digest(path)
    assert all(base.digest(base.ROOT/f)==h for f,h in preserved.items())
    assert sum(r['requests'] for r in report['completed'])+sum(r['requests'] for r in report['resume_checks'])+62==4876
    report.update(preserved_sha256=preserved,frozen_files_verified=len(plan['source_sha256']),retained_completed=16,remaining_conditions=5,
        body_before=4876,extra_before=8,discarded_B_body=62,resume_body_carried=295,actual_agents_restored=200,
        real_engine_processes=0,ray_started=False,agent_new_decisions=0,body_regenerations=0,
        remaining_first_attempt_opportunities=4830,worst_total_body_with_all_remaining_extra=12008,
        original_started_at=plan['started_at'],original_deadline_at=plan['deadline_at'])


def main():
    assert not controller.AUDIT.exists() and not controller.CHECK.exists(),'不覆盖已有验收证据'
    os.chdir(base.ROOT)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP='True',MEM0_TELEMETRY='False',ANONYMIZED_TELEMETRY='False')
    report=dict(status='checking',started_at=base.stamp(),network_attempts=0,llm_calls=0,
        controller_sha256=base.digest(controller.SELF),verifier_sha256=base.digest(Path(__file__)))
    def deny(*a,**kw):report['network_attempts']+=1;raise AssertionError('离线核查禁止联网')
    async def deny_llm(*a,**kw):report['llm_calls']+=1;raise AssertionError('离线核查禁止模型请求')
    try:
        report['controller_checks']=controller_checks()
        with tempfile.TemporaryDirectory(dir=base.HERE/'checks',prefix='.recovery3_cache_') as tmp:
            os.environ['BLACK_CACHE_DIR']=tmp
            with patch.object(socket.socket,'connect',deny),patch.object(socket.socket,'connect_ex',deny),patch.object(socket,'create_connection',deny):
                import litellm
                with patch.object(litellm.Router,'acompletion',deny_llm),patch.object(litellm,'acompletion',deny_llm):asyncio.run(verify(report))
        assert report['network_attempts']==report['llm_calls']==0
        report['status']='passed'
    except Exception as exc:
        import traceback
        report.update(status='failed',error=str(exc),traceback=traceback.format_exc())
    report['finished_at']=base.stamp()
    with controller.AUDIT.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k not in ('preserved_sha256','completed')},ensure_ascii=False))
    return 0 if report['status']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
