#!/usr/bin/env python3
"""人工复编码一致性计算与关键结论敏感性。

输入
----
--a / --b   编码者填好的 CSV（sample_id, category, valid, note）
--key       抽样答案表（sample_id, row_num, platform, week, model_category）
--adjudicated  可选：第三人裁定后的 CSV（列同上），用于"裁定后"口径

输出
----
REPORT.md：编码者间与"编码者×模型"的类别/有效性一致率与 Cohen's κ、逐类混淆矩阵、
以及不同编码口径下玩梗类份额与相位（起爆周）对比。

用法
----
    python compute_agreement.py --a sample/coderA.csv --b sample/coderB.csv --key sample/key.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORT = SCRIPT_DIR / "AGREEMENT_REPORT.md"

CATS = ["借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音"]
TYPE_OF = {
    "借势营销": "marketing", "事件悼念讨论": "mourning", "教育观点讨论": "education",
    "梗文化讨论": "meme", "其他讨论": "other", "爬取噪音": "noise",
}
VALID_TYPES = ["meme", "mourning", "education", "marketing", "other"]
TYPE_CN = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
           "marketing": "营销", "other": "其他"}


def read_csv(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {r["sample_id"]: r for r in csv.DictReader(fh) if r.get("sample_id")}


def kappa(pairs: list[tuple[str, str]]) -> tuple[float, float]:
    n = len(pairs)
    if not n:
        return 0.0, 0.0
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] / n * cb.get(k, 0) / n for k in set(ca) | set(cb))
    return po, ((po - pe) / (1 - pe) if pe < 1 else 0.0)


def confusion(pairs: list[tuple[str, str]], labels: list[str]) -> list[str]:
    m = Counter(pairs)
    out = ["| A＼B | " + " | ".join(labels) + " | 行合计 |",
           "|---|" + "---|" * (len(labels) + 1)]
    for a in labels:
        row = sum(m.get((a, b), 0) for b in labels)
        out.append(f"| {a} | " + " | ".join(str(m.get((a, b), 0)) for b in labels) + f" | {row} |")
    return out


def phase(rows: list[dict], cat_key: str) -> dict:
    """按周（五类归一）计算玩梗份额与相位。"""
    by_week: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        t = TYPE_OF.get(r.get(cat_key, ""))
        if t in VALID_TYPES:
            by_week[r["week"]][t] += 1
    weeks = sorted(by_week)
    share = {}
    for wk in weeks:
        tot = sum(by_week[wk].values())
        share[wk] = {t: (by_week[wk].get(t, 0) / tot if tot else 0.0) for t in VALID_TYPES}
    if not weeks:
        return {}
    pre = [share[w]["meme"] for w in weeks if w < "2026-W13"]
    base = statistics.fmean(pre) if pre else 0.0
    onset = next((w for w in weeks if w >= "2026-W13" and share[w]["meme"] > base + 0.10), None)
    late = [share[w]["meme"] for w in weeks if w >= "2026-W19"]
    peak = max(weeks, key=lambda w: share[w]["meme"])
    mpeak = max(weeks, key=lambda w: share[w]["mourning"])
    return {
        "n": len(rows), "weeks": weeks, "share": share,
        "meme_baseline": base, "meme_onset": onset,
        "meme_late_mean": statistics.fmean(late) if late else 0.0,
        "meme_peak_week": peak, "meme_peak_share": share[peak]["meme"],
        "mourning_peak_week": mpeak, "mourning_peak_share": share[mpeak]["mourning"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--adjudicated")
    args = ap.parse_args()

    key = read_csv(Path(args.key))
    coders = {"A": read_csv(Path(args.a)), "B": read_csv(Path(args.b))}
    if args.adjudicated:
        coders["裁定"] = read_csv(Path(args.adjudicated))

    # 只保留已填写的类别
    filled = {
        name: {sid: r for sid, r in rows.items() if (r.get("category") or "").strip()}
        for name, rows in coders.items()
    }
    common_ids = sorted(set(filled["A"]) & set(filled["B"]) & set(key))

    lines = ["# 人工复编码一致性报告", "",
             f"- 抽样条目：{len(key)}；编码者 A 已填 {len(filled['A'])}，B 已填 {len(filled['B'])}。",
             f"- A、B 同时填写且可对齐的条目：**{len(common_ids)}**。", ""]

    if not common_ids:
        REPORT.write_text("\n".join(lines + ["", "尚无可用的一致条目。"]) + "\n", encoding="utf-8")
        print("尚无可用的一致条目")
        return 0

    lines += ["## 1. 类别一致性（编码者与模型）", "",
              "| 比较 | 一致率 | Cohen's κ |", "|---|---|---|"]
    comparisons = [("A vs B", "A", "B")]
    comparisons += [("A vs 模型", "A", "key"), ("B vs 模型", "B", "key")]
    if "裁定" in filled:
        comparisons += [("裁定 vs 模型", "裁定", "key"), ("裁定 vs A", "裁定", "A")]
    for label, x, y in comparisons:
        if y == "key":
            ps = [(filled[x][sid]["category"].strip(), (key[sid]["model_category"] or "").strip())
                  for sid in common_ids]
        else:
            ps = [(filled[x][sid]["category"].strip(), filled[y][sid]["category"].strip())
                  for sid in common_ids]
        po, k = kappa(ps)
        lines.append(f"| {label} | {po:.1%} | {k:.3f} |")

    lines += ["", "### A vs B 类别混淆矩阵", ""]
    lines += confusion([(filled["A"][s]["category"].strip(), filled["B"][s]["category"].strip())
                        for s in common_ids], CATS)

    lines += ["", "### A vs 模型 类别混淆矩阵", ""]
    lines += confusion([(filled["A"][s]["category"].strip(), (key[s]["model_category"] or "").strip())
                        for s in common_ids], CATS)

    valid_pairs = [(filled["A"][s].get("valid", "").strip(), filled["B"][s].get("valid", "").strip())
                   for s in common_ids if (filled["A"][s].get("valid") or "").strip()
                   and (filled["B"][s].get("valid") or "").strip()]
    if valid_pairs:
        po, k = kappa(valid_pairs)
        lines += ["", f"## 2. 有效性一致性（A vs B，n={len(valid_pairs)}）", "",
                  f"一致率 {po:.1%}，Cohen's κ = {k:.3f}"]

    # 关键结论敏感性
    lines += ["", "## 3. 关键结论敏感性：玩梗轨迹与相位", "",
              "| 编码口径 | n | 事件前玩梗基线 | W19–W22 玩梗均值 | 起爆周（>基线+10pp） | 玩梗峰值周 | 悼念峰值周 |",
              "|---|---|---|---|---|---|---|"]
    subset = [dict(key[s], **{"A": filled["A"][s]["category"].strip(),
                              "B": filled["B"][s]["category"].strip()}) for s in common_ids]
    sources = [("模型标签", "model_category"), ("编码者 A", "A"), ("编码者 B", "B")]
    if "裁定" in filled:
        for r in subset:
            r["裁定"] = filled["裁定"].get(r["sample_id"], {}).get("category", "").strip()
        sources.append(("第三人裁定", "裁定"))
    for name, field in sources:
        p = phase(subset, field)
        if not p:
            continue
        lines.append(
            f"| {name} | {p['n']} | {p['meme_baseline']:.1%} | {p['meme_late_mean']:.1%} | "
            f"{(p['meme_onset'] or '未触发').replace('2026-', '')} | "
            f"{p['meme_peak_week'].replace('2026-', '')} | "
            f"{p['mourning_peak_week'].replace('2026-', '')} |")

    lines += ["", "> 说明：分层样本每周仅数条，周级相位检验功效很低。",
              "> 判定标准应以「W19–W22 玩梗均值相对事件前基线的抬升是否在人工编码下同样出现」为主，",
              "> 周级起爆周仅作描述性参照。"]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ 报告：{REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
