"""从 ReplayReader 与冻结 Agent/Env 账本复算模型服务比较；不调用模型。"""
import csv, hashlib, json, re, statistics, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from agentsociety2.storage import ReplayReader
ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'runs/2026-10-16-01-population-scale'
OUT=Path(__file__).resolve().parent/'data'; OUT.mkdir(exist_ok=True)
TYPES=['marketing','mourning','other','meme','education']
ALGS=['random','chronological','interest']
def dump(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def norm(s): return re.sub(r'\s+','',unicodedata.normalize('NFKC',s or ''))
def phase(w): return 'W12' if w.endswith('W12') else ('W13-W18' if int(w[-2:])<=18 else 'W19-W22')
def read_arm(p):
 agents={}; dec={}
 for f in sorted((p/'agents').glob('*/AGENT.json')):
  a=load(f); aid=str(a['id']);agents[aid]=a
  for d in a['decision_log']: dec[(aid,d['week'])]=d
 env=load(p/'env/CurationDynamicsSpace/state/ENV_STATE.json')
 pub={x['stable_key']:x for x in env['_posts'].values() if x.get('source')=='agent'}
 pub.update({x['stable_key']:x for x in env['_arrival_state']['delayed']})
 return {'path':p,'agents':agents,'dec':dec,'env':env,'published':pub}
def sample_side(arm,key):
 aid,w=key; d=arm['dec'][key];a=arm['agents'][aid];res=d.get('generation_results') or []
 return {'source':str(arm['path'].relative_to(ROOT)/'agents'/f'agent_{int(aid):04d}'/'AGENT.json'),'agent_id':aid,'week':w,'persona':a['profile']['persona'],'params':a['profile'].get('params'),'prompt_context':d.get('prompt_context'),'actual_feed':next((x['feed'] for x in arm['env']['_arrival_state']['actions'] if str(x['agent_id'])==aid and x['week']==w),None),'messages':d.get('messages'),'raw_first_response':res[0] if res else None,'all_generation_results':res,'final_published':arm['published'].get(f'agent:{aid}:{w}',{}).get('content'),'agent_record_content':d.get('content'),'environment_post':arm['published'].get(f'agent:{aid}:{w}'),'post_id':d.get('post_id'),'flags':{k:d.get(k) for k in ['speak','posted','reason','generation_attempts','initial_content_status','initial_content_checks','content_status','content_checks','content_origin','detail_edits','response_model','provider_refusal']},'utility':d.get('u'),'components':d.get('components')}
arms={}
for alg in ALGS:
 arms[('new',alg,0)]=read_arm(RUN/f'workspace/hypothesis_4/experiment_4/runs/cuc_model_v1/cuc_model_v1_{alg}')
 for seed in range(3):arms[('old',alg,seed)]=read_arm(ROOT/f'hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_{alg}_s{seed}')
# 配对键哈希稳定抽样：每制度×作者类型×阶段最多两对；仅共同成功发布键。
samples=[];selection=[]
for alg in ALGS:
 n,o=arms[('new',alg,0)],arms[('old',alg,0)];groups=defaultdict(list)
 for key,d in n['dec'].items():
  if d.get('posted') and o['dec'].get(key,{}).get('posted'):
   groups[(n['agents'][key[0]]['profile']['agent_type'],phase(key[1]))].append(key)
 for (typ,ph),keys in sorted(groups.items()):
  ordered=sorted(keys,key=lambda k:hashlib.sha256(f'{alg}|{typ}|{ph}|{k[0]}|{k[1]}'.encode()).hexdigest())
  selection.append({'algorithm':alg,'author_type':typ,'phase':ph,'eligible_pairs':len(keys),'selected':len(ordered[:2])})
  for key in ordered[:2]:samples.append({'sample_id':f'{alg}:{key[0]}:{key[1]}','algorithm':alg,'author_type':typ,'phase':ph,'new':sample_side(n,key),'old':sample_side(o,key)})
(OUT/'paired_text_samples.jsonl').write_text(''.join(json.dumps(s,ensure_ascii=False)+'\n' for s in samples))
dump('sample_selection.json',{'rule':'SHA256(algorithm|author_type|phase|agent_id|week), lexicographic ascending, first 2 per stratum; common posted Agent-week only','strata':selection,'pairs':len(samples)})
print('PAIRED_SAMPLES',len(samples),str(OUT/'paired_text_samples.jsonl'),flush=True)
weekly=[];quality=[];integrity=[];sources=[];summaries=[];macro={};details={}
def dist(texts):
 lengths=sorted(len(s or '') for s in texts); counts=Counter(norm(s) for s in texts)
 def pct(q):
  z=(len(lengths)-1)*q;i=int(z);return lengths[i]+(lengths[min(i+1,len(lengths)-1)]-lengths[i])*(z-i) if lengths else None
 return {'n':len(texts),'min':min(lengths) if lengths else None,'p25':pct(.25),'median':pct(.5),'p75':pct(.75),'max':max(lengths) if lengths else None,'mean':statistics.mean(lengths) if lengths else None,'over_300_chars':sum(x>300 for x in lengths),'normalized_unique':len(counts),'duplicate_excess':sum(c-1 for c in counts.values()),'posts_in_duplicate_groups':sum(c for c in counts.values() if c>1),'duplicate_rule':'NFKC then remove all whitespace; count n-minus-unique, within arm'}
for (version,alg,seed),a in arms.items():
 p=a['path'];r=ReplayReader(p/'replay');ds=r.get_dataset_by_id('curation_dynamics.env_state');rows=r.fetch_dataset_rows(ds,order_by='step')['rows'];r.close();a['rows']=rows
 dec=a['dec']; env=a['env']; actions=env['_arrival_state']['actions']; byweek=defaultdict(list)
 for (aid,w),d in dec.items():byweek[w].append((aid,d))
 types=Counter(x['profile']['agent_type'] for x in a['agents'].values());a['actions']={(str(x['agent_id']),x['week']):x for x in actions}
 for row in rows:
  z={'version':version,'algorithm':alg,'seed':seed,**row}
  ww=byweek[row['week']]
  for typ in TYPES:
   z['population_'+typ]=types[typ];z['posted_'+typ]=sum(bool(d.get('posted')) for aid,d in ww if a['agents'][aid]['profile']['agent_type']==typ);z['participation_'+typ]=z['posted_'+typ]/types[typ]
  z['actions']=len(ww);z['posted_all']=sum(bool(d.get('posted')) for _,d in ww)
  weekly.append(z)
 posted=[d for d in dec.values() if d.get('posted')]; intent=[d for d in dec.values() if d.get('speak')]; req=[d for d in dec.values() if d.get('generation_results')];firsts=[d['generation_results'][0] for d in req]
 originals=[x.get('generated_content',x.get('content','')) or '' for x in firsts];finals=[x.get('content','') or '' for x in a['published'].values()]
 status=Counter(d.get('initial_content_status') for d in req);checks=Counter(x for d in req for x in d.get('initial_content_checks',[]));origins=Counter(d.get('content_origin') for d in posted);purpose=Counter(x.get('purpose') for d in req for x in d['generation_results']);failures=[{'agent_id':aid,'week':w,'reason':d.get('reason'),'generation_status':d.get('generation_status')} for (aid,w),d in dec.items() if d.get('speak') and not d.get('posted')]
 q={'version':version,'algorithm':alg,'seed':seed,'posted':len(posted),'intended_speak':len(intent),'first_requests':len(req),'body_outer_requests':sum(d.get('generation_attempts',0) for d in dec.values()),'generation_attempt_purposes':dict(purpose),'initial_status':dict(status),'initial_checks':dict(checks),'origin':dict(origins),'local_detail_edited_posts':sum(bool(d.get('detail_edits')) for d in posted),'rewrite_attempts':sum(c for k,c in purpose.items() if k!='generation'),'fallback_posts':sum(c for k,c in origins.items() if 'fallback' in str(k)),'empty_first_raw':sum(not x.strip() for x in originals),'provider_refusal_first':sum(bool(x.get('provider_refusal')) for x in firsts),'failed_attempt_records':sum(bool(x.get('error')) or x.get('status')=='failed' for d in req for x in d['generation_results']),'response_models':dict(Counter(d.get('response_model') for d in posted)),'raw_text':dist(originals),'final_text':dist(finals),'intent_without_post':failures}
 quality.append(q)
 totals=dict(Counter(str(x['agent_id']) for x in actions));posted_agents=Counter(aid for (aid,w),d in dec.items() if d.get('posted'))
 ledger_counts={str(k):v for k,v in env['_total_posts_by_agent'].items()};pooled={x['stable_key']:x for x in env['_posts'].values() if x.get('source')=='agent'};pooled.update({x['stable_key']:x for x in env['_arrival_state']['delayed']});published_by_stable={f'agent:{aid}:{w}':d for (aid,w),d in dec.items() if d.get('posted')}
 integ={'version':version,'algorithm':alg,'seed':seed,'society':load(p/'SOCIETY_STEP.json'),'agents':len(a['agents']),'population':dict(types),'decisions':len(dec),'unique_action_keys':len(a['actions']),'environment_actions':len(actions),'weeks':sorted(byweek),'weekly_decisions':{w:len(v) for w,v in byweek.items()},'weekly_replay_rows':len(rows),'published_agent_ledger':len(posted),'published_environment_count':sum(ledger_counts.values()),'published_environment_post_records_including_delayed':len(pooled),'per_agent_post_counts_match':dict(posted_agents)==ledger_counts,'stable_post_keys_match':set(pooled)==set(published_by_stable),'all_published_texts_match_stripped_agent_records':all(pooled[k].get('content')==d.get('content','').strip() for k,d in published_by_stable.items()),'all_published_texts_match_agent_records':all(pooled[k].get('content')==d.get('content') for k,d in published_by_stable.items()),'published_text_mismatches':[{'stable_key':k,'agent_chars':len(d.get('content','')),'environment_chars':len(pooled[k].get('content','')),'environment_equals_agent_stripped':pooled[k].get('content')==d.get('content','').strip()} for k,d in published_by_stable.items() if pooled[k].get('content')!=d.get('content')],'weekly_replay_supply_matches_agent_posts':all(z['agent_supply']==sum(d.get('posted',False) for aid,d in byweek[z['week']]) for z in rows),'env_actions_week_keys_match_decisions':set(a['actions'])==set(dec)}
 integrity.append(integ)
 row13=next(x for x in weekly if x['version']==version and x['algorithm']==alg and x['seed']==seed and x['week']=='2026-W13');late=[x for x in weekly if x['version']==version and x['algorithm']==alg and x['seed']==seed and int(x['week'][-2:])>=19]
 s={'version':version,'algorithm':alg,'seed':seed,'posts':len(posted),'W13_mourning_author_posts':row13['posted_mourning'],'W13_mourning_author_participation':row13['participation_mourning'],'W13_agent_mourning_supply':row13['agent_supply_mourning'],'W13_mourning_exposure_share':row13['exposure_share_mourning'],'W13_official_exposure_slots':row13['official_exposure_slots'],'late_meme_author_posts':sum(x['posted_meme'] for x in late),'late_meme_author_participation':sum(x['posted_meme'] for x in late)/(types['meme']*4),'late_agent_meme_supply':sum(x['agent_supply_meme'] for x in late),'late_agent_all_supply':sum(x['agent_supply'] for x in late),'late_agent_meme_supply_share':sum(x['agent_supply_meme'] for x in late)/sum(x['agent_supply'] for x in late),'late_meme_exposures':sum(x['exposure_meme'] for x in late),'late_all_exposures':sum(x['total_exposures'] for x in late),'late_meme_exposure_share':sum(x['exposure_meme'] for x in late)/sum(x['total_exposures'] for x in late),'late_all_meme_supply_share':sum(x['agent_supply_meme']+x['injected_meme'] for x in late)/sum(x['total_supply'] for x in late)}
 summaries.append(s);macro[(version,alg,seed)]=s
 for f in [p/'SOCIETY_STEP.json',p/'env/CurationDynamicsSpace/state/ENV_STATE.json',p/'replay/_schema.json',*sorted((p/'replay').glob('curation_dynamics_env_state.*.jsonl')),*sorted((p/'agents').glob('*/AGENT.json'))]:sources.append({'role':'raw_'+version,'algorithm':alg,'seed':seed,'path':str(f.relative_to(ROOT)),'sha256':sha(f),'bytes':f.stat().st_size})
# 数值与逐Agent比较，保留全部1100对，不将正文差异混入决策数值。
comparisons=[];decision_diffs=[];feed_diffs=[];first_differences={}
NUMFIELDS=['speak','posted','u','threshold','components','reason']
for alg in ALGS:
 n,o=arms[('new',alg,0)],arms[('old',alg,0)];allkeys=sorted(n['dec'],key=lambda k:(n['dec'][k]['acted_at'],int(k[0])))
 diffs=[];feeds=[];tendency=[]
 for key in allkeys:
  nd,od=n['dec'][key],o['dec'][key]; changed={k:{'old':od.get(k),'new':nd.get(k)} for k in NUMFIELDS if nd.get(k)!=od.get(k)}
  if changed:diffs.append({'algorithm':alg,'agent_id':key[0],'week':key[1],'acted_at':nd['acted_at'],'changes':changed})
  na,oa=n['actions'][key],o['actions'][key];nf,of=na['feed'],oa['feed'];nk=[x['stable_key'] for x in nf];ok=[x['stable_key'] for x in of]
  if nk!=ok:feeds.append({'algorithm':alg,'agent_id':key[0],'week':key[1],'acted_at':na['acted_at'],'old_keys':ok,'new_keys':nk,'old_types':[x['type'] for x in of],'new_types':[x['type'] for x in nf]})
  if nd.get('posted') and od.get('posted'):
   sk=f'agent:{key[0]}:{key[1]}'
   def pmap(a):
    pp={x['stable_key']:x for x in a['env']['_posts'].values()};pp.update({x['stable_key']:x for x in a['env']['_arrival_state']['delayed']});return pp
   np,op=pmap(n).get(sk),pmap(o).get(sk)
   if np and op and np.get('tendencies')!=op.get('tendencies'):tendency.append({'agent_id':key[0],'week':key[1],'acted_at':nd['acted_at'],'stable_key':sk,'new':{k:np.get(k) for k in ['content','type','assigned_type','tendencies']},'old':{k:op.get(k) for k in ['content','type','assigned_type','tendencies']}})
 decision_diffs+=diffs;feed_diffs+=feeds
 numeric_weekly=[]
 for nr,orr in zip(n['rows'],o['rows']):
  numeric_weekly.append({'week':nr['week'],'differences':{k:{'old':orr.get(k),'new':v,'delta':v-orr.get(k) if isinstance(v,(int,float)) and isinstance(orr.get(k),(int,float)) else None} for k,v in nr.items() if k not in ['t'] and v!=orr.get(k)}})
 first_differences[alg]={'agent_decision_difference_count':len(diffs),'feed_key_difference_count':len(feeds),'post_tendency_difference_count':len(tendency),'first_decision_difference':diffs[0] if diffs else None,'first_posted_difference':next((d for d in diffs if 'posted' in d['changes']),None),'posted_difference_count':sum('posted' in d['changes'] for d in diffs),'first_feed_difference':feeds[0] if feeds else None,'first_post_tendency_difference':tendency[0] if tendency else None,'weekly_differences':numeric_weekly}
 for m,val in macro[('new',alg,0)].items():
  if m!='seed' and isinstance(val,(int,float)):
   old=macro[('old',alg,0)][m];rng=[macro[('old',alg,ss)][m] for ss in range(3)];comparisons.append({'algorithm':alg,'metric':m,'old_s0':old,'new':val,'delta':val-old,'old_s0_s1_s2_min':min(rng),'old_s0_s1_s2_max':max(rng),'new_inside_old_range':min(rng)<=val<=max(rng)})
# 全量异常、单侧发布及关键分歧上下文，独立于稳定配对语义样本。
anomalies=[];unpaired=[];class_rates=[]
for alg in ALGS:
 for version in ['new','old']:
  a=arms[(version,alg,0)]
  for key,d in a['dec'].items():
   envtxt=a['published'].get(f'agent:{key[0]}:{key[1]}',{}).get('content','') or ''
   if d.get('generation_results') and (d.get('initial_content_status')!='accepted' or d.get('detail_edits') or d.get('generation_attempts',0)>1 or len(envtxt)>300 or ('fallback' in str(d.get('content_origin')))):
    anomalies.append({'version':version,'algorithm':alg,'sample_id':f'{version}:{alg}:{key[0]}:{key[1]}',**sample_side(a,key)})
  for typ in TYPES:
   late=[d for (aid,w),d in a['dec'].items() if int(w[-2:])>=19 and a['agents'][aid]['profile']['agent_type']==typ]
   class_rates.append({'version':version,'algorithm':alg,'author_type':typ,'population':sum(x['profile']['agent_type']==typ for x in a['agents'].values()),'late_posted':sum(bool(d.get('posted')) for d in late),'late_opportunities':len(late),'late_participation':sum(bool(d.get('posted')) for d in late)/len(late)})
 n,o=arms[('new',alg,0)],arms[('old',alg,0)]
 for key in n['dec']:
  if bool(n['dec'][key].get('posted'))!=bool(o['dec'][key].get('posted')):unpaired.append({'algorithm':alg,'agent_id':key[0],'week':key[1],'new':sample_side(n,key),'old':sample_side(o,key)})
(OUT/'supplementary_anomaly_samples.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in anomalies))
(OUT/'unpaired_publication_samples.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in unpaired))
save_rates_path=OUT/'late_author_participation.csv'
with save_rates_path.open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(class_rates[0]));w.writeheader();w.writerows(class_rates)
dump('mechanism_trace.json',{'first_differences':first_differences,'critical_contexts':[{'reason':reason,'new':sample_side(arms[('new','interest',0)],key),'old':sample_side(arms[('old','interest',0)],key)} for reason,key in [('first_post_tendency',('57','2026-W12')),('first_feed_utility',('80','2026-W13')),('first_posting',('90','2026-W13'))]],'causal_scope':'Observed sequence plus executed source mechanism; no intervention replay, so first tendency example is an earliest carrier of change, not uniquely attributed cause of downstream differences.'})

# 三制度差值方向。
contrasts=[]
for high,low in [('interest','random'),('interest','chronological'),('chronological','random')]:
 for m in macro[('new',high,0)]:
  if m in ['seed'] or not isinstance(macro[('new',high,0)][m],(int,float)):continue
  od=macro[('old',high,0)][m]-macro[('old',low,0)][m];nd=macro[('new',high,0)][m]-macro[('new',low,0)][m]
  contrasts.append({'contrast':high+'-'+low,'metric':m,'old_s0':od,'new':nd,'change':nd-od,'strict_sign_reversal':od*nd<0})
def savecsv(name,rows):
 with (OUT/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
savecsv('weekly_metrics.csv',weekly);savecsv('paired_metric_differences.csv',comparisons);savecsv('institution_contrasts.csv',contrasts)
dump('metrics_summary.json',{'summaries':summaries,'definitions':{'type':'Fixed author profile agent_type; environment post pool_type/type is fixed to author type, not semantic text classification.','participation':'posted author actions / frozen author type population per week; late four-week rate / (19*4).','supply':'agent_supply_* is current-week successful posts, not all living pool posts; pooled next week.','exposure':'environment actual read feed type label counts; denominator all exposure slots incl noise (1000/week).','late':'W19-W22 pooled numerators/denominators, not unweighted averages of weekly supply shares.'}})
dump('quality_summary.json',quality);dump('integrity.json',integrity);dump('first_differences.json',first_differences);dump('agent_decision_differences.json',decision_diffs);dump('feed_key_differences.json',feed_diffs)
for f in [*sorted((RUN/'workspace/custom').rglob('curation*.py')), *sorted((RUN/'model-comparison-init').rglob('*.yaml')), RUN/'model-comparison-init/manifest.json',RUN/'model-comparison-execution.json',RUN/'model-comparison-analysis-plan.md',*sorted((RUN/'model-comparison-init').rglob('*.json'))]:
 sources.append({'role':'frozen_input_or_plan','path':str(f.relative_to(ROOT)),'sha256':sha(f),'bytes':f.stat().st_size})
dump('source_index.json',{'script':str(Path(__file__).relative_to(ROOT)),'script_sha256':sha(Path(__file__)),'recompute_command':'/Users/easylife/Project/AgentSociety/AgentSociety2/.venv/bin/python '+str(Path(__file__).relative_to(ROOT)),'reader':'agentsociety2.storage.ReplayReader.fetch_dataset_rows(curation_dynamics.env_state), plus frozen AGENT.json and ENV_STATE.json','sources':sources})
print('WEEKLY',len(weekly),'INTEGRITY',len(integrity),'DONE',flush=True)
print(json.dumps([x for x in summaries if x['version']=='new' or x['seed']==0],ensure_ascii=False,indent=2))
print(json.dumps({k:{x:v for x,v in z.items() if x.endswith('count')} for k,z in first_differences.items()},indent=2))
