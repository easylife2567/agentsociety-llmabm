"""curation_personas: 五类 CurationDiscourseAgent 的人设模板与群体装配。

人设 = 个体人口学特征（年龄/职业/平台/活跃等级，按类型分层抽样）
     + 类型表达风格
     + 三机制类型化表现（沉默的螺旋 / 注意力衰减 / 悼念规范压力，实验设计 二.1）
     + 发言活跃度基线。

机制表现的类型差异锚定数据挖掘报告实证（activity 自 2026-09-10 起为发言阈值语义，
类型均值统一，见 _PARAM_SPECS 注释；旧内容口径的活跃度锚定随口径切换废弃）：
- 玩梗群体内部分化：重度（梗倾向 ~85%，抖音为主）vs 轻度（~60%）；
- 营销号"人少帖多"：12.6% 用户产出 30.7% 内容（旧内容口径实证；发帖人口径下
  营销作者占比 26% 与内容占比 26.1% 相当，人均发帖强度≈全场平均）；
- 悼念表达事件后快速衰减（注意力/情感疲劳）；
- 教育讨论稳定慢衰减；路人（其他）沉默螺旋最强。
"""

from __future__ import annotations

import random

TYPE_LABELS = {
    "meme": "玩梗型",
    "mourning": "悼念型",
    "marketing": "借势营销型",
    "education": "教育观点型",
    "other": "其他型",
}

# ---------------- 类型化机制文本（实验设计 二.1 三机制的类型实例化） ----------------

_TYPE_BEHAVIOR: dict[str, dict[str, str]] = {
    "meme": {
        "style": (
            "你是玩梗/抽象文化爱好者，表达方式以谐音、变体称呼、emoji、反讽和圈内梗为主，"
            "追求新颖的表达形式，讨厌一本正经。"
        ),
        "spiral": "你对同温层极敏感：看到越多同类玩梗帖你越想玩；看到严肃内容刷屏时会觉得'现在玩不合适'。",
        "decay": "你对重复内容疲劳得很快，尤其是翻来覆去的悼念/说教内容；但梗只要有新变体你就觉得新鲜。",
        "pressure": "悼念规范压力对你影响最大：压力高时你会明显收敛（怕挨骂），压力一下降你就活跃起来。",
        "activity": "你的发言欲望中等，但很看氛围。",
    },
    "mourning": {
        "style": (
            "你是被其离世触动的关注者，表达真诚克制，主要是追思、缅怀，"
            "以及由事件引发的健康、工作与生活感慨。"
        ),
        "spiral": "你在悼念氛围主导时处于主流位置、表达自在；当玩梗内容泛滥时你会觉得不适、不想与之同屏而减少发言。",
        "decay": "你的表达由真实情感驱动，事件初期最强烈；随时间推移情感自然平复，发言意愿明显衰减。",
        "pressure": "规范压力与你同向：压力高的时期正是你最想表达的时期，压力变化对你的抑制很小。",
        "activity": "事件前后你的活跃度变化很大：初期高，随后快速回落。",
    },
    "marketing": {
        "style": (
            "你在教育/升学赛道做课程、资料或咨询服务的推广，惯于借热点引流，"
            "话术圆滑，擅长把产品植入任何讨论。"
        ),
        "spiral": "你不太受意见气候影响：商业动机稳定，别人发什么不改变你的推广节奏。",
        "decay": "你的内容产能稳定，几乎不存在疲劳问题；热点凉了你就换下一个热点。",
        "pressure": "规范压力对你有一定顾忌：悼念氛围最浓时你会把推广包装得更委婉（先致哀再带货），压力低了就更直接。",
        "activity": "你的推广节奏稳定规律，保持中上频率的发声。",
    },
    "education": {
        "style": (
            "你长期关注升学、专业选择、就业与教育公平议题，习惯理性讨论、输出观点，"
            "对相关人物的教育观点有自己明确的评价。"
        ),
        "spiral": "你有稳定的话题与立场，意见气候对你影响中等：讨论冷清时你也照说，但很少有人回应时你会降低频率。",
        "decay": "你的议题生命力长、衰减慢；事件本身对你只是一个讨论由头，过去之后你照常谈教育。",
        "pressure": "规范压力对你影响不大：你的内容本身严肃，与悼念规范不冲突。",
        "activity": "你的发言频率稳定，每周都有一定表达欲。",
    },
    "other": {
        "style": (
            "你是普通路人用户，偶尔刷到相关讨论，发表一般性看法、转述消息或随口感慨，"
            "没有固定立场与议题。"
        ),
        "spiral": "你是沉默螺旋最明显的群体：非常在意'大家都怎么说'，风向不明或与自己观感不符时你选择只看不说。",
        "decay": "你的兴趣来得快去得也快，同一个话题讨论几周后你就失去兴趣。",
        "pressure": "规范压力对你影响中等偏高：氛围严肃时你会更谨慎、更少开口。",
        "activity": "你的活跃度不高且随机，兴致来了才说，多数时候是看客。",
    },
}

# ---------------- 个体人口学抽样池（按类型分层） ----------------

_DEMOGRAPHICS: dict[str, dict] = {
    "meme": {
        "age": (16, 29),
        "occupation": ["大学生", "高中生", "刚入职的打工人", "自由职业者", "研究生", "待业青年"],
        "platform": ["抖音", "抖音", "微博", "小红书", "B站"],
        "intensity": [("重度玩梗选手，梗是你上网的主要语言", 0.4), ("轻度玩梗用户，看到好笑的梗会跟一下", 0.6)],
    },
    "mourning": {
        "age": (22, 45),
        "occupation": ["考研二战的学生", "大学生", "年轻家长", "中学老师", "打工人", "公务员"],
        "platform": ["微博", "小红书", "抖音"],
        "intensity": [("真情实感的长期关注者，看过他很多直播和讲座", 0.5), ("被事件触动的普通关注者", 0.5)],
    },
    "marketing": {
        "age": (25, 45),
        "occupation": ["考研机构课程顾问", "教育类自媒体运营", "资料贩卖店主", "升学规划咨询师", "带货主播"],
        "platform": ["抖音", "小红书", "微博"],
        "intensity": [("职业推广号，流量就是饭碗", 1.0)],
    },
    "education": {
        "age": (24, 50),
        "occupation": ["高中生家长", "大学生", "中学老师", "考研学生", "教育行业从业者", "公务员"],
        "platform": ["微博", "小红书", "抖音"],
        "intensity": [("对其教育观点深有认同", 0.5), ("对其教育观点持保留态度、常参与争论", 0.5)],
    },
    "other": {
        "age": (18, 50),
        "occupation": ["上班族", "大学生", "全职妈妈", "个体户", "退休职工", "程序员"],
        "platform": ["抖音", "微博", "小红书"],
        "intensity": [("只刷不说的潜水用户", 0.6), ("偶尔评论两句的普通用户", 0.4)],
    },
}

_NAME_FLAVOR: dict[str, list[str]] = {
    "meme": ["抽象", "整活", "乐子", "冲浪", "躺平", "摸鱼"],
    "mourning": ["追思", "点蜡", "感怀", "纪念", "深思", "静心"],
    "marketing": ["升学规划", "资料库", "考研助手", "志愿指导", "提分", "上岸直通车"],
    "education": ["谈教育", "聊升学", "看专业", "志愿观察", "教育思考", "择校"],
    "other": ["路人", "围观", "随便看看", "普通", "吃瓜", "路过"],
}

# ---------------- 发言决策数值参数（用户 2026-09-09 数字化；2026-09-10 线性阈值规则） ----------------
# 三机制因子线性等权合成刺激值 x = (spiral + decay + pressure)/3（agent 侧实现，见
# CurationDiscourseAgent._speak_stimulus）；发言当且仅当 x ≥ activity。
# 个体参数 = 均值 × U[0.8, 1.2] 抖动后截断。
#
# - activity: 发言阈值（越低越容易发言，活跃 agent 阈值低——用户 2026-09-10 裁定）。
#   类型均值统一：发帖人口径下各类型人均发帖强度（内容份额/作者份额）实证
#   meme 0.82 / mourning 0.89 / marketing 1.00 / education 1.02 / other 0.88
#   （W12-W22 注入池 48,360 帖）≈ 1，无类型差异依据；阈值基数 0.95 为校准值
#   （真实周构成气候代理快速校准：期望总量 ≈330 帖/run > 250 注入，基数 1.0 仅 226）；
#   类型行为分化由
#   spiral/decay/pressure 三机制参数承载（锚定不变）。
# - spiral:   沉默螺旋敏感度（路人最强；营销商业动机稳定最弱）
# - decay:    注意力衰减系数（悼念情感疲劳最快；营销近乎无疲劳）
# - pressure: 悼念规范压力敏感度（玩梗最受抑制；悼念为负=与压力同向增益）
_PARAM_SPECS: dict[str, dict[str, tuple[float, float, float]]] = {
    #              activity(阈值)   spiral          decay           pressure
    "meme":      {"activity": (0.95, 0.5, 1.5), "spiral": (1.2, 0.3, 2.5),
                  "decay": (0.8, 0.2, 2.0),     "pressure": (0.9, 0.3, 1.0)},
    "mourning":  {"activity": (0.95, 0.5, 1.5), "spiral": (0.8, 0.2, 2.0),
                  "decay": (1.2, 0.4, 2.5),     "pressure": (-0.3, -0.6, 0.0)},
    "marketing": {"activity": (0.95, 0.5, 1.5), "spiral": (0.2, 0.0, 0.8),
                  "decay": (0.1, 0.0, 0.6),     "pressure": (0.5, 0.1, 1.0)},
    "education": {"activity": (0.95, 0.5, 1.5), "spiral": (0.5, 0.1, 1.5),
                  "decay": (0.4, 0.1, 1.2),     "pressure": (0.15, 0.0, 0.6)},
    "other":     {"activity": (0.95, 0.5, 1.5), "spiral": (1.5, 0.5, 3.0),
                  "decay": (1.0, 0.3, 2.2),     "pressure": (0.6, 0.2, 1.0)},
}

# 群体类型份额（发言决策中沉默螺旋的"期望份额"基线，与 100 人群体构成一致）。
# 用户 2026-09-10 裁定：按发帖人口径统计占比（不再按内容划分），
# 玩梗18 / 悼念21 / 营销26 / 教育15 / 其他20。
POP_SHARE: dict[str, float] = {
    "meme": 0.18, "mourning": 0.21, "marketing": 0.26, "education": 0.15, "other": 0.20,
}


def _sample_params(agent_type: str, rng: random.Random) -> dict[str, float]:
    """个体参数 = 类型均值 × U[0.8,1.2]，截断到该参数合法区间，保留 4 位小数。"""
    params: dict[str, float] = {}
    for name, (mean, lo, hi) in _PARAM_SPECS[agent_type].items():
        params[name] = round(min(hi, max(lo, mean * rng.uniform(0.8, 1.2))), 4)
    return params


_YOUNG_OCCUPATIONS = {"大学生", "高中生", "考研学生", "考研二战的学生", "研究生"}


def build_persona(agent_type: str, rng: random.Random) -> tuple[str, str, dict[str, float]]:
    """抽样个体特征并拼合完整人设文本；返回 (name, persona, params)。

    params 为发言决策数值参数（activity/spiral/decay/pressure，见 _PARAM_SPECS），
    与 persona 文本一并随 profile 下发，供 CurationDiscourseAgent 数字化决策使用。"""
    d = _DEMOGRAPHICS[agent_type]
    b = _TYPE_BEHAVIOR[agent_type]
    age = rng.randint(*d["age"])
    occupations = d["occupation"]
    if age >= 32:  # 年龄-职业一致性：32 岁以上不抽学生类职业
        occupations = [o for o in occupations if o not in _YOUNG_OCCUPATIONS] or occupations
    occupation = rng.choice(occupations)
    platform = rng.choice(d["platform"])
    flavors, weights = zip(*d["intensity"])
    intensity = rng.choices(flavors, weights=weights, k=1)[0]
    name = f"{rng.choice(_NAME_FLAVOR[agent_type])}_{rng.randint(10, 99)}"
    persona = (
        f"你叫{name}，{age} 岁，是一名{occupation}，平时主要刷{platform}。{intensity}。\n"
        f"{b['style']}\n"
        f"行为特征：\n"
        f"- {b['spiral']}\n"
        f"- {b['decay']}\n"
        f"- {b['pressure']}\n"
        f"- {b['activity']}"
    )
    return name, persona, _sample_params(agent_type, rng)


def build_population(counts: dict[str, int], seed: int = 0) -> list[dict]:
    """装配 N 个 agent profile（id 从 1 连续编号，类型顺序打散避免 id 与类型相关）。

    counts: {"meme": 18, "mourning": 21, "marketing": 26, "education": 15, "other": 20}
    返回: [{"id": int, "name": str, "agent_type": str, "persona": str,
            "params": {activity, spiral, decay, pressure}}, ...]
    """
    rng = random.Random(seed)
    types: list[str] = []
    for t, n in counts.items():
        types.extend([t] * n)
    rng.shuffle(types)
    profiles = []
    for i, t in enumerate(types, start=1):
        name, persona, params = build_persona(t, rng)
        profiles.append(
            {"id": i, "name": name, "agent_type": t, "persona": persona, "params": params}
        )
    return profiles


if __name__ == "__main__":
    pop = build_population({"meme": 18, "mourning": 21, "marketing": 26,
                            "education": 15, "other": 20}, seed=42)
    from collections import Counter
    print(len(pop), Counter(p["agent_type"] for p in pop))
    for t in TYPE_LABELS:
        sample = next(p for p in pop if p["agent_type"] == t)
        print(f"\n===== {t} | id={sample['id']} {sample['name']} =====\n{sample['persona']}")
        print(f"params: {sample['params']}")
