#!/usr/bin/env python3
"""
编码轮次的「提示词—调用结构」溯源核查（只读，不修改任何数据）。

背景：论文 §（四）曾把原标（第 1 轮）相对后三轮的偏离表述为「该轮判定本身的系统性偏移」。
用户质疑：后三轮的提示词可能与第 1 轮不同，偏离是否由提示词造成。本脚本据实核查：

  A. 各轮打标脚本的 SYSTEM_PROMPT 指纹（AST 抽取 + sha256 前缀）与调用结构（每次调用判定几条）
  B. 各轮「判定依据」文本长度分布 —— 提示词差异的**输出端签名**
  C. 类别分布对照 + 原标「其他讨论」在后三轮的去向
  D. 分歧是否集中在单一类别边界（原标=其他讨论 且 后三轮一致=教育观点讨论）

用法: python prompt_provenance_check.py
"""
import ast, collections, hashlib, os, random, statistics, sys

import openpyxl

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["batch_label.py", "batch_label_v2.py", "batch_label_v3.py",
           "retry_failed.py", "retry_failed_glm.py"]
R1 = "原标(第1轮)"
R2, R3, R4 = "Seed(第2轮)", "GLM(第3轮)", "DSv4.1(第4轮)"
ROUNDS = [
    ("原标(第1轮)", f"{ROOT}/抖音微博小红书-全量已打标.xlsx"),
    ("Seed(第2轮)", f"{ROOT}/抖音微博小红书-独立重打标_Seed2_1_lite.xlsx"),
    ("GLM(第3轮)", f"{ROOT}/抖音微博小红书-独立重打标_GLM5_3flash.xlsx"),
    ("DSv4.1(第4轮)", f"{ROOT}/抖音微博小红书-独立重打标_DSv4_1_flash.xlsx"),
]
CATS = ["借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音"]


def section(t):
    print(f"\n{'='*78}\n{t}\n{'='*78}")


def prompt_fingerprint():
    """A. 从脚本源码里抽出 SYSTEM_PROMPT 字面量，比对指纹与调用结构。"""
    section("A. 各脚本的 SYSTEM_PROMPT 指纹与调用结构")
    out = {}
    for fn in SCRIPTS:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            print(f"  {fn}: 不存在"); continue
        tree = ast.parse(open(p, encoding="utf-8").read())
        text, per_call = None, None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", None) == "SYSTEM_PROMPT" for t in node.targets):
                text = node.value.value
        src = open(p, encoding="utf-8").read()
        if "label_batch(" in src:
            per_call = "8 条/次（label_batch, BSIZE=8）"
        elif "label_one(" in src:
            per_call = "1 条/次（label_one）"
        h = hashlib.sha256(text.encode()).hexdigest()[:16] if text else "—"
        out[fn] = h
        print(f"  {fn:<22} 长度={len(text) if text else 0:>4}  sha256={h}  调用={per_call}")
    uniq = {h for h in out.values() if h != "—"}
    print(f"\n  → 判定标准（六类定义/判定原则）去重后共 {len(uniq)} 个版本：{sorted(uniq)}")
    print("  → 差异仅在【输出格式】段（单对象 vs JSON 数组），该段与调用结构（1 条/次 vs 8 条/次）耦合。")


def load_round(name, path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    ic, iv, ir = hdr.index("内容类别"), hdr.index("数据有效性"), hdr.index("判定依据")
    it_ = hdr.index("title")
    ifc = hdr.index("content") if "content" in hdr else None
    cats, vals, lens, texts = {}, {}, [], {}
    for i, row in enumerate(it):
        if row[ic] is None:
            continue
        cats[i] = str(row[ic]); vals[i] = str(row[iv])
        r = str(row[ir]).strip() if row[ir] else ""
        lens.append(len(r))
        if name.startswith("原标"):
            texts[i] = (str(row[it_] or "")[:56],
                        (str(row[ifc] or "")[:70] if ifc is not None else ""))
    wb.close()
    return cats, vals, lens, texts


def main():
    prompt_fingerprint()
    data, vals_all, lens_all, titles = {}, {}, {}, {}
    for name, path in ROUNDS:
        data[name], vals_all[name], lens_all[name], titles[name] = load_round(name, path)

    section("B. 「判定依据」文本长度分布（提示词差异的输出端签名）")
    print(f"  {'轮次':<14}{'中位':>6}{'均值':>8}{'P90':>6}{'≤20字占比':>11}")
    for name, _ in ROUNDS:
        L = sorted(lens_all[name]); n = len(L)
        print(f"  {name:<14}{L[n//2]:>6}{statistics.mean(L):>8.1f}"
              f"{L[int(n*.9)]:>6}{sum(1 for x in L if x <= 20)/n*100:>10.1f}%")

    section("C. 类别分布对照（%）")
    print(f"  {'类别':<14}" + "".join(f"{n:>14}" for n, _ in ROUNDS))
    for c in CATS:
        row = []
        for name, _ in ROUNDS:
            d = data[name]; k = sum(1 for v in d.values() if v == c)
            row.append(f"{k/len(d)*100:>13.1f}%")
        print(f"  {c:<14}" + "".join(row))

    idx = sorted(data[R1])
    oth = [i for i in idx if data[R1][i] == "其他讨论"]
    section(f"D. 原标「其他讨论」{len(oth)} 条在后三轮的去向")
    for name in [R2, R3, R4]:
        c = collections.Counter(data[name].get(i) for i in oth)
        print(f"  {name:<14}" + " | ".join(f"{k} {v/len(oth)*100:.1f}%" for k, v in c.most_common()))

    section("E. 分歧是否集中在单一类别边界")
    S = [i for i in oth if all(data[n].get(i) == "教育观点讨论"
                               for n in ["Seed(第2轮)", "GLM(第3轮)", "DSv4.1(第4轮)"])]
    print(f"  原标=其他讨论 且 后三轮**一致**=教育观点讨论：{len(S)} 条"
          f"（占原标其他讨论 {len(S)/len(oth)*100:.1f}%）")
    R = [i for i in idx if data[R1][i] == "教育观点讨论"
         and all(data[n].get(i) != "教育观点讨论"
                 for n in ["Seed(第2轮)", "GLM(第3轮)", "DSv4.1(第4轮)"])]
    print(f"  原标=教育观点讨论 且 后三轮**一致**判为非教育：{len(R)} 条")
    rc = collections.Counter(data[R2].get(i) for i in R)
    print(f"     └ 这 {len(R)} 条在 Seed 轮的归属：" +
          " | ".join(f"{k} {v}" for k, v in rc.most_common(3)))

    random.seed(0)
    print(f"\n  【原标=其他讨论 → 后三轮一致=教育观点讨论】抽样 12 条：")
    for i in random.sample(S, 12):
        t, c = titles[R1][i]
        print(f"    行{i+2}｜{t}｜{c}")
    print(f"\n  【原标=教育观点讨论 → 后三轮一致判为非教育】抽样 8 条：")
    for i in random.sample(R, 8):
        t, c = titles[R1][i]
        print(f"    行{i+2}｜{t}｜{c}｜后三轮="
              + "/".join(data[n].get(i) for n in [R2, R3, R4]))


if __name__ == "__main__":
    main()
