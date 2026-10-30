"""只用标准库准备小时回流配置；不启动引擎、不创建运行账本。"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
E2 = ROOT / "hypothesis_4/experiment_2"
E3 = ROOT / "hypothesis_4/experiment_3"
MAIN = E2 / "init/hourly_return_v1"
ABLATION = E3 / "init/hourly_return_v1"
BASELINE = "aad3267fc9929a08a453ba427bdf25919bbffc70"
MAIN_RUN_ROOT = "hypothesis_4/experiment_2/runs/hourly_return_v1"
ABLATION_RUN_ROOT = "hypothesis_4/experiment_3/runs/hourly_return_bdr_v1"
MAIN_LEDGER = f"{MAIN_RUN_ROOT}/_extra_attempts.count"
ABLATION_LEDGER = f"{ABLATION_RUN_ROOT}/_extra_attempts.count"
MAIN_LIMIT = 2200
ABLATION_LIMIT = 3300
ALGORITHMS = ("random", "chronological", "interest")
CONDITIONS = {"no_b": "baseline_utility", "no_d": "spiral_scale", "no_r": "decay"}
MECHANISMS = (
    "custom/agents/curation_arrival_action.py",
    "custom/agents/curation_content_quality.py",
    "custom/agents/curation_discourse_agent.py",
    "custom/envs/curation_arrival_schedule.py",
    "custom/envs/curation_dynamics_space.py",
    "custom/envs/curation_mechanisms.py",
    "custom/envs/curation_assets/vocabs.json",
)
EXPECTED_COUNTS = {"agents": 100, "batches": 693, "action_records": 1100, "weeks": 11}


def relative(path):
    return path.relative_to(ROOT).as_posix()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_path(name):
    """来源只能指向本工作区，不能经绝对路径或符号链接逃逸。"""
    path = (ROOT / name).resolve()
    path.relative_to(ROOT)
    return path


def validate_full(config, seed, algorithm):
    if len(config["env_modules"]) != 1 or len(config["agents"]) != 100:
        raise ValueError("源配置必须为一个环境和100位Agent")
    env = config["env_modules"][0]
    kw = env["kwargs"]
    if env["module_type"] != "CurationDynamicsSpace" or kw["recommendation_algorithm"] != algorithm:
        raise ValueError("源环境或算法不符")
    if kw["random_seed"] != seed or kw["schedule_mode"] != "arrival_timing" or kw["arrival_mode"] != "timestamp":
        raise ValueError("源seed或信息时钟不符")
    if kw["chronological_total_batches"] != 693 or "arrival_agent_return_policy" in kw:
        raise ValueError("源批次数或历史回流配置不符")
    if {a["agent_id"] for a in config["agents"]} != set(range(1, 101)):
        raise ValueError("源Agent ID不完整")
    for agent in config["agents"]:
        profile = agent["kwargs"]
        if agent["agent_type"] != "CurationDiscourseAgent" or agent["agent_id"] != profile["id"]:
            raise ValueError("源Agent类型或profile ID不符")
        if not profile["arrival_timing"] or not all(k in profile["params"] for k in CONDITIONS.values()):
            raise ValueError("源Agent缺少时钟或组件参数")


def set_budget(config, limit, ledger):
    # 这是新批统一上界，不把旧批不同seed的共享上界混到同一账本。
    for agent in config["agents"]:
        agent["kwargs"]["content_retry_budget"] = {"limit": limit, "ledger_path": ledger}


def runtime_plan(limit, ledger, planned_runs):
    return {
        "execution_authorized": False,
        "status": "preparation_only",
        "new_runtime_budget_frozen": False,
        "planned_new_runs": planned_runs,
        "planned_decision_opportunities": planned_runs * 1100,
        "extra_requests_preparation_limit": limit,
        "body_outer_requests_preparation_limit": planned_runs * 1100 + limit,
        "max_extra_per_opportunity": 1,
        "retry_ratio": 0.1,
        "ledger_path": ledger,
        "ledger_created": False,
        "walltime_hours": None,
        "cost_limit": None,
        "model": None,
        "max_concurrent_runs": None,
        "started_at": None,
        "deadline_at": None,
        "note": "配置上界不构成运行授权；模型、费用、时限、顺序和停止规则须在未来执行前冻结。",
    }


def readme(label, run_root, variant=False):
    scope = "no_b/no_d/no_r各10seed；Full引用同seed新兴趣主实验，不新增Full运行" if variant else "三臂各10seed；随机/兴趣20次计划新运行，时序10次等待复用可比性核验"
    limit = ABLATION_LIMIT if variant else MAIN_LIMIT
    return f"""# {label}

本目录是小时回流候选配置，{scope}。全部配置显式声明`arrival_agent_return_policy=next_batch`：同小时批末统一入池，从后续行动批次可见。每人每周一次、外部输入、人口、行为、提示、周龄生命周期和步骤保持来源版本。

| 直接资产 | 用途 |
|---|---|
| [configs/](configs/README.md) | 30份候选配置及逐文件索引 |
| [manifest.json](manifest.json) | 来源/机制/输出哈希、配对、未来输出与预算准备上界 |
| [README.md](README.md) | 本级索引和准备边界 |

生成器为[prepare_hourly_return.py](../../../experiment_2/init/prepare_hourly_return.py)，从项目根执行`$PYTHON_PATH hypothesis_4/experiment_2/init/prepare_hourly_return.py --check`只读重算核对。默认生成也拒绝覆盖不一致文件，不调用旧生成器。steps引用旧冻结字节，没有复制或改写。

未来输出根为`{run_root}`，本次不创建引擎输出或账本。新批独立额外请求准备上界为{limit}，不借用或清零旧批账本；所有execution_authorized均为false，运行时限、费用和实际模型尚未冻结。生成成功不代表运行通过，时序复用与Full可用性均以manifest中的待验状态为准。

旧周回流结果和checkpoint保持，不用于新小时回流条件中途接续。消融仅改变一个组件参数与独立预算账本，并与同seed新Full配对；不将旧周回流消融直接减去新Full。
""".encode("utf-8")


def config_index(rows):
    lines = ["# 候选配置索引", "", "本级仅列配置文件；来源、配对和未授权运行边界见[上级清单](../manifest.json)。", "", "| 文件 | 条件 | seed | 准备状态 |", "|---|---|---:|---|"]
    for row in rows:
        name = Path(row["config"]).name
        lines.append(f"| [{name}]({name}) | {row['algorithm']}/{row['condition']} | {row['seed']} | {row['status']} |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_outputs():
    outputs, source_hashes, main_rows, ablation_rows, full_refs = {}, {}, [], [], {}
    # 原manifest锁住既有配置和输入；新生成器不重抽样，也不读取凭据。
    locks = [E2 / "init/manifest.json", E2 / "init/manifest_seed3_9.json"]
    expected_hashes = {}
    for path in locks:
        source_hashes[relative(path)] = sha256(path.read_bytes())
        for name, digest in read_json(path)["output_sha256"].items():
            if name in expected_hashes and expected_hashes[name] != digest:
                raise ValueError(f"旧清单对来源哈希有分歧：{name}")
            expected_hashes[name] = digest

    def frozen(path):
        name = relative(path)
        actual = sha256(path.read_bytes())
        if expected_hashes.get(name) != actual:
            raise ValueError(f"来源与旧冻结清单不一致：{name}")
        source_hashes[name] = actual

    for seed in range(10):
        steps = E2 / f"init/steps_s{seed}.yaml"
        frozen(steps)
        for stem in ("injection_sample", "initial_sample_weekly_lag", "population", "action_schedule"):
            frozen(E2 / f"init/inputs/{stem}_s{seed}.json")
        paired = []
        for algorithm in ALGORITHMS:
            old_path = E2 / f"init/configs/timestamp_v1_{algorithm}_s{seed}.json"
            frozen(old_path)
            old = read_json(old_path)
            validate_full(old, seed, algorithm)
            normalized = deepcopy(old)
            normalized["env_modules"][0]["kwargs"]["recommendation_algorithm"] = "interest"
            paired.append(normalized)
            new = deepcopy(old)
            new["env_modules"][0]["kwargs"]["arrival_agent_return_policy"] = "next_batch"
            set_budget(new, MAIN_LIMIT, MAIN_LEDGER)
            run_id = f"hourly_return_v1_{algorithm}_s{seed}"
            path = MAIN / f"configs/{run_id}.json"
            outputs[path] = encode(new)
            row = {
                "run_id": run_id, "algorithm": algorithm, "seed": seed, "condition": "full",
                "config": relative(path), "source_config": relative(old_path),
                "steps": relative(steps), "run_dir": f"{MAIN_RUN_ROOT}/{run_id}",
                "status": "planned_reuse_pending" if algorithm == "chronological" else "planned_new",
                "execution_authorized": False, "expected_counts": EXPECTED_COUNTS,
            }
            if algorithm == "chronological":
                row["reuse_candidate"] = {
                    "run_id": f"timestamp_v1_chronological_s{seed}",
                    "run_dir": f"hypothesis_4/experiment_2/runs/timestamp_v1/timestamp_v1_chronological_s{seed}",
                    "status": "pending",
                    "checks_required": ["实际完成性", "时序新旧行为等价", "输入及行动表一致", "模型/提示/运行参数可比"],
                    "approved": False,
                }
            main_rows.append(row)
            if algorithm == "interest":
                full_refs[str(seed)] = {"config": relative(path), "run_id": run_id,
                    "run_dir": row["run_dir"], "config_sha256": sha256(outputs[path]),
                    "status": "planned_new_full_pending_execution"}
                for condition, parameter in CONDITIONS.items():
                    variant = deepcopy(new)
                    for agent in variant["agents"]:
                        agent["kwargs"]["params"][parameter] = 0.0
                    set_budget(variant, ABLATION_LIMIT, ABLATION_LEDGER)
                    ablation_id = f"hourly_return_bdr_v1_interest_{condition}_s{seed}"
                    ablation_path = ABLATION / f"configs/{ablation_id}.json"
                    outputs[ablation_path] = encode(variant)
                    ablation_rows.append({
                        "run_id": ablation_id, "algorithm": "interest", "seed": seed, "condition": condition,
                        "config": relative(ablation_path), "source_config": relative(path),
                        "full_reference": relative(path), "full_run_dir": row["run_dir"],
                        "steps": relative(steps), "run_dir": f"{ABLATION_RUN_ROOT}/{ablation_id}",
                        "status": "planned_new", "execution_authorized": False,
                        "ablation_parameter": f"agents[*].kwargs.params.{parameter}", "ablation_value": 0.0,
                        "expected_counts": EXPECTED_COUNTS,
                    })
        if any(value != paired[0] for value in paired[1:]):
            raise ValueError(f"同seed三臂来源除算法外存在差异：{seed}")

    outputs[MAIN / "README.md"] = readme("小时回流三臂配置", MAIN_RUN_ROOT)
    outputs[ABLATION / "README.md"] = readme("小时回流兴趣组件消融配置", ABLATION_RUN_ROOT, True)
    outputs[MAIN / "configs/README.md"] = config_index(main_rows)
    outputs[ABLATION / "configs/README.md"] = config_index(ablation_rows)
    source_hashes[relative(Path(__file__).resolve())] = sha256(Path(__file__).read_bytes())
    mechanisms = {name: sha256(source_path(name).read_bytes()) for name in MECHANISMS}
    common = {
        "baseline_commit": BASELINE, "generator": relative(Path(__file__).resolve()),
        "execution_authorized": False, "llm_calls": 0, "timezone": "Asia/Shanghai",
        "arrival_agent_return_policy": "next_batch", "source_sha256": source_hashes,
        "mechanism_sha256": mechanisms, "combined_unique_conditions": 60,
        "combined_planned_new_runs": 50, "combined_planned_reuse_pending": 10,
        "combined_planned_new_decision_opportunities": 55000,
        "scientific_changes": ["env_modules[0].kwargs.arrival_agent_return_policy"],
        "operational_changes": ["agents[*].kwargs.content_retry_budget.limit", "agents[*].kwargs.content_retry_budget.ledger_path"],
        "preserved": ["外部输入/样本/人口/提示", "行动表与W13共同覆盖", "每人每周一次及693批steps", "整数周龄生命周期和曝光机制", "原始历史结果与checkpoint"],
    }
    for directory, rows, budget in (
        (MAIN, main_rows, runtime_plan(MAIN_LIMIT, MAIN_LEDGER, 20)),
        (ABLATION, ablation_rows, runtime_plan(ABLATION_LIMIT, ABLATION_LEDGER, 30)),
    ):
        manifest = dict(common)
        manifest.update({
            "batch_id": "hourly_return_v1" if directory == MAIN else "hourly_return_bdr_v1",
            "experiment_id": 2 if directory == MAIN else 3,
            "runs": rows, "seeds": list(range(10)), "generated_configs": len(rows),
            "runtime_conditions": budget,
            "output_sha256": {relative(path): sha256(data) for path, data in outputs.items() if directory in path.parents},
        })
        if directory == ABLATION:
            manifest.update({"full_references": full_refs, "comparison_cells": 40,
                "additional_full_runs": 0, "comparison": "ablation-minus-same-seed-new-interest-full",
                "component_definitions": {"no_b": "baseline_utility=0; U=R*D", "no_d": "spiral_scale=0; D=1; U=B+R*(1-B)", "no_r": "decay=0; R=1; U=D"}})
        else:
            manifest.update({"comparison_cells": 30, "planned_new_runs": 20, "planned_reuse_pending": 10})
        outputs[directory / "manifest.json"] = encode(manifest)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只读重算全部来源/输出；缺失或冲突即失败")
    args = parser.parse_args()
    outputs = build_outputs()
    conflicts, missing = [], []
    for path, data in outputs.items():
        if not path.exists():
            missing.append(path)
        elif not path.is_file() or path.read_bytes() != data:
            conflicts.append(relative(path))
    for directory in (MAIN, ABLATION):
        if directory.exists():
            conflicts.extend(relative(path) for path in directory.rglob("*") if path.is_file() and path not in outputs)
    if conflicts:
        raise ValueError(f"拒绝覆盖不一致或未登记资产：{conflicts}")
    if args.check and missing:
        raise ValueError(f"候选资产缺失：{[relative(path) for path in missing]}")
    if not args.check:
        # 全部来源和已有输出已核验，随后只独占创建缺失文件。
        for path in missing:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(outputs[path])
    print(json.dumps({"mode": "check" if args.check else "prepare", "configs": 60,
        "planned_new_runs": 50, "planned_reuse_pending": 10, "files": len(outputs),
        "execution_authorized": False, "llm_calls": 0,
        "manifests": [relative(MAIN / "manifest.json"), relative(ABLATION / "manifest.json")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
