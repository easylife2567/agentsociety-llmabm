"""只读复算四格诊断：主指标、周轨迹、来源、初始化和历史桥接。

输入由冻结manifest限定；不调用模型、不修改原始run。使用现有审计器与
Tagger，作者类型和正文词表标签分别计数，单seed只输出描述性对比。
"""
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TASK = Path(__file__).resolve().parent
OUT = ROOT / 'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
MANIFEST = ROOT / 'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/manifest.json'
LATE = {f'2026-W{w}' for w in range(19, 23)}


def read(path):
    return json.loads(Path(path).read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


AUDIT = module('arrival_audit', TASK / '2026-09-30-02-audit.py')
TAGGER = module('frozen_tagger', ROOT / 'custom/envs/curation_assets/build_assets.py').Tagger(
    read(ROOT / 'custom/envs/curation_assets/vocabs.json'))
MECH = module('frozen_mechanisms', ROOT / 'custom/envs/curation_mechanisms.py')


@lru_cache(maxsize=None)
def tag(text):
    """正文标签与作者类型独立；signal保留被判类优先级覆盖的玩梗命中。"""
    return TAGGER.tag(text)


def quantiles(values):
    return dict(zip(('min', 'q25', 'median', 'q75', 'max'),
                    map(float, np.quantile(values, [0, .25, .5, .75, 1]))))


def csv_write(name, rows):
    with (OUT / name).open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decisions(root):
    """保留原Agent身份，历史run也从相同账本读取作者口径。"""
    rows, profiles = [], {}
    for file in sorted((root / 'agents').glob('*/AGENT.json')):
        agent = read(file)
        aid = str(agent['id'])
        profiles[aid] = agent['profile']
        rows.extend(dict(d, agent_id=aid, agent_type=agent['profile']['agent_type'])
                    for d in agent['decision_log'])
    return rows, profiles


def production(rows):
    published = [d for d in rows if d.get('posted')]
    meme = sum(d['agent_type'] == 'meme' for d in published)
    return {'published': len(published), 'meme_author_posts': meme,
            'meme_author_share': meme / len(published) if published else None,
            'meme_author_participation': meme / sum(d['agent_type'] == 'meme' for d in rows)}


def summarize(actions, ds):
    result = AUDIT.metrics(actions)
    result.update(production(ds))
    published = [d for d in ds if d.get('posted')]
    result.update(semantic_meme_posts=sum(tag(d['content'])['type'] == 'meme' for d in published),
                  meme_signal_posts=sum(tag(d['content'])['is_meme_signal'] for d in published))
    result['semantic_meme_share'] = result['semantic_meme_posts'] / len(published) if published else None
    result['candidate_N'] = quantiles([a['candidate_count'] for a in actions])
    result['candidate_M'] = quantiles([a['candidate_meme'] for a in actions])
    result['candidate_meme_fraction'] = quantiles([a['candidate_meme'] / a['candidate_count'] if a['candidate_count'] else 0 for a in actions])
    result['short_feeds'] = sum(len(a['feed']) < 10 for a in actions)
    result['O_over_E'] = result['O'] / result['E'] if result['E'] else None
    result['meme_source_counts'] = dict(Counter(p['source'] for a in actions for p in a['feed'] if p['type'] == 'meme'))
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = read(MANIFEST)
    summary, weekly, future, sources, initial, historical, decision_rows = {}, [], [], [], [], [], []
    hashes = {}
    for run in manifest['runs']:
        key = run['arrival_mode'] + '-' + run['algorithm']
        root = ROOT / run['run_dir']
        audit = AUDIT.audit(root, run, expected_batches=693)
        assert not audit['failures'], audit['failures']
        state_file = root / 'env/CurationDynamicsSpace/state/ENV_STATE.json'
        env = read(state_file)
        state = env['_arrival_state']
        acts = state['actions']
        ds, profiles = decisions(root)
        summary[key] = {'audit': audit, 'full': summarize(acts, ds),
                        'late': summarize([a for a in acts if a['week'] in LATE], [d for d in ds if d['week'] in LATE])}
        # 独立核对周replay与最终环境快照，不仅相信监督器的成功状态。
        replay = [json.loads(line) for file in sorted((root / 'replay').glob('curation_dynamics_env_state.*.jsonl'))
                  for line in file.read_text().splitlines() if line.strip()]
        assert len(replay) == 11
        summary[key]['replay_columns'] = list(replay[0])
        for w in state['weeks']:
            week = w['week']
            aa = [a for a in acts if a['week'] == week]
            dd = [d for d in ds if d['week'] == week]
            m = summarize(aa, dd)
            assert w['agent_supply'] == m['published']
            assert w['exposure_meme'] == m['O']
            assert w['agent_supply_meme'] == m['meme_author_posts']
            # 原始replay为列名直接映射；周字段与账本逐项核对。
            rr = next(r for r in replay if r['week'] == week)
            assert rr['agent_supply'] == m['published'] and rr['exposure_meme'] == m['O']
            weekly.append(dict(condition=key, week=week, **{k:v for k,v in m.items() if not isinstance(v, dict)},
                mourning_posts=sum(d.get('posted') and d['agent_type'] == 'mourning' for d in dd),
                initial_exposure=sum(p.get('injection_role') == 'initial_history' for a in aa for p in a['feed']),
                lifecycle_excluded_mean=float(np.mean([a['lifecycle_excluded'] for a in aa])),
                candidate_N_min=m['candidate_N']['min'], candidate_N_median=m['candidate_N']['median'], candidate_N_max=m['candidate_N']['max']))
            # 类型×周提前曝光明确区分全部数值feed和实际已发出的生成上下文。
            generated = {(d['agent_id'], d['week']) for d in dd if d.get('generation_attempts', 0)}
            counts, advances, affected = Counter(), [], set()
            source_counts = Counter()
            for a in aa:
                t = datetime.fromisoformat(a['acted_at'])
                for index, p in enumerate(a['feed']):
                    category = 'initial' if p.get('injection_role') == 'initial_history' else 'official' if p['is_official'] else p['source']
                    route = 'pinned' if p['stable_key'] in a['pinned_keys'] else 'floor' if p['stable_key'] in a['floor_keys'] else 'sampled'
                    source_counts[category, route, p['type']] += 1
                    delay = (datetime.fromisoformat(p['published_at']) - t).total_seconds()
                    if delay > 0:
                        counts[p['type'], 'numeric'] += 1
                        if index < 5 and (a['agent_id'], week) in generated:
                            counts[p['type'], 'actual_prompt'] += 1
                        advances.append(delay)
                        affected.add(a['agent_id'])
            for kind in ('meme', 'mourning', 'education', 'marketing', 'other', 'noise'):
                future.append(dict(condition=key, week=week, type=kind, numeric_slots=counts[kind,'numeric'], actual_prompt_slots=counts[kind,'actual_prompt']))
            weekly[-1].update(future_slots=len(advances), future_actions=len(affected),
                future_mean_hours=float(np.mean(advances)/3600) if advances else None,
                future_max_hours=max(advances)/3600 if advances else None)
            sources.extend(dict(condition=key, week=week, source=c, route=r, type=t, slots=n) for (c,r,t),n in source_counts.items())
        # W13/W19第一批前的个人状态和供给，只作描述，不把中介当独立因果效应。
        posts = {p['stable_key']:p for p in env['_posts'].values()}
        posts.update({p['stable_key']:p for p in state['delayed']})
        external = [p for p in posts.values() if p['source'] == 'external']
        assert len(external) == len({p['stable_key'] for p in external}) == 267
        for week in ('2026-W13', '2026-W19'):
            start = state['week_start_states'][week]
            for aid, profile in profiles.items():
                own = start['cumulative_exposures'].get(aid, {}).get(profile['agent_type'], 0)
                initial.append(dict(condition=key, week=week, agent_id=aid, agent_type=profile['agent_type'],
                    cumulative_own=own, R=MECH.fatigue_factor(profile['params']['decay'], own),
                    prior_posts=start['agent_supply'].get(aid, 0),
                    candidates=len(start['candidate_keys']), candidate_meme=sum(posts[k]['type']=='meme' for k in start['candidate_keys'])))
        for d in ds:
            semantic = tag(d['content']) if d.get('posted') else {}
            decision_rows.append(dict(condition=key, agent_id=d['agent_id'], week=d['week'], type=d['agent_type'],
                posted=d.get('posted',False), post_id=d.get('post_id'), semantic_type=semantic.get('type'),
                meme_signal=semantic.get('is_meme_signal'), u=d.get('u'), R=(d.get('components') or {}).get('decay')))
        for file in [state_file, root/'SOCIETY_STEP.json', *sorted((root/'agents').glob('*/AGENT.json'))]:
            hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
    for rel in manifest['historical_references']:
        ds, _ = decisions(ROOT / rel)
        for file in sorted((ROOT / rel / 'agents').glob('*/AGENT.json')):
            hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
        for week in [f'2026-W{w}' for w in range(12,23)]:
            dd = [d for d in ds if d['week'] == week]
            assert len(dd) == 100
            historical.append(dict(run_id=Path(rel).name, week=week, **production(dd),
                mourning_posts=sum(d.get('posted') and d['agent_type']=='mourning' for d in dd)))
    contrasts = {}
    for metric in ('Y','S','A','meme_author_posts','meme_author_share','meme_author_participation','semantic_meme_posts','semantic_meme_share'):
        v = {k:s['late'][metric] for k,s in summary.items()}
        dp = v['preload-interest']-v['preload-random']
        dt = v['timestamp-interest']-v['timestamp-random']
        contrasts[metric] = dict(preload_gap=dp, timestamp_gap=dt, interaction=dt-dp,
            interest_arrival_effect=v['timestamp-interest']-v['preload-interest'], random_arrival_effect=v['timestamp-random']-v['preload-random'])
    for name, rows in [('weekly.csv',weekly), ('future.csv',future), ('sources.csv',sources),
                       ('initial.csv',initial), ('historical.csv',historical), ('decisions.csv',decision_rows)]:
        csv_write(name, rows)
    result = dict(runs=summary, contrasts=contrasts, source_manifest=str(MANIFEST.relative_to(ROOT)),
                  main_window=sorted(LATE), inference='单seed描述性对比，无显著性检验、置信区间或伪重复')
    (OUT/'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    # 记录实际判类/审计实现和冻结词表，避免只锁数据而遗漏分析口径。
    for file in (MANIFEST, Path(__file__), TASK/'2026-09-30-02-audit.py',
                 ROOT/'custom/envs/curation_assets/build_assets.py',
                 ROOT/'custom/envs/curation_assets/vocabs.json',
                 ROOT/'custom/envs/curation_mechanisms.py'):
        hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
    (OUT/'input_hashes.json').write_text(json.dumps(hashes, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'late':{k:v['late'] for k,v in summary.items()}, 'contrasts':contrasts},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
