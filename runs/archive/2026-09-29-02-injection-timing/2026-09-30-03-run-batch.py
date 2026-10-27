"""四格诊断串行监督器：先各跑三周，审计后按同序续跑，累计上限24小时。

使用官方 ExperimentRunner 与配置格式。子进程在批次边界响应停止信号，
只有通过完整前缀审计的checkpoint才可自动恢复，不覆盖旧主实验入口。
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
MANIFEST = ROOT / 'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/manifest.json'
BATCH = ROOT / 'hypothesis_4/experiment_1/runs/arrival_timing_diagnostic'
STATE = BATCH / 'batch_execution.json'
spec = importlib.util.spec_from_file_location('timing_audit', TASK / '2026-09-30-02-audit.py')
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)
read = audit_module.read_json


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs(manifest):
    for rel, sha in manifest['source_sha256'].items():
        if digest(ROOT / rel) != sha:
            raise ValueError('frozen source changed: ' + rel)
    for rel, sha in manifest['artifact_sha256'].items():
        if digest(MANIFEST.parent / rel) != sha:
            raise ValueError('frozen artifact changed: ' + rel)
    for run in manifest['runs']:
        if digest(ROOT / run['config']) != run['config_sha256']:
            raise ValueError('config changed: ' + run['run_id'])


def environment():
    """仅向子进程传凭据，不写入任何产物或命令行。"""
    from dotenv import dotenv_values
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    env['CURATION_RETRY_LEDGER'] = str(BATCH / 'content_retries.txt')
    return env


async def child(run, phase, remaining):
    from agentsociety2.society.cli import ExperimentRunner
    runner = ExperimentRunner(run_dir=ROOT / run['run_dir'])
    loop = asyncio.get_running_loop()
    started = time.monotonic()
    stop_reason = None

    def stop(reason='requested_stop'):
        nonlocal stop_reason
        stop_reason = reason
        # CLI在每个顶层RunStep前检查；所有步骤恰为一个行动批次。
        runner._should_terminate = True

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop)

    async def watch():
        while True:
            await asyncio.sleep(10)
            if time.monotonic() - started >= remaining:
                stop('runtime_budget')
            try:
                info = audit_module.audit(ROOT / run['run_dir'], run)
            except json.JSONDecodeError:
                # AGENT.json由框架逐个写入；轮询避开写入窗口，边界验收仍严格。
                continue
            if info['failures']:
                stop('integrity_failure:' + ','.join(info['failures']))
    monitor = asyncio.create_task(watch())
    try:
        await runner.run(config_path=ROOT / run['config'],
                         steps_path=ROOT / run['steps_prefix' if phase == 'prefix' else 'steps'],
                         experiment_id='h4e1_' + run['run_id'], resume=phase == 'full',
                         batch_size=100)
    finally:
        monitor.cancel()
        write(ROOT / run['run_dir'] / f'{phase}_exit.json', {
            'stop_reason': stop_reason, 'elapsed_seconds': time.monotonic()-started,
            'finished_at': datetime.now(timezone.utc).isoformat()})
    if stop_reason:
        raise RuntimeError(stop_reason)


def status(manifest):
    state = read(STATE)
    return {'execution': state, 'runs': {r['run_id']: audit_module.audit(ROOT / r['run_dir'], r) for r in manifest['runs']}}


def supervise(manifest):
    BATCH.mkdir(parents=True, exist_ok=True)
    # 防止重复点击启动同一批次；异常运行由人工检查，不自动覆盖。
    lock = (BATCH / 'supervisor.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if STATE.exists():
        raise RuntimeError('该批次已有执行记录；请先审查现场，禁止重复启动')
    env = environment()
    code_paths = ['custom/envs/curation_dynamics_space.py', 'custom/envs/curation_arrival_schedule.py',
                  'custom/agents/curation_discourse_agent.py', 'custom/agents/curation_arrival_action.py']
    code_paths += [str(p.relative_to(ROOT)) for p in TASK.glob('2026-09-30-*.py')]
    frozen = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'manifest_sha256': digest(MANIFEST), 'code_sha256': {p: digest(ROOT/p) for p in code_paths},
              'model': env.get('AGENTSOCIETY_LLM_MODEL'), 'api_base': env.get('AGENTSOCIETY_LLM_API_BASE'),
              'coder_model': env.get('AGENTSOCIETY_CODER_LLM_MODEL') or env.get('AGENTSOCIETY_LLM_MODEL'),
              'temperature': 1.0, 'content_timeout_seconds': 60, 'content_cache': False,
              'runtime_budget_seconds': 86400, 'content_retry_limit': 440}
    write(BATCH / 'runtime_freeze.json', frozen)
    state = {'supervisor_pid': os.getpid(), 'status': 'running', 'elapsed_seconds': 0.,
             'started_at': datetime.now(timezone.utc).isoformat(), 'segments': [], 'week_seconds': {}}
    write(STATE, state)
    child_proc = None

    def terminate(signum, frame):
        if child_proc is not None and child_proc.poll() is None:
            child_proc.send_signal(signal.SIGTERM)
        state['stop_requested'] = True
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    try:
        for phase in ('prefix', 'full'):
            if phase == 'full':
                estimate = sum(max(state['week_seconds'][r['run_id']]) * 8 for r in manifest['runs'])
                state['remaining_estimate_seconds'] = estimate
                if state['elapsed_seconds'] + estimate > 86400:
                    state['status'] = 'paused_budget_estimate'
                    write(STATE, state)
                    return
            for run in manifest['runs']:
                verify_inputs(manifest)
                for p, sha in frozen['code_sha256'].items():
                    if digest(ROOT/p) != sha:
                        raise ValueError('运行中代码发生变化: ' + p)
                directory = ROOT / run['run_dir']
                if phase == 'full':
                    report = audit_module.audit(directory, run, run['prefix_batches'])
                    if report['failures']:
                        raise ValueError('前缀恢复账本不一致: ' + str(report['failures']))
                elif (directory / 'SOCIETY.json').exists():
                    raise ValueError('拒绝覆盖已存在run')
                directory.mkdir(parents=True, exist_ok=True)
                child_env = dict(env)
                child_env['AGENTSOCIETY_HOME_DIR'] = str(ROOT / 'agentsociety_data/runs' / run['run_id'])
                remaining = 86400-state['elapsed_seconds']
                if remaining <= 0 or state.get('stop_requested'):
                    raise RuntimeError('预算耗尽或收到停止请求')
                command = [env.get('PYTHON_PATH') or sys.executable, str(Path(__file__).resolve()),
                           '--child', run['run_id'], '--phase', phase, '--remaining', str(remaining)]
                state.update(current_run=run['run_id'], phase=phase)
                start = time.monotonic()
                week_mark = start
                observed_weeks = 0 if phase == 'prefix' else 3
                week_durations = []
                with (directory / 'stdout.log').open('ab') as stdout, (directory / 'stderr.log').open('ab') as stderr:
                    child_proc = subprocess.Popen(command, cwd=ROOT, env=child_env, stdout=stdout, stderr=stderr)
                state['child_pid'] = child_proc.pid
                write(STATE, state)
                while child_proc.poll() is None:
                    time.sleep(10)
                    if time.monotonic()-start >= remaining:
                        child_proc.send_signal(signal.SIGTERM)
                    try:
                        info = audit_module.audit(directory, run)
                    except json.JSONDecodeError:
                        continue
                    if info['weeks'] > observed_weeks:
                        week_durations.append(time.monotonic()-week_mark)
                        week_mark, observed_weeks = time.monotonic(), info['weeks']
                    state['current_progress'] = info
                    state['active_segment_seconds'] = time.monotonic()-start
                    state['updated_at'] = datetime.now(timezone.utc).isoformat()
                    write(STATE, state)
                    if time.monotonic()-start >= remaining or info['failures']:
                        child_proc.send_signal(signal.SIGTERM)
                elapsed = time.monotonic()-start
                state['elapsed_seconds'] += elapsed
                state['active_segment_seconds'] = 0
                target = run['prefix_batches'] if phase == 'prefix' else run['expected_batches']
                report = audit_module.audit(directory, run, target)
                write(directory / f'{phase}_audit.json', report)
                state['segments'].append({'run_id': run['run_id'], 'phase': phase,
                                          'elapsed_seconds': elapsed, 'returncode': child_proc.returncode,
                                          'audit': report})
                if phase == 'prefix':
                    # 末周包含正常关闭与checkpoint开销；首周包含冷启动开销。
                    if len(week_durations) < 3:
                        week_durations.append(time.monotonic()-week_mark)
                    else:
                        week_durations[-1] += time.monotonic()-week_mark
                    state['week_seconds'][run['run_id']] = week_durations
                if child_proc.returncode or report['failures']:
                    raise RuntimeError('运行未通过完整性验收: ' + run['run_id'])
                models = {model for seg in state['segments'] for model in seg['audit']['response_models']}
                if len(models) > 1:
                    raise RuntimeError('模型响应版本跨run变化')
                write(STATE, state)
        state['status'] = 'completed'
    except Exception as exc:
        state.update(status='stopped', error=str(exc))
        if child_proc is not None and child_proc.poll() is None:
            child_proc.send_signal(signal.SIGTERM)
        raise
    finally:
        state['updated_at'] = datetime.now(timezone.utc).isoformat()
        write(STATE, state)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--child')
    parser.add_argument('--phase', choices=['prefix', 'full'])
    parser.add_argument('--remaining', type=float, default=86400)
    args = parser.parse_args()
    manifest = read(MANIFEST)
    if args.status:
        print(json.dumps(status(manifest), ensure_ascii=False, indent=2))
    elif args.child:
        run = next(r for r in manifest['runs'] if r['run_id'] == args.child)
        asyncio.run(child(run, args.phase, args.remaining))
    else:
        verify_inputs(manifest)
        if args.check:
            print('冻结源、配置和steps哈希一致；未启动实验。')
        else:
            supervise(manifest)

if __name__ == '__main__':
    main()
