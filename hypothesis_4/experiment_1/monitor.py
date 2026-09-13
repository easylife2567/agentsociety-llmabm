#!/usr/bin/env python3
"""curation_monitor: CurationDynamicsSpace 推演的实时状态快照监视器（hypothesis_4/experiment_1）。

**零侵入**：纯读模拟引擎已落盘的文件（不改任何模拟代码、零 LLM 调用），
每次执行即把每个 run 的最新状态刷新为快照文件（无 watch 循环；想看最新就再跑一次）。

数据源（全部由引擎每个 tick 立即落盘）：
- <run>/pid.json                                     进程心跳（~1s：status/pid/step_count/simulation_time）
- <run>/SOCIETY_STEP.json                            每 step 原子重写（current_time/step_count/terminated）
- <run>/replay/curation_dynamics_env_state.*.jsonl   env 周度指标（47 列，每 tick 1 行）
- <run>/replay/curation_dynamics_agent_state.*.jsonl agent 周度状态（21 列，每 tick ~100 行）
- <run>/agents/agent_*/AGENT.json                    agent 元数据 + decision_log（u/门槛/机制分量）
- <run>/env/*/state/ENV_STATE.json                   env 全量动态状态（帖池/feeds/玩梗涌现环境/当前周）

输出（原子写，均落本实验目录 monitor/ 下）：
- monitor/<run_id>/status.md + status.json   单 run 快照（周度指标 / Agent 行为 / 机制透视 /
                                             帖子流 / 派生视图 / 进程信息；每个字段含义内嵌）
- monitor/overview.md + overview.json        多 run 总览

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/monitor.py                 # 刷新全部快照（自动发现 run/ 与 runs/*）
    $PYTHON_PATH hypothesis_4/experiment_1/monitor.py --week 2026-W13 # 只看某周
    $PYTHON_PATH hypothesis_4/experiment_1/monitor.py --run-dir path/to/run [--label 名字]
    $PYTHON_PATH hypothesis_4/experiment_1/monitor.py --overview-only

注意：replay JSONL 为分片追加写，本脚本容忍读取瞬间末尾被截断的半行（跳过）；
pid.json 非原子写，读取失败时进程信息按未知处理，不影响周度数据。
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import time
from datetime import datetime
from pathlib import Path
from statistics import fmean

SCRIPT_DIR = Path(__file__).resolve().parent
BENCH_PATH = SCRIPT_DIR.parent / "benchmark_curves.json"  # hypothesis_4/benchmark_curves.json

# ---------------- 类型标签与顺序 ----------------

TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other"]
TYPE_ALL = TYPE_ORDER + ["noise"]
TYPE_LABEL = {
    "meme": "玩梗", "mourning": "悼念", "education": "教育",
    "marketing": "营销", "other": "其他", "noise": "噪音",
}
# benchmark_curves.json weekly_category_matrix 的中文键 -> 模拟类型
BENCH_KEY_MAP = {
    "梗文化讨论": "meme", "事件悼念讨论": "mourning", "教育观点讨论": "education",
    "借势营销": "marketing", "其他讨论": "other", "爬取噪音": "noise",
}

# ---------------- 字段含义（用户 2026-09-10 要求：每个参数都指明含义） ----------------

FIELDS: dict[str, str] = {
    # 通用
    "week": "ISO 周标签（2026-W12…W22）。模拟 1 tick = 1 真实周，共 11 周。",
    "step": "引擎内部 step 序号（0 起），与 week 一一对应。",
    # 进程/进度
    "status": "run 当前状态（pid.json 心跳）：running=运行中 / completed=完成 / failed=失败。",
    "pid": "引擎进程号（pid.json）。",
    "alive": "进程当前是否存活（kill(pid,0) 探测；completed/failed 后自然为否）。",
    "start_time": "run 启动时间（UTC ISO）。",
    "end_time": "run 结束时间（UTC ISO；completed/failed 时写入）。",
    "simulation_time": "引擎模拟时钟（pid.json 心跳；step 进行中约每秒刷新）。",
    "step_count": "引擎已完成 step 数（SOCIETY_STEP.json；本实验 11 步=11 周）。",
    "completed_step_count": "已完成的前置 step 数（含 Ask/Intervene 等非仿真步；本实验无）。",
    "terminated": "引擎是否已判定终止（SOCIETY_STEP.json）。",
    # env 周度（47 列）
    "meme_env_stock": "舆论场存量 Stock_t = 过去 6 周 arena 供给总数（注入 + agent 帖，内生）。玩梗涌现环境丰沛度 B_t 的输入：总帖子越丰沛越易诞生 meme（用户 2026-09-10 裁定）。",
    "meme_env_flow": "本周 arena 新增供给数（注入 + 上一周并入的 agent 帖）。存量的滚动窗口输入。",
    "meme_env_flow_world": "本周现实口径新增帖量（外生调度 emergence_flow_by_week = 真实数据各周全量帖数）。空旷度 S_t 的输入：当期新增越少越空旷越宜传播。sim arena 流量被注入预算压缩（峰谷比 ~1.6× vs 现实 ~9×），故 S 读现实口径。",
    "meme_env_abundance": "[仅观测·不参与决策] 丰沛度 B_t = f(Stock_t)/f(Stock_base)，f(x)=x/(x+K_a)；基线周（W12）=1。K_a 默认=注入计划事件周窗口存量（17+35=52）。",
    "meme_env_emptiness": "[仅观测·不参与决策] 空旷度 S_t = h(Flow_t)/h(Flow_base)，h(x)=K_f/(K_f+x)；基线周=1。sustained_hot 反事实臂：事件周（W13）记录、之后冻结（B 保持内生）。",
    "meme_env_gain": "[仅观测·不参与决策] 涌现增益 G_t = clamp(B^β·S^σ, 0.2, 3.0)，β=σ=1 起步。2026-09-12 用户裁定：G 与 agent 侧 θ 一并退役（原经玩梗型效用影响决策），本序列仅作描述性时间轴与审计。",
    "total_supply": "本 tick 新增供给总数 = Agent 产出 + 注入帖。",
    "agent_supply": "本 tick Agent 产出帖数（合计）。",
    "injected_count": "本 tick 注入的真实数据帖数（W13 含官方讣告 1 条）。",
    "supply_share_meme": "Agent 产出口径的玩梗帖供给份额（分母=五类 agent 帖，不含噪音）。",
    "supply_share_mourning": "Agent 产出口径的悼念帖供给份额（分母=五类 agent 帖）。",
    "supply_share_education": "Agent 产出口径的教育帖供给份额（分母=五类 agent 帖）。",
    "supply_share_marketing": "Agent 产出口径的营销帖供给份额（分母=五类 agent 帖）。",
    "supply_share_other": "Agent 产出口径的其他帖供给份额（分母=五类 agent 帖）。",
    "supply_share_all_meme": "combined 口径（注入+产出）玩梗供给份额，分母含噪音，与真实基准对齐。",
    "supply_share_all_mourning": "combined 口径（注入+产出）悼念供给份额，分母含噪音。",
    "supply_share_all_education": "combined 口径（注入+产出）教育供给份额，分母含噪音。",
    "supply_share_all_marketing": "combined 口径（注入+产出）营销供给份额，分母含噪音。",
    "supply_share_all_other": "combined 口径（注入+产出）其他供给份额，分母含噪音。",
    "supply_share_all_noise": "combined 口径（注入+产出）噪音供给份额（噪音只来自注入）。",
    "agent_supply_meme": "本 tick 玩梗型 Agent 产出帖数。",
    "agent_supply_mourning": "本 tick 悼念型 Agent 产出帖数。",
    "agent_supply_education": "本 tick 教育型 Agent 产出帖数。",
    "agent_supply_marketing": "本 tick 营销型 Agent 产出帖数。",
    "agent_supply_other": "本 tick 其他型 Agent 产出帖数。",
    "injected_meme": "本 tick 注入的玩梗类帖数。",
    "injected_mourning": "本 tick 注入的悼念类帖数。",
    "injected_education": "本 tick 注入的教育类帖数。",
    "injected_marketing": "本 tick 注入的营销类帖数。",
    "injected_other": "本 tick 注入的其他类帖数。",
    "injected_noise": "本 tick 注入的噪音类帖数。",
    "total_exposures": "本 tick 全部 Agent 的 feed 槽位总数（1 槽=1 次曝光；100 agent×feed_size=10 为上限）。",
    "exposure_share_meme": "玩梗类曝光份额 = 该类曝光槽位 / 总槽位。这是推荐算法的直接产出。",
    "exposure_share_mourning": "悼念类曝光份额（推荐算法的直接产出）。",
    "exposure_share_education": "教育类曝光份额（推荐算法的直接产出）。",
    "exposure_share_marketing": "营销类曝光份额（推荐算法的直接产出）。",
    "exposure_share_other": "其他类曝光份额（推荐算法的直接产出）。",
    "exposure_share_noise": "噪音类曝光份额（推荐算法的直接产出）。",
    "exposure_meme": "本 tick 玩梗类内容占据的曝光槽位数。",
    "exposure_mourning": "本 tick 悼念类曝光槽位数。",
    "exposure_education": "本 tick 教育类曝光槽位数。",
    "exposure_marketing": "本 tick 营销类曝光槽位数。",
    "exposure_other": "本 tick 其他类曝光槽位数。",
    "exposure_noise": "本 tick 噪音类曝光槽位数。",
    "official_posts_count": "本 tick 置顶集合中的官方帖数（仅 W13 讣告=1，其余周=0）。",
    "official_exposure_slots": "官方帖占据的 feed 槽位数。W13 应=100（全员置顶可见），其余周=0。",
    "event_floor_slots": "事件周议程保底槽位数（用户 2026-09-12 裁定）：W13 每条 feed 在置顶之后固定 5 个槽位放全池哀悼倾向分最高的帖（全员相同、三臂一致），其余周=0。平台级规则，非算法差异。",
    # feed 机制审计（用户 2026-09-12 裁定：帖子生命周期 + 曝光饱和 + 兴趣比例抽样）
    "feed_live_pool": "本周未退场、进入候选池的帖数（跨算法臂同源的内容可得性；三臂应相等）。",
    "feed_sample_temp": "interest 臂比例抽样温度（按 exp(score/temp) 无放回抽 feed_size 条；<=0=确定性 top-k 消融档）。",
    "feed_half_life_weeks": "帖子时间生命的半衰期（周）：1.5 周龄生命力折半。",
    "feed_saturation_scale": "曝光饱和尺度：累计曝光达该值时生命力折半（默认 20）。",
    "exposure_slots_age0": "本 tick 曝光槽位中帖龄 0 周（本周新帖）的槽位数——老帖霸屏的直接指标。",
    "exposure_slots_age1": "本 tick 曝光槽位中帖龄 1 周的槽位数。",
    "exposure_slots_age2": "本 tick 曝光槽位中帖龄 2 周的槽位数。",
    "exposure_slots_age3plus": "本 tick 曝光槽位中帖龄 ≥3 周的槽位数；给定 3 周流通窗口（退场线 0.35）下应恒为 0。",
    # agent 周度（21 列聚合）
    "n_agents": "该类型 Agent 人数（群体构成：营销23/悼念22/其他21/玩梗19/教育15，用户 2026-09-13 更正）。",
    "spoke_rate": "该类型本 tick 发言率 = 发言人数 / 类型人数。",
    "mismatch_rate": "该类型本 tick 判类不一致率：env 四词表判类(assigned_type)≠作者类型(pool_type)的帖子占比。仅诊断用，不影响发布。",
    "mean_climate_own": "该类型 agent 所见信息流中本类内容的平均占比（意见气候；沉默螺旋的输入）。",
    "mean_exposure_own": "该类型 agent 本 tick 本类内容的人均曝光数（注意力衰减的输入）。",
    "mean_feed_slots": "该类型 agent 本周信息流平均长度（正常=10）。",
    # 机制透视（锚定式表达效用模型，用户 2026-09-14 裁定）
    "u": "表达效用 U = B_i + R·(D−B_i)。发言当且仅当 U ≥ activity；R→0 时回归常态锚点 B_i，不机械归零。",
    "threshold": "个体表达门槛 activity（= 类型均值 0.95 × U[0.8,1.2] 抖动）。门槛越低越容易发言，活跃 agent 门槛低。",
    "spiral": "沉默的螺旋因子 D = 1 + (alpha_D·s_i)·tanh(1.5·(share_own−base)/base)；alpha_D=0.429695，只缩放敏感度，不改变D=1的中性中心。",
    "spiral_scale": "沉默螺旋全局强度 alpha_D=0.429695（仅用W13-W18标定）。",
    "decay": "注意力衰减因子 R = exp(−λ·cum_own/15)（收益侧折减）。本类累计曝光越多越低（疲劳）。尺度沿革 50 → 20（2026-09-12）→ 15（2026-09-13 用户裁定「R 力度再大一些」）。",
    "baseline_utility": "常态表达效用锚点 B_i；由W05-W12事件前供给映射固定，不参与W13-W18拟合。注意它不同于环境丰沛度B_t。",
    "benefit": "表达效用 U = B_i + R·(D−B_i)。",
    "emergence": "（已退役）涌现环境增益指数 θ：2026-09-12 用户裁定 G 退役，θ 不再进入任何决策；字段保留兼容历史 decision_log。",
    "env_abundance": "决策时所见丰沛度 B_t（快照键 meme_env.abundance；存量越丰沛越易诞生 meme）。",
    "env_emptiness": "决策时所见空旷度 S_t（快照键 meme_env.emptiness；当期新增越少越空旷越宜传播；sustained_hot 臂 W13 后冻结）。",
    "env_gain": "决策时所见涌现增益 G_t（快照键 meme_env.gain）。",
    "env_multiplier": "环境乘子 G^θ（θ=emergence；玩梗型随周变化，其余类型恒 1）。",
    "share_own": "该 agent 所见信息流中本类内容占比（spiral 的输入）。",
    "share_base": "本类型在 100 人群体中的份额（spiral 的期望基线：玩梗0.19/悼念0.22/营销0.23/教育0.15/其他0.21）。",
    "cum_own": "该 agent 累计本类曝光数（decay 的输入；R 的半饱和尺度为 15，即累计约 15 次本类曝光时 R≈e^(−λ)）。",
    "speak": "决策结果：是否发言（U ≥ activity）。",
    "posted": "发言是否成功发布（发言后还有 1 次内容 LLM 调用，失败/空则 posted=False）。",
    "n_decisions": "该周该类型有决策记录的 agent 数（正常=类型人数）。",
    "n_speak": "决策发言的人数。",
    "n_posted": "实际成功发布的人数。",
    "mean_u": "U 的类型内均值。",
    "mean_threshold": "activity 的类型内均值（个体间有 U[0.8,1.2] 抖动）。",
    "mean_benefit": "锚定式表达效用 U 的类型内均值。",
    "mean_baseline": "常态表达效用锚点 B_i 的类型内均值。",
    "mean_spiral": "当周沉默螺旋因子 D 的类型内均值。",
    "mean_fatigue": "当周注意力衰减因子 R 的类型内均值。",
    "mean_env_gain": "决策时所见涌现增益 G 的类型内均值。",
    "mean_env_multiplier": "环境乘子 G^θ 的类型内均值（仅玩梗型随周变化，其余恒 1）。",
    # 帖子流
    "post_id": "帖子编号（全局自增）。官方讣告=official_w13_announcement（字符串 id）。",
    "author_handle": "作者（注入帖=数据集作者；agent 帖=agent_id）。",
    "type": "作者类型（帖子主类型；注入帖=数据集标注）。",
    "assigned_type": "env 四词表对正文的独立判类结果（注入帖=数据集标签）。",
    "is_official": "是否官方帖（全程仅 W13 一条讣告）。",
    "exposure_count": "该帖累计被推荐进 feed 的次数（生命周期曝光量）。",
    "tick_produced": "该帖产生的 step 序号。",
    "source": "帖子来源：injected=真实数据注入 / agent=模拟 agent 产出。",
    # 派生视图
    "bias": "策展偏差 = exposure_share − supply_share_all（按类型按周）。>0 算法放大该类，<0 压制。全因子对比的核心量。",
    "bench_share": "真实基准周度份额（hypothesis_4/benchmark_curves.json weekly_category_matrix，combined 口径）。",
    "delta": "模拟 − 真实（combined 口径供给份额差，百分点）。衡量模拟对真实周度构成的贴合度。",
}


def _pct(v: float | None) -> str:
    return "—" if v is None else f"{v * 100:.1f}%"


def _num(v, nd: int = 3) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float) and abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.{nd}f}"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path):
    """容忍读取失败（pid.json 非原子写，可能撞上重写瞬间）。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_jsonl_table(run_dir: Path, table: str) -> list[dict]:
    """读 replay 表全部分片；容忍末尾被截断的半行（追加写进行中）。"""
    rows: list[dict] = []
    for f in sorted(glob.glob(str(run_dir / "replay" / f"{table}.*.jsonl"))):
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # 半行：下一 tick 数据完整后再读
        except OSError:
            continue
    return rows


def _find_env_state(run_dir: Path) -> Path | None:
    hits = sorted(glob.glob(str(run_dir / "env" / "*" / "state" / "ENV_STATE.json")))
    return Path(hits[0]) if hits else None


def _is_alive(pid) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


# ---------------- 单 run 采集 ----------------

def collect_run(run_dir: Path, label: str) -> dict:
    data: dict = {"run_id": run_dir.name, "label": label, "path": str(run_dir)}

    # 0) 进程/进度
    pid_data = _read_json(run_dir / "pid.json") or {}
    step_data = _read_json(run_dir / "SOCIETY_STEP.json") or {}
    status = pid_data.get("status")
    data["process"] = {
        "status": status or ("有数据无心跳" if (run_dir / "replay").exists() else "未知"),
        "pid": pid_data.get("pid"),
        "alive": _is_alive(pid_data.get("pid")) and str(status or "").lower() not in ("completed", "failed"),
        "start_time": pid_data.get("start_time"),
        "end_time": pid_data.get("end_time"),
        "simulation_time": pid_data.get("simulation_time"),
        "step_count": step_data.get("step_count", pid_data.get("step_count")),
        "completed_step_count": step_data.get("completed_step_count"),
        "terminated": step_data.get("terminated"),
        "experiment_id": pid_data.get("experiment_id"),
    }

    # 1) env 周度行（每 step 1 行，同 step 后写覆盖先写）
    env_rows: dict[int, dict] = {}
    for r in _read_jsonl_table(run_dir, "curation_dynamics_env_state"):
        s = r.get("step")
        if s is None:
            continue
        env_rows[int(s)] = r
    data["env_rows"] = [env_rows[k] for k in sorted(env_rows)]

    # 2) agent 周度行（每 step ~100 行）
    agent_by_step: dict[int, list[dict]] = {}
    for r in _read_jsonl_table(run_dir, "curation_dynamics_agent_state"):
        s = r.get("step")
        if s is None:
            continue
        agent_by_step.setdefault(int(s), []).append(r)
    data["agent_by_step"] = agent_by_step

    # 3) ENV_STATE.json（帖池 / 当前周 / 进行中 tick）
    env_state = None
    st_path = _find_env_state(run_dir)
    if st_path is not None:
        env_state = _read_json(st_path)
    data["env_state_path"] = str(st_path) if st_path else None
    data["env_state"] = env_state

    # 4) AGENT.json decision_log（机制透视）
    agents: list[dict] = []
    for meta_path in sorted(glob.glob(str(run_dir / "agents" / "agent_*" / "AGENT.json"))):
        meta = _read_json(Path(meta_path))
        if not meta:
            continue
        profile = meta.get("profile") or {}
        agents.append({
            "agent_id": meta.get("id"),
            "name": meta.get("name"),
            "agent_type": profile.get("agent_type", "other"),
            "activity": (profile.get("params") or {}).get("activity"),
            "decision_log": meta.get("decision_log") or [],
        })
    data["agents"] = agents
    return data


# ---------------- 聚合 ----------------

def aggregate_weekly(data: dict) -> list[dict]:
    """把 env 行 + agent 行聚合 + 机制聚合合并成逐周记录（按 step 排序）。"""
    # 机制聚合：(week, type) -> list of decision records
    mech: dict[tuple[str, str], list[dict]] = {}
    for ag in data["agents"]:
        atype = ag["agent_type"]
        for rec in ag["decision_log"]:
            wk = rec.get("week")
            if not wk or rec.get("u") is None:
                continue
            mech.setdefault((wk, atype), []).append(rec)

    weekly = []
    for erow in data["env_rows"]:
        step = int(erow["step"])
        wk = erow.get("week")
        row: dict = dict(erow)

        # agent 行为聚合（按类型）
        rows = data["agent_by_step"].get(step, [])
        by_type: dict[str, list[dict]] = {}
        for r in rows:
            by_type.setdefault(str(r.get("agent_type")), []).append(r)
        row["agent_agg"] = {}
        for t, rs in sorted(by_type.items()):
            own_ex = [float(r.get(f"exposure_{t}", 0) or 0) for r in rs]
            cli = [float(r.get(f"climate_{t}", 0) or 0) for r in rs]
            row["agent_agg"][t] = {
                "n_agents": len(rs),
                "spoke_rate": fmean(1 if r.get("spoke") else 0 for r in rs),
                "mismatch_rate": fmean(1 if r.get("type_mismatch") else 0 for r in rs),
                "mean_exposure_own": fmean(own_ex) if own_ex else 0.0,
                "mean_climate_own": fmean(cli) if cli else 0.0,
                "mean_feed_slots": fmean(float(r.get("feed_slots", 0) or 0) for r in rs),
            }

        # 机制聚合（按类型）
        row["mech_agg"] = {}
        for t in TYPE_ORDER:
            recs = mech.get((wk, t), [])
            if not recs:
                continue

            def _mean_of(key: str, source: str | None = None) -> float | None:
                vals = []
                for rc in recs:
                    container = rc.get(source) if source else rc
                    v = container.get(key) if isinstance(container, dict) else None
                    if v is not None:
                        vals.append(float(v))
                return fmean(vals) if vals else None

            row["mech_agg"][t] = {
                "n_decisions": len(recs),
                "n_speak": sum(1 for rc in recs if rc.get("speak")),
                "n_posted": sum(1 for rc in recs if rc.get("posted")),
                "mean_u": _mean_of("u"),
                "mean_threshold": _mean_of("threshold"),
                "mean_benefit": _mean_of("benefit", "components"),
                "mean_baseline": _mean_of("baseline_utility", "components"),
                "mean_spiral": _mean_of("spiral", "components"),
                "mean_fatigue": _mean_of("decay", "components"),
                "mean_env_gain": _mean_of("env_gain", "components"),
                "mean_env_multiplier": _mean_of("env_multiplier", "components"),
            }

        # 派生视图
        row["bias"] = {
            t: (erow.get(f"exposure_share_{t}") - erow.get(f"supply_share_all_{t}"))
            if erow.get(f"exposure_share_{t}") is not None and erow.get(f"supply_share_all_{t}") is not None
            else None
            for t in TYPE_ALL
        }
        weekly.append(row)
    return weekly


def attach_benchmark(weekly: list[dict], bench: dict | None) -> None:
    if not bench:
        return
    matrix = bench.get("weekly_category_matrix") or {}
    for row in weekly:
        wk = row.get("week")
        wm = matrix.get(wk)
        if not wm:
            continue
        total = float(wm.get("total", 0) or 0)
        if total <= 0:
            continue
        row["benchmark"] = {
            t: {"bench_share": float(wm.get(k, 0) or 0) / total,
                "delta": (row.get(f"supply_share_all_{t}") - float(wm.get(k, 0) or 0) / total)
                if row.get(f"supply_share_all_{t}") is not None else None}
            for k, t in BENCH_KEY_MAP.items()  # k=中文标签, t=模拟类型
        }


def posts_view(data: dict) -> dict:
    """帖子流：帖池按周分组 + 进行中 tick 的新帖。"""
    st = data["env_state"] or {}
    pool = st.get("_posts") or {}
    by_week: dict[str, list[dict]] = {}
    for pid_str, p in pool.items():
        rec = {
            "post_id": p.get("post_id", pid_str),
            "author_handle": p.get("author_handle"),
            "type": p.get("type"),
            "assigned_type": p.get("assigned_type"),
            "is_official": bool(p.get("is_official")),
            "exposure_count": p.get("exposure_count", 0),
            "tick_produced": p.get("tick_produced"),
            "week": p.get("week"),
            "content": p.get("content", ""),
        }
        rec["source"] = "injected" if str(rec["author_handle"]).startswith("ext_") or str(p.get("author_id", "")).startswith("ext_") else "agent"
        by_week.setdefault(str(p.get("week")), []).append(rec)
    for wk in by_week:
        by_week[wk].sort(key=lambda r: str(r["post_id"]), reverse=True)  # 最新在前
    current_week = st.get("_current_week")
    injected_now = []
    for pid in st.get("_injected_this_week_ids") or []:
        p = pool.get(str(pid))
        if p:
            injected_now.append(p.get("post_id", pid))
    pending = [
        {"post_id": r.get("post_id"), "author": r.get("agent_id"), "type": r.get("pool_type"),
         "assigned_type": r.get("assigned_type"), "content": r.get("content", "")}
        for r in (st.get("_pending_agent_posts") or [])
    ]
    return {
        "current_week": current_week,
        "pool_total": len(pool),
        "posts_by_week": by_week,
        "injected_this_tick": injected_now,
        "pending_agent_posts": pending,
    }


# ---------------- 渲染（md） ----------------

def _docs_block(keys: list[str]) -> str:
    lines = ["", "**字段说明**："]
    for k in keys:
        if k in FIELDS:
            lines.append(f"- `{k}`：{FIELDS[k]}")
    return "\n".join(lines)


def render_process_md(data: dict) -> str:
    p = data["process"]
    alive = "✅ 存活" if p["alive"] else "否"
    lines = [
        f"- **状态**：{p['status']}　**pid**：{p['pid'] or '—'}　**进程存活**：{alive}",
        f"- **启动**：{p['start_time'] or '—'}　**结束**：{p['end_time'] or '—'}",
        f"- **进度**：step_count={p['step_count'] if p['step_count'] is not None else '—'} / 11　**terminated**：{p['terminated']}",
        f"- **模拟时钟**：{p['simulation_time'] or '—'}",
    ]
    return "\n".join(lines)


def render_weekly_md(weekly: list[dict], week_filter: str | None) -> str:
    rows = [r for r in weekly if not week_filter or r.get("week") == week_filter]
    out = []
    # 表A 供给与玩梗涌现环境
    out.append("### 表A 周度供给与玩梗涌现环境\n")
    out.append("> 环境 B_t/S_t/G_t 为**观测序列**，不进入决策；agent 侧常态锚点 B_i 是另一参数，效用为 U = B_i + R·(D−B_i)。\n")
    head = ("| 周 | 存量 | arena新增 | 现实新增 | B丰沛 | S空旷 | G增益 | 供给总 | Agent帖 | 注入 | "
            + " | ".join(f"供给{TYPE_LABEL[t]}" for t in TYPE_ORDER)
            + " | 供给噪音 | 官方帖 | 官方槽位 |")
    sep = "|---" * (10 + len(TYPE_ORDER) + 3) + "|"
    out += [head, sep]
    for r in rows:
        cells = [r.get("week"), r.get("meme_env_stock"), r.get("meme_env_flow"),
                 r.get("meme_env_flow_world"), _num(r.get("meme_env_abundance"), 3),
                 _num(r.get("meme_env_emptiness"), 3), _num(r.get("meme_env_gain"), 3),
                 r.get("total_supply"), r.get("agent_supply"), r.get("injected_count")]
        cells += [_pct(r.get(f"supply_share_all_{t}")) for t in TYPE_ORDER]
        cells += [_pct(r.get("supply_share_all_noise")), r.get("official_posts_count"),
                  r.get("official_exposure_slots")]
        out.append("| " + " | ".join(str(c) if c is not None else "—" for c in cells) + " |")
    out.append(_docs_block(["week", "meme_env_stock", "meme_env_flow", "meme_env_flow_world",
                            "meme_env_abundance", "meme_env_emptiness", "meme_env_gain",
                            "total_supply", "agent_supply", "injected_count"] +
                           [f"supply_share_all_{t}" for t in TYPE_ORDER] +
                           ["official_posts_count", "official_exposure_slots"]))
    # 表B 曝光
    out.append("\n### 表B 周度曝光（推荐算法产出）\n")
    head = "| 周 | 总曝光 | " + " | ".join(f"曝光{TYPE_LABEL[t]}" for t in TYPE_ALL) + " | " + " | ".join(
        f"份额{TYPE_LABEL[t]}" for t in TYPE_ALL) + " |"
    sep = "|---" * (2 + 2 * len(TYPE_ALL)) + "|"
    out += [head, sep]
    for r in rows:
        cells = [r.get("week"), _num(r.get("total_exposures"))]
        cells += [_num(r.get(f"exposure_{t}")) for t in TYPE_ALL]
        cells += [_pct(r.get(f"exposure_share_{t}")) for t in TYPE_ALL]
        out.append("| " + " | ".join(str(c) if c is not None else "—" for c in cells) + " |")
    out.append(_docs_block(["total_exposures", "exposure_meme", "exposure_share_meme"]))
    # 表B2 feed 机制审计（生命周期 / 曝光年龄结构 / 抽样参数 / 强制槽位）
    out.append("\n### 表B2 feed 机制审计（帖子生命周期、候选取样与强制槽位）\n")
    head = "| 周 | 活池 | 曝光龄0 | 龄1 | 龄2 | 龄≥3 | 龄≥3占比 | 议程保底 | 抽样温度 | 半衰期 | 饱和尺度 |"
    out += [head, "|---" * 11 + "|"]
    for r in rows:
        a = [r.get(f"exposure_slots_age{k}") for k in (0, 1, 2)]
        old = r.get("exposure_slots_age3plus")
        tot = sum(x for x in a + [old] if isinstance(x, (int, float)))
        cells = [r.get("week"), r.get("feed_live_pool")] + [x if x is not None else "—" for x in a] + [
            old if old is not None else "—",
            _pct((old / tot) if (isinstance(old, (int, float)) and tot) else None),
            r.get("event_floor_slots") if r.get("event_floor_slots") is not None else "—",
            _num(r.get("feed_sample_temp"), 2), _num(r.get("feed_half_life_weeks"), 2),
            _num(r.get("feed_saturation_scale"), 1),
        ]
        out.append("| " + " | ".join(str(c) if c is not None else "—" for c in cells) + " |")
    out.append(_docs_block(["feed_live_pool", "exposure_slots_age0", "exposure_slots_age1",
                            "exposure_slots_age2", "exposure_slots_age3plus", "event_floor_slots",
                            "feed_sample_temp", "feed_half_life_weeks", "feed_saturation_scale"]))
    # 表C Agent 行为
    out.append("\n### 表C Agent 行为聚合（按类型）\n")
    head = "| 周 | 类型 | 人数 | 发言率 | 判类不一致率 | 本类人均曝光 | 所见本类占比(气候) | feed长度 |"
    out += [head, "|---" * 8 + "|"]
    for r in rows:
        # 类型按固定顺序展示（玩梗/悼念/教育/营销/其他），未知类型附后
        ordered = [t for t in TYPE_ORDER if t in (r.get("agent_agg") or {})]
        ordered += [t for t in sorted((r.get("agent_agg") or {})) if t not in TYPE_ORDER]
        for t in ordered:
            agg = r["agent_agg"][t]
            out.append(f"| {r.get('week')} | {TYPE_LABEL.get(t, t)} | {agg['n_agents']} | "
                       f"{_pct(agg['spoke_rate'])} | {_pct(agg['mismatch_rate'])} | "
                       f"{_num(agg['mean_exposure_own'], 2)} | {_pct(agg['mean_climate_own'])} | "
                       f"{_num(agg['mean_feed_slots'], 1)} |")
    out.append(_docs_block(["n_agents", "spoke_rate", "mismatch_rate", "mean_exposure_own",
                            "mean_climate_own", "mean_feed_slots"]))
    # 表D 机制透视
    out.append("\n### 表D 机制透视（锚定式效用：U = B_i + R·(D−B_i)，U ≥ activity 时发言）\n")
    head = ("| 周 | 类型 | 决策数 | 发言 | 发布 | mean U | mean门槛 | mean B_i | mean D | mean R | mean G(仅观测) |")
    out += [head, "|---" * 11 + "|"]
    for r in rows:
        for t in TYPE_ORDER:
            m = (r.get("mech_agg") or {}).get(t)
            if not m:
                continue
            out.append(
                f"| {r.get('week')} | {TYPE_LABEL[t]} | {m['n_decisions']} | {m['n_speak']} | "
                f"{m['n_posted']} | {_num(m['mean_u'])} | {_num(m['mean_threshold'])} | "
                f"{_num(m['mean_baseline'])} | {_num(m['mean_spiral'])} | "
                f"{_num(m['mean_fatigue'])} | {_num(m['mean_env_gain'])} |")
    out.append(_docs_block(["u", "threshold", "baseline_utility", "spiral_scale", "spiral", "decay", "benefit", "emergence",
                            "env_abundance", "env_emptiness", "env_gain", "env_multiplier",
                            "share_own", "share_base", "cum_own", "speak",
                            "posted", "n_decisions", "n_speak", "n_posted", "mean_u",
                            "mean_threshold", "mean_benefit", "mean_env_gain",
                            "mean_env_multiplier"]))
    return "\n".join(out)


def render_posts_md(pv: dict, week_filter: str | None, limit: int) -> str:
    lines = []
    cur = week_filter or pv["current_week"]
    weeks = sorted(pv["posts_by_week"])
    lines.append(f"- **当前周（引擎正在处理）**：{pv['current_week'] or '—'}　**帖池总量**：{pv['pool_total']}")
    if pv["injected_this_tick"] or pv["pending_agent_posts"]:
        lines.append(f"- **进行中 tick 新注入**：{len(pv['injected_this_tick'])} 条　"
                     f"**待并入 agent 帖**：{len(pv['pending_agent_posts'])} 条")
    target = cur if cur in pv["posts_by_week"] else (weeks[-1] if weeks else None)
    if target is None:
        lines.append("\n（帖池暂无数据）")
        return "\n".join(lines)
    posts = pv["posts_by_week"][target][:limit]
    lines.append(f"\n### 帖子流：{target}（最新 {len(posts)} / {len(pv['posts_by_week'][target])} 条，按 post_id 倒序）\n")
    lines.append("| post_id | 作者 | 类型 | 判类 | 来源 | 官方 | 曝光 | 内容摘录 |")
    lines.append("|---" * 8 + "|")
    for p in posts:
        excerpt = (p.get("content") or "").replace("\n", " ")[:60]
        lines.append(
            f"| {p['post_id']} | {p['author_handle']} | {TYPE_LABEL.get(p['type'], p['type'])} | "
            f"{TYPE_LABEL.get(p['assigned_type'], p['assigned_type'])} | {p['source']} | "
            f"{'是' if p['is_official'] else ''} | {p['exposure_count']} | {excerpt} |")
    if pv["pending_agent_posts"]:
        lines.append("\n**待并入的 agent 帖（本 tick 产出，下一周起传播）**：")
        for r in pv["pending_agent_posts"][:10]:
            excerpt = (r.get("content") or "").replace("\n", " ")[:60]
            lines.append(f"- {r['post_id']}（{TYPE_LABEL.get(r['type'], r['type'])}，判类 {TYPE_LABEL.get(r['assigned_type'], r['assigned_type'])}）：{excerpt}")
    lines.append(_docs_block(["post_id", "author_handle", "type", "assigned_type", "is_official",
                              "exposure_count", "tick_produced", "source"]))
    return "\n".join(lines)


def render_derived_md(weekly: list[dict], week_filter: str | None) -> str:
    rows = [r for r in weekly if not week_filter or r.get("week") == week_filter]
    out = ["### 策展偏差（曝光份额 − combined 供给份额，百分点）\n"]
    head = "| 周 | " + " | ".join(TYPE_LABEL[t] for t in TYPE_ALL) + " |"
    out += [head, "|---" * (1 + len(TYPE_ALL)) + "|"]
    for r in rows:
        cells = [r.get("week")] + [
            f"{(r['bias'][t] or 0) * 100:+.1f}" if r.get("bias", {}).get(t) is not None else "—"
            for t in TYPE_ALL
        ]
        out.append("| " + " | ".join(str(c) for c in cells) + " |")
    out.append(_docs_block(["bias"]))
    has_bench = any(r.get("benchmark") for r in rows)
    if has_bench:
        out.append("\n### 模拟 vs 真实基准（combined 供给份额，百分点）\n")
        out.append("| 周 | 类型 | 真实份额 | 模拟份额 | Δ(模拟−真实) |")
        out.append("|---|---|---|---|---|")
        for r in rows:
            for t in TYPE_ORDER:
                b = (r.get("benchmark") or {}).get(t)
                if not b:
                    continue
                delta = f"{b['delta'] * 100:+.1f}" if b.get("delta") is not None else "—"
                out.append(f"| {r.get('week')} | {TYPE_LABEL[t]} | {_pct(b['bench_share'])} | "
                           f"{_pct(r.get(f'supply_share_all_{t}'))} | {delta} |")
        out.append(_docs_block(["bench_share", "delta"]))
    else:
        out.append("\n（benchmark 对比：该周无真实基准行，跳过）")
    return "\n".join(out)


def render_run_status_md(data: dict, weekly: list[dict], pv: dict,
                         week_filter: str | None, limit: int) -> str:
    last = weekly[-1] if weekly else None
    title = f"# Run 监视快照：{data['label']}"
    lines = [
        title,
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- run 目录：`{data['path']}`",
    ]
    if last:
        lines.append(f"- **最近完结周**：{last.get('week')}（step {last.get('step')}）　"
                     f"涌现环境 B={_num(last.get('meme_env_abundance'))} S={_num(last.get('meme_env_emptiness'))} "
                     f"G={_num(last.get('meme_env_gain'))}　"
                     f"Agent 帖 {last.get('agent_supply')} / 注入 {last.get('injected_count')}")
    lines += ["", "## 进程与进度", render_process_md(data),
              _docs_block(["status", "pid", "alive", "start_time", "end_time", "simulation_time",
                           "step_count", "completed_step_count", "terminated"])]
    lines += ["", "## 周度指标", render_weekly_md(weekly, week_filter)]
    lines += ["", "## 帖子流", render_posts_md(pv, week_filter, limit)]
    lines += ["", "## 派生视图", render_derived_md(weekly, week_filter)]
    return "\n".join(lines) + "\n"


# ---------------- 总览 ----------------

def render_overview(runs: list[dict], weekly_map: dict[str, list[dict]]) -> str:
    lines = [
        "# 多 Run 总览（CurationDynamics 3 臂 × 3 seed = 9 runs）",
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "| run | 状态 | 进程 | 周进度 | 当前周 | 涌现G | Agent帖累计 | 供给前二(combined) | 帖池 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for data in sorted(runs, key=lambda d: d["label"]):
        p = data["process"]
        weekly = weekly_map.get(data["label"], [])
        last = weekly[-1] if weekly else None
        weeks_done = len(weekly)
        env_gain = _num(last.get("meme_env_gain")) if last else "—"
        cur_week = (data["env_state"] or {}).get("_current_week") or (last.get("week") if last else "—")
        agent_total = sum(int(r.get("agent_supply") or 0) for r in weekly)
        top2 = "—"
        if last:
            shares = {t: last.get(f"supply_share_all_{t}") for t in TYPE_ORDER
                      if last.get(f"supply_share_all_{t}") is not None}
            top2 = "、".join(f"{TYPE_LABEL[t]}{_pct(v)}" for t, v in
                             sorted(shares.items(), key=lambda kv: -kv[1])[:2]) or "—"
        alive = "✅" if p["alive"] else ""
        pool_total = len((data["env_state"] or {}).get("_posts") or {})
        lines.append(f"| {data['label']} | {p['status']} | {alive} | {weeks_done}/11 | "
                     f"{cur_week} | {env_gain} | {agent_total} | {top2} | {pool_total} |")
    lines += [
        "",
        "**字段说明**：",
    ]
    overview_docs = {
        "Agent帖累计": "该 run 各周 Agent 产出帖数之和（≈内容 LLM 调用总量）。",
        "供给前二(combined)": "最近完结周 combined 口径（注入+产出，分母含噪音）份额最高的两个类型。",
        "周进度": "已完结的周数 / 总周数（11 周 = W12…W22）。",
        "帖池": "ENV_STATE.json 帖池中的帖子总数（含注入与 agent 产出）。",
    }
    for k in ["status", "pid", "alive", "step_count", "week", "meme_env_gain",
              "agent_supply", "supply_share_all_meme", "exposure_count"]:
        if k in FIELDS:
            label = {"agent_supply": "Agent帖累计", "supply_share_all_meme": "供给前二(combined)",
                     "meme_env_gain": "涌现G"}.get(k, k)
            lines.append(f"- `{label}`：{overview_docs.get(label) or FIELDS[k]}")
    lines.append(f"- `周进度`：{overview_docs['周进度']}")
    lines.append(f"- `帖池`：{overview_docs['帖池']}")
    return "\n".join(lines) + "\n"


# ---------------- 主流程 ----------------

def discover_runs(args) -> list[tuple[Path, str]]:
    """显式 --run-dir 优先；否则自动发现 runs/* 与固定 run/。"""
    out: list[tuple[Path, str]] = []
    if args.run_dir:
        labels = args.label or []
        for i, rd in enumerate(args.run_dir):
            p = Path(rd).resolve()
            out.append((p, labels[i] if i < len(labels) else p.name))
    else:
        candidates: list[Path] = []
        runs_root = SCRIPT_DIR / "runs"
        if runs_root.is_dir():
            candidates += sorted(d for d in runs_root.iterdir() if d.is_dir())
        fixed = SCRIPT_DIR / "run"
        if fixed.is_dir():
            candidates.append(fixed)
        for d in candidates:
            looks_like_run = (d / "pid.json").exists() or (d / "SOCIETY.json").exists() \
                or (d / "replay").is_dir() or _find_env_state(d) is not None
            if looks_like_run:
                out.append((d, d.name))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="CurationDynamics 推演监视器（落盘快照，零侵入）")
    ap.add_argument("--run-dir", action="append", help="显式指定 run 目录（可重复；默认自动发现 runs/* 与 run/）")
    ap.add_argument("--label", action="append", help="与 --run-dir 顺序配对的显示名")
    ap.add_argument("--week", help="只看某周（如 2026-W13）")
    ap.add_argument("--posts-limit", type=int, default=30, help="帖子流摘录条数上限（默认 30）")
    ap.add_argument("--out-dir", default=str(SCRIPT_DIR / "monitor"), help="快照输出目录")
    ap.add_argument("--overview-only", action="store_true", help="只刷新多 run 总览")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    bench = _read_json(BENCH_PATH) if BENCH_PATH.exists() else None

    run_dirs = discover_runs(args)
    if not run_dirs:
        print("未发现任何 run 目录（等待 runs/* 或 run/ 出现；也可用 --run-dir 指定）。")

    weekly_map: dict[str, list[dict]] = {}
    collected: list[dict] = []
    for run_dir, label in run_dirs:
        data = collect_run(run_dir, label)
        collected.append(data)
        weekly = aggregate_weekly(data)
        attach_benchmark(weekly, bench)
        weekly_map[label] = weekly
        if not args.overview_only:
            pv = posts_view(data)
            status_json = {
                "run_id": data["run_id"],
                "label": label,
                "path": data["path"],
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "process": data["process"],
                "env_state_path": data["env_state_path"],
                "current_week": (data["env_state"] or {}).get("_current_week"),
                "weekly": weekly,
                "posts": pv,
                "field_docs": FIELDS,
            }
            _atomic_write(out_dir / label / "status.json",
                          json.dumps(status_json, ensure_ascii=False, indent=2, default=str))
            _atomic_write(out_dir / label / "status.md",
                          render_run_status_md(data, weekly, pv, args.week, args.posts_limit))
            print(f"✓ {label}: {len(weekly)} 周  -> {out_dir / label / 'status.md'}")

    _atomic_write(out_dir / "overview.md", render_overview(collected, weekly_map))
    _atomic_write(out_dir / "overview.json", json.dumps({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "runs": [
            {"label": d["label"], "path": d["path"], "process": d["process"],
             "current_week": (d["env_state"] or {}).get("_current_week"),
             "weeks_done": len(weekly_map.get(d["label"], [])),
             "posts_in_pool": len((d["env_state"] or {}).get("_posts") or {})}
            for d in collected
        ],
        "field_docs": {k: FIELDS[k] for k in
                       ["status", "pid", "alive", "step_count", "week", "meme_env_gain",
                        "agent_supply", "supply_share_all_meme", "exposure_count"] if k in FIELDS},
    }, ensure_ascii=False, indent=2, default=str))
    print(f"✓ 总览 -> {out_dir / 'overview.md'}")


if __name__ == "__main__":
    main()
