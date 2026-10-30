"""离线比较本次两臂及历史完整时序参考，按既有方法计算现实轨迹DTW。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyze_pilot import audit_recirculation, exposures
from plot_agent_supply import COLORS, LABELS, TYPES, WEEKS

PILOT = Path(__file__).resolve().parent
OUT = PILOT / "agent_supply"
ROOT = PILOT.parents[2]
ARMS = ("random", "chronological", "interest")
NAMES = {"random": "随机", "chronological": "时序", "interest": "兴趣"}
ARM_COLORS = ("#737373", "#0F4D92", "#B64342")


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_runtime(value):
    """仅剔除已明确不同的请求保护字段及回流策略声明，保留全部科学配置。"""
    if isinstance(value, dict):
        return {k: strip_runtime(v) for k, v in value.items()
                if k not in ("content_retry_budget", "arrival_agent_return_policy")}
    if isinstance(value, list):
        return [strip_runtime(v) for v in value]
    return value


def extract(arm, directory, sources):
    def load(path):
        sources[str(path)] = digest(path)
        return read(path)
    pid, step = load(directory / "pid.json"), load(directory / "SOCIETY_STEP.json")
    assert pid["status"] == "completed" and step["completed_step_count"] == step["step_count"] == 693
    env = load(directory / "env/CurationDynamicsSpace/state/ENV_STATE.json")
    assert arm == "chronological" or env["_arrival_agent_return_policy"] == "next_batch"
    actions = env["_arrival_state"]["actions"]
    expected = {(str(i), week) for i in range(1, 101) for week in WEEKS}
    assert len(actions) == 1100 and {(str(a["agent_id"]), a["week"]) for a in actions} == expected
    assert [w["week"] for w in env["_arrival_state"]["weeks"]] == list(WEEKS)
    audit = audit_recirculation(env)
    counts, models, profiles, decisions = Counter(), Counter(), {}, {}
    paths = sorted((directory / "agents").glob("*/AGENT.json"))
    assert len(paths) == 100
    for path in paths:
        agent = load(path)
        aid, kind = str(agent["profile"]["id"]), agent["profile"]["agent_type"]
        assert aid not in profiles and kind in TYPES
        profiles[aid] = strip_runtime(agent["profile"])
        rows = agent["decision_log"]
        assert sorted(r["week"] for r in rows) == list(WEEKS)
        for row in rows:
            assert row.get("reason") not in ("action_failed", "publication_failed")
            decisions[(aid, row["week"])] = row
            if row.get("posted"):
                post = env["_posts"][str(row["post_id"])]
                assert post["content"] == row["content"] and post["type"] == kind
                assert str(post["author_id"]) == aid and post["source_week"] == row["week"]
                counts[(row["week"], kind)] += 1
                models[row.get("response_model") or "missing"] += 1
    assert set(decisions) == expected and sum(counts.values()) == audit["agent_posts"]
    rows = []
    for week in env["_arrival_state"]["weeks"]:
        name = week["week"]
        values = {kind: counts[(name, kind)] for kind in TYPES}
        total = sum(values.values())
        assert total == week["agent_supply"] and 0 < total <= 80
        assert all(values[k] == week[f"agent_supply_{k}"] for k in TYPES)
        exp = exposures([a for a in actions if a["week"] == name])
        assert exp["feed_total"] == week["total_exposures"] and exp["feed_meme_tag"] == week["exposure_meme"]
        rows.append({"algorithm": arm, "seed": 0, "week": name, **values, "total": total,
                     **{f"share_{k}": values[k] / total for k in TYPES}})
    # 官方只读replay接口复验11周全部五类供给，快照与Agent两侧不能单独代替它。
    fields = ["week", "agent_supply", *[f"agent_supply_{k}" for k in TYPES]]
    sql = "SELECT " + ", ".join(fields) + " FROM curation_dynamics_env_state ORDER BY week"
    payload = json.loads(subprocess.run(
        [sys.executable, str(ROOT / ".agentsociety/bin/ags.py"), "analysis", "query-data",
         "--data-path", str(directory / "replay"), "--sql", sql],
        cwd=ROOT, capture_output=True, text=True, check=True,
        env={**os.environ, "MEM0_TELEMETRY": "False", "ANONYMIZED_TELEMETRY": "False",
             "LITELLM_LOCAL_MODEL_COST_MAP": "True"}).stdout)
    assert payload["success"] and payload["columns"] == fields
    assert payload["rows"] == [[w[k] for k in fields] for w in env["_arrival_state"]["weeks"]]
    for path in [directory / "replay/_schema.json", *sorted((directory / "replay").glob("curation_dynamics_env_state.*.jsonl"))]:
        sources[str(path)] = digest(path)
    late = [r for r in rows if r["week"] in WEEKS[-4:]]
    late_total, late_meme = sum(r["total"] for r in late), sum(r["meme"] for r in late)
    metric = {"algorithm": arm, "seed": 0, "total_posts": sum(counts.values()),
              "late_total_posts": late_total, "late_meme_posts": late_meme,
              "late_meme_share": late_meme / late_total,
              "late_exposures": exposures([a for a in actions if a["week"] in WEEKS[-4:]]),
              "response_models": dict(models), "recirculation_audit": audit,
              "completion": {"agents": 100, "decisions": len(decisions), "actions": len(actions), "steps": 693},
              "official_replay_all_five_types_verified": True,
              "historical_reference": arm == "chronological"}
    return rows, metric, profiles, decisions


def calculate():
    contract = read(OUT / "three_arm_contract.json")
    sources = {}
    for entry in contract["frozen_sources"]:
        assert digest(OUT / entry["frozen"]) == entry["sha256"], entry["frozen"]
    for name, expected in contract["protected_sha256"].items():
        assert digest(Path(name)) == expected, name
    sources.update(contract["protected_sha256"])
    assert digest(OUT / "inputs/dtw_method.py") == contract["method_sha256"]
    spec = importlib.util.spec_from_file_location("pilot_frozen_dtw", OUT / "inputs/dtw_method.py")
    method = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(method)
    dtw = method.constrained_multivariate_dtw
    old_config, new_config = [read(OUT / f"inputs/{name}_chronological_config.json") for name in ("historical", "pilot")]
    assert strip_runtime(old_config) == strip_runtime(new_config)
    rows, metrics, profiles, decisions = [], [], {}, {}
    for arm in ARMS:
        directory = OUT / "inputs/chronological_s0" if arm == "chronological" else PILOT / f"results/hourly_return_pilot_{arm}_s0"
        weekly, metric, profiles[arm], decisions[arm] = extract(arm, directory, sources)
        expected_model = contract["historical_reference"]["expected_model"] if arm == "chronological" else contract["current_model"]
        assert set(metric["response_models"]) == {expected_model}
        rows.extend(weekly)
        metrics.append(metric)
    assert profiles["random"] == profiles["chronological"] == profiles["interest"]
    # 用户撤回的时序只作复用条件核验，绝不计入三臂完整结果或DTW。
    partial = PILOT / "results/hourly_return_pilot_chronological_s0"
    partial_env = read(partial / "env/CurationDynamicsSpace/state/ENV_STATE.json")
    completed_keys = {(str(a["agent_id"]), a["week"]) for a in partial_env["_arrival_state"]["actions"]}
    prefix_fields = ("posted", "speak", "reason", "components", "threshold", "u", "acted_at", "tick")
    matched = set()
    for path in sorted((partial / "agents").glob("*/AGENT.json")):
        sources[str(path)] = digest(path)
        agent = read(path)
        for row in agent["decision_log"]:
            key = (str(agent["profile"]["id"]), row["week"])
            if key in completed_keys:
                assert all(row.get(k) == decisions["chronological"][key].get(k) for k in prefix_fields)
                matched.add(key)
    assert len(matched) == len(completed_keys) == 107
    sources[str(partial / "env/CurationDynamicsSpace/state/ENV_STATE.json")] = digest(partial / "env/CurationDynamicsSpace/state/ENV_STATE.json")
    mapping = {"meme": "梗文化讨论", "mourning": "事件悼念讨论", "education": "教育观点讨论", "marketing": "借势营销", "other": "其他讨论"}
    with (OUT / "inputs/reality_week_boundary.csv").open(encoding="utf-8-sig", newline="") as handle:
        observed_rows = list(csv.DictReader(handle))
    observed = {(r["week"], r["category"]): r for r in observed_rows}
    audit = read(OUT / "inputs/reality_measurement_audit.json")
    assert len(observed) == len(observed_rows) == 55
    for week in WEEKS:
        total = sum(audit["real_shanghai"][week][mapping[k]] for k in TYPES)
        for kind in TYPES:
            row = observed[(week, mapping[kind])]
            assert int(row["shanghai_count"]) == audit["real_shanghai"][week][mapping[kind]]
            assert np.isclose(float(row["shanghai_clean_share"]), int(row["shanghai_count"]) / total, rtol=0, atol=1e-12)
    matrices = {field: np.array([[float(observed[(w, mapping[k])][field]) for k in TYPES] for w in WEEKS])
                for field in ("shanghai_clean_share", "utc_clean_share")}
    for matrix in matrices.values():
        assert np.allclose(matrix.sum(axis=1), 1, rtol=0, atol=1e-12)
    for metric in metrics:
        sim = np.array([[r[f"share_{k}"] for k in TYPES] for r in rows if r["algorithm"] == metric["algorithm"]])
        score, path = dtw(sim, matrices["shanghai_clean_share"], window=1)
        utc, _ = dtw(sim, matrices["utc_clean_share"], window=1)
        costs = [float(np.linalg.norm(sim[i] - matrices["shanghai_clean_share"][j])) for i, j in path]
        assert np.isclose(score, sum(costs) / len(path), rtol=0, atol=1e-12)
        metric.update(dtw_x100=score * 100, utc_sensitivity_dtw_x100=utc * 100,
                      dtw_path_length=len(path), dtw_path=[{"simulated_week": WEEKS[i], "observed_week": WEEKS[j], "local_cost": c} for (i,j),c in zip(path,costs)])
    for path in (Path(__file__), PILOT / "analyze_pilot.py", PILOT / "plot_agent_supply.py", OUT / "three_arm_contract.json"):
        sources[str(path)] = digest(path)
    return rows, {"scope": "current random/interest seed0 + historical complete chronological seed0 reference",
                  "method": contract["dtw"], "benchmark": contract["reality"], "metrics": metrics,
                  "ranking": [m["algorithm"] for m in sorted(metrics, key=lambda m: m["dtw_x100"])],
                  "reuse_validation": {"science_configs_equal_after_declared_runtime_exclusions": True,
                                       "actual_profiles_equal_after_retry_budget_exclusion": True,
                                       "withdrawn_chronological_valid_decisions_matching_history": 107,
                                       "withdrawn_chronological_in_scores": False},
                  "source_sha256": sources, "limitations": contract["limitations"]}


def draw(rows, results):
    plt.rcParams.update({"font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"],
                         "axes.unicode_minus": False, "figure.facecolor": "white", "axes.facecolor": "white",
                         "axes.edgecolor": "#444444", "axes.spines.top": False, "axes.spines.right": False,
                         "font.size": 12, "svg.fonttype": "none", "svg.hashsalt": "hourly-return-three-arm-dtw"})
    fig, axes = plt.subplots(1, 3, figsize=(21, 7), sharey=True)
    fig.subplots_adjust(left=0.055, right=0.99, top=0.77, bottom=0.23, wspace=0.08)
    handles = None
    for ax, metric in zip(axes, results["metrics"]):
        arm = metric["algorithm"]
        selected = [r for r in rows if r["algorithm"] == arm]
        handles = ax.stackplot(range(11), *[[r[k] for r in selected] for k in TYPES], colors=COLORS,
                               labels=LABELS, edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
        ax.axvline(1, color="#D62728", linestyle="--", linewidth=1.4, alpha=0.85, zorder=3)
        ax.annotate("去世 3-24 (W13)", xy=(1,1), xycoords=("data","axes fraction"), xytext=(5,-6),
                    textcoords="offset points", color="#D62728", va="top", fontsize=10,
                    bbox={"fc":"white","ec":"none","alpha":0.85,"pad":2})
        label = "历史完整参考" if arm == "chronological" else "本次小时回流"
        ax.set_title(f"{NAMES[arm]}推荐 · seed0 · {metric['total_posts']} 帖\n{label}", loc="left", fontsize=13, pad=10)
        ax.set_ylim(0,80)
        ax.set_yticks(range(0,81,10))
        ax.set_xticks(range(11), [w.replace("2026-", "") for w in WEEKS], rotation=45, ha="right")
        ax.set_xlabel("模拟周次（2026年）")
        ax.grid(color="#DDDDDD", linewidth=0.8)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Agent 成功发帖数（帖）")
    fig.suptitle("三臂 Agent 每周发帖量对比", fontsize=21, fontweight="bold", y=0.98)
    fig.legend(handles, LABELS, loc="upper center", bbox_to_anchor=(0.52,0.91), ncol=5, frameon=False)
    fig.text(0.5,0.065,"仅固定作者类型的成功发布；不含外部注入、官方帖和历史池。各臂单seed，时序为历史复用。",ha="center",fontsize=11,color="#555555")
    fig.text(0.5,0.02,"随机/兴趣实际模型：deepseek-v4-1-flash-261017；历史时序：deepseek-v4-1-flash。",ha="center",fontsize=11,color="#555555")
    save(fig, "three_arm_supply_comparison")
    fig, ax = plt.subplots(figsize=(11,5.6))
    fig.subplots_adjust(left=0.20,right=0.92,top=0.78,bottom=0.27)
    values = [m["dtw_x100"] for m in results["metrics"]]
    bars = ax.barh(range(3), values, color=ARM_COLORS, height=0.56)
    ax.set_yticks(range(3), ["随机 · 本次", "时序 · 历史复用", "兴趣 · 本次"])
    ax.invert_yaxis()
    ax.set_xlim(0,max(values)*1.18)
    for bar,value in zip(bars,values):
        ax.text(value+0.5,bar.get_y()+bar.get_height()/2,f"{value:.2f}",va="center",fontsize=14)
    ax.grid(axis="x",color="#DDDDDD")
    ax.set_axisbelow(True)
    ax.set_xlabel("DTW 距离 × 100（越低，越贴近现实五类构成）")
    fig.suptitle("三臂对现实周度构成的拟合",fontsize=19,fontweight="bold",y=0.98)
    fig.text(0.5,0.87,"W12–W22 · 上海周 · 五类份额 · 最多错开 ±1 周 · 按路径长度归一化",ha="center",fontsize=11)
    fig.text(0.5,0.08,"现实效标为全量数据五类非噪音周份额；非250条注入样本。\n单seed描述拟合，时序模型版本不同；不等于总体效能最优或独立预测验证。",ha="center",fontsize=10.5,color="#555555")
    save(fig, "three_arm_dtw_comparison")


def save(fig, stem):
    for ext in ("png","svg"):
        fig.savefig(OUT / f"{stem}.{ext}",dpi=300,
                    metadata={"Date": None} if ext == "svg" else {"Software": "AgentSociety offline pilot analysis"})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只复算并核对既有数值与来源，不覆盖产物")
    args = parser.parse_args()
    rows, results = calculate()
    path = OUT / "three_arm_results.json"
    if args.check:
        assert read(path) == results
        with (OUT / "three_arm_weekly.csv").open(encoding="utf-8-sig",newline="") as f:
            stored = list(csv.DictReader(f))
        assert stored == [{k:str(v) for k,v in r.items()} for r in rows]
        bundle = read(OUT / "three_arm_outputs.json")
        for name, expected in bundle.items():
            assert digest(OUT / name) == expected
        print("PASS: 33 weekly rows, 3 DTW values/paths, raw sources, replay and output hashes reproducible")
    else:
        path.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
        with (OUT / "three_arm_weekly.csv").open("w",encoding="utf-8-sig",newline="") as f:
            writer = csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        draw(rows,results)
        names = ["three_arm_results.json","three_arm_weekly.csv",*[f"{stem}.{ext}" for stem in ("three_arm_supply_comparison","three_arm_dtw_comparison") for ext in ("png","svg")]]
        (OUT / "three_arm_outputs.json").write_text(json.dumps({n:digest(OUT/n) for n in names},indent=2)+"\n")
        print(json.dumps({"ranking":results["ranking"],"dtw_x100":{m['algorithm']:m['dtw_x100'] for m in results['metrics']}},ensure_ascii=False))


if __name__ == "__main__":
    main()
