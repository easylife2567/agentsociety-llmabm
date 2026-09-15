#!/usr/bin/env python3
"""从 anchored_v1 interest_s0 正式 decision log 构造 D/R/B 离线消融图。

不调用 LLM、不重新推进环境。逐 Agent、逐周读取正式 run 中落盘的 B、D、R 与
threshold，并离线重算四个条件的发言门控：

    full: U = B + R(D-B)
    no_b: U = RD
    no_d: U = B + R(1-B)
    no_r: U = D

注入帖保持事实 run 的周度类型供给不变。输出三张与 chart3 模板同构的堆叠面积图、
一张 2x2 总对比图，以及逐决策和逐周 CSV。这里识别的是固定事实 D/R 路径下的
offline replay counterfactual，不是反馈路径重新演化后的动态消融 run。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import warnings
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
ROUND_ROOT = SCRIPT_DIR / "runs" / "anchored_v1"
RUN_ID = "anchored_v1_interest_s0"
RUN_DIR = ROUND_ROOT / RUN_ID
STATUS_PATH = ROUND_ROOT / "_derived" / "monitor" / RUN_ID / "status.json"
OUT_DATA = ROUND_ROOT / "_derived" / "data" / "ablation_replay_interest_s0"
OUT_CHARTS = ROUND_ROOT / "_derived" / "charts" / "ablation_replay_interest_s0"

TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
AGENT_TYPES = [t for t in TYPE_ORDER if t != "noise"]
TYPE_LABEL = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
    "noise": "噪音",
}
TYPE_COLOR = {
    "mourning": "#4C72B0",
    "meme": "#DD8452",
    "education": "#55A868",
    "marketing": "#CCB974",
    "other": "#64B5CD",
    "noise": "#B07AA1",
}
CONDITION_ORDER = ["full", "no_b", "no_d", "no_r"]
CONDITION_LABEL = {
    "full": "完整模型：B + D + R",
    "no_b": "去 B：U = RD",
    "no_d": "去 D：D ≡ 1",
    "no_r": "去 R：R ≡ 1",
}
CONDITION_FILE = {"no_b": "no_b", "no_d": "no_d", "no_r": "no_r"}
DEATH_WEEK = "2026-W13"
DEATH_LABEL = "去世 3-24 (W13)"
YLIM = (0, 100)

DECISIONS_CSV = OUT_DATA / "offline_replay_ablation_decisions.csv"
WEEKLY_CSV = OUT_DATA / "offline_replay_ablation_weekly_supply.csv"
SUMMARY_JSON = OUT_DATA / "offline_replay_ablation_summary.json"
COMPOSITE_PNG = OUT_CHARTS / "anchored_v1_ablation_drb_s0__figure_supply_stacked_area_comparison.png"

warnings.filterwarnings("error", message=r"Glyph \d+ .* missing from font")
plt.rcParams.update(
    {
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


def utility(condition: str, b: float, d: float, r: float) -> float:
    if condition == "full":
        return b + r * (d - b)
    if condition == "no_b":
        return r * d
    if condition == "no_d":
        return b + r * (1.0 - b)
    if condition == "no_r":
        return d
    raise ValueError(f"unknown condition: {condition}")


def load_status() -> tuple[
    list[str],
    dict[str, dict[str, int]],
    dict[str, dict[str, int]],
    dict[str, dict[str, int]],
]:
    if not STATUS_PATH.is_file():
        raise FileNotFoundError(f"missing formal status snapshot: {STATUS_PATH}")
    doc = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    weekly = doc.get("weekly") or []
    weeks = [str(row["week"]) for row in weekly]
    if len(weeks) != 11 or len(set(weeks)) != 11:
        raise ValueError(f"expected 11 unique weeks, got {weeks}")
    injected = {
        str(row["week"]): {t: int(row.get(f"injected_{t}", 0) or 0) for t in TYPE_ORDER}
        for row in weekly
    }
    formal_agent = {
        str(row["week"]): {t: int(row.get(f"agent_supply_{t}", 0) or 0) for t in AGENT_TYPES}
        for row in weekly
    }
    formal_gate = {
        str(row["week"]): {
            t: int(((row.get("mech_agg") or {}).get(t) or {}).get("n_speak", 0) or 0)
            for t in AGENT_TYPES
        }
        for row in weekly
    }
    if any(sum(injected[w].values()) != int(row["injected_count"]) for w, row in zip(weeks, weekly)):
        raise ValueError("injected type counts do not sum to injected_count")
    return weeks, injected, formal_agent, formal_gate


def load_counterfactual_decisions(weeks: list[str]) -> tuple[list[dict], dict]:
    agent_files = sorted((RUN_DIR / "agents").glob("agent_*/AGENT.json"))
    if len(agent_files) != 100:
        raise ValueError(f"expected 100 formal agents, found {len(agent_files)}")

    rows: list[dict] = []
    counts = {c: {w: {t: 0 for t in AGENT_TYPES} for w in weeks} for c in CONDITION_ORDER}
    factual_gate_mismatches = 0
    factual_speak_without_post = 0
    max_full_u_error = 0.0
    seen_agent_week: set[tuple[int, str]] = set()

    for path in agent_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        agent_id = int(doc["id"])
        profile = doc.get("profile") or {}
        agent_type = str(profile.get("agent_type"))
        if agent_type not in AGENT_TYPES:
            raise ValueError(f"agent {agent_id} has invalid type {agent_type!r}")
        decisions = doc.get("decision_log") or []
        if len(decisions) != len(weeks):
            raise ValueError(f"agent {agent_id}: {len(decisions)} decisions != {len(weeks)} weeks")
        for rec in decisions:
            week = str(rec.get("week"))
            key = (agent_id, week)
            if week not in weeks or key in seen_agent_week:
                raise ValueError(f"invalid or duplicate agent-week: {key}")
            seen_agent_week.add(key)
            components = rec.get("components") or {}
            b = float(components["baseline_utility"])
            d = float(components["spiral"])
            r = float(components["decay"])
            threshold = float(rec["threshold"])
            observed_u = float(rec["u"])
            full_u = utility("full", b, d, r)
            max_full_u_error = max(max_full_u_error, abs(full_u - observed_u))
            full_speak = full_u >= threshold
            observed_speak = bool(rec.get("speak"))
            observed_posted = bool(rec.get("posted"))
            factual_speak_without_post += int(observed_speak and not observed_posted)
            if full_speak != observed_speak:
                factual_gate_mismatches += 1

            for condition in CONDITION_ORDER:
                u = utility(condition, b, d, r)
                speak = u >= threshold
                counts[condition][week][agent_type] += int(speak)
                rows.append(
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "week": week,
                        "condition": condition,
                        "baseline_B": b,
                        "spiral_D": d,
                        "fatigue_R": r,
                        "threshold": threshold,
                        "utility": u,
                        "speak": int(speak),
                        "observed_speak": int(observed_speak),
                        "observed_posted": int(observed_posted),
                    }
                )

    if len(seen_agent_week) != 1100:
        raise ValueError(f"expected 1100 unique formal decisions, got {len(seen_agent_week)}")
    audit = {
        "formal_agent_files": len(agent_files),
        "formal_decisions": len(seen_agent_week),
        "factual_gate_mismatches": factual_gate_mismatches,
        "factual_speak_without_post": factual_speak_without_post,
        "max_full_utility_reconstruction_abs_error": max_full_u_error,
    }
    return rows, {"counts": counts, "audit": audit}


def validate_full_counts(counts: dict, formal_gate: dict, weeks: list[str]) -> None:
    problems = []
    for week in weeks:
        for agent_type in AGENT_TYPES:
            got = counts["full"][week][agent_type]
            expected = formal_gate[week][agent_type]
            if got != expected:
                problems.append(f"{week}/{agent_type}: reconstructed={got}, formal_gate={expected}")
    if problems:
        raise ValueError("full-model weekly reconstruction mismatch:\n" + "\n".join(problems))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_weekly_rows(
    counts: dict,
    injected: dict[str, dict[str, int]],
    weeks: list[str],
) -> list[dict]:
    rows = []
    for condition in CONDITION_ORDER:
        for week in weeks:
            for agent_type in TYPE_ORDER:
                agent_supply = int(counts[condition][week].get(agent_type, 0))
                injected_supply = int(injected[week][agent_type])
                rows.append(
                    {
                        "condition": condition,
                        "week": week,
                        "type": agent_type,
                        "gate_implied_agent_supply": agent_supply,
                        "injected_supply": injected_supply,
                        "combined_supply": agent_supply + injected_supply,
                    }
                )
    return rows


def combined_series(weekly_rows: list[dict], condition: str, weeks: list[str]) -> dict[str, list[int]]:
    lookup = {
        (str(row["condition"]), str(row["week"]), str(row["type"])): int(row["combined_supply"])
        for row in weekly_rows
    }
    return {t: [lookup[(condition, week, t)] for week in weeks] for t in TYPE_ORDER}


def death_line(ax, weeks: list[str], annotate: bool = True) -> None:
    x = weeks.index(DEATH_WEEK)
    ax.axvline(x, color="#D62728", linestyle="--", linewidth=1.4, alpha=0.85, zorder=1)
    if annotate:
        ax.annotate(
            DEATH_LABEL,
            xy=(x, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(6, -4),
            textcoords="offset points",
            color="#D62728",
            fontsize=10,
            va="top",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
        )


def draw_stack(ax, weekly_rows: list[dict], condition: str, weeks: list[str], compact: bool = False) -> None:
    x = list(range(len(weeks)))
    series = combined_series(weekly_rows, condition, weeks)
    death_line(ax, weeks, annotate=not compact)
    ax.stackplot(
        x,
        *[series[t] for t in TYPE_ORDER],
        labels=[TYPE_LABEL[t] for t in TYPE_ORDER],
        colors=[TYPE_COLOR[t] for t in TYPE_ORDER],
        edgecolor="white",
        linewidth=0.6,
        alpha=0.92,
        zorder=2,
    )
    ax.set_xticks(x, weeks, rotation=45, ha="right")
    ax.set_ylim(*YLIM)
    ax.set_yticks(range(YLIM[0], YLIM[1] + 1, 10))
    ax.set_axisbelow(True)
    ax.margins(y=0.05)
    ax.set_title(CONDITION_LABEL[condition], fontweight="bold", fontsize=11 if compact else 13)


def plot_individuals(weekly_rows: list[dict], weeks: list[str]) -> list[Path]:
    OUT_CHARTS.mkdir(parents=True, exist_ok=True)
    paths = []
    for condition in ("no_b", "no_d", "no_r"):
        fig, ax = plt.subplots(figsize=(10, 5.4))
        draw_stack(ax, weekly_rows, condition, weeks)
        ax.set_ylabel("帖数（绝对数量）")
        ax.set_title(
            f"各内容类型供给量变化（堆叠面积 · 绝对数量，{CONDITION_LABEL[condition]}）",
            fontweight="bold",
            fontsize=13,
        )
        ax.legend(loc="upper right", frameon=False, fontsize=9)
        fig.text(
            0.5,
            0.006,
            "正式 anchored_v1_interest_s0 的 B/D/R/阈值离线反事实；门控发言按 1 帖计；注入供给固定。",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#555555",
        )
        fig.tight_layout(rect=(0, 0.035, 1, 1))
        path = OUT_CHARTS / f"anchored_v1_ablation_{CONDITION_FILE[condition]}_s0__chart3_supply_stacked_area.png"
        fig.savefig(path, dpi=300, facecolor="white")
        plt.close(fig)
        paths.append(path)
    return paths


def plot_composite(weekly_rows: list[dict], weeks: list[str]) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 9.3), sharex=True, sharey=True)
    for label, condition, ax in zip(("a", "b", "c", "d"), CONDITION_ORDER, axes.flat):
        draw_stack(ax, weekly_rows, condition, weeks, compact=True)
        ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=13,
                fontweight="bold", va="bottom", ha="left")
    axes[0, 0].set_ylabel("帖数（绝对数量）")
    axes[1, 0].set_ylabel("帖数（绝对数量）")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=6, frameon=False,
               bbox_to_anchor=(0.5, 0.945), fontsize=10)
    fig.suptitle(
        "D / R / B 消融：各内容类型供给量对比\n"
        "正式 interest_s0 replay 的离线门控反事实（注入 + Agent 供给）",
        fontweight="bold",
        fontsize=15,
        y=0.992,
    )
    fig.text(
        0.5,
        0.012,
        "共同纵轴 0–100（模板为 0–80；因 no D 峰值达到 92，统一扩展以避免截断）。"
        " D/R 路径固定为事实 run 的落盘值，因此本图不是反馈重演后的动态消融。",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0.02, 0.045, 0.98, 0.90), h_pad=1.8, w_pad=1.4)
    OUT_CHARTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(COMPOSITE_PNG, dpi=300, facecolor="white")
    plt.close(fig)
    return COMPOSITE_PNG


def summarize(weekly_rows: list[dict], audit: dict, weeks: list[str]) -> dict:
    totals: dict[str, dict[str, int]] = defaultdict(dict)
    for condition in CONDITION_ORDER:
        for week in weeks:
            totals[condition][week] = sum(
                int(r["combined_supply"])
                for r in weekly_rows
                if r["condition"] == condition and r["week"] == week
            )
    summary = {
        "artifact_status": "offline_replay_counterfactual_not_dynamic_ablation_run",
        "formal_source_run": str(RUN_DIR),
        "formal_status_source": str(STATUS_PATH),
        "formulas": {
            "full": "U=B+R(D-B)",
            "no_b": "U=RD",
            "no_d": "U=B+R(1-B), D=1",
            "no_r": "U=D, R=1",
        },
        "audit": audit,
        "weekly_combined_totals": totals,
        "peak_combined_supply": {
            c: {"value": max(totals[c].values()),
                "week": max(totals[c], key=totals[c].get)}
            for c in CONDITION_ORDER
        },
        "limitations": [
            "B, D, and R are read from the factual interest_s0 path and held fixed for offline gate recomputation.",
            "Counterfactual speaking does not alter later feeds, climates, fatigue, or generated text.",
            "One factual speaking decision failed to produce a post; all panels use gate-implied supply for a consistent counterfactual denominator.",
            "Counterfactual output type is the agent's preregistered fixed type; injected supply is factual and unchanged.",
            "These charts are not substitutes for newly executed dynamic ablation runs.",
        ],
    }
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot D/R/B offline replay ablations from formal interest_s0 data")
    parser.parse_args()
    weeks, injected, formal_agent, formal_gate = load_status()
    decision_rows, result = load_counterfactual_decisions(weeks)
    if result["audit"]["factual_gate_mismatches"] != 0:
        raise ValueError(f"formal gate reconstruction mismatches: {result['audit']}")
    validate_full_counts(result["counts"], formal_gate, weeks)
    result["audit"]["factual_gate_supply_minus_actual_posts"] = sum(
        result["counts"]["full"][week][agent_type] - formal_agent[week][agent_type]
        for week in weeks
        for agent_type in AGENT_TYPES
    )
    weekly_rows = build_weekly_rows(result["counts"], injected, weeks)
    write_csv(DECISIONS_CSV, list(decision_rows[0]), decision_rows)
    write_csv(WEEKLY_CSV, list(weekly_rows[0]), weekly_rows)
    summary = summarize(weekly_rows, result["audit"], weeks)
    individual_paths = plot_individuals(weekly_rows, weeks)
    composite_path = plot_composite(weekly_rows, weeks)
    print(
        json.dumps(
            {
                "status": "ok",
                "source": str(RUN_DIR),
                "audit": result["audit"],
                "peak_combined_supply": summary["peak_combined_supply"],
                "individual_charts": [str(p) for p in individual_paths],
                "composite_chart": str(composite_path),
                "data_dir": str(OUT_DATA),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
