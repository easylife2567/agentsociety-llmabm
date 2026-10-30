"""三臂seed0试跑配置禁网预检；不启动引擎、环境step、Agent行动或LLM。"""
from __future__ import annotations

import argparse
import asyncio
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


HERE = Path(__file__).resolve().parent
REPORT = dict(status="checking", preflight_only=True, engine_started=False,
              environment_steps=0, agent_actions=0, network_attempts=0, llm_calls=0,
              checks=[], configs=[], errors=[])


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


async def verify(plan_path, scratch):
    plan = read(plan_path)
    root = Path(plan["workspace"]).resolve()
    os.chdir(root)
    os.environ.update(WORKSPACE_PATH=str(root), AGENTSOCIETY_WORKSPACE=str(root))
    from agentsociety2.registry import (
        scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import InitConfig, StepsConfig
    import agentsociety2
    import yaml

    checked("运行授权仅覆盖三臂seed0", plan["execution_authorized"] is True
            and [(r["algorithm"], r["seed"]) for r in plan["runs"]]
            == [(a, 0) for a in ("random", "chronological", "interest")])
    checked("预算为独立3300机会与330次共享额外请求",
            plan["decision_opportunities"] == 3300 and plan["extra_requests_limit"] == 330
            and plan["body_outer_requests_limit"] == 3630 and plan["max_extra_per_action"] == 1
            and plan["max_parallel_runs"] == 1)
    created = datetime.fromisoformat(plan["created_at"])
    deadline = datetime.fromisoformat(plan["deadline_at"])
    checked("本批8小时绝对截止尚未到达", plan["max_wall_hours"] == 8
            and deadline - created == timedelta(hours=8) and datetime.now(timezone.utc) < deadline,
            dict(created_at=created.isoformat(), deadline_at=deadline.isoformat()))
    ledger = Path(plan["ledger_path"])
    checked("共享账本为本pilot独立绝对路径且尚未创建",
            ledger.is_absolute() and ledger.parent.resolve() == plan_path.parent.resolve() and not ledger.exists())
    checked("125项冻结来源保持", all(Path(p).is_file() and digest(Path(p)) == value
            for p, value in plan["source_sha256"].items()), len(plan["source_sha256"]))
    scan_and_register_custom_modules(root)
    env_cls = dict(get_registered_env_modules())["CurationDynamicsSpace"]
    agent_cls = dict(get_registered_agent_modules())["CurationDiscourseAgent"]
    locations = {key: str(Path(inspect.getfile(cls)).resolve())
                 for key, cls in {"env": env_cls, "agent": agent_cls}.items()}
    checked("实际registry加载隔离workspace的custom", locations == {
        "env": str(root / "custom/envs/curation_dynamics_space.py"),
        "agent": str(root / "custom/agents/curation_discourse_agent.py")})
    REPORT["runtime"] = dict(python=sys.executable, python_version=platform.python_version(),
                             sdk_version=importlib.metadata.version("agentsociety2"),
                             sdk_source=agentsociety2.__file__, loaded_modules=locations)
    official = load("pilot_official_config_check", root / ".claude/skills/agentsociety-experiment-config/scripts/config.py")
    official._ensure_agentsociety2()
    runner = ExperimentRunner.__new__(ExperimentRunner)
    common = None
    profile_count = 0
    new_dirs = set()
    for row in plan["runs"]:
        config_path, source_path, steps_path = (Path(row[k]).resolve() for k in ("config", "config_source", "steps"))
        assert config_path.parent == plan_path.parent / "configs"
        source_path.relative_to(root / "hypothesis_4/experiment_2/init/hourly_return_v1/configs")
        assert digest(config_path) == row["config_sha256"]
        raw, source = read(config_path), read(source_path)
        parsed = InitConfig.model_validate(raw)
        kwargs = parsed.env_modules[0].kwargs
        assert kwargs["arrival_agent_return_policy"] == "next_batch"
        assert kwargs["recommendation_algorithm"] == row["algorithm"] and kwargs["random_seed"] == row["seed"] == 0
        assert kwargs["chronological_total_batches"] == row["expected_batches"] == 693
        assert row["expected_actions"] == 1100 and row["expected_weeks"] == 11
        assert len(raw["agents"]) == 100 and {a["agent_id"] for a in raw["agents"]} == set(range(1, 101))
        assert all(a["agent_id"] == a["kwargs"]["id"] for a in raw["agents"])
        normalized = deepcopy(raw)
        for original, changed in zip(source["agents"], normalized["agents"]):
            assert changed["kwargs"]["content_retry_budget"] == {"limit": 330, "ledger_path": str(ledger)}
            changed["kwargs"]["content_retry_budget"] = deepcopy(original["kwargs"]["content_retry_budget"])
        assert normalized == source, row["run_id"]
        normalized = deepcopy(raw)
        normalized["env_modules"][0]["kwargs"].pop("recommendation_algorithm")
        if common is None:
            common = normalized
        else:
            assert common == normalized, "三臂除推荐算法外必须同配置"
        directory = Path(row["run_dir"]).resolve()
        directory.relative_to(root / "hypothesis_4/experiment_2/runs/hourly_return_pilot_s0")
        assert directory not in new_dirs and not directory.exists()
        new_dirs.add(directory)
        steps = StepsConfig.model_validate(yaml.safe_load(steps_path.read_text()))
        assert len(steps.steps) == 693
        current = datetime.fromisoformat(str(steps.start_t))
        assert current == datetime(2026, 3, 16, 6)
        for step in steps.steps:
            assert step.type == "run" and step.num_steps == 1
            current += timedelta(seconds=int(step.tick))
        assert current == datetime(2026, 6, 1)
        with patch.object(official, "get_experiment_paths", return_value={"init_config": config_path, "steps_yaml": steps_path}):
            result = official.action_check(root, "4", "2")
        assert result["success"], result
        env = env_cls(**kwargs)
        assert env._arrival_agent_return_policy == "next_batch" and env._agent_return_next_batch
        specs, class_name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
        assert class_name == "CurationDiscourseAgent" and len(specs) == 100
        for spec in specs:
            agent_path = scratch / "agents" / str(profile_count)
            agent_cls.create(agent_path, spec["profile"], spec["config"])
            with patch.object(agent_cls, "_bind_services"):
                agent = await agent_cls.from_workspace(agent_path, None)
            assert agent._profile == spec["profile"]
            assert agent._profile["content_retry_budget"] == {"limit": 330, "ledger_path": str(ledger)}
            assert agent._decision_log == [] and agent._step_count == 0
            profile_count += 1
        REPORT["configs"].append(dict(run_id=row["run_id"], algorithm=row["algorithm"], seed=0,
            config_sha256=digest(config_path), source_sha256=digest(source_path), steps_sha256=digest(steps_path),
            official_check_passed=True, environment_instantiated=True, profiles_created_restored=100,
            expected_batches=693, expected_actions=1100, expected_weeks=11))
        print("PASS", row["run_id"], flush=True)
    checked("三臂官方schema/steps/环境构造及300份profile恢复通过", len(REPORT["configs"]) == 3 and profile_count == 300)
    checked("三配置仅调整候选的预算上限及独立绝对账本", len(REPORT["configs"]) == 3)
    checked("预检未创建共享账本或三个引擎输出目录", not ledger.exists() and all(not p.exists() for p in new_dirs))
    ray = sys.modules.get("ray")
    checked("未启动Ray", ray is None or not ray.is_initialized())
    REPORT.update(runtime_plan_sha256=digest(plan_path), profiles_created_and_restored=profile_count,
                  source_files_verified=len(plan["source_sha256"]), environment_instances=3,
                  scope="仅三份运行配置的离线预检；未审查启动控制器、未试探接口、未运行引擎")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=HERE / "runtime_plan.json")
    parser.add_argument("--output", type=Path, default=HERE / "evidence/preflight.json")
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP="True", MEM0_TELEMETRY="False", ANONYMIZED_TELEMETRY="False")

    def deny_network(*args, **kwargs):
        REPORT["network_attempts"] += 1
        raise AssertionError("预检禁止网络连接")

    async def deny_llm(*args, **kwargs):
        REPORT["llm_calls"] += 1
        raise AssertionError("预检禁止模型调用")

    def deny_sync_llm(*args, **kwargs):
        REPORT["llm_calls"] += 1
        raise AssertionError("预检禁止模型调用")

    try:
        with patch.object(socket.socket, "connect", deny_network), \
             patch.object(socket.socket, "connect_ex", deny_network), \
             patch.object(socket, "create_connection", deny_network):
            import litellm
            with patch.object(litellm.Router, "acompletion", deny_llm), \
                 patch.object(litellm, "acompletion", deny_llm), \
                 patch.object(litellm.Router, "completion", deny_sync_llm), \
                 patch.object(litellm, "completion", deny_sync_llm), \
                 tempfile.TemporaryDirectory(dir=output.parent, prefix=".pilot-preflight-") as folder:
                with patch.object(tempfile, "tempdir", folder):
                    asyncio.run(verify(args.plan.resolve(), Path(folder)))
        checked("网络和模型调用尝试均为零", REPORT["network_attempts"] == REPORT["llm_calls"] == 0)
        REPORT["status"] = "passed"
    except Exception:
        REPORT["status"] = "failed"
        REPORT["errors"].append(traceback.format_exc())
    REPORT["checked_at"] = datetime.now(timezone.utc).isoformat()
    REPORT["verifier_sha256"] = digest(Path(__file__))
    if output.exists():
        previous = output.with_name(f"{output.stem}.previous-{digest(output)[:12]}.json")
        if not previous.exists():
            previous.write_bytes(output.read_bytes())
    output.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: REPORT.get(k) for k in ("status", "profiles_created_and_restored", "source_files_verified",
          "network_attempts", "llm_calls", "agent_actions", "environment_steps")}, ensure_ascii=False))
    if REPORT["status"] != "passed":
        print(REPORT["errors"][-1], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
