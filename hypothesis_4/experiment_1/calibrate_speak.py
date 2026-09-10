"""玩梗涌现环境门槛基数（activity_base）快速校准（2026-09-10 机制重设计后重写）。

方法论：与旧表达效用校准同框架（确定性决策、无随机数、真实数据代理），
环境项 P_t 替换为玩梗涌现增益 G_t，且环境-行为反馈与 env 实现**同构、完全内生化**：

- S_t（流量空旷度）：env 读外生现实口径周新增调度（config_params.EMERGENCE_FLOW_BY_WEEK，
  = injection_posts.json 各周全量帖数；sim arena 流量被 250 条注入预算压缩——保底 15/周
  托底谷值、洪峰仅 ~2×、agent 供给又平稳 → 峰谷比 ~1.6× vs 现实 ~9×，表达不出真实
  洪峰/退潮节律，故 S 读现实口径），S_t = h(Flow_w)/h(Flow_base)，h(x)=K_f/(K_f+x)，
  K_f = 调度基线周值（W12）→ 基线周 S=1。sustained_hot 反事实臂：事件周（W13）记录
  S，之后冻结（B 保持内生）。
- B_t（存量丰沛度）：env 内生——Stock_t = 过去 6 周 arena 供给总数（当周注入 + 上一周
  agent 发言；agent 帖滞后 1 tick 入池，与 env 的 step(k) 关池→_open_tick(k+1) 时机
  一致），B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)，K_a = 注入计划事件周窗口
  存量（W12+W13 注入 = 17+35 = 52，env 默认），Stock_base = W12 arena 流量（17）
  → 基线周 B=1。B 不因 sustained 臂冻结（meme 再拥挤反哺存量的自限反馈保留）。
- G_t = clamp(B_t^β · S_t^σ, 0.2, 3.0)，β=σ=1（env 默认起步值）。
- 气候代理（沉默螺旋 D 因子输入）：benchmark_curves.json weekly_category_matrix
  剔除「爬取噪音」的本类内容份额。
- 累计曝光代理：cum_own(w) += feed_size × share_own(w)（期望本类曝光；feed_size=10）。
- 决策：U = D·R·G^θ，发言当且仅当 U ≥ activity_i；θ = params["emergence"]
  （仅玩梗型 >0，其余类型 0 → G 不进入其效用）。D/R 公式与 agent 实现一致。
- 扫描门槛基数（个体门槛按基数等比例缩放，保持 U[0.8,1.2] 抖动结构），
  另做 OAT 敏感性：K_a/K_f 倍率、β、σ（其余保持默认）。

选点标准：agent 供给 ≈300-350 帖/run（>250 注入），形态合理（W13 悼念冲击、
玩梗 W20-22 回潮、营销/教育稳定供给）。本脚本零副作用，只读文件并打印；
定标结果由人工裁定后写入文档。
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

script_dir = Path(__file__).resolve().parent
workspace_root = script_dir.parent.parent
benchmark_path = workspace_root / "hypothesis_4" / "benchmark_curves.json"
personas_path = workspace_root / "custom" / "agents" / "curation_personas.py"
manifest_path = script_dir / "init" / "configs" / "manifest.json"

FEED_SIZE = 10          # 用户 2026-09-10 裁定：每 agent 每周 10 条信息流
BASE_REF = 0.95         # personas 当前门槛基数（缩放锚点）
CANDIDATE_BASES = [1.0, 0.95, 0.9, 0.85, 0.8, 0.7]
GAIN_MIN, GAIN_MAX = 0.2, 3.0
STOCK_WINDOW = 6        # env 默认 emergence_window_stock
DECAY_SCALE = 50.0      # agent 侧 _DECAY_SCALE

WEEKS = [f"2026-W{i}" for i in range(12, 23)]
START_WEEK = "2026-W12"
EVENT_WEEK = "2026-W13"

TYPE_KEYS = {  # benchmark 中文键 → agent 类型
    "梗文化讨论": "meme",
    "事件悼念讨论": "mourning",
    "借势营销": "marketing",
    "教育观点讨论": "education",
    "其他讨论": "other",
}
TYPE_ORDER = ["meme", "mourning", "marketing", "education", "other"]

# ---------------------------------------------------------------------------
# 输入：注入分配 + 现实口径流量调度（与 18 个配置同源：configs/manifest.json）
# ---------------------------------------------------------------------------
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
INJ_ALLOC: dict[str, int] = {str(k): int(v) for k, v in manifest["injection"]["allocation"].items()}
FLOW_WORLD: dict[str, int] = {str(k): int(v) for k, v in manifest["emergence_env"]["flow_schedule"].items()}
assert sorted(INJ_ALLOC) == sorted(FLOW_WORLD) == sorted(WEEKS), "manifest 周集合与 WEEKS 不一致"

K_F_DEFAULT = FLOW_WORLD[START_WEEK]                          # env 默认 emergence_kf（1246）
K_A_DEFAULT = INJ_ALLOC[START_WEEK] + INJ_ALLOC[EVENT_WEEK]   # env 默认 emergence_ka（17+35=52）
STOCK_BASE = INJ_ALLOC[START_WEEK]                            # W12 arena 流量（17，agent 帖滞后入池）

spec = importlib.util.spec_from_file_location("curation_personas", personas_path)
personas_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personas_mod)

POPULATION_COUNTS = {"meme": 18, "mourning": 21, "marketing": 26, "education": 15, "other": 20}
population = personas_mod.build_population(POPULATION_COUNTS, seed=42)


def typed_shares() -> dict[str, dict[str, float]]:
    """各周各类型真实内容份额（剔除爬取噪音；D 因子气候代理）。"""
    bench = json.loads(benchmark_path.read_text(encoding="utf-8"))
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
    shares: dict[str, dict[str, float]],
    ka: float = K_A_DEFAULT,
    kf: float = K_F_DEFAULT,
    beta: float = 1.0,
    sigma: float = 1.0,
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, float]]]:
    """端到端代理推演 11 周，返回 ({week: {type: 发言数}}, {week: 环境轨迹})。

    与 env 同构：agent 第 w 周发言在 w+1 周开池时并入 arena 流量（滞后 1 tick），
    Stock 以 6 周窗口滚动累计；S 读现实口径调度；sustained_hot 在事件周记录 S 并冻结。
    """
    cum_own = {p["id"]: 0.0 for p in population}
    flow_hist: dict[str, float] = {}
    prev_speak = 0.0            # 上一周 agent 发言总数（W11=0）
    result: dict[str, dict[str, int]] = {}
    trace: dict[str, dict[str, float]] = {}
    sustained_s: float | None = None
    flow_base = float(FLOW_WORLD[START_WEEK])   # 现实口径基线（env: flow_env_base）

    for wk in WEEKS:
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

        counts = {t: 0 for t in TYPE_ORDER}
        sh = shares[wk]
        for ag in population:
            t = ag["agent_type"]
            prm = ag["params"]
            base_share = personas_mod.POP_SHARE[t]
            d = 1.0 + prm["spiral"] * (sh[t] - base_share) / max(base_share, 0.05)
            d = max(0.05, min(2.0, d))
            r = math.exp(-prm["decay"] * cum_own[ag["id"]] / DECAY_SCALE)
            u = d * r * (gain ** prm["emergence"])
            if u >= prm["activity"] * base / BASE_REF:
                counts[t] += 1
            cum_own[ag["id"]] += FEED_SIZE * sh[t]
        result[wk] = counts
        prev_speak = float(sum(counts.values()))
    return result, trace


def summarize(label: str, res: dict, trace: dict | None = None) -> None:
    totals = {t: sum(res[wk][t] for wk in WEEKS) for t in TYPE_ORDER}
    grand = sum(totals.values())
    print(f"\n-- {label}：总发言 {grand} 帖/run（agent 供给 {grand / (grand + 250):.0%} > 注入 250）--")
    if trace is not None:
        print("环境轨迹   | " + " | ".join(f"{w[-3:]:>7}" for w in WEEKS))
        for key, name in (("stock", "Stock"), ("B", "B"), ("S", "S"), ("G", "G")):
            cells = " | ".join(f"{trace[wk][key]:>7.2f}" for wk in WEEKS)
            print(f"{name:<10} | {cells}")
    print("周        |  合计 | " + " | ".join(f"{t:>9}" for t in TYPE_ORDER))
    for wk in WEEKS:
        cells = " | ".join(f"{res[wk][t]:>9}" for t in TYPE_ORDER)
        print(f"{wk} | {sum(res[wk].values()):>5} | {cells}")
    meme_late = sum(res[wk]["meme"] for wk in ("2026-W20", "2026-W21", "2026-W22"))
    mourn_early = sum(res[wk]["mourning"] for wk in ("2026-W13", "2026-W14", "2026-W15"))
    print(f"要点：W13-W15 悼念 {mourn_early} 帖；W20-22 玩梗 {meme_late} 帖；"
          f"W12 合计 {sum(res['2026-W12'].values())} 帖")


def main() -> None:
    shares = typed_shares()

    print("== 输入代理 ==")
    print("周        | 注入 | 现实口径流量（S 调度）")
    for wk in WEEKS:
        print(f"{wk} | {INJ_ALLOC[wk]:>4} | {FLOW_WORLD[wk]}")
    print(f"env 默认：K_a={K_A_DEFAULT}（注入计划事件周窗口存量）、K_f={K_F_DEFAULT}"
          f"（调度基线周值）、窗口={STOCK_WINDOW} 周、G clamp[{GAIN_MIN},{GAIN_MAX}]、β=σ=1")

    for mode, label in (("normal", "涌现臂 normal"), ("sustained_hot", "反事实臂 sustained_hot（W13 后冻结 S）")):
        print(f"\n===== {label} =====")
        for base in CANDIDATE_BASES:
            res, trace = simulate(base, mode, shares)
            summarize(f"门槛基数 base={base:.2f}", res, trace)

    print("\n===== OAT 敏感性（base=0.95，其余参数保持默认）=====")
    print("参数           | 取值  | normal 总/玩梗W20-22/悼念W13-15 | sustained_hot 总/玩梗W20-22/悼念W13-15")
    base = 0.95
    for label, key, grid in (
        ("K_a 倍率", "ka", [0.5, 1.0, 2.0]),
        ("K_f 倍率", "kf", [0.5, 1.0, 2.0]),
        ("β", "beta", [0.5, 1.0, 1.5]),
        ("σ", "sigma", [0.5, 1.0, 1.5]),
    ):
        defaults = {"ka": K_A_DEFAULT, "kf": K_F_DEFAULT, "beta": 1.0, "sigma": 1.0}
        for v in grid:
            kw = dict(defaults)
            kw[key] = v * K_A_DEFAULT if key == "ka" else v * K_F_DEFAULT if key == "kf" else v
            res_n, _ = simulate(base, "normal", shares, **kw)
            res_s, _ = simulate(base, "sustained_hot", shares, **kw)

            def fmt(res: dict) -> str:
                g = sum(sum(res[wk].values()) for wk in WEEKS)
                ml = sum(res[wk]["meme"] for wk in ("2026-W20", "2026-W21", "2026-W22"))
                me = sum(res[wk]["mourning"] for wk in ("2026-W13", "2026-W14", "2026-W15"))
                return f"{g:>4}/{ml:>3}/{me:>3}"

            name = f"{label}={v:g}"
            print(f"{name:<14} | {v:>4g} | {fmt(res_n):>31} | {fmt(res_s):>35}")

    print("\n选点标准：agent 供给 ≈300-350 帖/run（>250 注入）；形态合理"
          "（W13 悼念冲击、玩梗 W20-22 回潮、营销/教育稳定供给、"
          "normal−sustained_hot 的玩梗尾部差可见）。")


if __name__ == "__main__":
    main()
