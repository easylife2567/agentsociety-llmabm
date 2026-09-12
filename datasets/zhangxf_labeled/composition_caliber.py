# Agent 群体构成（类型比例）的多种口径对照 —— 回答「是否应只用 W12 单周定群体比例」
#
# 【裁定留痕 2026-09-13：本脚本为一次性评估，结论是"不改"】
#   用户裁定维持原口径（W12–W22 全窗 + 发帖人口径 = 19/22/23/15/21），
#   本脚本列出的另外三种口径（W12 单周 / 事件前 / ≥2帖 complete-case）均已否决。
#   → 本文件不再作为生产口径输入；仅作决策依据留档。见 EXPERIMENT.md「口径定档」。
# 输入: 抖音微博小红书-全量已打标.xlsx（工作区根目录，用户提供）
# 输出: composition_caliber.json + 控制台对照表
#
# 背景：H4E1 现行群体构成 营销23/悼念22/其他21/梗19/教育15（发帖人口径，100 agents）
#       本脚本对照四种口径，回答「取单周 vs 取全窗」以及「单帖用户是否污染估计」。
#
# 口径说明：
#   stock  存量口径 = 窗内「只发一种内容类别」的用户，按类别计人（HYPOTHESIS 发帖人口径）
#   flow   流量口径 = 同上但只取单周（用户提出："只算 W12"）
#   1post / 2post+ ：分母为「发帖数 >= k 且单类型」——>=2 帖者类型多样性才真正可识别，
#                    单帖用户的「单类型」是恒真观测（censoring），会稀释构成
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "抖音微博小红书-全量已打标.xlsx"
OUT = Path(__file__).resolve().parent / "composition_caliber.json"
CACHE = Path("/tmp/labeled_full.parquet")

# 剔除爬取噪音：抓取残留非用户选择行为；借势营销保留（营销号是真实发帖人）
TYPES = ["借势营销", "事件悼念讨论", "其他讨论", "梗文化讨论", "教育观点讨论"]
WEEKS = [f"2026-W{w:02d}" for w in range(5, 23)]   # 数据覆盖 W05–W22


def load() -> pd.DataFrame:
    df = pd.read_parquet(CACHE) if CACHE.exists() else pd.read_excel(
        XLSX, usecols=['数据有效性', '内容类别', 'author', 'published_at', 'media_type'])
    df['published_at'] = pd.to_datetime(df['published_at'], utc=True)
    iso = df['published_at'].dt.isocalendar()
    df['week'] = [f"{y}-W{w:02d}" for y, w in zip(iso['year'], iso['week'])]
    return df[(df['数据有效性'] != '存疑') & df['author'].notna()].copy()


def composition(sub: pd.DataFrame, min_posts: int = 1) -> dict:
    n = sub.groupby('author').size()
    t = sub.groupby('author')['内容类别'].nunique()
    keep = n[(n >= min_posts) & (t == 1)].index
    c = (sub[sub['author'].isin(keep) & sub['内容类别'].isin(TYPES)]
         .groupby('内容类别')['author'].nunique())
    c = c.reindex(TYPES).fillna(0).astype(int)
    n_u = int(t.size)
    return {
        "帖子数": int(len(sub)),
        "用户数": n_u,
        "计入用户数(单类型且>=%d帖)" % min_posts: int(len(keep)),
        "单类型用户占比": round(len(keep) / n_u, 4),
        "构成人数": {k: int(v) for k, v in c.items() if v > 0},
        "构成份额": {k: round(v / c.sum(), 4) for k, v in c.items()},
        "100agent配额": {k: int(round(v / c.sum() * 100)) for k, v in c.items()},
    }


def main() -> None:
    d = load()
    wk = lambda lo, hi: d[(d['week'] >= f"2026-W{lo:02d}") & (d['week'] <= f"2026-W{hi:02d}")]
    res = {
        "meta": {
            "source": XLSX.name,
            "types_counted": TYPES,
            "excluded": "数据有效性=='存疑'；爬取噪音（非用户选择行为）；author 为空的行",
            "note": "构成份额分母 = 五类单类型用户合计；100agent配额 为最大余数法的近似读数",
        },
        "calibers": {
            "flow_W12单周": composition(wk(12, 12)),
            "stock_W05-W12事件前": composition(wk(5, 12)),
            "stock_W12-W22全窗(现行)": composition(wk(12, 22)),
            "complete_W12-W22_>=2帖": composition(wk(12, 22), min_posts=2),
        },
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    for name, r in res["calibers"].items():
        print(f"\n[{name}] 帖 {r['帖子数']:,} 用户 {r['用户数']:,} "
              f"单类型 {r['计入用户数(单类型且>=%d帖)' % (2 if '>=2' in name else 1)]:,}"
              f" ({r['单类型用户占比']:.2%})")
        print("   份额:", " ".join(f"{k} {v:.1%}" for k, v in r["构成份额"].items() if v))
        print("   → 100 agent:", {k: v for k, v in r["100agent配额"].items() if v})
    print("\n→", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
