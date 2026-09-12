"""CurationDiscourseAgent: 算法策展舆论场模拟的话语参与者 Agent。

每 tick 固定管线（LLM 调用预算受控，0-1 次/agent-tick）：
1. **get_feed**（readonly, template_mode）——取回本周 feed 快照（feed 列表、意见气候、
   玩梗涌现环境、全局供给/曝光份额、个人累计曝光）。
2. **数字化发言决策**（无 LLM，用户 2026-09-12 裁定：**双规则表达效用模型**）
   ——U = D·R，发言当且仅当 U ≥ activity（activity = 个体表达门槛，门槛低的 agent
   更容易发言；确定性决策，无随机数，给定状态与参数行为唯一）。两条规则乘法进入
   收益侧：沉默螺旋 D（同类气候共振/少数派抑制）与注意力衰减 R（重复曝光疲劳折减）。
   环境观测量（B/S/G）仍随快照取回并写入 decision_log，但不参与决策。
   决策分量（份额/因子/环境/效用/门槛）全量写入 decision_log，可完整审计与事后重算。
3. 若发言，一次内容生成 completion——提示词包含本周 feed 前 feed_context_n 条帖子的
   作者与正文摘录，要求**基于所见内容**回应/讨论/二创/跟帖式发言（用户 2026-09-10 裁定），
   按 Agent 固定类型生成中文帖子（≤300 字），并自然融入本类型词表词（type_vocab）。
4. **create_post**（幂等, template_mode）——发布，帖类型 = 作者类型（by construction）。

类型全程固定（实验设计 二.2）：LLM 只负责"说什么"，"是否说"由数值算法决定。
"""

from __future__ import annotations

import importlib.util
import json
import logging
import math
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

from agentsociety2.agent.base import AgentBase

logger = logging.getLogger(__name__)

# ---------------- 共享机制纯函数（与 env / calibrate_speak.py 同源） ----------------
# 沉默螺旋因子 D 的实现放 custom/envs/curation_mechanisms.py，三处（agent / env / 校准脚本）
# import 同一份，避免"校准-仿真不同构"。本模块按路径加载，与 env 模块同一模式。
_MECH_PATH = Path(__file__).resolve().parents[1] / "envs" / "curation_mechanisms.py"
_mech_spec = importlib.util.spec_from_file_location("curation_mechanisms", _MECH_PATH)
if _mech_spec is None or _mech_spec.loader is None:  # pragma: no cover
    raise ImportError(f"无法加载共享机制模块: {_MECH_PATH}")
mech = importlib.util.module_from_spec(_mech_spec)
_mech_spec.loader.exec_module(mech)

VALID_TYPES = ("meme", "mourning", "marketing", "education", "other")

# ---------------- 发言决策：双规则表达效用模型（用户 2026-09-12 裁定） ----------------
# U = D·R，发言当且仅当 U ≥ activity（activity = 个体表达门槛，越低越容易发言）。
#   D = 1 + s·tanh(k·(share_own − base)/base)           沉默的螺旋：同类气候共振放大收益、
#       少数派处境抑制收益（负值段即"孤立成本"）——有界 tanh，无地板（2026-09-12 裁定，
#       实现见共享模块 curation_mechanisms.spiral_factor）。
#       文献依据：Noelle-Neumann 1974（恐惧孤立）；Blanco 2005 博弈式给出"发言门槛
#       = 孤立成本/(收益+成本)"，与本模型 U ≥ activity 的门槛结构同构；Sohn & Geidner 2015
#       / Cabrera et al. 2021 用 logistic 有界映射把意见气候 δ 转成表达意愿；
#       Granovetter 1978 阈值分布对应 activity 的 U[0.8,1.2] 个体抖动。
#   R = exp(−λ·cum_own/20)                              注意力衰减：重复曝光疲劳折减收益
#       （Wu & Huberman 2007；Candia et al. 2019 两段式衰减）。半饱和尺度 20 ≈ 两周
#       活跃曝光；2026-09-12 用户裁定由 50 调至 20（依据见 SMOKE_DIAGNOSIS §五之五：
#       真实总量深 V 而模拟近平 → 退潮未显现；且趋势变陡后锯齿相对不显眼、效标拟合改善 3 倍）。
#
# 2026-09-12 用户裁定：原第三因子 **玩梗涌现环境增益 G = clamp(B^β·S^σ, 0.2, 3.0)** 退役
# （原 U = D·R·G^θ，仅玩梗型 θ>0）。依据（见 hypothesis_4/experiment_1/
# SMOKE_DIAGNOSIS_w19_cliff.md §五之二/§五之三）：① G 的两处标定常数（K_a=52 与基准周）
# 与它要比较的内生存量（约 450–510）量纲不匹配 → 丰沛度 B 从 W13 起饱和为常数 ≈3.6，
# "存量越丰沛越易诞生 meme" 在数值上未工作；② G 只对玩梗型生效，等价于把该类型的有效
# 门槛打个 3 折（W18-19 有效门槛 0.32 vs 其他类型 0.95），且随周漂移 6 倍，与"类型间不设
# 门槛差异"的裁定冲突；③ no-G 反事实探针实测：去掉 G 后玩梗第二波主体不受影响
# （W20-22：38 vs 47 帖 = 0.81），G 的作用集中在 W17–W19 的早期零星参与。
# B/S/G 仍在 env 侧逐周计算并写入 replay（作为描述性时间轴与审计线索），但**不进入任何
# 类型的决策**；`sustained_hot`（冻结 S）因此不再产生行为差异，配置统一为 normal。
#
# 确定性决策（无随机数）：给定环境快照与参数，行为完全确定，跨 cell/seed 可比性最强。
# 门槛基数 activity_base 为校准值（calibrate_speak.py 扫描定标），中性状态（D≈R≈1）
# 下 U≈1.0。类型均值与 curation_personas._PARAM_SPECS 一致；profile 未带 params 时的回退值。

_PARAM_DEFAULTS: dict[str, dict[str, float]] = {
    "meme":      {"activity": 0.95, "spiral": 1.2, "decay": 0.8},
    "mourning":  {"activity": 0.95, "spiral": 0.8, "decay": 1.2},
    "marketing": {"activity": 0.95, "spiral": 0.2, "decay": 0.05},
    "education": {"activity": 0.95, "spiral": 0.5, "decay": 0.4},
    "other":     {"activity": 0.95, "spiral": 1.5, "decay": 1.0},
}
# 沉默螺旋的期望份额基线。用户 2026-09-10 裁定：群体按发帖人口径比例
# 玩梗18/悼念21/营销26/教育15/其他20（不再按内容划分口径）。
_POP_SHARE = {"meme": 0.18, "mourning": 0.21, "marketing": 0.26, "education": 0.15, "other": 0.20}

# 各类型内容生成指引（人设之外的具体写作约束）
_CONTENT_GUIDE: dict[str, str] = {
    "meme": (
        "写一条玩梗/抽象风格的帖子：用谐音、变体称呼、emoji、反讽或圈内梗表达，"
        "短小轻快，不解释梗。"
    ),
    "mourning": (
        "写一条悼念/缅怀风格的帖子：真诚追思、表达哀悼或由其离世引发的生命/健康感慨，"
        "语气克制严肃，可用 🕯️ 等符号。"
    ),
    "marketing": (
        "写一条借势营销帖子：借当前讨论热点引流你的课程/资料/咨询/服务，"
        "含明确行动号召（链接/私信/领取/限时等），话术圆滑。"
    ),
    "education": (
        "写一条教育观点讨论帖子：围绕专业选择、升学规划、就业、教育公平或相关人物的教育观点"
        "展开理性讨论，有自己的明确立场，不做商业推广。"
    ),
    "other": (
        "写一条普通路人讨论帖：转述事件、表达一般性看法或闲聊式感慨，"
        "不属于玩梗/悼念/营销/教育讨论中的任何一类，口吻日常。"
    ),
}


class CurationDiscourseAgent(AgentBase):
    """算法策展舆论场中的固定类型话语参与者（玩梗/悼念/营销/教育/其他）。"""

    # ------------------------------------------------------------------
    # Registry descriptions
    # ------------------------------------------------------------------
    @classmethod
    def description(cls) -> str:
        return (
            "CurationDiscourseAgent: 固定内容类型的社媒发言者。"
            "每 tick 先读推荐 feed，再按双规则表达效用模型（沉默螺旋 × 注意力衰减，"
            "两者乘法进入收益侧）数值决策是否公开发言；"
            "发言内容严格限于自身类型并融入类型词表词。"
        )

    @classmethod
    def init_description(cls) -> str:
        return """CurationDiscourseAgent: 固定内容类型的社媒发言者。

通过 ``CurationDiscourseAgent.create(workspace_path, profile, config)`` 创建。

**Profile fields:**
- id (int): 唯一 agent id。
- name (str): 显示名（中文网名）。
- agent_type (str): 固定类型，取值 meme/mourning/marketing/education/other。
- persona (str): 完整人设文本（类型模板 + 个体人口学特征），内容生成风格依据。
- params (dict): 发言决策数值参数 {activity, spiral, decay}（可选，
  缺失回退类型均值）。activity = 表达门槛（越低越容易发言）；
  （旧版第四个参数 emergence/θ 已于 2026-09-12 退役，缺省即忽略）。
- type_vocab (list[str]): 本类型词表个人常用词库（可选），发言须自然融入 1-3 词。

**Config fields（均可选）:**
- max_content_chars (int, 默认 300): 单帖最大字符数。
- feed_context_n (int, 默认 5): 内容生成提示词中包含的本周 feed 帖子条数
  （发言须基于所见帖子：回应/讨论/二创/跟帖）。

**Example config:**
```json
{"id": 1, "profile": {"name": "抽象老雪", "agent_type": "meme", "persona": "...",
  "params": {"activity": 0.5, "spiral": 1.2, "decay": 0.8},
  "type_vocab": ["抽象", "乐子"]}, "config": {"feed_context_n": 5}}
```
"""

    # ------------------------------------------------------------------
    # Workspace contract（Template 1：自管 AGENT.json，不用 skill runtime）
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, workspace_path: Path, profile: dict, config: dict) -> None:
        workspace_path = Path(workspace_path)
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "config.json").write_text(
            json.dumps(config or {}, ensure_ascii=False, indent=2), encoding="utf-8")
        agent_id = int(profile.get("id", 0))
        name = str(profile.get("name") or f"Agent_{agent_id}")
        (workspace_path / "AGENT.json").write_text(
            json.dumps(
                {"id": agent_id, "name": name, "profile": profile,
                 "step_count": 0, "decision_log": []},
                ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    async def from_workspace(cls, workspace_path: Path, service_proxy: Any) -> "CurationDiscourseAgent":
        agent = cls()
        await agent.restore(workspace_path, service_proxy)
        return agent

    async def restore(self, workspace_path: Path, service_proxy: Any) -> None:
        workspace_path = Path(workspace_path)
        cfg: dict = {}
        cfg_path = workspace_path / "config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        meta = json.loads((workspace_path / "AGENT.json").read_text(encoding="utf-8"))
        self._id = int(meta.get("agent_id", meta.get("id", 0)))
        self._profile = meta.get("profile", {"name": meta.get("name")})
        self._name = meta.get("name") or f"Agent_{self._id}"
        self._config = dict(cfg or {})
        self._bind_services(service_proxy)
        self._step_count = int(meta.get("step_count", 0))
        self._decision_log: list[dict] = list(meta.get("decision_log", []))
        # 业务状态
        self._agent_type = str(self.get_profile().get("agent_type", "other"))
        if self._agent_type not in VALID_TYPES:
            raise ValueError(f"非法 agent_type: {self._agent_type}")
        self._persona = str(self.get_profile().get("persona", ""))
        # 类型词表（配置期从 vocabs.json 按类型抽样注入 profile；用户裁定：
        # 发言须用本类型词表中的词组织语言，同时让 env 判类标签与作者类型对齐）。
        self._type_vocab: list[str] = [str(w) for w in (self.get_profile().get("type_vocab") or [])]
        # 发言决策数值参数（profile.params 优先，缺失回退类型均值）。
        raw_params = self.get_profile().get("params") or {}
        defaults = _PARAM_DEFAULTS.get(self._agent_type, {})
        # emergence（θ）已于 2026-09-12 退役：旧 profile 里若仍带该键，此处直接忽略。
        self._params: dict[str, float] = {
            k: float(raw_params.get(k, defaults.get(k, 0.0)))
            for k in ("activity", "spiral", "decay")
        }

    async def to_workspace(self, workspace_path: Path) -> None:
        workspace_path = Path(workspace_path)
        (workspace_path / "AGENT.json").write_text(
            json.dumps(
                {"id": self._id, "name": self._name, "profile": self.get_profile(),
                 "step_count": getattr(self, "_step_count", 0),
                 "decision_log": getattr(self, "_decision_log", [])},
                ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Env 返回解析（防御式：codegen 生成的代码自行命名 results 键）
    # ------------------------------------------------------------------
    @staticmethod
    def _find_feed_dict(node: Any) -> dict | None:
        """在 ask_env 返回的 results 里查找 get_feed 快照（含 feed/meme_env 键的字典）。

        迭代 BFS 实现（浅层优先 + 命中即停），比递归 DFS 少一层函数调用开销且无深递归；
        跳过 variables 子树；对任意嵌套结构保持防御式兼容。"""
        if not isinstance(node, (dict, list)):
            return None
        queue: deque[Any] = deque([node])
        while queue:
            cur = queue.popleft()
            if isinstance(cur, dict):
                if "feed" in cur and "meme_env" in cur:
                    return cur
                for k, v in cur.items():
                    if k != "variables" and isinstance(v, (dict, list)):
                        queue.append(v)
            else:
                queue.extend(v for v in cur if isinstance(v, (dict, list)))
        return None

    # ---------------- 发言决策数值算法（无 LLM） ----------------

    def _speak_stimulus(self, snap: dict) -> tuple[float, dict]:
        """双规则表达效用模型（用户 2026-09-12 裁定：G 退役，只留沉默螺旋与注意力衰减）。

        U = D·R，发言当且仅当 U ≥ activity。

        - D（沉默的螺旋，收益侧共振/抑制因子）: `1 + s·tanh(k·(share_own − base)/base)`
          （共享实现 `curation_mechanisms.spiral_factor`，k=1.5）；base = 本类型在 100 人
          群体中的份额。同类气候强 → 共鸣放大收益；少数派 → 收益被抑制，D<0 时表达存在
          净成本（孤立成本）。有界 [1−s, 1+s]、单调、边际递减，无地板。
        - R（注意力衰减，收益侧折减因子）: `mech.fatigue_factor(λ, cum_own)`
          = exp(−λ·cum_own/20)（本类型累计曝光的半饱和尺度 20 ≈ 两周活跃曝光；
          2026-09-12 用户裁定由 50 调至 20，"让退潮显现"）。重复同类曝光越多，
          边际表达收益越低。

        2026-09-12 用户裁定：原第三因子 G^θ（玩梗涌现环境增益，仅玩梗型 θ>0）退役，
        理由与证据见模块头注释与 SMOKE_DIAGNOSIS_w19_cliff.md。env 快照里的
        meme_env（B/S/G）仍原样写入 `components` 供监测与审计，但**不参与本决策**。

        发言当且仅当 U ≥ activity（activity = 个体表达门槛；门槛低更易发言）。
        中性状态（D≈R≈1）下 U≈1.0。两因子乘法进入效用（收益侧），
        杜绝线性等权平均的补偿性稀释。
        """
        prm = self._params
        own = self._agent_type
        climate = snap.get("feed_type_distribution") or {}
        share_own = float(climate.get(own, 0.0) or 0.0)
        base = _POP_SHARE.get(own, 0.2)
        d = mech.spiral_factor(share_own, base, prm["spiral"])   # 有界 tanh，无地板（2026-09-12）
        cum = (snap.get("personal_stats") or {}).get("cumulative_exposures") or {}
        cum_own = float(cum.get(own, 0) or 0)
        r = mech.fatigue_factor(prm["decay"], cum_own)   # 共享纯函数（尺度 DEFAULT_DECAY_SCALE=20）
        u = d * r
        meme_env = snap.get("meme_env") or {}
        comps = {
            "share_own": round(share_own, 4),
            "share_base": base,
            "spiral": round(d, 4),
            "cum_own": cum_own,
            "decay": round(r, 4),
            "benefit": round(u, 4),   # U = D·R
            # 以下为环境观测量：仅记录（描述性时间轴 + 事后审计），不参与决策。
            "env_observed_only": True,
            "env_abundance": round(float(meme_env.get("abundance", 1.0) or 1.0), 4),
            "env_emptiness": round(float(meme_env.get("emptiness", 1.0) or 1.0), 4),
            "env_gain": round(float(meme_env.get("gain", 1.0) or 1.0), 4),
        }
        return u, comps

    # ------------------------------------------------------------------
    # LLM prompt（仅内容生成；发言必须基于本周看到的帖子——用户 2026-09-10 裁定）
    # ------------------------------------------------------------------
    def _content_messages(self, snap: dict, comps: dict) -> list[dict]:
        max_chars = int(self._config.get("max_content_chars", 300))
        feed_n = int(self._config.get("feed_context_n", 5))
        system = (
            f"你在扮演一个中文社交媒体用户，人设如下：\n\n{self._persona}\n\n"
            f"你的固定内容类型是：{self._agent_type}。{_CONTENT_GUIDE[self._agent_type]}"
        )
        vocab_note = ""
        if self._type_vocab:
            vocab_note = (
                "\n组织语言时，从你的常用词库里自然选用 1-3 个词融入正文"
                "（贴合语境、不要堆砌、不要逐字罗列）："
                + "、".join(self._type_vocab)
            )
        # feed 上下文：取本周 feed 前 feed_context_n 条（官方置顶/算法排序在前），
        # 摘录作者与正文（单条截断 120 字），作为发言对象。
        feed_lines: list[str] = []
        for it in (snap.get("feed") or [])[: max(0, feed_n)]:
            text = str(it.get("content", "")).strip().replace("\n", " ")[:120]
            badge = "【官方】" if it.get("is_official") else ""
            feed_lines.append(
                f"- {badge}@{it.get('author_handle', '?')}（{it.get('week', '?')}）：{text}"
            )
        if feed_lines:
            feed_block = (
                "\n你本周刷到的前几条帖子：\n" + "\n".join(feed_lines) + "\n"
                "你的发言必须建立在你看到的内容之上：可以回应、补充、反驳、二创、"
                "玩其中的梗、或接话跟帖式地引用讨论；若其中某条与你高度相关，优先围绕它展开。"
            )
        else:
            feed_block = "\n本周信息流为空，你可就当前话题自由发言。"
        env = snap.get("meme_env") or {}
        context = (
            f"本周舆论场存量 {env.get('stock', '?')} 帖、新增 {env.get('flow', '?')} 帖，"
            f"你的 feed 里同类内容占比约 {comps['share_own']:.0%}。"
        )
        user = (
            f"现在是 {snap.get('week', '?')}。你决定公开发言。\n{context}\n{feed_block}\n"
            f"请写一条不超过 {max_chars} 字的帖子正文，只输出正文本身，不要解释、不要引号。"
            "可以带 emoji 或话题标签，风格必须符合你的人设与类型。"
            + vocab_note
        )
        return [{"role": "system", "content": system},
                {"role": "user", "content": user}]

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------
    async def ask(self, message: str, readonly: bool = True, *, t: datetime | None = None) -> str:
        try:
            response = await self.acompletion([{"role": "user", "content": message}])
            if response and response.choices:
                return response.choices[0].message.content or ""
            return ""
        except Exception as exc:
            self.logger.error("[%s] ask failed: %s", self.name, exc)
            return f"[error] {exc}"

    async def step(self, tick: int, t: datetime) -> str:
        """一周行为：读 feed → 数值决策 → （若发言）生成并发布一条本类型帖子。"""
        self._step_count += 1
        agent_id = str(self._id)
        record: dict[str, Any] = {"tick": tick, "speak": False, "reason": "",
                                  "week": None, "posted": False}

        # 1) 读 feed（readonly；template_mode 安全——纯查询缓存 codegen）
        snap: dict = {}
        try:
            results, _answer = await self.ask_env(
                {"variables": {"agent_id": agent_id}},
                "Please call get_feed() using agent_id from ctx['variables'] "
                "to get my current weekly feed snapshot.",
                readonly=True,
                template_mode=True,
            )
            snap = self._find_feed_dict(results) or {}
        except Exception as exc:
            self.logger.error("[%s] get_feed failed: %s", self.name, exc)
        if not snap:
            record["reason"] = "feed_unavailable"
            self._decision_log.append(record)
            return f"{self.name}: feed unavailable, silent"

        record["week"] = snap.get("week")

        # 2) 数值决策（无 LLM）：U = D·R，发言当且仅当 U ≥ 门槛 activity
        u, comps = self._speak_stimulus(snap)
        threshold = self._params["activity"]
        speak = u >= threshold
        record.update({
            "u": round(u, 4),
            "threshold": round(threshold, 4),
            "components": comps,
            "speak": speak,
            "reason": f"u={u:.3f} {'>=' if speak else '<'} threshold={threshold:.3f}",
        })
        if not speak:
            self._decision_log.append(record)
            return f"{self.name}: silent (u={u:.3f} < threshold={threshold:.3f})"

        # 3) 内容生成（1 次 LLM 调用）
        content = ""
        try:
            resp = await self.acompletion(self._content_messages(snap, comps))
            content = (resp.choices[0].message.content or "").strip().strip('"“”')
        except Exception as exc:
            self.logger.error("[%s] content generation failed: %s", self.name, exc)
        max_chars = int(self._config.get("max_content_chars", 300))
        content = content[: max_chars + 100]  # 硬截断保护
        if not content:
            record["reason"] = "content_empty"
            self._decision_log.append(record)
            return f"{self.name}: content generation failed, silent"

        # 4) 发布（env 侧幂等：每 tick 每 agent 仅首帖生效；唯一写工具，template_mode 安全）
        try:
            await self.ask_env(
                {"variables": {"agent_id": agent_id, "content": content}},
                "Please call create_post() using agent_id and content "
                "from ctx['variables'] to publish my post.",
                readonly=False,
                template_mode=True,
            )
            record["posted"] = True
            record["content_preview"] = content[:80]
        except Exception as exc:
            self.logger.error("[%s] create_post failed: %s", self.name, exc)
            record["reason"] += " | post_failed"

        self._decision_log.append(record)
        return f"{self.name}: posted" if record["posted"] else f"{self.name}: post failed"
