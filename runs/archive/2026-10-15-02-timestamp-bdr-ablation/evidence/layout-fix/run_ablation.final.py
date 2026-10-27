"""本run九次LLM消融的串行控制：官方CLI、独立账本、异常即停。

仅运行已冻结的九份配置；不改机制，不自动重启或从Full恢复。
启动凭据只在内存中从主项目.env读取，不写入运行计划/报告。
"""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit

from dotenv import dotenv_values

RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[1]
WORKSPACE = RUN/'workspace'
INIT = WORKSPACE/'hypothesis_4/experiment_3/init'
ORIGINAL_BATCH = RUN/'results/timestamp_bdr_v1'
ATTEMPT = 'timestamp_bdr_v1_attempt_02'
BATCH = RUN/'results'/ATTEMPT
ENGINE_BATCH = WORKSPACE/'hypothesis_4/experiment_3/runtime'/ATTEMPT
STATE = BATCH/'batch_execution.json'
LEDGER = BATCH/'_extra_attempts.count'
MAX_HOURS = 48
MAX_EXTRA = 990
MAX_REQUESTS = 10890


def read(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def check_action(row, agent_id):
    require(row.get('reason') not in ('action_failed','publication_failed','generation_failed'),
            f'Agent {agent_id} 行动/发布失败: '+str(row.get('reason')))
    require(not any(a.get('error_type') for a in row.get('generation_results', [])),
            f'Agent {agent_id} 出现服务技术异常，停止并保留尝试记录')
    require(row.get('generation_attempts',0) <= 2, '单机会生成请求超过两次')
    require(bool(row.get('posted')) == (row.get('post_id') is not None), '发布确认与ID不一致')
    if row.get('posted'):
        require(row.get('speak') is True, '未决定发言却发布')


def inspect_run(directory, final=False):
    """从实际checkpoint和Agent记录核对；写入途中的JSON留待下一轮。"""
    result = {'agents_recorded':0,'agent_decisions':0,'posts':0,'provider_requests':0,'retries':0,
              'content_rewrites':0,'fallback_posts':0,'reasons':{}}
    for name in ('pid.json','SOCIETY_STEP.json'):
        path = directory/name
        if path.exists():
            try: result[name] = read(path)
            except json.JSONDecodeError:
                if final: raise
    reasons = Counter()
    ids = set()
    for path in sorted((directory/'agents').glob('*/AGENT.json')):
        try: doc = read(path)
        except json.JSONDecodeError:
            if final: raise
            continue
        aid = str(doc.get('id',doc.get('agent_id')))
        require(aid not in ids, 'Agent重复工作区')
        ids.add(aid)
        rows = doc.get('decision_log',[])
        require(len({row['week'] for row in rows}) == len(rows), f'Agent {aid} 同周重复行动')
        for row in rows:
            check_action(row, aid)
            result['posts'] += row.get('posted') is True
            result['provider_requests'] += row.get('generation_attempts',0)
            result['retries'] += max(0,row.get('generation_attempts',0)-1)
            result['content_rewrites'] += sum(a.get('purpose')=='rewrite' for a in row.get('generation_results',[]))
            result['fallback_posts'] += row.get('content_origin')=='fallback'
            reasons[row.get('reason','unknown')] += 1
        result['agent_decisions'] += len(rows)
    result['agents_recorded'] = len(ids)
    result['reasons'] = dict(reasons)
    path = directory/'env/CurationDynamicsSpace/state/ENV_STATE.json'
    if path.exists():
        try: arrival = read(path)['_arrival_state']
        except json.JSONDecodeError:
            if final: raise
            arrival = None
        if arrival is not None:
            actions = arrival['actions']
            require(len({(a['agent_id'],a['week']) for a in actions})==len(actions), '环境重复行动')
            require(all(a.get('candidate_future',0)==0 for a in actions), '未来候选违规')
            require(all(p['available_at']<=a['acted_at'] and p['published_at']<=a['acted_at']
                        for a in actions for p in a['feed']), '未来曝光违规')
            result.update(environment_actions=len(actions),weeks=len(arrival['weeks']))
    if final:
        require(result.get('pid.json',{}).get('status')=='completed', '引擎未报告completed')
        require(result.get('SOCIETY_STEP.json',{}).get('step_count')==693, '未完成693步')
        require(result.get('environment_actions')==result['agent_decisions']==1100, '未完成1100次唯一行动')
        require(result.get('weeks')==11 and result['agents_recorded']==100, '周数或Agent数不完整')
    return result


def remaining_budget():
    """沿用首次启动后的绝对48小时截止时刻；不因重新启动顺延。"""
    original = read(ORIGINAL_BATCH/'runtime_plan.json')
    failure = read(RUN/'evidence/startup-failure/RESULT.json')
    require(failure['LLM_calls']==failure['extra_requests_consumed']==0, '前次请求预算不是零，需重新核算')
    require(read(ORIGINAL_BATCH/'batch_execution.json')['status']=='stopped', '前次尚未停止')
    deadline = datetime.fromisoformat(original['started_at']) + timedelta(hours=original['max_wall_hours'])
    seconds = (deadline-datetime.now(timezone.utc)).total_seconds()
    require(seconds>0, '原48小时预算已到期，不允许重新启动')
    return dict(original_started_at=original['started_at'], deadline_at=deadline.isoformat(),
                remaining_seconds_at_check=seconds, previous_LLM_calls=0, previous_extra_requests=0,
                remaining_extra_requests=MAX_EXTRA, provider_requests_upper_bound=MAX_REQUESTS)


def mirror_run(source, destination, cache, final=False):
    """实际输出保持在隔离区；验证稳定文件后原子镜像，结束时逐文件核对。"""
    destination.mkdir(parents=True,exist_ok=True)
    final_hashes = {}
    for item in sorted(source.rglob('*')):
        if not item.is_file() or '__pycache__' in item.parts or item.name.endswith('.tmp'):
            continue
        rel = item.relative_to(source)
        stat = item.stat()
        fingerprint = (stat.st_mtime_ns,stat.st_size)
        target = destination/rel
        if cache.get(str(rel))!=fingerprint or final:
            data = item.read_bytes()
            after = item.stat()
            if not final and (after.st_mtime_ns,after.st_size)!=fingerprint:
                continue
            if item.suffix=='.json':
                try: json.loads(data)
                except json.JSONDecodeError:
                    if final: raise
                    continue
            target.parent.mkdir(parents=True,exist_ok=True)
            temp = target.with_name(target.name+'.mirror-tmp')
            temp.write_bytes(data)
            temp.replace(target)
            cache[str(rel)] = fingerprint
        if final:
            require(digest(item)==digest(target), '最终镜像不一致: '+str(rel))
            final_hashes[str(rel)] = digest(target)
    if final:
        write(destination/'mirror_manifest.json',dict(source=str(source),sha256=final_hashes,verified_at=now()))
    return dict(files=len(cache),final_hashes_verified=len(final_hashes))


def preflight():
    manifest = read(INIT/'manifest.json')
    require(len(manifest['runs'])==9 and manifest['decision_opportunities']==9900, '矩阵或机会预算不符')
    frozen = dict(manifest['source_sha256'])
    frozen.update(manifest['mechanism_sha256'])
    frozen.update(manifest['output_sha256'])
    frozen['hypothesis_4/experiment_3/init/manifest.json'] = digest(INIT/'manifest.json')
    frozen['hypothesis_4/experiment_3/init/source_lock.json'] = manifest['source_lock_sha256']
    frozen['hypothesis_4/experiment_3/init/config_params.py'] = manifest['generator_sha256']
    for name, expected in frozen.items():
        require(digest(WORKSPACE/name)==expected, '冻结文件已变化: '+name)
    require(not subprocess.check_output(['git','diff','--name-only','--','custom','hypothesis_4/experiment_2/init'],cwd=WORKSPACE,text=True), '隔离区已有机制或主配置修改')
    baseline = read(RUN/'baseline.json')
    for name,item in baseline['runtime_plan_source_hash_checks'].items():
        require(digest(PROJECT/name)==item['expected'], '主批来源已变化: '+name)
    for full in baseline['main_completed_runs']:
        if 'reference_state_sha256' in full:
            require(digest(PROJECT/full['run_dir']/'env/CurationDynamicsSpace/state/ENV_STATE.json')==full['reference_state_sha256'], 'Full参照状态已改变')
    verify = read(RUN/'evidence/verification/verify.json')
    require(verify['success'] and verify['network_attempts']==verify['provider_calls']==0, '离线验收记录不满足要求')
    env = os.environ.copy()
    env.update({k:str(v) for k,v in dotenv_values(PROJECT/'.env').items() if v is not None})
    main = read(INIT/'reference/main_runtime_plan.json')
    require(bool(env.get('AGENTSOCIETY_LLM_API_KEY')), '缺少模型凭据')
    require(env.get('AGENTSOCIETY_LLM_MODEL')==main['model'], '当前模型与主批不同，停止启动')
    require(urlsplit(env.get('AGENTSOCIETY_LLM_API_BASE','')).hostname==main['service_host'], '服务地址与主批不同')
    env.update(WORKSPACE_PATH=str(WORKSPACE), AGENTSOCIETY_WORKSPACE=str(WORKSPACE),
               LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16',
               PYTHONUNBUFFERED='1')
    # 离线验收钩子只供验收使用；实际运行不继承其PYTHONPATH或审计日志变量。
    env.pop('BDR_NETWORK_AUDIT',None)
    require('offline_guard' not in env.get('PYTHONPATH',''), '进程仍带离线网络钩子')
    remaining_budget()
    return manifest,frozen,env,main


def supervise():
    BATCH.mkdir(parents=True,exist_ok=True)
    lock = (BATCH/'supervisor.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    require(not STATE.exists(), '已有运行记录，禁止重复启动或覆盖')
    manifest,frozen,env,main = preflight()
    budget = remaining_budget()
    require(not ENGINE_BATCH.is_symlink() and ENGINE_BATCH.resolve().is_relative_to(WORKSPACE), '引擎输出必须实际位于隔离worktree')
    ENGINE_BATCH.mkdir(parents=True,exist_ok=True)
    require(not LEDGER.exists() or LEDGER.read_text().strip() in ('','0'), '新账本不是零')
    alias = WORKSPACE/'hypothesis_4/experiment_3/runs/timestamp_bdr_v1'
    require(alias.is_symlink() and alias.resolve()==BATCH, '隔离账本未映射到本run持久目录')
    for run in manifest['runs']:
        require(not (BATCH/run['run_id']).exists() and not (ENGINE_BATCH/run['run_id']).exists(), '输出目录已存在: '+run['run_id'])
    plan = dict(authorized=True,authorization='2026-10-15用户明确授权：修正输出布局、完整CLI禁网验收通过后，按原模型及剩余预算重新启动九次消融；保留首次失败，异常先停。',
        baseline_commit=manifest['baseline_commit'],source_sha256=frozen,supervisor_sha256=digest(Path(__file__)),
        model=main['model'],service_host=main['service_host'],runs=manifest['runs'],serial=True,
        decision_opportunities=9900,extra_requests_limit=MAX_EXTRA,provider_requests_upper_bound=MAX_REQUESTS,
        max_wall_hours=MAX_HOURS,stall_stop_minutes=30,stop_policy='异常或技术请求错误即停；保留记录，不自动重启/续跑/调参',
        workspace=str(WORKSPACE),engine_output=str(ENGINE_BATCH),persistent_output=str(BATCH),ledger_alias=str(alias),
        previous_attempt=str(ORIGINAL_BATCH),remaining_budget=budget,started_at=now())
    write(BATCH/'runtime_plan.json',plan)
    state = dict(supervisor_pid=os.getpid(),status='running',started_at=now(),completed=[],current_run=None,deadline_at=budget['deadline_at'])
    write(STATE,state)
    child = None
    directory = None
    persistent = None
    mirror_cache = {}
    stop_reason = None
    stop_at = None
    started = time.monotonic()

    def request_stop(reason):
        nonlocal stop_reason,stop_at
        if stop_reason is None:
            stop_reason,stop_at = reason,time.monotonic()
            state.update(status='stopping',failure_reason=reason)
            write(STATE,state)
            if child is not None and child.poll() is None:
                os.killpg(child.pid,signal.SIGINT)

    def on_signal(signum,frame):
        request_stop('收到停止信号 '+str(signum))

    signal.signal(signal.SIGTERM,on_signal)
    signal.signal(signal.SIGINT,on_signal)
    try:
        for run in manifest['runs']:
            require(stop_reason is None,'已请求停止')
            directory = ENGINE_BATCH/run['run_id']
            persistent = BATCH/run['run_id']
            directory.mkdir()
            mirror_cache = {}
            child_env = dict(env,AGENTSOCIETY_HOME_DIR=str(directory/'workspace'))
            command = [env.get('PYTHON_PATH') or sys.executable,'-m','agentsociety2.society.cli',
                       '--config',str(WORKSPACE/run['config']),'--steps',str(WORKSPACE/run['steps']),
                       '--run-dir',str(directory),'--experiment-id',run['run_id'],
                       '--log-file',str(directory/'engine.log'),'--batch-size','100']
            with (directory/'stdout.log').open('ab') as stdout,(directory/'stderr.log').open('ab') as stderr:
                child = subprocess.Popen(command,cwd=WORKSPACE,env=child_env,stdout=stdout,stderr=stderr,start_new_session=True)
            state.update(current_run=run['run_id'],current_run_dir=str(directory),persistent_mirror_dir=str(persistent),
                         child_pid=child.pid,command=command,updated_at=now())
            write(STATE,state)
            last_progress,last_at = None,time.monotonic()
            offsets = {}
            while child.poll() is None:
                time.sleep(10)
                try:
                    require(datetime.now(timezone.utc)<datetime.fromisoformat(budget['deadline_at']),'达到原48小时截止时刻')
                    require(all(digest(WORKSPACE/p)==h for p,h in frozen.items()),'运行期间源码或输入改变')
                    progress = inspect_run(directory)
                    signature = (progress.get('SOCIETY_STEP.json',{}).get('step_count'),progress['agent_decisions'])
                    if signature != last_progress:
                        last_progress,last_at = signature,time.monotonic()
                    require(time.monotonic()-last_at < 1800,'实际步数/行动记录连续30分钟未推进')
                    extra = int(LEDGER.read_text().strip() or '0') if LEDGER.exists() else 0
                    requests = sum(r['progress']['provider_requests'] for r in state['completed'])+progress['provider_requests']
                    require(extra<=MAX_EXTRA and requests<=MAX_REQUESTS,'累计请求超过冻结预算')
                    for name in ('engine.log','stderr.log'):
                        logfile = directory/name
                        if logfile.exists():
                            with logfile.open(errors='replace') as log:
                                log.seek(offsets.get(name,0));recent = log.read();offsets[name]=log.tell()
                            require(not any(s in recent for s in ('Error executing step','Traceback (most recent call last)','RayTaskError','OutOfMemoryError')),'引擎出现异常，见 '+name)
                    mirror = mirror_run(directory,persistent,mirror_cache)
                    state.update(progress=progress,mirror=mirror,provider_requests=requests,extra_requests=extra,
                                 budget_remaining_seconds=max(0,(datetime.fromisoformat(budget['deadline_at'])-datetime.now(timezone.utc)).total_seconds()),
                                 updated_at=now(),elapsed_seconds=time.monotonic()-started)
                    write(STATE,state)
                except Exception as exc:
                    request_stop(str(exc))
                if stop_reason and child.poll() is None and time.monotonic()-stop_at > 180:
                    os.killpg(child.pid,signal.SIGTERM)
                    child.wait(timeout=60)
            require(stop_reason is None,stop_reason or '已停止')
            require(child.returncode==0,f'官方引擎退出码异常 {child.returncode}')
            progress = inspect_run(directory,final=True)
            mirror_run(directory,persistent,mirror_cache,final=True)
            state['completed'].append(dict(run_id=run['run_id'],finished_at=now(),progress=progress))
            state.update(progress=progress,updated_at=now())
            write(STATE,state)
        state.update(status='completed',finished_at=now())
    except Exception as exc:
        if child is not None and child.poll() is None:
            request_stop(str(exc))
            try: child.wait(timeout=180)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGTERM)
                try: child.wait(timeout=60)
                except subprocess.TimeoutExpired: state['child_needs_manual_attention']=True
        state.update(status='stopped' if stop_reason else 'failed',error=str(exc),finished_at=now())
        print(str(exc),file=sys.stderr,flush=True)
    finally:
        if directory is not None and directory.exists():
            try: mirror_run(directory,persistent,mirror_cache,final=child is not None and child.poll() is not None)
            except Exception as exc: state['mirror_error']=str(exc)
        state.update(updated_at=now(),elapsed_seconds=time.monotonic()-started)
        write(STATE,state)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--stop',action='store_true')
    args = parser.parse_args()
    if args.status:
        state = read(STATE) if STATE.exists() else {'status':'not_started'}
        if state.get('current_run'):
            try: state['actual_progress']=inspect_run(Path(state.get('current_run_dir',str(ENGINE_BATCH/state['current_run']))))
            except RuntimeError as exc: state['actual_audit_error']=str(exc)
        for key in ('supervisor_pid','child_pid'):
            if key in state:
                check = subprocess.run(['ps','-p',str(state[key]),'-o','command='],capture_output=True,text=True)
                state[key+'_alive'] = check.returncode==0 and (str(RUN) in check.stdout)
        print(json.dumps(state,ensure_ascii=False,indent=2))
    elif args.stop:
        state = read(STATE)
        command = subprocess.check_output(['ps','-p',str(state['supervisor_pid']),'-o','command='],text=True)
        require(str(Path(__file__).resolve()) in command,'监督PID已不是本批进程，拒绝发信号')
        os.kill(state['supervisor_pid'],signal.SIGTERM)
        print('已请求停止当前及后续条件，保留现场。')
    elif args.check:
        manifest,frozen,env,main = preflight()
        print(json.dumps({'preflight':'PASS','runs':len(manifest['runs']),'frozen_files':len(frozen),
                          'model':main['model'],'service_host':main['service_host'],'remaining_budget':remaining_budget(),'LLM_calls':0},ensure_ascii=False))
    else:
        supervise()
