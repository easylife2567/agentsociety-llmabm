"""B标定窗口检验与正式环境的有限正文闭环代理；禁止网络和LLM。

原始工作簿只在prepare中只读聚合，不保存作者身份。后续实验可用冻结聚合恢复。
已有项目源码不修改；project-root必须是独立基线worktree。
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import csv
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import shutil
import socket
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from types import SimpleNamespace

os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
os.environ['MEM0_TELEMETRY'] = 'False'
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
NETWORK = []


def offline(*args, **kwargs):
    NETWORK.append('blocked_connection')
    raise RuntimeError('B calibration experiments forbid network connections')


socket.socket.connect = offline
socket.socket.connect_ex = offline
TYPES = {'meme': '梗文化讨论', 'mourning': '事件悼念讨论', 'marketing': '借势营销',
         'education': '教育观点讨论', 'other': '其他讨论'}
ALL_TYPES = (*TYPES, 'noise')
PRE = [f'2026-W{w:02}' for w in range(5, 13)]
WEEKS = [f'2026-W{w}' for w in range(12, 23)]
ARMS = ('random', 'chronological', 'interest')
COUNTS = {'meme': 19, 'mourning': 22, 'marketing': 23, 'education': 15, 'other': 21}
FALLBACK = {'meme': '牢峰这个梗让人感慨。', 'mourning': '一路走好，愿安息。',
            'marketing': '欢迎咨询我们的课程报名服务。', 'education': '志愿填报需要仔细了解专业。',
            'other': '最近看到一些相关讨论，记录一下想法。'}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csv_write(path, rows):
    with Path(path).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def anchor(activities, wanted):
    """原标定的整数映射，保持Python round与最低门槛减0.02。"""
    acts = sorted(activities)
    wanted = max(0., min(len(acts), wanted))
    if wanted < .5:
        return acts[0] - .02
    k = max(1, min(len(acts) - 1, round(wanted)))
    return (acts[k - 1] + acts[k]) / 2


def prepare(root, out, workbook):
    import pandas as pd
    frozen = out / 'frozen'
    frozen.mkdir()
    paths = [root / 'hypothesis_4/benchmark_curves.json']
    paths += sorted((root / 'hypothesis_4/experiment_2/init/configs').glob('timestamp_v1_*_s*.json'))
    assert len(paths) == 10
    for path in list(paths[1:]):
        cfg = read(path)
        for key in ('injection_data_path', 'weekly_initial_injection_data_path', 'vocab_path'):
            paths.append(root / cfg['env_modules'][0]['kwargs'][key])
    sources = {}
    for path in sorted(set(paths)):
        rel = str(path.relative_to(root))
        dest = frozen / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        sources[rel] = sha(path)
    matrix = read(frozen / 'hypothesis_4/benchmark_curves.json')['weekly_category_matrix']
    df = pd.read_excel(workbook, usecols=['数据有效性', '内容类别', 'author', 'published_at'])
    dates = pd.to_datetime(df['published_at'], utc=True, errors='raise')
    assert not dates.isna().any()
    for field, stamps in (('week', dates), ('week_shanghai', dates.dt.tz_convert('Asia/Shanghai'))):
        iso = stamps.dt.isocalendar()
        df[field] = [f'{y}-W{w:02}' for y, w in zip(iso['year'], iso['week'])]
    valid = df[df['数据有效性'] != '存疑'].copy()
    known = valid[valid.author.notna()].copy()
    window = known[known.week.isin(WEEKS)]
    kinds = window.groupby('author')['内容类别'].nunique()
    singles = window[window.author.isin(kinds[kinds == 1].index)].groupby('author')['内容类别'].first()
    observations = []
    cohorts = {}
    for typ, label in TYPES.items():
        cohort = set(singles[singles == label].index)
        cohorts[typ] = len(cohort)
        for week in sorted(set(PRE + WEEKS)):
            subset = valid[(valid.week == week) & (valid['内容类别'] == label)]
            loc = valid[(valid.week_shanghai == week) & (valid['内容类别'] == label)]
            assert len(subset) == matrix[week][label], (week, typ)
            observations.append({'week': week, 'type': typ, 'posts_utc': len(subset),
                                 'authors_utc': subset.author.nunique(), 'missing_author_posts': int(subset.author.isna().sum()),
                                 'cohort_active_authors': subset[subset.author.isin(cohort)].author.nunique(),
                                 'posts_shanghai': len(loc), 'authors_shanghai': loc.author.nunique()})
    csv_write(out / 'baseline_observations.csv', observations)
    write(frozen / 'observations.json', {'rows': observations, 'cohort_counts': cohorts})
    w13authors = next(r['authors_utc'] for r in observations if r['week'] == '2026-W13' and r['type'] == 'mourning')
    c = 22 / matrix['2026-W13'][TYPES['mourning']]
    scales = {'current': c, 'sample_population': 100 / sum(cohorts.values()),
              'unique_authors': 22 / w13authors, 'half_stress': c / 2, 'double_stress': c * 2}
    code_paths = list((root / 'custom/envs').glob('*.py')) + list((root / 'custom/agents').glob('*.py'))
    # 记录实际SDK版本及加载入口；不复制uv环境，也不读取凭据。
    import agentsociety2
    deps = {name: importlib.metadata.version(name) for name in ('agentsociety2', 'pandas', 'numpy', 'openpyxl')}
    manifest = {'baseline_commit': '69d243955d341444ae769fae5bf23dc160465cd6', 'created_at': datetime.now(timezone.utc).isoformat(),
                'frozen_inputs_sha256': sources, 'code_sha256': {str(p.relative_to(root)): sha(p) for p in code_paths},
                'raw_workbook': {'path': str(workbook), 'sha256': sha(workbook), 'valid_posts': len(valid),
                                 'missing_author_valid_posts': int(valid.author.isna().sum())},
                'dependencies': deps, 'sdk_loaded_from': str(Path(agentsociety2.__file__).resolve()),
                'sdk_entry_sha256': sha(agentsociety2.__file__), 'aggregate_sha256': sha(frozen / 'observations.json'),
                'script_sha256': sha(__file__), 'protocol_sha256': sha(out / 'experiment_protocol.md'),
                'scales': scales, 'cohort_counts': cohorts, 'frozen_fallback': FALLBACK,
                'matrix': {'scales': 5, 'arms': list(ARMS), 'input_seeds': [0, 1, 2], 'population': 100,
                           'weeks': WEEKS, 'cells': 45, 'opportunities': 49500, 'max_seconds': 1800}, 'network_attempts': len(NETWORK)}
    assert not NETWORK
    write(out / 'experiment_manifest.json', manifest)
    print(json.dumps({'prepared': True, 'scales': scales, 'cohort_counts': cohorts, 'dependencies': deps}, ensure_ascii=False), flush=True)


def baseline(out):
    manifest = read(out / 'experiment_manifest.json')
    obs = read(out / 'frozen/observations.json')['rows']
    cfg = read(out / 'frozen/hypothesis_4/experiment_2/init/configs/timestamp_v1_random_s0.json')
    population = [a['kwargs'] for a in cfg['agents']]
    rows = []
    windows = {'all': PRE, **{f'leave_{w}': [x for x in PRE if x != w] for w in PRE},
               'W05_W11': PRE[:-1], 'W09_W12': PRE[4:]}
    c = manifest['scales']['current']
    for typ in TYPES:
        acts = [p['params']['activity'] for p in population if p['agent_type'] == typ]
        original = next(p['params']['baseline_utility'] for p in population if p['agent_type'] == typ)
        for name, weeks in windows.items():
            pre = [r for r in obs if r['type'] == typ and r['week'] in weeks]
            for convention in ('posts_utc', 'authors_utc', 'posts_shanghai', 'authors_shanghai'):
                wanted = mean(r[convention] for r in pre) * c
                b = anchor(acts, wanted)
                count = sum(b >= a for a in acts)
                held = name.removeprefix('leave_') if name.startswith('leave_') else None
                held_target = next(r[convention] for r in obs if r['type'] == typ and r['week'] == held) * c if held else None
                rows.append({'type': typ, 'window': name, 'input_convention': convention, 'weeks_n': len(weeks),
                             'real_weekly_mean': mean(r[convention] for r in pre), 'current_c_expected': wanted,
                             'B': b, 'delta_B': b - original, 'R0_speakers': count, 'floor_active': wanted < .5,
                             'mean_mapping_residual': count - wanted, 'held_week': held,
                             'held_expected_fixed_c': held_target, 'held_residual_fixed_c': count - held_target if held else None})
        assert abs(next(r['B'] for r in rows if r['type'] == typ and r['window'] == 'all' and r['input_convention'] == 'posts_utc') - original) < 1e-12
    csv_write(out / 'window_checks.csv', rows)
    variants = []
    for name, scale in manifest['scales'].items():
        for typ in TYPES:
            acts = [p['params']['activity'] for p in population if p['agent_type'] == typ]
            metric = 'authors_utc' if name == 'unique_authors' else 'posts_utc'
            wanted = mean(r[metric] for r in obs if r['type'] == typ and r['week'] in PRE) * scale
            b = anchor(acts, wanted)
            variants.append({'scale_name': name, 'scale': scale, 'ratio_current': scale / c, 'type': typ,
                             'baseline_measure': metric, 'expected': wanted, 'B': b, 'R0_speakers': sum(b >= a for a in acts)})
    # 作者口径同时改变分子与峰的分母；其他候选仅改变共同尺度。
    csv_write(out / 'scale_anchors.csv', variants)
    write(out / 'baseline_evidence.json', {'window_rows': rows, 'scale_anchors': variants,
                                          'independent_validation': False, 'network_attempts': len(NETWORK)})
    print('baseline windows and scale anchors complete', flush=True)


def local(value):
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.astimezone(timezone(timedelta(hours=8))).replace(tzinfo=None) if value.tzinfo else value


async def cell(root, out, env_module, agent_module, scale_name, arm, seed, anchors):
    frozen = out / 'frozen'
    cfg = read(frozen / f'hypothesis_4/experiment_2/init/configs/timestamp_v1_{arm}_s{seed}.json')
    kwargs = copy.deepcopy(cfg['env_modules'][0]['kwargs'])
    for key in ('injection_data_path', 'weekly_initial_injection_data_path', 'vocab_path'):
        kwargs[key] = str(frozen / kwargs[key])
    profiles = {str(a['agent_id']): copy.deepcopy(a['kwargs']) for a in cfg['agents']}
    for p in profiles.values():
        old = p['params']['baseline_utility']
        p['params']['baseline_utility'] = anchors[scale_name, p['agent_type']]
        if scale_name == 'current':
            assert abs(p['params']['baseline_utility'] - old) < 1e-12
    env = env_module.CurationDynamicsSpace(**kwargs)
    hours = set(kwargs['chronological_action_hours'].values())
    for overrides in kwargs.get('chronological_action_hour_overrides', {}).values():
        hours.update(overrides.values())
    moments = [datetime(2026, 3, 16) + timedelta(weeks=w, hours=h) for w in range(11) for h in sorted(hours)]
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
            holder = SimpleNamespace(_agent_type=p['agent_type'], _params=p['params'])
            u, comps = agent_module.CurationDiscourseAgent._speak_stimulus(holder, snap)
            speak = bool(snap['feed']) and u >= p['params']['activity']
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
                      'components_rounded': comps, 'cumulative_before': original['cumulative_before'],
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
    assert len(actions) == len(env._arrival.state['actions']) == 1100
    assert len({(a['agent_id'], a['week']) for a in actions}) == 1100
    assert len(env._arrival.state['weeks']) == 11
    expected = {aid: Counter() for aid in profiles}
    for action in actions:
        expected[action['agent_id']].update(action['feed_types'])
    assert all(expected[aid][typ] == env._cumulative_exposures[aid].get(typ, 0) for aid in profiles for typ in ALL_TYPES)
    assert sum(a['speak'] for a in actions) == sum(env._total_posts_by_agent.values())
    rows = []
    for week in WEEKS:
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
            rows.append({'scale_name': scale_name, 'arm': arm, 'seed': seed, 'week': week, 'type': typ,
                         'agent_posts': supply[typ], 'agent_supply_share': supply[typ] / total_posts if total_posts else None,
                         'agent_opportunities': COUNTS[typ], 'speaking_rate': supply[typ] / COUNTS[typ],
                         'total_agent_posts': total_posts, 'external_posts': external[typ],
                         'feed_exposures': exposure[typ], 'feed_slots': total_slots,
                         'exposure_share': exposure[typ] / total_slots if total_slots else None,
                         'agent_post_exposures': agent_exposure[typ], 'eligible_pool_share': eligible_expected_slots / total_slots if total_slots else None,
                         'exposure_pool_gap': (exposure[typ] - eligible_expected_slots) / total_slots if total_slots else None,
                         'real_expected_fixed_c': real * read(out / 'experiment_manifest.json')['scales']['current'],
                         'absolute_residual_fixed_c': supply[typ] - real * read(out / 'experiment_manifest.json')['scales']['current']})
    name = f'{scale_name}_{arm}_s{seed}'
    audit_path = out / 'action_audits' / f'{name}.jsonl.gz'
    with gzip.open(audit_path, 'wt', encoding='utf-8') as f:
        for a in actions:
            f.write(json.dumps(a, ensure_ascii=False, separators=(',', ':')) + '\n')
    write(out / 'cell_metrics' / f'{name}.json', {'identity': name, 'weekly': rows, 'checks': {
        'actions': 1100, 'weeks': 11, 'future_exposures': 0, 'cumulative_verified': True,
        'fallback_posts': fallback_count, 'published': sum(a['speak'] for a in actions),
        'network_attempts': len(NETWORK)}, 'audit_sha256': sha(audit_path)})
    return rows


async def feedback(root, out):
    manifest = read(out / 'experiment_manifest.json')
    assert sha(__file__) == manifest['script_sha256']
    assert sha(out / 'experiment_protocol.md') == manifest['protocol_sha256']
    assert all(sha(root / p) == h for p, h in manifest['code_sha256'].items())
    assert all(sha(out / 'frozen' / p) == h for p, h in manifest['frozen_inputs_sha256'].items())
    env = module('b_calibration_environment', root / 'custom/envs/curation_dynamics_space.py')
    agent = module('b_calibration_agent', root / 'custom/agents/curation_discourse_agent.py')
    anchors = {(r['scale_name'], r['type']): r['B'] for r in read(out / 'baseline_evidence.json')['scale_anchors']}
    (out / 'action_audits').mkdir()
    (out / 'cell_metrics').mkdir()
    start = time.monotonic()
    rows = []
    for scale_name in manifest['scales']:
        for seed in manifest['matrix']['input_seeds']:
            for arm in ARMS:
                if time.monotonic() - start >= manifest['matrix']['max_seconds']:
                    raise TimeoutError('frozen budget reached; preserve completed cells')
                current_rows = await cell(root, out, env, agent, scale_name, arm, seed, anchors)
                rows.extend(current_rows)
                print(json.dumps({'cell': f'{scale_name}_{arm}_s{seed}', 'completed': len(rows) // 55,
                                  'published': sum(r['agent_posts'] for r in current_rows),
                                  'elapsed_seconds': round(time.monotonic() - start, 2)}, ensure_ascii=False), flush=True)
    assert not NETWORK
    csv_write(out / 'weekly_metrics.csv', rows)
    write(out / 'feedback_evidence.json', {'complete': True, 'cells': 45, 'opportunities': 49500,
                                         'model_calls': 0, 'network_attempts': len(NETWORK),
                                         'elapsed_seconds': time.monotonic() - start, 'weekly': rows})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=('prepare', 'baseline', 'feedback'))
    ap.add_argument('--project-root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--workbook', type=Path)
    args = ap.parse_args()
    if args.mode == 'prepare':
        prepare(args.project_root.resolve(), args.output.resolve(), args.workbook.resolve())
    elif args.mode == 'baseline':
        baseline(args.output.resolve())
    else:
        asyncio.run(feedback(args.project_root.resolve(), args.output.resolve()))


if __name__ == '__main__':
    main()
