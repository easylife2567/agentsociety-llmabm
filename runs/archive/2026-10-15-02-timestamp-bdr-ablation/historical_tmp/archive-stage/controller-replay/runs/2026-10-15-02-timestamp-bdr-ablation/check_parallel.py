"""两路调度、接管、共享限额与联停的禁网合成检查；不启动Ray或模型。"""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import importlib.util
import json
import signal
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('controller',ROOT/'run_ablation.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
results=[]

def scenario(fault=False):
    with TemporaryDirectory(dir=ROOT/'tmp') as tmp:
        t=Path(tmp);batch=t/'batch';engine=t/'workspace/runtime';history=t/'evidence/parallel'
        for p in (batch,engine,history):p.mkdir(parents=True)
        runs=[dict(run_id=f'r{i}',config=f'c{i}',steps=f's{i}') for i in range(9)]
        for i in (0,1):(engine/f'r{i}').mkdir()
        old=dict(status='running',supervisor_pid=10,child_pid=100,current_run='r1',current_run_dir=str(engine/'r1'),
                 persistent_mirror_dir=str(batch/'r1'),completed=[dict(run_id='r0',progress={'provider_requests':88})],
                 started_at=c.now(),deadline_at=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat())
        c.write(batch/'batch_execution.json',old);c.write(batch/'runtime_plan.json',{'serial':True,'remaining_budget':{'deadline_at':old['deadline_at']}})
        living={100:True};polls={};launches=[];signals=[];max_active=[1]
        class Proc:
            def __init__(self,command,**kwargs):
                self.pid=200+len(launches);self.returncode=None
                rid=command[command.index('--experiment-id')+1];launches.append(rid);living[self.pid]=True
                assert kwargs['env']['AGENTSOCIETY_LLM_MODEL']=='original'
                max_active[0]=max(max_active[0],sum(living.values()))
            def poll(self):
                self.returncode = None if living[self.pid] else 0
                return self.returncode
        def ps_alive(pid,expected):return living.get(pid,pid==10)
        def inspect(directory,final=False):
            rid=Path(directory).name
            if fault and len(launches) and rid=='r2':raise RuntimeError('synthetic provider failure')
            return {'provider_requests':1,'agent_decisions':1100 if final else polls.get(rid,1),'SOCIETY_STEP.json':{'step_count':693 if final else polls.get(rid,1)}}
        def sleep(seconds):
            if seconds==10:
                for pid in list(living):
                    if living[pid]:
                        polls[str(pid)]=polls.get(str(pid),0)+1
                        if polls[str(pid)]>=2:living[pid]=False
        def kill(pid,sig):
            signals.append((pid,sig))
            if pid==10 and sig==signal.SIGHUP:living[10]=False
        def killpg(pid,sig):signals.append((pid,sig));living[pid]=False
        env={'AGENTSOCIETY_LLM_API_BASE':'https://example.invalid/api/plan/v3','AGENTSOCIETY_LLM_MODEL':'original'}
        with patch.multiple(c,RUN=t,BATCH=batch,STATE=batch/'batch_execution.json',ENGINE_BATCH=engine,WORKSPACE=t/'workspace',LEDGER=batch/'ledger'), \
             patch.object(c,'preflight',return_value=({'runs':runs},{},env,{'model':'original'})), \
             patch.object(c,'process_alive',side_effect=ps_alive),patch.object(c,'inspect_run',side_effect=inspect), \
             patch.object(c,'mirror_run',return_value={'files':0}),patch.object(c.subprocess,'Popen',Proc), \
             patch.object(c.subprocess,'check_output',return_value='100 10 python -m agentsociety2.society.cli'), \
             patch.object(c.os,'kill',side_effect=kill),patch.object(c.os,'killpg',side_effect=killpg), \
             patch.object(c.signal,'signal'),patch.object(c.time,'sleep',side_effect=sleep):
            c.supervise(parallel_handoff=True)
        state=c.read(batch/'batch_execution.json')
        assert max_active[0]==2,(max_active,launches)
        assert 'r0' not in launches and 'r1' not in launches
        if fault:
            assert state['status']=='stopped' and launches==['r2'],state
            assert (100,signal.SIGINT) in signals and (200,signal.SIGINT) in signals,signals
        else:
            assert state['status']=='completed' and len(state['completed'])==9,state
            assert launches==[f'r{i}' for i in range(2,9)],launches
            assert state['provider_requests']==96,state
        assert state['deadline_at']==old['deadline_at']
        assert c.read(history/'serial-state.json')['child_pid']==100
        assert not any(pid==100 and sig in (signal.SIGINT,signal.SIGTERM) for pid,sig in signals) if not fault else True
        results.append(dict(case='joint_stop' if fault else 'adoption_and_all_nine',passed=True,launches=launches,max_parallel=max_active[0]))

(ROOT/'tmp').mkdir(exist_ok=True)
scenario();scenario(fault=True)
for completed,active,extra in [([{'progress':{'provider_requests':10800}}],[{'progress':{'provider_requests':91}}],0),([],[],991)]:
    try:c.enforce_budget(completed,active,extra)
    except RuntimeError:pass
    else:raise AssertionError('shared budget overflow accepted')
results.append(dict(case='sum_both_lanes_and_shared_extra_limit',passed=True))
print(json.dumps(dict(passed=True,checks=results,network_calls=0,LLM_calls=0),indent=2))
