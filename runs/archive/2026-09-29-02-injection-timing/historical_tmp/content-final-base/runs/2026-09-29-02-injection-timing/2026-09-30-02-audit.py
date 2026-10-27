"""只读运行审计与预登记指标：检查时间、机会、发布和周统计的守恒。

运行中仅用已提交环境批次判断曝光，完整前缀/全窗时核对Agent账本。
缺记录会报错，合法空feed计入主指标的计划机会分母。
"""
import json
import importlib.util
from collections import Counter
from datetime import datetime
from pathlib import Path


# 新内容账本与生产门控共用分类核对；旧记录保留原审计语义。
_quality_path = Path(__file__).resolve().parents[2] / 'custom/agents/curation_content_quality.py'
_quality_spec = importlib.util.spec_from_file_location('audit_content_quality', _quality_path)
quality = importlib.util.module_from_spec(_quality_spec)
_quality_spec.loader.exec_module(quality)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return {} if default is None else default


def metrics(rows):
    """返回Y/S/E/A；调用方先验收行动完备性，空分母记None。"""
    opportunities = len(rows)
    slots = sum(len(r['feed']) for r in rows)
    observed = sum(p['type'] == 'meme' for r in rows for p in r['feed'])
    expected = sum(len(r['feed']) * r['candidate_meme'] / r['candidate_count'] if r['candidate_count'] else 0 for r in rows)
    return {'J': opportunities, 'slots': slots, 'O': observed, 'E': expected,
            'Y': observed / opportunities if opportunities else None,
            'S': observed / slots if slots else None,
            'A': (observed - expected) / slots if slots else None}


def audit(run_dir, run, expected_batches=None):
    root = Path(run_dir)
    step = read_json(root / 'SOCIETY_STEP.json')
    state = read_json(root / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    arrival = state.get('_arrival_state') or {}
    actions = arrival.get('actions', [])
    weeks = arrival.get('weeks', [])
    failures = []
    keys = [(r['agent_id'], r['week']) for r in actions]
    if len(keys) != len(set(keys)):
        failures.append('duplicate actions')
    exposure_total, future_slots, future_prompts = 0, 0, 0
    future_actions, advances = set(), []
    for row in actions:
        t = datetime.fromisoformat(row['acted_at'])
        exposure_total += len(row['feed'])
        for index, p in enumerate(row['feed']):
            pub = datetime.fromisoformat(p['published_at'])
            if datetime.fromisoformat(p['available_at']) > t:
                failures.append('exposure before availability')
            if p['source'] == 'agent' and p['week'] >= row['week']:
                failures.append('same week agent exposure')
            if pub > t:
                if p['is_official'] or run['arrival_mode'] == 'timestamp':
                    failures.append('forbidden future exposure')
                future_slots += 1
                future_prompts += index < 5
                future_actions.add((row['agent_id'], row['week']))
                advances.append((pub-t).total_seconds())
    # 在已完成边界核对精确机会矩阵及成功帖子账本，不接受中批checkpoint续跑。
    decisions = []
    decision_pairs = []
    for path in sorted((root / 'agents').glob('*/AGENT.json')):
        doc = read_json(path)
        aid = str(doc.get('id'))
        for r in doc.get('decision_log', []):
            decisions.append(r)
            decision_pairs.append((aid, r['week']))
            if r.get('reason') in ('action_failed', 'generation_failed', 'publication_failed'):
                failures.append(r['reason'])
    content_ledger = quality.ledger_summary(decisions)
    failures.extend(content_ledger['failures'])
    actual_prompt_future = 0
    for decision in decisions:
        if decision.get('generation_attempts', 0) > 0:
            t = datetime.fromisoformat(decision['acted_at'])
            actual_prompt_future += sum(datetime.fromisoformat(p['published_at']) > t for p in decision.get('prompt_context', []))
    models = sorted({r['response_model'] for r in decisions if r.get('response_model')})
    if len(models) > 1:
        failures.append('response model changed within run')
    posted_ids = [r.get('post_id') for r in decisions if r.get('posted')]
    if expected_batches is not None:
        expected_weeks = expected_batches // 63
        if step.get('step_count') != expected_batches or state.get('_chronological_batch_index') != expected_batches:
            failures.append('batch count mismatch')
        if len(actions) != expected_weeks * 100 or len(weeks) != expected_weeks:
            failures.append('action/week count mismatch')
        if sorted(keys) != sorted(decision_pairs):
            failures.append('agent/env checkpoint action mismatch')
        week_counts = Counter(r['week'] for r in actions)
        expected_labels = [f'2026-W{12+i:02d}' for i in range(expected_weeks)]
        if dict(week_counts) != dict.fromkeys(expected_labels, 100):
            failures.append('week opportunity matrix mismatch')
        schedule = read_json(Path(__file__).resolve().parents[2] / 'hypothesis_4/experiment_1/init/arrival_timing_diagnostic/action_schedule.json')
        hours = schedule.get('action_hours', schedule.get('chronological_action_hours', schedule))
        for r in actions:
            t = datetime.fromisoformat(r['acted_at'])
            if int(hours[str(r['agent_id'])]) != t.weekday()*24+t.hour:
                failures.append('action schedule mismatch')
        ledger_ids = [int(pid) for pid, p in state.get('_posts', {}).items() if p.get('source') == 'agent']
        ledger_ids += [p['post_id'] for p in arrival.get('delayed', [])]
        if sorted(posted_ids) != sorted(ledger_ids) or len(set(posted_ids)) != len(posted_ids):
            failures.append('publication ledger mismatch')
        if sum(r['agent_supply'] for r in weeks) != len(posted_ids):
            failures.append('weekly publication mismatch')
        if sum(r['total_exposures'] for r in weeks) != exposure_total:
            failures.append('weekly exposure mismatch')
        if expected_batches == run['expected_batches'] and len(state.get('_injected_source_keys', [])) != 267:
            failures.append('external record count mismatch')
    return {'batches': step.get('step_count', 0), 'actions': len(actions), 'weeks': len(weeks),
            'published': len(posted_ids), 'exposures': exposure_total, 'future_slots': future_slots,
            'potential_context_future_slots': future_prompts, 'future_prompt_slots': actual_prompt_future, 'future_action_count': len(future_actions),
            'advance_seconds_mean': sum(advances)/len(advances) if advances else None,
            'advance_seconds_max': max(advances) if advances else None,
            'response_models': models, 'generation_attempts': sum(r.get('generation_attempts', 0) for r in decisions),
            'content_ledger': content_ledger, 'failures': sorted(set(failures)), 'late_metrics': metrics([r for r in actions if r['week'] >= '2026-W19'])}
