"""用户明确恢复授权后的单次续跑：干净检查点复制接续，失败条件独立重试。

原始计划、失败目录及账本不重置；总正文预算包含被保留的失败尝试。
"""
import argparse
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
from run_seed_extension_parallel import (
    ROOT, BATCH, STATE, PLAN, LEDGER, MAX_PARALLEL, EXPECTED_MODEL,
    read, write, digest, now, progress, agent_summary, final_result,
    require, process_alive, engine_alive, signal_engines, pending_runs, deadline,
)

RECORD = BATCH / 'recovery_1.json'
SOURCE_STATE = BATCH / 'stopped_execution_1.json'
SELF = Path(__file__).resolve()


def budget_total(done, active, discarded, extra, plan):
    total = sum(r['requests'] for r in done + discarded)
    total += sum(r['agent_summary']['requests'] for r in active)
    require(0 <= extra <= plan['extra_requests_limit'], '共享额外请求越界')
    require(total <= plan['max_agent_body_requests'], '含失败尝试的正文请求总额越界')
    return total


def prepare():
    plan, old = read(PLAN), read(STATE)
    require(old['status'] == 'stopped' and not RECORD.exists(), '只允许本次明确恢复一次')
    require(not process_alive(old['supervisor_pid'], 'run_seed_extension'), '监督器仍存活')
    require(all(not engine_alive(a) for a in old['active_runs']), '原引擎仍存活')
    require(datetime.now(timezone.utc) < deadline(plan), '原48小时截止已到')
    require(read(BATCH / 'recovery_probe_1.json')['status'] == 'passed', '额度测试未通过')
    require(all(digest(ROOT / p) == h for p, h in plan['source_sha256'].items()), '冻结输入或源码变化')
    env = os.environ.copy()
    env.update({k: str(v) for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    endpoint = urlsplit(env['AGENTSOCIETY_LLM_API_BASE'])
    require(env['AGENTSOCIETY_LLM_MODEL'] == plan['model'] and
            (endpoint.hostname, endpoint.path) == (plan['service_host'], plan['api_path']), '模型或接口变化')
    require(bool(env.get('AGENTSOCIETY_LLM_API_KEY')), '缺少凭据')
    env.update(LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    runs = [dict(r) for r in plan['runs']]
    for row in old['completed']:
        run = next(r for r in runs if r['run_id'] == row['run_id'])
        final_result(ROOT / run['run_dir'], run)
    require(len(old['completed']) == 11, '完成基线与本次恢复授权不符')
    sources = {a['run_id']: a for a in old['active_runs']}
    clean = sources['timestamp_v1_interest_s6']
    failed = sources['timestamp_v1_random_s7']
    summary = agent_summary(Path(clean['run_dir']))
    require(summary['action_failures'] == 0 and summary['unique_decisions'] == summary['decisions'] == 921,
            '兴趣seed6检查点有失败、重复或缺失')
    arrival = read(Path(clean['run_dir']) / 'env/CurationDynamicsSpace/state/ENV_STATE.json')['_arrival_state']
    actions = {(str(a['agent_id']), a['week']) for a in arrival['actions']}
    decisions = set()
    for path in (Path(clean['run_dir']) / 'agents').glob('*/AGENT.json'):
        agent = read(path)
        decisions.update((str(agent['id']), r['week']) for r in agent['decision_log'])
    require(actions == decisions and len(actions) == len(arrival['actions']) == 921, '环境与Agent检查点不一致')
    require(read(Path(clean['run_dir']) / 'SOCIETY_STEP.json')['step_count'] == 580, '恢复步数变化')
    failed_summary = agent_summary(Path(failed['run_dir']))
    require(failed_summary['action_failures'] == 1 and failed_summary['requests'] == 54, '失败现场变化')
    for run in runs:
        if run['run_id'] in sources:
            run['source_run_dir'] = sources[run['run_id']]['run_dir']
            run['resume'] = run['run_id'] == clean['run_id']
            run['run_dir'] += '_resume1' if run['resume'] else '_retry1'
        if run['run_id'] not in {r['run_id'] for r in old['completed']}:
            require(not (ROOT / run['run_dir']).exists(), '恢复目标已存在，拒绝覆盖')
    discarded = [dict(run_id=failed['run_id'], run_dir=failed['run_dir'], **failed_summary)]
    return plan, old, runs, discarded, env


def supervise():
    with (BATCH / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan, old, runs, discarded, env = prepare()
        # 保存停止状态原字节；旧目录不写入，接续只发生在完整副本。
        require(not SOURCE_STATE.exists(), '停止快照已存在')
        shutil.copy2(STATE, SOURCE_STATE)
        write(RECORD, dict(authorization='用户2026-10-23：额度已经恢复，尝试继续',
              prepared_at=now(), original_plan_sha256=digest(PLAN), controller_sha256=digest(SELF),
              original_deadline_at=deadline(plan).isoformat(), source_state=str(SOURCE_STATE.relative_to(ROOT)),
              runs=runs, discarded_attempts=discarded, prior_probe_requests=3, recovery_probe_requests=1,
              extra_requests_at_resume=int(LEDGER.read_text()), scientific_config_changed=False,
              rule='保留11次完成；兴趣seed6复制检查点接续；随机seed7原失败保留，独立重试；后续再失败即联停，不自动再试'))
        active = []
        state = dict(old, status='running', supervisor_pid=os.getpid(), active_runs=active,
                     recovery_record=str(RECORD.relative_to(ROOT)), recovery_started_at=now(),
                     discarded_attempts=discarded, controller=str(SELF.relative_to(ROOT)))
        for key in ('stop_reason', 'error', 'finished_at', 'children_needing_attention'):
            state.pop(key, None)
        stop_at = None

        def save():
            state['active_runs'] = [{k: v for k, v in a.items() if not k.startswith('_')} for a in active]
            state.update(updated_at=now(), extra_requests_used=int(LEDGER.read_text()),
                total_body_requests=budget_total(state['completed'], active, discarded, int(LEDGER.read_text()), plan),
                elapsed_seconds=(datetime.now(timezone.utc) - datetime.fromisoformat(plan['started_at'])).total_seconds(),
                budget_remaining_seconds=max(0, (deadline(plan) - datetime.now(timezone.utc)).total_seconds()))
            write(STATE, state)

        def stop(reason):
            nonlocal stop_at
            if stop_at is None:
                stop_at = time.monotonic()
                state.update(status='stopping', stop_reason=reason)
                signal_engines(active, signal.SIGINT)
                save()

        signal.signal(signal.SIGTERM, lambda *_: stop('收到停止请求'))
        signal.signal(signal.SIGINT, lambda *_: stop('收到停止请求'))
        try:
            while active or pending_runs(runs, state['completed'], active):
                require(stop_at is None, state.get('stop_reason', '停止请求'))
                require(datetime.now(timezone.utc) < deadline(plan), '达到原48小时绝对截止')
                finished = []
                for item in active:
                    d = Path(item['run_dir'])
                    alive = engine_alive(item)
                    item['progress'], item['agent_summary'] = progress(d), agent_summary(d)
                    require(not item['agent_summary']['action_failures'], '行动/发布失败: ' + item['run_id'])
                    require(not (set(item['agent_summary']['response_models']) - {EXPECTED_MODEL}), '模型版本变化')
                    log = Path(item['log_file'])
                    if log.exists():
                        with log.open(errors='replace') as f:
                            f.seek(item['_offset']); recent = f.read(); item['_offset'] = f.tell()
                        require(not any(s in recent for s in ('Error executing step', 'RayTaskError', 'OutOfMemoryError')),
                                '引擎日志失败: ' + item['run_id'])
                    if not alive:
                        require(item['_process'].returncode == 0, '引擎退出码异常: ' + item['run_id'])
                        run = next(r for r in runs if r['run_id'] == item['run_id'])
                        result = final_result(d, run)
                        result['run_dir'] = str(d)
                        finished.append((item, result))
                save()
                for item, result in finished:
                    state['completed'].append(result); active.remove(item)
                for run in pending_runs(runs, state['completed'], active)[:MAX_PARALLEL - len(active)]:
                    require(stop_at is None, '停止后禁止启动后续')
                    require(all(digest(ROOT / p) == h for p, h in plan['source_sha256'].items()), '冻结输入变化')
                    directory = ROOT / run['run_dir']
                    require(not directory.exists(), '目标已存在，禁止自动重试')
                    if run.get('resume'):
                        shutil.copytree(run['source_run_dir'], directory)
                    else:
                        directory.mkdir()
                    log = directory / 'recovery-engine.log'
                    command = [env['PYTHON_PATH'], '-m', 'agentsociety2.society.cli', '--config', str(ROOT / run['config']),
                               '--steps', str(ROOT / run['steps']), '--run-dir', str(directory),
                               '--experiment-id', run['run_id'], '--log-file', str(log), '--batch-size', '100']
                    if run.get('resume'):
                        command.append('--resume')
                    with (directory / 'recovery-stdout.log').open('ab') as out, (directory / 'recovery-stderr.log').open('ab') as err:
                        proc = subprocess.Popen(command, cwd=ROOT, env=dict(env, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                                                stdout=out, stderr=err, start_new_session=True)
                    active.append(dict(run_id=run['run_id'], run_dir=str(directory), child_pid=proc.pid,
                                       command=command, log_file=str(log), resume=run.get('resume', False),
                                       _process=proc, _offset=0, progress=progress(directory), agent_summary=agent_summary(directory)))
                    save()
                save(); time.sleep(10)
            state.update(status='completed', finished_at=now())
        except Exception as exc:
            stop(str(exc))
            while any(engine_alive(a) for a in active) and time.monotonic() - stop_at < 180:
                time.sleep(2)
            signal_engines(active, signal.SIGTERM)
            until = time.monotonic() + 60
            while any(engine_alive(a) for a in active) and time.monotonic() < until:
                time.sleep(2)
            remaining = [a['child_pid'] for a in active if engine_alive(a)]
            state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                         children_needing_attention=remaining, finished_at=now() if not remaining else None)
            print(str(exc), file=sys.stderr, flush=True)
        finally:
            for a in active:
                a['progress'], a['agent_summary'] = progress(Path(a['run_dir'])), agent_summary(Path(a['run_dir']))
            save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--continue-authorized', action='store_true')
    args = parser.parse_args()
    if args.check:
        plan, old, runs, discarded, _ = prepare()
        assert len(pending_runs(runs, old['completed'], [])) == 10
        assert budget_total(old['completed'], [dict(agent_summary=dict(requests=175))], discarded, 5, plan) == 2417
        try:
            budget_total([dict(requests=25400)], [], discarded, 5, plan)
        except RuntimeError:
            pass
        else:
            raise AssertionError('失败尝试未纳入总预算')
        print(json.dumps(dict(status='passed', completed=11, remaining=10, max_parallel=2,
              deadline_at=deadline(plan).isoformat(), failed_attempt_requests_retained=54,
              checkpoint_actions=921, simulation_calls=0, llm_calls=0), ensure_ascii=False))
    elif args.continue_authorized:
        supervise()
    else:
        parser.error('必须显式--check或--continue-authorized，不自动恢复')
