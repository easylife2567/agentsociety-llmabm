#!/usr/bin/env python3
"""绘制锚定式效用数值代理预测的 W12-W22 五类供给堆叠面积图。

本脚本只读取 ``data/anchored_utility_prediction.csv`` 中已经生成的
100-seed 均值，不重新估计参数、不运行正式仿真。W19-W22 是严格留出的
检验期，图中以浅灰底和事件线标识。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_CSV = SCRIPT_DIR / "data" / "anchored_utility_prediction.csv"
OUTPUT_DIR = SCRIPT_DIR / "charts" / "prediction"
OUTPUT_STEM = OUTPUT_DIR / "PROXY_anchored_utility_stacked_area"

TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other"]
TYPE_LABEL = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
}
TYPE_COLOR = {
    "meme": "#DD8452",
    "mourning": "#4C72B0",
    "education": "#55A868",
    "marketing": "#CCB974",
    "other": "#64B5CD",
}

plt.rcParams.update(
    {
        "font.sans-serif": [
            "Hiragino Sans GB",
            "PingFang SC",
            "Arial Unicode MS",
            "Heiti TC",
        ],
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
    }
)


def load_prediction() -> pd.DataFrame:
    """读取并校验锚定式数值代理预测均值。"""
    if not INPUT_CSV.exists():
        raise SystemExit(f"未找到预测数据：{INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    required = {"week", "period", "anchored_total"} | {
        f"anchored_{type_name}" for type_name in TYPE_ORDER
    }
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"预测数据缺少列：{sorted(missing)}")

    expected_weeks = [f"2026-W{week:02d}" for week in range(12, 23)]
    if df["week"].tolist() != expected_weeks:
        raise SystemExit("预测数据的周序列不是连续的 W12-W22")

    values = df[[f"anchored_{type_name}" for type_name in TYPE_ORDER]]
    if values.isna().any().any() or (values < 0).any().any():
        raise SystemExit("预测数据包含缺失值或负值")

    calculated_total = values.sum(axis=1)
    if not ((calculated_total - df["anchored_total"]).abs() < 1e-8).all():
        raise SystemExit("五类供给量之和与 anchored_total 不一致")
    return df


def plot(df: pd.DataFrame) -> tuple[Path, Path]:
    """生成与真实基线图同口径的 PNG 和 SVG。"""
    x = list(range(len(df)))
    weeks = df["week"].tolist()
    totals = df["anchored_total"].to_numpy()
    series = [df[f"anchored_{type_name}"].to_numpy() for type_name in TYPE_ORDER]

    fig, ax = plt.subplots(figsize=(10, 5.4))

    # W19-W22 是未参与参数拟合的留出检验期。
    w19_index = weeks.index("2026-W19")
    ax.axvspan(w19_index - 0.5, len(weeks) - 0.5, color="#BDBDBD", alpha=0.15, zorder=0)
    ax.axvline(
        w19_index,
        color="#F28E2B",
        linestyle=":",
        linewidth=1.5,
        alpha=0.95,
        zorder=4,
    )
    ax.annotate(
        "玩梗兴起 / 留出期开始 (W19)",
        xy=(w19_index, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(6, -22),
        textcoords="offset points",
        color="#D26A00",
        fontsize=9,
        va="top",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.88),
    )

    w13_index = weeks.index("2026-W13")
    ax.axvline(
        w13_index,
        color="#D62728",
        linestyle="--",
        linewidth=1.4,
        alpha=0.85,
        zorder=4,
    )
    ax.annotate(
        "去世 3-24 (W13)",
        xy=(w13_index, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(6, -4),
        textcoords="offset points",
        color="#D62728",
        fontsize=10,
        va="top",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.88),
    )

    ax.stackplot(
        x,
        *series,
        labels=[TYPE_LABEL[type_name] for type_name in TYPE_ORDER],
        colors=[TYPE_COLOR[type_name] for type_name in TYPE_ORDER],
        edgecolor="white",
        linewidth=0.6,
        alpha=0.92,
        zorder=2,
    )

    for index, total in enumerate(totals):
        horizontal_offset = 10 if index == 0 else (-10 if index == len(totals) - 1 else 0)
        ax.annotate(
            f"{total:.1f}",
            xy=(index, total),
            xytext=(horizontal_offset, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#333333",
            zorder=5,
        )

    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("Agent周发帖数（100 seeds均值）")
    ax.set_title(
        "各内容类型供给量变化（锚定式效用 · 数值代理预测 · W12–W22）",
        fontweight="bold",
        fontsize=13,
    )
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.margins(x=0, y=0.12)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.012,
        "注：U = B + R(D - B)；W13-W18用于参数拟合，W19-W22为留出检验期。本图是数值代理预测，不是正式仿真结果。",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUTPUT_STEM.with_suffix(".png")
    svg_path = OUTPUT_STEM.with_suffix(".svg")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, svg_path


def main() -> int:
    df = load_prediction()
    png_path, svg_path = plot(df)
    print(f"PNG: {png_path}")
    print(f"SVG: {svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
