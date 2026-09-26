#!/usr/bin/env python3
"""抽取人工复编码用的分层盲化样本（spot check）。

产出
----
sample/coderA.csv, sample/coderB.csv
    给两名编码者的编码表。两份**内容完全相同**，但顺序各自独立打乱；列只有
    sample_id / title / content / category(空) / valid(空) / note(空)。
    **不含**周次、平台、原模型标签、判定依据。
sample/key.csv
    答案表：sample_id → row_num、platform、week、原模型标签。编码者不得查看。

用法
----
    python draw_spot_check_sample.py --n 400 --coders 2 --seed 20260925
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import openpyxl

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
SOURCE = ROOT / "data" / "baseline" / "抖音微博小红书-全量已打标.xlsx"
OUT_DIR = SCRIPT_DIR / "sample"

WINDOW_START, WINDOW_END = "2026-W05", "2026-W22"
MAX_CHARS = 1200


def week_key(value) -> str | None:
    if value is None:
        return None
    dt = value if isinstance(value, datetime) else None
    if dt is None:
        text = str(value).strip().replace("Z", "+00:00")
        if not text:
            return None
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--coders", type=int, default=2)
    ap.add_argument("--seed", type=int, default=20260925)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.load_workbook(SOURCE, read_only=True)
    ws = wb.active
    strata: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        validity, category = str(row[0] or "").strip(), str(row[1] or "").strip()
        title, content = str(row[6] or "").strip(), str(row[7] or "").strip()
        published, platform = row[12], str(row[14] or "").strip()
        if validity == "存疑":
            continue
        wk = week_key(published)
        if wk is None or wk < WINDOW_START or wk > WINDOW_END:
            continue
        strata[(platform, wk)].append(
            {"row_num": i + 2, "platform": platform, "week": wk,
             "title": title, "content": content[:MAX_CHARS], "model_category": category}
        )
    wb.close()

    total = sum(len(v) for v in strata.values())
    print(f"分层框：{len(strata)} 个「平台×周」单元，共 {total} 条可用帖文")

    # 按比例分配，至少 1 条，凑满 n
    allocated = {}
    for key, items in strata.items():
        share = len(items) / total
        allocated[key] = max(1, min(len(items), round(share * args.n)))
    # 修正总量
    while sum(allocated.values()) > args.n:
        key = max((k for k in allocated if allocated[k] > 1), key=lambda k: allocated[k])
        allocated[key] -= 1
    while sum(allocated.values()) < args.n:
        key = max(strata, key=lambda k: len(strata[k]) - allocated[k])
        if allocated[key] >= len(strata[key]):
            break
        allocated[key] += 1

    sample = []
    for key, k in allocated.items():
        sample.extend(rng.sample(strata[key], k))
    rng.shuffle(sample)
    for idx, rec in enumerate(sample, start=1):
        rec["sample_id"] = f"S{idx:04d}"
    print(f"实际抽样：{len(sample)} 条")

    fieldnames = ["sample_id", "title", "content", "category", "valid", "note"]
    for c in range(args.coders):
        label = chr(ord("A") + c)
        order = sample[:]
        random.Random(args.seed + 100 + c).shuffle(order)  # 两名编码者顺序不同
        with (OUT_DIR / f"coder{label}.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            for rec in order:
                w.writerow({**rec, "category": "", "valid": "", "note": ""})

    with (OUT_DIR / "key.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["sample_id", "row_num", "platform", "week", "model_category"])
        w.writeheader()
        for rec in sample:
            w.writerow({k: rec[k] for k in
                        ("sample_id", "row_num", "platform", "week", "model_category")})

    print(f"✅ 编码表：{OUT_DIR}/coder{{A..{chr(ord('A') + args.coders - 1)}}}.csv")
    print(f"✅ 答案表：{OUT_DIR}/key.csv（编码者不得查看）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
