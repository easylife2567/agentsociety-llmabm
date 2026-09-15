#!/usr/bin/env python3
"""plot_arm_charts: 把 3 臂 × 3 seeds 的 run 汇成**臂级 3-seed 平均**图。

依据 EXPERIMENT.md 第 294 行（用户裁定）：
    「臂间比较与形态判定以『各臂 3 seed 平均』为准；单 run 曲线的锯齿不作为形态证据。」

故本脚本不做逐 run 展示（那是 plot_run_charts.py 的职责，用于诊断/QC），
只回答实验层的两个问题：
    1. 三个推荐算法臂的 Agent 自主产出是否复现真实周度构成？
       （主口径：Agent-only；真实 benchmark 排除 Agent 不生成的 noise 后重归一化）
    2. 哪个算法对五类内容整体构成的拟合误差最低？
       （口径：mean ± min–max 包络，n=3；n 这么小时用包络比 sd 带诚实）

输入：runs/anchored_v1/_derived/monitor/<run_id>/status.json（由 monitor.py 生成）
输出：runs/anchored_v1/_derived/charts/ARM_*.png
    + runs/anchored_v1/_derived/data/arm/weekly_*.csv（聚合数值，供复核）

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/plot_arm_charts.py
    $PYTHON_PATH hypothesis_4/experiment_1/plot_arm_charts.py --no-charts   # 只出 CSV
    # 干跑（任意快照，不要求是 9 个正式 run）
    $PYTHON_PATH hypothesis_4/experiment_1/plot_arm_charts.py \
        --status monitor/a/status.json --label interest_s0 \
        --status monitor/b/status.json --label interest_s1 --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

SCRIPT_DIR = Path(__file__).resolve().parent
ROUND_ROOT = SCRIPT_DIR / "runs" / "anchored_v1"
DERIVED_ROOT = ROUND_ROOT / "_derived"
DATA_DIR = DERIVED_ROOT / "data" / "arm"
CHARTS_DIR = DERIVED_ROOT / "charts"
MONITOR_DIR = DERIVED_ROOT / "monitor"

EXPECTED_WEEKS = 11
ARMS = ["random", "chronological", "interest"]
ARM_LABEL = {"random": "随机推荐", "chronological": "时序推荐", "interest": "兴趣推荐"}
ARM_LABEL_EN = {"random": "Random", "chronological": "Chronological", "interest": "Interest"}
# 臂配色：与 run 图区分开，三臂固定色以便跨图对照
ARM_COLOR = {"random": "#6B6B6B", "chronological": "#0072B2", "interest": "#D55E00"}

TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
TYPE_LABEL = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
              "marketing": "营销", "other": "其他", "noise": "噪音"}
TYPE_LABEL_EN = {"meme": "Meme", "mourning": "Mourning", "education": "Education",
                 "marketing": "Marketing", "other": "Other", "noise": "Noise"}
TYPE_COLOR = {"mourning": "#0072B2", "meme": "#D55E00", "education": "#009E73",
              "marketing": "#E69F00", "other": "#56B4E9", "noise": "#CC79A7"}

DEATH_WEEK = "2026-W13"
DEATH_LABEL = "去世 3-24 (W13)"

RUN_ID_RE = re.compile(r"^(?:anchored_v1_)?(random|chronological|interest)_s(\d+)$")

# 缺字告警升级为错误：matplotlib 遇到字体缺字时只发 UserWarning，图上表现为空白/方框，
# 图仍会正常落盘——属静默产出坏图。图是本实验的交付物，宁可炸也不要错。
warnings.filterwarnings("error", message=r"Glyph \d+ .* missing from font")

plt.rcParams.update({
    # DejaVu Sans 兜底：CJK 字体普遍缺 U+2212(减号) 等符号，缺字会让负面刻度渲染成空白
    "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS",
                        "Heiti TC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#444444",
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

BASELINE_SUPPLY_YLIM = (0, 80)
VALID_TYPES = [t for t in TYPE_ORDER if t != "noise"]


# ---------------- 载入与校验 ----------------

def replay_counts(run_path: Path) -> dict[str, int]:
    """统计 run/replay 下各逻辑表的**总行数**（JSONL 按 hash 分片，故要跨文件求和）。"""
    out: dict[str, int] = {}
    rp = run_path / "replay"
    if not rp.is_dir():
        return out
    for f in rp.glob("*.jsonl"):
        if f.name == "_schema.json":
            continue
        key = f.name.split(".")[0]
        with open(f, encoding="utf-8", errors="replace") as fh:
            out[key] = out.get(key, 0) + sum(1 for _ in fh)
    return out


def check_replay(run_path: Path, n_agents: int, label: str) -> str | None:
    """校验 replay 表**行数**是否与「n_agents × 11 周」相符，不符则返回原因。

    step_count 是引擎的自我申报；replay 行数才是实际落盘的数据。二者要同时成立
    才算真跑完——2026-09-13 那次事故里引擎把「第 0 步就崩」的 run 申报成
    completed，而 replay 里只剩 core_agent_profile、两张 curation_dynamics 表**全空**。
    只卡 step_count 挡不住「步数对但表被截断」这一族。
    """
    c = replay_counts(run_path)
    if not c:
        return f"{label}: replay/ 无任何 jsonl"
    want_agent = n_agents * EXPECTED_WEEKS
    got_agent = c.get("curation_dynamics_agent_state", 0)
    got_env = c.get("curation_dynamics_env_state", 0)
    if got_agent != want_agent:
        return (f"{label}: curation_dynamics_agent_state {got_agent} 行 ≠ "
                f"{n_agents} agents × {EXPECTED_WEEKS} 周 = {want_agent}")
    if got_env != EXPECTED_WEEKS:
        return f"{label}: curation_dynamics_env_state {got_env} 行 ≠ {EXPECTED_WEEKS}"
    return None


def load_runs(explicit: list[tuple[Path, str]], strict: bool = True) -> list[dict]:
    """载入快照并**强校验**：周数达 11 且 replay 表行数达标。任何 run 不合格就报错退出。

    这里刻意不做「有几个算几个」的宽松处理：少一个 seed 会让臂均值变成
    2 个 seed 的均值却仍然画成同样的曲线——是静默错误，必须炸出来。
    """
    runs: list[dict] = []
    problems: list[str] = []

    if explicit:
        sources = explicit
    else:
        sources = []
        for arm in ARMS:
            for d in sorted(MONITOR_DIR.glob(f"anchored_v1_{arm}_s*/status.json")):
                sources.append((d, d.parent.name))
        if not sources:
            raise SystemExit(
                f"未在 {MONITOR_DIR} 找到任何 <arm>_s<seed>/status.json。\n"
                f"请先跑：$PYTHON_PATH hypothesis_4/experiment_1/monitor.py")

    for path, label in sources:
        if not path.exists():
            problems.append(f"{label}: 快照不存在 {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        weekly = data.get("weekly") or []
        if len(weekly) != EXPECTED_WEEKS:
            problems.append(f"{label}: 周数 {len(weekly)} ≠ {EXPECTED_WEEKS}（run 未跑完或数据不全）")
            continue
        # agent 总数从快照自取（= 各类型 n_agents 之和），避免硬编码 100
        n_agents = sum(a.get("n_agents", 0) for a in weekly[0].get("agent_agg", {}).values())
        run_path = Path(data.get("path") or "")
        if not (n_agents and run_path.is_dir()):
            # 快照里的 path 指不回 run 目录（如已归档/搬移）→ 无法核对实际落盘数据。
            # 干跑放行；正式出图必须报错，否则「路径失效」会变成静默跳过完整性校验。
            if strict:
                problems.append(
                    f"{label}: 无法核对 replay（path={run_path or '(空)'} "
                    f"不存在或 n_agents={n_agents}）；快照可能已过期，请重新跑 monitor.py")
                continue
        else:
            why = check_replay(run_path, n_agents, label)
            if why:
                problems.append(why)
                continue
        m = RUN_ID_RE.match(label)
        runs.append({
            "label": label,
            "arm": m.group(1) if m else None,
            "seed": int(m.group(2)) if m else None,
            "weekly": weekly,
            "path": str(path),
        })

    if problems:
        raise SystemExit("快照校验失败，拒绝出图（避免用不完整数据算臂均值）：\n  - "
                         + "\n  - ".join(problems))
    return runs


def group_by_arm(runs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in runs:
        if r["arm"] is None:
            raise SystemExit(f"{r['label']}: label 不匹配 <arm>_s<seed>，无法归臂")
        out.setdefault(r["arm"], []).append(r)
    return out


def _ref_weeks(by_arm: dict) -> list[dict]:
    """取任一在场臂的首个 run 的 weekly——真实基准三臂同源（外生数据），取谁都一样。

    不能写死 ARMS[0]（random）：臂可能尚未跑完/缺失，写死会 KeyError。
    """
    return by_arm[next(iter(by_arm))][0]["weekly"]


def agg(runs_of_arm: list[dict], getter) -> tuple[list[float], list[float], list[float]]:
    """对同一臂的多个 seed 逐周取 mean / min / max。"""
    n_weeks = len(runs_of_arm[0]["weekly"])
    mean, lo, hi = [], [], []
    for i in range(n_weeks):
        vals = [getter(r["weekly"][i]) for r in runs_of_arm]
        mean.append(statistics.fmean(vals))
        lo.append(min(vals))
        hi.append(max(vals))
    return mean, lo, hi


def agent_share(w: dict, t: str) -> float:
    return w.get(f"supply_share_{t}", 0.0)


def clean_benchmark_share(w: dict, t: str) -> float:
    denom = sum(w["benchmark"][k]["bench_share"] for k in VALID_TYPES)
    return w["benchmark"][t]["bench_share"] / denom if denom else 0.0


def fit_mae(run: dict, *, types: list[str] = VALID_TYPES) -> float:
    """一个 seed 的周×类型平均绝对误差；先逐格取绝对值，避免 seed 间抵消。"""
    errors = [
        abs(agent_share(w, t) - clean_benchmark_share(w, t))
        for w in run["weekly"] for t in types
    ]
    return statistics.fmean(errors)


# ---------------- 绘图工具 ----------------

def _death_line(ax, weeks: list[str]) -> None:
    if DEATH_WEEK in weeks:
        ax.axvline(weeks.index(DEATH_WEEK), color="#D62728", linestyle="--",
                   linewidth=1.4, alpha=0.85, zorder=1)
        ax.annotate(DEATH_LABEL, xy=(weeks.index(DEATH_WEEK), 1.0),
                    xycoords=("data", "axes fraction"),
                    xytext=(6, -4), textcoords="offset points",
                    color="#D62728", fontsize=10, va="top",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def _tidy(ax) -> None:
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=45)


# ---------------- 图 A1：玩梗供给份额（头图） ----------------

def chart_a1_meme_share(by_arm: dict, weeks: list[str], out: Path) -> Path:
    """三臂 Agent-only 玩梗份额 vs 排除噪音后的真实基准。"""
    x = list(range(len(weeks)))
    fig, ax = plt.subplots(figsize=(11, 5.8))
    _death_line(ax, weeks)

    real = [clean_benchmark_share(w, "meme") for w in _ref_weeks(by_arm)]
    ax.plot(x, real, color="#111111", marker="s", markersize=6, linewidth=2.6,
            label="Observed all-platform benchmark (noise excluded)", zorder=5)

    for arm in ARMS:
        if arm not in by_arm:
            continue
        mean, lo, hi = agg(by_arm[arm], lambda w: agent_share(w, "meme"))
        c = ARM_COLOR[arm]
        ax.fill_between(x, lo, hi, color=c, alpha=0.16, linewidth=0, zorder=2)
        ax.plot(x, mean, color=c, marker="o", markersize=5, linewidth=2.4,
                label=f"{ARM_LABEL_EN[arm]} (mean, n={len(by_arm[arm])})", zorder=4)
        y_offsets = {"random": -2, "chronological": 10, "interest": -14}
        ax.annotate(f"{mean[-1]*100:.1f}%", xy=(x[-1], mean[-1]),
                    xytext=(8, y_offsets[arm]), textcoords="offset points",
                    color=c, fontweight="bold", va="center")

    ax.annotate(f"{real[-1]*100:.1f}%", xy=(x[-1], real[-1]),
                xytext=(8, 4), textcoords="offset points",
                color="#111111", fontweight="bold", va="center")

    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([i / 10 for i in range(11)])
    ax.set_ylabel("玩梗供给份额（仅 Agent 自主产出）")
    ax.set_title("玩梗 Agent 自主产出 · 三算法 3-seed 平均 vs 全平台真实基准\n"
                 "注入帖不进入拟合；阴影 = seed 间 min–max（n=3）",
                 fontweight="bold", fontsize=13)
    # 图例下移：4 条图例若贴顶会压住 W13 的去世标注（该标注固定在轴顶部）
    ax.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.82))
    ax.margins(x=0.06, y=0.12)
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- 图 A2：Agent 发帖量按类型（臂 × 面板） ----------------

def chart_a2_agent_supply(by_arm: dict, weeks: list[str], out: Path) -> Path:
    """三臂各自的 Agent 周发帖量堆叠面积（3-seed 平均），用于看「谁先开口」。"""
    present = [a for a in ARMS if a in by_arm]
    x = list(range(len(weeks)))
    fig, axes = plt.subplots(1, len(present), figsize=(5.6 * len(present), 5.2),
                             sharey=True)
    if len(present) == 1:
        axes = [axes]
    agent_types = [t for t in TYPE_ORDER if t != "noise"]

    for ax, arm in zip(axes, present):
        _death_line(ax, weeks)
        series = []
        for t in agent_types:
            mean, _, _ = agg(by_arm[arm], lambda w, t=t: w.get(f"agent_supply_{t}", 0))
            series.append(mean)
        ax.stackplot(x, *series, labels=[TYPE_LABEL_EN[t] for t in agent_types],
                     colors=[TYPE_COLOR[t] for t in agent_types],
                     edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
        ax.set_xticks(x, weeks, rotation=45)
        ax.set_title(f"{ARM_LABEL[arm]}（n={len(by_arm[arm])}）", fontweight="bold", fontsize=12)
        ax.set_ylim(*BASELINE_SUPPLY_YLIM)
        ax.set_yticks(range(BASELINE_SUPPLY_YLIM[0], BASELINE_SUPPLY_YLIM[1] + 1, 10))
        ax.margins(y=0.05)
        _tidy(ax)
    axes[0].set_ylabel("Agent 发帖数 / 周（3-seed 平均）")
    axes[-1].legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle("Agent 周发帖量 · 按内容类型（堆叠面积 · 3-seed 平均 · 不含注入帖）",
                 fontweight="bold", fontsize=13)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- 图 A3：玩梗型 Agent 发言率 ----------------

def chart_a3_meme_speaking(by_arm: dict, weeks: list[str], out: Path) -> Path:
    """玩梗型 Agent 发言率：三臂对比，看起爆时点与幅度是否被算法改变。"""
    x = list(range(len(weeks)))
    fig, ax = plt.subplots(figsize=(11, 5.4))
    _death_line(ax, weeks)
    for arm in ARMS:
        if arm not in by_arm:
            continue
        mean, lo, hi = agg(by_arm[arm], lambda w: w["agent_agg"]["meme"]["spoke_rate"])
        c = ARM_COLOR[arm]
        ax.fill_between(x, lo, hi, color=c, alpha=0.16, linewidth=0, zorder=2)
        ax.plot(x, mean, color=c, marker="o", markersize=5, linewidth=2.4,
                label=f"{ARM_LABEL_EN[arm]} (mean, n={len(by_arm[arm])})", zorder=4)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylim(0, 1.0)
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("玩梗型 Agent 发言率")
    ax.set_title("玩梗型 Agent 发言率 · 三臂 3-seed 平均\n阴影 = seed 间 min–max 包络",
                 fontweight="bold", fontsize=13)
    # 同 A1：图例下移避开 W13 去世标注
    ax.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.88))
    ax.margins(x=0.06, y=0.12)
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- 图 A4：推荐曝光中的玩梗可见度 ----------------

def chart_a4_meme_exposure(by_arm: dict, weeks: list[str], out: Path) -> Path:
    """直接展示算法输出的玩梗曝光份额；不伪装成候选池放大量。"""
    x = list(range(len(weeks)))
    fig, ax = plt.subplots(figsize=(11, 5.6))
    _death_line(ax, weeks)
    real = [w["benchmark"]["meme"]["bench_share"] for w in _ref_weeks(by_arm)]
    ax.plot(x, real, color="#111111", marker="s", markersize=5, linewidth=2.2,
            linestyle="--", label="Observed content benchmark (reference only)", zorder=4)
    for arm in ARMS:
        if arm not in by_arm:
            continue
        mean, lo, hi = agg(by_arm[arm], lambda w: w["exposure_share_meme"])
        c = ARM_COLOR[arm]
        ax.fill_between(x, lo, hi, color=c, alpha=0.14, linewidth=0, zorder=2)
        ax.plot(x, mean, color=c, marker="o", markersize=5, linewidth=2.4,
                label=f"{ARM_LABEL_EN[arm]} exposure", zorder=3)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylim(0, 0.8)
    ax.set_yticks([i / 10 for i in range(9)])
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("推荐曝光中的玩梗份额")
    ax.set_title("推荐算法输出的玩梗可见度（3-seed 平均）\n"
                 "真实线是内容构成参照，并非真实曝光日志", fontweight="bold", fontsize=13)
    ax.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.86))
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- 图 A5：五类整体构成拟合误差 ----------------

def chart_a5_fit_mae(by_arm: dict, out: Path) -> Path:
    """五类有效内容的周×类型 MAE；柱为 seed 均值，点为每个 seed。"""
    present = [a for a in ARMS if a in by_arm]
    xs = list(range(len(present)))
    values = {a: [fit_mae(r) * 100 for r in by_arm[a]] for a in present}
    means = [statistics.fmean(values[a]) for a in present]
    lo = [m - min(values[a]) for m, a in zip(means, present)]
    hi = [max(values[a]) - m for m, a in zip(means, present)]

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.bar(xs, means, width=0.58, color=[ARM_COLOR[a] for a in present], alpha=0.88,
           yerr=[lo, hi], capsize=6, edgecolor="white", linewidth=0.8, zorder=2)
    jitters = [-0.08, 0.0, 0.08]
    for x, arm in zip(xs, present):
        for j, v in zip(jitters, values[arm]):
            ax.scatter(x + j, v, s=34, color="#222222", edgecolor="white",
                       linewidth=0.5, zorder=4)
        ax.text(x, max(values[arm]) + 0.35, f"{statistics.fmean(values[arm]):.1f} pp",
                ha="center", va="bottom", fontweight="bold", color=ARM_COLOR[arm])
    ax.set_xticks(xs, [ARM_LABEL_EN[a] for a in present])
    ax.set_ylim(0, max(13.0, max(max(v) for v in values.values()) + 1.5))
    ax.set_ylabel("五类构成平均绝对误差（百分点，越低越好）")
    ax.set_title("兴趣推荐的整体五类内容构成误差最低\n"
                 "柱 = 3-seed 均值；点 = 各 seed；误差线 = min–max",
                 fontweight="bold", fontsize=13)
    ax.yaxis.grid(True, color="#E2E8F0", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- CSV ----------------

def export_csv(by_arm: dict, weeks: list[str], data_dir: Path) -> list[Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    def write(name: str, header: list[str], rows: list[list]) -> None:
        p = data_dir / name
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)
        paths.append(p)

    # 臂级周度汇总：每臂每指标 mean/sd/min/max，便于复核与二次统计
    metrics = {
        "meme_share_agent_only": lambda w: agent_share(w, "meme"),
        "meme_share_combined_descriptive": lambda w: w["supply_share_all_meme"],
        "meme_exposure_share": lambda w: w["exposure_share_meme"],
        "agent_supply": lambda w: w["agent_supply"],
        "total_supply": lambda w: w["total_supply"],
        "meme_speaking_rate": lambda w: w["agent_agg"]["meme"]["spoke_rate"],
        "meme_env_gain": lambda w: w["meme_env_gain"],
    }
    rows = []
    for arm in ARMS:
        if arm not in by_arm:
            continue
        for i, wk in enumerate(weeks):
            for name, getter in metrics.items():
                vals = [getter(r["weekly"][i]) for r in by_arm[arm]]
                rows.append([arm, wk, name, len(vals), statistics.fmean(vals),
                             statistics.stdev(vals) if len(vals) > 1 else 0.0,
                             min(vals), max(vals)])
    write("arm_weekly_summary.csv",
          ["arm", "week", "metric", "n_seeds", "mean", "sd", "min", "max"], rows)

    # 每类型：把 Agent 自主产出、曝光和环境混合供给分列，禁止再把三者混称为拟合。
    rows = []
    for arm in ARMS:
        if arm not in by_arm:
            continue
        for i, wk in enumerate(weeks):
            for t in TYPE_ORDER:
                a = [getattr_supply(r["weekly"][i], t) for r in by_arm[arm]]
                agent_s = [agent_share(r["weekly"][i], t) if t != "noise" else 0.0
                           for r in by_arm[arm]]
                exposure_s = [r["weekly"][i][f"exposure_share_{t}"] for r in by_arm[arm]]
                combined_s = [r["weekly"][i][f"supply_share_all_{t}"] for r in by_arm[arm]]
                rows.append([arm, wk, t, statistics.fmean(a), statistics.fmean(agent_s),
                             statistics.fmean(exposure_s), statistics.fmean(combined_s)])
    write("arm_weekly_by_type.csv",
          ["arm", "week", "type", "mean_agent_supply", "mean_agent_supply_share",
           "mean_exposure_share", "mean_combined_supply_share_descriptive"], rows)

    # 真实基准（各臂相同，单列一次）
    ref = _ref_weeks(by_arm)
    write("benchmark.csv",
          ["week", "type", "bench_share"],
          [[wk["week"], t, wk["benchmark"][t]["bench_share"]]
           for wk in ref for t in TYPE_ORDER if t in wk.get("benchmark", {})])

    # 每 seed 的拟合误差，供 A5 和后续统计复核。
    fit_rows = []
    for arm in ARMS:
        if arm not in by_arm:
            continue
        for r in by_arm[arm]:
            fit_rows.append([arm, r["seed"], "agent_only_5type_clean", fit_mae(r)])
            fit_rows.append([arm, r["seed"], "agent_only_meme_clean", fit_mae(r, types=["meme"])])
    write("arm_fit_summary.csv", ["arm", "seed", "metric_scope", "mae"], fit_rows)
    return paths


def getattr_supply(w: dict, t: str) -> float:
    return w.get(f"agent_supply_{t}", 0)


# ---------------- 主流程 ----------------

def main() -> int:
    ap = argparse.ArgumentParser(description="3 臂 × 3 seeds → 臂级 3-seed 平均图")
    ap.add_argument("--status", action="append", default=[], help="显式指定 status.json（可重复）")
    ap.add_argument("--label", action="append", default=[], help="与 --status 顺序配对的标签")
    ap.add_argument("--no-charts", action="store_true", help="只出 CSV")
    ap.add_argument("--no-csv", action="store_true", help="只出图")
    ap.add_argument("--dry-run", action="store_true",
                    help="允许标签不是正式 run id（仅用于验证脚本本身）")
    ap.add_argument("--charts-dir", default=str(CHARTS_DIR),
                    help="图输出目录（干跑时指向临时目录，避免污染正式产物）")
    ap.add_argument("--data-dir", default=str(DATA_DIR),
                    help="CSV 输出目录（干跑时指向临时目录，避免污染正式产物）")
    args = ap.parse_args()

    explicit: list[tuple[Path, str]] = []
    if args.status:
        labels = args.label or []
        if labels and len(labels) != len(args.status):
            raise SystemExit("--status 与 --label 数量不一致")
        for i, s in enumerate(args.status):
            p = Path(s)
            explicit.append((p, labels[i] if i < len(labels) else p.parent.name))

    runs = load_runs(explicit, strict=not args.dry_run)
    if not args.dry_run:
        for r in runs:
            if r["arm"] is None:
                raise SystemExit(f"{r['label']}: 非正式 run id；如确为干跑请加 --dry-run")
    by_arm = group_by_arm(runs)

    print(f"载入 {len(runs)} 个 run：")
    for arm in ARMS:
        if arm in by_arm:
            seeds = sorted(r["seed"] for r in by_arm[arm] if r["seed"] is not None)
            print(f"  {arm:14s} n={len(by_arm[arm])}  seeds={seeds}")
        else:
            print(f"  {arm:14s} 缺失")

    weeks = [w["week"] for w in runs[0]["weekly"]]

    charts_dir = Path(args.charts_dir)
    if not args.no_csv:
        for p in export_csv(by_arm, weeks, Path(args.data_dir)):
            print(f"✓ CSV {p}")

    if not args.no_charts:
        charts_dir.mkdir(parents=True, exist_ok=True)
        for fn, name in (
            (chart_a1_meme_share, "A1_meme_share_arms_vs_real.png"),
            (chart_a2_agent_supply, "A2_agent_supply_by_type_arms.png"),
            (chart_a3_meme_speaking, "A3_meme_speaking_rate_arms.png"),
            (chart_a4_meme_exposure, "A4_meme_exposure_arms.png"),
        ):
            out = charts_dir / f"ARM_{name}"
            fn(by_arm, weeks, out)
            print(f"✓ 图  {out}")
        out = charts_dir / "ARM_A5_five_type_fit_mae.png"
        chart_a5_fit_mae(by_arm, out)
        print(f"✓ 图  {out}")

    # 图旁判据：臂间差 vs seed 内噪声，直接支撑「差异是否真实」
    print("\n臂间对比（Agent-only；真实 benchmark 排除 noise 后重归一化）：")
    for arm in ARMS:
        if arm not in by_arm:
            continue
        mean, _, _ = agg(by_arm[arm], lambda w: agent_share(w, "meme"))
        real = [clean_benchmark_share(w, "meme") for w in by_arm[arm][0]["weekly"]]
        d = [abs(a - b) for a, b in zip(mean, real)]
        print(f"  {arm:14s} 均值绝对差={statistics.fmean(d):.4f}  最大={max(d):.4f} "
              f"@ {weeks[d.index(max(d))]}  W22={mean[-1]:.4f} vs 真实 {real[-1]:.4f}  "
              f"五类MAE(seed均值)={statistics.fmean(fit_mae(r) for r in by_arm[arm]):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
