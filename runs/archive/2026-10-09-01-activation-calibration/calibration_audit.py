"""只读冻结输入，独立复算B的尺度、整数映射与极限人数；不导入或运行项目代码。"""
from pathlib import Path
import hashlib
import json
from statistics import mean

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
LABELS = {"meme": "梗文化讨论", "mourning": "事件悼念讨论", "marketing": "借势营销",
          "education": "教育观点讨论", "other": "其他讨论"}
paths = [ROOT / "hypothesis_4/benchmark_curves.json",
         ROOT / "hypothesis_4/experiment_1/data/anchored_utility_prediction.json"]
paths += [ROOT / f"hypothesis_4/experiment_2/init/inputs/population_s{s}.json" for s in range(3)]
matrix = json.loads(paths[0].read_text())["weekly_category_matrix"]
prediction = json.loads(paths[1].read_text())
populations = [json.loads(p.read_text()) for p in paths[2:]]
# 三seed的实际数值人口相同；不把重复同一人口误当成独立门槛重抽。
params = [[(a["kwargs"]["agent_type"], a["kwargs"]["params"]) for a in pop] for pop in populations]
assert params[0] == params[1] == params[2]
scale = 22 / matrix["2026-W13"][LABELS["mourning"]]
assert abs(scale - prediction["real_to_agent_scale"]["multiplier"]) < 1e-14
rows = []
for typ, label in LABELS.items():
    agents = [a["kwargs"]["params"] for a in populations[0] if a["kwargs"]["agent_type"] == typ]
    acts = sorted(a["activity"] for a in agents)
    b_values = {a["baseline_utility"] for a in agents}
    assert len(b_values) == 1
    b = b_values.pop()
    pre_counts = [matrix[f"2026-W{w:02}"][label] for w in range(5, 13)]
    wanted = mean(pre_counts) * scale
    mapped = acts[0] - 0.02 if wanted < 0.5 else (
        acts[max(1, min(len(acts)-1, round(wanted)))-1]
        + acts[max(1, min(len(acts)-1, round(wanted)))]) / 2
    assert abs(b - mapped) < 1e-12
    assert abs(wanted - prediction["baseline_prior"]["real_scaled_weekly_mean"][typ]) < 1e-12
    # 只改变尺度的算术压力测试：非替代估计，非新仿真。
    variants = []
    for multiplier in (0.5, 1.0, 2.0):
        m = max(0, min(len(acts), wanted * multiplier))
        k = max(1, min(len(acts)-1, round(m)))
        candidate = acts[0] - 0.02 if m < 0.5 else (acts[k-1] + acts[k]) / 2
        variants.append({"scale_multiplier": multiplier, "expected_count": m,
                         "B": candidate, "R0_speakers": sum(candidate >= a for a in acts)})
    rows.append({"type": typ, "agents": len(agents), "pre_posts_sum": sum(pre_counts),
                 "pre_posts_weekly_mean": mean(pre_counts), "W12_posts": pre_counts[-1],
                 "expected_count": wanted, "B": b, "min_activity": acts[0],
                 "R0_speakers": sum(b >= a for a in acts),
                 "hypothetical_scale_stress": variants})

assert [r["R0_speakers"] for r in rows] == [0, 0, 3, 0, 0]
sources = paths + [ROOT / "hypothesis_4/experiment_1/predict_anchored_utility.py",
                  ROOT / "custom/agents/curation_discourse_agent.py",
                  ROOT / "custom/envs/curation_mechanisms.py"]
evidence = {"status": "independent_arithmetic_audit_only", "llm_calls": 0,
            "project_code_imports": 0, "simulation_runs": 0,
            "scale": scale, "W13_mourning_posts": matrix["2026-W13"][LABELS["mourning"]],
            "three_seed_numeric_populations_identical": True,
            "rows": rows,
            "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sources}}
(RUN / "calibration_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"scale": scale, "rows": [{k: r[k] for k in
      ("type", "expected_count", "B", "min_activity", "R0_speakers")} for r in rows]}, ensure_ascii=False))
