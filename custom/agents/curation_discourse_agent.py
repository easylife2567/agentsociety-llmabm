"""CurationDiscourseAgent: 算法策展舆论场模拟的话语参与者 Agent。

每 tick 固定管线（LLM 调用预算受控，0-1 次/agent-tick）：
1. **get_feed**（readonly, template_mode）——取回本周 feed 快照（feed 列表、意见气候、
   悼念规范压力、全局供给/曝光份额、个人累计曝光）。
2. **数字化发言决策**（无 LLM，用户 2026-09-09 裁定）——按参数合成
   p = activity × spiral × decay × pressure（三机制显式建模），
   发言当且仅当 u < p，u = Random(f"{id}:{tick}").random()（公共随机数：同一 (id, tick)
   在所有 cell/seed 取同一 u，处理组间可比；组间差异完全来自环境快照参数）。
   决策分量（份额/因子/概率/随机数）全量写入 decision_log，可完整审计与事后重算。
3. 若发言，一次内容生成 completion——按 Agent 固定类型生成中文帖子（≤300 字），
   并要求自然融入本类型词表词（type_vocab）。
4. **create_post**（幂等, template_mode）——发布，帖类型 = 作者类型（by construction）。

类型全程固定（实验设计 二.2）：LLM 只负责"说什么"，"是否说"由数值算法决定。
"""

from __future__ import annotations

import json
import logging
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from agentsociety2.agent.base import AgentBase

logger = logging.getLogger(__name__)

VALID_TYPES = ("meme", "mourning", "marketing", "education", "other")

# ---------------- 发言决策数值算法（用户 2026-09-09 裁定：发言行为数字化） ----------------
# p = activity × spiral × decay × pressure，clamp[0, _P_MAX]；发言当且仅当 u < p，
# u = Random(f"{agent_id}:{tick}").random()（公共随机数，见模块 docstring）。
# 类型均值与 curation_personas._PARAM_SPECS 一致；profile 未带 params 时的回退值。

_PARAM_DEFAULTS: dict[str, dict[str, float]] = {
    "meme":      {"activity": 0.50, "spiral": 1.2, "decay": 0.8, "pressure": 0.9},
    "mourning":  {"activity": 0.55, "spiral": 0.8, "decay": 1.2, "pressure": -0.3},
    "marketing": {"activity": 0.90, "spiral": 0.2, "decay": 0.1, "pressure": 0.5},
    "education": {"activity": 0.55, "spiral": 0.5, "decay": 0.4, "pressure": 0.15},
    "other":     {"activity": 0.25, "spiral": 1.5, "decay": 1.0, "pressure": 0.6},
}
_POP_SHARE = {"meme": 0.41, "mourning": 0.21, "marketing": 0.13, "education": 0.13, "other": 0.12}
_DECAY_SCALE = 50.0          # 注意力衰减半饱和尺度（本类型累计曝光，exp 半饱和）
_PRESSURE_FACTOR_CAP = 1.5   # 压力因子上限（mourning 同向增益封顶）
_P_MAX = 0.98                # 发言概率上限

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
            "每 tick 先读推荐 feed，再按数值算法（沉默螺旋/注意力衰减/规范压力三机制参数合成）"
            "决定是否公开发言；发言内容严格限于自身类型并融入类型词表词。"
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
- params (dict): 发言决策数值参数 {activity, spiral, decay, pressure}（可选，
  缺失回退类型均值）。
- type_vocab (list[str]): 本类型词表个人常用词库（可选），发言须自然融入 1-3 词。

**Config fields（均可选）:**
- max_content_chars (int, 默认 300): 单帖最大字符数。

**Example config:**
```json
{"id": 1, "profile": {"name": "抽象老雪", "agent_type": "meme", "persona": "...",
  "params": {"activity": 0.5, "spiral": 1.2, "decay": 0.8, "pressure": 0.9},
  "type_vocab": ["抽象", "乐子"]}, "config": {}}
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
        self._params: dict[str, float] = {
            k: float(raw_params.get(k, defaults.get(k, 0.0)))
            for k in ("activity", "spiral", "decay", "pressure")
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
    def _find_feed_dict(node: Any, depth: int = 0) -> dict | None:
        """在 ask_env 返回的 results 里深度搜索 get_feed 快照（含 feed/norm_pressure 键的字典）。"""
        if depth > 4 or not isinstance(node, (dict, list)):
            return None
        if isinstance(node, dict):
            if "feed" in node and "norm_pressure" in node:
                return node
            for k, v in node.items():
                if k == "variables":
                    continue
                found = CurationDiscourseAgent._find_feed_dict(v, depth + 1)
                if found is not None:
                    return found
        else:
            for v in node:
                found = CurationDiscourseAgent._find_feed_dict(v, depth + 1)
                if found is not None:
                    return found
        return None

    # ---------------- 发言决策数值算法（无 LLM） ----------------

    def _speak_probability(self, snap: dict) -> tuple[float, dict]:
        """p = activity × spiral × decay × pressure，clamp[0, _P_MAX]。

        - spiral（沉默的螺旋）: 1 + s·(share_own − base)/base，clamp[0.05, 2.0]；
          base = 本类型在 100 人群体中的份额。同类气候强 → 增益，处于少数 → 抑制。
        - decay（注意力衰减）: exp(−λ·cum_own/D0)，D0=50（本类型累计曝光的半饱和尺度）。
        - pressure（悼念规范压力）: 1 − s·P_t，clamp[0, 1.5]；mourning 参数为负 →
          与压力同向增益（压力高的时期正是悼念表达最盛的时期）。
        """
        prm = self._params
        own = self._agent_type
        climate = snap.get("feed_type_distribution") or {}
        share_own = float(climate.get(own, 0.0) or 0.0)
        base = _POP_SHARE.get(own, 0.2)
        spiral = 1.0 + prm["spiral"] * (share_own - base) / max(base, 0.05)
        spiral = max(0.05, min(2.0, spiral))
        cum = (snap.get("personal_stats") or {}).get("cumulative_exposures") or {}
        cum_own = float(cum.get(own, 0) or 0)
        decay = math.exp(-prm["decay"] * cum_own / _DECAY_SCALE)
        p_t = float(snap.get("norm_pressure", 0.0) or 0.0)
        pressure = max(0.0, min(_PRESSURE_FACTOR_CAP, 1.0 - prm["pressure"] * p_t))
        p = prm["activity"] * spiral * decay * pressure
        p = max(0.0, min(_P_MAX, p))
        comps = {
            "share_own": round(share_own, 4),
            "share_base": base,
            "spiral": round(spiral, 4),
            "cum_own": cum_own,
            "decay": round(decay, 4),
            "norm_pressure": round(p_t, 4),
            "pressure_factor": round(pressure, 4),
        }
        return p, comps

    # ------------------------------------------------------------------
    # LLM prompt（仅内容生成）
    # ------------------------------------------------------------------
    def _content_messages(self, snap: dict, comps: dict) -> list[dict]:
        max_chars = int(self._config.get("max_content_chars", 300))
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
        context = (
            f"本周悼念规范压力 P_t={comps['norm_pressure']:.2f}，"
            f"你的 feed 里同类内容占比约 {comps['share_own']:.0%}。"
        )
        user = (
            f"现在是 {snap.get('week', '?')}。你决定公开发言。\n{context}\n"
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

        # 2) 数值决策（无 LLM）：p = activity × spiral × decay × pressure，u 公共随机数
        p, comps = self._speak_probability(snap)
        u = random.Random(f"{self._id}:{tick}").random()
        speak = u < p
        record.update({
            "p": round(p, 4),
            "u": round(u, 4),
            "components": comps,
            "speak": speak,
            "reason": f"numeric p={p:.3f} {'>' if speak else '<='} u={u:.3f}",
        })
        if not speak:
            self._decision_log.append(record)
            return f"{self.name}: silent (p={p:.3f}, u={u:.3f})"

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
