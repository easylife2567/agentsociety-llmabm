"""候选小时回流配置禁网验收：不运行环境step、Agent行动、Ray或LLM。"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
from pathlib import Path
import platform
import socket
import sys
import tempfile
import traceback
from unittest.mock import patch


PARAMETERS = {"no_b": "baseline_utility", "no_d": "spiral_scale", "no_r": "decay"}
REPORT = dict(status="checking", simulation_started=False, execution_authorized=False,
              llm_calls=0, network_attempts=0, agent_actions=0, environment_steps=0,
              ray_started=False, checks=[], configs=[], errors=[])


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, condition, details=None):
    if not condition:
        raise AssertionError(name)
    REPORT["checks"].append(dict(name=name, passed=True, details=details))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_path(root, value):
    path = (root / value).resolve()
    path.relative_to(root)
    return path


def verify_environment(root):
    """调用环境技能的实际校验器；只在候选工作区写轻量验收材料。"""
    official = load("hourly_env_validator", root / ".claude/skills/agentsociety-create-env-module/scripts/validate.py")
    official.setup_sys_path(root)
    run_id, _ = official.create_validation_run(
        root, user_request="hourly return offline module acceptance", run_id="hourly-return-offline")
    result = official.validate_module(
        root, run_id=run_id, module_path="custom/envs/curation_dynamics_space.py",
        class_name="CurationDynamicsSpace", refresh_metadata=False)
    checked("官方环境scanner/router/registry验收", result["success"], result["errors"])
    REPORT["official_environment_validation"] = result
    REPORT["official_environment_artifacts"] = str(official.run_dir(root, run_id).relative_to(root))


async def verify(root, scratch):
    import agentsociety2
    import yaml
    from agentsociety2.registry import (
        scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import InitConfig, StepsConfig

    verify_environment(root)
    scan_and_register_custom_modules(root)
    env_cls = dict(get_registered_env_modules())["CurationDynamicsSpace"]
    agent_cls = dict(get_registered_agent_modules())["CurationDiscourseAgent"]
    locations = {name: str(Path(inspect.getfile(cls)).resolve())
                 for name, cls in {"env": env_cls, "agent": agent_cls}.items()}
    checked("实际registry加载本隔离工作区custom", locations == {
        "env": str(root / "custom/envs/curation_dynamics_space.py"),
        "agent": str(root / "custom/agents/curation_discourse_agent.py")})
    REPORT["runtime"] = dict(python=sys.executable, python_version=platform.python_version(),
                             sdk_version=importlib.metadata.version("agentsociety2"),
                             sdk_source=agentsociety2.__file__, loaded_modules=locations)
    official = load("hourly_official_config_check", root / ".claude/skills/agentsociety-experiment-config/scripts/config.py")
    official._ensure_agentsociety2()
    runner = ExperimentRunner.__new__(ExperimentRunner)
    main_configs, normalized_main, new_dirs, ledgers = {}, {}, set(), {}
    profile_count = 0
    representative_conditions = []
    manifest_hashes = {}
    for experiment in (2, 3):
        manifest_path = root / f"hypothesis_4/experiment_{experiment}/init/hourly_return_v1/manifest.json"
        manifest = read(manifest_path)
        checked(f"experiment_{experiment}仅准备30配置，未授权运行",
                manifest["execution_authorized"] is False and len(manifest["runs"]) == 30
                and manifest["arrival_agent_return_policy"] == "next_batch")
        counts = Counter((row["algorithm"], row["condition"]) for row in manifest["runs"])
        expected = {(a, "full"): 10 for a in ("random", "chronological", "interest")} if experiment == 2 else {
            ("interest", c): 10 for c in PARAMETERS}
        checked(f"experiment_{experiment}矩阵完整", dict(counts) == expected)
        for group in ("source_sha256", "mechanism_sha256", "output_sha256"):
            checked(f"experiment_{experiment}的{group}匹配",
                    all(digest(local_path(root, p)) == h for p, h in manifest[group].items()),
                    len(manifest[group]))
        manifest_hashes[str(manifest_path.relative_to(root))] = digest(manifest_path)
        for row in manifest["runs"]:
            path = local_path(root, row["config"])
            raw = read(path)
            parsed = InitConfig.model_validate(raw)
            steps_path = local_path(root, row["steps"])
            steps = StepsConfig.model_validate(yaml.safe_load(steps_path.read_text()))
            assert len(steps.steps) == 693
            current = datetime.fromisoformat(str(steps.start_t))
            assert current == datetime(2026, 3, 16, 6)
            for step in steps.steps:
                assert step.type == "run" and step.num_steps == 1
                current += timedelta(seconds=int(step.tick))
            assert current == datetime(2026, 6, 1)
            kwargs = parsed.env_modules[0].kwargs
            assert kwargs["arrival_agent_return_policy"] == "next_batch"
            assert kwargs["random_seed"] == row["seed"] and row["seed"] in range(10)
            assert kwargs["recommendation_algorithm"] == row["algorithm"]
            assert row["execution_authorized"] is False
            assert len(raw["agents"]) == 100
            assert {a["agent_id"] for a in raw["agents"]} == set(range(1, 101))
            assert all(a["agent_id"] == a["kwargs"]["id"] for a in raw["agents"])
            budgets = {json.dumps(a["kwargs"]["content_retry_budget"], sort_keys=True) for a in raw["agents"]}
            assert len(budgets) == 1
            budget = json.loads(budgets.pop())
            assert budget["limit"] == (2200 if experiment == 2 else 3300)
            ledger_path = local_path(root, budget["ledger_path"])
            assert not ledger_path.exists()
            ledgers.setdefault(experiment, set()).add(str(ledger_path))
            directory = local_path(root, row["run_dir"])
            assert directory not in new_dirs and not directory.exists()
            new_dirs.add(directory)
            if experiment == 2:
                baseline = read(local_path(root, row["source_config"]))
                scientific = deepcopy(raw)
                scientific["env_modules"][0]["kwargs"].pop("arrival_agent_return_policy")
                for old, changed in zip(baseline["agents"], scientific["agents"]):
                    changed["kwargs"]["content_retry_budget"] = deepcopy(old["kwargs"]["content_retry_budget"])
                assert scientific == baseline, row["run_id"]
                normalized = deepcopy(raw)
                normalized["env_modules"][0]["kwargs"].pop("recommendation_algorithm")
                if row["seed"] in normalized_main:
                    assert normalized == normalized_main[row["seed"]]
                else:
                    normalized_main[row["seed"]] = normalized
                main_configs[(row["seed"], row["algorithm"])] = (path, raw)
                expected_status = "planned_reuse_pending" if row["algorithm"] == "chronological" else "planned_new"
                assert row["status"] == expected_status
            else:
                full_path, full = main_configs[(row["seed"], "interest")]
                assert local_path(root, row["full_reference"]) == full_path
                assert row["status"] == "planned_new"
                scientific = deepcopy(raw)
                parameter = PARAMETERS[row["condition"]]
                for old, changed in zip(full["agents"], scientific["agents"]):
                    assert changed["kwargs"]["params"][parameter] == 0.0
                    assert old["kwargs"]["params"][parameter] != 0.0
                    changed["kwargs"]["params"][parameter] = old["kwargs"]["params"][parameter]
                    changed["kwargs"]["content_retry_budget"] = deepcopy(old["kwargs"]["content_retry_budget"])
                assert scientific == full, row["run_id"]
            with patch.object(official, "get_experiment_paths", return_value={"init_config": path, "steps_yaml": steps_path}):
                result = official.action_check(root, "4", str(experiment))
            assert result["success"], (row["run_id"], result)
            env = env_cls(**kwargs)
            assert env._arrival_agent_return_policy == "next_batch" and env._agent_return_next_batch
            specs, class_name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
            assert class_name == "CurationDiscourseAgent" and len(specs) == 100
            restored_profiles = 0
            if row["seed"] == 0:
                # 各条件选一个seed验证真实CLI profile切分与工作区恢复，不执行Agent行动。
                for spec in specs:
                    agent_path = scratch / "agents" / str(profile_count)
                    agent_cls.create(agent_path, spec["profile"], spec["config"])
                    with patch.object(agent_cls, "_bind_services"):
                        agent = await agent_cls.from_workspace(agent_path, None)
                    assert agent._profile == spec["profile"]
                    assert agent._decision_log == [] and agent._step_count == 0
                    if experiment == 3:
                        assert agent._params[PARAMETERS[row["condition"]]] == 0.0
                    profile_count += 1
                    restored_profiles += 1
                env_path = scratch / "environments" / row["run_id"]
                await env.to_workspace(env_path)
                saved = read(env_path / "state/ENV_STATE.json")
                assert saved["_arrival_agent_return_policy"] == "next_batch"
                restored_env = env_cls(**kwargs)
                assert await restored_env.restore(env_path)
                assert restored_env._arrival_agent_return_policy == "next_batch"
                assert restored_env._agent_return_next_batch
                representative_conditions.append(row["run_id"])
            REPORT["configs"].append(dict(run_id=row["run_id"], seed=row["seed"],
                algorithm=row["algorithm"], condition=row["condition"], official_check_passed=True,
                environment_instantiated=True, steps=693, profiles_restored=restored_profiles))
            print("PASS", row["run_id"], flush=True)
    checked("60份官方schema/steps/check及实际环境构造通过", len(REPORT["configs"]) == 60)
    checked("10组主三臂及30组消融科学参数严格配对", len(normalized_main) == 10 and len(main_configs) == 30)
    checked("6条件代表seed的600份CLI profile创建恢复通过", profile_count == 600 and len(representative_conditions) == 6)
    checked("两批独立预算账本与60个引擎目录尚未创建", all(len(v) == 1 for v in ledgers.values())
            and ledgers[2] != ledgers[3] and len(new_dirs) == 60)
    ray = sys.modules.get("ray")
    checked("未启动Ray", ray is None or not ray.is_initialized())
    REPORT.update(profiles_created_and_restored=profile_count, environment_instances=60,
                  representative_environment_restores=representative_conditions, manifest_sha256=manifest_hashes,
                  planned_new_runs=50, chronological_reuse="pending_runtime_comparability_review",
                  scope="仅配置、模块构造及保存恢复；环境step=0、Agent行动=0，不是仿真或结果验证")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "evidence/config_validation.json")
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    os.chdir(root)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP="True", MEM0_TELEMETRY="False",
                      ANONYMIZED_TELEMETRY="False", WORKSPACE_PATH=str(root), AGENTSOCIETY_WORKSPACE=str(root))

    def deny_network(*args, **kwargs):
        REPORT["network_attempts"] += 1
        raise AssertionError("离线验收禁止网络连接")

    async def deny_llm(*args, **kwargs):
        REPORT["llm_calls"] += 1
        raise AssertionError("离线验收禁止模型调用")

    def deny_sync_llm(*args, **kwargs):
        REPORT["llm_calls"] += 1
        raise AssertionError("离线验收禁止模型调用")

    try:
        with patch.object(socket.socket, "connect", deny_network), \
             patch.object(socket.socket, "connect_ex", deny_network), \
             patch.object(socket, "create_connection", deny_network):
            import litellm
            with patch.object(litellm.Router, "acompletion", deny_llm), \
                 patch.object(litellm, "acompletion", deny_llm), \
                 patch.object(litellm.Router, "completion", deny_sync_llm), \
                 patch.object(litellm, "completion", deny_sync_llm), \
                 tempfile.TemporaryDirectory(dir=output.parent, prefix=".candidate-check-") as folder:
                with patch.object(tempfile, "tempdir", folder):
                    asyncio.run(verify(root, Path(folder)))
        checked("网络与LLM调用尝试均为零", REPORT["network_attempts"] == REPORT["llm_calls"] == 0)
        REPORT["status"] = "passed"
    except Exception:
        REPORT["status"] = "failed"
        REPORT["errors"].append(traceback.format_exc())
    REPORT["checked_at"] = datetime.now(timezone.utc).isoformat()
    REPORT["workspace"] = str(root)
    REPORT["verifier_sha256"] = digest(Path(__file__))
    if output.exists():
        previous = output.with_name(f"{output.stem}.previous-{digest(output)[:12]}.json")
        if not previous.exists():
            previous.write_bytes(output.read_bytes())
    output.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: REPORT.get(k) for k in ("status", "profiles_created_and_restored", "environment_instances",
          "network_attempts", "llm_calls", "agent_actions", "environment_steps")}, ensure_ascii=False))
    if REPORT["status"] != "passed":
        print(REPORT["errors"][-1], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
