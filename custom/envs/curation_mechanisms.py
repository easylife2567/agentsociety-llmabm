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
