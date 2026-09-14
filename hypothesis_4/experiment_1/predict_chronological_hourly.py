#!/usr/bin/env python3
"""小时级 chronological 的离线代理预测；不调用 LLM，也不启动正式实验。

代理严格使用预登记行动表、真实帖 published_at、最新 10 条规则和锚定式效用
U=B_i+R(D-B_i)。Agent 发帖正文被抽象为作者固定类型，因此本图只预测行为层的方向
与量级，不是实验结果。
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
CONFIG_PATH = SCRIPT_DIR / "init" / "configs" / "anchored_v1_chronological_s0.json"
INJECTION_PATH = SCRIPT_DIR / "init" / "injection_sample_s0.json"
OUT_CSV = SCRIPT_DIR / "data" / "chronological_hourly_prediction.csv"
OUT_JSON = SCRIPT_DIR / "data" / "chronological_hourly_prediction.json"
OUT_PNG = SCRIPT_DIR / "charts" / "prediction" / "PROXY_chronological_hourly_expected.png"
OUT_SVG = SCRIPT_DIR / "charts" / "prediction" / "PROXY_chronological_hourly_expected.svg"

WEEKS = [f"2026-W{i:02d}" for i in range(12, 23)]
TYPES = ["meme", "mourning", "education", "marketing", "other"]
LABELS = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
}
COLORS = {
    "meme": "#DD8452",
    "mourning": "#4C72B0",
    "education": "#55A868",
    "marketing": "#CCB974",
    "other": "#64B5CD",
}
POP_SHARE = {"meme": 0.19, "mourning": 0.22, "marketing": 0.23,
             "education": 0.15, "other": 0.21}
Y_LIM = (0, 80)
SHANGHAI = timezone(timedelta(hours=8))


def _load_mechanisms():
    path = ROOT / "custom" / "envs" / "curation_mechanisms.py"
    spec = importlib.util.spec_from_file_location("curation_mechanisms_proxy_chrono", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mech = _load_mechanisms()


def _local_time(raw: str | None, pid: object, week: str) -> datetime:
    if not raw:
        if str(pid) == "official_w13_announcement":
            return datetime(2026, 3, 24, 20, 0, 0)
        year, number = week.split("-W")
        return datetime.fromisocalendar(int(year), int(number), 1) + timedelta(hours=12)
    dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.astimezone(SHANGHAI).replace(tzinfo=None)
    return dt


def _week_monday(week: str) -> datetime:
    year, number = week.split("-W")
    return datetime.fromisocalendar(int(year), int(number), 1)


def simulate() -> tuple[list[dict], dict]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    injection = json.loads(INJECTION_PATH.read_text(encoding="utf-8"))["posts"]
    agents = []
    for spec in config["agents"]:
        profile = spec["kwargs"]
        agents.append({
            "id": str(profile["id"]),
            "type": profile["agent_type"],
            "hour": int(profile["chronological_action_hour"]),
            "params": {k: float(v) for k, v in profile["params"].items()},
        })
    by_hour: dict[int, list[dict]] = defaultdict(list)
    for agent in agents:
        by_hour[agent["hour"]].append(agent)

    timed_injection = sorted(
        [
            (_local_time(p.get("published_at"), p.get("pid"), str(p["week"])), p)
            for p in injection
        ],
        key=lambda x: (x[0], str(x[1].get("pid", ""))),
    )
    pool: list[dict] = []
    injection_cursor = 0
    serial = 0
    cumulative_own = {a["id"]: 0.0 for a in agents}
    weekly_agent = {w: {t: 0 for t in TYPES} for w in WEEKS}
    weekly_exposure = {w: {t: 0 for t in TYPES + ["noise"]} for w in WEEKS}
    weekly_decisions = {w: 0 for w in WEEKS}

    for week in WEEKS:
        monday = _week_monday(week)
        for hour in sorted(by_hour):
            event_time = monday + timedelta(hours=hour)
            while injection_cursor < len(timed_injection) and timed_injection[injection_cursor][0] <= event_time:
                post_time, rec = timed_injection[injection_cursor]
                injection_cursor += 1
                serial += 1
                pool.append({"time": post_time, "serial": serial, "type": str(rec["type"])})

            feed = sorted(pool, key=lambda p: (p["time"], p["serial"]), reverse=True)[:10]
            batch_posts: list[dict] = []
            for agent in by_hour[hour]:
                own_type = agent["type"]
                own_n = sum(1 for post in feed if post["type"] == own_type)
                share_own = own_n / len(feed) if feed else 0.0
                prm = agent["params"]
                d = mech.spiral_factor(
                    share_own,
                    POP_SHARE[own_type],
                    prm["spiral"] * prm["spiral_scale"],
                )
                r = mech.fatigue_factor(prm["decay"], cumulative_own[agent["id"]])
                u = mech.anchored_utility(prm["baseline_utility"], d, r)
                weekly_decisions[week] += 1
                for post in feed:
                    if post["type"] in weekly_exposure[week]:
                        weekly_exposure[week][post["type"]] += 1
                if u >= prm["activity"]:
                    weekly_agent[week][own_type] += 1
                    serial += 1
                    batch_posts.append({
                        "time": event_time,
                        "serial": serial,
                        "type": own_type,
                    })
                # 与 Env 同构：本批 feed 在本次决策后才进入累计曝光。
                cumulative_own[agent["id"]] += own_n
            # 同小时同步：全部决策结束后才把 Agent 帖并入时间轴。
            pool.extend(batch_posts)

    injected_counts = {
        w: {t: sum(1 for p in injection if p["week"] == w and p["type"] == t)
            for t in TYPES + ["noise"]}
        for w in WEEKS
    }
    rows = []
    for week in WEEKS:
        agent_total = sum(weekly_agent[week].values())
        row = {"week": week, "agent_total": agent_total, "decisions": weekly_decisions[week]}
        for t in TYPES:
            row[f"agent_{t}"] = weekly_agent[week][t]
            row[f"agent_share_{t}"] = (
                weekly_agent[week][t] / agent_total if agent_total else 0.0
            )
            row[f"injected_{t}"] = injected_counts[week][t]
            row[f"exposure_{t}"] = weekly_exposure[week][t]
        row["injected_noise"] = injected_counts[week]["noise"]
        rows.append(row)

    meta = {
        "status": "proxy_prediction_not_experimental_result",
        "algorithm": "chronological_hourly",
        "formula": "U=B_i+R(D-B_i)",
        "feed_rule": "all posts published by action time; sort exact event_time descending; latest 10",
        "batch_rule": "same-hour agents share pre-batch snapshot; posts visible from later hours",
        "action_schedule": {
            "agents": len(agents),
            "unique_hours_per_week": len(by_hour),
            "engine_batches": len(by_hour) * len(WEEKS),
            "source": "W05-W12 empirical weekday-hour joint distribution, Asia/Shanghai",
            "seed": 44,
        },
        "y_axis_template": "anchored_v1_interest_s0_smoke__chart3_supply_stacked_area.png (0-80)",
    }
    return rows, meta


def _font_setup() -> None:
    candidates = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Arial Unicode MS"]
    plt.rcParams.update({
        "font.sans-serif": candidates + ["DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 11,
    })


def plot(rows: list[dict]) -> None:
    _font_setup()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    x = list(range(len(rows)))
    series = [[r[f"agent_{t}"] for r in rows] for t in TYPES]
    totals = [r["agent_total"] for r in rows]
    if max(totals) > Y_LIM[1]:
        raise RuntimeError(f"chronological proxy peak {max(totals)} exceeds baseline y-axis 80")
    fig, ax = plt.subplots(figsize=(12.5, 6.75), dpi=240)
    ax.stackplot(
        x, *series,
        labels=[LABELS[t] for t in TYPES],
        colors=[COLORS[t] for t in TYPES],
        alpha=0.92,
        linewidth=0.5,
        edgecolor="white",
    )
    ax.plot(x, totals, color="#303030", linewidth=1.6, marker="o", markersize=3.5,
            label="Agent 总供给")
    ax.axvline(1, color="#7A7A7A", linestyle="--", linewidth=1.1)
    ax.text(1.08, 76.5, "事件周 W13", color="#555555", fontsize=10, va="top")
    ax.set_xticks(x, [r["week"].replace("2026-", "") for r in rows])
    ax.set_xlim(0, len(rows) - 1)
    ax.set_ylim(*Y_LIM)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.set_ylabel("Agent 发帖数（条/周）")
    ax.set_xlabel("周")
    ax.set_title("小时级 Chronological 的预期 Agent 供给构成（离线代理）", pad=13)
    ax.grid(axis="y", color="#D8D8D8", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=3, frameon=False, loc="upper right")
    ax.text(
        0.0, -0.16,
        "注：代理预测，不是实验结果。纵轴固定 0–80，与 anchored_v1 interest s0 基线图相同。",
        transform=ax.transAxes, fontsize=9.5, color="#555555",
    )
    fig.tight_layout()
    fig.savefig(OUT_PNG, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows, meta = simulate()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(
        json.dumps({"meta": meta, "weekly": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plot(rows)
    print(json.dumps({
        "status": "proxy_only_no_experiment",
        "peak": max(r["agent_total"] for r in rows),
        "weekly_totals": {r["week"]: r["agent_total"] for r in rows},
        "png": str(OUT_PNG),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
