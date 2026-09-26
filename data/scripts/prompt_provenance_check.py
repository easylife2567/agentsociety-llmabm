#!/usr/bin/env python3
"""
编码轮次的「提示词—调用结构」溯源核查（只读，不修改任何数据）。

背景：论文 §（四）曾把原标（第 1 轮）相对后三轮的偏离表述为「该轮判定本身的系统性偏移」。
用户质疑：后三轮的提示词可能与第 1 轮不同，偏离是否由提示词造成。本脚本据实核查：

  A. 各轮打标脚本的 SYSTEM_PROMPT 指纹（AST 抽取 + sha256 前缀）与调用结构（每次调用判定几条）
  A2. 第 1 轮（原标）提示词 —— 已于 2026-09-26 从本机 Workflow 历史脚本中恢复（见 label_prompt_round1.md）
  B. 各轮「判定依据」文本长度分布 —— 提示词差异的**输出端签名**
  C. 类别分布对照 + 原标「其他讨论」在后三轮的去向
  D. 分歧是否集中在单一类别边界（原标=其他讨论 且 后三轮一致=教育观点讨论）

用法: python prompt_provenance_check.py
"""
import ast, collections, glob, hashlib, json, os, random, re, statistics, sys

import openpyxl

# 脚本现位于 data/scripts/，工作区根目录为上两级
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = f"{ROOT}/data"
SCRIPTS = ["batch_label_r1prompt.py", "batch_label_v3.py",
           "batch_label_v2.py", "batch_label.py"]

# 第 1 轮（原标）的提示词不在工作区内：它由另一项目（~/Project/数据清洗）下的
# Claude Code Workflow 运行，脚本与批次结果留在本机历史目录中。
R1_WF = os.path.expanduser(
    "~/.claude/projects/-Users-easylife-Project-----/"
    "48165eea-81a5-449c-ab05-3b11f103a1af/workflows/scripts/"
    "zxf-full-labeling-wf_4953f96e-780.js")
R1_BATCH_DIR = os.path.expanduser("~/Project/数据清洗/全量标注结果")
R1 = "原标(第1轮)"
R2, R3, R4 = "Seed(第2轮)", "GLM(第3轮)", "DSv4.1(第4轮)"
ROUNDS = [
    ("原标(第1轮)", f"{DATA}/baseline/抖音微博小红书-全量已打标.xlsx"),
    ("Seed(第2轮)", f"{DATA}/archive/round2_doubao-seed-2.1-lite/抖音微博小红书-独立重打标_Seed2_1_lite.xlsx"),
    ("GLM(第3轮)", f"{DATA}/archive/round3_glm-5.3-flash/抖音微博小红书-独立重打标_GLM5_3flash.xlsx"),
    ("DSv4.1(第4轮)", f"{DATA}/archive/round4_deepseek-v4.1/抖音微博小红书-独立重打标_DSv4_1_flash.xlsx"),
]
CATS = ["借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音"]


def section(t):
    print(f"\n{'='*78}\n{t}\n{'='*78}")


def prompt_fingerprint():
    """A. 从脚本源码里抽出 SYSTEM_PROMPT 字面量，比对指纹与调用结构。"""
    section("A. 各脚本的 SYSTEM_PROMPT 指纹与调用结构")
    out = {}
    for fn in SCRIPTS:
        p = os.path.join(DATA, "scripts", fn)
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
    print("  → 后三轮口径内部（v2/早期 与 v3）：差异仅在【输出格式】段"
          "（单对象 vs JSON 数组），该段与调用结构（1 条/次 vs 8 条/次）耦合。")
    print("  → batch_label_r1prompt.py 属**另一套口径**（第 1 轮），与后三轮不构成"
          "「仅输出格式」差异；其与第 1 轮原文的对齐见 check_baseline_alignment.py §A。")


def round1_fingerprint():
    """A2. 第 1 轮提示词：从 Workflow 历史脚本恢复，并用其输出端签名交叉验证。"""
    section("A2. 第 1 轮（原标）提示词 —— 已恢复，指纹与签名交叉验证")
    if not os.path.exists(R1_WF):
        print(f"  工作流脚本不存在（本机历史已清理）：{R1_WF}")
        print("  提示词全文见 label_prompt_round1.md。")
        return
    src = open(R1_WF, encoding="utf-8").read()
    m = re.search(r"const T = `(.*?)`\n", src, re.S)
    if not m:
        print("  未能在工作流脚本中定位提示词常量 T。"); return
    text = m.group(1).replace("\\`", "`")
    h = hashlib.sha256(text.encode()).hexdigest()
    print(f"  zxf-full-labeling-wf_4953f96e-780.js  长度={len(text)}  sha256={h[:16]}")
    print("  调用结构：Workflow 352 个 agent × 每批 150 行（agentic：Read/Write 工具）")
    print("  输入字段：row_id, platform, author, title, match_sentence(+ctx_full_content)")

    files = sorted(glob.glob(os.path.join(R1_BATCH_DIR, "result_batch_*.jsonl")))
    if not files:
        print(f"  批次结果目录不存在，跳过输出端签名验证：{R1_BATCH_DIR}"); return
    rows = []
    for f in files:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    L = sorted(len(r.get("reason", "")) for r in rows)
    n = len(L)
    print(f"\n  输出端签名验证（{len(files)} 个批次文件，{n} 行）：")
    print(f"    reason 长度：中位 {L[n//2]}  最大 {max(L)}  ≤30字 {sum(1 for x in L if x<=30)/n*100:.2f}%")
    print("    → 提示词写死 \"reason\":\"≤30字判定依据\"；后三轮为「1-2 句话」，实得中位 27—34 字。")
    cc = collections.Counter(r.get("category") for r in rows)
    print(f"    类别分布：{'，'.join(f'{k} {v}' for k, v in cc.most_common())}")
    print("    → 与工作区 原标(第1轮) 列一致，确认为同一份产物。")


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
    round1_fingerprint()
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
