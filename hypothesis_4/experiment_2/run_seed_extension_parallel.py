"""接管串行主批，保留当前引擎，以最多两路填补原矩阵空位。

只改变调度；科学输入、共享账本与首次启动后的绝对截止均继承。
--check只读核验，--handoff只能执行一次，--status读取两路实际进度。
"""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit

from dotenv import dotenv_values
from run_main_experiment import read, write, digest, now, progress, completed
from run_seed_extension import agent_summary, HERE, ROOT, BATCH, STATE, MANIFEST, EXPECTED_MODEL

HISTORY = HERE / 'parallel_control'
PLAN = BATCH / 'runtime_plan.json'
LEDGER = BATCH / '_extra_attempts.count'
SERIAL = HERE / 'run_seed_extension.py'
MAX_PARALLEL = 2


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def process_alive(pid, expected):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat=,command='], capture_output=True, text=True)
    parts = result.stdout.strip().split(None, 1)
    return result.returncode == 0 and len(parts) == 2 and not parts[0].startswith('Z') and expected in parts[1]


def pending_runs(runs, done, active):
    used = {r['run_id'] for r in done + active}
    return [r for r in runs if r['run_id'] not in used]


def deadline(plan):
    return datetime.fromisoformat(plan['started_at']) + timedelta(hours=plan['max_wall_hours'])


def enforce_budget(done, active, extra, plan):
    total = sum(r['requests'] for r in done) + sum(r['agent_summary']['requests'] for r in active)
    require(0 <= extra <= plan['extra_requests_limit'], '共享额外请求额度越界')
    require(total <= plan['max_agent_body_requests'], '正文外层请求总额越界')
    return total


def final_result(directory, run):
    result = completed(directory, run)
    summary = agent_summary(directory)
    require(summary['agent_files'] == 100 and summary['decisions'] == summary['unique_decisions'] == 1100,
            '最终Agent决策不完整或重复: ' + run['run_id'])
    require(not summary['action_failures'] and not (set(summary['response_models']) - {EXPECTED_MODEL}),
            '最终Agent记录有失败或模型版本变化: ' + run['run_id'])
    return dict(run_id=run['run_id'], finished_at=now(), **result, **summary)


def preflight():
    plan, state, manifest = read(PLAN), read(STATE), read(MANIFEST)
    require(plan['authorized'] and state['status'] == 'running', '只能接管正在正常运行的已授权批次')
    require('active_runs' not in state and not (HISTORY / 'serial-state.json').exists(), '本批已交接，禁止重复接管')
    require(len(manifest['runs']) == 21 and plan['runs'] == manifest['runs'], '原21次矩阵变化')
    require((plan['decision_opportunities'], plan['extra_requests_limit'], plan['max_agent_body_requests']) ==
            (23100, 2310, 25410), '原机会或请求预算变化')
    require(datetime.now(timezone.utc) < deadline(plan), '原截止时间已到')
    require(all(digest(ROOT / p) == h for p, h in plan['source_sha256'].items()), '原105项冻结输入/代码变化')
    require(process_alive(state['supervisor_pid'], str(SERIAL)), '原监督器已退出，不能自动续跑')
    current = next(r for r in manifest['runs'] if r['run_id'] == state['current_run'])
    require(process_alive(state['child_pid'], str(ROOT / current['run_dir'])), '当前引擎未存活')
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    endpoint = urlsplit(env['AGENTSOCIETY_LLM_API_BASE'])
    require(env['AGENTSOCIETY_LLM_MODEL'] == plan['model'] and
            (endpoint.hostname, endpoint.path) == (plan['service_host'], plan['api_path']), '当前模型或接口变化')
    require(bool(env.get('AGENTSOCIETY_LLM_API_KEY')), '缺少凭据')
    env.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    require(int(LEDGER.read_text() or '0') <= 2310, '现有账本超额，不能交接')
    return manifest, plan, state, env


def release_serial(manifest, plan, previous):
    """只暂停/退出父监督器；独立session的引擎不接收任何交接信号。"""
    old_pid = previous['supervisor_pid']
    require(process_alive(old_pid, str(SERIAL)), '原监督器命令不匹配')
    os.kill(old_pid, signal.SIGSTOP)
    released = False
    try:
        previous = read(STATE)
        require(previous['supervisor_pid'] == old_pid and previous['status'] == 'running', '交接时状态改变')
        current = next(r for r in manifest['runs'] if r['run_id'] == previous['current_run'])
        directory = ROOT / current['run_dir']
        require(process_alive(previous['child_pid'], str(directory)), '待接管引擎已退出，取消交接')
        children = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,command='], text=True).splitlines()
        actual = [int(fields[0]) for line in children if len(fields := line.split(None, 2)) == 3
                  and int(fields[1]) == old_pid and 'agentsociety2.society.cli' in fields[2]]
        require(actual == [previous['child_pid']], '父进程的真实引擎与记录不一致')
        for row in previous['completed']:
            run = next(r for r in manifest['runs'] if r['run_id'] == row['run_id'])
            final_result(ROOT / run['run_dir'], run)
        summary = agent_summary(directory)
        require(not summary['action_failures'] and not (set(summary['response_models']) - {EXPECTED_MODEL}),
                '待接管引擎已有行动失败或模型变化')
        HISTORY.mkdir(exist_ok=True)
        write(HISTORY / 'serial-state.json', previous)
        write(HISTORY / 'serial-runtime-plan.json', plan)
        write(HISTORY / 'handoff-before.json', dict(old_supervisor_pid=old_pid,
              preserved_child_pid=previous['child_pid'], run_id=current['run_id'],
              progress=progress(directory), agent_summary=summary, extra_requests=int(LEDGER.read_text() or '0'),
              original_deadline_at=deadline(plan).isoformat(), captured_at=now()))
        # 串行控制器只处理TERM/INT；HUP为默认退出，仅发给父PID而非进程组。
        os.kill(old_pid, signal.SIGHUP)
        os.kill(old_pid, signal.SIGCONT)
        for _ in range(100):
            if not process_alive(old_pid, str(SERIAL)):
                released = True
                break
            time.sleep(.1)
        require(released, '原监督器未释放；不启动第二路')
        require(process_alive(previous['child_pid'], str(directory)), '交接后原引擎退出，停止接管')
        return previous
    finally:
        if not released and process_alive(old_pid, str(SERIAL)):
            os.kill(old_pid, signal.SIGCONT)


def engine_alive(item):
    proc = item.get('_process')
    return proc.poll() is None if proc is not None else process_alive(item['child_pid'], item['run_dir'])


def signal_engines(active, sig):
    for item in active:
        if engine_alive(item) and process_alive(item['child_pid'], item['run_dir']):
            os.killpg(item['child_pid'], sig)


def supervise():
    manifest, original_plan, previous, env = preflight()
    previous = release_serial(manifest, original_plan, previous)
    active = []
    state = dict(previous, supervisor_pid=os.getpid(), max_parallel=2, active_runs=[],
                 deadline_at=deadline(original_plan).isoformat(), handoff_at=now())
    for key in ('current_run', 'child_pid', 'command', 'current_agent_summary', 'progress'):
        state.pop(key, None)
    old_run = next(r for r in manifest['runs'] if r['run_id'] == previous['current_run'])
    active.append(dict(run_id=old_run['run_id'], child_pid=previous['child_pid'],
                       run_dir=str(ROOT / old_run['run_dir']), command=previous['command'],
                       adopted=True, _process=None, _offset=0, agent_summary={}, progress={}))
    stop_at = None
    stop_reason = None

    def save():
        state['active_runs'] = [{k: v for k, v in item.items() if not k.startswith('_')} for item in active]
        state.update(updated_at=now(), extra_requests_used=int(LEDGER.read_text() or '0'),
                     elapsed_seconds=(datetime.now(timezone.utc) - datetime.fromisoformat(state['started_at'])).total_seconds(),
                     budget_remaining_seconds=max(0, (deadline(original_plan) - datetime.now(timezone.utc)).total_seconds()))
        write(STATE, state)

    def request_stop(reason):
        nonlocal stop_at, stop_reason
        if stop_at is None:
            stop_at, stop_reason = time.monotonic(), reason
            state.update(status='stopping', stop_reason=reason)
            signal_engines(active, signal.SIGINT)
            save()

    signal.signal(signal.SIGTERM, lambda *_: request_stop('收到停止请求'))
    signal.signal(signal.SIGINT, lambda *_: request_stop('收到停止请求'))
    lock = (BATCH / 'supervisor.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan = dict(original_plan, serial=False, max_parallel=2, parallel_changed_at=now(),
                    parallel_authorization='用户明确授权最多2路并行，保留现有引擎，科学配置/共享总预算/原截止不变',
                    deadline_at=deadline(original_plan).isoformat(),
                    parallel_controller=str(Path(__file__).relative_to(ROOT)),
                    parallel_controller_sha256=digest(Path(__file__)),
                    original_supervisor_pid=previous['supervisor_pid'], preserved_child_pid=previous['child_pid'],
                    launch_order='按原manifest补空位，完成顺序可不同', new_engine_ray_address='local')
        write(PLAN, plan)
        save()
        while active or pending_runs(manifest['runs'], state['completed'], active):
            require(stop_at is None, stop_reason or '已请求停止')
            require(datetime.now(timezone.utc) < deadline(original_plan), '达到原48小时绝对截止')
            finished = []
            for item in active:
                directory = Path(item['run_dir'])
                alive = engine_alive(item)
                if not alive and item['_process'] is not None:
                    require(item['_process'].returncode == 0, '引擎退出码异常: ' + item['run_id'])
                item['progress'] = progress(directory)
                item['agent_summary'] = agent_summary(directory)
                summary = item['agent_summary']
                require(not summary['action_failures'], '行动/发布失败: ' + item['run_id'])
                require(not (set(summary['response_models']) - {EXPECTED_MODEL}), '返回模型版本变化: ' + item['run_id'])
                log = directory / 'engine.log'
                if log.exists():
                    with log.open(errors='replace') as file:
                        file.seek(item['_offset'])
                        recent = file.read()
                        item['_offset'] = file.tell()
                    require(not any(s in recent for s in ('Error executing step', 'RayTaskError', 'OutOfMemoryError')),
                            '引擎日志异常: ' + item['run_id'])
                if not alive:
                    run = next(r for r in manifest['runs'] if r['run_id'] == item['run_id'])
                    finished.append((item, final_result(directory, run)))
            state['total_body_requests'] = enforce_budget(state['completed'], active,
                                                         int(LEDGER.read_text() or '0'), original_plan)
            for item, result in finished:
                state['completed'].append(result)
                active.remove(item)
            for run in pending_runs(manifest['runs'], state['completed'], active)[:MAX_PARALLEL - len(active)]:
                require(stop_at is None, '已请求停止，禁止填补新条件')
                require(all(digest(ROOT / p) == h for p, h in original_plan['source_sha256'].items()),
                        '冻结输入或代码变化')
                directory = ROOT / run['run_dir']
                require(not directory.exists(), '拒绝覆盖或重跑: ' + run['run_id'])
                directory.mkdir()
                command = [env.get('PYTHON_PATH') or sys.executable, '-m', 'agentsociety2.society.cli',
                           '--config', str(ROOT / run['config']), '--steps', str(ROOT / run['steps']),
                           '--run-dir', str(directory), '--experiment-id', run['run_id'],
                           '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
                with (directory / 'stdout.log').open('ab') as stdout, (directory / 'stderr.log').open('ab') as stderr:
                    proc = subprocess.Popen(command, cwd=ROOT,
                        env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                        stdout=stdout, stderr=stderr, start_new_session=True)
                active.append(dict(run_id=run['run_id'], child_pid=proc.pid, run_dir=str(directory),
                                   command=command, adopted=False, _process=proc, _offset=0,
                                   agent_summary={}, progress={}))
                require(len(active) <= MAX_PARALLEL, '并行路数超过2')
                save()
            save()
            time.sleep(10)
        state.update(status='completed', finished_at=now())
    except Exception as exc:
        request_stop(str(exc))
        while any(engine_alive(item) for item in active) and time.monotonic() - stop_at < 180:
            time.sleep(2)
        signal_engines(active, signal.SIGTERM)
        term_at = time.monotonic()
        while any(engine_alive(item) for item in active) and time.monotonic() - term_at < 60:
            time.sleep(2)
        remaining = [item['child_pid'] for item in active if engine_alive(item)]
        state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                     children_needing_attention=remaining, finished_at=now() if not remaining else None)
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        for item in active:
            item['progress'] = progress(Path(item['run_dir']))
            item['agent_summary'] = agent_summary(Path(item['run_dir']))
        save()
        lock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--handoff', action='store_true')
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    if args.status:
        state = read(STATE)
        state['supervisor_alive'] = process_alive(state['supervisor_pid'], str(Path(__file__)))
        for item in state.get('active_runs', []):
            item['engine_alive'] = process_alive(item['child_pid'], item['run_dir'])
            item['actual_progress'] = progress(Path(item['run_dir']))
            item['actual_agent_summary'] = agent_summary(Path(item['run_dir']))
        print(json.dumps(state, ensure_ascii=False, indent=2))
    elif args.check:
        manifest, plan, state, _ = preflight()
        print(json.dumps(dict(preflight='PASS', runs=len(manifest['runs']), max_parallel=2,
                             preserved_child_pid=state['child_pid'], deadline_at=deadline(plan).isoformat(),
                             extra_requests=int(LEDGER.read_text() or '0'), llm_calls=0), ensure_ascii=False))
    elif args.handoff:
        supervise()
    else:
        parser.error('必须显式指定--check、--handoff或--status；不自动重启')
