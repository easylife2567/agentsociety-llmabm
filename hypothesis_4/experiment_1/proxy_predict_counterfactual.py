#!/usr/bin/env python3
"""proxy_predict_counterfactual: 两机制（沉默螺旋 D / 注意力衰减 R）反事实的同构代理预测。

用途：正式 9-run 批跑已完成，下一步要做**机制反事实**。本脚本在跑真机反事实之前，
用与真机同构的代理先算出预测数据并出图——做法与 `proxy_predict.py` 完全一致
（**直接调用 calibrate_speak.simulate，单一实现**，只把 LLM 内容生成换成实测倾向分画像），
新增的只是两条机制的整体缩放开关 `spiral_mult` / `decay_mult`。

**反事实臂结构：2×2 消融**（用户 2026-09-13 要求）：挂在 interest 臂上（主臂）。

    cell          沉默螺旋 D      注意力衰减 R      U
    D1R1（基线）   开（s 原值）    开（λ 原值）      D·R   ← 即现有 interest_s{0,1,2}
    D0R1           关（s≡0）      开                R
    D1R0           开              关（λ≡0）         D
    D0R0           关              关                1（纯门槛）

置零是**精确消融**（`1+0·tanh ≡ 1`、`exp(−0·x) ≡ 1`），非近似档；真机反事实同构做法
= 把 profile 下发的 `params.spiral` / `params.decay` 整体乘同一倍数。

**两手准备（本脚本的两个产出）**：

1. **代理可信度校验**：基线 cell（D1R1）对**真机 interest 臂**（`data/arm/`，3 seed 均值）。
   正式跑已入库，这是以前做预测时没有的锚——若基线 cell 与真机吻合，则反事实的**差值**
   （本预测真正的用途）才可被信任。口径必须对齐：代理出的是 **agent 产出口径**，
   故真机侧取 `arm_weekly_by_type.mean_agent_supply` 现算份额，
   **不取** `arm_weekly_summary.meme_share`（那是 combined 口径，含注入帖，不可比）。
2. **反事实差值**：4 cell × N seed 的周度轨迹 + 主效应/交互项分解。

已知偏差（沿用 proxy_predict，判断时需扣除）：二波起爆相位略滞后；营销段系统性偏高。
另有本预测特有的一条：**代理没有 LLM 内容生成**，故反事实差值是"行为机制"的净效应，
真机里内容层的反馈（梗变体新鲜感等）会调制其幅度。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/proxy_predict_counterfactual.py          # 30 seed
    $PYTHON_PATH hypothesis_4/experiment_1/proxy_predict_counterfactual.py --seeds 50
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import statistics
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
# 出图分桶（2026-09-13 用户要求：烟测 / 预测 / 正式实验分开放）——本脚本产物全部落预测桶。
PRED_DIR = Path("charts") / "prediction" / "counterfactual_2mech"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cal = _load("calibrate_speak", SCRIPT_DIR / "calibrate_speak.py")
pltmod = _load("plot_run_charts", SCRIPT_DIR / "plot_run_charts.py")
mech = cal.mech
W = cal.WEEKS
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

# ---------------- 反事实 cell 定义 ----------------
# (spiral_mult, decay_mult, 短标签, 中文名, 画图色)
CELLS: list[tuple[float, float, str, str, str]] = [
    (1.0, 1.0, "D1R1", "基线（两机制全开）", "#222222"),
    (0.0, 1.0, "D0R1", "关沉默螺旋（s≡0）", "#1f77b4"),
    (1.0, 0.0, "D1R0", "关注意力衰减（λ≡0）", "#d62728"),
    (0.0, 0.0, "D0R0", "双关（U≡1 纯门槛）", "#9467bd"),
]
CELL_IDS = [c[2] for c in CELLS]


def simulate_cell(spiral_mult: float, decay_mult: float, seed: int,
                  r_scale: float = mech.DEFAULT_DECAY_SCALE,
                  w13_floor: int = cal.EVENT_WEEK_MOURNING_FLOOR) -> dict[str, dict[str, int]]:
    """一个反事实 cell 的一轮推演——**同一份 calibrate_speak.simulate**，只换两个缩放因子。

    其余全部同源：feed 生命周期/曝光饱和/退场、官方置顶 + 事件周议程保底、兴趣比例抽样、
    门槛 activity_base。rng_seed 偏移 +3000 与 proxy_predict / env 兴趣抽样流一致。
    """
    res, _trace, _climates = cal.simulate(
        cal.BASE_REF, "normal", r_scale=r_scale, w13_floor=w13_floor,
        rng_seed=seed + 3000, spiral_mult=spiral_mult, decay_mult=decay_mult,
    )
    return res


def load_real_arm_agent_shares(arm: str = "interest") -> tuple[dict, dict]:
    """真机臂级 **agent 产出口径**份额与逐类型周供给（来自 data/arm/arm_weekly_by_type.csv）。

    口径对齐关键：代理只产出 agent 帖，故真机侧也必须用 agent 口径现算份额，
    不能用 arm_weekly_summary.meme_share（combined 口径，含注入帖）。
    返回 (shares[week][type], supply[week][type])。
    """
    path = SCRIPT_DIR / "data" / "arm" / "arm_weekly_by_type.csv"
    supply: dict[str, dict[str, float]] = {w: {} for w in W}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["arm"] != arm or r["week"] not in supply:
                continue
            supply[r["week"]][r["type"]] = float(r["mean_agent_supply"])
    shares: dict[str, dict[str, float]] = {}
    for w in W:
        tot = sum(supply[w].get(t, 0.0) for t in TYPE_ORDER)
        shares[w] = {t: (supply[w].get(t, 0.0) / tot if tot > 0 else 0.0) for t in TYPE_ORDER}
    return shares, supply


def main() -> int:
    ap = argparse.ArgumentParser(description="两机制反事实的同构代理预测（只读）")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--prefix", default="PROXY_cf")
    ap.add_argument("--r-scale", type=float, default=mech.DEFAULT_DECAY_SCALE)
    ap.add_argument("--w13-floor", type=int, default=cal.EVENT_WEEK_MOURNING_FLOOR)
    args = ap.parse_args()

    # ---------- 推演 4 cell × N seed ----------
    raw: dict[str, list[dict[str, dict[str, int]]]] = {}
    for sm, dm, cid, _cn, _col in CELLS:
        raw[cid] = [simulate_cell(sm, dm, sd, args.r_scale, args.w13_floor)
                    for sd in range(args.seeds)]

    mean = {cid: {t: {w: statistics.mean(r[w][t] for r in raw[cid]) for w in W}
                  for t in TYPE_ORDER} for cid in CELL_IDS}
    sd_ = {cid: {t: {w: statistics.pstdev(r[w][t] for r in raw[cid]) for w in W}
                 for t in TYPE_ORDER} for cid in CELL_IDS}
    tot = {cid: [sum(mean[cid][t][w] for t in TYPE_ORDER) for w in W] for cid in CELL_IDS}
    sim_share = {cid: {w: {t: (mean[cid][t][w] / tot[cid][W.index(w)] if tot[cid][W.index(w)] else 0.0)
                           for t in TYPE_ORDER} for w in W} for cid in CELL_IDS}

    real_share, real_supply = load_real_arm_agent_shares("interest")
    bench_share = {w: {t: BENCH[w].get(BENCH_CN[t], 0) / BENCH[w]["total"] for t in TYPE_ORDER}
                   for w in W}

    # ---------- CSV ----------
    # 文件名跟随 --prefix：两套（30 seed / 100 seed 稳健性）各留一份，互不覆盖
    _sfx = args.prefix.replace("PROXY_cf", "")
    csv_path = SCRIPT_DIR / "data" / f"proxy_pred_counterfactual{_sfx}.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        wtr = csv.writer(f)
        wtr.writerow(["cell", "week"] + [f"{t}_mean" for t in TYPE_ORDER]
                     + [f"{t}_sd" for t in TYPE_ORDER] + ["total_mean", "meme_share"])
        for cid in CELL_IDS:
            for i, w in enumerate(W):
                wtr.writerow([cid, w] + [round(mean[cid][t][w], 3) for t in TYPE_ORDER]
                             + [round(sd_[cid][t][w], 3) for t in TYPE_ORDER]
                             + [round(tot[cid][i], 3), round(sim_share[cid][w]["meme"], 4)])

    # ---------- 校验：基线 cell vs 真机 interest 臂 ----------
    print(f"\n{'='*78}\n校验：基线 cell（D1R1）代理 vs 真机 interest 臂（agent 产出口径，3 seed）"
          f"\n{'='*78}")
    print(f"{'周':<12}{'代理玩梗':>9}{'真机玩梗':>9}{'差':>8} | "
          f"{'代理总量':>9}{'真机总量':>9}{'差':>8}")
    for i, w in enumerate(W):
        ps, rs = sim_share["D1R1"][w]["meme"], real_share[w]["meme"]
        rt = sum(real_supply[w].get(t, 0.0) for t in TYPE_ORDER)
        print(f"{w:<12}{ps:>9.3f}{rs:>9.3f}{ps-rs:>+8.3f} | "
              f"{tot['D1R1'][i]:>9.1f}{rt:>9.1f}{tot['D1R1'][i]-rt:>+8.1f}")
    _mf = [(abs(sim_share["D1R1"][w]["meme"] - real_share[w]["meme"]), w) for w in W]
    print(f"\n玩梗份额 逐周|差|：平均 {statistics.mean(d for d,_ in _mf):.3f} / "
          f"最大 {max(_mf)[0]:.3f} @{max(_mf)[1]}")
    print("（此差值即代理预测的**可信度折扣**：反事实差值应据此理解为方向与量级的估计，"
          "不是真机的逐值预测）")

    # ---------- 反事实主表 ----------
    print(f"\n{'='*78}\n反事实预测：玩梗份额轨迹（{args.seeds} seed 均值，agent 产出口径）\n{'='*78}")
    hdr = f"{'周':<12}" + "".join(f"{cid:>10}" for cid in CELL_IDS) + f"{'真机':>10}{'真基准':>10}"
    print(hdr)
    for w in W:
        print(f"{w:<12}" + "".join(f"{sim_share[cid][w]['meme']:>10.3f}" for cid in CELL_IDS)
              + f"{real_share[w]['meme']:>10.3f}{bench_share[w]['meme']:>10.3f}")

    print(f"\n{'='*78}\n反事实预测：周总产量（agent 帖）与峰值周\n{'='*78}")
    print(f"{'周':<12}" + "".join(f"{cid:>10}" for cid in CELL_IDS))
    for i, w in enumerate(W):
        print(f"{w:<12}" + "".join(f"{tot[cid][i]:>10.1f}" for cid in CELL_IDS))
    for cid, _cn, col, cn in [(c[2], c[1], c[4], c[3]) for c in CELLS]:
        pk = W[tot[cid].index(max(tot[cid]))]
        print(f"  {cid:<6}{cn:<22} 总帖 {sum(tot[cid]):>6.0f} | 峰值周 {pk}（{max(tot[cid]):.1f} 帖）")

    # ---------- 机制分解（W20 / W22）----------
    print(f"\n{'='*78}\n机制分解：玩梗份额的消融效应（Δ = 关掉后 − 全开）\n{'='*78}")
    s = {cid: {w: sim_share[cid][w]["meme"] for w in W} for cid in CELL_IDS}
    for w in ("2026-W20", "2026-W22"):
        print(f"\n【{w}】")
        print(f"  全开基线 D1R1 = {s['D1R1'][w]:.3f}")
        print(f"  关沉默螺旋（R 保持开）  D1R1→D0R1 : {s['D0R1'][w]-s['D1R1'][w]:+8.3f}")
        print(f"  关注意力衰减（D 保持开）D1R1→D1R0 : {s['D1R0'][w]-s['D1R1'][w]:+8.3f}")
        print(f"  双关                    D1R1→D0R0 : {s['D0R0'][w]-s['D1R1'][w]:+8.3f}")
        _d_at_r1 = s["D1R1"][w] - s["D0R1"][w]      # D 的效应（R 开时）
        _d_at_r0 = s["D1R0"][w] - s["D0R0"][w]      # D 的效应（R 关时）
        _r_at_d1 = s["D1R1"][w] - s["D1R0"][w]      # R 的效应（D 开时）
        _r_at_d0 = s["D0R1"][w] - s["D0R0"][w]      # R 的效应（D 关时）
        print(f"  —— D 主效应（两档平均）        : {(_d_at_r1+_d_at_r0)/2:+8.3f}"
              f"  （R 开时 {_d_at_r1:+.3f} / R 关时 {_d_at_r0:+.3f}）")
        print(f"  —— R 主效应（两档平均）        : {(_r_at_d1+_r_at_d0)/2:+8.3f}"
              f"  （D 开时 {_r_at_d1:+.3f} / D 关时 {_r_at_d0:+.3f}）")
        print(f"  —— 交互项 (D|R开 − D|R关)      : {_d_at_r1-_d_at_r0:+8.3f}")

    # 二波判据（W19-22）逐 cell
    print(f"\n{'='*78}\n二波判据（W19-22 玩梗份额）与起爆倍数\n{'='*78}")
    for cid, cn in [(c[2], c[3]) for c in CELLS]:
        seq = [s[cid][f"2026-W{i}"] for i in (19, 20, 21, 22)]
        print(f"  {cid:<6}{cn:<22} " + "/".join(f"{x:.3f}" for x in seq)
              + f"   W22/W20 ×{seq[3]/max(seq[1],1e-9):.1f}")

    # W13 事件周（议程保底 × D 的交叉读数）
    print(f"\n{'='*78}\n事件周 W13 悼念份额（议程保底 5 条的放大效应）\n{'='*78}")
    for cid, cn in [(c[2], c[3]) for c in CELLS]:
        print(f"  {cid:<6}{cn:<22} 代理 {sim_share[cid]['2026-W13']['mourning']:.3f}"
              f"  | 真机 {real_share['2026-W13']['mourning']:.3f}"
              f"  | 真基准 {bench_share['2026-W13']['mourning']:.3f}")

    # ---------- 出图 ----------
    plt = pltmod.plt
    plt.rcParams["axes.unicode_minus"] = False   # 中文字体缺 U+2212，负刻度用 ASCII 连字符
    x = list(range(len(W)))

    # 图 A：玩梗份额 —— 4 cell vs 真机 vs 真基准
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(15, 5.6))
    for sm, dm, cid, cn, col in CELLS:
        axA.plot(x, [s[cid][w] for w in W], color=col, linewidth=2.4, marker="o",
                 markersize=4, label=cn)
    axA.plot(x, [real_share[w]["meme"] for w in W], color="#2ca02c", linewidth=1.8,
             linestyle=":", marker="^", markersize=4, label="真机 interest 臂")
    axA.plot(x, [bench_share[w]["meme"] for w in W], color="#888888", linewidth=1.4,
             linestyle="--", label="真实基准（抖音）")
    pltmod._death_line(axA, W)
    axA.set_xticks(x, W, rotation=45)
    axA.yaxis.set_major_formatter(pltmod.PercentFormatter(1.0))
    axA.set_ylabel("玩梗份额（agent 产出口径）")
    axA.set_title(f"反事实预测 · 玩梗份额（{args.seeds} seed 均值）", fontweight="bold", fontsize=12)
    # 下压到 0.86：给顶部的世逝周标注让位（同 plot_run_charts 的做法）
    axA.legend(loc="upper left", frameon=False, fontsize=8, bbox_to_anchor=(0.0, 0.86))
    axA.set_axisbelow(True)

    # 图 A 右：周总产量
    for sm, dm, cid, cn, col in CELLS:
        axB.plot(x, tot[cid], color=col, linewidth=2.2, marker="o", markersize=4, label=cn)
    _rt = [sum(real_supply[w].get(t, 0.0) for t in TYPE_ORDER) for w in W]
    axB.plot(x, _rt, color="#2ca02c", linewidth=1.8, linestyle=":", marker="^",
             markersize=4, label="真机 interest 臂")
    pltmod._death_line(axB, W)
    axB.set_xticks(x, W, rotation=45)
    axB.set_ylabel("周总产量（agent 帖）")
    axB.set_title("反事实预测 · 周总产量（退潮与否的直接读数）", fontweight="bold", fontsize=12)
    # 放左下：双关 cell 恒在顶部 63 帖，右上角会压在它上面
    axB.legend(loc="lower left", frameon=False, fontsize=8)
    axB.set_axisbelow(True)
    fig.tight_layout()
    outA = SCRIPT_DIR / PRED_DIR / f"{args.prefix}_A_meme_share_and_volume.png"
    outA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outA, dpi=200)
    plt.close(fig)

    # 图 B：4 cell 的堆叠面积小倍图（构成差异一目了然）
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)
    for ax, (sm, dm, cid, cn, col) in zip(axes.ravel(), CELLS):
        ax.stackplot(x, *[[mean[cid][t][w] for w in W] for t in TYPE_ORDER],
                     labels=[TYPE_LABEL[t] for t in TYPE_ORDER],
                     colors=[TYPE_COLOR[t] for t in TYPE_ORDER], alpha=0.92,
                     linewidth=0.6, edgecolor="white")
        pltmod._death_line(ax, W)
        ax.set_title(f"{cn}（{cid}）", fontweight="bold", fontsize=11)
        ax.set_xticks(x, W, rotation=45)
        ax.set_axisbelow(True)
        ax.set_ylabel("周发帖数（堆叠）")
    axes.ravel()[0].legend(loc="upper right", frameon=False, fontsize=8)
    fig.suptitle(f"反事实预测 · 各 cell 周发帖构成（{args.seeds} seed 均值）",
                 fontweight="bold", fontsize=13)
    fig.tight_layout()
    outB = SCRIPT_DIR / PRED_DIR / f"{args.prefix}_B_cell_composition.png"
    fig.savefig(outB, dpi=200)
    plt.close(fig)

    # 图 C：机制分解柱状图
    fig, axC = plt.subplots(figsize=(9, 5.2))
    weeks_bar = ["2026-W20", "2026-W22"]
    bars = [
        ("关沉默螺旋 D1R1→D0R1", [s["D0R1"][w] - s["D1R1"][w] for w in weeks_bar], "#1f77b4"),
        ("关注意力衰减 D1R1→D1R0", [s["D1R0"][w] - s["D1R1"][w] for w in weeks_bar], "#d62728"),
        ("双关 D1R1→D0R0", [s["D0R0"][w] - s["D1R1"][w] for w in weeks_bar], "#9467bd"),
    ]
    _bw = 0.26
    for k, (lab, vals, col) in enumerate(bars):
        pos = [i + (k - 1) * _bw for i in range(len(weeks_bar))]
        axC.bar(pos, vals, width=_bw, label=lab, color=col, alpha=0.9)
        for p, v in zip(pos, vals):
            axC.text(p, v + (0.006 if v >= 0 else -0.018), f"{v:+.3f}",
                     ha="center", fontsize=8)
    axC.axhline(0, color="#444444", linewidth=1.0)
    axC.set_xticks(range(len(weeks_bar)), weeks_bar)
    axC.set_ylabel("玩梗份额变化 Δ（关掉后 - 全开）")
    axC.set_title("反事实预测 · 两机制对玩梗份额的消融效应", fontweight="bold", fontsize=12)
    axC.legend(frameon=False, fontsize=9)
    axC.set_axisbelow(True)
    fig.tight_layout()
    outC = SCRIPT_DIR / PRED_DIR / f"{args.prefix}_C_mechanism_decomposition.png"
    fig.savefig(outC, dpi=200)
    plt.close(fig)

    # 图 D：双重分离三联图 —— 分子（玩梗帖数）/ 分母（总产量）/ 比值（玩梗份额）。
    # 这是本预测最核心的读数，必须并排看：关 R 后前两者一平一涨、第三者腰斩。
    fig, axesD = plt.subplots(1, 3, figsize=(16.5, 5.0))
    _panels = [
        ("分子：玩梗帖数", {cid: [mean[cid]["meme"][w] for w in W] for cid in CELL_IDS},
         "周玩梗帖数（agent 帖）", False),
        ("分母：周总产量", {cid: tot[cid] for cid in CELL_IDS},
         "周总产量（agent 帖）", False),
        ("比值：玩梗份额", {cid: [s[cid][w] for w in W] for cid in CELL_IDS},
         "玩梗份额", True),
    ]
    for ax, (ptitle, series, ylab, is_pct) in zip(axesD, _panels):
        for sm, dm, cid, cn, col in CELLS:
            ax.plot(x, series[cid], color=col, linewidth=2.2, marker="o",
                    markersize=3.6, label=cn)
        pltmod._death_line(ax, W)
        ax.set_xticks(x, W, rotation=45)
        if is_pct:
            ax.yaxis.set_major_formatter(pltmod.PercentFormatter(1.0))
        ax.set_ylabel(ylab)
        ax.set_title(ptitle, fontweight="bold", fontsize=12)
        ax.set_axisbelow(True)
    # 三栏共用一套色标：图例提到图级，避免与标注打架
    _h, _l = axesD[0].get_legend_handles_labels()
    fig.legend(_h, _l, loc="upper center", bbox_to_anchor=(0.5, 0.935),
               ncol=4, frameon=False, fontsize=9)
    # 关键对比标注：用 axes fraction 定位，避免文本落到坐标轴外
    axesD[0].annotate(
        f"关 R 后 W22 玩梗 {mean['D1R0']['meme'][W[-1]]:.1f} vs 基线 {mean['D1R1']['meme'][W[-1]]:.1f}\n"
        f"→ 分子几乎不动（差 {abs(mean['D1R0']['meme'][W[-1]]-mean['D1R1']['meme'][W[-1]]):.1f} 帖）",
        xy=(len(W) - 1, mean["D1R0"]["meme"][W[-1]]),
        xytext=(0.30, 0.72), textcoords="axes fraction",
        fontsize=8.5, color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", linewidth=1.1))
    axesD[1].annotate(
        f"关 R 后 W22 总量 {tot['D1R0'][-1]:.0f} vs 基线 {tot['D1R1'][-1]:.0f}（≈1.8×）",
        xy=(len(W) - 1, tot["D1R0"][-1]),
        xytext=(0.30, 0.10), textcoords="axes fraction",
        fontsize=8.5, color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", linewidth=1.1))
    axesD[2].annotate(
        f"份额 W22 {s['D1R0'][W[-1]]:.3f} vs {s['D1R1'][W[-1]]:.3f}\n→ 比值腰斩",
        xy=(len(W) - 1, s["D1R0"][W[-1]]),
        xytext=(0.13, 0.66), textcoords="axes fraction",
        fontsize=8.5, color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", linewidth=1.1))
    fig.suptitle(f"反事实预测 · 双重分离：沉默螺旋管「分子」，注意力衰减管「分母」"
                 f"（{args.seeds} seed 均值）", fontweight="bold", fontsize=13, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    outD = SCRIPT_DIR / PRED_DIR / f"{args.prefix}_D_double_dissociation.png"
    fig.savefig(outD, dpi=200)
    plt.close(fig)

    for p in (outA, outB, outC, outD):
        print(f"✓ 图  {p.relative_to(SCRIPT_DIR)}")
    print(f"✓ CSV {csv_path.relative_to(SCRIPT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
