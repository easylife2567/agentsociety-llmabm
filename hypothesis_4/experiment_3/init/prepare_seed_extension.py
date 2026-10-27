"""仅离线准备 B/D/R 消融 seed 3–9；复用已完成的同 seed Full。

使用标准库，不导入历史生成器、不读取凭据、不调用模型或启动引擎。
新文件与已有字节不一致时拒绝覆盖；旧九配置及其冻结清单保持原样。
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

INIT = Path(__file__).resolve().parent
ROOT = INIT.parents[2]
E2 = ROOT / "hypothesis_4/experiment_2"
BASELINE = "69d243955d341444ae769fae5bf23dc160465cd6"
BATCH = "timestamp_bdr_v1_seed3_9"
RUN_ROOT = "hypothesis_4/experiment_3/runs/timestamp_bdr_v1_attempt_02"
LEDGER = f"{RUN_ROOT}/execution_records/seed3_9/_extra_attempts.count"
CONDITIONS = {"no_b": "baseline_utility", "no_d": "spiral_scale", "no_r": "decay"}
SEEDS = tuple(range(3, 10))
MODEL = "deepseek-v4.1-flash"
RESPONSE_MODEL = "deepseek-v4-1-flash-261017"
MANIFEST = INIT / "manifest_seed3_9.json"


def relative(path):
    return path.relative_to(ROOT).as_posix()


def source_path(value):
    path = (ROOT / value).resolve()
    path.relative_to(ROOT)
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def make_config(full, seed, parameter):
    config = deepcopy(full)
    if len(config["env_modules"]) != 1 or len(config["agents"]) != 100:
        raise ValueError("Full须含1环境及100人")
    env = config["env_modules"][0]
    if env["module_type"] != "CurationDynamicsSpace":
        raise ValueError("Full环境类型错误")
    kwargs = env["kwargs"]
    if kwargs["recommendation_algorithm"] != "interest" or kwargs["random_seed"] != seed:
        raise ValueError("Full推荐制度或seed错误")
    if (kwargs["arrival_mode"], kwargs["arrival_official_policy"]) != ("timestamp", "ordinary"):
        raise ValueError("Full时序/官方策略错误")
    for key, stem in (("injection_data_path", "injection_sample"),
                      ("weekly_initial_injection_data_path", "initial_sample_weekly_lag")):
        expected = f"hypothesis_4/experiment_2/init/inputs/{stem}_s{seed}.json"
        if kwargs[key] != expected:
            raise ValueError(f"Full输入路径错误: {key}")
    ids = []
    for agent in config["agents"]:
        profile = agent["kwargs"]
        ids.append(agent["agent_id"])
        if agent["agent_type"] != "CurationDiscourseAgent" or agent["agent_id"] != profile["id"]:
            raise ValueError("Full Agent类型或ID错误")
        if parameter not in profile["params"]:
            raise ValueError("Full缺少指定消融参数")
        if profile["content_retry_budget"] != {
                "limit": 2310,
                "ledger_path": "hypothesis_4/experiment_2/runs/timestamp_v1_seed3_9/_extra_attempts.count"}:
            raise ValueError("Full额外请求预算与冻结主实验不符")
        profile["params"][parameter] = 0.0
        profile["content_retry_budget"] = {"limit": 2310, "ledger_path": LEDGER}
    if set(ids) != set(range(1, 101)):
        raise ValueError("Full须完整覆盖ID 1至100")
    # 还原已声明差异后逐字段比较，避免混入额外科学或操作改动。
    restored = deepcopy(config)
    for original, current in zip(full["agents"], restored["agents"]):
        current["kwargs"]["params"][parameter] = original["kwargs"]["params"][parameter]
        current["kwargs"]["content_retry_budget"] = deepcopy(original["kwargs"]["content_retry_budget"])
    if restored != full:
        raise ValueError("消融含未声明的Full差异")
    return config


def prepare():
    old_lock = read_json(INIT / "source_lock.json")
    old_manifest = read_json(INIT / "manifest.json")
    old_paths = {INIT / "config_params.py", INIT / "source_lock.json", INIT / "manifest.json"}
    for group in (old_lock["source_sha256"], old_manifest["output_sha256"]):
        for name, expected in group.items():
            path = source_path(name)
            if sha256(path) != expected:
                raise ValueError(f"旧消融冻结资产已变化: {name}")
            old_paths.add(path)
    for name, expected in old_lock["mechanism_sha256"].items():
        if sha256(source_path(name)) != expected:
            raise ValueError(f"旧消融机制哈希已变化: {name}")
    relocation_path = E2 / "runs/timestamp_v1/relocation.json"
    relocation = read_json(relocation_path)
    completed = {row["seed"]: row for row in relocation["completed_runs"]
                 if row["algorithm"] == "interest" and row["seed"] in SEEDS}
    if set(completed) != set(SEEDS):
        raise ValueError("缺少完整的同seed Full配对目录")
    if not completed[6]["run_dir"].endswith("timestamp_v1_interest_s6_resume1"):
        raise ValueError("seed6 Full必须配对实际resume1结果")
    records = E2 / "runs/timestamp_v1/execution_records/seed3_9"
    runtime_path = records / "runtime_plan.json"
    completion_path = records / "completion_check.json"
    runtime, completion = read_json(runtime_path), read_json(completion_path)
    if runtime["model"] != MODEL or runtime["expected_response_model"] != RESPONSE_MODEL:
        raise ValueError("Full冻结模型与本次约定不符")
    if completion["status"] != "passed":
        raise ValueError("Full完成核验未通过")
    full_checks = {row["run_id"]: row for row in completion["runs"]}
    e2_manifest_path = E2 / "init/manifest_seed3_9.json"
    e2_manifest = read_json(e2_manifest_path)
    sources = old_paths | {Path(__file__).resolve(), relocation_path, runtime_path,
                           completion_path, e2_manifest_path}
    outputs, runs, pairings = {}, [], {}
    for seed in SEEDS:
        full_source = E2 / f"init/configs/timestamp_v1_interest_s{seed}.json"
        steps_source = E2 / f"init/steps_s{seed}.yaml"
        full_reference = INIT / f"reference/timestamp_v1_interest_s{seed}.json"
        steps_target = INIT / f"steps_s{seed}.yaml"
        full = read_json(full_source)
        sources.update((full_source, steps_source))
        for stem in ("injection_sample", "initial_sample_weekly_lag", "population", "action_schedule"):
            path = E2 / f"init/inputs/{stem}_s{seed}.json"
            sources.add(path)
        for path in (full_source, steps_source, *(E2 / f"init/inputs/{stem}_s{seed}.json"
                for stem in ("injection_sample", "initial_sample_weekly_lag", "population", "action_schedule"))):
            if sha256(path) != e2_manifest["output_sha256"][relative(path)]:
                raise ValueError(f"主实验来源哈希已变化: {relative(path)}")
        outputs[full_reference] = full_source.read_bytes()
        outputs[steps_target] = steps_source.read_bytes()
        actual = completed[seed]
        check = full_checks[actual["run_id"]]
        if (check["steps"], check["actions"], check["weeks"]) != (693, 1100, 11):
            raise ValueError("Full实际完成计数不符")
        if set(check["response_models"]) != {RESPONSE_MODEL}:
            raise ValueError("Full实际响应模型不符")
        actual_dir = source_path(actual["run_dir"])
        for name in ("SOCIETY.json", "SOCIETY_STEP.json", "env/CurationDynamicsSpace/state/ENV_STATE.json"):
            path = actual_dir / name
            if not path.is_file():
                raise ValueError(f"Full实际产物缺失: {relative(path)}")
            sources.add(path)
        pairings[str(seed)] = {"run_id": actual["run_id"], "run_dir": actual["run_dir"],
            "execution_record": actual["execution_record"], "reference": relative(full_reference),
            "source_config": relative(full_source), "source_steps": relative(steps_source),
            "configured_model": MODEL, "response_models": check["response_models"],
            "completion_evidence": relative(completion_path),
            "reused_without_rerunning": True}
        for condition, parameter in CONDITIONS.items():
            run_id = f"timestamp_bdr_v1_interest_{condition}_s{seed}"
            path = INIT / "configs" / f"{run_id}.json"
            outputs[path] = json_bytes(make_config(full, seed, parameter))
            runs.append({"run_id": run_id, "algorithm": "interest", "condition": condition, "seed": seed,
                "ablation_parameter": f"kwargs.params.{parameter}", "ablation_value": 0.0,
                "full_reference": relative(full_reference), "full_run_dir": actual["run_dir"],
                "config": relative(path), "steps": relative(steps_target),
                "run_dir": f"{RUN_ROOT}/{run_id}",
                "expected_counts": {"agents": 100, "batches": 693, "action_records": 1100, "weeks": 11},
                "execution_authorized": False})
    frozen = {relative(path): sha256(path) for path in sorted(sources)}
    manifest = {"batch_id": BATCH, "baseline_commit": BASELINE, "execution_authorized": False,
        "preparation_scope": "仅准备21次消融、离线验收及单列最小接口探针；不得启动仿真",
        "llm_calls_by_generator": 0, "generator": relative(Path(__file__).resolve()),
        "source_sha256": frozen, "mechanism_sha256": old_lock["mechanism_sha256"],
        "old_assets_unchanged_sha256": {relative(path): frozen[relative(path)] for path in sorted(old_paths)},
        "output_sha256": {relative(path): hashlib.sha256(data).hexdigest() for path, data in sorted(outputs.items())},
        "runs": runs, "execution_order": [row["run_id"] for row in runs], "full_pairings": pairings,
        "scientific_changes": {condition: {"parameter": f"agents[*].kwargs.params.{parameter}",
            "value": 0.0, "agent_count": 100} for condition, parameter in CONDITIONS.items()},
        "operational_changes": ["agents[*].kwargs.content_retry_budget.ledger_path"],
        "unchanged_from_same_seed_full": ["env_modules", "input_paths_and_bytes", "population_except_ablation",
            "action_schedule", "type_vocab", "activity_threshold", "timestamp_and_official_policy", "steps"],
        "metrics": {"comparison": "消融−同seed Full，先按seed汇总窗口指标", "full_window": ["2026-W12", "2026-W22"],
            "B_primary": {"window": ["2026-W19", "2026-W22"], "metric": "全体每周成功发帖数的四周均值"},
            "D_primary": {"window": ["2026-W19", "2026-W22"], "metric": "玩梗型Agent speak=true发言率", "denominator": 76},
            "R_primary": {"window": ["2026-W14", "2026-W18"], "metric": "全体speak=true发言率", "denominator": 500},
            "speak_vs_posted": "speak发言率与posted成功发帖率分开；空feed/行动/生成/发布失败不删分母",
            "source": "hypothesis_4/experiment_3/EXPERIMENT.md 原固定指标窗口"},
        "model": {"configured_alias": MODEL, "expected_response_model": RESPONSE_MODEL,
            "equivalence_basis": "用户明确确认沿用当前模型；Full实际响应见逐seed完成证据",
            "server_identity": "记录可得标识；名称及用户确认不提供后台权重可验证证明"},
        "decision_opportunities": 23100, "extra_requests_limit": 2310, "max_agent_body_requests": 25410,
        "budget": {"decision_opportunities": 23100, "extra_requests_limit": 2310,
            "max_agent_body_requests": 25410, "extra_requests_per_action": 1, "max_wall_hours": 48,
            "started_at": None, "deadline_at": None, "ledger_path": LEDGER,
            "execution_authorized": False, "api_probe_included": False},
        "retry_budget": {"scope": "all_21_new_runs", "limit": 2310, "ledger_path": LEDGER,
            "unique_ledger_paths": [LEDGER], "max_extra_per_opportunity": 1,
            "initial_count_required": 0, "ledger_created_by_generator": False,
            "old_ledger_extra_requests_used": 5, "old_ledger_policy": "旧账本及5次消耗保留，不抵扣或复用本次额度"},
        "runtime_controls": {"max_wall_hours": 48, "started_at": None, "deadline_at": None,
            "budget_starts": "未来正式启动时开始，不从准备或API探针开始", "max_parallel": 2,
            "launch_order": "seed3→9，各seed按no_b→no_d→no_r补空位；完成顺序取决于耗时",
            "stop_policy": "任一异常/技术请求错误时两路联停；保全记录，不自动恢复、重跑或接续checkpoint",
            "run_root": RUN_ROOT},
        "api_probe_accounting": {"separate_record_required": True, "included_in_body_ledger": False,
            "generator_probe_requests": 0, "note": "最小接口探针单列请求与tokens，不计正文额度，不授权启动仿真"},
        "execution_note": "配置存在及离线通过均不等于正式启动授权；沿既有实验目录扩充，不新建探索run"}
    outputs[MANIFEST] = json_bytes(manifest)
    return outputs, frozen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只复算检查，不写文件")
    args = parser.parse_args()
    outputs, frozen = prepare()
    for path, data in outputs.items():
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f"拒绝覆盖字节不同的既有目标: {relative(path)}")
        if args.check and not path.is_file():
            raise ValueError(f"缺少生成资产: {relative(path)}")
    if not args.check:
        for path, data in outputs.items():
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    for name, expected in frozen.items():
        if sha256(source_path(name)) != expected:
            raise ValueError(f"生成期间来源发生变化: {name}")
    print(json.dumps({"configs": 21, "outputs": len(outputs), "manifest": relative(MANIFEST),
        "mode": "check" if args.check else "prepare", "execution_authorized": False,
        "llm_calls": 0, "decision_opportunities": 23100, "max_agent_body_requests": 25410}, ensure_ascii=False))


if __name__ == "__main__":
    main()
