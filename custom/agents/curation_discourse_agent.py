"""CurationDiscourseAgent: 算法策展舆论场模拟的话语参与者 Agent。

每 tick 固定管线（LLM 调用预算受控，~2-3 次/agent-tick）：
1. **get_feed**（readonly, template_mode）——取回本周 feed 快照（feed 列表、意见气候、
   悼念规范压力、全局供给/曝光份额、个人累计曝光）。
2. 一次决策 completion——人设 + 三机制（沉默的螺旋 / 注意力衰减 / 悼念规范压力）
   对快照做判断是否公开发言，输出 JSON {"speak": bool, "reason": str}。
3. 若发言，一次内容生成 completion——按 Agent 固定类型生成中文帖子（≤300 字）。
4. **create_post**（幂等, template_mode）——发布，帖类型 = 作者类型（by construction）。

类型全程固定（实验设计 二.2）：LLM 只决定"是否说"与"说什么"，不得改变内容类型。
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from agentsociety2.agent.base import AgentBase

logger = logging.getLogger(__name__)

VALID_TYPES = ("meme", "mourning", "marketing", "education", "other")

# 各类型内容生成指引（人设之外的具体写作约束）
_CONTENT_GUIDE: dict[str, str] = {
    "meme": (
        "写一条玩梗/抽象风格的帖子：用谐音、变体称呼、emoji、反讽或圈内梗表达，"
        "短小轻快，不解释梗。不得对逝者家属进行人身攻击或恶意诅咒。"
    ),
    "mourning": (
        "写一条悼念/缅怀风格的帖子：真诚追思、表达哀悼或由其离世引发的生命/健康感慨，"
        "语气克制严肃，可用 🕯️ 等符号。"
    ),
    "marketing": (
        "写一条借势营销帖子：借当前讨论热点引流你的课程/资料/咨询/服务，"
        "含明确行动号召（链接/私信/领取/限时等），话术圆滑，初期可带一点表面惋惜。"
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

_DECISION_INSTRUCTION = """\
现在是 {week}。请你以这个人设判断：**本周你要不要公开发帖？**

## 你本周感知到的信息环境
- 悼念规范压力指数 P_t = {pressure:.2f}（等级：{pressure_level}；越高表示严肃悼念规范越强、轻松化表达的社会成本越高）
- 你 feed 里的意见气候（各类型占比）：{climate}
- 全局供给份额（最近完结周，Agent 产出口径）：{supply}
- 全局曝光份额：{exposure}
- 你本周是否已发言：{own_spoke}
- 你的累计曝光（你 historically 看过的各类型帖子数量，越多越容易疲劳）：{cumulative}
- 你 feed 中的部分帖子：
{feed_highlights}

## 决策规则（沉默的螺旋 / 注意力衰减 / 规范压力）
1. 沉默的螺旋：若意见气候与你自身类型相异、你处于少数位置，你的公开发言意愿应降低；若同类表达增多，意愿上升。沉默不改变你的类型。
2. 注意力衰减：某类内容你的累计曝光越多、内容越重复，你越不想参与相关讨论（按你人设的衰减特征执行）。
3. 悼念规范压力：P_t 越高，与你类型不相容的表达（尤其轻松/娱乐/营销化）的社会成本越高；压力下降会释放表达空间。

结合你的人设与上述环境，只输出一行 JSON（不要输出任何其他内容）：
{{"speak": true 或 false, "reason": "不超过 40 字的理由"}}"""


class CurationDiscourseAgent(AgentBase):
    """算法策展舆论场中的固定类型话语参与者（玩梗/悼念/营销/教育/其他）。"""

    # ------------------------------------------------------------------
    # Registry descriptions
    # ------------------------------------------------------------------
    @classmethod
    def description(cls) -> str:
        return (
            "CurationDiscourseAgent: 固定内容类型的社媒发言者。"
            "每 tick 先读推荐 feed，再基于沉默螺旋/注意力衰减/悼念规范压力三机制"
            "决定是否公开发言；发言内容严格限于自身类型。"
        )

    @classmethod
    def init_description(cls) -> str:
        return """CurationDiscourseAgent: 固定内容类型的社媒发言者。

通过 ``CurationDiscourseAgent.create(workspace_path, profile, config)`` 创建。

**Profile fields:**
- id (int): 唯一 agent id。
- name (str): 显示名（中文网名）。
- agent_type (str): 固定类型，取值 meme/mourning/marketing/education/other。
- persona (str): 完整人设文本（类型模板 + 个体人口学特征），决策与内容生成的核心依据。

**Config fields（均可选）:**
- max_content_chars (int, 默认 300): 单帖最大字符数。
- feed_highlight_n (int, 默认 6): 决策 prompt 中展示的 feed 帖条数。

**Example config:**
```json
{"id": 1, "profile": {"name": "抽象老雪", "agent_type": "meme", "persona": "..."}, "config": {}}
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

    @staticmethod
    def _parse_decision(text: str) -> tuple[bool, str]:
        """从 LLM 输出解析 {"speak": bool, "reason": str}；失败返回 (False, 'parse_error')。"""
        try:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if not m:
                return False, "parse_error"
            data = json.loads(m.group(0))
            return bool(data.get("speak")), str(data.get("reason", ""))[:80]
        except Exception:
            return False, "parse_error"

    # ------------------------------------------------------------------
    # LLM prompts
    # ------------------------------------------------------------------
    def _decision_messages(self, snap: dict) -> list[dict]:
        cfg = self._config
        n = int(cfg.get("feed_highlight_n", 6))
        feed = snap.get("feed") or []
        highlights = "\n".join(
            f"  - [{p.get('type', '?')}] {str(p.get('content', ''))[:80]}"
            for p in feed[:n]
        ) or "  - （本周 feed 为空）"
        fmt = {
            "week": snap.get("week", "?"),
            "pressure": float(snap.get("norm_pressure", 0.0)),
            "pressure_level": snap.get("norm_pressure_level", "low"),
            "climate": json.dumps(snap.get("feed_type_distribution", {}), ensure_ascii=False),
            "supply": json.dumps(snap.get("global_supply_shares", {}), ensure_ascii=False),
            "exposure": json.dumps(snap.get("global_exposure_shares", {}), ensure_ascii=False),
            "own_spoke": "是" if snap.get("own_spoke") else "否",
            "cumulative": json.dumps(
                (snap.get("personal_stats") or {}).get("cumulative_exposures", {}),
                ensure_ascii=False),
            "feed_highlights": highlights,
        }
        system = (
            f"你在扮演一个中文社交媒体用户，人设如下：\n\n{self._persona}\n\n"
            f"你的固定内容类型是：{self._agent_type}"
            "（meme=玩梗 / mourning=悼念 / marketing=借势营销 / education=教育观点 / other=其他）。"
            "你只产出该类型的内容，任何情况下不改变类型。"
        )
        return [{"role": "system", "content": system},
                {"role": "user", "content": _DECISION_INSTRUCTION.format(**fmt)}]

    def _content_messages(self, snap: dict, reason: str) -> list[dict]:
        max_chars = int(self._config.get("max_content_chars", 300))
        system = (
            f"你在扮演一个中文社交媒体用户，人设如下：\n\n{self._persona}\n\n"
            f"你的固定内容类型是：{self._agent_type}。{_CONTENT_GUIDE[self._agent_type]}"
        )
        user = (
            f"现在是 {snap.get('week', '?')}。你决定公开发言（动机：{reason}）。\n"
            f"请写一条不超过 {max_chars} 字的帖子正文，只输出正文本身，不要解释、不要引号。"
            "可以带 emoji 或话题标签，风格必须符合你的人设与类型。"
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
        """一周行为：读 feed → 三机制决策 → （可选）生成并发布一条本类型帖子。"""
        self._step_count += 1
        agent_id = str(self._id)
        record: dict[str, Any] = {"tick": tick, "speak": False, "reason": "",
                                  "week": None, "pressure": None, "posted": False}

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
        record["pressure"] = snap.get("norm_pressure")

        # 2) 决策（1 次 LLM 调用）
        try:
            resp = await self.acompletion(self._decision_messages(snap))
            text = resp.choices[0].message.content or ""
        except Exception as exc:
            self.logger.error("[%s] decision failed: %s", self.name, exc)
            text = ""
        speak, reason = self._parse_decision(text)
        record["speak"], record["reason"] = speak, reason
        if not speak:
            self._decision_log.append(record)
            return f"{self.name}: silent ({reason})"

        # 3) 内容生成（1 次 LLM 调用）
        content = ""
        try:
            resp = await self.acompletion(self._content_messages(snap, reason))
            content = (resp.choices[0].message.content or "").strip().strip('"“”')
        except Exception as exc:
            self.logger.error("[%s] content generation failed: %s", self.name, exc)
        max_chars = int(self._config.get("max_content_chars", 300))
        content = content[: max_chars + 100]  # 硬截断保护
        if len(content) < 5:
            record["reason"] = reason + " | content_empty"
            self._decision_log.append(record)
            return f"{self.name}: content generation empty, silent"

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
            record["reason"] = reason + " | post_failed"

        self._decision_log.append(record)
        return f"{self.name}: posted ({reason})" if record["posted"] else f"{self.name}: post failed"
