#!/usr/bin/env python3
"""proxy_predict: 用同构代理预测「各类 agent 周发帖数」并出图（只读，不跑 LLM）。

用途（用户 2026-09-12 要求）：在跑真实 run 之前，判断 R=20 之后各类 agent 的发帖趋势
能否说得过去。做法：复用 calibrate_speak.py 的模块级对象（真实 250 条注入样本、真实 100 人
群体）与 curation_mechanisms 的共享纯函数（与 env 同一套 feed 生命周期/曝光饱和/退场/抽样、
同一套 D 与 R），只把 LLM 内容生成换成实测倾向分画像——即"同构代理"。

跑 N 个 seed（只换 feed 抽样随机流）→ 逐周取均值/sd → 出双面板图：
  面板 A：各类 agent 周发帖数（堆叠面积，均值）—— 看退潮是否合理、玩梗起爆是否突兀；
  面板 B：各类构成份额 模拟 vs 真实基准（实线=模拟、虚线=真实）—— 效标是构成份额，不是绝对量。

已知偏差（图上会体现，判断时需扣除）：
  ① 议程设置：`--w13-floor N`（默认 5）让 W13 每个 agent 的 feed 保底含 N 条哀悼帖
     （按哀悼倾向分取全池前 N 条、全员相同），用于复现"讣告强制曝光"；设 0 可关闭（此时会低估悼念峰）；
  ② 营销 λ=0.05（2026-09-12 由 0.1 下调，"几乎不疲劳但热点凉了会换赛道"）；
  ③ 代理起爆略早于真实 run（形态用相对比较，绝对值以真实 run 为准）。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/proxy_predict.py            # 30 seed，出图 + CSV
    $PYTHON_PATH hypothesis_4/experiment_1/proxy_predict.py --seeds 50
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import statistics
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cal = _load("calibrate_speak", SCRIPT_DIR / "calibrate_speak.py")
pltmod = _load("plot_run_charts", SCRIPT_DIR / "plot_run_charts.py")
mech = cal.mech
W = cal.WEEKS
POP = cal.population
INJ = cal.INJECTED_BY_WEEK
BENCH = json.loads((ROOT / "hypothesis_4" / "benchmark_curves.json").read_text(encoding="utf-8"))[
    "weekly_category_matrix"
]

TYPE_ORDER = ("meme", "mourning", "education", "marketing", "other")
TYPE_LABEL = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
              "marketing": "营销", "other": "其他"}
TYPE_COLOR = pltmod.TYPE_COLOR
N_AGENTS = {"meme": 19, "mourning": 22, "marketing": 23, "education": 15, "other": 21}
BENCH_CN = {"meme": "梗文化讨论", "mourning": "事件悼念讨论", "education": "教育观点讨论",
            "marketing": "借势营销", "other": "其他讨论"}


EVENT_WEEK = "2026-W13"


def simulate(seed: int, base: float = 0.95, r_scale: float = 20.0,
             w13_mourning_floor: int = 5) -> dict[str, dict[str, int]]:
    """interest 臂一轮推演（与 calibrate_speak.simulate 同构）。

    r_scale：注意力衰减半饱和尺度（越小 R 越强；共享模块默认 20）。
    w13_mourning_floor：议程设置——事件周（W13）每个 agent 的 feed 保底包含 N 条
    哀悼帖（按哀悼倾向分取全池前 N 条，全员相同，等效"讣告 + 头版哀悼"的强制曝光）；
    N<=0 表示关闭。占用槽位后其余槽位照常按兴趣抽样（不与保底帖重复）。
    """
    rng = random.Random(seed + 3000)
    cum = {p["id"]: 0.0 for p in POP}
    pool: list[dict] = []
    res: dict[str, dict[str, int]] = {}
    for wk in W:
        step = mech.weekly_decay(cal.LIFE_HALF_LIFE_WEEKS)
        for it in pool:
            it["life"] *= step
        for rec in INJ[wk]:
            pool.append({"week": wk, "type": rec["type"], "tend": dict(rec["tend"]),
                         "life": 1.0, "exposure": 0})
        live = [it for it in pool if not mech.is_retired(it["life"], cal.LIFE_RETIRE_FLOOR)]
        cnt = {t: 0 for t in TYPE_ORDER}
        posts: list[dict] = []
        for ag in POP:
            t = ag["agent_type"]
            prm = ag["params"]
            scored = sorted(
                ((mech.interest_score(it["tend"].get(t, 0.0), 1.0, 0.5,
                                      mech.post_vitality(it["life"], it["exposure"],
                                                         cal.LIFE_SATURATION_SCALE)), it)
                 for it in live),
                key=lambda x: (-x[0], id(x[1])),
            )
            forced: list[dict] = []
            if wk == EVENT_WEEK and w13_mourning_floor > 0:
                top = sorted(
                    live,
                    key=lambda it: (-(it["tend"].get("mourning", 0.0)), id(it)),
                )[:w13_mourning_floor]
                forced = top
                forced_ids = {id(x) for x in forced}
                scored = [(s0, it) for s0, it in scored if id(it) not in forced_ids]
            picks = forced + mech.weighted_sample_without_replacement(
                [it for _, it in scored],
                mech.softmax_weights([s0 for s0, _ in scored], cal.INTEREST_SAMPLE_TEMP),
                10 - len(forced), rng,
            )
            own = sum(1 for it in picks if it["type"] == t)
            for it in picks:
                it["exposure"] += 1
            u = mech.spiral_factor(own / 10, cal.personas_mod.POP_SHARE[t], prm["spiral"]) * \
                mech.fatigue_factor(prm["decay"], cum[ag["id"]], r_scale)
            if u >= prm["activity"] * base / 0.95:
                cnt[t] += 1
                posts.append({"week": wk, "type": t,
                              "tend": dict(cal.AGENT_TENDENCY_PROFILE[t]),
                              "life": 1.0, "exposure": 0})
            cum[ag["id"]] += own
        pool.extend(posts)
        res[wk] = cnt
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="同构代理预测：各类 agent 周发帖数（只读）")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="PROXY_pred_agent_supply_by_type.png")
    ap.add_argument("--r-scale", type=float, default=20.0, help="R 半饱和尺度（越小 R 越强）")
    ap.add_argument("--w13-floor", type=int, default=5,
                    help="议程设置：W13 每 agent feed 保底哀悼帖条数（0=关闭）")
    args = ap.parse_args()

    runs = [simulate(sd, r_scale=args.r_scale, w13_mourning_floor=args.w13_floor)
            for sd in range(args.seeds)]
    mean = {t: {w: statistics.mean(r[w][t] for r in runs) for w in W} for t in TYPE_ORDER}
    sd_ = {t: {w: statistics.pstdev(r[w][t] for r in runs) for w in W} for t in TYPE_ORDER}
    tot = [sum(mean[t][w] for t in TYPE_ORDER) for w in W]

    # ---------- CSV ----------
    csv_path = SCRIPT_DIR / "data" / "proxy_pred_agent_supply.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        wtr = csv.writer(f)
        wtr.writerow(["week"] + [f"{t}_mean" for t in TYPE_ORDER]
                     + [f"{t}_sd" for t in TYPE_ORDER] + ["total_mean"])
        for i, w in enumerate(W):
            wtr.writerow([w] + [round(mean[t][w], 3) for t in TYPE_ORDER]
                         + [round(sd_[t][w], 3) for t in TYPE_ORDER] + [round(tot[i], 3)])

    # ---------- 判据打印 ----------
    real_share = {w: {t: BENCH[w].get(BENCH_CN[t], 0) / BENCH[w]["total"] for t in TYPE_ORDER}
                  for w in W}
    sim_share = {w: {t: (mean[t][w] / tot[W.index(w)] if tot[W.index(w)] else 0.0)
                     for t in TYPE_ORDER} for w in W}
    print(f"\n=== 判据 1：构成份额与真实的绝对差（{args.seeds} seed 均值，agent 产出口径）===")
    print(f"{'类型':<10}{'平均|差|':>10}{'最大|差|':>10}{'最大差所在周':>14}")
    for t in TYPE_ORDER:
        diffs = [(abs(sim_share[w][t] - real_share[w][t]), w) for w in W]
        mx = max(diffs)
        print(f"{TYPE_LABEL[t]:<10}{statistics.mean(d for d, _ in diffs):>10.3f}{mx[0]:>10.3f}{mx[1]:>14}")
    i13 = W.index("2026-W13")
    print(f"\n=== 判据 2：注册判据预测 ===")
    _m13s, _m13r = sim_share['2026-W13']['mourning'], real_share['2026-W13']['mourning']
    print(f"  W13 悼念份额：真实 {_m13r:.3f} vs 代理 {_m13s:.3f} → 差 {_m13s-_m13r:+.3f}"
          f"（判据 ±0.08 → {'✅' if abs(_m13s-_m13r)<=0.08 else '❌'}）"
          f"{'［保底已关闭，会低估］' if args.w13_floor<=0 else ''}")
    sh = [sim_share[f"2026-W{i}"]["meme"] for i in (19, 20, 21, 22)]
    rh = [real_share[f"2026-W{i}"]["meme"] for i in (19, 20, 21, 22)]
    print(f"  玩梗二波 W19-22：模拟 " + "/".join(f"{x:.3f}" for x in sh)
          + " vs 真实 " + "/".join(f"{x:.3f}" for x in rh))
    print(f"  起爆段倍数（W20→W22）：模拟 ×{sh[3]/max(sh[1],1e-9):.1f} vs 真实 ×{rh[3]/max(rh[1],1e-9):.1f}"
          f"（W19 代理为 0，故不参与比值）")
    print(f"\n=== 判据 3：各类峰值周与参与率轨迹（峰值周 / W13 / W18 / W22 参与率）===")
    for t in TYPE_ORDER:
        vals = [mean[t][w] for w in W]
        pk = W[vals.index(max(vals))]
        r = lambda w: mean[t][w] / N_AGENTS[t]
        print(f"  {TYPE_LABEL[t]:<6} 峰值周 {pk}（{max(vals):.1f} 帖）| 参与率 "
              f"W13 {r('2026-W13'):.2f} → W18 {r('2026-W18'):.2f} → W22 {r('2026-W22'):.2f}")

    # ---------- 出图 ----------
    plt = pltmod.plt
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(15, 5.6))
    # 面板 A：堆叠面积
    x = list(range(len(W)))
    axA.stackplot(x, *[ [mean[t][w] for w in W] for t in TYPE_ORDER ],
                  labels=[TYPE_LABEL[t] for t in TYPE_ORDER],
                  colors=[TYPE_COLOR[t] for t in TYPE_ORDER], alpha=0.92, linewidth=0.6,
                  edgecolor="white")
    pltmod._death_line(axA, W)
    axA.set_xticks(x, W, rotation=45)
    axA.set_ylabel("Agent 周发帖数（帖，堆叠）")
    _floor_note = f"，W13 保底 {args.w13_floor} 条哀悼帖" if args.w13_floor > 0 else ""
    axA.set_title(f"代理预测 · 各类 Agent 周发帖数（{args.seeds} seed 均值，"
                  f"R 尺度 {args.r_scale:g}{_floor_note}）",
                  fontweight="bold", fontsize=12)
    axA.legend(loc="upper right", frameon=False, fontsize=9)
    axA.set_axisbelow(True)
    # 面板 B：构成份额 模拟 vs 真实
    for t in TYPE_ORDER:
        axB.plot(x, [sim_share[w][t] for w in W], color=TYPE_COLOR[t], linewidth=2.4,
                 marker="o", markersize=4, label=f"{TYPE_LABEL[t]}（模拟）")
        axB.plot(x, [real_share[w][t] for w in W], color=TYPE_COLOR[t], linewidth=1.4,
                 linestyle="--", alpha=0.75, marker="s", markersize=3,
                 label=f"{TYPE_LABEL[t]}（真实）")
    pltmod._death_line(axB, W)
    axB.set_xticks(x, W, rotation=45)
    axB.yaxis.set_major_formatter(pltmod.PercentFormatter(1.0))
    axB.set_ylabel("周构成份额（agent 产出口径）")
    axB.set_title("代理预测 · 构成份额 模拟（实线）vs 真实（虚线）",
                  fontweight="bold", fontsize=12)
    axB.legend(loc="lower right", frameon=False, fontsize=8, ncol=2,
               bbox_to_anchor=(1.0, 0.02))
    axB.set_axisbelow(True)
    fig.tight_layout()
    out = SCRIPT_DIR / "charts" / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"\n✓ 图  {out.relative_to(SCRIPT_DIR)}")
    print(f"✓ CSV {csv_path.relative_to(SCRIPT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
