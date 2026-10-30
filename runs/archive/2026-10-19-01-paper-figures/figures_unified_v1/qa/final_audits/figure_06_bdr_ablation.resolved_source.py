"""图2—6统一出版样式；文字可编辑的SVG和原生矢量PDF。"""
from pathlib import Path
import hashlib
import json
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import offset_copy
from matplotlib.textpath import TextPath
from matplotlib.markers import MarkerStyle
from audit_panel_alignment import require_matplotlib_panel_alignment, audit_layout_manifest, write_json_report
from matplotlib.ticker import FuncFormatter, MultipleLocator

OUT = Path(__file__).resolve().parents[1]
DATA = OUT / 'source_data'
QA = OUT / 'qa'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9, 'axes.labelsize': 9, 'xtick.labelsize': 8,
    'ytick.labelsize': 8, 'legend.fontsize': 8, 'axes.linewidth': .65,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#424A52', 'text.color': '#20262D',
    'axes.labelcolor': '#20262D', 'xtick.color': '#303942',
    'ytick.color': '#303942', 'legend.frameon': False,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'figure.dpi': 150, 'savefig.dpi': 600,
    'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'text.usetex': False, 'mathtext.fontset': 'stix',
    'axes.unicode_minus': True,
    'svg.hashsalt': 'ica2027-dark2-compact-20261030',
})
CATS = ['education', 'mourning', 'meme', 'other', 'marketing']
COLORS = {'education': '#5595D0', 'mourning': '#F6AF4D', 'meme': '#DC4743',
          'other': '#7B873D', 'marketing': '#B69B58'}
FILL_COLORS = {'education': '#5595D0', 'mourning': '#F6AF4D', 'meme': '#DC4743',
               'other': '#7B873D', 'marketing': '#FEF3D5'}
NAMES = {'education': 'Education', 'mourning': 'Mourning',
         'meme': 'Memetic expression', 'other': 'Other discussion',
         'marketing': 'Marketing'}
STYLES = {'education': '--', 'mourning': '-', 'meme': '-',
          'other': ':', 'marketing': '-.'}
MARKERS = {'education': '^', 'mourning': 'o', 'meme': 's',
           'other': 'P', 'marketing': 'D'}
ARMS = ['random', 'chronological', 'interest']
ARM_NAMES = {'random': 'Random', 'chronological': 'Chronological',
             'interest': 'Interest-based'}
ARM_COLORS = {'random': '#5595D0', 'chronological': '#F6AF4D', 'interest': '#7B873D'}
INK = '#20262D'
PERCENT = FuncFormatter(lambda x, _: f'{x:g}%')
COUNT = FuncFormatter(lambda x, _: f'{x:,.0f}')
EVENT_TEXT = 'Official obituary'


def mm(value):
    return value / 25.4


def clean_axis(ax, grid='y'):
    ax.set_axisbelow(True)
    ax.grid(visible=False)
    ax.tick_params(length=3, width=.6, pad=3)
    return ax


def week_axis(ax, first=5, last=22, simulation=False):
    """同一周轴规格，加粗W13并附五角星。"""
    ticks = [5, 9, 13, 17, 22] if first == 5 else [12, 13, 16, 19, 22]
    ax.set_xlim(first - .18, last + .18)
    ax.set_xticks(ticks, [f'W{week:02d}' for week in ticks])
    ax.set_xlabel(('Simulation' if simulation else 'Publication') + ' week (2026)')
    for tick, week in zip(ax.get_xticklabels(), ticks):
        tick.set_fontweight('bold' if week == 13 else 'normal')
        if first == 12 and week == 12:
            tick.set_horizontalalignment('right')
    # 五角星在最终draw后按文字实际字形定位，此处先创建路径对象。
    star, = ax.plot([0], [0], transform=ax.figure.transFigure, marker='*', markersize=6,
        markeredgewidth=.7, color=INK, linestyle='none', clip_on=False, zorder=10)
    star.set_gid(f'event-star-W13-{ax.figure.axes.index(ax)}')
    ax._event_star = star
    clean_axis(ax)


def align_event_stars(fig, axes):
    """将可见五角星中心对齐W13可见大写字形中心。"""
    renderer = fig.canvas.get_renderer()
    marker = MarkerStyle('*')
    path_box = marker.get_path().transformed(marker.get_transform()).get_extents()
    metrics = []
    for ax in axes:
        if not hasattr(ax, '_event_star'):
            continue
        tick = next(label for label in ax.get_xticklabels() if label.get_text() == 'W13')
        _, lines, _ = tick._get_layout(renderer)
        _, _, dx, dy = lines[0]
        anchor = tick.get_transform().transform(tick.get_position())
        glyph = TextPath((0, 0), 'W13', prop=tick.get_fontproperties(), size=tick.get_fontsize()).get_extents()
        scale = fig.dpi / 72
        text_center_y = anchor[1] + dy + (glyph.y0 + glyph.y1) / 2 * scale
        text_right = anchor[0] + dx + glyph.x1 * scale
        size = ax._event_star.get_markersize()
        x = text_right + (3 + path_box.width / 2 * size) * scale
        y = text_center_y - (path_box.y0 + path_box.y1) / 2 * size * scale
        location = fig.transFigure.inverted().transform((x, y))
        ax._event_star.set_data([location[0]], [location[1]])
        true_center_y = y + (path_box.y0 + path_box.y1) / 2 * size * scale
        metrics.append({'panel': axes.index(ax), 'visible_center_delta_pt': round((true_center_y - text_center_y) / scale, 6)})
    return metrics


def shared_legend(fig, *, area=False, author=False, y=.012):
    """五类和加粗的事件释义合并为一行。"""
    handles = area_handles() if area else category_handles(author=author)
    handles.append(Line2D([], [], marker='*', markersize=6, markeredgewidth=.7,
        color=INK, linestyle='none', label=EVENT_TEXT))
    legend = fig.legend(handles=handles, loc='lower center', ncol=6,
        bbox_to_anchor=(.535, y), borderaxespad=0, fontsize=8,
        handlelength=1.25, handletextpad=.4, columnspacing=.7)
    legend.get_texts()[-1].set_fontweight('bold')
    return legend


def sublabel(fig, ax, text, y=None):
    """编号和必要条件名合并在绘图区内左上角，不占顶部行。"""
    artist = ax.annotate(text, xy=(0, 1), xycoords='axes fraction',
        xytext=(3, -3), textcoords='offset points', ha='left', va='top',
        fontsize=9, fontweight='bold', annotation_clip=False)
    ax._publication_panel_label = artist
    return artist


def area_handles():
    return [Patch(facecolor=FILL_COLORS[c], edgecolor='white', alpha=1.0, label=NAMES[c]) for c in CATS]


def category_handles(author=False):
    return [Line2D([], [], color=COLORS[c], linestyle=STYLES[c],
        marker=MARKERS[c], markersize=3, markeredgewidth=0, lw=1.5,
        label=('Memetic' if author and c == 'meme' else NAMES[c])) for c in CATS]


def save_figure(fig, stem, axes, panels):
    """固定幅面导出并记录实际文字边界，避免自动裁切造成各图比例变化。"""
    fig.canvas.draw()
    event_alignment = align_event_stars(fig, axes)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # 先按nature技能门禁核对绘图区，再显式加入带括号分图标记的实测锚点。
    report = require_matplotlib_panel_alignment(fig, axes=axes, panel_ids=panels,
        tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
    layout = report['layout']
    for ax, entry in zip(axes, layout['panels']):
        box = ax._publication_panel_label.get_window_extent(renderer)
        entry['panel_label'] = entry['id']
        entry['panel_label_anchor_pt'] = [box.x0 * 72 / fig.dpi, box.y0 * 72 / fig.dpi]
    report = audit_layout_manifest(layout, tolerance_pt=1.5,
        gutter_tolerance_pt=1.5, require_panel_labels=True)
    write_json_report(report, QA / f'{stem}.alignment.json')
    if report['verdict'] != 'PASS':
        raise RuntimeError(f"Panel alignment: {report['verdict']}")
    boxes = []
    for obj in fig.findobj(plt.Text):
        if not obj.get_visible() or not obj.get_text():
            continue
        box = obj.get_window_extent(renderer)
        if box.width and box.height:
            boxes.append({'text': obj.get_text(), 'font_pt': obj.get_fontsize(),
                'bbox_px': [round(v, 2) for v in box.extents],
                'outside_canvas': bool(box.x0 < -.5 or box.y0 < -.5 or
                    box.x1 > fig.bbox.width + .5 or box.y1 > fig.bbox.height + .5)})
    fig.savefig(OUT / f'{stem}.svg', format='svg')
    fig.savefig(OUT / f'{stem}.pdf', format='pdf', metadata={'Creator': 'ICA2027 unified scientific figures'})
    fig.savefig(OUT / f'{stem}.png', format='png', dpi=600)
    svg = OUT / f'{stem}.svg'
    svg.write_text(svg.read_text().replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', 1))
    info = {'figure': stem, 'size_mm': [round(v * 25.4, 2) for v in fig.get_size_inches()],
            'panels': panels, 'font': 'Arial', 'base_font_pt': 9,
            'python': platform.python_version(), 'matplotlib': matplotlib.__version__,
            'rendered_text_boxes': boxes,
            'outside_canvas': [item for item in boxes if item['outside_canvas']],
            'axes': [list(ax.get_position().bounds) for ax in axes],
            'event_star_count': sum(hasattr(ax, '_event_star') for ax in axes),
            'event_alignment': event_alignment,
            'legend_rows': 1 if any(hasattr(ax, '_event_star') for ax in axes) else 0,
            'outputs': {fmt: hashlib.sha256((OUT / f'{stem}.{fmt}').read_bytes()).hexdigest()
                        for fmt in ('svg', 'pdf', 'png')}}
    (QA / f'{stem}.build.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(f'Saved {stem}: SVG/PDF/PNG')

"""图6：同批完整模型与B/D/R干预的十种子配对比较。"""
from paper_plot_style import *
import math


def main():
    data = pd.read_csv(DATA / 'ablation_metrics.csv')
    assert len(data) == 100 and set(data.seed) == set(range(10))
    assert not data.duplicated(['panel', 'condition', 'seed']).any()
    specs = [
        ('a', 'W19–W22', 'Total output\n(posts per week)', 5, 'no_b', 'B = 0'),
        ('b', 'W19–W22', 'Memetic-type\nspeaking rate (%)', 20, 'no_d', 'D = 1'),
        ('c', 'W14–W18', 'Overall\nspeaking rate (%)', 20, 'no_r', 'R → 1'),
        ('d', 'W19–W22', 'Memetic-type\nsupply share (%)', 25, 'no_r', 'R → 1'),
        ('e', 'W19–W22', "Memetic content in\nothers’ feeds (%)", 10, 'no_r', 'R → 1'),
    ]
    fig = plt.figure(figsize=(mm(180), mm(84)))
    # 上排三面板各跨两列，下排两面板各跨三列，统一外缘与面板高度。
    grid = fig.add_gridspec(2, 6, left=.095, right=.98, bottom=.10,
                           top=.97, wspace=1.20, hspace=.42)
    axes = [fig.add_subplot(grid[0, 0:2]),
            fig.add_subplot(grid[0, 2:4]),
            fig.add_subplot(grid[0, 4:6]),
            fig.add_subplot(grid[1, 0:3]),
            fig.add_subplot(grid[1, 3:6])]
    offsets = np.linspace(-.15, .15, 10)
    for ax, (letter, window, ylabel, step, condition, label) in zip(axes, specs):
        part = data.loc[data.panel.eq(letter)]
        assert len(part) == 20 and set(part.condition) == {'full', condition}
        assert all(set(group.seed) == set(range(10)) for _, group in part.groupby('condition'))
        factor = 1 if letter == 'a' else 100
        expected = (14, 18) if letter == 'c' else (19, 22)
        assert set(part.week_start.str[-2:].astype(int)) == {expected[0]}
        assert set(part.week_end.str[-2:].astype(int)) == {expected[1]}
        assert np.allclose(part.value, part.numerator / part.denominator)
        maximum = part.value.max() * factor
        upper = math.ceil((maximum + step * .46) / 5) * 5
        segments = []
        for seed, offset in enumerate(offsets):
            pair = part.loc[part.seed.eq(seed)].set_index('condition')
            values = pair.loc[['full', condition], 'value'].to_numpy(float) * factor
            x = np.array([0, 1]) + offset
            segments.append((x, values))
            ax.plot(x, values, color='#A7AFB7', lw=.65, alpha=.8, zorder=2)
            for xx, yy, color, marker in zip(x, values,
                    ['#5595D0', '#F6AF4D'], ['o', 'D']):
                ax.scatter(xx, yy, marker=marker, s=19, facecolor=color,
                           edgecolor='white', linewidth=.35, zorder=4, clip_on=False)
        ax.set_xlim(-.45, 1.38)
        ax.set_ylim(0, upper)
        for x, cond in enumerate(['full', condition]):
            values = part.loc[part.condition.eq(cond), 'value'] * factor
            mean = values.mean()
            ax.plot([x - .21, x + .21], [mean, mean], color=INK, lw=1.75, zorder=5)
            # 用文字实际宽度核对其下方所有配对线，避免斜线穿过数字。
            text = ax.text(x, 0, f'{mean:.1f}' + ('' if letter == 'a' else '%'), ha='center', va='bottom', fontsize=8.5, fontweight='bold')
            fig.canvas.draw()
            half_width = text.get_window_extent(fig.canvas.get_renderer()).width / ax.bbox.width * (ax.get_xlim()[1] - ax.get_xlim()[0]) / 2
            local_top = float(values.max())
            for xx, yy in segments:
                lo, hi = max(xx[0], x - half_width), min(xx[1], x + half_width)
                if lo <= hi:
                    local_top = max(local_top, *(yy[0] + (yy[1] - yy[0]) * (v - xx[0]) / (xx[1] - xx[0]) for v in (lo, hi)))
            text.set_position((x, local_top + step * .22))
        ax.set_yticks(np.arange(0, upper + 1e-9, step))
        ax.set_xticks([0, 1], ['Full', label], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9, labelpad=4)
        clean_axis(ax)
        sublabel(fig, ax, f'({letter})')
    save_figure(fig, 'figure_06_bdr_ablation', axes, list('abcde'))


if __name__ == '__main__':
    main()
