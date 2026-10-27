"""复用原图3/4口径复算30次主实验；只读原始文件和官方查询CLI，不调用LLM。"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from itertools import product
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPERIMENT = ROOT / 'hypothesis_4/experiment_2'
sys.path.insert(0, str(EXPERIMENT))
from run_seed_extension_parallel import final_result
from run_main_experiment import completed
from run_asset_paths import resolve_asset_path

ARMS = ('random', 'chronological', 'interest')
TYPES = ('meme', 'mourning', 'education', 'marketing', 'other')
WEEKS = [f'2026-W{w}' for w in range(12, 23)]
LATE = WEEKS[7:]
FIELDS = ['agent_supply', *[f'agent_supply_{t}' for t in TYPES]]
SQL = 'SELECT week, ' + ', '.join(FIELDS) + ' FROM curation_dynamics_env_state ORDER BY week'
METRICS = ('late_meme_posts', 'late_meme_share', 'own_share', 'meme_post_rate', 'cross_generated_share')
PAIRS = (('interest', 'random'), ('chronological', 'random'), ('chronological', 'interest'))


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(item):
    run, directory, cohort, request_model = item
    if cohort == 'new7':
        final_result(directory, run)
    else:
        completed(directory, run)
    result = subprocess.run([sys.executable, str(ROOT / '.agentsociety/bin/ags.py'), 'analysis', 'query-data',
                            '--data-path', str(directory / 'replay'), '--sql', SQL],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    assert payload['success']
    weekly = [dict(zip(payload['columns'], row)) for row in payload['rows']]
    assert [r['week'] for r in weekly] == WEEKS
    env_path = directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json'
    actions = read(env_path)['_arrival_state']['actions']
    assert len(actions) == 1100
    assert len({(str(a['agent_id']), a['week']) for a in actions}) == 1100
    counts, models, requests, hashes = Counter(), Counter(), 0, {}
    for path in sorted((directory / 'agents').glob('*/AGENT.json')):
        a = read(path)
        assert len(a['decision_log']) == 11
        for row in a['decision_log']:
            assert row['reason'] not in ('action_failed', 'publication_failed')
            requests += row.get('generation_attempts', 0)
            if row.get('posted'):
                counts[(row['week'], a['profile']['agent_type'])] += 1
                models[row.get('response_model', 'missing')] += 1
        hashes[str(path.relative_to(ROOT))] = digest(path)
    metadata = dict(run_id=run['run_id'], arm=run['algorithm'], seed=run['seed'], cohort=cohort,
                    request_model=request_model, response_models=';'.join(sorted(models)),
                    run_dir=str(directory.relative_to(ROOT)))
    for row in weekly:
        assert row['agent_supply'] == sum(row[f'agent_supply_{t}'] for t in TYPES)
        for t in TYPES:
            assert row[f'agent_supply_{t}'] == counts[(row['week'], t)]
        row.update(metadata)
    late_actions = [a for a in actions if a['week'] in LATE]
    own = [a for a in late_actions if a['agent_type'] == 'meme']
    cross = [a for a in late_actions if a['agent_type'] != 'meme']
    own_feed = [p for a in own for p in a['feed']]
    cross_feed = [p for a in cross for p in a['feed']]
    assert len(late_actions) == 400 and len(own) == 76 and len(cross) == 324
    assert len(own_feed) == 760 and len(cross_feed) == 3240
    assert all(len(a['feed']) == 10 for a in late_actions)
    meme_posts = sum(counts[(w, 'meme')] for w in LATE)
    late_total = sum(v for (w, _), v in counts.items() if w in LATE)
    run_metrics = dict(**metadata, total_posts=sum(counts.values()), body_requests=requests,
        late_meme_posts=meme_posts, late_total_posts=late_total, late_meme_share=meme_posts / late_total,
        own_share=sum(p['type'] == 'meme' for p in own_feed) / 760,
        meme_post_rate=meme_posts / 76,
        cross_generated_share=sum(p.get('source') == 'agent' and p['type'] == 'meme' for p in cross_feed) / 3240,
        all_feed_meme_share=sum(p['type'] == 'meme' for p in own_feed + cross_feed) / 4000,
        w13_mourning_posts=counts[('2026-W13', 'mourning')],
        w13_mourning_rate=counts[('2026-W13', 'mourning')] / 22,
        mourning_peak_week=max(WEEKS, key=lambda w: counts[(w, 'mourning')]))
    for path in [env_path, directory / 'SOCIETY_STEP.json', directory / 'replay/_schema.json',
                 *sorted((directory / 'replay').glob('curation_dynamics_env_state.*.jsonl'))]:
        hashes[str(path.relative_to(ROOT))] = digest(path)
    return weekly, run_metrics, hashes, dict(models)


def summary(values):
    values = np.array(values, dtype=float)
    sem = stats.sem(values)
    half = stats.t.ppf(.975, len(values) - 1) * sem
    return dict(n=len(values), mean=float(values.mean()), sd=float(values.std(ddof=1)),
                minimum=float(values.min()), maximum=float(values.max()),
                ci_low=float(values.mean() - half), ci_high=float(values.mean() + half))


def paired(values):
    values = np.array(values, dtype=float)
    observed = abs(values.mean())
    null = np.array(list(product([-1, 1], repeat=len(values)))) @ values / len(values)
    loo = (values.sum() - values) / (len(values) - 1)
    return dict(**summary(values), positive=int(sum(values > 1e-12)), zero=int(sum(abs(values) <= 1e-12)),
                negative=int(sum(values < -1e-12)), permutation_p=float(np.mean(abs(null) >= observed - 1e-12)),
                leave_one_out_min=float(loo.min()), leave_one_out_max=float(loo.max()))


def main():
    target = OUT / 'seed10_sources.json'
    assert not target.exists(), '不覆盖本次来源证据；更改复算需明确版本'
    manifests = [(read(EXPERIMENT / 'init/manifest.json'), EXPERIMENT / 'runs/timestamp_v1/execution_records/seed0_2', 'old3'),
                 (read(EXPERIMENT / 'init/manifest_seed3_9.json'), EXPERIMENT / 'runs/timestamp_v1/execution_records/seed3_9', 'new7')]
    items, hashes = [], {}
    for manifest, batch, cohort in manifests:
        plan, state = read(batch / 'runtime_plan.json'), read(batch / 'batch_execution.json')
        assert state['status'] == 'completed'
        completion = {r['run_id']: r for r in state['completed']}
        for run in manifest['runs']:
            completed = completion[run['run_id']]
            directory = resolve_asset_path(completed.get('run_dir') or ROOT / run['run_dir'])
            items.append((run, directory, cohort, plan['model']))
        for name in ['runtime_plan.json', 'batch_execution.json']:
            hashes[str((batch / name).relative_to(ROOT))] = digest(batch / name)
    assert len(items) == 30
    outputs = list(ThreadPoolExecutor(max_workers=4).map(extract, items))
    weekly, runs, model_counts = [], [], {}
    for ws, run, source, models in outputs:
        weekly.extend(ws); runs.append(run); hashes.update(source); model_counts[run['run_id']] = models
    df, wf = pd.DataFrame(runs), pd.DataFrame(weekly)
    assert len(wf) == 330 and len(df) == 30
    old = pd.read_csv(OUT / 'timestamp_v1_agent_supply_by_run_week.csv')
    baseline = wf[wf.cohort == 'old3'].merge(old, on=['run_id', 'arm', 'seed', 'week'], suffixes=('', '_old'))
    assert len(baseline) == 99 and all((baseline[f] == baseline[f + '_old']).all() for f in FIELDS)
    # 原论文图3/4的三份表逐格复现，保证不是换口径后再判断稳定性。
    reference = ROOT / 'paper/figures/source_data'
    late_ref = pd.read_csv(reference / 'simulation_late.csv')
    exp_ref = pd.read_csv(reference / 'simulation_exposure.csv')
    for source, mapping in [(late_ref, {'late_meme_posts': 'meme_posts', 'late_total_posts': 'total_posts', 'late_meme_share': 'meme_share'}),
                            (exp_ref, {k: k for k in ('own_share', 'meme_post_rate', 'cross_generated_share')})]:
        compare = df[df.cohort == 'old3'].merge(source, on=['arm', 'seed'], suffixes=('', '_reference'))
        assert len(compare) == 9
        for key, oldkey in mapping.items():
            right = oldkey + '_reference' if oldkey in df.columns else oldkey
            assert np.allclose(compare[key], compare[right], rtol=0, atol=1e-12), key
    arm_rows, pairs, weekly_summary = [], [], []
    for cohort, subset in [('old3', df[df.cohort == 'old3']), ('new7', df[df.cohort == 'new7']), ('all10', df)]:
        for arm in ARMS:
            part = subset[subset.arm == arm]
            for metric in (*METRICS, 'total_posts', 'w13_mourning_posts', 'all_feed_meme_share'):
                arm_rows.append(dict(cohort=cohort, arm=arm, metric=metric, **summary(part[metric])))
        cohort_pairs = []
        for metric in METRICS:
            pivot = subset.pivot(index='seed', columns='arm', values=metric)
            for a, b in PAIRS:
                cohort_pairs.append(dict(cohort=cohort, contrast=f'{a}-{b}', metric=metric,
                                         **paired(pivot[a] - pivot[b])))
        ranked = sorted(range(len(cohort_pairs)), key=lambda i: cohort_pairs[i]['permutation_p'])
        last = 0
        for rank, index in enumerate(ranked):
            last = max(last, min(1., cohort_pairs[index]['permutation_p'] * (len(ranked) - rank)))
            cohort_pairs[index]['holm_p'] = last
        pairs.extend(cohort_pairs)
        selected = wf[wf.seed.isin(subset.seed.unique())]
        for (arm, week), group in selected.groupby(['arm', 'week'], sort=True):
            weekly_summary.append(dict(cohort=cohort, arm=arm, week=week, n=len(group),
                **{f'{f}_{stat}': float(getattr(group[f], stat)()) for f in FIELDS for stat in ['mean', 'min', 'max']}))
    for name, data in [('seed10_runs.csv', df), ('seed10_weekly.csv', wf),
                       ('seed10_arm_summary.csv', pd.DataFrame(arm_rows)), ('seed10_paired_contrasts.csv', pd.DataFrame(pairs)),
                       ('seed10_weekly_summary.csv', pd.DataFrame(weekly_summary))]:
        data.to_csv(OUT / name, index=False, float_format='%.12g')
    with sqlite3.connect(OUT / 'seed10_metrics.sqlite') as connection:
        df.to_sql('seed10_run_metrics', connection, index=False, if_exists='fail')
        wf.to_sql('seed10_weekly_metrics', connection, index=False, if_exists='fail')
    report = dict(created_at=datetime.now(timezone.utc).isoformat(), scope='main-only; 30 completed conditions; no ablation',
        query=SQL, script_sha256=digest(Path(__file__)), original_measurement_script='paper/figures/scripts/prepare_simulation.py',
        original_measurement_script_sha256=digest(ROOT / 'paper/figures/scripts/prepare_simulation.py'),
        old_weekly_and_paper_metrics_reproduced=True, runs=runs, response_model_counts=model_counts,
        cohort_definition={'old3': 'seed0–2: request260910; actual response undated alias',
                           'new7': 'seed3–9: request v4.1-flash; actual response261017', 'all10': 'mixed-version extension, descriptive + paired contrasts'},
        denominators={'late_meme_post_rate': 76, 'own_share': 760, 'cross_generated_share': 3240},
        late_window=LATE, uncertainty='seed-level t 95% interval; exact two-sided sign-flip; Holm family=15 contrasts within each cohort; leave-one-seed-out means',
        model_limit='seed ranges and backend version are confounded; no pure model-version causal estimate',
        source_sha256=hashes,
        output_sha256={f: digest(OUT / f) for f in ['seed10_runs.csv', 'seed10_weekly.csv', 'seed10_arm_summary.csv', 'seed10_paired_contrasts.csv', 'seed10_weekly_summary.csv', 'seed10_metrics.sqlite']})
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(runs=30, weeks=330, successful_posts=int(df.total_posts.sum()),
        old_metric_reproduction='passed', source_files=len(hashes)), ensure_ascii=False))


if __name__ == '__main__':
    main()
