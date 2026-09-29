"""生成真实帖到达时机四格诊断配置；只读取冻结基准，不运行仿真。

正式配置写入既有 experiment 的独立 init 子目录。输入哈希阻止无意重采样，
前缀使用完整 steps 的前三周；恢复时只接受清单登记的前缀到完整文件扩展。
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "hypothesis_4/experiment_1/init"
OUTPUT = INIT / "arrival_timing_diagnostic"
BATCH = "arrival_timing_diagnostic"
BASELINE_COMMIT = "bab8e2a98d5cf99d855a84de8da7d2ac16cad575"
SOURCE_HASHES = {
    "hypothesis_4/experiment_1/init/configs/anchored_v1_interest_s0.json": "10b24553bc941af81b20476c60207aa8cd6cf7a26c9327f71df6583d2e80aba1",
    "hypothesis_4/experiment_1/init/configs/anchored_v1_random_s0.json": "f0e3627dfa7712586009408d392bd252208c92bd7beb4acda2d16761e4fed88c",
    "hypothesis_4/experiment_1/init/configs/anchored_v1_chronological_s0.json": "1c2f527a12bee9923fcbb1bbaab060db78a59678beaf29f14cbf33b4df86de97",
    "hypothesis_4/experiment_1/init/injection_sample_s0.json": "5b0f9efedffac94ba2b3a8a639aa8b0b3c0ef2bb2c1f31a8377ac76ec29608d5",
    "hypothesis_4/experiment_1/init/initial_sample_weekly_lag_s0.json": "8915813f6b4258c03a137e3c8b0e27dc763a724bd0947b3a0190ee1cc04fe6bf",
    "custom/envs/curation_assets/vocabs.json": "7db323585fdc98594da4a4b97e49ce5d3d1654c89839da7c2a754c7515b15e69",
}


def digest(path):
    """哈希按文件原始字节计算，避免路径相同但内容变化。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def steps_text(times, count):
    """tick 从本次行动推进到下次行动，前缀末步保留完整时钟跨度。"""
    lines = [f'start_t: "{times[0].isoformat(timespec="seconds")}"', "steps:"]
    for index, moment in enumerate(times[:count]):
        following = times[index + 1] if index + 1 < len(times) else moment + timedelta(hours=1)
        lines.extend(["  - type: run", "    num_steps: 1", f"    tick: {int((following - moment).total_seconds())}"])
    return "\n".join(lines) + "\n"


def main():
    # 本批授权范围固定：共享100人、11周、seed 0，不从原生成器重抽人口。
    for path, expected in SOURCE_HASHES.items():
        if digest(ROOT / path) != expected:
            raise ValueError(f"冻结输入已变化：{path}")
    base = {algorithm: json.loads((INIT / f"configs/anchored_v1_{algorithm}_s0.json").read_text())
            for algorithm in ("interest", "random", "chronological")}
    assert base["interest"]["agents"] == base["random"]["agents"]
    schedule = base["chronological"]["env_modules"][0]["kwargs"]["chronological_action_hours"]
    hours = sorted(set(schedule.values()))
    assert len(schedule) == 100 and len(hours) == 63
    times = [datetime(2026, 3, 16) + timedelta(weeks=week, hours=hour)
             for week in range(11) for hour in hours]
    assert len(times) == 693 and times[0] == datetime(2026, 3, 16, 6)
    population = deepcopy(base["interest"]["agents"])
    assert Counter(a["kwargs"]["agent_type"] for a in population) == {
        "marketing": 23, "mourning": 22, "other": 21, "meme": 19, "education": 15}

    # 仅去掉固定人设对离世的确定陈述；职业、群体风格和数值参数保持冻结。
    statement = "你是被其离世触动的关注者，表达真诚克制，主要是追思、缅怀，以及由事件引发的健康、工作与生活感慨。"
    replacement = "你是关注相关人物的普通用户，表达真诚克制，重视情感与生活感受；只在所见内容支持离世事实时表达追思、缅怀，否则回应实际所见内容。"
    changed = []
    for agent in population:
        profile = agent["kwargs"]
        assert agent["agent_id"] == profile["id"]
        if statement in profile["persona"]:
            profile["persona"] = profile["persona"].replace(statement, replacement)
            changed.append(agent["agent_id"])
        profile["arrival_timing"] = True
        profile["chronological_action_hour"] = schedule[str(agent["agent_id"])]
    assert len(changed) == 22

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "steps.yaml").write_text(steps_text(times, 693), encoding="utf-8")
    (OUTPUT / "steps_prefix.yaml").write_text(steps_text(times, 189), encoding="utf-8")
    write_json(OUTPUT / "population.json", population)
    write_json(OUTPUT / "action_schedule.json", {"timezone": "Asia/Shanghai", "action_hours": schedule,
               "nonempty_hours_per_week": hours, "action_times": [t.isoformat() + "+08:00" for t in times]})

    # 四格唯一操纵为推荐制度和普通帖到达方式；所有配置均用相同种群与行动表。
    runs = []
    configs = []
    for algorithm in ("interest", "random"):
        for arrival_mode in ("preload", "timestamp"):
            config = deepcopy(base[algorithm])
            config["agents"] = deepcopy(population)
            kwargs = config["env_modules"][0]["kwargs"]
            kwargs.update(schedule_mode="arrival_timing", arrival_mode=arrival_mode,
                          chronological_action_hours=schedule, chronological_total_batches=693,
                          weekly_initial_injection_data_path="hypothesis_4/experiment_1/init/initial_sample_weekly_lag_s0.json")
            run_id = f"{BATCH}_{arrival_mode}_{algorithm}_s0"
            path = OUTPUT / f"{run_id}.json"
            write_json(path, config)
            configs.append(config)
            runs.append({"run_id": run_id, "algorithm": algorithm, "arrival_mode": arrival_mode, "seed": 0,
                         "config": str(path.relative_to(ROOT)), "config_sha256": digest(path),
                         "run_dir": f"hypothesis_4/experiment_1/runs/{BATCH}/{run_id}",
                         "steps": str((OUTPUT / "steps.yaml").relative_to(ROOT)),
                         "steps_prefix": str((OUTPUT / "steps_prefix.yaml").relative_to(ROOT)),
                         "expected_batches": 693, "prefix_batches": 189,
                         "expected_action_records": 1100, "expected_week_records": 11})
    common = []
    for config in configs:
        normalized = deepcopy(config)
        kwargs = normalized["env_modules"][0]["kwargs"]
        del kwargs["recommendation_algorithm"], kwargs["arrival_mode"]
        common.append(normalized)
    assert all(c == common[0] for c in common)

    # 这是冻结科学与执行清单；实时进度只由任务README及实际checkpoint表达。
    artifacts = ["steps.yaml", "steps_prefix.yaml", "population.json", "action_schedule.json"]
    manifest = {
        "batch_id": BATCH, "baseline_commit": BASELINE_COMMIT,
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "source_sha256": SOURCE_HASHES,
        "artifact_sha256": {name: digest(OUTPUT / name) for name in artifacts},
        "timezone": "Asia/Shanghai", "window_start": "2026-03-16T00:00:00+08:00",
        "window_end_exclusive": "2026-06-01T00:00:00+08:00",
        "official_available_at": "2026-03-24T20:00:00+08:00",
        "official_time_basis": "建模约定；原始官方帖无观测发布时间",
        "expected_external_records": {"initial": 17, "ordinary": 249, "official": 1, "total_unique": 267},
        "persona_cleaned_agent_ids": changed,
        "shared_schedule": "action_schedule.json", "shared_population": "population.json",
        "input_type_vocab_role": "冻结词表保留用于测量审计；新模式生成prompt不得读取它",
        "runs": runs, "execution_order": [run["run_id"] for run in runs],
        "phases": [{"name": "prefix", "end_week": "2026-W14", "batches_per_run": 189},
                   {"name": "full", "end_week": "2026-W22", "batches_per_run": 693}],
        "resume_contract": {"allowed_steps_transition": ["steps_prefix.yaml", "steps.yaml"],
                            "identical_prefix_steps": 189,
                            "engine_behavior": "CLI按completed_step_count与sim_step_cursor跳过已完成步骤；steps_hash变更会警告，runner仅允许清单记录的前缀扩展。",
                            "env_total_batches_remains": 693},
        "budget": {"concurrent_runs": 1, "active_wall_seconds": 86400,
                   "decision_opportunities": 4400, "max_feed_slots": 44000,
                   "content_retries_per_action": 1, "content_retries_batch_limit": 440,
                   "content_success_limit": 4400,
                   "other_api_requests": "另计环境路由与框架请求；4400不是API请求总上限",
                   "prefix_remaining_estimate": "每run前三周最大实测单周耗时乘8再相加；若超过剩余24小时预算，停止等待决策"},
        "primary_outcome": {"weeks": ["2026-W19", "2026-W20", "2026-W21", "2026-W22"],
                            "definition": "Y=实际内部meme类型曝光槽位数/400计划行动机会", "independent_replicates": 1},
        "knowledge_audit": {"full_manual": "W12全部正文与W13官方发布时间前全部正文",
                            "remaining_screen_terms": ["去世", "离世", "逝世", "讣告", "猝死", "抢救无效", "一路走好", "安息", "天堂", "阴间", "冥", "复活", "尸", "逝者"],
                            "meme_screen_source": "custom/envs/curation_assets/vocabs.json",
                            "manual_rule": "记录当前prompt是否支持新增事件事实，并区分真实已发布来源、preload提前来源和无可见来源支持；关键词命中不是违规判定。",
                            "nonhit_sample_seed": 0, "nonhit_max_per_run": 20,
                            "nonhit_strata": {"early_W12_W18": 10, "late_W19_W22": 10}},
        "historical_references": [f"archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/raw/anchored_v1_{a}_s0" for a in ("interest", "random")],
    }
    write_json(OUTPUT / "manifest.json", manifest)
    print(json.dumps({"manifest": str((OUTPUT / "manifest.json").relative_to(ROOT)),
                      "runs": len(runs), "agents_per_run": 100, "batches_per_run": 693,
                      "prefix_batches_per_run": 189, "persona_cleaned": len(changed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
