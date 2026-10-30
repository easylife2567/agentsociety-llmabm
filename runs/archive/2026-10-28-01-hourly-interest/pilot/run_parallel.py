"""接管本pilot的在跑引擎，最多两路补齐三臂；不重跑、不重置预算或截止。"""
from __future__ import annotations

import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from dotenv import dotenv_values
import run_pilot as serial

read, write, digest, now, require = serial.read, serial.write, serial.digest, serial.now, serial.require
agent_summary, health, final_result = serial.agent_summary, serial.health, serial.final_result
progress, frozen_sources, process_matches = serial.progress, serial.frozen_sources, serial.process_matches
HERE = Path(__file__).resolve().parent
PLAN, STATE = HERE / 'runtime_plan.json', HERE / 'batch_execution.json'
REVISION, HISTORY = HERE / 'parallel_revision.json', HERE / 'parallel_handoff'
SERIAL = HERE / 'run_pilot.py'
MAX_PARALLEL = 2


def pending_runs(runs, done, active):
    used = {item['run_id'] for item in done + active}
    return [run for run in runs if run['run_id'] not in used]


def enforce_budget(plan, done, active, extra):
    total = sum(item['requests'] for item in done) + sum(item.get('agent_summary', {}).get('requests', 0) for item in active)
    require(0 <= extra <= plan['extra_requests_limit'] and total <= plan['body_outer_requests_limit'], '本批共享请求预算越界')
    return total


def environment(plan):
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(plan['env_file']).items() if v is not None})
    require(all(env.get(k) for k in ('AGENTSOCIETY_LLM_API_KEY', 'AGENTSOCIETY_LLM_MODEL', 'AGENTSOCIETY_LLM_API_BASE')), '模型配置不完整')
    require(env['AGENTSOCIETY_LLM_MODEL'] == plan['requested_model'], '请求模型改变')
    require(hashlib.sha256(env['AGENTSOCIETY_LLM_API_BASE'].encode()).hexdigest() == plan['api_base_sha256'], '服务地址改变')
    env.update(WORKSPACE_PATH=plan['workspace'], LITELLM_LOCAL_MODEL_COST_MAP='True',
               MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    return env


def preflight():
    plan, revision, state = read(PLAN), read(REVISION), read(STATE)
    require(plan['execution_authorized'] and revision['execution_authorized'], '缺少本次运行或并行授权')
    require(revision['max_parallel'] == MAX_PARALLEL and revision['runtime_plan_sha256'] == digest(PLAN), '并行授权或原计划不匹配')
    require(revision['controller_sha256'] == digest(__file__), '并行控制器哈希不匹配')
    for key, expected in (('decision_opportunities', 3300), ('extra_requests_limit', 330), ('body_outer_requests_limit', 3630)):
        require(plan[key] == revision[key] == expected, '原总预算变化')
    require(revision['deadline_at'] == plan['deadline_at'] and now() < datetime.fromisoformat(plan['deadline_at']), '原绝对截止已到或改变')
    require(tuple(r['algorithm'] for r in plan['runs']) == serial.ALGORITHMS, '原三臂矩阵改变')
    require(state['status'] == 'running' and 'active_runs' not in state and not (HISTORY / 'serial-state.json').exists(), '只能交接一次正常串行批次')
    require(state['runtime_plan_sha256'] == digest(PLAN), '在跑批次使用不同原计划')
    require(state['expected_returned_model'] == revision['expected_returned_model'], '实际模型锁定不同')
    require(process_matches(state['supervisor_pid'], str(SERIAL)), '旧监督器PID身份不匹配')
    current = state.get('active_run')
    require(current is not None, '旧监督器正处于条件转场，请稍后重新只读检查')
    run = next(r for r in plan['runs'] if r['run_id'] == current['run_id'])
    require(Path(run['run_dir']).resolve() == Path(current['run_dir']).resolve(), '在跑目录与计划不符')
    require(process_matches(current['child_pid'], current['run_dir']), '旧引擎已退出或PID身份不匹配')
    frozen_sources(plan)
    summary = agent_summary(Path(current['run_dir']))[0]
    health(summary, revision['expected_returned_model'])
    enforce_budget(plan, state['completed'], [dict(current, agent_summary=summary)], int(Path(plan['ledger_path']).read_text() or '0'))
    for completed in state['completed']:
        row = next(r for r in plan['runs'] if r['run_id'] == completed['run_id'])
        final_result(Path(row['run_dir']), row, revision['expected_returned_model'])
    for row in pending_runs(plan['runs'], state['completed'], [current]):
        require(not Path(row['run_dir']).exists(), '未登记条件已有目录，拒绝重跑')
    return plan, revision, state, environment(plan)


def release_serial(plan, previous):
    """仅对旧父PID发STOP/HUP/CONT，独立session的在跑引擎保持连续。"""
    old_pid = previous['supervisor_pid']
    require(process_matches(old_pid, str(SERIAL)), '旧监督器身份变化')
    os.kill(old_pid, signal.SIGSTOP)
    released = False
    try:
        previous = read(STATE)
        require(previous['supervisor_pid'] == old_pid and previous['status'] == 'running' and 'active_runs' not in previous, '冻结旧父时批次状态改变')
        item = previous.get('active_run')
        require(item is not None, '冻结恰逢条件转场，取消交接并恢复旧父')
        run = next(r for r in plan['runs'] if r['run_id'] == item['run_id'])
        directory = Path(item['run_dir'])
        require(directory == Path(run['run_dir']) and process_matches(item['child_pid'], str(directory)), '冻结时引擎已退出或身份不符，取消交接')
        children = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,command='], text=True).splitlines()
        actual = [int(fields[0]) for line in children if len(fields := line.split(None, 2)) == 3
                  and int(fields[1]) == old_pid and 'agentsociety2.society.cli' in fields[2]]
        require(actual == [item['child_pid']], '旧父的真实引擎与记录不一致')
        health(agent_summary(directory)[0], previous['expected_returned_model'])
        frozen_sources(plan)
        HISTORY.mkdir(exist_ok=True)
        require(not (HISTORY / 'serial-state.json').exists(), '已有交接历史，拒绝重复')
        write(HISTORY / 'serial-state.json', previous)
        write(HISTORY / 'serial-runtime-plan.json', plan)
        write(HISTORY / 'handoff-before.json', dict(captured_at=now().isoformat(), old_supervisor_pid=old_pid,
              preserved_child_pid=item['child_pid'], run_id=item['run_id'], progress=progress(directory),
              agent_summary=agent_summary(directory)[0], extra_requests_used=int(Path(plan['ledger_path']).read_text() or '0'),
              original_deadline_at=plan['deadline_at']))
        # 旧控制器只注册TERM/INT；默认HUP退出父进程，不触及独立引擎进程组。
        os.kill(old_pid, signal.SIGHUP)
        os.kill(old_pid, signal.SIGCONT)
        for _ in range(100):
            if not process_matches(old_pid, str(SERIAL)):
                released = True
                break
            time.sleep(.1)
        require(released, '旧监督器未退出，禁止启动第二路')
        # 引擎可在交接瞬间正常完成；主循环会严格核验并吸收完成记录。
        return previous
    finally:
        if not released and process_matches(old_pid, str(SERIAL)):
            os.kill(old_pid, signal.SIGCONT)


def engine_alive(item):
    proc = item.get('_process')
    return proc.poll() is None if proc is not None else process_matches(item['child_pid'], item['run_dir'])


def signal_engines(active, sig):
    for item in active:
        if engine_alive(item) and process_matches(item['child_pid'], item['run_dir']):
            try:
                os.killpg(item['child_pid'], sig)
            except ProcessLookupError:
                pass


def supervise(poll_seconds=10):
    plan, revision, previous, env = preflight()
    plan_hash, revision_hash = digest(PLAN), digest(REVISION)
    previous = release_serial(plan, previous)
    item = previous['active_run']
    active = [dict(item, adopted=True, _process=None, _offset=0)]
    state = dict(previous, supervisor_pid=os.getpid(), max_parallel=MAX_PARALLEL,
                 active_runs=[], handoff_at=now().isoformat(),
                 parallel_revision_sha256=revision_hash, parallel_controller_sha256=digest(__file__))
    state.pop('active_run', None)
    lock = (HERE / 'supervisor.lock').open('a')
    stop_requested = False

    def request_stop(*_):
        nonlocal stop_requested
        stop_requested = True

    def save():
        state['active_runs'] = [{k: v for k, v in entry.items() if not k.startswith('_')} for entry in active]
        state['updated_at'] = now().isoformat()
        try:
            state['extra_requests_used'] = int(Path(plan['ledger_path']).read_text() or '0')
            state['total_body_requests'] = enforce_budget(plan, state['completed'], active, state['extra_requests_used'])
        except Exception as exc:
            state['accounting_error'] = str(exc)
        write(STATE, state)

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        save()
        while active or pending_runs(plan['runs'], state['completed'], active):
            require(not stop_requested, '收到本批停止请求')
            require(now() < datetime.fromisoformat(plan['deadline_at']), '达到原绝对截止')
            require(digest(PLAN) == plan_hash and digest(REVISION) == revision_hash, '冻结计划或并行修订改变')
            require(digest(__file__) == revision['controller_sha256'], '并行控制器运行中改变')
            frozen_sources(plan)
            finished = []
            for entry in active:
                directory = Path(entry['run_dir'])
                alive = engine_alive(entry)
                if not alive and entry['_process'] is not None:
                    require(entry['_process'].returncode == 0, '引擎退出码异常')
                entry['progress'] = progress(directory)
                entry['agent_summary'] = agent_summary(directory)[0]
                state['expected_returned_model'] = health(entry['agent_summary'], state['expected_returned_model'])
                logfile = directory / 'engine.log'
                if logfile.exists():
                    with logfile.open(errors='replace') as stream:
                        stream.seek(entry['_offset']); recent = stream.read(); entry['_offset'] = stream.tell()
                    require(not any(text in recent for text in ('Error executing step', 'RayTaskError', 'OutOfMemoryError')), '引擎步骤或资源失败')
                if not alive:
                    run = next(r for r in plan['runs'] if r['run_id'] == entry['run_id'])
                    finished.append((entry, final_result(directory, run, state['expected_returned_model'])))
            enforce_budget(plan, state['completed'], active, int(Path(plan['ledger_path']).read_text() or '0'))
            for entry, result in finished:
                write(HERE / f"completion_{result['algorithm']}.json", result)
                state['completed'].append(result)
                active.remove(entry)
            for run in pending_runs(plan['runs'], state['completed'], active)[:MAX_PARALLEL - len(active)]:
                require(not stop_requested, '停止后禁止新增条件')
                require(now() < datetime.fromisoformat(plan['deadline_at']), '启动新路前已达原截止')
                directory = serial.path_in(Path(plan['workspace']).resolve(), run['run_dir'])
                require(not directory.exists(), '拒绝覆盖或自动重跑既有目录')
                directory.mkdir(parents=True)
                command = [plan['python'], '-m', 'agentsociety2.society.cli', '--config', run['config'],
                           '--steps', run['steps'], '--run-dir', str(directory), '--experiment-id',
                           '4_2_hourly_return_pilot_s0', '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
                with (directory / 'stdout.log').open('xb') as stdout, (directory / 'stderr.log').open('xb') as stderr:
                    child = subprocess.Popen(command, cwd=plan['workspace'],
                        env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                        stdout=stdout, stderr=stderr, start_new_session=True)
                active.append(dict(run_id=run['run_id'], algorithm=run['algorithm'], run_dir=str(directory),
                                   child_pid=child.pid, command=command, adopted=False, _process=child,
                                   _offset=0, agent_summary={}, progress={}))
                require(len(active) <= MAX_PARALLEL, '并行路数超过2')
                save()
            save()
            if active:
                time.sleep(poll_seconds)
        state.update(status='completed', finished_at=now().isoformat())
    except Exception as exc:
        state.update(status='stopping', error=str(exc))
        signal_engines(active, signal.SIGINT)
        save()
        grace = time.monotonic() + 30
        while any(engine_alive(entry) for entry in active) and time.monotonic() < grace:
            time.sleep(.5)
        signal_engines(active, signal.SIGTERM)
        grace = time.monotonic() + 30
        while any(engine_alive(entry) for entry in active) and time.monotonic() < grace:
            time.sleep(.5)
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
        lock.close()
    return state['status'] == 'completed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--handoff', action='store_true')
    modes.add_argument('--status', action='store_true')
    modes.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    if args.check:
        plan, revision, state, _ = preflight()
        print(json.dumps(dict(preflight='passed', preserved_child_pid=state['active_run']['child_pid'],
              max_parallel=MAX_PARALLEL, deadline_at=plan['deadline_at'], llm_calls=0)))
    elif args.status:
        state = read(STATE)
        for entry in state.get('active_runs', []):
            entry['actual_progress'] = progress(Path(entry['run_dir']))
            entry['actual_agent_summary'] = agent_summary(Path(entry['run_dir']))[0]
            entry['engine_alive'] = process_matches(entry['child_pid'], entry['run_dir'])
        print(json.dumps(state, ensure_ascii=False, indent=2))
    elif args.stop:
        state = read(STATE)
        require(state['status'] == 'running' and process_matches(state['supervisor_pid'], str(Path(__file__).resolve())), '本批并行监督器身份不匹配')
        os.kill(state['supervisor_pid'], signal.SIGTERM)
        print('已向本批并行监督器请求停止')
    else:
        raise SystemExit(0 if supervise() else 1)


if __name__ == '__main__':
    main()
