#!/usr/bin/env python3
"""plot_real_baseline_chart: 真实打标数据的 W12-W22「各内容类型供给量」堆叠面积图。

用途：作为 `plot_run_charts.chart3_stacked_area`（模拟 run 侧）的**真实基准对照图**。
两图同款式（配色 / 事件线 / 轴标签 / figsize / dpi），可直接并排比读形态与量级：

    模拟 run（250 条注入预算）   ~50-80 帖/周
    真实基准（xlsx 全量 52,716 条） W12-W22 共 48,360 帖，W13 单周 11,394

数据源：工作区根目录 `抖音微博小红书-全量已打标.xlsx`（用户提供，人工打标）。
口径：剔除 `数据有效性=='存疑'`（20 行）；`无效` 保留（=营销+噪音，属真实供给组成）。
     与 `hypothesis_4/benchmark_curves.json.weekly_category_matrix`、
     `custom/envs/curation_assets/injection_posts.json.meta.weekly_counts` 逐周完全一致，
     脚本自校验，不一致直接报错退出（防止口径漂移后静默出图）。

读图提示：绝对量口径下 W13（去世周）占全期 23.6%（11,394/48,360），
     纵轴被尖峰支配 → 另出一张 --zoom 变体（只画 W14-W22）供细看衰减与二波。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/plot_real_baseline_chart.py
    $PYTHON_PATH hypothesis_4/experiment_1/plot_real_baseline_chart.py --zoom   # 另出 W14-W22 细看版
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]                       # 工作区根目录
XLSX = ROOT / "抖音微博小红书-全量已打标.xlsx"
BENCH = ROOT / "hypothesis_4" / "benchmark_curves.json"

OUT_DIR = ROOT / "hypothesis_4" / "experiment_1" / "results" / "charts"
TABLE_DIR = ROOT / "hypothesis_4" / "experiment_1" / "results" / "tables"

# ---------------- 样式（与 plot_run_charts.py 逐项一致，保证两图可直接并读） ----------------

plt.rcParams.update({
    "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "Heiti TC"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#444444",
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

DEATH_WEEK = "2026-W13"
DEATH_LABEL = "去世 3-24 (W13)"

# 顺序与配色对齐 plot_run_charts.TYPE_ORDER / TYPE_COLOR
TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
TYPE_LABEL = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
              "marketing": "营销", "other": "其他", "noise": "噪音"}
TYPE_COLOR = {"mourning": "#4C72B0", "meme": "#DD8452", "education": "#55A868",
              "marketing": "#CCB974", "other": "#64B5CD", "noise": "#B07AA1"}

# xlsx「内容类别」中文键 → type（与 benchmark_curves / calibrate_speak.TYPE_KEYS 同映射）
CN_TO_TYPE = {
    "梗文化讨论": "meme", "事件悼念讨论": "mourning", "教育观点讨论": "education",
    "借势营销": "marketing", "其他讨论": "other", "爬取噪音": "noise",
}


def weeks_range(start: int, end: int) -> list[str]:
    return [f"2026-W{w:02d}" for w in range(start, end + 1)]


# ---------------- 数据 ----------------

def load_real_matrix() -> dict[str, dict[str, int]]:
    """从 xlsx 现算「周 × 类型」精确计数，并对照 benchmark_curves.json 自校验。"""
    if not XLSX.exists():
        raise SystemExit(f"未找到源数据：{XLSX}")
    df = pd.read_excel(XLSX, sheet_name="Sheet1", usecols=["id", "内容类别", "数据有效性", "published_at"])
    n_all = len(df)
    df = df[df["数据有效性"] != "存疑"]
    dt = pd.to_datetime(df["published_at"], format="ISO8601", utc=True)
    iso = dt.dt.isocalendar()
    df = df.assign(week=iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2))

    piv = df.pivot_table(index="week", columns="内容类别", values="id",
                         aggfunc="size", fill_value=0)
    matrix = {wk: {t: int(piv.loc[wk].get(cn, 0)) for cn, t in CN_TO_TYPE.items()}
              for wk in piv.index}
    print(f"源数据 {XLSX.name}：{n_all:,} 行 → 剔除存疑 20 行后 {len(df):,} 行进入口径")

    # 自校验：与包内基准矩阵逐周逐类对齐（不一致=口径已漂移，必须停下）
    if BENCH.exists():
        bm = json.loads(BENCH.read_text(encoding="utf-8"))["weekly_category_matrix"]
        bad = [(wk, cn, matrix[wk][t], bm[wk][cn])
               for wk in bm for cn, t in CN_TO_TYPE.items()
               if wk in matrix and matrix[wk][t] != bm[wk][cn]]
        if bad:
            for wk, cn, got, exp in bad[:10]:
                print(f"  ✗ {wk} {cn}: 实算 {got} ≠ 基准 {exp}")
            raise SystemExit("口径与 benchmark_curves.json 不一致，已中止出图")
        print(f"✓ 自校验通过：{len(bm)} 周 × {len(CN_TO_TYPE)} 类与 "
              f"benchmark_curves.json 完全一致")
    return matrix


def write_csv(matrix: dict[str, dict[str, int]], weeks: list[str], out: Path) -> Path:
    """长表导出：week, type, type_cn, count, week_total, share。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["week", "type", "type_cn", "count", "week_total", "share"])
        for wk in weeks:
            row = matrix[wk]
            tot = sum(row.values())
            for t in TYPE_ORDER:
                cn = next(k for k, v in CN_TO_TYPE.items() if v == t)
                w.writerow([wk, t, cn, row[t], tot, f"{row[t] / tot:.6f}" if tot else "0"])
    return out


# ---------------- 出图 ----------------

def _death_line(ax, weeks: list[str]) -> None:
    if DEATH_WEEK in weeks:
        ax.axvline(weeks.index(DEATH_WEEK), color="#D62728", linestyle="--",
                   linewidth=1.4, alpha=0.85, zorder=1)
        ax.annotate(DEATH_LABEL, xy=(weeks.index(DEATH_WEEK), 1.0),
                    xycoords=("data", "axes fraction"),
                    xytext=(6, -4), textcoords="offset points",
                    color="#D62728", fontsize=10, va="top",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def plot_stacked(matrix: dict[str, dict[str, int]], weeks: list[str], out: Path,
                 title: str, annotate: bool = False) -> Path:
    x = list(range(len(weeks)))
    series = {t: [matrix[wk][t] for wk in weeks] for t in TYPE_ORDER}
    totals = [sum(matrix[wk].values()) for wk in weeks]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    _death_line(ax, weeks)
    ax.stackplot(x, *[series[t] for t in TYPE_ORDER],
                 labels=[TYPE_LABEL[t] for t in TYPE_ORDER],
                 colors=[TYPE_COLOR[t] for t in TYPE_ORDER],
                 edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("帖数（绝对数量）")
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.margins(y=0.05)
    # 绝对量到万级：刻度加千分位，避免 11000 与 1000 视觉上难分
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
    if annotate:
        for i, tv in enumerate(totals):
            vmax = max(totals)
            off = 4 if tv < vmax * 0.85 else -13      # 尖峰顶部留白，其余标在顶点上方
            # 离开轴中点：顶点标注与红色事件虚线（画在轴上）会互相压字
            ax.annotate(f"{tv:,}", xy=(i, tv), xytext=(10, off), textcoords="offset points",
                        ha="center", fontsize=8.5, color="#333333", zorder=5)
        ax.margins(y=0.10)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="真实打标数据 W12-W22 各内容类型供给量堆叠面积图")
    ap.add_argument("--zoom", action="store_true",
                    help="另出 W14-W22 细看版（剔除 W13 尖峰，看衰减与玩梗二波）")
    args = ap.parse_args()

    matrix = load_real_matrix()
    all_weeks = [w for w in weeks_range(12, 22) if w in matrix]
    missing = set(all_weeks) - set(matrix)
    if missing:
        raise SystemExit(f"源数据缺周：{sorted(missing)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tot_all = sum(sum(matrix[w].values()) for w in all_weeks)
    w13 = sum(matrix["2026-W13"].values())

    csv_path = write_csv(matrix, all_weeks, TABLE_DIR / "real_baseline_weekly_category.csv")
    print(f"✓ CSV  {csv_path.relative_to(ROOT)}")

    main_out = OUT_DIR / "real_baseline__chart3_supply_stacked_area.png"
    plot_stacked(matrix, all_weeks, main_out,
                 title="各内容类型供给量变化（真实打标数据 · 堆叠面积 · 绝对数量 · W12–W22）",
                 annotate=True)
    print(f"✓ 图   {main_out.relative_to(ROOT)}")

    if args.zoom:
        zw = [w for w in all_weeks if w != "2026-W13"]
        zoom_out = OUT_DIR / "real_baseline__chart3_supply_stacked_area_W14-W22.png"
        plot_stacked(matrix, zw, zoom_out,
                     title="各内容类型供给量变化（真实打标数据 · 剔除 W13 尖峰 · 绝对数量）",
                     annotate=True)
        print(f"✓ 图   {zoom_out.relative_to(ROOT)}")

    print(f"\nW12–W22 合计 {tot_all:,} 帖｜W13 单周 {w13:,}（占全期 {w13 / tot_all:.1%}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
