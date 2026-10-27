#!/usr/bin/env python3
"""离线整理正文图3、图4的原timestamp_v1数据，并核对原始成功发布记录。

从项目根运行：
    AgentSociety2/.venv/bin/python paper/figures/scripts/prepare_simulation.py
本脚本只读取既有结果，不运行社会仿真、网络请求或LLM。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import statistics
import subprocess
from collections import Counter
from pathlib import Path

ARMS = ("random", "chronological", "interest")
CATEGORIES = ("education", "mourning", "meme", "marketing", "other")
WEEKS = tuple(f"2026-W{week}" for week in range(12, 23))
LATE_WEEKS = WEEKS[7:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.project_root.resolve()
    out = args.output_dir or root / "paper/figures/source_data"
    qa = root / "paper/figures/qa"
    out.mkdir(parents=True, exist_ok=True)
    qa.mkdir(parents=True, exist_ok=True)
    sources: dict[str, dict] = {}

    def read_bytes(path: Path, role: str) -> bytes:
        data = path.read_bytes()
        sources[str(path.relative_to(root))] = {
            "role": role, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()
        }
        return data

    def read_json(path: Path, role: str) -> dict:
        return json.loads(read_bytes(path, role))

    def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
        with (out / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    # 周供给采用正式派生表；后续逐run、逐周、逐类型与AGENT成功发布记录交叉。
    source_csv = root / "presentation/hypothesis_4/data/timestamp_v1_agent_supply_by_run_week.csv"
    rows = list(csv.DictReader(io.StringIO(read_bytes(source_csv, "official_weekly_supply").decode("utf-8-sig"))))
    weekly_index = {(row["arm"], int(row["seed"]), row["week"]): row for row in rows}
    assert len(rows) == len(weekly_index) == 99, "正式周表应为9 run×11周，且没有重复键"
    weekly, late, exposure, runs = [], [], [], []
    total_posts = 0
    for arm in ARMS:
        for seed in range(3):
            run_id = f"timestamp_v1_{arm}_s{seed}"
            run = root / "hypothesis_4/experiment_2/runs/timestamp_v1" / run_id
            completion = read_json(run / "SOCIETY_STEP.json", "engine_completion")
            assert completion["completed_step_count"] == 693
            assert completion["current_time"] == "2026-06-01T00:00:00"
            env = read_json(run / "env/CurationDynamicsSpace/state/ENV_STATE.json", "raw_actual_feed_actions")
            actions = env["_arrival_state"]["actions"]
            assert len(actions) == 1100
            assert len({(a["agent_id"], a["week"]) for a in actions}) == 1100
            late_actions = [a for a in actions if a["week"] in LATE_WEEKS]
            own_actions = [a for a in late_actions if a["agent_type"] == "meme"]
            cross_actions = [a for a in late_actions if a["agent_type"] != "meme"]
            own_feed = [post for action in own_actions for post in action["feed"]]
            cross_feed = [post for action in cross_actions for post in action["feed"]]
            assert (len(late_actions), len(own_actions), len(cross_actions)) == (400, 76, 324)
            assert (len(own_feed), len(cross_feed)) == (760, 3240)
            assert all(len(action["feed"]) == 10 for action in late_actions)

            posted_counts = Counter()
            model_names = Counter()
            agent_files = sorted((run / "agents").glob("agent_*/AGENT.json"))
            assert len(agent_files) == 100
            opportunities = 0
            for agent_path in agent_files:
                agent = read_json(agent_path, "raw_successful_post_decisions")
                category = agent["profile"]["agent_type"]
                assert category in CATEGORIES
                assert len(agent["decision_log"]) == 11
                opportunities += len(agent["decision_log"])
                for decision in agent["decision_log"]:
                    if decision.get("posted"):
                        posted_counts[(decision["week"], category)] += 1
                        if decision.get("response_model"):
                            model_names[decision["response_model"]] += 1
            assert opportunities == 1100
            for week in WEEKS:
                row = weekly_index[(arm, seed, week)]
                assert row["run_id"] == run_id
                for category in CATEGORIES:
                    count = int(row[f"agent_supply_{category}"])
                    assert count == posted_counts[(week, category)], (run_id, week, category)
                    weekly.append({"arm": arm, "seed": seed, "week": week, "category": category, "count": count})
                assert sum(posted_counts[(week, c)] for c in CATEGORIES) == int(row["agent_supply"])
            meme_posts = sum(posted_counts[(week, "meme")] for week in LATE_WEEKS)
            n_posts = sum(count for (week, _), count in posted_counts.items() if week in LATE_WEEKS)
            late.append({"arm": arm, "seed": seed, "meme_posts": meme_posts, "total_posts": n_posts, "meme_share": meme_posts / n_posts})
            own_meme_slots = sum(post["type"] == "meme" for post in own_feed)
            cross_generated_slots = sum(post.get("source") == "agent" and post["type"] == "meme" for post in cross_feed)
            exposure.append({"arm": arm, "seed": seed, "own_share": own_meme_slots / len(own_feed), "meme_post_rate": meme_posts / len(own_actions), "cross_generated_share": cross_generated_slots / len(cross_feed)})
            total_posts += sum(posted_counts.values())
            runs.append({
                "run_id": run_id, "actions": opportunities, "weeks": 11,
                "posts": sum(posted_counts.values()), "late_posts": n_posts, "late_meme_posts": meme_posts,
                "late_own_opportunities": len(own_actions), "late_own_feed_slots": len(own_feed),
                "late_own_meme_slots": own_meme_slots, "late_cross_feed_slots": len(cross_feed),
                "late_cross_generated_meme_slots": cross_generated_slots,
                "response_model_counts": dict(model_names),
                "weekly_type_successful_posts_match": True,
            })
    assert total_posts == 1818
    means = {
        arm: {key: statistics.mean(row[key] for row in exposure if row["arm"] == arm)
              for key in ("own_share", "meme_post_rate", "cross_generated_share")}
        for arm in ARMS
    }
    expected_percent = {
        "random": (3.201754385964912, 3.9473684210526314, 0.1131687242798354),
        "chronological": (42.01754385964912, 56.57894736842105, 22.73662551440329),
        "interest": (25.17543859649123, 47.80701754385965, 6.841563786008231),
    }
    for arm, expected in expected_percent.items():
        for key, value in zip(("own_share", "meme_post_rate", "cross_generated_share"), expected):
            assert abs(100 * means[arm][key] - value) < 1e-9, (arm, key)
    write_csv("simulation_weekly.csv", ["arm", "seed", "week", "category", "count"], weekly)
    write_csv("simulation_late.csv", ["arm", "seed", "meme_posts", "total_posts", "meme_share"], late)
    write_csv("simulation_exposure.csv", ["arm", "seed", "own_share", "meme_post_rate", "cross_generated_share"], exposure)
    outputs = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in ("simulation_weekly.csv", "simulation_late.csv", "simulation_exposure.csv")}
    manifest = {
        "batch": "hypothesis_4/experiment_2/runs/timestamp_v1", "arms": list(ARMS), "seeds": [0, 1, 2],
        "window": list(WEEKS), "late_window": list(LATE_WEEKS), "python": platform.python_version(),
        "git_commit_at_preparation": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "script": {"path": str(Path(__file__).resolve().relative_to(root)), "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "measurement_contract": {
            "simulation_weekly": "成功发布供给按固定作者agent_type归类，排除外部输入、官方帖和初始历史池；不是生成正文的独立语义分类。",
            "simulation_late": "每seed内W19—W22玩梗型作者供给/全部五类作者供给。绘制制度值时先逐seed计算再取算术均值。",
            "own_share": "W19—W22玩梗型用户实际数值feed中type=meme槽位/该群体全部760槽；type是环境标签，feed包含外部帖和生成帖。",
            "meme_post_rate": "W19—W22玩梗型用户成功发布次数/19人×4周=76次机会。",
            "cross_generated_share": "W19—W22非玩梗型用户feed中source=agent且type=meme槽位/该群体全部3240槽。衡量实际再次展示，不是候选池占比，也不是回流独立净效应。",
            "unit": "所有share/rate保存为0—1比例；作百分比展示时乘100。",
            "reading_limit": "接触指实际数值feed槽位（每次10槽）；正文生成仅取前5条，不将10槽等同LLM读入文字。",
        },
        "runs": runs, "arm_mean_exposure": means,
        "checks": {"weekly_rows": len(weekly), "run_late_rows": len(late), "run_exposure_rows": len(exposure), "successful_posts": total_posts, "weekly_type_comparisons": 495, "all_passed": True},
        "output_sha256": outputs, "sources": sources,
    }
    (out / "simulation_sources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks = {"batch": manifest["batch"], "checks": manifest["checks"], "arm_mean_exposure": means, "source_manifest": str((out / "simulation_sources.json").relative_to(root))}
    (qa / "simulation_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
