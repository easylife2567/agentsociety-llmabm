"""冻结统一论文图2—6所需数据，只读原始来源，不启动仿真或联网。"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import openpyxl
import pandas as pd

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
DATA = OUT / "source_data"
QA = OUT / "qa"
OLD = OUT.parent / "figures_seed10/source_data"
HOURLY = OUT.parent / "figures_hourly_return_v1/source_data"
FORMAL = ROOT / "presentation/hypothesis_4/hourly_return_v1"
MANIFEST = ROOT / "hypothesis_4/experiment_2/runs/hourly_return_v1/manifest.json"
ARMS = ("random", "chronological", "interest")
CATEGORIES = ("education", "mourning", "meme", "other", "marketing")
WEEKS = tuple(f"2026-W{w:02d}" for w in range(12, 23))
LATE = WEEKS[-4:]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main():
    DATA.mkdir(exist_ok=True)
    QA.mkdir(exist_ok=True)
    sources = {}

    def tracked(path, expected=None):
        path = Path(path)
        digest = sha(path)
        if expected is not None:
            assert digest == expected, (str(path), digest, expected)
        sources[str(path.relative_to(ROOT))] = digest
        return path

    def freeze(path, name=None, expected=None):
        path = tracked(path, expected)
        output = DATA / (name or path.name)
        content = path.read_bytes()
        if output.exists():
            assert output.read_bytes() == content, ("frozen output differs", str(output))
        output.write_bytes(content)
        return output

    # 总量趋势使用全部采集样本；五类构成和焦点类型计数沿用既有分类周表。
    observed_source = read(tracked(OLD / "observed_sources.json"))
    workbook = ROOT / "data/baseline/抖音微博小红书-全量已打标.xlsx"
    workbook_expected = next(s["sha256"] for s in observed_source["sources"] if s["path"] == str(workbook.relative_to(ROOT)))
    tracked(workbook, workbook_expected)
    weekly_raw = Counter()
    weekly_classified = Counter()
    mapping = {"gsdata": "douyin", "sinamidu": "xiaohongshu"}
    category_mapping = {"教育观点讨论": "education", "事件悼念讨论": "mourning", "梗文化讨论": "meme", "其他讨论": "other", "借势营销": "marketing"}
    book = openpyxl.load_workbook(workbook, read_only=True, data_only=True)
    for row in book.active.iter_rows(min_row=2, values_only=True):
        platform = mapping.get(str(row[14]).strip())
        if platform is None:
            continue
        moment = row[12]
        if not isinstance(moment, datetime):
            moment = datetime.fromisoformat(str(moment).replace("Z", "+00:00"))
        iso = moment.isocalendar()
        week = f"{iso.year}-W{iso.week:02d}"
        weekly_raw[platform, week] += 1
        if row[1] in category_mapping:
            weekly_classified[platform, week, category_mapping[row[1]]] += 1
    book.close()
    assert sum(weekly_raw.values()) == 49930
    assert sum(weekly_classified.values()) == 46602
    for platform, expected in observed_source["source_audit"]["raw_week_counts_by_platform"].items():
        assert {w: v for (p, w), v in weekly_raw.items() if p == platform} == expected
    observed_path = freeze(OLD / "observed_weekly.csv")
    freeze(OLD / "observed_sources.json")
    observed = pd.read_csv(observed_path)
    assert len(observed) == 270
    for row in observed.itertuples():
        total = sum(weekly_classified[p, row.week, row.category] for p in ("douyin", "xiaohongshu")) if row.platform == "pooled" else weekly_classified[row.platform, row.week, row.category]
        assert int(row.count) == total
    raw_rows = []
    for platform, output_name in (("douyin", "douyin"), ("xiaohongshu", "rednote"), ("pooled", "pooled")):
        for week in sorted({w for _, w in weekly_raw}):
            total = sum(weekly_raw[p, week] for p in ("douyin", "xiaohongshu")) if platform == "pooled" else weekly_raw[platform, week]
            raw_rows.append(dict(platform=output_name, week=week, total_posts=total))
    pd.DataFrame(raw_rows).to_csv(DATA / "observed_total.csv", index=False)

    # 正式小时回流30run矩阵，保持时序复用来源身份。
    previous = read(tracked(HOURLY / "figure_sources.json"))
    freeze(HOURLY / "weekly_supply.csv", expected=previous["output_sha256"]["weekly_supply.csv"])
    freeze(HOURLY / "main_runs.csv", expected=previous["output_sha256"]["main_runs.csv"])
    official_weekly_path = freeze(FORMAL / "results/weekly.csv", "official_weekly.csv", previous["output_sha256"]["official_weekly.csv"])
    official_runs_path = freeze(FORMAL / "results/run_metrics.csv", "official_run_metrics.csv", previous["output_sha256"]["official_run_metrics.csv"])
    freeze(MANIFEST, "official_manifest.json", previous["output_sha256"]["official_manifest.json"])
    freeze(FORMAL / "results/provenance.json", "official_provenance.json", previous["output_sha256"]["official_provenance.json"])
    manifest = read(MANIFEST)
    assert manifest["status"] == "passed" and manifest["adopted"] is True
    official_weekly = pd.read_csv(official_weekly_path)
    official_runs = pd.read_csv(official_runs_path)
    weekly = pd.read_csv(DATA / "weekly_supply.csv")
    runs = pd.read_csv(DATA / "main_runs.csv")
    assert len(weekly) == len(official_weekly) == 330
    assert len(runs) == len(official_runs) == 30
    assert {(r["algorithm"], r["seed"]) for r in manifest["runs"]} == {(arm, seed) for arm in ARMS for seed in range(10)}
    for row in weekly.itertuples():
        ref = official_weekly[(official_weekly.algorithm == row.arm) & (official_weekly.seed == row.seed) & (official_weekly.week == row.week)].iloc[0]
        assert row.agent_supply == ref.posted_total
        for category in CATEGORIES:
            assert getattr(row, f"agent_supply_{category}") == ref[f"posted_{category}_authors"]
    for row in runs.itertuples():
        ref = official_runs[(official_runs.algorithm == row.arm) & (official_runs.seed == row.seed)].iloc[0]
        assert row.run_id == ref.run_id
        assert int(row.total_posts) == int(ref.total_posts)
        assert int(row.late_meme_posts) == int(ref.late_meme_posts)
        assert int(row.late_total_posts) == int(ref.late_total_posts)
        assert np.isclose(row.late_meme_share, ref.late_meme_share)

    # 图5重新逐run读取ENV，核对三指标的实际分子、分母。
    feedback, raw_checks = [], []
    for descriptor in sorted(manifest["runs"], key=lambda d: (ARMS.index(d["algorithm"]), d["seed"])):
        arm, seed = descriptor["algorithm"], descriptor["seed"]
        relative = "env/CurationDynamicsSpace/state/ENV_STATE.json"
        env_path = tracked(ROOT / descriptor["run_dir"] / relative, descriptor["frozen"][relative])
        env = read(env_path)
        actions = env["_arrival_state"]["actions"]
        assert len(actions) == 1100 and len({(str(a["agent_id"]), a["week"]) for a in actions}) == 1100
        late_actions = [a for a in actions if a["week"] in LATE]
        meme_actions = [a for a in late_actions if a["agent_type"] == "meme"]
        assert len(late_actions) == 400 and len(meme_actions) == 76
        own = [p for a in meme_actions for p in a["feed"]]
        cross = [p for a in late_actions if a["agent_type"] != "meme" for p in a["feed"]]
        own_num = sum(p["type"] == "meme" for p in own)
        cross_num = sum(p["source"] == "agent" and p["type"] == "meme" for p in cross)
        assert len(own) == 760 and len(cross) == 3240
        agent_type = {str(a["agent_id"]): a["agent_type"] for a in actions}
        posted = [p for p in env["_posts"].values() if p.get("source") == "agent" and p["source_week"] in LATE]
        meme_post_num = sum(agent_type[str(p["author_id"])] == "meme" for p in posted)
        ref = official_runs[(official_runs.algorithm == arm) & (official_runs.seed == seed)].iloc[0]
        ref_weekly = official_weekly[(official_weekly.algorithm == arm) & (official_weekly.seed == seed) & official_weekly.week.isin(LATE)]
        assert meme_post_num == ref.late_meme_posts == ref_weekly.posted_meme_authors.sum()
        assert np.isclose(own_num / len(own), ref.late_own_meme_tag_share)
        assert np.isclose(cross_num / len(cross), ref.late_cross_generated_meme_share)
        feedback.append(dict(arm=arm, seed=seed, run_id=descriptor["run_id"], own_share=own_num / len(own), meme_post_rate=meme_post_num / len(meme_actions), cross_generated_share=cross_num / len(cross), own_numerator=own_num, own_denominator=len(own), meme_post_numerator=meme_post_num, meme_post_denominator=len(meme_actions), cross_generated_numerator=cross_num, cross_generated_denominator=len(cross)))
        raw_checks.append(dict(arm=arm, seed=seed, run_id=descriptor["run_id"], env_sha256=sha(env_path), actions=1100, late_actions=400, own_denominator=len(own), meme_post_denominator=len(meme_actions), cross_generated_denominator=len(cross)))
    feedback_frame = pd.DataFrame(feedback)
    feedback_frame.to_csv(DATA / "feedback_runs.csv", index=False)

    # 旧组件消融保留同批Full与干预配对，绝不替换成新版Full。
    ablation_source_path = tracked(OLD / "ablation_seed10_sources.json")
    ablation_source = read(ablation_source_path)
    ablation_path = freeze(OLD / "ablation_seed10_metrics.csv", "ablation_metrics.csv", ablation_source["output_sha256"]["ablation_seed10_metrics.csv"])
    ablation = pd.read_csv(ablation_path)
    assert len(ablation) == 100 and not ablation.duplicated(["panel", "condition", "seed"]).any()
    assert set(ablation.seed) == set(range(10))
    assert np.allclose(ablation.value, ablation.numerator / ablation.denominator)
    assert set(ablation[ablation.condition == "full"].run_id) == {f"timestamp_v1_interest_s{s}" for s in range(10)}
    write_json(DATA / "ablation_source_index.json", dict(source_path=str(ablation_source_path.relative_to(ROOT)), source_sha256=sha(ablation_source_path), metrics_sha256=sha(ablation_path), scope=ablation_source["scope"], scientific_comparability=ablation_source["scientific_comparability"], runs=ablation_source["runs"], excluded=ablation_source["excluded"], panel_e_definition=ablation_source["panel_e_definition"], display_R="R → 1", actual_no_r="decay parameter set to 0; computed fatigue factor R equals 1"))

    generated = {p.name: sha(p) for p in sorted(DATA.iterdir()) if p.is_file() and p.name != "provenance.json"}
    provenance = dict(created_at=datetime.now(timezone.utc).isoformat(), scope="Unified figures 2–6; figure 1 unchanged", source_sha256=sources, output_sha256=generated, preparation_script_sha256=sha(Path(__file__)), observed_total="49,930 raw collected posts; original timestamp ISO week; all classified, noise and uncertain rows retained in total", observed_categories="46,602 posts assigned to five categories; same category mapping as accepted source matrix", main_matrix="hourly_return_v1: 20 random/interest new runs and 10 equivalent historical chronological runs", ablation_matrix="Original timestamp_v1 interest Full paired with no_b/no_d/no_r, 10 seeds each; no new hourly Full substitution", display_platform_mapping={"xiaohongshu": "Rednote", "douyin": "Douyin"}, formulas=dict(own_share="memetic-tag feed items viewed by memetic-type authors / all their actual feed items, W19–W22", meme_post_rate="successful posts by memetic-type authors / their expression opportunities, W19–W22", cross_generated_share="generated memetic-tag feed items viewed by non-memetic authors / all their actual feed items, W19–W22"), feedback_raw_checks=raw_checks, reused_verification="Formal hourly analysis previously verified all Agent decisions, official replay and recirculation; this preparation rereads 30 ENV and verifies actual feedback denominators and successful posts; no replay SQL or Agent-file rescan", model_identity=official_runs.groupby("algorithm")["model"].unique().map(list).to_dict(), simulation_calls=0, network_calls=0)
    write_json(DATA / "provenance.json", provenance)
    write_json(QA / "data_checks.json", dict(passed=True, observed_raw_workbook_rows_verified=49930, observed_five_category_rows_verified=46602, observed_weeks=18, raw_total_peak_W13=10674, observed_total_rows=54, observed_category_rows=270, main_runs=30, main_week_rows=330, raw_feedback_ENV_verified=30, actual_denominators=dict(own=760, meme_opportunities=76, cross=3240), feedback_means_percent=feedback_frame.groupby("arm")[["own_share", "meme_post_rate", "cross_generated_share"]].mean().mul(100).to_dict("index"), ablation_metric_rows=100, ablation_full_origin="timestamp_v1_interest_s0–s9", display_R="R → 1", actual_no_r="decay=0 yields R=1", network_calls=0, simulation_calls=0))
    print("Prepared figures 2–6: raw total 49,930; main 30 runs; feedback 30 ENV; ablation 100 rows")


if __name__ == "__main__":
    main()
