"""舆论场数字表征转移模拟环境（CurationDynamicsSpace）。

实验背景：张雪峰 2026-03-24（2026-W13）去世后，三种推荐算法 × 两种悼念规范压力
（3×2 全因子 6 cells）下，100 个固定类型 Agent 的差异化激活与公共表征构成变化
（W12→W22 共 11 周）。Agent 每 tick 先通过 **get_feed(agent_id)** 读取本周推荐信息流
（feed）、意见气候、悼念规范压力与全局供给/曝光份额，再决定是否发言；发言通过
**create_post(agent_id, content)** 发布一篇类型由其固定 Agent 类型决定的内容（每 tick
至多 1 帖，重复调用无效）。

本模块仅继承 EnvBase（No-Inheritance Rule）；全部 @tool 在类体内重新实现。
判类器逐字移植 custom/envs/curation_assets/build_assets.py 的 normalize()/Tagger 语义。
"""

from __future__ import annotations

import asyncio
import json
import random
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, ClassVar, Optional

from agentsociety2.env import EnvBase, tool
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef
from agentsociety2.storage.workspace_state import atomic_write_text

logger = get_logger()

# 本模块自选的 workspace 布局：<workspace_root>/state/ENV_STATE.json
_STATE_REL = "state/ENV_STATE.json"

# 类型顺序（env 内部统一顺序；判类优先级另见 PRECEDENCE）。
TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other"]
TYPE_ORDER_ALL = TYPE_ORDER + ["noise"]

# 判类优先级：逐字移植 build_assets.py PRECEDENCE（悼念 > 营销 > 教育 > 玩梗，其余 other）。
PRECEDENCE = ["mourning", "marketing", "education", "meme"]


# ---------------- 判类器（与 build_assets.py 完全同源，勿改判定语义） ----------------

# 逐字移植 build_assets.py _EMOJI（emoji / 符号 / 国旗 / 变体选择器 / 零宽连接符）。
_EMOJI = re.compile(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️‍]")


def _normalize(s: str) -> str:
    """逐字移植 build_assets.py normalize()：去 emoji 后剥掉所有非单词字符（保留 CJK+字母数字），小写。"""
    s = _EMOJI.sub("", str(s))
    return re.sub(r"[\W_]+", "", s).lower()


_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
_EPOCH_MONDAY = date(2026, 1, 5)  # 固定周一锚点（2026-01-05），用于 ISO 周序数比较


def _week_monday(week: str) -> date:
    """ISO 周标签 → 该周周一（ISO 8601 算法：1 月 4 日所在周为第 1 周）。"""
    m = _WEEK_RE.match(str(week))
    if not m:
        raise ValueError(f"invalid ISO week label: {week!r}")
    y, w = int(m.group(1)), int(m.group(2))
    jan4 = date(y, 1, 4)
    return jan4 - timedelta(days=jan4.isoweekday() - 1) + timedelta(weeks=w - 1)


def _week_add(week: str, n: int) -> str:
    """ISO 周标签偏移 n 周（2026-03~05 窗口无跨年问题，通用实现）。"""
    d = _week_monday(week) + timedelta(weeks=n)
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _week_ord(week: str) -> int:
    """ISO 周标签 → 周序数（自 _EPOCH_MONDAY 起的周数，仅用于比较）。"""
    return (_week_monday(week) - _EPOCH_MONDAY).days // 7


def _rng_state_from_json(v: Any) -> Any:
    """把 JSON 反序列化后的 RNG getstate() 结构（list）递归还原为 tuple（random.setstate 要求）。"""
    if isinstance(v, list):
        return tuple(_rng_state_from_json(x) for x in v)
    return v


class CurationDynamicsSpace(EnvBase):
    """舆论场数字表征转移模拟环境：三种推荐算法 × 两种悼念规范压力（3×2 全因子 6 cells），
    100 个固定类型 Agent 的差异化激活与公共表征构成变化（张雪峰 2026-03-24 去世 W13，W12→W22 共 11 周）。"""

    # ---------------- Replay 列声明 ----------------
    # env 级：每 step 一行（主键 step=_step_index），43 列。
    _env_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("week", "TEXT", description="当前 tick 的 ISO 周标签"),
        ColumnDef("norm_pressure", "REAL", description="悼念规范压力 P_t"),
        ColumnDef("norm_pressure_level", "TEXT", description="P_t 等级 high/medium/low"),
        ColumnDef("total_supply", "INTEGER", description="本 tick 新增供给总数（agent 产出+注入）"),
        ColumnDef("agent_supply", "INTEGER", description="本 tick Agent 产出帖数"),
        ColumnDef("injected_count", "INTEGER", description="本 tick 注入帖数"),
        ColumnDef("supply_share_meme", "REAL", description="Agent 产出口径供给份额（分母=五类 agent 帖）"),
        ColumnDef("supply_share_mourning", "REAL", description="Agent 产出口径供给份额"),
        ColumnDef("supply_share_education", "REAL", description="Agent 产出口径供给份额"),
        ColumnDef("supply_share_marketing", "REAL", description="Agent 产出口径供给份额"),
        ColumnDef("supply_share_other", "REAL", description="Agent 产出口径供给份额"),
        ColumnDef("supply_share_all_meme", "REAL", description="combined 口径供给份额（注入+产出，分母含 noise，对齐 benchmark total）"),
        ColumnDef("supply_share_all_mourning", "REAL", description="combined 口径供给份额"),
        ColumnDef("supply_share_all_education", "REAL", description="combined 口径供给份额"),
        ColumnDef("supply_share_all_marketing", "REAL", description="combined 口径供给份额"),
        ColumnDef("supply_share_all_other", "REAL", description="combined 口径供给份额"),
        ColumnDef("supply_share_all_noise", "REAL", description="combined 口径供给份额"),
        ColumnDef("agent_supply_meme", "INTEGER", description="本 tick Agent 产出（按类型）"),
        ColumnDef("agent_supply_mourning", "INTEGER", description="本 tick Agent 产出（按类型）"),
        ColumnDef("agent_supply_education", "INTEGER", description="本 tick Agent 产出（按类型）"),
        ColumnDef("agent_supply_marketing", "INTEGER", description="本 tick Agent 产出（按类型）"),
        ColumnDef("agent_supply_other", "INTEGER", description="本 tick Agent 产出（按类型）"),
        ColumnDef("injected_meme", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("injected_mourning", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("injected_education", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("injected_marketing", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("injected_other", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("injected_noise", "INTEGER", description="本 tick 注入（按类型）"),
        ColumnDef("total_exposures", "INTEGER", description="本 tick 全部 Agent 的 feed 槽位总数（1 槽=1 次曝光）"),
        ColumnDef("exposure_share_meme", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_share_mourning", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_share_education", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_share_marketing", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_share_other", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_share_noise", "REAL", description="推荐服务口径曝光份额"),
        ColumnDef("exposure_meme", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("exposure_mourning", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("exposure_education", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("exposure_marketing", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("exposure_other", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("exposure_noise", "INTEGER", description="本 tick 曝光槽位（按类型）"),
        ColumnDef("official_posts_count", "INTEGER", description="本 tick 置顶集合中的官方帖数"),
        ColumnDef("official_exposure_slots", "INTEGER", description="本 tick 官方帖占据的 feed 槽位数"),
    ]

    # agent 级：每 step 每 agent 一行（主键 agent_id+step），20 列。
    _agent_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("agent_type", "TEXT", description="Agent 固定类型（全程不变）"),
        ColumnDef("spoke", "INTEGER", description="本 tick 是否发言"),
        ColumnDef("produced_type", "TEXT", description="发言时的产出类型（=agent_type；沉默为 NULL）"),
        ColumnDef("assigned_type", "TEXT", description="发言内容的四词表判类结果"),
        ColumnDef("type_mismatch", "INTEGER", description="判类结果与产出类型是否不一致"),
        ColumnDef("exposure_meme", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("exposure_mourning", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("exposure_education", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("exposure_marketing", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("exposure_other", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("exposure_noise", "INTEGER", description="本 tick 该 Agent feed 中类型槽位数"),
        ColumnDef("climate_meme", "REAL", description="该 Agent 所见意见气候（feed 类型分布）"),
        ColumnDef("climate_mourning", "REAL", description="该 Agent 所见意见气候"),
        ColumnDef("climate_education", "REAL", description="该 Agent 所见意见气候"),
        ColumnDef("climate_marketing", "REAL", description="该 Agent 所见意见气候"),
        ColumnDef("climate_other", "REAL", description="该 Agent 所见意见气候"),
        ColumnDef("climate_noise", "REAL", description="该 Agent 所见意见气候"),
        ColumnDef("norm_pressure_seen", "REAL", description="本 tick 该 Agent 看到的 P_t"),
        ColumnDef("norm_pressure_level_seen", "TEXT", description="本 tick 该 Agent 看到的 P_t 等级"),
        ColumnDef("feed_slots", "INTEGER", description="本 tick 该 Agent feed 槽位数"),
    ]

    # ---------------- 构造 ----------------

    def __init__(self, **kwargs: Any):
        super().__init__()
        # config kwargs（全部有默认值，与 spec config_kwargs 一致；cls() 无必填参数）。
        self._recommendation_algorithm = str(kwargs.pop("recommendation_algorithm", "random"))
        self._mourning_norm_pressure = str(kwargs.pop("mourning_norm_pressure", "decay"))
        self._random_seed = int(kwargs.pop("random_seed", 0))
        self._feed_size = int(kwargs.pop("feed_size", 20))
        self._sampling_ratio = float(kwargs.pop("sampling_ratio", 0.05))
        self._injection_data_path = str(kwargs.pop("injection_data_path", ""))
        self._vocab_path = str(kwargs.pop("vocab_path", ""))
        raw_agent_types = kwargs.pop("agent_types", None) or {}
        self._agent_types: dict[str, str] = {str(k): str(v) for k, v in raw_agent_types.items()}
        self._start_week = str(kwargs.pop("start_week", "2026-W12"))
        self._num_ticks = int(kwargs.pop("num_ticks", 11))
        self._event_week = str(kwargs.pop("event_week", "2026-W13"))
        self._official_pin_extend_weeks = int(kwargs.pop("official_pin_extend_weeks", 1))
        self._alpha = float(kwargs.pop("alpha", 1.0))
        self._beta = float(kwargs.pop("beta", 1.0))  # 废弃：倾向分替代词表重合项（2026-09-09 裁定）
        self._gamma = float(kwargs.pop("gamma", 0.5))
        self._interest_noise_eps = float(kwargs.pop("interest_noise_eps", 0.05))
        self._recency_max_age_weeks = int(kwargs.pop("recency_max_age_weeks", 8))
        self._exposure_mode = str(kwargs.pop("exposure_mode", "none"))
        self._exposure_penalty_weight = float(kwargs.pop("exposure_penalty_weight", 0.1))
        rrw = kwargs.pop("random_recency_window_weeks", None)
        self._random_recency_window_weeks: Optional[int] = int(rrw) if rrw is not None else None
        self._w_official = float(kwargs.pop("w_official", 0.3))
        self._w_mourning = float(kwargs.pop("w_mourning", 0.4))
        self._w_volume = float(kwargs.pop("w_volume", 0.3))
        self._pressure_high_threshold = float(kwargs.pop("pressure_high_threshold", 0.6))
        self._pressure_medium_threshold = float(kwargs.pop("pressure_medium_threshold", 0.3))
        if kwargs:
            logger.warning(
                "CurationDynamicsSpace received unknown init kwargs: %s; ignored.",
                sorted(kwargs.keys()),
            )

        if self._recommendation_algorithm not in ("random", "chronological", "interest"):
            raise ValueError(f"recommendation_algorithm must be one of random/chronological/interest, got {self._recommendation_algorithm!r}")
        if self._mourning_norm_pressure not in ("decay", "sustained"):
            raise ValueError(f"mourning_norm_pressure must be decay/sustained, got {self._mourning_norm_pressure!r}")
        if self._exposure_mode not in ("none", "penalize", "exclude"):
            raise ValueError(f"exposure_mode must be none/penalize/exclude, got {self._exposure_mode!r}")
        for aid, ttype in self._agent_types.items():
            if ttype not in TYPE_ORDER:
                raise ValueError(f"agent_types[{aid!r}] = {ttype!r} not in {TYPE_ORDER}")

        # 三 RNG 流分离：注入=seed、随机臂=seed+1000、兴趣噪声=seed+2000（噪声流按 tick 重播种，
        # 保证六 cell 除算法/压力开关外完全一致）。
        self._rng_injection = random.Random(self._random_seed)
        self._rng_feed_random = random.Random(self._random_seed + 1000)
        self._rng_interest_noise = random.Random(self._random_seed + 2000)

        # 静态资产（空路径=空资产，仅调试/冒烟）。
        self._vocab: dict[str, Any] = self._load_json_asset(self._vocab_path, "vocab")
        self._injection_by_week: dict[str, list[dict[str, Any]]] = self._load_injection(
            self._injection_data_path
        )
        self._vocab_mourning_main = list((self._vocab.get("mourning") or {}).get("main", []) or [])
        self._vocab_marketing_main = list((self._vocab.get("marketing") or {}).get("main", []) or [])
        self._vocab_education_main = list((self._vocab.get("education") or {}).get("main", []) or [])
        meme_v = self._vocab.get("meme") or {}
        self._vocab_meme_linkage = list(meme_v.get("linkage", []) or [])
        self._vocab_meme_strong = list(meme_v.get("strong", []) or [])
        self._vocab_meme_exclude_death_fact = list(meme_v.get("exclude_death_fact", []) or [])
        self._vocab_meme_weak_markers = list(meme_v.get("weak_markers", []) or [])  # 不参与判类，仅审计

        # 动态状态（全部在 __init__ 初始化；restore() 在 __init__/init() 之后覆盖）。
        self._lock = asyncio.Lock()  # 不序列化，每次 __init__ 重建
        self._step_index = 0  # replay step 主键（自增，绝不用 tick 时长参数）
        self._tick_index = 1  # 当前已打开 tick 的 1-based 序号
        self._current_week = self._start_week
        self._posts: dict[int, dict[str, Any]] = {}
        self._pending_agent_posts: list[dict[str, Any]] = []
        self._spoke_this_tick: dict[str, bool] = {}
        self._posted_this_step: set[str] = set()
        self._feeds: dict[str, list[dict[str, Any]]] = {}
        self._norm_pressure = 0.0
        self._norm_pressure_level = "low"
        self._norm_pressure_peak: Optional[float] = None  # sustained 模式冻结峰值
        self._official_pinned: dict[str, list[int]] = {}
        self._pinned_ids: list[int] = []
        self._global_landscape: dict[str, Any] = {}
        self._seen_by_agent: dict[str, set[int]] = {}
        self._cumulative_exposures: dict[str, dict[str, int]] = {}
        self._total_posts_by_agent: dict[str, int] = {}
        self._next_post_id = 1
        self._exposure_counts_tick: dict[str, dict[str, int]] = {}
        self._climate_shares: dict[str, dict[str, float]] = {}
        self._injected_this_week: dict[str, int] = {t: 0 for t in TYPE_ORDER_ALL}
        self._injected_this_week_ids: list[int] = []
        self._official_injected_this_week = 0
        self._agent_posts_pooled_prev: set[int] = set()
        self._injected_count_by_week: dict[str, int] = {}
        self._event_week_injected_count = 0

        # 周窗口 + 确定性注入量（k_w = round(池大小 × ratio)，与 RNG 无关，init 即可得，
        # 供 volume 比 V_t 与 replay 的 injected_count 使用；采样本身在每 tick 打开时进行）。
        self._weeks: list[str] = [_week_add(self._start_week, i) for i in range(self._num_ticks)]
        for week in self._weeks:
            pool = self._injection_by_week.get(week, [])
            k = int(round(len(pool) * self._sampling_ratio))
            if pool and k <= 0:
                k = 1
            self._injected_count_by_week[week] = min(k, len(pool))
        self._event_week_injected_count = self._injected_count_by_week.get(self._event_week, 0)

    # ---------------- 资产加载 ----------------

    def _resolve_asset(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        if p.is_file():  # 相对 cwd（CLI 通常从 workspace 根运行）
            return p
        if self._workspace_root is not None and (self._workspace_root / p).is_file():
            return self._workspace_root / p
        return p

    def _load_json_asset(self, path: str, label: str) -> dict[str, Any]:
        if not path:
            return {}
        p = self._resolve_asset(path)
        if not p.is_file():
            logger.warning("CurationDynamicsSpace: %s asset not found at %s; using empty asset.", label, p)
            return {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("CurationDynamicsSpace: failed to load %s asset %s: %s", label, p, exc)
            return {}
        return data if isinstance(data, dict) else {}

    def _load_injection(self, path: str) -> dict[str, list[dict[str, Any]]]:
        """注入资产：顶层 {"meta":..., "posts":[...]}，按 week 索引；每条含 pid/week/type/content/author/is_official。"""
        if not path:
            return {}
        data = self._load_json_asset(path, "injection")
        posts = data.get("posts", []) if isinstance(data, dict) else []
        by_week: dict[str, list[dict[str, Any]]] = {}
        for rec in posts:
            if not isinstance(rec, dict) or "week" not in rec:
                continue
            by_week.setdefault(str(rec["week"]), []).append(rec)
        return by_week

    # ---------------- 判类器（逐字移植 build_assets.py Tagger 判定语义） ----------------

    @staticmethod
    def _hits(words: list[str], layers: list[str]) -> list[str]:
        return [w for w in words if any(w.lower() in l for l in layers)]

    def _tag_content_type(self, text: str) -> str:
        """四词表判类：raw.lower() + normalize() 两层子串匹配；meme=linkage 命中 或
        死因词替换为「□」后的 strong 命中；主类按优先级 悼念>营销>教育>玩梗>other。
        逐字移植 build_assets.py Tagger.tag（仅用 main 与 meme 四列表，aux/context_aux/
        legacy_markers/pruned 等均不参与判类）。"""
        raw = str(text)
        nrm = _normalize(raw)
        layers = [raw.lower(), nrm]
        hit_m = self._hits(self._vocab_mourning_main, layers)
        hit_mk = self._hits(self._vocab_marketing_main, layers)
        hit_ed = self._hits(self._vocab_education_main, layers)
        hit_link = self._hits(self._vocab_meme_linkage, layers)
        stripped = [raw.lower(), nrm]
        for w in self._vocab_meme_exclude_death_fact:
            stripped = [s.replace(w.lower(), "□") for s in stripped]
        hit_strong = [w for w in self._vocab_meme_strong if any(w.lower() in l for l in stripped)]
        is_meme = bool(hit_link or hit_strong)
        if hit_m:
            return "mourning"
        if hit_mk:
            return "marketing"
        if hit_ed:
            return "education"
        if is_meme:
            return "meme"
        return "other"

    def _compute_tendencies(self, text: str) -> dict[str, float]:
        """四类倾向分：各类型词表命中次数 ÷ 句长（命中/50 字），与判类器同口径两层匹配。

        用户裁定（2026-09-09）：帖子类型表征不由 LLM 解析，用词表命中次数与句子长度
        计算 梗/教育/哀悼/营销 倾向，作为兴趣推荐臂的匹配依据与 feed item 的信息字段。
        meme 命中 = linkage 命中数 + 死因词替换「□」后的 strong 命中数；其余主类 = main
        命中数；other/noise 无词表不参与。返回各类密度值（≥0，未截断，保留 4 位小数）。"""
        raw = str(text)
        nrm = _normalize(raw)
        layers = [raw.lower(), nrm]
        stripped = list(layers)
        for w in self._vocab_meme_exclude_death_fact:
            stripped = [s.replace(w.lower(), "□") for s in stripped]
        hits = {
            "mourning": len(self._hits(self._vocab_mourning_main, layers)),
            "marketing": len(self._hits(self._vocab_marketing_main, layers)),
            "education": len(self._hits(self._vocab_education_main, layers)),
            "meme": len(self._hits(self._vocab_meme_linkage, layers))
            + sum(1 for w in self._vocab_meme_strong if any(w.lower() in l for l in stripped)),
        }
        norm_len = max(1.0, len(raw) / 50.0)
        return {t: round(h / norm_len, 4) for t, h in hits.items()}

    # ---------------- 周/打开/收尾逻辑 ----------------

    def _compute_norm_pressure(self, week: str) -> tuple[float, str]:
        """P_t = w_official·O_t + w_mourning·M_t + w_volume·V_t，clamp[0,1]。
        O_t=当周官方注入占比；M_t=当周供给（注入周 t ∪ 上一 tick 收尾入池的 agent 帖）中悼念占比；
        V_t=当周注入量/event_week 注入量（≤1）。sustained 模式：W12 正常计算，event_week 正常计算
        并记录峰值，此后冻结为峰值。"""
        inj_total = sum(self._injected_this_week.values())
        o_t = self._official_injected_this_week / inj_total if inj_total > 0 else 0.0
        supply_ids = list(self._injected_this_week_ids)
        supply_ids += [pid for pid in self._agent_posts_pooled_prev if pid in self._posts]
        if supply_ids:
            m_t = sum(1 for pid in supply_ids if self._posts[pid]["type"] == "mourning") / len(supply_ids)
        else:
            m_t = 0.0
        v_t = (
            min(1.0, inj_total / self._event_week_injected_count)
            if self._event_week_injected_count > 0
            else 0.0
        )
        p = self._w_official * o_t + self._w_mourning * m_t + self._w_volume * v_t
        p = max(0.0, min(1.0, p))
        if self._mourning_norm_pressure == "sustained":
            if self._norm_pressure_peak is not None and _week_ord(week) > _week_ord(self._event_week):
                p = float(self._norm_pressure_peak)
            elif week == self._event_week:
                self._norm_pressure_peak = p
        level = (
            "high"
            if p >= self._pressure_high_threshold
            else ("medium" if p >= self._pressure_medium_threshold else "low")
        )
        return p, level

    def _compute_pinned_ids(self, week: str) -> list[int]:
        """官方置顶：is_official 注入帖在当周 + official_pin_extend_weeks 延伸周内置顶，
        最近周优先。"""
        ids: list[int] = []
        for i in range(self._official_pin_extend_weeks, -1, -1):
            w = _week_add(week, -i)
            for pid in self._official_pinned.get(w, []):
                if pid in self._posts:
                    ids.append(pid)
        return ids

    def _feed_item(self, pid: int) -> dict[str, Any]:
        p = self._posts[pid]
        return {
            "post_id": pid,
            "author_handle": p["author_handle"],
            "content": p["content"],
            "type": p["type"],
            "tendencies": p.get("tendencies") or {},
            "week": p["week"],
            "is_official": p["is_official"],
        }

    def _interest_rank(self, aid: str, week: str, candidates: list[int]) -> list[int]:
        """interest 臂：score = alpha·倾向分匹配 + gamma·时新近度 + 均匀噪声[-eps,+eps]。

        倾向分匹配（用户裁定 2026-09-09）：取帖子四类倾向分中本 Agent 类型维度的值
        （词表命中次数/句长密度），替代此前的硬类型命中 + 词表重合两项（beta 项废弃，
        倾向分本身即词表命中的密度归一化）。已曝光帖按 exposure_mode none/penalize/exclude
        处理。无帖子级热度/互动项（纯兴趣匹配最小机制）。"""
        atype = self._agent_types.get(aid, "other")
        seen = self._seen_by_agent.get(aid, set())
        eps = self._interest_noise_eps
        scored: list[tuple[float, int]] = []
        for pid in candidates:
            if self._exposure_mode == "exclude" and pid in seen:
                continue
            p = self._posts[pid]
            sc = self._alpha * (p.get("tendencies") or {}).get(atype, 0.0)
            age = max(0, _week_ord(week) - _week_ord(p["week"]))
            sc += self._gamma * max(0.0, 1.0 - age / self._recency_max_age_weeks)
            if self._exposure_mode == "penalize" and pid in seen:
                sc -= self._exposure_penalty_weight
            if eps > 0:
                sc += self._rng_interest_noise.uniform(-eps, eps)
            scored.append((sc, pid))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return [pid for _, pid in scored]

    def _assemble_feed(self, aid: str, week: str) -> list[dict[str, Any]]:
        """为单个 Agent 装配本周 feed：官方置顶帖占前部槽位（各算法臂一致），
        算法填充余下槽位并排除已置顶 id；候选=全池（累积不删除，可见性由 recency/曝光/窗口 knob 控制）。"""
        pinned_set = set(self._pinned_ids)
        feed: list[dict[str, Any]] = []
        for pid in self._pinned_ids[: self._feed_size]:
            feed.append(self._feed_item(pid))
        remaining = self._feed_size - len(feed)
        if remaining <= 0:
            return feed
        candidates = [pid for pid in sorted(self._posts) if pid not in pinned_set]
        alg = self._recommendation_algorithm
        if alg == "random":
            if self._random_recency_window_weeks is not None and self._random_recency_window_weeks > 0:
                wmin = _week_ord(_week_add(week, -(self._random_recency_window_weeks - 1)))
                wmax = _week_ord(week)
                candidates = [
                    pid for pid in candidates
                    if wmin <= _week_ord(self._posts[pid]["week"]) <= wmax
                ]
            take = min(remaining, len(candidates))
            chosen = self._rng_feed_random.sample(candidates, take) if take > 0 else []
        elif alg == "chronological":
            candidates.sort(key=lambda pid: (_week_ord(self._posts[pid]["week"]), pid), reverse=True)
            chosen = candidates[:remaining]
        else:  # interest
            chosen = self._interest_rank(aid, week, candidates)[:remaining]
        for pid in chosen:
            feed.append(self._feed_item(pid))
        return feed

    def _open_tick(self, week: str) -> None:
        """打开一个 tick：注入本周内容、计算 P_t、官方置顶集合、预装配全部 Agent 的 feed，
        并在装配时一次性记账曝光（get_feed 零副作用）。"""
        self._current_week = week
        self._tick_index = _week_ord(week) - _week_ord(self._start_week) + 1
        self._exposure_counts_tick = {}
        self._climate_shares = {}
        self._injected_this_week = {t: 0 for t in TYPE_ORDER_ALL}
        self._injected_this_week_ids = []
        self._official_injected_this_week = 0

        # 1) 注入（rng_injection 流，与 feed 层 RNG 分离）。
        pool = self._injection_by_week.get(week, [])
        k = min(self._injected_count_by_week.get(week, 0), len(pool))
        if pool and k > 0:
            for rec in self._rng_injection.sample(pool, k):
                pid = self._next_post_id
                self._next_post_id += 1
                ttype = str(rec.get("type", "other"))
                if ttype not in TYPE_ORDER_ALL:
                    ttype = "other"
                author = str(rec.get("author", "unknown"))
                content = str(rec.get("content", ""))
                self._posts[pid] = {
                    "post_id": pid,
                    "author_id": "ext_" + author,
                    "author_handle": author,
                    "content": content,
                    "type": ttype,
                    "assigned_type": ttype,  # 注入帖判类结果=数据集标签
                    "type_mismatch": False,
                    "tendencies": self._compute_tendencies(content),
                    "week": str(rec.get("week", week)),
                    "is_official": bool(rec.get("is_official", False)),
                    "exposure_count": 0,
                    "tick_produced": self._tick_index,
                }
                self._injected_this_week[ttype] += 1
                self._injected_this_week_ids.append(pid)
                if self._posts[pid]["is_official"]:
                    self._official_injected_this_week += 1
                    self._official_pinned.setdefault(week, []).append(pid)

        # 2) 规范压力。
        self._norm_pressure, self._norm_pressure_level = self._compute_norm_pressure(week)

        # 3) 官方置顶集合。
        self._pinned_ids = self._compute_pinned_ids(week)

        # 4) 预装配全部 feed（曝光在装配时记账：1 次/agent/tick；get_feed 只读缓存快照）。
        for aid in sorted(self._agent_types):
            feed = self._assemble_feed(aid, week)
            self._feeds[aid] = feed
            seen = self._seen_by_agent.setdefault(aid, set())
            counts = {t: 0 for t in TYPE_ORDER_ALL}
            for item in feed:
                pid = item["post_id"]
                seen.add(pid)
                self._posts[pid]["exposure_count"] += 1
                counts[item["type"]] += 1
            self._exposure_counts_tick[aid] = counts
            n = len(feed)
            self._climate_shares[aid] = {t: (c / n if n else 0.0) for t, c in counts.items()}

    def _set_baseline_landscape(self) -> None:
        """tick 1（W12）无前序完结 tick，global 份额用 W12 注入池基线快照（裁定 U4；
        营销主导，对齐真实 W12 77.8%，分母含 noise）。"""
        tot = sum(self._injected_this_week.values())
        shares = {t: (c / tot if tot else 0.0) for t, c in self._injected_this_week.items()}
        self._global_landscape = {
            "week": self._current_week,
            "supply_shares": dict(shares),
            "combined_shares": dict(shares),
            "exposure_shares": {t: 0.0 for t in TYPE_ORDER_ALL},
        }

    def _flush_pending_to_pool(self) -> list[dict[str, Any]]:
        """把本 tick 的 pending agent 帖并入 _posts（供下一 tick 传播），返回并入记录。"""
        merged = list(self._pending_agent_posts)
        for rec in merged:
            pid = rec["post_id"]
            self._posts[pid] = {
                "post_id": pid,
                "author_id": rec["agent_id"],
                "author_handle": rec["agent_id"],
                "content": rec["content"],
                "type": rec["pool_type"],
                "assigned_type": rec["assigned_type"],
                "type_mismatch": rec["type_mismatch"],
                "tendencies": rec.get("tendencies") or {},
                "week": rec["week"],
                "is_official": False,
                "exposure_count": 0,
                "tick_produced": self._step_index,
            }
        self._pending_agent_posts = []
        self._agent_posts_pooled_prev = {rec["post_id"] for rec in merged}
        return merged

    def _env_row(self, week: str, merged: list[dict[str, Any]]) -> dict[str, Any]:
        """env 级指标（43 列，key 与 _env_state_columns 精确一致）。"""
        agent_counts = {t: 0 for t in TYPE_ORDER}
        for rec in merged:
            pt = rec["pool_type"]
            agent_counts[pt if pt in agent_counts else "other"] += 1
        agent_supply = len(merged)
        injected_counts = dict(self._injected_this_week)
        injected_count = sum(injected_counts.values())
        total_supply = agent_supply + injected_count

        # Agent 产出口径：分母=五类 agent 帖总数（noise 无 agent 产出不在内）。
        denom_a = sum(agent_counts.values())
        supply_shares = {t: (agent_counts[t] / denom_a if denom_a else 0.0) for t in TYPE_ORDER}

        # combined 口径：分母=注入+产出，含 noise（对齐 benchmark weekly_category_matrix total）。
        combined_counts = {t: injected_counts.get(t, 0) for t in TYPE_ORDER_ALL}
        for t in TYPE_ORDER:
            combined_counts[t] += agent_counts[t]
        denom_c = total_supply
        combined_shares = {t: (combined_counts[t] / denom_c if denom_c else 0.0) for t in TYPE_ORDER_ALL}

        # 曝光（推荐服务口径，槽位计数）。
        exposure_counts = {t: 0 for t in TYPE_ORDER_ALL}
        total_exposures = 0
        for counts in self._exposure_counts_tick.values():
            for t in TYPE_ORDER_ALL:
                c = counts.get(t, 0)
                exposure_counts[t] += c
                total_exposures += c
        exposure_shares = {
            t: (exposure_counts[t] / total_exposures if total_exposures else 0.0) for t in TYPE_ORDER_ALL
        }

        official_exposure_slots = sum(
            1 for feed in self._feeds.values() for item in feed if item["is_official"]
        )

        row: dict[str, Any] = {
            "week": week,
            "norm_pressure": self._norm_pressure,
            "norm_pressure_level": self._norm_pressure_level,
            "total_supply": total_supply,
            "agent_supply": agent_supply,
            "injected_count": injected_count,
        }
        for t in TYPE_ORDER:
            row[f"supply_share_{t}"] = supply_shares[t]
        for t in TYPE_ORDER_ALL:
            row[f"supply_share_all_{t}"] = combined_shares[t]
        for t in TYPE_ORDER:
            row[f"agent_supply_{t}"] = agent_counts[t]
        for t in TYPE_ORDER_ALL:
            row[f"injected_{t}"] = injected_counts[t]
        row["total_exposures"] = total_exposures
        for t in TYPE_ORDER_ALL:
            row[f"exposure_share_{t}"] = exposure_shares[t]
            row[f"exposure_{t}"] = exposure_counts[t]
        row["official_posts_count"] = len(self._pinned_ids)
        row["official_exposure_slots"] = official_exposure_slots
        return row

    def _landscape_row(self, week: str, merged: list[dict[str, Any]]) -> dict[str, Any]:
        """最近完结 tick 的全局份额快照（get_feed 的 global_supply/exposure_shares）。"""
        row = self._env_row(week, merged)
        return {
            "week": week,
            "supply_shares": {t: row[f"supply_share_{t}"] for t in TYPE_ORDER},
            "combined_shares": {t: row[f"supply_share_all_{t}"] for t in TYPE_ORDER_ALL},
            "exposure_shares": {t: row[f"exposure_share_{t}"] for t in TYPE_ORDER_ALL},
        }

    def _agent_rows(self, week: str, merged: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """agent 级指标（20 列，batch 写）。"""
        by_aid = {rec["agent_id"]: rec for rec in merged}
        rows: list[dict[str, Any]] = []
        for aid in sorted(self._agent_types):
            rec = by_aid.get(aid)
            exc = self._exposure_counts_tick.get(aid, {})
            cli = self._climate_shares.get(aid, {})
            rows.append(
                {
                    "agent_id": self._replay_agent_id(aid),
                    "agent_type": self._agent_types.get(aid, "other"),
                    "spoke": 1 if self._spoke_this_tick.get(aid, False) else 0,
                    "produced_type": rec["pool_type"] if rec else None,
                    "assigned_type": rec["assigned_type"] if rec else None,
                    "type_mismatch": 1 if (rec and rec["type_mismatch"]) else 0,
                    "exposure_meme": exc.get("meme", 0),
                    "exposure_mourning": exc.get("mourning", 0),
                    "exposure_education": exc.get("education", 0),
                    "exposure_marketing": exc.get("marketing", 0),
                    "exposure_other": exc.get("other", 0),
                    "exposure_noise": exc.get("noise", 0),
                    "climate_meme": cli.get("meme", 0.0),
                    "climate_mourning": cli.get("mourning", 0.0),
                    "climate_education": cli.get("education", 0.0),
                    "climate_marketing": cli.get("marketing", 0.0),
                    "climate_other": cli.get("other", 0.0),
                    "climate_noise": cli.get("noise", 0.0),
                    "norm_pressure_seen": self._norm_pressure,
                    "norm_pressure_level_seen": self._norm_pressure_level,
                    "feed_slots": len(self._feeds.get(aid, [])),
                }
            )
        return rows

    @staticmethod
    def _replay_agent_id(aid: str) -> Any:
        try:
            return int(aid)
        except (TypeError, ValueError):
            return aid

    def _agent_last_post(self, aid: str) -> Optional[dict[str, Any]]:
        """该 Agent 最近一帖（先查 pending 缓冲，再查池）。"""
        best = None
        for rec in self._pending_agent_posts:
            if rec["agent_id"] == aid and (best is None or rec["post_id"] > best["post_id"]):
                best = rec
        if best is not None:
            return {
                "post_id": best["post_id"],
                "type": best["pool_type"],
                "assigned_type": best["assigned_type"],
                "content": best["content"],
            }
        pid_max: Optional[int] = None
        for pid, p in self._posts.items():
            if p["author_id"] == aid and (pid_max is None or pid > pid_max):
                pid_max = pid
        if pid_max is None:
            return None
        p = self._posts[pid_max]
        return {
            "post_id": pid_max,
            "type": p["type"],
            "assigned_type": p["assigned_type"],
            "content": p["content"],
        }

    # ---------------- 工具 ----------------

    @tool(readonly=True, kind="observe")
    async def get_feed(self, agent_id: str) -> dict:
        """读取您本周在舆论场的完整感知快照（只读观测工具，无任何副作用）。

        **get_feed(agent_id)** 返回：当前周标签 **week**；本周悼念规范压力 **norm_pressure**
        及其等级 **norm_pressure_level**；您本周是否已发言 **own_spoke**；您最近一帖
        **own_last_post**；您的本周推荐信息流 **feed**（长度 = feed_size，官方置顶帖在前，
        每条含 post_id / author_handle / content / type / week / is_official）；您所见意见气候
        **feed_type_distribution**（feed 中六类内容占比，六类=玩梗/悼念/教育/营销/其他/噪音）；
        最近完结 tick 的全局供给份额 **global_supply_shares** 与曝光份额 **global_exposure_shares**
        （本周即第一周时为 W12 注入池基线快照）；您的个人统计 **personal_stats**（累计发帖数、
        累计各类型曝光数）。同 tick 内重复调用返回同一快照，不重复计曝光。

        建议每周先调用本工具了解舆论场，再决定是否发言。

        参数：**agent_id** 为调用方 Agent 标识（框架约定首参）。
        """
        aid = str(agent_id)
        feed = [dict(item) for item in self._feeds.get(aid, [])]
        climate = dict(self._climate_shares.get(aid, {t: 0.0 for t in TYPE_ORDER_ALL}))
        last = self._agent_last_post(aid)
        landscape = self._global_landscape or {}
        stats = {
            "total_posts": self._total_posts_by_agent.get(aid, 0),
            "cumulative_exposures": dict(
                self._cumulative_exposures.get(aid, {t: 0 for t in TYPE_ORDER_ALL})
            ),
        }
        return {
            "status": "success",
            "week": self._current_week,
            "norm_pressure": round(float(self._norm_pressure), 4),
            "norm_pressure_level": self._norm_pressure_level,
            "own_spoke": bool(self._spoke_this_tick.get(aid, False)),
            "own_last_post": last,
            "feed": feed,
            "feed_type_distribution": climate,
            "global_supply_shares": dict(landscape.get("supply_shares", {})),
            "global_exposure_shares": dict(landscape.get("exposure_shares", {})),
            "personal_stats": stats,
            "response": (
                f"您在本周（{self._current_week}）的推荐信息流共 {len(feed)} 条"
                f"（官方置顶 {sum(1 for it in feed if it['is_official'])} 条），"
                f"悼念规范压力 {self._norm_pressure:.3f}（{self._norm_pressure_level}），"
                f"您本周已发言：{'是' if self._spoke_this_tick.get(aid, False) else '否'}。"
            ),
        }

    @tool(readonly=False)
    async def create_post(self, agent_id: str, content: str) -> dict:
        """发布一篇帖子（写操作，每 tick 每 Agent 至多 1 帖，重复调用无效）。

        **create_post(agent_id, content)** 提交您本 tick 要发布的帖子。帖子类型不由您指定：
        帖子池类型 **pool_type** 恒等于您的固定 Agent 类型（by construction）；环境用四词表
        判类器对正文独立打标得到 **assigned_type**，两者不一致时返回 **type_mismatch=true**
        供参考（不影响发布）。返回 **status**（字符串 success/fail/error）、**post_id**、
        **week** 与供阅读的 **response**。同一 tick 内重复调用（含路由器重试导致的重复执行）
        返回 status=success、**already_posted=true**，不改变任何状态（first-write-wins），
        且返回首次发布的 post_id。正文为空返回 status=fail。

        建议每周至多发言一次：先调用 **get_feed(agent_id)** 观察舆论场，再决定是否发言；
        您本 tick 发布的帖子将自下一周起进入信息流传播。

        参数：**agent_id** 为调用方 Agent 标识；**content** 为帖子正文（非空字符串）。
        """
        aid = str(agent_id)
        text = str(content or "").strip()
        if not text:
            return {
                "status": "fail",
                "reason": "content 为空：帖子正文不能为空字符串。",
                "already_posted": False,
                "week": self._current_week,
                "response": "发布失败：帖子正文为空，请补充内容后再试。",
            }
        async with self._lock:
            if aid in self._posted_this_step:
                pid = next(
                    (r["post_id"] for r in self._pending_agent_posts if r["agent_id"] == aid),
                    None,
                )
                return {
                    "status": "success",
                    "post_id": pid,
                    "pool_type": self._agent_types.get(aid, "other"),
                    "assigned_type": None,
                    "type_mismatch": False,
                    "already_posted": True,
                    "week": self._current_week,
                    "response": "本 tick 您已发布过帖子（每 tick 至多 1 帖，first-write-wins），"
                    "本次调用不产生任何变化。",
                }
            try:
                assigned = self._tag_content_type(text)
            except Exception as exc:  # 判类器异常不阻断发布
                logger.error("CurationDynamicsSpace tagger failed for agent %s: %s", aid, exc)
                return {
                    "status": "error",
                    "reason": f"判类器异常: {exc}",
                    "already_posted": False,
                    "week": self._current_week,
                    "response": "发布失败：内容判定服务暂时不可用，请稍后重试。",
                }
            pool_type = self._agent_types.get(aid, "other")
            pid = self._next_post_id
            self._next_post_id += 1
            self._pending_agent_posts.append(
                {
                    "post_id": pid,
                    "agent_id": aid,
                    "content": text,
                    "pool_type": pool_type,
                    "assigned_type": assigned,
                    "type_mismatch": assigned != pool_type,
                    "tendencies": self._compute_tendencies(text),
                    "week": self._current_week,
                }
            )
            self._spoke_this_tick[aid] = True
            self._posted_this_step.add(aid)
            mismatch_note = "（判类结果与您的类型不一致，仅供参考）" if assigned != pool_type else ""
            return {
                "status": "success",
                "post_id": pid,
                "pool_type": pool_type,
                "assigned_type": assigned,
                "type_mismatch": assigned != pool_type,
                "already_posted": False,
                "week": self._current_week,
                "response": f"发布成功：帖子 post_id={pid} 将在下一周进入信息流传播{mismatch_note}。",
            }

    # ---------------- 生命周期 ----------------

    async def init(self, start_datetime: datetime) -> None:
        """打开 tick 1（W12）：注入本周内容、计算 P_t、预装配全部 Agent 的 feed，并
        以 W12 注入池构成建立全局份额基线快照（U4）。无 replay 写入。"""
        self.t = start_datetime
        self._open_tick(self._weeks[0])
        self._set_baseline_landscape()

    async def step(self, tick: int, t: datetime) -> None:
        """每 tick 恰执行一次：先收尾当前 tick k（pending agent 帖并入池、写 env 1 行 +
        agent batch 行、更新全局份额快照、清空每 tick 状态），再预卷打开 tick k+1
        （注入、P_t、装配 feed）；step(11) 只收尾不打开 W23。replay 主键 = 内部 _step_index。"""
        self._step_index += 1
        week = self._current_week
        merged = self._flush_pending_to_pool()

        # 累积个人统计。
        for rec in merged:
            aid = rec["agent_id"]
            self._total_posts_by_agent[aid] = self._total_posts_by_agent.get(aid, 0) + 1
        for aid in sorted(self._agent_types):
            cum = self._cumulative_exposures.setdefault(aid, {t: 0 for t in TYPE_ORDER_ALL})
            for ttype in TYPE_ORDER_ALL:
                cum[ttype] = cum.get(ttype, 0) + self._exposure_counts_tick.get(aid, {}).get(ttype, 0)

        # replay 写入（每 step 恰一次；主键=_step_index）。
        await self._write_env_state(self._step_index, t, **self._env_row(week, merged))
        await self._write_agent_state_batch(
            self._step_index, t, self._agent_rows(week, merged)
        )

        # 全局份额快照 ← 最近完结 tick。
        self._global_landscape = self._landscape_row(week, merged)

        # 清空每 tick 状态（P3 Pattern B）。
        self._spoke_this_tick = {}
        self._posted_this_step = set()

        # 预卷打开下一 tick。
        if self._step_index < self._num_ticks:
            self._open_tick(_week_add(week, 1))

    async def close(self) -> None:
        """收尾：把残留 pending agent 帖并入池（11 步后正常应无残留）。"""
        self._flush_pending_to_pool()

    # ---------------- 描述（P2：散文+加粗函数名，面向中文 LLM Agent） ----------------

    @classmethod
    def description(cls) -> str:
        return (
            "舆论场数字表征转移模拟环境（CurationDynamicsSpace）：三种推荐算法 × 两种悼念"
            "规范压力（3×2 全因子 6 cells）下，100 个固定类型 Agent 的差异化激活与公共表征构成"
            "变化（张雪峰 2026-03-24 去世 W13，W12→W22 共 11 周）。Agent 每周通过 "
            "**get_feed(agent_id)** 查看本周推荐信息流、意见气候、悼念规范压力与全局供给/曝光"
            "份额，再决定是否发言；发言通过 **create_post(agent_id, content)** 发布一篇类型由"
            "其固定 Agent 类型决定的内容（每 tick 至多 1 帖，重复调用无效）。环境按周注入真实"
            "打标内容、按推荐算法装配 feed、内生计算规范压力，并把供给/曝光/发言漏斗指标写入"
            "replay 表供分析。"
        )

    @classmethod
    def init_description(cls) -> str:
        return (
            "CurationDynamicsSpace：舆论场数字表征转移模拟环境。全部构造参数均为关键字参数且含"
            "默认值（cls() 无必填参数）：**recommendation_algorithm** 推荐算法（random 全池均匀"
            "随机 / chronological 时间倒序 / interest 纯兴趣匹配，默认 random）；"
            "**mourning_norm_pressure** 悼念规范压力模式（decay 内生衰减 / sustained 事件周后"
            "冻结峰值，默认 decay）；**random_seed** cell 种子（注入/随机臂/兴趣噪声三条 RNG 流"
            "由同一种子加固定偏移派生，默认 0）；**feed_size** 每 Agent 每 tick feed 槽位数"
            "（默认 20）；**sampling_ratio** 每周注入抽样比例（默认 0.05）；**injection_data_path**"
            " 注入数据集 JSON 路径（顶层含 posts 数组，空串=无外部注入）；**vocab_path** 四词表"
            "判类器 JSON 路径（空串=词表为空，判类回落 other）；**agent_types** Agent 类型字典"
            "（{agent_id: meme|mourning|marketing|education|other}，未列出默认 other）；"
            "**start_week** 起始 ISO 周（默认 2026-W12）；**num_ticks** 总 tick 数（默认 11）；"
            "**event_week** 去世周（默认 2026-W13）；**official_pin_extend_weeks** 官方置顶延伸"
            "周数（默认 1）；interest 臂权重 **alpha**/**beta**/**gamma**、噪声幅度 "
            "**interest_noise_eps**、时新衰减窗 **recency_max_age_weeks**、已曝光处理 "
            "**exposure_mode**（none/penalize/exclude）与 **exposure_penalty_weight**、随机臂窗口 "
            "**random_recency_window_weeks**；规范压力权重 **w_official**/**w_mourning**/**w_volume**"
            " 与等级阈值 **pressure_high_threshold**/**pressure_medium_threshold**。"
        )

    # ---------------- workspace 持久化（--resume） ----------------

    async def to_workspace(self, workspace_path: Optional[Path] = None) -> None:
        """把动态状态原子写入 state/ENV_STATE.json（asyncio.Lock 与静态资产不序列化；
        RNG 用 getstate()）。"""
        if workspace_path is not None:
            self._bind_workspace(workspace_path)
        if self._workspace_root is None:
            raise RuntimeError("CurationDynamicsSpace workspace is not bound")
        state = {
            "_step_index": self._step_index,
            "_tick_index": self._tick_index,
            "_current_week": self._current_week,
            "_posts": self._posts,  # json 自动把 int 键转 str
            "_pending_agent_posts": self._pending_agent_posts,
            "_spoke_this_tick": self._spoke_this_tick,
            "_posted_this_step": sorted(self._posted_this_step),
            "_feeds": self._feeds,
            "_norm_pressure": self._norm_pressure,
            "_norm_pressure_level": self._norm_pressure_level,
            "_norm_pressure_peak": self._norm_pressure_peak,
            "_global_landscape": self._global_landscape,
            "_seen_by_agent": {aid: sorted(ids) for aid, ids in self._seen_by_agent.items()},
            "_cumulative_exposures": self._cumulative_exposures,
            "_total_posts_by_agent": self._total_posts_by_agent,
            "_next_post_id": self._next_post_id,
            "_rng_injection": self._rng_injection.getstate(),
            "_rng_feed_random": self._rng_feed_random.getstate(),
            "_rng_interest_noise": self._rng_interest_noise.getstate(),
            "_official_pinned": {w: list(ids) for w, ids in self._official_pinned.items()},
            "_pinned_ids": list(self._pinned_ids),
            "_agent_posts_pooled_prev": sorted(self._agent_posts_pooled_prev),
            "_injected_count_by_week": {w: int(c) for w, c in self._injected_count_by_week.items()},
            "_injected_this_week": dict(self._injected_this_week),
            "_injected_this_week_ids": list(self._injected_this_week_ids),
            "_official_injected_this_week": self._official_injected_this_week,
            "_exposure_counts_tick": self._exposure_counts_tick,
            "_climate_shares": self._climate_shares,
        }
        atomic_write_text(
            self._workspace_root / _STATE_REL,
            json.dumps(state, ensure_ascii=False, indent=2, default=str),
        )

    async def restore(self, workspace_path: Path) -> bool:
        """从 state/ENV_STATE.json 恢复动态状态（在 __init__/init() 之后调用，覆盖之）。
        _lock 由 __init__ 重建，不反序列化；_vocab/_injection_data/_agent_types 由资产路径与
        kwargs 重建。"""
        self._bind_workspace(workspace_path)
        state_path = self._workspace_root / _STATE_REL
        if not state_path.is_file():
            return False
        d = json.loads(state_path.read_text(encoding="utf-8"))
        self._step_index = int(d.get("_step_index", 0))
        self._tick_index = int(d.get("_tick_index", 1))
        self._current_week = str(d.get("_current_week", self._start_week))
        self._posts = {int(k): v for k, v in (d.get("_posts") or {}).items()}
        self._pending_agent_posts = list(d.get("_pending_agent_posts", []) or [])
        self._spoke_this_tick = dict(d.get("_spoke_this_tick", {}) or {})
        self._posted_this_step = set(d.get("_posted_this_step", []) or [])
        self._feeds = dict(d.get("_feeds", {}) or {})
        self._norm_pressure = float(d.get("_norm_pressure", 0.0))
        self._norm_pressure_level = str(d.get("_norm_pressure_level", "low"))
        self._norm_pressure_peak = d.get("_norm_pressure_peak")
        self._global_landscape = dict(d.get("_global_landscape", {}) or {})
        self._seen_by_agent = {
            str(aid): set(ids) for aid, ids in (d.get("_seen_by_agent") or {}).items()
        }
        self._cumulative_exposures = {
            str(aid): dict(v) for aid, v in (d.get("_cumulative_exposures") or {}).items()
        }
        self._total_posts_by_agent = {
            str(aid): int(v) for aid, v in (d.get("_total_posts_by_agent") or {}).items()
        }
        self._next_post_id = int(d.get("_next_post_id", 1))
        for attr, key in (
            ("_rng_injection", "_rng_injection"),
            ("_rng_feed_random", "_rng_feed_random"),
            ("_rng_interest_noise", "_rng_interest_noise"),
        ):
            st = d.get(key)
            if st is not None:
                getattr(self, attr).setstate(_rng_state_from_json(st))
        self._official_pinned = {str(w): list(ids) for w, ids in (d.get("_official_pinned") or {}).items()}
        self._pinned_ids = [int(pid) for pid in (d.get("_pinned_ids") or [])]
        self._agent_posts_pooled_prev = set(int(pid) for pid in (d.get("_agent_posts_pooled_prev") or []))
        loaded_ic = d.get("_injected_count_by_week")
        if isinstance(loaded_ic, dict):
            self._injected_count_by_week = {str(w): int(c) for w, c in loaded_ic.items()}
        self._injected_this_week = {
            t: int((d.get("_injected_this_week") or {}).get(t, 0)) for t in TYPE_ORDER_ALL
        }
        self._injected_this_week_ids = [int(pid) for pid in (d.get("_injected_this_week_ids") or [])]
        self._official_injected_this_week = int(d.get("_official_injected_this_week", 0))
        self._exposure_counts_tick = {
            str(aid): {t: int(v.get(t, 0)) for t in TYPE_ORDER_ALL}
            for aid, v in (d.get("_exposure_counts_tick") or {}).items()
        }
        self._climate_shares = {
            str(aid): {t: float(v.get(t, 0.0)) for t in TYPE_ORDER_ALL}
            for aid, v in (d.get("_climate_shares") or {}).items()
        }
        # 容错：老 checkpoint 缺每 tick 导出数据时，由已持久化的 feed 重建（不重复计 post 曝光）。
        if not self._exposure_counts_tick:
            for aid, feed in self._feeds.items():
                counts = {t: 0 for t in TYPE_ORDER_ALL}
                for item in feed:
                    counts[item["type"]] += 1
                self._exposure_counts_tick[aid] = counts
                n = len(feed)
                self._climate_shares[aid] = {t: (c / n if n else 0.0) for t, c in counts.items()}
        return True
