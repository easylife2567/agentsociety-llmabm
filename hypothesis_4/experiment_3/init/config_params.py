"""从冻结的 timestamp Full 生成九份单因素消融配置；不启动仿真。"""

import hashlib
import json
from pathlib import Path


INIT = Path(__file__).resolve().parent
WORKSPACE = INIT.parents[2]
BASELINE = "69d243955d341444ae769fae5bf23dc160465cd6"
CONDITIONS = {
    "no_b": "baseline_utility",
    "no_d": "spiral_scale",
    "no_r": "decay",
}
LEDGER = "hypothesis_4/experiment_3/runs/timestamp_bdr_v1/_extra_attempts.count"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(WORKSPACE).as_posix()


def workspace_path(value):
    """冻结清单只能指向当前隔离工作区内的文件。"""
    path = (WORKSPACE / value).resolve()
    path.relative_to(WORKSPACE)
    return path


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def verify_sources():
    lock = json.loads((INIT / "source_lock.json").read_text(encoding="utf-8"))
    if lock["baseline_commit"] != BASELINE or lock["execution_authorized"] is not False:
        raise ValueError("基线或未授权执行标记不符合当前冻结方案")
    required = {relative(INIT / "reference/main_runtime_plan.json")}
    for seed in range(3):
        required.add(relative(INIT / f"reference/timestamp_v1_interest_s{seed}.json"))
        required.add(relative(INIT / f"steps_s{seed}.yaml"))
        for stem in ("injection_sample", "initial_sample_weekly_lag", "population", "action_schedule"):
            required.add(relative(INIT / f"inputs/{stem}_s{seed}.json"))
    if set(lock["source_sha256"]) != required:
        raise ValueError("冻结输入清单缺失或包含非预期文件")
    mechanisms = {
        "custom/agents/curation_arrival_action.py",
        "custom/agents/curation_content_quality.py",
        "custom/agents/curation_discourse_agent.py",
        "custom/envs/curation_arrival_schedule.py",
        "custom/envs/curation_assets/vocabs.json",
        "custom/envs/curation_dynamics_space.py",
        "custom/envs/curation_mechanisms.py",
    }
    if set(lock["mechanism_sha256"]) != mechanisms:
        raise ValueError("冻结机制清单缺失或包含非预期文件")
    for group in ("source_sha256", "mechanism_sha256"):
        for name, expected in lock[group].items():
            if sha256(workspace_path(name)) != expected:
                raise ValueError(f"冻结哈希不一致：{name}")
    return lock


def make_config(source, seed, parameter):
    # JSON往返复制，避免三个消融条件相互污染。
    config = json.loads(json.dumps(source))
    if len(config["env_modules"]) != 1 or len(config["agents"]) != 100:
        raise ValueError("Full必须包含1个环境及100位Agent")
    env = config["env_modules"][0]
    if env["module_type"] != "CurationDynamicsSpace":
        raise ValueError("Full环境类型不符")
    kwargs = env["kwargs"]
    if kwargs["recommendation_algorithm"] != "interest" or kwargs["random_seed"] != seed:
        raise ValueError("Full制度或seed不符")
    for key, stem in (
        ("injection_data_path", "injection_sample"),
        ("weekly_initial_injection_data_path", "initial_sample_weekly_lag"),
    ):
        expected = f"hypothesis_4/experiment_2/init/inputs/{stem}_s{seed}.json"
        if kwargs[key] != expected:
            raise ValueError(f"Full输入路径不符：{key}")
        kwargs[key] = relative(INIT / f"inputs/{stem}_s{seed}.json")
    ids = []
    for agent in config["agents"]:
        profile = agent["kwargs"]
        ids.append(agent["agent_id"])
        if agent["agent_type"] != "CurationDiscourseAgent" or agent["agent_id"] != profile["id"]:
            raise ValueError("Full Agent类型或ID不符")
        if parameter not in profile["params"]:
            raise ValueError(f"Full缺少消融参数：{parameter}")
        profile["params"][parameter] = 0.0
        budget = profile["content_retry_budget"]
        if budget != {
            "limit": 990,
            "ledger_path": "hypothesis_4/experiment_2/runs/timestamp_v1/_extra_attempts.count",
        }:
            raise ValueError("Full额外请求预算不符")
        budget["ledger_path"] = LEDGER
    if set(ids) != set(range(1, 101)):
        raise ValueError("Full Agent ID应完整覆盖1至100")
    return config


def main():
    # 所有冻结检查和九配置构造均先完成，任何异常都发生在输出写入之前。
    lock = verify_sources()
    outputs = {}
    runs = []
    for seed in range(3):
        full_path = INIT / f"reference/timestamp_v1_interest_s{seed}.json"
        full = json.loads(full_path.read_text(encoding="utf-8"))
        for condition, parameter in CONDITIONS.items():
            run_id = f"timestamp_bdr_v1_interest_{condition}_s{seed}"
            config_path = INIT / "configs" / f"{run_id}.json"
            outputs[config_path] = json_bytes(make_config(full, seed, parameter))
            runs.append({
                "run_id": run_id,
                "algorithm": "interest",
                "seed": seed,
                "condition": condition,
                "ablation_parameter": f"kwargs.params.{parameter}",
                "ablation_value": 0.0,
                "full_reference": relative(full_path),
                "config": relative(config_path),
                "steps": relative(INIT / f"steps_s{seed}.yaml"),
                "expected_counts": {
                    "agents": 100,
                    "batches": 693,
                    "action_records": 1100,
                    "weeks": 11,
                },
                "execution_authorized": False,
            })
    outputs[INIT / "init_config.json"] = outputs[INIT / "configs/timestamp_bdr_v1_interest_no_b_s0.json"]
    outputs[INIT / "steps.yaml"] = (INIT / "steps_s0.yaml").read_bytes()
    manifest = {
        "baseline_commit": BASELINE,
        "execution_authorized": False,
        "llm_calls": 0,
        "source_lock_sha256": sha256(INIT / "source_lock.json"),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "source_sha256": lock["source_sha256"],
        "mechanism_sha256": lock["mechanism_sha256"],
        "output_sha256": {
            relative(path): hashlib.sha256(data).hexdigest()
            for path, data in outputs.items()
        },
        "runs": runs,
        "execution_order": [run["run_id"] for run in runs],
        "decision_opportunities": 9900,
        "extra_requests_limit": 990,
        "retry_budget": {
            "scope": "all_9_runs",
            "ledger_path": LEDGER,
            "unique_ledger_paths": [LEDGER],
            "initial_count_required": 0,
            "ledger_created": False,
        },
        "operational_changes": [
            "env_modules[0].kwargs.injection_data_path",
            "env_modules[0].kwargs.weekly_initial_injection_data_path",
            "agents[*].kwargs.content_retry_budget.ledger_path",
        ],
    }
    outputs[INIT / "manifest.json"] = json_bytes(manifest)
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({
        "configs": len(runs),
        "manifest": relative(INIT / "manifest.json"),
        "execution_authorized": False,
        "llm_calls": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
