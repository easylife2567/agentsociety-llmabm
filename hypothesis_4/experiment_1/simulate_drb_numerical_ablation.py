#!/usr/bin/env python3
"""D/R/B 机制的配对数值消融（不调用 LLM，不启动正式 AgentSociety run）。

复用 ``calibrate_speak.simulate`` 与正式环境共享的纯函数，冻结 anchored_v1
已标定参数，并在相同 100 个随机种子下比较：

    full: U = B + R(D-B)
    no_B: U = RD
    no_D: U = B + R(1-B)
    no_R: U = D

输出长表、汇总表、机读摘要和一张 publication-ready 复合图。所有产物均标注为
numerical proxy，不能替代正式 ABM/LLM 实验结果。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import calibrate_speak as cal
import predict_anchored_utility as anchored

OUT_ROOT = SCRIPT_DIR / "results" / "numerical_ablation_drb"
DATA_DIR = OUT_ROOT / "data"
CHART_DIR = OUT_ROOT / "charts"
LONG_CSV = DATA_DIR / "drb_ablation_seed_week_type.csv"
SUMMARY_CSV = DATA_DIR / "drb_ablation_weekly_summary.csv"
SUMMARY_JSON = DATA_DIR / "drb_ablation_summary.json"
FIGURE_PNG = CHART_DIR / "figure_01_drb_numerical_ablation.png"
FIGURE_SVG = CHART_DIR / "figure_01_drb_numerical_ablation.svg"

WEEKS = cal.WEEKS
TYPES = cal.TYPE_ORDER
TYPE_LABEL = {
    "meme": "Meme",
    "mourning": "Mourning",
    "marketing": "Marketing",
    "education": "Education",
    "other": "Other",
}
CONDITIONS = {
    "full": {
        "label": "Full (B+D+R)",
        "formula": "U=B+R(D-B)",
        "spiral_mult": None,
        "decay_mult": 1.0,
        "baseline": "calibrated",
    },
    "no_B": {
        "label": "No B",
        "formula": "U=RD",
        "spiral_mult": None,
        "decay_mult": 1.0,
        "baseline": "zero",
    },
    "no_D": {
        "label": "No D (D=1)",
        "formula": "U=B+R(1-B)",
        "spiral_mult": 0.0,
        "decay_mult": 1.0,
        "baseline": "calibrated",
    },
    "no_R": {
        "label": "No R (R=1)",
        "formula": "U=D",
        "spiral_mult": None,
        "decay_mult": 0.0,
        "baseline": "calibrated",
    },
}
COLORS = {
    "full": "#0072B2",
    "no_B": "#D55E00",
    "no_D": "#009E73",
    "no_R": "#CC79A7",
}
PERIODS = {
    "Event W13-W15": ["2026-W13", "2026-W14", "2026-W15"],
    "Transition W16-W19": ["2026-W16", "2026-W17", "2026-W18", "2026-W19"],
    "Late W20-W22": ["2026-W20", "2026-W21", "2026-W22"],
}


def mean_ci95(values: list[float]) -> tuple[float, float, float, float]:
    """Return mean, population SD, and normal-approximation 95% CI."""
    mean = statistics.mean(values)
    sd = statistics.pstdev(values)
    half = 1.96 * sd / math.sqrt(len(values))
    return mean, sd, mean - half, mean + half


def load_frozen_parameters() -> tuple[float, dict[str, float], dict[str, float]]:
    doc = json.loads(anchored.JSON_PATH.read_text(encoding="utf-8"))
    params = doc["parameters"]
    alpha_d = float(params["alpha_D"])
    baseline = {str(k): float(v) for k, v in params["baseline_utility"].items()}
    lambdas = {str(k): float(v) for k, v in params["lambda_mean"].items()}
    if set(baseline) != set(TYPES) or set(lambdas) != set(TYPES):
        raise ValueError("Frozen anchored_v1 parameters do not cover all five agent types")
    return alpha_d, baseline, lambdas


def run_simulation(seeds: list[int]) -> tuple[list[dict], dict]:
    alpha_d, baseline, lambdas = load_frozen_parameters()
    anchored.set_lambda_means(lambdas)
    zero_baseline = {t: 0.0 for t in TYPES}
    rows: list[dict] = []
    runs: dict[str, dict[int, dict]] = {c: {} for c in CONDITIONS}

    for seed in seeds:
        for condition, spec in CONDITIONS.items():
            baseline_map = zero_baseline if spec["baseline"] == "zero" else baseline
            spiral_mult = alpha_d if spec["spiral_mult"] is None else spec["spiral_mult"]
            result, trace, climates = cal.simulate(
                cal.BASE_REF,
                "normal",
                rng_seed=seed,
                spiral_mult=spiral_mult,
                decay_mult=float(spec["decay_mult"]),
                utility_mode="anchored",
                baseline_utility=baseline_map,
            )
            runs[condition][seed] = {
                "result": result,
                "trace": trace,
                "climates": climates,
            }
            for week in WEEKS:
                total = sum(result[week].values())
                for agent_type in TYPES:
                    supply = int(result[week][agent_type])
                    rows.append(
                        {
                            "seed": seed,
                            "condition": condition,
                            "week": week,
                            "agent_type": agent_type,
                            "supply": supply,
                            "total_supply": total,
                            "representation_share": supply / total if total else 0.0,
                        }
                    )
    metadata = {
        "alpha_D": alpha_d,
        "baseline_utility": baseline,
        "lambda_mean": lambdas,
        "decay_scale": cal.mech.DEFAULT_DECAY_SCALE,
    }
    return rows, {"runs": runs, "parameters": metadata}


def write_long_csv(rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LONG_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict], simulation: dict, seeds: list[int]) -> dict:
    index = {
        (int(row["seed"]), str(row["condition"]), str(row["week"]), str(row["agent_type"])): row
        for row in rows
    }
    weekly: list[dict] = []
    for condition in CONDITIONS:
        for week in WEEKS:
            total_values = [
                sum(index[(seed, condition, week, t)]["supply"] for t in TYPES)
                for seed in seeds
            ]
            total_mean, total_sd, total_lo, total_hi = mean_ci95(total_values)
            meme_shares = [
                index[(seed, condition, week, "meme")]["supply"] / total
                if (total := sum(index[(seed, condition, week, t)]["supply"] for t in TYPES))
                else 0.0
                for seed in seeds
            ]
            meme_mean, meme_sd, meme_lo, meme_hi = mean_ci95(meme_shares)
            for agent_type in TYPES:
                values = [index[(seed, condition, week, agent_type)]["supply"] for seed in seeds]
                mean, sd, lo, hi = mean_ci95(values)
                weekly.append(
                    {
                        "condition": condition,
                        "week": week,
                        "agent_type": agent_type,
                        "mean_supply": mean,
                        "sd_supply": sd,
                        "ci95_low_supply": lo,
                        "ci95_high_supply": hi,
                        "mean_total_supply": total_mean,
                        "sd_total_supply": total_sd,
                        "ci95_low_total_supply": total_lo,
                        "ci95_high_total_supply": total_hi,
                        "mean_meme_share": meme_mean,
                        "sd_meme_share": meme_sd,
                        "ci95_low_meme_share": meme_lo,
                        "ci95_high_meme_share": meme_hi,
                    }
                )

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(weekly[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(weekly)

    paired_effects: dict[str, dict] = {}
    for condition in ("no_B", "no_D", "no_R"):
        period_doc: dict[str, dict] = {}
        for period, weeks in PERIODS.items():
            type_doc: dict[str, dict] = {}
            for agent_type in TYPES:
                diffs = [
                    statistics.mean(
                        index[(seed, condition, week, agent_type)]["supply"]
                        / cal.POPULATION_COUNTS[agent_type]
                        - index[(seed, "full", week, agent_type)]["supply"]
                        / cal.POPULATION_COUNTS[agent_type]
                        for week in weeks
                    )
                    for seed in seeds
                ]
                mean, sd, lo, hi = mean_ci95(diffs)
                type_doc[agent_type] = {
                    "mean_rate_difference": mean,
                    "sd": sd,
                    "ci95_low": lo,
                    "ci95_high": hi,
                }
            period_doc[period] = type_doc
        paired_effects[condition] = period_doc

    key_diagnostics = {}
    diagnostic_specs = {
        "no_B_late_total_rate": ("no_B", PERIODS["Late W20-W22"], "total_rate"),
        "no_D_late_meme_rate": ("no_D", PERIODS["Late W20-W22"], "meme_rate"),
        "no_R_transition_total_rate": ("no_R", PERIODS["Transition W16-W19"], "total_rate"),
    }
    for name, (condition, weeks, metric) in diagnostic_specs.items():
        diffs = []
        for seed in seeds:
            seed_diffs = []
            for week in weeks:
                if metric == "meme_rate":
                    seed_diffs.append(
                        index[(seed, condition, week, "meme")]["supply"]
                        / cal.POPULATION_COUNTS["meme"]
                        - index[(seed, "full", week, "meme")]["supply"]
                        / cal.POPULATION_COUNTS["meme"]
                    )
                else:
                    cond_total = sum(index[(seed, condition, week, t)]["supply"] for t in TYPES)
                    full_total = sum(index[(seed, "full", week, t)]["supply"] for t in TYPES)
                    seed_diffs.append((cond_total - full_total) / sum(cal.POPULATION_COUNTS.values()))
            diffs.append(statistics.mean(seed_diffs))
        mean, sd, lo, hi = mean_ci95(diffs)
        key_diagnostics[name] = {
            "condition": condition,
            "weeks": weeks,
            "metric": metric,
            "mean_difference": mean,
            "sd": sd,
            "ci95_low": lo,
            "ci95_high": hi,
        }

    doc = {
        "artifact_status": "numerical_proxy_ablation_not_formal_abm_or_llm_run",
        "generated_by": Path(__file__).name,
        "formula": "U=B+R(D-B)",
        "conditions": CONDITIONS,
        "design": {
            "paired_seed_count": len(seeds),
            "seed_start": min(seeds),
            "seed_end": max(seeds),
            "weeks": WEEKS,
            "agent_count": sum(cal.POPULATION_COUNTS.values()),
            "agent_type_counts": cal.POPULATION_COUNTS,
            "recommendation_regime": "interest numerical proxy",
            "llm_calls": 0,
        },
        "frozen_parameters": simulation["parameters"],
        "paired_effects": paired_effects,
        "key_diagnostics": key_diagnostics,
        "limitations": [
            "This is a mechanism-isomorphic numerical proxy, not a formal AgentSociety/LLM run.",
            "Agent post type is proxied by the author's fixed type, so representation share is a supply-composition proxy.",
            "Normal-approximation 95% CIs quantify Monte Carlo uncertainty across paired seeds, not population sampling uncertainty.",
            "One-at-a-time ablations estimate total changes after endogenous feed feedback; they do not identify higher-order interactions.",
        ],
    }
    SUMMARY_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"weekly": weekly, "doc": doc}


def weekly_lookup(summary: list[dict]) -> dict[tuple[str, str, str], dict]:
    return {(r["condition"], r["week"], r["agent_type"]): r for r in summary}


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=12,
            fontweight="bold", ha="left", va="bottom")


def plot(summary: dict) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 9.5,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 1.0,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    lookup = weekly_lookup(summary["weekly"])
    x = np.arange(len(WEEKS))
    fig = plt.figure(figsize=(14.5, 9.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], hspace=0.34, wspace=0.20)
    ax_total = fig.add_subplot(gs[0, 0])
    ax_meme = fig.add_subplot(gs[0, 1])
    heat_gs = gs[1, :].subgridspec(1, 3, wspace=0.12)
    heat_axes = [fig.add_subplot(heat_gs[0, i]) for i in range(3)]

    for condition, spec in CONDITIONS.items():
        total_mean = np.array([lookup[(condition, w, "meme")]["mean_total_supply"] for w in WEEKS])
        total_lo = np.array([lookup[(condition, w, "meme")]["ci95_low_total_supply"] for w in WEEKS])
        total_hi = np.array([lookup[(condition, w, "meme")]["ci95_high_total_supply"] for w in WEEKS])
        meme_mean = np.array([lookup[(condition, w, "meme")]["mean_meme_share"] * 100 for w in WEEKS])
        meme_lo = np.array([lookup[(condition, w, "meme")]["ci95_low_meme_share"] * 100 for w in WEEKS])
        meme_hi = np.array([lookup[(condition, w, "meme")]["ci95_high_meme_share"] * 100 for w in WEEKS])
        for ax in (ax_total, ax_meme):
            ax.axvspan(6.5, 10.5, color="#ECECEC", alpha=0.55, zorder=0)
        ax_total.plot(x, total_mean, color=COLORS[condition], lw=2.0,
                      marker="o" if condition == "full" else None,
                      markersize=4.0, label=spec["label"])
        ax_total.fill_between(x, total_lo, total_hi, color=COLORS[condition], alpha=0.10, linewidth=0)
        ax_meme.plot(x, meme_mean, color=COLORS[condition], lw=2.0,
                     marker="o" if condition == "full" else None,
                     markersize=4.0, label=spec["label"])
        ax_meme.fill_between(x, meme_lo, meme_hi, color=COLORS[condition], alpha=0.10, linewidth=0)

    week_labels = [w[-3:] for w in WEEKS]
    for ax in (ax_total, ax_meme):
        ax.axvline(1, color="#777777", ls=":", lw=1.1)
        ax.axvline(7, color="#777777", ls=":", lw=1.1)
        ax.set_xticks(x, week_labels)
        ax.set_xlabel("Week")
    ax_total.set_title("Weekly agent supply", fontweight="bold")
    ax_total.set_ylabel("Speaking agents per week (mean)")
    ax_total.set_ylim(bottom=0)
    ax_total.legend(ncol=2, loc="upper right")
    ax_meme.set_title("Meme representation among agent supply", fontweight="bold")
    ax_meme.set_ylabel("Meme share (%)")
    ax_meme.set_ylim(bottom=0)
    ax_meme.legend(ncol=2, loc="upper left")
    add_panel_label(ax_total, "a")
    add_panel_label(ax_meme, "b")

    paired = summary["doc"]["paired_effects"]
    matrices = []
    for condition in ("no_B", "no_D", "no_R"):
        matrix = np.array(
            [
                [paired[condition][period][t]["mean_rate_difference"] * 100 for t in TYPES]
                for period in PERIODS
            ]
        )
        matrices.append(matrix)
    vmax = max(abs(float(np.nanmin(m))) for m in matrices)
    vmax = max(vmax, max(abs(float(np.nanmax(m))) for m in matrices))
    vmax = math.ceil(vmax / 5.0) * 5.0
    image = None
    for idx, (condition, matrix, ax) in enumerate(zip(("no_B", "no_D", "no_R"), matrices, heat_axes)):
        image = ax.imshow(matrix, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.grid(False)
        ax.set_xticks(np.arange(len(TYPES)), [TYPE_LABEL[t] for t in TYPES], rotation=28, ha="right")
        ax.set_yticks(np.arange(len(PERIODS)), list(PERIODS) if idx == 0 else ["", "", ""])
        ax.set_title(CONDITIONS[condition]["label"], color=COLORS[condition], fontweight="bold")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                ax.text(j, i, f"{value:+.1f}", ha="center", va="center",
                        color="white" if abs(value) > vmax * 0.53 else "#222222", fontsize=8.5)
    add_panel_label(heat_axes[0], "c")
    heat_axes[0].set_ylabel("Period")
    cbar = fig.colorbar(image, ax=heat_axes, orientation="horizontal", fraction=0.065, pad=0.22, aspect=45)
    cbar.set_label("Change vs full model (percentage points in type-specific speaking rate)")

    fig.suptitle("D/R/B numerical ablation: distinct temporal and category signatures",
                 fontsize=15, fontweight="bold", y=0.985)
    fig.text(
        0.5,
        0.012,
        "Numerical proxy only; no LLM calls. Lines show means and 95% Monte Carlo CIs over 100 paired seeds. "
        "Gray area: held-out weeks W19-W22. Heatmaps average paired differences within each period.",
        ha="center",
        va="bottom",
        fontsize=8.6,
        color="#444444",
    )
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PNG, dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(FIGURE_SVG, bbox_inches="tight", facecolor="white")
    # Matplotlib writes path commands with trailing spaces. Normalize the generated
    # text artifact so repository whitespace checks stay useful.
    svg_text = FIGURE_SVG.read_text(encoding="utf-8")
    FIGURE_SVG.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run paired numerical D/R/B ablations without LLM calls")
    parser.add_argument("--seeds", type=int, default=100, help="Number of paired seeds (default: 100)")
    parser.add_argument("--seed-start", type=int, default=3000, help="First seed (default: 3000)")
    args = parser.parse_args()
    if args.seeds < 2:
        raise SystemExit("--seeds must be at least 2")
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    rows, simulation = run_simulation(seeds)
    write_long_csv(rows)
    summary = summarize(rows, simulation, seeds)
    plot(summary)
    print(json.dumps({
        "status": "ok",
        "llm_calls": 0,
        "paired_seeds": len(seeds),
        "data_dir": str(DATA_DIR),
        "chart_dir": str(CHART_DIR),
        "figure": str(FIGURE_PNG),
        "key_diagnostics": summary["doc"]["key_diagnostics"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
