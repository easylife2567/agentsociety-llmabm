#!/usr/bin/env python3
"""verify_experiment.py: 全链路离线核验（不跑 LLM、不写 replay、不写任何实验产物；秒级）。

动机（用户 2026-09-13 要求"再核实一遍整体实验"）：R 尺度 15 与事件周议程保底（W13 保底 5 条
哀悼帖 + 官方讣告置顶）是**平台级**改动，一旦 env / agent / 校准脚本 / 代理 / 配置五处口径漂移，
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
     B3 类型参数均值：personas._PARAM_SPECS[*][k][0] == agent 侧 _PARAM_DEFAULTS[type][k]；
     B4 议程保底条数：config_params == manifest == 校准脚本解析值；
     B5 D/R 公式：三处对同一输入给出同值（共享纯函数 + cliff 边界）；
     B6 保底候选资格口径：仅排除 noise，不限定 mourning 类型；
     B7 校准器确定性：同 (seed,N,scale) 两次调用逐值一致（防 id() 平票漂移）；
     B8 调度/监视/代理脚本可编译（防语法错误静默上线）；
     B9 批跑成功口径：步数唯一判据 + 死进程判 interrupted（防空 run 静默混入 / 静默跳过）。

  C. **机制层**（直接驱动 env 逐周，无 agent 产出、无 LLM、不写 replay）
     C1 W13 每条 feed 首位 = 官方讣告帖（official=True），三臂一致；
     C2 W13 紧随置顶之后恰有 5 条保底帖，**全员相同**、三臂一致，且恰为全池哀悼倾向分前 5
        （裁定口径是"倾向分前 5"而非"5 条 mourning 类型"；保底的实际类型构成列为**观察项**）；
     C3 非事件周保底集合为空；保底帖不计入算法槽位（不与余下槽位重复）；
     C4 同周 feed_live_pool / 置顶槽位数三臂相等（跨臂可比性）；每 feed 长度 = feed_size；
     C5 曝光槽位帖龄 ≥3 周恒为 0（生命周期退场生效）；
     C6 W13 每条 feed 的悼念槽位 ≥ 1 置顶 + 保底中判为 mourning 的条数（事件周强制暴露下界）。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/verify_experiment.py
    $PYTHON_PATH hypothesis_4/experiment_1/verify_experiment.py --quiet   # 只打印结论
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
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
    tracked = [CONFIGS_DIR / f"{a}_s{s}.json" for a in ("random", "chronological", "interest")
               for s in (0, 1, 2)]
    tracked += [CONFIGS_DIR / "manifest.json", SCRIPT_DIR / "init" / "steps.yaml",
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

    param_ok, bad = True, []
    for t, spec in personas._PARAM_SPECS.items():
        for k, v in agent._PARAM_DEFAULTS[t].items():
            mean = spec[k][0] if isinstance(spec[k], (tuple, list)) else spec[k]
            if abs(float(mean) - float(v)) > 1e-9:
                param_ok = False
                bad.append(f"{t}.{k}: personas {mean} vs agent {v}")
    check(param_ok, "B3 类型参数均值 personas == agent 回退值", "；".join(bad) or "activity/spiral/decay 全对齐")

    floor_ok = (cal.EVENT_WEEK_MOURNING_FLOOR == 5)
    cfg = json.loads((CONFIGS_DIR / "manifest.json").read_text(encoding="utf-8"))
    floor_ok &= cfg["feed_mechanism"]["event_week_mourning_floor"]["value"] == 5
    floors: set[int] = set()
    for p in CONFIGS_DIR.glob("*_s*.json"):
        floors.add(json.loads(p.read_text(encoding="utf-8"))["env_modules"][0]["kwargs"]
                   ["event_week_mourning_floor"])
    floor_ok &= floors == {5}
    check(floor_ok, "B4 议程保底条数 = 5（manifest / 9 配置 / 校准脚本同源）",
          f"manifest=5，9 配置={sorted(floors)}，校准解析={cal.EVENT_WEEK_MOURNING_FLOOR}")

    # B4b 校准器保留注入帖原始类型（含 noise）：否则方案 B 的过滤在校准侧失效，
    # 且 env 把 noise 单列一类、校准器若并入 "other" 会抬高"其他"型 agent 的 cum_own。
    raw_types = {rec["type"] for lst in cal.INJECTED_BY_WEEK.values() for rec in lst}
    check("noise" in raw_types, "B4b 校准器保留注入帖原始类型（与 env 同口径，含 noise）",
          f"注入池出现类型 {sorted(raw_types)}")

    # B5 公式同值：D 与 R 对同一输入与解析式逐值一致
    import math
    px = mech.spiral_factor(0.30, 0.19, 1.2)
    py = mech.spiral_factor(0.0, 0.19, 1.2)          # 完全看不到本类 → 净成本段
    rz = mech.fatigue_factor(0.8, 30.0)
    # D<0 的临界占比：s·tanh(k·gap) < −1 ⟺ share < base·(1 + atanh(−1/s)/k)
    crit = 0.19 * (1 + math.atanh(-1 / 1.2) / 1.5)
    check(abs(px - (1 + 1.2 * math.tanh(1.5 * ((0.30 - 0.19) / 0.19)))) < 1e-12
          and py < 0 < px and abs(rz - math.exp(-0.8 * 30.0 / 15.0)) < 1e-12,
          "B5 D/R 公式（含 D<0 的净成本段与 R 尺度 15）",
          f"D(0.30)={px:.4f} >0；D(share=0)={py:.4f} <0（孤立成本；s=1.2 时占比需低于 "
          f"{crit:.3f} 才转负）；R(λ=0.8,cum=30)={rz:.4f}")

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
    return mech, cal


# ---------------------------------------------------------------------------
# C. 机制层：直接驱动 env（无 agent / 无 LLM / 不写 replay）
# ---------------------------------------------------------------------------
def layer_c(mech, cal) -> None:
    env_mod = _load("curation_dynamics_space", ROOT / "custom" / "envs" / "curation_dynamics_space.py")
    wk_list = [f"2026-W{i}" for i in range(12, 23)]
    arms = {}
    for alg in ("random", "chronological", "interest"):
        kw = json.loads((CONFIGS_DIR / f"{alg}_s0.json").read_text(encoding="utf-8"))
        kw = dict(kw["env_modules"][0]["kwargs"])
        kw["injection_data_path"] = str(ROOT / kw["injection_data_path"])
        kw["vocab_path"] = str(ROOT / kw["vocab_path"])
        env = env_mod.CurationDynamicsSpace(**kw)
        snap: dict[str, dict] = {}
        for wk in wk_list:
            env._open_tick(wk)          # 无 agent 产出 → 与 init+step 的逐周推进等价
            snap[wk] = {
                "feeds": {aid: [dict(it) for it in f] for aid, f in env._feeds.items()},
                "pinned": list(env._pinned_ids),
                "floor": list(env._event_floor_ids),
                "live": env._feed_live_pool,
                "age": dict(env._exposure_age_buckets),
                "posts": {pid: dict(p) for pid, p in env._posts.items()},
            }
        arms[alg] = snap

    ev = "2026-W13"
    aids = sorted(arms["interest"][ev]["feeds"])
    posts_i = arms["interest"][ev]["posts"]

    # C1 官方置顶首位 + 三臂一致
    def pinned_first(alg: str) -> bool:
        return all(arms[alg][ev]["feeds"][a]
                   and arms[alg][ev]["feeds"][a][0]["is_official"] for a in aids)

    pin_ids = {alg: tuple(arms[alg][ev]["pinned"]) for alg in arms}
    check(all(pinned_first(a) for a in arms) and len(set(pin_ids.values())) == 1
          and len(pin_ids["interest"]) == 1 and posts_i[pin_ids["interest"][0]]["week"] == ev,
          "C1 W13 每条 feed 首位 = 官方讣告帖（三臂同一集合）",
          f"置顶槽位 {len(pin_ids['interest'])} 条/feed，三臂 id 集合一致；"
          f"非事件周置顶数 W12={len(arms['interest']['2026-W12']['pinned'])}")

    # C2 保底 5 条、全员相同、且为全池哀悼倾向前 5
    fl_sets = {alg: frozenset(arms[alg][ev]["floor"]) for alg in arms}
    # 每个 agent 的 feed 第 2~6 槽位（置顶之后 = 保底段）序列；集合大小为 1 ⇔ 全员相同
    per_agent = {alg: {tuple(it["post_id"] for it in arms[alg][ev]["feeds"][a][1:1 + 5])
                       for a in sorted(arms[alg][ev]["feeds"])} for alg in arms}
    all_live = [pid for pid, p in posts_i.items()
                if not mech.is_retired(p.get("life", 1.0), 0.35)
                and pid not in set(arms["interest"][ev]["pinned"])
                and mech.floor_eligible(p.get("type", ""))]   # 方案 B：候选池排除 noise
    top5 = set(sorted(all_live, key=lambda pid: (-(posts_i[pid].get("tendencies") or {}).get("mourning", 0.0), -pid))[:5])
    uniq_ok = all(len(s) == 1 for s in per_agent.values())
    seq_ok = uniq_ok and all(next(iter(s)) == tuple(arms["interest"][ev]["floor"]) for s in per_agent.values())
    check(len(fl_sets["interest"]) == 5 and uniq_ok and seq_ok
          and fl_sets["interest"] == top5 and len({frozenset(v) for v in fl_sets.values()}) == 1,
          "C2 W13 保底 5 条：全员相同、三臂一致，且 = 全池哀悼倾向分前 5（用户裁定口径）",
          f"保底集合 {sorted(fl_sets['interest'])}；三臂各自'全员第2-6槽位唯一'={uniq_ok}；"
          f"序列与 _event_floor_ids 一致={seq_ok}；等于哀悼倾向前5={fl_sets['interest'] == top5}")
    # 保底集合的**类型构成**：裁定口径是"哀悼倾向分前 5"，不保证 5 条都判为 mourning
    # （倾向分 = 命中数/(字数/50)，短文本密度虚高）。此处只观察不判负，供人工判断。
    comp = [posts_i[pid]["type"] for pid in arms["interest"][ev]["floor"]]
    n_noise = sum(1 for t in comp if t == "noise")
    check(n_noise == 0, "C2b 保底候选池排除 noise（用户 2026-09-13 裁定·方案 B）",
          f"保底类型构成 {comp}；noise {n_noise} 条（应为 0）")
    observe("W13 保底帖类型构成（裁定为「哀悼倾向分前5」，非「5 条 mourning 类型」）",
            f"{comp}；其中 noise {n_noise} 条")

    # C3 非事件周无保底 + 保底帖不与算法槽位重复
    no_floor = all(len(arms["interest"][wk]["floor"]) == 0 for wk in wk_list if wk != ev)
    dup = any(len({it["post_id"] for it in f}) != len(f) for alg in arms for wk in wk_list
              for f in arms[alg][wk]["feeds"].values())
    check(no_floor and not dup, "C3 非事件周无保底；feed 内无重复帖",
          f"10 个非事件周保底集合均为空={no_floor}；feed 内 post_id 唯一={not dup}")

    # C4 跨臂可比性 + feed 长度
    live_eq = all(len({arms[alg][wk]["live"] for alg in arms}) == 1 for wk in wk_list)
    pin_eq = all(len({tuple(arms[alg][wk]["pinned"]) for alg in arms}) == 1 for wk in wk_list)
    lens = {len(f) for alg in arms for wk in wk_list for f in arms[alg][wk]["feeds"].values()}
    check(live_eq and pin_eq and lens == {10},
          "C4 三臂同周活池/置顶相等（跨臂可比）；feed 长度恒 = 10",
          f"feed_live_pool 三臂相等={live_eq}；置顶相等={pin_eq}；feed 长度取值 {sorted(lens)}")

    # C5 老帖退场生效
    age3 = {wk: arms["interest"][wk]["age"]["age3plus"] for wk in wk_list}
    check(all(v == 0 for v in age3.values()), "C5 曝光槽位帖龄 ≥3 周恒为 0（生命周期退场）",
          f"逐周 {[age3[w] for w in wk_list]}")

    # C6 事件周悼念槽位下限：1 条官方置顶 + 保底中判为 mourning 的条数（保底可能含非 mourning 帖）
    floor_m = sum(1 for pid in arms["interest"][ev]["floor"] if posts_i[pid]["type"] == "mourning")
    m13 = {alg: min(sum(1 for it in arms[alg][ev]["feeds"][a] if it["type"] == "mourning") for a in aids)
           for alg in arms}
    check(all(v >= 1 + floor_m for v in m13.values()),
          "C6 W13 每条 feed 悼念槽位 ≥ 1 置顶 + 保底 mourning 数（强制暴露下界）",
          f"下界 {1 + floor_m}（1 置顶 + 保底中 {floor_m} 条 mourning）；三臂实际最小值 {m13}")


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
