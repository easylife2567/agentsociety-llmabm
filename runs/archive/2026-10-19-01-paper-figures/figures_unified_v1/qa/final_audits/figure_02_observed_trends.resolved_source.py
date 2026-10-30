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

"""图2：五类内容周数量堆积与悼念/玩梗数量。"""
from paper_plot_style import *


def main():
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    counts = observed.loc[observed.platform.eq('pooled')].pivot(index='week', columns='category', values='count').reindex(columns=CATS)
    assert counts.shape == (18, 5) and counts.to_numpy().sum() == 46602
    assert counts.ge(0).all().all()
    weeks = counts.index.str[-2:].astype(int).to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(52)))
    fig.subplots_adjust(left=.105, right=.985, top=.96, bottom=.33, wspace=.22)
    ax = axes[0]
    ax.stackplot(weeks, *(counts[cat].to_numpy() for cat in CATS), colors=[FILL_COLORS[cat] for cat in CATS], alpha=1.0, edgecolor='white', linewidth=.35, zorder=2)
    ax.set_ylabel('Posts per week')
    ax.set_ylim(0, 11000)
    ax.set_yticks([0, 2500, 5000, 7500, 10000])
    ax.yaxis.set_major_formatter(COUNT)
    week_axis(ax)
    ax.set_xlabel('')
    sublabel(fig, ax, '(a)')
    ax = axes[1]
    for cat in ['mourning', 'meme']:
        ax.plot(weeks, counts[cat], color=COLORS[cat], linewidth=1.65, linestyle=STYLES[cat], marker=MARKERS[cat], markersize=3, markeredgewidth=0, zorder=4)
    ax.set_ylim(0, 5500)
    ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000])
    ax.yaxis.set_major_formatter(COUNT)
    week_axis(ax)
    ax.set_xlabel('')
    sublabel(fig, ax, '(b)')
    fig.text(.545, .145, 'Publication week (2026)', ha='center', va='center', fontsize=9)
    shared_legend(fig, area=True)
    save_figure(fig, 'figure_02_observed_trends', list(axes), ['a', 'b'])


if __name__ == '__main__':
    main()
