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


def preflight(pin_main_model=False):
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
    if pin_main_model:
        env['AGENTSOCIETY_LLM_MODEL'] = main['model']
    require(env.get('AGENTSOCIETY_LLM_MODEL')==main['model'], '当前模型与主批不同，停止启动')
    require(urlsplit(env.get('AGENTSOCIETY_LLM_API_BASE','')).hostname==main['service_host'], '服务地址与主批不同')
    env.update(WORKSPACE_PATH=str(WORKSPACE), AGENTSOCIETY_WORKSPACE=str(WORKSPACE),
               LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False',
               AGENTSOCIETY_LLM_RAY_MAX_WORKERS='4', AGENTSOCIETY_LLM_RAY_CONCURRENCY='16',
               PYTHONUNBUFFERED='1', RAY_ADDRESS='local')
    # 离线验收钩子只供验收使用；实际运行不继承其PYTHONPATH或审计日志变量。
    env.pop('BDR_NETWORK_AUDIT',None)
    require('offline_guard' not in env.get('PYTHONPATH',''), '进程仍带离线网络钩子')
    remaining_budget()
    return manifest,frozen,env,main


def process_alive(pid, expected):
    check = subprocess.run(['ps','-p',str(pid),'-o','stat=,command='],capture_output=True,text=True)
    fields = check.stdout.strip().split(None,1)
    return check.returncode==0 and len(fields)==2 and not fields[0].startswith('Z') and expected in fields[1]


def engine_alive(item):
    proc = item.get('_process')
    return proc.poll() is None if proc is not None else process_alive(item['child_pid'],item['current_run_dir'])


def signal_engines(active, sig):
    # 只对本run且命令仍匹配的独立引擎进程组发信号，避免PID复用误伤。
    for item in active:
        if engine_alive(item) and process_alive(item['child_pid'],item['current_run_dir']):
            os.killpg(item['child_pid'],sig)


def enforce_budget(completed, active, extra):
    requests = sum(row['progress']['provider_requests'] for row in completed+active)
    require(extra<=MAX_EXTRA and requests<=MAX_REQUESTS,'两路累计请求超过冻结共享预算')
    return requests


def pending_runs(runs, completed, active):
    used = {row['run_id'] for row in completed+active}
    return [run for run in runs if run['run_id'] not in used]


def supervise(parallel_handoff=False):
    manifest,frozen,env,main = preflight(pin_main_model=True)
    require(parallel_handoff, '本批已有记录；必须显式使用--parallel-handoff，禁止重复启动')
    history = RUN/'evidence/parallel'
    require(not (history/'serial-state.json').exists(), '已交接过，禁止重启或再次接管')
    previous = read(STATE)
    require(previous['status']=='running' and 'active_runs' not in previous,'只接管正常运行的原串行监督器')
    old_pid = previous['supervisor_pid']
    require(process_alive(old_pid,str(Path(__file__).resolve())), '原监督器不存活，不能自动续接')
    # 原控制器只处理TERM/INT，它们会中断子引擎。暂停父进程取得一致快照，
    # 再用默认HUP退出父进程；独立session的引擎保持运行，由本进程接管。
    os.kill(old_pid,signal.SIGSTOP)
    parent_released = False
    try:
        previous = read(STATE)
        require(previous['supervisor_pid']==old_pid and previous['status']=='running','交接时串行状态改变')
        directory = Path(previous['current_run_dir'])
        require(process_alive(previous['child_pid'],str(directory)), '待接管引擎已退出')
        children = subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()
        actual = [int(p[0]) for line in children if len(p:=line.split(None,2))==3 and int(p[1])==old_pid and 'agentsociety2.society.cli' in p[2]]
        require(actual==[previous['child_pid']], '父进程与状态中的引擎不一致，取消交接')
        inspect_run(directory)
        for row in previous['completed']:
            inspect_run(ENGINE_BATCH/row['run_id'],final=True)
        write(history/'serial-state.json',previous)
        write(history/'serial-runtime-plan.json',read(BATCH/'runtime_plan.json'))
        os.kill(old_pid,signal.SIGHUP)
        os.kill(old_pid,signal.SIGCONT)
        parent_released = True
    finally:
        if not parent_released and process_alive(old_pid,str(Path(__file__).resolve())):
            os.kill(old_pid,signal.SIGCONT)
    # 持有原批次同一把锁，沿用原输出和原账本，绝不创建新预算。
    lock = (BATCH/'supervisor.lock').open('a')
    for attempt in range(50):
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            break
        except BlockingIOError:
            time.sleep(.1)
    else:
        signal_engines([dict(child_pid=previous['child_pid'],current_run_dir=previous['current_run_dir'])],signal.SIGINT)
        raise RuntimeError('交接未能取得原监督锁，已请求引擎停止')
    state = dict(previous,supervisor_pid=os.getpid(),max_parallel=2,active_runs=[],
                 handoff_at=now(),status='running',updated_at=now())
    for key in ('current_run','current_run_dir','persistent_mirror_dir','child_pid','command','progress','mirror'):
        state.pop(key,None)
    active = []
    stop_reason = None
    stop_at = None

    def add_active(run, pid, proc=None, credential_epoch='new_env_pinned_original_model'):
        item = dict(run_id=run['run_id'],child_pid=pid,current_run_dir=str(ENGINE_BATCH/run['run_id']),
                    persistent_mirror_dir=str(BATCH/run['run_id']),credential_epoch=credential_epoch,
                    _process=proc,_cache={},_signature=None,_last_at=time.monotonic(),_offsets={},progress={})
        active.append(item)
        return item

    def save():
        state['active_runs'] = [{k:v for k,v in item.items() if not k.startswith('_')} for item in active]
        state.update(updated_at=now(),elapsed_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(state['started_at'])).total_seconds(),
                     budget_remaining_seconds=max(0,(datetime.fromisoformat(state['deadline_at'])-datetime.now(timezone.utc)).total_seconds()))
        write(STATE,state)

    def request_stop(reason):
        nonlocal stop_reason,stop_at
        if stop_reason is None:
            stop_reason,stop_at = reason,time.monotonic()
            state.update(status='stopping',failure_reason=reason)
            signal_engines(active,signal.SIGINT)
            save()

    signal.signal(signal.SIGTERM,lambda sig,frame: request_stop('收到停止信号 '+str(sig)))
    signal.signal(signal.SIGINT,lambda sig,frame: request_stop('收到停止信号 '+str(sig)))
    old_run = next(run for run in manifest['runs'] if run['run_id']==previous['current_run'])
    add_active(old_run,previous['child_pid'],credential_epoch='existing_engine_old_api_unchanged')
    try:
        plan = read(BATCH/'runtime_plan.json')
        plan.update(serial=False,max_parallel=2,parallel_changed_at=now(),
                    parallel_authorization='用户明确授权两个独立实验并行，保持原模型/科学配置/共享预算/截止，异常两路联停',
                    supervisor_sha256=digest(Path(__file__)),api_change=dict(new_host=urlsplit(env['AGENTSOCIETY_LLM_API_BASE']).hostname,
                    new_path=urlsplit(env['AGENTSOCIETY_LLM_API_BASE']).path,env_model_overridden_to=main['model'],
                    existing_engine_restarted=False,secrets_saved=False),launch_order='原manifest顺序补空位；完成顺序由运行耗时决定')
        write(BATCH/'runtime_plan.json',plan)
        save()
        while active or pending_runs(manifest['runs'],state['completed'],active):
            require(stop_reason is None,stop_reason or '已停止')
            require(datetime.now(timezone.utc)<datetime.fromisoformat(state['deadline_at']),'达到原48小时截止时刻')
            require(all(digest(WORKSPACE/p)==h for p,h in frozen.items()),'运行期间源码或输入改变')
            finished = []
            for item in active:
                directory = Path(item['current_run_dir'])
                alive = engine_alive(item)
                if not alive and item['_process'] is not None:
                    require(item['_process'].returncode==0, '官方引擎退出码异常 '+str(item['_process'].returncode))
                progress = inspect_run(directory,final=not alive)
                item['progress'] = progress
                signature = (progress.get('SOCIETY_STEP.json',{}).get('step_count'),progress['agent_decisions'])
                if signature!=item['_signature']:
                    item['_signature'],item['_last_at'] = signature,time.monotonic()
                require(time.monotonic()-item['_last_at']<1800,'实际步数/行动连续30分钟未推进: '+item['run_id'])
                for name in ('engine.log','stderr.log'):
                    logfile = directory/name
                    if logfile.exists():
                        with logfile.open(errors='replace') as log:
                            log.seek(item['_offsets'].get(name,0));recent=log.read();item['_offsets'][name]=log.tell()
                        require(not any(s in recent for s in ('Error executing step','Traceback (most recent call last)','RayTaskError','OutOfMemoryError')),'引擎异常: '+item['run_id']+'/'+name)
                item['mirror'] = mirror_run(directory,Path(item['persistent_mirror_dir']),item['_cache'],final=not alive)
                if not alive:
                    finished.append(item)
            extra = int(LEDGER.read_text().strip() or '0') if LEDGER.exists() else 0
            state.update(provider_requests=enforce_budget(state['completed'],active,extra),extra_requests=extra)
            for item in finished:
                state['completed'].append(dict(run_id=item['run_id'],finished_at=now(),progress=item['progress']))
                active.remove(item)
            for run in pending_runs(manifest['runs'],state['completed'],active)[:2-len(active)]:
                require(stop_reason is None,'已经请求停止，禁止新开条件')
                directory = ENGINE_BATCH/run['run_id']
                require(not directory.exists() and not (BATCH/run['run_id']).exists(),'拒绝覆盖或重跑 '+run['run_id'])
                directory.mkdir()
                child_env = dict(env,AGENTSOCIETY_HOME_DIR=str(directory/'workspace'))
                command = [env.get('PYTHON_PATH') or sys.executable,'-m','agentsociety2.society.cli',
                           '--config',str(WORKSPACE/run['config']),'--steps',str(WORKSPACE/run['steps']),
                           '--run-dir',str(directory),'--experiment-id',run['run_id'],
                           '--log-file',str(directory/'engine.log'),'--batch-size','100']
                with (directory/'stdout.log').open('ab') as stdout,(directory/'stderr.log').open('ab') as stderr:
                    proc = subprocess.Popen(command,cwd=WORKSPACE,env=child_env,stdout=stdout,stderr=stderr,start_new_session=True)
                add_active(run,proc.pid,proc)
                save()
            require(len(active)<=2,'并行数超过2')
            save()
            time.sleep(10)
        state.update(status='completed',finished_at=now())
    except Exception as exc:
        request_stop(str(exc))
        # 两路同时收到INT；共用同一停机等待窗，不能逐路各等180秒。
        while any(engine_alive(item) for item in active) and time.monotonic()-stop_at<180:
            time.sleep(2)
        signal_engines(active,signal.SIGTERM)
        term_at = time.monotonic()
        while any(engine_alive(item) for item in active) and time.monotonic()-term_at<60:
            time.sleep(2)
        state.update(status='stopped',error=str(exc),finished_at=now(),
                     children_needing_attention=[item['child_pid'] for item in active if engine_alive(item)])
        print(str(exc),file=sys.stderr,flush=True)
    finally:
        for item in active:
            try:
                item['progress'] = inspect_run(Path(item['current_run_dir']))
            except Exception as exc:
                item['final_audit_error'] = str(exc)
            # 审计发现失败也必须镜像原始证据，不让异常检查跳过保全。
            try:
                item['mirror'] = mirror_run(Path(item['current_run_dir']),Path(item['persistent_mirror_dir']),item['_cache'],final=not engine_alive(item))
            except Exception as exc:
                item['mirror_error'] = str(exc)
        save()


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--stop',action='store_true')
    parser.add_argument('--parallel-handoff',action='store_true')
    args = parser.parse_args()
    if args.status:
        state = read(STATE) if STATE.exists() else {'status':'not_started'}
        if 'active_runs' in state:
            for item in state['active_runs']:
                item['child_pid_alive'] = process_alive(item['child_pid'],item['current_run_dir'])
                try: item['actual_progress'] = inspect_run(Path(item['current_run_dir']))
                except RuntimeError as exc: item['actual_audit_error'] = str(exc)
        elif state.get('current_run'):
            try: state['actual_progress']=inspect_run(Path(state['current_run_dir']))
            except RuntimeError as exc: state['actual_audit_error']=str(exc)
            state['child_pid_alive'] = process_alive(state['child_pid'],state['current_run_dir'])
        if 'supervisor_pid' in state:
            state['supervisor_pid_alive'] = process_alive(state['supervisor_pid'],str(Path(__file__).resolve()))
        print(json.dumps(state,ensure_ascii=False,indent=2))
    elif args.stop:
        state = read(STATE)
        if process_alive(state['supervisor_pid'],str(Path(__file__).resolve())):
            os.kill(state['supervisor_pid'],signal.SIGTERM)
        else:
            active = state.get('active_runs') or ([state] if state.get('child_pid') else [])
            signal_engines(active,signal.SIGINT)
            state.update(status='stopping',failure_reason='监督器已退出；停止入口直接请求全部残留子引擎退出',updated_at=now())
            write(STATE,state)
        print('已请求两路当前及后续条件全部停止，保留现场。')
    elif args.check:
        manifest,frozen,env,main = preflight(pin_main_model=True)
        print(json.dumps({'preflight':'PASS','runs':len(manifest['runs']),'frozen_files':len(frozen),
                          'model':main['model'],'max_parallel':2,'service_host':main['service_host'],
                          'remaining_budget':remaining_budget(),'LLM_calls':0},ensure_ascii=False))
    else:
        supervise(parallel_handoff=args.parallel_handoff)
