"""从逐行动记录独立核对U补充检验并保留全部条件、类型、种子。"""
from calibration_experiments import read, write, sha, csv_write, TYPES, COUNTS, ARMS
from u_experiments import CONDITIONS, paired_noise, probability
from pathlib import Path
from collections import Counter
from statistics import mean
import argparse
import gzip
import json
import math


def audit(path):
    with gzip.open(path, 'rt') as f:
        return list(map(json.loads, f))


def analyze(parent):
    out = parent / 'u_results'
    manifest = read(out / 'manifest.json')
    complete = read(out / 'completion.json')
    assert complete['complete'] and complete['new_cells'] == 108
    assert manifest['script_sha256'] == sha(parent / 'u_experiments.py')
    assert manifest['protocol_sha256'] == sha(parent / 'u_protocol.md')
    assert manifest['helper_sha256'] == sha(parent / 'calibration_experiments.py')
    totals, weekly, verified = [], [], []
    for condition in ('baseline', *CONDITIONS):
        for arm in (('interest',) if condition in ('old_U', 'no_D', 'no_R') else ARMS):
            for seed in range(3):
                name = f'{condition}_{arm}_s{seed}'
                path = parent / f'action_audits/current_{arm}_s{seed}.jsonl.gz' if condition == 'baseline' else out / f'action_audits/{name}.jsonl.gz'
                actions = audit(path)
                assert len({(a['week'], a['agent_id']) for a in actions}) == len(actions)
                opts = CONDITIONS.get(condition, dict(eps=0, init='publish'))
                for a in actions:
                    if condition != 'baseline':
                        assert a['noise'] == paired_noise(seed, a['week'], a['agent_id'], opts['eps'])
                        expected = a['phase'] == 'decision' and bool(a['feed_keys']) and a['u'] + a['noise'] >= a['A']
                        assert a['speak'] == expected
                    else:
                        assert a['speak'] == (bool(a['feed_keys']) and a['u'] >= a['A'])
                    assert f"agent:{a['agent_id']}:{a['week']}" not in a['feed_keys']
                    assert len(a['feed_keys']) == len(a['feed_types']) == len(a['feed_sources'])
                if condition == 'no_feedback':
                    assert all(s != 'agent' for a in actions for s in a['feed_sources'])
                if condition != 'baseline':
                    cell = read(out / f'cell_metrics/{name}.json')
                    assert cell['audit_sha256'] == sha(path)
                    assert sum(a['speak'] for a in actions) == cell['checks']['published']
                    assert cell['checks']['network_attempts'] == 0
                post = [a for a in actions if a['week'] >= '2026-W13']
                late = [a for a in actions if a['week'] >= '2026-W19']
                for typ in TYPES:
                    spoke = [a for a in post if a['type'] == typ and a['speak']]
                    late_n = sum(a['type'] == typ and a['speak'] for a in late)
                    late_total = sum(a['speak'] for a in late)
                    n13 = sum(a['week'] == '2026-W13' and a['type'] == typ and a['speak'] for a in post)
                    n22 = sum(a['week'] == '2026-W22' and a['type'] == typ and a['speak'] for a in post)
                    all_feed = [t for a in late for t in a['feed_types']]
                    total_generated = sum(s == 'agent' for a in late for s in a['feed_sources'])
                    other = [a for a in late if a['type'] != 'meme']
                    other_slots = sum(len(a['feed_types']) for a in other)
                    other_meme = sum(t == 'meme' for a in other for t in a['feed_types'])
                    counts = Counter(a['week'] for a in spoke)
                    peak = max(counts.values(), default=0)
                    totals.append(dict(condition=condition, arm=arm, seed=seed, type=typ,
                                       post_event_posts=len(spoke), late_posts=late_n, late_share=late_n / late_total if late_total else None,
                                       late_total=late_total, W13_posts=n13, W22_posts=n22,
                                       W22_minus_W13=n22-n13, peak_posts=peak,
                                       peak_weeks='|'.join(w for w in sorted(set(a['week'] for a in post)) if counts[w] == peak),
                                       late_exposure_share=all_feed.count(typ)/len(all_feed) if all_feed else None,
                                       late_generated_exposures=total_generated,
                                       non_meme_agent_meme_exposure_share=other_meme/other_slots if other_slots else None))
                    for w in sorted(set(a['week'] for a in actions)):
                        aa = [a for a in actions if a['week'] == w]
                        supply = sum(a['speak'] and a['type'] == typ for a in aa)
                        total = sum(a['speak'] for a in aa)
                        feeds = [t for a in aa for t in a['feed_types']]
                        weekly.append(dict(condition=condition, arm=arm, seed=seed, week=w, type=typ,
                                           posts=supply,total_posts=total,share=supply/total if total else None,
                                           exposures=feeds.count(typ),feed_slots=len(feeds),
                                           generated_exposures=sum(t==typ and s=='agent' for a in aa for t,s in zip(a['feed_types'],a['feed_sources']))))
                verified.append(dict(condition=condition, arm=arm, seed=seed, actions=len(actions), audit_sha256=sha(path)))
    # 事后供给拟合诊断：来源固定，不参与重拟合或条件选择。
    obs=read(parent/'frozen/observations.json')['rows']
    fixed_c=read(parent/'experiment_manifest.json')['scales']['current']
    diagnostic=[]
    for condition in ('baseline','hard_warm','soft_publish','soft_warm','soft_cold'):
        for arm in ARMS:
            chosen=[r for r in weekly if r['condition']==condition and r['arm']==arm and '2026-W13'<=r['week']<='2026-W18']
            errors=[((r['posts']-next(o['posts_utc'] for o in obs if o['type']==r['type'] and o['week']==r['week'])*fixed_c)/COUNTS[r['type']])**2 for r in chosen]
            diagnostic.append(dict(condition=condition,arm=arm,normalized_RMSE=math.sqrt(mean(errors)),rows=len(chosen),status='posthoc_transfer_diagnostic_not_selection_or_independent_validation'))
    csv_write(out/'transfer_diagnostic.csv',diagnostic)
    csv_write(out / 'trajectory_summary.csv', totals)
    csv_write(out / 'audited_weekly.csv', weekly)
    index = {(r['condition'],r['arm'],r['seed'],r['type']):r for r in totals}
    effects = []
    for condition in ('baseline', *CONDITIONS):
        arms = ('interest',) if condition in ('old_U','no_D','no_R') else ARMS
        for arm in arms:
            for typ in TYPES:
                for metric in ('late_posts','late_share','W13_posts','W22_posts','late_total','late_generated_exposures','non_meme_agent_meme_exposure_share'):
                    values = [index[condition,arm,s,typ][metric] for s in range(3)]
                    if any(v is None for v in values):
                        continue
                    candidate = [v-index['soft_warm',arm,s,typ][metric] for s,v in enumerate(values)]
                    original = [v-index['baseline',arm,s,typ][metric] for s,v in enumerate(values)]
                    delta = [v-index[condition,'random',s,typ][metric] for s,v in enumerate(values)] if 'random' in arms else None
                    effects.append(dict(condition=condition,arm=arm,type=typ,metric=metric,mean=mean(values),minimum=min(values),maximum=max(values),seed0=values[0],seed1=values[1],seed2=values[2],mean_minus_candidate=mean(candidate),mean_minus_original=mean(original),paired_minus_random=mean(delta) if delta else None))
    csv_write(out / 'effects.csv', effects)
    selected = [r for r in effects if r['type']=='meme' and r['metric'] in ('late_posts','late_share')]
    technical = dict(cells_verified=len(verified),audits=verified,network_attempts=0,model_calls=0,
                     three_baseline_verifications=complete['baseline_verification'],
                     static_max_error=max(abs(r['residual']) for r in read(out/'static_mapping.json') if r['condition']!='baseline'))
    assert len(verified)==117  # 九个原单元复用，新增108个。
    assert technical['static_max_error']<1e-10
    write(out/'analysis.json',dict(technical=technical,meme_results=selected,all_effects=effects))
    print(json.dumps(dict(cells_verified=len(verified),technical=technical['static_max_error'],meme_results=selected),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',type=Path,required=True)
    analyze(ap.parse_args().run_dir.resolve())
