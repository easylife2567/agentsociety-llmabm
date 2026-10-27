"""汇总配对制度/尺度效果，核验反馈与可恢复输入，不进行选模或重拟合。"""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import mean


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def csv_write(path, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def audit(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return {(r['agent_id'], r['week']): r for r in map(json.loads, f)}


def sign(x):
    return 1 if x > 1e-12 else -1 if x < -1e-12 else 0


def main(out):
    manifest = read(out / 'experiment_manifest.json')
    evidence = read(out / 'feedback_evidence.json')
    rows = evidence['weekly']
    types = ('meme', 'mourning', 'marketing', 'education', 'other')
    arms = ('random', 'chronological', 'interest')
    scales = list(manifest['scales'])
    seeds = manifest['matrix']['input_seeds']
    indexed = {(r['scale_name'], r['arm'], r['seed'], r['week'], r['type']): r for r in rows}
    assert len(indexed) == 45 * 55
    metric_names = ('agent_posts', 'agent_supply_share', 'feed_exposures', 'exposure_share', 'exposure_pool_gap')
    totals = []
    for scale in scales:
        for arm in arms:
            for seed in seeds:
                for typ in types:
                    weekly = [r for r in rows if (r['scale_name'], r['arm'], r['seed'], r['type']) == (scale, arm, seed, typ)]
                    late = [r for r in weekly if r['week'] >= '2026-W19']
                    w13 = indexed[scale, arm, seed, '2026-W13', typ]
                    w22 = indexed[scale, arm, seed, '2026-W22', typ]
                    peak = max(r['agent_posts'] for r in weekly)
                    late_posts = sum(r['agent_posts'] for r in late)
                    late_total = sum(r['total_agent_posts'] for r in late)
                    totals.append({'scale_name': scale, 'arm': arm, 'seed': seed, 'type': typ,
                                   'all_posts': sum(r['agent_posts'] for r in weekly), 'late_posts': late_posts,
                                   'late_supply_share': late_posts / late_total if late_total else None,
                                   'late_exposure_share': sum(r['feed_exposures'] for r in late) / sum(r['feed_slots'] for r in late),
                                   'late_agent_post_exposures': sum(r['agent_post_exposures'] for r in late),
                                   'W13_posts': w13['agent_posts'], 'W22_posts': w22['agent_posts'],
                                   'W22_minus_W13_posts': w22['agent_posts'] - w13['agent_posts'],
                                   'peak_posts': peak, 'peak_weeks': '|'.join(r['week'] for r in weekly if r['agent_posts'] == peak)})
    csv_write(out / 'trajectory_summary.csv', totals)
    differences = []
    for scale in scales:
        for left, right in combinations(arms, 2):
            for week in manifest['matrix']['weeks']:
                for typ in types:
                    for metric in metric_names:
                        delta = [indexed[scale, left, seed, week, typ][metric] - indexed[scale, right, seed, week, typ][metric] for seed in seeds]
                        base = [indexed['current', left, seed, week, typ][metric] - indexed['current', right, seed, week, typ][metric] for seed in seeds]
                        differences.append({'scale_name': scale, 'left_minus_right': f'{left}-{right}', 'week': week,
                                            'type': typ, 'metric': metric, 'paired_mean': mean(delta), 'paired_min': min(delta),
                                            'paired_max': max(delta), 'seed0': delta[0], 'seed1': delta[1], 'seed2': delta[2],
                                            'current_mean': mean(base), 'mean_sign_changed': sign(mean(delta)) != sign(mean(base)),
                                            'nonzero_mean_reversal': sign(mean(delta)) * sign(mean(base)) == -1})
    csv_write(out / 'arm_contrasts.csv', differences)
    changes = []
    for scale in scales:
        for arm in arms:
            for seed in seeds:
                original = audit(out / f'action_audits/current_{arm}_s{seed}.jsonl.gz')
                alternate = audit(out / f'action_audits/{scale}_{arm}_s{seed}.jsonl.gz')
                assert original.keys() == alternate.keys()
                decision_changed = [key for key in original if original[key]['speak'] != alternate[key]['speak']]
                feed_changed = [key for key in original if original[key]['feed_keys'] != alternate[key]['feed_keys']]
                cumulative_changed = [key for key in original if original[key]['cumulative_before'] != alternate[key]['cumulative_before']]
                new_post_exposures = sum(k.startswith('agent:') for a in alternate.values() for k in a['feed_keys'])
                changes.append({'scale_name': scale, 'arm': arm, 'seed': seed, 'decision_changes': len(decision_changed),
                                'changed_decisions_by_type': dict(Counter(original[key]['type'] for key in decision_changed)),
                                'feed_changes': len(feed_changed), 'cumulative_changes': len(cumulative_changed),
                                'agent_post_exposures': new_post_exposures,
                                'earliest_feed_changed_week': min((key[1] for key in feed_changed), default=None)})
    assert sum(r['decision_changes'] for r in changes if r['scale_name'] != 'current') > 0
    assert sum(r['feed_changes'] for r in changes if r['scale_name'] != 'current') > 0
    # 两种替代口径可能落入同一整数档：不能把重复轨迹算作两份独立支持。
    duplicate = []
    for arm in arms:
        for seed in seeds:
            a = audit(out / f'action_audits/sample_population_{arm}_s{seed}.jsonl.gz')
            b = audit(out / f'action_audits/unique_authors_{arm}_s{seed}.jsonl.gz')
            duplicate.append({'arm': arm, 'seed': seed, 'sample_population_equals_unique_authors': a == b})
    # 独立从聚合输入/冻结人口复算门槛，并逐行动核验数值决策。
    spec = importlib.util.spec_from_file_location('calibration_runner', out / 'calibration_experiments.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    baseline = read(out / 'baseline_evidence.json')
    frozen_obs = read(out / 'frozen/observations.json')['rows']
    cfg = read(out / 'frozen/hypothesis_4/experiment_2/init/configs/timestamp_v1_random_s0.json')
    population = {str(p['agent_id']): p['kwargs'] for p in cfg['agents']}
    for v in baseline['scale_anchors']:
        acts = [p['params']['activity'] for p in population.values() if p['agent_type'] == v['type']]
        wanted = mean(r[v['baseline_measure']] for r in frozen_obs if r['type'] == v['type'] and r['week'] in runner.PRE) * v['scale']
        assert abs(runner.anchor(acts, wanted) - v['B']) < 1e-12
    checked = 0
    import math
    pop_share = {'meme': .19, 'mourning': .22, 'marketing': .23, 'education': .15, 'other': .21}
    for path in sorted((out / 'action_audits').glob('*.gz')):
        for record in audit(path).values():
            p = population[record['agent_id']]['params']
            own = record['type']
            observed = record['feed_types'].count(own) / len(record['feed_types']) if record['feed_types'] else 0.
            d = 1 + p['spiral'] * p['spiral_scale'] * math.tanh(1.5 * (observed - pop_share[own]) / max(pop_share[own], .05))
            r = math.exp(-p['decay'] * record['cumulative_before'].get(own, 0) / 15)
            u = record['B'] + r * (d - record['B'])
            assert abs(u - record['u']) < 1e-12
            assert (bool(record['feed_types']) and u >= record['A']) == record['speak']
            checked += 1
    assert checked == 49500
    aggregate = []
    for scale in scales:
        for arm in arms:
            for typ in types:
                subset = [r for r in totals if (r['scale_name'], r['arm'], r['type']) == (scale, arm, typ)]
                aggregate.append({'scale_name': scale, 'arm': arm, 'type': typ,
                                  **{m: mean(r[m] for r in subset) for m in ('all_posts', 'late_posts', 'late_supply_share',
                                      'late_exposure_share', 'late_agent_post_exposures', 'W13_posts', 'W22_posts', 'W22_minus_W13_posts')},
                                  'peak_weeks_by_seed': [r['peak_weeks'] for r in subset]})
    result = {'complete': True, 'cells': 45, 'opportunities': checked, 'model_calls': 0, 'network_attempts': 0,
              'baseline_independent_validation': False, 'aggregate': aggregate, 'closed_feedback_changes': changes,
              'duplicate_anchor_trajectories': duplicate,
              'nonzero_weekly_arm_mean_reversals': {scale: sum(r['nonzero_mean_reversal'] for r in differences if r['scale_name'] == scale) for scale in scales},
              'note': 'Descriptive 3-input-seed conditional content proxy; no confidence interval or universal robustness claim'}
    write(out / 'experiment_summary.json', result)
    print(json.dumps({k: result[k] for k in ('cells', 'opportunities', 'nonzero_weekly_arm_mean_reversals')}, ensure_ascii=False))
    for r in aggregate:
        if r['type'] in ('meme', 'marketing'):
            print(json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    main(ap.parse_args().output.resolve())
