#!/usr/bin/env python3
"""Plot the platform-user coupling chain and Agent content feedback.

Figure contract
---------------
Core finding: curation regimes create different joint configurations of visible
content, user speaking, and endogenous supply. At W22, Interest produces the
highest meme-agent speaking rate and meme supply despite lower aggregate meme
exposure than Chronological, supporting a coupled platform-user interpretation.
Evidence: anchored_v1, 3 arms x 3 seeds, W12--W22 formal runs.
Figure: W20/W22 mechanism-chain panels plus three Agent-only supply panels.
Caveat: connected percentages have different denominators; the lines encode the
model sequence, not a conserved conversion rate. Exposure minus mixed supply is
descriptive and is not a net causal amplification estimate.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import plot_arm_charts as armplot  # noqa: E402


OUTPUT_DIR = (
    SCRIPT_DIR
    / "runs"
    / "anchored_v1"
    / "_derived"
    / "charts"
    / "report_composites"
)
DATA_DIR = SCRIPT_DIR / "runs" / "anchored_v1" / "_derived" / "data" / "arm"
PNG_OUT = OUTPUT_DIR / "figure_05_platform_user_coupling_and_feedback.png"
SVG_OUT = OUTPUT_DIR / "figure_05_platform_user_coupling_and_feedback.svg"
JSON_OUT = OUTPUT_DIR / "figure_05_platform_user_coupling_and_feedback.json"
CSV_OUT = DATA_DIR / "arm_platform_user_chain.csv"

CHAIN_WEEKS = ["2026-W20", "2026-W22"]
STAGES = [
    ("mixed_supply_share", "混合供给\n玩梗份额"),
    ("exposure_share", "$\\Gamma$输出\n玩梗曝光份额"),
    ("speaking_rate", "$U$响应\n玩梗型Agent发言率"),
    ("agent_supply_share", "内容回流\nAgent-only玩梗份额"),
]
VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]
TYPE_LABELS = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
}


def weekly_row(run: dict, week: str) -> dict:
    for row in run["weekly"]:
        if row["week"] == week:
            return row
    raise KeyError(f"{run['label']} missing {week}")


def stage_value(row: dict, stage: str) -> float:
    if stage == "mixed_supply_share":
        return float(row["supply_share_all_meme"])
    if stage == "exposure_share":
        return float(row["exposure_share_meme"])
    if stage == "speaking_rate":
        return float(row["agent_agg"]["meme"]["spoke_rate"])
    if stage == "agent_supply_share":
        return float(row["supply_share_meme"])
    raise KeyError(stage)


def summary(values: list[float]) -> tuple[float, float, float]:
    return statistics.fmean(values), min(values), max(values)


def panel_label(ax, label: str) -> None:
    ax.text(
        -0.10,
        1.06,
        label,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        ha="left",
        va="bottom",
    )


def draw_chain_panel(ax, by_arm: dict, week: str, title: str, label: str, records: list[dict]) -> None:
    x = np.arange(len(STAGES))
    for arm in armplot.ARMS:
        means, lows, highs = [], [], []
        for stage, _ in STAGES:
            values = [stage_value(weekly_row(run, week), stage) for run in by_arm[arm]]
            mean, low, high = summary(values)
            means.append(mean)
            lows.append(low)
            highs.append(high)
            records.append(
                {
                    "week": week,
                    "arm": arm,
                    "stage": stage,
                    "mean": mean,
                    "min": low,
                    "max": high,
                }
            )
        color = armplot.ARM_COLOR[arm]
        ax.plot(
            x,
            means,
            color=color,
            linewidth=2.5,
            marker="o",
            markersize=6,
            zorder=4,
        )
        ax.errorbar(
            x,
            means,
            yerr=[np.asarray(means) - np.asarray(lows), np.asarray(highs) - np.asarray(means)],
            fmt="none",
            ecolor=color,
            elinewidth=1.1,
            capsize=3,
            alpha=0.75,
            zorder=3,
        )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    ax.set_xticks(x, [stage_label for _, stage_label in STAGES])
    ax.set_xlim(-0.18, len(STAGES) - 0.82)
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", color="#E2E2E2", linewidth=0.8)
    ax.set_axisbelow(True)
    panel_label(ax, label)


def draw_supply_panel(ax, by_arm: dict, weeks: list[str], arm: str, label: str) -> None:
    x = np.arange(len(weeks))
    series = []
    for content_type in VALID_TYPES:
        values = []
        for index in range(len(weeks)):
            values.append(
                statistics.fmean(
                    float(run["weekly"][index].get(f"agent_supply_{content_type}", 0.0))
                    for run in by_arm[arm]
                )
            )
        series.append(values)

    ax.stackplot(
        x,
        *series,
        colors=[armplot.TYPE_COLOR[t] for t in VALID_TYPES],
        edgecolor="white",
        linewidth=0.45,
        alpha=0.94,
    )
    if armplot.DEATH_WEEK in weeks:
        ax.axvline(
            weeks.index(armplot.DEATH_WEEK),
            color="#D62728",
            linestyle="--",
            linewidth=1.1,
            alpha=0.82,
        )
    tick_indices = [0, 1, 4, 7, 10]
    ax.set_xticks(tick_indices, [weeks[i].replace("2026-", "") for i in tick_indices])
    ax.set_ylim(0, 45)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_title(f"{armplot.ARM_LABEL_EN[arm]}：Agent内容回流", fontsize=11, fontweight="bold", pad=6)
    ax.set_xlabel("周次")
    ax.grid(axis="y", color="#E2E2E2", linewidth=0.7)
    ax.set_axisbelow(True)
    panel_label(ax, label)


def main() -> int:
    runs = armplot.load_runs([], strict=True)
    by_arm = armplot.group_by_arm(runs)
    invalid = [arm for arm in armplot.ARMS if len(by_arm.get(arm, [])) != 3]
    if invalid:
        raise SystemExit(f"Expected exactly three seeds for every arm; invalid: {invalid}")

    weeks = [row["week"] for row in runs[0]["weekly"]]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Hiragino Sans GB",
                "PingFang SC",
                "Arial Unicode MS",
                "Heiti TC",
                "DejaVu Sans",
            ],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    fig = plt.figure(figsize=(12.0, 9.4))
    grid = fig.add_gridspec(2, 6, height_ratios=[1.0, 0.78], hspace=0.40, wspace=0.34)
    records: list[dict] = []
    chain_axes = [fig.add_subplot(grid[0, 0:3]), fig.add_subplot(grid[0, 3:6])]
    draw_chain_panel(chain_axes[0], by_arm, CHAIN_WEEKS[0], "W20：二次增长启动", "a", records)
    draw_chain_panel(chain_axes[1], by_arm, CHAIN_WEEKS[1], "W22：后段终点", "b", records)
    chain_axes[0].set_ylabel("比例")
    chain_axes[1].tick_params(labelleft=False)

    arm_handles = [
        Line2D(
            [0],
            [0],
            color=armplot.ARM_COLOR[arm],
            marker="o",
            linewidth=2.5,
            label=armplot.ARM_LABEL_EN[arm],
        )
        for arm in armplot.ARMS
    ]
    chain_axes[0].legend(handles=arm_handles, loc="upper left", fontsize=9.5)

    supply_axes = [
        fig.add_subplot(grid[1, 0:2]),
        fig.add_subplot(grid[1, 2:4]),
        fig.add_subplot(grid[1, 4:6]),
    ]
    for index, (ax, arm) in enumerate(zip(supply_axes, armplot.ARMS)):
        draw_supply_panel(ax, by_arm, weeks, arm, chr(ord("c") + index))
    supply_axes[0].set_ylabel("Agent自主发帖量（条/周，3-seed均值）")
    for ax in supply_axes[1:]:
        ax.tick_params(labelleft=False)

    type_handles = [
        Patch(facecolor=armplot.TYPE_COLOR[t], edgecolor="none", label=TYPE_LABELS[t])
        for t in VALID_TYPES
    ]
    supply_axes[-1].legend(handles=type_handles, loc="upper right", fontsize=8.5)

    fig.text(
        0.5,
        0.485,
        "连线表示模型中的机制顺序；各指标分母不同，不表示同一数量的转化率。误差线为seed间min–max范围。",
        ha="center",
        va="center",
        fontsize=9.2,
        color="#444444",
    )
    fig.subplots_adjust(top=0.965, bottom=0.07, left=0.08, right=0.975)
    fig.savefig(PNG_OUT, dpi=300, facecolor="white")
    fig.savefig(SVG_OUT, facecolor="white")
    plt.close(fig)

    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["week", "arm", "stage", "mean", "min", "max"])
        writer.writeheader()
        writer.writerows(records)

    gap_summary = {}
    for week in CHAIN_WEEKS:
        gap_summary[week] = {}
        for arm in armplot.ARMS:
            subset = {(row["arm"], row["stage"]): row for row in records if row["week"] == week}
            gap_summary[week][arm] = 100 * (
                subset[(arm, "exposure_share")]["mean"]
                - subset[(arm, "mixed_supply_share")]["mean"]
            )

    JSON_OUT.write_text(
        json.dumps(
            {
                "figure_contract": {
                    "core_finding": "Platform visibility configuration and user expression jointly shape content feedback.",
                    "evidence": "anchored_v1 3 arms x 3 seeds; formal W12-W22 runs",
                    "panels": {
                        "a": "W20 four-stage platform-user chain",
                        "b": "W22 four-stage platform-user chain",
                        "c-e": "Agent-only weekly supply by content type and arm",
                    },
                    "caveat": "Connected percentages use different denominators; curation gaps are descriptive, not net causal amplification estimates.",
                },
                "descriptive_curation_gap_pp": gap_summary,
                "outputs": {
                    "png": str(PNG_OUT),
                    "svg": str(SVG_OUT),
                    "csv": str(CSV_OUT),
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(PNG_OUT)
    print(JSON_OUT)
    print(CSV_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
