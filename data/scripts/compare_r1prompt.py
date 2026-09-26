#!/usr/bin/env python3
"""
「第1轮口径 × DeepSeek-V4.1」与 原标 / 第4轮 的三方对比 —— 把口径差异与判定质量差异分离。

设计（2×2 对照，本次补上左下格）：
                    第1轮口径                    后三轮口径
  原标模型(v4-flash) 已有（=原标，agentic 150行/批）  —
  V4.1              **本次（R1prompt_V4_1，API 8条/批）**  已有（=第4轮，API 8条/批）

  · 本次 vs 第4轮：同模型、同调用结构，仅口径不同 → **纯口径效应（提示词+输入字段）**
  · 本次 vs 原标  ：同提示词、同输入字段，模型与调用结构不同 → **模型+调用结构效应**
  · 原标 vs 第4轮：两者都不同（基准参照）

用法: python compare_r1prompt.py [slug]   # 默认 slug=R1prompt_V4_1
"""
import os, sys, datetime
from collections import Counter
from itertools import combinations

import openpyxl

ROOT = "/Users/easylife/Project/AgentSociety"
DATA = f"{ROOT}/data"   # 打标工作总目录（2026-09-27 起，见 data/README.md）
SLUG = sys.argv[1] if len(sys.argv) > 1 else "R1prompt_V4_1"
CAT_ORDER = ["借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音", "存疑"]
VAL_ORDER = ["有效", "无效", "存疑"]

PATHS = {
    "原标(第1轮口径,v4-flash)": f"{DATA}/baseline/抖音微博小红书-全量已打标.xlsx",
    "第4轮(后三轮口径,V4.1)": f"{DATA}/archive/round4_deepseek-v4.1/抖音微博小红书-独立重打标_DSv4_1_flash.xlsx",
    f"本次(第1轮口径,V4.1)": f"{DATA}/runs/抖音微博小红书-独立重打标_{SLUG}.xlsx",
}
A, B, C = list(PATHS)          # 原标 / 第4轮 / 本次


def load_labels(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    header = list(next(it))
    id_i, t_i, c_i = header.index("id"), header.index("title"), header.index("content")
    out = []
    for row in it:
        if row[0] is None:
            continue
        title, content = row[t_i] or "", row[c_i] or ""
        snippet = str(title)[:40] if str(title).strip() else str(content)[:40]
        out.append((str(row[0]), str(row[1]), str(row[2]), row[id_i], snippet))
    wb.close()
    return out


def kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    joint = Counter(zip(a, b))
    p_o = sum(v for (x, y), v in joint.items() if x == y) / n
    ca, cb = Counter(a), Counter(b)
    p_e = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if p_e == 1:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def confusion(a, b, order):
    m = {x: {y: 0 for y in order} for x in order}
    for x, y in zip(a, b):
        m.setdefault(x, {}).setdefault(y, 0)
        m[x][y] = m[x].get(y, 0) + 1
    return m


def fmt_matrix(m, order, la, lb):
    short = {c: c[:2] for c in order}
    head = f"{'A\\B':<6}" + "".join(f"{short[c]:>7}" for c in order)
    lines = [head, "-" * len(head)]
    for x in order:
        lines.append(f"{short[x]:<6}" + "".join(f"{m.get(x, {}).get(y, 0):>7}" for y in order))
    return "\n".join(lines)


def main():
    data = {}
    for name, p in PATHS.items():
        if not os.path.exists(p):
            print(f"❌ 缺少文件: {name} → {p}")
            sys.exit(1)
        data[name] = load_labels(p)
        print(f"载入 {name}: {len(data[name])} 行")

    names = list(data)
    n = len(data[A])
    for nm in names:
        assert len(data[nm]) == n, f"{nm} 行数不一致: {len(data[nm])} != {n}"
    for i in [0, n // 2, n - 1]:
        assert len({str(data[nm][i][3]) for nm in names}) == 1, f"行 {i} id 不对齐"
    print(f"行数与 id 对齐校验通过（n={n}）\n")

    cats = {nm: [r[1] for r in data[nm]] for nm in names}
    vals = {nm: [r[0] for r in data[nm]] for nm in names}
    lens = {nm: sorted(len(r[2]) for r in data[nm]) for nm in names}

    today = datetime.date.today().strftime("%Y%m%d")
    md = [f"# 第1轮口径复现对比报告（{today}）\n",
          "**目的**：第 1 轮（原标）提示词已于 2026-09-26 恢复（`label_prompt_round1.md`）。",
          f"本报告用该提示词 + 该轮输入字段在 DeepSeek-V4.1 上重跑全量（slug=`{SLUG}`），",
          "补上 2×2 对照中缺失的一格，把「口径差异」与「判定质量差异」分离。\n",
          "|  | 第1轮口径 | 后三轮口径 |", "|---|---|---|",
          "| 原标模型 (v4-flash) | 原标（agentic 150行/批） | — |",
          "| DeepSeek-V4.1 | **本次**（API 8条/批） | 第4轮（API 8条/批） |\n",
          "**两个可分离的效应**：",
          f"- **纯口径效应（提示词+输入字段）**：`{C}` vs `{B}` —— 同模型、同调用结构",
          f"- **模型+调用结构效应**：`{C}` vs `{A}` —— 同提示词、同输入字段",
          f"- 参照（两者皆不同）：`{A}` vs `{B}`\n", ""]

    md.append("## A. 分布对照\n")
    md.append("### 类别分布\n")
    md.append("| 类别 | " + " | ".join(names) + " |")
    md.append("|---" * (len(names) + 1) + "|")
    for c in CAT_ORDER:
        row = [f"{sum(1 for v in cats[nm] if v == c)} ({sum(1 for v in cats[nm] if v == c)*100/n:.1f}%)"
               for nm in names]
        md.append(f"| {c} | " + " | ".join(row) + " |")
    md.append("")
    md.append("### 有效性分布\n")
    md.append("| 有效性 | " + " | ".join(names) + " |")
    md.append("|---" * (len(names) + 1) + "|")
    for v in VAL_ORDER:
        row = [f"{sum(1 for x in vals[nm] if x == v)}" for nm in names]
        if all(r == "0" for r in row):
            continue
        md.append(f"| {v} | " + " | ".join(row) + " |")
    md.append("")
    md.append("### 判定依据长度（提示词约束的输出端签名）\n")
    md.append("| 轮次 | 中位 | 均值 | P90 | 最大 | ≤20字 | ≤30字 |")
    md.append("|---|---|---|---|---|---|---|")
    for nm in names:
        L = lens[nm]
        md.append(f"| {nm} | {L[n//2]} | {sum(L)/n:.1f} | {L[int(n*.9)]} | {L[-1]} | "
                  f"{sum(1 for x in L if x <= 20)/n*100:.1f}% | {sum(1 for x in L if x <= 30)/n*100:.1f}% |")
    md.append("")

    md.append("## B. 两两一致性与 κ\n")
    for a, b in combinations(names, 2):
        ac = sum(x == y for x, y in zip(cats[a], cats[b]))
        av = sum(x == y for x, y in zip(vals[a], vals[b]))
        md.append(f"### {a}  vs  {b}\n")
        md.append(f"- 类别一致率 **{ac/n*100:.2f}%**（{ac}/{n}），Cohen's κ = **{kappa(cats[a], cats[b]):.4f}**")
        md.append(f"- 有效性一致率 {av/n*100:.2f}%，κ = {kappa(vals[a], vals[b]):.4f}\n")
        order = [c for c in CAT_ORDER if c in set(cats[a]) | set(cats[b])]
        md.append("类别混淆矩阵（行=" + a + "，列=" + b + "）：\n```\n"
                  + fmt_matrix(confusion(cats[a], cats[b], order), order, a, b) + "\n```\n")

    md.append("## C. 效应分解\n")
    k_ac = kappa(cats[A], cats[C])
    k_bc = kappa(cats[B], cats[C])
    k_ab = kappa(cats[A], cats[B])
    md.append(f"| 对比 | 变的是什么 | 类别一致率 | κ |")
    md.append("|---|---|---|---|")
    md.append(f"| 本次 vs 第4轮 | **仅口径**（提示词+输入字段） | "
              f"{sum(x==y for x,y in zip(cats[C],cats[B]))/n*100:.2f}% | {k_bc:.4f} |")
    md.append(f"| 本次 vs 原标 | **仅模型+调用结构** | "
              f"{sum(x==y for x,y in zip(cats[C],cats[A]))/n*100:.2f}% | {k_ac:.4f} |")
    md.append(f"| 原标 vs 第4轮 | 口径与模型皆不同 | "
              f"{sum(x==y for x,y in zip(cats[A],cats[B]))/n*100:.2f}% | {k_ab:.4f} |")
    md.append("")
    md.append("读法：若「仅口径」的一致率明显高于「口径与模型皆不同」，说明原标偏离主要来自口径；")
    md.append("若「仅模型+调用结构」的一致率也很低，说明换模型本身也会带来同等量级的差异。\n")

    # 原标独有的「存疑」
    dq = [i for i in range(n) if cats[A][i] == "存疑"]
    md.append(f"## D. 原标独有「存疑」{len(dq)} 条的归属\n")
    md.append("「存疑」是第 1 轮口径独有的类别（后三轮无此取值）。\n")
    md.append("| 行号 | 内容摘要 | 本次 | 第4轮 |")
    md.append("|---|---|---|---|")
    for i in dq:
        md.append(f"| {i+2} | {data[A][i][4]} | {cats[C][i]}（{vals[C][i]}） | {cats[B][i]}（{vals[B][i]}） |")
    md.append("")
    nc = sum(1 for i in range(n) if cats[C][i] == "存疑")
    md.append(f"本次（第1轮口径）判为「存疑」：{nc} 条（{nc/n*100:.2f}%）；"
              f"原标 {len(dq)} 条（{len(dq)/n*100:.2f}%）\n")

    path = f"{DATA}/reports/第1轮口径复现对比报告_{today}.md"
    open(path, "w").write("\n".join(md))
    print(f"✅ 报告：{path}")


if __name__ == "__main__":
    main()
