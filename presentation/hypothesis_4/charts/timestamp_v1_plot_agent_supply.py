#!/usr/bin/env python3
"""复用 chart3b 模板，绘制 timestamp_v1 正式实验的 Agent 周发帖量。

从项目根目录用 .env 的 PYTHON_PATH 运行；只读原始实验，不调用 LLM。
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
CHARTS = Path(__file__).resolve().parent
DATA = CHARTS.parent / "data"
BATCH = ROOT / "hypothesis_4/experiment_2/runs/timestamp_v1"
TEMPLATE = ROOT / "hypothesis_4/experiment_1/plot_run_charts.py"
TYPES = ("meme", "mourning", "education", "marketing", "other")
ARMS = ("random", "chronological", "interest")
WEEKS = [f"2026-W{w}" for w in range(12, 23)]
FIELDS = ["agent_supply", *[f"agent_supply_{t}" for t in TYPES]]
SQL = "SELECT week, " + ", ".join(FIELDS) + " FROM curation_dynamics_env_state ORDER BY week"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    batch = json.loads((BATCH / "execution_records/seed0_2/batch_execution.json").read_text())
    expected = {f"timestamp_v1_{arm}_s{seed}" for arm in ARMS for seed in range(3)}
    assert batch["status"] == "completed"
    assert {r["run_id"] for r in batch["completed"]} == expected

    # 直接调用模板，避免重新实现配色、事件标记或纵轴规则。
    spec = importlib.util.spec_from_file_location("chart3b_template", TEMPLATE)
    template = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(template)
    rows_by_run = {}
    all_rows = []
    evidence = []
    outputs = []
    for arm in ARMS:
        for seed in range(3):
            run_id = f"timestamp_v1_{arm}_s{seed}"
            run = BATCH / run_id
            pid = json.loads((run / "pid.json").read_text())
            step = json.loads((run / "SOCIETY_STEP.json").read_text())
            assert pid["status"] == "completed" and step["completed_step_count"] == 693
            command = [sys.executable, str(ROOT / ".agentsociety/bin/ags.py"),
                       "analysis", "query-data", "--data-path", str(run / "replay"), "--sql", SQL]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                    env={**os.environ, "LITELLM_LOCAL_MODEL_COST_MAP": "True"}, check=True)
            payload = json.loads(result.stdout)
            assert payload["success"], payload
            weekly = [dict(zip(payload["columns"], row)) for row in payload["rows"]]
            assert [w["week"] for w in weekly] == WEEKS

            # 用100人的持久化决策记录独立复算实际发布数，排除仅打算发帖但未成功者。
            actual = Counter()
            decisions = Counter()
            files = sorted((run / "agents").glob("*/AGENT.json"))
            assert len(files) == 100
            agent_sources = []
            for path in files:
                agent = json.loads(path.read_text())
                kind = agent["profile"]["agent_type"]
                assert kind in TYPES
                assert len(agent["decision_log"]) == 11
                for record in agent["decision_log"]:
                    decisions[record["week"]] += 1
                    if record.get("posted"):
                        actual[(record["week"], kind)] += 1
                agent_sources.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path)})
            assert all(decisions[w] == 100 for w in WEEKS)
            for w in weekly:
                assert all(isinstance(w[f], int) and w[f] >= 0 for f in FIELDS)
                assert w["agent_supply"] == sum(w[f"agent_supply_{t}"] for t in TYPES)
                assert w["agent_supply"] <= 80
                for kind in TYPES:
                    assert w[f"agent_supply_{kind}"] == actual[(w["week"], kind)]
                all_rows.append({"run_id": run_id, "arm": arm, "seed": seed, **w})
            rows_by_run[run_id] = weekly
            stem = CHARTS / f"{run_id}__chart3b_agent_supply_stacked_area"
            for ext in (".png", ".svg"):
                template.chart3b_agent_supply_stacked_area(weekly, run_id, stem.with_suffix(ext))
            outputs.extend([str(stem.with_suffix(ext).relative_to(ROOT)) for ext in (".png", ".svg")])
            replay_files = [run / "replay/_schema.json", *sorted((run / "replay").glob("curation_dynamics_env_state.*.jsonl"))]
            evidence.append({"run_id": run_id, "weeks": len(weekly), "actions": sum(decisions.values()),
                             "posts": sum(w["agent_supply"] for w in weekly),
                             "weekly_peak": max(w["agent_supply"] for w in weekly),
                             "decision_log_crosscheck": "PASS: all 11 weeks × 5 types",
                             "sources": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in replay_files],
                             "agent_sources": agent_sources})
            print(run_id, 'posts=', evidence[-1]["posts"], 'peak=', evidence[-1]["weekly_peak"], flush=True)

    means = []
    for arm in ARMS:
        weekly = []
        for index, week in enumerate(WEEKS):
            row = {"week": week, **{f: sum(rows_by_run[f"timestamp_v1_{arm}_s{s}"][index][f] for s in range(3)) / 3 for f in FIELDS}}
            weekly.append(row)
            means.append({"arm": arm, "n_seeds": 3, **row})
        stem = CHARTS / f"timestamp_v1_{arm}_mean__chart3b_agent_supply_stacked_area"
        for ext in (".png", ".svg"):
            template.chart3b_agent_supply_stacked_area(weekly, f"timestamp_v1_{arm}，三次重复均值", stem.with_suffix(ext))
        outputs.extend([str(stem.with_suffix(ext).relative_to(ROOT)) for ext in (".png", ".svg")])
    dump_csv(DATA / "timestamp_v1_agent_supply_by_run_week.csv", all_rows)
    dump_csv(DATA / "timestamp_v1_agent_supply_arm_week_mean.csv", means)
    manifest = {
        "batch": str(BATCH.relative_to(ROOT)), "query": SQL,
        "figure_contract": {
            "purpose": "描述三种正式策展制度下W12–W22五类Agent实际发帖量及其变化。",
            "scope": "9个单次运行图、3个制度内三seed算术均值图；均值不表示单次实测整数。",
            "measure": "按固定Agent类型pool_type统计成功发布；排除外部注入帖、历史池和官方输入。",
            "style": "复用原chart3b函数，五类顺序/配色、W13事件线、0–80纵轴不变。",
            "limitations": "仿真描述性轨迹；作者类型不是正文语义重分类；3次重复均值不含置信区间。",
        },
        "template": {"path": str(TEMPLATE.relative_to(ROOT)), "sha256": digest(TEMPLATE)},
        "script": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))},
        "batch_execution_sha256": digest(BATCH / "execution_records/seed0_2/batch_execution.json"),
        "runs": evidence, "chart_outputs": outputs,
    }
    (DATA / "timestamp_v1_agent_supply_sources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
