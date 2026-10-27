"""只读12次完成实验，按冻结口径提取/配对；官方CLI读取replay，Agent和环境记录独立复核。"""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import copy,hashlib,json,os,subprocess,sys
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
RUN=BASE
ROOT=BASE.parents[1]
WORKSPACE=ROOT
OUT=ROOT/'presentation/hypothesis_4/timestamp_bdr_v1/data'
TYPES=['meme','mourning','education','marketing','other']
CONDS=['full','no_b','no_d','no_r']
WEEKS=[f'2026-W{x}' for x in range(12,23)]
LATE=WEEKS[7:];MID=WEEKS[2:7]
POP={'meme':19,'mourning':22,'education':15,'marketing':23,'other':21}
AGSPY=ROOT/'.agentsociety/bin/ags.py'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csv(name,rows):
    df=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(OUT/name,index=False,encoding='utf-8-sig',float_format='%.12g')
    return df

def normalized(doc,root):
    doc=copy.deepcopy(doc)
    for e in doc['env_modules']:
        for key,value in e['kwargs'].items():
            if key.endswith('_path'):
                p=root/value
                assert p.is_file(),(key,p)
                e['kwargs'][key]={'input_sha256':sha(p)}
    for a in doc['agents']:a['kwargs']['content_retry_budget']['ledger_path']='__shared_run_specific_ledger__'
    return doc

def query(run_id,path):
    fields=['week','agent_supply']+[f'agent_supply_{t}' for t in TYPES]
    queries={
        'weekly': 'SELECT '+', '.join(fields)+' FROM curation_dynamics_env_state ORDER BY week',
        'agent': 'SELECT step,agent_type,COUNT(*) AS opportunities,SUM(spoke) AS spoke FROM curation_dynamics_agent_state GROUP BY step,agent_type ORDER BY step,agent_type'
    }
    result={}
    for label,sql in queries.items():
        p=subprocess.run([sys.executable,str(AGSPY),'analysis','query-data','--data-path',str(path/'replay'),'--sql',sql],cwd=ROOT,capture_output=True,text=True,env=dict(os.environ,LITELLM_LOCAL_MODEL_COST_MAP='True'))
        assert p.returncode==0,(run_id,label,p.stderr[:1000],p.stdout[:1000])
        d=json.loads(p.stdout);assert d['success'],d
        result[label]=[dict(zip(d['columns'],row)) for row in d['rows']]
        save(OUT/f'replay_{run_id}_{label}.json',{'sql':sql,**d})
    return result

def main():
    assert os.environ.get('BDR_ANALYSIS_OFFLINE_GUARD')=='active','必须启用离线保护'
    manifest=read(WORKSPACE/'hypothesis_4/experiment_3/init/manifest.json')
    prior=read(BASE/'provenance/exploration_baseline.json')
    checks={}
    checks['main_frozen_33']=all(sha(ROOT/p)==item['expected'] for p,item in prior['runtime_plan_source_hash_checks'].items())
    checks['full_env_reference']=all(sha(ROOT/e['run_dir']/'env/CurationDynamicsSpace/state/ENV_STATE.json')==e['reference_state_sha256'] for e in prior['main_completed_runs'] if 'reference_state_sha256' in e)
    assert all(checks.values()),checks
    plan=read(BASE/'runs/timestamp_bdr_v1_attempt_02/runtime_plan.json')
    assert all(sha(WORKSPACE/p)==h for p,h in plan['source_sha256'].items())
    checks['ablation_frozen_40']=True
    tasks=[];sources=[];compat=[]
    for seed in range(3):
        fp=ROOT/f'hypothesis_4/experiment_2/init/configs/timestamp_v1_interest_s{seed}.json'
        full=read(fp);norm_full=normalized(full,ROOT)
        for cond in CONDS:
            if cond=='full':
                rid=f'timestamp_v1_interest_s{seed}';directory=ROOT/'hypothesis_4/experiment_2/runs/timestamp_v1'/rid;config=fp;config_root=ROOT
            else:
                rid=f'timestamp_bdr_v1_interest_{cond}_s{seed}';directory=BASE/'runs/timestamp_bdr_v1_attempt_02'/rid;config=WORKSPACE/'hypothesis_4/experiment_3/init/configs'/(rid+'.json');config_root=WORKSPACE
                variant=read(config);norm=normalized(variant,WORKSPACE);param={'no_b':'baseline_utility','no_d':'spiral_scale','no_r':'decay'}[cond]
                assert len(norm['agents'])==100
                for a,f in zip(norm['agents'],norm_full['agents']):
                    assert a['agent_id']==f['agent_id'] and a['kwargs']['params'][param]==0
                    a['kwargs']['params'][param]=f['kwargs']['params'][param]
                assert norm==norm_full,(rid,'normalized configuration mismatch')
                main_steps=ROOT/f'hypothesis_4/experiment_2/init/steps_s{seed}.yaml';new_steps=WORKSPACE/f'hypothesis_4/experiment_3/init/steps_s{seed}.yaml'
                assert sha(main_steps)==sha(new_steps)
                compat.append(dict(run_id=rid,paired_full=f'timestamp_v1_interest_s{seed}',normalized_other_scientific_parameters_equal=True,only_parameter=param,value=0.0,inputs_and_steps_sha256_match=True))
            tasks.append((cond,seed,rid,directory,config,config_root))
    with ThreadPoolExecutor(max_workers=4) as pool:
        replay=list(pool.map(lambda v:query(v[2],v[3]),tasks))
    decisions=[];weekly=[];exposures=[];summaries=[];examples=[]
    for task,rep in zip(tasks,replay):
        cond,seed,rid,directory,config,config_root=task
        pid=read(directory/'pid.json');clock=read(directory/'SOCIETY_STEP.json');assert pid['status']=='completed' and clock['completed_step_count']==693
        envpath=directory/'env/CurationDynamicsSpace/state/ENV_STATE.json';env=read(envpath);arrival=env['_arrival_state']
        assert len(arrival['actions'])==1100 and len(arrival['weeks'])==11
        amap={(str(a['agent_id']),a['week']):a for a in arrival['actions']};assert len(amap)==1100
        agent_files=sorted((directory/'agents').glob('*/AGENT.json'));assert len(agent_files)==100
        config_by_id={str(x['agent_id']):x['kwargs'] for x in read(config)['agents']}
        agent_source=[];allrows=[];type_counts=Counter();post_ids=[];response_models=Counter();reasons=Counter()
        for ap in agent_files:
            doc=read(ap);ah=sha(ap);aid=str(doc['id']);kind=doc['profile']['agent_type'];type_counts[kind]+=1
            assert doc['profile']==config_by_id[aid],(rid,aid,'runtime profile differs from configuration')
            assert len(doc['decision_log'])==11 and sorted(x['week'] for x in doc['decision_log'])==WEEKS
            agent_source.append(dict(path=str(ap),sha256=ah))
            for index,row in enumerate(doc['decision_log']):
                week=row['week'];action=amap[(aid,week)];feed=action['feed'];cs=row.get('components') or {};reasons[row['reason']]+=1
                assert action['agent_type']==kind and action['acted_at']==row['acted_at']
                assert action.get('candidate_future',0)==0
                assert all(datetime.fromisoformat(post['published_at'])<=datetime.fromisoformat(action['acted_at']) and datetime.fromisoformat(post['available_at'])<=datetime.fromisoformat(action['acted_at']) for post in feed)
                assert row['reason'] not in ('action_failed','publication_failed','generation_failed')
                assert not any(g.get('error_type') for g in row.get('generation_results',[]))
                assert bool(row['posted'])==(row.get('post_id') is not None)
                if feed:
                    assert row['speak']==(row['u']>=row['threshold'])
                else:assert row['reason']=='no_context' and not row['posted']
                if row['posted']:
                    assert row['speak'] is True;post_ids.append(row['post_id'])
                    # W22新帖已发布但尚未到次周推荐资格，保存在week_posts而非_posts。
                    post=env['_posts'].get(str(row['post_id'])) or next(z for z in arrival['week_posts'] if z['post_id']==row['post_id'])
                    assert post.get('source','agent')=='agent' and post['agent_id']==aid and post.get('type',post['pool_type'])==kind and post['content']==row['content']
                if cond=='no_b':assert cs.get('baseline_utility',0)==0
                if cond=='no_d' and cs:assert cs['spiral']==1
                if cond=='no_r' and cs:assert cs['decay']==1
                if row.get('response_model'):response_models[row['response_model']]+=1
                base=dict(condition=cond,seed=seed,run_id=rid,agent_id=int(aid),agent_type=kind,week=week)
                x={**base,'speak':int(row.get('speak') is True),'posted':int(row.get('posted') is True),'no_context':int(row['reason']=='no_context'),'reason':row['reason'],'provider_requests':row['generation_attempts'],'extra_requests':max(0,row['generation_attempts']-1),'rewrites':sum(g.get('purpose')=='rewrite' for g in row.get('generation_results',[])),'u':row.get('u'),'threshold':row.get('threshold'),'margin':row['u']-row['threshold'] if row.get('u') is not None else None,'B':cs.get('baseline_utility'),'D':cs.get('spiral'),'R':cs.get('decay'),'cum_own':cs.get('cum_own'),'share_own':cs.get('share_own'),'acted_at':row['acted_at'],'post_id':row.get('post_id'),'source_file':str(ap),'source_sha256':ah,'record_index':index,'assigned_type':post.get('assigned_type') if row['posted'] else None}
                decisions.append(x);allrows.append(x)
                counts=Counter(p['type'] for p in feed);agent_slots=sum(p['source']=='agent' for p in feed)
                exposures.append({**base,'feed_slots':len(feed),'meme_slots':counts['meme'],'mourning_slots':counts['mourning'],'agent_post_slots':agent_slots,'external_post_slots':sum(p['source']=='external' for p in feed),'cohort':'meme' if kind=='meme' else 'non_meme'})
                if row['posted']:examples.append({**base,'content':row['content'],'post_id':row['post_id'],'source_file':str(ap),'source_sha256':ah,'record_index':index,'assigned_type':post.get('assigned_type') if row['posted'] else None})
        assert type_counts==POP and len(post_ids)==len(set(post_ids))
        df=pd.DataFrame(allrows)
        for w,repw in zip(arrival['weeks'],rep['weekly']):
            assert w['week']==repw['week']
            for field in repw:assert w[field]==repw[field],(rid,field,w[field],repw[field])
            sub=df[df.week==w['week']];assert len(sub)==100
            for kind in TYPES:
                group=sub[sub.agent_type==kind];rep_agent=next(z for z in rep['agent'] if z['step']==WEEKS.index(w['week'])+1 and z['agent_type']==kind)
                assert int(group.posted.sum())==w['agent_supply_'+kind]
                assert int(group.speak.sum())==rep_agent['spoke'] and len(group)==rep_agent['opportunities']==POP[kind]
                weekly.append(dict(condition=cond,seed=seed,run_id=rid,week=w['week'],agent_type=kind,opportunities=len(group),speak=int(group.speak.sum()),posted=int(group.posted.sum()),no_context=int(group.no_context.sum()),provider_requests=int(group.provider_requests.sum()),extra_requests=int(group.extra_requests.sum()),B_mean=group.B.mean(),D_mean=group.D.mean(),R_mean=group.R.mean(),u_mean=group.u.mean(),margin_mean=group.margin.mean()))
        summaries.append(dict(condition=cond,seed=seed,run_id=rid,actions=len(df),posts=int(df.posted.sum()),speak=int(df.speak.sum()),requests=int(df.provider_requests.sum()),extra=int(df.extra_requests.sum()),no_context=int(df.no_context.sum()),zero_output_weeks=sum(int(df[df.week==w].posted.sum())==0 for w in WEEKS),response_models=dict(response_models),started_at=pid['start_time'],finished_at=pid.get('end_time'),reasons=dict(reasons)))
        replay_files=[directory/'replay/_schema.json',*sorted((directory/'replay').glob('*.jsonl'))]
        sources.append(dict(condition=cond,seed=seed,run_id=rid,root=str(directory),config_path=str(config),config_sha256=sha(config),env_path=str(envpath),env_sha256=sha(envpath),clock_sha256=sha(directory/'SOCIETY_STEP.json'),replay=[dict(path=str(p),sha256=sha(p)) for p in replay_files],agents=agent_source))
    dec=csv('decisions.csv',decisions);wk=csv('weekly_by_type.csv',weekly);ex=csv('exposure_by_opportunity.csv',exposures)
    exw=ex.groupby(['condition','seed','run_id','week','cohort'],as_index=False)[['feed_slots','meme_slots','mourning_slots','agent_post_slots','external_post_slots']].sum()
    exw['meme_label_share']=exw.meme_slots/exw.feed_slots.replace(0,np.nan);exw['agent_read_share']=exw.agent_post_slots/exw.feed_slots.replace(0,np.nan);csv('weekly_exposure_by_cohort.csv',exw)
    assigned=dec[dec.posted==1].groupby(['condition','seed','week','agent_type','assigned_type'],dropna=False).size().reset_index(name='posts');csv('vocab_label_counts.csv',assigned)
    totals=wk.groupby(['condition','seed','run_id','week'],as_index=False)[['opportunities','speak','posted','provider_requests','no_context']].sum();csv('weekly_totals.csv',totals)
    out=[]
    for v in summaries:
        cond,seed=v['condition'],v['seed'];d=dec[(dec.condition==cond)&(dec.seed==seed)];late=d[d.week.isin(LATE)];mid=d[d.week.isin(MID)];m=late[late.agent_type=='meme']
        x={k:v[k] for k in ('condition','seed','run_id','posts','speak','requests','extra','no_context','zero_output_weeks')}
        x.update(late_posts_per_week=late.posted.sum()/4,late_posts=int(late.posted.sum()),late_meme_speak_rate=m.speak.sum()/76,late_meme_post_rate=m.posted.sum()/76,late_meme_posts=int(m.posted.sum()),late_meme_author_share=m.posted.sum()/late.posted.sum() if late.posted.sum() else np.nan,mid_speak_rate=mid.speak.sum()/500,mid_post_rate=mid.posted.sum()/500)
        for kind in TYPES:
            x['late_posts_'+kind]=int(late[late.agent_type==kind].posted.sum());x['mid_speak_rate_'+kind]=mid[mid.agent_type==kind].speak.sum()/(POP[kind]*5)
        for week in ('2026-W13','2026-W18'):
            x['mourning_posts_'+week]=int(d[(d.week==week)&(d.agent_type=='mourning')].posted.sum())
        for cohort in ('meme','non_meme'):
            z=ex[(ex.condition==cond)&(ex.seed==seed)&ex.week.isin(LATE)&(ex.cohort==cohort)]
            x['late_meme_exposure_'+cohort]=z.meme_slots.sum()/z.feed_slots.sum() if z.feed_slots.sum() else np.nan
            x['late_agent_read_share_'+cohort]=z.agent_post_slots.sum()/z.feed_slots.sum() if z.feed_slots.sum() else np.nan
        out.append(x)
    met=csv('run_metrics.csv',out);pairs=[]
    fields=[k for k in met.columns if k not in ('condition','seed','run_id')]
    for cond in CONDS[1:]:
        for seed in range(3):
            full=met[(met.condition=='full')&(met.seed==seed)].iloc[0];ab=met[(met.condition==cond)&(met.seed==seed)].iloc[0]
            for metric in fields:pairs.append(dict(condition=cond,seed=seed,metric=metric,full=float(full[metric]),ablation=float(ab[metric]),delta=float(ab[metric]-full[metric])))
    paired=csv('paired_differences.csv',pairs)
    stats=paired.groupby(['condition','metric'],as_index=False).agg(full_mean=('full','mean'),ablation_mean=('ablation','mean'),delta_mean=('delta','mean'),delta_min=('delta','min'),delta_max=('delta','max'),n=('seed','size'))
    csv('paired_summary.csv',stats)
    save(OUT/'source_index.json',dict(checks=checks,comparability=compat,sources=sources,template=dict(source=str(ROOT/'hypothesis_4/experiment_1/plot_run_charts.py'),sha256=sha(ROOT/'hypothesis_4/experiment_1/plot_run_charts.py')),analysis_script_sha256=sha(Path(__file__)),model=plan['model'],network_guard='active',representative_replay_for_harness_only=None,actual_scope='12 runs listed above, 13200 opportunities, no new LLM calls'))
    save(OUT/'runtime_summary.json',summaries);save(OUT/'generated_examples_all.json',examples)
    save(BASE/'checks/extraction.json',dict(passed=True,runs=12,decisions=len(dec),weekly_type_rows=len(wk),weekly_total_rows=len(totals),replay_agent_and_environment_crosschecks=12,profile_and_unique_actions_checked=13200,template_max_weekly_posts=int(totals.posted.max()),model_calls_added=0,comparability='all nine scientific-normalized config comparisons passed; old Full hash baseline unchanged'))
    print(stats[((stats.condition=='no_b')&(stats.metric=='late_posts_per_week'))|((stats.condition=='no_d')&(stats.metric=='late_meme_speak_rate'))|((stats.condition=='no_r')&(stats.metric=='mid_speak_rate'))].to_string(index=False))

if __name__=='__main__':main()
