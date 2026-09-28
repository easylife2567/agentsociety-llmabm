#!/usr/bin/env python3
"""weekly_lag1_event_v2 离线门禁；不调用 LLM，也不创建实验 run。"""

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
ROUND_TAG = "weekly_lag1_event_v2"
WEEKS = [f"2026-W{week:02d}" for week in range(12, 24)]
EXPECTED = [17, 18, 34, 30, 24, 22, 19, 18, 18, 20, 23, 24]
EVENT_SIGNAL_TYPE = ""
EVENT_SIGNAL_SALIENCE_SLOTS = 0.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(arm: str, seed: int = 0) -> dict:
    path = CONFIGS_DIR / f"{ROUND_TAG}_{arm}_s{seed}.json"
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
        "weekly_lag_event_v2_config",
        SCRIPT_DIR / "init" / "weekly_lag_event_v2_config.py",
    )
    problems = generator.validate()
    require(not problems, "配置产物校验失败：" + "；".join(problems))

    manifest = json.loads(
        (CONFIGS_DIR / f"{ROUND_TAG}_manifest.json").read_text(encoding="utf-8")
    )
    require(
        list(manifest["timing"]["expected_external_arrivals_by_week"].values()) == EXPECTED,
        "manifest 的逐周外部入池表与审核方案不一致",
    )
    require(manifest["timing"]["expected_external_arrivals_in_window"] == 267,
            "W12-W23 窗口内外部入池总量不是 267")
    require(manifest["timing"]["w22_posts_drained_in_w23"] == 24,
            "W23 drain/readout 周接收的 W22 普通帖子不是 24 条")
    require(manifest["timing"]["deferred_beyond_window"] == 0,
            "仍有外部帖子被延至 W23 窗口之外")
    require(manifest["timing"]["drain_readout_week"] == "2026-W23",
            "drain/readout 周不是 W23")
    require(manifest["timing"]["drain_readout_week_has_same_week_external_source"] is False,
            "W23 不应注入 W23 来源外部帖")
    require(manifest["event_signal"] == {
        "enabled": False,
        "week": "2026-W13",
        "type": EVENT_SIGNAL_TYPE,
        "salience_slots": EVENT_SIGNAL_SALIENCE_SLOTS,
        "reason": "avoid forcing a W13 participation peak through deterministic thresholds",
        "event_week_mourning_floor": 0,
    }, "manifest 的事件效用关闭定义错误")

    for arm in ("interest", "random"):
        kwargs = load_config(arm)["env_modules"][0]["kwargs"]
        require(kwargs["num_ticks"] == 12, f"{arm}: num_ticks 不是 12")
        require(kwargs["event_signal_type"] == EVENT_SIGNAL_TYPE,
                f"{arm}: event_signal_type 错误")
        require(kwargs["event_signal_salience_slots"] == EVENT_SIGNAL_SALIENCE_SLOTS,
                f"{arm}: event_signal_salience_slots 错误")
        require(kwargs["event_week_mourning_floor"] == 0,
                f"{arm}: 旧的兴趣臂哀悼保底未关闭")


def verify_arm(env_cls, mech, arm: str) -> None:
    env = env_cls(**env_kwargs(load_config(arm)))
    require(env._injected_count_by_week == dict(zip(WEEKS, EXPECTED)),
            f"{arm}: env 的逐周计划量不符合审核表")

    require(env._event_signal_type == EVENT_SIGNAL_TYPE,
            f"{arm}: env 仍启用事件类型信号")
    require(env._event_signal_salience_slots == EVENT_SIGNAL_SALIENCE_SLOTS,
            f"{arm}: env 仍启用事件等效槽位")
    require(env._event_week_mourning_floor == 0,
            f"{arm}: env 仍启用旧的 interest-only 哀悼保底")

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
        agent_id = next(iter(env._agent_types))
        signal = asyncio.run(env.get_feed(agent_id))["event_signal"]
        require(signal["active"] is False,
                f"{arm} {week}: 不应有事件效用信号生效")
        require(signal["type"] is None,
                f"{arm} {week}: 事件效用类型应为空")
        require(signal["salience_slots"] == EVENT_SIGNAL_SALIENCE_SLOTS,
                f"{arm} {week}: 外生事件等效槽位错误")
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
            require(not env._event_floor_ids,
                    f"{arm}: 统一事件信号启用后仍存在旧哀悼保底帖")
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
        if week == "2026-W23":
            require(len(newly) == 24, f"{arm}: W23 未接收全部 24 条 W22 延迟帖")
            require(all(post.get("source_week") == "2026-W22" for post in newly),
                    f"{arm}: W23 出现非 W22 来源的外部帖")
            require(not any(post.get("source_week") == "2026-W23"
                            for post in external_posts(env)),
                    f"{arm}: drain/readout 周注入了 W23 来源外部帖")

    require(observed == EXPECTED, f"{arm}: 实际逐周入池数 {observed} != {EXPECTED}")
    require(sum(observed) == 267, f"{arm}: W12-W23 实际窗口总入池数不是 267")
    require(all(math.isclose(life, mech.life_at_age(1, env._life_half_life_weeks))
                for life in w12_lives), f"{arm}: W11 初始化帖在 W12 不是 1 周龄")
    require(sum(post.get("source_week") == "2026-W22" for post in external_posts(env)) == 24,
            f"{arm}: W22 普通真实帖未全部在 W23 进入")
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


def verify_event_signal_does_not_override_decision(env_cls, agent_cls) -> None:
    """验证W13官方讣告存在，但不再用等效槽位强制改变发言效用。"""
    for arm in ("interest", "random"):
        config = load_config(arm)
        env = env_cls(**env_kwargs(config))
        env._open_tick("2026-W12")
        env._open_tick("2026-W13")
        for spec in config["agents"]:
            profile = spec["kwargs"]
            if profile["agent_type"] != "mourning":
                continue
            agent = object.__new__(agent_cls)
            agent._params = profile["params"]
            agent._agent_type = "mourning"
            snapshot = asyncio.run(env.get_feed(str(spec["agent_id"])))
            _utility, components = agent._speak_stimulus(snapshot)
            require(components["event_signal_active"] is False,
                    f"{arm}: W13 mourning 决策仍收到事件效用信号")
            require(components["share_own"] == components["share_own_observed"],
                    f"{arm}: mourning 有效份额仍被事件槽位改写")

        education = next(
            spec for spec in config["agents"]
            if spec["kwargs"]["agent_type"] == "education"
        )
        agent = object.__new__(agent_cls)
        agent._params = education["kwargs"]["params"]
        agent._agent_type = "education"
        snapshot = asyncio.run(env.get_feed(str(education["agent_id"])))
        _utility, components = agent._speak_stimulus(snapshot)
        require(components["event_signal_active"] is False,
                f"{arm}: 事件效用信号错误作用于 education Agent")


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
        "event_signal_type",
        "event_signal_salience_slots",
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
    agent_mod = load_module(
        "curation_discourse_agent_weekly_lag_verify",
        ROOT / "custom" / "agents" / "curation_discourse_agent.py",
    )
    mech = env_mod.mech
    verify_config_artifacts()
    verify_arm(env_mod.CurationDynamicsSpace, mech, "interest")
    verify_arm(env_mod.CurationDynamicsSpace, mech, "random")
    verify_agent_real_age_parity(env_mod.CurationDynamicsSpace, mech)
    verify_event_signal_does_not_override_decision(
        env_mod.CurationDynamicsSpace, agent_mod.CurationDiscourseAgent
    )
    verify_legacy_and_chronological(env_mod.CurationDynamicsSpace)
    verify_resume_does_not_reinject(env_mod.CurationDynamicsSpace)
    if not args.quiet:
        print(f"{ROUND_TAG} offline verification passed")
        print("- arrivals W12-W23:", dict(zip(WEEKS, EXPECTED)))
        print("- total external arrivals: 267; W23 drains 24 W22-source posts")
        print("- W23 is drain/readout only; no W23-source external posts")
        print("- W13 utility-level event signal: disabled in both interest/random")
        print("- W13 peak is not forced through mourning-agent decision thresholds")
        print("- legacy interest-only mourning floor: disabled in both arms")
        print("- W13 obituary: once; interest pinned; random unpinned")
        print("- W15 real and Agent posts: first available in W16 at age 1")
        print("- legacy weekly behavior and chronological config: unchanged")
        print("- checkpoint restore: no repeated initial/history/official injection")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"{ROUND_TAG} offline verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
