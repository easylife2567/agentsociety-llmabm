#!/usr/bin/env python3
"""weekly_lag1 注入时机离线门禁；不调用 LLM，也不创建实验 run。"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
CONFIGS_DIR = SCRIPT_DIR / "init" / "configs"
WEEKS = [f"2026-W{week:02d}" for week in range(12, 23)]
EXPECTED = [17, 18, 34, 30, 24, 22, 19, 18, 18, 20, 23]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(arm: str, seed: int = 0) -> dict:
    path = CONFIGS_DIR / f"weekly_lag1_{arm}_s{seed}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def env_kwargs(config: dict) -> dict:
    kwargs = dict(config["env_modules"][0]["kwargs"])
    for key in ("injection_data_path", "weekly_initial_injection_data_path", "vocab_path"):
        value = kwargs.get(key)
        if value:
            kwargs[key] = str(ROOT / value)
    return kwargs


def external_posts(env) -> list[dict]:
    return [post for post in env._posts.values() if str(post.get("author_id", "")).startswith("ext_")]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def verify_config_artifacts() -> None:
    generator = load_module(
        "weekly_lag_config", SCRIPT_DIR / "init" / "weekly_lag_config.py"
    )
    problems = generator.validate()
    require(not problems, "配置产物校验失败：" + "；".join(problems))

    manifest = json.loads(
        (CONFIGS_DIR / "weekly_lag1_manifest.json").read_text(encoding="utf-8")
    )
    require(
        list(manifest["timing"]["expected_external_arrivals_by_week"].values()) == EXPECTED,
        "manifest 的逐周外部入池表与审核方案不一致",
    )
    require(manifest["timing"]["expected_external_arrivals_in_window"] == 243,
            "窗口内外部入池总量不是 243")
    require(manifest["timing"]["deferred_to_w23"] == 24,
            "延至 W23 的 W22 普通帖子不是 24 条")


def verify_arm(env_cls, mech, arm: str) -> None:
    env = env_cls(**env_kwargs(load_config(arm)))
    require(env._injected_count_by_week == dict(zip(WEEKS, EXPECTED)),
            f"{arm}: env 的逐周计划量不符合审核表")

    observed: list[int] = []
    w12_lives: list[float] = []
    w13_official_id = None
    for week in WEEKS:
        env._open_tick(week)
        observed.append(len(env._injected_this_week_ids))
        newly = [env._posts[pid] for pid in env._injected_this_week_ids]
        require(all(post["injected_week"] == week for post in newly),
                f"{arm} {week}: injected_week 记录错误")
        require(all(post["available_week"] == week for post in newly),
                f"{arm} {week}: available_week 记录错误")
        if week == "2026-W12":
            require(all(post["source_week"] == "2026-W11" for post in newly),
                    f"{arm}: W12 初始内容并非全部来自 W11")
            require(all(post["injection_role"] == "initial_history" for post in newly),
                    f"{arm}: W12 初始化角色记录错误")
            w12_lives = [post["life"] for post in newly]
        if week == "2026-W13":
            official = [post for post in newly if post.get("source_pid") == "official_w13_announcement"]
            require(len(official) == 1, f"{arm}: W13 官方讣告不是恰好 1 条")
            require(official[0]["source_week"] == "2026-W13",
                    f"{arm}: 官方讣告来源周错误")
            require(math.isclose(official[0]["life"], 1.0),
                    f"{arm}: 官方讣告 W13 首次可见时不是 0 周龄")
            w13_official_id = official[0]["post_id"]
            if arm == "interest":
                require(w13_official_id in env._pinned_ids,
                        "interest: W13 官方讣告未置顶")
            else:
                require(not env._pinned_ids, "random: 不应存在置顶帖")
        if week == "2026-W14":
            require(not any(post.get("source_pid") == "official_w13_announcement" for post in newly),
                    f"{arm}: 官方讣告在 W14 被重复注入")
            require(w13_official_id not in env._pinned_ids,
                    f"{arm}: 官方讣告置顶延伸到了 W14")
        if week == "2026-W15":
            require(not any(post.get("source_week") == "2026-W15" for post in external_posts(env)),
                    f"{arm}: W15 普通真实帖在 W15 提前可见")
        if week == "2026-W16":
            source_w15 = [post for post in newly if post.get("source_week") == "2026-W15"]
            require(len(source_w15) == 24,
                    f"{arm}: W15 普通真实帖未在 W16 按 24 条进入")
            expected_life = mech.life_at_age(1, env._life_half_life_weeks)
            require(all(math.isclose(post["life"], expected_life) for post in source_w15),
                    f"{arm}: W15 真实帖在 W16 的生命值不是 1 周龄")

    require(observed == EXPECTED, f"{arm}: 实际逐周入池数 {observed} != {EXPECTED}")
    require(sum(observed) == 243, f"{arm}: 实际窗口总入池数不是 243")
    require(all(math.isclose(life, mech.life_at_age(1, env._life_half_life_weeks))
                for life in w12_lives), f"{arm}: W11 初始化帖在 W12 不是 1 周龄")
    require(not any(post.get("source_week") == "2026-W22" for post in external_posts(env)),
            f"{arm}: W22 普通真实帖不应在窗口内进入")
    keys = [env._injection_source_key(post) for post in external_posts(env)]
    require(len(keys) == len(set(keys)), f"{arm}: 存在重复注入的外部 source key")


def verify_agent_real_age_parity(env_cls, mech) -> None:
    env = env_cls(**env_kwargs(load_config("interest")))
    for week in WEEKS[:4]:  # 开到 W15
        env._open_tick(week)
    env._pending_agent_posts = [{
        "post_id": env._next_post_id,
        "agent_id": "agent_000",
        "content": "离线时机校验帖",
        "pool_type": "meme",
        "assigned_type": "meme",
        "type_mismatch": False,
        "tendencies": {"meme": 1.0},
        "week": "2026-W15",
        "event_time": None,
    }]
    env._next_post_id += 1
    agent_pid = env._pending_agent_posts[0]["post_id"]
    env._flush_pending_to_pool()
    env._open_tick("2026-W16")
    real_w15 = [env._posts[pid] for pid in env._injected_this_week_ids
                if env._posts[pid].get("source_week") == "2026-W15"]
    require(real_w15, "没有找到 W16 入池的 W15 真实帖")
    expected = mech.life_at_age(1, env._life_half_life_weeks)
    require(math.isclose(env._posts[agent_pid]["life"], expected),
            "W15 Agent 帖在 W16 不是 1 周龄")
    require(all(math.isclose(post["life"], env._posts[agent_pid]["life"])
                for post in real_w15), "同期 Agent 帖与真实帖首次可见时不同龄")


def verify_legacy_and_chronological(env_cls) -> None:
    legacy_path = CONFIGS_DIR / "anchored_v1_interest_s0.json"
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    env = env_cls(**env_kwargs(legacy))
    env._open_tick("2026-W12")
    require(len(env._injected_this_week_ids) == 17,
            "旧配置默认零滞后行为发生变化")
    require(all(env._posts[pid]["source_week"] == "2026-W12"
                for pid in env._injected_this_week_ids),
            "旧配置 W12 不再注入 W12 内容")

    chronological = json.loads(
        (CONFIGS_DIR / "anchored_v1_chronological_s0.json").read_text(encoding="utf-8")
    )
    kwargs = chronological["env_modules"][0]["kwargs"]
    forbidden = {
        "weekly_real_post_lag_weeks",
        "weekly_initial_injection_data_path",
        "weekly_same_week_official_source_pids",
    }
    require(not (forbidden & set(kwargs)), "chronological 配置被周级滞后字段污染")


def verify_resume_does_not_reinject(env_cls) -> None:
    async def scenario() -> None:
        kwargs = env_kwargs(load_config("interest"))
        env = env_cls(**kwargs)
        env._open_tick("2026-W12")
        env._open_tick("2026-W13")
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            await env.to_workspace(workspace)
            restored = env_cls(**kwargs)
            require(await restored.restore(workspace), "新 checkpoint 未能恢复")
            require(len(external_posts(restored)) == 35,
                    "恢复后 W12-W13 的外部帖数量改变")
            restored._open_tick("2026-W14")
            require(len(restored._injected_this_week_ids) == 34,
                    "恢复后 W14 入池数错误")
            require(len(external_posts(restored)) == 69,
                    "恢复后出现漏注入或重复注入")
            require(sum(post.get("source_pid") == "official_w13_announcement"
                        for post in external_posts(restored)) == 1,
                    "恢复后官方讣告不是恰好一条")

    asyncio.run(scenario())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    env_mod = load_module(
        "curation_dynamics_space_weekly_lag_verify",
        ROOT / "custom" / "envs" / "curation_dynamics_space.py",
    )
    mech = env_mod.mech
    verify_config_artifacts()
    verify_arm(env_mod.CurationDynamicsSpace, mech, "interest")
    verify_arm(env_mod.CurationDynamicsSpace, mech, "random")
    verify_agent_real_age_parity(env_mod.CurationDynamicsSpace, mech)
    verify_legacy_and_chronological(env_mod.CurationDynamicsSpace)
    verify_resume_does_not_reinject(env_mod.CurationDynamicsSpace)
    if not args.quiet:
        print("weekly_lag1 offline verification passed")
        print("- arrivals W12-W22:", dict(zip(WEEKS, EXPECTED)))
        print("- total external arrivals: 243; W23 deferred: 24")
        print("- W13 obituary: once; interest pinned; random unpinned")
        print("- W15 real and Agent posts: first available in W16 at age 1")
        print("- legacy weekly behavior and chronological config: unchanged")
        print("- checkpoint restore: no repeated initial/history/official injection")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"weekly_lag1 offline verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
