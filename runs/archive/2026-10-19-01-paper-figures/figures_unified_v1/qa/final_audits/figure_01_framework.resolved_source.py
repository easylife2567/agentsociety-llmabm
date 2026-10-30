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

"""图1：两项互补研究与小时回流机制的精简环形框架。"""
import hashlib
import json

from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from paper_plot_style import (
    OUT, INK, COLORS, FILL_COLORS, CATS, mm, plt,
    require_matplotlib_panel_alignment, audit_layout_manifest, write_json_report,
)

WIDTH, HEIGHT = 180, 66
QA = OUT / 'qa/framework_utility'
STEM = 'figure_01_framework'
NEUTRAL = '#879098'
EDGE = '#AAB2B8'


def text(ax, x, y, label, size=9, bold=False, color=INK, ha='center'):
    return ax.text(x, y, label, ha=ha, va='center', fontsize=size,
                   fontweight='bold' if bold else 'normal', color=color,
                   linespacing=1.1, clip_on=False, zorder=8)


def box(ax, x, y, width, height, *, fill='white', accent=None):
    patch = FancyBboxPatch((x, y), width, height,
        boxstyle='round,pad=0,rounding_size=1.1', linewidth=.75,
        facecolor=fill, edgecolor=EDGE, clip_on=False, zorder=3)
    ax.add_patch(patch)
    if accent:
        ax.add_patch(Rectangle((x, y + 1.1), .85, height - 2.2,
            facecolor=accent, edgecolor='none', clip_on=False, zorder=4))
    return patch


def arrow(ax, points, color=INK, width=.85, head=6.5, curved=False):
    codes = ([Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
             if curved else [Path.MOVETO] + [Path.LINETO] * (len(points) - 1))
    patch = FancyArrowPatch(path=Path(points, codes), arrowstyle='-|>',
        mutation_scale=head, linewidth=width, color=color,
        capstyle='round', joinstyle='round', clip_on=False, zorder=2)
    ax.add_patch(patch)
    return patch


def mourning_icon(ax):
    """原创白花与蜡烛，仅标示研究情境，不编码样本量。"""
    original_artists = set(ax.get_children())
    ax.plot([9, 10.3], [46, 52], color=COLORS['other'], lw=.7, zorder=5)
    ax.add_patch(Ellipse((9.1, 48.1), 2.5, .8, angle=35,
        facecolor=COLORS['other'], edgecolor='none', zorder=5))
    for angle in range(0, 360, 30):
        from math import cos, sin, radians
        r = radians(angle)
        ax.add_patch(Ellipse((10.3 + 1.3 * cos(r), 52 + 1.3 * sin(r)),
            2.4, .72, angle=angle, facecolor='white', edgecolor=NEUTRAL,
            linewidth=.35, zorder=6))
    ax.add_patch(Circle((10.3, 52), .58, facecolor=FILL_COLORS['marketing'],
        edgecolor=NEUTRAL, linewidth=.35, zorder=7))
    ax.add_patch(FancyBboxPatch((13.4, 46.5), 2.4, 5.3,
        boxstyle='round,pad=0,rounding_size=.25', facecolor='white',
        edgecolor=INK, linewidth=.65, zorder=6))
    ax.plot([12.7, 16.5], [46.2, 46.2], lw=.65, color=INK, zorder=6)
    flame = Path([(14.6, 55.3), (12.5, 52.9), (14.3, 51.7), (14.7, 52.4),
                  (16.1, 53.3), (15.3, 54.5), (14.6, 55.3)],
                 [Path.MOVETO] + [Path.CURVE4] * 6)
    ax.add_patch(PathPatch(flame, facecolor=COLORS['mourning'],
        edgecolor='none', zorder=7))
    for artist in ax.get_children():
        if artist not in original_artists:
            artist.set_transform(Affine2D().translate(0, 1.9) + ax.transData)


def fixed_authors(ax):
    """五色图标表示作者类型异质，图标数不编码人群比例。"""
    for x, category in zip([90.3, 93.9, 97.5, 101.1, 104.7], CATS):
        ax.add_patch(Circle((x, 31.8), .82, facecolor=FILL_COLORS[category],
            edgecolor=INK, linewidth=.4, zorder=6))
        ax.add_patch(FancyBboxPatch((x - 1.1, 28.2), 2.2, 2.4,
            boxstyle='round,pad=0,rounding_size=.6', facecolor=FILL_COLORS[category],
            edgecolor=INK, linewidth=.4, zorder=6))
    text(ax, 97.5, 25, 'Fixed author types', size=8.5)


def node_icons(ax):
    """信息流与成功发布图标；选择性表达核心由公式和门槛直接显示。"""
    ax.add_patch(FancyBboxPatch((76.5, 46.7), 5.3, 6.1,
        boxstyle='round,pad=0,rounding_size=.45', facecolor='white',
        edgecolor=INK, linewidth=.5, zorder=6))
    for y, category in zip([51.7, 50.7, 49.7, 48.7, 47.7], CATS):
        ax.plot([77.5, 80.8], [y, y], color=COLORS[category], lw=.85, zorder=7)
    for x, y in [(81, 17), (82.2, 15.8)]:
        ax.add_patch(FancyBboxPatch((x, y), 4.4, 4.7,
            boxstyle='round,pad=0,rounding_size=.35', facecolor='white',
            edgecolor=INK, linewidth=.5, zorder=6))
    ax.plot([83.1, 84.1, 85.8], [18, 17.2, 19.1],
            color=COLORS['other'], lw=.85, zorder=7)


def main():
    fig = plt.figure(figsize=(mm(WIDTH), mm(HEIGHT)))
    left = fig.add_axes([2 / WIDTH, 8 / HEIGHT, 56 / WIDTH, 52 / HEIGHT])
    right = fig.add_axes([64 / WIDTH, 8 / HEIGHT, 114 / WIDTH, 52 / HEIGHT])
    for ax, xlim in [(left, (2, 58)), (right, (64, 178))]:
        ax.set_xlim(*xlim)
        ax.set_ylim(8, 60)
        ax.set_axis_off()
    headings = [text(left, 2, 63.5, '(a) Platform data analysis', size=10.5, bold=True, ha='left'),
                text(right, 64, 63.5, '(b) Simulation modeling', size=10.5, bold=True, ha='left')]

    box(left, 3, 46, 53, 13, fill=FILL_COLORS['marketing'])
    mourning_icon(left)
    text(left, 36.2, 52.5, 'Douyin · Rednote', size=9.2, bold=True)
    box(left, 9, 33.5, 41, 8)
    text(left, 29.5, 37.5, 'Content coding')
    arrow(left, [(29.5, 46), (29.5, 41.5)])
    for x, label in [(15.5, 'Temporal\npatterns'), (43.5, 'Platform\ndifferences')]:
        box(left, x - 12.5, 16, 25, 11)
        text(left, x, 21.5, label, size=8.8)
        arrow(left, [(29.5, 33.5), (29.5, 30.5), (x, 30.5), (x, 27)])

    arrow(left, [(29.5, 13.3), (67, 13.3), (67, 45.5), (73, 45.5)], color=NEUTRAL)
    text(right, 64, 55, 'Mechanism\nquestions', size=8, color='#59636B')

    box(right, 73, 37, 41, 17, accent=COLORS['education'])
    text(right, 98.5, 49.3, 'Visibility\nconfiguration', size=9.5, bold=True,
         color=COLORS['education'])
    text(right, 93.5, 40.3, 'Random · Chronological\nInterest-based', size=8)

    # 原生公式为选择性表达主卡；门槛沿用实际参数activity，不新增机制符号。
    box(right, 121, 22.5, 56, 36.5, accent=COLORS['mourning'])
    text(right, 149, 55.8, 'Selective expression', size=10, bold=True)
    text(right, 149, 50.7, r'$U_{it}=B_i+R_{it}(D_{it}-B_i)$', size=12)
    for y, label in [
        (45.7, 'U  Expression utility'),
        (42.4, 'B  Baseline expression utility'),
        (39.1, 'D  Opinion-climate response'),
        (35.8, 'R  Exposure-dependent attention weight'),
    ]:
        text(right, 124, y, label, size=8, ha='left')
    text(right, 125.5, 30.5, r'$U_{it}\geq\mathrm{activity}_i$', size=12, ha='left')
    arrow(right, [(149.8, 30.5), (152.4, 30.5)], color=INK, width=.8, head=6.5).set_zorder(7)
    text(right, 164, 30.5, 'LLM generation', size=8)
    text(right, 149, 25.8, 'activity: Fixed individual threshold', size=8)

    box(right, 78, 8.5, 42, 14, accent=COLORS['other'])
    text(right, 102.5, 18.4, 'Content\nrecirculation', size=9.5, bold=True,
         color=COLORS['other'])
    text(right, 99, 11.4, 'Hourly return', size=8.5)
    node_icons(right)
    fixed_authors(right)
    arrow(right, [(104, 54), (112, 63), (132, 64), (145, 59)],
          color=COLORS['education'], width=2, head=9, curved=True)
    arrow(right, [(160, 22.5), (167, 9), (137, 10), (120, 15.5)],
          color=COLORS['mourning'], width=2, head=9, curved=True)
    arrow(right, [(78, 15.5), (72, 17), (73, 31), (82, 37)],
          color=COLORS['other'], width=2, head=9, curved=True)

    transform = Affine2D().scale(1 / WIDTH, 1 / HEIGHT) + fig.transFigure
    for vertices in [
        [(15.5, 16), (15.5, 13.3), (43.5, 13.3), (43.5, 16)],
        [(29.5, 13.3), (29.5, 6.7), (99, 6.7), (99, 8.5)],
    ]:
        fig.add_artist(PathPatch(Path(vertices, [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1)),
            transform=transform, facecolor='none', edgecolor=NEUTRAL, linewidth=.7,
            joinstyle='round', capstyle='round', clip_on=False, zorder=1))
    fig.add_artist(FancyArrowPatch((90, 6.7), (90, 5.1), transform=transform,
        arrowstyle='-|>', mutation_scale=5.5, linewidth=.7, color=NEUTRAL,
        shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
    fig.text(.5, 2.8 / HEIGHT, 'Public representation reorganization',
        ha='center', va='center', fontsize=10, fontweight='bold', color=INK)

    fig.canvas.draw()
    exemptions = [{'panels': ['a', 'b'], 'checks': ['panel-width'],
        'reason': 'Complementary evidence modules intentionally use 56:114 mm content widths; the circular mechanism is the hero.'}]
    report = require_matplotlib_panel_alignment(fig, axes=[left, right], panel_ids=['a', 'b'],
        row_groups=[{'id': 'complementary-modules', 'panels': ['a', 'b']}],
        exemptions=exemptions, tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
    renderer = fig.canvas.get_renderer()
    for entry, artist in zip(report['layout']['panels'], headings):
        bb = artist.get_window_extent(renderer)
        entry['panel_label'] = entry['id']
        entry['panel_label_anchor_pt'] = [bb.x0 * 72 / fig.dpi, bb.y0 * 72 / fig.dpi]
    report = audit_layout_manifest(report['layout'], require_panel_labels=True,
        tolerance_pt=1.5, gutter_tolerance_pt=1.5)
    assert report['verdict'] == 'PASS', report
    write_json_report(report, QA / f'{STEM}.alignment.json')
    boxes = []
    for artist in fig.findobj(plt.Text):
        if not artist.get_visible() or not artist.get_text():
            continue
        bb = artist.get_window_extent(renderer)
        if bb.width and bb.height:
            boxes.append({'text': artist.get_text(), 'font_pt': artist.get_fontsize(),
                'bbox_px': list(bb.extents), 'outside_canvas': bool(bb.x0 < -.5 or bb.y0 < -.5
                    or bb.x1 > fig.bbox.width + .5 or bb.y1 > fig.bbox.height + .5)})
    assert not any(item['outside_canvas'] for item in boxes)
    assert min(item['font_pt'] for item in boxes) >= 8
    for fmt in ['svg', 'pdf', 'png']:
        fig.savefig(OUT / f'{STEM}.{fmt}', format=fmt, dpi=600)
    svg = OUT / f'{STEM}.svg'
    svg.write_text(svg.read_text().replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', 1))
    (QA / f'{STEM}.build.json').write_text(json.dumps({
        'size_mm': [WIDTH, HEIGHT], 'font': 'Arial', 'minimum_font_pt': min(b['font_pt'] for b in boxes),
        'word_count': sum(len(b['text'].split()) for b in boxes), 'text_objects': boxes,
        'backend': 'Python/Matplotlib', 'axes_mm': [[2, 8, 56, 52], [64, 8, 114, 52]],
        'outputs': {fmt: hashlib.sha256((OUT / f'{STEM}.{fmt}').read_bytes()).hexdigest()
                    for fmt in ['svg', 'pdf', 'png']},
    }, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(f'Saved {STEM}: 180×66 mm, SVG/PDF/PNG')


if __name__ == '__main__':
    main()
