"""图5森林绿/赭黄风格候选：同一冻结数据，单独输出原生矢量图。"""
from pathlib import Path
import hashlib
import json
import math
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
STEM = 'figure_05_bdr_ablation_forest_v1'
PALETTE = {
    'forest': '#1B3D2E', 'olive': '#6B7F5B', 'sage': '#A7B89F',
    'ochre': '#D4A85A', 'terracotta': '#C76A4F', 'rose': '#D9A5A3',
    'charcoal': '#3A3A3A',
}
CONDITION_COLORS = {
    'full': PALETTE['forest'], 'no_b': PALETTE['ochre'],
    'no_d': PALETTE['terracotta'], 'no_r': PALETTE['olive'],
}
plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9, 'axes.labelsize': 9, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.linewidth': .65, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': PALETTE['charcoal'], 'text.color': PALETTE['charcoal'],
    'axes.labelcolor': PALETTE['charcoal'], 'xtick.color': PALETTE['charcoal'],
    'ytick.color': PALETTE['charcoal'], 'figure.facecolor': 'white',
    'savefig.facecolor': 'white', 'figure.dpi': 150, 'savefig.dpi': 400,
    'svg.fonttype': 'none', 'pdf.fonttype': 42, 'text.usetex': False,
    'mathtext.fontset': 'stix', 'axes.unicode_minus': True,
    'svg.hashsalt': 'ica2027-fig5-forest-style-trial-v1',
})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    data = pd.read_csv(OUT / 'source_data/ablation_seed10_metrics.csv')
    assert len(data) == 100 and set(data.seed) == set(range(10))
    assert not data.duplicated(['panel', 'condition', 'seed']).any()
    assert np.allclose(data.value, data.numerator / data.denominator)
    # 保留原版三项预设指标在上、两项R干预构成指标在下的阅读顺序。
    specs = [
        ('a', 'W19–W22', 'Total output\n(posts per week)', 5, 'no_b', 'B = 0'),
        ('b', 'W19–W22', 'Memetic-type\nspeaking rate (%)', 20, 'no_d', 'D = 1'),
        ('c', 'W14–W18', 'Overall\nspeaking rate (%)', 20, 'no_r', 'R = 1'),
        ('d', 'W19–W22', 'Memetic-type\nsupply share (%)', 25, 'no_r', 'R = 1'),
        ('e', 'W19–W22', 'Memetic content in\nothers’ feeds (%)', 10, 'no_r', 'R = 1'),
    ]
    fig = plt.figure(figsize=(180 / 25.4, 112 / 25.4))
    # 外框含坐标及窗口；白底细线分格对应参考的图版层级。
    cards = [
        (.006, .518, .324, .471), (.339, .518, .324, .471),
        (.672, .518, .322, .471), (.006, .008, .490, .492),
        (.505, .008, .489, .492),
    ]
    positions = [
        (.090, .577, .224, .326), (.423, .577, .224, .326),
        (.756, .577, .222, .326), (.090, .065, .389, .344),
        (.590, .065, .388, .344),
    ]
    axes = []
    means = []
    offsets = np.linspace(-.15, .15, 10)
    for card, position, spec in zip(cards, positions, specs):
        letter, window, ylabel, step, condition, label = spec
        x0, y0, width, height = card
        fig.add_artist(Rectangle((x0, y0), width, height, transform=fig.transFigure,
                                 facecolor='none', edgecolor='#9AAA9C',
                                 linewidth=.55, zorder=0))
        ax = fig.add_axes(position)
        axes.append(ax)
        part = data.loc[data.panel.eq(letter)]
        assert len(part) == 20 and set(part.condition) == {'full', condition}
        assert all(set(group.seed) == set(range(10)) for _, group in part.groupby('condition'))
        factor = 1 if letter == 'a' else 100
        expected = (14, 18) if letter == 'c' else (19, 22)
        assert set(part.week_start.str[-2:].astype(int)) == {expected[0]}
        assert set(part.week_end.str[-2:].astype(int)) == {expected[1]}
        upper = math.ceil((part.value.max() * factor + step * .23) / .92 / 5) * 5
        for seed, offset in enumerate(offsets):
            pair = part.loc[part.seed.eq(seed)].set_index('condition')
            values = pair.loc[['full', condition], 'value'].to_numpy(float) * factor
            x = np.array([0, 1]) + offset
            ax.plot(x, values, color='#B3BDAF', lw=.60, alpha=.82, zorder=2)
            for xx, yy, cond, marker in zip(x, values, ['full', condition], ['o', 'D']):
                ax.scatter(xx, yy, marker=marker, s=20, facecolor=CONDITION_COLORS[cond],
                           edgecolor=PALETTE['charcoal'], lw=.32, zorder=4)
        for x, cond in enumerate(['full', condition]):
            values = part.loc[part.condition.eq(cond), 'value'] * factor
            mean = values.mean()
            ax.plot([x - .21, x + .21], [mean, mean], color=PALETTE['charcoal'],
                    lw=1.65, solid_capstyle='butt', zorder=5)
            ax.text(x, values.max() + step * .23,
                    f'{mean:.1f}' + ('' if letter == 'a' else '%'),
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')
            means.append({'panel': letter, 'condition': cond, 'mean': float(mean)})
        ax.set_xlim(-.38, 1.38)
        ax.set_ylim(0, upper)
        ax.set_yticks(np.arange(0, upper + 1e-9, step))
        ax.set_xticks([0, 1], ['Full', label], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=8.5, labelpad=4)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#E2E7DD', linewidth=.45)
        # 编号与窗口构成克制的标题栏，不嵌入整体图题或说明段落。
        header_y = y0 + height - .029
        fig.text(x0 + .012, header_y, f'Fig. 5{letter}', color=PALETTE['forest'],
                 fontsize=10, fontweight='bold', ha='left', va='center')
        fig.text(x0 + width - .012, header_y, window, color=PALETTE['forest'],
                 fontsize=8.5, ha='right', va='center')

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = []
    for text in fig.findobj(plt.Text):
        if text.get_visible() and text.get_text():
            box = text.get_window_extent(renderer)
            if box.width and box.height:
                labels.append({'text': text.get_text(), 'bbox_px': list(map(float, box.extents)),
                               'outside_canvas': bool(box.x0 < -.5 or box.y0 < -.5 or
                                                      box.x1 > fig.bbox.width + .5 or
                                                      box.y1 > fig.bbox.height + .5)})
    for extension in ('svg', 'pdf', 'png'):
        fig.savefig(OUT / f'{STEM}.{extension}', format=extension, dpi=400,
                    metadata={'Creator': 'ICA2027 Figure 5 forest palette style trial'}
                    if extension == 'pdf' else None)
    svg = OUT / f'{STEM}.svg'
    svg.write_text(svg.read_text().replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', 1))
    record = {
        'figure': STEM, 'date': '2026-10-26', 'trial_only': True,
        'size_mm': [180, 112], 'palette': PALETTE, 'condition_colors': CONDITION_COLORS,
        'source_csv_sha256': sha(OUT / 'source_data/ablation_seed10_metrics.csv'),
        'script_sha256': sha(Path(__file__)), 'panels': [f'Fig. 5{x}' for x in 'abcde'],
        'means': means, 'font': 'Times New Roman', 'base_font_pt': 9,
        'python': platform.python_version(), 'matplotlib': matplotlib.__version__,
        'labels': [item for item in labels if item['outside_canvas']],
        'text_boxes': labels, 'outputs': {ext: sha(OUT / f'{STEM}.{ext}')
                                         for ext in ('svg', 'pdf', 'png')},
    }
    (OUT / 'qa/build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(f'Saved {STEM}: SVG/PDF/PNG')


if __name__ == '__main__':
    main()
