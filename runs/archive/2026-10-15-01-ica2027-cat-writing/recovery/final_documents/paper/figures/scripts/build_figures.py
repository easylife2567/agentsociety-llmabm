#!/usr/bin/env python3
"""用既有实验数据绘制正文图1—5；默认只读本文件夹内的CSV。

从项目根运行：
    AgentSociety2/.venv/bin/python paper/figures/scripts/build_figures.py
加 --prepare 可先从既有原始数据重新生成CSV；不启动仿真或LLM。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.transforms import ScaledTranslation
from PIL import Image, ImageDraw, ImageFont

from audit_panel_alignment import require_matplotlib_panel_alignment

# 保留SVG文本和PDF TrueType字体，便于论文排版时编辑。
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams.update({
    "svg.fonttype": "none",
    "pdf.fonttype": 42, "font.size": 8.2, "axes.labelsize": 8.2,
    "axes.titlesize": 9, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5, "axes.linewidth": .6,
    "axes.spines.right": False, "axes.spines.top": False,
    "axes.edgecolor": "#5D636C", "text.color": "#20242A",
    "axes.labelcolor": "#20242A", "xtick.color": "#444B54",
    "ytick.color": "#444B54", "legend.frameon": False,
    "savefig.facecolor": "white", "figure.facecolor": "white",
    "xtick.major.size": 3, "ytick.major.size": 3,
    "svg.hashsalt": "agentsociety-timestamp-paper-figures",
})

OUT = Path(__file__).resolve().parents[1]
DATA = OUT / "source_data"
QA = OUT / "qa"
ROOT = OUT.parents[1]
CATS = ["education", "mourning", "meme", "other", "marketing"]
COLORS = {"education": "#4C78A8", "mourning": "#D55E00",
          "meme": "#6F4C9B", "other": "#B5BCC5", "marketing": "#DDBD64"}
NAMES = {"education": "Education", "mourning": "Mourning",
         "meme": "Memetic expression", "other": "Other discussion", "marketing": "Marketing"}
STYLES = {"education": "--", "mourning": "-", "meme": "-", "other": ":", "marketing": "-."}
ARMS = ["random", "chronological", "interest"]
ARM_NAMES = {"random": "Random", "chronological": "Chronological", "interest": "Interest"}
ARM_COLORS = {"random": "#7D8794", "chronological": "#4776A8", "interest": "#8E5D9F"}
MARKERS = ["o", "^", "s"]
PERCENT = FuncFormatter(lambda x, _: f"{x:g}%")
FIGURES = []
PDF_BOOK = None


def mm(value):
    return value / 25.4


def panel(ax, letter, title):
    # 面板字母用固定物理位移，避免不同图高带来错位。
    offset = ScaledTranslation(-25 / 72, 11 / 72, ax.figure.dpi_scale_trans)
    ax.text(0, 1, letter, transform=ax.transAxes + offset,
            fontsize=10, fontweight="bold", va="bottom", ha="left")
    ax.set_title(title, loc="left", pad=12, fontsize=9, fontweight="medium")
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E4E7EB", lw=.45)


def week_axis(ax, start, stop, step=2):
    ax.set_xlim(start, stop)
    ticks = list(range(start, stop + 1, step))
    if stop not in ticks:
        if stop - ticks[-1] < step:
            ticks.pop()
        ticks.append(stop)
    ax.set_xticks(ticks, [f"W{x:02d}" for x in ticks])
    ax.set_xlabel("Publication week (2026)")
    ax.axvline(13, color="#424953", ls=(0, (3, 2)), lw=.85, zorder=6)


def legend_items(author=False):
    labels = {**NAMES, "meme": "Memetic"} if author else NAMES
    handles = [Patch(facecolor=COLORS[c], edgecolor="none", label=labels[c]) for c in CATS]
    handles.append(Line2D([], [], color="#424953", lw=.9, ls="--", label="Event week (W13)"))
    return handles


def save(fig, stem, axes, labels):
    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig, axes=axes, panel_ids=labels,
        json_out=QA / f"{stem}.alignment.json",
        overlay_svg=QA / f"{stem}.alignment.svg",
        tolerance_pt=1.5, gutter_tolerance_pt=1.5,
        require_panel_labels=True, strict=True,
    )
    fig.savefig(OUT / f"{stem}.svg", dpi=600)
    fig.savefig(OUT / f"{stem}.pdf", dpi=600,
                metadata={"Creator": "AgentSociety: existing timestamp data"})
    fig.savefig(OUT / f"{stem}.png", dpi=600)
    if PDF_BOOK is not None:
        PDF_BOOK.savefig(fig)
    FIGURES.append(stem)
    plt.close(fig)


def stack_composition(ax, frame):
    shares = frame.pivot(index="week", columns="category", values="share").reindex(columns=CATS)
    assert not shares.isna().any().any()
    assert np.allclose(shares.sum(axis=1).values, 1), "五类比例必须加总为1"
    weeks = shares.index.str[-2:].astype(int).to_numpy()
    # 不平滑曲线；直接连接相邻周的真实比例，周网格在CSV中保留。
    ax.stackplot(weeks, *(shares[c].values * 100 for c in CATS),
                 colors=[COLORS[c] for c in CATS], edgecolor="white", linewidth=.35, zorder=2)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(MultipleLocator(25))
    ax.yaxis.set_major_formatter(PERCENT)
    ax.set_ylabel("Within-week content share")
    week_axis(ax, int(weeks.min()), int(weeks.max()))


def observed_figures():
    observed = pd.read_csv(DATA / "observed_weekly.csv")
    pooled = observed.loc[observed.platform.eq("pooled")]
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(88)))
    fig.subplots_adjust(left=.105, right=.975, top=.84, bottom=.29, wspace=.30)
    stack_composition(axes[0], pooled)
    panel(axes[0], "a", "Pooled content composition")
    counts = pooled.pivot(index="week", columns="category", values="count")
    weeks = counts.index.str[-2:].astype(int).to_numpy()
    for cat, marker in [("mourning", "o"), ("meme", "s")]:
        axes[1].plot(weeks, counts[cat], color=COLORS[cat], lw=1.6, marker=marker,
                     markersize=2.9, markeredgewidth=0, label=NAMES[cat], zorder=4)
    axes[1].set_ylim(0, 4800)
    axes[1].yaxis.set_major_locator(MultipleLocator(1000))
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}"))
    axes[1].set_ylabel("Posts per week")
    week_axis(axes[1], int(weeks.min()), int(weeks.max()))
    panel(axes[1], "b", "Mourning and memetic posts")
    fig.legend(handles=legend_items(), loc="lower center", ncol=3,
               bbox_to_anchor=(.52, .012), columnspacing=1.8, handlelength=1.7)
    save(fig, "figure_01_observed_pooled", list(axes), ["a", "b"])

    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(88)))
    fig.subplots_adjust(left=.105, right=.975, top=.84, bottom=.29, wspace=.30)
    for ax, letter, name, title in zip(axes, "ab", ["douyin", "xiaohongshu"], ["Douyin", "Xiaohongshu"]):
        stack_composition(ax, observed.loc[observed.platform.eq(name)])
        panel(ax, letter, title)
    fig.legend(handles=legend_items(), loc="lower center", ncol=3,
               bbox_to_anchor=(.52, .012), columnspacing=1.8, handlelength=1.7)
    save(fig, "figure_02_observed_platforms", list(axes), ["a", "b"])


def replicate_points(ax, values, positions, horizontal=False):
    """展示每个seed的实际取值与算术均值，不构造推断性误差条。"""
    for i, arm in enumerate(ARMS):
        group = values.loc[values.arm.eq(arm)].sort_values("seed")
        for j, value in enumerate(group.value):
            jitter = (j - 1) * .12
            x, y = (value, positions[i] + jitter) if horizontal else (positions[i] + jitter, value)
            ax.scatter(x, y, s=23, marker=MARKERS[j], facecolor=ARM_COLORS[arm],
                       edgecolor="white", linewidth=.35, zorder=4)
        mean = group.value.mean()
        x, y = (mean, positions[i]) if horizontal else (positions[i], mean)
        ax.plot(x, y, marker="|" if horizontal else "_", ms=15, mew=1.8,
                color="#20242A", zorder=5, ls="none")


def simulation_figure():
    weekly = pd.read_csv(DATA / "simulation_weekly.csv")
    late = pd.read_csv(DATA / "simulation_late.csv")
    assert len(late) == 9 and len(weekly) == 9 * 11 * 5
    fig, axes = plt.subplots(2, 2, figsize=(mm(180), mm(144)))
    fig.subplots_adjust(left=.105, right=.975, top=.91, bottom=.22, wspace=.30, hspace=.60)
    for ax, arm, letter in zip(axes.flat, ARMS, "abc"):
        current = weekly.loc[weekly.arm.eq(arm)]
        for category in CATS:
            matrix = current.loc[current.category.eq(category)].pivot(index="seed", columns="week", values="count")
            assert matrix.shape == (3, 11) and not matrix.isna().any().any()
            weeks = matrix.columns.str[-2:].astype(int).to_numpy()
            # 所有三次重复均画为同色细线；粗线为跨seed均值，避免隐藏运行间差异。
            for _, row in matrix.iterrows():
                ax.plot(weeks, row.values, color=COLORS[category], lw=.55,
                        alpha=.32, ls=STYLES[category], zorder=2)
            ax.plot(weeks, matrix.mean(axis=0).values, color=COLORS[category], lw=1.65,
                    ls=STYLES[category], marker="s" if category == "meme" else None,
                    markersize=2.2, markeredgewidth=0, zorder=4)
        ax.set_ylim(0, 25)
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.set_ylabel("Posts per week")
        week_axis(ax, 12, 22)
        ax.set_xlabel("Simulation week (2026)")
        panel(ax, letter, ARM_NAMES[arm])
    ax = axes[1, 1]
    points = late.assign(value=late.meme_share * 100)
    replicate_points(ax, points, np.arange(3))
    ax.set_xticks(range(3), [ARM_NAMES[a] for a in ARMS], fontsize=7.4)
    ax.set_xlim(-.5, 2.5)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(MultipleLocator(25))
    ax.yaxis.set_major_formatter(PERCENT)
    ax.set_ylabel("Memetic-type supply share")
    ax.set_xlabel("Curation regime")
    panel(ax, "d", "Late supply composition (W19–W22)")
    fig.legend(handles=legend_items(author=True), loc="lower center", ncol=3,
               title="Author type", title_fontsize=7.8, bbox_to_anchor=(.52, .058),
               columnspacing=1.8, handlelength=1.7)
    fig.text(.52, .025, "Thin lines and points: individual seeds; thick lines and bars: means (n = 3).",
             ha="center", fontsize=7.3)
    save(fig, "figure_03_simulated_trajectories", list(axes.flat), list("abcd"))


def exposure_figure():
    exposure = pd.read_csv(DATA / "simulation_exposure.csv")
    specs = [
        ("own_share", "Same-type exposure", "Own feed items (%)", 50, 10),
        ("meme_post_rate", "Posting participation", "Expression\nopportunities (%)", 70, 20),
        ("cross_generated_share", "Generated recirculation", "Other authors' feed\nitems (%)", 30, 10),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(mm(180), mm(82)), sharey=True)
    fig.subplots_adjust(left=.17, right=.97, top=.80, bottom=.26, wspace=.30)
    for ax, letter, (metric, title, xlabel, upper, step) in zip(axes, "abc", specs):
        values = exposure.assign(value=exposure[metric] * 100)
        replicate_points(ax, values, [2, 1, 0], horizontal=True)
        ax.set_xlim(-upper * .025, upper)
        ax.set_xticks(np.arange(0, upper + .1, step))
        ax.set_yticks([2, 1, 0], [ARM_NAMES[a] for a in ARMS])
        ax.set_ylim(-.5, 2.5)
        ax.set_xlabel(xlabel, fontsize=7.8, labelpad=7)
        panel(ax, letter, title)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color="#E4E7EB", lw=.45)
    fig.text(.56, .95, "Late window: W19–W22", ha="center", fontsize=9)
    fig.text(.56, .07, "Points: individual seeds; vertical bars: means (n = 3 per regime).",
             ha="center", fontsize=7.3)
    save(fig, "figure_04_feedback_exposure", list(axes), list("abc"))


def ablation_figure():
    data = pd.read_csv(DATA / "ablation_metrics.csv")
    specs = [
        ("a", "Total output\nW19–W22", "Posts per week", 20, 5, "B = 0"),
        ("b", "Memetic-type participation\nW19–W22", "Posting opportunities (%)", 65, 20, "D = 1"),
        ("c", "Overall participation\nW14–W18", "Posting opportunities (%)", 60, 20, "R = 1"),
        ("d", "Memetic-type supply share\nW19–W22", "Generated posts (%)", 85, 20, "R = 1"),
        ("e", "Cross-group exposure\nW19–W22", "Other authors' feed items (%)", 30, 10, "R = 1"),
    ]
    fig, grid = plt.subplots(2, 3, figsize=(mm(183), mm(140)))
    fig.subplots_adjust(left=.10, right=.975, top=.85, bottom=.13, wspace=.46, hspace=.72)
    axes = list(grid.flat)[:5]
    for ax, (letter, title, ylabel, upper, step, intervention) in zip(axes, specs):
        current = data.loc[data.panel.eq(letter)].copy()
        assert len(current) == 6
        conditions = list(current.condition.unique())
        full = next(c for c in conditions if c in ("full", "Full", "baseline"))
        ablated = next(c for c in conditions if c != full)
        factor = 1 if letter == "a" else 100
        for seed in range(3):
            pair = current.loc[current.seed.eq(seed)].set_index("condition")
            values = pair.loc[[full, ablated], "value"].to_numpy(float) * factor
            offset = (seed - 1) * .065
            ax.plot(np.array([0, 1]) + offset, values, color="#AEB5BD", lw=.9, zorder=2)
            for x, y, color in zip(np.array([0, 1]) + offset, values, ["#66717F", "#4776A8"]):
                ax.scatter(x, y, marker=MARKERS[seed], s=26, facecolor=color,
                           edgecolor="white", linewidth=.35, zorder=4)
        means = current.groupby("condition").value.mean()
        for x, condition in enumerate([full, ablated]):
            ax.plot(x, means[condition] * factor, marker="_", ms=17, mew=1.8,
                    color="#20242A", ls="none", zorder=5)
        ax.set_xlim(-.35, 1.35)
        ax.set_ylim(0, upper)
        ax.yaxis.set_major_locator(MultipleLocator(step))
        ax.set_ylabel(ylabel, fontsize=7.8)
        ax.set_xticks([0, 1], ["Full", intervention], fontsize=8.2)
        panel(ax, letter, title)
        ax.title.set_fontsize(8.3)
    legend_ax = grid[1, 2]
    legend_ax.axis("off")
    handles = [Line2D([], [], marker=m, color="none", markerfacecolor="#66717F",
                      markeredgecolor="white", markersize=5, label=f"Seed {i}")
               for i, m in enumerate(MARKERS)]
    handles.append(Line2D([], [], marker="_", color="#20242A", lw=0, mew=1.8,
                          markersize=15, label="Mean"))
    legend_ax.legend(handles=handles, loc="upper left", fontsize=8, handlelength=2,
                     title="Paired runs (n = 3)", title_fontsize=8.5, labelspacing=.8)
    legend_ax.text(.03, .02, "Lines connect the same seed.\nAll comparisons: interest regime.",
                   transform=legend_ax.transAxes, va="bottom", fontsize=7.5, linespacing=1.5)
    save(fig, "figure_05_bdr_ablation", axes, list("abcde"))


def contact_sheet():
    width, padding, title_height = 1800, 48, 58
    tiles = []
    font_path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    font = ImageFont.truetype(str(font_path), 32) if font_path.exists() else ImageFont.load_default(size=32)
    for number, stem in enumerate(FIGURES, 1):
        img = Image.open(OUT / f"{stem}.png").convert("RGB")
        img.thumbnail((width - 2 * padding, 1600), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (width, img.height + title_height + padding), "white")
        ImageDraw.Draw(tile).text((padding, 10), f"Figure {number}", fill="#20242A", font=font)
        tile.paste(img, ((width - img.width) // 2, title_height))
        tiles.append(tile)
    sheet = Image.new("RGB", (width, sum(t.height for t in tiles)), "#EEF1F4")
    y = 0
    for tile in tiles:
        sheet.paste(tile, (0, y))
        y += tile.height
    sheet.save(OUT / "all_figures_preview.png")


def main():
    global PDF_BOOK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="先离线重新整理现有原始结果")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    QA.mkdir(exist_ok=True)
    if args.prepare:
        for script in ["prepare_observed.py", "prepare_simulation.py", "prepare_ablation.py"]:
            subprocess.run([sys.executable, str(Path(__file__).with_name(script))], check=True, cwd=ROOT)
    with PdfPages(OUT / "all_figures.pdf") as book:
        PDF_BOOK = book
        observed_figures()
        simulation_figure()
        exposure_figure()
        ablation_figure()
    PDF_BOOK = None
    contact_sheet()
    manifest = {
        "backend": "Python / Matplotlib", "python": platform.python_version(),
        "matplotlib": matplotlib.__version__, "numpy": np.__version__, "pandas": pd.__version__,
        "manuscript_sha256": (hashlib.sha256((ROOT / "paper/manuscript/manuscript.accepted.md").read_bytes()).hexdigest()
                              if (ROOT / "paper/manuscript/manuscript.accepted.md").exists() else None),
        "dimensions_mm": {stem: ([183, 140] if stem.startswith("figure_05") else
                               [180, 144] if stem.startswith("figure_03") else
                               [180, 82] if stem.startswith("figure_04") else [180, 88]) for stem in FIGURES},
        "replicates": "three original seeds, 0/1/2; individual observations and arithmetic means",
        "interpolation": "straight segments between observed weekly values; no curve smoothing",
        "palette": COLORS,
        "outputs": [{"file": str(p.relative_to(OUT)), "bytes": p.stat().st_size,
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                    for stem in FIGURES for p in sorted(OUT.glob(f"{stem}.*"))],
        "source_data": [{"file": str(p.relative_to(OUT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted(DATA.glob("*.csv"))],
    }
    (QA / "build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures": FIGURES, "exports": len(manifest["outputs"]), "folder": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
