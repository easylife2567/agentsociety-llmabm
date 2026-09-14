#!/usr/bin/env python3
"""verify_experiment.py: 全链路离线核验（不跑 LLM、不写 replay、不写任何实验产物；秒级）。

动机：锚定式效用、R 尺度 15 与策展臂的事件周议程保底（W13 保底 5 条
哀悼帖 + 官方讣告置顶）是关键机制；random 则是全历史、全槽位均匀抽样的强去策展反事实。
一旦 env / agent / 校准脚本 / 代理 / 配置五处口径漂移，
真实 run 跑完 8-9 小时才发现代价极高。本脚本把可离线判定的部分全部断言化，作为跑批前的门禁。

三层检查（任一不过 → 退出码 1）：

  A. **配置层**（可复现性 + 群体口径）
     A1 config_params.py 重跑后，9 个 configs/*.json + manifest + steps.yaml + init_config.json
        逐字节不变（证明盘上的配置确实是源码产物，没有手改残渣）；
     A2 9 个配置共享同一群体（agent_types 逐值相同）且构成 = 营销23/悼念22/其他21/玩梗19/教育15；
     A3 每份注入样本 250 条、周分配 = manifest.allocation、官方帖全程仅 1 条且在 W13。

  B. **同构层**（公式与常数跨模块逐值一致）
     B1 R 半饱和尺度：env/agent/校准/代理四处都取共享模块的 DEFAULT_DECAY_SCALE，无独立常量；
     B2 群体份额 POP_SHARE：personas == agent 侧 _POP_SHARE == counts/100；
     B3 锚定参数：配置内五类 λ 实际均值、B_i、alpha_D 与权威常数逐值一致；
     B4 议程保底条数：config_params == manifest == 校准脚本解析值；
     B5 锚定式公式边界：R=1⇒U=D、R=0⇒U=B、D=B⇒U=B；
     B6 保底候选资格口径：仅排除 noise，不限定 mourning 类型；
     B7 校准器确定性：同 (seed,N,scale) 两次调用逐值一致（防 id() 平票漂移）；
     B8 调度/监视/出图脚本可编译（防语法错误静默上线）；
     B9 批跑成功口径：步数唯一判据 + 死进程判 interrupted（防空 run 静默混入 / 静默跳过）；
     B10 replay 落盘完整性：agent_state 行数 = n_agents × 11 周、env_state = 11
        （卡实际落盘数据，补 B9 只卡引擎自我申报的缺口）。

  C. **机制层**（直接驱动 env，无 LLM、不写 replay）
     C1-C4 验证 chronological 冻结行动表、精确时间、最新10条、同小时同步与跨小时可见；
     C5 验证 random / interest 各自旧定义未被 chronological 改造；
     C6 验证去B/去D/去R三个消融参数边界；
     C7 完整推进693个小时批次，确认只形成11个周度快照且250条注入全部到达。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/verify_experiment.py
    $PYTHON_PATH hypothesis_4/experiment_1/verify_experiment.py --quiet   # 只打印结论
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
CONFIGS_DIR = SCRIPT_DIR / "init" / "configs"

RESULTS: list[tuple[bool, str, str]] = []   # (通过, 名称, 细节)
OBSERVED: list[tuple[str, str]] = []        # 观察项：不参与退出码，供人工判断（如保底的类型构成）


def check(ok: bool, name: str, detail: str = "") -> bool:
    RESULTS.append((bool(ok), name, detail))
    return bool(ok)


def observe(name: str, detail: str) -> None:
    OBSERVED.append((name, detail))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# A. 配置层
# ---------------------------------------------------------------------------
def layer_a() -> None:
    round_tag = "anchored_v1"
    tracked = [CONFIGS_DIR / f"{round_tag}_{a}_s{s}.json"
               for a in ("random", "chronological", "interest")
               for s in (0, 1, 2)]
    tracked += [CONFIGS_DIR / f"{round_tag}_ablation_{a}_s0.json"
                for a in ("no_b", "no_d", "no_r")]
    tracked += [CONFIGS_DIR / "manifest.json", SCRIPT_DIR / "init" / "steps.yaml",
                SCRIPT_DIR / "init" / "steps_chronological_hourly.yaml",
                SCRIPT_DIR / "init" / "init_config.json"]
    tracked += [SCRIPT_DIR / "init" / f"injection_sample_s{s}.json" for s in (0, 1, 2)]
    before = {p: p.read_bytes() for p in tracked if p.is_file()}
    missing = [p.name for p in tracked if not p.is_file()]
    check(not missing, "A0 配置产物齐全", f"缺失 {missing}" if missing else f"{len(before)} 个文件")

    cfg = _load("config_params", SCRIPT_DIR / "init" / "config_params.py")   # 副作用：重新生成配置
    changed = [p.name for p, b in before.items() if p.read_bytes() != b]
    check(not changed, "A1 配置可复现（源码重跑逐字节一致）",
          f"被重新生成改变的文件：{changed}" if changed else "config_params.py 重跑后盘上文件不变")

    check(cfg.POPULATION_COUNTS == {"meme": 19, "mourning": 22, "marketing": 23,
                                    "education": 15, "other": 21},
          "A2a 群体构成 = 用户裁定 19/22/23/15/21", f"{cfg.POPULATION_COUNTS}")

    type_maps = []
    for p in tracked[:9]:
        d = json.loads(p.read_text(encoding="utf-8"))
        type_maps.append({a["kwargs"]["id"]: a["kwargs"]["agent_type"] for a in d["agents"]})
    same = all(m == type_maps[0] for m in type_maps)
    counts: dict[str, int] = {}
    for t in type_maps[0].values():
        counts[t] = counts.get(t, 0) + 1
    check(same and len(type_maps[0]) == 100,
          "A2b 9 配置共享同一 100 人群体", f"构成 {counts}，9 配置群体逐值相同={same}")

    total_ok, week_ok, official_ok, msgs = True, True, True, []
    for seed in (0, 1, 2):
        doc = json.loads((SCRIPT_DIR / "init" / f"injection_sample_s{seed}.json").read_text(encoding="utf-8"))
        posts = doc["posts"]
        if len(posts) != 250:
            total_ok = False
            msgs.append(f"s{seed} 总数 {len(posts)}")
        wc = {w: 0 for w in cfg.INJECTION_ALLOCATION}
        for rec in posts:
            wc[rec["week"]] = wc.get(rec["week"], 0) + 1
        if wc != cfg.INJECTION_ALLOCATION:
            week_ok = False
            msgs.append(f"s{seed} 周分配 {wc}")
        off = [r for r in posts if r.get("is_official")]
        if len(off) != 1 or off[0]["week"] != cfg.ANNOUNCEMENT_WEEK:
            official_ok = False
            msgs.append(f"s{seed} 官方帖 {[(r['week'], r['pid']) for r in off]}")
    check(total_ok, "A3a 注入样本各 250 条", "；".join(msgs) or "s0/s1/s2 = 250 条")
    check(week_ok, "A3b 周分配 = manifest.allocation", "；".join(msgs) or f"{cfg.INJECTION_ALLOCATION}")
    check(official_ok, "A3c 官方帖全程唯一且在 W13", "；".join(msgs) or "仅 official_w13_announcement")


# ---------------------------------------------------------------------------
# B. 同构层
# ---------------------------------------------------------------------------
def layer_b():
    mech = _load("curation_mechanisms", ROOT / "custom" / "envs" / "curation_mechanisms.py")
    personas = _load("curation_personas", ROOT / "custom" / "agents" / "curation_personas.py")
    agent = _load("curation_discourse_agent", ROOT / "custom" / "agents" / "curation_discourse_agent.py")
    cal = _load("calibrate_speak", SCRIPT_DIR / "calibrate_speak.py")

    check(mech.DEFAULT_DECAY_SCALE == 15.0, "B1 R 半饱和尺度 = 15（共享常量）",
          f"mech.DEFAULT_DECAY_SCALE={mech.DEFAULT_DECAY_SCALE:g}；agent/校准/代理均不传 scale 参数")

    share = {"meme": 0.19, "mourning": 0.22, "marketing": 0.23, "education": 0.15, "other": 0.21}
    check(personas.POP_SHARE == share and agent._POP_SHARE == share, "B2 群体份额四处一致",
          f"personas={personas.POP_SHARE}；agent={agent._POP_SHARE}")

    population = personas.build_population(
        {"meme": 19, "mourning": 22, "marketing": 23, "education": 15, "other": 21},
        seed=42,
    )
    param_ok, bad = True, []
    for t, target_lambda in personas.CALIBRATED_LAMBDA_MEAN.items():
        members = [p for p in population if p["agent_type"] == t]
        actual_lambda = sum(p["params"]["decay"] for p in members) / len(members)
        checks = {
            "lambda_mean": (actual_lambda, target_lambda),
            "baseline": (agent._PARAM_DEFAULTS[t]["baseline_utility"],
                         personas.BASELINE_UTILITY[t]),
            "spiral_scale": (agent._PARAM_DEFAULTS[t]["spiral_scale"],
                             personas.CALIBRATED_ALPHA_D),
        }
        for key, (got, expected) in checks.items():
            if abs(float(got) - float(expected)) > 1e-12:
                param_ok = False
                bad.append(f"{t}.{key}: {got} != {expected}")
    check(param_ok, "B3 锚定参数均值/B_i/alpha_D 与权威常数一致",
          "；".join(bad) or "五类 λ 实际均值、B_i、alpha_D 全对齐")

    floor_ok = (cal.EVENT_WEEK_MOURNING_FLOOR == 5)
    cfg = json.loads((CONFIGS_DIR / "manifest.json").read_text(encoding="utf-8"))
    floor_ok &= cfg["feed_mechanism"]["event_week_mourning_floor"]["value"] == 5
    floors: dict[str, set[int]] = {a: set() for a in ("random", "chronological", "interest")}
    for run_id in cfg["run_ids"]:
        arm = next(a for a in floors if f"_{a}_" in run_id)
        p = CONFIGS_DIR / f"{run_id}.json"
        floors[arm].add(json.loads(p.read_text(encoding="utf-8"))["env_modules"][0]["kwargs"]
                        ["event_week_mourning_floor"])
    floor_ok &= floors == {"random": {5}, "chronological": {0}, "interest": {5}}
    check(floor_ok, "B4 议程保底只属于 interest；chronological 显式关闭",
          f"manifest interest=5；配置={floors}；校准解析={cal.EVENT_WEEK_MOURNING_FLOOR}")

    # B4b 校准器保留注入帖原始类型（含 noise）：否则方案 B 的过滤在校准侧失效，
    # 且 env 把 noise 单列一类、校准器若并入 "other" 会抬高"其他"型 agent 的 cum_own。
    raw_types = {rec["type"] for lst in cal.INJECTED_BY_WEEK.values() for rec in lst}
    check("noise" in raw_types, "B4b 校准器保留注入帖原始类型（与 env 同口径，含 noise）",
          f"注入池出现类型 {sorted(raw_types)}")

    # B5 锚定式公式同值与边界。
    import math
    d = mech.spiral_factor(0.30, 0.19, 1.2 * personas.CALIBRATED_ALPHA_D)
    r = mech.fatigue_factor(1.2430377762128202, 15.0)
    b = personas.BASELINE_UTILITY["meme"]
    u = mech.anchored_utility(b, d, r)
    expected = b + math.exp(-1.2430377762128202) * (d - b)
    boundaries = (
        mech.anchored_utility(b, d, 1.0) == d
        and mech.anchored_utility(b, d, 0.0) == b
        and mech.anchored_utility(b, b, r) == b
    )
    check(abs(u - expected) < 1e-12 and boundaries,
          "B5 锚定式 U=B_i+R(D−B_i) 与三条边界",
          f"U={u:.6f}；R=1⇒U=D、R=0⇒U=B、D=B⇒U=B 全通过")

    # B6 保底候选资格口径：noise 出局、其余类型（含 other/marketing）按倾向分参与。
    check(not mech.floor_eligible("noise") and mech.floor_eligible("mourning")
          and mech.floor_eligible("other") and mech.floor_eligible("marketing"),
          "B6 保底候选资格：仅排除 noise，不限定 mourning 类型",
          f"排除表 {mech.DEFAULT_EVENT_FLOOR_EXCLUDE_TYPES}")

    # B7 校准器可复现：同一 (seed, N, scale) 两次调用必须逐值一致。
    # 回归护栏——曾经平票次序用 id()（内存地址）做 tie-break，同一 seed 每次跑出的
    # W13 份额都在漂移（±0.01 量级），使所有代理预估失去可复现性。
    _kw = dict(r_scale=15.0, w13_floor=5, rng_seed=3000)
    _r1, _r2 = cal.simulate(0.95, "normal", **_kw)[0], cal.simulate(0.95, "normal", **_kw)[0]
    _same = _r1 == _r2
    check(_same, "B7 校准器确定性（同 seed 两次调用逐值一致）",
          "逐周逐类型完全一致" if _same else
          "不一致：" + "；".join(f"{w}/{t} {_r1[w][t]}≠{_r2[w][t]}"
                                for w in _r1 for t in _r1[w] if _r1[w][t] != _r2[w][t])[:200])
    # B8 调度/监视/代理脚本可编译（防语法错误静默上线）。
    # 回归护栏——2026-09-13 实测 monitor.py 的中文说明里混入 ASCII 双引号，
    # `--with-monitor` 每完成一个 run 就崩一次，只有跑到那时候才暴露。
    _syn: list[str] = []
    _scripts = ("run_batch.py", "monitor.py", "proxy_predict.py", "verify_experiment.py",
                "plot_run_charts.py", "plot_arm_charts.py", "probe_llm.py")
    for _f in _scripts:
        _p = SCRIPT_DIR / _f
        try:
            compile(_p.read_text(encoding="utf-8"), str(_p), "exec")
        except SyntaxError as _e:
            _syn.append(f"{_f}:{_e.lineno} {_e.msg}")
    check(not _syn, "B8 调度/监视/出图脚本可编译（防语法错误静默上线）",
          f"{len(_scripts)} 个脚本全部通过" if not _syn else "；".join(_syn))

    # B9 批跑成功口径：**只看步数**，不看 pid.status；死进程判 interrupted 不判 running。
    # 回归护栏——引擎在 step 抛异常后仍落盘 status=completed 并打印
    # "Experiment completed successfully"。旧口径把 step=0 的空 run 记成 completed，
    # 会让空 run 静默混进 9-run 数据集（2026-09-13 实测 random_s2）。
    # 另一条：死进程若留在 running，build_plan→"wait" 会把它永久静默跳过、永远补不上。
    import tempfile as _tf
    _rb = _load("run_batch", SCRIPT_DIR / "run_batch.py")
    _exp = _rb.EXPECTED_STEPS
    with _tf.TemporaryDirectory() as _td:
        _d = Path(_td)

        def _stage(pid: dict, step_doc: dict) -> None:
            (_d / "pid.json").write_text(json.dumps(pid), encoding="utf-8")
            (_d / "SOCIETY_STEP.json").write_text(json.dumps(step_doc), encoding="utf-8")

        _stage({"pid": 0, "status": "completed", "step_count": 0}, {"step_count": 0})
        _s_short, _ = _rb.classify_run(_d)          # 自称 completed 但一步没跑
        _stage({"pid": 0, "status": "completed", "step_count": _exp},
               {"step_count": _exp, "terminated": True})
        _s_full, _ = _rb.classify_run(_d)           # 真跑完
        _stage({"pid": 999999, "status": "running", "step_count": 1}, {"step_count": 1})
        _s_dead, _ = _rb.classify_run(_d)           # 自称 running 但进程已死
    check(_s_short == "failed" and _s_full == "completed" and _s_dead == "interrupted",
          "B9 批跑成功口径（步数唯一判据 + 死进程判 interrupted）",
          f"自称completed但step=0→{_s_short}；step={_exp}+terminated→{_s_full}；死进程→{_s_dead}")

    # B10 replay 落盘完整性：agent_state 行数须 = n_agents × 11，env_state 须 = 11。
    # B9 卡的是引擎**自我申报**的步数；本项卡的是**实际落盘的数据**。二者缺一不可——
    # 事故形态「step_count 对但 curation 表为空/被截断」只靠 B9 挡不住。
    _pac = _load("plot_arm_charts", SCRIPT_DIR / "plot_arm_charts.py")
    _cases: list[tuple[str, bool]] = []
    with _tf.TemporaryDirectory() as _td2:
        _rd = Path(_td2) / "replay"
        _rd.mkdir(parents=True)

        def _fill(agent_lines: int, env_lines: int, profile_lines: int = 0) -> None:
            for f in _rd.glob("*.jsonl"):
                f.unlink()
            if agent_lines:
                (_rd / "curation_dynamics_agent_state.aa.jsonl").write_text(
                    "{}\n" * agent_lines, encoding="utf-8")
            if env_lines:
                (_rd / "curation_dynamics_env_state.bb.jsonl").write_text(
                    "{}\n" * env_lines, encoding="utf-8")
            if profile_lines:
                (_rd / "core_agent_profile.cc.jsonl").write_text(
                    "{}\n" * profile_lines, encoding="utf-8")

        _NA = 100
        _fill(_NA * _exp, _exp, _NA)
        _cases.append(("完整", _pac.check_replay(Path(_td2), _NA, "t") is None))
        _fill(_NA * _exp - 1, _exp)                       # agent_state 少一行
        _cases.append(("agent_state 少1行", _pac.check_replay(Path(_td2), _NA, "t") is not None))
        _fill(_NA * _exp, _exp - 1)                       # env_state 少一行
        _cases.append(("env_state 少1行", _pac.check_replay(Path(_td2), _NA, "t") is not None))
        _fill(0, 0, _NA)                                  # 只有 profile（事故原始形态）
        _cases.append(("仅 profile（事故形态）", _pac.check_replay(Path(_td2), _NA, "t") is not None))
        _fill(0, 0, 0)                                    # 全空
        _cases.append(("replay 全空", _pac.check_replay(Path(_td2), _NA, "t") is not None))
    _bad = [n for n, ok in _cases if not ok]
    check(not _bad, "B10 replay 落盘完整性（行数 = n_agents × 11 周）",
          "5 种情形判定全对（含 09-13 事故形态「仅 profile」）" if not _bad
          else "判定错误：" + "、".join(_bad))
    return mech, cal


# ---------------------------------------------------------------------------
# C. 机制层：直接驱动 env（无 agent / 无 LLM / 不写 replay）
# ---------------------------------------------------------------------------
def layer_c(mech, cal) -> None:
    env_mod = _load("curation_dynamics_space", ROOT / "custom" / "envs" / "curation_dynamics_space.py")
    cfg_doc = json.loads(
        (CONFIGS_DIR / "anchored_v1_chronological_s0.json").read_text(encoding="utf-8")
    )
    kw = dict(cfg_doc["env_modules"][0]["kwargs"])
    kw["injection_data_path"] = str(ROOT / kw["injection_data_path"])
    kw["vocab_path"] = str(ROOT / kw["vocab_path"])
    action_hours = {str(k): int(v) for k, v in kw["chronological_action_hours"].items()}
    unique_hours = sorted(set(action_hours.values()))
    step_text = (SCRIPT_DIR / "init" / "steps_chronological_hourly.yaml").read_text(encoding="utf-8")
    first_line = step_text.splitlines()[0]
    start_t = datetime.fromisoformat(first_line.split('"', 2)[1])
    n_batches = step_text.count("num_steps: 1")

    check(len(action_hours) == 100 and len(unique_hours) == 63
          and n_batches == 11 * len(unique_hours)
          and n_batches == kw["chronological_total_batches"],
          "C1 chronological 冻结行动表与事件驱动批次完整",
          f"100 agents；每周 {len(unique_hours)} 个有人行动小时；总批次 {n_batches}")

    # 取 W12 最后一个行动小时做完整 10 槽检查；最早小时可能发生在首条样本发布前，
    # 此时按严格时序允许 feed 少于 10 条（不能用未来帖补齐）。
    check_t = datetime.fromisocalendar(2026, 12, 1) + timedelta(hours=max(unique_hours))
    env = env_mod.CurationDynamicsSpace(**kw)
    asyncio.run(env.init(check_t))
    active = sorted(env._chronological_active_agents)
    feeds = [env._feeds[aid] for aid in active]
    feed_ok = bool(feeds) and all(len(feed) == 10 for feed in feeds)
    ordered = all(
        [it.get("event_time", "") for it in feed]
        == sorted([it.get("event_time", "") for it in feed], reverse=True)
        for feed in feeds
    )
    no_future = all(
        datetime.fromisoformat(it["event_time"]) <= check_t
        for feed in feeds for it in feed
    )
    check(feed_ok and ordered and no_future,
          "C2 chronological 只看已发布内容并按精确时间倒序取最新10条",
          f"首批 active={len(active)}；feed=10={feed_ok}；倒序={ordered}；无未来帖={no_future}")

    check(not env._pinned_ids and not env._event_floor_ids
          and env._feed_live_pool == len(env._posts),
          "C3 chronological 无生命周期/退场、置顶或W13保底",
          f"候选池={env._feed_live_pool}=全池{len(env._posts)}；pin={env._pinned_ids}；floor={env._event_floor_ids}")

    # 找一个至少两人的小时，验证同小时互不可见；提交后并池，下一小时即成为可见候选。
    crowded_hour = next(h for h in unique_hours if sum(v == h for v in action_hours.values()) >= 2)
    crowded_t = datetime.fromisocalendar(2026, 12, 1) + timedelta(hours=crowded_hour)
    env2 = env_mod.CurationDynamicsSpace(**kw)
    asyncio.run(env2.init(crowded_t))
    pair = sorted(env2._chronological_active_agents)[:2]
    before_ids = {it["post_id"] for aid in pair for it in env2._feeds[aid]}
    responses = [asyncio.run(env2.create_post(aid, "离线时序验证帖")) for aid in pair]
    new_ids = {r["post_id"] for r in responses}
    mutually_hidden = new_ids.isdisjoint(before_ids)
    env2._flush_pending_to_pool()
    eligible_next = new_ids.issubset(env2._posts)
    check(len(pair) == 2 and mutually_hidden and eligible_next,
          "C4 同小时同步快照互不可见；批次结束后跨小时可见",
          f"pair={pair}；同小时feed不含新帖={mutually_hidden}；批次后进入候选池={eligible_next}")

    # random / interest 继续走自己的周级制度，确认 chronological 改造没有借用或覆盖它们。
    weekly = {}
    for alg in ("random", "interest"):
        d = json.loads((CONFIGS_DIR / f"anchored_v1_{alg}_s0.json").read_text(encoding="utf-8"))
        wkw = dict(d["env_modules"][0]["kwargs"])
        wkw["injection_data_path"] = str(ROOT / wkw["injection_data_path"])
        wkw["vocab_path"] = str(ROOT / wkw["vocab_path"])
        e = env_mod.CurationDynamicsSpace(**wkw)
        e._open_tick("2026-W12")
        e._open_tick("2026-W13")
        weekly[alg] = e
    check(not weekly["random"]._pinned_ids and not weekly["random"]._event_floor_ids
          and len(weekly["interest"]._pinned_ids) == 1
          and len(weekly["interest"]._event_floor_ids) == 5,
          "C5 random / interest 定义未被 chronological 改造",
          "random仍为全历史全槽随机且无强制位；interest仍保留生命周期、置顶与W13保底")

    expected = {
        "no_b": ("baseline_utility", 0.0),
        "no_d": ("spiral_scale", 0.0),
        "no_r": ("decay", 0.0),
    }
    ablation_ok = True
    details = []
    for name, (key, value) in expected.items():
        d = json.loads((CONFIGS_DIR / f"anchored_v1_ablation_{name}_s0.json").read_text(encoding="utf-8"))
        vals = {float(a["kwargs"]["params"][key]) for a in d["agents"]}
        ablation_ok &= vals == {value}
        details.append(f"{name}.{key}={sorted(vals)}")
    check(ablation_ok, "C6 新公式的去B/去D/去R三个单因素消融配置正确",
          "；".join(details))

    ticks = [int(line.split(":", 1)[1].strip()) for line in step_text.splitlines()
             if line.strip().startswith("tick:")]
    env3 = env_mod.CurationDynamicsSpace(**kw)

    async def _drive_full_schedule() -> None:
        async def _no_write(*args, **kwargs):
            return None

        env3._write_env_state = _no_write
        env3._write_agent_state_batch = _no_write
        now = start_t
        await env3.init(now)
        for seconds in ticks:
            await env3.step(seconds, now)
            now += timedelta(seconds=seconds)

    asyncio.run(_drive_full_schedule())
    check(env3._chronological_batch_index == n_batches
          and env3._step_index == 11
          and env3._chronological_injection_cursor == 250,
          "C7 chronological 全693批次离线推进后仅形成11个周度快照",
          f"batch={env3._chronological_batch_index}；week_rows={env3._step_index}；"
          f"注入游标={env3._chronological_injection_cursor}/250")


def main() -> int:
    ap = argparse.ArgumentParser(description="h4e1 全链路离线核验（无 LLM）")
    ap.add_argument("--quiet", action="store_true", help="只打印失败项与总结")
    args = ap.parse_args()

    print("===== h4e1 离线核验（不跑 LLM / 不写 replay）=====\n")
    layer_a()
    print("--- A 配置层 完成 ---")
    mech, cal = layer_b()
    print("--- B 同构层 完成 ---")
    layer_c(mech, cal)
    print("--- C 机制层 完成 ---\n")

    for ok, name, detail in RESULTS:
        if args.quiet and ok:
            continue
        print(f"{'✓' if ok else '✗'} {name}\n    {detail}")
    if OBSERVED:
        print("\n----- 观察项（不参与退出码，供人工判断）-----")
        for name, detail in OBSERVED:
            print(f"⚠ {name}\n    {detail}")
    bad = [r for r in RESULTS if not r[0]]
    print(f"\n===== 通过 {len(RESULTS) - len(bad)}/{len(RESULTS)} =====")
    for _, name, _ in bad:
        print(f"  ✗ {name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
