"""正式主工作区30份小时回流配置的禁网schema、实例化与保存恢复验收。"""
from __future__ import annotations

import asyncio
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import traceback
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = dict(status="checking", checks=[], configs=[], errors=[], network_attempts=0,
              llm_attempts=0, ray_start_attempts=0, environment_steps=0, agent_actions=0,
              profiles_created_and_restored=0, environments_saved_and_restored=0,
              scientific_simulation_started=False, source_sha256={})


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tracked(path):
    path = Path(path).resolve()
    path.relative_to(ROOT)
    REPORT["source_sha256"][str(path)] = digest(path)
    return path


def read(path):
    return json.loads(tracked(path).read_text(encoding="utf-8"))


def require(condition, name):
    if not condition:
        raise AssertionError(name)
    REPORT["checks"].append(name)


def deny_network(*args, **kwargs):
    REPORT["network_attempts"] += 1
    raise AssertionError("正式配置验收禁止网络连接")


def deny_llm_sync(*args, **kwargs):
    REPORT["llm_attempts"] += 1
    raise AssertionError("正式配置验收禁止模型调用")


async def deny_llm(*args, **kwargs):
    return deny_llm_sync(*args, **kwargs)


def deny_ray(*args, **kwargs):
    REPORT["ray_start_attempts"] += 1
    raise AssertionError("正式配置验收禁止启动Ray")


async def verify(scratch):
    import yaml
    import ray
    import agentsociety2
    from agentsociety2.registry import (scan_and_register_custom_modules,
        get_registered_agent_modules, get_registered_env_modules)
    from agentsociety2.society.cli import ExperimentRunner
    from agentsociety2.society.models import InitConfig, StepsConfig

    require(not ray.is_initialized(), "进入验收前Ray未启动")
    with patch.object(ray, "init", deny_ray):
        scan_and_register_custom_modules(ROOT)
        env_cls = dict(get_registered_env_modules())["CurationDynamicsSpace"]
        agent_cls = dict(get_registered_agent_modules())["CurationDiscourseAgent"]
        loaded = {name: str(Path(inspect.getfile(cls)).resolve()) for name, cls in
                  {"env": env_cls, "agent": agent_cls}.items()}
        require(loaded == {"env": str(ROOT / "custom/envs/curation_dynamics_space.py"),
                           "agent": str(ROOT / "custom/agents/curation_discourse_agent.py")},
                "registry实际加载正式主工作区custom")
        for path in loaded.values():
            tracked(path)
        tracked(ROOT / "custom/envs/curation_arrival_schedule.py")
        REPORT["runtime"] = dict(python=sys.executable, sdk_version=importlib.metadata.version("agentsociety2"),
                                 sdk_source=agentsociety2.__file__, loaded_modules=loaded)
        base = ROOT / "hypothesis_4/experiment_2/init/hourly_return_v1"
        accepted, prepared = read(base / "manifest.json"), read(base / "preparation_manifest.json")
        require(accepted["status"] == "adopted" and accepted["new_execution_authorized"] is False,
                "正式接收不扩大运行授权")
        rows = prepared["runs"]
        require(len(rows) == 30 and {(r["algorithm"],r["seed"]) for r in rows} ==
                {(a,s) for a in ("random","chronological","interest") for s in range(10)},
                "主实验30配置完整唯一矩阵")
        runner = ExperimentRunner.__new__(ExperimentRunner)
        normalized = {}
        counts = Counter()
        for row in rows:
            config_path, steps_path = (ROOT / row[k] for k in ("config", "steps"))
            raw, old = read(config_path), read(ROOT / row["source_config"])
            require(digest(config_path) == accepted["configs_sha256"][row["config"]],
                    f"{row['run_id']}正式配置SHA")
            parsed = InitConfig.model_validate(raw)
            steps = StepsConfig.model_validate(yaml.safe_load(tracked(steps_path).read_text()))
            require(len(steps.steps) == 693, f"{row['run_id']}693步")
            now = datetime.fromisoformat(str(steps.start_t))
            require(now == datetime(2026,3,16,6), f"{row['run_id']}开始时间")
            require(all(step.type == "run" and step.num_steps == 1 and int(step.tick) > 0 for step in steps.steps),
                    f"{row['run_id']}全部官方步骤类型与时长")
            for step in steps.steps:
                now += timedelta(seconds=int(step.tick))
            require(now == datetime(2026,6,1), f"{row['run_id']}完整11周结束时间")
            kw = parsed.env_modules[0].kwargs
            require(kw["arrival_agent_return_policy"] == "next_batch" and
                    kw["recommendation_algorithm"] == row["algorithm"] and
                    kw["random_seed"] == row["seed"], f"{row['run_id']}算法seed回流")
            require(len(raw["agents"]) == 100 and {a["agent_id"] for a in raw["agents"]} == set(range(1,101))
                    and all(a["agent_id"] == a["kwargs"]["id"] for a in raw["agents"]),
                    f"{row['run_id']}完整100profile及id")
            scientific = deepcopy(raw)
            scientific["env_modules"][0]["kwargs"].pop("arrival_agent_return_policy")
            for before, after in zip(old["agents"], scientific["agents"]):
                after["kwargs"]["content_retry_budget"] = deepcopy(before["kwargs"]["content_retry_budget"])
            require(scientific == old, f"{row['run_id']}除回流和重试预算外科学配置保持")
            shared = deepcopy(raw)
            shared["env_modules"][0]["kwargs"].pop("recommendation_algorithm")
            seed = row["seed"]
            if seed in normalized:
                require(shared == normalized[seed], f"seed{seed}三臂输入行为相同")
            else:
                normalized[seed] = shared
            specs, class_name = runner._build_agent_specs([a.model_dump() for a in parsed.agents])
            require(class_name == "CurationDiscourseAgent" and len(specs) == 100,
                    f"{row['run_id']}官方CLI profile切分")
            for i, spec in enumerate(specs):
                folder = scratch / row["run_id"] / "agents" / str(i)
                agent_cls.create(folder, spec["profile"], spec["config"])
                with patch.object(agent_cls, "_bind_services"):
                    agent = await agent_cls.from_workspace(folder, None)
                require(agent._profile == spec["profile"] and agent._config == spec["config"]
                        and agent._id == int(spec["profile"]["id"])
                        and agent._decision_log == [] and agent._step_count == 0,
                        f"{row['run_id']}Agent{agent._id}profile/config创建恢复一致")
                REPORT["profiles_created_and_restored"] += 1
            env = env_cls(**kw)
            require(env._arrival_agent_return_policy == "next_batch" and env._agent_return_next_batch,
                    f"{row['run_id']}正式环境构造")
            folder = scratch / row["run_id"] / "environment"
            await env.to_workspace(folder)
            saved = json.loads((folder / "state/ENV_STATE.json").read_text())
            require(saved["_arrival_agent_return_policy"] == "next_batch", f"{row['run_id']}保存回流契约")
            restored = env_cls(**kw)
            require(await restored.restore(folder) and restored._arrival_agent_return_policy == "next_batch"
                    and restored._agent_return_next_batch, f"{row['run_id']}环境恢复一致")
            REPORT["environments_saved_and_restored"] += 1
            counts[row["algorithm"]] += 1
            REPORT["configs"].append(dict(run_id=row["run_id"], algorithm=row["algorithm"], seed=seed,
                schema_passed=True, steps=693, profiles_created_and_restored=100, environment_saved_and_restored=True))
            print("PASS", row["run_id"], flush=True)
        require(counts == Counter(random=10,chronological=10,interest=10) and len(normalized) == 10,
                "30配置与10组三臂完整配对")
        require(REPORT["profiles_created_and_restored"] == 3000 and REPORT["environments_saved_and_restored"] == 30,
                "全部3000profile和30环境真实保存恢复")
        require(not ray.is_initialized(), "验收结束Ray未启动")


def main():
    os.chdir(ROOT)
    os.environ.update(WORKSPACE_PATH=str(ROOT), AGENTSOCIETY_WORKSPACE=str(ROOT),
        PYTHONDONTWRITEBYTECODE="1", LITELLM_LOCAL_MODEL_COST_MAP="True",
        MEM0_TELEMETRY="False", ANONYMIZED_TELEMETRY="False")
    try:
        with patch.object(socket.socket,"connect",deny_network), patch.object(socket.socket,"connect_ex",deny_network), \
             patch.object(socket,"create_connection",deny_network):
            import litellm
            with patch.object(litellm,"acompletion",deny_llm), patch.object(litellm.Router,"acompletion",deny_llm), \
                 patch.object(litellm,"completion",deny_llm_sync), patch.object(litellm.Router,"completion",deny_llm_sync), \
                 tempfile.TemporaryDirectory(dir=HERE,prefix=".main-config-check-") as folder:
                with patch.object(tempfile,"tempdir",folder):
                    asyncio.run(verify(Path(folder)))
        require(REPORT["network_attempts"] == REPORT["llm_attempts"] == REPORT["ray_start_attempts"] == 0,
                "网络/模型/Ray启动尝试均零")
        require(all(digest(path) == sha for path,sha in REPORT["source_sha256"].items()),
                "验收读取的正式文件均未改变")
        REPORT["status"] = "passed"
    except Exception:
        REPORT["status"] = "failed"
        REPORT["errors"].append(traceback.format_exc())
    REPORT.update(checked_at=datetime.now(timezone.utc).isoformat(), workspace=str(ROOT),
                  verifier_sha256=digest(__file__), temporary_directory_cleaned=True)
    output = HERE / "main_config_validation.json"
    if output.exists():
        output.with_name(f"main_config_validation.previous-{digest(output)[:12]}.json").write_bytes(output.read_bytes())
    output.write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:REPORT[k] for k in ("status","profiles_created_and_restored","environments_saved_and_restored",
          "network_attempts","llm_attempts","ray_start_attempts")},ensure_ascii=False))
    if REPORT["errors"]:
        print(REPORT["errors"][-1], file=sys.stderr)
    return REPORT["status"] != "passed"


if __name__ == "__main__":
    raise SystemExit(main())
