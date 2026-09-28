#!/usr/bin/env python3
"""Compare formal anchored and one-week-lag runs for timing-design review."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-matplotlib")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/_derived/data"
LAG = ROOT / "archive/hypothesis_4_experiment_1_batches/formal_superseded/weekly_lag1/_derived/data"
WEEKS = [f"2026-W{week:02d}" for week in range(12, 23)]
TYPES = ["marketing", "education", "other", "mourning", "meme"]
COLORS = {
    "marketing": "#E69F00",
    "education": "#009E73",
    "other": "#888888",
    "mourning": "#0072B2",
    "meme": "#D55E00",
}


def load_behavior(path: Path) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    with path.open(encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            result.setdefault(row["week"], {})[row["type"]] = (
                float(row["n_agents"]) * float(row["spoke_rate"])
            )
    return result


def run_path(round_name: str, arm: str, seed: int) -> Path:
    base = ARCHIVE if round_name == "anchored_v1" else LAG
    return base / f"{round_name}_{arm}_s{seed}" / "weekly_agent_behavior.csv"


def total_series(data: dict[str, dict[str, float]]) -> np.ndarray:
    return np.asarray([sum(data[week].values()) for week in WEEKS], dtype=float)


def mean_series(round_name: str, arm: str) -> np.ndarray:
    return np.mean(
        [total_series(load_behavior(run_path(round_name, arm, seed))) for seed in range(3)],
        axis=0,
    )


def aligned_metrics(anchored: np.ndarray, lagged: np.ndarray) -> dict[str, float]:
    raw_corr = float(np.corrcoef(anchored, lagged)[0, 1])
    raw_rmse = float(np.sqrt(np.mean((anchored - lagged) ** 2)))
    aligned_a = anchored[:-1]
    aligned_l = lagged[1:]
    return {
        "raw_correlation": raw_corr,
        "raw_rmse": raw_rmse,
        "one_week_aligned_correlation": float(np.corrcoef(aligned_a, aligned_l)[0, 1]),
        "one_week_aligned_rmse": float(np.sqrt(np.mean((aligned_a - aligned_l) ** 2))),
    }


def write_comparison_csv(path: Path, series: dict[tuple[str, str], np.ndarray]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "arm", "week", "anchored_formal_mean", "lag1_formal_mean",
            "lag1_shifted_back_one_week_mean",
        ])
        for arm in ("interest", "random"):
            anchored = series[("anchored_v1", arm)]
            lagged = series[("weekly_lag1", arm)]
            for index, week in enumerate(WEEKS):
                shifted = lagged[index + 1] if index + 1 < len(lagged) else ""
                writer.writerow([arm, week, anchored[index], lagged[index], shifted])


def render(path: Path, series: dict[tuple[str, str], np.ndarray], metrics: dict) -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": 300,
        "svg.fonttype": "none",
    })
    fig = plt.figure(figsize=(13, 9))
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 1.12), hspace=0.32, wspace=0.22)
    x = np.arange(len(WEEKS))
    labels = [week.replace("2026-", "") for week in WEEKS]

    for column, arm in enumerate(("interest", "random")):
        axis = fig.add_subplot(grid[0, column])
        anchored = series[("anchored_v1", arm)]
        lagged = series[("weekly_lag1", arm)]
        axis.plot(x, anchored, marker="o", color="#222222", linewidth=2,
                  label="Anchored formal")
        axis.plot(x, lagged, marker="o", color="#4C78A8", linewidth=2,
                  label="Lag-1 formal (action week)")
        axis.plot(x[:-1], lagged[1:], marker="s", color="#4C78A8", linewidth=1.5,
                  linestyle="--", alpha=0.8, label="Lag-1 shifted back 1 week")
        m = metrics[arm]
        axis.text(
            0.02, 0.96,
            f"aligned r={m['one_week_aligned_correlation']:.3f}, "
            f"RMSE={m['one_week_aligned_rmse']:.2f}",
            transform=axis.transAxes, va="top", color="#444444",
        )
        axis.set_title(f"{arm.capitalize()} arm — 3-seed formal means", loc="left")
        axis.set_xticks(x)
        axis.set_xticklabels(labels, rotation=45, ha="right")
        axis.set_ylabel("Agent posts")
        axis.grid(axis="y", alpha=0.3)
        if column == 0:
            axis.legend(frameon=False, fontsize=8)

    axis = fig.add_subplot(grid[1, :])
    anchored_s0 = load_behavior(run_path("anchored_v1", "interest", 0))
    lag_s0 = load_behavior(run_path("weekly_lag1", "interest", 0))
    bars = [
        ("Anchored W13", anchored_s0["2026-W13"]),
        ("Lag-1 W13", lag_s0["2026-W13"]),
        ("Lag-1 W14", lag_s0["2026-W14"]),
        ("Lag-1 W15", lag_s0["2026-W15"]),
    ]
    bottom = np.zeros(len(bars))
    for post_type in TYPES:
        values = np.asarray([item[1].get(post_type, 0.0) for item in bars])
        axis.bar(
            np.arange(len(bars)), values, bottom=bottom,
            color=COLORS[post_type], label=post_type.capitalize(), width=0.65,
        )
        bottom += values
    for i, total in enumerate(bottom):
        axis.text(i, total + 0.8, f"{total:.0f}", ha="center", fontweight="bold")
    axis.set_ylim(0, float(max(bottom)) * 1.16)
    axis.set_xticks(np.arange(len(bars)))
    axis.set_xticklabels([item[0] for item in bars])
    axis.set_ylabel("Agent posts")
    axis.set_title(
        "Interest s0: the original W13 response is split across W13–W15 by lagging",
        loc="left", pad=12,
    )
    axis.grid(axis="y", alpha=0.3)
    axis.legend(ncol=5, frameon=False, loc="upper right")

    fig.suptitle("Why the one-week injection lag changes the visible curve", fontsize=15,
                 fontweight="bold", y=0.98)
    fig.text(
        0.01, 0.01,
        "Formal replay data only. Dashed lines re-label lagged action output by the prior source week; "
        "they do not alter the simulation.",
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.95))
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    series = {
        (round_name, arm): mean_series(round_name, arm)
        for round_name in ("anchored_v1", "weekly_lag1")
        for arm in ("interest", "random")
    }
    metrics = {
        arm: aligned_metrics(
            series[("anchored_v1", arm)], series[("weekly_lag1", arm)]
        )
        for arm in ("interest", "random")
    }
    write_comparison_csv(args.output_dir / "formal_timing_comparison.csv", series)
    (args.output_dir / "formal_timing_diagnostics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    render(args.output_dir / "formal_timing_rethink", series, metrics)
    print(json.dumps(metrics, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
