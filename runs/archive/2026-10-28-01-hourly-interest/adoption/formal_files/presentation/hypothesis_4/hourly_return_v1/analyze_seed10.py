"""三臂各10seed的只读描述分析；--check复算而不覆盖任何既有产物。"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from copy import deepcopy
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import socket
import statistics
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_MANIFEST = ROOT / "hypothesis_4/experiment_2/runs/hourly_return_v1/manifest.json"

ARMS = ("random", "chronological", "interest")
TYPES = ("meme", "mourning", "education", "marketing", "other")
WEEKS = tuple(f"2026-W{week}" for week in range(12, 23))
LATE = WEEKS[-4:]
PAIRS = (("interest", "random"), ("chronological", "random"), ("interest", "chronological"))
MODEL = "deepseek-v4-1-flash-261017"
OLD_MODEL = "deepseek-v4-1-flash"
MAPPING = dict(zip(TYPES, ("梗文化讨论", "事件悼念讨论", "教育观点讨论", "借势营销", "其他讨论")))
REPLAY_FIELDS = ("week", "agent_supply", *[f"agent_supply_{kind}" for kind in TYPES],
                 "total_exposures", *[f"exposure_{kind}" for kind in (*TYPES, "noise")])
REPLAY_SQL = "SELECT " + ", ".join(REPLAY_FIELDS) + " FROM curation_dynamics_env_state ORDER BY week"
# 子进程仍调用官方只读CLI，导入前阻断Python网络连接，不改变项目文件。
OFFLINE_QUERY = """import runpy, socket, sys
def deny(*args, **kwargs):
    raise RuntimeError('offline analysis forbids network connections')
socket.socket.connect = deny
socket.socket.connect_ex = deny
socket.create_connection = deny
entry = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(entry, run_name='__main__')
"""


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def encode_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def descriptive(values, seeds=None):
    values = [float(value) for value in values]
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("统计必须使用非空有限的完整seed指标")
    result = dict(n=len(values), mean=statistics.fmean(values),
                  sample_sd=statistics.stdev(values) if len(values) > 1 else None,
                  min=min(values), max=max(values))
    if seeds is not None:
        result.update(seeds=list(seeds), values=values)
    return result


def stability(metrics, seeds, pairs=PAIRS):
    """统计单位为配对seed；较小DTW胜出，差值方向固定为first-minus-second。"""
    seeds = tuple(seeds)
    lookup = {(r["algorithm"], r["seed"]): r for r in metrics}
    by_arm = {arm: descriptive([lookup[arm, seed]["dtw_x100"] for seed in seeds], seeds) for arm in ARMS}
    pair_rows, pair_summary = [], {}
    for first, second in pairs:
        deltas, wins = [], Counter()
        for seed in seeds:
            left, right = (lookup[arm, seed]["dtw_x100"] for arm in (first, second))
            delta = left - right
            winner = "tie" if abs(delta) <= 1e-12 else first if delta < 0 else second
            wins[winner] += 1
            deltas.append(delta)
            pair_rows.append(dict(first=first, second=second, seed=seed, first_dtw_x100=left,
                                  second_dtw_x100=right, delta_first_minus_second=delta, winner=winner))
        pair_summary[f"{first}_vs_{second}"] = dict(
            first=first, second=second, delta_direction="first minus second; negative favors first",
            **descriptive(deltas, seeds), first_wins=wins[first], second_wins=wins[second], ties=wins["tie"])
    ranks = {arm: Counter({"1": 0, "2": 0, "3": 0}) for arm in ARMS}
    per_seed = []
    for seed in seeds:
        values = {arm: lookup[arm, seed]["dtw_x100"] for arm in ARMS}
        ranking = {arm: 1 + sum(other < value - 1e-12 for other in values.values()) for arm, value in values.items()}
        for arm, rank in ranking.items():
            ranks[arm][str(rank)] += 1
        per_seed.append(dict(seed=seed, dtw_x100=values, ranks=ranking,
                             best_arms=[arm for arm in ARMS if ranking[arm] == 1]))
    return dict(seeds=list(seeds), dtw_by_arm=by_arm, paired_comparisons=pair_summary,
                rank_frequency={arm: dict(ranks[arm]) for arm in ARMS}, rankings_per_seed=per_seed), pair_rows


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


def extract(descriptor):
    arm, seed = descriptor["algorithm"], descriptor["seed"]
    directory, frozen = Path(descriptor["run_dir"]), descriptor["frozen"]
    sources = {}

    def track(path):
        actual = digest(path)
        relative = path.relative_to(directory).as_posix()
        if relative not in frozen or actual != frozen[relative]:
            raise ValueError(f"来源未冻结或已改变：{path}")
        sources[str(path)] = actual
        return path

    def load(name):
        return read(track(directory / name))

    pid, step = load("pid.json"), load("SOCIETY_STEP.json")
    if pid["status"] != "completed" or step["completed_step_count"] != 693 or step["step_count"] != 693:
        raise ValueError(f"{arm}/s{seed}未实际完成693步")
    env = load("env/CurationDynamicsSpace/state/ENV_STATE.json")
    if arm != "chronological" and env.get("_arrival_agent_return_policy") != "next_batch":
        raise ValueError("随机/兴趣必须使用本次next_batch结果")
    audit = audit_recirculation(env)
    actions, observed = env["_arrival_state"]["actions"], env["_arrival_state"]["weeks"]
    expected = {(str(aid), week) for aid in range(1, 101) for week in WEEKS}
    if len(actions) != 1100 or {(str(a["agent_id"]), a["week"]) for a in actions} != expected:
        raise ValueError("环境行动未唯一完整覆盖100人×11周")
    if [row["week"] for row in observed] != list(WEEKS):
        raise ValueError("11个统计周不完整")
    counts, speaks, models, population = Counter(), Counter(), Counter(), Counter()
    decisions, posted_ids, fingerprints = set(), set(), {}
    requests = 0
    files = sorted((directory / "agents").glob("*/AGENT.json"))
    if len(files) != 100:
        raise ValueError("未发现完整100名Agent")
    for path in files:
        agent = read(track(path))
        aid, kind = str(agent["profile"]["id"]), agent["profile"]["agent_type"]
        if aid in fingerprints or kind not in TYPES or str(agent["id"]) != aid:
            raise ValueError("作者ID或固定类型不符")
        profile = deepcopy(agent["profile"])
        profile.pop("content_retry_budget", None)
        fingerprints[aid] = hashlib.sha256(encode_json(profile)).hexdigest()
        population[kind] += 1
        rows = agent["decision_log"]
        if sorted(row["week"] for row in rows) != list(WEEKS):
            raise ValueError("Agent决策未完整唯一覆盖11周")
        for row in rows:
            key = aid, row["week"]
            if key in decisions or row.get("reason") in ("action_failed", "publication_failed"):
                raise ValueError("决策重复或包含未解决行动/发布失败")
            decisions.add(key)
            requests += int(row.get("generation_attempts", 0))
            speaks[row["week"], kind] += row.get("speak") is True
            if row.get("posted"):
                post_id = str(row["post_id"])
                post = env["_posts"][post_id]
                if post_id in posted_ids or not isinstance(row.get("content"), str) or not row["content"].strip():
                    raise ValueError("成功发布缺少正文或post_id重复")
                if (post["content"] != row["content"] or post["type"] != kind
                        or str(post["author_id"]) != aid or post["source_week"] != row["week"]):
                    raise ValueError("实际发布与环境入池正文/身份/周不一致")
                counts[row["week"], kind] += 1
                models[row.get("response_model") or "missing"] += 1
                posted_ids.add(post_id)
    actual_posts = {str(key) for key, post in env["_posts"].items() if post.get("source") == "agent"}
    if decisions != expected or posted_ids != actual_posts or len(posted_ids) != audit["agent_posts"]:
        raise ValueError("实际发布入池集合或决策不守恒")
    if population != Counter(marketing=23, mourning=22, other=21, meme=19, education=15):
        raise ValueError("固定人口构成改变")
    if dict(models) != descriptor["expected_models"]:
        raise ValueError("实际正文模型计数与冻结完成/时序审计不符")
    if requests != descriptor["expected_requests"]:
        raise ValueError("正文外层请求计数与已验收原始决策不符")
    weekly = []
    for row in observed:
        week = row["week"]
        total = sum(counts[week, kind] for kind in TYPES)
        if total <= 0:
            raise ValueError("零供给周的五类份额未定义，不允许补零后计算DTW")
        if row["agent_supply"] != total or any(row[f"agent_supply_{k}"] != counts[week, k] for k in TYPES):
            raise ValueError("周供给与Agent成功posted不一致")
        selected = [action for action in actions if action["week"] == week]
        exp = exposures(selected)
        actual_exposure_types = Counter(p["type"] for action in selected for p in action["feed"])
        if any(kind not in (*TYPES, "noise") for kind in actual_exposure_types):
            raise ValueError("实际feed存在未知标签")
        if (exp["feed_total"] != row["total_exposures"]
                or any(actual_exposure_types[k] != row[f"exposure_{k}"] for k in (*TYPES, "noise"))):
            raise ValueError("环境五类/噪音曝光与实际行动feed不一致")
        weekly.append(dict(algorithm=arm, seed=seed, week=week, decision_opportunities=len(selected),
                           posted_total=total, **{f"posted_{k}_authors": counts[week, k] for k in TYPES},
                           **{f"share_{k}": counts[week, k] / total for k in TYPES},
                           speak_total=sum(speaks[week, k] for k in TYPES), **exp))
    command = [sys.executable, "-c", OFFLINE_QUERY, str(ROOT / ".agentsociety/bin/ags.py"),
               "analysis", "query-data", "--data-path", str(directory / "replay"), "--sql", REPLAY_SQL]
    payload = json.loads(subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                        check=True, timeout=180, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                        "LITELLM_LOCAL_MODEL_COST_MAP": "True", "MEM0_TELEMETRY": "False",
                        "ANONYMIZED_TELEMETRY": "False"}).stdout)
    if (not payload.get("success") or payload["columns"] != list(REPLAY_FIELDS)
            or payload["rows"] != [[row[field] for field in REPLAY_FIELDS] for row in observed]):
        raise ValueError("官方只读replay五类供给/全部标签曝光核验不通过")
    for path in [directory / "replay/_schema.json", *sorted((directory / "replay").glob("curation_dynamics_env_state.*.jsonl"))]:
        track(path)
    late_rows = [row for row in weekly if row["week"] in LATE]
    late_exp = exposures([action for action in actions if action["week"] in LATE])
    late_meme = sum(row["posted_meme_authors"] for row in late_rows)
    late_total = sum(row["posted_total"] for row in late_rows)
    metric = dict(algorithm=arm, seed=seed, run_id=descriptor["run_id"], origin=descriptor["origin"],
                  historical_reference=arm == "chronological", model=next(iter(models)),
                  total_posts=sum(counts.values()), body_outer_requests=requests,
                  late_meme_posts=late_meme, late_total_posts=late_total,
                  late_meme_share=late_meme / late_total if late_total else None,
                  **{f"late_{key}": value for key, value in late_exp.items()})
    validation = dict(run_dir=str(directory), completion=dict(agents=100, steps=693, actions=1100,
                      decisions=len(decisions), weeks=11), population=dict(population),
                      actual_models=dict(models), recirculation_audit=audit,
                      official_replay_all_types_supply_and_exposure_verified=True,
                      historical_legacy_chronological_equivalence=arm == "chronological")
    return weekly, metric, validation, fingerprints, sources


def calculate(args):
    sources = {}
    def source(path):
        path = Path(path).resolve()
        sources[str(path)] = digest(path)
        return read(path)
    contract = source(args.contract)
    if (contract["arms"] != list(ARMS) or contract["seeds"] != list(range(10))
            or contract["weeks"] != list(WEEKS) or contract["late_weeks"] != list(LATE)
            or contract["author_types"] != list(TYPES) or contract["dtw"]["window_weeks"] != 1
            or contract["dtw"]["primary_share_field"] != "shanghai_clean_share"
            or contract["dtw"]["z_normalization"] is not False
            or contract["stability"]["pairs"] != [list(p) for p in PAIRS]):
        raise ValueError("冻结分析合约与已确认口径不符")
    # 计算所需来源仅从正式路径解析；历史迁移清单内部的旧路径不参与加载。
    for relative, expected in contract["source_sha256"].items():
        path = ROOT / relative
        if digest(path) != expected:
            raise ValueError(f"合约来源改变：{path}")
        sources[str(path)] = expected
    manifest = source(args.manifest)
    if manifest["status"] != "passed":
        raise ValueError("正式30run矩阵须先通过落地核验")
    expected_matrix = {(arm, seed) for arm in ARMS for seed in range(10)}
    if (len(manifest["runs"]) != 30
            or {(r["algorithm"], r["seed"]) for r in manifest["runs"]} != expected_matrix):
        raise ValueError("正式矩阵未完整唯一覆盖三臂各10seed")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if digest(path) != expected:
            raise ValueError(f"正式冻结来源改变：{path}")
        sources[str(path)] = expected
    descriptors = []
    for row in manifest["runs"]:
        directory = (ROOT / row["run_dir"]).resolve()
        if not directory.is_relative_to(ROOT / "hypothesis_4/experiment_2/runs"):
            raise ValueError("原始运行必须从正式实验目录读取")
        if row["algorithm"] != "chronological" and set(row["expected_models"]) != {MODEL}:
            raise ValueError("新版随机/兴趣实际模型与冻结结果不符")
        descriptors.append({**row, "run_dir": str(directory)})
    descriptors.sort(key=lambda r:(ARMS.index(r["algorithm"]),r["seed"]))
    with ThreadPoolExecutor(max_workers=2) as pool:
        extracted = list(pool.map(extract, descriptors))
    weekly, metrics, validation, profiles = [], [], {}, {}
    for descriptor, (rows, metric, valid, fingerprints, hashes) in zip(descriptors, extracted):
        weekly.extend(rows)
        metrics.append(metric)
        validation[descriptor["run_id"]] = valid
        profiles[metric["algorithm"],metric["seed"]] = fingerprints
        sources.update(hashes)
        print("PASS",metric["run_id"],flush=True)
    for seed in range(10):
        if not profiles["random",seed] == profiles["interest",seed] == profiles["chronological",seed]:
            raise ValueError("同seed三臂实际人口/行为profile不一致")
    method_path = ROOT / manifest["dtw_method"]
    spec = importlib.util.spec_from_file_location("seed10_frozen_dtw", method_path)
    method = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(method)
    sources[str(method_path)] = digest(method_path)
    benchmark_path = ROOT / manifest["reality_csv"]
    if benchmark_path != ROOT / contract["dtw"]["benchmark"]:
        raise ValueError("正式矩阵与合约的现实效标路径不同")
    sources[str(benchmark_path)] = digest(benchmark_path)
    with benchmark_path.open(newline="",encoding="utf-8-sig") as stream:
        observations = list(csv.DictReader(stream))
    observed = {(r["week"],r["category"]):r for r in observations}
    if len(observed) != 55 or len(observations) != 55:
        raise ValueError("现实效标并非11周×5类唯一记录")
    reality_audit = source(ROOT / manifest["reality_audit"])
    matrices = {}
    for field in ("shanghai_clean_share","utc_clean_share"):
        matrix = np.array([[float(observed[w,MAPPING[k]][field]) for k in TYPES] for w in WEEKS])
        if not np.all(np.isfinite(matrix)) or np.any(matrix < 0) or not np.allclose(matrix.sum(axis=1),1,rtol=0,atol=1e-12):
            raise ValueError("现实份额不守恒")
        matrices[field] = matrix
    for week in WEEKS:
        total = sum(reality_audit["real_shanghai"][week][MAPPING[k]] for k in TYPES)
        for kind in TYPES:
            row = observed[week,MAPPING[kind]]
            if int(row["shanghai_count"]) != reality_audit["real_shanghai"][week][MAPPING[kind]] or not math.isclose(float(row["shanghai_clean_share"]),int(row["shanghai_count"])/total,abs_tol=1e-12):
                raise ValueError("上海周效标与冻结全量计数不符")
    run_paths, sim_matrices = [], {}
    def score_matrix(sim):
        score,path = method.constrained_multivariate_dtw(sim,matrices["shanghai_clean_share"],window=1)
        utc,utc_path = method.constrained_multivariate_dtw(sim,matrices["utc_clean_share"],window=1)
        def details(path,observed_matrix):
            return [dict(simulated_week=WEEKS[i],observed_week=WEEKS[j],
                         local_cost=float(np.linalg.norm(sim[i]-observed_matrix[j]))) for i,j in path]
        primary = details(path,matrices["shanghai_clean_share"])
        if not math.isclose(score,sum(p["local_cost"] for p in primary)/len(path),rel_tol=0,abs_tol=1e-12):
            raise ValueError("DTW路径归一化不符")
        return dict(dtw_x100=float(score)*100,utc_sensitivity_dtw_x100=float(utc)*100,
                    path_length=len(path),primary_path=primary,
                    utc_secondary_path=details(utc_path,matrices["utc_clean_share"]))
    for metric in metrics:
        key = metric["algorithm"],metric["seed"]
        sim = np.array([[r[f"share_{k}"] for k in TYPES] for r in weekly if (r["algorithm"],r["seed"]) == key])
        sim_matrices[key] = sim
        result = score_matrix(sim)
        metric.update(dtw_x100=result["dtw_x100"],utc_sensitivity_dtw_x100=result["utc_sensitivity_dtw_x100"],
                      dtw_path_length=result["path_length"])
        run_paths.append(dict(algorithm=key[0],seed=key[1],**result))
    mean_trajectory, mean_paths = {}, []
    for arm in ARMS:
        result = score_matrix(np.mean(np.stack([sim_matrices[arm,seed] for seed in range(10)]),axis=0))
        mean_trajectory[arm] = {k:result[k] for k in ("dtw_x100","utc_sensitivity_dtw_x100","path_length")}
        mean_paths.append(dict(algorithm=arm,measure="DTW of equally weighted mean share trajectory; distinct from mean run DTW",**result))
    main, paired = stability(metrics,range(10))
    without0,_ = stability(metrics,range(1,10))
    same_model = [seed for seed in range(10) if all(next(r for r in metrics if r["algorithm"]==arm and r["seed"]==seed)["model"]==MODEL for arm in ARMS)]
    if same_model != list(range(3,10)):
        raise ValueError("实际模型分层与冻结预期不同，不能直接按seed号分层")
    same_version,_ = stability(metrics,same_model)
    omitted=[]
    loo_ranks={arm:Counter({"1":0,"2":0,"3":0}) for arm in ARMS}
    for seed in range(10):
        cohort,_ = stability(metrics,[s for s in range(10) if s!=seed])
        means={arm:cohort["dtw_by_arm"][arm]["mean"] for arm in ARMS}
        ranking=sorted(ARMS,key=lambda arm:means[arm])
        for arm in ARMS:
            rank=1+sum(value < means[arm]-1e-12 for value in means.values())
            loo_ranks[arm][str(rank)]+=1
        omitted.append(dict(omitted_seed=seed,n=9,mean_dtw_x100=means,ranking=ranking,
                            paired_comparisons=cohort["paired_comparisons"]))
    outcome_fields=("total_posts","late_meme_posts","late_total_posts","late_meme_share","late_feed_total","late_feed_meme_tag","late_feed_meme_tag_share")
    outcome_summary={arm:{field:descriptive([r[field] for r in metrics if r["algorithm"]==arm]) for field in outcome_fields} for arm in ARMS}
    chrono_models=sorted({r["model"] for r in metrics if r["algorithm"]=="chronological"})
    strata={model:descriptive([r["dtw_x100"] for r in metrics if r["algorithm"]=="chronological" and r["model"]==model],
                             [r["seed"] for r in metrics if r["algorithm"]=="chronological" and r["model"]==model]) for model in chrono_models}
    summary=dict(status="passed",scope=contract["scope"],arms=list(ARMS),seeds=list(range(10)),weeks=list(WEEKS),
                 late_weeks=list(LATE),author_types=list(TYPES),method=contract["dtw"],
                 contract_sha256=digest(args.contract),dtw_by_arm=main["dtw_by_arm"],
                 mean_trajectory_dtw=mean_trajectory,paired_comparisons=main["paired_comparisons"],
                 rank_frequency=main["rank_frequency"],rankings_per_seed=main["rankings_per_seed"],
                 mean_dtw_ranking=sorted(ARMS,key=lambda arm:main["dtw_by_arm"][arm]["mean"]),
                 late_outcomes_by_arm=outcome_summary,
                 sensitivity=dict(exclude_pilot_seed0=without0,same_actual_model_seed3_9=same_version,
                     chronological_actual_model_strata=strata,leave_one_seed_out=dict(results=omitted,
                     rank_frequency={arm:dict(loo_ranks[arm]) for arm in ARMS})),
                 provenance_file="provenance.json",paths_file="dtw_paths.json",
                 output_row_counts=dict(weekly=330,run_metrics=30,paired_dtw=30,dtw_summary=3),
                 limitations=contract["limitations"])
    summary_rows=[dict(algorithm=arm,**{k:main["dtw_by_arm"][arm][k] for k in ("n","mean","sample_sd","min","max")},
                       mean_trajectory_dtw_x100=mean_trajectory[arm]["dtw_x100"],
                       mean_trajectory_path_length=mean_trajectory[arm]["path_length"]) for arm in ARMS]
    for path in (Path(__file__),ROOT/".agentsociety/bin/ags.py"):
        sources[str(path)] = digest(path)
    if len(weekly)!=330 or len(metrics)!=30 or len(paired)!=30:
        raise ValueError("输出行数不符")
    # 分析结束再核所读来源，避免长查询期间的数据改变被误当作同一版本。
    for path,expected in sources.items():
        if digest(path)!=expected:
            raise ValueError(f"分析期间来源改变：{path}")
    return {"weekly.csv":encode_csv(weekly),"run_metrics.csv":encode_csv(metrics),
            "paired_dtw.csv":encode_csv(paired),"dtw_summary.csv":encode_csv(summary_rows),
            "summary.json":encode_json(summary),"dtw_paths.json":encode_json(dict(run_paths=run_paths,mean_trajectory_paths=mean_paths)),
            "provenance.json":encode_json(dict(source_sha256=sources,run_validation=validation,
                  replay_sql=REPLAY_SQL,analysis_processes_max_parallel=2,simulation_or_llm_requests=False,
                  python_version=sys.version.split()[0],numpy_version=np.__version__))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    parser.add_argument("--contract",type=Path,default=HERE/"contract.json")
    parser.add_argument("--output-dir",type=Path,default=HERE/"results")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    args.output_dir=args.output_dir.resolve()
    args.output_dir.relative_to(HERE)
    def deny_network(*args,**kwargs):
        raise RuntimeError("分析禁止网络连接")
    with patch.object(socket.socket,"connect",deny_network),patch.object(socket.socket,"connect_ex",deny_network),patch.object(socket,"create_connection",deny_network):
        payloads=calculate(args)
    if args.check:
        for name,content in payloads.items():
            path=args.output_dir/name
            if not path.is_file() or path.read_bytes()!=content:
                raise ValueError(f"确定性复算不一致：{path}")
        print("PASS --check：7份分析产物确定性一致；没有覆盖文件")
    else:
        for name,content in payloads.items():
            path=args.output_dir/name
            if path.exists() and path.read_bytes()!=content:
                raise ValueError(f"已有冲突产物，拒绝覆盖：{path}")
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for name,content in payloads.items():
            (args.output_dir/name).write_bytes(content)
        print("PASS：三臂30run/330周；7份分析产物已生成")


if __name__=="__main__":
    main()
