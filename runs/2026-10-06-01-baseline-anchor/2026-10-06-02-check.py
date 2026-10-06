"""固定旧曝光路径，诊断常态锚点换算；无LLM、无内容回流、无参数重拟合。

输入只读：用户工作簿、冻结基准及anchored_v1的profile/行动日志/replay。
输出：presentation下的候选锚点、9900条行动对照、聚合指标和数值诊断图。
类型始终是作者固定类型，不把候选开口人数称为已发布帖子。
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/raw"
OUT = ROOT / "presentation/hypothesis_4/2026-10-06-01-baseline-anchor"
WORKBOOK = ROOT / "data/baseline/抖音微博小红书-全量已打标.xlsx"
BENCH = ROOT / "hypothesis_4/benchmark_curves.json"
MECHANISMS = ROOT / "custom/envs/curation_mechanisms.py"
TYPES = {"meme": "梗文化讨论", "mourning": "事件悼念讨论", "marketing": "借势营销",
         "education": "教育观点讨论", "other": "其他讨论"}
COUNTS = {"meme": 19, "mourning": 22, "marketing": 23, "education": 15, "other": 21}
COHORT_N = {"meme": 5943, "mourning": 7056, "marketing": 7234, "education": 4917, "other": 6620}
PRE = [f"2026-W{w:02}" for w in range(5, 13)]
WEEKS = [f"2026-W{w:02}" for w in range(12, 23)]
VARIANTS = ["original", "population_posts", "cohort_authors"]


def digest(paths: list[Path]) -> str:
    """目录来源哈希含相对文件名和每个文件字节哈希，不输出昵称或正文。"""
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def jsonl(run: Path, table: str) -> list[dict]:
    """读取全部分片，不依赖已失效的SQLite缓存或修改归档。"""
    return [json.loads(line) for p in sorted((run / "replay").glob(f"{table}.*.jsonl"))
            for line in p.read_text().splitlines() if line.strip()]


def utility_anchor(activities: list[float], wanted: float) -> float:
    """保持旧整数阈值映射：低于0.5人时取最低阈值减0.02。"""
    acts = sorted(activities)
    wanted = max(0.0, min(float(len(acts)), wanted))
    if wanted < 0.5:
        return acts[0] - 0.02
    k = max(1, min(len(acts) - 1, round(wanted)))
    return (acts[k - 1] + acts[k]) / 2


def author_counts(matrix: dict) -> tuple[dict, list[dict], dict]:
    """固定全窗单类型作者队列；前期活动按作者×周去重，分母为队列人口。"""
    df = pd.read_excel(WORKBOOK, usecols=["数据有效性", "内容类别", "author", "published_at"])
    dates = pd.to_datetime(df["published_at"], utc=True)
    iso = dates.dt.isocalendar()
    df["week"] = [f"{y}-W{w:02}" for y, w in zip(iso["year"], iso["week"])]
    valid = df[df["数据有效性"] != "存疑"].copy()
    # 先核对全平台原帖子基准；未知作者只在用户口径排除，不能混入尺度对照。
    for week in PRE:
        for name in TYPES.values():
            assert int(((valid.week == week) & (valid["内容类别"] == name)).sum()) == matrix[week][name]
    known = valid[valid.author.notna()].copy()
    window = known[known.week.isin(WEEKS)]
    ntypes = window.groupby("author")["内容类别"].nunique()
    singles = window[window.author.isin(ntypes[ntypes == 1].index)].groupby("author")["内容类别"].first()
    rows, targets, accounting = [], {}, {}
    for typ, name in TYPES.items():
        cohort = set(singles[singles == name].index)
        assert len(cohort) == COHORT_N[typ], (typ, len(cohort))
        subset = known[(known.week.isin(PRE)) & (known["内容类别"] == name)]
        matched = subset[subset.author.isin(cohort)]
        a = matched.groupby("week").author.nunique().reindex(PRE, fill_value=0)
        targets[typ] = COUNTS[typ] * float(a.mean()) / len(cohort)
        accounting[typ] = {"cohort_users": len(cohort), "pre_all_author_weeks": len(subset[["week", "author"]].drop_duplicates()),
                           "pre_cohort_author_weeks": int(a.sum()), "pre_all_posts_with_author": len(subset)}
        for week in PRE:
            rows.append({"week": week, "type": typ, "cohort_users": len(cohort),
                         "cohort_active_authors": int(a.loc[week]), "benchmark_posts": matrix[week][name]})
    return targets, rows, accounting


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def plot(weekly: list[dict]) -> None:
    """一图三面板比较周总开口判定；固定曝光不代表新发帖轨迹。"""
    os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).parent / "tmp/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "pdf.fonttype": 42,
                         "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    labels = {"original": "Original", "population_posts": "Population scale", "cohort_authors": "Cohort activity"}
    peak = 0.0
    for ax, arm in zip(axes, ["interest", "random", "chronological"]):
        for variant, color in zip(VARIANTS, ["#333333", "#0072B2", "#D55E00"]):
            values = [mean(sum(r["speak_count"] for r in weekly if r["arm"] == arm and
                                r["seed"] == seed and r["week"] == week and r["variant"] == variant)
                           for seed in range(3)) for week in WEEKS]
            peak = max(peak, max(values))
            ax.plot(range(12, 23), values, label=labels[variant], color=color,
                    linestyle="-" if variant == "original" else "--", marker="o", markersize=3)
        ax.set_title(arm.capitalize())
        ax.set_xticks(range(12, 23), [f"W{w}" for w in range(12, 23)], rotation=45)
        ax.axvline(13, color="#999999", linewidth=.8)
        ax.grid(alpha=.2)
    axes[0].set_ylim(0, peak + 5)
    axes[0].set_ylabel("Speak decisions / week (3-seed mean)")
    axes[-1].legend(fontsize=8)
    fig.suptitle("Baseline-anchor diagnostic: historical exposure paths held fixed")
    fig.tight_layout()
    for ext in ["png", "svg"]:
        path = OUT / f"2026-10-06-01-fixed-exposure.{ext}"
        fig.savefig(path, dpi=180, bbox_inches="tight")
        if ext == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def main() -> None:
    started = datetime.now(timezone.utc)
    spec = importlib.util.spec_from_file_location("baseline_mechanisms", MECHANISMS)
    mech = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mech)
    matrix = json.loads(BENCH.read_text())["weekly_category_matrix"]
    cohorts, pre_rows, accounting = author_counts(matrix)
    expected = {
        "original": {t: mean(matrix[w][cn] for w in PRE) * 22 / 4714 for t, cn in TYPES.items()},
        "population_posts": {t: mean(matrix[w][cn] for w in PRE) * 100 / sum(COHORT_N.values()) for t, cn in TYPES.items()},
        "cohort_authors": cohorts,
    }
    actions, anchors, weekly, sources, checks = [], [], [], {}, []
    assert mech.anchored_utility(.7, 1.2, 1) == 1.2
    assert mech.anchored_utility(.7, 1.2, 0) == .7
    runs = sorted(RAW.glob("anchored_v1_*_s*"))
    assert len(runs) == 9
    for run in runs:
        arm, seed_text = run.name.removeprefix("anchored_v1_").rsplit("_s", 1)
        seed = int(seed_text)
        profiles = {int(p["id"]): json.loads(p["profile"]) if isinstance(p["profile"], str) else p["profile"]
                    for p in jsonl(run, "core_agent_profile")}
        replay_rows = jsonl(run, "curation_dynamics_agent_state")
        replay = {}
        for row in replay_rows:
            iso = datetime.fromisoformat(str(row["t"])).isocalendar()
            key = (int(row["agent_id"]), f"{iso.year}-W{iso.week:02}")
            assert key not in replay
            replay[key] = row
        assert len(profiles) == 100 and len(replay_rows) == len(replay) == 1100
        assert Counter(p["agent_type"] for p in profiles.values()) == COUNTS
        acts = {t: [p["params"]["activity"] for p in profiles.values() if p["agent_type"] == t] for t in TYPES}
        bs = {v: {t: utility_anchor(acts[t], expected[v][t]) for t in TYPES} for v in VARIANTS}
        for p in profiles.values():
            assert abs(bs["original"][p["agent_type"]] - p["params"]["baseline_utility"]) < 1e-10
        for v in VARIANTS:
            for typ in TYPES:
                anchors.append({"run": run.name, "variant": v, "type": typ, "expected_baseline_agents": expected[v][typ],
                                "B": bs[v][typ], "R0_speakers": sum(bs[v][typ] >= a for a in acts[typ])})
        grouped = defaultdict(lambda: [0, 0, 0])
        seen, max_error, w13, content_empty = set(), 0.0, 0, 0
        for f in sorted((run / "agents").glob("*/AGENT.json")):
            a = json.loads(f.read_text())
            aid = int(a["id"])
            p = profiles[aid]
            assert a["profile"] == p and len(a["decision_log"]) == 11
            typ, prm = p["agent_type"], p["params"]
            for log in a["decision_log"]:
                week, c = log["week"], log["components"]
                assert week in WEEKS and (aid, week) not in seen
                seen.add((aid, week))
                # 用实际整数槽数重建气候，避免使用日志中四位小数的占比。
                row = replay[(aid, week)]
                share = row[f"exposure_{typ}"] / row["feed_slots"] if row["feed_slots"] else 0.0
                assert row[f"climate_{typ}"] == share
                assert abs(c["share_own"] - share) <= .0000500001
                assert c["share_base"] == COUNTS[typ] / 100
                d = mech.spiral_factor(share, COUNTS[typ] / 100, prm["spiral"] * prm["spiral_scale"])
                r = mech.fatigue_factor(prm["decay"], c["cum_own"])
                us = {v: mech.anchored_utility(bs[v][typ], d, r) for v in VARIANTS}
                speak = {v: int(us[v] >= prm["activity"]) for v in VARIANTS}
                err = abs(us["original"] - log["u"])
                assert err <= .0000500001 and speak["original"] == int(log["speak"])
                assert int(row["spoke"]) == int(log["posted"])
                if speak["original"] != int(log["posted"]):
                    assert speak["original"] == 1 and log["reason"] == "content_empty"
                    content_empty += 1
                assert row["agent_type"] == typ
                max_error = max(max_error, err)
                w13 += int(week == "2026-W13" and typ == "mourning") * speak["original"]
                actions.append({"run": run.name, "arm": arm, "seed": seed, "agent_id": aid, "week": week,
                                "type": typ, "activity": prm["activity"], "D": d, "R": r,
                                "historical_posted": int(log["posted"]), "historical_content_empty": int(log["reason"] == "content_empty"),
                                **{f"B_{v}": bs[v][typ] for v in VARIANTS},
                                **{f"U_{v}": us[v] for v in VARIANTS}, **{f"speak_{v}": speak[v] for v in VARIANTS}})
                for v in VARIANTS:
                    g = grouped[(week, typ, v)]
                    g[0] += speak[v]
                    g[1] += int(speak["original"] == 1 and speak[v] == 0)
                    g[2] += int(speak["original"] == 0 and speak[v] == 1)
        assert len(seen) == 1100
        checks.append({"run": run.name, "actions": len(seen), "old_decision_mismatches": 0,
                       "replay_post_mismatches": 0, "max_U_rounding_error": max_error, "W13_mourning_speakers": w13,
                       "empty_feed_actions": sum(not row["feed_slots"] for row in replay_rows),
                       "historical_content_empty_actions": content_empty})
        for (week, typ, v), (spoke, off, on) in sorted(grouped.items()):
            weekly.append({"run": run.name, "arm": arm, "seed": seed, "week": week, "type": typ,
                           "variant": v, "actions": COUNTS[typ], "speak_count": spoke, "on_to_off": off, "off_to_on": on})
        sources[run.name] = {"path": str(run.relative_to(ROOT)), "agent_logs_hash": digest(list((run / "agents").glob("*/AGENT.json"))),
                             "profile_state_replay_hash": digest(list((run / "replay").glob("curation_dynamics_agent_state.*.jsonl")) +
                                                                list((run / "replay").glob("core_agent_profile.*.jsonl")))}
    assert len(actions) == 9900
    summary = []
    for run in runs:
        for v in VARIANTS:
            for period in ["W12-W22", "W19-W22"]:
                part = [a for a in actions if a["run"] == run.name and (period == "W12-W22" or a["week"] >= "2026-W19")]
                summary.append({"run": run.name, "variant": v, "period": period, "actions": len(part),
                                "speak_count": sum(a[f"speak_{v}"] for a in part),
                                "changed": sum(a[f"speak_{v}"] != a["speak_original"] for a in part),
                                "meme_speakers": sum(a[f"speak_{v}"] for a in part if a["type"] == "meme"),
                                "marketing_speakers": sum(a[f"speak_{v}"] for a in part if a["type"] == "marketing")})
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in [("pre_activity", pre_rows), ("anchors", anchors), ("decisions", actions), ("weekly", weekly), ("summary", summary)]:
        write_csv(OUT / f"2026-10-06-01-{name}.csv", rows)
    # 条件差先逐seed计算再平均，明确份额分母是开口判定而非实际正文。
    contrasts = []
    for v in VARIANTS:
        for period in ["W12-W22", "W19-W22"]:
            for seed in range(3):
                pair = {arm: next(s for s in summary if s["run"] == f"anchored_v1_{arm}_s{seed}" and
                                  s["variant"] == v and s["period"] == period) for arm in ["interest", "random"]}
                i, q = pair["interest"], pair["random"]
                contrasts.append({"variant": v, "period": period, "seed": seed,
                                  "interest_meme_count": i["meme_speakers"], "random_meme_count": q["meme_speakers"],
                                  "meme_count_difference": i["meme_speakers"] - q["meme_speakers"],
                                  "interest_meme_share": i["meme_speakers"] / i["speak_count"],
                                  "random_meme_share": q["meme_speakers"] / q["speak_count"],
                                  "meme_share_difference": i["meme_speakers"] / i["speak_count"] - q["meme_speakers"] / q["speak_count"]})
    write_csv(OUT / "2026-10-06-01-contrasts.csv", contrasts)
    manifest = {"run_id": "baseline_anchor_fixed_exposure_20261006_01", "kind": "fixed_exposure_numerical_diagnostic",
                "started_at": started.isoformat(), "ended_at": datetime.now(timezone.utc).isoformat(),
                "LLM_calls": 0, "LLM_tokens": 0, "actions": len(actions), "new_simulation_paths": 0,
                "code_baseline_commit": "b2fa8ec0293d96f604068c19666a116594caef29",
                "population_information_window": "W12-W22 retrospective", "expected_baseline_agents": expected,
                "cohort_accounting": accounting, "checks": checks, "input_hashes": sources,
                "workbook_hash": digest([WORKBOOK]), "benchmark_hash": digest([BENCH]),
                "script_hash": digest([Path(__file__)]), "formula_hash": digest([MECHANISMS]),
                "scope": "Only B changes; historical D/R/exposure/time/content remain fixed; no feedback or predictive validation."}
    (OUT / "2026-10-06-01-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    plot(weekly)
    print(json.dumps({"run_id": manifest["run_id"], "actions": len(actions), "old_decision_mismatches": 0,
                      "LLM_calls": 0, "expected_baseline_agents": expected,
                      "changed": {v: sum(s["changed"] for s in summary if s["variant"] == v and s["period"] == "W12-W22")
                                  for v in VARIANTS}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
