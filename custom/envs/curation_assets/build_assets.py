# build_assets.py — 构建 CurationDynamicsSpace 的两个数据资产
# 1) vocabs.json        : 四类型词表机器可读版（与 词表_*_最终版.md / meme_matcher.py 同尺）
# 2) injection_posts.json : 真实打标数据周切片（供 env 每周抽样注入）
# 3) --validate          : 用判类器回测全量人工标签，输出混淆矩阵（质量门）
#
# 用法: python build_assets.py [--validate]
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]  # 工作区根目录
OUT = Path(__file__).resolve().parent

VOCAB_MD = {
    "mourning": ROOT / "词表_哀悼型_最终版.md",
    "education": ROOT / "词表_教育型_最终版.md",
    "marketing": ROOT / "词表_营销型_最终版.md",
}
MEME_MATCHER = ROOT / "datasets/zhangxf_labeled/meme_matcher.py"
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
    """用 AST 从 meme_matcher.py 抽取列表字面量（不执行模块代码）。"""
    tree = ast.parse(MEME_MATCHER.read_text(encoding="utf-8"))
    wanted = {"LINKAGE": "linkage", "STRONG": "strong",
              "EXCLUDE_DEATH_FACT": "exclude_death_fact", "WEAK_MARKERS": "weak_markers"}
    out: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            name = getattr(node.targets[0], "id", None)
            if name in wanted:
                out[wanted[name]] = [el.value for el in node.value.elts
                                     if isinstance(el, ast.Constant) and isinstance(el.value, str)]
    missing = set(wanted.values()) - set(out)
    if missing:
        raise RuntimeError(f"meme_matcher.py 列表抽取失败: {missing}")
    return out


def build_vocabs() -> dict:
    vocabs: dict = {"version": "2026-09-08-final",
                    "precedence": PRECEDENCE,
                    "residual": "other",
                    "sources": {"mourning": "词表_哀悼型_最终版.md",
                                "education": "词表_教育型_最终版.md",
                                "marketing": "词表_营销型_最终版.md",
                                "meme": "词表_玩梗型_最终版.md + meme_matcher.py"},
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
    df = df[df["数据有效性"] == "有效"].copy()
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
    meta = {"source": XLSX.name, "rows_valid": len(df), "weekly_counts": weeks,
            "official_counts": off_cnt,
            "official_keywords": OFFICIAL_KEYWORDS,
            "note": "content=title+content 截断1000字; is_official 为关键词预标(讣告/官方确认/公司声明/家属声明),可在 config 覆盖"}
    return {"meta": meta, "posts": posts}


def validate(vocabs: dict) -> None:
    df = pd.read_excel(XLSX)
    df = df[df["数据有效性"] == "有效"].copy()
    content = (df["title"].fillna("") + "\n" + df["content"].fillna("")).str.strip()
    tagger = Tagger(vocabs)
    pred = content.map(lambda c: tagger.tag(c)["type"])
    gold = df["内容类别"].map(TYPE_MAP)
    ct = pd.crosstab(gold, pred, rownames=["gold"], colnames=["pred"], dropna=False)
    print("\n=== 判类器回测（gold=人工标签, pred=词表判类）===")
    print(ct.to_string())
    agree = (gold == pred).mean()
    print(f"\n总体一致率: {agree:.3f}")
    for t in ["mourning", "meme", "education", "marketing"]:
        mask = gold == t
        rec = (pred[mask] == t).mean() if mask.any() else float("nan")
        print(f"  {t}: 召回(金标→判类) = {rec:.3f} (n={int(mask.sum())})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="回测判类器对人工标签的一致率")
    args = ap.parse_args()

    vocabs = build_vocabs()
    (OUT / "vocabs.json").write_text(
        json.dumps(vocabs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vocabs.json 写出。各类规模:", json.dumps(vocabs["stats"], ensure_ascii=False))

    inj = build_injection()
    (OUT / "injection_posts.json").write_text(
        json.dumps(inj, ensure_ascii=False), encoding="utf-8")
    print(f"injection_posts.json 写出。有效行 {inj['meta']['rows_valid']}, "
          f"周分布 {inj['meta']['weekly_counts']}")
    print(f"官方帖预标: {inj['meta']['official_counts']}")

    if args.validate:
        validate(vocabs)


if __name__ == "__main__":
    main()
