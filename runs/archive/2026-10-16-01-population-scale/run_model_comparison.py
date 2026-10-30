"""串行执行本轮三个官方CLI；失败停批、不覆盖、不自动重跑；状态保存在run内。"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from dotenv import dotenv_values

RUN = Path(__file__).resolve().parent
WORKSPACE = RUN / 'workspace'
INIT = WORKSPACE / 'hypothesis_4/experiment_4/init'
STATE = RUN / 'model-comparison-execution.json'


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def progress(directory):
    info = {}
    for name in ('pid.json', 'SOCIETY_STEP.json'):
        path = directory / name
        if path.exists():
            try:
                info[name] = read(path)
            except json.JSONDecodeError:
                pass
    return info


def ledger_rows(directory):
    return [row for path in (directory / 'agents').glob('*/AGENT.json')
            for row in read(path).get('decision_log', [])]


def finish(directory, spec):
    info = progress(directory)
    assert info['pid.json']['status'] == 'completed', '引擎未完成'
    assert info['SOCIETY_STEP.json']['completed_step_count'] == spec['expected_batches'], '步数不完整'
    arrival = read(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')['_arrival_state']
    assert len(arrival['actions']) == len({(r['agent_id'], r['week']) for r in arrival['actions']}) == 1100
    assert len(arrival['weeks']) == 11
    rows = ledger_rows(directory)
    assert len(rows) == 1100, '实际Agent决策不完整'
    assert all(r['reason'] not in ('action_failed', 'publication_failed') for r in rows), '存在失败行动'
    summary = {'run_id': spec['run_id'], 'finished_at': now(), 'steps': 693, 'actions': 1100,
               'weeks': 11, 'posts': sum(bool(r.get('posted')) for r in rows),
               'requests': sum(r.get('generation_attempts', 0) for r in rows),
               'response_models': dict(Counter(r.get('response_model') for r in rows if r.get('response_model'))),
               'content_origins': dict(Counter(r.get('content_origin') for r in rows if r.get('posted'))),
               'service_failures': sum(r.get('generation_status') == 'service_failed' for r in rows)}
    write(directory / 'completion-summary.json', summary)
    assert summary['service_failures'] == 0, '存在未恢复服务失败，停止后续臂'
    return summary


def supervise():
    manifest = read(INIT / 'manifest.json')
    assert read(RUN / 'service-check.json')['success']
    assert read(RUN / 'model-comparison-verification.json')['success']
    lock = (RUN / 'model-comparison.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if STATE.exists():
        raise RuntimeError('本轮已有执行记录，不覆盖、不自动重跑')
    frozen = {WORKSPACE / p: h for p, h in manifest['source_sha256'].items()}
    frozen.update({INIT / p: h for p, h in manifest['payload_sha256'].items()})
    for spec in manifest['runs']:
        if (WORKSPACE / spec['run_dir'] / 'SOCIETY.json').exists():
            raise RuntimeError('已有仿真结果，禁止覆盖')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('AGENTSOCIETY_LLM_', 'AGENTSOCIETY_CODER_', 'AGENTSOCIETY_EMBEDDING_'))}
    env.update({k: v for k, v in dotenv_values(RUN / '.env').items() if v is not None})
    env.update(AGENTSOCIETY_CODER_LLM_API_KEY=env['AGENTSOCIETY_LLM_API_KEY'],
               AGENTSOCIETY_CODER_LLM_API_BASE=env['AGENTSOCIETY_LLM_API_BASE'],
               AGENTSOCIETY_CODER_LLM_MODEL=env['AGENTSOCIETY_LLM_MODEL'],
               AGENTSOCIETY_WORKSPACE=str(WORKSPACE), PYTHONDONTWRITEBYTECODE='1')
    state = {'status': 'running', 'supervisor_pid': os.getpid(), 'started_at': now(),
             'model': manifest['model'], 'max_wall_hours': manifest['max_wall_hours'],
             'formal_requests_upper_bound': manifest['formal_requests_upper_bound'],
             'completed': [], 'current_run': None, 'scientific_parameters_changed': False}
    write(STATE, state)
    child, stopping = None, False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGINT)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    started = time.monotonic()
    try:
        for spec in manifest['runs']:
            if stopping:
                raise RuntimeError('已请求停止')
            assert all(digest(p) == h for p, h in frozen.items()), '冻结源码/输入发生变化'
            directory = WORKSPACE / spec['run_dir']
            directory.mkdir(parents=True, exist_ok=True)
            command = [env['PYTHON_PATH'], '-m', 'agentsociety2.society.cli',
                       '--config', str(WORKSPACE / spec['config']), '--steps', str(WORKSPACE / spec['steps']),
                       '--run-dir', str(directory), '--experiment-id', spec['run_id'],
                       '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
            with (directory / 'stdout.log').open('ab') as out, (directory / 'stderr.log').open('ab') as err:
                child = subprocess.Popen(command, cwd=WORKSPACE,
                                         env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                                         stdout=out, stderr=err, start_new_session=True)
            state.update(current_run=spec['run_id'], child_pid=child.pid, run_dir=str(directory), command=command)
            write(STATE, state)
            while child.poll() is None:
                time.sleep(10)
                if time.monotonic() - started > manifest['max_wall_hours'] * 3600:
                    state['stop_reason'] = '达到总运行时限'
                    stop(signal.SIGTERM, None)
                log = directory / 'engine.log'
                if log.exists() and 'Error executing step' in log.read_text():
                    state['stop_reason'] = '引擎步骤失败'
                    stop(signal.SIGTERM, None)
                state.update(progress=progress(directory), updated_at=now(), elapsed_seconds=time.monotonic()-started)
                write(STATE, state)
            if stopping or child.returncode != 0:
                raise RuntimeError(state.get('stop_reason') or f'引擎退出，code={child.returncode}')
            state['completed'].append(finish(directory, spec))
            write(STATE, state)
        state.update(status='completed', finished_at=now())
    except Exception as exc:
        state.update(status='stopped' if stopping else 'failed', error=str(exc), finished_at=now())
    finally:
        write(STATE, state)
    return 0 if state['status'] == 'completed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    if args.status:
        print(json.dumps(read(STATE) if STATE.exists() else {'status': 'not_started'}, ensure_ascii=False, indent=2))
    else:
        sys.exit(supervise())
