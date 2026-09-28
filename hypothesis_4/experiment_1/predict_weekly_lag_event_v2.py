#!/usr/bin/env python3
"""Mechanism-only Agent posting forecast for weekly_lag1_event_v2.

This is an offline proxy, not an AgentSociety experiment run.  It executes the
frozen feed assembly and deterministic speaking rule, then represents each
speaker's generated text by the median tendency vector observed in the six
completed weekly_lag1 runs.  The proxy therefore propagates posting feedback
without making any LLM calls.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-matplotlib")

import matplotlib.pyplot as plt
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
CONFIGS_DIR = SCRIPT_DIR / "init" / "configs"
ROUND_TAG = "weekly_lag1_event_v2"
WEEKS = [f"2026-W{week:02d}" for week in range(12, 24)]
TYPES = ["meme", "mourning", "education", "marketing", "other"]
TYPE_LABELS = {
    "meme": "Meme",
    "mourning": "Mourning",
    "education": "Education",
    "marketing": "Marketing",
    "other": "Other",
}
TYPE_COLORS = {
    "meme": "#D55E00",
    "mourning": "#0072B2",
    "education": "#009E73",
    "marketing": "#E69F00",
    "other": "#7A7A7A",
}

# Median classifier tendency vectors from all Agent-authored posts in the six
# completed weekly_lag1 runs (n=1,110).  These stand in only for LLM wording in
# the feedback pool; whether an Agent speaks is still computed by the real rule.
PROTOTYPE_TENDENCIES: dict[str, dict[str, float]] = {
    "meme": {"mourning": 0.1207, "marketing": 0.6784, "education": 0.4485, "meme": 5.3223},
    "mourning": {"mourning": 2.7027, "marketing": 0.2809, "education": 1.1477, "meme": 0.0},
    "education": {"mourning": 0.0, "marketing": 1.2411, "education": 3.8934, "meme": 0.0},
    "marketing": {"mourning": 0.0, "marketing": 4.7511, "education": 1.7176, "meme": 0.0},
    "other": {"mourning": 0.2740, "marketing": 0.8572, "education": 0.8877, "meme": 0.0},
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(arm: str, seed: int) -> dict:
    return read_json(CONFIGS_DIR / f"{ROUND_TAG}_{arm}_s{seed}.json")


def env_kwargs(config: dict) -> dict:
    kwargs = dict(config["env_modules"][0]["kwargs"])
    for key in ("injection_data_path", "weekly_initial_injection_data_path", "vocab_path"):
        value = kwargs.get(key)
        if value:
            kwargs[key] = str(ROOT / value)
    return kwargs


def event_signal(env) -> dict[str, Any]:
    return {
        "active": bool(
            env._event_signal_type
            and env._event_signal_salience_slots > 0
            and env._current_week == env._event_week
        ),
        "week": env._event_week,
        "type": env._event_signal_type or None,
        "salience_slots": env._event_signal_salience_slots,
        "source": "official_external_event",
    }


def snapshot(env, aid: str) -> dict[str, Any]:
    return {
        "week": env._current_week,
        "event_signal": event_signal(env),
        "feed": [dict(item) for item in env._feeds.get(aid, [])],
        "feed_type_distribution": dict(env._climate_shares.get(aid, {})),
        "personal_stats": {
            "total_posts": env._total_posts_by_agent.get(aid, 0),
            "cumulative_exposures": dict(env._cumulative_exposures.get(aid, {})),
        },
        "meme_env": dict(env._meme_env),
    }


def predict_run(env_cls, agent_cls, arm: str, seed: int) -> list[dict[str, Any]]:
    config = load_config(arm, seed)
    env = env_cls(**env_kwargs(config))
    env._open_tick(WEEKS[0])
    env._set_baseline_landscape()

    agents: list[tuple[str, str, Any]] = []
    for spec in config["agents"]:
        profile = spec["kwargs"]
        agent = object.__new__(agent_cls)
        agent._agent_type = profile["agent_type"]
        agent._params = profile["params"]
        agents.append((str(spec["agent_id"]), profile["agent_type"], agent))

    rows: list[dict[str, Any]] = []
    for week_index, week in enumerate(WEEKS):
        counts = Counter({post_type: 0 for post_type in TYPES})
        utilities: dict[str, list[float]] = {post_type: [] for post_type in TYPES}
        thresholds: dict[str, list[float]] = {post_type: [] for post_type in TYPES}
        effective_shares: dict[str, list[float]] = {post_type: [] for post_type in TYPES}
        observed_shares: dict[str, list[float]] = {post_type: [] for post_type in TYPES}
        pending: list[dict[str, Any]] = []
        env._spoke_this_tick = {}
        env._posted_this_step = set()

        for aid, agent_type, agent in agents:
            utility, components = agent._speak_stimulus(snapshot(env, aid))
            threshold = float(agent._params["activity"])
            speaks = utility >= threshold
            utilities[agent_type].append(float(utility))
            thresholds[agent_type].append(threshold)
            effective_shares[agent_type].append(float(components["share_own"]))
            observed_shares[agent_type].append(float(components["share_own_observed"]))
            env._spoke_this_tick[aid] = speaks
            if not speaks:
                continue
            counts[agent_type] += 1
            post_id = env._next_post_id
            env._next_post_id += 1
            pending.append({
                "post_id": post_id,
                "agent_id": aid,
                "content": f"mechanism_proxy_{agent_type}",
                "pool_type": agent_type,
                "assigned_type": agent_type,
                "type_mismatch": False,
                "tendencies": dict(PROTOTYPE_TENDENCIES[agent_type]),
                "week": week,
                "event_time": None,
            })

        for post_type in TYPES:
            rows.append({
                "run_id": f"{ROUND_TAG}_{arm}_s{seed}",
                "arm": arm,
                "seed": seed,
                "week": week,
                "week_num": int(week[-2:]),
                "type": post_type,
                "agent_posts": counts[post_type],
                "mean_utility": statistics.fmean(utilities[post_type]),
                "mean_threshold": statistics.fmean(thresholds[post_type]),
                "mean_observed_share": statistics.fmean(observed_shares[post_type]),
                "mean_effective_share": statistics.fmean(effective_shares[post_type]),
                "event_signal_active": week == env._event_week,
                "proxy_content_tendency_source": "weekly_lag1 completed runs median",
            })

        env._pending_agent_posts = pending
        env._step_index += 1
        merged = env._flush_pending_to_pool()
        for rec in merged:
            aid = rec["agent_id"]
            env._total_posts_by_agent[aid] = env._total_posts_by_agent.get(aid, 0) + 1
        for aid in sorted(env._agent_types):
            cumulative = env._cumulative_exposures.setdefault(
                aid, {post_type: 0 for post_type in env_mod.TYPE_ORDER_ALL}
            )
            for post_type in env_mod.TYPE_ORDER_ALL:
                cumulative[post_type] = cumulative.get(post_type, 0) + (
                    env._exposure_counts_tick.get(aid, {}).get(post_type, 0)
                )
        env._global_landscape = env._landscape_row(week, merged)
        if week_index + 1 < len(WEEKS):
            env._open_tick(WEEKS[week_index + 1])

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[int]] = {}
    for row in rows:
        grouped.setdefault((row["arm"], row["week"], row["type"]), []).append(
            int(row["agent_posts"])
        )
    result: list[dict[str, Any]] = []
    for arm in ("interest", "random"):
        for week in WEEKS:
            for post_type in TYPES:
                values = grouped[(arm, week, post_type)]
                result.append({
                    "arm": arm,
                    "week": week,
                    "week_num": int(week[-2:]),
                    "type": post_type,
                    "agent_posts_mean": statistics.fmean(values),
                    "agent_posts_min": min(values),
                    "agent_posts_max": max(values),
                    "agent_posts_std": statistics.stdev(values) if len(values) > 1 else 0.0,
                })
    return result


def aggregate_totals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_run_week: dict[tuple[str, int, str], int] = {}
    for row in rows:
        key = (row["arm"], int(row["seed"]), row["week"])
        by_run_week[key] = by_run_week.get(key, 0) + int(row["agent_posts"])

    result: list[dict[str, Any]] = []
    for arm in ("interest", "random"):
        for week in WEEKS:
            values = [by_run_week[(arm, seed, week)] for seed in (0, 1, 2)]
            result.append({
                "arm": arm,
                "week": week,
                "week_num": int(week[-2:]),
                "total_agent_posts_mean": statistics.fmean(values),
                "total_agent_posts_min": min(values),
                "total_agent_posts_max": max(values),
                "total_agent_posts_std": statistics.stdev(values),
            })
    return result


def plot_prediction(aggregate_rows: list[dict[str, Any]], output_base: Path) -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "figure.dpi": 160,
        "savefig.dpi": 300,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    x = np.arange(len(WEEKS))
    labels = [week.replace("2026-", "") for week in WEEKS]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8.2), sharex=True, sharey=True)
    max_total = 0.0
    for axis, arm in zip(axes, ("interest", "random")):
        by_type = {
            post_type: [
                next(
                    row["agent_posts_mean"] for row in aggregate_rows
                    if row["arm"] == arm and row["week"] == week and row["type"] == post_type
                )
                for week in WEEKS
            ]
            for post_type in TYPES
        }
        stack_order = ["marketing", "education", "other", "mourning", "meme"]
        stacks = [np.asarray(by_type[post_type], dtype=float) for post_type in stack_order]
        axis.stackplot(
            x,
            stacks,
            labels=[TYPE_LABELS[post_type] for post_type in stack_order],
            colors=[TYPE_COLORS[post_type] for post_type in stack_order],
            alpha=0.88,
            linewidth=0.5,
            edgecolor="white",
        )
        totals = np.sum(stacks, axis=0)
        max_total = max(max_total, float(np.max(totals)))
        axis.plot(x, totals, color="#202020", linewidth=1.5, label="Total")
        axis.axvline(1, color="#8B1A1A", linestyle="--", linewidth=1.1)
        axis.axvspan(10.5, 11.5, color="#BDBDBD", alpha=0.18)
        axis.text(1.05, max(totals) * 0.94, "W13 event", color="#8B1A1A", fontsize=9)
        axis.text(10.58, max(totals) * 0.84, "W23 drain", color="#555555", fontsize=9)
        axis.set_title(f"{arm.capitalize()} arm — predicted mean across 3 seeds", loc="left")
        axis.set_ylabel("Agent posts")
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
    axes[0].legend(ncol=6, loc="upper right", frameon=False)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(labels)
    axes[-1].set_xlabel("Simulation week")
    for axis in axes:
        axis.set_ylim(0, max_total * 1.13)
    fig.suptitle(
        "Predicted Agent Posting Volume — weekly_lag1_event_v2",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.01,
        0.01,
        "Mechanism-only proxy (no LLM calls). W23 is a drain/readout week and is not benchmark-fitted.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.955))
    for suffix in ("png", "svg"):
        fig.savefig(output_base.with_suffix(f".{suffix}"), bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    global env_mod
    env_mod = load_module(
        "curation_dynamics_space_prediction",
        ROOT / "custom" / "envs" / "curation_dynamics_space.py",
    )
    agent_mod = load_module(
        "curation_discourse_agent_prediction",
        ROOT / "custom" / "agents" / "curation_discourse_agent.py",
    )
    run_rows: list[dict[str, Any]] = []
    for arm in ("interest", "random"):
        for seed in (0, 1, 2):
            run_rows.extend(
                predict_run(env_mod.CurationDynamicsSpace, agent_mod.CurationDiscourseAgent, arm, seed)
            )
    aggregate_rows = aggregate(run_rows)
    total_rows = aggregate_totals(run_rows)
    write_csv(args.output_dir / "predicted_agent_posts_run_level.csv", run_rows)
    write_csv(args.output_dir / "predicted_agent_posts_by_type.csv", aggregate_rows)
    write_csv(args.output_dir / "predicted_agent_posts_total.csv", total_rows)
    plot_prediction(
        aggregate_rows,
        args.output_dir / "weekly_lag1_event_v2_agent_post_volume_prediction",
    )

    totals: dict[str, dict[str, float]] = {}
    for arm in ("interest", "random"):
        totals[arm] = {}
        for week in WEEKS:
            totals[arm][week] = sum(
                float(row["agent_posts_mean"])
                for row in aggregate_rows
                if row["arm"] == arm and row["week"] == week
            )
    summary = {
        "artifact_status": "mechanism_only_proxy_prediction_not_experiment_result",
        "round": ROUND_TAG,
        "weeks": WEEKS,
        "seeds": [0, 1, 2],
        "arms": ["interest", "random"],
        "method": (
            "Frozen v2 feed assembly and deterministic speaking rule; Agent-authored feedback "
            "uses median type-tendency vectors from the six completed weekly_lag1 runs; no LLM calls."
        ),
        "prototype_tendencies": PROTOTYPE_TENDENCIES,
        "total_agent_posts_mean": totals,
        "limitations": [
            "Generated wording is replaced by a median tendency vector, so downstream ranking is approximate.",
            "The event signal changes feedback after W13; only the formal experiment can confirm the trajectory.",
            "W23 is a drain/readout week without a same-week real-data benchmark.",
        ],
    }
    (args.output_dir / "prediction_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"output_dir": str(args.output_dir), "totals": totals}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
