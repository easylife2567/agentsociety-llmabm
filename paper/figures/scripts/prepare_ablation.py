#!/usr/bin/env python3
"""离线整理正文图5的正式timestamp B/D/R消融数据，不绘图或运行模型。

从项目根运行：
    AgentSociety2/.venv/bin/python paper/figures/scripts/prepare_ablation.py
比例按0—1保存；先在每seed内计算，再对三个配对seed取均值。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import statistics
import subprocess
from pathlib import Path

CONDITIONS = ("full", "no_b", "no_d", "no_r")
SEEDS = (0, 1, 2)
LATE = tuple(f"2026-W{week}" for week in range(19, 23))
MID = tuple(f"2026-W{week}" for week in range(14, 19))
METRICS = (
    ("a", "late_posts_per_week", "no_b", "B = 0", LATE, "posts_per_week", "all"),
    ("b", "late_meme_post_rate", "no_d", "D = 1", LATE, "proportion", "meme"),
    ("c", "mid_post_rate", "no_r", "R = 1", MID, "proportion", "all"),
    ("d", "late_meme_author_share", "no_r", "R = 1", LATE, "proportion", "all"),
    ("e", "late_meme_exposure_non_meme", "no_r", "R = 1", LATE, "proportion", "non_meme"),
)


def require(condition: bool, message: object) -> None:
    if not condition:
        raise ValueError(str(message))


def close(actual: float, expected: float, context: object) -> None:
    require(math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9),
            {"context": context, "actual": actual, "expected": expected})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--qa-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.project_root.resolve()
    out = (args.output_dir or root / "paper/figures/source_data").resolve()
    qa = (args.qa_dir or root / "paper/figures/qa").resolve()
    base = root / "presentation/hypothesis_4/timestamp_bdr_v1"
    sources: dict[str, dict] = {}

    def read_bytes(path: Path, role: str) -> bytes:
        data = path.read_bytes()
        sources[str(path.relative_to(root))] = {
            "role": role, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()
        }
        return data

    def read_csv(name: str, role: str) -> list[dict[str, str]]:
        return list(csv.DictReader(io.StringIO(
            read_bytes(base / "data" / name, role).decode("utf-8-sig"))))

    weekly = read_csv("weekly_by_type.csv", "official_successful_posts_and_opportunities")
    exposure = read_csv("weekly_exposure_by_cohort.csv", "official_actual_feed_counts")
    run_metrics = read_csv("run_metrics.csv", "crosscheck_official_per_seed_metrics")
    paired = read_csv("paired_summary.csv", "crosscheck_official_paired_summaries")
    definitions = json.loads(read_bytes(base / "data/metric_dictionary.json", "metric_definitions"))
    read_bytes(base / "data/source_index.json", "upstream_raw_result_locations_and_hashes")
    read_bytes(base / "report_zh.md", "accepted_results_and_limits")
    read_bytes(root / "hypothesis_4/experiment_3/EXPERIMENT.md", "frozen_ablation_design")

    # 从正式逐周计数独立汇总，再与正式窗口指标和配对统计逐项交叉。
    require(len(weekly) == len({(r["condition"], r["seed"], r["week"], r["agent_type"])
                               for r in weekly}) == 660, "逐周作者表须为660个唯一单元")
    require(len(exposure) == len({(r["condition"], r["seed"], r["week"], r["cohort"])
                                 for r in exposure}) == 264, "逐周接触表须为264个唯一单元")
    run_index = {(r["condition"], int(r["seed"])): r for r in run_metrics}
    require(set(run_index) == {(c, s) for c in CONDITIONS for s in SEEDS}, "须有完整12单元")
    paired_index = {(r["condition"], r["metric"]): r for r in paired}
    records, summaries = [], []
    comparisons = 0
    for panel, metric, ablation, label, weeks, unit, cohort in METRICS:
        values: dict[str, list[float]] = {"full": [], ablation: []}
        for condition in ("full", ablation):
            for seed in SEEDS:
                source = run_index[(condition, seed)]
                group = [r for r in weekly if r["condition"] == condition
                         and int(r["seed"]) == seed and r["week"] in weeks]
                require(len(group) == len(weeks) * 5, (condition, seed, metric, "缺少逐周类型"))
                require(all(r["run_id"] == source["run_id"] for r in group), "run_id不一致")
                if metric == "late_posts_per_week":
                    numerator = sum(int(r["posted"]) for r in group)
                    denominator, denominator_unit = len(weeks), "weeks"
                elif metric in ("late_meme_post_rate", "mid_post_rate"):
                    selected = [r for r in group if cohort == "all" or r["agent_type"] == cohort]
                    numerator = sum(int(r["posted"]) for r in selected)
                    denominator = sum(int(r["opportunities"]) for r in selected)
                    require(denominator == (76 if cohort == "meme" else 500), "机会分母不一致")
                    require(numerator == sum(int(r["speak"]) for r in selected),
                            "所选条件发言与成功发布已不相等，不能沿用正文口径")
                    denominator_unit = "opportunities"
                elif metric == "late_meme_author_share":
                    numerator = sum(int(r["posted"]) for r in group if r["agent_type"] == "meme")
                    denominator = sum(int(r["posted"]) for r in group)
                    denominator_unit = "successful_agent_posts"
                else:
                    selected = [r for r in exposure if r["condition"] == condition
                                and int(r["seed"]) == seed and r["week"] in weeks
                                and r["cohort"] == "non_meme"]
                    require(len(selected) == 4, "跨群体接触须包含晚期四周")
                    numerator = sum(int(r["meme_slots"]) for r in selected)
                    denominator = sum(int(r["feed_slots"]) for r in selected)
                    require(denominator == 3240, "非玩梗型作者实际feed分母不一致")
                    require(all(int(r["feed_slots"]) == int(r["agent_post_slots"])
                                + int(r["external_post_slots"]) for r in selected), "feed来源计数不闭合")
                    denominator_unit = "actual_feed_slots"
                require(denominator > 0, (metric, condition, seed, "零分母"))
                value = numerator / denominator
                close(value, float(source[metric]), (metric, condition, seed))
                if unit == "proportion":
                    require(0 <= value <= 1, "比例必须在0—1内")
                values[condition].append(value)
                records.append({
                    "panel": panel, "metric": metric, "comparison": ablation,
                    "condition": condition, "condition_label": "Full" if condition == "full" else label,
                    "seed": seed, "run_id": source["run_id"],
                    "week_start": weeks[0], "week_end": weeks[-1], "cohort": cohort,
                    "numerator": numerator, "denominator": denominator,
                    "denominator_unit": denominator_unit, "unit": unit, "value": value,
                })
                comparisons += 1
        deltas = [a - f for a, f in zip(values[ablation], values["full"])]
        summary = {
            "panel": panel, "metric": metric, "comparison": ablation, "unit": unit,
            "window": list(weeks), "n_paired_seeds": 3,
            "full_values_by_seed": values["full"], "ablation_values_by_seed": values[ablation],
            "full_mean": statistics.mean(values["full"]),
            "ablation_mean": statistics.mean(values[ablation]),
            "paired_deltas_by_seed": deltas, "delta_mean": statistics.mean(deltas),
            "delta_min": min(deltas), "delta_max": max(deltas),
            "all_paired_deltas_negative": all(d < 0 for d in deltas),
            "all_paired_deltas_positive": all(d > 0 for d in deltas),
        }
        official = paired_index[(ablation, metric)]
        require(int(official["n"]) == 3, "正式配对表重复数改变")
        for field in ("full_mean", "ablation_mean", "delta_mean", "delta_min", "delta_max"):
            close(summary[field], float(official[field]), (metric, "paired_summary", field))
            comparisons += 1
        require(summary["all_paired_deltas_positive"] if metric == "mid_post_rate"
                else summary["all_paired_deltas_negative"], (metric, "三seed方向不一致"))
        summaries.append(summary)

    require(len(records) == 30, "图5须为5指标×2条件×3seed共30条")
    out.mkdir(parents=True, exist_ok=True)
    qa.mkdir(parents=True, exist_ok=True)
    csv_path = out / "ablation_metrics.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    script = Path(__file__).resolve()
    manifest = {
        "figure": 5, "data_identity": "timestamp_bdr_v1, interest curation only",
        "full_batch": "hypothesis_4/experiment_2/runs/timestamp_v1",
        "ablation_batch": "hypothesis_4/experiment_3/runs/timestamp_bdr_v1_attempt_02",
        "seeds": list(SEEDS), "conditions": list(CONDITIONS),
        "python": platform.python_version(),
        "git_commit_at_preparation": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "script": {"path": str(script.relative_to(root)),
                   "sha256": hashlib.sha256(script.read_bytes()).hexdigest()},
        "calculation_rules": {
            "aggregation": "先汇总每run的窗口分子/分母，再对三个seed比值取算术均值；连线只连接同seed。",
            "late_posts_per_week": "W19—W22全部固定作者群体成功发布数/4周，不含外部与官方输入。",
            "late_meme_post_rate": "W19—W22玩梗型作者成功发布数/(19人×4周=76机会)。",
            "mid_post_rate": "W14—W18全体作者成功发布数/(100人×5周=500机会)。",
            "late_meme_author_share": "W19—W22玩梗型作者成功发布数/全部智能体成功发布数。",
            "late_meme_exposure_non_meme": "W19—W22非玩梗型作者所见type=meme槽位/全部实际3240个feed槽位，含外部与生成帖，不是图4仅生成帖跨群体项。",
            "unit": "proportion保存为0—1，展示百分比时乘100；posts_per_week保持帖/周。",
            "delta": "每seed消融减同seed Full；范围为实际三配对差值最小—最大，不是置信区间。",
        },
        "measurement_contract": definitions["labels"],
        "reading_limit": "展示统计是实际数值feed槽位；不等同全部槽位正文都进入LLM提示。",
        "comparison_limits": [
            "固定同一人口/行动表的三个配对seed，不将机会或周当独立重复。",
            "组件比较限于冻结兴趣制度，允许后续供给、接触和正文反馈自然分叉。",
            "R=1同时令U=D并取消B权重，比较不是保持B贡献不变的正交R效应。",
            "Full与消融分批运行，API路径及返回模型标识差异尚未通过同期新对照排除。",
            "生成帖按固定作者类型归类，外部帖沿用来源标签；没有新增独立正文语义编码。",
        ],
        "checks": {"all_passed": True, "long_table_rows": len(records),
                   "metric_pairs": len(summaries), "numeric_crosschecks": comparisons},
        "metric_summaries": summaries,
        "output_sha256": {csv_path.name: hashlib.sha256(csv_path.read_bytes()).hexdigest()},
        "sources": sources,
    }
    manifest_path = out / "ablation_sources.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks = {
        "figure": 5, "checks": manifest["checks"], "metric_summaries": summaries,
        "source_manifest": str(manifest_path.relative_to(root)),
        "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "conflicts": [],
    }
    (qa / "ablation_checks.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": manifest["checks"], "means": [
        {k: s[k] for k in ("metric", "full_mean", "ablation_mean", "unit")}
        for s in summaries]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
