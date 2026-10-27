"""本次授权恢复：修复副本待提交发布、保留失败用量、完整最终决策失败即联停。"""
import argparse
import asyncio
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

import run_seed_extension_recovery as previous
base = previous.base
SELF = Path(__file__).resolve()
RECORD = base.CONTROL / 'recovery_2.json'
SNAPSHOT = base.CONTROL / 'stopped_execution_2.json'
AUDIT = base.CONTROL / 'recovery_2_offline_check.json'
PROBE = base.CONTROL / 'recovery_probe_2.json'
CHECK = base.CONTROL / 'recovery_2_controller_check.json'
CHECKPOINT = base.CONTROL / 'recovery_2_checkpoint'
FATAL = previous.FATAL
environment = previous.environment


def agent_summary(directory):
    """检查最终决策；保留已成功的有限重试，不把历史generation_error当当前失败。"""
    summary = base.agent_summary(directory)
    summary.update(service_failures=0, posted_model_failures=0)
    for path in (directory / 'agents').glob('*/AGENT.json'):
        try:
            agent = base.read(path)
        except (OSError, ValueError):
            continue  # Agent正在写回时下轮重读；完批仍须全矩阵验收。
        for row in agent.get('decision_log', []):
            summary['service_failures'] += row.get('generation_status') == 'service_failed'
            summary['posted_model_failures'] += bool(row.get('posted')) and row.get('response_model') != base.EXPECTED_MODEL
    return summary


def final_result(directory, run):
    summary = agent_summary(directory)
    base.require(not summary['service_failures'], '完整结果含正文服务失败')
    base.require(not summary['posted_model_failures'], '完整结果含无有效返回模型的发布')
    return base.completed(directory, run)


async def reconstruct_pending(directory):
    """只在指定副本的内存中补回已成功的694号发布，不重新生成正文或推进时钟。"""
    from agentsociety2.registry import scan_and_register_custom_modules, get_registered_env_modules
    scan_and_register_custom_modules(base.ROOT)
    cls = dict(get_registered_env_modules())['CurationDynamicsSpace']
    meta = base.read(directory / 'SOCIETY.json')
    step = base.read(directory / 'SOCIETY_STEP.json')
    raw = base.read(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    base.require(step['step_count'] == step['completed_step_count'] == raw['_chronological_batch_index'] == 602, '接续步数变化')
    actions = {(str(x['agent_id']), x['week']) for x in raw['_arrival_state']['actions']}
    decisions = {}
    for path in (directory / 'agents').glob('*/AGENT.json'):
        a = base.read(path)
        for row in a['decision_log']:
            key = (str(a['id']), row['week'])
            base.require(key not in decisions, '重复决策')
            decisions[key] = row
    base.require(len(actions) == len(raw['_arrival_state']['actions']) == 951 and len(decisions) == 953, '停止矩阵变化')
    base.require(set(decisions) - actions == {('29', '2026-W21'), ('95', '2026-W21')}, '待提交决策变化')
    silent, row = decisions['29', '2026-W21'], decisions['95', '2026-W21']
    base.require(silent['reason'] == 'below_threshold' and not silent['speak'] and not silent['generation_attempts'], '沉默决策有副作用')
    base.require(row['posted'] and row['generation_status'] == 'service_success' and row['response_model'] == base.EXPECTED_MODEL,
                 '待补正文并非成功原始响应')
    base.require(row['post_id'] == raw['_next_post_id'] == 694 and row['generation_attempts'] == 1, '待补帖子ID/请求变化')
    base.require(not raw['_pending_agent_posts'] and not raw['_posted_this_step'], '原检查点已有待提交发布，拒绝重复补齐')
    env = cls(**meta['env_kwargs']['CurationDynamicsSpace'])
    base.require(await env.restore(directory / 'env/CurationDynamicsSpace'), '环境恢复失败')
    rng = {k: getattr(env, k).getstate() for k in ('_rng_injection', '_rng_feed_random', '_rng_interest_noise', '_rng_interest_sample')}
    result = await env.create_post('95', row['content'])
    base.require(result['status'] == 'success' and result['post_id'] == 694 and not result['already_posted'], '原正文补齐失败')
    base.require(len(env._pending_agent_posts) == 1 and env._pending_agent_posts[0]['content'] == row['content'], '待提交正文不一致')
    base.require(env._next_post_id == 695 and all(getattr(env, k).getstate() == v for k, v in rng.items()), '补齐改变了随机状态')
    return env, dict(agent_id='95', week=row['week'], post_id=694, generation_attempts=1,
        response_model=row['response_model'], body_regenerated=False, source_step=602,
        reconstructed_keys=['_pending_agent_posts', '_posted_this_step', '_spoke_this_tick', '_next_post_id'])


async def probe():
    previous.PROBE, previous.AUDIT = PROBE, AUDIT
    await previous.probe()


def prepare():
    plan, old, audit = base.read(base.PLAN), base.read(base.STATE), base.read(AUDIT)
    base.require(not RECORD.exists() and not SNAPSHOT.exists() and old['status'] == 'stopped', '只允许本次明确恢复一次')
    base.require(not base.process_alive(old['supervisor_pid'], 'run_seed_extension'), '旧监督器仍活着')
    base.require(all(not base.process_alive(a['child_pid'], a['run_dir']) for a in old['active_runs']), '旧引擎仍活着')
    base.require(audit['status'] == base.read(CHECK)['status'] == base.read(PROBE)['status'] == 'passed', '本次离线/调度/接口检查未通过')
    base.require(audit['controller_sha256'] == base.digest(SELF) == base.read(CHECK)['controller_sha256'], '调度器验收已过期')
    base.require(len(old['completed']) == 11 and old['body_requests_used'] == 3529 and base.ledger_count(plan) == 7, '停止基线变化')
    for name, expected in {**plan['source_sha256'], **audit['preserved_sha256']}.items():
        base.require(base.digest(base.ROOT / name) == expected, '冻结来源/完成或失败证据变化: ' + name)
    for name, expected in audit['checkpoint_sha256'].items():
        base.require(base.digest(CHECKPOINT / name) == expected, '准备副本变化: ' + name)
    base.check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
        body_requests=3529, extra_requests=7, active_runs=0)
    done = {r['run_id']: r for r in old['completed']}
    sources = {a['run_id']: a for a in old['active_runs']}
    runs = [dict(r) for r in plan['runs']]
    for run in runs:
        if run['run_id'] in done:
            run['run_dir'] = done[run['run_id']]['run_dir']
        elif run['run_id'] == 'timestamp_bdr_v1_interest_no_r_s6':
            run.update(source_run_dir=str(CHECKPOINT), resume=True, prior_requests=465, run_dir=run['run_dir'] + '_resume2')
        elif run['run_id'] == 'timestamp_bdr_v1_interest_no_b_s7':
            run.update(resume=False, run_dir=run['run_dir'] + '_retry1')
        if run['run_id'] not in done:
            base.require(not (base.ROOT / run['run_dir']).exists(), '运行目标已存在，不覆盖或再次重试')
    failed = sources['timestamp_bdr_v1_interest_no_b_s7']
    discarded = [dict(run_id=failed['run_id'], run_dir=failed['run_dir'], **base.agent_summary(Path(failed['run_dir'])))]
    base.require(discarded[0]['requests'] == 62 and sum(r['requests'] for r in old['completed']) + 465 + 62 == 3529, '失败用量未正确累计')
    return plan, old, runs, environment(plan), discarded


def execute(plan, old, runs, env, discarded):
    active = []
    state = dict(old, status='running', supervisor_pid=os.getpid(), active_runs=[],
        controller=str(SELF.relative_to(base.ROOT)), recovery_record=str(RECORD.relative_to(base.ROOT)),
        recovery_started_at=base.stamp(), discarded_attempts=discarded)
    for key in ('error', 'stop_reason', 'finished_at', 'children_needing_attention'):
        state.pop(key, None)
    stop_at = None

    def save():
        for a in active:
            a['progress'], a['agent_summary'] = base.progress(Path(a['run_dir'])), agent_summary(Path(a['run_dir']))
        state['active_runs'] = [{k: v for k, v in a.items() if not k.startswith('_')} for a in active]
        # R副本已累计465次；B旧失败的62次单列，不重复加原R目录。
        state['body_requests_used'] = sum(r['requests'] for r in state['completed']) + sum(a['agent_summary']['requests'] for a in active)
        used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
        state['body_requests_used'] += sum(r.get('prior_requests', 0) for r in runs if r['run_id'] not in used) + sum(r['requests'] for r in discarded)
        state.update(extra_requests_used=base.ledger_count(plan), updated_at=base.stamp())
        base.write(base.STATE, state)

    def stop(reason):
        nonlocal stop_at
        if stop_at is None:
            stop_at = time.monotonic()
            state.update(status='stopping', stop_reason=reason)
            base.signal_engines(active, signal.SIGINT)

    signal.signal(signal.SIGTERM, lambda *_: stop('收到停止请求'))
    signal.signal(signal.SIGINT, lambda *_: stop('收到停止请求'))
    try:
        while active or len(state['completed']) < len(runs):
            base.require(stop_at is None, state.get('stop_reason', '停止请求'))
            save()
            base.check_limits(plan['budget'], started_at=plan['started_at'], now=datetime.now(timezone.utc),
                body_requests=state['body_requests_used'], extra_requests=state['extra_requests_used'], active_runs=len(active))
            base.require(all(base.digest(base.ROOT / p) == h for p, h in plan['source_sha256'].items()), '冻结文件变化')
            if RECORD.exists():
                base.require(all(base.digest(base.ROOT / p) == h for p, h in base.read(RECORD)['recovery_source_sha256'].items()), '接续工具变化')
            finished = []
            for a in active:
                summary = a['agent_summary']
                base.require(not summary['action_failures'], '行动/发布失败: ' + a['run_id'])
                base.require(not summary['service_failures'], '正文服务失败: ' + a['run_id'])
                base.require(not summary['posted_model_failures'], '已发布正文缺有效返回模型: ' + a['run_id'])
                base.require(not(set(summary['response_models']) - {base.EXPECTED_MODEL}), '实际返回模型变化')
                for name in ('recovery2-engine.log', 'recovery2-stderr.log'):
                    path = Path(a['run_dir']) / name
                    if path.exists():
                        with path.open(errors='replace') as f:
                            f.seek(a['_offsets'].get(name, 0)); recent = f.read(); a['_offsets'][name] = f.tell()
                        base.require(not any(s in recent for s in FATAL), '引擎/服务错误: ' + a['run_id'])
                code = a['_process'].poll()
                if code is not None:
                    base.require(code == 0, '引擎异常退出: ' + a['run_id'])
                    run = next(r for r in runs if r['run_id'] == a['run_id'])
                    finished.append((a, final_result(Path(a['run_dir']), run)))
            for a, result in finished:
                state['completed'].append(result); active.remove(a)
            used = {r['run_id'] for r in state['completed']} | {a['run_id'] for a in active}
            for run in [r for r in runs if r['run_id'] not in used][:2 - len(active)]:
                base.require(stop_at is None, '停止后不补位')
                base.require(datetime.now(timezone.utc) < datetime.fromisoformat(plan['deadline_at']), '原48小时截止已到')
                d = base.ROOT / run['run_dir']
                base.require(not d.exists(), '目标存在，不覆盖或再试')
                if run.get('resume'):
                    shutil.copytree(run['source_run_dir'], d)
                else:
                    d.mkdir()
                command = [env['PYTHON_PATH'], '-m', 'agentsociety2.society.cli', '--config', str(base.ROOT / run['config']),
                    '--steps', str(base.ROOT / run['steps']), '--run-dir', str(d), '--experiment-id', run['run_id'],
                    '--log-file', str(d / 'recovery2-engine.log'), '--batch-size', '100']
                if run.get('resume'):
                    command.append('--resume')
                with (d / 'recovery2-stdout.log').open('xb') as out, (d / 'recovery2-stderr.log').open('xb') as err:
                    proc = subprocess.Popen(command, cwd=base.ROOT, env=dict(env, AGENTSOCIETY_HOME_DIR=str(d / 'workspace')),
                                            stdout=out, stderr=err, start_new_session=True)
                active.append(dict(run_id=run['run_id'], condition=run['condition'], seed=run['seed'], run_dir=str(d),
                    child_pid=proc.pid, command=command, log_file=str(d / 'recovery2-engine.log'),
                    started_at=base.stamp(), resume=run.get('resume', False), _process=proc, _offsets={}))
                save()
            save()
            if active:
                time.sleep(10)
        state.update(status='completed', finished_at=base.stamp())
    except Exception as exc:
        stop(str(exc)); save()
        while any(a['_process'].poll() is None for a in active) and time.monotonic() - stop_at < 180:
            time.sleep(2)
        base.signal_engines(active, signal.SIGTERM)
        until = time.monotonic() + 60
        while any(a['_process'].poll() is None for a in active) and time.monotonic() < until:
            time.sleep(2)
        remaining = [a['child_pid'] for a in active if a['_process'].poll() is None]
        state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                     children_needing_attention=remaining, finished_at=None if remaining else base.stamp())
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        save()
    return state


def supervise():
    with (base.CONTROL / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan, old, runs, env, discarded = prepare()
        shutil.copy2(base.STATE, SNAPSHOT)
        record = dict(authorization='用户2026-10-24：按核查方案补完，保留11次与失败现场，R副本补齐后接续，B独立重跑及其余8次，检测修复并离线验收后两路启动，原配置/预算/截止，30分钟汇报，不分析',
            prepared_at=base.stamp(), original_runtime_plan_sha256=base.digest(base.PLAN),
            original_started_at=plan['started_at'], original_deadline_at=plan['deadline_at'],
            source_state=str(SNAPSHOT.relative_to(base.ROOT)), runs=runs, completed_retained=11,
            original_body_requests=3529, original_extra_requests=7, discarded_attempts=discarded,
            checkpoint_preparation=str(AUDIT.relative_to(base.ROOT)), pending_publication=base.read(AUDIT)['pending_publication'],
            prior_probe_requests=2, prior_probe_tokens=90, recovery_1_probe_requests=1, recovery_1_probe_tokens=51,
            recovery_2_probe=base.read(PROBE), scientific_config_changed=False,
            rule='R修复副本接续；B失败62次保留计费，独立重跑；其余8次补位，再次失败联停不自动重试',
            recovery_source_sha256={str(p.relative_to(base.ROOT)): base.digest(p) for p in
                (SELF, base.HERE / 'verify_seed_extension_recovery_2.py', AUDIT, PROBE, CHECK)})
        with RECORD.open('x') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        return execute(plan, old, runs, env, discarded)


def status():
    state = base.read(base.STATE)
    state['supervisor_alive'] = base.process_alive(state['supervisor_pid'], SELF.name + ' --continue-authorized')
    for a in state.get('active_runs', []):
        a.update(engine_alive=base.process_alive(a['child_pid'], a['run_dir']),
            actual_progress=base.progress(Path(a['run_dir'])), actual_agent_summary=agent_summary(Path(a['run_dir'])))
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for name in ('check', 'probe', 'continue-authorized', 'status', 'stop'):
        group.add_argument('--' + name, action='store_true')
    args = parser.parse_args()
    if args.probe:
        asyncio.run(probe())
    elif args.check:
        plan, old, runs, _, discarded = prepare()
        print(json.dumps(dict(status='passed', completed=11, remaining=10, discarded_body_requests=62,
            resume_body_carried=465, body_before=3529, extra_before=7, deadline_at=plan['deadline_at'],
            max_parallel=2, simulation_calls=0, llm_calls=0), ensure_ascii=False))
    elif args.status:
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif args.stop:
        s = status()
        if s['supervisor_alive']:
            os.kill(s['supervisor_pid'], signal.SIGTERM)
        else:
            for a in s.get('active_runs', []):
                if a['engine_alive']:
                    os.killpg(a['child_pid'], signal.SIGINT)
        print('已向本批匹配PID请求停止；用--status确认完全退出')
    else:
        raise SystemExit(0 if supervise()['status'] == 'completed' else 1)
