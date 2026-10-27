from pathlib import Path
import difflib
r=Path(__file__).resolve().parents[2]
s=(Path(__file__).parent/'run_ablation.before.py').read_text()
s=s.replace('def preflight():','def preflight(pin_main_model=False):')
s=s.replace("    require(env.get('AGENTSOCIETY_LLM_MODEL')==main['model'],", "    if pin_main_model:\n        env['AGENTSOCIETY_LLM_MODEL'] = main['model']\n    require(env.get('AGENTSOCIETY_LLM_MODEL')==main['model'],")
a=s.index('def supervise():')
s=s[:a]+'''def process_alive(pid, expected):
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
                item['mirror'] = mirror_run(Path(item['current_run_dir']),Path(item['persistent_mirror_dir']),item['_cache'],final=not engine_alive(item))
            except Exception as exc:
                item['final_audit_error'] = str(exc)
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
'''
final=Path(__file__).parent/'run_ablation.final.py'
final.write_text(s)
original=(Path(__file__).parent/'run_ablation.before.py').read_text()
patch=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='a/'+str((r/'run_ablation.py').relative_to(r.parents[1])),tofile='b/'+str((r/'run_ablation.py').relative_to(r.parents[1]))))
(r/'parallel-control.patch').write_text(patch)
print(len(s.splitlines()),'lines; patch saved')
