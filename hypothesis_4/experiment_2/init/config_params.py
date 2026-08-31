"""配置参数生成脚本 — H3 群体差异试点（100 agents，单 run 双组）

假设 3：圈外群体（低熟）vs 圈内群体（高熟）认知偏移差异；两组共存于同一 run，
环境/供给/推荐器完全一致（DATA_DRIVEN_DESIGN.md v0.2）。

persona：5 特征族 × 个体特征权重交叉（平台无关），熟悉度与特征族正交。
生成 init_config.json / steps.yaml / agent_profiles.json / CONFIG_NOTES.md。
仅用标准库：供给池读缓存的 supply_pool.json（生成器版本见 git 历史中的
build_config_from_data.py，需 pandas 采样 xlsx）。
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

script_dir = Path(__file__).parent
POOL_JSON = script_dir / "supply_pool.json"
SEED = 42
N_AGENTS = 100

# ============================================
# 1. 供给池 → persons / posts（沿用 v0.1 逻辑）
# ============================================
QUOTA_THEMES = [
    "悼念颂扬", "泛议论杂谈", "巧乐兹雪碧梗", "人生语录", "死因健康科普",
    "家庭教育观点", "志愿填报干货", "学习方法观点", "公司接班后事", "借势营销",
]
TOPIC_CATEGORY = {
    "悼念颂扬": "mourning", "泛议论杂谈": "general", "巧乐兹雪碧梗": "meme",
    "人生语录": "quote", "死因健康科普": "health_info", "家庭教育观点": "edu_opinion",
    "志愿填报干货": "edu_practical", "学习方法观点": "study_method",
    "公司接班后事": "aftermath", "借势营销": "marketing",
}
PRE_DEATH_THEMES = {"志愿填报干货", "学习方法观点"}
T0 = datetime(2026, 3, 24, 8, 0, 0)


def build_env(pool: list[dict]) -> dict:
    persons, person_of_theme = {}, {}
    pid = 901
    for theme in QUOTA_THEMES:
        person_of_theme[theme] = []
        for suffix in ("作者A", "作者B"):
            persons[str(pid)] = {
                "id": pid, "username": f"{theme}_{suffix}",
                "created_at": "2025-06-01T00:00:00",
            }
            person_of_theme[theme].append(pid)
            pid += 1

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

    return {"persons": persons, "posts": posts}


# ============================================
# 2. persona：5 特征族 × 个体特征权重交叉（v0.2）
# ============================================
# 族 → (中文名, n, 梗倾向, n_low_familiarity)
FAMILIES = {
    "meme":     ("玩梗", 23, 0.78, 12),
    "mourning": ("悼念", 29, 0.16, 15),
    "edu":      ("教育", 27, 0.08, 13),
    "reflect":  ("反思", 8, 0.35, 4),
    "casual":   ("吃瓜", 13, 0.08, 6),
}
FAMILY_CN = {k: v[0] for k, v in FAMILIES.items()}

# 风味（族内二级分化，来自簇内占比）→ (风味名, 占比, [背景句变体])
FLAVORS = {
    "meme": [
        ("重度玩梗", 0.73, [
            "你平时一有空就刷短视频，看到好笑的内容必凑热闹，热梗出来第二天就会用，聊天也爱带梗，评论区的段子手里有你一个。",
            "你是短视频重度用户，以玩梗为乐，追热点就是为了参与造梗，看到有趣的帖子忍不住整活。",
        ]),
        ("轻度玩梗", 0.27, [
            "你平时刷短视频娱乐消遣，遇到特别好笑的梗会跟着玩两句，但不会刻意追梗。",
            "你爱刷搞笑内容，偶尔在朋友群里转发梗图，算轻度跟梗用户。",
        ]),
    ],
    "mourning": [
        ("个人惋惜", 0.46, [
            "你平时关注生活情感类内容，看到意外的噩耗会停下来叹口气，为一条生命的逝去感到惋惜。",
            "你刷到新闻容易感性先行，对突然离世的消息尤其敏感，会真诚表达难过。",
        ]),
        ("严肃追思", 0.19, [
            "你尊重认真做事的人，逝者生前的行业贡献会引发你真挚的敬意与追思。",
            "你看重一个人的品行与事业，愿意认真回顾逝者一生所为。",
        ]),
        ("悼念加教育", 0.18, [
            "你平时关注教育话题，对逝者的追念会自然联想到他留下的观点与建议。",
        ]),
        ("学子惋惜", 0.16, [
            "你曾受惠于别人的指点，对'一位帮过很多学生的老师离世'这类消息心怀感慨。",
        ]),
    ],
    "edu": [
        ("教育关怀", 0.25, ["你关心老师和学生的处境，平时会看教育新闻，为师生群体发声。"]),
        ("观点讨论", 0.25, ["你爱讨论学历与努力的话题，对'读书有没有用'这类争议有自己的看法。"]),
        ("专业就业", 0.19, ["你正面临专业选择或就业决策，会主动搜集报考与求职信息。"]),
        ("大学学校", 0.16, ["你在了解大学与专业信息，关注各类学校的口碑。"]),
        ("基础课业", 0.08, ["你是中小学生的家长，关注孩子的课业与成长。"]),
        ("实用主义", 0.07, ["你信奉务实的生活哲学，觉得先挣钱养活自己比谈理想更实在。"]),
    ],
    "reflect": [
        ("健康过劳反思", 1.00, [
            "你关注健康养生话题，看到'猝死''过劳'这类新闻会认真点开，反思自己的作息。",
            "你平时留意健康知识，对熬夜、透支身体的讨论很有共鸣，也常提醒家人注意身体。",
        ]),
    ],
    "casual": [
        ("日常杂谈", 0.90, [
            "你把社交媒体当日常树洞，什么热点都看一眼，随手聊聊工作生活。",
            "你上网主要图个放松，各类话题都围观，偶尔插一句嘴。",
        ]),
        ("新闻议论", 0.10, ["你习惯刷新闻资讯，看到大事会到评论区看看大家怎么说。"]),
    ],
}

# 族间邻近权重（次级族采样概率 ∝ 此表；依据簇共现语义，见设计文档 §1.3）
ADJACENCY = {
    ("mourning", "reflect"): 0.35, ("meme", "casual"): 0.35,
    ("mourning", "edu"): 0.30, ("edu", "casual"): 0.20,
    ("meme", "mourning"): 0.15, ("reflect", "edu"): 0.15,
    ("meme", "edu"): 0.10, ("reflect", "casual"): 0.10,
    ("mourning", "casual"): 0.10, ("meme", "reflect"): 0.05,
}
SECONDARY_SENTENCE = {
    "meme": "看到好笑的梗你也会跟着玩两句",
    "mourning": "你也为生命的逝去感到惋惜",
    "edu": "你也关注教育相关的讨论",
    "reflect": "你也留意过劳与健康的话题",
    "casual": "你也爱凑热闹看大家的议论",
}
EXPRESSION_BAND = {
    "high": "你表达直来直去，情绪来了就直接说，评论爱用夸张戏谑的说法。",
    "mid": "你表达有分寸，多数时候认真讨论，偶尔轻松调侃。",
    "low": "你表达平和克制，评论偏认真，基本不开玩笑。",
}
FAM_SENTENCE = {
    "low": "你此前完全不知道张雪峰是谁，对他没有任何既有印象，也不知道他的职业背景——今天是你第一次在信息流里刷到与他有关的内容。",
    "high_base": "你此前就知道张雪峰：他是有名的考研辅导老师，讲高考志愿填报和考研择校，说话直、风格犀利。",
}
VALENCE = [("认同", 0.40, "你看过他的一些直播切片，认同他讲的大部分观点，觉得他真诚、敢说真话。"),
           ("无感", 0.35, "你刷到过他的视频，对他谈不上喜欢或讨厌，印象比较淡。"),
           ("有保留", 0.25, "你看过他的部分言论，觉得他有些话过于功利绝对，对他有保留意见。")]


def adj_weight(a: str, b: str) -> float:
    return ADJACENCY.get((a, b), ADJACENCY.get((b, a), 0.0))


def pick_weighted(rng: random.Random, pairs: list[tuple[str, float]]) -> str:
    total = sum(w for _, w in pairs)
    r = rng.random() * total
    acc = 0.0
    for k, w in pairs:
        acc += w
        if r <= acc:
            return k
    return pairs[-1][0]


def flavor_quota(n: int, flavor_defs: list) -> list[str]:
    """族内风味配额：最大余数法确定性分配，保证小风味不因随机被挤掉。"""
    raw = [(f[0], n * f[1]) for f in flavor_defs]
    counts = {k: int(v) for k, v in raw}
    short = n - sum(counts.values())
    by_rem = sorted(raw, key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for k, _ in by_rem[:short]:
        counts[k] += 1
    out = []
    for f in flavor_defs:
        out += [f[0]] * counts[f[0]]
    return out


def build_agents(rng: random.Random) -> tuple[list[dict], list[list[int, str]], list[dict]]:
    agents, pairs, profiles = [], [], []
    aid = 1
    for fam, (_, n, rate, n_low) in FAMILIES.items():
        # 熟悉度与风味：族内各配 n_low/n-n_low，两者独立打乱（解耦）
        fam_flags = ["low"] * n_low + ["high"] * (n - n_low)
        fam_flavors = flavor_quota(n, FLAVORS[fam])
        rng.shuffle(fam_flags)
        rng.shuffle(fam_flavors)
        cell_idx = {"low": 0, "high": 0}
        for j in range(n):
            familiarity = fam_flags[j]
            flavor = fam_flavors[j]
            bg = None
            for fname, _, variants in FLAVORS[fam]:
                if fname == flavor:
                    bg = variants[rng.randrange(len(variants))]
            # 次级族（80% 1 个，20% 2 个）
            cand = [(f2, adj_weight(fam, f2)) for f2 in FAMILIES if f2 != fam]
            cand = [(f2, w) for f2, w in cand if w > 0]
            n_sec = 2 if rng.random() < 0.20 else 1
            n_sec = min(n_sec, len(cand))
            secondaries, used = [], set()
            for _ in range(n_sec):
                choices = [(f2, w) for f2, w in cand if f2 not in used]
                if not choices:
                    break
                f2 = pick_weighted(rng, choices)
                used.add(f2)
                secondaries.append((f2, round(rng.uniform(0.15, 0.30), 2)))
            # 特征权重向量
            weights = {fam: 1.0 - sum(w for _, w in secondaries)}
            for f2, w in secondaries:
                weights[f2] = w
            tendency = round(sum(weights.get(f2, 0.0) * FAMILIES[f2][2]
                                 for f2 in FAMILIES), 3)
            band = "high" if tendency >= 0.45 else ("mid" if tendency >= 0.20 else "low")
            # persona 文本
            parts = [bg]
            for f2, _ in secondaries:
                parts.append(f"同时，{SECONDARY_SENTENCE[f2]}。")
            parts.append(EXPRESSION_BAND[band])
            if familiarity == "low":
                parts.append(FAM_SENTENCE["low"])
                valence = None
            else:
                r = rng.random()
                acc = 0.0
                valence, vsent = VALENCE[-1][0], VALENCE[-1][2]
                for vname, p, vs in VALENCE:
                    acc += p
                    if r <= acc:
                        valence, vsent = vname, vs
                        break
                parts.append(FAM_SENTENCE["high_base"] + vsent)
            persona = "".join(parts)
            tag = "低" if familiarity == "low" else "高"
            cell_idx[familiarity] += 1
            name = f"{FAMILY_CN[fam]}{tag}{cell_idx[familiarity]:02d}"
            agents.append({
                "agent_id": aid, "agent_type": "PersonAgent",
                "kwargs": {
                    "id": aid, "name": name, "persona": persona,
                    "max_react_turns": 6, "enable_memory": True, "enable_todo_list": False,
                },
            })
            pairs.append([aid, name])
            profiles.append({
                "agent_id": aid, "name": name, "family": fam, "flavor": flavor,
                "trait_weights": weights, "meme_tendency": tendency, "meme_band": band,
                "familiarity": familiarity, "attitude_valence": valence,
            })
            aid += 1
    return agents, pairs, profiles


# ============================================
# 3. steps.yaml（T0 基线 → 4+4+4 ticks → T1/T2/T3）
# ============================================
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
WAVES = [("T0_baseline", "基线问卷（曝光前，检验分组效度）"),
         ("T1_day4", "第 1 次曝光后（死亡冲击波衰减期）"),
         ("T2_day8", "第 2 次曝光后（梗供给占比稳定期）"),
         ("T3_day12", "第 3 次曝光后（窗口终点）")]


def build_steps() -> str:
    lines = ["start_t: '2026-03-24T08:00:00'", "steps:"]
    for qid, desc in WAVES:
        lines += [f"- type: questionnaire",
                  f"  questionnaire_id: {qid}",
                  f"  title: {desc}",
                  "  questions:"]
        for q in QUESTIONS:
            lines += [f"  - id: {q['id']}",
                      f"    prompt: \"{q['prompt']}\"",
                      f"    response_type: {q['response_type']}"]
            if q.get("choices"):
                lines.append("    choices: [" + ", ".join(q["choices"]) + "]")
        if qid != "T3_day12":
            lines += ["- num_steps: 4", "  tick: 1", "  type: run"]
    return "\n".join(lines) + "\n"


def main() -> None:
    rng = random.Random(SEED)
    pool = json.loads(POOL_JSON.read_text(encoding="utf-8"))
    env = build_env(pool)
    agents, pairs, profiles = build_agents(rng)

    config = {
        "env_modules": [{
            "module_type": "SocialMediaSpace",
            "kwargs": {
                "agent_id_name_pairs": pairs,
                "persons": env["persons"],
                "posts": env["posts"],
                "comments": {}, "follows": {}, "likes": {},
                "feed_source": "global",
                "polarization_mode": "none",
                # H4 去策展化臂：时间线排序（移除热度加权策展信号）；
                # 与策展基线（hypothesis_3/experiment_1, reddit_hot）唯一差异在此
                "recommendation_algorithm": "chronological",
                "random_seed": SEED,
            },
        }],
        "agents": agents,
    }
    (script_dir / "init_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (script_dir / "steps.yaml").write_text(build_steps(), encoding="utf-8")
    (script_dir / "agent_profiles.json").write_text(
        json.dumps(profiles, ensure_ascii=False, indent=1), encoding="utf-8")

    n_low = sum(1 for p in profiles if p["familiarity"] == "low")
    fam_counts = {f: sum(1 for p in profiles if p["family"] == f) for f in FAMILIES}
    flavor_counts = {}
    for p in profiles:
        key = (p["family"], p["flavor"])
        flavor_counts[f"{key[0]}/{key[1]}"] = flavor_counts.get(f"{key[0]}/{key[1]}", 0) + 1
    sec_frac = sum(1 for p in profiles if len(p["trait_weights"]) > 1) / len(profiles)
    band_counts = {b: sum(1 for p in profiles if p["meme_band"] == b)
                   for b in ("high", "mid", "low")}
    summary = {
        "design": "DATA_DRIVEN_DESIGN.md v0.2（H3 单 run 双组，5 特征族 × 个体交叉）",
        "seed": SEED,
        "pool_n": len(pool),
        "agents_n": len(agents),
        "familiarity": {"low": n_low, "high": len(agents) - n_low},
        "family_counts": fam_counts,
        "flavor_counts": flavor_counts,
        "agents_with_secondary_traits": round(sec_frac, 3),
        "meme_band_counts": band_counts,
        "recommendation_algorithm": "chronological",
        "start_t": "2026-03-24T08:00:00",
        "run_ticks_total": 12,
        "questionnaires": [w[0] for w in WAVES],
    }
    (script_dir / "CONFIG_NOTES.md").write_text(
        "# 试点配置生成记录（v0.2）\n\n```json\n"
        + json.dumps(summary, ensure_ascii=False, indent=2)
        + "\n```\n\n"
        "- persona：5 特征族 × 个体特征权重交叉（无平台维度），详见 ../DATA_DRIVEN_DESIGN.md\n"
        "- 供给池：`supply_pool.json`（自 hypothesis_1 原样迁移，140 条真实文本，seed=42）\n"
        "- 分组：`agent_profiles.json` 的 `familiarity` 字段（低熟=圈外 / 高熟=圈内），\n"
        "  与特征族正交（族内分层等比分配）\n"
        "- 推荐算法：`chronological`（H4 去策展化处理臂；基线见 hypothesis_3/experiment_1）\n",
        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
