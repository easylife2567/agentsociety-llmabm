"""随机/兴趣seed1–9运行配置禁网预检；只构造环境与恢复profile，不启动仿真。"""
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
WEEKS = tuple(f"2026-W{week}" for week in range(12, 23))
EXPECTED_RUNS = [(arm, seed) for seed in range(1, 10) for arm in ("random", "interest")]
REPORT = dict(status="checking", preflight_only=True, engine_started=False,
              environment_steps=0, agent_actions=0, network_attempts=0, llm_calls=0,
              ray_start_attempts=0, checks=[], configs=[], reused=[], errors=[])


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


def verify_reuse(plan, plan_path):
    """seed0只读复用冻结快照，不进入新运行矩阵或新预算。"""
    rows = plan["reuse_runs"]
    checked("仅复用本run随机/兴趣两份完整seed0",
            [(r["algorithm"], r["seed"]) for r in rows] == [("random", 0), ("interest", 0)])
    for row in rows:
        arm = row["algorithm"]
        directory = Path(row["run_dir"]).resolve()
        expected = plan_path.parent.parent / f"pilot/results/hourly_return_pilot_{arm}_s0"
        assert directory == expected.resolve() and row["run_id"] == directory.name
        assert row["raw_sha256"], "复用必须有完整冻结哈希"
        for name, expected_hash in row["raw_sha256"].items():
            path = (directory / name).resolve()
            path.relative_to(directory)
            assert path.is_file() and digest(path) == expected_hash, name
        pid, step = read(directory / "pid.json"), read(directory / "SOCIETY_STEP.json")
        assert pid["status"] == "completed"
        assert step["step_count"] == step["completed_step_count"] == 693
        env = read(directory / "env/CurationDynamicsSpace/state/ENV_STATE.json")
        assert env["_arrival_agent_return_policy"] == "next_batch"
        actions = env["_arrival_state"]["actions"]
        expected_actions = {(str(aid), week) for aid in range(1, 101) for week in WEEKS}
        assert len(actions) == 1100
        assert {(str(a["agent_id"]), a["week"]) for a in actions} == expected_actions
        assert [r["week"] for r in env["_arrival_state"]["weeks"]] == list(WEEKS)
        agents = sorted((directory / "agents").glob("*/AGENT.json"))
        assert len(agents) == 100
        decision_keys, posts = set(), 0
        for path in agents:
            agent = read(path)
            assert sorted(r["week"] for r in agent["decision_log"]) == list(WEEKS)
            for record in agent["decision_log"]:
                decision_keys.add((str(agent["profile"]["id"]), record["week"]))
                if record.get("posted"):
                    assert record["response_model"] == plan["expected_returned_model"]
                    posts += 1
        assert decision_keys == expected_actions
        REPORT["reused"].append(dict(run_id=row["run_id"], algorithm=arm, seed=0,
                                     raw_files_verified=len(row["raw_sha256"]), posts=posts,
                                     completed_steps=693, actions=1100, newly_started=False))


async def verify(plan_path, scratch):
    plan = read(plan_path)
    root = Path(plan["workspace"]).resolve()
    checked("计划属于当前run的seed_extension", plan_path.parent == HERE
            and root == HERE.parent / "workspace")
    checked("使用计划指定项目解释器与现有环境文件",
            Path(sys.executable).resolve() == Path(plan["python"]).resolve()
            and Path(plan["env_file"]).is_file())
    checked("新授权严格为随机/兴趣seed1–9共18次",
            plan["execution_authorized"] is True
            and plan["batch_id"] == "hourly_return_v1"
            and [(r["algorithm"], r["seed"]) for r in plan["runs"]] == EXPECTED_RUNS)
    checked("独立预算19800机会/1980额外/21780正文，两路上限",
            plan["decision_opportunities"] == 19800 and plan["extra_requests_limit"] == 1980
            and plan["body_outer_requests_limit"] == 21780
            and plan["max_extra_per_action"] == 1 and plan["max_parallel_runs"] == 2)
    created, deadline = (datetime.fromisoformat(plan[k]) for k in ("created_at", "deadline_at"))
    checked("本批48小时固定绝对截止尚未到达",
            created.tzinfo is not None and deadline.tzinfo is not None
            and plan["max_wall_hours"] == 48 and deadline - created == timedelta(hours=48)
            and datetime.now(timezone.utc) < deadline,
            dict(created_at=created.isoformat(), deadline_at=deadline.isoformat()))
    checked("请求别名与实际返回版本延续已完成pilot",
            plan["requested_model"] == "deepseek-v4.1-flash"
            and plan["expected_returned_model"] == "deepseek-v4-1-flash-261017")
    ledger = Path(plan["ledger_path"])
    checked("独立账本为seed_extension内绝对路径且未创建",
            ledger.is_absolute() and ledger.parent.resolve() == plan_path.parent and not ledger.exists())
    checked("全部冻结来源字节保持",
            bool(plan["source_sha256"]) and all(Path(name).is_file() and digest(Path(name)) == value
            for name, value in plan["source_sha256"].items()), len(plan["source_sha256"]))
    verify_reuse(plan, plan_path)
    os.chdir(root)
    os.environ.update(WORKSPACE_PATH=str(root), AGENTSOCIETY_WORKSPACE=str(root))
    from agentsociety2.registry import (
        scan_and_register_custom_modules, get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import InitConfig, StepsConfig
    import agentsociety2
    import yaml

    scan_and_register_custom_modules(root)
    env_cls = dict(get_registered_env_modules())["CurationDynamicsSpace"]
    agent_cls = dict(get_registered_agent_modules())["CurationDiscourseAgent"]
    locations = {key: str(Path(inspect.getfile(cls)).resolve())
                 for key, cls in {"env": env_cls, "agent": agent_cls}.items()}
    checked("registry实际加载本run隔离custom", locations == {
        "env": str(root / "custom/envs/curation_dynamics_space.py"),
        "agent": str(root / "custom/agents/curation_discourse_agent.py")})
    REPORT["runtime"] = dict(python=sys.executable, python_version=platform.python_version(),
                             sdk_version=importlib.metadata.version("agentsociety2"),
                             sdk_source=agentsociety2.__file__, loaded_modules=locations)
    official = load("seed_extension_official_config_check",
                    root / ".claude/skills/agentsociety-experiment-config/scripts/config.py")
    official._ensure_agentsociety2()
    runner = ExperimentRunner.__new__(ExperimentRunner)
    common_by_seed, new_dirs, run_ids = {}, set(), set()
    profile_count = 0
    assert Path(plan["batch_id"]).name == plan["batch_id"]
    output_root = root / "hypothesis_4/experiment_2/runs" / plan["batch_id"]
    for row in plan["runs"]:
        arm, seed = row["algorithm"], row["seed"]
        config_path, source_path, steps_path = (Path(row[k]).resolve() for k in ("config", "config_source", "steps"))
        assert config_path.parent == plan_path.parent / "configs"
        assert source_path == root / f"hypothesis_4/experiment_2/init/hourly_return_v1/configs/hourly_return_v1_{arm}_s{seed}.json"
        assert steps_path == root / f"hypothesis_4/experiment_2/init/steps_s{seed}.yaml"
        assert digest(config_path) == row["config_sha256"]
        assert all(str(p) in plan["source_sha256"] for p in (config_path, source_path, steps_path))
        raw, source = read(config_path), read(source_path)
        parsed = InitConfig.model_validate(raw)
        assert len(parsed.env_modules) == 1
        kwargs = parsed.env_modules[0].kwargs
        assert kwargs["arrival_agent_return_policy"] == "next_batch"
        assert kwargs["schedule_mode"] == "arrival_timing" and kwargs["arrival_mode"] == "timestamp"
        assert kwargs["recommendation_algorithm"] == arm and kwargs["random_seed"] == seed
        assert kwargs["chronological_total_batches"] == row["expected_batches"] == 693
        assert row["expected_actions"] == 1100 and row["expected_weeks"] == 11
        assert len(raw["agents"]) == 100 and {a["agent_id"] for a in raw["agents"]} == set(range(1, 101))
        assert all(a["agent_id"] == a["kwargs"]["id"] for a in raw["agents"])
        normalized = deepcopy(raw)
        for original, changed in zip(source["agents"], normalized["agents"]):
            assert changed["kwargs"]["content_retry_budget"] == {"limit": 1980, "ledger_path": str(ledger)}
            changed["kwargs"]["content_retry_budget"] = deepcopy(original["kwargs"]["content_retry_budget"])
        assert normalized == source, row["run_id"]
        paired = deepcopy(raw)
        paired["env_modules"][0]["kwargs"].pop("recommendation_algorithm")
        if seed in common_by_seed:
            assert common_by_seed[seed] == paired, f"seed{seed}两臂除推荐算法外必须同配置"
        else:
            common_by_seed[seed] = paired
        directory = Path(row["run_dir"]).resolve()
        assert row["run_id"] == f"hourly_return_v1_{arm}_s{seed}"
        assert directory.parent == output_root and directory.name == row["run_id"]
        assert directory not in new_dirs and row["run_id"] not in run_ids and not directory.exists()
        new_dirs.add(directory)
        run_ids.add(row["run_id"])
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
            assert agent._profile["content_retry_budget"] == {"limit": 1980, "ledger_path": str(ledger)}
            assert agent._decision_log == [] and agent._step_count == 0
            profile_count += 1
        REPORT["configs"].append(dict(run_id=row["run_id"], algorithm=arm, seed=seed,
            config_sha256=digest(config_path), source_sha256=digest(source_path), steps_sha256=digest(steps_path),
            official_check_passed=True, environment_instantiated=True, profiles_created_restored=100,
            expected_batches=693, expected_actions=1100, expected_weeks=11))
        print("PASS", row["run_id"], flush=True)
    checked("18份官方schema/steps/环境实例与1800份profile创建恢复通过",
            len(REPORT["configs"]) == 18 and profile_count == 1800 and len(common_by_seed) == 9)
    checked("18配置仅改变候选预算；九组两臂科学参数配对相同", len(new_dirs) == len(run_ids) == 18)
    checked("预检未创建账本或任何新引擎目录", not ledger.exists() and all(not p.exists() for p in new_dirs))
    checked("预检后冻结来源与两份seed0保持",
            all(digest(Path(name)) == value for name, value in plan["source_sha256"].items()))
    import ray
    checked("未启动Ray", not ray.is_initialized() and REPORT["ray_start_attempts"] == 0)
    REPORT.update(runtime_plan_sha256=digest(plan_path), profiles_created_and_restored=profile_count,
                  source_files_verified=len(plan["source_sha256"]), environment_instances=18,
                  scope="随机/兴趣seed1–9配置离线预检；复用seed0只读核对；不运行仿真或检查接口")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=HERE / "runtime_plan.json")
    parser.add_argument("--output", type=Path, default=HERE / "evidence/preflight.json")
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(HERE)
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

    def deny_ray(*args, **kwargs):
        REPORT["ray_start_attempts"] += 1
        raise AssertionError("预检禁止启动Ray")

    try:
        with patch.object(socket.socket, "connect", deny_network), \
             patch.object(socket.socket, "connect_ex", deny_network), \
             patch.object(socket, "create_connection", deny_network):
            import litellm
            import ray
            with patch.object(litellm.Router, "acompletion", deny_llm), \
                 patch.object(litellm, "acompletion", deny_llm), \
                 patch.object(litellm.Router, "completion", deny_sync_llm), \
                 patch.object(litellm, "completion", deny_sync_llm), \
                 patch.object(ray, "init", deny_ray), \
                 tempfile.TemporaryDirectory(dir=output.parent, prefix=".seed-extension-preflight-") as folder:
                with patch.object(tempfile, "tempdir", folder):
                    asyncio.run(verify(args.plan.resolve(), Path(folder)))
        checked("网络、模型及Ray启动尝试均为零",
                REPORT["network_attempts"] == REPORT["llm_calls"] == REPORT["ray_start_attempts"] == 0)
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
          "network_attempts", "llm_calls", "ray_start_attempts", "agent_actions", "environment_steps")}, ensure_ascii=False))
    if REPORT["status"] != "passed":
        print(REPORT["errors"][-1], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
