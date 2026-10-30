"""沿用 chart3b 五类堆叠样式，绘制已完成两臂 seed0 的实际周发帖量。

只读本 pilot 的已验收周表和原始结果快照；不启动引擎、不调用模型。
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_pilot import verified_rows

PILOT = Path(__file__).resolve().parent
OUT = PILOT / "agent_supply"
ARMS = ("random", "interest")
TYPES = ("meme", "mourning", "education", "marketing", "other")
LABELS = ("Meme", "Mourning", "Education", "Marketing", "Other")
# 与用户先前指定的 chart3b 模板保持顺序、配色和绝对数量比例尺一致。
COLORS = ("#DD8452", "#4C72B0", "#55A868", "#CCB974", "#64B5CD")
WEEKS = tuple(f"2026-W{w}" for w in range(12, 23))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    summary_path = PILOT / "analysis/summary.json"
    csv_path = PILOT / "analysis/weekly.csv"
    selection_path = PILOT / "selected_revision.json"
    summary = json.loads(summary_path.read_text())
    selection = json.loads(selection_path.read_text())
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    grouped = verified_rows(summary, rows, selection)
    sources = {str(p.relative_to(PILOT)): digest(p) for p in
               (summary_path, csv_path, selection_path, Path(__file__), PILOT / "plot_pilot.py")}
    plot_rows, checks = [], {}
    for arm in ARMS:
        actual = Counter()
        run = PILOT / "results" / f"hourly_return_pilot_{arm}_s0"
        files = sorted((run / "agents").glob("*/AGENT.json"))
        if len(files) != 100:
            raise ValueError(f"{arm}: 原始快照未覆盖100名Agent")
        # 独立读取持久化的 posted，逐周逐类核对，避免将发帖意图当成功发布。
        for path in files:
            agent = json.loads(path.read_text())
            kind = agent["profile"]["agent_type"]
            records = agent["decision_log"]
            if kind not in TYPES or sorted(r["week"] for r in records) != list(WEEKS):
                raise ValueError(f"{arm}: 作者类型或11周决策不完整")
            for record in records:
                if record.get("posted"):
                    actual[(record["week"], kind)] += 1
            expected_hash = summary["source_sha256"][str(
                Path(next(r["run_dir"] for r in summary["runs"] if r["algorithm"] == arm))
                / path.relative_to(run))]
            if digest(path) != expected_hash:
                raise ValueError(f"{path}: 原始快照与验收来源哈希不一致")
            sources[str(path.relative_to(PILOT))] = expected_hash
        for row in grouped[arm]:
            counts = {kind: int(row[f"posted_{kind}_authors"]) for kind in TYPES}
            total = int(row["posted_total"])
            if any(counts[k] != actual[(row["week"], k)] for k in TYPES):
                raise ValueError(f"{arm}/{row['week']}: 周表与Agent实际发布记录不一致")
            if sum(counts.values()) != total or not 0 <= total <= 80:
                raise ValueError("分类数量不守恒，或超出既有0–80纵轴，不能裁剪")
            plot_rows.append({"algorithm": arm, "seed": 0, "week": row["week"],
                              **counts, "total": total})
        checks[arm] = {"agents": len(files), "decisions": 1100, "weeks": 11,
                       "posts": sum(actual.values()),
                       "late_meme_posts": sum(actual[(w, "meme")] for w in WEEKS[-4:]),
                       "weekly_by_type_matches_raw_posted": True}

    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({
        "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"],
        "axes.unicode_minus": False, "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.edgecolor": "#444444", "axes.grid": True, "grid.color": "#DDDDDD",
        "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "font.size": 12, "svg.fonttype": "none",
    })
    fig, axes = plt.subplots(1, 2, figsize=(18, 6.8), sharey=True)
    fig.subplots_adjust(left=0.065, right=0.99, bottom=0.20, top=0.78, wspace=0.08)
    handles = None
    names = {"random": "随机推荐 / Random", "interest": "兴趣推荐 / Interest"}
    for ax, arm in zip(axes, ARMS):
        values = [r for r in plot_rows if r["algorithm"] == arm]
        handles = ax.stackplot(range(11), *[[r[k] for r in values] for k in TYPES],
                               colors=COLORS, labels=LABELS, edgecolor="white",
                               linewidth=0.6, alpha=0.92, zorder=2)
        ax.axvline(1, color="#D62728", linestyle="--", linewidth=1.4, alpha=0.85, zorder=3)
        ax.annotate("去世 3-24 (W13)", xy=(1, 1), xycoords=("data", "axes fraction"),
                    xytext=(6, -6), textcoords="offset points", color="#D62728", va="top",
                    fontsize=11, bbox={"fc": "white", "ec": "none", "alpha": 0.85, "pad": 2})
        ax.set_xticks(range(11), WEEKS, rotation=45, ha="right")
        ax.set_ylim(0, 80)
        ax.set_yticks(range(0, 81, 10))
        ax.set_axisbelow(True)
        ax.set_title(f"{names[arm]}  ·  seed0  ·  全窗 {checks[arm]['posts']} 帖", loc="left", pad=12)
        ax.set_xlabel("模拟周次")
    axes[0].set_ylabel("Agent 发帖数（帖）")
    fig.suptitle("小时回流测试：Agent 每周发帖量", fontsize=20, fontweight="bold", y=0.97)
    fig.legend(handles, LABELS, loc="upper center", bbox_to_anchor=(0.53, 0.91),
               ncol=5, frameon=False, fontsize=12)
    fig.text(0.5, 0.03, "五类固定作者的成功发帖数；不含外部注入、官方帖和历史池。单 seed 初步观察，非多种子均值。",
             ha="center", fontsize=11, color="#555555")
    outputs = []
    for ext in ("png", "svg"):
        path = OUT / f"agent_supply_comparison.{ext}"
        fig.savefig(path, dpi=300, metadata={"Creator": "AgentSociety hourly-return pilot"})
        outputs.append(path)
    plt.close(fig)
    export = OUT / "weekly_agent_supply.csv"
    with export.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plot_rows[0]))
        writer.writeheader()
        writer.writerows(plot_rows)
    outputs.append(export)
    manifest = {
        "scope": "random/interest, seed0, W12–W22; chronological excluded",
        "measure": "successful posted by fixed author type; exclude external/official/history",
        "style_reference": "hypothesis_4/experiment_1/plot_run_charts.py::chart3b_agent_supply_stacked_area",
        "style": {"type_order": TYPES, "legend": LABELS, "colors": COLORS,
                  "shared_y_axis": [0, 80], "y_tick": 10, "event_week": "2026-W13"},
        "matplotlib": matplotlib.__version__, "validation": checks,
        "source_sha256": sources,
        "outputs_sha256": {p.name: digest(p) for p in outputs},
        "limitations": "single-seed description; author type is not independent content coding; no significance claim",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"outputs": [str(p) for p in outputs], "validation": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
