# 用户类型集中度：W12–W22 内只发「一种」内容类别的用户占比
# 输入: 抖音微博小红书-全量已打标.xlsx（工作区根目录，用户提供）
# 输出: type_concentration.json（控制台同表）
#
# 口径:
#   时间窗 = ISO 周 2026-W12 – 2026-W22（W12 周一 2026-03-16 UTC 起；与仿真 11 周窗对齐）。
#            用户指定口径，2026-09-12 由 W11 起更正为 W12 起。
#   行过滤 = 剔除 数据有效性=='存疑'(20 行)；'无效'(营销+噪音) 视为真实供给保留
#   用户身份 = author 字段（主口径）；(media_type, author) 为稳健性口径
#   类型 = 内容类别 字段
#   单类型用户 = 该用户在该窗内的全部帖子只落在 1 个 内容类别
#   比例 = 单类型用户数 / 有帖用户数（分母 = 窗内有 >=1 帖且 author 非空的用户）
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "抖音微博小红书-全量已打标.xlsx"
OUT = Path(__file__).resolve().parent / "type_concentration.json"
CACHE = Path("/tmp/labeled_full.parquet")   # 列子集缓存（首次跑由 --recache 生成）

COLS = ['数据有效性', '内容类别', 'author', 'author_handle', 'published_at', 'media_type']
W_START, W_END = "2026-W12", "2026-W22"
DISCUSSION_TYPES = ["事件悼念讨论", "其他讨论", "教育观点讨论", "梗文化讨论"]  # 有效=真实讨论
NOISE_TYPE = "爬取噪音"


def load() -> pd.DataFrame:
    if CACHE.exists():
        df = pd.read_parquet(CACHE)
    else:
        df = pd.read_excel(XLSX, usecols=COLS)
        df.to_parquet(CACHE)
    df['published_at'] = pd.to_datetime(df['published_at'], utc=True)
    iso = df['published_at'].dt.isocalendar()
    df['week'] = [f"{y}-W{w:02d}" for y, w in zip(iso['year'], iso['week'])]
    return df


def summarize(df: pd.DataFrame, user_col, types, label: str) -> dict:
    """user_col: 用户身份列(list 或 str)；types: 计入的类型集合（None 表示全部）"""
    d = df if types is None else df[df['内容类别'].isin(types)]
    n_posts, n_users = len(d), d[user_col].nunique()
    t = d.groupby(user_col)['内容类别'].nunique()
    n_single = int((t == 1).sum())
    # 单类型用户的类型构成
    single_users = t[t == 1].index
    comp = (d[d[user_col].isin(single_users)]
            .groupby('内容类别')[user_col].nunique().sort_values(ascending=False))
    n_single_posts = int(d[d[user_col].isin(single_users)].shape[0])
    return {
        "口径": label,
        "帖子数": n_posts,
        "用户数": n_users,
        "单类型用户数": n_single,
        "单类型用户占比": round(n_single / n_users, 4) if n_users else None,
        "单类型用户帖子数": n_single_posts,
        "单类型用户帖子占比": round(n_single_posts / n_posts, 4) if n_posts else None,
        "多类型用户数": n_users - n_single,
        "类型数分布": {int(k): int(v) for k, v in t.value_counts().sort_index().items()},
        "单类型用户类型构成": {k: int(v) for k, v in comp.items()},
        # 构成占比：分母分别为 单类型用户数 / 全部用户数 / 剔除爬取噪音后的五类合计
        "单类型用户构成占比": {
            "占单类型用户": {k: round(v / n_single, 4) for k, v in comp.items()} if n_single else {},
            "占全部用户": {k: round(v / n_users, 4) for k, v in comp.items()} if n_users else {},
            "占五类(不含爬取噪音)": {
                k: round(v / sum(x for kk, x in comp.items() if kk != NOISE_TYPE), 4)
                for k, v in comp.items() if k != NOISE_TYPE},
        },
    }


def main() -> None:
    df = load()
    base = df[(df['week'] >= W_START) & (df['week'] <= W_END)
              & (df['数据有效性'] != '存疑')].copy()
    n_author_null = int(base['author'].isna().sum())
    base = base[base['author'].notna()].copy()
    base['user'] = base['media_type'].astype(str) + "|" + base['author'].astype(str)

    res = {
        "meta": {
            "source": XLSX.name,
            "window": f"{W_START} – {W_END} (2026-03-16 起 UTC, 与仿真 11 周窗对齐)",
            "row_filter": "剔除 数据有效性=='存疑'；W12 前与 W22 后的帖子不含",
            "user_identity": "author（主口径） / media_type+author（稳健性）",
            "author_null_dropped": n_author_null,
            "weeks_seen": sorted(base['week'].unique()),
        },
        "primary": summarize(base, 'author', None, "全部 6 类（含借势营销/爬取噪音），身份=author"),
        "variants": [
            summarize(base, 'author', [c for c in base['内容类别'].unique() if c != NOISE_TYPE],
                      "剔除爬取噪音（5 类），身份=author"),
            summarize(base, 'author', DISCUSSION_TYPES,
                      "仅有效讨论（4 类），分母=有>=1有效帖的用户"),
            summarize(base, 'user', None, "全部 6 类，身份=平台|author（稳健性）"),
        ],
        "by_platform": {},
    }
    for p, sub in base.groupby('media_type'):
        s = summarize(sub, 'author', None, f"{p} 全部 6 类")
        res["by_platform"][p] = {"帖子数": s["帖子数"], "用户数": s["用户数"],
                                 "单类型用户数": s["单类型用户数"], "单类型用户占比": s["单类型用户占比"],
                                 "类型数分布": s["类型数分布"]}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    p = res["primary"]
    print(f"窗口 {res['meta']['window']}；帖子 {p['帖子数']:,}；用户 {p['用户数']:,}"
          f"（丢弃 author 空 {n_author_null} 行）")
    print(f"单类型用户 {p['单类型用户数']:,} / {p['用户数']:,} = {p['单类型用户占比']:.2%}")
    print("类型数分布:", p["类型数分布"])
    print("单类型用户构成:", p["单类型用户类型构成"])
    sh = p["单类型用户构成占比"]
    for k, v in sorted(sh["占五类(不含爬取噪音)"].items(), key=lambda x: -x[1]):
        print(f"    {k}: 占五类 {v:.2%} | 占单类型 {sh['占单类型用户'][k]:.2%}"
              f" | 占全用户 {sh['占全部用户'][k]:.2%}")
    print(f"单类型用户覆盖帖子 {p['单类型用户帖子数']:,} / {p['帖子数']:,} = {p['单类型用户帖子占比']:.2%}")
    for v in res["variants"] + [dict(x, 口径=f"[平台] {k}") for k, x in res["by_platform"].items()]:
        print(f"  - {v['口径']}: {v['单类型用户数']:,}/{v['用户数']:,} = {v['单类型用户占比']:.2%}")
    print("→", OUT.relative_to(ROOT))


if __name__ == "__main__":
    sys.exit(main())
