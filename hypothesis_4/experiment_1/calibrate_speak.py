"""表达效用模型门槛基数（activity_base）快速校准（2026-09-10 裁定方案 B 后重扫）。

方法论与线性规则校准（EXPERIMENT.md 历史记录）一致，仅把决策规则换成表达效用模型：

- 真实周构成气候代理：benchmark_curves.json weekly_category_matrix（剔除「爬取噪音」），
  agent 所见本类占比 share_own(w) = 真实当周本类内容份额。
- P_t(w) = min(0.7, 0.4·M_t(w) + 0.3·V(w))，V(w) = total(w)/total(W13)（均剔除噪音；
  与 env 实现同式，w_official=0 无官方项）。
- 群体：curation_personas.build_population(POPULATION_COUNTS, seed=42)，与 18 runs 一致。
- 累计曝光代理：cum_own(w) += feed_size × share_own(w)（期望本类曝光；feed_size=10）。
- 决策：U = D·R − c·v·P_t，发言当且仅当 U ≥ activity_i（确定性，无随机数）。
- sustained 臂：P_t 冻结在 W13 峰值（与 env 的 mourning_norm_pressure=sustained 一致）。
- 扫描门槛基数：个体门槛按基数等比例缩放 activity_i(base) = activity_i(0.95)·base/0.95，
  保持 U[0.8,1.2] 个体抖动结构不变。

选点标准：期望总发言 ≈300-350 帖/run（agent 供给占比 ~55-58% > 注入 250），
且形态合理（W13 悼念冲击、玩梗 W20-22 回潮、营销/教育稳定供给）。
本脚本零副作用，只读文件并打印；定标结果由人工裁定后写入 personas/agent/文档。
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

FEED_SIZE = 10          # 用户 2026-09-10 裁定：每 agent 每周 10 条信息流
BASE_REF = 0.95         # personas 当前门槛基数（缩放锚点）
CANDIDATE_BASES = [1.0, 0.95, 0.9, 0.85, 0.8, 0.7]
NORM_COST_C = 1.0       # 规范成本全局尺度（与 agent 实现一致）
P_T_CAP = 0.7
W_MOURNING = 0.4
W_VOLUME = 0.3
WEEKS = [f"2026-W{i}" for i in range(12, 23)]
EVENT_WEEK = "2026-W13"

TYPE_KEYS = {  # benchmark 中文键 → agent 类型
    "梗文化讨论": "meme",
    "事件悼念讨论": "mourning",
    "借势营销": "marketing",
    "教育观点讨论": "education",
    "其他讨论": "other",
}
TYPE_ORDER = ["meme", "mourning", "marketing", "education", "other"]

spec = importlib.util.spec_from_file_location("curation_personas", personas_path)
personas_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personas_mod)

POPULATION_COUNTS = {"meme": 18, "mourning": 21, "marketing": 26, "education": 15, "other": 20}
population = personas_mod.build_population(POPULATION_COUNTS, seed=42)


def weekly_composition() -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """返回 (各周各类型真实份额[剔除噪音], 各周 P_t)。"""
    bench = json.loads(benchmark_path.read_text(encoding="utf-8"))
    matrix = bench["weekly_category_matrix"]
    shares: dict[str, dict[str, float]] = {}
    p_t: dict[str, float] = {}
    total_event = None
    for wk in WEEKS:
        row = matrix[wk]
        typed = {t: float(row.get(cn, 0) or 0) for cn, t in TYPE_KEYS.items()}
        total = sum(typed.values())
        sh = {t: (typed[t] / total if total > 0 else 0.0) for t in TYPE_ORDER}
        shares[wk] = sh
        if wk == EVENT_WEEK:
            total_event = total
    for wk in WEEKS:
        row = matrix[wk]
        typed = {t: float(row.get(cn, 0) or 0) for cn, t in TYPE_KEYS.items()}
        total = sum(typed.values())
        v_ratio = (total / total_event) if total_event else 0.0
        p_t[wk] = min(P_T_CAP, W_MOURNING * shares[wk]["mourning"] + W_VOLUME * v_ratio)
    return shares, p_t


def simulate(base: float, shares: dict, p_t_sched: dict[str, float]) -> dict[str, dict[str, int]]:
    """给定门槛基数与 P_t 调度，代理推演 11 周，返回 {week: {type: 发言数}}。"""
    cum_own = {p["id"]: 0.0 for p in population}
    result: dict[str, dict[str, int]] = {}
    for wk in WEEKS:
        counts = {t: 0 for t in TYPE_ORDER}
        sh = shares[wk]
        p_t = p_t_sched[wk]
        for ag in population:
            t = ag["agent_type"]
            prm = ag["params"]
            base_share = personas_mod.POP_SHARE[t]
            d = 1.0 + prm["spiral"] * (sh[t] - base_share) / max(base_share, 0.05)
            d = max(0.05, min(2.0, d))
            r = math.exp(-prm["decay"] * cum_own[ag["id"]] / 50.0)
            benefit = d * r
            cost = NORM_COST_C * prm["norm_dev"] * p_t
            activity_i = prm["activity"] * base / BASE_REF
            if benefit - cost >= activity_i:
                counts[t] += 1
            cum_own[ag["id"]] += FEED_SIZE * sh[t]
        result[wk] = counts
    return result


def main() -> None:
    shares, p_t_decay = weekly_composition()
    p_t_sustained = {wk: p_t_decay[EVENT_WEEK] for wk in WEEKS}

    print("== 真实周构成气候代理（剔除爬取噪音）==")
    print("周        | " + " | ".join(f"{t:>9}" for t in TYPE_ORDER) + " |   P_t")
    for wk in WEEKS:
        cells = " | ".join(f"{shares[wk][t]:>8.1%}" for t in TYPE_ORDER)
        print(f"{wk} | {cells} | {p_t_decay[wk]:.3f}")

    for label, sched in (("decay", p_t_decay), ("sustained(P_t 冻结 W13 峰值)", p_t_sustained)):
        print(f"\n===== 压力臂：{label} =====")
        for base in CANDIDATE_BASES:
            res = simulate(base, shares, sched)
            totals = {t: sum(res[wk][t] for wk in WEEKS) for t in TYPE_ORDER}
            grand = sum(totals.values())
            print(f"\n-- 门槛基数 base={base:.2f}：总发言 {grand} 帖/run"
                  f"（agent 供给 {grand / (grand + 250):.0%}）--")
            print("周        |  合计 | " + " | ".join(f"{t:>9}" for t in TYPE_ORDER))
            for wk in WEEKS:
                cells = " | ".join(f"{res[wk][t]:>9}" for t in TYPE_ORDER)
                print(f"{wk} | {sum(res[wk].values()):>5} | {cells}")
            meme_late = sum(res[wk]["meme"] for wk in ("2026-W20", "2026-W21", "2026-W22"))
            mourn_early = sum(res[wk]["mourning"] for wk in ("2026-W13", "2026-W14", "2026-W15"))
            print(f"要点：W13-W15 悼念 {mourn_early} 帖；W20-22 玩梗 {meme_late} 帖；"
                  f"W12 合计 {sum(res['2026-W12'].values())} 帖")


if __name__ == "__main__":
    main()
