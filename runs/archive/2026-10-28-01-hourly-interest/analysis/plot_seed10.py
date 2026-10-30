"""绘制三臂各 10 seed 的实际发帖均值与逐 seed DTW 稳定性。

只读已完成的离线分析表；不启动仿真，不调用模型。时序臂是历史完整
结果复用，random/interest 的 seed0 是已看过结果的先导测试。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


BASE = Path(__file__).resolve().parent
ARMS = ("random", "chronological", "interest")
SEEDS = tuple(range(10))
WEEKS = tuple(f"2026-W{week}" for week in range(12, 23))
TYPES = ("meme", "mourning", "education", "marketing", "other")
TYPE_LABELS = ("Meme", "Mourning", "Education", "Marketing", "Other")
TYPE_COLORS = ("#DD8452", "#4C72B0", "#55A868", "#CCB974", "#64B5CD")
ARM_LABELS = {"random": "Random", "chronological": "Chronological", "interest": "Interest"}
ARM_TITLES = {"random": "随机推荐", "chronological": "时序推荐（历史结果复用）", "interest": "兴趣推荐"}
ARM_COLORS = {"random": "#737373", "chronological": "#0F4D92", "interest": "#B64342"}
# 每个 seed 的位置固定，重算时不引入随机抖动。
JITTER = (-0.18, -0.14, -0.10, -0.06, -0.02, 0.02, 0.06, 0.10, 0.14, 0.18)
EXPECTED_METHOD = {
    "primary_share_field": "shanghai_clean_share",
    "secondary_share_field": "utc_clean_share",
    "window_weeks": 1,
    "local_distance": "Euclidean five-type shares",
    "z_normalization": False,
    "optimization": "minimum cumulative cost; diagonal/up/left tie order",
    "score": "cumulative distance / selected path length *100",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{label}: 必须是有限的非负数")
    return result


def count(value: object, label: str) -> int:
    result = number(value, label)
    if not result.is_integer():
        raise ValueError(f"{label}: 必须是整数")
    return int(result)


def same(actual: object, expected: float, label: str) -> None:
    if not math.isclose(number(actual, label), expected, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"{label}: {actual} 与独立复算值 {expected} 不一致")


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not required.issubset(fields):
            raise ValueError(f"{path}: CSV 字段缺失或重复")
        return list(reader)


def verify_inputs(analysis_dir: Path) -> dict:
    paths = {name: analysis_dir / "results" / name for name in
             ("weekly.csv", "run_metrics.csv", "summary.json", "dtw_summary.csv")}
    paths["contract.json"] = analysis_dir / "contract.json"
    source_hashes = {str(path): digest(path) for path in paths.values()}
    contract = json.loads(paths["contract.json"].read_text(encoding="utf-8"))
    summary = json.loads(paths["summary.json"].read_text(encoding="utf-8"))
    for key, expected in (("arms", ARMS), ("seeds", SEEDS), ("weeks", WEEKS),
                          ("author_types", TYPES), ("late_weeks", WEEKS[-4:])):
        if tuple(contract[key]) != expected:
            raise ValueError(f"contract.{key}: 与冻结的三臂 10 seed/11 周绘图范围不符")
    supply = contract["supply_plot"]
    if (supply["template"] != "chart3b" or supply["y_axis"] != [0, 80]
            or supply["y_tick"] != 10 or tuple(supply["colors"]) != TYPE_COLORS
            or supply["event_week"] != "2026-W13"):
        raise ValueError("contract.supply_plot: 与 chart3b 的颜色、事件线或比例尺不符")
    if summary["contract_sha256"] != source_hashes[str(paths["contract.json"])]:
        raise ValueError("summary 的 contract SHA 与实际冻结文件不一致")
    if summary["method"] != contract["dtw"]:
        raise ValueError("summary.method 与冻结 DTW 口径不一致")
    if any(contract["dtw"].get(key) != value for key, value in EXPECTED_METHOD.items()):
        raise ValueError("contract.dtw: 主 DTW 方法或计分单位不符")

    weekly_rows = read_csv(paths["weekly.csv"], {"algorithm", "seed", "week", "posted_total"}
                           | {f"posted_{kind}_authors" for kind in TYPES}
                           | {f"share_{kind}" for kind in TYPES})
    metric_rows = read_csv(paths["run_metrics.csv"], {
        "algorithm", "seed", "dtw_x100", "total_posts", "late_meme_posts",
        "late_total_posts", "late_meme_share", "late_feed_total", "late_feed_meme_tag",
        "late_feed_meme_tag_share"})
    dtw_rows = read_csv(paths["dtw_summary.csv"], {
        "algorithm", "n", "mean", "sample_sd", "min", "max",
        "mean_trajectory_dtw_x100", "mean_trajectory_path_length"})
    expected_runs = {(arm, seed) for arm in ARMS for seed in SEEDS}
    expected_weeks = {(arm, seed, week) for arm, seed in expected_runs for week in WEEKS}
    weekly, metrics, dtw_table = {}, {}, {}
    for row in weekly_rows:
        key = (row["algorithm"], count(row["seed"], "weekly.seed"), row["week"])
        if key not in expected_weeks or key in weekly:
            raise ValueError(f"weekly: 非矩阵行或重复行 {key}")
        values = {kind: count(row[f"posted_{kind}_authors"], f"{key}/{kind}") for kind in TYPES}
        total = count(row["posted_total"], f"{key}/posted_total")
        if sum(values.values()) != total:
            raise ValueError(f"{key}: 五类成功发布数不守恒")
        for kind in TYPES:
            same(row[f"share_{kind}"], values[kind] / total if total else 0.0,
                 f"{key}/share_{kind}")
        weekly[key] = {**values, "posted_total": total}
    if set(weekly) != expected_weeks or len(weekly_rows) != 330:
        raise ValueError("weekly 必须恰好覆盖 30 run × 11 周，即 330 行")
    for row in metric_rows:
        key = (row["algorithm"], count(row["seed"], "run_metrics.seed"))
        if key not in expected_runs or key in metrics:
            raise ValueError(f"run_metrics: 非矩阵行或重复行 {key}")
        arm, seed = key
        total = sum(weekly[(arm, seed, week)]["posted_total"] for week in WEEKS)
        late_total = sum(weekly[(arm, seed, week)]["posted_total"] for week in WEEKS[-4:])
        late_meme = sum(weekly[(arm, seed, week)]["meme"] for week in WEEKS[-4:])
        for field, expected in (("total_posts", total), ("late_total_posts", late_total),
                                ("late_meme_posts", late_meme)):
            if count(row[field], f"{key}/{field}") != expected:
                raise ValueError(f"{key}/{field}: 周表与 run 汇总不一致")
        same(row["late_meme_share"], late_meme / late_total if late_total else 0.0,
             f"{key}/late_meme_share")
        feed_total = count(row["late_feed_total"], f"{key}/late_feed_total")
        feed_meme = count(row["late_feed_meme_tag"], f"{key}/late_feed_meme_tag")
        if feed_meme > feed_total:
            raise ValueError(f"{key}: 玩梗标签曝光超过全部实际曝光")
        same(row["late_feed_meme_tag_share"], feed_meme / feed_total if feed_total else 0.0,
             f"{key}/late_feed_meme_tag_share")
        metrics[key] = {"dtw_x100": number(row["dtw_x100"], f"{key}/dtw_x100"),
                        "total_posts": total}
    if set(metrics) != expected_runs or len(metric_rows) != 30:
        raise ValueError("run_metrics 必须恰好覆盖三臂各 seed0–9，即 30 行")
    for row in dtw_rows:
        arm = row["algorithm"]
        if arm not in ARMS or arm in dtw_table:
            raise ValueError(f"dtw_summary: 臂缺失或重复 {arm}")
        dtw_table[arm] = row
    if set(dtw_table) != set(ARMS) or len(dtw_rows) != 3:
        raise ValueError("dtw_summary 必须恰好三行")
    if set(summary["dtw_by_arm"]) != set(ARMS):
        raise ValueError("summary.dtw_by_arm 必须恰好三臂")

    dtw, means = {}, []
    for arm in ARMS:
        values = [metrics[(arm, seed)]["dtw_x100"] for seed in SEEDS]
        stats = {"n": 10, "mean": statistics.mean(values), "sample_sd": statistics.stdev(values),
                 "min": min(values), "max": max(values), "seeds": list(SEEDS), "values": values}
        arm_summary = summary["dtw_by_arm"][arm]
        if arm_summary["seeds"] != list(SEEDS) or len(arm_summary["values"]) != 10:
            raise ValueError(f"{arm}: summary 的逐 seed DTW 列表不完整")
        for seed, value in enumerate(values):
            same(arm_summary["values"][seed], value, f"{arm}/seed{seed}/DTW")
        for field in ("n", "mean", "sample_sd", "min", "max"):
            same(arm_summary[field], stats[field], f"summary/{arm}/{field}")
            same(dtw_table[arm][field], stats[field], f"dtw_summary/{arm}/{field}")
        # 均值轨迹另算的 DTW 仅核验，绝不代替图中的逐 run 主分数。
        trajectory = summary["mean_trajectory_dtw"][arm]
        same(dtw_table[arm]["mean_trajectory_dtw_x100"], trajectory["dtw_x100"],
             f"{arm}/mean_trajectory_dtw_x100")
        same(dtw_table[arm]["mean_trajectory_path_length"], trajectory["path_length"],
             f"{arm}/mean_trajectory_path_length")
        dtw[arm] = stats
        for week in WEEKS:
            counts = {kind: statistics.mean(weekly[(arm, seed, week)][kind] for seed in SEEDS)
                      for kind in TYPES}
            total = statistics.mean(weekly[(arm, seed, week)]["posted_total"] for seed in SEEDS)
            if not math.isclose(sum(counts.values()), total, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(f"{arm}/{week}: 各 seed 等权均值不守恒")
            if total > 80:
                raise ValueError(f"{arm}/{week}: 均值发帖数超出冻结的 0–80 纵轴，不能裁剪")
            means.append({"algorithm": arm, "week": week, "n": 10, **counts,
                          "posted_total": total})
    return {"paths": paths, "input_sha256": source_hashes, "contract": contract,
            "dtw": dtw, "means": means, "metrics": metrics,
            "mean_trajectory_dtw": summary["mean_trajectory_dtw"],
            "checks": {"runs": 30, "weekly_rows": 330, "arms": 3, "seeds_per_arm": 10,
                       "weeks_per_run": 11, "mean_week_rows": 33,
                       "five_author_types_conserve_posted": True,
                       "means_are_equal_seed_arithmetic_means": True,
                       "dtw_summary_matches_individual_runs": True,
                       "error_bar": "sample standard deviation (ddof=1), not confidence interval",
                       "chronological": "historical complete runs reused",
                       "seed0": "random/interest pilot; already observed"}}


def apply_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Hiragino Sans GB", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"],
        "axes.unicode_minus": False, "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.edgecolor": "#444444", "axes.grid": True, "grid.color": "#DDDDDD",
        "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "hourly-return-seed10",
    })


def save_bundle(fig, stem: Path) -> list[Path]:
    paths = [stem.with_suffix(".png"), stem.with_suffix(".svg")]
    fig.savefig(paths[0], dpi=300, metadata={"Software": "AgentSociety offline seed10 analysis"})
    fig.savefig(paths[1], metadata={"Creator": "AgentSociety offline seed10 analysis", "Date": None})
    plt.close(fig)
    return paths


def plot_supply(data: dict, output_dir: Path) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(21, 6.8), sharey=True)
    fig.subplots_adjust(left=0.045, right=0.99, bottom=0.20, top=0.77, wspace=0.10)
    handles = None
    for ax, arm in zip(axes, ARMS):
        rows = [row for row in data["means"] if row["algorithm"] == arm]
        handles = ax.stackplot(range(11), *[[row[kind] for row in rows] for kind in TYPES],
                               colors=TYPE_COLORS, labels=TYPE_LABELS, edgecolor="white",
                               linewidth=0.6, alpha=0.92, zorder=2)
        ax.axvline(1, color="#D62728", linestyle="--", linewidth=1.4, alpha=0.85, zorder=3)
        ax.annotate("去世 3-24 (W13)", xy=(1, 1), xycoords=("data", "axes fraction"),
                    xytext=(6, -6), textcoords="offset points", color="#D62728", va="top",
                    fontsize=10, bbox={"fc": "white", "ec": "none", "alpha": 0.85, "pad": 2})
        mean_total = statistics.mean(data["metrics"][(arm, seed)]["total_posts"] for seed in SEEDS)
        ax.set_title(f"{ARM_TITLES[arm]}\n10 seed 均值 · 全窗平均 {mean_total:.1f} 帖", loc="left", pad=12)
        ax.set_xticks(range(11), [week.removeprefix("2026-") for week in WEEKS], rotation=45, ha="right")
        ax.set_xlabel("模拟周次（2026）")
        ax.set_ylim(0, 80)
        ax.set_yticks(range(0, 81, 10))
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Agent 每周发帖数（帖，10 seed 算术均值）")
    fig.suptitle("三臂 Agent 每周实际发帖量：各 10 seed 均值", fontsize=20, fontweight="bold", y=0.97)
    fig.legend(handles, TYPE_LABELS, loc="upper center", bbox_to_anchor=(0.52, 0.91),
               ncol=5, frameon=False, fontsize=12)
    fig.text(0.5, 0.045, "每臂各 10 seed 等权平均；五类按固定作者类型统计，仅计成功 posted。",
             ha="center", fontsize=11, color="#555555")
    fig.text(0.5, 0.012, "不含外部注入、官方帖和历史池；时序臂复用历史完整运行；随机、兴趣 seed0 为先导测试。",
             ha="center", fontsize=10, color="#555555")
    return save_bundle(fig, output_dir / "three_arm_mean_supply")


def plot_dtw(data: dict, output_dir: Path) -> list[Path]:
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.8), sharey=True)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.23, top=0.79, wspace=0.15)
    left, right = axes
    for index, arm in enumerate(ARMS):
        stats, color = data["dtw"][arm], ARM_COLORS[arm]
        left.errorbar(index + 0.27, stats["mean"], yerr=stats["sample_sd"], fmt="D",
                      color=color, markersize=6, capsize=6, elinewidth=2.0, zorder=5)
        for seed, value in zip(SEEDS, stats["values"]):
            pilot = seed == 0 and arm in ("random", "interest")
            left.scatter(index + JITTER[seed], value, s=50, facecolors="white" if pilot else color,
                         edgecolors=color, linewidths=1.5 if pilot else 0.6, alpha=1.0 if pilot else 0.8,
                         zorder=4)
        right.plot(SEEDS, stats["values"], color=color, linewidth=1.8,
                   label=ARM_LABELS[arm] + (" (historical)" if arm == "chronological" else ""), zorder=3)
        for seed, value in zip(SEEDS, stats["values"]):
            pilot = seed == 0 and arm in ("random", "interest")
            right.scatter(seed, value, s=44, facecolors="white" if pilot else color,
                          edgecolors=color, linewidths=1.5 if pilot else 0.6, zorder=4)
    lower = min(data["dtw"][arm]["mean"] - data["dtw"][arm]["sample_sd"] for arm in ARMS)
    upper = max(max(max(data["dtw"][arm]["values"]),
                    data["dtw"][arm]["mean"] + data["dtw"][arm]["sample_sd"]) for arm in ARMS)
    margin = max((upper - min(0.0, lower)) * 0.12, 0.5)
    left.set_ylim(min(0.0, lower - margin) if lower < 0 else 0.0, upper + margin)
    left.set_xlim(-0.4, 2.6)
    left.set_xticks(range(3), ("Random", "Chronological\n(historical)", "Interest"))
    left.set_ylabel("逐 run DTW 距离 ×100")
    left.set_title("逐 seed 分布与均值 ± 样本标准差", loc="left", pad=12)
    left.legend(handles=[Line2D([], [], color="#555555", marker="D", linestyle="none",
                                label="Mean ± sample SD"),
                         Line2D([], [], color="#555555", marker="o", markerfacecolor="white",
                                linestyle="none", label="Pilot seed0 (Random / Interest)")],
                loc="upper left", fontsize=9, frameon=False)
    right.set_title("相同 seed 的三臂 DTW 得分", loc="left", pad=12)
    right.set_xticks(SEEDS)
    right.set_xlabel("seed")
    right.legend(loc="upper left", fontsize=10, frameon=False)
    for ax in axes:
        ax.set_axisbelow(True)
        ax.grid(axis="x", visible=False)
    fig.suptitle("三臂 DTW 的跨种子稳定性", fontsize=20, fontweight="bold", y=0.96)
    fig.text(0.5, 0.115, "每臂 10 个完整 run；误差棒为样本标准差（SD，ddof=1），表示种子间波动。",
             ha="center", fontsize=11, color="#555555")
    fig.text(0.5, 0.072, "主分数为每个 run 独立计算的 DTW；五类份额欧氏距离、周窗口 ±1、路径长度归一化后 ×100。",
             ha="center", fontsize=10, color="#555555")
    fig.text(0.5, 0.029, "时序臂复用历史运行；空心点为随机、兴趣的先导 seed0。DTW 越小表示当前现实份额轨迹的描述距离越小。",
             ha="center", fontsize=10, color="#555555")
    return save_bundle(fig, output_dir / "dtw_stability")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, default=BASE,
                        help="包含 contract.json 和 results/ 四份分析表的目录")
    parser.add_argument("--output-dir", type=Path, help="输出目录；默认 analysis-dir/assets")
    args = parser.parse_args()
    analysis_dir = args.analysis_dir.resolve()
    output_dir = (args.output_dir or analysis_dir / "assets").resolve()
    data = verify_inputs(analysis_dir)
    apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = plot_supply(data, output_dir) + plot_dtw(data, output_dir)
    if any(digest(Path(path)) != sha for path, sha in data["input_sha256"].items()):
        raise ValueError("绘图期间输入文件发生变化，拒绝写入完成清单")
    manifest = {
        "scope": "random/chronological/interest × seed0–9 × W12–W22; offline only",
        "input_sha256": data["input_sha256"],
        "code_sha256": {str(Path(__file__).resolve()): digest(Path(__file__).resolve())},
        "output_sha256": {str(path): digest(path) for path in outputs},
        "validation": data["checks"],
        "mean_weekly_counts": data["means"],
        "dtw_by_arm": data["dtw"],
        "mean_trajectory_dtw_not_plotted": data["mean_trajectory_dtw"],
        "method": data["contract"]["dtw"],
        "limitations": data["contract"]["limitations"],
        "style": {"type_order": TYPES, "type_labels": TYPE_LABELS, "type_colors": TYPE_COLORS,
                  "supply_y_axis": [0, 80], "y_tick": 10, "event_week": "2026-W13",
                  "arm_colors": ARM_COLORS, "fixed_seed_jitter": JITTER,
                  "png_dpi": 300, "svg_text_editable": True},
        "matplotlib": matplotlib.__version__,
    }
    manifest_path = output_dir / "plot_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"outputs": [str(path) for path in outputs],
                      "manifest": str(manifest_path), "validation": data["checks"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
