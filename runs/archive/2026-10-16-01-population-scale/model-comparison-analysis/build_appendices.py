"""Build readable weekly and matched runtime appendices from completed runs, offline."""
from pathlib import Path
from datetime import datetime
import json,csv,hashlib
B=Path(__file__).resolve().parent; R=B.parent; ROOT=R.parents[1]
OLD=ROOT/'hypothesis_4/experiment_2/runs/timestamp_v1'
NEW=R/'workspace/hypothesis_4/experiment_4/runs/cuc_model_v1'
load=lambda p:json.loads(p.read_text())
dt=lambda x:datetime.fromisoformat(x)
old=load(OLD/'batch_execution.json');new=load(R/'model-comparison-execution.json')
paths=[OLD/'batch_execution.json',R/'model-comparison-execution.json',Path(__file__)]
arms=[]
for a in ['random','chronological','interest']:
 po=OLD/f'timestamp_v1_{a}_s0/pid.json';pn=NEW/f'cuc_model_v1_{a}/pid.json';paths += [po,pn]
 o=load(po);n=load(pn)
 arms.append({'algorithm':a,'old_s0_engine_minutes':(dt(o['end_time'])-dt(o['start_time'])).total_seconds()/60,'new_engine_minutes':(dt(n['end_time'])-dt(n['start_time'])).total_seconds()/60,'old_pid_source':str(po.relative_to(ROOT)),'new_pid_source':str(pn.relative_to(ROOT))})
endold=next(x['finished_at'] for x in old['completed'] if x['run_id']=='timestamp_v1_interest_s0')
om=(dt(endold)-dt(old['started_at'])).total_seconds()/60
nm=(dt(new['finished_at'])-dt(new['started_at'])).total_seconds()/60
runtime={'matched_scope':'three s0 arms, serial; wall interval includes scheduling and framework calls','old_s0_wall_started_at':old['started_at'],'old_s0_wall_finished_at':endold,'old_s0_wall_minutes':om,'new_wall_started_at':new['started_at'],'new_wall_finished_at':new['finished_at'],'new_wall_minutes':nm,'new_to_old_wall_ratio':nm/om,'old_engine_total_minutes':sum(a['old_s0_engine_minutes'] for a in arms),'new_engine_total_minutes':sum(a['new_engine_minutes'] for a in arms),'arms':arms,'limitation':'Cross-time service/batch observation, not isolated provider latency or intrinsic model throughput; price unknown.','sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
(B/'data/runtime_comparison.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n')
rows=list(csv.DictReader((B/'data/weekly_metrics.csv').open()))
lines=['# 11周配对供给与曝光','', '每格为旧s0 → 新批。供给为当周成功发布的Agent帖，类型按固定作者；份额分母为当周全部Agent帖。曝光按实际feed池标签，包含外部与Agent，分母每周1000槽。百分比均按合并计数计算；本表不是正文语义分类。原始全部字段见[weekly_metrics.csv](weekly_metrics.csv)。','']
for a in ['random','chronological','interest']:
 lines += [f'## {a}','', '| 周 | 全部Agent供给 | 悼念Agent供给 | 悼念Agent供给份额 | 悼念曝光 | 玩梗Agent供给 | 玩梗Agent供给份额 | 玩梗曝光 |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for week in [f'2026-W{n}' for n in range(12,23)]:
  rr={v:next(r for r in rows if r['version']==v and r['algorithm']==a and r['seed']=='0' and r['week']==week) for v in ['old','new']}
  fields=[('agent_supply',False),('agent_supply_mourning',False),('supply_share_mourning',True),('exposure_share_mourning',True),('agent_supply_meme',False),('supply_share_meme',True),('exposure_share_meme',True)]
  vals=[]
  for key,pct in fields:
   fmt=lambda v:f'{100*float(rr[v][key]):.2f}%' if pct else str(int(float(rr[v][key])))
   vals.append(fmt('old')+' → '+fmt('new'))
  lines.append('| '+week+' | '+' | '.join(vals)+' |')
 lines.append('')
lines += ['## 全期峰位（并列均列）','','W13事件周不是所有曲线的全期最大值；以下按11周逐项查找。','','| 制度 | 指标 | 旧s0最大值/周 | 新最大值/周 |','|---|---|---|---|']
for a in ['random','chronological','interest']:
 for key,label,pct in [('agent_supply_mourning','悼念Agent供给',False),('exposure_share_mourning','悼念曝光份额',True),('agent_supply_meme','玩梗Agent供给',False),('exposure_share_meme','玩梗曝光份额',True)]:
  cells=[]
  for v in ['old','new']:
   rs=[r for r in rows if r['algorithm']==a and r['version']==v and r['seed']=='0'];m=max(float(r[key]) for r in rs);weeks=','.join(r['week'] for r in rs if float(r[key])==m);cells.append((f'{100*m:.2f}%' if pct else str(int(m)))+'/'+weeks)
  lines.append('| '+a+' | '+label+' | '+' | '.join(cells)+' |')
(B/'data/weekly_comparison.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'old_s0_wall_minutes':om,'new_wall_minutes':nm,'ratio':nm/om,'weekly_rows':33}))
