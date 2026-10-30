"""接管本pilot的随机/兴趣；时序由用户撤回，消耗仍计账，不重跑或重置截止。"""
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
import run_parallel as parallel

read, write, digest, now, require = serial.read, serial.write, serial.digest, serial.now, serial.require
agent_summary, health, final_result = serial.agent_summary, serial.health, serial.final_result
progress, frozen_sources, process_matches = serial.progress, serial.frozen_sources, serial.process_matches
HERE = Path(__file__).resolve().parent
PLAN, STATE = HERE / 'runtime_plan.json', HERE / 'batch_execution.json'
REVISION, HISTORY = HERE / 'selected_revision.json', HERE / 'scope_handoff'
PREVIOUS_CONTROLLER = HERE / 'run_parallel.py'
SELECTED = ('random', 'interest')
EXCLUDED = ('chronological',)
MAX_PARALLEL = 2


def selected_runs(plan):
    return [run for run in plan['runs'] if run['algorithm'] in SELECTED]


def pending_runs(runs, done, active):
    used = {item['run_id'] for item in done + active}
    return [run for run in runs if run['algorithm'] in SELECTED and run['run_id'] not in used]


def enforce_budget(plan, done, active, extra, withdrawn_requests=0):
    total = (withdrawn_requests + sum(item['requests'] for item in done)
             + sum(item.get('agent_summary', {}).get('requests', 0) for item in active))
    require(0 <= extra <= plan['extra_requests_limit'] and total <= plan['body_outer_requests_limit'],
            '本批累计请求预算越界（含用户撤回时序消耗）')
    return total


def withdrawal_record(revision, plan):
    path = Path(revision['withdrawal_record'])
    if not path.is_absolute():
        path = HERE / path
    require(digest(path) == revision['withdrawal_sha256'], '撤回现场哈希不匹配')
    record = read(path)
    run = next(run for run in plan['runs'] if run['algorithm'] == 'chronological')
    require(record['algorithm'] == 'chronological' and record['run_id'] == run['run_id']
            and Path(record['run_dir']).resolve() == Path(run['run_dir']).resolve(), '撤回记录不属于本批时序')
    require(record['status'] == 'withdrawn_by_user' and isinstance(record['consumed_requests'], int)
            and record['consumed_requests'] >= 0, '撤回记录状态或消耗不完整')
    require(not process_matches(record['child_pid'], record['run_dir']), '时序引擎仍活跃，先完成定向停止')
    return record


def selected_previous(previous):
    done = [row for row in previous['completed'] if row['algorithm'] in SELECTED]
    active = [dict(row) for row in previous.get('active_runs', []) if row['algorithm'] in SELECTED]
    return done, active


def preflight():
    plan, revision, state = read(PLAN), read(REVISION), read(STATE)
    require(plan['execution_authorized'] and revision['execution_authorized'], '缺少原运行或范围缩减授权')
    require(tuple(revision['selected_algorithms']) == SELECTED and tuple(revision['excluded_algorithms']) == EXCLUDED,
            '只允许随机与兴趣，时序必须排除')
    require(revision['max_parallel'] == MAX_PARALLEL and revision['selected_decision_opportunities'] == 2200,
            '当前条件规模或并行上限不符')
    require(revision['runtime_plan_sha256'] == digest(PLAN), '原运行计划改变')
    require(revision['parallel_revision_sha256'] == digest(HERE / 'parallel_revision.json'), '原并行修订改变')
    require(read(HERE / 'parallel_revision.json')['controller_sha256'] == digest(PREVIOUS_CONTROLLER), '原并行辅助源码改变')
    require(revision['controller_sha256'] == digest(__file__), '当前控制器哈希不匹配')
    for key, expected in (('decision_opportunities', 3300), ('extra_requests_limit', 330), ('body_outer_requests_limit', 3630)):
        require(plan[key] == revision[key] == expected, '原累计预算变化')
    require(revision['deadline_at'] == plan['deadline_at'] and now() < datetime.fromisoformat(plan['deadline_at']),
            '原绝对截止已到或改变')
    require(state['status'] == 'running' and 'active_runs' in state and not (HISTORY / 'parallel-state.json').exists(),
            '仅允许一次从原并行监督器接管')
    require(state['runtime_plan_sha256'] == digest(PLAN), '在跑批次计划不同')
    require(state['expected_returned_model'] == revision['expected_returned_model'], '实际模型锁不同')
    require(process_matches(state['supervisor_pid'], str(PREVIOUS_CONTROLLER)), '原并行监督器身份不符')
    frozen_sources(plan)
    record = withdrawal_record(revision, plan)
    done, active = selected_previous(state)
    ids = [row['run_id'] for row in done + active]
    require(len(ids) == len(set(ids)), '当前条件重复登记')
    allowed = {run['run_id']: run for run in selected_runs(plan)}
    for row in done + active:
        require(row['run_id'] in allowed and Path(row['run_dir']).resolve() == Path(allowed[row['run_id']]['run_dir']).resolve(),
                '继承条件或路径不符')
    for row in done:
        final_result(Path(row['run_dir']), allowed[row['run_id']], revision['expected_returned_model'])
    for row in active:
        directory = Path(row['run_dir'])
        row['agent_summary'] = agent_summary(directory)[0]
        health(row['agent_summary'], revision['expected_returned_model'])
        if not process_matches(row['child_pid'], row['run_dir']):
            final_result(directory, allowed[row['run_id']], revision['expected_returned_model'])
    for row in pending_runs(plan['runs'], done, active):
        require(not Path(row['run_dir']).exists(), '未登记条件已有目录，拒绝重跑')
    enforce_budget(plan, done, active, int(Path(plan['ledger_path']).read_text() or '0'), record['consumed_requests'])
    return plan, revision, state, parallel.environment(plan), record


def release_parallel(plan, revision, previous):
    """退出原并行父监督器；selected引擎保持，已结束selected可由主循环吸收。"""
    old_pid = previous['supervisor_pid']
    require(process_matches(old_pid, str(PREVIOUS_CONTROLLER)), '原父PID身份改变')
    os.kill(old_pid, signal.SIGSTOP)
    released = False
    try:
        previous = read(STATE)
        require(previous['supervisor_pid'] == old_pid and previous['status'] == 'running'
                and 'active_runs' in previous, '冻结旧父时状态改变')
        record = withdrawal_record(revision, plan)
        done, active = selected_previous(previous)
        for item in active:
            directory = Path(item['run_dir'])
            health(agent_summary(directory)[0], previous['expected_returned_model'])
            if not process_matches(item['child_pid'], item['run_dir']):
                run = next(run for run in plan['runs'] if run['run_id'] == item['run_id'])
                final_result(directory, run, previous['expected_returned_model'])
        frozen_sources(plan)
        HISTORY.mkdir(exist_ok=True)
        require(not (HISTORY / 'parallel-state.json').exists(), '已有范围交接历史，拒绝重复')
        write(HISTORY / 'parallel-state.json', previous)
        write(HISTORY / 'scope-handoff-before.json', dict(captured_at=now().isoformat(),
              old_supervisor_pid=old_pid, selected_engine_pids=[row['child_pid'] for row in active],
              selected_run_ids=[row['run_id'] for row in done + active],
              withdrawn=record, extra_requests_used=int(Path(plan['ledger_path']).read_text() or '0'),
              original_started_at=previous['started_at'], original_deadline_at=plan['deadline_at']))
        os.kill(old_pid, signal.SIGHUP)
        os.kill(old_pid, signal.SIGCONT)
        for _ in range(100):
            if not process_matches(old_pid, str(PREVIOUS_CONTROLLER)):
                released = True
                break
            time.sleep(.1)
        require(released, '旧监督器未退出，不能接管')
        return previous
    finally:
        # 时序已由用户撤回，旧监督器不能恢复轮询，否则会误触发两路联停。
        # 失败时保留其暂停状态，由操作者核对；绝不自动重启时序或误停selected。
        if not released:
            print('范围交接未完成：原父保持暂停，请核对本批现场', file=sys.stderr)


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
    plan, revision, previous, env, withdrawn = preflight()
    plan_hash, revision_hash = digest(PLAN), digest(REVISION)
    previous = release_parallel(plan, revision, previous)
    done, inherited = selected_previous(previous)
    active = [dict(item, adopted=True, _process=None, _offset=0) for item in inherited]
    state = dict(previous, supervisor_pid=os.getpid(), max_parallel=MAX_PARALLEL,
                 completed=done, active_runs=[], scope_handoff_at=now().isoformat(),
                 selected_algorithms=list(SELECTED), excluded_runs=[withdrawn],
                 withdrawn_body_requests=withdrawn['consumed_requests'],
                 selected_revision_sha256=revision_hash, selected_controller_sha256=digest(__file__))
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
            state['total_body_requests'] = enforce_budget(plan, state['completed'], active, state['extra_requests_used'], withdrawn['consumed_requests'])
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
            require(digest(PLAN) == plan_hash and digest(REVISION) == revision_hash, '冻结计划或范围修订改变')
            require(digest(__file__) == revision['controller_sha256'], '范围控制器运行中改变')
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
            enforce_budget(plan, state['completed'], active, int(Path(plan['ledger_path']).read_text() or '0'), withdrawn['consumed_requests'])
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
        require({row['algorithm'] for row in state['completed']} == set(SELECTED), '当前两条件完成记录不全')
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
        plan, revision, state, _, withdrawn = preflight()
        print(json.dumps(dict(preflight='passed', selected=list(SELECTED), excluded=list(EXCLUDED),
              inherited_pids=[row['child_pid'] for row in selected_previous(state)[1]],
              withdrawn_body_requests=withdrawn['consumed_requests'], max_parallel=MAX_PARALLEL,
              deadline_at=plan['deadline_at'], llm_calls=0)))
    elif args.status:
        state = read(STATE)
        for entry in state.get('active_runs', []):
            entry['actual_progress'] = progress(Path(entry['run_dir']))
            entry['actual_agent_summary'] = agent_summary(Path(entry['run_dir']))[0]
            entry['engine_alive'] = process_matches(entry['child_pid'], entry['run_dir'])
        print(json.dumps(state, ensure_ascii=False, indent=2))
    elif args.stop:
        state = read(STATE)
        require(state['status'] == 'running' and process_matches(state['supervisor_pid'], str(Path(__file__).resolve())), '本批当前监督器身份不匹配')
        os.kill(state['supervisor_pid'], signal.SIGTERM)
        print('已向本批随机/兴趣监督器请求停止')
    else:
        raise SystemExit(0 if supervise() else 1)


if __name__ == '__main__':
    main()
