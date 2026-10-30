"""补齐随机/兴趣seed1–9的两路监督器；失败即停，不重跑或恢复。"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time

from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'pilot'))
import run_pilot as serial

read, write, digest, now, require = serial.read, serial.write, serial.digest, serial.now, serial.require
agent_summary, health, final_result = serial.agent_summary, serial.health, serial.final_result
progress, frozen_sources = serial.progress, serial.frozen_sources
PLAN, STATE = HERE / 'runtime_plan.json', HERE / 'batch_execution.json'
MAX_PARALLEL = 2
ALGORITHMS = ('random', 'interest')


def matrix(plan):
    runs = plan['runs']
    expected = [(seed, algorithm) for seed in range(1, 10) for algorithm in ALGORITHMS]
    require([(row['seed'], row['algorithm']) for row in runs] == expected,
            '只允许seed1–9，每seed随机→兴趣的18次固定顺序')
    require(len({row['run_id'] for row in runs}) == 18 and len({row['run_dir'] for row in runs}) == 18,
            '运行ID或输出目录重复')
    return runs


def pending_runs(runs, done, active):
    used = {row['run_id'] for row in done + active}
    return [row for row in runs if row['run_id'] not in used]


def enforce_budget(plan, done, active, extra):
    requests = sum(row['requests'] for row in done) + sum(row.get('agent_summary', {}).get('requests', 0) for row in active)
    require(0 <= extra <= plan['extra_requests_limit'] and requests <= plan['body_outer_requests_limit'],
            '新批独立请求额度越界')
    return requests


def command_matches(pid, expected):
    """核对PID仍活跃且完整参数一致，不凭路径片段发送停止信号。"""
    result = subprocess.run(['ps', '-ww', '-p', str(pid), '-o', 'stat=,command='], capture_output=True, text=True)
    parts = result.stdout.strip().split(None, 1)
    if result.returncode or len(parts) != 2 or parts[0].startswith('Z'):
        return False
    try:
        actual = shlex.split(parts[1])
    except ValueError:
        return False
    return (len(actual) == len(expected) and Path(actual[0]).resolve() == Path(expected[0]).resolve()
            and actual[1:] == expected[1:])


def environment(plan):
    env = os.environ.copy()
    env.update({key: str(value) for key, value in dotenv_values(plan['env_file']).items() if value is not None})
    require(all(env.get(key) for key in ('AGENTSOCIETY_LLM_API_KEY', 'AGENTSOCIETY_LLM_MODEL', 'AGENTSOCIETY_LLM_API_BASE')),
            '模型配置不完整')
    require(env['AGENTSOCIETY_LLM_MODEL'] == plan['requested_model'], '当前请求模型改变')
    require(hashlib.sha256(env['AGENTSOCIETY_LLM_API_BASE'].encode()).hexdigest() == plan['api_base_sha256'],
            '当前服务地址改变')
    env.update(WORKSPACE_PATH=plan['workspace'], LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False',
               ANONYMIZED_TELEMETRY='False', AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4',
               AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    return env


def validate_reuse(plan):
    """seed0仅验收来源，不加入新批排程或新预算。"""
    rows = plan['reuse_runs']
    require(len(rows) == 2 and {row['algorithm'] for row in rows} == set(ALGORITHMS)
            and all(row['seed'] == 0 for row in rows), '只允许引用两份已完成seed0')
    results = []
    for row in rows:
        directory = Path(row['run_dir']).resolve()
        result = final_result(directory, row, plan['expected_returned_model'])
        require(row.get('raw_sha256'), '复用seed0缺少原始来源哈希')
        for name, expected in row['raw_sha256'].items():
            path = (directory / name).resolve()
            require(path.is_relative_to(directory) and digest(path) == expected, '复用seed0原始数据改变')
        results.append(dict(run_id=row['run_id'], algorithm=row['algorithm'], run_dir=str(directory),
                            steps=result['steps'], actions=result['actions'], posted=result['posted']))
    return results


def preflight(plan=None):
    plan = read(PLAN) if plan is None else plan
    require(plan['execution_authorized'] is True, '缺少本批明确运行授权')
    require((plan['decision_opportunities'], plan['extra_requests_limit'], plan['body_outer_requests_limit']) ==
            (19800, 1980, 21780), '新批规模或请求上界改变')
    require(plan['max_parallel_runs'] == MAX_PARALLEL and plan['max_wall_hours'] == 48, '并行或时限不符')
    runs = matrix(plan)
    deadline = datetime.fromisoformat(plan['deadline_at'])
    created = datetime.fromisoformat(plan['created_at'])
    require(deadline - created == timedelta(hours=48) and now() < deadline, '48小时原绝对截止已到或不符')
    require(not STATE.exists(), '本批已有状态，禁止重复启动、自动重试或恢复')
    root = Path(plan['workspace']).resolve()
    ledger = Path(plan['ledger_path']).resolve()
    require(ledger.parent == HERE and not ledger.exists(), '新批账本必须独立且未创建')
    require(plan['expected_returned_model'] == 'deepseek-v4-1-flash-261017', '冻结返回模型改变')
    for row in runs:
        directory = serial.path_in(root, row['run_dir'])
        require(not directory.exists(), '输出已存在，禁止覆盖或自动重跑')
    frozen_sources(plan)
    for row in runs:
        config_path = Path(row['config'])
        if not config_path.is_absolute():
            config_path = root / config_path
        config = read(config_path)
        kw = config['env_modules'][0]['kwargs']
        require(kw['recommendation_algorithm'] == row['algorithm'] and kw['random_seed'] == row['seed']
                and kw['arrival_agent_return_policy'] == 'next_batch' and kw['chronological_total_batches'] == 693
                and len(config['agents']) == 100, '新配置的算法/seed/回流/规模不符')
        for agent in config['agents']:
            require(agent['kwargs']['content_retry_budget'] == dict(limit=1980, ledger_path=str(ledger)),
                    '新配置未使用新批1980独立账本')
    validate_reuse(plan)
    return plan, root, ledger, environment(plan)


def engine_alive(entry):
    return entry['_process'].poll() is None


def signal_engines(active, sig):
    for entry in active:
        if engine_alive(entry) and command_matches(entry['child_pid'], entry['command']):
            try:
                os.killpg(entry['child_pid'], sig)
            except ProcessLookupError:
                pass


def supervise(poll_seconds=10):
    with (HERE / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan, root, ledger, env = preflight()
        plan_hash = digest(PLAN)
        # 独占创建；绝不把旧pilot账本或已有新批计数归零。
        with ledger.open('x') as stream:
            stream.write('0')
        active = []
        state = dict(status='running', supervisor_pid=os.getpid(), started_at=now().isoformat(),
                     deadline_at=plan['deadline_at'], max_parallel=MAX_PARALLEL,
                     runtime_plan_sha256=plan_hash, controller_sha256=digest(__file__),
                     controller_command=[plan['python'], str(Path(__file__).resolve()), '--start-authorized'],
                     expected_returned_model=plan['expected_returned_model'], completed=[], active_runs=[],
                     reuse_runs=plan['reuse_runs'], extra_requests_used=0, total_body_requests=0)
        stop_requested = False

        def request_stop(*_):
            nonlocal stop_requested
            stop_requested = True

        def save():
            state['active_runs'] = [{key: value for key, value in row.items() if not key.startswith('_')} for row in active]
            state['updated_at'] = now().isoformat()
            try:
                state['extra_requests_used'] = int(ledger.read_text() or '0')
                state['total_body_requests'] = enforce_budget(plan, state['completed'], active, state['extra_requests_used'])
            except Exception as exc:
                state['accounting_error'] = str(exc)
            write(STATE, state)

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        save()
        try:
            while active or pending_runs(plan['runs'], state['completed'], active):
                require(not stop_requested, '收到本批停止请求')
                require(now() < datetime.fromisoformat(plan['deadline_at']), '达到本批原48小时截止')
                require(digest(PLAN) == plan_hash, '冻结运行计划改变')
                require(digest(__file__) == state['controller_sha256'], '本批控制器运行中改变')
                frozen_sources(plan)
                finished = []
                for entry in active:
                    directory = Path(entry['run_dir'])
                    alive = engine_alive(entry)
                    if not alive:
                        require(entry['_process'].returncode == 0, '引擎退出码异常')
                    entry['progress'] = progress(directory)
                    entry['agent_summary'] = agent_summary(directory)[0]
                    health(entry['agent_summary'], state['expected_returned_model'])
                    logfile = directory / 'engine.log'
                    if logfile.exists():
                        with logfile.open(errors='replace') as stream:
                            stream.seek(entry['_offset']); recent = stream.read(); entry['_offset'] = stream.tell()
                        require(not any(text in recent for text in ('Error executing step', 'RayTaskError', 'OutOfMemoryError')),
                                '引擎步骤或资源失败')
                    if not alive:
                        run = next(row for row in plan['runs'] if row['run_id'] == entry['run_id'])
                        finished.append((entry, final_result(directory, run, state['expected_returned_model'])))
                enforce_budget(plan, state['completed'], active, int(ledger.read_text() or '0'))
                for entry, result in finished:
                    write(HERE / f"completion_{result['run_id']}.json", result)
                    state['completed'].append(result)
                    active.remove(entry)
                for run in pending_runs(plan['runs'], state['completed'], active)[:MAX_PARALLEL - len(active)]:
                    require(not stop_requested and now() < datetime.fromisoformat(plan['deadline_at']), '停止或截止后禁止启动新条件')
                    directory = serial.path_in(root, run['run_dir'])
                    require(not directory.exists(), '拒绝覆盖或重跑已有结果')
                    directory.mkdir(parents=True)
                    config = Path(run['config']); config = config if config.is_absolute() else root / config
                    steps = Path(run['steps']); steps = steps if steps.is_absolute() else root / steps
                    command = [plan['python'], '-m', 'agentsociety2.society.cli', '--config', str(config),
                               '--steps', str(steps), '--run-dir', str(directory), '--experiment-id', run['run_id'],
                               '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
                    with (directory / 'stdout.log').open('xb') as stdout, (directory / 'stderr.log').open('xb') as stderr:
                        child = subprocess.Popen(command, cwd=root, env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                                                 stdout=stdout, stderr=stderr, start_new_session=True)
                    active.append(dict(run_id=run['run_id'], algorithm=run['algorithm'], seed=run['seed'],
                                       run_dir=str(directory), child_pid=child.pid, command=command,
                                       progress={}, agent_summary={}, _process=child, _offset=0))
                    require(len(active) <= MAX_PARALLEL, '并行超过两路')
                    save()
                save()
                if active:
                    time.sleep(poll_seconds)
            require(len(state['completed']) == 18, '18条件完成登记不全')
            state.update(status='completed', finished_at=now().isoformat())
        except Exception as exc:
            state.update(status='stopping', error=str(exc))
            signal_engines(active, signal.SIGINT)
            save()
            for sig in (signal.SIGTERM, None):
                until = time.monotonic() + 30
                while any(engine_alive(entry) for entry in active) and time.monotonic() < until:
                    time.sleep(.5)
                if sig is not None:
                    signal_engines(active, sig)
            remaining = [entry['child_pid'] for entry in active if engine_alive(entry)]
            state.update(status='stopping' if remaining else 'stopped', children_needing_attention=remaining,
                         finished_at=None if remaining else now().isoformat())
            print(str(exc), file=sys.stderr, flush=True)
        finally:
            for entry in active:
                try:
                    entry['progress'] = progress(Path(entry['run_dir']))
                    entry['agent_summary'] = agent_summary(Path(entry['run_dir']))[0]
                except Exception as exc:
                    entry['final_read_error'] = str(exc)
            save()
        return state['status'] == 'completed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--preflight', action='store_true')
    modes.add_argument('--start-authorized', action='store_true')
    modes.add_argument('--status', action='store_true')
    modes.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    if args.check:
        raise SystemExit(subprocess.run([sys.executable, str(HERE / 'test_extension.py')], cwd=HERE.parent).returncode)
    elif args.preflight:
        plan, _, _, _ = preflight()
        print(json.dumps(dict(preflight='passed', runs=18, max_parallel=MAX_PARALLEL,
                              deadline_at=plan['deadline_at'], network_calls=0)))
    elif args.status:
        state = read(STATE) if STATE.exists() else dict(status='not_started')
        for row in state.get('active_runs', []):
            row['actual_progress'] = progress(Path(row['run_dir']))
            row['actual_agent_summary'] = agent_summary(Path(row['run_dir']))[0]
            row['engine_command_matches'] = command_matches(row['child_pid'], row['command'])
        print(json.dumps(state, ensure_ascii=False, indent=2))
    elif args.stop:
        state = read(STATE)
        require(state['status'] == 'running' and command_matches(state['supervisor_pid'], state['controller_command']),
                '本批监督器完整命令或PID不匹配')
        os.kill(state['supervisor_pid'], signal.SIGTERM)
        print('已向本批监督器请求两路安全停止')
    else:
        raise SystemExit(0 if supervise() else 1)


if __name__ == '__main__':
    main()
