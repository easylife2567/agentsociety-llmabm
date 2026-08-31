# 对打标数据的有效内容做主题聚类，产出供给主题画像（供 LLMABM 配置使用）
# 输入: 抖音微博小红书-全量已打标.xlsx（工作区根目录，用户提供）
# 输出: valid_posts_clusters.parquet / cluster_profiles.json
# 方法: jieba 分词 → TF-IDF(1-2gram) → LSA(100) → MiniBatchKMeans(k=12, 固定种子)
#       后处理: C3+C6 合并为「巧乐兹雪碧梗」（同梗分裂，文本多样性极低）;
#               C10/C11 标记 noise（小红书话题模板残留 / 评论区抓取残留）
import hashlib
import json
import re
import warnings
from pathlib import Path

import jieba
import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "抖音微博小红书-全量已打标.xlsx"
OUT = Path(__file__).resolve().parent

K = 12
RANDOM_STATE = 42
# k=12 的簇号 → 主题名（依据簇画像人工命名，见 CLUSTERS.md）
THEME_NAMES = {
    0: "人生语录",        # 张雪峰语录（健康/生命/人生），小红书为主
    1: "死因健康科普",    # 猝死/AED/心源性
    2: "学习方法观点",    # 小学筛选家长等
    3: "巧乐兹雪碧梗",    # 抖音 97%，广告梗
    4: "公司接班后事",    # 峰学蔚来/武亮
    5: "泛议论杂谈",      # 观点杂谈大簇
    6: "巧乐兹雪碧梗",    # 同 C3，合并
    7: "家庭教育观点",    # N 情感 34%（争议性最高）
    8: "志愿填报干货",    # 专业/就业/高考
    9: "悼念颂扬",        # 张老师/寒门/一路走好
}
NOISE_CLUSTERS = {10: "小红书话题模板噪音", 11: "评论抓取残留噪音"}

STOP = set("的了和是就都而及与著或一个没有我们你们他们自己这个那个什么怎么因为所以但是如果虽然然而因此于是真的还是就是已经觉得可以可能这样那样开始问题现在时候知道东西地方".split())


def tokenize(s: str) -> str:
    s = re.sub(r"https?://\S+|[@#]", " ", str(s))
    ws = [w for w in jieba.cut(s)
          if len(w) > 1 and w not in STOP
          and not re.fullmatch(r"[\d\s\W]+", w)
          and not re.fullmatch(r"[a-zA-Z]+", w)]
    return " ".join(ws)


def gini(x) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    return float(2 * ((np.arange(1, n + 1) * x).sum()) / (n * x.sum()) - (n + 1) / n)


def main() -> None:
    df = pd.read_excel(XLSX)
    val = df[df["数据有效性"] == "有效"].copy()
    val["published_at"] = pd.to_datetime(val["published_at"], utc=True)

    # 去重（保留首见，记录重复次数 dup = 同文帖子数，即再生产强度）
    key = val["content"].map(lambda s: hashlib.md5(re.sub(r"\s+", "", str(s))[:500].encode()).hexdigest())
    val["_key"] = key
    val = val.sort_values("published_at")
    val["dup"] = val.groupby("_key")["_key"].transform("count")
    val_u = val.drop_duplicates("_key").copy()

    val_u["tokens"] = val_u["content"].map(tokenize)
    vec = TfidfVectorizer(min_df=5, max_df=0.3, ngram_range=(1, 2), sublinear_tf=True)
    X = vec.fit_transform(val_u["tokens"])
    svd = TruncatedSVD(n_components=100, random_state=RANDOM_STATE)
    Xl = Normalizer().fit_transform(svd.fit_transform(X))
    km = MiniBatchKMeans(n_clusters=K, batch_size=2048, n_init=10, random_state=RANDOM_STATE).fit(Xl)
    val_u["k"] = km.labels_

    val_u["theme"] = val_u["k"].map(lambda c: THEME_NAMES.get(c) or NOISE_CLUSTERS.get(c, f"未命名簇{c}"))
    val_u["is_noise"] = val_u["k"].isin(NOISE_CLUSTERS)
    # 重复帖子权重展开回全量有效数据（每条原帖继承其唯一文本的簇标签）
    full = val.merge(val_u[["_key", "k", "theme", "is_noise"]], on="_key", how="left")

    terms = np.array(vec.get_feature_names_out())
    cent = km.cluster_centers_ @ svd.components_

    death = pd.Timestamp("2026-03-24", tz="UTC")
    profiles = {}
    for c in sorted(int(k) for k in val_u["k"].unique()):
        sub = val_u[val_u["k"] == c]
        sub_full = full[full["k"] == c]
        top_terms = [str(t) for t in terms[cent[c].argsort()[::-1][:12]]]
        reps = (sub[sub["dup"] >= sub["dup"].quantile(0.9)]
                .nlargest(5, "dup")["content"].str[:120].tolist())
        daily = sub_full.set_index("published_at").resample("D").size()
        pre = int((sub_full["published_at"] < death).sum())
        profiles[c] = {
            "theme": sub["theme"].iloc[0],
            "is_noise": bool(sub["is_noise"].iloc[0]),
            "n_unique": int(len(sub)),
            "n_total_with_dups": int(len(sub_full)),
            "dup_mean": round(float(sub["dup"].mean()), 2),
            "unique_author_n": int(sub["author"].nunique()),
            "author_gini": round(gini(sub["author"].value_counts().values), 3),
            "category_mix": sub["内容类别"].value_counts(normalize=True).round(3).to_dict(),
            "sentiment_mix": sub["sentiment"].value_counts(normalize=True).round(3).to_dict(),
            "platform_mix": sub["media_type"].value_counts(normalize=True).round(3).to_dict(),
            "pre_death_share": round(pre / max(len(sub_full), 1), 3),
            "peak_day": str(daily.idxmax().date()) if len(daily) else None,
            "peak_count": int(daily.max()) if len(daily) else 0,
            "top_terms": top_terms,
            "examples": reps,
        }

    cols = ["id", "author", "media_type", "sentiment", "内容类别", "theme", "k", "is_noise",
            "dup", "published_at", "reach", "title", "content"]
    val_u[cols].to_parquet(OUT / "valid_posts_clusters.parquet", index=False)
    (OUT / "cluster_profiles.json").write_text(
        json.dumps(profiles, ensure_ascii=False, indent=1), encoding="utf-8")

    summary = pd.DataFrame(profiles).T[
        ["theme", "is_noise", "n_unique", "n_total_with_dups", "dup_mean",
         "unique_author_n", "pre_death_share", "peak_day", "peak_count"]]
    print(summary.to_string())
    print(f"\n输出: {OUT/'valid_posts_clusters.parquet'} / cluster_profiles.json")


if __name__ == "__main__":
    main()
