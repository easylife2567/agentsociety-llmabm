"""按既定顺序串行运行九次主实验；调用官方CLI，不修改社会机制。"""
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

EXPERIMENT = Path(__file__).resolve().parent
ROOT = EXPERIMENT.parents[1]
BATCH = EXPERIMENT / 'runs/timestamp_v1'
STATE = BATCH / 'batch_execution.json'


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def progress(directory):
    result = {}
    for name in ('pid.json', 'SOCIETY_STEP.json'):
        path = directory / name
        if path.exists():
            try:
                result[name] = read(path)
            except json.JSONDecodeError:
                pass  # 引擎写文件期间下次读取。
    return result


def completed(directory, run):
    info = progress(directory)
    step = info.get('SOCIETY_STEP.json', {})
    if info.get('pid.json', {}).get('status') != 'completed':
        raise RuntimeError('引擎没有报告完成: ' + run['run_id'])
    if step.get('step_count') != run['expected_batches']:
        raise RuntimeError('实际执行步数不完整: ' + run['run_id'])
    state_path = directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json'
    env = read(state_path)
    arrival = env['_arrival_state']
    actions = arrival['actions']
    if len(actions) != 1100 or len({(a['agent_id'], a['week']) for a in actions}) != 1100:
        raise RuntimeError('实际用户行动不完整或重复: ' + run['run_id'])
    if len(arrival['weeks']) != 11:
        raise RuntimeError('实际统计周不完整: ' + run['run_id'])
    return dict(steps=step['step_count'], actions=len(actions), weeks=len(arrival['weeks']))


def supervise(max_hours):
    manifest = read(EXPERIMENT / 'init/manifest.json')
    # 准备期文件保持原样；本次用户授权单独记录在运行目录。
    frozen = dict(manifest['output_sha256'])
    verification = read(EXPERIMENT / '2026-10-09-06-ordinary-official-verification.json')
    frozen.update({p: h for p, h in verification['frozen_sha256'].items() if p.startswith(('custom/agents/', 'custom/envs/'))})
    for rel, expected in frozen.items():
        if digest(ROOT / rel) != expected:
            raise RuntimeError('正式输入或代码已改变: ' + rel)
    BATCH.mkdir(parents=True, exist_ok=True)
    lock = (BATCH / 'supervisor.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if STATE.exists():
        raise RuntimeError('本批已有运行记录；不重复启动、不覆盖或自动重跑')
    for run in manifest['runs']:
        if (ROOT / run['run_dir'] / 'SOCIETY.json').exists():
            raise RuntimeError('已有仿真文件，禁止覆盖: ' + run['run_id'])
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    env.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    env['AGENTSOCIETY_LLM_RAY_MAX_WORKERS'] = '4'
    env['AGENTSOCIETY_LLM_RAY_CONCURRENCY'] = '16'
    python = env.get('PYTHON_PATH') or sys.executable
    write(BATCH / 'runtime_plan.json', dict(
        authorized=True, authorization='2026-10-14用户：把两份报告落实到主项目，然后开始跑主实验',
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_sha256=frozen, supervisor_sha256=digest(Path(__file__)),
        model=env['AGENTSOCIETY_LLM_MODEL'], service_host=urlsplit(env['AGENTSOCIETY_LLM_API_BASE']).hostname,
        runs=manifest['runs'], decision_opportunities=9900, extra_requests_limit=990,
        serial=True, max_wall_hours=max_hours, scientific_parameters_changed=False,
        restart_policy='出现失败时停止，保留现场，不自动重跑', started_at=now()))
    state = dict(supervisor_pid=os.getpid(), status='running', started_at=now(), completed=[], current_run=None)
    write(STATE, state)
    child = None
    stop_requested = False

    def stop(signum, frame):
        nonlocal stop_requested
        stop_requested = True
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGINT)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    started = time.monotonic()
    try:
        for run in manifest['runs']:
            if stop_requested:
                raise RuntimeError('用户或监督器请求停止')
            if any(digest(ROOT / p) != h for p, h in frozen.items()):
                raise RuntimeError('运行期间正式代码或输入改变')
            directory = ROOT / run['run_dir']
            directory.mkdir(parents=True, exist_ok=True)
            child_env = dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace'))
            command = [python, '-m', 'agentsociety2.society.cli', '--config', str(ROOT / run['config']),
                       '--steps', str(ROOT / run['steps']), '--run-dir', str(directory),
                       '--experiment-id', run['run_id'], '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
            with (directory / 'stdout.log').open('ab') as stdout, (directory / 'stderr.log').open('ab') as stderr:
                child = subprocess.Popen(command, cwd=ROOT, env=child_env, stdout=stdout, stderr=stderr, start_new_session=True)
            state.update(current_run=run['run_id'], child_pid=child.pid, command=command, updated_at=now())
            write(STATE, state)
            log_offset = 0
            while child.poll() is None:
                time.sleep(10)
                if time.monotonic() - started > max_hours * 3600:
                    stop(signal.SIGTERM, None)
                logfile = directory / 'engine.log'
                if logfile.exists():
                    with logfile.open() as f:
                        f.seek(log_offset)
                        recent = f.read()
                        log_offset = f.tell()
                    if 'Error executing step' in recent:
                        stop(signal.SIGTERM, None)
                        state['failure_reason'] = '引擎步骤失败，停止后续实验'
                state.update(progress=progress(directory), updated_at=now(), elapsed_seconds=time.monotonic()-started)
                write(STATE, state)
            if stop_requested or child.returncode != 0:
                raise RuntimeError(state.get('failure_reason') or f'运行停止或失败: {run["run_id"]}, code={child.returncode}')
            result = completed(directory, run)
            state['completed'].append(dict(run_id=run['run_id'], finished_at=now(), **result))
            write(STATE, state)
        state.update(status='completed', finished_at=now())
    except Exception as exc:
        state.update(status='stopped' if stop_requested else 'failed', error=str(exc), finished_at=now())
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        write(STATE, state)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-hours', type=float, default=48)
    ap.add_argument('--status', action='store_true')
    args = ap.parse_args()
    if args.status:
        print(json.dumps(read(STATE) if STATE.exists() else {'status': 'not_started'}, ensure_ascii=False, indent=2))
    else:
        supervise(args.max_hours)
