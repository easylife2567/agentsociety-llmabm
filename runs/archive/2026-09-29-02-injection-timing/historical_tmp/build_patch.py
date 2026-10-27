"""基于明确基线生成并核验已有代码的最终接线补丁。"""
from pathlib import Path
import subprocess
import difflib
root=Path.cwd()
task=root/'runs/2026-09-29-02-injection-timing'
paths=['custom/envs/curation_dynamics_space.py','custom/agents/curation_discourse_agent.py']
base='bab8e2a'
patch=[]
for name in paths:
    old=subprocess.check_output(['git','show',f'{base}:{name}'],text=True)
    new=old
    if '/envs/' in name:
        marker='        self._recommendation_algorithm = str(kwargs.pop("recommendation_algorithm", "random"))'
        new=new.replace(marker,'''        # 显式调度开关独立于推荐算法；未配置时使用原有制度。
        schedule_mode = kwargs.pop("schedule_mode", "legacy")
        arrival_mode = kwargs.pop("arrival_mode", "timestamp")
'''+marker)
        marker='    # ---------------- 资产加载 ----------------'
        new=new.replace(marker,'''        self._arrival = None
        if schedule_mode == "arrival_timing":
            spec = importlib.util.spec_from_file_location(
                "curation_arrival_schedule", Path(__file__).with_name("curation_arrival_schedule.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._arrival_mech = mech
            self._arrival = module.ArrivalSchedule(self, arrival_mode)

'''+marker)
        new=new.replace('        self.t = start_datetime\n', '''        self.t = start_datetime
        if self._arrival is not None:
            await self._arrival.init(start_datetime)
            return
''')
        marker='        if self._recommendation_algorithm == "chronological":\n            await self._step_chronological(tick, t)'
        new=new.replace(marker,'''        if self._arrival is not None:
            await self._arrival.step(tick, t)
            return
'''+marker)
        marker='        feed = [dict(item) for item in self._feeds.get(aid, [])]'
        new=new.replace(marker,'''        if self._arrival is not None:
            return self._arrival.get_feed(aid)
'''+marker)
        marker='        text = str(content or "").strip()'
        new=new.replace(marker,'''        if self._arrival is not None and aid not in self._chronological_active_agents:
            return {"status": "fail", "reason": "inactive agent"}
'''+marker)
        marker='        self._flush_pending_to_pool()\n\n    def set_replay_writer'
        new=new.replace(marker,'''        if self._arrival is None:
            self._flush_pending_to_pool()

    def set_replay_writer''')
        marker='            "_step_index": self._step_index,'
        new=new.replace(marker,'''            "_arrival_state": self._arrival.state if self._arrival is not None else None,
            "_exposure_age_buckets": self._exposure_age_buckets,
'''+marker)
        marker='        expected_policy = {\n'
        new=new.replace(marker,'''        if self._arrival is not None:
            restored = d.get("_arrival_state")
            if not restored or restored.get("mode") != self._arrival.mode:
                raise ValueError("checkpoint arrival mode mismatch")
            self._arrival.state = restored
        self._exposure_age_buckets = d.get("_exposure_age_buckets", self._exposure_age_buckets)
'''+marker)
    else:
        marker='        if self._chronological_action_hour is not None:\n            hour_of_week'
        new=new.replace(marker,'''        if self.get_profile().get("arrival_timing", False):
            # 到达诊断使用单独的生成与记账流程，保持数值效用同源。
            spec = importlib.util.spec_from_file_location(
                "curation_arrival_action", Path(__file__).with_name("curation_arrival_action.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return await module.act(self, tick, t)
        if self._chronological_action_hour is not None:
            hour_of_week''')
    if new==old: raise RuntimeError('empty patch')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    target=task/'tmp/baseline'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(old)
    (task/'tmp'/Path(name).name).write_text(new)
p=task/'2026-09-30-01-arrival-timing.patch'
p.write_text(''.join(patch))
subprocess.run(['git','apply','--check',str(p)],cwd=task/'tmp/baseline',check=True)
subprocess.run(['git','apply',str(p)],cwd=root,check=True)
