"""U的冻结离线检验；复用原闭环、禁止网络和LLM，候选不改正式代码。"""
from calibration_experiments import *
import math
import random
import sys
import numpy as np

# 原规则之外的条件预先固定；最后三项只检查兴趣臂。
CONDITIONS = {
 'hard_warm': dict(eps=0, init='warm'),
 'soft_publish': dict(eps=.02, init='publish'),
 'soft_warm': dict(eps=.02, init='warm'),
 'soft_cold': dict(eps=.02, init='cold'),
 'eps01': dict(eps=.01, init='warm'),
 'eps04': dict(eps=.04, init='warm'),
 'threshold090': dict(eps=.02, init='warm', threshold=.90),
 'threshold100': dict(eps=.02, init='warm', threshold=1.),
 'alternate_D': dict(eps=.02, init='warm', function='D'),
 'alternate_R': dict(eps=.02, init='warm', function='R'),
 'no_feedback': dict(eps=.02, init='warm', feedback=False),
 'old_U': dict(eps=.02, init='warm', function='old'),
 'no_D': dict(eps=.02, init='warm', function='no_D'),
 'no_R': dict(eps=.02, init='warm', function='no_R'),
}

def probability(b, a, eps):
    return max(0., min(1., .5 + (b-a)/(2*eps)))

def continuous_anchor(acts, target, eps):
    lo, hi = min(acts)-eps, max(acts)+eps
    for _ in range(100):
        mid=(lo+hi)/2
        if sum(probability(mid,a,eps) for a in acts) < target:
            lo=mid
        else:
            hi=mid
    b=(lo+hi)/2
    assert abs(sum(probability(b,a,eps) for a in acts)-target) < 1e-10
    return b

def prepare_profiles(cfg, parent, condition):
    opts=CONDITIONS.get(condition, dict(eps=0, init='publish'))
    profiles={str(a['agent_id']):copy.deepcopy(a['kwargs']) for a in cfg['agents']}
    current={r['type']:r for r in read(parent/'baseline_evidence.json')['scale_anchors'] if r['scale_name']=='current'}
    targets={typ:r['expected'] for typ,r in current.items()}
    for p in profiles.values():
        p['params']['baseline_utility']=current[p['agent_type']]['B']
        p['params']['activity'] *= opts.get('threshold',.95)/.95
    if opts['eps']:
        for typ in TYPES:
            acts=[p['params']['activity'] for p in profiles.values() if p['agent_type']==typ]
            b=continuous_anchor(acts,targets[typ],opts['eps'])
            for p in profiles.values():
                if p['agent_type']==typ:
                    p['params']['baseline_utility']=b
    return profiles,opts

def stimulus(agent_module,p,snap,kind):
    holder=SimpleNamespace(_agent_type=p['agent_type'],_params=p['params'])
    u,comps=agent_module.CurationDiscourseAgent._speak_stimulus(holder,snap)
    if not kind:
        return u,comps
    prm=p['params']; own=p['agent_type']
    share=float(snap['feed_type_distribution'].get(own,0))
    share,_,_=agent_module._event_adjusted_share(share,len(snap['feed']),snap.get('event_signal') or {},own)
    base=agent_module._POP_SHARE[own]
    d=agent_module.mech.spiral_factor(share,base,prm['spiral']*prm['spiral_scale'])
    c=float(snap['personal_stats']['cumulative_exposures'].get(own,0))
    rr=agent_module.mech.fatigue_factor(prm['decay'],c)
    if kind=='D':
        x=1.5*(share-base)/max(base,.05)
        d=1+prm['spiral']*prm['spiral_scale']*(2/math.pi)*math.atan(math.pi*x/2)
    elif kind=='R':
        rr=1/(1+prm['decay']*c/(15*math.log(2)))
    elif kind=='no_D': d=1.
    elif kind=='no_R': rr=1.
    u=d*rr if kind=='old' else agent_module.mech.anchored_utility(prm['baseline_utility'],d,rr)
    comps={**comps,'D_full':d,'R_full':rr,'U_full':u,'function':kind}
    return u,comps

def paired_noise(seed,week,aid,eps):
    key=f'{seed}|{week}|{aid}|decision_noise'
    return random.Random(int.from_bytes(hashlib.sha256(key.encode()).digest(),'big')).uniform(-eps,eps) if eps else 0.

async def cell(root, out, env_module, agent_module, condition, arm, seed):
    parent = out.parent
    frozen = parent / 'frozen'
    cfg = read(frozen / f'hypothesis_4/experiment_2/init/configs/timestamp_v1_{arm}_s{seed}.json')
    kwargs = copy.deepcopy(cfg['env_modules'][0]['kwargs'])
    for key in ('injection_data_path', 'weekly_initial_injection_data_path', 'vocab_path'):
        kwargs[key] = str(frozen / kwargs[key])
    profiles,opts = prepare_profiles(cfg,parent,condition)
    env = env_module.CurationDynamicsSpace(**kwargs)
    hours = set(kwargs['chronological_action_hours'].values())
    for overrides in kwargs.get('chronological_action_hour_overrides', {}).values():
        hours.update(overrides.values())
    weeks = WEEKS[1:] if opts['init']=='cold' else WEEKS
    start_date = datetime(2026,3,23) if opts['init']=='cold' else datetime(2026,3,16)
    moments = [start_date + timedelta(weeks=w,hours=h) for w in range(len(weeks)) for h in sorted(hours)]
    env._chronological_total_batches=len(moments)
    excluded=[]
    if opts.get('feedback',True) is False:
        original_candidates=env._arrival.candidates
        def external_candidates():
            ids=original_candidates()
            removed=[pid for pid in ids if env._posts[pid]['source']=='agent']
            excluded.extend(removed)
            return [pid for pid in ids if pid not in set(removed)]
        env._arrival.candidates=external_candidates
    assert len(moments) == env._chronological_total_batches
    bodies = read(kwargs['injection_data_path'])['posts'] + read(kwargs['weekly_initial_injection_data_path'])['posts']
    bodies = sorted(bodies, key=lambda p: str(p['pid']))
    await env.init(moments[0])
    actions = []
    fallback_count = 0
    for index, moment in enumerate(moments):
        candidates = env._arrival.candidates()
        pool_types = Counter(env._posts[pid]['type'] for pid in candidates)
        batch = []
        for aid in sorted(env._chronological_active_agents):
            snap = await env.get_feed(aid)
            p = profiles[aid]
            u,comps=stimulus(agent_module,p,snap,opts.get('function'))
            warmup=opts['init']=='warm' and env._current_week=='2026-W12'
            noise=paired_noise(seed,env._current_week,aid,opts['eps'])
            speak=not warmup and bool(snap['feed']) and u+noise>=p['params']['activity']
            original = env._arrival.state['snapshots'][aid]
            assert original['candidate_future'] == 0
            assert all(local(post['available_at']) <= moment for post in snap['feed'])
            assert all(post['stable_key'] != f'agent:{aid}:{env._current_week}' for post in snap['feed'])
            available = [body for body in bodies if body['type'] == p['agent_type'] and not body.get('is_official')
                         and body.get('published_at') and local(body['published_at']) <= moment]
            key = f"{aid}|{env._current_week}"
            if available:
                body = available[int.from_bytes(hashlib.sha256(key.encode()).digest(), 'big') % len(available)]
                content, body_id = body['content'], str(body['pid'])
            else:
                content, body_id = FALLBACK[p['agent_type']], 'fallback:' + p['agent_type']
            fallback_count += int(speak and not available)
            record = {'agent_id': aid, 'type': p['agent_type'], 'week': env._current_week, 'acted_at': snap['event_time'],
                      'B': p['params']['baseline_utility'], 'A': p['params']['activity'], 'u': u,
                      'noise':noise,'phase':'warmup' if warmup else 'decision','components_rounded': comps, 'cumulative_before': original['cumulative_before'],
                      'feed_keys': [x['stable_key'] for x in snap['feed']], 'feed_types': [x['type'] for x in snap['feed']],
                      'feed_sources': [x['source'] for x in snap['feed']], 'candidate_types': dict(pool_types),
                      'candidate_count': len(candidates), 'speak': speak, 'body_source': body_id if speak else None}
            actions.append(record)
            batch.append((aid, content, speak))
        # 同批所有决策依据已冻结feed；只有step提交后后续batch可见新帖。
        for aid, content, speak in batch:
            if speak:
                published = await env.create_post(aid, content)
                assert published['status'] == 'success' and not published.get('already_posted', False)
        next_moment = moments[index + 1] if index + 1 < len(moments) else datetime(2026, 6, 1)
        await env.step(int((next_moment - moment).total_seconds()), moment)
    assert len(actions) == len(env._arrival.state['actions']) == 100*len(weeks)
    assert len({(a['agent_id'], a['week']) for a in actions}) == 100*len(weeks)
    assert len(env._arrival.state['weeks']) == len(weeks)
    expected = {aid: Counter() for aid in profiles}
    for action in actions:
        expected[action['agent_id']].update(action['feed_types'])
    assert all(expected[aid][typ] == env._cumulative_exposures[aid].get(typ, 0) for aid in profiles for typ in ALL_TYPES)
    assert sum(a['speak'] for a in actions) == sum(env._total_posts_by_agent.values())
    rows = []
    for week in weeks:
        weekly_actions = [a for a in actions if a['week'] == week]
        supply = Counter(a['type'] for a in weekly_actions if a['speak'])
        exposure = Counter(t for a in weekly_actions for t in a['feed_types'])
        agent_exposure = Counter(t for a in weekly_actions for t, source in zip(a['feed_types'], a['feed_sources']) if source == 'agent')
        external = Counter(item[3]['type'] for item in env._arrival.events if env._week_for_time(item[1]) == week)
        total_slots, total_posts = sum(exposure.values()), sum(supply.values())
        for typ in TYPES:
            eligible_expected_slots = sum(len(a['feed_types']) * a['candidate_types'].get(typ, 0) / a['candidate_count']
                                          for a in weekly_actions if a['candidate_count'])
            real = next(r['posts_utc'] for r in read(frozen / 'observations.json')['rows'] if r['week'] == week and r['type'] == typ)
            rows.append({'condition':condition, 'arm': arm, 'seed': seed, 'week': week, 'type': typ,
                         'agent_posts': supply[typ], 'agent_supply_share': supply[typ] / total_posts if total_posts else None,
                         'agent_opportunities': sum(a['phase']=='decision' and a['type']==typ for a in weekly_actions), 'speaking_rate': supply[typ] / COUNTS[typ],
                         'total_agent_posts': total_posts, 'external_posts': external[typ],
                         'feed_exposures': exposure[typ], 'feed_slots': total_slots,
                         'exposure_share': exposure[typ] / total_slots if total_slots else None,
                         'agent_post_exposures': agent_exposure[typ], 'eligible_pool_share': eligible_expected_slots / total_slots if total_slots else None,
                         'exposure_pool_gap': (exposure[typ] - eligible_expected_slots) / total_slots if total_slots else None,
                         'real_expected_fixed_c': real * read(parent / 'experiment_manifest.json')['scales']['current'],
                         'absolute_residual_fixed_c': supply[typ] - real * read(parent / 'experiment_manifest.json')['scales']['current']})
    name = f'{condition}_{arm}_s{seed}'
    audit_path = out / 'action_audits' / f'{name}.jsonl.gz'
    with gzip.open(audit_path, 'wt', encoding='utf-8') as f:
        for a in actions:
            f.write(json.dumps(a, ensure_ascii=False, separators=(',', ':')) + '\n')
    write(out / 'cell_metrics' / f'{name}.json', {'identity': name, 'weekly': rows, 'checks': {
        'actions': len(actions), 'weeks':len(weeks), 'post_opportunities':sum(a['phase']=='decision' for a in actions), 'feedback_exclusion_calls_total':len(excluded), 'future_exposures': 0, 'cumulative_verified': True,
        'fallback_posts': fallback_count, 'published': sum(a['speak'] for a in actions),
        'network_attempts': len(NETWORK)}, 'audit_sha256': sha(audit_path)})
    if opts.get('feedback',True) is False:
        assert all(source!='agent' for a in actions for source in a['feed_sources'])
    return rows


def audit_read(path):
    with gzip.open(path,'rt') as f:
        return list(map(json.loads,f))

def static_check(parent,out):
    cfg=read(parent/'frozen/hypothesis_4/experiment_2/init/configs/timestamp_v1_random_s0.json')
    targets={r['type']:r['expected'] for r in read(parent/'baseline_evidence.json')['scale_anchors'] if r['scale_name']=='current'}
    rows=[]
    for condition in ('baseline','soft_warm','eps01','eps04','threshold090','threshold100'):
        profiles,opts=prepare_profiles(cfg,parent,condition)
        for ti,typ in enumerate(TYPES):
            ps=[p['params'] for p in profiles.values() if p['agent_type']==typ]
            a=np.array([p['activity'] for p in ps]); b=ps[0]['baseline_utility']; eps=opts['eps']
            probabilities=np.array([probability(b,x,eps) for x in a]) if eps else (b>=a).astype(float)
            rng=np.random.default_rng(710+ti)
            counts=np.zeros(100000,dtype=np.int16)
            for i in range(0,len(counts),2000):
                noise=rng.uniform(-eps,eps,size=(2000,len(a))) if eps else np.zeros((2000,len(a)))
                counts[i:i+2000]=(b+noise>=a).sum(axis=1)
            exact=float(probabilities.sum()); se=math.sqrt(float((probabilities*(1-probabilities)).sum())/100000)
            assert abs(float(counts.mean())-exact)<=6*se+1e-10
            rows.append(dict(condition=condition,type=typ,epsilon=eps,B=b,target=targets[typ],exact_expected=exact,simulated_mean=float(counts.mean()),standard_error=se,trials=100000,nonzero_agents=int((probabilities>0).sum()),residual=exact-targets[typ]))
    csv_write(out/'static_mapping.csv',rows)
    write(out/'static_mapping.json',rows)

async def run(root,parent,out):
    frozen_manifest=read(parent/'experiment_manifest.json')
    assert all(sha(root/p)==h for p,h in frozen_manifest['code_sha256'].items())
    assert all(sha(parent/'frozen'/p)==h for p,h in frozen_manifest['frozen_inputs_sha256'].items())
    assert sha(parent/'frozen/observations.json')==frozen_manifest['aggregate_sha256']
    assert not out.exists(),'Use a fresh output directory; never overwrite original evidence'
    out.mkdir();(out/'action_audits').mkdir();(out/'cell_metrics').mkdir()
    write(out/'manifest.json',dict(baseline=frozen_manifest['baseline_commit'],script_sha256=sha(__file__),helper_sha256=sha(parent/'calibration_experiments.py'),protocol_sha256=sha(parent/'u_protocol.md'),parent_manifest_sha256=sha(parent/'experiment_manifest.json'),conditions=CONDITIONS,new_cells=108,verification_cells=3,seeds=[0,1,2],max_seconds=1800,model_calls=0))
    static_check(parent,out)
    env=module('u_environment',root/'custom/envs/curation_dynamics_space.py')
    agent=module('u_agent',root/'custom/agents/curation_discourse_agent.py')
    start=time.monotonic();checks=[];rows=[]
    for arm in ARMS:
        current=await cell(root,out,env,agent,'baseline',arm,0)
        old=audit_read(parent/f'action_audits/current_{arm}_s0.jsonl.gz')
        new=audit_read(out/f'action_audits/baseline_{arm}_s0.jsonl.gz')
        assert len(old)==len(new)==1100
        assert all(all(a[k]==b[k] for k in a) for a,b in zip(old,new)),arm
        checks.append(dict(arm=arm,actions=1100,all_original_fields_identical=True))
    for condition,opts in CONDITIONS.items():
        for seed in range(3):
            for arm in (('interest',) if condition in ('old_U','no_D','no_R') else ARMS):
                if time.monotonic()-start>1800: raise TimeoutError('Frozen runtime budget reached')
                current=await cell(root,out,env,agent,condition,arm,seed)
                rows.extend(current)
                print(json.dumps(dict(condition=condition,arm=arm,seed=seed,cells=len(list((out/'cell_metrics').glob('*.json')))-3,elapsed=round(time.monotonic()-start,2))),flush=True)
    oldrows=read(parent/'feedback_evidence.json')['weekly']
    rows.extend({**r,'condition':'baseline'} for r in oldrows if r['scale_name']=='current')
    for row in rows: row.pop('scale_name',None)
    csv_write(out/'weekly_metrics.csv',rows)
    assert len(list((out/'cell_metrics').glob('*.json')))==111
    assert not NETWORK
    write(out/'completion.json',dict(complete=True,new_cells=108,baseline_verification=checks,model_calls=0,network_attempts=len(NETWORK),elapsed_seconds=time.monotonic()-start,code_sha256=frozen_manifest['code_sha256'],inputs_sha256=frozen_manifest['frozen_inputs_sha256'],opportunities=sum(read(p)['checks']['post_opportunities'] for p in (out/'cell_metrics').glob('*.json') if not p.name.startswith('baseline_'))))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--project-root',type=Path,required=True);ap.add_argument('--run-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert args.output.resolve().parent==args.run_dir.resolve()
    asyncio.run(run(args.project_root.resolve(),args.run_dir.resolve(),args.output.resolve()))
