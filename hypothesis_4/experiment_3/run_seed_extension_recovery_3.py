"""2026-10-26本次授权恢复：保留16次完成，两个同步检查点复制接续，再补seed9。"""
import argparse
import asyncio
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import run_seed_extension_recovery_2 as previous
base = previous.base
SELF = Path(__file__).resolve()
RECORD = base.CONTROL / 'recovery_3.json'
SNAPSHOT = base.CONTROL / 'stopped_execution_3.json'
AUDIT = base.CONTROL / 'recovery_3_offline_check.json'
PROBE = base.CONTROL / 'recovery_probe_3.json'
CHECK = base.CONTROL / 'recovery_3_controller_check.json'
FATAL = previous.FATAL
environment = previous.environment
agent_summary = previous.agent_summary
final_result = previous.final_result


async def probe():
    previous.PROBE, previous.AUDIT = PROBE, AUDIT
    await previous.probe()


def prepare():
    plan, old, audit = base.read(base.PLAN), base.read(base.STATE), base.read(AUDIT)
    base.require(not RECORD.exists() and not SNAPSHOT.exists() and old['status'] == 'stopped', '只允许本次明确恢复一次')
    base.require(not base.process_alive(old['supervisor_pid'], 'run_seed_extension'), '旧监督器仍活着')
    base.require(all(not base.process_alive(a['child_pid'], a['run_dir']) for a in old['active_runs']), '旧引擎仍活着')
    base.require(audit['status'] == base.read(CHECK)['status'] == base.read(PROBE)['status'] == 'passed', '本次离线/调度/接口核查未通过')
    base.require(audit['controller_sha256'] == base.digest(SELF) == base.read(CHECK)['controller_sha256'], '恢复控制器验收已过期')
    base.require(len(old['completed']) == 16 and old['body_requests_used'] == 4876 and base.ledger_count(plan) == 8, '停止基线变化')
    base.require(base.digest(base.STATE) == audit['source_state_sha256'], '原停止状态变化')
    for name, expected in {**plan['source_sha256'], **audit['preserved_sha256']}.items():
        base.require(base.digest(base.ROOT / name) == expected, '冻结/完成/失败来源变化: ' + name)
    base.check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
        body_requests=4876, extra_requests=8, active_runs=0)
    done = {r['run_id']: r for r in old['completed']}
    checked = {r['run_id']: r for r in audit['resume_checks']}
    runs = [dict(r) for r in plan['runs']]
    for run in runs:
        if run['run_id'] in done:
            run['run_dir'] = done[run['run_id']]['run_dir']
        elif run['run_id'] in checked:
            info = checked[run['run_id']]
            base.require(info['safe_to_resume'], '检查点不可安全接续')
            run.update(source_run_dir=info['run_dir'], resume=True, prior_requests=info['requests'], run_dir=run['run_dir'] + '_resume1')
        if run['run_id'] not in done:
            base.require(not (base.ROOT / run['run_dir']).exists(), '目标已存在，不覆盖或再次重试')
    discarded = old['discarded_attempts']
    base.require(len(discarded) == 1 and discarded[0]['requests'] == 62, '原失败62次记录变化')
    base.require(sum(r['requests'] for r in old['completed']) + sum(r['requests'] for r in audit['resume_checks']) + 62 == 4876, '用量不一致或重复累计')
    return plan, old, runs, environment(plan), discarded


def execute(plan, old, runs, env, discarded):
    active = []
    state = dict(old, status='running', supervisor_pid=os.getpid(), active_runs=[],
        controller=str(SELF.relative_to(base.ROOT)), recovery_record=str(RECORD.relative_to(base.ROOT)),
        recovery_started_at=base.stamp(), discarded_attempts=discarded)
    for key in ('error', 'stop_reason', 'finished_at', 'children_needing_attention'):
        state.pop(key, None)
    stop_at = None

    def save():
        for a in active:
            a['progress'], a['agent_summary'] = base.progress(Path(a['run_dir'])), agent_summary(Path(a['run_dir']))
        state['active_runs'] = [{k: v for k, v in a.items() if not k.startswith('_')} for a in active]
        # 两个副本已累计183/112次；旧B失败62次单列，原中断目录不重复相加。
        state['body_requests_used'] = sum(r['requests'] for r in state['completed']) + sum(a['agent_summary']['requests'] for a in active)
        used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
        state['body_requests_used'] += sum(r.get('prior_requests', 0) for r in runs if r['run_id'] not in used) + sum(r['requests'] for r in discarded)
        state.update(extra_requests_used=base.ledger_count(plan), updated_at=base.stamp())
        base.write(base.STATE, state)

    def stop(reason):
        nonlocal stop_at
        if stop_at is None:
            stop_at = time.monotonic()
            state.update(status='stopping', stop_reason=reason)
            base.signal_engines(active, signal.SIGINT)

    signal.signal(signal.SIGTERM, lambda *_: stop('收到停止请求'))
    signal.signal(signal.SIGINT, lambda *_: stop('收到停止请求'))
    try:
        while active or len(state['completed']) < len(runs):
            base.require(stop_at is None, state.get('stop_reason', '停止请求'))
            save()
            base.check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
                body_requests=state['body_requests_used'], extra_requests=state['extra_requests_used'], active_runs=len(active))
            base.require(all(base.digest(base.ROOT / p) == h for p, h in plan['source_sha256'].items()), '冻结文件变化')
            if RECORD.exists():
                base.require(all(base.digest(base.ROOT / p) == h for p, h in base.read(RECORD)['recovery_source_sha256'].items()), '接续工具变化')
            finished = []
            for a in active:
                summary = a['agent_summary']
                base.require(not summary['action_failures'], '行动/发布失败: ' + a['run_id'])
                base.require(not summary['service_failures'], '正文服务失败: ' + a['run_id'])
                base.require(not summary['posted_model_failures'], '已发布正文缺有效返回模型: ' + a['run_id'])
                base.require(not(set(summary['response_models']) - {base.EXPECTED_MODEL}), '实际返回模型变化')
                for name in ('recovery3-engine.log', 'recovery3-stderr.log'):
                    path = Path(a['run_dir']) / name
                    if path.exists():
                        with path.open(errors='replace') as f:
                            f.seek(a['_offsets'].get(name, 0)); recent = f.read(); a['_offsets'][name] = f.tell()
                        base.require(not any(s in recent for s in FATAL), '引擎/服务错误: ' + a['run_id'])
                code = a['_process'].poll()
                if code is not None:
                    base.require(code == 0, '引擎异常退出: ' + a['run_id'])
                    run = next(r for r in runs if r['run_id'] == a['run_id'])
                    finished.append((a, final_result(Path(a['run_dir']), run)))
            for a, result in finished:
                state['completed'].append(result); active.remove(a)
            used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
            for run in [r for r in runs if r['run_id'] not in used][:2 - len(active)]:
                base.require(stop_at is None, '停止后不补位')
                base.require(datetime.now(timezone.utc) < datetime.fromisoformat(plan['deadline_at']), '原48小时截止已到')
                d = base.ROOT / run['run_dir']
                base.require(not d.exists(), '目标存在，不覆盖或再试')
                if run.get('resume'):
                    shutil.copytree(run['source_run_dir'], d)
                else:
                    d.mkdir()
                command = [env['PYTHON_PATH'], '-m', 'agentsociety2.society.cli', '--config', str(base.ROOT / run['config']),
                    '--steps', str(base.ROOT / run['steps']), '--run-dir', str(d), '--experiment-id', run['run_id'],
                    '--log-file', str(d / 'recovery3-engine.log'), '--batch-size', '100']
                if run.get('resume'):
                    command.append('--resume')
                with (d / 'recovery3-stdout.log').open('xb') as out, (d / 'recovery3-stderr.log').open('xb') as err:
                    proc = subprocess.Popen(command, cwd=base.ROOT, env=dict(env, AGENTSOCIETY_HOME_DIR=str(d / 'workspace')),
                                            stdout=out, stderr=err, start_new_session=True)
                active.append(dict(run_id=run['run_id'], condition=run['condition'], seed=run['seed'], run_dir=str(d),
                    child_pid=proc.pid, command=command, log_file=str(d / 'recovery3-engine.log'),
                    started_at=base.stamp(), resume=run.get('resume', False), _process=proc, _offsets={}))
                save()
            save()
            if active:
                time.sleep(10)
        state.update(status='completed', finished_at=base.stamp())
    except Exception as exc:
        stop(str(exc)); save()
        while any(a['_process'].poll() is None for a in active) and time.monotonic() - stop_at < 180:
            time.sleep(2)
        base.signal_engines(active, signal.SIGTERM)
        until = time.monotonic() + 60
        while any(a['_process'].poll() is None for a in active) and time.monotonic() < until:
            time.sleep(2)
        remaining = [a['child_pid'] for a in active if a['_process'].poll() is None]
        state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                     children_needing_attention=remaining, finished_at=None if remaining else base.stamp())
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        save()
    return state


def supervise():
    with (base.CONTROL / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan, old, runs, env, discarded = prepare()
        shutil.copy2(base.STATE, SNAPSHOT)
        dependencies = (SELF, base.HERE / 'verify_seed_extension_recovery_3.py', Path(previous.__file__),
            base.HERE / 'run_seed_extension_recovery.py', AUDIT, PROBE, CHECK)
        record = dict(authorization='用户2026-10-26：额度已恢复，尝试恢复并完成当前剩余实验，每30分钟汇报；延续原配置/总预算/原截止及完成停止结束汇报、不分析',
            prepared_at=base.stamp(), original_runtime_plan_sha256=base.digest(base.PLAN),
            original_started_at=plan['started_at'], original_deadline_at=plan['deadline_at'],
            source_state=str(SNAPSHOT.relative_to(base.ROOT)), runs=runs, completed_retained=16,
            original_body_requests=4876, original_extra_requests=8, discarded_attempts=discarded,
            resume_checks=base.read(AUDIT)['resume_checks'], historical_probes=[dict(requests=2,tokens=90),dict(requests=1,tokens=51),dict(requests=1,tokens=65)],
            recovery_3_probe=base.read(PROBE), scientific_config_changed=False,
            rule='两个检查点完整复制接续，不编辑状态或重生成既有正文；其余seed9三次补位，再失败联停，不自动继续',
            recovery_source_sha256={str(p.relative_to(base.ROOT)): base.digest(p) for p in dependencies})
        with RECORD.open('x') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        return execute(plan, old, runs, env, discarded)


def status():
    state = base.read(base.STATE)
    state['supervisor_alive'] = base.process_alive(state['supervisor_pid'], SELF.name + ' --continue-authorized')
    for a in state.get('active_runs', []):
        a.update(engine_alive=base.process_alive(a['child_pid'], a['run_dir']),
            actual_progress=base.progress(Path(a['run_dir'])), actual_agent_summary=agent_summary(Path(a['run_dir'])))
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for name in ('check','probe','continue-authorized','status','stop'):
        group.add_argument('--' + name, action='store_true')
    args = parser.parse_args()
    if args.probe:
        asyncio.run(probe())
    elif args.check:
        plan, old, runs, _, discarded = prepare()
        print(json.dumps(dict(status='passed',completed=16,remaining=5,body_before=4876,extra_before=8,
            discarded_body_requests=62,max_parallel=2,deadline_at=plan['deadline_at'],simulation_calls=0,llm_calls=0),ensure_ascii=False))
    elif args.status:
        print(json.dumps(status(),ensure_ascii=False,indent=2))
    elif args.stop:
        s=status()
        if s['supervisor_alive']:
            os.kill(s['supervisor_pid'], signal.SIGTERM)
        else:
            for a in s.get('active_runs',[]):
                if a['engine_alive']:
                    os.killpg(a['child_pid'],signal.SIGINT)
        print('已向本批匹配PID请求停止；用--status核对')
    else:
        raise SystemExit(0 if supervise()['status']=='completed' else 1)
