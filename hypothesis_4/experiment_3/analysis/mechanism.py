"""复核已采纳的D/R过程解释：逐周轨迹、同人同周门槛与原始feed；不运行反事实仿真。"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
DATA = ROOT / 'presentation/hypothesis_4/timestamp_bdr_v1/data'
d = pd.read_csv(DATA / 'decisions.csv')
source = json.loads((DATA / 'source_index.json').read_text())
subset = d[d.condition.isin(['full', 'no_d', 'no_r'])]
weekly = subset.groupby(['condition', 'seed', 'week']).agg(total=('posted', 'sum')).reset_index()
meme = subset[subset.agent_type == 'meme']
mc = meme.groupby(['condition', 'seed', 'week']).posted.sum().rename('meme').reset_index()
weekly = weekly.merge(mc, on=['condition', 'seed', 'week'])
weekly.to_csv(DATA / 'mechanism_weekly_by_seed.csv', index=False)
weekly.groupby(['condition', 'week'])[['total', 'meme']].mean().reset_index().to_csv(DATA / 'mechanism_weekly_mean.csv', index=False)

def transitions(condition):
    f = meme[meme.condition == 'full']
    a = meme[meme.condition == condition]
    pair = f.merge(a, on=['seed', 'agent_id', 'week'], suffixes=('_full', '_ab'))
    late = pair[pair.week >= '2026-W19']
    counts = {f'{i}->{j}': int(((late.speak_full == i) & (late.speak_ab == j)).sum())
              for i in [0, 1] for j in [0, 1]}
    assert len(late) == 228
    return late, counts

r, rcounts = transitions('no_r')
_, dcounts = transitions('no_d')
lost = r[(r.speak_full == 1) & (r.speak_ab == 0)]
assert rcounts == {'0->0': 118, '0->1': 1, '1->0': 34, '1->1': 75}
assert dcounts == {'0->0': 96, '0->1': 23, '1->0': 93, '1->1': 16}
assert (lost.D_ab < lost.D_full).all()
assert (meme[meme.condition == 'full'].threshold > meme[meme.condition == 'full'].B).all()
examples = []
for condition, week in [('full', '2026-W12'), ('no_d', '2026-W12'),
                        ('full', '2026-W20'), ('no_d', '2026-W20'), ('no_r', '2026-W20')]:
    x = d[(d.condition == condition) & (d.seed == 0) & (d.agent_id == 12) & (d.week == week)].iloc[0]
    path = Path(x.source_file)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == x.source_sha256
    row = json.loads(path.read_text())['decision_log'][int(x.record_index)]
    s = next(v for v in source['sources'] if v['condition'] == condition and v['seed'] == 0)
    env = json.loads(Path(s['env_path']).read_text())
    action = next(a for a in env['_arrival_state']['actions'] if str(a['agent_id']) == '12' and a['week'] == week)
    examples.append({'condition': condition, 'seed': 0, 'agent_id': 12, 'week': week,
                     'source_file': str(path), 'source_sha256': x.source_sha256,
                     'record_index': int(x.record_index), 'decision': row,
                     'feed_types': dict(Counter(p['type'] for p in action['feed'])),
                     'feed_sources': dict(Counter(p['source'] for p in action['feed'])),
                     'environment_source': s['env_path']})
(DATA / 'mechanism_agent12_records.json').write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
result = {'passed': True, 'late_meme_opportunities_per_comparison': 228,
          'late_no_d_transition_full_to_ablation': dcounts,
          'late_no_r_transition_full_to_ablation': rcounts,
          'all_34_no_r_losses_have_lower_D': True,
          'all_meme_author_thresholds_exceed_B': True,
          'direct_implication': 'At a fixed Full state that already speaks, setting R=1 cannot silence a meme author in this population.',
          'inference_limit': 'No new counterfactual runs or identified mediation decomposition; observed feedback changes do not isolate each path.',
          'raw_example_count': len(examples), 'additional_LLM_calls': 0}
(DATA / 'mechanism_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
(HERE / 'checks/mechanism.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
