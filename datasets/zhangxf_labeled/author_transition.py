# 作者级话题转换（"换话题率"）审计 —— 回答「4% 这个数是否严谨」
#
# 输入: data/baseline/抖音微博小红书-全量已打标.xlsx（用户提供）
# 输出: author_transition.json（控制台同表）
#
# 背景：用户报告"只有 4% 左右的人会换话题"，用以支撑
#   「转向来自发声机会变化，而非大量个体态度转变」。
#   本脚本不复用该口径，而是把"换话题率"重新算一遍，并补上三个缺失的对照：
#     1) 删失校正：只发 1 帖的用户"单类型"是恒真观测，不能进分母
#     2) 零假设：把事件后类型随机重排，看"纯随机下应该换多少"
#     3) 时间安慰剂：事件前的相邻两周窗之间，本来就有多少人换话题
#   另给出帖量加权口径（人头口径会低估高产出用户的影响）。
#
# 口径:
#   事件日 2026-03-24 ∈ ISO W13；pre = W05–W12，post = W13–W22
#   类型 = 内容类别；剔除 爬取噪音（非用户选择行为）与 数据有效性=='存疑'
#   作者身份 = author
#   主类型 = 该作者在该窗内的众数；并列时记为 ambiguous，单独计数、不计入转换率分子分母
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data" / "baseline" / "抖音微博小红书-全量已打标.xlsx"
OUT = Path(__file__).resolve().parent / "author_transition.json"
CACHE = Path("/tmp/labeled_transition.pkl")

COLS = ["数据有效性", "内容类别", "author", "published_at"]
NOISE = "爬取噪音"
TYPES = ["借势营销", "事件悼念讨论", "其他讨论", "梗文化讨论", "教育观点讨论"]

PRE = ("2026-W05", "2026-W12")
POST = ("2026-W13", "2026-W22")
# 等长对照（各 4 周）：安慰剂 = 事件前内部；处理 = 跨越事件日
PLACEBO_PAIR = (("2026-W05", "2026-W08"), ("2026-W09", "2026-W12"))
TREAT_PAIR = (("2026-W09", "2026-W12"), ("2026-W13", "2026-W16"))

N_PERM = 500


def load() -> pd.DataFrame:
    if CACHE.exists():
        df = pd.read_pickle(CACHE)
    else:
        df = pd.read_excel(XLSX, usecols=COLS)
        df = df[df["数据有效性"] != "存疑"]
        df = df[df["author"].notna()]
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
        df = df[df["published_at"].notna()]
        iso = df["published_at"].dt.isocalendar()
        df["week"] = "2026-W" + iso["week"].astype(int).astype(str).str.zfill(2)
        df = df[["author", "内容类别", "week"]]
        df.to_pickle(CACHE)
    return df


def dominant(series: pd.Series):
    """众数；并列返回 None（ambiguous）。"""
    vc = series.value_counts()
    if len(vc) == 0:
        return None
    if len(vc) > 1 and vc.iloc[0] == vc.iloc[1]:
        return None
    return vc.index[0]


def pair_rate(df: pd.DataFrame, w1: tuple, w2: tuple, permute: bool = False, rng=None):
    """两个周窗之间、活跃于两窗的作者的主类型转换率。"""
    a = df[(df["week"] >= w1[0]) & (df["week"] <= w1[1])]
    b = df[(df["week"] >= w2[0]) & (df["week"] <= w2[1])].copy()
    if permute:
        b["内容类别"] = rng.permutation(b["内容类别"].to_numpy())
    both = set(a["author"]) & set(b["author"])
    if not both:
        return None
    ta = a[a["author"].isin(both)].groupby("author")["内容类别"].apply(dominant)
    tb = b[b["author"].isin(both)].groupby("author")["内容类别"].apply(dominant)
    j = pd.concat([ta.rename("pre"), tb.rename("post")], axis=1)
    valid = j.dropna()
    amb = len(j) - len(valid)
    if len(valid) == 0:
        return None
    switched = (valid["pre"] != valid["post"]).sum()
    return {
        "n_panel": int(len(j)),
        "n_ambiguous": int(amb),
        "n_valid": int(len(valid)),
        "n_switched": int(switched),
        "switch_rate": float(switched / len(valid)),
        "post_posts_from_switchers": float(
            b[b["author"].isin(valid[valid["pre"] != valid["post"]].index)].shape[0]
            / max(b[b["author"].isin(both)].shape[0], 1)
        ),
    }


def transition_matrix(df: pd.DataFrame, w1: tuple, w2: tuple):
    """两个周窗之间、活跃于两窗作者的主类型转移矩阵（行=前窗主类型，列=后窗）。"""
    a = df[(df["week"] >= w1[0]) & (df["week"] <= w1[1])]
    b = df[(df["week"] >= w2[0]) & (df["week"] <= w2[1])]
    both = set(a["author"]) & set(b["author"])
    ta = a[a["author"].isin(both)].groupby("author")["内容类别"].apply(dominant)
    tb = b[b["author"].isin(both)].groupby("author")["内容类别"].apply(dominant)
    j = pd.concat([ta.rename("pre"), tb.rename("post")], axis=1).dropna()
    m = pd.crosstab(j["pre"], j["post"]).reindex(index=TYPES, columns=TYPES, fill_value=0)
    row = m.div(m.sum(axis=1).replace(0, np.nan), axis=0).round(4)
    return {
        "n_valid": int(len(j)),
        "counts": m.to_dict(),
        "row_normalized": row.fillna(0).to_dict(),
        "offdiag_rate": round(float(1 - np.trace(m.to_numpy()) / max(m.to_numpy().sum(), 1)), 4),
    }


def main():
    df = load()
    df = df[df["内容类别"].isin(TYPES)]
    rng = np.random.default_rng(20260927)
    out = {
        "meta": {
            "source": XLSX.name,
            "pre": f"{PRE[0]}–{PRE[1]}",
            "post": f"{POST[0]}–{POST[1]}",
            "row_filter": "剔除 数据有效性=='存疑'、author 空、爬取噪音",
            "type_rule": "作者在该窗内的众数；并列记 ambiguous 并剔除",
            "n_perm": N_PERM,
        }
    }

    # --- 1. 删失：每个作者的发帖量分布 ---
    n_posts = df.groupby("author").size()
    out["censoring"] = {
        "用户数": int(len(n_posts)),
        "帖子数": int(len(df)),
        "人均帖数": round(float(n_posts.mean()), 3),
        "只发1帖用户占比": round(float((n_posts == 1).mean()), 4),
        "发>=2帖用户数": int((n_posts >= 2).sum()),
        "发>=2帖用户占比": round(float((n_posts >= 2).mean()), 4),
    }

    # --- 2. 主口径：pre -> post ---
    main_pair = pair_rate(df, PRE, POST)
    out["pre_post"] = main_pair

    # 只保留两窗各 >=2 帖的作者（类型真正可识别）
    a = df[(df["week"] >= PRE[0]) & (df["week"] <= PRE[1])]
    b = df[(df["week"] >= POST[0]) & (df["week"] <= POST[1])]
    na, nb = a.groupby("author").size(), b.groupby("author").size()
    strict = set(na[na >= 2].index) & set(nb[nb >= 2].index)
    if strict:
        ta = a[a["author"].isin(strict)].groupby("author")["内容类别"].apply(dominant)
        tb = b[b["author"].isin(strict)].groupby("author")["内容类别"].apply(dominant)
        j = pd.concat([ta.rename("pre"), tb.rename("post")], axis=1).dropna()
        out["pre_post_strict_2post_each"] = {
            "n_valid": int(len(j)),
            "n_switched": int((j["pre"] != j["post"]).sum()),
            "switch_rate": round(float((j["pre"] != j["post"]).mean()), 4),
        }

    # --- 3. 零假设：事件后类型随机重排 ---
    nulls = []
    for _ in range(N_PERM):
        r = pair_rate(df, PRE, POST, permute=True, rng=rng)
        if r:
            nulls.append(r["switch_rate"])
    out["null_permutation"] = {
        "mean": round(float(np.mean(nulls)), 4),
        "p05": round(float(np.percentile(nulls, 5)), 4),
        "p95": round(float(np.percentile(nulls, 95)), 4),
        "note": "保持每位作者事件后帖数与整体类型分布不变，仅打散作者-类型关联",
    }

    # --- 4. 时间安慰剂（等长 4v4） ---
    out["placebo_pre_internal"] = pair_rate(df, *PLACEBO_PAIR)
    out["treatment_matched"] = pair_rate(df, *TREAT_PAIR)

    # --- 5. 转移矩阵：全窗 与 哀悼期→玩梗期 ---
    out["transition_pre_post"] = transition_matrix(df, PRE, POST)
    MOURN_WIN = ("2026-W13", "2026-W18")
    MEME_WIN = ("2026-W19", "2026-W22")
    out["transition_mourning_to_meme"] = transition_matrix(df, MOURN_WIN, MEME_WIN)
    out["mourning_to_meme_pair"] = pair_rate(df, MOURN_WIN, MEME_WIN)

    # 众数翻转 vs 真转换：要求两窗各 >=3 帖，排除"只多发一条就翻众数"
    ma = df[(df["week"] >= MOURN_WIN[0]) & (df["week"] <= MOURN_WIN[1])]
    mb = df[(df["week"] >= MEME_WIN[0]) & (df["week"] <= MEME_WIN[1])]
    na3, nb3 = ma.groupby("author").size(), mb.groupby("author").size()
    strict3 = set(na3[na3 >= 3].index) & set(nb3[nb3 >= 3].index)
    if strict3:
        ta = ma[ma["author"].isin(strict3)].groupby("author")["内容类别"].apply(dominant)
        tb = mb[mb["author"].isin(strict3)].groupby("author")["内容类别"].apply(dominant)
        j3 = pd.concat([ta.rename("pre"), tb.rename("post")], axis=1).dropna()
        out["mourning_to_meme_strict_3post_each"] = {
            "n_valid": int(len(j3)),
            "n_switched": int((j3["pre"] != j3["post"]).sum()),
            "switch_rate": round(float((j3["pre"] != j3["post"]).mean()), 4),
        }

    # 面板构成偏差：转移矩阵面板中营销号占比 vs 总体
    out["panel_composition_bias"] = {
        "面板中营销号占比": round(
            float(
                (j3["pre"] == "借势营销").mean() if strict3 else 0
            ),
            4,
        ),
        "总体营销号占比": round(
            float((df["内容类别"] == "借势营销").mean()), 4
        ),
    }

    # 玩梗期新面孔：W19–W22 发帖者中，哀悼期未出现过的占比
    mem = df[(df["week"] >= MEME_WIN[0]) & (df["week"] <= MEME_WIN[1])]
    mour = df[(df["week"] >= MOURN_WIN[0]) & (df["week"] <= MOURN_WIN[1])]
    mem_authors = set(mem["author"])
    new_faces = mem_authors - set(mour["author"])
    out["meme_window_new_faces"] = {
        "玩梗期发帖人数": int(len(mem_authors)),
        "哀悼期未出现过的": int(len(new_faces)),
        "新面孔占比": round(float(len(new_faces) / max(len(mem_authors), 1)), 4),
        "新面孔帖子占比": round(
            float(mem[mem["author"].isin(new_faces)].shape[0] / max(mem.shape[0], 1)), 4
        ),
    }

    # --- 6. "新面孔"基线：多数用户只发 1 帖，跨窗重叠本来就低 ---
    # 没有基线的话，"92% 是新面孔"这种数字不说明任何问题。
    pairs = [
        ("W05-08→W09-12 (安慰剂·事件前)", ("2026-W05", "2026-W08"), ("2026-W09", "2026-W12")),
        ("W09-12→W13-16 (跨事件·等长)", ("2026-W09", "2026-W12"), ("2026-W13", "2026-W16")),
        ("W13-16→W17-20 (事件后内部)", ("2026-W13", "2026-W16"), ("2026-W17", "2026-W20")),
        ("W14-18→W19-22 (紧邻处理窗)", ("2026-W14", "2026-W18"), ("2026-W19", "2026-W22")),
        ("W13-18→W19-22 (处理窗)", ("2026-W13", "2026-W18"), ("2026-W19", "2026-W22")),
    ]
    overlap = {}
    for label, w1, w2 in pairs:
        a = set(df[(df["week"] >= w1[0]) & (df["week"] <= w1[1])]["author"])
        b = df[(df["week"] >= w2[0]) & (df["week"] <= w2[1])]
        ba = set(b["author"])
        overlap[label] = {
            "后窗发帖人数": int(len(ba)),
            "前窗也发过帖": int(len(ba & a)),
            "新面孔占比": round(float(len(ba - a) / max(len(ba), 1)), 4),
            "新面孔帖子占比": round(
                float(b[~b["author"].isin(a)].shape[0] / max(b.shape[0], 1)), 4
            ),
        }
    out["new_face_baselines"] = overlap

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
