"""feed 推荐机制的共享纯函数（env 与校准脚本同源，避免"校准-仿真不同构"漂移）。

用户 2026-09-12 裁定（见 hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md）：
烟测暴露 interest 臂的两个机制缺陷，修复集中在"内容可得性 + 选择"两步，打分函数本身不变。

1. **帖子生命周期**（问题 1：老帖霸屏）：每帖有寿命，随时间冷却、被推得越多也越冷，
   寿终（life < 退场线）即退出候选池 —— 老帖不再永久霸占 feed。
2. **曝光饱和**（用户裁定的"曝光上限"落地形态）：硬上限会饿死早期 feed
   （W12 仅 47 帖，C=2 只供 94 槽位而当周需求 1000 槽位），故改为衰减项：
   一条内容被推给约 saturation_scale 人后吸引力减半，实现同一意图而无副作用。
3. **兴趣比例抽样**（问题 2：同类型 agent 共享同一份 top-10 → D 输入退化）：
   把"排序后取前 k"换成"按 exp(score/temperature) 无放回抽 k"，
   使每个 agent 的 10 条成为"比例的样本"，逐 agent 有梯度。

本模块只放纯函数（无状态、无 I/O、无随机源），env 与 calibrate_speak.py 同时 import，
以代码保证两条实现的逐值一致（校准脚本另加 G 序列断言）。
"""

from __future__ import annotations

import math
import re
from datetime import date, timedelta
from typing import Any, Mapping, Sequence

# ---------------- 文本归一化与词表命中（与 env 判类器/倾向分同源） ----------------

# 逐字移植 build_assets.py _EMOJI（emoji / 符号 / 国旗 / 变体选择器 / 零宽连接符）。
_EMOJI = re.compile(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️‍]")


def normalize(s: str) -> str:
    """逐字移植 build_assets.py normalize()：去 emoji 后剥掉所有非单词字符（保留 CJK+字母数字），小写。"""
    s = _EMOJI.sub("", str(s))
    return re.sub(r"[\W_]+", "", s).lower()


def hits(words: Sequence[str], layers: Sequence[str]) -> list[str]:
    """两层子串匹配命中词表（raw.lower() + normalize()）。"""
    return [w for w in words if any(w.lower() in l for l in layers)]


# 倾向分词表键（由 vocab JSON 提取；键名与 env 内部列表一一对应）。
TENDENCY_VOCAB_KEYS = (
    "mourning_main",
    "marketing_main",
    "education_main",
    "meme_linkage",
    "meme_strong",
    "meme_exclude_death_fact",
)


def vocab_lists_from_doc(vocab_doc: Mapping[str, Any]) -> dict[str, list[str]]:
    """从 vocabs.json 结构提取倾向分/判类所需的六份词表（与 env 同口径）。"""
    meme_v = dict(vocab_doc.get("meme") or {})
    return {
        "mourning_main": list((vocab_doc.get("mourning") or {}).get("main", []) or []),
        "marketing_main": list((vocab_doc.get("marketing") or {}).get("main", []) or []),
        "education_main": list((vocab_doc.get("education") or {}).get("main", []) or []),
        "meme_linkage": list(meme_v.get("linkage", []) or []),
        "meme_strong": list(meme_v.get("strong", []) or []),
        "meme_exclude_death_fact": list(meme_v.get("exclude_death_fact", []) or []),
    }


def compute_tendencies(text: str, vocab: Mapping[str, Sequence[str]]) -> dict[str, float]:
    """四类倾向分：各类型词表命中次数 ÷ 句长（命中/50 字），与判类器同口径两层匹配。

    用户裁定（2026-09-09）：帖子类型表征不由 LLM 解析，用词表命中次数与句子长度计算
    梗/教育/哀悼/营销倾向，作为兴趣推荐臂的匹配依据。meme 命中 = linkage 命中数 +
    死因词替换「□」后的 strong 命中数；其余主类 = main 命中数。返回各类密度值（≥0，4 位小数）。
    """
    raw = str(text)
    nrm = normalize(raw)
    layers = [raw.lower(), nrm]
    stripped = list(layers)
    for w in vocab.get("meme_exclude_death_fact", ()) or ():
        stripped = [s.replace(w.lower(), "□") for s in stripped]
    cnt = {
        "mourning": len(hits(vocab.get("mourning_main", ()) or (), layers)),
        "marketing": len(hits(vocab.get("marketing_main", ()) or (), layers)),
        "education": len(hits(vocab.get("education_main", ()) or (), layers)),
        "meme": len(hits(vocab.get("meme_linkage", ()) or (), layers))
        + sum(
            1 for w in (vocab.get("meme_strong", ()) or ())
            if any(w.lower() in l for l in stripped)
        ),
    }
    norm_len = max(1.0, len(raw) / 50.0)
    return {t: round(h / norm_len, 4) for t, h in cnt.items()}

# ---------------- ISO 周工具（唯一的周序数来源，env 的 _week_ord 委托到此处） ----------------

_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
_EPOCH_MONDAY = date(2026, 1, 5)  # 固定周一锚点（2026-01-05），用于 ISO 周序数比较


def week_monday(week: str) -> date:
    """ISO 周标签 → 该周周一（ISO 8601 算法：1 月 4 日所在周为第 1 周）。"""
    m = _WEEK_RE.match(str(week))
    if not m:
        raise ValueError(f"invalid ISO week label: {week!r}")
    y, w = int(m.group(1)), int(m.group(2))
    jan4 = date(y, 1, 4)
    return jan4 - timedelta(days=jan4.isoweekday() - 1) + timedelta(weeks=w - 1)


def week_add(week: str, n: int) -> str:
    """ISO 周标签偏移 n 周（2026-03~05 窗口无跨年问题，通用实现）。"""
    d = week_monday(week) + timedelta(weeks=n)
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def week_ord(week: str) -> int:
    """ISO 周标签 → 周序数（自 _EPOCH_MONDAY 起的周数，仅用于比较）。"""
    return (week_monday(week) - _EPOCH_MONDAY).days // 7


def age_weeks(current_week: str, post_week: str) -> int:
    """帖龄（周）：本周与产出周的周序数之差，同周为 0（不小于 0）。"""
    return max(0, week_ord(current_week) - week_ord(post_week))


# ---------------- 帖子生命周期 ----------------

# 默认参数（env kwargs 与校准脚本共用同一套默认值；改这里即同时改两条实现）。
DEFAULT_HALF_LIFE_WEEKS = 1.5      # 时间冷却半衰期（周）
DEFAULT_SATURATION_SCALE = 20.0    # 曝光饱和尺度：累计曝光达该值时生命折半
DEFAULT_RETIRE_FLOOR = 0.35        # 生命低于该值的帖退出候选池（≈3 周流通窗口：age 0/1/2）


def weekly_decay(half_life_weeks: float) -> float:
    """每周的时间冷却步长 = 0.5 ** (1 / 半衰期)（half_life<=0 视为不冷却，恒 1）。"""
    if half_life_weeks is None or half_life_weeks <= 0:
        return 1.0
    return 0.5 ** (1.0 / float(half_life_weeks))


def life_at_age(age: int, half_life_weeks: float) -> float:
    """由帖龄直接算时间生命（= 逐周乘 weekly_decay 的累积结果，用于校验/老 checkpoint 回填）。"""
    if half_life_weeks is None or half_life_weeks <= 0:
        return 1.0
    return 0.5 ** (float(age) / float(half_life_weeks))


def exposure_saturation(exposure_count: int, saturation_scale: float) -> float:
    """曝光饱和因子：0.5 ** (累计曝光 / 尺度)；尺度<=0 视为不饱和（恒 1）。"""
    if saturation_scale is None or saturation_scale <= 0:
        return 1.0
    return 0.5 ** (float(exposure_count) / float(saturation_scale))


def post_vitality(
    life: float,
    exposure_count: int,
    saturation_scale: float = DEFAULT_SATURATION_SCALE,
) -> float:
    """帖子生命力 = 时间生命（逐帖状态）× 曝光饱和（按累计曝光现算），取值 (0, 1]。

    两者共用"半衰"语义：1.5 周龄折半、被推给约 20 人折半；
    又老又已被推很多次的帖生命力迅速趋零，自然让出视野。
    曝光项现算而非缓存：同一 tick 内为 100 个 agent 依次装配 feed 时，
    先被抽中的帖其后续边际权重即行下降（抑制单帖在同周垄断）。
    """
    return float(life) * exposure_saturation(exposure_count, saturation_scale)


def is_retired(life: float, retire_floor: float = DEFAULT_RETIRE_FLOOR) -> bool:
    """时间生命低于退场线的帖退出候选池（默认 0.35 ≈ 3 周流通窗口，等效于候选窗口）。

    只按时间生命退场、不按曝光饱和退场：避免把"被推得多"的高热帖提前踢出池子
    而使池子在后期（总曝光远超池容量时）塌缩。
    """
    return float(life) < float(retire_floor)


# ---------------- 议程保底候选资格 ----------------

# 事件周议程保底的候选池过滤（用户 2026-09-13 裁定，方案 B）。
# 保底按"哀悼倾向分"排序，而倾向分 = 命中数/(字数/50)，短文本密度天然偏高：
# 实测（s0–s2）曾有 1 张 35–98 字的语料噪声帖（type=noise，乱码/广告拼接）挤进
# 全员强制位。机制上 noise 不是"话语"，平台级议程规则不会把它推给全员。
# 故从保底候选池中剔除 noise；其余类型（含 other/marketing 的哀悼相关帖）仍按倾向分参与。
# 类型不硬限定为 mourning：同 N=5 下"仅取 mourning 类型"档 W13 悼念份额 0.555，
# 比本口径 0.515 更差（Δ+0.141 vs +0.101），故不采用。
# 效应量提示：**本条过滤几乎不影响结果**（开关对照 |Δ| ≤ 0.01 且符号不定，小于 seed 间噪声），
# 它是口径清理（避免平台规则把语料噪声推给全员），不是标定杠杆。
# 事件周水平几乎完全由**保底条数 N** 决定——N≥2 时 W13 悼念帖数恒为 22.0（悼念型全员发言），
# 份额变化来自分母（非悼念类型被议程压到门槛下）；N 的取值待用户裁定（见 EXPERIMENT.md）。
DEFAULT_EVENT_FLOOR_EXCLUDE_TYPES: tuple[str, ...] = ("noise",)


def floor_eligible(post_type: str,
                   exclude_types: Sequence[str] = DEFAULT_EVENT_FLOOR_EXCLUDE_TYPES) -> bool:
    """该帖是否有资格进入事件周议程保底候选池（纯函数，env 与校准脚本同源）。

    仅排除语料噪声类；不限定必须为 mourning 类型（见上方裁定说明）。
    """
    return str(post_type) not in tuple(exclude_types)


# ---------------- 兴趣打分 ----------------

def interest_score(
    tendency_value: float,
    alpha: float,
    gamma: float,
    vitality: float,
) -> float:
    """interest 臂打分：`(α·本类倾向分 + γ) · 生命力`。

    相对烟测前的改动只有一处：时新项从**加性加成** `γ·max(0, 1−age/max_age)`
    （8 周后归零但不降权，故老帖仍以 α·T 竞争）改为**乘性生命力**
    （老帖整体打折并最终退场）。α 仍是倾向分权重，γ 成为新鲜度基准项。
    仍无任何帖子级热度/互动项——纯兴趣匹配的最小机制不变。
    """
    return (float(alpha) * float(tendency_value) + float(gamma)) * float(vitality)


# ---------------- 沉默螺旋（D 因子） ----------------

# 有界共振因子：D = 1 + s·tanh(k·(share − base)/base)。
# 2026-09-12 用户裁定（依据见 hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md §五之四）：
# 原实现 `clamp(1 + s·x, 0.05, 2.0)` 的线性 + 地板是自造的，且地板在行为上不可观测
# （抬到 0.3/0.5/0.7 结果逐周相同），真实副作用是"气候不利时把所有类型压成同一个值、
# 抹掉 spiral 参数的类间差异"。改为有界 tanh 后：
#   * 无地板、有界 [1−s, 1+s]、单调、边际效应递减；
#   * 负值段 = 表达净成本（"孤立成本"，对应 Blanco 2005 博弈式中的 −c；发言门槛
#     = c/(b+c) 的门槛结构与本模型 U ≥ activity 同构）；
#   * 有界平滑的映射与文献里的 logistic 传统一致（Sohn & Geidner 2015 的 δ 逻辑式、
#     Cabrera et al. 2021 的置信度 logistic 更新），且个体阈值抖动对应 Granovetter 阈值分布。
DEFAULT_SPIRAL_K = 1.5


def spiral_factor(
    share_own: float,
    base: float,
    spiral: float,
    k: float = DEFAULT_SPIRAL_K,
) -> float:
    """沉默螺旋共振/抑制因子 D（用户 2026-09-12 裁定：有界 tanh，无地板）。

    share_own = agent 本周 feed 中本类内容占比（**感知**气候，符合"感知气候与实际意见
    分开测量"的规范）；base = 本类型在群体中的份额（参照点）；spiral = 个体敏感度 s。
    D > 1 表示同类气候共振放大表达收益，D < 1 表示少数派处境抑制收益，D < 0 表示
    表达存在净成本（孤立成本）。k 控制过渡陡度（默认 1.5）。
    """
    gap = (float(share_own) - float(base)) / max(float(base), 0.05)
    return 1.0 + float(spiral) * math.tanh(float(k) * gap)


# ---------------- 注意力衰减（R 因子） ----------------

# R = exp(−λ·cum_own/scale)：重复同类曝光带来的边际表达收益递减（疲劳）。
# 2026-09-12 用户裁定：半饱和尺度 50 → 20（λ 等效 ×2.5，"让退潮显现"）；
# 2026-09-13 进一步下压到 **15**（λ 等效 ×3.33）——用户要求"R 力度再大一些"，
# 代理实测（新群体 19/22/23/15/21 + W13 保底 + 营销 λ=0.05）：玩梗 W22 0.608 vs 真实 0.603、
# W13 悼念 0.456 vs 0.414。依据（原始）：
#   ① 真实平台总量是深 V（W13 11394 → W18 1703，6.7 倍衰减 → W22 5338），而模拟的周总产量
#      几乎平（52→45→44）—— R 太弱、事件后疲劳退潮没显现；
#   ② 增强 R 让趋势变陡，锯齿（抽样噪声，绝对幅度不变）相对不显眼：信噪比 0.45 → 0.82；
#   ③ 核心效标（combined 口径玩梗份额 W19–W22 vs 真实）拟合误差 RMSE 0.132 → **0.043**（最优档），
#      ×3 及以上会在 W22 过冲。
# 机制：R 增强 → 其他类型更快退潮 → 份额分母缩小 → 玩梗份额被动抬升；玩梗型累计曝光起步晚，
# 二波不受损。详见 hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md §五之五。
# 注：scale 是模型级形状常数（非 agent 参数）；λ=decay 仍是每 agent 一份的个体参数。
DEFAULT_DECAY_SCALE = 15.0


def fatigue_factor(
    decay: float,
    cum_own: float,
    scale: float = DEFAULT_DECAY_SCALE,
) -> float:
    """注意力衰减因子 R（收益侧折减），用户 2026-09-12/13 裁定尺度 50 → 20 → **15**。

    decay(λ) = 该 agent 的疲劳速度（个体参数）；cum_own = 该 agent 累计见到的本类型曝光数。
    cum_own ≈ scale 时 R ≈ e^(−λ)。尺度 15 ≈ "一周半活跃曝光"即进入明显疲劳。
    纯函数：agent 与 calibrate_speak.py 共用同一实现，保证校准-仿真同构。
    """
    return math.exp(-float(decay) * float(cum_own) / float(scale))


def anchored_utility(
    baseline_utility: float,
    spiral_factor_value: float,
    fatigue_factor_value: float,
) -> float:
    """锚定式表达效用 ``U = B + R * (D - B)``。

    ``B`` 是事件前常态表达效用锚点，区别于环境观测量中的存量丰沛度 ``B_t``；
    ``D`` 是沉默螺旋形成的当周意见气候效用；``R`` 是注意力衰减因子。因而
    ``R=1`` 时 ``U=D``，``R=0`` 时 ``U=B``，疲劳只让事件冲击回归常态锚点，
    不再把表达效用机械压到零。

    该纯函数由正式 Agent 与数值校准器共用，防止代理和仿真实现漂移。
    """
    baseline = float(baseline_utility)
    spiral = float(spiral_factor_value)
    fatigue = float(fatigue_factor_value)
    return baseline + fatigue * (spiral - baseline)


# ---------------- 比例抽样（选择步骤） ----------------

def softmax_weights(scores: Sequence[float], temperature: float) -> list[float]:
    """分数 → 抽样权重 exp(score / temperature)，减最大值以保证数值稳定。

    temperature <= 0 时返回"确定性 top-k"所需的单位权重占位（调用方须改走排序路径），
    此处仍返回全 1 以避免除零。
    """
    if temperature is None or temperature <= 0:
        return [1.0] * len(scores)
    t = float(temperature)
    if not scores:
        return []
    mx = max(scores)
    return [math.exp((float(s) - mx) / t) for s in scores]


def weighted_sample_without_replacement(
    items: Sequence[Any],
    weights: Sequence[float],
    k: int,
    rng: Any,
) -> list[Any]:
    """按权重无放回抽 k 个（Plackett–Luce / 顺序抽样）。rng 需有 random()。

    无放回保证一个 agent 的 feed 内不重复；跨 agent 不做限制（同一帖可被不同 agent
    各自抽到，但权重与曝光饱和项使其边际吸引力递减）。
    """
    pool = [(items[i], float(weights[i])) for i in range(len(items))]
    total = sum(w for _, w in pool)
    out: list[Any] = []
    k = max(0, min(int(k), len(pool)))
    while len(out) < k and pool:
        if total <= 0:  # 全零权重：退化为均匀抽样
            idx = rng.randrange(len(pool))
        else:
            r = rng.random() * total
            acc = 0.0
            idx = len(pool) - 1
            for i, (_, w) in enumerate(pool):
                acc += w
                if acc >= r:
                    idx = i
                    break
        item, w = pool.pop(idx)
        total -= w
        out.append(item)
    return out
