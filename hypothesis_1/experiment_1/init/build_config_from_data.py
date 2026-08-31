# 数据驱动试点配置生成器
# 依据 DATA_DRIVEN_DESIGN.md：真实打标数据 → 供给池采样 → init_config.json + steps.yaml
# 输出（本目录）: init_config.json / steps.yaml / supply_pool.json / CONFIG_NOTES.md
# 供给池缓存: supply_pool.json 存在时直接复用（避免重读 80MB xlsx）；删除后重新采样
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

INIT_DIR = Path(__file__).resolve().parent
DATA_DIR = INIT_DIR.parents[2] / "datasets" / "zhangxf_labeled"
PARQUET = DATA_DIR / "valid_posts_clusters.parquet"
XLSX = INIT_DIR.parents[2] / "抖音微博小红书-全量已打标.xlsx"
POOL_JSON = INIT_DIR / "supply_pool.json"
SEED = 42

# ---- 设计参数（DATA_DRIVEN_DESIGN.md §1.2 / §2.1）----
QUOTA = {
    "悼念颂扬": 28, "泛议论杂谈": 16, "巧乐兹雪碧梗": 20, "人生语录": 14,
    "死因健康科普": 12, "家庭教育观点": 12, "志愿填报干货": 10,
    "学习方法观点": 10, "公司接班后事": 8, "借势营销": 10,
}
TOPIC_CATEGORY = {
    "悼念颂扬": "mourning", "泛议论杂谈": "general", "巧乐兹雪碧梗": "meme",
    "人生语录": "quote", "死因健康科普": "health_info", "家庭教育观点": "edu_opinion",
    "志愿填报干货": "edu_practical", "学习方法观点": "study_method",
    "公司接班后事": "aftermath", "借势营销": "marketing",
}
# 死亡日前存量供给（pre-death 主题 created_at 设在 03-20~23）
PRE_DEATH_THEMES = {"志愿填报干货", "学习方法观点"}
T0 = datetime(2026, 3, 24, 8, 0, 0)

AUDIENCE_GROUPS = [  # (archetype, n, n_low_familiarity)
    ("抖音娱乐向", 30, 25), ("小红书共鸣向", 30, 15),
    ("教育关切向", 30, 10), ("热点吃瓜向", 10, 9),
]
PERSONA = {
    ("抖音娱乐向", "low"): "你是抖音重度用户，平时只刷短视频娱乐消遣，看到什么都先图一乐。你此前完全不知道张雪峰是谁，对他没有任何既有印象——今天是你第一次在信息流里刷到与他有关的内容，你也不知道他的职业背景。",
    ("抖音娱乐向", "high"): "你是抖音重度用户，平时只刷短视频娱乐消遣。你生前刷到过张雪峰的直播切片，知道他是讲考研和高考志愿的辅导老师，说话直、风格犀利，对他有些印象但谈不上喜欢或讨厌。",
    ("小红书共鸣向", "low"): "你是小红书用户，平时关注情感、生活方式和教育话题，容易被图文笔记打动，看到感人的内容会点赞收藏。你此前完全不了解张雪峰，对他没有任何既有印象——今天第一次刷到与他有关的内容。",
    ("小红书共鸣向", "high"): "你是小红书用户，平时关注情感、生活方式和教育话题。你看过张雪峰讲高考志愿和考研择校的笔记与直播切片，曾收藏过他的建议，对他有一定了解。",
    ("教育关切向", "low"): "你是一名学生家长或面临升学择业的大学生，正在为志愿填报、考研择校收集信息，关注教育干货。你此前完全不知道张雪峰，对他没有任何既有印象。",
    ("教育关切向", "high"): "你是一名学生家长或面临升学择业的大学生，正在为志愿填报、考研择校收集信息。你生前看过张雪峰的志愿填报直播，了解他的报考观点，认同其中一部分，也有保留。",
    ("热点吃瓜向", "low"): "你是热搜冲浪选手，什么热点都围观一下，主要图一乐，很少认真站队。你此前完全不知道张雪峰，对他没有任何既有印象。",
    ("热点吃瓜向", "high"): "你是热搜冲浪选手，什么热点都围观一下。你以前刷到过张雪峰的争议言论切片，对他印象一般。",
}


def clean_text(s: str, limit: int = 280) -> str:
    return " ".join(str(s).split())[:limit]


def sample_pool() -> list[dict]:
    """按配额从真实数据采样供给池（dup 加权，保留同质化结构）。"""
    rng = random.Random(SEED)
    df = pd.read_parquet(PARQUET)
    df = df[~df["is_noise"]].copy()
    df["content"] = df["content"].map(clean_text)
    df = df[df["content"].str.len() >= 15]

    # 借势营销（无效侧）从 xlsx 采样
    mkt = pd.read_excel(
        XLSX, usecols=["数据有效性", "内容类别", "media_type", "published_at", "content"])
    mkt = mkt[(mkt["数据有效性"] == "无效") & (mkt["内容类别"] == "借势营销")].copy()
    mkt["content"] = mkt["content"].map(clean_text)
    mkt = mkt[mkt["content"].str.len() >= 15]

    pool = []
    for theme, n in QUOTA.items():
        if theme == "借势营销":
            cand = mkt
            weights, meme_flags = None, [False] * len(cand)
        else:
            cand = df[df["theme"] == theme]
            weights = cand["dup"].tolist()
            meme_flags = cand["is_meme"].tolist()
        # 加权无放回采样（循环补齐去重）
        picked, seen = [], set()
        guard = 0
        while len(picked) < n and guard < 20 * n:
            i = rng.choices(range(len(cand)), weights=weights, k=1)[0] if weights else \
                rng.randrange(len(cand))
            guard += 1
            if i in seen:
                continue
            seen.add(i)
            picked.append(i)
        picked = picked[:n]
        for rank, i in enumerate(picked):
            row = cand.iloc[i]
            pool.append({
                "theme": theme,
                "platform": str(row["media_type"]),
                "is_meme": bool(meme_flags[i]),
                "dup": float(row.get("dup", 1.0)) if theme != "借势营销" else 1.0,
                "content": str(row["content"]),
                "_rank": rank,
            })
    rng.shuffle(pool)
    (POOL_JSON).write_text(json.dumps(pool, ensure_ascii=False, indent=1), encoding="utf-8")
    return pool


def load_pool() -> list[dict]:
    if POOL_JSON.exists():
        return json.loads(POOL_JSON.read_text(encoding="utf-8"))
    return sample_pool()


def build() -> None:
    pool = load_pool()

    # ---- persons：每主题 2 个真实作者化名代理（id 901 起）----
    themes = list(QUOTA)
    persons, person_of_theme = {}, {}
    pid = 901
    for theme in themes:
        person_of_theme[theme] = []
        for suffix in ("作者A", "作者B"):
            persons[str(pid)] = {
                "id": pid, "username": f"{theme}_{suffix}",
                "created_at": "2025-06-01T00:00:00",
            }
            person_of_theme[theme].append(pid)
            pid += 1

    # ---- posts：id 1..N，时间戳按主题曲线 ----
    posts, counters = {}, {"pre": 0, "day": 0, "mkt": 0}
    for i, item in enumerate(pool, start=1):
        theme = item["theme"]
        if theme in PRE_DEATH_THEMES:
            created = datetime(2026, 3, 20, 10, 0) + timedelta(minutes=47 * counters["pre"])
            counters["pre"] += 1
        elif theme == "借势营销":
            created = T0 + timedelta(hours=8, minutes=5 * counters["mkt"])
            counters["mkt"] += 1
        else:
            created = T0 + timedelta(minutes=3 * counters["day"])
            counters["day"] += 1
        tags = [theme, item["platform"]] + (["is_meme"] if item["is_meme"] else [])
        posts[str(i)] = {
            "post_id": i,
            "author_id": person_of_theme[theme][item["_rank"] % 2],
            "content": item["content"],
            "post_type": "original",
            "parent_id": None,
            "created_at": created.isoformat(),
            "likes_count": 0, "reposts_count": 0, "comments_count": 0, "view_count": 0,
            "tags": tags,
            "topic_category": TOPIC_CATEGORY[theme],
        }

    # ---- 100 受众 agent：archetype × 熟悉度 ----
    agents, pairs, aid = [], [], 1
    for arch, n, n_low in AUDIENCE_GROUPS:
        for j in range(n):
            fam = "low" if j < n_low else "high"
            tag = "低熟" if fam == "low" else "高熟"
            agents.append({
                "agent_id": aid, "agent_type": "PersonAgent",
                "kwargs": {
                    "id": aid, "name": f"{arch}{tag}{j + 1:02d}",
                    "persona": PERSONA[(arch, fam)],
                    "max_react_turns": 6, "enable_memory": True, "enable_todo_list": False,
                },
            })
            pairs.append([aid, f"{arch}{tag}{j + 1:02d}"])
            aid += 1

    config = {
        "env_modules": [{
            "module_type": "SocialMediaSpace",
            "kwargs": {
                "agent_id_name_pairs": pairs,
                "persons": persons,
                "posts": posts,
                "comments": {}, "follows": {}, "likes": {},
                "feed_source": "global",
                "polarization_mode": "none",
                "recommendation_algorithm": "chronological",  # 基线臂 A；对照臂换 reddit_hot/random
                "random_seed": SEED,
            },
        }],
        "agents": agents,
    }

    # ---- steps.yaml：T0 基线 → 4+4+4 ticks → T1/T2/T3 ----
    QUESTIONS = [
        {"id": "impression_words", "prompt": "用 3-5 个词描述你对「张雪峰」的印象。如果你此前没听说过他，请回答「没听说过」。",
         "response_type": "text"},
        {"id": "familiarity", "prompt": "你对张雪峰的熟悉程度（1=完全没听说过，5=非常熟悉）？",
         "response_type": "integer"},
        {"id": "impression_source", "prompt": "如果你对张雪峰有印象，你的印象主要来自哪里？",
         "response_type": "choice",
         "choices": ["生前视频/直播", "死亡事件相关短视频或帖子", "新闻报道", "朋友讨论", "没听说过/不适用"]},
        {"id": "occupation", "prompt": "在你印象中，张雪峰是做什么的？（没有印象请回答「不知道」）",
         "response_type": "text"},
    ]
    waves = [("T0_baseline", "基线问卷（曝光前，检验 persona 分组效度）"),
             ("T1_day4", "第 1 次曝光后（死亡冲击波衰减期）"),
             ("T2_day8", "第 2 次曝光后（梗供给占比稳定期）"),
             ("T3_day12", "第 3 次曝光后（窗口终点）")]
    step_lines = ["start_t: '2026-03-24T08:00:00'", "steps:"]
    for qid, desc in waves:
        step_lines += [
            f"- type: questionnaire",
            f"  questionnaire_id: {qid}",
            f"  title: {desc}",
            "  questions:",
        ]
        for q in QUESTIONS:
            step_lines += [
                f"  - id: {q['id']}",
                f"    prompt: \"{q['prompt']}\"",
                f"    response_type: {q['response_type']}",
            ]
            if q.get("choices"):
                step_lines.append("    choices: [" + ", ".join(q["choices"]) + "]")
        if qid != "T3_day12":
            step_lines += ["- num_steps: 4", "  tick: 1", "  type: run"]

    (INIT_DIR / "init_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (INIT_DIR / "steps.yaml").write_text("\n".join(step_lines) + "\n", encoding="utf-8")

    # ---- 汇总 ----
    n_meme = sum(1 for p in pool if p["is_meme"])
    theme_counts = {t: sum(1 for p in pool if p["theme"] == t) for t in themes}
    summary = {
        "seed": SEED,
        "pool_n": len(pool), "pool_is_meme": n_meme,
        "pool_theme_counts": theme_counts,
        "agents_n": len(agents),
        "low_familiarity_n": sum(nl for _, _, nl in AUDIENCE_GROUPS),
        "recommendation_algorithm": "chronological",
        "start_t": "2026-03-24T08:00:00", "run_ticks_total": 12,
        "questionnaires": [w[0] for w in waves],
    }
    (INIT_DIR / "CONFIG_NOTES.md").write_text(
        "# 试点配置生成记录\n\n```json\n"
        + json.dumps(summary, ensure_ascii=False, indent=2)
        + "\n```\n\n"
        "- 供给池：`supply_pool.json`（真实文本采样，dup 加权，seed=42；删除该文件可重采样）\n"
        "- 推荐臂：基线 `chronological`（臂 A）；Q1 三臂对照复制本配置仅改 `recommendation_algorithm`\n"
        "  （臂 B 个性化需 `douyin_space.py` 二期实现；臂 C `random`）\n"
        "- 试点简化：producer 不作为 LLM agent（静态存量供给池），详见 DATA_DRIVEN_DESIGN.md §2.3\n",
        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
