# build_assets.py — 构建 CurationDynamicsSpace 的两个数据资产
# 1) vocabs.json        : 四类型词表机器可读版（四份 词表_*_最终版.md 为唯一词源；
#                         meme_matcher.py 已改为从 vocabs.json 加载，保持同尺同源）
# 2) injection_posts.json : 真实打标数据周切片（供 env 每周抽样注入）
# 3) --validate          : 用判类器回测全量人工标签，输出混淆矩阵（质量门）
#
# 用法: python build_assets.py [--validate]
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]  # 工作区根目录
OUT = Path(__file__).resolve().parent

VOCAB_MD = {
    "mourning": ROOT / "词表_哀悼型_最终版.md",
    "education": ROOT / "词表_教育型_最终版.md",
    "marketing": ROOT / "词表_营销型_最终版.md",
}
MEME_MD = ROOT / "词表_玩梗型_最终版.md"
XLSX = ROOT / "抖音微博小红书-全量已打标.xlsx"

# 判定优先级（三词表文档一致声明）
PRECEDENCE = ["mourning", "marketing", "education", "meme"]

# 哀悼上下文词：单独出现不判悼念，仅辅助标记（词表_哀悼型 §十一 + meme_matcher EXCLUDE_DEATH_FACT）
MOURNING_CONTEXT_AUX = [
    "猝死", "心源性猝死", "心原性猝死", "心脏性猝死", "心搏骤停", "心脏骤停",
    "心肌梗死", "心源性休克", "心梗", "心源猝死", "抢救3小时", "健康", "身体", "心脏",
    "突然去世", "突然走了", "突然没了", "突然离世", "突发心脏病", "跑步机猝死", "跑步后猝死",
]

# 教育遗产消费次类标记（词表_教育型 §七，表格内容，手工转录）
EDU_LEGACY_MARKERS = [
    "张雪峰说", "张老师忠告", "语录", "曾经说过", "生前", "留下", "提醒",
    "搬运", "搬运历史视频", "评价教育贡献",
]

# 玩梗 §五：弱关联话题标记（非玩梗，不触发判类，仅审计）
MEME_WEAK_MARKERS = ["悼念", "缅怀", "一路走好", "健身", "跑步锻炼", "嘴唇发紫"]
# 玩梗 §五：正常称呼人名（提人名=讨论非玩梗）及其全拼/拼音缩写（匹配统一小写比较）。
# 谐音梗（张雪封/张雪峯等）与 §五 保留例外不在扣减之列。
MEME_PERSONA_NAMES = {
    "张雪峰", "张老师", "张师", "张总", "雪峰老师", "雪峰哥", "峰哥",
    "老张", "老峰", "老雪", "张生", "张胜",
    "zhangxuefeng", "zhangsheng", "zxf", "张seng", "张sheng",
}

# 判类所需各文件的主库章节（中文数字章节号）
MAIN_SECTIONS = {
    "mourning": ["一", "二", "三", "四", "五", "六"],
    "education": ["一", "二", "三", "四", "五"],
    "marketing": ["一", "二", "三", "四", "五", "六", "七"],
}
AUX_SECTIONS = {  # 辅助标记（不单独触发判类）
    "education": ["六"],
    "marketing": ["八"],
}

CN_NUM = "一二三四五六七八九十十一"


def parse_sections(md_path: Path) -> dict[str, list[str]]:
    """把词表 md 按 '## 一、' 章节切分，抽取顿号分隔词表（跳过表格/引用/标题行）。"""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+([一二三四五六七八九十]+)、", line.strip())
        if m:
            current = m.group(1)
            sections.setdefault(current, [])
            continue
        if line.startswith("#"):
            current = current  # 其他标题不改变当前章节
        if current is None:
            continue
        s = line.strip()
        if not s or s.startswith((">", "|", "#", "-", "```", "---")):
            continue
        for tok in re.split(r"[、，,]", s):
            w = tok.strip().strip("。").strip()
            w = w.strip("*").strip()
            if w and len(w) <= 40:
                sections[current].append(w)
    return sections


def dedup_keep_order(words: list[str]) -> list[str]:
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def extract_meme_lists() -> dict[str, list[str]]:
    """解析 词表_玩梗型_最终版.md（梗热词全量表，唯一词源）：
    §一 强梗词主库→strong、§二 联动人名→linkage、§三 慎用数字→cautious_numbers（不进判类）、
    §四 已排除词→exclude_death_fact；§五 的弱关联标记与正常称呼人名按硬编码口径扣减。

    对 §一 枚举做四处机械扣减（均记录在 dropped 字段，供审计）：
    1) weak_markers 交集（§五：话题标记非玩梗，不触发判类）；
    2) §三 慎用数字原文（§三：不收入主库，新闻事实陈述误伤；§一中重出的以 §三 为准）；
    3) len<=1（单字子串噪声，与三类主库同一弃用规则）；
    4) §五 正常称呼人名及其全拼/拼音缩写（提人名=讨论非玩梗）；
      谐音梗（张雪封/张雪峯等）与 §五 保留例外（张雪峰死了/张雪峰套餐、张圣、念/忆张师、
      牢峰/牢张/牢雪）均不在扣减之列。
    """
    secs = parse_sections(MEME_MD)
    missing = [s for s in ("一", "二", "三", "四") if s not in secs]
    if missing:
        raise RuntimeError(f"词表_玩梗型_最终版.md 缺少章节: {missing}")
    cautious = set(secs["三"])
    enumerated = dedup_keep_order(secs["一"])
    dropped = {
        "weak_markers_overlap": [w for w in enumerated if w in MEME_WEAK_MARKERS],
        "cautious_numbers": [w for w in enumerated if w in cautious],
        "persona_names": [w for w in enumerated if w.lower() in MEME_PERSONA_NAMES],
        "single_char": [w for w in enumerated if len(w) <= 1],
    }
    strong = [w for w in enumerated
              if w not in MEME_WEAK_MARKERS
              and w not in cautious
              and w.lower() not in MEME_PERSONA_NAMES
              and len(w) > 1]
    return {
        "linkage": dedup_keep_order(secs["二"]),
        "strong": strong,
        "exclude_death_fact": dedup_keep_order(secs["四"]),
        "weak_markers": list(MEME_WEAK_MARKERS),
        "cautious_numbers": sorted(cautious),  # 审计用，不参与判类（§三：靠 LLM 辅助判定）
        "dropped": dropped,                    # §一 扣减记录，供审计
    }


def build_vocabs() -> dict:
    vocabs: dict = {"version": "2026-09-10-meme-full",
                    "precedence": PRECEDENCE,
                    "residual": "other",
                    "sources": {"mourning": "词表_哀悼型_最终版.md",
                                "education": "词表_教育型_最终版.md",
                                "marketing": "词表_营销型_最终版.md",
                                "meme": "词表_玩梗型_最终版.md（梗热词全量表 967 词版）"},
                    "matching": "two layers: raw.lower() + normalized (strip emoji/punct/space/underscore, keep CJK+alnum, lowercase); substring match"}
    stats = {}
    for cat, md in VOCAB_MD.items():
        secs = parse_sections(md)
        main: list[str] = []
        for sec in MAIN_SECTIONS[cat]:
            main.extend(secs.get(sec, []))
        aux: list[str] = []
        for sec in AUX_SECTIONS.get(cat, []):
            aux.extend(secs.get(sec, []))
        main = dedup_keep_order(main)
        aux = dedup_keep_order(aux)
        entry: dict = {"main": main}
        if aux:
            entry["aux"] = aux
        if cat == "mourning":
            # 上下文词从主库剔除，仅作辅助标记（词表文档：is_mourning = hit_mourning，上下文词不触发）
            ctx = set(MOURNING_CONTEXT_AUX)
            entry["context_aux"] = sorted(ctx & set(main)) + [w for w in MOURNING_CONTEXT_AUX if w not in set(main)]
            entry["main"] = [w for w in main if w not in ctx]
        if cat == "education":
            entry["legacy_markers"] = EDU_LEGACY_MARKERS
        vocabs[cat] = entry
        stats[cat] = {k: len(v) for k, v in entry.items()}
    vocabs["meme"] = extract_meme_lists()
    stats["meme"] = {k: len(v) for k, v in vocabs["meme"].items()}
    vocabs["stats"] = stats
    return vocabs


# ---------------- 数据驱动剪枝 ----------------
#
# 规则（2026-09-09 实验比选 A/B/C/D/E/F 后裁定，见 vocabs.json pruning 元信息）：
# - 三类主库统一：词的条件有效精确度 < 0.3 且条件命中数 >= 30 → 移入 pruned 列表（不再触发判类）。
#   “条件” = 按判定优先级顺序，排除已被更高优先级类别（剪枝后）命中的帖子；
#   条件精确度 = P(金标==本类 | 词命中且未被高优先类截获)。
# - 单字词一律弃用（子串匹配下噪声过大，如 新/沸）。
# - 梗词表（meme_matcher.py 同源）不剪：已验证的参考实现。
# 关键实证：
# - 金标悼念帖 66.7% 命中营销主库词、金标营销帖 72.6% 命中悼念主库词 —— 真实帖框架混合，
#   单词匹配存在天花板（总体一致率 ~0.44）；LLM agent 帖为人设刻板单框架文本，实际判类优于回测。
# - “营销前置”实验（F）：mourning 召回 0.903→0.337，一致率仅 +0.005，否决——
#   保持文档规定的 悼念>营销>教育>玩梗 优先级。
# - 教育召回低（~0.05）是“宽口径营销优先”的结构性后果（教育帖大量命中营销词），非 bug。
PRUNE_MIN_HITS = 30
PRUNE_MIN_PRECISION = 0.3
PRUNE_ORDER = ["mourning", "marketing", "education"]  # = PRECEDENCE[:-1]


def _hit_matrix(words: list[str], raw_l: np.ndarray, nrm: np.ndarray) -> np.ndarray:
    """n_posts × n_words 布尔矩阵：两层（原文 lower + 归一化）子串命中。"""
    cols = []
    for w in words:
        wl = w.lower()
        cols.append(np.array([(wl in r) or (wl in s) for r, s in zip(raw_l, nrm)]))
    if not cols:
        return np.zeros((len(raw_l), 0), dtype=bool)
    return np.column_stack(cols)


def precision_prune(vocabs: dict) -> dict:
    """按 PRUNE_ORDER 顺序做条件精确度剪枝，结果写回 vocabs（main 缩减 + pruned 记录）。"""
    df = pd.read_excel(XLSX)
    df = df[df["数据有效性"] != "存疑"].copy()
    content = (df["title"].fillna("") + "\n" + df["content"].fillna("")).str.strip()
    gold = df["内容类别"].map(TYPE_MAP).to_numpy()
    raw_l = content.str.lower().to_numpy()
    nrm = content.map(normalize).to_numpy()
    higher = np.zeros(len(df), dtype=bool)
    summary = {}
    for cat in PRUNE_ORDER:
        words = vocabs[cat]["main"]
        single = [w for w in words if len(w) <= 1]
        words = [w for w in words if len(w) > 1]
        M = _hit_matrix(words, raw_l, nrm)
        ch = M & (~higher)[:, None]
        hits = ch.sum(0)
        good = ((gold == cat)[:, None] & ch).sum(0)
        prec = np.where(hits > 0, good / np.maximum(hits, 1), 1.0)
        keep = (hits < PRUNE_MIN_HITS) | (prec >= PRUNE_MIN_PRECISION)
        pruned = [{"word": w, "cond_hits": int(h), "cond_precision": round(float(p), 3)}
                  for w, h, p, k in zip(words, hits, prec, keep) if not k]
        entry = vocabs[cat]
        entry["main"] = [w for w, k in zip(words, keep) if k]
        if single:
            entry["dropped_single_char"] = single
        entry["pruned"] = pruned
        higher = higher | (M[:, keep]).any(1)
        summary[cat] = {"kept": int(keep.sum()), "pruned": len(pruned), "single_char_dropped": len(single)}
        print(f"剪枝 {cat}: 保留 {keep.sum()} / 剪 {len(pruned)} / 弃单字 {len(single)}")
    vocabs["pruning"] = {
        "rule": f"cond_precision < {PRUNE_MIN_PRECISION} and cond_hits >= {PRUNE_MIN_HITS} -> pruned; "
                f"len<=1 -> dropped_single_char; 条件=未被更高优先级类别(剪枝后)命中",
        "gold_source": f"{XLSX.name} 内容类别列(剔除存疑, n={len(df)})",
        "summary": summary,
        "notes": "营销前置实验被否决(mourning召回0.903→0.337)；教育低召回=宽口径营销优先的结构性后果;"
                 "真实帖框架混合致单词匹配天花板~0.44，agent帖判类优于回测",
    }
    return vocabs


# ---------------- 判类器（与 env _tag_content_type 同逻辑，供回测） ----------------

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️‍]")


def normalize(s: str) -> str:
    s = _EMOJI.sub("", str(s))
    return re.sub(r"[\W_]+", "", s).lower()


class Tagger:
    def __init__(self, vocabs: dict):
        self.v = vocabs

    def _hits(self, words: list[str], layers: list[str]) -> list[str]:
        return [w for w in words if any(w.lower() in l for l in layers)]

    def tag(self, text: str) -> dict:
        raw = str(text)
        nrm = normalize(raw)
        layers = [raw.lower(), nrm]
        v = self.v
        hit_m = self._hits(v["mourning"]["main"], layers)
        hit_mk = self._hits(v["marketing"]["main"], layers)
        hit_ed = self._hits(v["education"]["main"], layers)
        # meme: linkage → strong (after death-fact strip)
        hit_link = self._hits(v["meme"]["linkage"], layers)
        stripped = [raw.lower(), nrm]
        for w in v["meme"]["exclude_death_fact"]:
            stripped = [s.replace(w.lower(), "□") for s in stripped]
        hit_strong = [w for w in v["meme"]["strong"] if any(w.lower() in l for l in stripped)]
        is_meme = bool(hit_link or hit_strong)
        main = "other"
        if hit_m:
            main = "mourning"
        elif hit_mk:
            main = "marketing"
        elif hit_ed:
            main = "education"
        elif is_meme:
            main = "meme"
        return {"type": main,
                "is_meme_signal": is_meme,
                "hits": {"mourning": hit_m[:5], "marketing": hit_mk[:5],
                         "education": hit_ed[:5], "meme": (hit_link + hit_strong)[:5]}}


# ---------------- 注入数据 ----------------

TYPE_MAP = {"借势营销": "marketing", "事件悼念讨论": "mourning", "其他讨论": "other",
            "教育观点讨论": "education", "梗文化讨论": "meme", "爬取噪音": "noise"}

OFFICIAL_KEYWORDS = ["讣告", "官方确认", "公司声明", "家属声明"]


def build_injection() -> dict:
    df = pd.read_excel(XLSX)
    print(f"xlsx 行数: {len(df)}; 数据有效性取值: {df['数据有效性'].value_counts().to_dict()}")
    # 数据有效性标记的语义（已核实）："无效"=借势营销+爬取噪音（非真实讨论标记），"存疑"=20 行剔除项。
    # benchmark 周矩阵口径 = 剔除存疑后的全部 52,716 行（含营销/噪音），注入数据必须同口径。
    df = df[df["数据有效性"] != "存疑"].copy()
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    iso = df["published_at"].dt.isocalendar()
    df["week"] = [f"{y}-W{w:02d}" for y, w in zip(iso["year"], iso["week"])]
    df["type"] = df["内容类别"].map(TYPE_MAP)
    assert df["type"].notna().all(), df[df["type"].isna()]["内容类别"].unique()
    content = (df["title"].fillna("") + "\n" + df["content"].fillna("")).str.strip().str[:1000]
    posts = []
    for i, (_, r) in enumerate(df.iterrows()):
        c = content.iloc[i]
        posts.append({
            "pid": int(i),
            "week": r["week"],
            "type": r["type"],
            "content": c,
            "author": str(r["author_handle"]) if pd.notna(r["author_handle"]) else "unknown",
            "is_official": any(k in c for k in OFFICIAL_KEYWORDS),
            "published_at": r["published_at"].isoformat(),
        })
    weeks = df.groupby("week").size().to_dict()
    off = df.assign(c=content.values)
    off_cnt = off[off["c"].apply(lambda c: any(k in c for k in OFFICIAL_KEYWORDS))].groupby("week").size().to_dict()
    meta = {"source": XLSX.name, "rows_total": len(df),
            "filter": "剔除数据有效性=='存疑'(20行)；'无效'标记=营销+噪音,属真实供给组成部分,保留",
            "weekly_counts": weeks,
            "official_counts": off_cnt,
            "official_keywords": OFFICIAL_KEYWORDS,
            "note": "content=title+content 截断1000字; is_official 为关键词预标(讣告/官方确认/公司声明/家属声明),可在 config 覆盖"}
    # 硬性校验：周总量必须与 benchmark_curves.json weekly_category_matrix 完全一致
    bm = json.loads((ROOT / "hypothesis_4/benchmark_curves.json").read_text(encoding="utf-8"))
    bm_weeks = {w: v["total"] for w, v in bm["weekly_category_matrix"].items()}
    mismatches = {w: (weeks.get(w, 0), bm_weeks[w]) for w in bm_weeks if weeks.get(w, 0) != bm_weeks[w]}
    if mismatches:
        raise RuntimeError(f"周总量与 benchmark 不一致: {mismatches}")
    print("周总量与 benchmark_curves.json 逐周一致 ✓")
    return {"meta": meta, "posts": posts}


def validate(vocabs: dict) -> dict:
    df = pd.read_excel(XLSX)
    df = df[df["数据有效性"] != "存疑"].copy()
    content = (df["title"].fillna("") + "\n" + df["content"].fillna("")).str.strip()
    tagger = Tagger(vocabs)
    pred = content.map(lambda c: tagger.tag(c)["type"])
    gold = df["内容类别"].map(TYPE_MAP)
    ct = pd.crosstab(gold, pred, rownames=["gold"], colnames=["pred"], dropna=False)
    print("\n=== 判类器回测（gold=人工标签, pred=词表判类）===")
    print(ct.to_string())
    agree = (gold == pred).mean()
    print(f"\n总体一致率: {agree:.3f}")
    metrics = {"overall_agreement": round(float(agree), 3),
               "confusion": {str(g): {str(p): int(ct.loc[g, p]) for p in ct.columns}
                             for g in ct.index}}
    for t in ["mourning", "meme", "education", "marketing"]:
        mask = gold == t
        rec = (pred[mask] == t).mean() if mask.any() else float("nan")
        pmask = pred == t
        prec = (gold[pmask] == t).mean() if pmask.any() else float("nan")
        metrics[t] = {"recall": round(float(rec), 3), "precision": round(float(prec), 3),
                      "n_gold": int(mask.sum())}
        print(f"  {t}: 召回 = {rec:.3f} | 精确 = {prec:.3f} (n={int(mask.sum())})")
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="回测判类器对人工标签的一致率")
    ap.add_argument("--no-prune", action="store_true", help="关闭数据驱动剪枝（消融用）")
    args = ap.parse_args()

    vocabs = build_vocabs()
    if not args.no_prune:
        precision_prune(vocabs)
    vocabs["stats"] = {cat: {k: len(v) for k, v in vocabs[cat].items()}
                       for cat in ["mourning", "education", "marketing", "meme"]}

    inj = build_injection()
    (OUT / "injection_posts.json").write_text(
        json.dumps(inj, ensure_ascii=False), encoding="utf-8")
    print(f"injection_posts.json 写出。总行数 {inj['meta']['rows_total']}, "
          f"周分布 {inj['meta']['weekly_counts']}")
    print(f"官方帖预标: {inj['meta']['official_counts']}")

    if args.validate:
        vocabs["backtest"] = validate(vocabs)

    (OUT / "vocabs.json").write_text(
        json.dumps(vocabs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vocabs.json 写出。各类规模:", json.dumps(vocabs["stats"], ensure_ascii=False))


if __name__ == "__main__":
    main()
