"""生成 timestamp 主实验九格配置，保留冻结人口、输入和行为参数。

仅用标准库读取 experiment_1 的已选定资产；输入逐字节复制到本实验，
不导入历史生成器、不调用模型。官方 experiment-config run 负责执行本脚本。
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import random

INIT = Path(__file__).resolve().parent
ROOT = INIT.parents[2]
SOURCE = ROOT / "hypothesis_4/experiment_1/init"
BATCH = "timestamp_v1"
ALGORITHMS = ("random", "chronological", "interest")
SHANGHAI = timezone(timedelta(hours=8))
START = datetime(2026, 3, 16)
END = datetime(2026, 6, 1)
EVENT_WEEK = "2026-W13"
EVENT_WEEK_START = datetime(2026, 3, 23)
OFFICIAL_HOUR = 44
EVENT_SCHEDULE_SEED = 20261009
POPULATION_COUNTS = {"marketing": 23, "mourning": 22, "other": 21, "meme": 19, "education": 15}
RETRY_BUDGET = {"limit": 990, "ledger_path": "hypothesis_4/experiment_2/runs/timestamp_v1/_extra_attempts.count"}


def relative(path):
    """配置中使用工作区相对路径，便于官方入口解析。"""
    return str(path.relative_to(ROOT))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_time(value):
    """普通样本必须具备实际时间，转换到上海周界后验证窗口。"""
    moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("普通样本发布时间缺少时区")
    return moment.astimezone(SHANGHAI).replace(tzinfo=None)


def validate_samples(window, initial):
    """固定250条窗口样本和17条历史；官方唯一无实测时刻，另按约定门控。"""
    assert len(window) == 250 and len(initial) == 17
    assert sum(bool(row.get("is_official")) for row in window) == 1
    keys = [str(row["pid"]) for row in window + initial]
    assert len(keys) == len(set(keys)) == 267
    for row in initial:
        assert not row.get("is_official") and local_time(row["published_at"]) < START
    for row in window:
        if not row.get("is_official"):
            assert START <= local_time(row["published_at"]) < END


def build_event_schedule(hours, source_agents):
    """只顺延5位事件前悼念Agent；独立抽样一次，三臂三seed复用。"""
    mourning_ids = {str(agent["agent_id"]) for agent in source_agents
                    if agent["kwargs"]["agent_type"] == "mourning"}
    early_ids = sorted((aid for aid in mourning_ids if hours[aid] < OFFICIAL_HOUR),
                       key=lambda aid: (hours[aid], int(aid)))
    assert early_ids == ["70", "21", "22", "20", "56"]
    # 使用既有调度网格的不同小时，保持693步；抽样流不参与推荐或效用计算。
    eligible_hours = sorted({hour for hour in hours.values() if hour > OFFICIAL_HOUR})
    selected = sorted(random.Random(EVENT_SCHEDULE_SEED).sample(eligible_hours, len(early_ids)))
    overrides = dict(zip(early_ids, selected))
    assert overrides == {"70": 61, "21": 67, "22": 96, "20": 113, "56": 166}
    effective_hours = dict(hours, **overrides)
    adjustments = [{"agent_id": int(aid), "original_hour": hours[aid], "adjusted_hour": overrides[aid],
                    "original_at": (EVENT_WEEK_START + timedelta(hours=hours[aid])).replace(tzinfo=SHANGHAI).isoformat(),
                    "adjusted_at": (EVENT_WEEK_START + timedelta(hours=overrides[aid])).replace(tzinfo=SHANGHAI).isoformat()}
                   for aid in early_ids]
    return {"week": EVENT_WEEK, "selection_seed": EVENT_SCHEDULE_SEED,
            "selection_rule": "从原100人表中严格晚于官方hour44的不同小时等权无放回抽5个，排序对应原5人先后；不读取结果，不使用推荐随机流",
            "basis": "用户采纳的事件后参与条件；不是观测活动时刻",
            "chronological_action_hour_overrides": {EVENT_WEEK: overrides},
            "adjustments": adjustments,
            "empty_dispatch_hours": sorted(set(hours.values()) - set(effective_hours.values()))}


def build_population(source_agents, hours, overrides):
    """清理22份固定预知陈述，保留职业、风格、词表和全部数值profile。"""
    population = deepcopy(source_agents)
    assert len(population) == 100
    assert Counter(agent["kwargs"]["agent_type"] for agent in population) == POPULATION_COUNTS
    statement = "你是被其离世触动的关注者，表达真诚克制，主要是追思、缅怀，以及由事件引发的健康、工作与生活感慨。"
    replacement = "你是关注相关人物的普通用户，表达真诚克制，重视情感与生活感受；只在所见内容支持离世事实时表达追思、缅怀，否则回应实际所见内容。"
    cleaned = []
    for agent in population:
        profile = agent["kwargs"]
        assert agent["agent_id"] == profile["id"]
        if statement in profile["persona"]:
            profile["persona"] = profile["persona"].replace(statement, replacement)
            cleaned.append(agent["agent_id"])
        profile.update(arrival_timing=True, chronological_action_hour=hours[str(agent["agent_id"])],
                       content_retry_budget=deepcopy(RETRY_BUDGET))
        # baseline小时保留用于其他10周，只有这5份profile接入W13覆盖。
        aid = str(agent["agent_id"])
        if aid in overrides[EVENT_WEEK]:
            profile["chronological_action_hour_overrides"] = {EVENT_WEEK: overrides[EVENT_WEEK][aid]}
    assert len(cleaned) == 22
    return population, cleaned


def build_steps(hours):
    """保留基线调度网格；W13允许空批，末步收齐窗口且不增加W23行动。"""
    unique_hours = sorted(set(hours.values()))
    assert all(isinstance(hour, int) and 0 <= hour < 168 for hour in unique_hours)
    times = [START + timedelta(weeks=week, hours=hour) for week in range(11) for hour in unique_hours]
    lines = [f'start_t: "{times[0].isoformat(timespec="seconds")}"', "steps:"]
    for index, moment in enumerate(times):
        following = times[index + 1] if index + 1 < len(times) else END
        tick = int((following - moment).total_seconds())
        assert tick > 0
        lines.extend(["  - type: run", "    num_steps: 1", f"    tick: {tick}"])
    return "\n".join(lines) + "\n", times


def main():
    # user_data目前为空；正式采用的是已登记冻结样本，而非自动吸收后来放入的文件。
    user_data_files = sorted(relative(path) for path in (ROOT / "user_data").rglob("*") if path.is_file())
    inputs = INIT / "inputs"
    configs = INIT / "configs"
    inputs.mkdir(exist_ok=True)
    configs.mkdir(exist_ok=True)
    source_hashes = {}
    generated = []
    runs = []
    seeds = {}
    common_hours = None
    common_event_schedule = None
    source_paths = []
    for seed in range(3):
        source_paths.extend(SOURCE / f"configs/anchored_v1_{algorithm}_s{seed}.json" for algorithm in ALGORITHMS)
        source_paths.extend([SOURCE / f"injection_sample_s{seed}.json", SOURCE / f"initial_sample_weekly_lag_s{seed}.json"])
    source_paths.append(ROOT / "custom/envs/curation_assets/vocabs.json")
    source_hashes.update({relative(path): sha256(path) for path in source_paths})

    # 再次生成必须匹配已记录源哈希，避免同名输入被替换后悄悄覆盖冻结配置。
    manifest_path = INIT / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous["source_sha256"] != source_hashes:
            raise ValueError("源资产哈希已变化；请先核对并明确处理冻结清单")
    for seed in range(3):
        base = {algorithm: json.loads((SOURCE / f"configs/anchored_v1_{algorithm}_s{seed}.json").read_text(encoding="utf-8"))
                for algorithm in ALGORITHMS}
        assert base["interest"]["agents"] == base["random"]["agents"]
        hours = base["chronological"]["env_modules"][0]["kwargs"]["chronological_action_hours"]
        ids = {str(agent["agent_id"]) for agent in base["interest"]["agents"]}
        assert len(ids) == 100 and set(hours) == ids
        # 不逐seed重抽；先核对原时刻完全相同，再共用一次冻结的覆盖表。
        if common_hours is None:
            common_hours = deepcopy(hours)
            common_event_schedule = build_event_schedule(hours, base["interest"]["agents"])
        else:
            assert hours == common_hours, "三seed基线小时表不一致，不能复用既定事件安排"
        overrides = common_event_schedule["chronological_action_hour_overrides"]
        population, cleaned = build_population(base["interest"]["agents"], hours, overrides)
        steps, times = build_steps(hours)
        steps_path = INIT / f"steps_s{seed}.yaml"
        steps_path.write_text(steps, encoding="utf-8")
        generated.append(steps_path)
        initial_name = f"initial_sample_weekly_lag_s{seed}.json"
        window_name = f"injection_sample_s{seed}.json"
        validate_samples(json.loads((SOURCE / window_name).read_text())["posts"],
                         json.loads((SOURCE / initial_name).read_text())["posts"])
        for name in (window_name, initial_name):
            destination = inputs / name
            destination.write_bytes((SOURCE / name).read_bytes())
            assert sha256(destination) == source_hashes[relative(SOURCE / name)]
            generated.append(destination)
        population_path = inputs / f"population_s{seed}.json"
        schedule_path = inputs / f"action_schedule_s{seed}.json"
        write_json(population_path, population)
        write_json(schedule_path, {"timezone": "Asia/Shanghai", "action_hours": hours,
                                  "chronological_action_hour_overrides": overrides,
                                  "event_week_action_schedule": common_event_schedule,
                                  "action_times": [moment.replace(tzinfo=SHANGHAI).isoformat() for moment in times]})
        generated.extend([population_path, schedule_path])
        seeds[str(seed)] = {"population": relative(population_path), "schedule": relative(schedule_path),
                            "cleaned_persona_agent_ids": cleaned, "dispatch_hours_per_week": len(set(hours.values())),
                            "empty_dispatch_hours_by_week": {EVENT_WEEK: common_event_schedule["empty_dispatch_hours"]},
                            "expected_batches": len(times)}

        # 三臂共同声明官方普通推荐；chronological/random不使用事件周悼念保底。
        common_configs = []
        for algorithm in ALGORITHMS:
            config = deepcopy(base[algorithm])
            config["agents"] = deepcopy(population)
            env = config["env_modules"][0]["kwargs"]
            env.update(schedule_mode="arrival_timing", arrival_mode="timestamp", arrival_official_policy="ordinary",
                       chronological_action_hours=hours, chronological_action_hour_overrides=deepcopy(overrides),
                       chronological_total_batches=len(times),
                       injection_data_path=relative(inputs / window_name),
                       weekly_initial_injection_data_path=relative(inputs / initial_name),
                       event_week_mourning_floor=base["interest"]["env_modules"][0]["kwargs"]["event_week_mourning_floor"])
            normalized = deepcopy(config)
            del normalized["env_modules"][0]["kwargs"]["recommendation_algorithm"]
            common_configs.append(normalized)
            run_id = f"{BATCH}_{algorithm}_s{seed}"
            config_path = configs / f"{run_id}.json"
            write_json(config_path, config)
            generated.append(config_path)
            runs.append({"run_id": run_id, "algorithm": algorithm, "seed": seed,
                         "config": relative(config_path), "steps": relative(steps_path),
                         "run_dir": f"hypothesis_4/experiment_2/runs/{BATCH}/{run_id}",
                         "expected_batches": len(times), "expected_action_records": 1100, "expected_week_records": 11})
        assert all(config == common_configs[0] for config in common_configs)

    # 默认入口供官方check使用；九run实际矩阵以独立manifest为准。
    (INIT / "init_config.json").write_bytes((configs / f"{BATCH}_interest_s0.json").read_bytes())
    (INIT / "steps.yaml").write_bytes((INIT / "steps_s0.yaml").read_bytes())
    generated.extend([INIT / "init_config.json", INIT / "steps.yaml"])
    manifest = {
        "batch_id": BATCH, "execution_authorized": False,
        "generator": relative(Path(__file__).resolve()),
        "source_sha256": source_hashes, "output_sha256": {relative(path): sha256(path) for path in generated},
        "user_data": {"files_observed": user_data_files, "used": False, "basis": "采用experiment_1已冻结人口、参数、样本和行动表"},
        "timezone": "Asia/Shanghai", "window_start": START.replace(tzinfo=SHANGHAI).isoformat(),
        "window_end_exclusive": END.replace(tzinfo=SHANGHAI).isoformat(),
        "official_available_at": "2026-03-24T20:00:00+08:00", "official_time_basis": "建模约定；不是原帖观测时刻",
        "event_week_action_schedule": common_event_schedule,
        "seeds": seeds, "runs": runs,
        "budget": {"decision_opportunities": 9900, "extra_requests_limit": 990, "extra_requests_per_action": 1,
                   "content_retry_budget": RETRY_BUDGET, "active_wall_seconds": None,
                   "execution_note": "本轮只准备与离线验收，模型、发送范围和时长/费用在启动前另行确定"},
        "mechanisms": {"arrival": "三臂timestamp，published_at与本臂available_at均不晚于行动",
                       "agent_return": {"random": "次周周一", "interest": "次周周一", "chronological": "批末统一入池，后续行动批次可见"},
                       "agenda": "官方普通参与推荐，不置顶、不经悼念保底强制选入，不保证22/22阅读；只有interest使用事件周其他悼念帖最多5条保底，其余臂不使用议程",
                       "event_week_schedule": "只覆盖5位悼念Agent的W13决策小时；三臂三seed同表，保留693调度批，W13原hour18为空批",
                       "stable_keys": "外部帖external:source_pid；Agent帖作者×周，运行期自增ID不参与选择",
                       "tie_break": "chronological按发布时间与稳定来源键倒序；不依赖入池或生成完成顺序",
                       "random_stream": "seed、周、Agent、用途分流；逐帖噪声包含稳定来源键",
                       "prompt_vocab": "保留冻结type_vocab用于推荐特征与测量；生成prompt只选当次可见正文已出现的词，不引入未见词、整周统计或全feed份额摘要",
                       "final_tick": "末次行动后推进到窗口右界并收齐W22尾部真实帖，不增加行动机会"},
        "default_config": relative(INIT / "init_config.json"), "default_steps": relative(INIT / "steps.yaml"),
    }
    write_json(manifest_path, manifest)
    # 子目录各自只索引一级资产，父级README仅链接子目录。
    for directory, description in [(inputs, "冻结样本、共享人口与行动表"), (configs, "timestamp三臂×三seed配置")]:
        rows = [f"# {description}", "", "由上级config_params.py生成，哈希和含义见上级manifest.json。", "", "| 文件 | 职责 |", "|---|---|"]
        for path in sorted(directory.glob("*.json")):
            role = ("窗口250条原始样本" if path.name.startswith("injection") else
                    "W11初始17条原始样本" if path.name.startswith("initial") else
                    "配对三臂共享人口" if path.name.startswith("population") else
                    "配对三臂行动表" if path.name.startswith("action_schedule") else "独立run配置；algorithm/seed见文件名")
            rows.append(f"| [{path.name}]({path.name}) | {role} |")
        (directory / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": relative(manifest_path), "runs": len(runs), "opportunities": 9900,
                      "batches_by_seed": {seed: data["expected_batches"] for seed, data in seeds.items()},
                      "execution_authorized": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
