"""H4 v0.3 配置生成器(可复现)。

依据: hypothesis_4/DESIGN_V0.3.md(2026-09-07 用户裁定版)
数据: 抖音微博小红书-全量已打标.xlsx(工作区根目录, 52,736 行)

用法(在 experiment_1/init 目录下):
    $PYTHON_PATH config_params.py            # 生成 E1(reddit_hot) + E2(chronological)

产出:
    ./supply_pool.json ./agent_profiles.json ./init_config.json ./steps.yaml ./CONFIG_NOTES.md
    ../../experiment_2/init/{supply_pool,agent_profiles,init_config}.json + CONFIG_NOTES.md(仅算法不同)

机制参数(全部有依据, 见 CONFIG_NOTES):
    - 供给池: 周×类群真实文本采样, 目标 ~500 条, seed=42
    - 媒体配额: 周 verified 数 × scale × 3(过采样系数保议程可见性), 仅非噪音类
    - 初始互动: 类群底数 × 周注意力 × 对数正态噪声(非黑箱, 公式见 supply_notes)
"""

from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------- 常量
SEED = 42
TARGET_POOL = 500
WINDOW_WEEKS = [f"2026-W{n:02d}" for n in range(12, 23)]  # W12-W22(W23 无数据)
START_T = "2026-03-16T00:00:00"  # W12 周一
EVENT_START_ISO = "2026-03-24T08:00:00"  # 去世时刻(W13)
TICK_SECONDS = 604800  # 1周
EXTERNAL_SPIKE = 100.0
EXTERNAL_HALF_LIFE_WEEKS = 2.0
INTERNAL_ELASTICITY = 0.3
INTERNAL_HALF_LIFE_WEEKS = 1.0
SALIENCE_FLOOR = 5.0
AMBIENT_LIKE_BASE_RATE = 8.0
FEED_LIMIT = 20
MEDIA_OVERSAMPLE = 3.0

CAT_CODE = {
    "借势营销": "marketing",
    "事件悼念讨论": "mourning",
    "其他讨论": "general",
    "教育观点讨论": "edu",
    "梗文化讨论": "meme",
    "爬取噪音": "noise",
}
CAT_BASE_LIKE = {  # 类群互动底数(悼念帖死亡窗口高, 水军低), 按 topic_category 编码
    "marketing": 1.0,
    "mourning": 1.6,
    "general": 0.8,
    "edu": 1.2,
    "meme": 1.1,
    "noise": 0.3,
}
CLASS_SIZE_WEIGHTS = {  # 全量占比(用户裁定①: 全量口径)
    "marketing": 0.306,
    "mourning": 0.170,
    "general": 0.163,
    "edu": 0.147,
    "meme": 0.136,
    "noise": 0.076,
}
AGENT_TURNS = {"marketing": 6, "mourning": 3, "general": 3, "edu": 3, "meme": 3, "noise": 2}

PERSONAS = {
    "marketing": (
        "你是一个微博/短视频平台的营销号运营者,手上有几个账号,靠蹭热点做流量。"
        "你的运营逻辑:什么话题热就借什么势——哪类内容互动高,你就跟着做哪类,借势文案、话题标签、带货链接都是你的常规操作。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;热度越高,你蹭得越勤(发帖/转发/评论都更频繁);热度回落后,你转回日常选题。是否出手、出手几次由你自行判断,没人强制你。"
        "【层2·框架】参与时你选择当下最容易带流量的框架:事件初期哀悼氛围浓,你就用追思体借势文案;玩梗火起来,你就玩梗借势;教育话题回温,你就挂课程和干货。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你熟悉张雪峰——他是考研辅导领域的顶级流量人物,话题度高,是你眼中的优质流量池。你对他没有真假情感,只有流量判断。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
    "mourning": (
        "你是一个普通的社交媒体用户,性格温和重感情。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;事件热度高时你会参与讨论,热度退去你也自然回到日常,不会一直沉溺在同一个话题里。是否发言由你的心情决定,没人强制你发悼念内容。"
        "【层2·框架】你参与事件讨论时默认用悼念框架:蜡烛、RIP、「一路走好」、回忆他给你带来的帮助;看到夸大的谣言你也会表达惋惜或不满。但如果你刷到的内容触动了你,你也可以用别的方式回应。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你熟悉张雪峰:刷到过他的讲课切片,觉得他说话直、接地气,对他印象是好感的。你对他的突然离世(如果你刷到了)会真心难过。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
    "general": (
        "你是一个社交媒体的重度围观用户,日常以刷帖、吃瓜、偶尔闲聊为主,对热点事件卷入度低。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;热度很高时你偶尔跟着议论两句,热度一般时你大多只看不发。发不发、发什么由你自己决定。"
        "【层2·框架】你发言通常是日常杂谈式的围观评论:感慨一句、吐槽一句、跟着大家的态度走。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你可能刷到过张雪峰的视频,印象比较淡,谈不上喜欢或讨厌。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
    "edu": (
        "你是一名正在准备考研或关心升学规划的学生/家长,活跃在教育讨论社群,熟悉志愿填报和考研择校的话语体系。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;与教育相关的话题你参与意愿高,纯娱乐热点你大多路过。是否发言由你自己决定。"
        "【层2·框架】你始终用专业视角发言:讨论志愿填报、考研规划、他的观点和方法是否可信;就算在事件讨论中,你也倾向谈他的专业遗产和观点争论,而不是跟风玩梗。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你熟悉张雪峰:看过他的志愿填报直播,可能用过他的建议,对他的专业能力认可,对他部分观点有保留(你既可能夸他,也可能争论他)。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
    "meme": (
        "你是短视频重度用户,以玩梗为乐,追热点就是为了参与造梗,看到有趣的帖子忍不住整活。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;热度越高你越兴奋,参与越频繁;热度退去你去找别的乐子。是否整活由你自己决定。"
        "【层2·框架】你只对实际刷到的梗模板做二创、改编和组合——没见过的梗你编不出来;同一模板你能翻出新花样。如果刷到的内容不适合玩梗,你也可以正常评论。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你熟悉张雪峰:他的语录和直播切片本身就是素材库,你对他谈不上恶意,但好素材你不介意解构。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
    "noise": (
        "你是一个低质搬运小号,日常就是复制粘贴热门内容、灌水、蹭话题标签涨粉,没有原创观点。"
        "【层1·参与】你刷 feed 时会看到「全站热搜」给出的全站事件热度;哪里热你往哪里凑,热度低你就沉底。"
        "【层2·框架】你的发言基本是搬运和复读:改几个字转发热帖、复制热门评论、堆标签。你的所有评论和转发必须基于你实际刷到的帖子,禁止对没见过的内容凭空评价。"
        "【层3·底色】你对张雪峰没有任何真实认知,他只是一个可以蹭的词。"
        "你不知道未来会发生什么:你此刻的记忆停留在当前时间,一切以你实际刷到的内容为准。"
    ),
}

AGENT_NAMES = {
    "marketing": "借势营销群",
    "mourning": "悼念讨论群",
    "general": "杂谈围观群",
    "edu": "教育观点群",
    "meme": "梗文化群",
    "noise": "水军低质号",
}
FAMILIARITY_PRIOR = {
    "marketing": "高(流量视角熟悉)",
    "mourning": "高(看过其视频,有好感)",
    "general": "低(印象淡)",
    "edu": "高(专业使用者)",
    "meme": "高(素材视角熟悉)",
    "noise": "无认知(仅当标签蹭)",
}
SENTIMENT_PROFILE = {
    "marketing": "P为主(表面友好文案)",
    "mourning": "P为主,夹杂V(惋惜)",
    "general": "中性",
    "edu": "P与N并存(认可与争论)",
    "meme": "P与N混杂(解构)",
    "noise": "无关情感",
}


def iso_naive(s: str) -> str:
    """UTC ISO → naive ISO(仿真时钟为 naive 本地,统一截断时区)。"""
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(sep="T")


def build_supply(df: pd.DataFrame, rng: random.Random) -> tuple[list[dict], dict]:
    """周×类群采样 + 媒体重指派 + 初始互动合成。"""
    ts = pd.to_datetime(df["published_at"], format="ISO8601", utc=True)
    df = df.copy()
    df["week"] = ts.dt.strftime("%G-W%V")
    df = df[df["week"].isin(WINDOW_WEEKS) & (df["内容类别"] != "存疑") & df["content"].notna()]

    mat = df.pivot_table(index="week", columns="内容类别", values="id", aggfunc="count", fill_value=0)
    window_total = int(mat.values.sum())
    scale = TARGET_POOL / window_total
    week_total = {w: int(mat.loc[w].sum()) for w in WINDOW_WEEKS}
    max_week = max(week_total.values())

    # 媒体通道: 周 verified 非噪音行独立抽样(保真实议程节奏 W13 高密集), 重指派给媒体账号 999
    media_rows: list[tuple[str, str, object]] = []
    for w in WINDOW_WEEKS:
        vw = df[(df["week"] == w) & (df["author_verified"] == 1.0) & (df["内容类别"] != "爬取噪音")]
        if len(vw) == 0:
            continue
        quota = max(1, round(len(vw) * scale * MEDIA_OVERSAMPLE))
        take = vw.sample(n=min(quota, len(vw)), random_state=rng.randrange(1 << 30))
        for _, row in take.iterrows():
            media_rows.append((w, CAT_CODE[str(row["内容类别"])], row))
    media_idx = {row.name for _, _, row in media_rows}

    # 通用通道: 周×类群采样(排除已选媒体行, 防重复)
    sampled: list[tuple[str, str, object]] = []
    for w in WINDOW_WEEKS:
        for cat, code in CAT_CODE.items():
            cell = df[(df["week"] == w) & (df["内容类别"] == cat) & (~df.index.isin(media_idx))]
            n = 0 if len(cell) == 0 else max(1, round(len(cell) * scale))
            if n == 0:
                continue
            take = cell.sample(n=min(n, len(cell)), random_state=rng.randrange(1 << 30))
            for _, row in take.iterrows():
                sampled.append((w, code, row))

    # 周注意力(用于初始互动合成)
    week_attn = {w: week_total[w] / max_week for w in WINDOW_WEEKS}

    posts: list[dict] = []
    bg_author_seq = 1001  # 背景作者段 1001+, 避免撞媒体账号 999
    all_rows = ([(w, c, r, True) for w, c, r in media_rows]
                + [(w, c, r, False) for w, c, r in sampled])
    for i, (w_, code, row, is_media) in enumerate(all_rows):
        author_id = 999
        if not is_media:
            author_id = bg_author_seq
            bg_author_seq += 1
        cat_base = CAT_BASE_LIKE[code]
        mu = math.log(max(cat_base * (0.3 + 0.7 * week_attn[w_]) * 12.0, 0.05))
        likes0 = min(int(rng.lognormvariate(mu, 0.8)), 400)
        views0 = int(likes0 * 25 * (1 + rng.uniform(0, 0.5)))
        posts.append(
            {
                "post_id": i + 1,
                "author_id": author_id,
                "content": str(row["content"])[:2000],
                "post_type": "original",
                "parent_id": None,
                "created_at": iso_naive(str(row["published_at"])),
                "likes_count": likes0,
                "reposts_count": 0,
                "comments_count": 0,
                "view_count": views0,
                "tags": [code, str(row["media_type"])],
                "topic_category": code,
            }
        )
    week_counts = {w: 0 for w in WINDOW_WEEKS}
    cat_counts: dict[str, int] = {c: 0 for c in CAT_CODE.values()}
    media_week: dict[str, int] = {w: 0 for w in WINDOW_WEEKS}
    for w, code, _, is_media in all_rows:
        week_counts[w] += 1
        cat_counts[code] += 1
        if is_media:
            media_week[w] += 1
    notes = {
        "scale": round(scale, 5),
        "target_pool": TARGET_POOL,
        "window_total_real": window_total,
        "pool_n": len(posts),
        "media_n": len(media_rows),
        "media_week": media_week,
        "week_counts": week_counts,
        "category_counts": cat_counts,
        "initial_like_rule": "likes0 = lognorm(mu=ln(cat_base*(0.3+0.7*week_attn)*12), sigma=0.8), cap 400; views0=likes0*25*(1+U(0,0.5)); reposts/comments 初始为 0(由模拟内生成)",
        "cat_base_like": CAT_BASE_LIKE,
        "week_attn": {w: round(week_attn[w], 3) for w in WINDOW_WEEKS},
        "media_oversample": MEDIA_OVERSAMPLE,
    }
    return posts, notes


def build_persons(posts: list[dict]) -> dict:
    persons: dict[int, dict] = {}
    for p in posts:
        aid = p["author_id"]
        if aid not in persons:
            if aid == 999:
                persons[aid] = {
                    "id": 999,
                    "username": "权威媒体",
                    "bio": "官方新闻媒体账号(环境注入,非问卷对象)",
                    "followers_count": 1000000,
                }
            else:
                persons[aid] = {
                    "id": aid,
                    "username": f"网友{aid - 1000}",
                    "bio": None,
                    "followers_count": 0,
                }
    return {str(k): v for k, v in persons.items()}


def build_agents() -> list[dict]:
    agents = []
    for i, (code, weight) in enumerate(CLASS_SIZE_WEIGHTS.items(), start=1):
        agents.append(
            {
                "agent_id": i,
                "agent_type": "PersonAgent",
                "kwargs": {
                    "id": i,
                    "name": AGENT_NAMES[code],
                    "persona": PERSONAS[code],
                    "max_react_turns": AGENT_TURNS[code],
                    "enable_memory": True,
                    "enable_todo_list": False,
                },
            }
        )
    return agents


def build_profiles() -> list[dict]:
    profiles = []
    for i, (code, weight) in enumerate(CLASS_SIZE_WEIGHTS.items(), start=1):
        profiles.append(
            {
                "agent_id": i,
                "name": AGENT_NAMES[code],
                "family": code,
                "class_label": code,
                "class_size_weight": weight,
                "max_react_turns": AGENT_TURNS[code],
                "familiarity_prior": FAMILIARITY_PRIOR[code],
                "sentiment_profile": SENTIMENT_PROFILE[code],
            }
        )
    return profiles


STEPS_YAML = """start_t: '{start_t}'
steps:
- type: questionnaire
  questionnaire_id: T0_baseline_w12
  title: 基线问卷(W12 生前基线周,曝光前)
  questions:
  - id: impression_words
    prompt: "用 3-5 个词描述你对「张雪峰」的印象。如果你此前没听说过他,请回答「没听说过」。"
    response_type: text
  - id: familiarity
    prompt: "你对张雪峰的熟悉程度(1=完全没听说过,5=非常熟悉)?"
    response_type: integer
  - id: impression_source
    prompt: "如果你对张雪峰有印象,你的印象主要来自哪里?"
    response_type: choice
    choices: [生前视频/直播, 死亡事件相关短视频或帖子, 新闻报道, 朋友讨论, 没听说过/不适用]
  - id: occupation
    prompt: "在你印象中,张雪峰是做什么的?(没有印象请回答「不知道」)"
    response_type: text
- num_steps: 3
  tick: 604800
  type: run
- type: questionnaire
  questionnaire_id: T1_w15_decay
  title: 第 1 次测量(W15,悼念退潮期:已历死亡冲击周 W13 与衰减 W14)
  questions:
  - id: impression_words
    prompt: "用 3-5 个词描述你对「张雪峰」的印象。如果你此前没听说过他,请回答「没听说过」。"
    response_type: text
  - id: familiarity
    prompt: "你对张雪峰的熟悉程度(1=完全没听说过,5=非常熟悉)?"
    response_type: integer
  - id: impression_source
    prompt: "如果你对张雪峰有印象,你的印象主要来自哪里?"
    response_type: choice
    choices: [生前视频/直播, 死亡事件相关短视频或帖子, 新闻报道, 朋友讨论, 没听说过/不适用]
  - id: occupation
    prompt: "在你印象中,张雪峰是做什么的?(没有印象请回答「不知道」)"
    response_type: text
- num_steps: 4
  tick: 604800
  type: run
- type: questionnaire
  questionnaire_id: T2_w19_secondwave
  title: 第 2 次测量(W19,第二波启动点)
  questions:
  - id: impression_words
    prompt: "用 3-5 个词描述你对「张雪峰」的印象。如果你此前没听说过他,请回答「没听说过」。"
    response_type: text
  - id: familiarity
    prompt: "你对张雪峰的熟悉程度(1=完全没听说过,5=非常熟悉)?"
    response_type: integer
  - id: impression_source
    prompt: "如果你对张雪峰有印象,你的印象主要来自哪里?"
    response_type: choice
    choices: [生前视频/直播, 死亡事件相关短视频或帖子, 新闻报道, 朋友讨论, 没听说过/不适用]
  - id: occupation
    prompt: "在你印象中,张雪峰是做什么的?(没有印象请回答「不知道」)"
    response_type: text
- num_steps: 3
  tick: 604800
  type: run
- type: questionnaire
  questionnaire_id: T3_w22_memepeak
  title: 第 3 次测量(W22,玩梗峰值周)
  questions:
  - id: impression_words
    prompt: "用 3-5 个词描述你对「张雪峰」的印象。如果你此前没听说过他,请回答「没听说过」。"
    response_type: text
  - id: familiarity
    prompt: "你对张雪峰的熟悉程度(1=完全没听说过,5=非常熟悉)?"
    response_type: integer
  - id: impression_source
    prompt: "如果你对张雪峰有印象,你的印象主要来自哪里?"
    response_type: choice
    choices: [生前视频/直播, 死亡事件相关短视频或帖子, 新闻报道, 朋友讨论, 没听说过/不适用]
  - id: occupation
    prompt: "在你印象中,张雪峰是做什么的?(没有印象请回答「不知道」)"
    response_type: text
- num_steps: 2
  tick: 604800
  type: run
"""


def build_init_config(posts: list[dict], persons: dict, algorithm: str) -> dict:
    return {
        "env_modules": [
            {
                "module_type": "CurationDynamicsSpace",
                "kwargs": {
                    "agent_id_name_pairs": [[i, AGENT_NAMES[c]] for i, c in enumerate(CLASS_SIZE_WEIGHTS, start=1)] + [[999, "权威媒体"]],
                    "persons": persons,
                    "posts": {str(p["post_id"]): p for p in posts},
                    "comments": {},
                    "likes": {},
                    "recommendation_algorithm": algorithm,
                    "random_seed": SEED,
                    "event_start_iso": EVENT_START_ISO,
                    "external_spike": EXTERNAL_SPIKE,
                    "external_half_life_weeks": EXTERNAL_HALF_LIFE_WEEKS,
                    "internal_elasticity": INTERNAL_ELASTICITY,
                    "internal_decay_half_life_weeks": INTERNAL_HALF_LIFE_WEEKS,
                    "salience_floor": SALIENCE_FLOOR,
                    "class_size_weights": {str(k): v for k, v in CLASS_SIZE_WEIGHTS.items()},
                    "ambient_like_base_rate": AMBIENT_LIKE_BASE_RATE,
                    "feed_limit": FEED_LIMIT,
                },
            }
        ],
        "agents": build_agents(),
    }


CONFIG_NOTES_TMPL = """# 试点配置生成记录(v0.3, {algorithm})

```json
{summary_json}
```

## 设计依据
- 设计总纲: [../../DESIGN_V0.3.md](../../DESIGN_V0.3.md)(2026-09-07 用户裁定版)
- 效标: [../../benchmark_curves.json](../../benchmark_curves.json)
- 生成器: `config_params.py`(可复现;E2 由同一脚本产出,仅 `recommendation_algorithm` 不同)

## 关键设定
- **Agent**: 6 类群代表(1 agent = 1 内容类群,全量占比划行动预算);权威媒体(id=999)为 env 侧供给源,非问卷对象
- **供给池**: xlsx 周×类群采样 {pool_n} 条(真实宇宙 {window_total} 条,scale≈{scale}),created_at 按真实发表时间错峰(时间门控依赖)
- **媒体**: 周 verified×scale×3 过采样(保议程可见性),重指派给 999,仅非噪音类
- **初始互动**: 机制规则合成(类群底数×周注意力×对数正态,seed 固定),非黑箱
- **时间**: start_t={start_t}(W12 周一),tick=604800s=1 周,12 ticks 覆盖 W12→W23;死亡事件 {event_start}(W13)经 S(t) 与媒体/供给帖注入
- **问卷**: T0@W12 生前基线 / T1@W15 悼念退潮 / T2@W19 二波启动 / T3@W22 玩梗峰值
- **唯一实验操纵**: `recommendation_algorithm={algorithm}`
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default="../../../抖音微博小红书-全量已打标.xlsx")
    ap.add_argument("--e2-dir", default="../../experiment_2/init")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    df = pd.read_excel(root / args.xlsx)
    rng = random.Random(SEED)

    posts, notes = build_supply(df, rng)
    persons = build_persons(posts)
    profiles = build_profiles()

    e1_summary = {
        "design": "DESIGN_V0.3.md(6 类群代表/周级/媒体归env/背景互动当量)",
        **{k: v for k, v in notes.items() if k != "week_attn"},
        "agents_n": 6,
        "recommendation_algorithm": "reddit_hot",
        "start_t": START_T,
        "event_start": EVENT_START_ISO,
        "tick_seconds": TICK_SECONDS,
        "run_ticks_total": 12,
        "questionnaires": ["T0@W12", "T1@W15", "T2@W19", "T3@W22"],
    }

    # E1
    json.dump(posts, open(root / "supply_pool.json", "w"), ensure_ascii=False, indent=1)
    json.dump(profiles, open(root / "agent_profiles.json", "w"), ensure_ascii=False, indent=1)
    json.dump(build_init_config(posts, persons, "reddit_hot"), open(root / "init_config.json", "w"), ensure_ascii=False, indent=1)
    (root / "steps.yaml").write_text(STEPS_YAML.format(start_t=START_T), encoding="utf-8")
    (root / "CONFIG_NOTES.md").write_text(
        CONFIG_NOTES_TMPL.format(
            algorithm="reddit_hot(策展基线)",
            summary_json=json.dumps(e1_summary, ensure_ascii=False, indent=2),
            pool_n=notes["pool_n"], window_total=notes["window_total_real"], scale=notes["scale"],
            start_t=START_T, event_start=EVENT_START_ISO,
        ),
        encoding="utf-8",
    )

    # E2(仅算法不同)
    e2_dir = root / args.e2_dir
    e2_dir.mkdir(parents=True, exist_ok=True)
    stale = e2_dir / "config_params.py"
    if stale.exists():
        stale.unlink()  # 防 drift:E2 由 E1 生成器统一产出
    e2_summary = dict(e1_summary, recommendation_algorithm="chronological")
    json.dump(posts, open(e2_dir / "supply_pool.json", "w"), ensure_ascii=False, indent=1)
    json.dump(profiles, open(e2_dir / "agent_profiles.json", "w"), ensure_ascii=False, indent=1)
    json.dump(build_init_config(posts, persons, "chronological"), open(e2_dir / "init_config.json", "w"), ensure_ascii=False, indent=1)
    (e2_dir / "steps.yaml").write_text(STEPS_YAML.format(start_t=START_T), encoding="utf-8")
    (e2_dir / "CONFIG_NOTES.md").write_text(
        CONFIG_NOTES_TMPL.format(
            algorithm="chronological(去策展化)",
            summary_json=json.dumps(e2_summary, ensure_ascii=False, indent=2),
            pool_n=notes["pool_n"], window_total=notes["window_total_real"], scale=notes["scale"],
            start_t=START_T, event_start=EVENT_START_ISO,
        ),
        encoding="utf-8",
    )

    print(f"pool={notes['pool_n']} media={notes['media_n']} scale={notes['scale']}")
    print("E1 ->", root)
    print("E2 ->", e2_dir)


if __name__ == "__main__":
    main()
