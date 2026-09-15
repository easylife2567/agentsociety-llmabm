#!/usr/bin/env python3
"""Render template-matched D/R/B comparisons from existing numerical proxy data.

This script does not read any formal run/replay output. Agent supply comes only
from the 100-seed numerical ablation CSV, while injected supply is counted from
the fixed numerical-proxy input exposed by ``calibrate_speak.INJECTED_BY_WEEK``.
"""

from __future__ import annotations

import csv
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import calibrate_speak as cal

OUT_ROOT = SCRIPT_DIR / "results" / "numerical_ablation_drb"
INPUT_CSV = OUT_ROOT / "data" / "drb_ablation_seed_week_type.csv"
SUMMARY_CSV = OUT_ROOT / "data" / "drb_ablation_combined_supply_summary.csv"
CHART_DIR = OUT_ROOT / "charts" / "template_stacked_area"

WEEKS = list(cal.WEEKS)
CONDITION_ORDER = ["full", "no_B", "no_D", "no_R"]
CONDITION_LABEL = {
    "full": "完整模型 (B + D + R)",
    "no_B": "去 B",
    "no_D": "去 D",
    "no_R": "去 R",
}
PAIR_TITLES = {
    "no_B": "D/R/B 数值消融：完整模型 vs 去 B",
    "no_D": "D/R/B 数值消融：完整模型 vs 去 D",
    "no_R": "D/R/B 数值消融：完整模型 vs 去 R",
}
PAIR_FILES = {
    "no_B": "figure_02_full_vs_no_b_supply_stacked_area.png",
    "no_D": "figure_03_full_vs_no_d_supply_stacked_area.png",
    "no_R": "figure_04_full_vs_no_r_supply_stacked_area.png",
}

# Exact stack order and colors from the user-specified formal chart template.
STACK_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
STACK_LABEL = {
    "meme": "Meme",
    "mourning": "Mourning",
    "education": "Education",
    "marketing": "Marketing",
    "other": "Other",
    "noise": "Noise",
}
STACK_COLORS = {
    "meme": "#DD8452",
    "mourning": "#4C72B0",
    "education": "#55A868",
    "marketing": "#CCB974",
    "other": "#64B5CD",
    "noise": "#B07AA1",
}

CAPTION = (
    "100-seed numerical proxy mean + fixed injected supply from the numerical-proxy input. "
    "No formal replay or LLM run was used."
)


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Arial Unicode MS",
                "PingFang SC",
                "Heiti TC",
                "SimHei",
                "Arial",
                "DejaVu Sans",
            ],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 10.5,
            "axes.titlesize": 12.5,
            "axes.labelsize": 11,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 10,
            "legend.fontsize": 9.5,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.9,
            "axes.grid": True,
            "grid.color": "#D0D0D0",
            "grid.alpha": 0.72,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def load_agent_means() -> tuple[dict[tuple[str, str, str], float], int]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Numerical ablation input not found: {INPUT_CSV}")

    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    seeds_by_condition: dict[str, set[int]] = defaultdict(set)
    with INPUT_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            condition = str(row["condition"])
            week = str(row["week"])
            agent_type = str(row["agent_type"])
            seed = int(row["seed"])
            grouped[(condition, week, agent_type)].append(float(row["supply"]))
            seeds_by_condition[condition].add(seed)

    missing_conditions = set(CONDITION_ORDER) - set(seeds_by_condition)
    if missing_conditions:
        raise ValueError(f"Missing conditions in numerical CSV: {sorted(missing_conditions)}")
    seed_counts = {condition: len(seeds_by_condition[condition]) for condition in CONDITION_ORDER}
    if len(set(seed_counts.values())) != 1:
        raise ValueError(f"Unequal paired seed counts: {seed_counts}")
    seed_count = next(iter(seed_counts.values()))
    if seed_count != 100:
        raise ValueError(f"Expected the existing 100-seed numerical result, found {seed_count} seeds")

    means = {key: float(np.mean(values)) for key, values in grouped.items()}
    expected = {
        (condition, week, agent_type)
        for condition in CONDITION_ORDER
        for week in WEEKS
        for agent_type in cal.TYPE_ORDER
    }
    missing_cells = expected - set(means)
    if missing_cells:
        raise ValueError(f"Numerical CSV is missing {len(missing_cells)} condition-week-type cells")
    return means, seed_count


def injected_counts() -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for week in WEEKS:
        week_counts = Counter(str(post.get("type", "other")) for post in cal.INJECTED_BY_WEEK[week])
        unknown = set(week_counts) - set(STACK_ORDER)
        if unknown:
            raise ValueError(f"Unexpected injected post types in {week}: {sorted(unknown)}")
        for category in STACK_ORDER:
            counts[(week, category)] = int(week_counts.get(category, 0))
    return counts


def build_combined_series(
    means: dict[tuple[str, str, str], float],
    injections: dict[tuple[str, str], int],
    seed_count: int,
) -> dict[str, dict[str, np.ndarray]]:
    combined: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, str]] = []
    for condition in CONDITION_ORDER:
        combined[condition] = {}
        for category in STACK_ORDER:
            values: list[float] = []
            for week in WEEKS:
                agent_mean = means[(condition, week, category)] if category in cal.TYPE_ORDER else 0.0
                injected = injections[(week, category)]
                total = agent_mean + injected
                values.append(total)
                rows.append(
                    {
                        "condition": condition,
                        "week": week,
                        "category": category,
                        "mean_agent_supply": f"{agent_mean:.6f}",
                        "fixed_injected_supply": str(injected),
                        "mean_combined_supply": f"{total:.6f}",
                        "paired_seed_count": str(seed_count),
                        "source": "numerical_proxy_only_no_formal_replay_or_llm_run",
                    }
                )
            combined[condition][category] = np.asarray(values, dtype=float)

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return combined


def add_stack_panel(
    ax: plt.Axes,
    condition: str,
    combined: dict[str, dict[str, np.ndarray]],
    y_max: float,
) -> None:
    x = np.arange(len(WEEKS))
    series = [combined[condition][category] for category in STACK_ORDER]
    ax.stackplot(
        x,
        *series,
        labels=[STACK_LABEL[category] for category in STACK_ORDER],
        colors=[STACK_COLORS[category] for category in STACK_ORDER],
        alpha=0.92,
        linewidth=0.8,
        edgecolor="white",
    )
    ax.axvline(1, color="#E53935", linestyle="--", linewidth=1.4, zorder=8)
    ax.text(
        1.10,
        y_max * 0.965,
        "去世 3-24 (W13)",
        color="#E53935",
        fontsize=9.5,
        ha="left",
        va="top",
        zorder=9,
    )
    ax.set_title(CONDITION_LABEL[condition], fontweight="bold", pad=8)
    ax.set_xticks(x, WEEKS, rotation=48, ha="right")
    ax.set_xlabel("周")
    ax.set_xlim(-0.5, len(WEEKS) - 0.5)
    ax.set_ylim(0, y_max)
    ax.set_axisbelow(True)


def save_figure(fig: plt.Figure, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "AgentSociety numerical proxy plotting script"},
    )
    plt.close(fig)


def plot_pairwise(
    ablation: str,
    combined: dict[str, dict[str, np.ndarray]],
    y_max: float,
) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.0), sharex=True, sharey=True)
    add_stack_panel(axes[0], "full", combined, y_max)
    add_stack_panel(axes[1], ablation, combined, y_max)
    axes[0].set_ylabel("帖数（绝对供给量）")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(0.985, 0.53), ncol=1)
    fig.suptitle(PAIR_TITLES[ablation], fontsize=16, fontweight="bold", y=0.985)
    fig.text(0.5, 0.015, CAPTION, ha="center", va="bottom", fontsize=9, color="#4D4D4D")
    fig.subplots_adjust(left=0.065, right=0.865, bottom=0.21, top=0.86, wspace=0.08)
    output = CHART_DIR / PAIR_FILES[ablation]
    save_figure(fig, output)
    return output


def plot_overview(combined: dict[str, dict[str, np.ndarray]], y_max: float) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(15.7, 10.2), sharex=True, sharey=True)
    for ax, condition, label in zip(axes.flat, CONDITION_ORDER, ("a", "b", "c", "d")):
        add_stack_panel(ax, condition, combined, y_max)
        ax.text(
            -0.075,
            1.04,
            label,
            transform=ax.transAxes,
            fontsize=13,
            fontweight="bold",
            ha="left",
            va="bottom",
        )
    axes[0, 0].set_ylabel("帖数（绝对供给量）")
    axes[1, 0].set_ylabel("帖数（绝对供给量）")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(0.985, 0.52), ncol=1)
    fig.suptitle(
        "D/R/B 数值消融：各内容类型供给量总览",
        fontsize=17,
        fontweight="bold",
        y=0.985,
    )
    fig.text(0.5, 0.012, CAPTION, ha="center", va="bottom", fontsize=9, color="#4D4D4D")
    fig.subplots_adjust(left=0.065, right=0.875, bottom=0.13, top=0.91, hspace=0.32, wspace=0.08)
    output = CHART_DIR / "figure_05_drb_supply_stacked_area_overview.png"
    save_figure(fig, output)
    return output


def main() -> None:
    apply_style()
    means, seed_count = load_agent_means()
    injections = injected_counts()
    combined = build_combined_series(means, injections, seed_count)
    maximum = max(
        float(sum(combined[condition][category][i] for category in STACK_ORDER))
        for condition in CONDITION_ORDER
        for i in range(len(WEEKS))
    )
    y_max = max(80.0, math.ceil(maximum / 10.0) * 10.0)
    outputs = [
        plot_pairwise(condition, combined, y_max)
        for condition in ("no_B", "no_D", "no_R")
    ]
    outputs.append(plot_overview(combined, y_max))
    print(f"source={INPUT_CSV}")
    print(f"paired_seeds={seed_count}")
    print(f"shared_y_axis=0-{y_max:g}")
    print(f"summary={SUMMARY_CSV}")
    for output in outputs:
        print(f"figure={output}")


if __name__ == "__main__":
    main()
