"""CurationDynamicsSpace — 算法策展动力学环境模块。

微博式全局 feed 的轻量社交环境，用于 H4「算法策展如何塑造逝者数字表征」实验
（参见 ``hypothesis_4/DESIGN_V0.3.md`` §3）。

定位
====
6 个类群代表 agent（借势营销 / 事件悼念讨论 / 其他讨论 / 教育观点讨论 / 梗文化讨论 /
水军低质号）+ 1 个权威媒体账号（env 侧、非问卷对象）在同一全局 feed 中互动。
实验操纵 = 推荐算法（``reddit_hot`` vs ``chronological``）；tick = 1 周，窗口 12 ticks。

相对内置 SocialMediaSpace 的 3 个新增机制（本模块的存在意义）：

1. **时间门控** —— 所有 feed / 候选集只包含 ``created_at <= self.t`` 的帖子，
   周级错峰供给的前提（内置版无此过滤，未来帖会泄漏）。
2. **事件显著性 S(t)** —— 外部关注：死亡事件时刻后立即跳 ``external_spike``，
   按半衰期指数衰减；内部关注：上一 tick 梗类内容互动增量 × ``internal_elasticity``
   回灌并同样指数衰减；``S = min(100, salience_floor + ext + internal)``。
   S(t) 以「全站热搜」条目暴露在 ``refresh_feed`` 上下文中。
3. **背景互动当量** —— 6-agent 互动稀薄，正反馈不足；按类群规模权重对每次实质
   动作（发 / 评 / 转 / 赞）以 ``Poisson(ambient_like_base_rate × weight ×
   (0.5 + 0.5·S/100))`` 合成被动点赞，计入帖子 ``likes_count``；逐动作明细写入
   ``curation_action`` 表供分析剥离。

持久化
======
- Replay（分析）：3 张表 ``curation_action`` / ``curation_step`` / ``curation_post``，
  通过 ``ColumnDef`` + ``ReplayWriter`` 注册写入。
- Workspace（resume）：``to_workspace()`` / ``restore()`` 把动态状态写到
  ``state/ENV_STATE.json``（帖子 / 人员 / S 状态 / 计数器 / 已赞集合 / 已写 replay 集合）。

仅继承 ``EnvBase``（P5）：本类体内的所有 ``@tool`` 方法均为重实现，不继承任何
具体 env 类的工具。
"""

import asyncio
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

from agentsociety2.env import EnvBase, tool
from agentsociety2.env.base import load_int_map
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef, ReplayDatasetSpec, TableSchema
from agentsociety2.storage.workspace_state import atomic_write_text

_STATE_REL = "state/ENV_STATE.json"

_SUPPORTED_ALGORITHMS = ("reddit_hot", "chronological")

# ---------------------------------------------------------------------------
# Replay schemas
# ---------------------------------------------------------------------------

_CURATION_ACTION_SCHEMA = TableSchema(
    name="curation_action",
    columns=[
        ColumnDef(
            "step",
            "INTEGER",
            nullable=False,
            logical_type="step",
            analysis_role="timestamp",
            description="Simulation step at which the substantive action was recorded.",
        ),
        ColumnDef(
            "t",
            "TIMESTAMP",
            nullable=False,
            logical_type="timestamp",
            analysis_role="timestamp",
            description="Simulation timestamp of the action.",
        ),
        ColumnDef(
            "agent_id",
            "INTEGER",
            nullable=False,
            logical_type="identifier",
            analysis_role="dimension",
            description="Agent (class-group representative) who performed the action.",
        ),
        ColumnDef(
            "action",
            "TEXT",
            nullable=False,
            logical_type="category",
            analysis_role="dimension",
            description="Substantive action type: post, repost, comment, like.",
        ),
        ColumnDef(
            "category",
            "TEXT",
            logical_type="category",
            analysis_role="dimension",
            description="Class group (topic category) of the target post.",
        ),
        ColumnDef(
            "target_post_id",
            "INTEGER",
            logical_type="identifier",
            analysis_role="dimension",
            description="Target post id; for post actions this is the newly created post id.",
        ),
        ColumnDef(
            "ambient_likes_synthesized",
            "REAL",
            nullable=False,
            logical_type="count",
            analysis_role="measure",
            description="Passive like equivalent synthesized for this action by the background interaction mechanism (0 when none).",
        ),
    ],
    primary_key=["step", "agent_id", "action", "target_post_id"],
    indexes=[["step"], ["agent_id"], ["target_post_id"]],
)

_CURATION_STEP_SCHEMA = TableSchema(
    name="curation_step",
    columns=[
        ColumnDef(
            "step",
            "INTEGER",
            nullable=False,
            logical_type="step",
            analysis_role="timestamp",
            description="Simulation step index (monotonic, one row per step() call).",
        ),
        ColumnDef(
            "t",
            "TIMESTAMP",
            nullable=False,
            logical_type="timestamp",
            analysis_role="timestamp",
            description="Simulation timestamp at the end of this step.",
        ),
        ColumnDef(
            "s_external",
            "REAL",
            nullable=False,
            logical_type="measure",
            analysis_role="measure",
            description="External attention component of event salience S(t).",
        ),
        ColumnDef(
            "s_internal",
            "REAL",
            nullable=False,
            logical_type="measure",
            analysis_role="measure",
            description="Internal (meme-feedback) attention component of S(t).",
        ),
        ColumnDef(
            "s_total",
            "REAL",
            nullable=False,
            logical_type="measure",
            analysis_role="measure",
            description="Total event salience S(t) = min(100, salience_floor + external + internal).",
        ),
        ColumnDef(
            "posts_by_category_json",
            "JSON",
            logical_type="category",
            analysis_role="dimension",
            description="Posts created during this step, aggregated by class group category.",
        ),
        ColumnDef(
            "engagement_by_category_json",
            "JSON",
            logical_type="category",
            analysis_role="dimension",
            description="Engagement increments (likes/comments/reposts) during this step, aggregated by target post category.",
        ),
        ColumnDef(
            "feed_refresh_count",
            "INTEGER",
            nullable=False,
            logical_type="count",
            analysis_role="measure",
            description="Number of refresh_feed calls issued during this step.",
        ),
    ],
    primary_key=["step"],
    indexes=[["t"]],
)

_CURATION_POST_SCHEMA = TableSchema(
    name="curation_post",
    columns=[
        ColumnDef(
            "post_id",
            "INTEGER",
            nullable=False,
            logical_type="identifier",
            analysis_role="identifier",
            description="Post id.",
        ),
        ColumnDef(
            "author_id",
            "INTEGER",
            nullable=False,
            logical_type="identifier",
            analysis_role="dimension",
            description="Author agent id.",
        ),
        ColumnDef(
            "category",
            "TEXT",
            logical_type="category",
            analysis_role="dimension",
            description="Class group (topic category) of the post (usually tags[0]).",
        ),
        ColumnDef(
            "created_at",
            "TIMESTAMP",
            nullable=False,
            logical_type="timestamp",
            analysis_role="timestamp",
            description="Post creation time.",
        ),
        ColumnDef(
            "content",
            "TEXT",
            logical_type="text",
            analysis_role="metadata",
            description="Post content.",
        ),
        ColumnDef(
            "is_media",
            "INTEGER",
            nullable=False,
            logical_type="category",
            analysis_role="dimension",
            description="1 if authored by the authoritative media account, else 0.",
        ),
        ColumnDef(
            "ambient_likes_total",
            "REAL",
            nullable=False,
            logical_type="count",
            analysis_role="measure",
            description="Cumulative background-interaction likes on this post at write time (0 at creation).",
        ),
    ],
    primary_key=["post_id"],
    indexes=[["author_id"], ["category"]],
)


class CurationDynamicsSpace(EnvBase):
    """算法策展动力学环境（微博式全局 feed，6 类群代表 + 权威媒体）。

    Agent 通过 ``refresh_feed`` 观察全站 feed 与事件热度热搜行，通过
    ``create_post`` / ``repost`` / ``comment_on_post`` / ``like_post`` 表达互动，
    通过 ``view_post`` 查看帖文详情。推荐算法（reddit_hot / chronological）在构造时
    固定，是唯一实验操纵变量。
    """

    # ---- Skill Discovery ----
    # 单文件模块约定：custom/envs/curation_dynamics_agent_skills/social-media-curation/SKILL.md

    @classmethod
    def skill_dirs(cls) -> list[Path]:
        """返回本环境附带的 agent 技能目录（``<模块目录>/<stem>_agent_skills/``）。"""
        skills_dir = Path(__file__).parent / "curation_dynamics_agent_skills"
        return [skills_dir] if skills_dir.is_dir() else []

    def __init__(
        self,
        agent_id_name_pairs: Optional[
            List[Tuple[int, str]] | List[List[Any]]
        ] = None,
        persons: Optional[Dict[Any, Any]] = None,
        posts: Optional[Dict[Any, Any]] = None,
        comments: Optional[Dict[Any, Any]] = None,
        likes: Optional[Dict[Any, Any]] = None,
        recommendation_algorithm: str = "reddit_hot",
        random_seed: int = 42,
        event_start_iso: Optional[str] = None,
        external_spike: float = 100.0,
        external_half_life_weeks: float = 2.0,
        internal_elasticity: float = 0.3,
        internal_decay_half_life_weeks: float = 1.0,
        salience_floor: float = 5.0,
        class_size_weights: Optional[Dict[Any, float]] = None,
        ambient_like_base_rate: float = 8.0,
        feed_limit: int = 20,
        **kwargs: Any,
    ):
        """初始化算法策展动力学环境。

        :param agent_id_name_pairs: 显式 agent–类群映射 [[agent_id, name], ...]，
            例如 [[1,"借势营销"], ..., [999,"权威媒体"]]。用于构建类群名与媒体账号集合。
        :param persons: 初始用户，key=person_id, value 为可序列化 dict（至少含 id）。
        :param posts: 初始帖子（供给池），key=post_id, value 为 Post 可序列化 dict
            （post_id, author_id, content, post_type, parent_id, created_at(ISO),
            likes_count, reposts_count, comments_count, view_count, tags=[类群,平台],
            topic_category）。
        :param comments: 初始评论，key=post_id, value=评论 dict 列表（本模块工具不新增评论对象）。
        :param likes: 初始点赞关系，key=user_id, value=已赞 post_id 列表。
        :param recommendation_algorithm: 推荐算法，"reddit_hot" | "chronological"
            （仅支持这两种，其他值抛 ValueError）。
        :param random_seed: 背景互动当量独立 RNG 的种子（不污染其他随机性）。
        :param event_start_iso: 死亡事件时刻（ISO 字符串），事件后外部关注脉冲注入。
        :param external_spike: 外部关注峰值（默认 100）。
        :param external_half_life_weeks: 外部关注半衰期（周，默认 2.0）。
        :param internal_elasticity: 内部关注回灌弹性（默认 0.3）。
        :param internal_decay_half_life_weeks: 内部关注半衰期（周，默认 1.0）。
        :param salience_floor: 事件前基线热度（默认 5）。
        :param class_size_weights: 类群规模权重 {agent_id: weight}（全量占比）。
        :param ambient_like_base_rate: 每次实质动作合成的被动点赞当量均值（默认 8.0）。
        :param feed_limit: refresh_feed 返回条数上限（默认 20）。
        """
        super().__init__()

        # ---- 构造配置（resume 时由 env_kwargs 重建，不写入 ENV_STATE.json）----
        self._agent_id_name_pairs: List[Tuple[int, str]] = []
        if agent_id_name_pairs:
            for pair in agent_id_name_pairs:
                if isinstance(pair, (list, tuple)) and len(pair) == 2:
                    self._agent_id_name_pairs.append((int(pair[0]), str(pair[1])))
                else:
                    raise ValueError(
                        f"Invalid agent_id_name_pair: {pair}. "
                        f"Expected [agent_id, name] or (agent_id, name)"
                    )
        self._agent_names: Dict[int, str] = {
            aid: name for aid, name in self._agent_id_name_pairs
        }

        if recommendation_algorithm not in _SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported recommendation_algorithm: {recommendation_algorithm!r}. "
                f"Supported: {_SUPPORTED_ALGORITHMS}"
            )
        self._recommendation_algorithm: str = recommendation_algorithm

        self._random_seed: int = int(random_seed)
        # 独立 RNG 实例，仅用于背景互动当量合成，不污染其他随机性（不序列化，__init__ 重建）
        self._rng = random.Random(self._random_seed)

        # 事件显著性参数
        self._event_start: Optional[datetime] = None
        if event_start_iso is not None:
            self._event_start = self._parse_dt(event_start_iso)
        self._external_spike: float = float(external_spike)
        self._external_half_life_weeks: float = float(external_half_life_weeks)
        self._internal_elasticity: float = float(internal_elasticity)
        self._internal_decay_half_life_weeks: float = float(
            internal_decay_half_life_weeks
        )
        self._salience_floor: float = float(salience_floor)

        # 背景互动当量参数
        self._class_size_weights: Dict[int, float] = {
            int(k): float(v) for k, v in (class_size_weights or {}).items()
        }
        self._ambient_like_base_rate: float = float(ambient_like_base_rate)
        self._feed_limit: int = int(feed_limit)

        # 初始数据（init() 时应用）
        self._initial_persons = persons
        self._initial_posts = posts
        self._initial_comments = comments
        self._initial_likes = likes

        # ---- 动态状态（resume 时由 restore() 覆盖）----
        self._lock = asyncio.Lock()
        self._persons: Dict[int, Dict[str, Any]] = {}
        self._posts: Dict[int, Dict[str, Any]] = {}
        self._comments: Dict[int, List[Any]] = defaultdict(list)
        self._liked_pairs: Set[Tuple[int, int]] = set()

        self._next_post_id: int = 1

        # 媒体账号集合（权威媒体，非问卷对象）
        self._media_agent_ids: Set[int] = {
            aid
            for aid, name in self._agent_id_name_pairs
            if "媒体" in str(name) or "media" in str(name).lower()
        }
        if not self._media_agent_ids and 999 in {
            int(k) for k in (persons or {})
        }:
            self._media_agent_ids.add(999)

        # 事件显著性 S(t) 状态
        self._s_external: float = 0.0
        self._s_internal: float = 0.0
        self._s_total: float = float(self._salience_floor)
        self._meme_engagement_this_tick: int = 0

        # 每 tick 累积缓冲（step() 末尾消费并重置）
        self._pending_action_rows: List[dict] = []
        self._pending_post_rows: List[dict] = []
        self._tick_action_log: List[dict] = []
        self._posts_created_this_step: Dict[str, int] = {}
        self._feed_refresh_count_this_step: int = 0

        # 去重状态（P3：同一步重复调用安全）
        self._repost_seen_keys: Set[Tuple[int, int, int]] = set()
        self._create_seen_keys: Set[Tuple[int, str, int]] = set()
        self._comment_seen_keys: Set[Tuple[int, int, str, int]] = set()

        # replay 后设状态（避免 resume 重复写初始帖子行）
        self._posts_replay_written: Set[int] = set()
        self._initial_posts_dumped: bool = False

        # replay 计数器
        self._step_counter: int = 0
        self._replay_event_id: int = 0
        self._recent_actions = []

        get_logger().info(
            "CurationDynamicsSpace initialized (algorithm=%s, seed=%d, feed_limit=%d)",
            self._recommendation_algorithm,
            self._random_seed,
            self._feed_limit,
        )

    # ------------------------------------------------------------------
    # 时间处理辅助（tz 对齐，兼容 aware/naive 混用）
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_dt(value: Any) -> datetime:
        """把 ISO 字符串（或 datetime）解析为 datetime（``Z`` → ``+00:00``）。"""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    @staticmethod
    def _align_tz(dt: datetime, ref: datetime) -> datetime:
        """把 ``dt`` 的 tz 感知性与 ``ref`` 对齐，使其可直接比较。"""
        if dt.tzinfo is None and ref.tzinfo is not None:
            return dt.replace(tzinfo=ref.tzinfo)
        if dt.tzinfo is not None and ref.tzinfo is None:
            return dt.replace(tzinfo=None)
        return dt

    @staticmethod
    def _as_utc(dt: datetime) -> datetime:
        """转为 UTC 感知 datetime（naive 视为 UTC），用于时长计算。"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _epoch_seconds(dt: datetime) -> float:
        """1970-01-01 起的秒数（tz 安全）。"""
        if dt.tzinfo is not None:
            return dt.timestamp()
        return (dt - datetime(1970, 1, 1)).total_seconds()

    # ------------------------------------------------------------------
    # 数据归一化
    # ------------------------------------------------------------------

    @staticmethod
    def _norm_person(data: Any) -> Dict[str, Any]:
        d = dict(data)
        d["id"] = int(d["id"])
        d.setdefault("name", str(d["id"]))
        return d

    @staticmethod
    def _norm_post(data: Any) -> Dict[str, Any]:
        d = dict(data)
        d["post_id"] = int(d["post_id"])
        d["author_id"] = int(d["author_id"])
        if "created_at" in d and isinstance(d["created_at"], str):
            d["created_at"] = CurationDynamicsSpace._parse_dt(d["created_at"])
        d.setdefault("post_type", "original")
        d.setdefault("parent_id", None)
        d.setdefault("likes_count", 0)
        d.setdefault("reposts_count", 0)
        d.setdefault("comments_count", 0)
        d.setdefault("view_count", 0)
        d.setdefault("tags", [])
        d.setdefault("topic_category", None)
        for k in ("likes_count", "reposts_count", "comments_count", "view_count"):
            d[k] = int(d.get(k) or 0)
        d["tags"] = [str(t) for t in (d.get("tags") or [])]
        return d

    # ------------------------------------------------------------------
    # 语义辅助
    # ------------------------------------------------------------------

    def _category_of(self, post: Dict[str, Any]) -> str:
        """帖子所属类群（分类）：tags[0]（类群），否则按作者类群名。"""
        tags = post.get("tags") or []
        if tags and str(tags[0]).strip():
            return str(tags[0])
        return self._agent_names.get(post["author_id"], "unknown")

    def _is_media_author(self, author_id: int) -> bool:
        return author_id in self._media_agent_ids

    def _is_meme_post(self, post: Dict[str, Any]) -> bool:
        """梗类内容判定：topic_category 含 "meme" 或 "梗"，或任一 tag 含之。"""
        texts: List[str] = []
        tc = post.get("topic_category")
        if tc:
            texts.append(str(tc))
        texts.extend(str(t) for t in (post.get("tags") or []))
        return any(("meme" in t.lower()) or ("梗" in t) for t in texts)

    def _person_name(self, agent_id: int) -> str:
        return self._agent_names.get(agent_id, f"agent_{agent_id}")

    # ------------------------------------------------------------------
    # 推荐算法（照抄内置 recommend.py 公式，tz 安全化）
    # ------------------------------------------------------------------

    def _sort_feed(self, posts: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """按构造时配置的推荐算法排序候选帖子，取前 limit 条。"""
        if self._recommendation_algorithm == "chronological":
            ordered = sorted(posts, key=lambda p: p["created_at"], reverse=True)
            return ordered[:limit]
        # reddit_hot
        def hot_score(post: Dict[str, Any]) -> float:
            s = int(post["likes_count"])
            order = math.log10(max(abs(s), 1))
            sign = 1 if s > 0 else 0 if s == 0 else -1
            epoch_seconds = self._epoch_seconds(post["created_at"])
            reddit_epoch = 1134028003
            seconds = epoch_seconds - reddit_epoch
            return round(sign * order + seconds / 45000.0, 7)

        ordered = sorted(posts, key=hot_score, reverse=True)
        return ordered[:limit]

    def _get_candidate_posts(self) -> List[Dict[str, Any]]:
        """候选集 = created_at <= self.t 的全部帖子（时间门控）。"""
        t = self.t
        return [
            p
            for p in self._posts.values()
            if self._align_tz(p["created_at"], t) <= t
        ]

    def _engagement(self, post: Dict[str, Any]) -> int:
        return (
            int(post["likes_count"])
            + int(post["comments_count"])
            + int(post["reposts_count"])
        )

    # ------------------------------------------------------------------
    # 背景互动当量
    # ------------------------------------------------------------------

    def _ambient_lambda(self, agent_id: int) -> float:
        """某 agent 一次实质动作的被动点赞 Poisson 速率 λ。"""
        weight = self._class_size_weights.get(agent_id, 1.0)
        salience_factor = 0.5 + 0.5 * (self._s_total / 100.0)
        return self._ambient_like_base_rate * weight * salience_factor

    @staticmethod
    def _poisson_sample(rng: random.Random, lam: float) -> int:
        """Knuth 泊松采样（``random.Random`` 无内建 poisson，用独立 RNG 实现）。"""
        if lam <= 0.0:
            return 0
        limit = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            k += 1
            p *= rng.random()
            if p <= limit:
                return k - 1

    def _record_action(
        self,
        agent_id: int,
        action: str,
        target_post_id: Optional[int],
        category: Optional[str],
    ) -> None:
        """记录一次实质动作到本 tick 日志（供背景互动当量与聚合行使用）。"""
        self._replay_event_id += 1
        row = {
            "id": self._replay_event_id,
            "step": self._step_counter,
            "t": self.t,
            "agent_id": int(agent_id),
            "action": action,
            "category": category,
            "target_post_id": target_post_id,
            "ambient_likes_synthesized": 0.0,
        }
        self._pending_action_rows.append(row)
        self._recent_actions.append(dict(row))
        self._tick_action_log.append(
            {
                "agent_id": int(agent_id),
                "action": action,
                "target_post_id": target_post_id,
                "category": category,
            }
        )

    # ------------------------------------------------------------------
    # 持久化（resume）
    # ------------------------------------------------------------------

    async def to_workspace(self, workspace_path=None) -> None:
        """写入 ``state/ENV_STATE.json``（原子写）。

        序列化：帖子 / 人员 / 评论 / 已赞集合 / S 状态 / 计数器 / 已写 replay 集合 /
        待刷写缓冲。``_rng``（random.Random）与 ``asyncio.Lock`` 不序列化，
        由 ``__init__`` 从 ``random_seed`` 重建。
        """
        if workspace_path is not None:
            self._bind_workspace(workspace_path)
        if self._workspace_root is None:
            raise RuntimeError("Env module workspace is not bound")
        atomic_write_text(
            self._workspace_root / _STATE_REL,
            json.dumps(
                {
                    "persons": {
                        str(pid): p for pid, p in self._persons.items()
                    },
                    "posts": {
                        str(pid): {
                            **p,
                            "created_at": (
                                p["created_at"].isoformat()
                                if isinstance(p["created_at"], datetime)
                                else p["created_at"]
                            ),
                        }
                        for pid, p in self._posts.items()
                    },
                    "comments": {
                        str(pid): list(cs) for pid, cs in self._comments.items()
                    },
                    "liked_pairs": sorted(
                        (a, b) for a, b in self._liked_pairs
                    ),
                    "next_post_id": self._next_post_id,
                    "s_external": self._s_external,
                    "s_internal": self._s_internal,
                    "s_total": self._s_total,
                    "meme_engagement_this_tick": self._meme_engagement_this_tick,
                    "pending_action_rows": list(self._pending_action_rows),
                    "pending_post_rows": list(self._pending_post_rows),
                    "recent_actions": list(self._recent_actions),
                    "replay_event_id": self._replay_event_id,
                    "posts_replay_written": sorted(self._posts_replay_written),
                    "initial_posts_dumped": self._initial_posts_dumped,
                    "step_counter": self._step_counter,
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
        )

    async def restore(self, workspace_path) -> bool:
        """从 ``state/ENV_STATE.json`` 恢复动态状态（晚于 ``init()``，覆盖重置）。

        ``_rng`` / 推荐算法 / 参数由 ``__init__`` 从 env_kwargs 重建，不在此覆盖。
        """
        self._bind_workspace(workspace_path)
        state_path = self._workspace_root / _STATE_REL
        if not state_path.is_file():
            return False
        d = json.loads(state_path.read_text(encoding="utf-8"))
        self._persons = {
            int(pid): self._norm_person(p)
            for pid, p in load_int_map(d.get("persons")).items()
        }
        posts_raw = load_int_map(d.get("posts"))
        self._posts = {
            pid: self._norm_post(p) for pid, p in posts_raw.items()
        }
        comments_raw = load_int_map(d.get("comments"))
        self._comments = defaultdict(
            list,
            {pid: list(cs) for pid, cs in comments_raw.items()},
        )
        self._liked_pairs = {
            (int(a), int(b)) for a, b in d.get("liked_pairs", [])
        }
        self._next_post_id = int(d.get("next_post_id", 1))
        self._s_external = float(d.get("s_external", 0.0))
        self._s_internal = float(d.get("s_internal", 0.0))
        self._s_total = float(d.get("s_total", self._salience_floor))
        self._meme_engagement_this_tick = int(
            d.get("meme_engagement_this_tick", 0)
        )
        self._pending_action_rows = list(d.get("pending_action_rows", []))
        self._pending_post_rows = list(d.get("pending_post_rows", []))
        # 与 pending_action_rows 同源的 tick 日志（恢复后重建，保证中断恢复后聚合正确）
        self._tick_action_log = [
            {
                "agent_id": int(r["agent_id"]),
                "action": r["action"],
                "target_post_id": r.get("target_post_id"),
                "category": r.get("category"),
            }
            for r in self._pending_action_rows
        ]
        self._recent_actions = list(d.get("recent_actions", []))
        self._replay_event_id = int(d.get("replay_event_id", 0))
        self._posts_replay_written = {
            int(pid) for pid in d.get("posts_replay_written", [])
        }
        self._initial_posts_dumped = bool(d.get("initial_posts_dumped", False))
        self._step_counter = int(d.get("step_counter", 0))
        return True

    # ------------------------------------------------------------------
    # Replay（curation_action / curation_step / curation_post）
    # ------------------------------------------------------------------

    async def _register_event_table(self) -> None:
        """注册 3 张 replay 表 + dataset 元数据（幂等）。"""
        if self._replay_writer is None:
            return
        writer = self._replay_writer
        await writer.register_table(_CURATION_ACTION_SCHEMA)
        await writer.register_dataset(
            ReplayDatasetSpec(
                dataset_id="curation.action",
                table_name="curation_action",
                module_name=self.name,
                kind="event_stream",
                title="Curation Dynamics Action Stream",
                description="Substantive social actions (post/repost/comment/like) with per-action background like synthesis, exported by CurationDynamicsSpace.",
                entity_key="agent_id",
                step_key="step",
                time_key="t",
                default_order=["step", "id"],
                capabilities=["event_stream", "social_event", "curation"],
            ),
            _CURATION_ACTION_SCHEMA.columns,
        )
        await writer.register_table(_CURATION_STEP_SCHEMA)
        await writer.register_dataset(
            ReplayDatasetSpec(
                dataset_id="curation.step",
                table_name="curation_step",
                module_name=self.name,
                kind="env_snapshot",
                title="Curation Dynamics Step Snapshot",
                description="Per-step event salience S(t) and category-aggregated supply/engagement, exported by CurationDynamicsSpace.",
                entity_key=None,
                step_key="step",
                time_key="t",
                default_order=["step"],
                capabilities=["env_snapshot", "timeseries", "salience"],
            ),
            _CURATION_STEP_SCHEMA.columns,
        )
        await writer.register_table(_CURATION_POST_SCHEMA)
        await writer.register_dataset(
            ReplayDatasetSpec(
                dataset_id="curation.post",
                table_name="curation_post",
                module_name=self.name,
                kind="entity_static",
                title="Curation Dynamics Post Registry",
                description="Post creation registry (author, class-group category, media flag, ambient likes at write time), exported by CurationDynamicsSpace.",
                entity_key="post_id",
                step_key=None,
                time_key="created_at",
                default_order=["post_id"],
                capabilities=["entity", "post"],
            ),
            _CURATION_POST_SCHEMA.columns,
        )
        get_logger().info("Registered curation_action / curation_step / curation_post tables")

    def _schedule_replay_task(self, coro) -> None:
        if self._replay_writer is None:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return
        asyncio.create_task(coro)

    def _build_post_replay_row(self, post: Dict[str, Any]) -> dict:
        return {
            "post_id": int(post["post_id"]),
            "author_id": int(post["author_id"]),
            "category": self._category_of(post),
            "created_at": post["created_at"],
            "content": str(post.get("content", "")),
            "is_media": 1 if self._is_media_author(post["author_id"]) else 0,
            "ambient_likes_total": 0.0,
        }

    def _queue_post_replay_row(self, post: Dict[str, Any]) -> None:
        """为新建帖子缓冲 curation_post 行（创建时写入）。"""
        pid = int(post["post_id"])
        if pid in self._posts_replay_written:
            return
        self._pending_post_rows.append(self._build_post_replay_row(post))
        self._posts_replay_written.add(pid)

    def _dump_initial_posts_to_replay(self) -> None:
        """首次 step() 时把供给池初始帖子补写为 curation_post 行（防 resume 重复）。"""
        if self._initial_posts_dumped:
            return
        for pid, post in self._posts.items():
            if pid not in self._posts_replay_written:
                self._pending_post_rows.append(self._build_post_replay_row(post))
                self._posts_replay_written.add(pid)
        self._initial_posts_dumped = True

    async def _flush_replay(self) -> None:
        """把缓冲的 action / post / step 行刷写到 replay（step 末尾调用）。"""
        if self._replay_writer is None:
            self._pending_action_rows.clear()
            self._pending_post_rows.clear()
            return
        writer = self._replay_writer
        if self._pending_action_rows:
            await writer.write_batch("curation_action", self._pending_action_rows)
            self._pending_action_rows.clear()
        if self._pending_post_rows:
            await writer.write_batch("curation_post", self._pending_post_rows)
            self._pending_post_rows.clear()

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    @classmethod
    def description(cls) -> str:
        """返回模块简短描述。"""
        return (
            "Curation dynamics social media environment: Weibo-style global feed with "
            "event salience S(t) and background interaction synthesis, for the "
            "algorithmic-curation (reddit_hot vs chronological) experiment."
        )

    @classmethod
    def init_description(cls) -> str:
        """返回 AI 可读的初始化指导（散文体 + 加粗参数名，见 pitfalls P2）。"""
        return f"""{cls.__name__}: 算法策展动力学社交媒体环境模块（微博式全局 feed）。

**Description:** 6 个类群代表 agent + 1 个权威媒体账号在同一全局 feed 中互动；
实验操纵 = 推荐算法（reddit_hot 热度加权 vs chronological 时间线）。三个新增机制：
时间门控（仅可见 created_at <= 当前仿真时间的帖子）、事件显著性 S(t)（外部脉冲 +
梗类互动回灌，以全站热搜暴露）、背景互动当量（按类群规模权重合成被动点赞）。

**Initialization Parameters:**
- **agent_id_name_pairs** (list of [agent_id, name], optional): 显式 agent–类群映射，
  例如 [[1,"借势营销"], ..., [999,"权威媒体"]]；用于类群名与媒体账号识别。
- **persons** (dict, optional): 初始用户，key=person_id, value 为 dict（至少含 id）。
- **posts** (dict, optional): 初始帖子（供给池），key=post_id, value 为 dict
  （post_id, author_id, content, post_type, parent_id, created_at ISO,
  likes_count, reposts_count, comments_count, view_count, tags=[类群, 平台],
  topic_category）。
- **comments** (dict, optional): 初始评论，key=post_id, value=评论 dict 列表。
- **likes** (dict, optional): 初始点赞关系，key=user_id, value=已赞 post_id 列表。
- **recommendation_algorithm** (str, default "reddit_hot"): 推荐算法，
  仅支持 "reddit_hot" | "chronological"，其他值抛 ValueError。
- **random_seed** (int, default 42): 背景互动当量独立 RNG 种子。
- **event_start_iso** (str, optional): 死亡事件时刻（ISO）。
- **external_spike** (float, default 100.0): 外部关注峰值。
- **external_half_life_weeks** (float, default 2.0): 外部关注半衰期（周）。
- **internal_elasticity** (float, default 0.3): 梗类互动回灌弹性。
- **internal_decay_half_life_weeks** (float, default 1.0): 内部关注半衰期（周）。
- **salience_floor** (float, default 5.0): 事件前基线热度。
- **class_size_weights** (dict, optional): 类群规模权重 {{agent_id: weight}}。
- **ambient_like_base_rate** (float, default 8.0): 被动点赞当量 Poisson 速率均值。
- **feed_limit** (int, default 20): refresh_feed 返回条数上限。

**Example initialization config:**
```json
{{
  "agent_id_name_pairs": [[1, "借势营销"], [2, "事件悼念讨论"], [5, "梗文化讨论"], [999, "权威媒体"]],
  "posts": {{ "1": {{ "post_id": 1, "author_id": 999, "content": "官方通报", "post_type": "original",
    "created_at": "2026-03-24T08:00:00+08:00", "likes_count": 100, "reposts_count": 20,
    "comments_count": 30, "view_count": 1000, "tags": ["事件悼念讨论", "微博"], "topic_category": "事件悼念讨论" }} }},
  "comments": {{}},
  "likes": {{}},
  "recommendation_algorithm": "reddit_hot",
  "random_seed": 42,
  "event_start_iso": "2026-03-24T00:00:00+08:00",
  "class_size_weights": {{ "1": 0.306, "2": 0.170, "3": 0.163, "4": 0.147, "5": 0.136, "6": 0.076 }}
}}
```
"""

    async def init(self, start_datetime: datetime):
        """初始化环境：应用初始数据、重置动态状态、注册 replay 表。"""
        self.t = start_datetime
        self._apply_initial_data()
        # 重置每 tick 缓冲与去重状态（fresh 运行）
        self._s_external = 0.0
        self._s_internal = 0.0
        self._s_total = float(self._salience_floor)
        self._meme_engagement_this_tick = 0
        self._pending_action_rows = []
        self._pending_post_rows = []
        self._tick_action_log = []
        self._posts_created_this_step = {}
        self._feed_refresh_count_this_step = 0
        self._repost_seen_keys = set()
        self._create_seen_keys = set()
        self._comment_seen_keys = set()
        self._posts_replay_written = set()
        self._initial_posts_dumped = False
        self._step_counter = 0
        self._replay_event_id = 0
        self._recent_actions = []
        if self._replay_writer is not None:
            await self._register_event_table()

    def _apply_initial_data(self) -> None:
        """从构造初始数据填充 persons / posts / comments / liked_pairs。"""
        self._persons = {
            int(uid): self._norm_person(data)
            for uid, data in (self._initial_persons or {}).items()
        }
        # 显式映射中尚未存在于 persons 的 id 补建（含权威媒体）
        for aid, name in self._agent_id_name_pairs:
            if aid not in self._persons:
                self._persons[aid] = {"id": aid, "name": name}
        self._posts = {
            int(pid): self._norm_post(data)
            for pid, data in (self._initial_posts or {}).items()
        }
        self._comments = defaultdict(
            list,
            {
                int(pid): list(cs)
                for pid, cs in (self._initial_comments or {}).items()
            },
        )
        self._next_post_id = max(self._posts.keys()) + 1 if self._posts else 1
        # 初始点赞关系：填充已赞集合（likes_count 以供给池数据为准，不叠加）
        for uid, post_ids in (self._initial_likes or {}).items():
            uid = int(uid)
            for pid in post_ids:
                self._liked_pairs.add((uid, int(pid)))
        # 媒体账号回填
        if not self._media_agent_ids and 999 in self._persons:
            self._media_agent_ids.add(999)
        get_logger().info(
            "CurationDynamicsSpace applied initial data: %d persons, %d posts",
            len(self._persons),
            len(self._posts),
        )

    def set_replay_writer(self, writer) -> None:
        """绑定 replay writer 并异步注册 3 张表。"""
        super().set_replay_writer(writer)
        if writer is not None:
            self._schedule_replay_task(self._register_event_table())

    async def step(self, tick: int, t: datetime):
        """推进一个仿真步（tick = 1 周）。

        顺序：更新时间门控基准 → 更新事件显著性 S(t) → 合成背景互动当量 → 写
        ``curation_step`` 聚合行 → 刷写 replay → 推进计数器、重置 tick 局部缓冲。

        :param tick: 本步时间跨度（周）。
        :param t: 本步结束后的仿真时间。
        """
        self.t = t

        # 1) 把供给池初始帖子补写为 curation_post 行（fresh 首次 step）
        self._dump_initial_posts_to_replay()

        # 2) 更新事件显著性 S(t)
        self._update_salience(t)

        # 3) 合成背景互动当量（基于本 tick 实质动作日志）
        self._synthesize_ambient_likes()

        # 4) 聚合本步的供给 / 互动 / 热搜刷新计数，写 curation_step 行
        posts_by_category = dict(self._posts_created_this_step)
        engagement_by_category = self._aggregate_engagement_by_category()
        step_row = {
            "step": self._step_counter,
            "t": t,
            "s_external": round(self._s_external, 4),
            "s_internal": round(self._s_internal, 4),
            "s_total": round(self._s_total, 4),
            "posts_by_category_json": posts_by_category,
            "engagement_by_category_json": engagement_by_category,
            "feed_refresh_count": self._feed_refresh_count_this_step,
        }
        if self._replay_writer is not None:
            await self._replay_writer.write("curation_step", step_row)

        # 5) 刷写 action / post 行
        await self._flush_replay()

        # 6) 推进计数器，重置 tick 局部缓冲
        self._step_counter += 1
        self._tick_action_log = []
        self._posts_created_this_step = {}
        self._feed_refresh_count_this_step = 0
        self._meme_engagement_this_tick = 0

    def _update_salience(self, t: datetime) -> None:
        """更新事件显著性 S(t)：外部关注即时脉冲 + 指数衰减，内部关注回灌 + 指数衰减。"""
        # 外部关注：事件后立即跳 external_spike，此后按半衰期指数衰减
        if self._event_start is not None and self._align_tz(
            self._event_start, t
        ) <= t:
            dt_weeks = (
                self._as_utc(t) - self._as_utc(self._event_start)
            ).total_seconds() / (7 * 86400.0)
            ext = self._external_spike * 0.5 ** (
                dt_weeks / max(self._external_half_life_weeks, 1e-9)
            )
        else:
            ext = 0.0
        # 内部关注：上一 tick（本 tick 已结束）梗类互动增量 × 弹性回灌，整体按半衰期衰减
        decay = 0.5 ** (1.0 / max(self._internal_decay_half_life_weeks, 1e-9))
        internal = (
            self._s_internal * decay
            + self._meme_engagement_this_tick * self._internal_elasticity
        )
        self._s_external = ext
        self._s_internal = internal
        self._s_total = min(
            100.0, self._salience_floor + ext + internal
        )

    def _synthesize_ambient_likes(self) -> None:
        """按本 tick 实质动作日志合成被动点赞，计入帖子 likes_count 与 action 行。"""
        for row in self._pending_action_rows:
            target_id = row.get("target_post_id")
            if target_id is None or target_id not in self._posts:
                continue
            agent_id = int(row["agent_id"])
            lam = self._ambient_lambda(agent_id)
            n = self._poisson_sample(self._rng, lam)
            if n > 0:
                self._posts[target_id]["likes_count"] += n
                row["ambient_likes_synthesized"] = float(n)

    def _aggregate_engagement_by_category(self) -> Dict[str, Dict[str, int]]:
        """聚合本 tick 互动增量（like/comment/repost）按目标帖类群分布。"""
        agg: Dict[str, Dict[str, int]] = {}
        for row in self._tick_action_log:
            action = row["action"]
            if action not in ("like", "comment", "repost"):
                continue
            target_id = row.get("target_post_id")
            if target_id is None or target_id not in self._posts:
                continue
            cat = self._category_of(self._posts[target_id])
            entry = agg.setdefault(
                cat, {"likes": 0, "comments": 0, "reposts": 0, "total": 0}
            )
            entry[action if action in entry else "total"] += 1
            entry["total"] += 1
        return agg

    async def close(self):
        """关闭环境：刷写剩余 replay 行。"""
        await self._flush_replay()
        get_logger().info("CurationDynamicsSpace closed")

    # ------------------------------------------------------------------
    # @tool 只读工具
    # ------------------------------------------------------------------

    @tool(readonly=True)
    async def refresh_feed(self, user_id: int) -> dict:
        """**刷新信息流 refresh_feed(user_id)**：返回当前可见的全站 feed。

        只读观察工具，不会修改任何状态。

        - **user_id** (int): 当前 agent 的 id（用于日志标注，不改变推荐结果）。
        - 候选集 = 所有 ``created_at <= 当前仿真时间`` 的帖子（时间门控），
          按构造时配置的推荐算法（reddit_hot 热度加权 或 chronological 时间倒序）
          排序，取前 feed_limit 条。
        - 返回的 response 文本**开头**为「全站热搜」行：事件热度 S(t) 取整百分位
          （0–100）+ 当前互动（赞+评+转）最高的前 3 帖标题。
        - 返回的 ``posts`` 字段为结构化帖子列表（含各计数），供下游分析使用。

        请在每个 step 先调用本工具了解当前信息流与事件热度，再决定互动。
        """
        self._feed_refresh_count_this_step += 1
        candidates = self._get_candidate_posts()
        feed = self._sort_feed(candidates, self._feed_limit)

        # 全站热搜行：事件热度 + 当前互动最高的前 3 帖
        hot_posts = sorted(candidates, key=self._engagement, reverse=True)[:3]
        salience_pct = int(round(self._s_total))
        hot_lines = [f"【全站热搜】事件热度 {salience_pct}/100"]
        for rank, p in enumerate(hot_posts, start=1):
            title = str(p.get("content", ""))[:30].replace("\n", " ")
            hot_lines.append(
                f"{rank}. [{self._category_of(p)}] post_id={p['post_id']} {title}"
            )

        feed_lines = [f"【信息流】共 {len(feed)} 条（算法={self._recommendation_algorithm}）"]
        for p in feed:
            feed_lines.append(
                f"- [post_id={p['post_id']}] [{self._category_of(p)}] "
                f"{self._person_name(p['author_id'])}: "
                f"{str(p.get('content',''))[:60]}"
                f"(赞{p['likes_count']}/评{p['comments_count']}/转{p['reposts_count']})"
            )

        response_text = "\n".join(hot_lines) + "\n" + "\n".join(feed_lines)
        return {
            "status": "success",
            "response": response_text,
            "user_id": user_id,
            "hot_search": [
                {
                    "rank": i,
                    "post_id": p["post_id"],
                    "title": str(p.get("content", ""))[:80],
                    "category": self._category_of(p),
                    "engagement": self._engagement(p),
                }
                for i, p in enumerate(hot_posts, start=1)
            ],
            "salience": round(self._s_total, 4),
            "salience_percent": salience_pct,
            "algorithm": self._recommendation_algorithm,
            "posts": [dict(p) for p in feed],
            "count": len(feed),
        }

    @tool(readonly=True)
    async def view_post(self, view_target_post_id: int) -> dict:
        """**查看帖文详情 view_post(view_target_post_id)**：返回指定帖子的完整内容。

        只读观察工具，不修改任何状态（不增加浏览计数）。

        - **view_target_post_id** (int): 要查看的帖子 id。
        - 返回该帖的 content、作者、类群、各互动计数与时间，供决定是否互动。

        若帖子不存在，返回失败原因。
        """
        if view_target_post_id not in self._posts:
            return {
                "status": "fail",
                "reason": f"帖子 post_id={view_target_post_id} 不存在",
            }
        p = self._posts[view_target_post_id]
        return {
            "status": "success",
            "response": (
                f"[post_id={p['post_id']}] [{self._category_of(p)}] "
                f"{self._person_name(p['author_id'])}: {p['content']}"
            ),
            "post": dict(p),
        }

    # ------------------------------------------------------------------
    # @tool 写工具
    # ------------------------------------------------------------------

    @tool(readonly=False)
    async def create_post(
        self, author_id: int, content: str, tags: List[str] | None = None
    ) -> dict:
        """**发布新帖 create_post(author_id, content, tags)**：创建一条原创帖。

        - **author_id** (int): 当前 agent 的 id（必须为本环境注册的类群代表）。
        - **content** (str): 帖文正文。
        - **tags** (list[str], optional): 话题标签，建议 [[类群], [平台]] 形式，
          如 ["梗文化讨论", "微博"]；用于确定帖子的类群分类。
        - 新帖 ``created_at`` 为当前仿真时间，立即进入（时间门控下的）信息流候选集。
        - 同一 agent 在同一 step 内发布完全相同的正文会被去重为 noop（幂等）。
        - 返回新帖 id 与状态。

        发布后本 tick 会为该帖按类群规模权重合成被动点赞当量。
        """
        if tags is None:
            tags = []
        tags = [str(t) for t in tags]
        async with self._lock:
            if author_id not in self._persons:
                return {
                    "status": "fail",
                    "reason": f"agent_id={author_id} 不是本环境的注册类群代表",
                }
            dedup_key = (int(author_id), str(content), self._step_counter)
            if dedup_key in self._create_seen_keys:
                return {
                    "status": "success",
                    "response": f"noop（agent {author_id} 本 step 已发布过相同内容）",
                }
            self._create_seen_keys.add(dedup_key)

            post_id = self._next_post_id
            self._next_post_id += 1
            post = {
                "post_id": post_id,
                "author_id": int(author_id),
                "content": str(content),
                "post_type": "original",
                "parent_id": None,
                "created_at": self.t,
                "likes_count": 0,
                "reposts_count": 0,
                "comments_count": 0,
                "view_count": 0,
                "tags": tags,
                "topic_category": tags[0] if tags else None,
            }
            self._posts[post_id] = post
            category = self._category_of(post)
            self._posts_created_this_step[category] = (
                self._posts_created_this_step.get(category, 0) + 1
            )
            self._record_action(
                int(author_id), "post", post_id, category
            )
            self._queue_post_replay_row(post)
            get_logger().info(
                "Agent %d created post %d (category=%s)",
                author_id,
                post_id,
                category,
            )
            return {
                "status": "success",
                "response": (
                    f"已发布新帖 post_id={post_id}（作者 {self._person_name(author_id)}，"
                    f"类群 {category}）"
                ),
                "post_id": post_id,
                "category": category,
            }

    @tool(readonly=False)
    async def repost(
        self,
        author_id: int,
        repost_target_post_id: int,
        content: str = "",
    ) -> dict:
        """**转发帖子 repost(author_id, repost_target_post_id, content)**：转发并附言。

        - **author_id** (int): 当前 agent 的 id。
        - **repost_target_post_id** (int): 要转发的原帖 id。
        - **content** (str, optional): 转发附言（可为空串，表示纯转发）。
        - 转发会生成一条 post_type="repost" 的新帖（parent_id 指向原帖），
          并使原帖 ``reposts_count + 1``。
        - 同一 agent 对同一原帖在同一 step 内的重复转发会被去重为 noop（幂等）。
        - 若原帖不存在，返回失败原因。

        转发梗类内容会为内部关注 S(t) 贡献互动增量。
        """
        async with self._lock:
            if author_id not in self._persons:
                return {
                    "status": "fail",
                    "reason": f"agent_id={author_id} 不是本环境的注册类群代表",
                }
            if repost_target_post_id not in self._posts:
                return {
                    "status": "fail",
                    "reason": f"目标帖 post_id={repost_target_post_id} 不存在",
                }
            dedup_key = (
                int(author_id),
                int(repost_target_post_id),
                self._step_counter,
            )
            if dedup_key in self._repost_seen_keys:
                return {
                    "status": "success",
                    "response": (
                        f"noop（agent {author_id} 本 step 已转发过 "
                        f"post_id={repost_target_post_id}）"
                    ),
                }
            self._repost_seen_keys.add(dedup_key)

            target = self._posts[repost_target_post_id]
            target["reposts_count"] += 1

            new_post_id = self._next_post_id
            self._next_post_id += 1
            repost_post = {
                "post_id": new_post_id,
                "author_id": int(author_id),
                "content": str(content) if content else f"repost {repost_target_post_id}",
                "post_type": "repost",
                "parent_id": int(repost_target_post_id),
                "created_at": self.t,
                "likes_count": 0,
                "reposts_count": 0,
                "comments_count": 0,
                "view_count": 0,
                "tags": list(target.get("tags") or []),
                "topic_category": target.get("topic_category"),
            }
            self._posts[new_post_id] = repost_post
            category = self._category_of(repost_post)
            self._posts_created_this_step[category] = (
                self._posts_created_this_step.get(category, 0) + 1
            )
            self._record_action(
                int(author_id), "repost", int(repost_target_post_id), category
            )
            if self._is_meme_post(target):
                self._meme_engagement_this_tick += 1
            self._queue_post_replay_row(repost_post)
            get_logger().info(
                "Agent %d reposted post %d as %d",
                author_id,
                repost_target_post_id,
                new_post_id,
            )
            return {
                "status": "success",
                "response": (
                    f"已转发 post_id={repost_target_post_id} 为新帖 post_id={new_post_id}"
                    f"（原帖转发数 {target['reposts_count']}）"
                ),
                "new_post_id": new_post_id,
                "original_post_id": int(repost_target_post_id),
                "category": category,
            }

    @tool(readonly=False)
    async def comment_on_post(
        self,
        author_id: int,
        comment_target_post_id: int,
        content: str,
    ) -> dict:
        """**评论帖子 comment_on_post(author_id, comment_target_post_id, content)**。

        - **author_id** (int): 当前 agent 的 id。
        - **comment_target_post_id** (int): 要评论的原帖 id。
        - **content** (str): 评论文本。
        - 评论使原帖 ``comments_count + 1``。
        - 同一 agent 对同一原帖的完全相同评论在同一 step 内会被去重为 noop（幂等）。
        - 若原帖不存在，返回失败原因。

        评论梗类内容会为内部关注 S(t) 贡献互动增量。
        """
        async with self._lock:
            if author_id not in self._persons:
                return {
                    "status": "fail",
                    "reason": f"agent_id={author_id} 不是本环境的注册类群代表",
                }
            if comment_target_post_id not in self._posts:
                return {
                    "status": "fail",
                    "reason": f"目标帖 post_id={comment_target_post_id} 不存在",
                }
            dedup_key = (
                int(author_id),
                int(comment_target_post_id),
                str(content),
                self._step_counter,
            )
            if dedup_key in self._comment_seen_keys:
                return {
                    "status": "success",
                    "response": (
                        f"noop（agent {author_id} 本 step 已对 post_id="
                        f"{comment_target_post_id} 发过相同评论）"
                    ),
                }
            self._comment_seen_keys.add(dedup_key)

            target = self._posts[comment_target_post_id]
            target["comments_count"] += 1
            category = self._category_of(target)
            self._record_action(
                int(author_id),
                "comment",
                int(comment_target_post_id),
                category,
            )
            if self._is_meme_post(target):
                self._meme_engagement_this_tick += 1
            get_logger().info(
                "Agent %d commented on post %d",
                author_id,
                comment_target_post_id,
            )
            return {
                "status": "success",
                "response": (
                    f"已评论 post_id={comment_target_post_id}（评论数 "
                    f"{target['comments_count']}）"
                ),
                "post_id": int(comment_target_post_id),
                "total_comments": int(target["comments_count"]),
            }

    @tool(readonly=False)
    async def like_post(self, author_id: int, like_target_post_id: int) -> dict:
        """**点赞帖子 like_post(author_id, like_target_post_id)**。

        - **author_id** (int): 当前 agent 的 id。
        - **like_target_post_id** (int): 要点赞的帖子 id。
        - 点赞使帖子 ``likes_count + 1``。
        - 幂等：同一 agent 对同一帖子的点赞只生效一次（持久 (author, post) 已赞集合），
          重复点赞返回 noop success。
        - 若帖子不存在，返回失败原因。

        点赞梗类内容会为内部关注 S(t) 贡献互动增量。
        """
        async with self._lock:
            if author_id not in self._persons:
                return {
                    "status": "fail",
                    "reason": f"agent_id={author_id} 不是本环境的注册类群代表",
                }
            if like_target_post_id not in self._posts:
                return {
                    "status": "fail",
                    "reason": f"目标帖 post_id={like_target_post_id} 不存在",
                }
            pair = (int(author_id), int(like_target_post_id))
            if pair in self._liked_pairs:
                return {
                    "status": "success",
                    "response": (
                        f"noop（agent {author_id} 已点赞过 post_id={like_target_post_id}）"
                    ),
                }
            self._liked_pairs.add(pair)
            target = self._posts[like_target_post_id]
            target["likes_count"] += 1
            category = self._category_of(target)
            self._record_action(
                int(author_id), "like", int(like_target_post_id), category
            )
            if self._is_meme_post(target):
                self._meme_engagement_this_tick += 1
            get_logger().info(
                "Agent %d liked post %d",
                author_id,
                like_target_post_id,
            )
            return {
                "status": "success",
                "response": (
                    f"已点赞 post_id={like_target_post_id}（点赞数 "
                    f"{target['likes_count']}）"
                ),
                "post_id": int(like_target_post_id),
                "total_likes": int(target["likes_count"]),
            }


__all__ = ["CurationDynamicsSpace"]
