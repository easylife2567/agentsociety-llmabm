"""timestamp无LLM验证：原轨迹重放、拒答库存诊断及测量周界核对。

复用正式环境与效用函数，只使用已存正文；不修改原始run或调用模型。
固定供给与有限正文支持的闭环分支分别登记，不能冒充新生成实验。
"""
import asyncio
import csv
import hashlib
import importlib.util
import json
import os
import socket
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
CONFIG = ROOT/'hypothesis_4/experiment_1/init/arrival_timing_diagnostic'
TYPES = ('meme', 'mourning', 'education', 'marketing', 'other', 'noise')
LATE = {f'2026-W{w}' for w in range(19, 23)}
NETWORK_ATTEMPTS = []
# 依赖库支持原生离线价格表，避免导入时发起远程配置请求。
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'


def no_network(*args, **kwargs):
    """离线验证期间任何连接尝试都终止，防止误走模型/远程路由。"""
    NETWORK_ATTEMPTS.append('blocked')
    raise RuntimeError('numerical check forbids network connections')


socket.socket.connect = no_network
socket.socket.connect_ex = no_network


def read(path):
    return json.loads(Path(path).read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


ENV = module('numeric_environment', ROOT/'custom/envs/curation_dynamics_space.py')
AGENT = module('numeric_agent', ROOT/'custom/agents/curation_discourse_agent.py')
ACTION = module('numeric_action', ROOT/'custom/agents/curation_arrival_action.py')
TAGGER = module('numeric_tagger', ROOT/'custom/envs/curation_assets/build_assets.py').Tagger(
    read(ROOT/'custom/envs/curation_assets/vocabs.json'))


def numeric_agent(profile):
    """仅为纯效用函数提供冻结参数，不构造带服务的Agent实例。"""
    return SimpleNamespace(_agent_type=profile['agent_type'], _params=profile['params'])


def utility(profile, snap):
    return AGENT.CurationDiscourseAgent._speak_stimulus(numeric_agent(profile), snap)


def keys(feed):
    return [p['stable_key'] for p in feed]


def snap_from_action(action):
    counts = Counter(p['type'] for p in action['feed'])
    n = len(action['feed'])
    return {'feed': action['feed'], 'event_signal': {}, 'meme_env': {},
            'feed_type_distribution': {k: counts[k]/n if n else 0. for k in TYPES},
            'personal_stats': {'cumulative_exposures': action['cumulative_before']}}


def load_run(algorithm):
    cfg = read(CONFIG/f'arrival_timing_diagnostic_timestamp_{algorithm}_s0.json')
    directory = ROOT/f'hypothesis_4/experiment_1/runs/arrival_timing_diagnostic/arrival_timing_diagnostic_timestamp_{algorithm}_s0'
    state_file = directory/'env/CurationDynamicsSpace/state/ENV_STATE.json'
    state = read(state_file)
    agents, decisions = {}, {}
    files = sorted((directory/'agents').glob('*/AGENT.json'))
    for file in files:
        doc = read(file)
        aid = str(doc['id'])
        agents[aid] = doc['profile']
        for row in doc['decision_log']:
            decisions[aid, row['week']] = row
    actions = {(a['agent_id'], a['week']): a for a in state['_arrival_state']['actions']}
    assert len(agents) == 100 and len(actions) == len(decisions) == 1100
    return cfg, state, agents, decisions, actions, [state_file, *files]


def fixed_snapshot_check(agents, decisions, actions):
    """从原始整数槽位复算，不使用日志里已舍入的份额或U分量。"""
    errors = []
    for pair, action in actions.items():
        profile = agents[pair[0]]
        u, _ = utility(profile, snap_from_action(action))
        old = decisions[pair]
        errors.append(abs(u-old['u']))
        assert abs(u-old['u']) <= 1e-12, pair
        assert (u >= profile['params']['activity']) == old['speak'], pair
        assert old['speak'] == old['posted'], pair
    return {'actions': len(errors), 'max_u_error': max(errors), 'decision_mismatches': 0}


async def replay(algorithm, cfg, agents, decisions, actions, mode):
    """基线按原正文重放；屏蔽分支不生成未知正文或伪装完整反事实。"""
    env = ENV.CurationDynamicsSpace(**cfg['env_modules'][0]['kwargs'])
    hours = sorted(set(env._chronological_action_hours.values()))
    times = [datetime(2026, 3, 16)+timedelta(weeks=w, hours=h) for w in range(11) for h in hours]
    await env.init(times[0])
    records, refusals, boundary = [], 0, None
    max_error = 0.
    refusal_pair = ('79', '2026-W16') if algorithm == 'interest' and mode != 'baseline' else None
    for index, t in enumerate(times):
        batch = []
        # 全批先验收再提交；若遇支持边界，该批任何帖子都不提交。
        for aid in sorted(env._chronological_active_agents):
            week = env._current_week
            pair = aid, week
            old, source = decisions[pair], actions[pair]
            snap = await env.get_feed(aid)
            actual = env._arrival.state['snapshots'][aid]
            u, comps = utility(agents[aid], snap)
            speak = u >= agents[aid]['params']['activity']
            max_error = max(max_error, abs(u-old['u']))
            # 原基线必须逐项复现，不能把代码/输入漂移当作拒答效应。
            if mode == 'baseline':
                assert keys(snap['feed']) == keys(source['feed']), (algorithm, pair, 'feed')
                assert actual['candidate_count'] == source['candidate_count'], pair
                assert actual['candidate_meme'] == source['candidate_meme'], pair
                assert actual['cumulative_before'] == source['cumulative_before'], pair
                assert abs(u-old['u']) <= 1e-12 and speak == old['speak'], pair
            feed_changed = keys(snap['feed'][:5]) != keys(source['feed'][:5])
            if mode == 'closed_support' and speak and pair != refusal_pair:
                if not old.get('posted') or feed_changed:
                    boundary = {'agent_id': aid, 'week': week, 'acted_at': snap['event_time'],
                                'reason': 'missing_original_body' if not old.get('posted') else 'changed_generation_context',
                                'original_speak': old['speak'], 'new_speak': speak,
                                'original_keys': keys(source['feed'][:5]), 'new_keys': keys(snap['feed'][:5]),
                                'original_u': old['u'], 'new_u': u, 'threshold': agents[aid]['params']['activity'],
                                'uncommitted_batch_size': len(env._chronological_active_agents)}
                    break
            for post in snap['feed']:
                assert post['published_at'] <= snap['event_time']
                assert post['source'] != 'agent' or post['week'] < week
            publish = old['posted'] if mode != 'closed_support' else speak
            if pair == refusal_pair:
                assert old['posted'] and '抱歉，这个我写不了' in old['content']
                publish = False
            batch.append((aid, pair, old, publish,
                          {'algorithm': algorithm, 'mode': mode, 'agent_id': aid, 'week': week,
                           'acted_at': snap['event_time'], 'type': agents[aid]['agent_type'],
                           'original_u': old['u'], 'recomputed_u': u, 'threshold': agents[aid]['params']['activity'],
                           'original_speak': old['speak'], 'recomputed_speak': speak,
                           'scheduled_publish': publish, 'generation_context_changed': feed_changed,
                           'candidate_count': actual['candidate_count'],
                           'own_share': comps['share_own_observed'], 'R': comps['decay']}))
        if boundary:
            break
        before_post_id = env._next_post_id
        for aid, pair, old, publish, record in batch:
            if pair == refusal_pair:
                refusals += 1
                # 在真实create_post之前屏蔽已确认的固定拒答，检查未分配ID。
            if publish:
                result = await env.create_post(aid, old['content'])
                assert result['status'] == 'success'
            records.append(record)
        if refusal_pair and any(pair == refusal_pair for _, pair, *_ in batch):
            assert env._next_post_id == before_post_id+sum(publish for _, _, _, publish, _ in batch)
            assert not any(p['agent_id'] == '79' and p['week'] == '2026-W16' for p in env._pending_agent_posts)
        nxt = times[index+1] if index+1 < len(times) else datetime(2026, 6, 1)
        await env.step(int((nxt-t).total_seconds()), t)
    committed = env._arrival.state['actions']
    # 曝光应照常累计，拒答不能撤销本人的阅读。
    expected = {aid: Counter() for aid in agents}
    for a in committed:
        expected[a['agent_id']].update(p['type'] for p in a['feed'])
    for aid in agents:
        assert all(expected[aid][k] == env._cumulative_exposures.get(aid, {}).get(k, 0) for k in TYPES)
    ledger = list(env._posts.values())+env._arrival.state['delayed']
    if refusal_pair:
        assert not any(p.get('stable_key') == 'agent:79:2026-W16' for p in ledger)
    if boundary is None:
        assert len(committed) == len(records) == 1100 and len(env._arrival.state['weeks']) == 11
    late_actions = [a for a in committed if a['week'] in LATE]
    result = {'complete': boundary is None, 'committed_batches': env._chronological_batch_index,
              'actions': len(records), 'completed_weeks': len(env._arrival.state['weeks']),
              'published': sum(r['scheduled_publish'] for r in records), 'blocked_known_refusals': refusals,
              'decision_changes': sum(r['original_speak'] != r['recomputed_speak'] for r in records),
              'context_changes': sum(r['generation_context_changed'] for r in records),
              'max_u_difference': max_error, 'late_opportunities': len(late_actions),
              'late_meme_exposures': sum(p['type'] == 'meme' for a in late_actions for p in a['feed']),
              'boundary': boundary}
    return result, records


def measurement():
    """复用只读矩阵，量化周界影响，不计算不同分类程序的虚假拟合。"""
    audit = read(TASK/'2026-10-03-02-measurement-audit.json')
    rows = []
    for w in [f'2026-W{x}' for x in range(12, 23)]:
        utc, local = audit['real_utc'][w], audit['real_shanghai'][w]
        for category in utc:
            if category == '爬取噪音':
                continue
            a, b = sum(utc.values())-utc['爬取噪音'], sum(local.values())-local['爬取噪音']
            rows.append({'week': w, 'category': category, 'utc_count': utc[category],
                         'shanghai_count': local[category], 'utc_clean_share': utc[category]/a,
                         'shanghai_clean_share': local[category]/b,
                         'shift_pp': 100*(local[category]/b-utc[category]/a)})
    largest = max(rows, key=lambda r: abs(r['shift_pp']))
    meme = max((r for r in rows if r['category'] == '梗文化讨论'), key=lambda r: abs(r['shift_pp']))
    return {'largest_share_shift': largest, 'largest_meme_shift': meme}, rows


def date_input_check(decisions, agents):
    """任务内输入示例：只验证元数据和原正文预算，不替代正式模板修复。"""
    total, missing, source_slots = 0, 0, 0
    for (aid, _), row in decisions.items():
        if not row['posted']:
            continue
        context = row['prompt_context']
        total += 1
        missing += '发布时间' not in row['messages'][1]['content']
        # 原始实际messages保持不动，示例只添加已有时间，不生成新正文。
        lines = [f"[{p['stable_key']} 发布时间={p['published_at']}] @{p['author']}：{p['text']}" for p in context]
        proposal = f"当前模拟时间={row['acted_at']}\n"+'\n'.join(lines)
        assert len(context) <= 5 and all(len(p['text']) <= 120 for p in context)
        assert all(p['published_at'] in proposal and p['text'] in proposal for p in context)
        source_slots += len(context)
    return {'generated_contexts': total, 'missing_source_time_field': missing,
            'prototype_contexts_checked': total, 'prototype_source_slots': source_slots,
            'generation_quality_validated': False}


def write_csv(name, rows):
    with (OUT/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary, rows, hashes = {}, [], {}
    source_names = ['custom/agents/curation_discourse_agent.py', 'custom/agents/curation_arrival_action.py',
                    'custom/envs/curation_dynamics_space.py', 'custom/envs/curation_arrival_schedule.py',
                    'custom/envs/curation_mechanisms.py', 'custom/envs/curation_assets/build_assets.py',
                    str(Path(__file__).relative_to(ROOT)),
                    str((TASK/'2026-10-03-02-measurement-audit.json').relative_to(ROOT))]
    for name in source_names:
        hashes[name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    for algorithm in ('interest', 'random'):
        cfg, state, agents, decisions, actions, files = load_run(algorithm)
        # 在计算前锁定正式配置、输入和原始账本。
        files += [CONFIG/f'arrival_timing_diagnostic_timestamp_{algorithm}_s0.json']
        files += [ROOT/cfg['env_modules'][0]['kwargs'][k] for k in ('injection_data_path', 'weekly_initial_injection_data_path', 'vocab_path')]
        for file in files:
            hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
        summary[algorithm] = {'fixed_snapshots': fixed_snapshot_check(agents, decisions, actions),
                              'date_inputs': date_input_check(decisions, agents)}
        for name in ('baseline', 'fixed_supply_screen', 'closed_support'):
            result, recs = await replay(algorithm, cfg, agents, decisions, actions, name)
            summary[algorithm][name] = result
            rows.extend(recs)
            print(algorithm, name, json.dumps(result, ensure_ascii=False))
    measures, measure_rows = measurement()
    summary['measurement'] = measures
    summary['network_attempts'] = len(NETWORK_ATTEMPTS)
    summary['model_calls'] = 0
    assert not NETWORK_ATTEMPTS
    for name, digest in hashes.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    summary['input_sha256'] = hashes
    write_csv('2026-10-06-01-numerical-decisions.csv', rows)
    write_csv('2026-10-06-02-week-boundary.csv', measure_rows)
    (OUT/'2026-10-06-03-numerical-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print('输出：', OUT)


if __name__ == '__main__':
    asyncio.run(main())
