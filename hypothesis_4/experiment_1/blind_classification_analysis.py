#!/usr/bin/env python3
"""盲法判类结果分析（W2 整改第三步）。

回答的问题
----------
论文图 3b/图 4 的"玩梗供给"用的是 **pool_type**（Agent 固定身份，by construction），
因此"表征向玩梗转移"可能只是"身份为玩梗的 Agent 说话更多"，而不是生成文本真的变成
了玩梗。本脚本用盲法判类（GLM，与生成模型不同族，只看正文）重算同一批轨迹，检验：

1. 身份 ↔ 文本 的错配结构（是否闭环）；
2. 环境的四词表复核与盲法判类谁更接近身份标签（即论文的"独立观测"是否成立）；
3. 用**文本类别**重算周级玩梗供给轨迹后，W19 回升 / W20 起爆是否仍然存在；
4. 用文本类别重算三臂对真实效标的 DTW，排序是否与论文一致。

用法
----
    python blind_classification_analysis.py [judge_jsonl]
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

BLIND_DIR = SCRIPT_DIR / "results" / "blind_classification"
META_JSONL = BLIND_DIR / "agent_posts.jsonl"
MATRICES_CACHE = SCRIPT_DIR / "results" / "labeler_sensitivity" / "weekly_matrices.json"
REPORT = BLIND_DIR / "REPORT.md"

CAT2TYPE = {
    "借势营销": "marketing",
    "事件悼念讨论": "mourning",
    "教育观点讨论": "education",
    "梗文化讨论": "meme",
    "其他讨论": "other",
    "爬取噪音": "noise",
}
TYPE_CN = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
           "marketing": "营销", "other": "其他", "noise": "噪音"}
VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]
ARMS = ["random", "chronological", "interest"]
WINDOW = 1


def load_rows(judge_path: Path) -> list[dict]:
    meta = [json.loads(l) for l in META_JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    judged: dict[int, dict] = {}
    for line in judge_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            idx = int(row["index"])
            if not row.get("failed") and row.get("category"):
                judged[idx] = row
    rows = []
    for i, rec in enumerate(meta):
        j = judged.get(i)
        if j is None:
            continue
        rows.append({**rec, "blind_cat": j["category"],
                     "blind_type": CAT2TYPE.get(j["category"], "other")})
    return rows


def cohen_kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if not n:
        return 0.0
    po = sum(1 for a, b in pairs if a == b) / n
    cats_a = Counter(a for a, _ in pairs)
    cats_b = Counter(b for _, b in pairs)
    pe = sum(cats_a[k] / n * cats_b.get(k, 0) / n for k in set(cats_a) | set(cats_b))
    return (po - pe) / (1 - pe) if pe < 1 else 0.0


def weekly_shares(rows: list[dict], key: str) -> dict[tuple[str, str], dict[str, float]]:
    """(arm, week) -> 五类供给份额（排除噪音后归一）。"""
    buckets: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in rows:
        t = r.get(key)
        if t in VALID_TYPES:
            buckets[(r["arm"], r["week"])][t] += 1
    out = {}
    for k, counter in buckets.items():
        total = sum(counter.values())
        out[k] = {t: (counter.get(t, 0) / total if total else 0.0) for t in VALID_TYPES}
    return out


def run_dtw(rows: list[dict], key: str, observed: np.ndarray, weeks: list[str]) -> dict:
    from plot_dtw_validation import constrained_multivariate_dtw
    shares = weekly_shares(rows, key)
    scores = {arm: [] for arm in ARMS}
    for arm in ARMS:
        for seed in (0, 1, 2):
            mat = np.asarray(
                [[shares.get((arm, wk), {}).get(t, 0.0) for t in VALID_TYPES] for wk in weeks],
                dtype=float,
            )
            score, _ = constrained_multivariate_dtw(mat, observed, window=WINDOW)
            scores[arm].append(score * 100)
    return {
        arm: {
            "mean": statistics.fmean(v), "sd": statistics.stdev(v),
            "min": min(v), "max": max(v),
        }
        for arm, v in scores.items()
    }


def main() -> int:
    judge_path = Path(sys.argv[1]) if len(sys.argv) > 1 else BLIND_DIR / "judge_glm-5-3-flash-260828.jsonl"
    if not judge_path.exists():
        raise SystemExit(f"判类结果不存在：{judge_path}")
    rows = load_rows(judge_path)
    total_meta = sum(1 for l in META_JSONL.read_text(encoding="utf-8").splitlines() if l.strip())
    print(f"载入 {len(rows)}/{total_meta} 条已判类记录")

    weeks = sorted({r["week"] for r in rows})
    blind_dist = Counter(r["blind_type"] for r in rows)
    pool_dist = Counter(r["pool_type"] for r in rows)
    env_dist = Counter(r["env_assigned_type"] for r in rows)

    pairs_pt = [(r["pool_type"], r["blind_type"]) for r in rows]
    pairs_env = [(r["pool_type"], r["env_assigned_type"]) for r in rows]
    pairs_eb = [(r["env_assigned_type"], r["blind_type"]) for r in rows]

    blind_shares = weekly_shares(rows, "blind_type")
    pool_shares = weekly_shares(rows, "pool_type")

    # 真实效标（三标注器）
    benchmarks = {}
    if MATRICES_CACHE.exists():
        matrices = json.loads(MATRICES_CACHE.read_text(encoding="utf-8"))
        for labeler, matrix in matrices.items():
            denom = {wk: sum(matrix[wk][k] for k in VALID_TYPES) for wk in matrix}
            benchmarks[labeler] = np.asarray(
                [[matrix[wk][t] / denom[wk] if denom[wk] else 0.0 for t in VALID_TYPES]
                 for wk in weeks],
                dtype=float,
            )
    dtw_pool = {l: run_dtw(rows, "pool_type", obs, weeks) for l, obs in benchmarks.items()}
    dtw_blind = {l: run_dtw(rows, "blind_type", obs, weeks) for l, obs in benchmarks.items()}

    lines = ["# 盲法判类分析：文本类别 vs 身份标签（W2 整改）", ""]
    lines += [
        f"- 判类模型：GLM（`{judge_path.stem.replace('judge_', '')}`），生成模型为 `deepseek-v4-flash`。",
        f"- 判定标准：与真实帖文打标完全相同的 prompt（AST 取自 `batch_label_v3.py`）。",
        f"- 输入：仅正文；不含 arm、身份、周次、四词表。覆盖 {len(rows)}/{total_meta} 条。",
        "",
        "## 1. 三种口径下的类别分布",
        "",
        "| 口径 | " + " | ".join(TYPE_CN[t] for t in VALID_TYPES + ["noise"]) + " |",
        "|---|" + "---|" * 6,
    ]
    for name, dist in (("pool_type（身份，论文现用）", pool_dist),
                       ("env_assigned_type（环境四词表复核）", env_dist),
                       ("blind_type（盲法文本判类）", blind_dist)):
        lines.append(f"| {name} | " + " | ".join(str(dist.get(t, 0)) for t in VALID_TYPES + ["noise"]) + " |")

    lines += ["", "## 2. 一致性：身份标签到底能不能代表文本", "",
              "| 比较 | 一致率 | Cohen's κ |", "|---|---|---|"]
    for name, pairs in (("身份 vs 盲法文本", pairs_pt),
                        ("身份 vs 环境四词表复核", pairs_env),
                        ("环境四词表复核 vs 盲法文本", pairs_eb)):
        agree = sum(1 for a, b in pairs if a == b) / len(pairs) if pairs else 0.0
        lines.append(f"| {name} | {agree:.1%} | {cohen_kappa(pairs):.3f} |")

    # 错配矩阵
    lines += ["", "### 身份 → 盲法文本 错配矩阵（行=身份，列=盲法判类，行内占比）", ""]
    cols = VALID_TYPES + ["noise"]
    lines.append("| 身份＼文本 | " + " | ".join(TYPE_CN[c] for c in cols) + " | 行合计 |")
    lines.append("|---|" + "---|" * (len(cols) + 1))
    matrix = Counter((r["pool_type"], r["blind_type"]) for r in rows)
    for pt in VALID_TYPES:
        row_total = sum(matrix.get((pt, c), 0) for c in cols)
        cells = [
            f"{matrix.get((pt, c), 0)} ({matrix.get((pt, c), 0) / row_total:.0%})" if row_total else "0"
            for c in cols
        ]
        lines.append(f"| {TYPE_CN[pt]} | " + " | ".join(cells) + f" | {row_total} |")

    # 周级轨迹
    lines += ["", "## 3. 周级玩梗供给份额：身份口径 vs 文本口径", ""]
    lines.append("| 臂 | 周 | 身份口径 | 文本口径 |")
    lines.append("|---|---|---|---|")
    for arm in ARMS:
        for wk in weeks:
            lines.append(
                f"| {arm} | {wk.replace('2026-', '')} | "
                f"{pool_shares.get((arm, wk), {}).get('meme', 0.0):.1%} | "
                f"{blind_shares.get((arm, wk), {}).get('meme', 0.0):.1%} |"
            )

    # DTW 比较
    lines += ["", "## 4. 三臂 DTW：身份口径 vs 文本口径", ""]
    for labeler in benchmarks:
        lines.append(f"### 效标 = {labeler}")
        lines.append("")
        lines.append("| 口径 | 排序（由优到劣） | " + " | ".join(
            f"{a} 均值±sd [min,max]" for a in ARMS) + " |")
        lines.append("|---|---|" + "---|" * 3)
        for name, table in (("身份 pool_type", dtw_pool[labeler]),
                            ("文本 blind_type", dtw_blind[labeler])):
            ranking = sorted(ARMS, key=lambda a: table[a]["mean"])
            cells = " | ".join(
                f"{table[a]['mean']:.2f}±{table[a]['sd']:.2f} "
                f"[{table[a]['min']:.2f}, {table[a]['max']:.2f}]" for a in ARMS
            )
            lines.append(f"| {name} | {' > '.join(ranking)} | {cells} |")
        lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ 报告：{REPORT}")
    print("\n身份 vs 盲法文本：一致率 "
          f"{sum(1 for a, b in pairs_pt if a == b) / len(pairs_pt):.1%}，"
          f"κ={cohen_kappa(pairs_pt):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
