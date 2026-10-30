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
