"""舆论场数字表征转移模拟环境（CurationDynamicsSpace）。

实验背景：张雪峰 2026-03-24（2026-W13）去世后，三种推荐算法（random / chronological /
interest，单因子 3 臂 × 3 seeds = 9 runs；2026-09-12 用户裁定：玩梗涌现环境增益 G 退役，
原 3×2 全因子的第二因子随之失效）下，100 个固定类型 Agent 的差异化激活与公共表征构成
变化（W12→W22 共 11 周）。Agent 每 tick 先通过 **get_feed(agent_id)** 读取本周推荐信息流
（feed）、意见气候、玩梗涌现环境与全局供给/曝光份额，再决定是否发言；发言通过
**create_post(agent_id, content)** 发布一篇类型由其固定 Agent 类型决定的内容（每 tick
至多 1 帖，重复调用无效）。

本模块仅继承 EnvBase（No-Inheritance Rule）；全部 @tool 在类体内重新实现。
判类器逐字移植 custom/envs/curation_assets/build_assets.py 的 normalize()/Tagger 语义。
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import random
import re
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, ClassVar, Optional

from agentsociety2.env import EnvBase, tool
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef
from agentsociety2.storage.workspace_state import atomic_write_text

logger = get_logger()


# ---------------- feed 机制共享纯函数（与 calibrate_speak.py 同源，避免校准-仿真漂移） ----------------
# 用户 2026-09-12 裁定（见 hypothesis_4/experiment_1/SMOKE_DIAGNOSIS_w19_cliff.md）：
# 帖子生命周期（老帖冷却 + 曝光饱和 + 过期退场）与兴趣比例抽样。
# 纯函数放 custom/envs/curation_mechanisms.py，env 与校准脚本各自按路径 import 同一份实现。
_MECH_MODULE_NAME = "curation_mechanisms"
_MECH_PATH = Path(__file__).resolve().parent / f"{_MECH_MODULE_NAME}.py"
_mech_spec = importlib.util.spec_from_file_location(_MECH_MODULE_NAME, _MECH_PATH)
if _mech_spec is None or _mech_spec.loader is None:  # pragma: no cover - 路径异常时快速失败
    raise ImportError(f"无法加载共享机制模块: {_MECH_PATH}")
mech = importlib.util.module_from_spec(_mech_spec)
_mech_spec.loader.exec_module(mech)


# ---------------- 模板缓存嵌入补丁（本地确定性向量，替代外部 embedding 服务） ----------------
# 背景：框架 EnvRouterActor 的模板代码缓存（CacheCodeProvider）在每次查找前后都要把指令文本
# 嵌入成向量做 FAISS 精确匹配。用户的 Ark 计划无任何 embedding 模型（全套 doubao-embedding
# 404 / v3 401），导致每次嵌入都失败 → 缓存永远 miss → 每个 agent 每 tick 都重新让 LLM 现场
# 生成同一段代码（实测中位数 ~11.5s/次，单 run ~6-7 小时）。
# 本补丁在 EnvRouterActor 的工作进程内（本模块 import 时，早于首次 get_feed）把
# _compute_embedding 替换为完全确定性的哈希向量：
#   * 相同文本 → 逐字节相同的向量 → FAISS sim=1.0 → 缓存精确命中（复用 LLM 首次生成的代码）；
#   * 不同文本 → 各维独立伪随机、L2 归一 → 余弦≈0 → 远低于 0.85 阈值 → 正常 miss。
# 安全：哈希向量无语义含义，不可能造成错误代码复用（误命中只发生在 sim≈1，即文本逐字节
# 相同时）；与配置无关，不含外部请求。缓存内容仍是 env 的同一份确定性代码，不动实验语义。
# 有意保留本模块 import 的 raw 版本参考（embedding_stub.py 已废弃）——进程内版本为唯一实现。

def _patch_cache_embedding() -> None:
    """把框架的 embedding 静态方法替换为进程内确定性哈希向量（须在首次 get_feed 前生效）。"""
    import hashlib

    import numpy as np
    from agentsociety2.config.config import Config
    from agentsociety2.env.router_codegen import CacheCodeProvider

    dim = Config.EMBEDDING_DIMS

    def _det_vec(text: str):
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        vec = np.array([rng.uniform(-1.0, 1.0) for _ in range(dim)], dtype=np.float32)
        norm = float(np.sqrt(float(np.dot(vec, vec)))) or 1.0
        return vec / norm

    async def _local_embedding(router, text):
        async with router._embedding_cache_lock:
            if text in router._embedding_cache:
                return router._embedding_cache[text]
        emb = _det_vec(text)
        async with router._embedding_cache_lock:
            if len(router._embedding_cache) < 10000:
                router._embedding_cache[text] = emb
        return emb

    CacheCodeProvider._compute_embedding = staticmethod(_local_embedding)


_patch_cache_embedding()


# ---------------- 模板代码确定性补丁（固定指令短路为完整快照代码） ----------------
# 背景：模板缓存 miss 时由 LLM 现场生成执行代码，生成结果不可控——实测首次 codegen
# 的 get_feed 代码只把 status/week/feed_size 等摘要存入 results，丢弃了 loader 端
# （CurationDiscourseAgent._find_feed_dict）等待的完整 feed/meme_env 快照 → 所有 Agent
# 每 tick 判 feed_unavailable → 全员沉默、Agent 帖 0，整个反馈回路不产生任何 Agent 内容。
# 本补丁在 CacheCodeProvider.get_code 前拦截两条固定指令，返回确定性执行代码：
#   * get_feed：把 get_feed 返回的完整快照写入 results 顶层（含 feed/meme_env 键）；
#   * create_post：确定性发布（status/post_id/week）。
# 其余指令仍走原 cache→LLM 代码生成路径。确定性代码不依赖 LLM，杜绝同类契约漂移。

def _patch_template_code() -> None:
    import agentsociety2.env.router_codegen as _rc

    _GET_FEED_CODE = """\
agent_id = ctx['variables']['agent_id']
response = await modules['CurationDynamicsSpace'].get_feed(agent_id)
if isinstance(response, dict) and response.get('status') == 'success':
    results['status'] = 'success'
    for _k in ('week', 'meme_env', 'own_spoke', 'own_last_post', 'feed',
               'feed_type_distribution', 'global_supply_shares',
               'global_exposure_shares', 'personal_stats'):
        results[_k] = response.get(_k)
    _feed = results.get('feed') or []
    _env = results.get('meme_env') or {}
    print(f"Feed snapshot for agent {agent_id} in week {results.get('week')}: "
          f"{len(_feed)} posts (official "
          f"{sum(1 for it in _feed if it.get('is_official'))}), "
          f"meme gain {_env.get('gain')}")
else:
    results['status'] = 'fail'
    results['reason'] = response.get('reason', 'unknown') if isinstance(response, dict) else 'unknown'
"""

    _CREATE_POST_CODE = """\
agent_id = ctx['variables']['agent_id']
content = ctx['variables']['content']
response = await modules['CurationDynamicsSpace'].create_post(agent_id, content)
if isinstance(response, dict) and response.get('status') == 'success':
    results['status'] = 'success'
    results['week'] = response.get('week')
    results['post_id'] = response.get('post_id')
    results['already_posted'] = response.get('already_posted', False)
    results['type_mismatch'] = response.get('type_mismatch', False)
    print(f"Post published {response.get('post_id')} in week {response.get('week')}")
else:
    results['status'] = 'fail'
    results['reason'] = response.get('reason', 'unknown') if isinstance(response, dict) else 'unknown'
"""

    _orig_get_code = _rc.CacheCodeProvider.get_code

    async def _patched_get_code(self, context, router):
        inst = str(getattr(context, "instruction", "") or "").strip()
        if inst.startswith("Please call get_feed()"):
            return _GET_FEED_CODE
        if inst.startswith("Please call create_post()"):
            return _CREATE_POST_CODE
        return await _orig_get_code(self, context, router)

    _rc.CacheCodeProvider.get_code = _patched_get_code


_patch_template_code()

# 本模块自选的 workspace 布局：<workspace_root>/state/ENV_STATE.json
_STATE_REL = "state/ENV_STATE.json"

# 类型顺序（env 内部统一顺序；判类优先级另见 PRECEDENCE）。
TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other"]
TYPE_ORDER_ALL = TYPE_ORDER + ["noise"]

# 判类优先级：逐字移植 build_assets.py PRECEDENCE（悼念 > 营销 > 教育 > 玩梗，其余 other）。
PRECEDENCE = ["mourning", "marketing", "education", "meme"]


# ---------------- 判类器（与 build_assets.py 完全同源，勿改判定语义） ----------------

# 逐字移植 build_assets.py _EMOJI（emoji / 符号 / 国旗 / 变体选择器 / 零宽连接符）。
_EMOJI = mech._EMOJI


def _normalize(s: str) -> str:
    """逐字移植 build_assets.py normalize()（委托共享机制模块，保证与校准脚本同一实现）。"""
    return mech.normalize(s)


_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
_EPOCH_MONDAY = date(2026, 1, 5)  # 固定周一锚点（2026-01-05），用于 ISO 周序数比较


def _week_monday(week: str) -> date:
    """ISO 周标签 → 该周周一（委托共享机制模块，保证与校准脚本同一实现）。"""
    return mech.week_monday(week)


def _week_add(week: str, n: int) -> str:
    """ISO 周标签偏移 n 周（委托共享机制模块）。"""
    return mech.week_add(week, n)


def _week_ord(week: str) -> int:
    """ISO 周标签 → 周序数（委托共享机制模块，仅用于比较）。"""
    return mech.week_ord(week)


def _post_age_weeks(current_week: str, post_week: str) -> int:
    """帖龄（周）：同周为 0（委托共享机制模块）。"""
    return mech.age_weeks(current_week, post_week)


def _rng_state_from_json(v: Any) -> Any:
    """把 JSON 反序列化后的 RNG getstate() 结构（list）递归还原为 tuple（random.setstate 要求）。"""
    if isinstance(v, list):
        return tuple(_rng_state_from_json(x) for x in v)
    return v


class CurationDynamicsSpace(EnvBase):
    """舆论场数字表征转移模拟环境：推荐算法单因子三臂，100 个固定类型 Agent，
    W12→W22 共 11 周；环境 B_t/S_t/G_t 只记录、不进入 Agent 决策。"""

    # ---------------- Replay 列声明 ----------------
    # env 级：每 step 一行（主键 step=_step_index），55 列。
    _env_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("week", "TEXT", description="当前 tick 的 ISO 周标签"),
        ColumnDef("meme_env_stock", "INTEGER", description="涌现环境存量 Stock_t：过去 emergence_window_stock 周（含本周）供给总数（注入+agent 帖）"),
        ColumnDef("meme_env_flow", "INTEGER", description="涌现环境流量（arena 口径）：本 tick 新增供给总数（注入+agent 帖）"),
        ColumnDef("meme_env_flow_world", "INTEGER", description="涌现环境流量（现实口径）：本周真实新增帖量镜像调度值"),
        ColumnDef("meme_env_abundance", "REAL", description="丰沛度 B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)；基线周=1"),
        ColumnDef("meme_env_emptiness", "REAL", description="空旷度 S_t = h(Flow_t)/h(Flow_base)，h(x)=K_f/(K_f+x)；基线周=1；sustained_hot 臂事件周后冻结"),
        ColumnDef("meme_env_gain", "REAL", description="涌现增益 G_t = clamp(B_t^β·S_t^σ, gain_min, gain_max)；**观测序列**（2026-09-12 起不进入任何类型的决策）"),
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
        # —— feed 机制审计（用户 2026-09-12 裁定：帖子生命周期 + 曝光饱和 + 比例抽样）——
        ColumnDef("feed_live_pool", "INTEGER", description="本周算法实际候选池帖数：random=截至当周全部历史帖；chronological/interest=未退场活帖"),
        ColumnDef("feed_sample_temp", "REAL", description="interest 臂比例抽样的温度（<=0 表示确定性 top-k 消融档）"),
        ColumnDef("feed_half_life_weeks", "REAL", description="帖子时间生命的半衰期（周）"),
        ColumnDef("feed_saturation_scale", "REAL", description="曝光饱和尺度：累计曝光达该值时生命折半"),
        ColumnDef("exposure_slots_age0", "INTEGER", description="本 tick 曝光槽位中帖龄 0 周（本周新帖）的槽位数"),
        ColumnDef("exposure_slots_age1", "INTEGER", description="本 tick 曝光槽位中帖龄 1 周的槽位数"),
        ColumnDef("exposure_slots_age2", "INTEGER", description="本 tick 曝光槽位中帖龄 2 周的槽位数"),
        ColumnDef("exposure_slots_age3plus", "INTEGER", description="本 tick 曝光槽位中帖龄 ≥3 周的槽位数（老帖霸屏的直接指标）"),
        ColumnDef("event_floor_slots", "INTEGER", description="议程设置：本 tick 事件周保底哀悼帖集合的条数（全员各占同样多槽位；非事件周=0）"),
    ]

    # agent 级：每 step 每 agent 一行（主键 agent_id+step），21 列。
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
        ColumnDef("meme_env_abundance_seen", "REAL", description="本 tick 该 Agent 所见丰沛度 B_t"),
        ColumnDef("meme_env_emptiness_seen", "REAL", description="本 tick 该 Agent 所见空旷度 S_t"),
        ColumnDef("meme_env_gain_seen", "REAL", description="本 tick 该 Agent 所见涌现增益 G_t"),
        ColumnDef("feed_slots", "INTEGER", description="本 tick 该 Agent feed 槽位数"),
    ]

    # ---------------- 构造 ----------------

    def __init__(self, **kwargs: Any):
        super().__init__()
        # config kwargs（全部有默认值，与 spec config_kwargs 一致；cls() 无必填参数）。
        self._recommendation_algorithm = str(kwargs.pop("recommendation_algorithm", "random"))
        self._meme_emergence_mode = str(kwargs.pop("meme_emergence_mode", "normal"))
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
        # 议程设置（用户 2026-09-12/13 裁定）：事件周（event_week）为**每个** agent 的 feed
        # 保底注入 N 条哀悼帖（按哀悼倾向分取全池前 N 条、全员相同，等效"讣告 + 头版哀悼"的
        # 强制曝光，使事件周全体 agent 都暴露于哀悼叙事）。0=关闭。平台级规则，三臂一致。
        self._event_week_mourning_floor = int(kwargs.pop("event_week_mourning_floor", 0))
        self._alpha = float(kwargs.pop("alpha", 1.0))
        self._beta = float(kwargs.pop("beta", 1.0))  # 废弃：倾向分替代词表重合项（2026-09-09 裁定）
        self._gamma = float(kwargs.pop("gamma", 0.5))
        self._interest_noise_eps = float(kwargs.pop("interest_noise_eps", 0.05))
        # 旧加性时新项（gamma·max(0,1−age/max_age)）已退役，仅保留 kwarg 兼容；见 curation_mechanisms。
        self._recency_max_age_weeks = int(kwargs.pop("recency_max_age_weeks", 8))
        # —— 帖子生命周期（用户 2026-09-12 裁定：老帖随时间冷却、被推多也冷却、过期退场）——
        self._life_half_life_weeks = float(
            kwargs.pop("life_half_life_weeks", mech.DEFAULT_HALF_LIFE_WEEKS)
        )
        self._life_saturation_scale = float(
            kwargs.pop("life_saturation_scale", mech.DEFAULT_SATURATION_SCALE)
        )
        self._life_retire_floor = float(
            kwargs.pop("life_retire_floor", mech.DEFAULT_RETIRE_FLOOR)
        )
        # —— 兴趣比例抽样（用户 2026-09-12 裁定：A+B 都上；temperature<=0 退化为确定性 top-k）——
        self._interest_sample_temp = float(kwargs.pop("interest_sample_temp", 4.0))
        self._exposure_mode = str(kwargs.pop("exposure_mode", "none"))
        self._exposure_penalty_weight = float(kwargs.pop("exposure_penalty_weight", 0.1))
        rrw = kwargs.pop("random_recency_window_weeks", None)
        self._random_recency_window_weeks: Optional[int] = int(rrw) if rrw is not None else None
        raw_flow_sched = kwargs.pop("emergence_flow_by_week", None)
        self._emergence_flow_by_week: dict[str, int] = (
            {str(w): int(c) for w, c in raw_flow_sched.items()} if raw_flow_sched else {}
        )
        self._emergence_window_stock = int(kwargs.pop("emergence_window_stock", 6))
        self._emergence_ka = kwargs.pop("emergence_ka", None)
        self._emergence_kf = kwargs.pop("emergence_kf", None)
        self._emergence_beta = float(kwargs.pop("emergence_beta", 1.0))
        self._emergence_sigma = float(kwargs.pop("emergence_sigma", 1.0))
        self._emergence_gain_min = float(kwargs.pop("emergence_gain_min", 0.2))
        self._emergence_gain_max = float(kwargs.pop("emergence_gain_max", 3.0))
        if kwargs:
            logger.warning(
                "CurationDynamicsSpace received unknown init kwargs: %s; ignored.",
                sorted(kwargs.keys()),
            )

        if self._recommendation_algorithm not in ("random", "chronological", "interest"):
            raise ValueError(f"recommendation_algorithm must be one of random/chronological/interest, got {self._recommendation_algorithm!r}")
        if self._meme_emergence_mode not in ("normal", "sustained_hot"):
            raise ValueError(f"meme_emergence_mode must be normal/sustained_hot, got {self._meme_emergence_mode!r}")
        if self._emergence_window_stock < 1:
            raise ValueError(f"emergence_window_stock must be >= 1, got {self._emergence_window_stock}")
        if self._exposure_mode not in ("none", "penalize", "exclude"):
            raise ValueError(f"exposure_mode must be none/penalize/exclude, got {self._exposure_mode!r}")
        if self._life_half_life_weeks <= 0:
            raise ValueError(f"life_half_life_weeks must be > 0, got {self._life_half_life_weeks}")
        if self._life_retire_floor < 0:
            raise ValueError(f"life_retire_floor must be >= 0, got {self._life_retire_floor}")
        if self._event_week_mourning_floor < 0:
            raise ValueError(
                f"event_week_mourning_floor must be >= 0, got {self._event_week_mourning_floor}"
            )
        for aid, ttype in self._agent_types.items():
            if ttype not in TYPE_ORDER:
                raise ValueError(f"agent_types[{aid!r}] = {ttype!r} not in {TYPE_ORDER}")

        # 四 RNG 流分离：注入=seed、随机臂=seed+1000、兴趣噪声=seed+2000、
        # 兴趣比例抽样=seed+3000（同 seed 跨 cell 抽出同一序列，保证臂间可比）。
        self._rng_injection = random.Random(self._random_seed)
        self._rng_feed_random = random.Random(self._random_seed + 1000)
        self._rng_interest_noise = random.Random(self._random_seed + 2000)
        self._rng_interest_sample = random.Random(self._random_seed + 3000)

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
        # 倾向分词表（六份，与判类器同口径）打包给共享机制模块用。
        self._tendency_vocab = mech.vocab_lists_from_doc(self._vocab)

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
        self._meme_env: dict[str, Any] = {
            "stock": 0, "flow": 0, "flow_world": 0,
            "abundance": 1.0, "emptiness": 1.0, "gain": 1.0,
        }
        self._sustained_s: Optional[float] = None  # sustained_hot 模式：event_week 冻结的空旷度
        self._flow_by_week: dict[str, int] = {}  # arena 周供给总量历史（丰沛度存量口径的输入）
        self._official_pinned: dict[str, list[int]] = {}
        self._pinned_ids: list[int] = []
        self._event_floor_ids: list[int] = []  # 事件周保底哀悼帖（全员相同）
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
        # feed 机制审计（用户 2026-09-12 裁定后的新增观测量）：
        self._feed_live_pool = 0            # 实际候选池帖数：random 全历史；其余两臂未退场活帖
        self._exposure_age_buckets: dict[str, int] = {"age0": 0, "age1": 0, "age2": 0, "age3plus": 0}

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

        # 涌现环境形状常数（半饱和点；机制定形状、效标定尺度，可被 config 显式覆盖）：
        # K_a = 注入计划口径的事件周存量估计（B 读内生 arena 计数，同尺度）；
        # K_f = 空旷度流量口径的基线周值（S 读外生真实调度时有现实尺度，回退内生时同arena尺度）。
        # 效标拟合见 calibrate_speak.py；K→0 极限退化为纯比值。
        ev_idx = (
            self._weeks.index(self._event_week) if self._event_week in self._weeks else len(self._weeks) - 1
        )
        ka_window = self._weeks[: ev_idx + 1][-self._emergence_window_stock :]
        self._emergence_ka_final = (
            float(self._emergence_ka)
            if self._emergence_ka is not None
            else float(sum(self._injected_count_by_week.get(w, 0) for w in ka_window))
        )
        flow_base_world = self._emergence_flow_by_week.get(
            self._start_week, self._injected_count_by_week.get(self._start_week, 0)
        )
        self._emergence_kf_final = (
            float(self._emergence_kf) if self._emergence_kf is not None else float(flow_base_world)
        )

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
        return mech.hits(words, layers)

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
        实现委托共享机制模块（curation_mechanisms.compute_tendencies），
        保证校准脚本与 env 的倾向分逐值一致。"""
        return mech.compute_tendencies(text, self._tendency_vocab)

    # ---------------- 周/打开/收尾逻辑 ----------------

    def _compute_meme_env(self, week: str) -> dict[str, Any]:
        """玩梗涌现环境（用户 2026-09-10 裁定，取代悼念规范压力 P_t）。

        存量（丰沛度输入，内生）：Stock_t = 过去 emergence_window_stock 周（含本周）的
        供给总数之和（供给口径 = 注入周 t ∪ 上一 tick 收尾入池的 agent 帖，含全部类型含
        noise）。流量（空旷度输入，外生）：Flow_t = 真实周新增帖量镜像调度
        emergence_flow_by_week（未提供该周时回退内生 arena 计数——250 条注入预算把
        arena 洪峰压缩到 ~2×、agent 周供给近似恒定，只有现实口径保留「洪峰→退潮」
        的完整对比度，见 EXPERIMENT.md）。两序列均以基线周（start_week）为 1：
        B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)（存量越丰沛越易诞生 meme）；
        S_t = h(Flow_t)/h(Flow_base)，h(x)=K_f/(K_f+x)（单期新增越少越空旷、越宜传播）。
        涌现增益 G_t = clamp(B_t^β·S_t^σ, gain_min, gain_max)。**2026-09-12 用户裁定：
        G 与 agent 侧 θ 一并退役，本函数结果仅作为观测序列写入 replay 与监控（描述性
        时间轴 + 审计线索），不进入任何类型的决策**（agent 侧现为
        U = B_i + R·(D−B_i)；这里的常态锚点 B_i 不同于环境丰沛度 B_t）。
        sustained_hot 模式（反事实臂「维持高热」）：W12/W13 正常计算，W13 记录 S
        （事件周空旷度），此后冻结为该值；B 保持内生演化（用户裁定）。"""
        flow_sim = sum(self._injected_this_week.values()) + len(
            [pid for pid in self._agent_posts_pooled_prev if pid in self._posts]
        )
        self._flow_by_week[week] = flow_sim
        w0_ord = _week_ord(self._start_week)
        w_ord = _week_ord(week)
        window_lo = max(w0_ord, w_ord - self._emergence_window_stock + 1)
        stock_t = sum(
            c for w, c in self._flow_by_week.items() if window_lo <= _week_ord(w) <= w_ord
        )
        # 窗口在基线周截断 → Stock_W12 = Flow_W12。
        stock_base = self._flow_by_week.get(self._start_week, 0)

        # 空旷度流量口径：外生真实调度优先，缺该周回退内生计数。
        flow_env = int(self._emergence_flow_by_week.get(week, flow_sim))
        flow_env_base = self._emergence_flow_by_week.get(self._start_week, stock_base)

        ka = max(float(self._emergence_ka_final), 1e-9)
        kf = max(float(self._emergence_kf_final), 1e-9)
        f_b0 = stock_base / (stock_base + ka)
        abundance = (stock_t / (stock_t + ka)) / f_b0 if f_b0 > 0 else 1.0
        h_f0 = kf / (kf + flow_env_base)
        emptiness = (kf / (kf + flow_env)) / h_f0 if h_f0 > 0 else 1.0

        if self._meme_emergence_mode == "sustained_hot":
            if self._sustained_s is not None and w_ord > _week_ord(self._event_week):
                emptiness = float(self._sustained_s)
            elif week == self._event_week:
                self._sustained_s = emptiness

        gain = (abundance ** self._emergence_beta) * (emptiness ** self._emergence_sigma)
        gain = max(self._emergence_gain_min, min(self._emergence_gain_max, gain))
        return {
            "stock": int(stock_t),
            "flow": int(flow_sim),
            "flow_world": int(flow_env),
            "abundance": round(float(abundance), 4),
            "emptiness": round(float(emptiness), 4),
            "gain": round(float(gain), 4),
        }

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

    def _compute_event_floor_ids(self, week: str) -> list[int]:
        """事件周议程保底：取全池（未退场、非置顶）中哀悼倾向分最高的 N 条，全员相同。

        用户 2026-09-12 裁定的议程设置：W13（去世周）所有 agent 的 feed 保底包含 5 条
        哀悼讯息 —— 等效"官方讣告 + 头版哀悼"的强制曝光。非事件周或 floor<=0 时返回空。
        该规则仅供 chronological / interest 使用；random 强反事实不调用本函数。

        用户 2026-09-13 补裁定（方案 B）：候选池剔除语料噪声类（`mech.floor_eligible`），
        因倾向分对短文本密度虚高，乱码噪音帖曾挤进全员强制位；不限定必须为 mourning 类型
        （实测同 N=5 下"仅取 mourning 类型"档 W13 悼念份额 0.555，比本口径 0.515 更差）。
        """
        if self._event_week_mourning_floor <= 0 or week != self._event_week:
            return []
        pinned_set = set(self._pinned_ids)
        pool = [pid for pid in self._live_candidates()
                if pid not in pinned_set
                and mech.floor_eligible(self._posts[pid].get("type", ""))]
        pool.sort(
            key=lambda pid: (-(self._posts[pid].get("tendencies") or {}).get("mourning", 0.0), -pid)
        )
        return pool[: self._event_week_mourning_floor]

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

    def _decay_post_lives(self, week: str) -> None:
        """每周开场把在池帖的时间生命乘一次冷却步长（帖子生命周期，用户 2026-09-12 裁定）。

        放在注入**之前**执行：本周新注入/新入池的帖保持 life=1.0（帖龄 0）。
        缺 life 字段的帖（老 checkpoint / 新代码混跑）按帖龄回填，保证幂等。
        """
        step = mech.weekly_decay(self._life_half_life_weeks)
        for pid, p in self._posts.items():
            life = p.get("life")
            if life is None:
                life = mech.life_at_age(
                    _post_age_weeks(week, p["week"]), self._life_half_life_weeks
                )
            p["life"] = float(life) * step

    def _live_candidates(self) -> list[int]:
        """候选池 = 全池中未退场的帖（生命周期机制）。

        chronological / interest 共用此活帖池：帖的时间生命低于退场线即退出视野，
        同时取代"候选窗口"这一独立旋钮。random 强反事实不调用本候选池。
        """
        return [
            pid
            for pid in sorted(self._posts)
            if not mech.is_retired(self._posts[pid].get("life", 1.0), self._life_retire_floor)
        ]

    def _post_vitality(self, pid: int) -> float:
        p = self._posts[pid]
        return mech.post_vitality(
            p.get("life", 1.0),
            int(p.get("exposure_count", 0)),
            self._life_saturation_scale,
        )

    def _interest_rank(self, aid: str, week: str, candidates: list[int]) -> list[tuple[float, int]]:
        """interest 臂：score = (alpha·倾向分匹配 + gamma)·生命力 + 均匀噪声[-eps,+eps]。

        倾向分匹配（用户裁定 2026-09-09）：取帖子四类倾向分中本 Agent 类型维度的值
        （词表命中次数/句长密度），替代此前的硬类型命中 + 词表重合两项（beta 项废弃，
        倾向分本身即词表命中的密度归一化）。已曝光帖按 exposure_mode none/penalize/exclude
        处理。无帖子级热度/互动项（纯兴趣匹配最小机制）。

        用户裁定 2026-09-12：时新项由**加性加成**（8 周后归零但不降权，老帖仍以 α·T
        竞争）改为**乘性生命力**（老帖整体打折并最终退场）。返回 (score, pid) 供调用方
        做比例抽样或确定性 top-k。"""
        atype = self._agent_types.get(aid, "other")
        seen = self._seen_by_agent.get(aid, set())
        eps = self._interest_noise_eps
        scored: list[tuple[float, int]] = []
        for pid in candidates:
            if self._exposure_mode == "exclude" and pid in seen:
                continue
            p = self._posts[pid]
            sc = mech.interest_score(
                (p.get("tendencies") or {}).get(atype, 0.0),
                self._alpha,
                self._gamma,
                self._post_vitality(pid),
            )
            if self._exposure_mode == "penalize" and pid in seen:
                sc -= self._exposure_penalty_weight
            if eps > 0:
                sc += self._rng_interest_noise.uniform(-eps, eps)
            scored.append((sc, pid))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return scored

    def _select_slots(self, scored: list[tuple[float, int]], k: int) -> list[int]:
        """按 exp(score/temperature) 无放回抽 k 条（用户裁定 2026-09-12 的"比例抽样"）。

        烟测诊断：只要"取分数最高的 k 条"这个操作还在、而高分帖数量 ≥ k，选出的集合就与
        agent 无关（同类型 18 人拿到同一份 top-10 → 气候 share_own 逐 agent sd=0 →
        D 的输入退化成 {0,1}）。改为比例抽样后，每个 agent 的 k 条成为"分数比例的样本"，
        逐 agent 有梯度。temperature<=0 退化为确定性 top-k（消融开关）。
        """
        if k <= 0 or not scored:
            return []
        if self._interest_sample_temp <= 0:
            return [pid for _, pid in scored[:k]]
        pids = [pid for _, pid in scored]
        weights = mech.softmax_weights([s for s, _ in scored], self._interest_sample_temp)
        return mech.weighted_sample_without_replacement(
            pids, weights, k, self._rng_interest_sample
        )

    def _assemble_feed(self, aid: str, week: str) -> list[dict[str, Any]]:
        """为单个 Agent 装配本周 feed。

        ``random`` 是强去策展反事实：从截至本周已经进入 Env 的**全部历史帖子**中
        等概率无放回抽取 ``feed_size`` 条，不读取帖子年龄、生命力、累计曝光、内容类型，
        也不应用官方置顶或事件周哀悼保底。未来帖子尚未进入 ``self._posts``，因此不会
        发生时间穿越。

        ``chronological`` 与 ``interest`` 保持原实现：先应用官方置顶和事件周保底，
        再从未退场活帖池中按各自逻辑填充剩余槽位。
        """
        alg = self._recommendation_algorithm
        if alg == "random":
            candidates = sorted(self._posts)
            take = min(self._feed_size, len(candidates))
            chosen = self._rng_feed_random.sample(candidates, take) if take > 0 else []
            return [self._feed_item(pid) for pid in chosen]

        pinned_set = set(self._pinned_ids)
        feed: list[dict[str, Any]] = []
        for pid in self._pinned_ids[: self._feed_size]:
            feed.append(self._feed_item(pid))
        # 事件周议程保底（用户 2026-09-12 裁定）：紧接置顶之后固定占 N 个槽位，全员相同。
        floor_set = set(self._event_floor_ids)
        for pid in self._event_floor_ids:
            if len(feed) >= self._feed_size:
                break
            feed.append(self._feed_item(pid))
        remaining = self._feed_size - len(feed)
        if remaining <= 0:
            return feed
        candidates = [
            pid for pid in self._live_candidates()
            if pid not in pinned_set and pid not in floor_set
        ]
        if alg == "chronological":
            candidates.sort(key=lambda pid: (_week_ord(self._posts[pid]["week"]), pid), reverse=True)
            chosen = candidates[:remaining]
        else:  # interest
            chosen = self._select_slots(self._interest_rank(aid, week, candidates), remaining)
        for pid in chosen:
            feed.append(self._feed_item(pid))
        return feed

    def _open_tick(self, week: str) -> None:
        """打开一个 tick：注入本周内容、计算玩梗涌现环境、官方置顶集合、预装配全部
        Agent 的 feed，并在装配时一次性记账曝光（get_feed 零副作用）。"""
        self._current_week = week
        self._tick_index = _week_ord(week) - _week_ord(self._start_week) + 1
        self._exposure_counts_tick = {}
        self._climate_shares = {}
        self._injected_this_week = {t: 0 for t in TYPE_ORDER_ALL}
        self._injected_this_week_ids = []
        self._official_injected_this_week = 0
        self._exposure_age_buckets = {"age0": 0, "age1": 0, "age2": 0, "age3plus": 0}

        # 0) 帖子生命周期：本周冷却步长（须在注入之前，保证新帖 life=1.0）。
        self._decay_post_lives(week)

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
                    "life": 1.0,  # 生命周期起点（用户 2026-09-12 裁定）
                    "tick_produced": self._tick_index,
                }
                self._injected_this_week[ttype] += 1
                self._injected_this_week_ids.append(pid)
                if self._posts[pid]["is_official"]:
                    self._official_injected_this_week += 1
                    self._official_pinned.setdefault(week, []).append(pid)

        # 2) 玩梗涌现环境（存量/流量/丰沛度/空旷度/涌现增益）。
        self._meme_env = self._compute_meme_env(week)

        # 3) 策展臂的官方置顶 + 事件周议程保底；random 强反事实不应用。
        # random 是全历史、全槽位均匀抽样的强去策展反事实：官方帖仍作为普通帖子存在于
        # self._posts，但不置顶，也不应用 W13 哀悼保底。其余两臂保持原平台议程设置。
        if self._recommendation_algorithm == "random":
            self._pinned_ids = []
            self._event_floor_ids = []
        else:
            self._pinned_ids = self._compute_pinned_ids(week)
            self._event_floor_ids = self._compute_event_floor_ids(week)

        # 4) 预装配全部 feed（曝光在装配时记账：1 次/agent/tick；get_feed 只读缓存快照）。
        self._feed_live_pool = (
            len(self._posts)
            if self._recommendation_algorithm == "random"
            else len(self._live_candidates())
        )
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
                # 老帖霸屏的直接指标：本周曝光槽位的帖龄分桶（0/1/2/≥3 周）。
                age = _post_age_weeks(week, self._posts[pid]["week"])
                self._exposure_age_buckets["age3plus" if age >= 3 else f"age{age}"] += 1
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
                "life": 1.0,  # 生命周期起点（用户 2026-09-12 裁定）
                "tick_produced": self._step_index,
            }
        self._pending_agent_posts = []
        self._agent_posts_pooled_prev = {rec["post_id"] for rec in merged}
        return merged

    def _env_row(self, week: str, merged: list[dict[str, Any]]) -> dict[str, Any]:
        """env 级指标（55 列，key 与 _env_state_columns 精确一致）。"""
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
            "meme_env_stock": self._meme_env["stock"],
            "meme_env_flow": self._meme_env["flow"],
            "meme_env_flow_world": self._meme_env["flow_world"],
            "meme_env_abundance": self._meme_env["abundance"],
            "meme_env_emptiness": self._meme_env["emptiness"],
            "meme_env_gain": self._meme_env["gain"],
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
        row["feed_live_pool"] = self._feed_live_pool
        row["feed_sample_temp"] = self._interest_sample_temp
        row["feed_half_life_weeks"] = self._life_half_life_weeks
        row["feed_saturation_scale"] = self._life_saturation_scale
        for bucket, cnt in self._exposure_age_buckets.items():
            row[f"exposure_slots_{bucket}"] = cnt
        row["event_floor_slots"] = len(self._event_floor_ids)
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
        """agent 级指标（21 列，batch 写）。"""
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
                    "meme_env_abundance_seen": self._meme_env["abundance"],
                    "meme_env_emptiness_seen": self._meme_env["emptiness"],
                    "meme_env_gain_seen": self._meme_env["gain"],
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

        **get_feed(agent_id)** 返回：当前周标签 **week**；本周玩梗涌现环境 **meme_env**
        （stock/flow=arena 存量与本周新增、flow_world=现实口径新增、abundance=丰沛度、
        emptiness=空旷度、gain=涌现增益）；您本周是否已发言 **own_spoke**；您最近一帖
        **own_last_post**；您的本周推荐信息流 **feed**（长度 = feed_size；chronological /
        interest 的官方置顶帖在前，random 无置顶，
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
        env = self._meme_env
        official_count = sum(1 for it in feed if it["is_official"])
        official_note = (
            f"官方来源 {official_count} 条（random 无置顶）"
            if self._recommendation_algorithm == "random"
            else f"官方置顶 {official_count} 条"
        )
        return {
            "status": "success",
            "week": self._current_week,
            "meme_env": {
                "stock": int(env["stock"]),
                "flow": int(env["flow"]),
                "flow_world": int(env["flow_world"]),
                "abundance": round(float(env["abundance"]), 4),
                "emptiness": round(float(env["emptiness"]), 4),
                "gain": round(float(env["gain"]), 4),
            },
            "own_spoke": bool(self._spoke_this_tick.get(aid, False)),
            "own_last_post": last,
            "feed": feed,
            "feed_type_distribution": climate,
            "global_supply_shares": dict(landscape.get("supply_shares", {})),
            "global_exposure_shares": dict(landscape.get("exposure_shares", {})),
            "personal_stats": stats,
            "response": (
                f"您在本周（{self._current_week}）的推荐信息流共 {len(feed)} 条"
                f"（{official_note}），"
                f"本周舆论场存量 {env['stock']} 帖、新增 {env['flow']} 帖"
                f"（现实口径新增 {env['flow_world']} 帖），"
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
        """打开 tick 1（W12）：注入本周内容、计算玩梗涌现环境、预装配全部 Agent 的 feed，并
        以 W12 注入池构成建立全局份额基线快照（U4）。无 replay 写入。"""
        self.t = start_datetime
        self._open_tick(self._weeks[0])
        self._set_baseline_landscape()

    async def step(self, tick: int, t: datetime) -> None:
        """每 tick 恰执行一次：先收尾当前 tick k（pending agent 帖并入池、写 env 1 行 +
        agent batch 行、更新全局份额快照、清空每 tick 状态），再预卷打开 tick k+1
        （注入、涌现环境、装配 feed）；step(11) 只收尾不打开 W23。replay 主键 = 内部 _step_index。"""
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

    def set_replay_writer(self, writer: Any) -> None:
        """只接受真正的 replay 写入器；其余一律拒绝并大声报错。

        背景：2026-09-13 的 9-run 批跑中，random_s2 与 interest_s1 两次出现
        ``AttributeError: 'dict' object has no attribute 'write'``（env/base.py:836）。
        引擎把该 run 在 step 0 就申报成 completed，而 curation_dynamics 两张表**全空**——
        既不报错也不留行。排查已排除 Ray 往返（``ReplayProxy.__getstate__`` /
        ``__setstate__`` 往返正常），只剩「迟到的 set_replay_writer 覆盖」一条路径：
        ``EnvBase.set_replay_writer`` 先赋值再 ``create_task`` 异步注册表，注册过程中
        若再来一次覆盖，表已注册（``_state_tables_registered=True``）而写入器已换人，
        于是 ``_write_env_state`` 跳过注册守卫、直接对非写入器调 ``.write``。

        这里的处理是**拒绝坏写入器、保留原有好写入器**：宁可少一次覆盖，也不能让一个
        非写入器对象把整张 replay 表写空——那种失败不报错、不留行，只能靠 step 数之外的
        独立校验（verify B10 / plot_arm_charts.check_replay）事后才发现。
        """
        if writer is not None and not all(
            callable(getattr(writer, m, None))
            for m in ("write", "write_batch", "register_table")
        ):
            logger.error(
                "拒绝非写入器对象，保留原写入器：传入 type=%s%s；原写入器 type=%s。调用栈：\n%s",
                type(writer).__name__,
                f" keys={sorted(writer)}" if isinstance(writer, dict) else "",
                type(getattr(self, "_replay_writer", None)).__name__,
                "".join(traceback.format_stack()[-6:-1]),
            )
            return
        super().set_replay_writer(writer)

    # ---------------- 描述（P2：散文+加粗函数名，面向中文 LLM Agent） ----------------

    @classmethod
    def description(cls) -> str:
        return (
            "舆论场数字表征转移模拟环境（CurationDynamicsSpace）：推荐算法单因子三臂"
            "（random / chronological / interest）下，100 个固定类型 Agent 的差异化激活与公共表征构成"
            "变化（张雪峰 2026-03-24 去世 W13，W12→W22 共 11 周）。Agent 每周通过 "
            "**get_feed(agent_id)** 查看本周推荐信息流、意见气候、玩梗涌现环境与全局供给/曝光"
            "份额，再决定是否发言；发言通过 **create_post(agent_id, content)** 发布一篇类型由"
            "其固定 Agent 类型决定的内容（每 tick 至多 1 帖，重复调用无效）。环境按周注入真实"
            "打标内容、按推荐算法装配 feed、逐周计算涌现环境（存量丰沛度 × 流量空旷度），"
            "并把供给/曝光/发言漏斗指标写入 replay 表供分析。"
        )

    @classmethod
    def init_description(cls) -> str:
        return (
            "CurationDynamicsSpace：舆论场数字表征转移模拟环境。全部构造参数均为关键字参数且含"
            "默认值（cls() 无必填参数）：**recommendation_algorithm** 推荐算法（random 从截至当周"
            "全部历史帖中全槽位均匀随机且无置顶/保底 / chronological 活帖池时间倒序 / interest "
            "活帖池纯兴趣匹配，默认 random）；"
            "**meme_emergence_mode** 玩梗涌现环境模式（normal 正常演化 / sustained_hot 反事实臂："
            "空旷度 S 冻结在事件周值、丰沛度 B 保持内生，默认 normal）；**random_seed** cell 种子"
            "（注入/随机臂/兴趣噪声三条 RNG 流由同一种子加固定偏移派生，默认 0）；"
            "**feed_size** 每 Agent 每 tick feed 槽位数（默认 20）；**sampling_ratio** 每周注入"
            "抽样比例（默认 0.05）；**injection_data_path** 注入数据集 JSON 路径（顶层含 posts "
            "数组，空串=无外部注入）；**vocab_path** 四词表判类器 JSON 路径（空串=词表为空，"
            "判类回落 other）；**agent_types** Agent 类型字典"
            "（{agent_id: meme|mourning|marketing|education|other}，未列出默认 other）；"
            "**start_week** 起始 ISO 周（默认 2026-W12）；**num_ticks** 总 tick 数（默认 11）；"
            "**event_week** 去世周（默认 2026-W13）；**official_pin_extend_weeks** 官方置顶延伸"
            "周数（默认 1）；interest 臂权重 **alpha**/**beta**/**gamma**、噪声幅度 "
            "**interest_noise_eps**、已曝光处理 "
            "**exposure_mode**（none/penalize/exclude）与 **exposure_penalty_weight**；"
            "**帖子生命周期**（仅 chronological / interest 使用；random 忽略）："
            "**life_half_life_weeks** 时间冷却半衰期"
            "（默认 1.5）、**life_saturation_scale** 曝光饱和尺度（累计曝光达该值生命折半，"
            "默认 20）、**life_retire_floor** 退场线（时间生命低于此值退出候选池，默认 0.05"
            "≈6.5 周龄）；**interest_sample_temp** interest 臂比例抽样温度（按 "
            "exp(score/temp) 无放回抽 feed_size 条，默认 4.0；<=0 退化为确定性 top-k）；"
            "涌现环境 **emergence_flow_by_week**（真实周新增帖量"
            "镜像调度 {周: 帖数}，空旷度 S 的外生流量口径，缺省回退内生 arena 计数）、"
            "**emergence_window_stock**（存量回看窗口周数，默认 6）、**emergence_ka**/**emergence_kf**"
            "（半饱和形状常数，缺省自动取注入计划的事件周存量与基线周流量）、"
            "**emergence_beta**/**emergence_sigma**（B/S 指数，默认 1）、"
            "**emergence_gain_min**/**emergence_gain_max**（G 截断，默认 0.2/3.0）。"
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
            "_meme_env": dict(self._meme_env),
            "_sustained_s": self._sustained_s,
            "_flow_by_week": {w: int(c) for w, c in self._flow_by_week.items()},
            "_global_landscape": self._global_landscape,
            "_seen_by_agent": {aid: sorted(ids) for aid, ids in self._seen_by_agent.items()},
            "_cumulative_exposures": self._cumulative_exposures,
            "_total_posts_by_agent": self._total_posts_by_agent,
            "_next_post_id": self._next_post_id,
            "_rng_injection": self._rng_injection.getstate(),
            "_rng_feed_random": self._rng_feed_random.getstate(),
            "_rng_interest_noise": self._rng_interest_noise.getstate(),
            "_rng_interest_sample": self._rng_interest_sample.getstate(),
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
        loaded_env = d.get("_meme_env") or {}
        self._meme_env = {
            "stock": int(loaded_env.get("stock", 0)),
            "flow": int(loaded_env.get("flow", 0)),
            "flow_world": int(loaded_env.get("flow_world", 0)),
            "abundance": float(loaded_env.get("abundance", 1.0)),
            "emptiness": float(loaded_env.get("emptiness", 1.0)),
            "gain": float(loaded_env.get("gain", 1.0)),
        }
        self._sustained_s = d.get("_sustained_s")
        self._flow_by_week = {str(w): int(c) for w, c in (d.get("_flow_by_week") or {}).items()}
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
        for key in (
            "_rng_injection",
            "_rng_feed_random",
            "_rng_interest_noise",
            "_rng_interest_sample",
        ):
            st = d.get(key)
            if st is not None:
                getattr(self, key).setstate(_rng_state_from_json(st))
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
