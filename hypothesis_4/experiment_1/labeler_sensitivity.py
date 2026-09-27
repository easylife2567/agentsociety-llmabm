#!/usr/bin/env python3
"""标注器敏感性分析（W5 整改第一步）。

问题
----
真实基准的六类标签来自一轮 LLM 打标（DeepSeek），而非人工编码。一致性对比
（`data/archive/reports/四模型标签一致性对比报告_20260926.md`）显示原标与三个独立重打标轮的类别
一致率仅 53.9%–60.7%、Cohen's κ = 0.43–0.51，且分歧集中在「借势营销 ↔
教育观点讨论」边界。因此必须回答：论文的核心经验结论（悼念峰值、玩梗延迟
爆发、以及三臂拟合排序）是否依赖某一特定标注器？

四个标注器中有三个（doubao-seed、GLM、DeepSeek-V4.1）为独立重打标轮，
且 DeepSeek-V4.1 与原标同属 DeepSeek 家族，可用于排除「原标偏离是模型族
特性」这一替代解释。

本脚本做两件事，都不需要重跑仿真：

A. 用三个独立标注轮分别重建 W05–W22 周级类别矩阵，与 DeepSeek 基准对齐校验，
   并比较玩梗/悼念轨迹的相位（峰值周、起爆周、W22 水平）。
B. 固定各臂 Agent-only 供给轨迹不变，只替换效标标注器，重算每个 run 的受限
   多变量 DTW，检查「interest 拟合最优」这一结论是否随标注器翻转。

用法
----
    python labeler_sensitivity.py            # A + B
    python labeler_sensitivity.py --part a   # 仅 A（快）
    python labeler_sensitivity.py --part b   # 仅 B（需读取 run 目录）
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import openpyxl

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

OUT_DIR = SCRIPT_DIR / "results" / "labeler_sensitivity"
CACHE = OUT_DIR / "weekly_matrices.json"
REPORT = OUT_DIR / "REPORT.md"

SOURCE_XLSX = ROOT / "data" / "baseline" / "抖音微博小红书-全量已打标.xlsx"

LABELERS = {
    "DeepSeek": SOURCE_XLSX,
    # 2026-09-27 新增：doubao 用**第 1 轮口径**重跑的那一轮。它与 DeepSeek 原标口径相同、
    # 仅模型不同，故「DeepSeek vs doubao-R1口径」是干净的模型效应；
    # 而其余三个归档轮都是后三轮口径，「DeepSeek vs 它们」的差异里混着口径效应（口径是主因，
    # 见 data/README.md 的效应分解）。两者必须分开读。
    "doubao-R1口径": ROOT / "data" / "runs" / "抖音微博小红书-独立重打标_R1prompt_Seed2_1_lite.xlsx",
    "doubao-seed": ROOT / "data" / "archive" / "round2_doubao-seed-2.1-lite" / "抖音微博小红书-独立重打标_Seed2_1_lite.xlsx",
    "GLM": ROOT / "data" / "archive" / "round3_glm-5.3-flash" / "抖音微博小红书-独立重打标_GLM5_3flash.xlsx",
    "DeepSeek-V4.1": ROOT / "data" / "archive" / "round4_deepseek-v4.1" / "抖音微博小红书-独立重打标_DSv4_1_flash.xlsx",
}

CAT2TYPE = {
    "借势营销": "marketing",
    "事件悼念讨论": "mourning",
    "教育观点讨论": "education",
    "梗文化讨论": "meme",
    "其他讨论": "other",
    "爬取噪音": "noise",
}
TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
TYPE_CN = {
    "meme": "玩梗",
    "mourning": "悼念",
    "education": "教育",
    "marketing": "营销",
    "other": "其他",
    "noise": "噪音",
}

# 与 plot_dtw_validation.py 保持一致：五个有效类型，排除噪音后重新归一
VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]

WINDOW_START = "2026-W05"
WINDOW_END = "2026-W22"
EVENT_WEEK = "2026-W13"


# --------------------------------------------------------------------------
# A. 周级矩阵重建
# --------------------------------------------------------------------------


def week_key(value) -> str | None:
    """把 published_at 转成 ISO 周标签 '2026-Www'。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        text = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def read_weeks_from_source() -> list[str | None]:
    """从源表读取逐行 ISO 周标签（行序与三份标注表一致，已由一致性脚本校验）。"""
    wb = openpyxl.load_workbook(SOURCE_XLSX, read_only=True)
    ws = wb.active
    weeks: list[str | None] = []
    for row in ws.iter_rows(min_row=2, min_col=13, max_col=13, values_only=True):
        weeks.append(week_key(row[0]))
    wb.close()
    return weeks


def read_categories(path: Path) -> list[str]:
    """读取某标注轮的『内容类别』列（第 2 列）。"""
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    cats: list[str] = []
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=2, values_only=True):
        cats.append(str(row[0]).strip() if row[0] is not None else "")
    wb.close()
    return cats


def build_weekly_matrices(weeks: list[str | None]) -> dict[str, dict[str, dict[str, int]]]:
    result: dict[str, dict[str, dict[str, int]]] = {}
    for labeler, path in LABELERS.items():
        cats = read_categories(path)
        if len(cats) != len(weeks):
            raise SystemExit(f"{labeler}: 行数 {len(cats)} 与源表 {len(weeks)} 不一致")
        weekly: dict[str, Counter] = defaultdict(Counter)
        dropped = Counter()
        for wk, cat in zip(weeks, cats):
            if wk is None or wk < WINDOW_START or wk > WINDOW_END:
                continue
            t = CAT2TYPE.get(cat)
            if t is None:
                dropped[cat or "<空>"] += 1
                continue
            weekly[wk][t] += 1
        matrix = {
            wk: {**{t: weekly[wk].get(t, 0) for t in TYPE_ORDER},
                 "total": sum(weekly[wk].values())}
            for wk in sorted(weekly)
        }
        result[labeler] = matrix
        print(f"[A] {labeler}: {len(matrix)} 周，剔除 {sum(dropped.values())} 行 "
              f"（{dict(dropped)}）", flush=True)
    return result


def validate_against_frozen(matrices: dict) -> list[str]:
    """与冻结效标 benchmark_curves.json 的 DeepSeek 矩阵逐格比对。"""
    frozen_path = ROOT / "hypothesis_4" / "benchmark_curves.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))["weekly_category_matrix"]
    cn_by_type = {v: k for k, v in CAT2TYPE.items()}
    lines, mismatches = [], 0
    for wk, cells in frozen.items():
        if wk < WINDOW_START or wk > WINDOW_END:
            continue
        got = matrices["DeepSeek"].get(wk)
        if got is None:
            lines.append(f"- {wk}: 缺失")
            mismatches += 1
            continue
        for t, cn in cn_by_type.items():
            want = cells.get(cn)
            have = got.get(t)
            if want is not None and want != have:
                lines.append(f"- {wk} {cn}: 冻结 {want} vs 重算 {have}")
                mismatches += 1
    return lines, mismatches


def phase_summary(matrix: dict[str, dict[str, int]]) -> dict:
    """核心相位：悼念峰值周、玩梗起爆周、W22 玩梗份额。"""
    weeks = sorted(matrix)
    clean = {
        wk: {t: matrix[wk][t] for t in VALID_TYPES} for wk in weeks
    }
    totals = {wk: sum(clean[wk].values()) for wk in weeks}
    share = {
        wk: {t: (clean[wk][t] / totals[wk] if totals[wk] else 0.0) for t in VALID_TYPES}
        for wk in weeks
    }
    mourning_peak = max(weeks, key=lambda w: share[w]["mourning"])
    pre = [share[w]["meme"] for w in weeks if w < EVENT_WEEK]
    baseline = statistics.fmean(pre) if pre else 0.0
    onset = next(
        (w for w in weeks if w >= EVENT_WEEK and share[w]["meme"] > baseline + 0.10),
        None,
    )
    peak_meme = max(weeks, key=lambda w: share[w]["meme"])
    return {
        "share": share,
        "mourning_peak_week": mourning_peak,
        "mourning_peak_share": share[mourning_peak]["mourning"],
        "pre_event_meme_baseline": baseline,
        "meme_onset_week": onset,
        "meme_peak_week": peak_meme,
        "meme_peak_share": share[peak_meme]["meme"],
        "meme_w22": share[weeks[-1]]["meme"],
        "weeks": weeks,
    }


# --------------------------------------------------------------------------
# B. 三臂拟合排序对标注器的稳健性
# --------------------------------------------------------------------------


def run_arm_robustness(matrices: dict) -> dict:
    import numpy as np

    import plot_arm_charts as armplot  # noqa: E402
    from plot_dtw_validation import constrained_multivariate_dtw, run_matrix, WINDOW

    runs = armplot.load_runs([], strict=True)
    by_arm = armplot.group_by_arm(runs)
    weeks = [w["week"] for w in runs[0]["weekly"]]

    clean = {}
    for labeler, matrix in matrices.items():
        clean[labeler] = np.asarray(
            [
                [
                    (matrix[wk][t] / sum(matrix[wk][k] for k in VALID_TYPES))
                    if sum(matrix[wk][k] for k in VALID_TYPES) else 0.0
                    for t in VALID_TYPES
                ]
                for wk in weeks
            ],
            dtype=float,
        )

    table: dict[str, dict[str, dict]] = {}
    for labeler in LABELERS:
        observed = clean[labeler]
        per_arm: dict[str, dict] = {}
        for arm in armplot.ARMS:
            seed_scores, seed_maes = [], []
            for run in sorted(by_arm[arm], key=lambda item: item["seed"]):
                mat = run_matrix(run)
                score, _ = constrained_multivariate_dtw(mat, observed, window=WINDOW)
                seed_scores.append(score * 100)
                seed_maes.append(float(np.abs(mat - observed).mean()))
            per_arm[arm] = {
                "dtw_pp": seed_scores,
                "dtw_mean": statistics.fmean(seed_scores),
                "dtw_sd": statistics.stdev(seed_scores) if len(seed_scores) > 1 else 0.0,
                "dtw_min": min(seed_scores),
                "dtw_max": max(seed_scores),
                "mae_mean": statistics.fmean(seed_maes),
            }
        ranking = sorted(per_arm, key=lambda a: per_arm[a]["dtw_mean"])
        table[labeler] = {"per_arm": per_arm, "ranking": ranking}
        print(f"[B] {labeler}: 排序 {ranking} | "
              + " ".join(f"{a}={per_arm[a]['dtw_mean']:.2f}" for a in armplot.ARMS),
              flush=True)
    return {"weeks": weeks, "labelers": table}


def paired_test(matrices: dict) -> dict:
    """interest vs random 的配对检验（同 seed 配对），每个标注器一次。"""
    from scipy import stats
    import numpy as np

    import plot_arm_charts as armplot
    from plot_dtw_validation import constrained_multivariate_dtw, run_matrix, WINDOW

    runs = armplot.load_runs([], strict=True)
    by_arm = armplot.group_by_arm(runs)
    weeks = [w["week"] for w in runs[0]["weekly"]]
    out = {}
    for labeler, matrix in matrices.items():
        denom = [sum(matrix[wk][k] for k in VALID_TYPES) for wk in weeks]
        observed = np.asarray(
            [
                [matrix[wk][t] / denom[i] if denom[i] else 0.0 for t in VALID_TYPES]
                for i, wk in enumerate(weeks)
            ],
            dtype=float,
        )
        scores = {}
        for arm in armplot.ARMS:
            scores[arm] = [
                constrained_multivariate_dtw(run_matrix(r), observed, window=WINDOW)[0] * 100
                for r in sorted(by_arm[arm], key=lambda item: item["seed"])
            ]
        diff = np.asarray(scores["interest"]) - np.asarray(scores["random"])
        t, p = stats.ttest_rel(scores["interest"], scores["random"])
        out[labeler] = {
            "interest": scores["interest"],
            "random": scores["random"],
            "mean_diff": float(diff.mean()),
            "t": float(t),
            "p": float(p),
        }
    return out


# --------------------------------------------------------------------------
# 报告
# --------------------------------------------------------------------------


def write_report(matrices, validation, phases, robustness, paired) -> None:
    lines = ["# 标注器敏感性分析（W5 整改第一步）", ""]
    lines += [
        "真实基准的类别标签来自一轮 LLM 打标（DeepSeek，即原标）。各独立重打标轮与原标的类别一致率",
        "仅 53.9%–60.7%、Cohen's κ = 0.43–0.51。本报告检验论文的核心经验结论是否依赖某一特定标注器。",
        "",
        "> **读表须知（2026-09-27 补）**：五个标注器中只有 `doubao-R1口径` 与原标**口径相同、仅模型不同**，",
        "> 故 `DeepSeek` vs `doubao-R1口径` 是干净的模型效应；`doubao-seed` / `GLM` / `DeepSeek-V4.1` 三个",
        "> 归档轮都是**后三轮口径**，它们与原标的差异里混着口径效应。而口径已被证明是差异主因",
        "> （同模型换口径 κ=0.4238，换模型 κ=0.7159，见 `data/README.md`），故后三列不能读作",
        "> 「标注器质量」。",
        "",
        "## 0. 与冻结效标的对齐校验",
        "",
    ]
    mism, n_mism = validation
    lines.append(f"- 逐格比对 W05–W22 六类计数：**不一致 {n_mism} 格**。")
    if n_mism:
        lines += [""] + mism[:20]
    lines += ["", "## 1. 相位比较（五类口径，排除噪音后归一）", ""]
    lines.append("| 指标 | " + " | ".join(LABELERS) + " |")
    lines.append("|---|" + "---|" * len(LABELERS))
    rows = [
        ("悼念峰值周", lambda p: p["mourning_peak_week"]),
        ("悼念峰值份额", lambda p: f"{p['mourning_peak_share']:.1%}"),
        ("事件前玩梗基线", lambda p: f"{p['pre_event_meme_baseline']:.1%}"),
        ("玩梗起爆周（>基线+10pp）", lambda p: p["meme_onset_week"] or "未触发"),
        ("玩梗峰值周", lambda p: p["meme_peak_week"]),
        ("玩梗峰值份额", lambda p: f"{p['meme_peak_share']:.1%}"),
        ("W22 玩梗份额", lambda p: f"{p['meme_w22']:.1%}"),
    ]
    for name, getter in rows:
        lines.append(f"| {name} | " + " | ".join(getter(phases[l]) for l in LABELERS) + " |")

    lines += ["", "### 周级玩梗份额轨迹", ""]
    weeks = phases["DeepSeek"]["weeks"]
    lines.append("| 周 | " + " | ".join(LABELERS) + " |")
    lines.append("|---|" + "---|" * len(LABELERS))
    for wk in weeks:
        cells = [f"{phases[l]['share'][wk]['meme']:.1%}" for l in LABELERS]
        lines.append(f"| {wk.replace('2026-', '')} | " + " | ".join(cells) + " |")

    lines += ["", "### 周级悼念份额轨迹", ""]
    lines.append("| 周 | " + " | ".join(LABELERS) + " |")
    lines.append("|---|" + "---|" * len(LABELERS))
    for wk in weeks:
        cells = [f"{phases[l]['share'][wk]['mourning']:.1%}" for l in LABELERS]
        lines.append(f"| {wk.replace('2026-', '')} | " + " | ".join(cells) + " |")

    if robustness:
        lines += ["", "## 2. 三臂拟合排序是否随标注器翻转", ""]
        lines.append("路径归一化 DTW（pp），Agent-only 五类供给份额 vs 各标注器效标。")
        lines.append("")
        lines.append("| 标注器 | 排序（由优到劣） | " + " | ".join(
            f"{a} 均值±sd" for a in ("random", "chronological", "interest")) + " |")
        lines.append("|---|---|" + "---|" * 3)
        for labeler, payload in robustness["labelers"].items():
            per = payload["per_arm"]
            cells = " | ".join(
                f"{per[a]['dtw_mean']:.2f}±{per[a]['dtw_sd']:.2f} "
                f"[{per[a]['dtw_min']:.2f}, {per[a]['dtw_max']:.2f}]"
                for a in ("random", "chronological", "interest")
            )
            lines.append(f"| {labeler} | {' > '.join(payload['ranking'])} | {cells} |")

    if paired:
        lines += ["", "### interest vs random 配对 t 检验（同 seed 配对，n=3）", ""]
        lines.append("| 标注器 | interest 均值 | random 均值 | 均值差 | t | p |")
        lines.append("|---|---|---|---|---|---|")
        for labeler, payload in paired.items():
            lines.append(
                f"| {labeler} | {statistics.fmean(payload['interest']):.2f} | "
                f"{statistics.fmean(payload['random']):.2f} | {payload['mean_diff']:.2f} | "
                f"{payload['t']:.2f} | {payload['p']:.3f} |"
            )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n✅ 报告：{REPORT}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=["a", "b", "all"], default="all")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE.exists() and args.part in {"b", "all"}:
        matrices = json.loads(CACHE.read_text(encoding="utf-8"))
        print(f"[cache] 载入 {CACHE}", flush=True)
    else:
        print("[A] 读取源表周标签 …", flush=True)
        weeks = read_weeks_from_source()
        matrices = build_weekly_matrices(weeks)
        CACHE.write_text(json.dumps(matrices, ensure_ascii=False), encoding="utf-8")
        print(f"[cache] 写入 {CACHE}", flush=True)

    validation = validate_against_frozen(matrices)
    phases = {labeler: phase_summary(matrices[labeler]) for labeler in LABELERS}

    robustness = paired = None
    if args.part in {"b", "all"}:
        robustness = run_arm_robustness(matrices)
        paired = paired_test(matrices)

    write_report(matrices, validation, phases, robustness, paired)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
