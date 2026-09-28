#!/usr/bin/env python3
"""Aggregate weekly_lag1 runs and render claim-focused comparison figures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "hypothesis_4" / "experiment_1" / "runs" / "weekly_lag1"
SOURCE_ROOT = RUN_ROOT / "_derived" / "data"
OUTPUT_ROOT = ROOT / "presentation" / "hypothesis_4"
DATA_DIR = OUTPUT_ROOT / "data"
FINAL_CHART_DIR = OUTPUT_ROOT / "charts"

ARMS = ("interest", "random")
ARM_COLORS = {"interest": "#0072B2", "random": "#D55E00"}
METRICS = (
    "supply_share_meme",
    "exposure_share_meme",
    "meme_spoke_rate",
    "bias_meme",
    "supply_share_mourning",
    "exposure_share_mourning",
    "total_supply",
)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _run_meta(run_id: str) -> tuple[str, int]:
    match = re.fullmatch(r"weekly_lag1_(interest|random)_s([0-2])", run_id)
    if not match:
        raise ValueError(f"Unexpected run id: {run_id}")
    return match.group(1), int(match.group(2))


def load_run(run_dir: Path) -> pd.DataFrame:
    arm, seed = _run_meta(run_dir.name)
    supply = _read_csv(run_dir / "weekly_supply.csv").rename(
        columns={
            "supply_share_all_meme": "supply_share_meme",
            "supply_share_all_mourning": "supply_share_mourning",
        }
    )
    exposure = _read_csv(run_dir / "weekly_exposure.csv")
    behavior = _read_csv(run_dir / "weekly_agent_behavior.csv")
    behavior = behavior.loc[behavior["type"] == "meme", ["week", "spoke_rate"]].rename(
        columns={"spoke_rate": "meme_spoke_rate"}
    )
    bias = _read_csv(run_dir / "weekly_bias.csv")[["week", "bias_meme"]]
    benchmark = _read_csv(run_dir / "weekly_benchmark.csv")
    benchmark = benchmark.loc[
        benchmark["type"].isin(["meme", "mourning"]),
        ["week", "type", "bench_share_clean"],
    ].pivot(index="week", columns="type", values="bench_share_clean")
    benchmark = benchmark.rename(
        columns={
            "meme": "benchmark_meme_share",
            "mourning": "benchmark_mourning_share",
        }
    ).reset_index()

    keep_supply = [
        "week",
        "total_supply",
        "supply_share_meme",
        "supply_share_mourning",
    ]
    keep_exposure = [
        "week",
        "exposure_share_meme",
        "exposure_share_mourning",
    ]
    out = supply[keep_supply]
    for frame in (exposure[keep_exposure], behavior, bias, benchmark):
        out = out.merge(frame, on="week", how="inner", validate="one_to_one")
    out.insert(0, "run_id", run_dir.name)
    out.insert(1, "arm", arm)
    out.insert(2, "seed", seed)
    out.insert(4, "week_num", out["week"].str.extract(r"W(\d+)")[0].astype(int))
    if len(out) != 11:
        raise ValueError(f"{run_dir.name}: expected 11 weeks, got {len(out)}")
    return out


def aggregate_runs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    run_dirs = sorted(path for path in SOURCE_ROOT.glob("weekly_lag1_*") if path.is_dir())
    if len(run_dirs) != 6:
        raise ValueError(f"Expected 6 derived run directories, got {len(run_dirs)}")
    run_week = pd.concat([load_run(path) for path in run_dirs], ignore_index=True)
    counts = run_week.groupby("arm")["run_id"].nunique().to_dict()
    if counts != {"interest": 3, "random": 3}:
        raise ValueError(f"Expected three seeds per arm, got {counts}")

    grouped = run_week.groupby(["arm", "week", "week_num"], sort=True)
    arm_week = grouped[list(METRICS)].agg(["mean", "min", "max", "std"])
    arm_week.columns = [f"{metric}_{stat}" for metric, stat in arm_week.columns]
    arm_week = arm_week.reset_index().sort_values(["arm", "week_num"])

    bench = (
        run_week.groupby(["week", "week_num"])[
            ["benchmark_meme_share", "benchmark_mourning_share"]
        ]
        .mean()
        .reset_index()
        .sort_values("week_num")
    )
    arm_week = arm_week.merge(bench, on=["week", "week_num"], how="left")

    late = run_week.loc[run_week["week_num"].between(19, 22)]
    per_seed_late = late.groupby(["arm", "seed"])[list(METRICS)].mean().reset_index()
    late_summary: dict[str, dict[str, dict[str, float]]] = {}
    for arm in ARMS:
        subset = per_seed_late.loc[per_seed_late["arm"] == arm]
        late_summary[arm] = {}
        for metric in METRICS:
            values = subset[metric]
            late_summary[arm][metric] = {
                "mean": float(values.mean()),
                "min": float(values.min()),
                "max": float(values.max()),
            }

    arm_week_indexed = arm_week.set_index(["arm", "week_num"])
    gap = {}
    for metric in ("supply_share_meme", "exposure_share_meme", "meme_spoke_rate", "bias_meme"):
        interest = arm_week_indexed.loc["interest", f"{metric}_mean"]
        random = arm_week_indexed.loc["random", f"{metric}_mean"]
        late_weeks = [week for week in interest.index if 19 <= week <= 22]
        gap[metric] = float((interest.loc[late_weeks] - random.loc[late_weeks]).mean())

    fit = {}
    for arm in ARMS:
        subset = arm_week.loc[arm_week["arm"] == arm]
        diff = subset["supply_share_meme_mean"] - subset["benchmark_meme_share"]
        late_diff = diff.loc[subset["week_num"].between(19, 22)]
        fit[arm] = {
            "meme_supply_rmse_all_weeks": float(np.sqrt(np.mean(np.square(diff)))),
            "meme_supply_rmse_w19_w22": float(np.sqrt(np.mean(np.square(late_diff)))),
        }

    summary = {
        "batch": "weekly_lag1",
        "run_count": 6,
        "seeds_per_arm": 3,
        "weeks": [f"2026-W{week:02d}" for week in range(12, 23)],
        "uncertainty_display": "min-max across three seeds; not a confidence interval",
        "late_period_w19_w22": late_summary,
        "interest_minus_random_late_period": gap,
        "benchmark_fit": fit,
        "limitations": [
            "Three seeds per arm; ranges are descriptive.",
            "Chronological was not rerun under weekly_lag1 and is excluded.",
            "Simulation comparison does not establish an external real-platform causal effect.",
        ],
    }
    return run_week, arm_week, summary


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "#D9D9D9",
            "grid.linewidth": 0.7,
            "grid.alpha": 0.65,
            "legend.frameon": False,
            "svg.fonttype": "none",
        }
    )


def _decorate_time(ax: plt.Axes, weeks: list[int]) -> None:
    event_x = weeks.index(13)
    late_start = weeks.index(19)
    ax.axvline(event_x, color="#555555", lw=1, ls=":", alpha=0.9)
    ax.axvspan(late_start - 0.45, len(weeks) - 0.55, color="#F3E8FF", alpha=0.5, zorder=0)
    ax.set_xticks(range(len(weeks)))
    ax.set_xticklabels([f"W{week}" for week in weeks], rotation=0)


def _series_panel(
    ax: plt.Axes,
    arm_week: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    benchmark: str | None = None,
    percent: bool = True,
) -> None:
    weeks = sorted(arm_week["week_num"].unique())
    x = np.arange(len(weeks))
    scale = 100 if percent else 1
    for arm in ARMS:
        subset = arm_week.loc[arm_week["arm"] == arm].sort_values("week_num")
        mean = subset[f"{metric}_mean"].to_numpy(dtype=float) * scale
        low = subset[f"{metric}_min"].to_numpy(dtype=float) * scale
        high = subset[f"{metric}_max"].to_numpy(dtype=float) * scale
        ax.fill_between(x, low, high, color=ARM_COLORS[arm], alpha=0.14, linewidth=0)
        ax.plot(x, mean, color=ARM_COLORS[arm], lw=2.2, marker="o", ms=3.8, label=arm.title())
    if benchmark:
        bench = (
            arm_week.loc[arm_week["arm"] == "interest"]
            .sort_values("week_num")[benchmark]
            .to_numpy(dtype=float)
            * scale
        )
        ax.plot(x, bench, color="#222222", lw=1.8, ls="--", marker="s", ms=3.2, label="Observed benchmark")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_ylabel(ylabel)
    _decorate_time(ax, weeks)


def render_figures(
    arm_week: pd.DataFrame,
    summary: dict,
    chart_dir: Path,
    filename_prefix: str,
) -> list[Path]:
    _style()
    chart_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.4), constrained_layout=True)
    _series_panel(
        axes[0, 0],
        arm_week,
        "supply_share_meme",
        "A  Meme share in total content supply",
        "Share (%)",
        benchmark="benchmark_meme_share",
    )
    _series_panel(
        axes[0, 1],
        arm_week,
        "exposure_share_meme",
        "B  Meme share in feed exposure",
        "Share (%)",
    )
    _series_panel(
        axes[1, 0],
        arm_week,
        "meme_spoke_rate",
        "C  Meme-agent speaking rate",
        "Agents speaking (%)",
    )
    _series_panel(
        axes[1, 1],
        arm_week,
        "bias_meme",
        "D  Curation bias for meme content",
        "Exposure minus supply (pp)",
    )
    axes[1, 1].axhline(0, color="#555555", lw=1)
    for ax in axes.flat:
        ax.set_xlabel("Simulation week")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.025))
    fig.suptitle(
        "One-week content lag: interest curation vs random feed",
        fontsize=15,
        fontweight="bold",
        y=1.07,
    )
    fig.text(
        0.5,
        -0.015,
        "Lines are 3-seed means; bands show seed min-max (descriptive, not confidence intervals). "
        "Vertical line: W13 obituary event; shaded area: W19-W22 late meme wave.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    base = chart_dir / f"{filename_prefix}figure_01_weekly_lag_meme_trajectory"
    for suffix in (".png", ".svg"):
        path = base.with_suffix(suffix)
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        outputs.append(path)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.4), constrained_layout=True)
    _series_panel(
        axes[0, 0],
        arm_week,
        "supply_share_mourning",
        "A  Mourning share in total content supply",
        "Share (%)",
        benchmark="benchmark_mourning_share",
    )
    _series_panel(
        axes[0, 1],
        arm_week,
        "total_supply",
        "B  Total weekly content supply",
        "Posts",
        percent=False,
    )

    weeks = sorted(arm_week["week_num"].unique())
    x = np.arange(len(weeks))
    indexed = arm_week.set_index(["arm", "week_num"])
    for metric, label, color in (
        ("supply_share_meme", "Meme supply gap", "#6A3D9A"),
        ("exposure_share_meme", "Meme exposure gap", "#009E73"),
        ("meme_spoke_rate", "Meme speaking gap", "#CC79A7"),
    ):
        interest = indexed.loc["interest", f"{metric}_mean"].reindex(weeks)
        random = indexed.loc["random", f"{metric}_mean"].reindex(weeks)
        axes[1, 0].plot(x, (interest - random) * 100, marker="o", ms=3.8, lw=2, label=label, color=color)
    axes[1, 0].axhline(0, color="#555555", lw=1)
    axes[1, 0].set_title("C  Interest minus random", loc="left", fontweight="bold")
    axes[1, 0].set_ylabel("Difference (pp)")
    axes[1, 0].set_xlabel("Simulation week")
    axes[1, 0].legend(loc="upper left")
    _decorate_time(axes[1, 0], weeks)

    late = summary["late_period_w19_w22"]
    labels = ["Meme supply", "Meme exposure", "Meme speaking"]
    metrics = ["supply_share_meme", "exposure_share_meme", "meme_spoke_rate"]
    positions = np.arange(len(labels))
    width = 0.34
    for offset, arm in ((-width / 2, "interest"), (width / 2, "random")):
        values = [late[arm][metric]["mean"] * 100 for metric in metrics]
        low = [late[arm][metric]["min"] * 100 for metric in metrics]
        high = [late[arm][metric]["max"] * 100 for metric in metrics]
        yerr = np.array([[v - lo for v, lo in zip(values, low)], [hi - v for v, hi in zip(values, high)]])
        axes[1, 1].bar(
            positions + offset,
            values,
            width,
            color=ARM_COLORS[arm],
            alpha=0.88,
            label=arm.title(),
            yerr=yerr,
            capsize=3,
        )
    axes[1, 1].set_xticks(positions)
    axes[1, 1].set_xticklabels(labels)
    axes[1, 1].set_ylabel("W19-W22 mean (%)")
    axes[1, 1].set_title("D  Late-wave summary", loc="left", fontweight="bold")
    axes[1, 1].legend()

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.025))
    for ax in axes[0, :]:
        ax.set_xlabel("Simulation week")
    fig.suptitle(
        "Event response and late-wave differences",
        fontsize=15,
        fontweight="bold",
        y=1.07,
    )
    fig.text(
        0.5,
        -0.015,
        "Simulation evidence from weekly_lag1; n=3 seeds per arm. Error bars and bands are seed min-max.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    base = chart_dir / f"{filename_prefix}figure_02_weekly_lag_event_and_arm_gap"
    for suffix in (".png", ".svg"):
        path = base.with_suffix(suffix)
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        outputs.append(path)
    plt.close(fig)
    return outputs


def write_caption() -> Path:
    path = DATA_DIR / "weekly_lag1_figure_notes.md"
    path.write_text(
        "# weekly_lag1 figure notes\n\n"
        "- **Figure 1:** Three-seed arm means for meme supply, exposure, meme-agent speaking, and exposure-minus-supply bias. "
        "The real-data benchmark appears only where an aligned observed supply share exists.\n"
        "- **Figure 2:** Mourning response, total supply, weekly interest-minus-random gaps, and W19-W22 mean comparisons.\n"
        "- Bands and error bars are the minimum and maximum across three seeds. They are descriptive ranges, not confidence intervals.\n"
        "- Source: all six completed `weekly_lag1_{interest,random}_s{0,1,2}` runs. "
        "The non-rerun chronological arm is excluded.\n",
        encoding="utf-8",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-only", action="store_true")
    parser.add_argument(
        "--final",
        action="store_true",
        help="Write approved final charts under presentation/hypothesis_4/charts.",
    )
    args = parser.parse_args()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    run_week, arm_week, summary = aggregate_runs()
    run_week.to_csv(DATA_DIR / "weekly_lag1_run_week_metrics.csv", index=False)
    arm_week.to_csv(DATA_DIR / "weekly_lag1_arm_week_summary.csv", index=False)
    (DATA_DIR / "weekly_lag1_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_caption()
    if not args.data_only:
        if args.final:
            render_figures(arm_week, summary, FINAL_CHART_DIR, "")
        else:
            render_figures(arm_week, summary, DATA_DIR, "eda_")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
