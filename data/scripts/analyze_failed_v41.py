#!/usr/bin/env python3
"""诊断 V4.1 轮全程失败行：原因分类、与 GLM 轮失败行重叠、样例内容。"""
import json, openpyxl
from collections import defaultdict, Counter

ROOT = "/Users/easylife/Project/AgentSociety"
DATA = f"{ROOT}/data"   # 打标工作总目录（2026-09-27 起，见 data/README.md）
V41 = f"{DATA}/archive/round4_deepseek-v4.1/.label_results_DSv4_1_flash.jsonl"
GLM = f"{DATA}/archive/round3_glm-5.3-flash/.label_results_GLM5_3flash.jsonl"
SRC = f"{DATA}/baseline/抖音微博小红书-全量已打标.xlsx"


def load(path):
    recs = defaultdict(list)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if isinstance(o, dict) and "row_num" in o:
                rec = o
            elif isinstance(o, list) and len(o) == 5 and isinstance(o[0], int):
                rec = {"row_num": o[0], "category": str(o[1]), "reason": str(o[2]),
                       "valid": str(o[3]), "failed": bool(o[4])}
            else:
                continue
            recs[rec["row_num"]].append(rec)
    return recs


v41, glm = load(V41), load(GLM)
v41_failed = sorted(n for n, rs in v41.items() if not any(not r.get("failed") for r in rs))
glm_failed = sorted(n for n, rs in glm.items() if not any(not r.get("failed") for r in rs))
print(f"V4.1 全程失败: {len(v41_failed)} 条")
print(f"GLM  全程失败: {len(glm_failed)} 条")
print(f"两轮共同失败: {len(set(v41_failed) & set(glm_failed))} 条")

pat = Counter()
for n in v41_failed:
    reasons = " || ".join(r["reason"] for r in v41[n])
    if "SensitiveContentDetected" in reasons:
        pat["内容审核拒绝"] += 1
    elif "无法回答" in reasons or "无法提供" in reasons:
        pat["模型拒答"] += 1
    elif "empty content" in reasons:
        pat["空content"] += 1
    elif "no json array" in reasons:
        pat["无JSON输出"] += 1
    elif "timeout" in reasons.lower() or "timed out" in reasons.lower():
        pat["超时"] += 1
    else:
        pat["其他"] += 1
print(f"V4.1 失败原因: {dict(pat)}")
print(f"V4.1 失败行号: {v41_failed}")

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb["Sheet1"]
it = ws.iter_rows(values_only=True)
h = list(next(it))
idx = {n: h.index(n) for n in ["title", "content", "full_content", "media_type"]}
rows = {}
rn = 1
for row in it:
    rn += 1
    if row is None or all(v is None for v in row):
        continue
    rows[rn] = row
wb.close()

print("\n失败帖样例(前6条):")
for n in v41_failed[:6]:
    r = rows[n]
    t = str(r[idx["title"]] or "")[:50]
    c = str(r[idx["content"]] or r[idx["full_content"]] or "")[:80].replace("\n", " ")
    print(f"  行{n} [{r[idx['media_type']]}] 标题={t!r} 正文={c!r}")
    print(f"    失败原因: {v41[n][-1]['reason'][:110]}")
