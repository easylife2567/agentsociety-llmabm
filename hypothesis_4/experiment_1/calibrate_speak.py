"""玩梗涌现环境门槛基数（activity_base）快速校准（2026-09-12 feed 机制重设计后重写）。

方法论：与旧表达效用校准同框架（真实数据代理），但**气候输入改为同构的 feed 层推演**——
烟测诊断（SMOKE_DIAGNOSIS_w19_cliff.md）指出：旧校准用"真实世界当周本类内容份额"作 D 因子的
气候代理，而真实 sim 里 D 读的是 agent 本人 feed 的类型分布，二者口径差正是"校准说 W19 温和起量、
sim 却一步到顶"的来源。本版直接推演 feed：候选池 = 真实注入样本（带正文→真倾向分）+ agent 帖，
按**与 env 完全相同的**生命周期/曝光饱和/退场与兴趣比例抽样装配 feed，再算 share_own → D。

机制同构由代码保证：周序数、生命衰减、曝光饱和、倾向分、兴趣打分、softmax 抽样全部来自
`custom/envs/curation_mechanisms.py`（env 同时 import 同一份）。另提供
`--assert-replay <run_dir>`：用 replay 记录的逐周供给计数复算 B/S/G 并与 replay 记录值
逐值比对（容差 1e-6），直接校验涌现环境公式的同构性。

- S_t（流量空旷度）：env 读外生现实口径周新增调度（config_params.EMERGENCE_FLOW_BY_WEEK，
  = injection_posts.json 各周全量帖数），S_t = h(Flow_w)/h(Flow_base)，h(x)=K_f/(K_f+x)，
  K_f = 调度基线周值（W12）。sustained_hot 反事实臂：事件周（W13）记录 S，之后冻结。
- B_t（存量丰沛度）：env 内生——Stock_t = 过去 6 周 arena 供给总数（注入 + 滞后 1 tick 的
  agent 帖），B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)，K_a = 注入计划事件周窗口存量。
- G_t = clamp(B_t^β · S_t^σ, 0.2, 3.0)（**观测序列**，2026-09-12 起不进入决策）。
- 决策：**U = B_i + R·(D−B_i)**，发言当且仅当 U ≥ activity_i（2026-09-14
  锚定式修订；环境增益 G^θ 维持退役）。D、R、U 均走共享纯函数
  `mech.spiral_factor`（有界 tanh，无地板）；R 的 cum_own 用推演中该 agent 实际见到的
  本类槽位数累计；R→0 时回到事件前常态锚点 B_i。旧纯乘法代理实测：门槛下调
  （0.85-0.4）对起爆时点无杠杆——区间 [0.85,1.0] 内
  一律 W20 起步，只有 0.4 档量级持平但 W14-W17 就出现玩梗（与真实基准 W12-W18
  梗份额 ≤1.5% 相悖）；故门槛维持 0.95。

选点标准（2026-09-12 更新）：agent 供给 > 注入 250 且总量在可接受预算内 ＋ 形态合理
（W13 悼念冲击、**玩梗 W18-W19 温和起步 → W20-W22 起量**、营销/教育稳定供给）＋
玩梗 share_own 逐 agent 有梯度（sd > 0）。

**2026-09-12 复核结论（用户裁定"activity 基数本轮不动"）**：feed 机制重设计后重扫
1.15/1.10/1.05/1.00/0.95，门槛基数维持 **0.95**（personas 未改）。基准基数 0.95 下
normal 臂代理总量 525 帖/run（旧机制定标 463，上移 13%，主因气候从 {0,1} 变为有梯度后
多数类型的 D 抬升）；若按旧"300-350 帖/run"目标则应取 1.15（该档代理总量 337、
玩梗轨迹 0/0/0/0/2/2/6/13/15/17 更平缓、反事实臂 W20-22 仅 6 帖）——**留作后续裁定项**。
本脚本只读文件并打印；定标结果人工裁定后写入文档。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
from pathlib import Path

script_dir = Path(__file__).resolve().parent
workspace_root = script_dir.parent.parent

FEED_SIZE = 10          # 用户 2026-09-10 裁定：每 agent 每周 10 条信息流
BASE_REF = 0.95         # personas 当前门槛基数（缩放锚点）
CANDIDATE_BASES = [1.0, 0.95, 0.9, 0.85, 0.8, 0.7]
GAIN_MIN, GAIN_MAX = 0.2, 3.0
STOCK_WINDOW = 6        # env 默认 emergence_window_stock

WEEKS = [f"2026-W{i}" for i in range(12, 23)]
START_WEEK = "2026-W12"
EVENT_WEEK = "2026-W13"

# ---------------------------------------------------------------------------
# feed 机制参数（与 init/configs/manifest.json 的 feed_mechanism 同源）
# ---------------------------------------------------------------------------
LIFE_HALF_LIFE_WEEKS = 1.5      # 时间冷却半衰期（周）
LIFE_SATURATION_SCALE = 20.0    # 曝光饱和尺度：累计曝光达该值生命折半
LIFE_RETIRE_FLOOR = 0.35        # 退场线（≈3 周流通窗口：age 0/1/2）
INTEREST_SAMPLE_TEMP = 4.0      # 兴趣比例抽样温度
# env 侧 RNG 流：注入=seed、随机臂=seed+1000、兴趣噪声=seed+2000、兴趣抽样=seed+3000。
# 校准取 seed=0（cell 种子之一），抽样流偏移与 env 一致。
CALIB_SAMPLE_SEED = 3000

# 注入样本（config_params 按 seed+777 预抽样；校准用 seed0 → 777）
INJECTION_SAMPLE_PATH = script_dir / "init" / "injection_sample_s0.json"
VOCAB_PATH = workspace_root / "custom" / "envs" / "curation_assets" / "vocabs.json"
MANIFEST_PATH = script_dir / "init" / "configs" / "manifest.json"
BENCH_PATH = workspace_root / "hypothesis_4" / "benchmark_curves.json"

# agent 帖倾向分画像（逐类型中位数）——LLM 内容生成器的输入参数，不是本机制的产出。
# 来源：feed 机制重设计后的烟测 run interest_normal_s0 的 ENV_STATE.json 全池 agent 帖
# 实测中位数（2026-09-12 复填；agent 帖短而词表密度高，meme 帖倾向分系统性高于注入帖，
# 见 SMOKE_DIAGNOSIS_w19_cliff.md 第 3.7 节）。LLM 内容生成器（prompt / 温度 / 词表）
# 若有改动需回填复核——敏感性实测：画像整体缩放 ×0.4-1.0 不改变玩梗起量形态。
AGENT_TENDENCY_PROFILE: dict[str, dict[str, float]] = {
    "meme":      {"mourning": 0.42,  "marketing": 0.0,   "education": 0.0,   "meme": 6.56},
    "mourning":  {"mourning": 3.13,  "marketing": 0.43,  "education": 1.37,  "meme": 0.17},
    "marketing": {"mourning": 0.14,  "marketing": 4.64,  "education": 2.13,  "meme": 0.0},
    "education": {"mourning": 0.0,   "marketing": 1.25,  "education": 3.98,  "meme": 0.0},
    "other":     {"mourning": 0.42,  "marketing": 0.81,  "education": 1.14,  "meme": 0.0},
}

TYPE_KEYS = {  # benchmark 中文键 → agent 类型
    "梗文化讨论": "meme",
    "事件悼念讨论": "mourning",
    "借势营销": "marketing",
    "教育观点讨论": "education",
    "其他讨论": "other",
}
TYPE_ORDER = ["meme", "mourning", "marketing", "education", "other"]


# ---------------------------------------------------------------------------
# 共享机制模块（与 env 完全同一份实现）
# ---------------------------------------------------------------------------
def _load_shared_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mech = _load_shared_module("curation_mechanisms", workspace_root / "custom" / "envs" / "curation_mechanisms.py")
personas_mod = _load_shared_module("curation_personas", workspace_root / "custom" / "agents" / "curation_personas.py")

POPULATION_COUNTS = {"meme": 19, "mourning": 22, "marketing": 23, "education": 15, "other": 21}
population = personas_mod.build_population(POPULATION_COUNTS, seed=42)
AGENT_TYPES = {str(p["id"]): p["agent_type"] for p in population}

# ---------------------------------------------------------------------------
# 输入：注入分配 + 现实口径流量调度（与 18 个配置同源：configs/manifest.json）
# ---------------------------------------------------------------------------
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
INJ_ALLOC: dict[str, int] = {str(k): int(v) for k, v in manifest["injection"]["allocation"].items()}
FLOW_WORLD: dict[str, int] = {str(k): int(v) for k, v in manifest["emergence_env"]["flow_schedule"].items()}
assert sorted(INJ_ALLOC) == sorted(FLOW_WORLD) == sorted(WEEKS), "manifest 周集合与 WEEKS 不一致"

# 议程设置（与 env / config_params 同源）：事件周每 agent feed 保底 N 条哀悼帖。
_event_floor_meta = (manifest.get("feed_mechanism") or {}).get("event_week_mourning_floor") or {}
EVENT_WEEK_MOURNING_FLOOR = int(_event_floor_meta.get("value", 0))

K_F_DEFAULT = FLOW_WORLD[START_WEEK]                          # env 默认 emergence_kf（1246）
K_A_DEFAULT = INJ_ALLOC[START_WEEK] + INJ_ALLOC[EVENT_WEEK]   # env 默认 emergence_ka（17+35=52）
STOCK_BASE = INJ_ALLOC[START_WEEK]                            # W12 arena 流量（17，agent 帖滞后入池）

# 注入样本（带正文）：倾向分用共享函数现算，与 env 注入时同口径
_sample_doc = json.loads(INJECTION_SAMPLE_PATH.read_text(encoding="utf-8"))
_vocab_lists = mech.vocab_lists_from_doc(json.loads(VOCAB_PATH.read_text(encoding="utf-8")))
INJECTED_BY_WEEK: dict[str, list[dict]] = {}
for _p in _sample_doc["posts"]:
    _t = str(_p.get("type", "other"))
    INJECTED_BY_WEEK.setdefault(str(_p["week"]), []).append(
        # 保留原始类型（含 "noise"），与 env 同口径：env 的候选池计数把 noise 单列一类，
        # 既不抬升"其他"型 agent 的 cum_own/气候，也是议程保底候选过滤（方案 B）的依据。
        # 2026-09-13 前此处把非五类映射为 "other"，与 env 不同构。
        {"type": _t,
         "official": bool(_p.get("is_official", False)),   # 官方帖在当周对全员置顶（env 同一规则）
         "tend": mech.compute_tendencies(str(_p.get("content", "")), _vocab_lists)}
    )
assert all(len(INJECTED_BY_WEEK.get(w, [])) == INJ_ALLOC[w] for w in WEEKS), \
    "注入样本周量与 manifest 分配不一致"


def typed_shares() -> dict[str, dict[str, float]]:
    """各周各类型真实内容份额（剔除爬取噪音）——仅作输出对照，不再作为 D 的气候输入。"""
    bench = json.loads(BENCH_PATH.read_text(encoding="utf-8"))
    matrix = bench["weekly_category_matrix"]
    shares: dict[str, dict[str, float]] = {}
    for wk in WEEKS:
        row = matrix[wk]
        typed = {t: float(row.get(cn, 0) or 0) for cn, t in TYPE_KEYS.items()}
        total = sum(typed.values())
        shares[wk] = {t: (typed[t] / total if total > 0 else 0.0) for t in TYPE_ORDER}
    return shares


def simulate(
    base: float,
    mode: str,
    ka: float = K_A_DEFAULT,
    kf: float = K_F_DEFAULT,
    beta: float = 1.0,
    sigma: float = 1.0,
    temp: float = INTEREST_SAMPLE_TEMP,
    half_life: float = LIFE_HALF_LIFE_WEEKS,
    saturation: float = LIFE_SATURATION_SCALE,
    r_scale: float = mech.DEFAULT_DECAY_SCALE,
    w13_floor: int = EVENT_WEEK_MOURNING_FLOOR,
    rng_seed: int = CALIB_SAMPLE_SEED,
    spiral_mult: float | None = None,
    decay_mult: float = 1.0,
    utility_mode: str = "anchored",
    baseline_utility: dict[str, float] | None = None,
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """端到端代理推演 11 周，返回 ({week: {type: 发言数}}, {week: 环境轨迹}, {week: {type: 本类可见份额}})。

    与 env 同构（周序数/生命衰减/曝光饱和/退场/倾向分/兴趣打分/比例抽样全部走共享纯函数）：
    - 候选池：当周注入 + 上一 tick 收尾并入的 agent 帖（agent 帖滞后 1 tick 可见）；
    - 每帖 life 每周 × weekly_decay，注入/入池置 1.0；life < 退场线 → 退出候选池；
    - **强制位（与 env 的平台级规则逐条对应，2026-09-13 补齐）**：
      ① 官方置顶：is_official 注入帖在当周占全员 feed 首位（official_pin_extend_weeks=0，
         即仅 W13 的讣告帖）；② 议程保底：事件周（W13）取全池（未退场、非置顶）哀悼倾向分
         最高的 w13_floor 条，全员相同，紧接置顶之后占槽位（`--w13-floor`，0=关闭）；
    - feed 余下槽位：对每个 agent 按 interest_score 打分，按 exp(score/T) 无放回抽满；
      装配时即记账曝光（曝光饱和项随之下降，抑制单帖同周垄断）；
    - share_own = 该 agent 本周 feed 中本类槽位占比（D 的气候输入，逐 agent 不同）；
    - Stock 以 6 周窗口滚动累计；S 读现实口径调度（B/S/G 仅作 trace 观测，不进入决策）。
    - 决策默认 U = B_i+R·(D−B_i)（D/R/U 均走共享纯函数）；
      mode 仅影响 trace 里 S 是否冻结。
    - **效用形式**：默认 `anchored` 使用
      `U=B_i+R·(D−B_i)`，其中 `baseline_utility` 可按 agent id 或类型提供锚点。
      `multiplicative` 仅保留为旧机制历史对照。
    - **反事实开关**（默认 1.0 = 现状，即两条机制全开，不影响既有任何结论）：
      spiral_mult 显式传入时覆盖 profile 的 spiral_scale，并乘在每个 agent 的 s 上
      （0 → D≡1，沉默螺旋关闭）；缺省读取本轮标定的 alpha_D；
      decay_mult  乘在每个 agent 的 λ 上（0 → R≡1，注意力衰减关闭）。
      置零为**精确消融**（1 + 0·tanh ≡ 1、exp(−0·x) ≡ 1），不是近似档；
      与真机反事实同构：真机即把 profile 下发的 params.spiral / params.decay 整体缩放同一倍数。
      注意 D、R 非独立——基线里正是 D 的共振放大把 agent 抬过 R 衰减后的门槛，
      故两机制同时关闭（U≡1，纯门槛）是必须单列的一档。

    已知未建模的 env 细节（量级 <1.5%，需判断时扣除）：interest 打分的均匀噪声
    ±interest_noise_eps=0.05（env 的 Random(seed+2000) 流）。另 env 打分与抽样共用同一
    RNG 流声明顺序，本脚本按 population 顺序逐 agent 消费，逐值不完全同步但分布同构。
    """
    rng = random.Random(rng_seed)
    cum_own = {p["id"]: 0.0 for p in population}
    pool: list[dict] = []           # {seq, week, type, official, tend(dict), life, exposure}
    _seq = 0                        # 稳定序号：入池顺序（确定性），充当 env 里 pid 的角色
    flow_hist: dict[str, float] = {}
    prev_speak = 0.0                # 上一周 agent 发言总数（W11=0）
    result: dict[str, dict[str, int]] = {}
    trace: dict[str, dict[str, float]] = {}
    climates: dict[str, dict[str, float]] = {}
    sustained_s: float | None = None
    flow_base = float(FLOW_WORLD[START_WEEK])   # 现实口径基线（env: flow_env_base）

    for wk in WEEKS:
        # 0) 生命周期：本周冷却步长（在注入之前，保证新帖 life=1.0）。
        step = mech.weekly_decay(half_life)
        for item in pool:
            item["life"] *= step

        # 1) 注入本周（life=1.0）。
        for rec in INJECTED_BY_WEEK[wk]:
            pool.append({"seq": _seq, "week": wk, "type": rec["type"],
                         "official": rec["official"], "tend": dict(rec["tend"]),
                         "life": 1.0, "exposure": 0})
            _seq += 1

        # 2) 涌现环境（与 env 同式；B 的输入是 arena 供给计数，与内容无关）。
        flow_arena = INJ_ALLOC[wk] + prev_speak
        flow_hist[wk] = flow_arena
        i = WEEKS.index(wk)
        stock = sum(flow_hist[w] for w in WEEKS[max(0, i - STOCK_WINDOW + 1): i + 1])
        stock_base = flow_hist[START_WEEK]
        abundance = (stock / (stock + ka)) / (stock_base / (stock_base + ka))
        emptiness = (kf / (kf + FLOW_WORLD[wk])) / (kf / (kf + flow_base))
        if mode == "sustained_hot":
            if wk == EVENT_WEEK:
                sustained_s = emptiness     # 事件周记录
            elif sustained_s is not None:
                emptiness = sustained_s     # 之后冻结（B 保持内生）
        gain = max(GAIN_MIN, min(GAIN_MAX, (abundance ** beta) * (emptiness ** sigma)))
        trace[wk] = {
            "flow_arena": round(flow_arena, 1), "stock": round(stock, 1),
            "B": round(abundance, 3), "S": round(emptiness, 3), "G": round(gain, 3),
        }

        # 3) 逐 agent 装配 feed（曝光现算现记账）+ 数值决策。
        live = [it for it in pool if not mech.is_retired(it["life"], LIFE_RETIRE_FLOOR)]
        # 强制位①官方置顶：is_official 注入帖当周置顶（env：official_pin_extend_weeks=0 → 仅当周）。
        pinned = [it for it in live if it.get("official") and it["week"] == wk]
        # 强制位②议程保底：事件周取全池（未退场、非置顶、非语料噪声）哀悼倾向分最高的 N 条，
        # 全员相同。候选资格与 env 同源（mech.floor_eligible，用户 2026-09-13 补裁定·方案 B）。
        forced: list[dict] = []
        if w13_floor > 0 and wk == EVENT_WEEK:
            _pin_ids = {id(x) for x in pinned}
            forced = sorted(
                (it for it in live
                 if id(it) not in _pin_ids and mech.floor_eligible(it.get("type", ""))),
                key=lambda it: -it["tend"].get("mourning", 0.0),
            )[:w13_floor]
        trace[wk]["pinned"], trace[wk]["forced"] = len(pinned), len(forced)
        head = pinned + forced
        head_ids = {id(x) for x in head}

        counts = {t: 0 for t in TYPE_ORDER}
        share_by_type: dict[str, list[float]] = {t: [] for t in TYPE_ORDER}
        agent_posts: list[dict] = []
        for ag in population:
            t = ag["agent_type"]
            prm = ag["params"]
            scored = [
                (mech.interest_score(it["tend"].get(t, 0.0), 1.0, 0.5,
                                     mech.post_vitality(it["life"], it["exposure"],
                                                        saturation)), it)
                for it in live if id(it) not in head_ids
            ]
            # 平票次序按入池序号（env 同构：`scored.sort(key=lambda x: (-x[0], -x[1]))` 用 pid）。
            # 不可用 id()：内存地址每次运行都变，会让同一 seed 的结果不可复现。
            scored.sort(key=lambda x: (-x[0], x[1]["seq"]))
            picks = head + mech.weighted_sample_without_replacement(
                [it for _, it in scored],
                mech.softmax_weights([s for s, _ in scored], temp),
                max(0, FEED_SIZE - len(head)), rng,
            )
            own = 0
            for it in picks:
                it["exposure"] += 1
                if it["type"] == t:
                    own += 1
            share_own = own / len(picks) if picks else 0.0   # env 同口径：分母 = 实际 feed 槽位数
            share_by_type[t].append(share_own)

            base_share = personas_mod.POP_SHARE[t]
            # D 走共享纯函数（与 agent 侧同一份实现）：有界 tanh、无地板（2026-09-12 裁定）
            effective_spiral_scale = (
                float(spiral_mult) if spiral_mult is not None
                else float(prm.get("spiral_scale", 1.0))
            )
            d = mech.spiral_factor(share_own, base_share,
                                   prm["spiral"] * effective_spiral_scale)
            r = mech.fatigue_factor(prm["decay"] * decay_mult, cum_own[ag["id"]])   # 与 agent 同一份实现
            if utility_mode == "multiplicative":
                u = d * r                 # U = D·R（环境因子 G 已退役，gain 仅供 trace 记录）
            elif utility_mode == "anchored":
                baseline_map = baseline_utility or personas_mod.BASELINE_UTILITY
                b = baseline_map.get(str(ag["id"]),
                                     baseline_map.get(t, prm.get("baseline_utility")))
                if b is None:
                    raise ValueError(f"missing baseline utility for agent={ag['id']} type={t}")
                u = mech.anchored_utility(float(b), d, r)
            else:
                raise ValueError(f"unknown utility_mode: {utility_mode!r}")
            if u >= prm["activity"] * base / BASE_REF:
                counts[t] += 1
                agent_posts.append({"seq": _seq, "week": wk, "type": t,
                                    "tend": dict(AGENT_TENDENCY_PROFILE[t]),
                                    "life": 1.0, "exposure": 0})
                _seq += 1
            cum_own[ag["id"]] += own

        # 4) 本 tick 产出的 agent 帖滞后 1 tick 入池（下一周才可见）。
        pool.extend(agent_posts)

        climates[wk] = {t: (sum(v) / len(v) if v else 0.0) for t, v in share_by_type.items()}
        climates[wk + "_sd"] = {t: (statistics_pstdev(v) if v else 0.0)
                                for t, v in share_by_type.items()}
        result[wk] = counts
        prev_speak = float(sum(counts.values()))
    return result, trace, climates


def statistics_pstdev(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = sum(vals) / len(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))


def summarize(label: str, res: dict, trace: dict | None = None, climates: dict | None = None) -> None:
    totals = {t: sum(res[wk][t] for wk in WEEKS) for t in TYPE_ORDER}
    grand = sum(totals.values())
    print(f"\n-- {label}：总发言 {grand} 帖/run（agent 供给 {grand / (grand + 250):.0%} > 注入 250）--")
    if trace is not None:
        print("环境轨迹   | " + " | ".join(f"{w[-3:]:>7}" for w in WEEKS))
        for key, name in (("stock", "Stock"), ("B", "B"), ("S", "S"), ("G", "G")):
            cells = " | ".join(f"{trace[wk][key]:>7.2f}" for wk in WEEKS)
            print(f"{name:<10} | {cells}")
    if climates is not None:
        print("气候 share_own（均值/逐agent sd，D 因子的实际输入）")
        print("类型       | " + " | ".join(f"{w[-3:]:>13}" for w in WEEKS))
        for t in TYPE_ORDER:
            cells = " | ".join(
                f"{climates[w][t]:>6.2f}/{climates[w + '_sd'][t]:>5.2f}" for w in WEEKS
            )
            print(f"{t:<10} | {cells}")
    print("周        |  合计 | " + " | ".join(f"{t:>9}" for t in TYPE_ORDER))
    for wk in WEEKS:
        cells = " | ".join(f"{res[wk][t]:>9}" for t in TYPE_ORDER)
        print(f"{wk} | {sum(res[wk].values()):>5} | {cells}")
    meme_late = sum(res[wk]["meme"] for wk in ("2026-W20", "2026-W21", "2026-W22"))
    meme_onset = sum(res[wk]["meme"] for wk in ("2026-W18", "2026-W19"))
    mourn_early = sum(res[wk]["mourning"] for wk in ("2026-W13", "2026-W14", "2026-W15"))
    print(f"要点：W13-W15 悼念 {mourn_early} 帖；W18-W19 玩梗起步 {meme_onset} 帖；"
          f"W20-22 玩梗 {meme_late} 帖；W12 合计 {sum(res['2026-W12'].values())} 帖")


# ---------------------------------------------------------------------------
# 同构断言：用 replay 记录的供给计数复算 B/S/G，与 replay 记录值逐值比对
# ---------------------------------------------------------------------------
def assert_emergence_isomorphic(run_dir: Path, tol: float = 1e-4) -> bool:
    """校验"校准脚本的涌现环境公式 == env 实现"。

    做法：读 runs/<id>/replay/curation_dynamics_env_state.*.jsonl 的逐周
    (injected_count, agent_supply, meme_env_flow_world)，用本脚本的公式复算 B/S/G，
    与 replay 记录的 meme_env_abundance / meme_env_emptiness / meme_env_gain 逐值比对。
    只依赖供给计数（与内容/行为无关），因此不受推演差异影响，能直接暴露公式漂移。

    口径要点：env 的当周 arena 流量 = 当周注入 + **上一周**收尾并入的 agent 帖
    （`_compute_meme_env` 用 `_agent_posts_pooled_prev`），故复算需取前一周的 agent_supply。
    容差：replay 落盘的 B/S/G 保留 4 位小数，故用 1e-4（> 半个末位）而非 1e-6。
    """
    files = sorted((run_dir / "replay").glob("curation_dynamics_env_state.*.jsonl"))
    if not files:
        print(f"✗ 同构断言失败：{run_dir}/replay 下无 curation_dynamics_env_state.*.jsonl")
        return False
    rows = []
    for fp in files:
        for line in fp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows.sort(key=lambda r: r.get("step", 0))
    if not rows:
        print("✗ 同构断言失败：replay 无数据行")
        return False

    flow_hist: dict[str, float] = {}
    prev_agent_supply = 0.0
    bad = 0
    for r in rows:
        wk = str(r["week"])
        flow_hist[wk] = float(r["injected_count"]) + prev_agent_supply
        prev_agent_supply = float(r["agent_supply"])
        i = WEEKS.index(wk)
        stock = sum(flow_hist[w] for w in WEEKS[max(0, i - STOCK_WINDOW + 1): i + 1])
        stock_base = flow_hist[START_WEEK]
        b = (stock / (stock + K_A_DEFAULT)) / (stock_base / (stock_base + K_A_DEFAULT))
        s = ((K_F_DEFAULT / (K_F_DEFAULT + FLOW_WORLD[wk]))
             / (K_F_DEFAULT / (K_F_DEFAULT + FLOW_WORLD[START_WEEK])))
        g = max(GAIN_MIN, min(GAIN_MAX, b * s))
        for name, got, exp in (("B", b, r["meme_env_abundance"]),
                               ("S", s, r["meme_env_emptiness"]),
                               ("G", g, r["meme_env_gain"])):
            if abs(got - float(exp)) > tol:
                bad += 1
                print(f"✗ {wk} {name}: 复算 {got:.10f} != replay {float(exp):.10f}")
    if bad:
        print(f"✗ 同构断言失败：{bad} 个值不一致（容差 {tol:g}）")
        return False
    print(f"✓ 同构断言通过：{len(rows)} 周 B/S/G 与 replay 逐值一致（容差 {tol:g}）")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="activity_base 快速校准（feed 层同构推演）")
    ap.add_argument("--assert-replay", type=Path, default=None,
                    help="给定 run 目录，先做涌现环境公式同构断言再继续（如 hypothesis_4/experiment_1/runs/interest_normal_s0）")
    ap.add_argument("--bases", type=float, nargs="*", default=CANDIDATE_BASES,
                    help="待扫的门槛基数（默认 1.0/0.95/0.9/0.85/0.8/0.7）")
    args = ap.parse_args()

    if args.assert_replay is not None and not assert_emergence_isomorphic(args.assert_replay):
        raise SystemExit(1)

    shares = typed_shares()

    print("== 输入代理 ==")
    print("周        | 注入 | 现实口径流量（S 调度） | 真实口径本类份额（对照，非气候输入）")
    for wk in WEEKS:
        print(f"{wk} | {INJ_ALLOC[wk]:>4} | {FLOW_WORLD[wk]:>21} | "
              + " ".join(f"{t[:4]}={shares[wk][t]:.2f}" for t in TYPE_ORDER))
    print(f"env 默认：K_a={K_A_DEFAULT}（注入计划事件周窗口存量）、K_f={K_F_DEFAULT}"
          f"（调度基线周值）、窗口={STOCK_WINDOW} 周、G clamp[{GAIN_MIN},{GAIN_MAX}]、β=σ=1")
    print(f"feed 机制：half_life={LIFE_HALF_LIFE_WEEKS} 周、饱和尺度={LIFE_SATURATION_SCALE}、"
          f"退场线={LIFE_RETIRE_FLOOR}、抽样温度={INTEREST_SAMPLE_TEMP}、"
          f"抽样流 Random({CALIB_SAMPLE_SEED})、注入样本={INJECTION_SAMPLE_PATH.name}")

    for mode, label in (("normal", "涌现臂 normal"), ("sustained_hot", "反事实臂 sustained_hot（W13 后冻结 S）")):
        print(f"\n===== {label} =====")
        for base in args.bases:
            res, trace, climates = simulate(base, mode)
            summarize(f"门槛基数 base={base:.2f}", res, trace, climates)

    print("\n===== OAT 敏感性（base=0.95，其余参数保持默认）=====")
    print("参数           | 取值  | normal 总/玩梗起步W18-19/玩梗W20-22/悼念W13-15 | sustained_hot 同口径")
    base = 0.95
    for label, key, grid in (
        ("K_a 倍率", "ka", [0.5, 1.0, 2.0]),
        ("K_f 倍率", "kf", [0.5, 1.0, 2.0]),
        ("β", "beta", [0.5, 1.0, 1.5]),
        ("σ", "sigma", [0.5, 1.0, 1.5]),
        ("抽样温度", "temp", [2.0, 4.0, 8.0]),
        ("半衰期(周)", "half", [1.0, 1.5, 3.0]),
    ):
        for v in grid:
            if key == "temp":
                res_n = simulate(base, "normal", temp=v)[0]
                res_s = simulate(base, "sustained_hot", temp=v)[0]
            elif key == "half":
                res_n = simulate(base, "normal", half_life=v)[0]
                res_s = simulate(base, "sustained_hot", half_life=v)[0]
            else:
                defaults = {"ka": K_A_DEFAULT, "kf": K_F_DEFAULT, "beta": 1.0, "sigma": 1.0}
                kw = dict(defaults)
                kw[key] = v * K_A_DEFAULT if key == "ka" else v * K_F_DEFAULT if key == "kf" else v
                res_n = simulate(base, "normal", **kw)[0]
                res_s = simulate(base, "sustained_hot", **kw)[0]

            def fmt(res: dict) -> str:
                g = sum(sum(res[wk].values()) for wk in WEEKS)
                mo = sum(res[wk]["meme"] for wk in ("2026-W18", "2026-W19"))
                ml = sum(res[wk]["meme"] for wk in ("2026-W20", "2026-W21", "2026-W22"))
                me = sum(res[wk]["mourning"] for wk in ("2026-W13", "2026-W14", "2026-W15"))
                return f"{g:>4}/{mo:>3}/{ml:>3}/{me:>3}"

            print(f"{label:<14} | {v:<5g} | {fmt(res_n)} | {fmt(res_s)}")


if __name__ == "__main__":
    main()
