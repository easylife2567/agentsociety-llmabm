#!/usr/bin/env python3
"""Predict the revised random-global arm without running an AgentSociety experiment.

This numerical proxy keeps the frozen anchored utility parameters and agent population,
but gives every agent a ten-post uniform sample from every post that has entered the Env
by the current week. It deliberately ignores age, lifecycle, interest, popularity,
exposure saturation, official pinning, and the W13 mourning floor. Future posts remain
unavailable. The interest curve is the existing calibrated proxy and is shown only as a
reference. All outputs are labelled as proxy expectations, never experimental results.
"""

from __future__ import annotations

import copy
import csv
import json
import math
import os
import random
import statistics
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

import calibrate_speak as cal


SCRIPT_DIR = Path(__file__).resolve().parent
PARAM_PATH = SCRIPT_DIR / "data" / "anchored_utility_prediction.json"
OUT_DATA = SCRIPT_DIR / "data" / "random_global_proxy_prediction.csv"
OUT_META = SCRIPT_DIR / "data" / "random_global_proxy_prediction.json"
OUT_PNG = SCRIPT_DIR / "charts" / "prediction" / "PROXY_random_global_expected.png"
OUT_SVG = SCRIPT_DIR / "charts" / "prediction" / "PROXY_random_global_expected.svg"

WEEKS = cal.WEEKS
TYPES = cal.TYPE_ORDER
TYPE_LABEL = {
    "meme": "Meme",
    "mourning": "Mourning",
    "marketing": "Marketing",
    "education": "Education",
    "other": "Other",
}
TYPE_COLOR = {
    "meme": "#D55E00",
    "mourning": "#0072B2",
    "marketing": "#E69F00",
    "education": "#009E73",
    "other": "#56B4E9",
}


def load_parameters() -> tuple[float, dict[str, float], dict[str, float]]:
    doc = json.loads(PARAM_PATH.read_text(encoding="utf-8"))
    params = doc["parameters"]
    return (
        float(params["alpha_D"]),
        {str(k): float(v) for k, v in params["baseline_utility"].items()},
        {str(k): float(v) for k, v in params["lambda_mean"].items()},
    )


def frozen_population(lambdas: dict[str, float]) -> list[dict]:
    """Copy the registered population and align each type mean to frozen lambdas."""
    population = copy.deepcopy(cal.population)
    current_mean = {
        t: statistics.mean(
            a["params"]["decay"] for a in population if a["agent_type"] == t
        )
        for t in TYPES
    }
    for agent in population:
        t = agent["agent_type"]
        agent["params"]["decay"] *= lambdas[t] / current_mean[t]
    return population


def injected_counts() -> dict[str, dict[str, int]]:
    return {
        week: {
            t: sum(1 for post in cal.INJECTED_BY_WEEK[week] if post["type"] == t)
            for t in TYPES
        }
        for week in WEEKS
    }


def simulate_random_global(
    seed: int,
    population: list[dict],
    alpha_d: float,
    baseline: dict[str, float],
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, float]]]:
    """Run an Env-isomorphic decision proxy for the revised random arm."""
    rng = random.Random(seed + 1000)
    cumulative_own = {a["id"]: 0.0 for a in population}
    pool: list[dict[str, str]] = []
    weekly_counts: dict[str, dict[str, int]] = {}
    weekly_climate: dict[str, dict[str, float]] = {}

    for week in WEEKS:
        # Current-week injected posts exist before feeds are assembled.
        pool.extend({"type": post["type"], "week": week} for post in cal.INJECTED_BY_WEEK[week])

        counts = {t: 0 for t in TYPES}
        climate_values: dict[str, list[float]] = {t: [] for t in TYPES}
        next_posts: list[dict[str, str]] = []
        for agent in population:
            t = agent["agent_type"]
            prm = agent["params"]
            take = min(cal.FEED_SIZE, len(pool))
            feed = rng.sample(pool, take) if take else []
            own = sum(1 for post in feed if post["type"] == t)
            share_own = own / len(feed) if feed else 0.0
            climate_values[t].append(share_own)

            d = cal.mech.spiral_factor(
                share_own,
                cal.personas_mod.POP_SHARE[t],
                prm["spiral"] * alpha_d,
            )
            r = cal.mech.fatigue_factor(prm["decay"], cumulative_own[agent["id"]])
            u = cal.mech.anchored_utility(baseline[t], d, r)
            if u >= prm["activity"]:
                counts[t] += 1
                next_posts.append({"type": t, "week": week})
            cumulative_own[agent["id"]] += own

        # Agent posts become visible only from the following week.
        pool.extend(next_posts)
        weekly_counts[week] = counts
        weekly_climate[week] = {
            t: statistics.mean(values) if values else 0.0
            for t, values in climate_values.items()
        }
    return weekly_counts, weekly_climate


def simulate_interest(
    seed: int,
    alpha_d: float,
    baseline: dict[str, float],
    lambdas: dict[str, float],
) -> dict[str, dict[str, int]]:
    """Existing interest proxy, retained unchanged as a visual reference."""
    population = frozen_population(lambdas)
    original = cal.population
    try:
        cal.population = population
        result, _, _ = cal.simulate(
            cal.BASE_REF,
            "normal",
            rng_seed=seed + 3000,
            spiral_mult=alpha_d,
            utility_mode="anchored",
            baseline_utility=baseline,
        )
        return result
    finally:
        cal.population = original


def aggregate(runs: list[dict[str, dict[str, int]]]) -> tuple[dict, dict]:
    mean = {
        w: {t: statistics.mean(run[w][t] for run in runs) for t in TYPES}
        for w in WEEKS
    }
    sd = {
        w: {t: statistics.pstdev(run[w][t] for run in runs) for t in TYPES}
        for w in WEEKS
    }
    return mean, sd


def benchmark_shares() -> dict[str, dict[str, float]]:
    matrix = json.loads(cal.BENCH_PATH.read_text(encoding="utf-8"))["weekly_category_matrix"]
    cn_for_type = {v: k for k, v in cal.TYPE_KEYS.items()}
    out = {}
    for week in WEEKS:
        vals = {t: float(matrix[week].get(cn_for_type[t], 0) or 0) for t in TYPES}
        total = sum(vals.values())
        out[week] = {t: vals[t] / total if total else 0.0 for t in TYPES}
    return out


def combined_shares(agent_mean: dict, injected: dict) -> dict[str, dict[str, float]]:
    out = {}
    for week in WEEKS:
        vals = {t: agent_mean[week][t] + injected[week][t] for t in TYPES}
        total = sum(vals.values())
        out[week] = {t: vals[t] / total if total else 0.0 for t in TYPES}
    return out


def write_outputs(seed_count: int = 100) -> tuple[Path, Path]:
    alpha_d, baseline, lambdas = load_parameters()
    population = frozen_population(lambdas)

    random_runs = []
    climate_runs = []
    interest_runs = []
    for seed in range(seed_count):
        result, climate = simulate_random_global(seed, population, alpha_d, baseline)
        random_runs.append(result)
        climate_runs.append(climate)
        interest_runs.append(simulate_interest(seed, alpha_d, baseline, lambdas))

    random_mean, random_sd = aggregate(random_runs)
    interest_mean, _ = aggregate(interest_runs)
    injected = injected_counts()
    random_share = combined_shares(random_mean, injected)
    interest_share = combined_shares(interest_mean, injected)
    real_share = benchmark_shares()
    random_climate = {
        w: {t: statistics.mean(run[w][t] for run in climate_runs) for t in TYPES}
        for w in WEEKS
    }

    OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    with OUT_DATA.open("w", newline="", encoding="utf-8-sig") as handle:
        fields = ["week"]
        for prefix in ("random_agent", "random_agent_sd", "random_combined_share",
                       "interest_combined_share", "real_share", "random_feed_share"):
            fields.extend(f"{prefix}_{t}" for t in TYPES)
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for w in WEEKS:
            row = {"week": w}
            for t in TYPES:
                row[f"random_agent_{t}"] = random_mean[w][t]
                row[f"random_agent_sd_{t}"] = random_sd[w][t]
                row[f"random_combined_share_{t}"] = random_share[w][t]
                row[f"interest_combined_share_{t}"] = interest_share[w][t]
                row[f"real_share_{t}"] = real_share[w][t]
                row[f"random_feed_share_{t}"] = random_climate[w][t]
            writer.writerow(row)

    meta = {
        "artifact_status": "numerical_proxy_expectation_not_experiment_result",
        "random_definition": (
            "uniform sample without replacement from all posts present in Env by current week; "
            "no lifecycle, recency, interest, popularity, exposure penalty, official pin, or W13 floor"
        ),
        "future_posts_visible": False,
        "feed_size": cal.FEED_SIZE,
        "seed_count": seed_count,
        "formula": "U_i=B_i+R_i*(D_i-B_i)",
        "parameters": {"alpha_D": alpha_d, "baseline_utility": baseline, "lambda_mean": lambdas},
        "input": {
            "injection_sample": str(cal.INJECTION_SAMPLE_PATH.relative_to(cal.workspace_root)),
            "agent_tendency_profile": "not used by random-global; used by interest reference proxy",
        },
        "limitations": [
            "This is a deterministic numerical proxy over 100 feed-sampling seeds, not an LLM ABM run.",
            "All proxy seeds reuse injection sample s0; uncertainty reflects feed sampling, not injection-sample variation.",
            "Agent post semantic variation is replaced by the registered median type tendency profile in the interest reference.",
            "The random-global arm intentionally changes candidate eligibility and agenda forcing as well as ranking, so its contrast is an overall curation-regime effect.",
        ],
        "weekly": {
            w: {
                "random_agent_mean": random_mean[w],
                "random_agent_sd": random_sd[w],
                "random_combined_share": random_share[w],
                "interest_combined_share": interest_share[w],
                "real_share": real_share[w],
                "random_feed_share": random_climate[w],
            }
            for w in WEEKS
        },
    }
    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    plt.rcParams.update({
        "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "font.size": 10,
    })
    x = list(range(len(WEEKS)))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.8), gridspec_kw={"width_ratios": [1.05, 1]})

    ax1.plot(x, [real_share[w]["meme"] for w in WEEKS], color="#111111", linewidth=2.5,
             marker="s", markersize=4.5, label="Real benchmark")
    ax1.plot(x, [interest_share[w]["meme"] for w in WEEKS], color="#D55E00", linewidth=2.3,
             marker="o", markersize=4, label="Interest proxy")
    ax1.plot(x, [random_share[w]["meme"] for w in WEEKS], color="#7F7F7F", linewidth=2.3,
             marker="o", markersize=4, label="Random-global proxy")
    ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.set_ylabel("Meme share of combined supply")
    ax1.set_title("Expected meme-share trajectory", fontweight="bold")
    ax1.legend(frameon=False, loc="upper left")

    stack = [[random_mean[w][t] for w in WEEKS] for t in TYPES]
    ax2.stackplot(x, *stack, labels=[TYPE_LABEL[t] for t in TYPES],
                  colors=[TYPE_COLOR[t] for t in TYPES], alpha=0.9,
                  linewidth=0.6, edgecolor="white")
    ax2.set_ylabel("Agent posts per week (100-seed proxy mean)")
    ax2.set_title("Expected random-global agent supply", fontweight="bold")
    ax2.legend(frameon=False, loc="upper right", fontsize=8)

    for ax in (ax1, ax2):
        ax.axvline(1, color="#D62728", linestyle="--", linewidth=1.2, alpha=0.8)
        ax.axvline(7, color="#9467BD", linestyle=":", linewidth=1.2, alpha=0.8)
        ax.set_xticks(x, [w.replace("2026-", "") for w in WEEKS], rotation=45)
        ax.set_axisbelow(True)
    ax2.annotate("Death event", xy=(1, 1), xycoords=("data", "axes fraction"),
                 xytext=(5, -18), textcoords="offset points", color="#D62728", fontsize=8)
    ax1.annotate("Meme-wave window", xy=(7, 1), xycoords=("data", "axes fraction"),
                 xytext=(5, -32), textcoords="offset points", color="#6A3D9A", fontsize=8)

    fig.suptitle("PROXY EXPECTATION — REVISED RANDOM-GLOBAL ARM — NOT EXPERIMENT RESULTS",
                 fontsize=13, fontweight="bold", y=0.99)
    fig.text(0.5, 0.012,
             "Frozen anchored utility; 100 feed-sampling seeds; all historical posts remain equally eligible in random-global.",
             ha="center", fontsize=8.5, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    plt.close(fig)
    return OUT_PNG, OUT_SVG


def main() -> int:
    png, svg = write_outputs()
    print(f"PNG: {png}")
    print(f"SVG: {svg}")
    print(f"CSV: {OUT_DATA}")
    print(f"META: {OUT_META}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
