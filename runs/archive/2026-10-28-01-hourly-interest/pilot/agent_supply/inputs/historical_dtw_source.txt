#!/usr/bin/env python3
"""Create the report figure for generative reproduction and DTW fit.

Figure contract
---------------
Core finding: Interest curation has the lowest five-type trajectory distance to the
observed benchmark, while the small multiples expose remaining local deviations.
Evidence: anchored_v1 3 arms x 3 seeds, Agent-only supply shares, W12--W22;
observed five-type shares are renormalized after excluding noise.
Archetype: four composition small multiples plus one seed-aware comparison panel.
Reviewer check: DTW is constrained to +/- one week, uses no z-normalization, and is
path-length normalized; lower distance is relative fit, not exact prediction.
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
PNG_OUT = OUTPUT_DIR / "figure_04_dtw_reproduction_and_fit.png"
SVG_OUT = OUTPUT_DIR / "figure_04_dtw_reproduction_and_fit.svg"
JSON_OUT = OUTPUT_DIR / "figure_04_dtw_reproduction_and_fit.json"
CSV_OUT = DATA_DIR / "arm_dtw_fit_summary.csv"

WINDOW = 1
VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]
STACK_TYPES = ["meme", "mourning", "education", "marketing", "other"]
TYPE_COLORS = {t: armplot.TYPE_COLOR[t] for t in STACK_TYPES}
TYPE_LABELS = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
}


def constrained_multivariate_dtw(
    simulated: np.ndarray, observed: np.ndarray, *, window: int = WINDOW
) -> tuple[float, list[tuple[int, int]]]:
    """Return path-normalized multivariate DTW and the optimal path.

    Each time point is the five-dimensional composition vector. Local cost is its
    Euclidean distance. The Sakoe--Chiba window is expressed in weekly indices.
    """
    if simulated.ndim != 2 or observed.ndim != 2:
        raise ValueError("DTW inputs must be two-dimensional [time, type]")
    if simulated.shape[1] != observed.shape[1]:
        raise ValueError("DTW inputs must have the same number of content types")

    n, m = len(simulated), len(observed)
    window = max(window, abs(n - m))
    inf = float("inf")
    cumulative = np.full((n, m), inf, dtype=float)
    path_length = np.zeros((n, m), dtype=int)
    predecessor: dict[tuple[int, int], tuple[int, int]] = {}

    for i in range(n):
        for j in range(max(0, i - window), min(m, i + window + 1)):
            local = float(np.linalg.norm(simulated[i] - observed[j]))
            if i == 0 and j == 0:
                cumulative[i, j] = local
                path_length[i, j] = 1
                continue

            # Prefer the diagonal only when cumulative costs tie.
            candidates = []
            for rank, (pi, pj) in enumerate(((i - 1, j - 1), (i - 1, j), (i, j - 1))):
                if pi >= 0 and pj >= 0 and np.isfinite(cumulative[pi, pj]):
                    candidates.append((cumulative[pi, pj], rank, pi, pj))
            if not candidates:
                continue
            _, _, pi, pj = min(candidates)
            cumulative[i, j] = cumulative[pi, pj] + local
            path_length[i, j] = path_length[pi, pj] + 1
            predecessor[(i, j)] = (pi, pj)

    if not np.isfinite(cumulative[-1, -1]):
        raise ValueError("No admissible DTW path under the selected window")

    path = [(n - 1, m - 1)]
    while path[-1] != (0, 0):
        path.append(predecessor[path[-1]])
    path.reverse()
    score = cumulative[-1, -1] / path_length[-1, -1]
    return score, path


def observed_matrix(by_arm: dict) -> np.ndarray:
    return np.asarray(
        [
            [armplot.clean_benchmark_share(week, content_type) for content_type in VALID_TYPES]
            for week in armplot._ref_weeks(by_arm)
        ],
        dtype=float,
    )


def run_matrix(run: dict) -> np.ndarray:
    return np.asarray(
        [
            [armplot.agent_share(week, content_type) for content_type in VALID_TYPES]
            for week in run["weekly"]
        ],
        dtype=float,
    )


def arm_mean_matrix(runs: list[dict]) -> np.ndarray:
    return np.mean(np.stack([run_matrix(run) for run in runs], axis=0), axis=0)


def add_event_marker(ax, x: int = 1) -> None:
    ax.axvline(x, color="#D62728", linestyle="--", linewidth=1.0, alpha=0.8)


def plot_composition_panel(
    ax, values: np.ndarray, weeks: list[str], title: str, panel: str
) -> None:
    x = np.arange(len(weeks))
    ax.stackplot(
        x,
        *[values[:, VALID_TYPES.index(t)] for t in STACK_TYPES],
        labels=[TYPE_LABELS[t] for t in STACK_TYPES],
        colors=[TYPE_COLORS[t] for t in STACK_TYPES],
        edgecolor="white",
        linewidth=0.45,
        alpha=0.94,
    )
    add_event_marker(ax)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, len(weeks) - 1)
    ticks = [0, 1, 4, 7, 10]
    ax.set_xticks(ticks, [weeks[i].replace("2026-", "") for i in ticks])
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=5)
    ax.text(
        -0.10,
        1.05,
        panel,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        ha="left",
        va="bottom",
    )
    ax.grid(axis="y", color="#E4E4E4", linewidth=0.7)
    ax.set_axisbelow(True)


def main() -> int:
    runs = armplot.load_runs([], strict=True)
    by_arm = armplot.group_by_arm(runs)
    missing = [arm for arm in armplot.ARMS if len(by_arm.get(arm, [])) != 3]
    if missing:
        raise SystemExit(f"Expected exactly three seeds for every arm; invalid: {missing}")

    weeks = [week["week"] for week in runs[0]["weekly"]]
    observed = observed_matrix(by_arm)
    mean_matrices = {arm: arm_mean_matrix(by_arm[arm]) for arm in armplot.ARMS}

    scores: dict[str, list[float]] = {}
    paths: dict[str, dict[str, list[list[int]]]] = {}
    rows = []
    for arm in armplot.ARMS:
        scores[arm] = []
        paths[arm] = {}
        for run in sorted(by_arm[arm], key=lambda item: item["seed"]):
            score, path = constrained_multivariate_dtw(run_matrix(run), observed)
            score_pp = score * 100
            scores[arm].append(score_pp)
            paths[arm][str(run["seed"])] = [[i, j] for i, j in path]
            rows.append(
                {
                    "arm": arm,
                    "seed": run["seed"],
                    "window_weeks": WINDOW,
                    "local_metric": "euclidean_5type_share",
                    "path_length": len(path),
                    "normalized_dtw_pp": score_pp,
                }
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

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

    fig = plt.figure(figsize=(11.8, 10.6))
    grid = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.88], hspace=0.43, wspace=0.18)
    panels = [
        ("现实基准", observed, "a"),
        ("Random（3-seed均值）", mean_matrices["random"], "b"),
        ("Chronological（3-seed均值）", mean_matrices["chronological"], "c"),
        ("Interest（3-seed均值）", mean_matrices["interest"], "d"),
    ]
    axes = []
    for index, (title, values, label) in enumerate(panels):
        ax = fig.add_subplot(grid[index // 2, index % 2])
        plot_composition_panel(ax, values, weeks, title, label)
        axes.append(ax)
    for ax in (axes[0], axes[2]):
        ax.set_ylabel("内容构成")
    for ax in (axes[1], axes[3]):
        ax.tick_params(labelleft=False)
    for ax in (axes[2], axes[3]):
        ax.set_xlabel("周次")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        fontsize=9.5,
    )

    ax = fig.add_subplot(grid[2, :])
    present = armplot.ARMS
    y = np.arange(len(present))
    means = [statistics.fmean(scores[arm]) for arm in present]
    lower = [mean - min(scores[arm]) for mean, arm in zip(means, present)]
    upper = [max(scores[arm]) - mean for mean, arm in zip(means, present)]
    colors = [armplot.ARM_COLOR[arm] for arm in present]
    ax.barh(y, means, height=0.54, color=colors, alpha=0.9, edgecolor="white", zorder=2)
    ax.errorbar(
        means,
        y,
        xerr=[lower, upper],
        fmt="none",
        ecolor="#222222",
        elinewidth=1.2,
        capsize=5,
        zorder=4,
    )
    offsets = [-0.10, 0.0, 0.10]
    for yi, arm, mean, color in zip(y, present, means, colors):
        for offset, value in zip(offsets, scores[arm]):
            ax.scatter(
                value,
                yi + offset,
                s=34,
                color="#222222",
                edgecolor="white",
                linewidth=0.6,
                zorder=5,
            )
        ax.text(
            max(scores[arm]) + 0.55,
            yi,
            f"{mean:.1f}",
            color=color,
            fontweight="bold",
            va="center",
            fontsize=10.5,
        )
    best_index = int(np.argmin(means))
    ax.text(
        means[best_index] * 0.50,
        best_index,
        "均值最低",
        color="white",
        fontweight="bold",
        va="center",
        ha="center",
        fontsize=9.5,
        zorder=6,
    )
    ax.set_yticks(y, [armplot.ARM_LABEL_EN[arm] for arm in present])
    ax.invert_yaxis()
    ax.set_xlim(0, max(max(values) for values in scores.values()) + 5.0)
    ax.set_xlabel("路径长度归一化的多变量DTW距离（×100；数值越低，拟合越好）")
    ax.set_title(
        "五类内容构成的受限多变量DTW拟合（窗口 = ±1周）\n"
        "条形 = 3-seed均值；点 = 各seed；误差线 = min–max范围",
        fontsize=11.5,
        fontweight="bold",
        pad=6,
    )
    ax.grid(axis="x", color="#E4E4E4", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.text(
        -0.045,
        1.05,
        "e",
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        ha="left",
        va="bottom",
    )

    fig.subplots_adjust(top=0.925, bottom=0.075, left=0.085, right=0.965)
    fig.savefig(PNG_OUT, dpi=300, facecolor="white")
    fig.savefig(SVG_OUT, facecolor="white")
    plt.close(fig)

    summary = {
        "figure_contract": {
            "core_finding": "Interest has the lowest constrained multivariate DTW distance.",
            "evidence": "anchored_v1 3 arms x 3 seeds; W12-W22 Agent-only five-type shares",
            "observed_scope": "five valid content types, noise excluded and renormalized",
            "window_weeks": WINDOW,
            "local_metric": "Euclidean distance between five-dimensional share vectors",
            "normalization": "optimal cumulative cost divided by warping-path length, multiplied by 100",
        },
        "arm_summary_pp": {
            arm: {
                "mean": statistics.fmean(scores[arm]),
                "min": min(scores[arm]),
                "max": max(scores[arm]),
                "seeds": scores[arm],
            }
            for arm in armplot.ARMS
        },
        "paths": paths,
        "outputs": {"png": str(PNG_OUT), "svg": str(SVG_OUT), "csv": str(CSV_OUT)},
    }
    JSON_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    for arm in armplot.ARMS:
        values = scores[arm]
        print(
            f"{arm}: mean={statistics.fmean(values):.3f} pp, "
            f"range={min(values):.3f}--{max(values):.3f} pp"
        )
    print(PNG_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
