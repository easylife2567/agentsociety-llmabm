"""18次扩种全部完成后的离线复核和原始结果保全；不启动或恢复实验。"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import run_extension as control

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'pilot'))
from analyze_pilot import audit_recirculation, TYPES, WEEKS

read, digest, require = control.read, control.digest, control.require
FIELDS = ('week', 'agent_supply', *(f'agent_supply_{kind}' for kind in TYPES),
          'total_exposures', 'exposure_meme')
SQL = 'SELECT ' + ', '.join(FIELDS) + ' FROM curation_dynamics_env_state ORDER BY week'
STABLE_RESULT_KEYS = ('run_id', 'algorithm', 'run_dir', 'steps', 'actions', 'weeks',
                     'agent_files', 'decisions', 'unique_decisions', 'posted', 'requests',
                     'action_failures', 'service_failures', 'posted_model_failures',
                     'response_models', 'invalid_publications', 'expected_returned_model')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def verify_run(row, expected_model, workspace, proofs):
    directory = Path(row['run_dir']).resolve()
    result = control.final_result(directory, row, expected_model)
    step = read(directory / 'SOCIETY_STEP.json')
    require(step['completed_step_count'] == 693, '已完成步数不是693')
    env_path = directory / 'env/CurationDynamicsSpace/state/ENV_STATE.json'
    env = read(env_path)
    arrival = env['_arrival_state']
    require([r['week'] for r in arrival['weeks']] == list(WEEKS), '周顺序或数量不完整')
    audit = audit_recirculation(env)
    require(len(result['raw_sha256']) == 103, '完成快照应包含103份核心原始文件')
    counts, publications = Counter(), {}
    for path in sorted((directory / 'agents').glob('*/AGENT.json')):
        agent = read(path)
        aid, kind = str(agent['profile']['id']), agent['profile']['agent_type']
        require(kind in TYPES and str(agent['id']) == aid, 'Agent身份或作者类型不符')
        require(len(agent['decision_log']) == 11 and
                {r['week'] for r in agent['decision_log']} == set(WEEKS), '单人11周决策不完整')
        for decision in agent['decision_log']:
            if decision.get('posted'):
                pid = str(decision['post_id'])
                require(pid not in publications and decision['response_model'] == expected_model,
                        '发布ID重复或正文模型不符')
                publications[pid] = dict(author=aid, content=decision['content'], kind=kind,
                                        week=decision['week'])
                counts[(decision['week'], kind)] += 1
    pool = {str(pid): post for pid, post in env['_posts'].items() if post.get('source') == 'agent'}
    require(set(publications) == set(pool), '成功发布ID集合与环境生成帖集合不一致')
    for pid, item in publications.items():
        post = pool[pid]
        require(str(post['author_id']) == item['author'] and post['content'] == item['content']
                and post['type'] == item['kind'] and post['source_week'] == item['week'],
                '发布正文、作者类型或周与环境不一致')
    for week in arrival['weeks']:
        require(week['agent_supply'] == sum(counts[(week['week'], kind)] for kind in TYPES)
                and all(week[f'agent_supply_{kind}'] == counts[(week['week'], kind)] for kind in TYPES),
                '五类周供给或总供给不守恒')
        actions = [a for a in arrival['actions'] if a['week'] == week['week']]
        feed = [post for action in actions for post in action['feed']]
        require(len(feed) == week['total_exposures'] and
                sum(post['type'] == 'meme' for post in feed) == week['exposure_meme'], '周曝光不守恒')
    query_env = dict(os.environ, WORKSPACE_PATH=str(workspace), LITELLM_LOCAL_MODEL_COST_MAP='True',
                     MEM0_TELEMETRY='False', ANONYMIZED_TELEMETRY='False')
    query = subprocess.run([sys.executable, str(workspace / '.agentsociety/bin/ags.py'),
                            'analysis', 'query-data', '--data-path', str(directory / 'replay'),
                            '--sql', SQL], cwd=workspace, env=query_env, capture_output=True,
                           text=True, check=True)
    payload = json.loads(query.stdout)
    require(payload.get('success') is True, '官方只读replay查询失败')
    replay = [dict(zip(payload['columns'], values)) for values in payload['rows']]
    require([[r[key] for key in FIELDS] for r in replay] ==
            [[r[key] for key in FIELDS] for r in arrival['weeks']], 'replay周表与环境记录不一致')
    proofs.update({str(directory / name): sha for name, sha in result['raw_sha256'].items()})
    return result, audit


def snapshot_files(directory):
    files, folders = {}, []
    for path in sorted(directory.rglob('*')):
        require(not path.is_symlink(), '原始输出含符号链接，保留现场并人工核对：' + str(path))
        if path.is_file():
            files[path.relative_to(directory).as_posix()] = digest(path)
        elif path.is_dir():
            folders.append(path.relative_to(directory).as_posix())
    return files, folders


def mirror_check(source, target, files, folders, check_only):
    require(not target.is_symlink() and target.resolve().is_relative_to(HERE / 'results'), '结果镜像路径逃逸')
    if target.exists():
        require(target.is_dir(), '镜像目标不是目录')
        existing, existing_folders = snapshot_files(target)
        require(set(existing) <= set(files) and set(existing_folders) <= set(folders), '镜像出现未登记资产')
        require(all(files[name] == sha for name, sha in existing.items()), '已有镜像内容冲突，拒绝覆盖')
    else:
        existing, existing_folders = {}, []
    if check_only:
        require(existing == files and set(existing_folders) == set(folders), '镜像缺失或不完整')


def prepare():
    plan_path, state_path = HERE / 'runtime_plan.json', HERE / 'batch_execution.json'
    plan, state = read(plan_path), read(state_path)
    runs = control.matrix(plan)
    require(state['status'] == 'completed' and state.get('active_runs') == []
            and not state.get('children_needing_attention'), '18次尚未全部完成或仍有活跃引擎')
    require(len(state['completed']) == 18 and
            {r['run_id'] for r in state['completed']} == {r['run_id'] for r in runs}, '完成登记不精确覆盖18条件')
    require(state['runtime_plan_sha256'] == digest(plan_path), '完成状态与原计划不一致')
    require(state['expected_returned_model'] == plan['expected_returned_model'] == 'deepseek-v4-1-flash-261017',
            '正文模型不符')
    control.frozen_sources(plan)
    workspace = Path(plan['workspace']).resolve()
    output_root = workspace / 'hypothesis_4/experiment_2/runs/hourly_return_v1'
    require(not (HERE / 'results').is_symlink(), '镜像根不能是符号链接')
    completed = {r['run_id']: r for r in state['completed']}
    proofs = {str(path): digest(path) for path in (plan_path, state_path, Path(__file__))}
    rows, mirrors = [], []
    for run in runs:
        source = Path(run['run_dir']).resolve()
        require(source.parent == output_root and source.name == run['run_id'], '新结果目录越出固定输出根')
        result, audit = verify_run(run, plan['expected_returned_model'], workspace, proofs)
        completion_path = HERE / f"completion_{run['run_id']}.json"
        stored = read(completion_path)
        proofs[str(completion_path)] = digest(completion_path)
        require(stored == completed[run['run_id']], '逐run完成文件与批次登记不同')
        require(all(stored.get(key) == result.get(key) for key in STABLE_RESULT_KEYS)
                and stored['raw_sha256'] == result['raw_sha256'], '完成数值或103项原始SHA与实际结果不同')
        target = HERE / 'results' / run['run_id']
        files, folders = snapshot_files(source)
        mirrors.append(dict(run_id=run['run_id'], algorithm=run['algorithm'], seed=run['seed'],
                            source_run_dir=str(source), preserved_run_dir=str(target),
                            files_sha256=files, directories=folders))
        rows.append(summary_row(run, result, source, target, 'new_seed1_to9', audit))
    control.validate_reuse(plan)
    for run in plan['reuse_runs']:
        source = Path(run['run_dir']).resolve()
        require(source == HERE.parent / f"pilot/results/{run['run_id']}", 'seed0来源不属于已冻结pilot镜像')
        result, audit = verify_run(run, plan['expected_returned_model'], workspace, proofs)
        require(all(digest(source / name) == sha for name, sha in run['raw_sha256'].items()), 'seed0复用来源改变')
        rows.append(summary_row(run, result, source, source, 'reused_pilot_seed0', audit))
    rows.sort(key=lambda r: (r['seed'], control.ALGORITHMS.index(r['algorithm'])))
    require(len(rows) == 20, '20个比较条件不完整')
    new = [r for r in rows if r['origin'] == 'new_seed1_to9']
    reused = [r for r in rows if r['origin'] == 'reused_pilot_seed0']
    new_requests = sum(r['body_outer_requests'] for r in new)
    reused_requests = sum(r['body_outer_requests'] for r in reused)
    extra = int(Path(plan['ledger_path']).read_text() or '0')
    require(new_requests == state['total_body_requests'] and extra == state['extra_requests_used']
            and 0 <= extra <= 1980 and new_requests <= 21780, '新批实际用量与状态或上界不符')
    pilot_state_path = HERE.parent / 'pilot/batch_execution.json'
    pilot_state = read(pilot_state_path)
    historical = plan['pilot_preserved_body_requests']
    withdrawn = plan['withdrawn_chronological_historical_body_requests']
    require(reused_requests == plan['reused_seed0_historical_body_requests']
            and historical == reused_requests + withdrawn == pilot_state['total_body_requests']
            and withdrawn == pilot_state['withdrawn_body_requests'], 'pilot复用与撤回消耗账不一致')
    proofs[str(pilot_state_path)] = digest(pilot_state_path)
    raw_manifest = dict(status='passed', batch_id=plan['batch_id'],
                        completed_at=state['finished_at'], new_runs=18, copied_seed0=False,
                        runs=mirrors, verification_sources_sha256=proofs)
    summary = dict(status='passed', batch_id=plan['batch_id'], completed_at=state['finished_at'],
                   new_runs=18, reused_seed0_runs=2, comparison_runs=20, new_decision_opportunities=19800,
                   reused_seed0_decision_opportunities=2200, actual_models=[plan['expected_returned_model']],
                   new_body_outer_requests=new_requests, new_extra_requests=extra,
                   new_body_outer_requests_limit=21780, new_extra_requests_limit=1980,
                   reused_seed0_body_outer_requests=reused_requests,
                   withdrawn_chronological_historical_body_outer_requests=withdrawn,
                   prior_pilot_body_outer_requests=historical,
                   scientific_comparison_body_outer_requests=new_requests + reused_requests,
                   cross_batch_body_outer_requests_including_withdrawn=new_requests + historical,
                   usage_scope='正文外层请求；不是全部SDK调用或token账单。新批预算不混入旧410消耗。',
                   runs=rows, source_sha256=proofs)
    columns = ('algorithm', 'seed', 'origin', 'run_id', 'posts', 'body_outer_requests', 'steps',
               'actions', 'decisions', 'weeks', 'agents', 'actual_models', 'source_run_dir', 'preserved_run_dir')
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    products = {HERE / 'raw_results_manifest.json': encoded(raw_manifest),
                HERE / 'completion_summary.json': encoded(summary),
                HERE / 'completion_runs.csv': stream.getvalue().encode('utf-8')}
    return mirrors, products


def summary_row(run, result, source, target, origin, audit):
    return dict(algorithm=run['algorithm'], seed=run['seed'], origin=origin, run_id=run['run_id'],
                posts=result['posted'], body_outer_requests=result['requests'], steps=result['steps'],
                actions=result['actions'], decisions=result['decisions'], weeks=result['weeks'],
                agents=result['agent_files'], actual_models='|'.join(sorted(result['response_models'])),
                source_run_dir=str(source), preserved_run_dir=str(target), recirculation_audit=audit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只重算和核对已有产物/镜像，不写文件')
    args = parser.parse_args()
    mirrors, products = prepare()
    for path, data in products.items():
        require(not path.exists() or path.read_bytes() == data, '已有收尾产物不一致，拒绝覆盖：' + str(path))
        require(not args.check or path.exists(), '收尾产物尚不存在：' + str(path))
    for item in mirrors:
        mirror_check(Path(item['source_run_dir']), Path(item['preserved_run_dir']),
                     item['files_sha256'], item['directories'], args.check)
    if not args.check:
        for item in mirrors:
            source, target = Path(item['source_run_dir']), Path(item['preserved_run_dir'])
            target.mkdir(parents=True, exist_ok=True)
            for directory in item['directories']:
                (target / directory).mkdir(parents=True, exist_ok=True)
            for name, expected in item['files_sha256'].items():
                destination = target / name
                require(digest(source / name) == expected, '复制前原始文件已改变')
                if not destination.exists():
                    with destination.open('xb') as stream, (source / name).open('rb') as original:
                        shutil.copyfileobj(original, stream)
                require(digest(destination) == expected, '原始镜像哈希不一致')
        for path, data in products.items():
            if not path.exists():
                with path.open('xb') as stream:
                    stream.write(data)
    print(json.dumps(dict(status='passed', mode='check' if args.check else 'closeout',
                         new_runs=18, reused_seed0_runs=2,
                         mirrored_files=sum(len(item['files_sha256']) for item in mirrors),
                         engine_started=False, llm_calls=0), ensure_ascii=False))


if __name__ == '__main__':
    main()
