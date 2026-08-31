# 张雪峰梗词判定器 —— 依据《张雪峰梗词判定规则(完整版)》实现
# 三方共用尺子之一: env 供给标注（is_meme 元数据）
# 逻辑: 归一化(去emoji/标点/空格) → ①联动人名(原文本+归一化两层,出现即玩梗)
#       → ②排除死亡事实陈述后,强梗词库两层匹配 → 都不命中=非玩梗
#       高召回口径(用户已接受误伤); 弱关联词仅作话题标记不触发
import re
import json
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent

LINKAGE = ["牢大", "科比", "五条悟", "牢师", "良子", "火车头", "墨茶", "冬雪莲", "霍金",
           "seeyouagain", "夜之城没有活着的传奇", "三圣跳舞", "truemusic"]

STRONG = [
    # 三大件
    "巧乐兹", "雪碧", "跑步机",
    # 戏谑称号
    "牢峰", "牢张", "牢雪", "张圣", "巧乐兹战神", "雪碧超人", "跑步机狂魔",
    "考研神嘴", "寒门引路人", "地狱梗圣体",
    # 组合/套餐
    "雪人三项", "雪峰上岸套餐", "考研套餐", "双生武魂", "雪峰铠甲合体",
    "巧乐兹雪碧冰红茶三合一", "圣遗物", "赛博永生核心装备", "张雪峰套餐",
    # 经典语录/回旋镖（归一化后子串匹配）
    "你跑不过我你信吗", "你跑不过我", "跑到没我快信吗", "你跑到没我快",
    "强者是不会死的", "我的人生目标就是死了上热搜", "若让我挑选死法",
    "千万别把我救过来", "我终于能休息了", "我提前为自己写好了墓志铭",
    "下辈子还来", "我或许会成为一代人的记忆", "我希望是不久之后",
    "买不起房就是因为不努力", "买得起房的都不会抱怨房价太高",
    "狗死了是它的命", "人拉稀了没事", "44岁在跑步机猝死那个事儿",
    "三口一个巧乐兹", "生产队的驴", "你没成功就是因为你不够努力",
    # 数字/战绩
    "9/1/0", "0/9/1", "1/0/0", "跑完100公里", "10分钟6根", "一场直播9根", "一口气冰雪碧",
    # BGM/二创
    "念张师", "忆张师", "鬼畜", "蓝底半身照", "红眼特效", "同人小说",
    # 高频句式/衍生
    "赛博永生", "地狱梗", "社达", "社会达尔文主义", "回旋镖", "逝者保护期",
    "造神与毁神", "内卷祛魅", "死后成梗", "死后更火", "buff叠满", "透心凉心飞扬",
    "头七都没挺过去", "上柱香", "演算法捕捉到了我", "拼命三郎", "头像变灰",
    "社达言论", "社达代言人", "弱肉强食", "适者生存", "一口先敬张老师",
    # 数据反挖补充（高召回偏收）
    "汽水", "雪糕", "饮料", "瓶雪碧", "碧巧", "研套餐", "套餐", "一根巧",
    "峰雪糕", "滋雪糕", "野生代言人", "雪人", "铁人三项", "雪山",
    "跑步猝死", "根巧", "格聂", "一根雪糕解决不了",
]

EXCLUDE_DEATH_FACT = [
    "心源性猝死", "心原性猝死", "心脏性猝死", "心搏骤停", "心脏骤停", "心肌梗死",
    "心源性休克", "心梗", "突然去世", "突然走了", "突然没了", "突然离世",
    "突发心脏病", "跑步机猝死", "跑步后猝死", "心源猝死", "猝死", "抢救3小时",
]

WEAK_MARKERS = ["悼念", "缅怀", "一路走好", "健身", "跑步锻炼", "嘴唇发紫"]

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
