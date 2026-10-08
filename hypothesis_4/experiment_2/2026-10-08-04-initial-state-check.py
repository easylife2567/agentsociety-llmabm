"""核对官方帖覆盖与W11历史池的直接影响，不调用LLM或修改冻结配置。

真实归档只读；数值比较使用正式环境和Agent效用函数，比较保留17条历史与空历史。
两条件均不生成/回流Agent帖，因此只量化外部输入的直接通道，不预测闭环产量。
"""
import asyncio
import hashlib
import importlib.util
import json
import os
import socket
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
INIT = EXP / 'init'
NETWORK_ATTEMPTS = []


def block_network(*args, **kwargs):
    """离线核对包括模块导入阶段；任何连接均报错。"""
    NETWORK_ATTEMPTS.append('connection')
    raise RuntimeError('offline input check forbids network')


socket.socket.connect = block_network
socket.socket.connect_ex = block_network


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENV = load('checked_initial_env', ROOT/'custom/envs/curation_dynamics_space.py')
AGENT = load('checked_initial_agent', ROOT/'custom/agents/curation_discourse_agent.py')
OFFICIAL = datetime(2026, 3, 24, 20)


def read(path):
    return json.loads(path.read_text())


def summarized(rows):
    """数值feed和实际生成前五条分开；历史曝光用来源角色识别。"""
    slots = sum(r['feed_size'] for r in rows)
    history = sum(r['history_slots'] for r in rows)
    return {'action_count': len(rows), 'feed_slots': slots, 'history_slots': history,
            'history_fraction': history/slots if slots else None,
            'official_in_feed': sum(r['official_in_feed'] for r in rows),
            'official_in_prompt': sum(r['official_in_prompt'] for r in rows),
            'empty_feed_actions': sum(r['feed_size'] == 0 for r in rows),
            'numeric_speak_by_type': dict(Counter(r['agent_type'] for r in rows if r.get('would_speak'))) if any('would_speak' in r for r in rows) else None}


def observe(row):
    feed = row['feed']
    return {'agent_id': row['agent_id'], 'agent_type': row['agent_type'],
            'week': row['week'], 'acted_at': row['acted_at'],
            'before_official': datetime.fromisoformat(row['acted_at']).replace(tzinfo=None) < OFFICIAL,
            'feed_size': len(feed), 'history_slots': sum(p['injection_role'] == 'initial_history' for p in feed),
            'official_in_feed': any(p['is_official'] for p in feed),
            'official_in_prompt': any(p['is_official'] for p in feed[:5]),
            'candidate_count': row['candidate_count']}


async def proxy(algorithm, seed, history):
    """重放W12与W13的真实到达和曝光更新；开口判定不转成合成帖子。"""
    doc = read(INIT/f'configs/timestamp_v1_{algorithm}_s{seed}.json')
    kwargs = dict(doc['env_modules'][0]['kwargs'])
    if not history:
        kwargs['weekly_initial_injection_data_path'] = None
    env = ENV.CurationDynamicsSpace(**kwargs)
    profiles = {str(a['agent_id']): a['kwargs'] for a in doc['agents']}
    hours = sorted(set(env._chronological_action_hours.values()))
    moments = [datetime(2026, 3, 16)+timedelta(weeks=w, hours=h) for w in range(3) for h in hours]
    await env.init(moments[0])
    rows = []
    week_start = {}
    for i, moment in enumerate(moments[:126]):
        if env._current_week not in week_start:
            candidates = env._arrival.candidates()
            historical = sum(env._posts[p]['injection_role'] == 'initial_history' for p in candidates)
            week_start[env._current_week] = {'candidate_count': len(candidates), 'history_candidates': historical}
        for aid, snap in env._arrival.state['snapshots'].items():
            profile = profiles[aid]
            # 调用正式数值方法；不绑定服务、不创建Agent工作区。
            holder = SimpleNamespace(_agent_type=profile['agent_type'], _params=profile['params'])
            u, components = AGENT.CurationDiscourseAgent._speak_stimulus(holder, env._arrival.get_feed(aid))
            row = observe(snap)
            row.update(u=u, own_share=components['share_own_observed'], cum_own=components['cum_own'],
                       would_speak=bool(snap['feed']) and u >= profile['params']['activity'])
            rows.append(row)
        await env.step(int((moments[i+1]-moment).total_seconds()), moment)
    assert len(rows) == 200 and len(env._arrival.state['weeks']) == 2
    assert len({(r['week'],r['agent_id']) for r in rows}) == 200
    assert all(r['candidate_future'] == 0 for r in env._arrival.state['actions'])
    return {'algorithm': algorithm, 'seed': seed, 'history_count': 17 if history else 0,
            'week_start_pool': week_start,
            'weekly': {week: summarized([r for r in rows if r['week'] == week]) for week in ('2026-W12','2026-W13')},
            'w13_mourning': [r for r in rows if r['week'] == '2026-W13' and r['agent_type'] == 'mourning']}


async def main():
    manifest = read(INIT/'manifest.json')
    frozen = read(EXP/'2026-10-08-03-configuration-verification.json')['source_code_and_config_sha256']
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in frozen.items())
    archival = []
    sources = {}
    for algorithm in ('random','interest'):
        path = ROOT/f'hypothesis_4/experiment_1/runs/arrival_timing_diagnostic/arrival_timing_diagnostic_timestamp_{algorithm}_s0/env/CurationDynamicsSpace/state/ENV_STATE.json'
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        state = read(path)['_arrival_state']
        rows = [observe(r) for r in state['actions'] if r['week'] == '2026-W13']
        mourning = [r for r in rows if r['agent_type'] == 'mourning']
        archival.append({'algorithm':algorithm,'seed':0,'identity':'已完成单seed四格归档；不是experiment_2新结果',
                         'w13_all':summarized(rows),'w13_mourning_summary':summarized(mourning),
                         'w13_mourning':mourning})
    proxies = [await proxy(a,s,h) for s in range(3) for a in ('random','chronological','interest') for h in (True,False)]
    # 记录W11完整源池组成，区分现实结构与17条离散抽样的损失。
    full_path = ROOT/'custom/envs/curation_assets/injection_posts.json'
    full_w11 = [p for p in read(full_path)['posts'] if p['week'] == '2026-W11']
    sources[str(full_path.relative_to(ROOT))] = hashlib.sha256(full_path.read_bytes()).hexdigest()
    composition = {str(s):dict(Counter(p['type'] for p in read(INIT/f'inputs/initial_sample_weekly_lag_s{s}.json')['posts'])) for s in range(3)}
    result = {'scope':'事实核对与无Agent供给回流的外部池数值比较；不是LLM闭环实验，不预测新波峰',
              'model_calls':0,'network_connection_attempts':len(NETWORK_ATTEMPTS),'official_available_at':manifest['official_available_at'],
              'initial_composition_by_seed':composition,'full_w11_source':{'count':len(full_w11),'type_counts':dict(Counter(p['type'] for p in full_w11))},'archival':archival,'external_only_proxies':proxies,
              'source_sha256':{**frozen,**sources,str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    assert not NETWORK_ATTEMPTS
    (EXP/'2026-10-08-05-initial-state-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for a in archival:
        print(json.dumps({'archive_algorithm':a['algorithm'],'mourning_summary':a['w13_mourning_summary'],'early_mourning_ids':[r['agent_id'] for r in a['w13_mourning'] if r['before_official']],'all_history_fraction':a['w13_all']['history_fraction']},ensure_ascii=False))
    for p in proxies:
        print(json.dumps({'algorithm':p['algorithm'],'seed':p['seed'],'history':p['history_count'],'week_start':p['week_start_pool'],'w13':p['weekly']['2026-W13'],'w12_empty':p['weekly']['2026-W12']['empty_feed_actions']},ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
