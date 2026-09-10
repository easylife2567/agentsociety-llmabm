# 张雪峰梗词判定器 —— 词表唯一词源为 词表_玩梗型_最终版.md（梗热词全量表），
# 经 custom/envs/curation_assets/build_assets.py 编译进 vocabs.json 后在此加载，
# 与 env 判类器（CurationDynamicsSpace）同尺同源，避免双源漂移。
# 逻辑: 归一化(去emoji/标点/空格) → ①联动人名(原文本+归一化两层,出现即玩梗)
#       → ②排除死亡事实陈述后,强梗词库两层匹配 → 都不命中=非玩梗
#       高召回口径(用户已接受误伤); 弱关联词仅作话题标记不触发
import re
import json
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
_VOCAB_PATH = Path(__file__).resolve().parents[2] / "custom/envs/curation_assets/vocabs.json"
_MEME = json.loads(_VOCAB_PATH.read_text(encoding="utf-8"))["meme"]

LINKAGE: list[str] = list(_MEME["linkage"])
STRONG: list[str] = list(_MEME["strong"])
EXCLUDE_DEATH_FACT: list[str] = list(_MEME["exclude_death_fact"])
WEAK_MARKERS: list[str] = list(_MEME["weak_markers"])

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️‍]")


def normalize(s: str) -> str:
    s = _EMOJI.sub("", str(s))
    # \W 保留 CJK+字母数字，去除标点/空白/符号；下划线一并去除
    return re.sub(r"[\W_]+", "", s).lower()


def match(text: str) -> dict:
    raw = str(text)
    nrm = normalize(raw)
    layers = [raw.lower(), nrm]

    hit_linkage = [w for w in LINKAGE if any(w in l for l in layers)]

    stripped = [raw, nrm]
    for w in EXCLUDE_DEATH_FACT:
        stripped = [s.replace(w, "□") for s in stripped]
    hit_strong = [w for w in STRONG
                  if any(w in l for l in [stripped[0].lower(), stripped[1]])]
    hit_weak = [w for w in WEAK_MARKERS if any(w in l for l in layers)]

    meme_words = hit_linkage + [w for w in hit_strong if w not in hit_linkage]
    return {"is_meme": bool(meme_words), "meme_words": meme_words, "weak_words": hit_weak}


def main() -> None:
    df = pd.read_parquet(OUT / "valid_posts_clusters.parquet")
    res = df["content"].map(match).apply(pd.Series)
    df["is_meme"] = res["is_meme"]
    df["meme_words"] = res["meme_words"]
    df["weak_words"] = res["weak_words"]
    df.to_parquet(OUT / "valid_posts_clusters.parquet", index=False)

    full = pd.read_excel("/Users/easylife/Project/AgentSociety/抖音微博小红书-全量已打标.xlsx")
    val = full[full["数据有效性"] == "有效"].copy()
    val["published_at"] = pd.to_datetime(val["published_at"], utc=True)
    r = val["content"].map(match).apply(pd.Series)
    val["is_meme"] = r["is_meme"]
    val["published_day"] = val["published_at"].dt.date

    prof = json.loads((OUT / "cluster_profiles.json").read_text(encoding="utf-8"))
    rates = {}
    for c, g in df.groupby("k"):
        theme = prof[str(c)]["theme"] if str(c) in prof else prof[c]["theme"]
        rates[theme] = {
            "meme_rate_unique": round(float(g["is_meme"].mean()), 3),
            "top_meme_words": pd.Series([w for ws in g["meme_words"] for w in ws])
            .value_counts().head(6).to_dict() if g["is_meme"].any() else {},
        }
    daily_meme = val.groupby("published_day")["is_meme"].mean().round(3)
    window = daily_meme.loc[pd.Timestamp("2026-03-23").date():pd.Timestamp("2026-04-05").date()]
    stats = {
        "overall_meme_rate_valid": round(float(val["is_meme"].mean()), 3),
        "meme_rate_by_theme": rates,
        "daily_meme_share_0323_0405": {str(k): v for k, v in window.items()},
    }
    (OUT / "meme_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    print("总体玩梗率(有效):", stats["overall_meme_rate_valid"])
    for t, v in rates.items():
        print(f"  {t}: {v['meme_rate_unique']}")
    print("死亡日前后每日玩梗供给占比:")
    for d, v in window.items():
        print(f"  {d}: {v}")


if __name__ == "__main__":
    main()
