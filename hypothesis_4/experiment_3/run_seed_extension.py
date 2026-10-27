"""执行已授权的21次兴趣B/D/R消融；最多两路，失败联停，不自动重跑。"""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit

from dotenv import dotenv_values
from seed_extension_guard import check_limits

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROL = HERE / 'runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9'
MANIFEST = HERE / 'init/manifest_seed3_9.json'
STATE = CONTROL / 'batch_execution.json'
PLAN = CONTROL / 'runtime_plan.json'
EXPECTED_MODEL = 'deepseek-v4-1-flash-261017'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def agent_summary(directory):
    result = dict(agent_files=0, decisions=0, unique_decisions=0, posted=0, requests=0,
                  action_failures=0, response_models={})
    unique = set()
    for path in sorted((directory / 'agents').glob('*/AGENT.json')):
        try:
            agent = read(path)
        except (OSError, ValueError):
            continue
        result['agent_files'] += 1
        for row in agent.get('decision_log', []):
            result['decisions'] += 1
            unique.add((str(agent['id']), row['week']))
            result['posted'] += bool(row.get('posted'))
            result['requests'] += row.get('generation_attempts', 0)
            result['action_failures'] += row.get('reason') in ('action_failed', 'publication_failed')
            if row.get('response_model'):
                model = row['response_model']
                result['response_models'][model] = result['response_models'].get(model, 0) + 1
    result['unique_decisions'] = len(unique)
    return result


def progress(directory):
    result = {}
    for name in ('pid.json', 'SOCIETY_STEP.json'):
        try:
            result[name] = read(directory / name)
        except (OSError, ValueError):
            pass
    return result


def completed(directory, run):
    """核验完整笛卡尔矩阵，不以监督器退出文字替代原始记录。"""
    info = progress(directory)
    require(info.get('pid.json', {}).get('status') == 'completed', '引擎未报告完成')
    require(info.get('SOCIETY_STEP.json', {}).get('step_count') == 693, '步数未完成693')
    arrival = read(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')['_arrival_state']
    expected = {(str(a), f'2026-W{w}') for a in range(1, 101) for w in range(12, 23)}
    actions = arrival['actions']
    require(len(actions) == 1100 and {(str(r['agent_id']), r['week']) for r in actions} == expected,
            '环境行动矩阵缺失或重复')
    require(len(arrival['weeks']) == 11 and
            {r['week'] for r in arrival['weeks']} == {f'2026-W{w}' for w in range(12, 23)}, '周汇总不完整')
    summary = agent_summary(directory)
    require(summary['agent_files'] == 100 and summary['decisions'] == summary['unique_decisions'] == 1100,
            'Agent决策数量不完整或重复')
    decisions = set()
    for path in (directory / 'agents').glob('*/AGENT.json'):
        a = read(path)
        for row in a['decision_log']:
            decisions.add((str(a['id']), row['week']))
            require(row.get('reason') not in ('action_failed', 'publication_failed'), 'Agent行动/发布失败')
            if row.get('posted'):
                require(row.get('content') and row.get('post_id') is not None and
                        row.get('response_model') == EXPECTED_MODEL, '发布记录缺正文/ID或模型变化')
    require(decisions == expected, 'Agent决策矩阵缺失')
    require(not summary['action_failures'] and not(set(summary['response_models']) - {EXPECTED_MODEL}),
            '存在行动失败或返回模型变化')
    return dict(run_id=run['run_id'], run_dir=str(directory), finished_at=stamp(),
                steps=693, actions=1100, weeks=11, **summary)


def ledger_count(plan):
    with (ROOT / plan['budget']['ledger_path']).open() as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        return int(f.read().strip())


def process_alive(pid, expected):
    r = subprocess.run(['ps', '-p', str(pid), '-o', 'stat=,command='], capture_output=True, text=True)
    parts = r.stdout.strip().split(None, 1)
    return r.returncode == 0 and len(parts) == 2 and not parts[0].startswith('Z') and expected in parts[1]


def preflight():
    require(not PLAN.exists() and not STATE.exists(), '本批已有正式记录，禁止覆盖、重复启动或自动恢复')
    m = read(MANIFEST)
    prep = read(CONTROL / 'preparation_plan.json')
    report = read(HERE / 'checks/seed3_9_preparation_check.json')
    require(report['status'] == 'passed' and report['manifest_sha256'] == digest(MANIFEST), '准备验收或manifest变化')
    controller_check = read(HERE / 'checks/seed3_9_controller_check.json')
    require(controller_check['status'] == 'passed' and
            controller_check['controller_sha256'] == digest(Path(__file__)), '调度器离线检查缺失或过期')
    require(read(HERE / 'checks/seed3_9_offline_verification.json')['status'] == 'passed', '离线验收未通过')
    require(read(HERE / 'checks/model_probe_seed3_9_token_cap_correction.json')['status'] == 'passed', '接口探针未通过')
    require([(r['seed'], r['condition']) for r in m['runs']] ==
            [(s, c) for s in range(3, 10) for c in ('no_b', 'no_d', 'no_r')], '矩阵或顺序变化')
    frozen = {}
    for group in ('source_sha256', 'mechanism_sha256', 'output_sha256', 'old_assets_unchanged_sha256'):
        frozen.update(m[group])
    frozen.update(prep['control_sha256'])
    frozen[str(Path(__file__).relative_to(ROOT))] = digest(Path(__file__))
    for name, expected in frozen.items():
        require(digest(ROOT / name) == expected, '冻结来源/配置/控制代码变化: ' + name)
    require(all(not (ROOT / r['run_dir']).exists() for r in m['runs']), '目标运行目录已存在，不自动重试')
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    require(env.get('AGENTSOCIETY_LLM_MODEL') == m['model']['configured_alias'], '当前请求模型变化')
    require(bool(env.get('AGENTSOCIETY_LLM_API_KEY')), '缺少模型凭据')
    probe = read(HERE / 'checks/model_probe_seed3_9_token_cap_correction.json')
    endpoint = urlsplit(env['AGENTSOCIETY_LLM_API_BASE'])
    require((endpoint.hostname, endpoint.path) == (probe['service_host'], probe['api_path']), '当前接口变化')
    env.update(PYTHON_PATH=env.get('PYTHON_PATH') or sys.executable,
               LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    require(ledger_count(prep) == 0, '独立账本不为0，禁止归零重启')
    require((HERE / 'runs/timestamp_bdr_v1_attempt_02/_extra_attempts.count').read_text().strip() == '5',
            '旧账本变化')
    return m, prep, env, frozen


def signal_engines(active, signum):
    for a in active:
        if a['_process'].poll() is None:
            try:
                os.killpg(a['child_pid'], signum)
            except ProcessLookupError:
                pass


def execute(plan, env):
    active = []
    state = dict(batch_id=plan['batch_id'], hypothesis_id=4, experiment_id=3, status='running',
                 supervisor_pid=os.getpid(), started_at=plan['started_at'], deadline_at=plan['deadline_at'],
                 completed=[], active_runs=[], total_runs=21, extra_requests_used=0, body_requests_used=0)
    stop_at = None

    def save():
        for a in active:
            a['progress'] = progress(Path(a['run_dir']))
            a['agent_summary'] = agent_summary(Path(a['run_dir']))
        state['active_runs'] = [{k: v for k, v in a.items() if not k.startswith('_')} for a in active]
        state['body_requests_used'] = sum(x['requests'] for x in state['completed']) + sum(
            a['agent_summary']['requests'] for a in active)
        state['extra_requests_used'] = ledger_count(plan)
        state['updated_at'] = stamp()
        write(STATE, state)

    def stop(reason):
        nonlocal stop_at
        if stop_at is None:
            stop_at = time.monotonic()
            state.update(status='stopping', stop_reason=reason)
            signal_engines(active, signal.SIGINT)

    signal.signal(signal.SIGTERM, lambda *_: stop('收到停止请求'))
    signal.signal(signal.SIGINT, lambda *_: stop('收到停止请求'))
    try:
        save()
        while active or len(state['completed']) < len(plan['runs']):
            require(stop_at is None, state.get('stop_reason', '停止请求'))
            save()
            check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
                         body_requests=state['body_requests_used'], extra_requests=state['extra_requests_used'],
                         active_runs=len(active))
            for name, expected in plan['live_guard_sha256'].items():
                require(digest(ROOT / name) == expected, '运行期间冻结参数/机制变化: ' + name)
            finished = []
            for a in active:
                summary = a['agent_summary']
                require(not summary['action_failures'], '行动或发布失败: ' + a['run_id'])
                require(not(set(summary['response_models']) - {EXPECTED_MODEL}), '实际返回模型变化: ' + a['run_id'])
                for name in ('engine.log', 'stderr.log'):
                    path = Path(a['run_dir']) / name
                    if path.exists():
                        with path.open(errors='replace') as f:
                            f.seek(a['_offsets'].get(name, 0)); recent = f.read(); a['_offsets'][name] = f.tell()
                        require(not any(s in recent for s in
                            ('Error executing step', 'RayTaskError', 'LLMDispatchError', 'OutOfMemoryError')),
                            '引擎日志失败: ' + a['run_id'])
                code = a['_process'].poll()
                if code is not None:
                    require(code == 0, '引擎异常退出: ' + a['run_id'] + ' code=' + str(code))
                    run = next(r for r in plan['runs'] if r['run_id'] == a['run_id'])
                    finished.append((a, completed(Path(a['run_dir']), run)))
            for a, result in finished:
                state['completed'].append(result)
                active.remove(a)
            used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
            pending = [r for r in plan['runs'] if r['run_id'] not in used]
            for run in pending[:2 - len(active)]:
                require(stop_at is None, '停止后禁止继续补位')
                require(datetime.now(timezone.utc) < datetime.fromisoformat(plan['deadline_at']), '48小时截止已到')
                require(all(digest(ROOT / p) == h for p, h in plan['source_sha256'].items()), '冻结来源变化')
                directory = ROOT / run['run_dir']
                require(not directory.exists(), '目录已存在，禁止覆盖或重试: ' + run['run_id'])
                directory.mkdir()
                log = directory / 'engine.log'
                command = [env['PYTHON_PATH'], '-m', 'agentsociety2.society.cli',
                    '--config', str(ROOT / run['config']), '--steps', str(ROOT / run['steps']),
                    '--run-dir', str(directory), '--experiment-id', run['run_id'],
                    '--log-file', str(log), '--batch-size', '100']
                with (directory / 'stdout.log').open('xb') as out, (directory / 'stderr.log').open('xb') as err:
                    proc = subprocess.Popen(command, cwd=ROOT,
                        env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                        stdout=out, stderr=err, start_new_session=True)
                active.append(dict(run_id=run['run_id'], condition=run['condition'], seed=run['seed'],
                    run_dir=str(directory), child_pid=proc.pid, command=command, log_file=str(log),
                    started_at=stamp(), _process=proc, _offsets={}))
                save()
            save()
            if active:
                time.sleep(10)
        state.update(status='completed', finished_at=stamp())
    except Exception as exc:
        stop(str(exc))
        signal_engines(active, signal.SIGINT)
        save()
        while any(a['_process'].poll() is None for a in active) and time.monotonic() - stop_at < 180:
            time.sleep(2)
        signal_engines(active, signal.SIGTERM)
        until = time.monotonic() + 60
        while any(a['_process'].poll() is None for a in active) and time.monotonic() < until:
            time.sleep(2)
        remaining = [a['child_pid'] for a in active if a['_process'].poll() is None]
        state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                     children_needing_attention=remaining, finished_at=None if remaining else stamp())
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        save()
    return state


def supervise():
    with (CONTROL / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m, prep, env, frozen = preflight()
        started = datetime.now(timezone.utc)
        plan = dict(authorized=True, execution_authorized=True, hypothesis_id=4, experiment_id=3,
            batch_id=m['batch_id'], authorization='2026-10-24用户明确正式启动seed3–9兴趣B/D/R21次、两路并行、冻结预算及48小时，每30分钟汇报，完成或停止暂停，不分析',
            started_at=started.isoformat(), deadline_at=(started + timedelta(hours=48)).isoformat(),
            max_parallel=2, max_wall_hours=48, model=m['model']['configured_alias'], expected_response_model=EXPECTED_MODEL,
            budget=prep['budget'], execution_conditions=prep['execution_conditions'], runs=m['runs'],
            source_sha256=frozen, live_guard_sha256={p: h for p, h in frozen.items()
                if p.startswith('custom/') or p in m['output_sha256'] or p in prep['control_sha256']
                or p == str(Path(__file__).relative_to(ROOT))},
            stop_policy=prep['stop_policy'], probe_requests=2, probe_tokens=90, probe_in_body_budget=False,
            preparation_plan_sha256=digest(CONTROL / 'preparation_plan.json'),
            manifest_sha256=digest(MANIFEST), supervisor_sha256=digest(Path(__file__)))
        plan['budget'] = dict(plan['budget'], started_at=plan['started_at'], deadline_at=plan['deadline_at'], execution_authorized=True)
        with PLAN.open('x') as f:
            f.write(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        return execute(plan, env)


def status():
    if not STATE.exists():
        return dict(status='prepared_not_started', total_runs=21, active_runs=[], completed=[])
    state = read(STATE)
    state['supervisor_alive'] = process_alive(state['supervisor_pid'], str(Path(__file__)))
    for a in state.get('active_runs', []):
        a['engine_alive'] = process_alive(a['child_pid'], a['run_dir'])
        a['actual_progress'] = progress(Path(a['run_dir']))
        a['actual_agent_summary'] = agent_summary(Path(a['run_dir']))
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--status', action='store_true')
    group.add_argument('--stop', action='store_true')
    group.add_argument('--start-authorized', action='store_true')
    args = parser.parse_args()
    if args.check:
        m, _, _, frozen = preflight()
        print(json.dumps(dict(status='passed', new_conditions=len(m['runs']), frozen_files=len(frozen),
                              max_parallel=2, simulation_calls=0, llm_calls=0), ensure_ascii=False))
    elif args.status:
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif args.stop:
        state = read(STATE)
        if process_alive(state['supervisor_pid'], str(Path(__file__))):
            os.kill(state['supervisor_pid'], signal.SIGTERM)
        else:
            for a in state.get('active_runs', []):
                if process_alive(a['child_pid'], a['run_dir']):
                    os.killpg(a['child_pid'], signal.SIGINT)
        print('已向本批实际匹配的进程发送停止请求；用--status核对是否完全退出')
    else:
        result = supervise()
        raise SystemExit(0 if result['status'] == 'completed' else 1)
