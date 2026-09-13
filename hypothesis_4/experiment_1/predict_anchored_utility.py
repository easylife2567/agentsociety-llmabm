#!/usr/bin/env python3
"""锚定式效用的受约束数值代理、调参与预测图。

只运行与现有 feed/决策规则同构的数值代理，不调用 LLM、不启动正式仿真：

    U_it = B_i + R_it * (D_it - B_i)

参数只用 W13-W18 拟合；W19-W22 留出验证。B_i 由真实 W05-W12
周均供给映射到现有 activity 门槛分布后固定，只搜索一个全局 D 强度与五类 λ。
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import statistics
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/agentsociety-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/agentsociety-cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import qmc

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import calibrate_speak as cal

WEEKS = cal.WEEKS
TYPES = cal.TYPE_ORDER
FIT_WEEKS = [f"2026-W{i}" for i in range(13, 19)]
VALID_WEEKS = [f"2026-W{i}" for i in range(19, 23)]
PRE_WEEKS = [f"2026-W{i:02d}" for i in range(5, 13)]
LABEL = {"meme": "玩梗", "mourning": "悼念", "marketing": "营销",
         "education": "教育", "other": "其他"}
COLOR = {"meme": "#D55E00", "mourning": "#0072B2", "marketing": "#E69F00",
         "education": "#009E73", "other": "#56B4E9"}
CURRENT_COLOR = "#9A9A9A"
REAL_COLOR = "#222222"

OUT_DATA = SCRIPT_DIR / "data"
OUT_CHART = SCRIPT_DIR / "charts" / "prediction"
JSON_PATH = OUT_DATA / "anchored_utility_prediction.json"
CSV_PATH = OUT_DATA / "anchored_utility_prediction.csv"
PNG_PATH = OUT_CHART / "PROXY_anchored_utility_prediction.png"
SVG_PATH = OUT_CHART / "PROXY_anchored_utility_prediction.svg"

ORIGINAL_POPULATION = copy.deepcopy(cal.population)
CURRENT_LAMBDA = {
    t: statistics.mean(a["params"]["decay"] for a in ORIGINAL_POPULATION
                       if a["agent_type"] == t)
    for t in TYPES
}


def real_targets():
    matrix = json.loads(cal.BENCH_PATH.read_text(encoding="utf-8"))["weekly_category_matrix"]
    cn_of = {v: k for k, v in cal.TYPE_KEYS.items()}
    scale = cal.POPULATION_COUNTS["mourning"] / float(matrix["2026-W13"]["事件悼念讨论"])
    all_targets = {
        w: {t: float(matrix[w].get(cn_of[t], 0)) * scale for t in TYPES}
        for w in WEEKS
    }
    baseline_counts = {
        t: statistics.mean(float(matrix[w].get(cn_of[t], 0)) * scale for w in PRE_WEEKS)
        for t in TYPES
    }
    return matrix, scale, all_targets, baseline_counts


REAL_MATRIX, REAL_SCALE, TARGET, BASELINE_COUNTS = real_targets()


def baseline_prior_from_activity() -> dict[str, float]:
    """把事件前周均 agent 当量映射到现有 activity 分布的效用分位点。"""
    out = {}
    for t in TYPES:
        acts = sorted(a["params"]["activity"] for a in ORIGINAL_POPULATION
                      if a["agent_type"] == t)
        wanted = max(0.0, min(float(len(acts)), BASELINE_COUNTS[t]))
        if wanted < 0.5:
            out[t] = acts[0] - 0.02
        else:
            k = max(1, min(len(acts) - 1, int(round(wanted))))
            out[t] = (acts[k - 1] + acts[k]) / 2.0
    return out


BASELINE_PRIOR = baseline_prior_from_activity()


def set_lambda_means(means: dict[str, float]) -> None:
    """保留个体相对异质性，只改变每类 λ 的均值。"""
    for agent, original in zip(cal.population, ORIGINAL_POPULATION):
        t = agent["agent_type"]
        ratio = means[t] / CURRENT_LAMBDA[t]
        agent["params"]["decay"] = original["params"]["decay"] * ratio


def simulate_mean(alpha_d: float, baseline: dict[str, float], lambdas: dict[str, float],
                  seeds: list[int], anchored: bool = True):
    set_lambda_means(lambdas)
    runs = []
    for seed in seeds:
        res, _, _ = cal.simulate(
            cal.BASE_REF, "normal", rng_seed=seed, spiral_mult=alpha_d,
            utility_mode="anchored" if anchored else "multiplicative",
            baseline_utility=baseline if anchored else None,
        )
        runs.append(res)
    mean = {w: {t: statistics.mean(r[w][t] for r in runs) for t in TYPES} for w in WEEKS}
    sd = {w: {t: statistics.pstdev(r[w][t] for r in runs) for t in TYPES} for w in WEEKS}
    return mean, sd, runs


def data_rmse(pred: dict, weeks: list[str]) -> float:
    errs = [((pred[w][t] - TARGET[w][t]) / cal.POPULATION_COUNTS[t]) ** 2
            for w in weeks for t in TYPES]
    return math.sqrt(statistics.mean(errs))


def total_shape_rmse(pred: dict, weeks: list[str]) -> float:
    real_w13 = sum(TARGET["2026-W13"].values())
    pred_w13 = sum(pred["2026-W13"].values())
    errs = []
    for w in weeks:
        real_ratio = sum(TARGET[w].values()) / real_w13
        pred_ratio = sum(pred[w].values()) / pred_w13 if pred_w13 else 0.0
        errs.append((pred_ratio - real_ratio) ** 2)
    return math.sqrt(statistics.mean(errs))


def decode(unit: np.ndarray):
    # alpha_D + 5 个 log(lambda)；B 使用事件前实证锚点，不参与拟合。
    alpha = 0.08 + unit[0] * 0.92
    baseline = dict(BASELINE_PRIOR)
    lambdas = {}
    lo_hi = {
        "meme": (0.05, 2.5), "mourning": (0.15, 5.0), "marketing": (0.015, 5.0),
        "education": (0.05, 5.0), "other": (0.10, 6.0),
    }
    for j, t in enumerate(TYPES):
        lo, hi = lo_hi[t]
        lambdas[t] = math.exp(math.log(lo) + unit[1 + j] * (math.log(hi) - math.log(lo)))
    return alpha, baseline, lambdas


def objective(unit: np.ndarray, seeds: list[int]):
    alpha, baseline, lambdas = decode(unit)
    pred, _, _ = simulate_mean(alpha, baseline, lambdas, seeds)
    fit = data_rmse(pred, FIT_WEEKS)
    l_pen = statistics.mean(math.log(lambdas[t] / CURRENT_LAMBDA[t]) ** 2 for t in TYPES)
    # 小幅正则化只用于打破等拟合解；数据误差仍占主导。
    return fit + 0.004 * l_pen, fit


def tune(search_power: int, local_n: int):
    sampler = qmc.Sobol(d=6, scramble=True, seed=20260913)
    points = sampler.random_base2(search_power)
    coarse = []
    for i, unit in enumerate(points, 1):
        score, fit = objective(unit, [3000])
        coarse.append((score, fit, unit.copy()))
        if i % 256 == 0:
            print(f"coarse {i}/{len(points)} best={min(x[0] for x in coarse):.5f}", flush=True)
    coarse.sort(key=lambda x: x[0])

    # 多 seed 复核粗搜前 32 名，过滤单一抽样流的偶然最优。
    reviewed = []
    for _, _, unit in coarse[:32]:
        score, fit = objective(unit, list(range(3000, 3008)))
        reviewed.append((score, fit, unit.copy()))
    reviewed.sort(key=lambda x: x[0])

    # 围绕前 4 名做截断高斯局部搜索。
    rng = np.random.default_rng(20260914)
    local = list(reviewed)
    centers = [x[2] for x in reviewed[:4]]
    for i in range(local_n):
        center = centers[i % len(centers)]
        scale = 0.10 if i < local_n * 0.55 else 0.045
        unit = np.clip(center + rng.normal(0.0, scale, size=6), 0.0, 1.0)
        score, fit = objective(unit, [3000, 3001])
        local.append((score, fit, unit.copy()))
        if (i + 1) % 256 == 0:
            print(f"local {i+1}/{local_n} best={min(x[0] for x in local):.5f}", flush=True)
    local.sort(key=lambda x: x[0])

    # 最终候选统一用 20 seed，仅按拟合期目标选模。
    finalists = []
    for _, _, unit in local[:24]:
        score, fit = objective(unit, list(range(3000, 3020)))
        finalists.append((score, fit, unit.copy()))
    finalists.sort(key=lambda x: x[0])
    return finalists[0], {
        "coarse_candidates": len(points), "coarse_seed_count": 1,
        "reviewed_candidates": 32, "review_seed_count": 8,
        "local_candidates": local_n, "local_seed_count": 2,
        "finalists": 24, "finalist_seed_count": 20,
    }


def write_outputs(params, search_meta, final_seed_count: int):
    score, fit_score, unit = params
    alpha, baseline, lambdas = decode(unit)
    seeds = list(range(3000, 3000 + final_seed_count))
    pred, sd, runs = simulate_mean(alpha, baseline, lambdas, seeds)
    current, current_sd, _ = simulate_mean(1.0, BASELINE_PRIOR, CURRENT_LAMBDA, seeds, anchored=False)

    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_CHART.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["week", "period"]
        for prefix in ("real", "current", "anchored"):
            fields += [f"{prefix}_{t}" for t in TYPES] + [f"{prefix}_total"]
        fields += [f"anchored_{t}_sd" for t in TYPES] + ["anchored_total_sd"]
        wtr = csv.DictWriter(f, fieldnames=fields)
        wtr.writeheader()
        for w in WEEKS:
            row = {"week": w, "period": "fit" if w in FIT_WEEKS else ("validation" if w in VALID_WEEKS else "baseline")}
            for t in TYPES:
                row[f"real_{t}"] = TARGET[w][t]
                row[f"current_{t}"] = current[w][t]
                row[f"anchored_{t}"] = pred[w][t]
                row[f"anchored_{t}_sd"] = sd[w][t]
            row["real_total"] = sum(TARGET[w].values())
            row["current_total"] = sum(current[w].values())
            row["anchored_total"] = sum(pred[w].values())
            row["anchored_total_sd"] = statistics.pstdev(sum(r[w].values()) for r in runs)
            wtr.writerow(row)

    doc = {
        "artifact_status": "numerical_proxy_prediction_not_simulation",
        "formula": "U_i=B_i+R_i*(D_i-B_i)",
        "selection_rule": "B fixed from W05-W12; alpha_D and lambdas selected only on W13-W18; W19-W22 held out",
        "real_to_agent_scale": {
            "rule": "W13 real mourning posts map to all 22 mourning agents speaking once",
            "multiplier": REAL_SCALE,
        },
        "baseline_prior": {
            "weeks": PRE_WEEKS,
            "real_scaled_weekly_mean": BASELINE_COUNTS,
            "utility_prior_from_activity_quantile": BASELINE_PRIOR,
        },
        "parameters": {"alpha_D": alpha, "baseline_utility": baseline,
                       "lambda_mean": lambdas, "lambda_current_mean": CURRENT_LAMBDA,
                       "decay_scale": cal.mech.DEFAULT_DECAY_SCALE},
        "search": search_meta | {"final_prediction_seed_count": final_seed_count,
                                  "regularized_training_score": score,
                                  "unregularized_training_rate_rmse": fit_score},
        "metrics": {
            "type_rate_rmse_fit_W13_W18": data_rmse(pred, FIT_WEEKS),
            "type_rate_rmse_validation_W19_W22": data_rmse(pred, VALID_WEEKS),
            "total_shape_rmse_fit_W13_W18": total_shape_rmse(pred, FIT_WEEKS),
            "total_shape_rmse_validation_W19_W22": total_shape_rmse(pred, VALID_WEEKS),
            "current_type_rate_rmse_fit": data_rmse(current, FIT_WEEKS),
            "current_type_rate_rmse_validation": data_rmse(current, VALID_WEEKS),
        },
        "weekly": {w: {"real_scaled": TARGET[w], "current_mean": current[w],
                        "anchored_mean": pred[w], "anchored_sd": sd[w]}
                   for w in WEEKS},
        "limitations": [
            "Real benchmark rows are post counts, not active-author counts; scaling is an explicit proxy assumption.",
            "Numerical proxy reuses the existing feed mechanism and sampled injection pool s0; it is not a formal simulation run.",
            "Parameter selection uses W13-W18 only; W19-W22 metrics are genuine held-out diagnostics.",
        ],
    }
    JSON_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    plot(pred, sd, current, runs, alpha, baseline, lambdas)
    return doc


def plot(pred, sd, current, runs, alpha, baseline, lambdas):
    plt.rcParams.update({
        "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"],
        "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.22, "grid.linewidth": 0.7,
        "figure.facecolor": "white", "axes.facecolor": "white", "font.size": 10,
    })
    x = np.arange(len(WEEKS))
    fig = plt.figure(figsize=(14, 9.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=0.34, wspace=0.22)
    axes = [fig.add_subplot(gs[0, :])]
    axes += [fig.add_subplot(gs[1, i]) for i in range(3)]
    # 用第二行三个格子的嵌套布局承载五类小图：总图占第一行，第二行五等分。
    for ax in axes[1:]:
        ax.remove()
    sub = gs[1, :].subgridspec(1, 5, wspace=0.27)
    type_axes = [fig.add_subplot(sub[0, i]) for i in range(5)]
    ax = axes[0]

    real_total = np.array([sum(TARGET[w].values()) for w in WEEKS])
    current_total = np.array([sum(current[w].values()) for w in WEEKS])
    pred_total = np.array([sum(pred[w].values()) for w in WEEKS])
    total_sd = np.array([statistics.pstdev(sum(r[w].values()) for r in runs) for w in WEEKS])
    ax.axvspan(6.5, 10.5, color="#E8E8E8", alpha=0.55, zorder=0, label="留出检验 W19–W22")
    ax.plot(x, real_total, color=REAL_COLOR, marker="s", lw=2.4, label="真实数据（Agent当量）")
    ax.plot(x, current_total, color=CURRENT_COLOR, ls="--", lw=1.8, label="当前 U=D·R")
    ax.plot(x, pred_total, color="#7B2CBF", marker="o", lw=2.5, label="锚定式预测均值")
    ax.fill_between(x, np.maximum(0, pred_total-total_sd), pred_total+total_sd,
                    color="#7B2CBF", alpha=0.14, linewidth=0, label="±1 SD")
    ax.axvline(1, color="#CC3311", ls=":", lw=1.4)
    ax.axvline(7, color="#EE7733", ls=":", lw=1.4)
    ax.set_xticks(x, [w[-3:] for w in WEEKS])
    ax.set_ylabel("周发帖 Agent 当量")
    ax.set_title("锚定式效用预测：总量曲线（参数仅用 W13–W18 拟合）", fontweight="bold", fontsize=13)
    ax.legend(ncol=4, frameon=False, loc="upper right", fontsize=9)

    for idx, (t, tax) in enumerate(zip(TYPES, type_axes)):
        y_real = np.array([TARGET[w][t] for w in WEEKS])
        y_cur = np.array([current[w][t] for w in WEEKS])
        y_pred = np.array([pred[w][t] for w in WEEKS])
        y_sd = np.array([sd[w][t] for w in WEEKS])
        tax.axvspan(6.5, 10.5, color="#E8E8E8", alpha=0.55, zorder=0)
        tax.plot(x, y_real, color=REAL_COLOR, marker="s", ms=3.3, lw=1.7)
        tax.plot(x, y_cur, color=CURRENT_COLOR, ls="--", lw=1.25)
        tax.plot(x, y_pred, color=COLOR[t], marker="o", ms=3.4, lw=1.9)
        tax.fill_between(x, np.maximum(0, y_pred-y_sd), y_pred+y_sd,
                         color=COLOR[t], alpha=0.14, linewidth=0)
        tax.axvline(1, color="#CC3311", ls=":", lw=1.0)
        tax.axvline(7, color="#EE7733", ls=":", lw=1.0)
        tax.set_title(f"{LABEL[t]}\nλ={lambdas[t]:.3f}, B={baseline[t]:.3f}",
                      color=COLOR[t], fontweight="bold", fontsize=10)
        tax.set_xticks([0, 3, 6, 7, 10], ["W12", "W15", "W18", "W19", "W22"], rotation=45)
        if idx == 0:
            tax.set_ylabel("周发帖 Agent 当量")
        tax.set_ylim(bottom=0)

    fig.suptitle(
        f"U = B + R(D - B) 数值代理预测｜α_D={alpha:.3f}｜100 seed 均值与波动\n"
        "黑线=真实缩放值，灰虚线=当前机制，彩线=锚定式；灰底=W19–W22留出期",
        y=0.985, fontsize=14, fontweight="bold",
    )
    fig.text(0.5, 0.012,
             "注：真实帖子量按 W13 悼念 4714 帖→22名悼念Agent 等比例换算；这是数值代理，不是正式仿真结果。",
             ha="center", fontsize=9, color="#555555")
    fig.subplots_adjust(top=0.90, bottom=0.09, left=0.07, right=0.985)
    fig.savefig(PNG_PATH, dpi=300)
    fig.savefig(SVG_PATH)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="锚定式效用的数值代理调参与预测")
    ap.add_argument("--search-power", type=int, default=10,
                    help="Sobol 粗搜候选数=2^N（默认 1024）")
    ap.add_argument("--local", type=int, default=768, help="局部搜索候选数")
    ap.add_argument("--final-seeds", type=int, default=100, help="最终预测 seed 数")
    args = ap.parse_args()

    print("baseline counts", BASELINE_COUNTS, flush=True)
    print("baseline utility prior", BASELINE_PRIOR, flush=True)
    best, meta = tune(args.search_power, args.local)
    doc = write_outputs(best, meta, args.final_seeds)
    print(json.dumps({"parameters": doc["parameters"], "metrics": doc["metrics"]},
                     ensure_ascii=False, indent=2))
    print(PNG_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
