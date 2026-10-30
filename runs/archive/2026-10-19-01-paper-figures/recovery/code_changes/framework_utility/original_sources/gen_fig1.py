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

WIDTH, HEIGHT = 180, 56
QA = OUT / 'qa/framework_density'
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
            artist.set_transform(Affine2D().translate(0, -8.1) + ax.transData)


def fixed_authors(ax):
    """五色图标表示作者类型异质，图标数不编码人群比例。"""
    for x, category in zip([119.3, 122.9, 126.5, 130.1, 133.7], CATS):
        ax.add_patch(Circle((x, 33.8), .82, facecolor=FILL_COLORS[category],
            edgecolor=INK, linewidth=.4, zorder=6))
        ax.add_patch(FancyBboxPatch((x - 1.1, 30.2), 2.2, 2.4,
            boxstyle='round,pad=0,rounding_size=.6', facecolor=FILL_COLORS[category],
            edgecolor=INK, linewidth=.4, zorder=6))
    text(ax, 126.5, 26.3, 'Fixed author types', size=8.5)


def node_icons(ax):
    """信息流、表达和成功发布图标只说明原有节点，不添加观测值。"""
    ax.add_patch(FancyBboxPatch((79, 38.9), 5.3, 6.1,
        boxstyle='round,pad=0,rounding_size=.45', facecolor='white',
        edgecolor=INK, linewidth=.5, zorder=6))
    for y, category in zip([43.9, 42.9, 41.9, 40.9, 39.9], CATS):
        ax.plot([80, 83.3], [y, y], color=COLORS[category], lw=.85, zorder=7)
    ax.add_patch(Circle((141.8, 42.6), .8, facecolor='white',
        edgecolor=INK, linewidth=.5, zorder=6))
    ax.add_patch(FancyBboxPatch((140.6, 39.3), 2.4, 2.3,
        boxstyle='round,pad=0,rounding_size=.55', facecolor='white',
        edgecolor=INK, linewidth=.5, zorder=6))
    bubble = Path([(143.7, 44.5), (147.4, 44.5), (147.4, 42.2),
                   (145.3, 42.2), (144.1, 41.2), (144.1, 42.2),
                   (143.7, 42.2), (143.7, 44.5)],
                  [Path.MOVETO] + [Path.LINETO] * 6 + [Path.CLOSEPOLY])
    ax.add_patch(PathPatch(bubble, facecolor='white', edgecolor=INK,
        linewidth=.5, zorder=6))
    for x, y in [(109, 17), (110.2, 15.8)]:
        ax.add_patch(FancyBboxPatch((x, y), 4.4, 4.7,
            boxstyle='round,pad=0,rounding_size=.35', facecolor='white',
            edgecolor=INK, linewidth=.5, zorder=6))
    ax.plot([111.1, 112.1, 113.8], [18, 17.2, 19.1],
            color=COLORS['other'], lw=.85, zorder=7)


def main():
    fig = plt.figure(figsize=(mm(WIDTH), mm(HEIGHT)))
    # 两模块实际区域等高，左右约三七开；文字字号不随画布收紧而缩小。
    left = fig.add_axes([2 / WIDTH, 8 / HEIGHT, 56 / WIDTH, 42 / HEIGHT])
    right = fig.add_axes([64 / WIDTH, 8 / HEIGHT, 114 / WIDTH, 42 / HEIGHT])
    for ax, xlim in [(left, (2, 58)), (right, (64, 178))]:
        ax.set_xlim(*xlim)
        ax.set_ylim(8, 50)
        ax.set_axis_off()
    headings = [text(left, 2, 53, '(a) Platform data analysis', size=10.5, bold=True, ha='left'),
                text(right, 64, 53, '(b) Simulation modeling', size=10.5, bold=True, ha='left')]

    box(left, 3, 36.8, 53, 11, fill=FILL_COLORS['marketing'])
    mourning_icon(left)
    text(left, 36.2, 42.3, 'Douyin · Rednote', size=9.2, bold=True)
    box(left, 9, 26.7, 41, 7.2)
    text(left, 29.5, 30.3, 'Content coding')
    arrow(left, [(29.5, 36.8), (29.5, 33.9)])
    for x, label in [(15.5, 'Temporal\npatterns'), (43.5, 'Platform\ndifferences')]:
        box(left, x - 12.5, 12.9, 25, 10.6)
        text(left, x, 18.2, label, size=8.8)
        arrow(left, [(29.5, 26.7), (29.5, 25.4), (x, 25.4), (x, 23.5)])

    # 两实证出口汇合后提出机制问题；并非整份经验样本直接输入模型。
    arrow(left, [(29.5, 10.2), (70, 10.2), (70, 38.45), (76, 38.45)], color=NEUTRAL)
    text(right, 62, 27.5, 'Mechanism\nquestions', size=8, color='#59636B')

    box(right, 76, 31.2, 40, 14.5, accent=COLORS['education'])
    text(right, 99, 41.5, 'Visibility\nconfiguration', size=9.5, bold=True,
         color=COLORS['education'])
    text(right, 96, 34.5, 'Random · Chronological\nInterest-based', size=8)
    box(right, 137, 31.2, 40, 14.5, accent=COLORS['mourning'])
    text(right, 160, 41.5, 'Selective\nexpression', size=9.5, bold=True)
    text(right, 157, 34.4, 'LLM post generation', size=8)
    box(right, 106.5, 8.5, 40, 14, accent=COLORS['other'])
    text(right, 130, 18.4, 'Content\nrecirculation', size=9.5, bold=True,
         color=COLORS['other'])
    text(right, 126.5, 11.4, 'Hourly return', size=8.5)
    node_icons(right)
    fixed_authors(right)
    arrow(right, [(104, 45.7), (114, 51), (143, 51), (151, 45.7)],
          color=COLORS['education'], width=2, head=9, curved=True)
    arrow(right, [(162, 31.2), (174, 22), (158, 13), (146.5, 15.5)],
          color=COLORS['mourning'], width=2, head=9, curved=True)
    arrow(right, [(106.5, 15.5), (92, 11), (82, 21), (87, 31.2)],
          color=COLORS['other'], width=2, head=9, curved=True)

    transform = Affine2D().scale(1 / WIDTH, 1 / HEIGHT) + fig.transFigure
    for vertices in [
        [(15.5, 12.9), (15.5, 10.2), (43.5, 10.2), (43.5, 12.9)],
        [(29.5, 10.2), (29.5, 6.7), (126.5, 6.7), (126.5, 8.5)],
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
        'backend': 'Python/Matplotlib', 'axes_mm': [[2, 8, 56, 42], [64, 8, 114, 42]],
        'outputs': {fmt: hashlib.sha256((OUT / f'{STEM}.{fmt}').read_bytes()).hexdigest()
                    for fmt in ['svg', 'pdf', 'png']},
    }, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(f'Saved {STEM}: 180×56 mm, SVG/PDF/PNG')


if __name__ == '__main__':
    main()
