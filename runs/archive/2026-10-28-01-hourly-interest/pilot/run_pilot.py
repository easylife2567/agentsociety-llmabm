"""三臂单seed串行控制器；只调用官方CLI，失败即停，不自动重跑或恢复。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
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

HERE = Path(__file__).resolve().parent
PLAN = HERE / 'runtime_plan.json'
STATE = HERE / 'batch_execution.json'
ALGORITHMS = ('random', 'chronological', 'interest')
WEEKS = {f'2026-W{i:02d}' for i in range(12, 23)}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def path_in(root, value):
    path = (root / value).resolve()
    require(path.is_relative_to(root), '路径越出隔离工作区')
    return path


def progress(directory):
    result = {}
    for name in ('pid.json', 'SOCIETY_STEP.json'):
        try:
            result[name] = read(directory / name)
        except (OSError, ValueError):
            pass  # 引擎写入瞬间的不完整JSON在下轮读取，完成检查则严格读取。
    return result


def agent_summary(directory, strict=False):
    result = dict(agent_files=0, decisions=0, unique_decisions=0, posted=0,
                  requests=0, action_failures=0, service_failures=0,
                  posted_model_failures=0, response_models={}, invalid_publications=0)
    keys, posts = set(), {}
    for path in sorted((directory / 'agents').glob('*/AGENT.json')):
        try:
            agent = read(path)
        except (OSError, ValueError):
            if strict:
                raise
            continue
        result['agent_files'] += 1
        for row in agent.get('decision_log', []):
            key = (str(agent['id']), row['week'])
            require(key not in keys, '出现重复Agent周决策')
            require(key[0] in {str(i) for i in range(1, 101)} and key[1] in WEEKS, 'Agent或统计周越界')
            keys.add(key)
            result['decisions'] += 1
            result['requests'] += int(row.get('generation_attempts', 0))
            result['action_failures'] += row.get('reason') in ('action_failed', 'publication_failed')
            result['service_failures'] += row.get('generation_status') == 'service_failed'
            model = row.get('response_model')
            if model:
                result['response_models'][model] = result['response_models'].get(model, 0) + 1
            if row.get('posted'):
                result['posted'] += 1
                result['posted_model_failures'] += not bool(model)
                valid = bool(row.get('content', '').strip()) and row.get('post_id') is not None and row.get('reason') == 'published'
                result['invalid_publications'] += not valid
                if valid:
                    pid = str(row['post_id'])
                    require(pid not in posts, '不同决策记录使用重复post_id')
                    posts[pid] = dict(author=str(agent['id']), content=row['content'])
    result['unique_decisions'] = len(keys)
    return result, keys, posts


def health(summary, expected_model):
    require(not any(summary[k] for k in ('action_failures', 'service_failures',
                                        'posted_model_failures', 'invalid_publications')),
            'Agent行动、最终服务返回或确认发布记录失败')
    models = set(summary['response_models'])
    require(len(models) <= 1, '同一条件出现不同实际返回模型')
    if models:
        actual = next(iter(models))
        require(expected_model is None or actual == expected_model, '实际返回模型与本批锁定版本不同')
        return actual
    return expected_model


def final_result(directory, run, expected_model):
    info = progress(directory)
    require(info.get('pid.json', {}).get('status') == 'completed', '引擎没有报告完成')
    require(info.get('SOCIETY_STEP.json', {}).get('step_count') == 693, '实际步数不是693')
    env = read(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    require(env['_arrival_agent_return_policy'] == 'next_batch', '环境实际回流策略错误')
    arrival = env['_arrival_state']
    actions = arrival['actions']
    action_keys = {(str(row['agent_id']), row['week']) for row in actions}
    expected_keys = {(str(i), week) for i in range(1, 101) for week in WEEKS}
    require(len(actions) == 1100 and action_keys == expected_keys, '环境行动缺失或重复')
    require(len(arrival['weeks']) == 11 and {row['week'] for row in arrival['weeks']} == WEEKS,
            '11周汇总不完整')
    require(not arrival['delayed'], '小时回流仍有延迟队列')
    summary, decisions, published = agent_summary(directory, strict=True)
    expected_model = health(summary, expected_model)
    require(summary['agent_files'] == 100 and decisions == expected_keys and summary['decisions'] == 1100,
            '100份Agent决策不完整')
    require(decisions == action_keys, 'Agent与环境行动不对应')
    pool = env['_posts']
    for pid, post in published.items():
        require(pid in pool and pool[pid]['content'] == post['content'] and
                str(pool[pid]['author_id']) == post['author'], '确认发布未在最终环境中找到对应正文/作者')
    for row in actions:
        require(not row['candidate_future'], '发生未来曝光')
        require(all(p['published_at'] <= row['acted_at'] and p['available_at'] <= row['acted_at']
                    for p in row['feed']), '帖子曝光早于实际可用时间')
    source_files = [directory / 'SOCIETY_STEP.json', directory / 'pid.json',
                    directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json',
                    *sorted((directory / 'agents').glob('*/AGENT.json'))]
    return dict(run_id=run['run_id'], algorithm=run['algorithm'], run_dir=str(directory),
                finished_at=now().isoformat(), steps=693, actions=1100, weeks=11, **summary,
                expected_returned_model=expected_model,
                raw_sha256={str(p.relative_to(directory)): digest(p) for p in source_files})


def frozen_sources(plan):
    root = Path(plan['workspace']).resolve()
    for name, expected in plan['source_sha256'].items():
        path = Path(name) if Path(name).is_absolute() else root / name
        require(digest(path) == expected, '冻结输入或源码已改变: ' + name)


def preflight(plan):
    require(plan['execution_authorized'] is True, '没有本批运行授权')
    require((plan['decision_opportunities'], plan['extra_requests_limit'], plan['body_outer_requests_limit']) ==
            (3300, 330, 3630), '本批规模或请求上界变化')
    require(tuple(r['algorithm'] for r in plan['runs']) == ALGORITHMS and len(plan['runs']) == 3,
            '只允许既定顺序三臂seed0')
    require(now() < datetime.fromisoformat(plan['deadline_at']), '本批绝对截止已到')
    root = Path(plan['workspace']).resolve()
    frozen_sources(plan)
    require(not STATE.exists(), '本批已有状态，禁止重复启动或自动恢复')
    ledger = Path(plan['ledger_path']).resolve()
    require(ledger.parent == HERE and not ledger.exists(), '本批账本必须独立、尚不存在')
    directories = set()
    for row in plan['runs']:
        directory = path_in(root, row['run_dir'])
        require(directory not in directories and not directory.exists(), '运行目标已存在或重复')
        directories.add(directory)
        config = read(path_in(root, row['config']) if not Path(row['config']).is_absolute() else row['config'])
        env = config['env_modules'][0]['kwargs']
        require(env['arrival_agent_return_policy'] == 'next_batch' and env['random_seed'] == 0 and
                env['recommendation_algorithm'] == row['algorithm'] and len(config['agents']) == 100,
                '测试配置机制、seed、算法或人数不符')
        for agent in config['agents']:
            require(agent['kwargs']['content_retry_budget'] == dict(limit=330, ledger_path=str(ledger)),
                    '额外请求未使用本批330共享账本')
    environment = os.environ.copy()
    environment.update({k: str(v) for k, v in dotenv_values(plan['env_file']).items() if v is not None})
    require(all(environment.get(k) for k in ('AGENTSOCIETY_LLM_MODEL', 'AGENTSOCIETY_LLM_API_KEY',
                                           'AGENTSOCIETY_LLM_API_BASE')), '当前模型配置不完整')
    require(environment['AGENTSOCIETY_LLM_MODEL'] == plan['requested_model'], '实际请求模型改变')
    require(hashlib.sha256(environment['AGENTSOCIETY_LLM_API_BASE'].encode()).hexdigest() ==
            plan['api_base_sha256'], '实际模型服务地址改变')
    environment.update(WORKSPACE_PATH=str(root), LITELLM_LOCAL_MODEL_COST_MAP='True',
                       MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
                       AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16', RAY_ADDRESS='local')
    return root, ledger, environment


def process_matches(pid, text):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat=,command='], capture_output=True, text=True)
    parts = result.stdout.strip().split(None, 1)
    return result.returncode == 0 and len(parts) == 2 and not parts[0].startswith('Z') and text in parts[1]


def stop_child(child, directory, grace=30):
    if child is None or child.poll() is not None:
        return []
    if not process_matches(child.pid, str(directory)):
        return [child.pid]  # PID身份不符时不误伤其他进程。
    try:
        os.killpg(child.pid, signal.SIGINT)
    except ProcessLookupError:
        return []
    try:
        child.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        if process_matches(child.pid, str(directory)):
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                return []
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            return [child.pid]
    return []


def supervise(poll_seconds=10):
    with (HERE / 'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan = read(PLAN)
        plan_hash = digest(PLAN)
        root, ledger, environment = preflight(plan)
        ledger.write_text('0')
        state = dict(status='running', supervisor_pid=os.getpid(), started_at=now().isoformat(),
                     updated_at=now().isoformat(), runtime_plan_sha256=plan_hash,
                     controller_sha256=digest(__file__), deadline_at=plan['deadline_at'],
                     completed=[], active_run=None, expected_returned_model=plan.get('expected_returned_model'),
                     extra_requests_used=0, total_body_requests=0)
        child, directory = None, None
        stop_requested = False

        def request_stop(*_):
            nonlocal stop_requested
            stop_requested = True

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        write(STATE, state)
        try:
            for run in plan['runs']:
                require(not stop_requested, '收到停止请求')
                require(now() < datetime.fromisoformat(plan['deadline_at']), '达到本批绝对截止')
                require(digest(PLAN) == plan_hash, '运行计划被改变')
                frozen_sources(plan)
                directory = path_in(root, run['run_dir'])
                require(not directory.exists(), '已有引擎目录，拒绝自动重跑')
                directory.mkdir(parents=True)
                config_path = Path(run['config']) if Path(run['config']).is_absolute() else root / run['config']
                steps_path = Path(run['steps']) if Path(run['steps']).is_absolute() else root / run['steps']
                command = [plan['python'], '-m', 'agentsociety2.society.cli', '--config', str(config_path),
                           '--steps', str(steps_path), '--run-dir', str(directory), '--experiment-id',
                           '4_2_hourly_return_pilot_s0', '--log-file', str(directory / 'engine.log'), '--batch-size', '100']
                with (directory / 'stdout.log').open('xb') as out, (directory / 'stderr.log').open('xb') as err:
                    child = subprocess.Popen(command, cwd=root,
                        env=dict(environment, AGENTSOCIETY_HOME_DIR=str(directory / 'workspace')),
                        stdout=out, stderr=err, start_new_session=True)
                state['active_run'] = dict(run_id=run['run_id'], algorithm=run['algorithm'], run_dir=str(directory),
                                           child_pid=child.pid, command=command)
                write(STATE, state)
                offset = 0
                while True:
                    require(not stop_requested, '收到停止请求')
                    require(now() < datetime.fromisoformat(plan['deadline_at']), '达到本批绝对截止')
                    require(digest(PLAN) == plan_hash, '运行计划被改变')
                    frozen_sources(plan)
                    summary, _, _ = agent_summary(directory)
                    state['expected_returned_model'] = health(summary, state['expected_returned_model'])
                    extra = int(ledger.read_text() or '0')
                    requests = sum(r['requests'] for r in state['completed']) + summary['requests']
                    require(0 <= extra <= 330 and requests <= 3630, '本批请求预算越界')
                    logfile = directory / 'engine.log'
                    if logfile.exists():
                        with logfile.open(errors='replace') as stream:
                            stream.seek(offset); recent = stream.read(); offset = stream.tell()
                        require(not any(s in recent for s in ('Error executing step', 'RayTaskError', 'OutOfMemoryError')),
                                '引擎日志报告步骤或资源失败')
                    state.update(updated_at=now().isoformat(), extra_requests_used=extra, total_body_requests=requests)
                    state['active_run'].update(progress=progress(directory), agent_summary=summary)
                    write(STATE, state)
                    if child.poll() is not None:
                        require(child.returncode == 0, '引擎退出码异常')
                        result = final_result(directory, run, state['expected_returned_model'])
                        write(HERE / f"completion_{run['algorithm']}.json", result)
                        state['completed'].append(result)
                        state['active_run'] = None
                        write(STATE, state)
                        break
                    time.sleep(poll_seconds)
            state.update(status='completed', finished_at=now().isoformat())
        except Exception as exc:
            remaining = stop_child(child, directory)
            state.update(status='stopping' if remaining else 'stopped', error=str(exc),
                         children_needing_attention=remaining, finished_at=None if remaining else now().isoformat())
            print(str(exc), file=sys.stderr, flush=True)
        finally:
            if child is not None and directory is not None:
                try:
                    summary, _, _ = agent_summary(directory)
                    state.update(extra_requests_used=int(ledger.read_text() or '0'),
                                 total_body_requests=sum(r['requests'] for r in state['completed']) +
                                 (summary['requests'] if state['active_run'] is not None else 0))
                except Exception as exc:
                    state['final_read_error'] = str(exc)
                state['updated_at'] = now().isoformat()
            write(STATE, state)
        return state['status'] == 'completed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--start', action='store_true')
    modes.add_argument('--status', action='store_true')
    modes.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    if args.status:
        state = read(STATE) if STATE.exists() else dict(status='not_started')
        if state.get('active_run'):
            directory = Path(state['active_run']['run_dir'])
            state['actual_progress'] = progress(directory)
            state['actual_agent_summary'] = agent_summary(directory)[0]
        print(json.dumps(state, ensure_ascii=False, indent=2))
    elif args.stop:
        state = read(STATE)
        require(state['status'] == 'running' and process_matches(state['supervisor_pid'], str(Path(__file__).resolve())),
                '本批监督器未运行或PID身份不匹配')
        os.kill(state['supervisor_pid'], signal.SIGTERM)
        print('已向本批监督器请求停止')
    else:
        raise SystemExit(0 if supervise() else 1)


if __name__ == '__main__':
    main()
