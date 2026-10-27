"""图5十个配对种子：只读原始Agent/环境/官方replay，冻结五面板作图表。"""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
DATA = OUT / 'source_data'
QA = OUT / 'qa'
E3 = ROOT / 'hypothesis_4/experiment_3'
E2 = ROOT / 'hypothesis_4/experiment_2'
sys.path.insert(0, str(E2))
from run_asset_paths import resolve_asset_path
CONTROL = E3 / 'runs/timestamp_bdr_v1_attempt_02/execution_records/seed3_9'
TYPES = ['education', 'mourning', 'meme', 'other', 'marketing']
POPULATION = {'education': 15, 'mourning': 22, 'meme': 19, 'other': 21, 'marketing': 23}
WEEKS = [f'2026-W{w}' for w in range(12, 23)]
LATE = WEEKS[7:]
MID = WEEKS[2:7]
CONDITIONS = ['full', 'no_b', 'no_d', 'no_r']


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def normalized(doc):
    """仅消除等字节输入路径和运行专属正文重写账本的表示差异。"""
    result = copy.deepcopy(doc)
    for env in result['env_modules']:
        for key, value in list(env['kwargs'].items()):
            if key.endswith('_path'):
                env['kwargs'][key] = {'input_sha256': sha(ROOT / value)}
    for agent in result['agents']:
        agent['kwargs']['content_retry_budget']['ledger_path'] = '__run_ledger__'
    return result


def query(task):
    """复用正式分析的官方只读SQL接口；子进程以既有sitecustomize阻断网络。"""
    columns = ['week', 'agent_supply'] + [f'agent_supply_{t}' for t in TYPES]
    queries = {
        'weekly': 'SELECT ' + ', '.join(columns) + ' FROM curation_dynamics_env_state ORDER BY week',
        'agent': 'SELECT step,agent_type,COUNT(*) AS opportunities,SUM(spoke) AS spoke '
                 'FROM curation_dynamics_agent_state GROUP BY step,agent_type ORDER BY step,agent_type',
    }
    env = dict(os.environ, PYTHONPATH=str(E3 / 'analysis/offline_guard'),
               BDR_ANALYSIS_NETWORK_AUDIT=str(QA / 'fig5_network_attempts.jsonl'),
               LITELLM_LOCAL_MODEL_COST_MAP='True', MEM0_TELEMETRY='False',
               ANONYMIZED_TELEMETRY='False', PYTHONDONTWRITEBYTECODE='1')
    rows = {}
    for name, sql in queries.items():
        process = subprocess.run(
            [sys.executable, str(ROOT / '.agentsociety/bin/ags.py'), 'analysis', 'query-data',
             '--data-path', str(task['directory'] / 'replay'), '--sql', sql],
            cwd=ROOT, capture_output=True, text=True, env=env, check=False)
        assert process.returncode == 0, (task['run_id'], name, process.stderr[-1500:])
        result = json.loads(process.stdout)
        assert result['success'], result
        rows[name] = [dict(zip(result['columns'], row)) for row in result['rows']]
    return rows


def main():
    # 来源包括旧九次和最新21次完批清单；失败/中断目录不自动发现、不混入。
    main_source = read(DATA / 'seed10_sources.json')
    original = read(ROOT / 'presentation/hypothesis_4/timestamp_bdr_v1/data/source_index.json')
    manifest = read(E3 / 'init/manifest_seed3_9.json')
    old_manifest = read(E3 / 'init/manifest.json')
    execution = read(CONTROL / 'batch_execution.json')
    completion = read(CONTROL / 'completion_check_recovery_3.json')
    relocation = read(E2 / 'runs/timestamp_v1/relocation.json')
    assert execution['status'] == completion['status'] == 'completed'
    assert len(execution['completed']) == completion['completed_count'] == 21
    completed = {item['run_id']: item for item in execution['completed']}
    tasks = []
    for source in main_source['runs']:
        if source['arm'] != 'interest':
            continue
        tasks.append({'condition': 'full', 'seed': source['seed'], 'run_id': source['run_id'],
                      'directory': resolve_asset_path(source['run_dir']),
                      'config': E2 / f'init/configs/timestamp_v1_interest_s{source["seed"]}.json'})
    old_sources = {(s['condition'], s['seed']): s for s in original['sources']}
    for item in old_manifest['runs']:
        source = old_sources[(item['condition'], item['seed'])]
        tasks.append({'condition': item['condition'], 'seed': item['seed'], 'run_id': item['run_id'],
                      'directory': Path(source['root']), 'config': ROOT / item['config']})
    for item in manifest['runs']:
        done = completed[item['run_id']]
        assert done['steps'] == 693 and done['decisions'] == done['unique_decisions'] == 1100
        tasks.append({'condition': item['condition'], 'seed': item['seed'], 'run_id': item['run_id'],
                      'directory': Path(done['run_dir']), 'config': ROOT / item['config']})
    assert len(tasks) == 40 and len({(t['condition'], t['seed']) for t in tasks}) == 40
    assert all({t['seed'] for t in tasks if t['condition'] == c} == set(range(10)) for c in CONDITIONS)
    tasks.sort(key=lambda t: (CONDITIONS.index(t['condition']), t['seed']))

    # 将每个实际使用文件与已有独立来源指纹对应，避免沿用未完成的恢复前目录。
    expected = {str(resolve_asset_path(p)): h for p, h in main_source['source_sha256'].items()}
    expected.update({str(resolve_asset_path(p)): h for p, h in completion['source_sha256'].items()})
    # Full原始replay的历史路径和逐文件迁移指纹由正式迁移清单共同固定。
    expected.update({str(ROOT / item['path']): item['sha256'] for item in relocation['files']})
    for source in original['sources']:
        expected[source['config_path']] = source['config_sha256']
        expected[source['env_path']] = source['env_sha256']
        expected[str(Path(source['root']) / 'SOCIETY_STEP.json')] = source['clock_sha256']
        expected.update({s['path']: s['sha256'] for s in source['agents'] + source['replay']})
    for plan in (read(E3 / 'runs/timestamp_bdr_v1_attempt_02/runtime_plan.json'), manifest):
        for p, h in plan['source_sha256'].items():
            assert sha(resolve_asset_path(p)) == h, p
            expected[str(resolve_asset_path(p))] = h
    for plan in (old_manifest, manifest):
        for p, h in plan['output_sha256'].items():
            assert sha(resolve_asset_path(p)) == h, p
            expected[str(resolve_asset_path(p))] = h
    used_hashes = {}
    def checked(path, require_expected=True):
        path = Path(path).resolve()
        digest = sha(path)
        if require_expected:
            assert str(path) in expected, ('source not in frozen index', str(path))
            assert digest == expected[str(path)], ('source changed', str(path))
        used_hashes[str(path.relative_to(ROOT))] = digest
        return digest

    compatibility = []
    for task in tasks:
        checked(task['config'])
        full_config = E2 / f'init/configs/timestamp_v1_interest_s{task["seed"]}.json'
        if task['condition'] != 'full':
            full = normalized(read(full_config)); variant = normalized(read(task['config']))
            parameter = {'no_b': 'baseline_utility', 'no_d': 'spiral_scale', 'no_r': 'decay'}[task['condition']]
            for agent, reference in zip(variant['agents'], full['agents']):
                assert agent['agent_id'] == reference['agent_id'] and agent['kwargs']['params'][parameter] == 0
                agent['kwargs']['params'][parameter] = reference['kwargs']['params'][parameter]
            assert variant == full, task['run_id']
            assert sha(E3 / f'init/steps_s{task["seed"]}.yaml') == sha(E2 / f'init/steps_s{task["seed"]}.yaml')
            compatibility.append({'run_id': task['run_id'], 'paired_seed': task['seed'],
                                  'only_scientific_parameter': parameter, 'inputs_schedule_and_steps_equal': True})

    # 先核验查询会读取的replay文件；80条SQL只读，不启动仿真。
    for task in tasks:
        directory = task['directory']
        for path in [directory / 'replay/_schema.json', *sorted((directory / 'replay').glob('*.jsonl'))]:
            checked(path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        replay = list(pool.map(query, tasks))

    run_rows = []; weekly_rows = []; source_rows = []
    for task, sql in zip(tasks, replay):
        condition = task['condition']; seed = task['seed']; directory = task['directory']
        env_path = directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json'
        checked(env_path); checked(directory / 'SOCIETY_STEP.json')
        assert read(directory / 'SOCIETY_STEP.json')['completed_step_count'] == 693
        env = read(env_path); arrival = env['_arrival_state']
        assert len(arrival['actions']) == 1100 and len(arrival['weeks']) == 11
        assert [w['week'] for w in arrival['weeks']] == WEEKS
        action_map = {(str(a['agent_id']), a['week']): a for a in arrival['actions']}
        assert len(action_map) == 1100
        agent_files = sorted((directory / 'agents').glob('*/AGENT.json'))
        assert len(agent_files) == 100
        records = []; population = Counter(); models = Counter(); unique = set(); post_ids = []
        historical_generation_errors = []
        config_profiles = {str(a['agent_id']): a['kwargs'] for a in read(task['config'])['agents']}
        for path in agent_files:
            checked(path); agent = read(path); agent_id = str(agent['id']); kind = agent['profile']['agent_type']
            population[kind] += 1
            assert agent['profile'] == config_profiles[agent_id], (task['run_id'], agent_id)
            assert len(agent['decision_log']) == 11
            for row in agent['decision_log']:
                week = row['week']; unique.add((agent_id, week)); action = action_map[(agent_id, week)]
                assert row['reason'] not in ('action_failed', 'publication_failed', 'generation_failed')
                errors = [g['error_type'] for g in row.get('generation_results', []) if g.get('error_type')]
                if errors:
                    # 去R seed6恢复前的Timeout尝试保留在原始日志，最终已成功发布。
                    # 不据此删机会或帖子，也不把历史尝试误记为当前运行的最终失败。
                    assert row['posted'] and row.get('generation_status') == 'service_success'
                    historical_generation_errors.append({'agent_id': agent_id, 'week': week,
                                                         'error_types': errors, 'final_posted': True})
                assert bool(row['posted']) == (row.get('post_id') is not None)
                assert row['acted_at'] == action['acted_at'] and kind == action['agent_type']
                assert action.get('candidate_future', 0) == 0
                if action['feed']:
                    assert row['speak'] == (row['u'] >= row['threshold'])
                else:
                    assert row['reason'] == 'no_context' and not row['posted']
                components = row.get('components') or {}
                if components:
                    if condition == 'no_b': assert components['baseline_utility'] == 0
                    if condition == 'no_d': assert components['spiral'] == 1
                    if condition == 'no_r': assert components['decay'] == 1
                if row['posted']:
                    assert row['speak'] is True; post_ids.append(row['post_id']); models[row['response_model']] += 1
                records.append({'agent_id': agent_id, 'agent_type': kind, 'week': week,
                                'speak': int(row['speak'] is True), 'posted': int(row['posted'] is True),
                                'requests': row['generation_attempts']})
        assert population == POPULATION and len(unique) == len(records) == 1100
        assert len(post_ids) == len(set(post_ids))
        frame = pd.DataFrame(records)
        for week, env_week, replay_week in zip(WEEKS, arrival['weeks'], sql['weekly']):
            assert week == env_week['week'] == replay_week['week']
            for field, value in replay_week.items(): assert value == env_week[field]
            for kind in TYPES:
                group = frame[(frame.week == week) & (frame.agent_type == kind)]
                replay_agent = next(r for r in sql['agent'] if r['step'] == WEEKS.index(week) + 1 and r['agent_type'] == kind)
                assert len(group) == replay_agent['opportunities'] == POPULATION[kind]
                assert int(group.speak.sum()) == replay_agent['spoke']
                assert int(group.posted.sum()) == env_week[f'agent_supply_{kind}']
                weekly_rows.append({'condition': condition, 'seed': seed, 'run_id': task['run_id'],
                                    'week': week, 'agent_type': kind, 'opportunities': len(group),
                                    'speak': int(group.speak.sum()), 'posted': int(group.posted.sum())})
        late = frame[frame.week.isin(LATE)]; mid = frame[frame.week.isin(MID)]
        meme = late[late.agent_type == 'meme']
        assert len(late) == 400 and len(mid) == 500 and len(meme) == 76
        # 图5e沿用旧图的全部meme标签内容口径，包含外部帖和生成帖。
        other_feed = [p for action in arrival['actions']
                      if action['week'] in LATE and action['agent_type'] != 'meme'
                      for p in action['feed']]
        assert len(other_feed) == 3240
        exposure_numerator = sum(p['type'] == 'meme' for p in other_feed)
        total_late = int(late.posted.sum()); meme_late = int(meme.posted.sum())
        values = {'condition': condition, 'seed': seed, 'run_id': task['run_id'],
                  'total_posts': int(frame.posted.sum()), 'total_speak': int(frame.speak.sum()),
                  'requests': int(frame.requests.sum()), 'late_posts': total_late,
                  'late_posts_per_week': total_late / 4,
                  'late_meme_speak': int(meme.speak.sum()), 'late_meme_posted': meme_late,
                  'late_meme_speak_rate': float(meme.speak.sum() / 76),
                  'late_meme_post_rate': float(meme.posted.sum() / 76),
                  'mid_speak': int(mid.speak.sum()), 'mid_posted': int(mid.posted.sum()),
                  'mid_speak_rate': float(mid.speak.sum() / 500),
                  'mid_post_rate': float(mid.posted.sum() / 500),
                  'late_meme_author_share': meme_late / total_late,
                  'late_meme_exposure_non_meme_numerator': exposure_numerator,
                  'late_meme_exposure_non_meme_denominator': len(other_feed),
                  'late_meme_exposure_non_meme': exposure_numerator / len(other_feed)}
        if seed >= 3 and condition != 'full':
            assert values['total_posts'] == completed[task['run_id']]['posted']
        run_rows.append(values)
        source_rows.append({'condition': condition, 'seed': seed, 'run_id': task['run_id'],
                            'run_dir': str(directory.relative_to(ROOT)), 'config': str(task['config'].relative_to(ROOT)),
                            'config_sha256': sha(task['config']), 'env_sha256': sha(env_path),
                            'clock_sha256': sha(directory / 'SOCIETY_STEP.json'),
                            'response_models': dict(models), 'environment_actions': 1100,
                            'unique_agent_decisions': 1100, 'weeks': 11, 'replay_verified': True,
                            'historical_generation_errors': historical_generation_errors})

    runs = pd.DataFrame(run_rows)
    assert runs[(runs.seed >= 3) & (runs.condition != 'full')].total_posts.sum() == 6206
    assert runs[(runs.seed < 3) & (runs.condition != 'full')].total_posts.sum() == 2652
    rows = []
    specs = [('a', 'late_posts_per_week', 'no_b', 'all', 'weeks', 'posts_per_week'),
             ('b', 'late_meme_speak_rate', 'no_d', 'meme', 'expression_opportunities', 'proportion'),
             ('c', 'mid_speak_rate', 'no_r', 'all', 'expression_opportunities', 'proportion'),
             ('d', 'late_meme_author_share', 'no_r', 'meme', 'successful_agent_posts', 'proportion'),
             ('e', 'late_meme_exposure_non_meme', 'no_r', 'non_meme', 'feed_slots', 'proportion')]
    for panel, metric, comparison, cohort, denominator_unit, unit in specs:
        for condition in ('full', comparison):
            for seed in range(10):
                row = runs[(runs.condition == condition) & (runs.seed == seed)].iloc[0]
                numerator, denominator = {
                    'a': (int(row.late_posts), 4),
                    'b': (int(row.late_meme_speak), 76),
                    'c': (int(row.mid_speak), 500),
                    'd': (int(row.late_meme_posted), int(row.late_posts)),
                    'e': (int(row.late_meme_exposure_non_meme_numerator), 3240),
                }[panel]
                assert np.isclose(numerator / denominator, row[metric])
                rows.append({'panel': panel, 'metric': metric, 'comparison': comparison,
                             'condition': condition, 'condition_label': {'full': 'Full', 'no_b': 'B = 0', 'no_d': 'D = 1', 'no_r': 'R = 1'}[condition],
                             'seed': seed, 'run_id': row.run_id,
                             'week_start': '2026-W14' if panel == 'c' else '2026-W19',
                             'week_end': '2026-W18' if panel == 'c' else '2026-W22',
                             'cohort': cohort, 'numerator': numerator, 'denominator': denominator,
                             'denominator_unit': denominator_unit, 'unit': unit, 'value': float(row[metric])})
    metrics = pd.DataFrame(rows); assert len(metrics) == 100
    old = pd.read_csv(OUT / 'deferred_ablation/source_data/ablation_metrics.csv')
    # 旧图5b/c成功发帖率在这批无发布失败的结果中等于预设speak率。
    join = metrics[metrics.seed < 3].merge(old, on=['panel', 'condition', 'seed'], suffixes=('_new', '_old'))
    assert len(join) == 30 and np.allclose(join.value_new, join.value_old, atol=1e-11)
    outputs = {'ablation_seed10_metrics.csv': metrics,
               'ablation_seed10_runs.csv': runs,
               'ablation_seed10_weekly.csv': pd.DataFrame(weekly_rows)}
    for filename, frame in outputs.items(): frame.to_csv(DATA / filename, index=False, float_format='%.15g')
    summary = []
    for panel, metric, comparison, *_ in specs:
        selected = metrics[metrics.panel == panel].pivot(index='seed', columns='condition', values='value')
        factor = 1 if panel == 'a' else 100
        delta = (selected[comparison] - selected['full']) * factor
        summary.append({'panel': panel, 'metric': metric, 'comparison': comparison,
                        'full_mean': float(selected['full'].mean() * factor),
                        'ablation_mean': float(selected[comparison].mean() * factor),
                        'paired_delta_mean': float(delta.mean()), 'paired_delta_min': float(delta.min()),
                        'paired_delta_max': float(delta.max()), 'n_paired_seeds': 10})
    source = {'created_at': datetime.now(timezone.utc).isoformat(),
              'scope': '40 completed run units; 10 reused Full + 30 completed ablations; seeds 0–9',
              'runs': source_rows, 'scientific_comparability': compatibility,
              'old30_panel_values_reproduced': True,
              'integrity': {'run_units': 40, 'unique_agent_decisions': 44000, 'agent_files': 4000,
                            'new21_successful_posts': 6206, 'old9_successful_posts': 2652,
                            'all_used_files_matched_existing_frozen_or_relocation_sha256': True},
              'source_sha256': used_hashes, 'script_sha256': sha(Path(__file__)),
              'output_sha256': {name: sha(DATA / name) for name in outputs},
              'query': {'weekly': 'curation_dynamics_env_state weekly supply', 'agent': 'curation_dynamics_agent_state step/type opportunity and spoke'},
              'model_equivalence': '用户已确认研究内等价；保留逐run真实返回标识，不声称后台权重相同',
              'excluded': 'Only completed.run_dir selected; failed no_b seed7 and interrupted predecessors excluded',
              'panel_e_definition': 'All meme-labelled feed slots for non-meme authors; external and generated posts included',
              'network': 'Official replay subprocesses guarded by existing offline sitecustomize; no LLM calls',
              'primary_comparison': 'Ablation minus same-seed Full; means computed after per-run window aggregation'}
    save(DATA / 'ablation_seed10_sources.json', source)
    check = {'passed': True, 'run_units': 40, 'unique_agent_decisions': 44000,
             'agent_files': 4000, 'new21_successful_posts': 6206, 'old9_successful_posts': 2652,
             'all_ablation_successful_posts': 8858, 'replay_environment_agent_crosschecks': 40,
             'source_files_fingerprinted': len(used_hashes), 'old30_panel_values_reproduced': True,
             'model_calls_added': 0, 'summary': summary,
             'output_sha256': {name: sha(DATA / name) for name in outputs}}
    save(QA / 'fig5_extraction.json', check)
    print(json.dumps(check, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
