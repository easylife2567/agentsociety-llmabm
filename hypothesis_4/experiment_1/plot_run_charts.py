#!/usr/bin/env python3
"""plot_run_charts: 从 monitor 快照（status.json）绘制 CurationDynamics 关键周度折线图。

图表样式对齐仓库根目录《图表解读.docx》的真实数据分析图（结论式标题、
去世事件红虚线、末端终值标注、%刻度），用于模拟 run 的同等解读：

    chart1  玩梗供给份额 — 模拟 vs 真实基准   （对应 docx 图1 双线对比）
    chart2  周度供给量 — 注入+Agent 产出堆叠柱（对应 docx 图2 总量柱状）
    chart3  各内容类型供给量堆叠面积          （对应 docx 图3 绝对数量堆叠）
    chart3b 各内容类型 Agent 发帖量堆叠面积    （图3 的 Agent 侧变体，不含注入帖）
    chart4  玩梗型 Agent 发言率 + 涌现增益 G  （对应 docx 图4 玩梗率，副轴加机制量）

同时把周度指标导出为 CSV（data/<run_id>/weekly_*.csv），作为 run/（已 gitignore）
之外的持久数据副本；按 run 分目录，避免多 run 批跑时互相覆盖。

出图分桶（用户 2026-09-13 要求：烟测 / 预测 / 正式实验分开放）：
    默认写 charts/formal/（正式 9-run 批跑）；烟测/预跑单 run 须显式传
    `--charts-dir charts/smoke`。预测图不归本脚本（见 proxy_predict*.py）。

用法：
    $PYTHON_PATH hypothesis_4/experiment_1/plot_run_charts.py \
        --status hypothesis_4/experiment_1/monitor/<run_id>/status.json        # 正式 run（→ charts/formal/）
    $PYTHON_PATH hypothesis_4/experiment_1/plot_run_charts.py \
        --status hypothesis_4/experiment_1/monitor/<run_id>/status.json \
        --charts-dir hypothesis_4/experiment_1/charts/smoke                    # 烟测 run
    $PYTHON_PATH hypothesis_4/experiment_1/plot_run_charts.py --no-charts     # 只导出 CSV
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
# 出图分桶（用户 2026-09-13 要求：烟测 / 预测 / 正式实验分开放）：
#   charts/formal/  正式 9-run 批跑的逐 run 图（本脚本主用途）
#   charts/smoke/   烟测与预跑单 run —— 须显式传 --charts-dir charts/smoke
# 本脚本不产出预测图（那是 proxy_predict*.py 的职责，写 charts/prediction/）。
CHARTS_DIR = SCRIPT_DIR / "charts" / "formal"


def _rel(p: Path) -> str:
    """尽量相对 SCRIPT_DIR 显示；树外路径（--charts-dir 指到项目外）原样返回。"""
    try:
        return str(Path(p).relative_to(SCRIPT_DIR))
    except ValueError:
        return str(p)


def _resolve_dir(d: str) -> Path:
    """--charts-dir 解析：相对路径按 SCRIPT_DIR 解释（与帮助文本 `charts/smoke` 一致），
    不按 CWD——否则从别处调用会静默写到意外位置。"""
    p = Path(d)
    return p if p.is_absolute() else (SCRIPT_DIR / p)

# ---------------- 样式（对齐《图表解读.docx》） ----------------

plt.rcParams.update({
    "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "Heiti TC"],
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
})

# 事件周：W13（去世 2026-03-24，官方讣告置顶周）
DEATH_WEEK = "2026-W13"
DEATH_LABEL = "去世 3-24 (W13)"

TYPE_ORDER = ["meme", "mourning", "education", "marketing", "other", "noise"]
TYPE_LABEL = {"meme": "玩梗", "mourning": "悼念", "education": "教育",
              "marketing": "营销", "other": "其他", "noise": "噪音"}
# 图3 堆叠面积配色（对齐 docx image3：悼念蓝 / 玩梗橙 / 教育绿 / 营销黄 / 其他浅蓝 / 噪音灰紫）
TYPE_COLOR = {"mourning": "#4C72B0", "meme": "#DD8452", "education": "#55A868",
              "marketing": "#CCB974", "other": "#64B5CD", "noise": "#B07AA1"}


def _death_line(ax, weeks: list[str], label: str = DEATH_LABEL) -> None:
    if DEATH_WEEK in weeks:
        ax.axvline(weeks.index(DEATH_WEEK), color="#D62728", linestyle="--",
                   linewidth=1.4, alpha=0.85, zorder=1)
        # 标注固定在轴顶部右侧（x 用数据坐标、y 用轴分数，避免被 ylim 裁剪或与刻度重叠）；
        # 白底防止压在色块/图例上
        ax.annotate(label, xy=(weeks.index(DEATH_WEEK), 1.0),
                    xycoords=("data", "axes fraction"),
                    xytext=(6, -4), textcoords="offset points",
                    color="#D62728", fontsize=10, va="top",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def _tidy(ax) -> None:
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=45)


# ---------------- CSV 导出 ----------------

def export_csv(weekly: list[dict], out_dir: Path) -> list[Path]:
    """把单 run 的周度表导出到 out_dir。

    ⚠ out_dir 必须是**按 run 分目录**的（见 main 里 DATA_DIR / run_id）。早期版本
    直接写 data/ 下的固定文件名（weekly_supply.csv 等），9 个 run 顺序执行时每个
    run 都会覆盖前一个，最终 data/ 里只剩最后一个 run 的数据而无任何报错——
    属静默数据污染。改为 data/<run_id>/weekly_*.csv 后互不干扰。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    def write(name: str, header: list[str], rows: list[list]) -> None:
        p = out_dir / name
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        paths.append(p)

    # 表A 供给与涌现环境
    write("weekly_supply.csv",
          ["week", "meme_env_stock", "meme_env_flow", "meme_env_flow_world",
           "abundance_B", "emptiness_S", "gain_G", "total_supply", "agent_supply",
           "injected_count", "official_posts_count"]
          + [f"supply_share_all_{t}" for t in TYPE_ORDER],
          [[w["week"], w["meme_env_stock"], w["meme_env_flow"], w["meme_env_flow_world"],
            w["meme_env_abundance"], w["meme_env_emptiness"], w["meme_env_gain"],
            w["total_supply"], w["agent_supply"], w["injected_count"], w["official_posts_count"]]
           + [w[f"supply_share_all_{t}"] for t in TYPE_ORDER] for w in weekly])

    # 表B 曝光
    write("weekly_exposure.csv",
          ["week", "total_exposures"]
          + [f"exposure_{t}" for t in TYPE_ORDER]
          + [f"exposure_share_{t}" for t in TYPE_ORDER],
          [[w["week"], w["total_exposures"]]
           + [w[f"exposure_{t}"] for t in TYPE_ORDER]
           + [w[f"exposure_share_{t}"] for t in TYPE_ORDER] for w in weekly])

    # 表C Agent 行为（长表）
    write("weekly_agent_behavior.csv",
          ["week", "type", "n_agents", "spoke_rate", "mismatch_rate",
           "mean_exposure_own", "mean_climate_own", "mean_feed_slots"],
          [[w["week"], t, a["n_agents"], a["spoke_rate"], a["mismatch_rate"],
            a["mean_exposure_own"], a["mean_climate_own"], a["mean_feed_slots"]]
           for w in weekly for t, a in sorted(w["agent_agg"].items())])

    # 表D 机制透视（长表）
    write("weekly_mechanism.csv",
          ["week", "type", "n_decisions", "n_speak", "n_posted", "mean_u",
           "mean_threshold", "mean_benefit", "mean_env_gain", "mean_env_multiplier"],
          [[w["week"], t, m["n_decisions"], m["n_speak"], m["n_posted"], m["mean_u"],
            m["mean_threshold"], m["mean_benefit"], m["mean_env_gain"], m["mean_env_multiplier"]]
           for w in weekly for t, m in sorted(w["mech_agg"].items())])

    # 模拟 vs 真实基准
    write("weekly_benchmark.csv",
          ["week", "type", "sim_share_all", "bench_share", "delta"],
          [[w["week"], t, w[f"supply_share_all_{t}"],
            w["benchmark"][t]["bench_share"], w["benchmark"][t]["delta"]]
           for w in weekly for t in TYPE_ORDER if t in w.get("benchmark", {})])

    # 策展偏差
    write("weekly_bias.csv",
          ["week"] + [f"bias_{t}" for t in TYPE_ORDER],
          [[w["week"]] + [w["bias"][t] for t in TYPE_ORDER] for w in weekly])

    return paths


# ---------------- 图表 ----------------

def chart1_meme_share(weekly: list[dict], run_id: str, out: Path) -> Path:
    """玩梗 combined 供给份额：模拟 vs 真实基准（对应 docx 图1 双平台对比）。"""
    weeks = [w["week"] for w in weekly]
    sim = [w["supply_share_all_meme"] for w in weekly]
    real = [w["benchmark"]["meme"]["bench_share"] for w in weekly]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    _death_line(ax, weeks)
    ax.plot(weeks, real, color="#1F77B4", marker="s", markersize=5, linewidth=2,
            label="真实基准（抖音）", zorder=3)
    ax.plot(weeks, sim, color="#D95F02", marker="o", markersize=5, linewidth=2.4,
            label=f"模拟（{run_id}）", zorder=4)
    ax.annotate(f"{real[-1]*100:.1f}%", xy=(len(weeks) - 1, real[-1]),
                xytext=(0, 8), textcoords="offset points", ha="center",
                color="#1F77B4", fontweight="bold")
    ax.annotate(f"{sim[-1]*100:.1f}%", xy=(len(weeks) - 1, sim[-1]),
                xytext=(0, -14), textcoords="offset points", ha="center",
                color="#D95F02", fontweight="bold")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("玩梗供给份额（combined 口径）")
    ax.set_title("玩梗份额 — 模拟复现「事件压抑 → W19+ 涌现浪潮」形态", fontweight="bold", fontsize=13)
    ax.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.90))
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def chart2_supply_volume(weekly: list[dict], run_id: str, out: Path) -> Path:
    """周度供给量堆叠柱：注入 + Agent 产出（对应 docx 图2 总量柱状）。"""
    weeks = [w["week"] for w in weekly]
    injected = [w["injected_count"] for w in weekly]
    agent = [w["agent_supply"] for w in weekly]
    totals = [i + a for i, a in zip(injected, agent)]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    _death_line(ax, weeks)
    ax.bar(weeks, injected, color="#9ECBE8", edgecolor="white", label="注入（真实数据）", zorder=2)
    ax.bar(weeks, agent, bottom=injected, color="#2166AC", edgecolor="white",
           label="Agent 产出", zorder=2)
    for i, tv in enumerate(totals):
        ax.annotate(str(tv), xy=(i, tv), xytext=(0, 4), textcoords="offset points",
                    ha="center", fontsize=9, color="#333333")
    ax.set_ylabel("周供给量（帖）")
    ax.set_title(f"周度供给量 — 事件尖峰与玩梗第二波（{run_id}，arena 口径）",
                 fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", frameon=False)
    ax.margins(y=0.12)
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def chart3_stacked_area(weekly: list[dict], run_id: str, out: Path) -> Path:
    """各内容类型供给绝对量堆叠面积（对应 docx 图3）。绝对量 = 注入 + Agent 产出。"""
    weeks = [w["week"] for w in weekly]
    x = list(range(len(weeks)))
    # noise 仅存在于注入侧（agent 不产噪音帖），agent 侧缺键取 0
    series = {t: [w.get(f"agent_supply_{t}", 0) + w.get(f"injected_{t}", 0) for w in weekly]
              for t in TYPE_ORDER}

    fig, ax = plt.subplots(figsize=(10, 5.4))
    _death_line(ax, weeks)
    ax.stackplot(x, *[series[t] for t in TYPE_ORDER],
                 labels=[TYPE_LABEL[t] for t in TYPE_ORDER],
                 colors=[TYPE_COLOR[t] for t in TYPE_ORDER],
                 edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("帖数（绝对数量）")
    ax.set_title(f"各内容类型供给量变化（堆叠面积 · 绝对数量，{run_id}）",
                 fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.margins(y=0.05)
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def chart3b_agent_supply_stacked_area(weekly: list[dict], run_id: str, out: Path) -> Path:
    """各内容类型 Agent 发帖量堆叠面积（图3 的 Agent 侧变体，不含注入帖）。

    noise 仅存在于注入侧（Agent 不产噪音帖），故序列只含 5 类。
    """
    weeks = [w["week"] for w in weekly]
    x = list(range(len(weeks)))
    agent_types = [t for t in TYPE_ORDER if t != "noise"]
    series = {t: [w.get(f"agent_supply_{t}", 0) for w in weekly] for t in agent_types}

    fig, ax = plt.subplots(figsize=(10, 5.4))
    _death_line(ax, weeks)
    ax.stackplot(x, *[series[t] for t in agent_types],
                 labels=[TYPE_LABEL[t] for t in agent_types],
                 colors=[TYPE_COLOR[t] for t in agent_types],
                 edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
    ax.set_xticks(x, weeks, rotation=45)
    ax.set_ylabel("Agent 发帖数（帖）")
    ax.set_title(f"Agent 发帖量变化（堆叠面积 · 仅 Agent 产出 · 不含注入帖，{run_id}）",
                 fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.margins(y=0.05)
    _tidy(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def chart4_meme_speaking(weekly: list[dict], run_id: str, out: Path) -> Path:
    """玩梗型 Agent 发言率（绿线填充）+ 涌现增益 G 副轴（对应 docx 图4 + 机制量）。"""
    weeks = [w["week"] for w in weekly]
    x = list(range(len(weeks)))
    rate = [w["agent_agg"]["meme"]["spoke_rate"] for w in weekly]
    gain = [w["meme_env_gain"] for w in weekly]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    _death_line(ax, weeks)
    line_rate, = ax.plot(x, rate, color="#2E9E6B", marker="o", markersize=5,
                         linewidth=2.4, zorder=4, label="玩梗型 Agent 发言率")
    ax.fill_between(x, rate, color="#2E9E6B", alpha=0.15, zorder=2)
    ax.annotate(f"{rate[-1]*100:.0f}%", xy=(len(weeks) - 1, rate[-1]),
                xytext=(0, 8), textcoords="offset points", ha="center",
                color="#2E9E6B", fontweight="bold")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("玩梗型 Agent 发言率")
    ax.set_ylim(-0.05, 1.12)

    ax2 = ax.twinx()
    line_gain, = ax2.plot(x, gain, color="#8172B3", linestyle=":", marker="",
                          linewidth=1.8, zorder=3, label="涌现增益 G（右轴）")
    ax2.set_ylabel("涌现增益 G = clamp(B·S, 0.2, 3.0)", color="#8172B3")
    ax2.tick_params(axis="y", colors="#8172B3")
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color("#8172B3")
    ax2.set_ylim(0, 3.4)
    ax2.grid(False)

    ax.legend([line_rate, line_gain], [line_rate.get_label(), line_gain.get_label()],
              loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.86))
    # 2026-09-12：原标题"涌现增益 G 释放后 W19 起爆"把跳变归因给 G，已被诊断推翻
    # （W18/W19 的 G 同为 3.0，跳变来自 D 的输入退化）；改中性描述，结论由数据自证。
    ax.set_title(f"玩梗型 Agent 发言率与涌现增益 G（{run_id}）",
                 fontweight="bold", fontsize=13)
    ax.set_xticks(x, weeks, rotation=45)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# ---------------- 主流程 ----------------

def main() -> int:
    ap = argparse.ArgumentParser(description="CurationDynamics 周度关键图绘制（对齐图表解读.docx 样式）")
    ap.add_argument("--status", default=str(SCRIPT_DIR / "monitor" / "run" / "status.json"),
                    help="monitor 快照 status.json（默认烟测 monitor/run/）")
    ap.add_argument("--run-id", default=None,
                    help="覆盖 run_id（默认取 status.json 内值，再退回快照目录名）")
    ap.add_argument("--no-charts", action="store_true", help="只导出 CSV 不画图")
    ap.add_argument("--no-csv", action="store_true", help="只画图不导出 CSV")
    ap.add_argument("--charts-dir", default=str(CHARTS_DIR),
                    help=f"出图目录（默认 {CHARTS_DIR.relative_to(SCRIPT_DIR)}；"
                         f"烟测/预跑单 run 请传 charts/smoke）")
    args = ap.parse_args()
    charts_dir = _resolve_dir(args.charts_dir)

    status_path = Path(args.status)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    run_id = args.run_id or data.get("run_id") or status_path.parent.name
    weekly = data["weekly"]
    print(f"run_id={run_id}  weeks={len(weekly)}  source={status_path}")

    if not args.no_csv:
        for p in export_csv(weekly, DATA_DIR / run_id):
            print(f"✓ CSV {p.relative_to(SCRIPT_DIR)}")

    if not args.no_charts:
        charts_dir.mkdir(parents=True, exist_ok=True)
        for fn, name in (
            (chart1_meme_share, "chart1_meme_share_sim_vs_real.png"),
            (chart2_supply_volume, "chart2_weekly_supply_volume.png"),
            (chart3_stacked_area, "chart3_supply_stacked_area.png"),
            (chart3b_agent_supply_stacked_area, "chart3b_agent_supply_stacked_area.png"),
            (chart4_meme_speaking, "chart4_meme_speaking_rate.png"),
        ):
            out = charts_dir / f"{run_id}__{name}"
            fn(weekly, run_id, out)
            print(f"✓ 图  {_rel(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())