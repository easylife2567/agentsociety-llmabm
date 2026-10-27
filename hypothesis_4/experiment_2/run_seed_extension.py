"""串行执行已授权的seed 3–9三臂补充批；失败停止，不自动重跑。

只组织官方CLI，复用旧主批的进度读取、原子记录和完成核验；不修改科学机制。
--check只做本地冻结/路径/预算检查，--status只读本批，不使用旧固定run入口。
"""
import argparse
import fcntl
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit

from dotenv import dotenv_values
from run_asset_paths import resolve_asset_path
from run_main_experiment import read, write, digest, now, progress, completed

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BATCH = HERE / 'runs/timestamp_v1/execution_records/seed3_9'
STATE = BATCH / 'batch_execution.json'
MANIFEST = HERE / 'init/manifest_seed3_9.json'
EXPECTED_MODEL = 'deepseek-v4-1-flash-261017'


def preflight():
    """核对实际已验收字节；不调用模型，不覆盖已有运行记录或账本。"""
    manifest = read(MANIFEST)
    evidence = read(HERE / 'seed_extension_verification.json')
    probe = read(HERE / 'model_compatibility_probe.json')
    assert evidence['status'] == probe['status'] == 'passed'
    assert probe['returned_model_identifiers'] == [EXPECTED_MODEL]
    assert len(manifest['runs']) == 21
    assert [(r['seed'], r['algorithm']) for r in manifest['runs']] == [
        (s, a) for s in range(3, 10) for a in ('random', 'chronological', 'interest')]
    assert manifest['budget']['decision_opportunities'] == 23100
    assert manifest['budget']['extra_requests_limit'] == 2310
    frozen = dict(manifest['source_sha256'])
    frozen.update(manifest['output_sha256'])
    frozen.update(read(HERE / 'runs/timestamp_v1/runtime_plan.json')['source_sha256'])
    frozen.update(evidence['runtime_conditions']['current_runtime_sha256'])
    for path in (MANIFEST, HERE / 'seed_extension_verification.json', HERE / 'model_compatibility_probe.json',
                 HERE / 'run_main_experiment.py', Path(__file__)):
        frozen[str(path.relative_to(ROOT))] = digest(path)
    for path, expected in frozen.items():
        if digest(ROOT / path) != expected:
            raise RuntimeError('冻结输入或代码不一致: ' + path)
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    endpoint = urlsplit(env['AGENTSOCIETY_LLM_API_BASE'])
    assert env['AGENTSOCIETY_LLM_MODEL'] == probe['requested_model_alias']
    assert (endpoint.hostname, endpoint.path) == (probe['service_host'], probe['api_path'])
    assert env.get('AGENTSOCIETY_LLM_API_KEY')
    env.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16')
    if STATE.exists() or (BATCH / 'runtime_plan.json').exists():
        raise RuntimeError('本批已有运行记录；禁止覆盖或自动重启')
    ledger = ROOT / manifest['budget']['content_retry_budget']['ledger_path']
    if ledger.exists() or any((ROOT / r['run_dir']).exists() for r in manifest['runs']):
        raise RuntimeError('新批输出或账本已存在；不清理、不覆盖')
    return manifest, frozen, env, endpoint, ledger


def agent_summary(directory):
    """只读取引擎已保存的真实决策，写文件瞬间的不完整JSON留待下次读取。"""
    directory = resolve_asset_path(directory)
    summary = dict(agent_files=0, decisions=0, unique_decisions=0, posted=0, requests=0,
                   action_failures=0, response_models={})
    unique = set()
    for path in sorted((directory / 'agents').glob('*/AGENT.json')):
        try:
            agent = read(path)
        except (OSError, ValueError):
            continue
        summary['agent_files'] += 1
        for row in agent.get('decision_log', []):
            summary['decisions'] += 1
            unique.add((agent['id'], row['week']))
            summary['posted'] += bool(row.get('posted'))
            summary['requests'] += row.get('generation_attempts', 0)
            summary['action_failures'] += row.get('reason') in ('action_failed', 'publication_failed')
            if row.get('response_model'):
                model = row['response_model']
                summary['response_models'][model] = summary['response_models'].get(model, 0) + 1
    summary['unique_decisions'] = len(unique)
    return summary


def supervise(max_hours):
    manifest, frozen, env, endpoint, ledger = preflight()
    BATCH.mkdir(parents=True, exist_ok=True)
    with (BATCH / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 取得本批锁后再复核，两个启动进程不能同时创建同一账本。
        if STATE.exists() or ledger.exists():
            raise RuntimeError('本批已有执行状态或额度记录')
        with ledger.open('x') as file:
            file.write('0')
        plan = dict(authorized=True,
            authorization='2026-10-22用户明确启动当前模型seed3–9三臂主实验，消融不补，每30分钟汇报，完成或停止暂停定时器',
            batch_id=manifest['batch_id'], hypothesis_id=4, experiment_id=2,
            commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            source_sha256=frozen, model=env['AGENTSOCIETY_LLM_MODEL'], expected_response_model=EXPECTED_MODEL,
            service_host=endpoint.hostname, api_path=endpoint.path, runs=manifest['runs'],
            decision_opportunities=23100, extra_requests_limit=2310, max_agent_body_requests=25410,
            prior_probe_requests=3, prior_probe_tokens=3697, serial=True, batch_size=100,
            max_wall_hours=max_hours, model_workers=4, model_concurrency=16,
            restart_policy='失败停批、保留证据，不自动重跑或恢复checkpoint',
            manifest_execution_authorized_note='准备期manifest保持false；本runtime_plan为本次实际启动授权',
            started_at=now())
        write(BATCH / 'runtime_plan.json', plan)
        state = dict(supervisor_pid=os.getpid(), status='running', started_at=now(),
                     completed=[], total_runs=21, current_run=None, extra_requests_used=0)
        write(STATE, state)
        child = None
        stopped_at = None
        started = time.monotonic()

        def stop(reason):
            nonlocal stopped_at
            if stopped_at is None:
                stopped_at = time.monotonic()
                state['stop_reason'] = reason
                if child is not None and child.poll() is None:
                    os.killpg(child.pid, signal.SIGINT)

        signal.signal(signal.SIGTERM, lambda *_: stop('收到停止请求'))
        signal.signal(signal.SIGINT, lambda *_: stop('收到停止请求'))
        try:
            for run in manifest['runs']:
                if stopped_at is not None:
                    raise RuntimeError(state['stop_reason'])
                if any(digest(ROOT / p) != h for p, h in frozen.items()):
                    raise RuntimeError('运行期间冻结输入或代码变化，停止后续')
                directory = ROOT / run['run_dir']
                directory.mkdir()
                command = [env.get('PYTHON_PATH') or sys.executable, '-m', 'agentsociety2.society.cli',
                    '--config', str(ROOT / run['config']), '--steps', str(ROOT / run['steps']),
                    '--run-dir', str(directory), '--experiment-id', run['run_id'],
                    '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
                with (directory / 'stdout.log').open('ab') as stdout, (directory / 'stderr.log').open('ab') as stderr:
                    child = subprocess.Popen(command, cwd=ROOT,
                        env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                        stdout=stdout, stderr=stderr, start_new_session=True)
                state.update(current_run=run['run_id'], child_pid=child.pid, command=command,
                             current_agent_summary={}, updated_at=now())
                write(STATE, state)
                offset = 0
                while child.poll() is None:
                    time.sleep(10)
                    if time.monotonic() - started >= max_hours * 3600:
                        stop('达到本批48小时保护上限')
                    log = directory / 'engine.log'
                    if log.exists():
                        with log.open() as file:
                            file.seek(offset)
                            recent = file.read()
                            offset = file.tell()
                        if 'Error executing step' in recent:
                            stop('引擎步骤失败')
                    summary = agent_summary(directory)
                    if set(summary['response_models']) - {EXPECTED_MODEL}:
                        stop('实际返回模型标识改变，停止以免混入未授权版本')
                    if summary['action_failures']:
                        stop('真实Agent记录出现行动/发布失败')
                    used = int(ledger.read_text() or '0')
                    if used > 2310:
                        stop('额外请求账本超过冻结上限')
                    if stopped_at is not None and time.monotonic() - stopped_at > 120 and child.poll() is None:
                        os.killpg(child.pid, signal.SIGTERM)
                    state.update(progress=progress(directory), current_agent_summary=summary,
                        extra_requests_used=used, updated_at=now(), elapsed_seconds=time.monotonic() - started)
                    write(STATE, state)
                if stopped_at is not None or child.returncode != 0:
                    raise RuntimeError(state.get('stop_reason') or f'引擎退出码{child.returncode}')
                result = completed(directory, run)
                summary = agent_summary(directory)
                if summary['agent_files'] != 100 or summary['decisions'] != 1100 or summary['unique_decisions'] != 1100:
                    raise RuntimeError('已保存Agent决策不完整或重复')
                if summary['action_failures'] or set(summary['response_models']) - {EXPECTED_MODEL}:
                    raise RuntimeError('最终Agent记录存在失败或模型变化')
                state['completed'].append(dict(run_id=run['run_id'], finished_at=now(), **result, **summary))
                write(STATE, state)
            state.update(status='completed', finished_at=now())
        except Exception as exc:
            if child is not None and child.poll() is None:
                stop('监督器异常，停止当前引擎')
                try:
                    child.wait(timeout=90)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait()
            state.update(status='stopped' if stopped_at is not None else 'failed',
                         error=str(exc), finished_at=now())
            print(str(exc), file=sys.stderr, flush=True)
        finally:
            state['elapsed_seconds'] = time.monotonic() - started
            state['extra_requests_used'] = int(ledger.read_text() or '0')
            write(STATE, state)


def self_check():
    """用假子进程验证失败不续跑、成功按序推进；不调用CLI或模型。"""
    import tempfile
    from unittest.mock import Mock, patch
    checks = []
    module = sys.modules[__name__]
    for exit_code in (1, 0):
        with tempfile.TemporaryDirectory(dir=HERE / 'tmp') as folder:
            root = Path(folder)
            batch = root / 'batch'
            ledger = batch / 'retry.count'
            runs = [dict(run_id=f'test_{i}', config='config.json', steps='steps.yaml',
                         run_dir=f'batch/test_{i}') for i in range(2)]
            fake = Mock(returncode=exit_code, pid=999999)
            fake.poll.return_value = exit_code
            summary = dict(agent_files=100, decisions=1100, unique_decisions=1100, posted=1,
                           requests=1, action_failures=0, response_models={EXPECTED_MODEL: 1})
            env = dict(AGENTSOCIETY_LLM_MODEL='offline-test')
            with patch.object(module, 'ROOT', root), patch.object(module, 'BATCH', batch), \
                 patch.object(module, 'STATE', batch / 'batch_execution.json'), \
                 patch.object(module, 'preflight', return_value=(dict(batch_id='offline', runs=runs), {}, env,
                     urlsplit('https://offline.invalid/v3'), ledger)), \
                 patch.object(subprocess, 'check_output', return_value='offline-baseline'), \
                 patch.object(subprocess, 'Popen', return_value=fake) as launch, \
                 patch.object(signal, 'signal'), \
                 patch.object(module, 'completed', return_value=dict(steps=693, actions=1100, weeks=11)), \
                 patch.object(module, 'agent_summary', return_value=summary):
                supervise(48)
            state = read(batch / 'batch_execution.json')
            assert launch.call_count == (1 if exit_code else 2)
            assert len(state['completed']) == (0 if exit_code else 2)
            assert state['status'] == ('failed' if exit_code else 'completed')
            checks.append(dict(case='failure_stops_remaining' if exit_code else 'success_advances_in_order',
                               passed=True, subprocesses_launched=launch.call_count))
    write(HERE / 'seed_extension_launcher_check.json',
          dict(status='passed', checks=checks, real_cli_calls=0, llm_calls=0,
               controller_sha256=digest(Path(__file__))))
    print('PASS: failure stops remaining runs; success advances in order; real CLI/LLM calls=0')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--max-hours', type=float, default=48)
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.status:
        import json
        print(json.dumps(read(STATE) if STATE.exists() else {'status': 'not_started'}, ensure_ascii=False, indent=2))
    elif args.check:
        manifest, frozen, env, _, _ = preflight()
        print(f'PASS: {len(manifest["runs"])} runs; {len(frozen)} frozen files; model={env["AGENTSOCIETY_LLM_MODEL"]}; no LLM calls')
    else:
        if args.max_hours != 48:
            raise SystemExit('本次启动固定48小时保护上限')
        supervise(args.max_hours)
