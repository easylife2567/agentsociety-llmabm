"""离线准备 timestamp 主实验 seed 3–9；不启动引擎、不读取凭据。

旧 seed 0–2 的配置、人口、调度和样本均只读。原始源池是已入 Git 的冻结
资产，通过基线 commit 和 SHA256 引用，不另复制 70 MB。仅复刻两个历史
生成器的纯抽样规则，绝不执行会写文件的历史脚本。
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import json
from pathlib import Path
import random

INIT = Path(__file__).resolve().parent
ROOT = INIT.parents[2]
BASELINE_COMMIT = "69d243955d341444ae769fae5bf23dc160465cd6"
BATCH = "timestamp_v1_seed3_9"
ALGORITHMS = ("random", "chronological", "interest")
SEEDS = tuple(range(3, 10))
POOL = ROOT / "custom/envs/curation_assets/injection_posts.json"
MANIFEST = INIT / "manifest_seed3_9.json"
RETRY = {"limit": 2310,
         "ledger_path": f"hypothesis_4/experiment_2/runs/{BATCH}/_extra_attempts.count"}
SHANGHAI = timezone(timedelta(hours=8))


def relative(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def largest_remainder(total, groups):
    """保留原最大余数排序；余数相同时按类型名称排序。"""
    count = sum(len(rows) for rows in groups.values())
    if not 0 <= total <= count:
        raise ValueError("抽样配额超过源池容量")
    quotas = {name: total * len(rows) / count for name, rows in groups.items()}
    result = {name: int(quota) for name, quota in quotas.items()}
    order = sorted(groups, key=lambda name: (-(quotas[name] - int(quotas[name])), name))
    index = 0
    while sum(result.values()) < total:
        name = order[index % len(order)]
        if result[name] < len(groups[name]):
            result[name] += 1
        index += 1
    return result


def stratified(pool, total, rng, include_empty):
    """W11原函数含sample(..., 0)；窗口原函数跳过0配额，分别保留。"""
    groups = {}
    for row in pool:
        groups.setdefault(str(row.get("type", "other")), []).append(row)
    allocations = largest_remainder(total, groups)
    selected = []
    for name in sorted(groups):
        if include_empty or allocations[name] > 0:
            selected.extend(rng.sample(groups[name], allocations[name]))
    rng.shuffle(selected)
    return selected


def samples(seed, by_week, allocation, announcement, initial_pool=None):
    window = []
    rng = random.Random(seed + 777)
    for week, quota in sorted(allocation.items()):
        regular = quota - int(week == "2026-W13")
        window.extend(dict(row, is_official=False)
                      for row in stratified(by_week[week], regular, rng, False))
        if week == "2026-W13":
            window.append(deepcopy(announcement))
    window.sort(key=lambda row: (row["week"], str(row["pid"])))
    initial = stratified(by_week["2026-W11"] if initial_pool is None else initial_pool,
                         17, random.Random(seed + 1777), True)
    initial.sort(key=lambda row: str(row["pid"]))
    return window, initial


def validate_samples(window, initial, allocation):
    assert len(window) == 250 and len(initial) == 17
    assert len({str(row["pid"]) for row in window + initial}) == 267
    assert Counter(row["week"] for row in window) == allocation
    assert sum(bool(row.get("is_official")) for row in window) == 1
    start, end = datetime(2026, 3, 16, tzinfo=SHANGHAI), datetime(2026, 6, 1, tzinfo=SHANGHAI)
    for is_initial, rows in ((False, window), (True, initial)):
        for row in rows:
            if row.get("is_official"):
                continue
            moment = datetime.fromisoformat(str(row["published_at"]).replace("Z", "+00:00"))
            assert moment.tzinfo is not None
            moment = moment.astimezone(SHANGHAI)
            valid = (row["week"] == "2026-W11" and moment < start) if is_initial else (start <= moment < end)
            assert valid, f"样本时间不合规: {row['pid']} {row['published_at']}"


def prepare():
    """先在内存完成复算与全部冲突检查，再允许写入新资产。"""
    legacy = read_json(INIT / "manifest.json")
    old_window = read_json(INIT / "inputs/injection_sample_s0.json")
    old_initial = read_json(INIT / "inputs/initial_sample_weekly_lag_s0.json")
    allocation = old_window["meta"]["allocation"]
    announcement = next(row for row in old_window["posts"] if row.get("is_official"))
    by_week = {}
    for row in read_json(POOL)["posts"]:
        by_week.setdefault(str(row["week"]), []).append(row)
    # W11标签由源数据沿用；timestamp初始池另要求上海发布时间严格早于窗口。
    # 原890条池中6条跨界，不能进入历史池，否则旧引擎会拒绝初始化。
    start = datetime(2026, 3, 16, tzinfo=SHANGHAI)
    initial_pool = [row for row in by_week["2026-W11"]
                    if datetime.fromisoformat(row["published_at"]).astimezone(SHANGHAI) < start]
    excluded = [{**{key: row[key] for key in ("pid", "week", "published_at", "type")},
                 "published_at_shanghai": datetime.fromisoformat(row["published_at"]).astimezone(SHANGHAI).isoformat()}
                for row in by_week["2026-W11"] if row not in initial_pool]
    assert len(by_week["2026-W11"]) == 890 and len(initial_pool) == 884 and len(excluded) == 6
    guards = {ROOT / path for path in legacy["output_sha256"]}
    guards.add(INIT / "manifest.json")
    guards.add(INIT / "config_params.py")
    guards.update(INIT / "configs" / f"timestamp_v1_{arm}_s{seed}.json"
                  for arm in ALGORITHMS for seed in range(3))
    source_paths = guards | {POOL, Path(__file__).resolve(),
        ROOT / "hypothesis_4/experiment_1/init/config_params.py",
        ROOT / "hypothesis_4/experiment_1/init/weekly_lag_config.py",
        ROOT / "custom/envs/curation_assets/vocabs.json"}
    source_hashes = {relative(path): digest(path.read_bytes()) for path in sorted(source_paths)}
    for path, expected in legacy["output_sha256"].items():
        assert source_hashes[path] == expected, f"原冻结资产已变化: {path}"
    reconstruction = {}
    eligibility_comparison = {}
    for seed in range(3):
        window, initial = samples(seed, by_week, allocation, announcement)
        filtered_window, filtered_initial = samples(seed, by_week, allocation, announcement, initial_pool)
        assert filtered_window == window and filtered_initial == initial, "历史seed资格修正改变了原样本"
        for kind, posts in (("injection_sample", window), ("initial_sample_weekly_lag", initial)):
            frozen = INIT / "inputs" / f"{kind}_s{seed}.json"
            assert posts == read_json(frozen)["posts"], f"原规则复算不一致: {frozen}"
        reconstruction[str(seed)] = {"window_250_posts_exact_match": True,
                                     "initial_17_posts_exact_match": True,
                                     "includes_order_and_all_post_fields": True,
                                     "filtered_initial_17_posts_exact_match": True}

    # 核对三个旧seed的人口和行动表完全一致；只替换新批账本，不重抽人口或时刻。
    population = read_json(INIT / "inputs/population_s0.json")
    schedule = read_json(INIT / "inputs/action_schedule_s0.json")
    for seed in (1, 2):
        assert read_json(INIT / f"inputs/population_s{seed}.json") == population
        assert read_json(INIT / f"inputs/action_schedule_s{seed}.json") == schedule
        assert (INIT / f"steps_s{seed}.yaml").read_bytes() == (INIT / "steps_s0.yaml").read_bytes()
    assert len(population) == 100
    assert len(schedule["action_times"]) == 693
    overrides = schedule["chronological_action_hour_overrides"]
    assert overrides == {"2026-W13": {"70": 61, "21": 67, "22": 96, "20": 113, "56": 166}}
    for agent in population:
        assert agent["agent_id"] == agent["kwargs"]["id"]
        agent["kwargs"]["content_retry_budget"] = deepcopy(RETRY)
    outputs = {}
    runs = []
    seeds = {}
    templates = {arm: read_json(INIT / "configs" / f"timestamp_v1_{arm}_s0.json") for arm in ALGORITHMS}
    normalized = []
    for arm, config in templates.items():
        item = deepcopy(config)
        assert item["env_modules"][0]["kwargs"].pop("recommendation_algorithm") == arm
        normalized.append(item)
    assert all(config == normalized[0] for config in normalized)
    for seed in SEEDS:
        window, initial = samples(seed, by_week, allocation, announcement, initial_pool)
        original_window, original_initial = samples(seed, by_week, allocation, announcement)
        assert window == original_window
        original_pids = [row["pid"] for row in original_initial]
        filtered_pids = [row["pid"] for row in initial]
        eligibility_comparison[str(seed)] = {
            "window_250_posts_unchanged": True, "initial_posts_exact_match": original_initial == initial,
            "original_initial_pids": original_pids, "filtered_initial_pids": filtered_pids,
            "removed_pids": [pid for pid in original_pids if pid not in filtered_pids],
            "added_pids": [pid for pid in filtered_pids if pid not in original_pids],
            "original_initial_violations": [row["pid"] for row in original_initial
                if datetime.fromisoformat(row["published_at"]).astimezone(SHANGHAI) >= start]}
        validate_samples(window, initial, allocation)
        window_doc, initial_doc = deepcopy(old_window), deepcopy(old_initial)
        for doc, posts, offset in ((window_doc, window, 777), (initial_doc, initial, 1777)):
            doc["posts"] = posts
            doc["meta"]["seed"] = seed
            doc["meta"]["sample_rng"] = f"Random({seed}+{offset})"
            doc["meta"]["purpose"] = ("timestamp三臂主实验seed 3–9扩充；沿用原抽样规则，"
                                      "实际可见性按timestamp及arrival_official_policy=ordinary执行")
        window_doc["meta"]["weekly_type_counts"] = {
            week: dict(sorted(Counter(row["type"] for row in window if row["week"] == week).items()))
            for week in sorted(allocation)}
        window_doc["meta"]["official_announcement"]["note"] = (
            "全程唯一官方讣告，实际可用时间2026-03-24T20:00:00+08:00；三臂普通推荐，不置顶、不进入悼念保底")
        initial_doc["meta"]["candidate_eligibility"] = {"source_rows": 890, "eligible_rows": 884,
            "rule": "W11标签且Asia/Shanghai发布时间严格早于2026-03-16T00:00:00+08:00",
            "basis": "既有timestamp历史池资格约束；见manifest_seed3_9.json的差异披露"}
        initial_doc["meta"]["type_counts"] = dict(sorted(Counter(str(row.get("type", "other")) for row in initial).items()))
        window_path = INIT / "inputs" / f"injection_sample_s{seed}.json"
        initial_path = INIT / "inputs" / f"initial_sample_weekly_lag_s{seed}.json"
        population_path = INIT / "inputs" / f"population_s{seed}.json"
        schedule_path = INIT / "inputs" / f"action_schedule_s{seed}.json"
        steps_path = INIT / f"steps_s{seed}.yaml"
        outputs.update({window_path: json_bytes(window_doc), initial_path: json_bytes(initial_doc),
                        population_path: json_bytes(population), schedule_path: json_bytes(schedule),
                        steps_path: (INIT / "steps_s0.yaml").read_bytes()})
        seeds[str(seed)] = {"population": relative(population_path), "schedule": relative(schedule_path),
                            "window_sample": relative(window_path), "initial_sample": relative(initial_path),
                            "expected_batches": 693, "expected_action_records": 1100,
                            "expected_week_records": 11}
        for arm in ALGORITHMS:
            config = deepcopy(templates[arm])
            config["agents"] = deepcopy(population)
            env = config["env_modules"][0]["kwargs"]
            env.update(random_seed=seed, injection_data_path=relative(window_path),
                       weekly_initial_injection_data_path=relative(initial_path))
            run_id = f"timestamp_v1_{arm}_s{seed}"
            config_path = INIT / "configs" / f"{run_id}.json"
            outputs[config_path] = json_bytes(config)
            runs.append({"run_id": run_id, "algorithm": arm, "seed": seed,
                         "config": relative(config_path), "steps": relative(steps_path),
                         "run_dir": f"hypothesis_4/experiment_2/runs/{BATCH}/{run_id}",
                         "expected_batches": 693, "expected_action_records": 1100, "expected_week_records": 11})
    manifest = {"batch_id": BATCH, "execution_authorized": False,
        "preparation_authorization": "仅准备三臂主实验seed 3–9、核对运行条件与离线验证；不启动仿真，消融不补",
        "baseline_commit": BASELINE_COMMIT, "generator": relative(Path(__file__).resolve()),
        "source_sha256": source_hashes,
        "source_pool_freeze": {"path": relative(POOL), "git_commit": BASELINE_COMMIT,
                               "sha256": source_hashes[relative(POOL)], "copied": False,
                               "restore": "从记录commit恢复此已入Git源池，并核验SHA256；源池顺序是抽样输入的一部分"},
        "sampling_rules": {"window": {"source": "hypothesis_4/experiment_1/init/config_params.py:stratified_week_sample及seed循环",
                                       "rng": "Random(seed+777)", "allocation": allocation,
                                       "rule": "每周类型最大余数；按类型名组内sample、shuffle；W13加入固定官方帖；最终week/pid排序"},
                           "initial": {"source": "hypothesis_4/experiment_1/init/weekly_lag_config.py:stratified_sample及generate",
                                       "rng": "Random(seed+1777)", "rows": 17,
                                       "rule": "W11类型最大余数；按类型名组内sample、shuffle；最终pid排序"}},
        "legacy_seed_reconstruction": reconstruction,
        "initial_pool_eligibility_revision": {"source_rows": 890, "eligible_rows": 884, "excluded_rows": excluded,
            "rule": "原W11标签加Asia/Shanghai发布时间严格早于2026-03-16T00:00:00+08:00",
            "basis": "custom/envs/curation_arrival_schedule.py:ArrivalSchedule.init既有历史时间窗约束",
            "scope": "只修正新seed的历史候选资格；类型分层最大余数、seed流及sample/shuffle/sort不变；旧资产不变",
            "original_pool_incompatibility": "原890条池使seed4及seed8抽中窗口内pid4496，既有引擎将拒绝初始化",
            "legacy_filtered_reconstruction": "seed0–2使用884条合规池复算仍与旧17条完整posts及次序相同",
            "new_seed_comparison": eligibility_comparison},
        "legacy_assets_unchanged_sha256": {relative(path): source_hashes[relative(path)] for path in sorted(guards)},
        "output_sha256": {relative(path): digest(data) for path, data in sorted(outputs.items())},
        "timezone": legacy["timezone"], "window_start": legacy["window_start"],
        "window_end_exclusive": legacy["window_end_exclusive"],
        "official_available_at": legacy["official_available_at"], "official_time_basis": legacy["official_time_basis"],
        "event_week_action_schedule": legacy["event_week_action_schedule"],
        "mechanisms": legacy["mechanisms"], "seeds": seeds, "runs": runs,
        "budget": {"decision_opportunities": 23100, "extra_requests_limit": 2310,
                   "extra_requests_per_action": 1, "content_retry_budget": RETRY,
                   "active_wall_seconds": None, "execution_note": "配置上限不是模型调用授权；时长及费用启动前另定"},
        "runtime_conditions": {"scientific_config_template": "timestamp_v1_*_s0.json",
                               "allowed_changes": ["random_seed", "新增样本路径", "新批额外请求额度及账本"],
                               "model_check": "模型与接口、引擎和custom源码核对证据见实验级离线验证记录；本生成器不读取凭据",
                               "execution_note": "旧run_main_experiment.py固定旧批次；当前不得用它启动新增矩阵"}}
    manifest["mechanisms"]["event_week_schedule"] = (
        "只覆盖5位悼念Agent的W13决策小时；三臂全部10个seed同表，保留693调度批，W13原hour18为空批")
    outputs[MANIFEST] = json_bytes(manifest)
    return outputs, guards, source_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只复算并核对，不写文件")
    args = parser.parse_args()
    outputs, guards, sources = prepare()
    # 全批预检，拒绝覆盖任何不一致文件；不接触未来run目录或旧结果。
    for path, expected in outputs.items():
        if path.exists() and path.read_bytes() != expected:
            raise ValueError(f"拒绝覆盖与复算不一致的文件: {relative(path)}")
        if args.check and not path.is_file():
            raise ValueError(f"缺少生成资产: {relative(path)}")
    if not args.check:
        for path, data in outputs.items():
            if not path.exists():
                path.write_bytes(data)
    for path in guards:
        assert digest(path.read_bytes()) == sources[relative(path)], f"旧资产被改动: {relative(path)}"
    print(json.dumps({"batch_id": BATCH, "runs": 21, "seeds": list(SEEDS),
                      "decision_opportunities": 23100, "execution_authorized": False,
                      "mode": "check" if args.check else "prepare", "outputs": len(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
