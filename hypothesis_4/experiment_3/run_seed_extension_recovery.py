"""本次明确授权的单次接续：保留10次完成和两份失败现场，原截止/账本不重置。"""
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
from urllib.parse import urlsplit

from dotenv import dotenv_values
import run_seed_extension as base

SELF = Path(__file__).resolve()
RECORD = base.CONTROL / 'recovery_1.json'
SNAPSHOT = base.CONTROL / 'stopped_execution_1.json'
AUDIT = base.CONTROL / 'recovery_1_offline_check.json'
PROBE = base.CONTROL / 'recovery_probe_1.json'
CHECK = base.CONTROL / 'recovery_1_controller_check.json'
FATAL = ('Error executing step', 'RayTaskError', 'LLMDispatchError', 'OutOfMemoryError',
         'RateLimitError', 'usage quota', 'AuthenticationError', 'PermissionDeniedError',
         'ServiceUnavailableError', 'APIConnectionError')


def environment(plan):
    env = dict(os.environ)
    env.update({k: str(v) for k, v in dotenv_values(base.ROOT / '.env').items() if v is not None})
    reference = base.read(base.HERE / 'checks/model_probe_seed3_9_token_cap_correction.json')
    endpoint = urlsplit(env['AGENTSOCIETY_LLM_API_BASE'])
    base.require(env['AGENTSOCIETY_LLM_MODEL'] == plan['model'] and
        (endpoint.hostname, endpoint.path) == (reference['service_host'], reference['api_path']), '模型或接口变化')
    base.require(bool(env.get('AGENTSOCIETY_LLM_API_KEY')), '缺少凭据')
    env.update(PYTHON_PATH=env.get('PYTHON_PATH') or sys.executable, PYTHONDONTWRITEBYTECODE='1',
        LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
        AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    return env


async def probe():
    """恢复前一次短探针；显式单列，不占用仿真正文或共享额外账本。"""
    base.require(not PROBE.exists() and base.read(AUDIT)['status'] == 'passed', '先通过离线核查；不覆盖或重复探针')
    plan = base.read(base.PLAN)
    os.environ.update(environment(plan))
    from agentsociety2.config.config import Config
    before = (base.ROOT / plan['budget']['ledger_path']).read_bytes()
    report = dict(status='testing', authorization='用户2026-10-24明确授权额度恢复后继续剩余消融',
        started_at=base.stamp(), attempted_requests=1, completed_requests=0, simulation_requests=0,
        counted_in_formal_body_budget=False, requested_model=plan['model'])
    with PROBE.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    try:
        router = Config.get_router()
        router.num_retries, router.fallbacks = 0, []
        result = await router.acompletion(model=plan['model'], messages=[{'role': 'user', 'content': '请只回复OK。'}],
            max_tokens=128, temperature=1.0, timeout=60, num_retries=0, caching=False, stream=False)
        report.update(completed_requests=1, response_model=result.model,
            content=result.choices[0].message.content or '', usage=result.usage.model_dump() if result.usage else None)
        base.require(result.model == base.EXPECTED_MODEL and report['content'].strip().strip('。.!！') == 'OK', '探针模型/正文不符')
        report['status'] = 'passed'
    except Exception as exc:
        report.update(status='failed', error_type=type(exc).__name__, status_code=getattr(exc, 'status_code', None))
    finally:
        report.update(finished_at=base.stamp(), ledger_unchanged=(base.ROOT / plan['budget']['ledger_path']).read_bytes() == before)
        base.require(report['ledger_unchanged'], '探针改变正文额外账本')
        base.write(PROBE, report)
    print(json.dumps(report, ensure_ascii=False))
    base.require(report['status'] == 'passed', '服务未通过恢复探针，不启动')


def prepare():
    plan, old, audit = base.read(base.PLAN), base.read(base.STATE), base.read(AUDIT)
    base.require(not RECORD.exists() and not SNAPSHOT.exists() and old['status'] == 'stopped', '只允许本次接续一次')
    base.require(not base.process_alive(old['supervisor_pid'], 'run_seed_extension'), '旧监督器仍活着')
    base.require(all(not base.process_alive(a['child_pid'], a['run_dir']) for a in old['active_runs']), '旧引擎仍活着')
    base.require(audit['status'] == 'passed' and base.read(PROBE)['status'] == 'passed', '离线检查或额度探针未通过')
    base.require(len(old['completed']) == 10 and base.ledger_count(plan) == 4, '停止基线变化')
    for p, h in {**plan['source_sha256'], **audit['preserved_sha256']}.items():
        base.require(base.digest(base.ROOT / p) == h, '冻结来源/已完成/失败现场变化: ' + p)
    base.check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
        body_requests=3208, extra_requests=4, active_runs=0)
    checked = {r['run_id']: r for r in audit['resume_checks']}
    runs = [dict(r) for r in plan['runs']]
    for run in runs:
        if run['run_id'] in checked:
            base.require(checked[run['run_id']]['safe_to_resume'], '检查点不可安全接续')
            run.update(source_run_dir=checked[run['run_id']]['source_run_dir'], resume=True,
                       prior_requests=checked[run['run_id']]['body_requests'],
                       run_dir=run['run_dir'] + '_resume1')
        if run['run_id'] not in {r['run_id'] for r in old['completed']}:
            base.require(not (base.ROOT / run['run_dir']).exists(), '目标已存在，不覆盖或自动再试')
    return plan, old, runs, environment(plan)


def execute(plan, old, runs, env):
    active = []
    state = dict(old, status='running', supervisor_pid=os.getpid(), active_runs=[],
        controller=str(SELF.relative_to(base.ROOT)), recovery_record=str(RECORD.relative_to(base.ROOT)),
        recovery_started_at=base.stamp())
    for key in ('error', 'stop_reason', 'finished_at', 'children_needing_attention'):
        state.pop(key, None)
    stop_at = None

    def save():
        for a in active:
            a['progress'], a['agent_summary'] = base.progress(Path(a['run_dir'])), base.agent_summary(Path(a['run_dir']))
        state['active_runs'] = [{k: v for k, v in a.items() if not k.startswith('_')} for a in active]
        # 副本已累计接续前262/208次请求；原失败目录不重复相加。
        state['body_requests_used'] = sum(r['requests'] for r in state['completed']) + sum(a['agent_summary']['requests'] for a in active)
        used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
        state['body_requests_used'] += sum(r.get('prior_requests', 0) for r in runs if r['run_id'] not in used)
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
                base.require(not(set(summary['response_models']) - {base.EXPECTED_MODEL}), '实际返回模型变化')
                for name in ('recovery-engine.log', 'recovery-stderr.log'):
                    path = Path(a['run_dir']) / name
                    if path.exists():
                        with path.open(errors='replace') as f:
                            f.seek(a['_offsets'].get(name, 0)); recent = f.read(); a['_offsets'][name] = f.tell()
                        base.require(not any(s in recent for s in FATAL), '引擎/服务错误: ' + a['run_id'])
                code = a['_process'].poll()
                if code is not None:
                    base.require(code == 0, '引擎异常退出: ' + a['run_id'])
                    run = next(r for r in runs if r['run_id'] == a['run_id'])
                    finished.append((a, base.completed(Path(a['run_dir']), run)))
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
                    '--log-file', str(d / 'recovery-engine.log'), '--batch-size', '100']
                if run.get('resume'):
                    command.append('--resume')
                with (d / 'recovery-stdout.log').open('xb') as out, (d / 'recovery-stderr.log').open('xb') as err:
                    proc = subprocess.Popen(command, cwd=base.ROOT, env=dict(env, AGENTSOCIETY_HOME_DIR=str(d / 'workspace')),
                                            stdout=out, stderr=err, start_new_session=True)
                active.append(dict(run_id=run['run_id'], condition=run['condition'], seed=run['seed'], run_dir=str(d),
                    child_pid=proc.pid, command=command, log_file=str(d / 'recovery-engine.log'),
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
        plan, old, runs, env = prepare()
        check = base.read(CHECK)
        base.require(check['status'] == 'passed' and check['controller_sha256'] == base.digest(SELF), '接续调度检查未通过或过期')
        shutil.copy2(base.STATE, SNAPSHOT)
        record = dict(authorization='用户2026-10-24：额度恢复后继续剩余消融，先核查两次中断安全接续，保留完成与失败现场，原配置/总预算/截止，30分钟汇报，不分析',
            prepared_at=base.stamp(), original_runtime_plan_sha256=base.digest(base.PLAN),
            original_started_at=plan['started_at'], original_deadline_at=plan['deadline_at'],
            source_state=str(SNAPSHOT.relative_to(base.ROOT)), runs=runs, completed_retained=10,
            original_body_requests=3208, original_extra_requests=4, discarded_attempts=[],
            prior_probe_requests=2, prior_probe_tokens=90, recovery_probe=base.read(PROBE),
            scientific_config_changed=False, rule='两份完整复制接续；后续9次补位。再次失败即联停，不自行重试',
            recovery_source_sha256={str(p.relative_to(base.ROOT)): base.digest(p) for p in
                (SELF, base.HERE / 'verify_seed_extension_recovery.py', AUDIT, PROBE, CHECK)})
        with RECORD.open('x') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        return execute(plan, old, runs, env)


def status():
    state = base.read(base.STATE)
    state['supervisor_alive'] = base.process_alive(state['supervisor_pid'], str(SELF))
    for a in state.get('active_runs', []):
        a.update(engine_alive=base.process_alive(a['child_pid'], a['run_dir']),
                 actual_progress=base.progress(Path(a['run_dir'])), actual_agent_summary=base.agent_summary(Path(a['run_dir'])))
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for option in ('check', 'probe', 'continue-authorized', 'status', 'stop'):
        group.add_argument('--' + option, action='store_true')
    args = parser.parse_args()
    if args.probe:
        asyncio.run(probe())
    elif args.check:
        plan, old, runs, _ = prepare()
        print(json.dumps(dict(status='passed', completed=len(old['completed']), remaining=11,
            resume=[r['run_id'] for r in runs if r.get('resume')], deadline_at=plan['deadline_at'], simulation_calls=0), ensure_ascii=False))
    elif args.status:
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif args.stop:
        s = status()
        if s['supervisor_alive']:
            os.kill(s['supervisor_pid'], signal.SIGTERM)
        else:
            for a in s.get('active_runs', []):
                if a['engine_alive']:
                    os.killpg(a['child_pid'], signal.SIGINT)
        print('已按实际PID与命令请求停止本批；继续用--status核对')
    else:
        raise SystemExit(0 if supervise()['status'] == 'completed' else 1)
