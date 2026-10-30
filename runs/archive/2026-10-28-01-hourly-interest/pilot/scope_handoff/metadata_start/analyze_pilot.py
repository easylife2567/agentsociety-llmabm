"""所选制度seed0试运行的确定性描述分析；只有全部所选运行完成后才产出。"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys


ARMS = ('random', 'chronological', 'interest')
NAMES = {'random': '随机', 'chronological': '时序', 'interest': '兴趣'}
TYPES = ('marketing', 'mourning', 'other', 'meme', 'education')
WEEKS = tuple(f'2026-W{i:02d}' for i in range(12, 23))
LATE = tuple(f'2026-W{i:02d}' for i in range(19, 23))
REPLAY_SQL = ('SELECT week, agent_supply, agent_supply_meme, total_exposures, exposure_meme '
              'FROM curation_dynamics_env_state ORDER BY week')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def moment(value):
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('审计时间戳缺少时区')
    return result


def exposures(actions):
    """曝光均按实际feed条数，不用10槽的理论上限替代分母。"""
    feeds = [post for action in actions for post in action['feed']]
    generated = [post for post in feeds if post['source'] == 'agent']
    external = [post for post in feeds if post['source'] == 'external']
    if len(generated) + len(external) != len(feeds):
        raise ValueError('存在未定义的feed来源')
    own = [post for action in actions if action['agent_type'] == 'meme' for post in action['feed']]
    cross = [post for action in actions if action['agent_type'] != 'meme' for post in action['feed']]
    return dict(
        feed_total=len(feeds), feed_meme_tag=sum(post['type'] == 'meme' for post in feeds),
        feed_meme_tag_share=ratio(sum(post['type'] == 'meme' for post in feeds), len(feeds)),
        feed_agent_total=len(generated), feed_external_total=len(external),
        feed_agent_fraction=ratio(len(generated), len(feeds)),
        feed_agent_meme_tag=sum(post['type'] == 'meme' for post in generated),
        feed_agent_meme_tag_share=ratio(sum(post['type'] == 'meme' for post in generated), len(generated)),
        feed_external_meme_tag=sum(post['type'] == 'meme' for post in external),
        feed_external_meme_tag_share=ratio(sum(post['type'] == 'meme' for post in external), len(external)),
        own_meme_tag_share=ratio(sum(post['type'] == 'meme' for post in own), len(own)),
        cross_generated_meme_share=ratio(sum(post['source'] == 'agent' and post['type'] == 'meme'
                                            for post in cross), len(cross)),
    )


def audit_recirculation(env):
    actions = env['_arrival_state']['actions']
    audit = dict(future_exposures=0, same_batch_agent_exposures=0,
                 agent_exposures=0, available_time_mismatches=0,
                 agent_posts=0, delayed_queue_size=len(env['_arrival_state']['delayed']))
    for action in actions:
        acted = moment(action['acted_at'])
        if action['candidate_future']:
            audit['future_exposures'] += action['candidate_future']
        for post in action['feed']:
            published, available = moment(post['published_at']), moment(post['available_at'])
            if published > acted or available > acted:
                audit['future_exposures'] += 1
            if post['source'] == 'agent':
                audit['agent_exposures'] += 1
                audit['same_batch_agent_exposures'] += published >= acted
                audit['available_time_mismatches'] += available != published
    for post in env['_posts'].values():
        if post.get('source') != 'agent':
            continue
        audit['agent_posts'] += 1
        audit['available_time_mismatches'] += moment(post['available_at']) != moment(post['published_at'])
        if post['source_week'] != post['available_week'] or post['source_week'] != post['injected_week']:
            raise ValueError('生成帖回流周与发布周不一致')
    if any(audit[name] for name in ('future_exposures', 'same_batch_agent_exposures',
                                    'available_time_mismatches', 'delayed_queue_size')):
        raise ValueError(f'小时回流审计未通过：{audit}')
    return audit


def extract_run(run, workspace, source_hashes):
    directory = Path(run['run_dir'])
    if not directory.is_absolute():
        directory = workspace / directory
    directory = directory.resolve()
    if not directory.is_relative_to(workspace):
        raise ValueError('结果目录超出本run隔离workspace')

    def source(path):
        source_hashes[str(path)] = digest(path)
        return read(path)

    pid = source(directory / 'pid.json')
    step = source(directory / 'SOCIETY_STEP.json')
    if pid.get('status') != 'completed' or step.get('step_count') != 693 or step.get('completed_step_count') != 693:
        raise ValueError(f"运行尚未真实完成：{run['run_id']}")
    schema_path = directory / 'replay/_schema.json'
    source_hashes[str(schema_path)] = digest(schema_path)
    env = source(directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json')
    if env.get('_arrival_agent_return_policy') != 'next_batch':
        raise ValueError('结果不属于本次next_batch方案')
    arrival = env['_arrival_state']
    actions, observed_weeks = arrival['actions'], arrival['weeks']
    expected_keys = {(str(aid), week) for aid in range(1, 101) for week in WEEKS}
    actual_keys = {(str(action['agent_id']), action['week']) for action in actions}
    if len(actions) != 1100 or actual_keys != expected_keys:
        raise ValueError('实际行动未完整唯一覆盖100人×11周')
    if [row['week'] for row in observed_weeks] != list(WEEKS):
        raise ValueError('实际周记录不完整或顺序错误')
    audit = audit_recirculation(env)
    counts, speaks, models, origins = Counter(), Counter(), Counter(), Counter()
    population = Counter()
    decisions = []
    body_requests = 0
    agent_paths = sorted((directory / 'agents').glob('*/AGENT.json'))
    if len(agent_paths) != 100:
        raise ValueError('Agent工作区数量不是100')
    ids = set()
    for path in agent_paths:
        agent = source(path)
        aid, kind = str(agent['profile']['id']), agent['profile']['agent_type']
        if aid in ids or kind not in TYPES:
            raise ValueError('Agent身份重复或类型不符')
        ids.add(aid)
        population[kind] += 1
        rows = agent['decision_log']
        if len(rows) != 11 or {row['week'] for row in rows} != set(WEEKS):
            raise ValueError('Agent未完整唯一覆盖11周决策')
        for row in rows:
            if row.get('reason') in ('action_failed', 'publication_failed'):
                raise ValueError('存在行动或发布失败')
            body_requests += row.get('generation_attempts', 0)
            if row.get('speak') is True:
                speaks[(row['week'], kind)] += 1
            if row.get('posted'):
                if not isinstance(row.get('content'), str) or not row['content'].strip() or row.get('post_id') is None:
                    raise ValueError('成功发布缺少正文或post_id')
                post = env['_posts'].get(str(row['post_id']))
                if post is None or str(post['author_id']) != aid or post['source_week'] != row['week']:
                    raise ValueError('Agent发布与实际入池记录不一致')
                if post['content'] != row['content'] or post['type'] != kind:
                    raise ValueError('成功发布正文/作者类型与环境不一致')
                counts[(row['week'], kind)] += 1
                models[row.get('response_model') or 'missing'] += 1
                origins[row.get('content_origin') or 'unspecified'] += 1
            decisions.append((aid, row['week']))
    if set(decisions) != expected_keys or len(decisions) != 1100 or ids != {str(i) for i in range(1, 101)}:
        raise ValueError('决策与行动完整性不一致')
    if audit['agent_posts'] != sum(counts.values()):
        raise ValueError('发布数与入池生成帖总数不守恒')
    weekly = []
    for observed in observed_weeks:
        week = observed['week']
        selected = [a for a in actions if a['week'] == week]
        total = sum(counts[(week, kind)] for kind in TYPES)
        if observed['agent_supply'] != total or any(observed[f'agent_supply_{kind}'] != counts[(week, kind)] for kind in TYPES):
            raise ValueError('周供给与实际成功发布记录不一致')
        exp = exposures(selected)
        if exp['feed_total'] != observed['total_exposures'] or exp['feed_meme_tag'] != observed['exposure_meme']:
            raise ValueError('周曝光与行动快照不一致')
        weekly.append(dict(algorithm=run['algorithm'], seed=0, week=week, decision_opportunities=len(selected),
                           posted_total=total,
                           meme_author_share=ratio(counts[(week, 'meme')], total),
                           meme_author_post_rate=ratio(counts[(week, 'meme')], population['meme']),
                           speak_total=sum(speaks[(week, kind)] for kind in TYPES),
                           **{f'posted_{kind}_authors': counts[(week, kind)] for kind in TYPES}, **exp))
    # 正式只读query-data交叉核对replay表，防止仅凭监督器或单一checkpoint推断结果。
    result = subprocess.run([sys.executable, str(workspace / '.agentsociety/bin/ags.py'),
                             'analysis', 'query-data', '--data-path', str(directory / 'replay'),
                             '--sql', REPLAY_SQL], cwd=workspace, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    if not payload.get('success'):
        raise ValueError('官方replay只读查询未成功')
    replay_rows = [dict(zip(payload['columns'], row)) for row in payload['rows']]
    fields = ('week', 'agent_supply', 'agent_supply_meme', 'total_exposures', 'exposure_meme')
    if [[row[key] for key in fields] for row in replay_rows] != [[row[key] for key in fields] for row in observed_weeks]:
        raise ValueError('官方replay周表与实际环境保存记录不一致')
    late_actions = [action for action in actions if action['week'] in LATE]
    late_meme = sum(counts[(week, 'meme')] for week in LATE)
    late_total = sum(counts[(week, kind)] for week in LATE for kind in TYPES)
    metrics = dict(algorithm=run['algorithm'], seed=0, run_id=run['run_id'], run_dir=str(directory),
                   total_posts=sum(counts.values()), body_outer_requests=body_requests,
                   late_meme_posts=late_meme, late_total_posts=late_total,
                   late_meme_share=ratio(late_meme, late_total),
                   late_meme_post_rate=ratio(late_meme, population['meme'] * len(LATE)),
                   late_exposures=exposures(late_actions),
                   total_exposures=exposures(actions), response_model_counts=dict(models),
                   content_origin_counts=dict(origins), population=dict(population),
                   audit=audit, replay_weekly_verified=True,
                   completion=dict(batches=693, actions=1100, decisions=1100, weeks=11, agents=100))
    return weekly, metrics


def pct(value):
    return '无分母' if value is None else f'{value * 100:.2f}%'


def winners(metrics, field):
    values = {row['algorithm']: row[field] for row in metrics if row[field] is not None}
    if not values:
        return '无可比较分母'
    highest = max(values.values())
    selected = [NAMES[arm] for arm in ARMS if values.get(arm) == highest]
    return '、'.join(selected) + ('并列最高' if len(selected) > 1 else '最高')


def outputs(plan_path, output, selection_path=None):
    plan = read(plan_path)
    if plan.get('execution_authorized') is not True:
        raise ValueError('该计划没有运行授权标记')
    state_path = Path(plan.get('state_path', plan_path.parent / 'batch_execution.json'))
    state = read(state_path)
    if state.get('status') != 'completed':
        raise ValueError('所选制度尚未全部完成；不生成分析产物' if selection_path is not None else '三臂尚未全部完成；不生成分析产物')
    all_runs = plan['runs']
    if len(all_runs) != 3 or {row['algorithm'] for row in all_runs} != set(ARMS) or any(row['seed'] != 0 for row in all_runs):
        raise ValueError('原计划必须完整保留三臂seed0，使用selection显式缩小本次比较范围')
    arms, excluded, excluded_runs = ARMS, (), []
    if selection_path is not None:
        selection = read(selection_path)
        chosen = selection['selected_algorithms']
        omitted = selection['excluded_algorithms']
        if len(chosen) != 2 or set(chosen) != {'random', 'interest'} or omitted != ['chronological']:
            raise ValueError('当前selection仅允许随机/兴趣，明确排除时序')
        arms = tuple(arm for arm in ARMS if arm in chosen)
        excluded = tuple(omitted)
        excluded_runs = state.get('excluded_runs', [])
        if len(excluded_runs) != 1 or excluded_runs[0].get('algorithm') != 'chronological':
            raise ValueError('中止时序的排除记录缺失或不唯一')
        consumed = excluded_runs[0].get('consumed_requests')
        if not isinstance(consumed, int) or isinstance(consumed, bool) or consumed < 0:
            raise ValueError('中止时序必须单列已消耗正文外层请求数')
    runs = [row for row in all_runs if row['algorithm'] in arms]
    scope_name = '随机与兴趣两臂' if selection_path is not None else '三臂'
    if set(plan['analysis_contract']['late_weeks']) != set(LATE):
        raise ValueError('主要观察窗口与已冻结约定不一致')
    if {row['run_id'] for row in state['completed']} != {row['run_id'] for row in runs}:
        raise ValueError('完成登记未精确覆盖所选制度；不得将中止时序混入比较')
    workspace = Path(plan['workspace']).resolve()
    hashes = {str(plan_path): digest(plan_path), str(state_path): digest(state_path), str(Path(__file__).resolve()): digest(Path(__file__).resolve())}
    if selection_path is not None:
        hashes[str(selection_path)] = digest(selection_path)
    weekly, metrics = [], []
    for arm in arms:
        run = next(row for row in runs if row['algorithm'] == arm)
        rows, result = extract_run(run, workspace, hashes)
        weekly.extend(rows)
        metrics.append(result)
        for name in ('config', 'steps'):
            path = Path(run[name])
            hashes[str(path)] = digest(path)
    if len(weekly) != len(arms) * 11:
        raise ValueError('周表不是所选制度×11周')
    models = set().union(*(set(row['response_model_counts']) for row in metrics))
    if len(models) != 1 or 'missing' in models:
        raise ValueError('实际成功正文模型不唯一或有缺失')
    body_requests = sum(row['body_outer_requests'] for row in metrics)
    excluded_requests = sum(row['consumed_requests'] for row in excluded_runs)
    accounted_requests = body_requests + excluded_requests
    if accounted_requests > plan['body_outer_requests_limit']:
        raise ValueError('含已中止制度的正文外层请求超过本pilot预算')
    summary = dict(status='complete',
                   scope='selected-arms-seed0-exploratory-only' if selection_path is not None else 'three-arms-seed0-exploratory-only',
                   selected_algorithms=list(arms), excluded_algorithms=list(excluded),
                   excluded_runs=excluded_runs, selected_body_outer_requests=body_requests,
                   excluded_body_outer_requests=excluded_requests,
                   late_weeks=list(LATE), requested_model=plan['requested_model'],
                   actual_response_models=sorted(models), runs=metrics, total_body_outer_requests=accounted_requests,
                   replay_query=REPLAY_SQL,
                   primary_comparison='fixed-author-type-successful-posts; no semantic recoding',
                   inference='single-seed descriptive comparison; no significance or prediction', source_sha256=hashes)
    table = ['| 制度 | 全窗总发帖 | 晚期玩梗作者发帖 | 晚期总发帖 | 晚期玩梗作者份额 | 晚期玩梗标签曝光份额 |',
             '|---|---:|---:|---:|---:|---:|']
    for row in metrics:
        table.append(f"| {NAMES[row['algorithm']]} | {row['total_posts']} | {row['late_meme_posts']} | {row['late_total_posts']} | {pct(row['late_meme_share'])} | {pct(row['late_exposures']['feed_meme_tag_share'])} |")
    source_table = ['| 制度 | 晚期全部曝光条数 | 其中Agent帖 | Agent帖中玩梗标签份额 | 玩梗作者所见玩梗份额 | 非玩梗作者所见Agent玩梗份额 |', '|---|---:|---:|---:|---:|---:|']
    for row in metrics:
        exp = row['late_exposures']
        source_table.append(f"| {NAMES[row['algorithm']]} | {exp['feed_total']} | {exp['feed_agent_total']} | {pct(exp['feed_agent_meme_tag_share'])} | {pct(exp['own_meme_tag_share'])} | {pct(exp['cross_generated_meme_share'])} |")
    report = '\n'.join([
        f'# 小时回流{scope_name}seed0试运行观察', '',
        f"{scope_name}均从W12初始状态新运行；每臂100人、11周、693批、1100次行动。实际正文返回模型为`{next(iter(models))}`。",
        '本次只有一个seed，结果用于观测当前规则的运行表现，不作显著性检验或跨seed稳定性判断。', '',
        f"主要窗口固定为W19–W22。晚期玩梗型作者发帖数量为{winners(metrics, 'late_meme_posts')}，其供给份额为{winners(metrics, 'late_meme_share')}。数量与份额分别列出，不能只凭份额判断产量。", '',
        *table, '',
        '曝光统计直接汇总实际行动feed，分开标记外部真实帖和Agent生成帖；分母为实际曝光条数。', '',
        *source_table, '',
        f'{scope_name}小时回流审计均通过：生成帖可用时刻与发布时间一致，同批生成帖曝光为0，未来曝光为0，发布与入池数量守恒。这里的入池不等于每条帖子必定被推荐。', '',
        '作者类型是初始化固定身份；供给指标按成功posted计数，不是独立语义判定。feed中的玩梗标签是模型使用的pool type；Agent帖标签来自作者类型，外部帖沿用冻结输入标签。曝光接触也不等于证明全文理解。', '',
        f'本次只比较统一回流下{len(arms)}套完整制度。生命周期、保底、兴趣抽样等原有制度差异保持，不能把臂间差异单独归为排序效应。结果不证明任何制度在所有目标下最优，也不据本seed结果调整参数。', '',
        f"所选制度正文外层请求合计{body_requests}次；已中止排除制度消耗{excluded_requests}次，预算累计{accounted_requests}次。这不是全部SDK请求量或token账单。逐run来源哈希、模型计数和回流审计见summary.json，逐周曲线数据见weekly.csv。", '',
        ('时序已按用户指示中止，其不完整轨迹不进入供给、曝光、排序或图表比较；本次没有自动搬入旧时序结果。' if excluded else ''), '',
    ])
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(weekly[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(weekly)
    return {
        output / 'summary.json': json.dumps(summary, ensure_ascii=False, indent=2) + '\n',
        output / 'weekly.csv': buffer.getvalue(), output / 'report.md': report,
        output / 'README.md': f'# {scope_name}seed0试运行分析\n\n仅在所选制度实际完成并独立核验后生成，不含占位图或预测；排除制度不混入比较。\n\n| 文件 | 用途 |\n|---|---|\n| [report.md](report.md) | 中文描述性观察、口径与限制 |\n| [summary.json](summary.json) | 逐run汇总、回流审计、排除消耗和原始来源SHA256 |\n| [weekly.csv](weekly.csv) | {len(arms)}臂×11周供给与曝光长表，0分母留空 |\n'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--selection', type=Path, help='显式采用所选随机/兴趣两臂修订；不改原运行计划')
    parser.add_argument('--check', action='store_true', help='只读重算并核对已有分析产物')
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    output = (args.output_dir or plan_path.parent / 'analysis').resolve()
    if not output.is_relative_to(plan_path.parent):
        raise ValueError('分析输出只能位于本pilot目录')
    products = outputs(plan_path, output, args.selection.resolve() if args.selection else None)
    if args.check:
        if any(not path.is_file() or path.read_text(encoding='utf-8') != data for path, data in products.items()):
            raise ValueError('分析输出与独立重算不一致')
    else:
        if any(path.exists() for path in products):
            raise ValueError('不覆盖已有分析产物；请先核对来源或使用--check')
        output.mkdir(parents=True, exist_ok=True)
        for path, data in products.items():
            with path.open('x', encoding='utf-8', newline='') as stream:
                stream.write(data)
    print(json.dumps(dict(status='checked' if args.check else 'written', files=len(products), output=str(output)), ensure_ascii=False))


if __name__ == '__main__':
    main()
