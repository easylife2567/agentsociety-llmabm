"""图5两种结构候选的冻结数据、出版样式与原生矢量导出。"""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


OUT = Path(__file__).resolve().parent
FOREST = '#1B3D2E'
CHARCOAL = '#3A3A3A'
OLIVE = '#6B7F5B'
COLORS = {'full': FOREST, 'no_b': '#D4A85A', 'no_d': '#C76A4F', 'no_r': OLIVE}
LABELS = {'full': 'Full', 'no_b': 'B = 0', 'no_d': 'D = 1', 'no_r': 'R = 1'}
SPECS = [
    ('a', 'no_b', 'W19–W22', 'Total output', 'Posts / week', 1),
    ('b', 'no_d', 'W19–W22', 'Memetic-type\nspeaking rate', 'Percent (%)', 100),
    ('c', 'no_r', 'W14–W18', 'Overall\nspeaking rate', 'Percent (%)', 100),
    ('d', 'no_r', 'W19–W22', 'Memetic-type\nsupply share', 'Percent (%)', 100),
    ('e', 'no_r', 'W19–W22', 'Memetic content in\nothers’ feeds', 'Percent (%)', 100),
]
plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9, 'axes.labelsize': 8, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.linewidth': .6, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': CHARCOAL, 'text.color': CHARCOAL, 'axes.labelcolor': CHARCOAL,
    'xtick.color': CHARCOAL, 'ytick.color': CHARCOAL, 'legend.frameon': False,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'figure.dpi': 150, 'savefig.dpi': 400, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'text.usetex': False, 'mathtext.fontset': 'stix', 'axes.unicode_minus': True,
    'svg.hashsalt': 'ica2027-figure5-structure-rework-v1',
})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_table():
    data = pd.read_csv(OUT / 'source_data/ablation_seed10_metrics.csv')
    assert len(data) == 100 and not data.duplicated(['panel', 'condition', 'seed']).any()
    assert np.allclose(data.value, data.numerator / data.denominator)
    for letter, condition, window, *_ in SPECS:
        part = data[data.panel.eq(letter)]
        assert len(part) == 20 and set(part.condition) == {'full', condition}
        assert all(set(group.seed) == set(range(10)) for _, group in part.groupby('condition'))
    return data


def paired(data, letter, condition, factor):
    part = data[data.panel.eq(letter)].pivot(index='seed', columns='condition', values='value')
    return part[['full', condition]].sort_index() * factor


def save(fig, stem, script, statistics):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    outside = []
    for label in fig.findobj(plt.Text):
        if label.get_visible() and label.get_text():
            box = label.get_window_extent(renderer)
            if box.width and box.height and (box.x0 < -.5 or box.y0 < -.5 or
                    box.x1 > fig.bbox.width + .5 or box.y1 > fig.bbox.height + .5):
                outside.append(label.get_text())
    for ext in ('svg', 'pdf', 'png'):
        fig.savefig(OUT / f'{stem}.{ext}', format=ext, dpi=400,
                    metadata={'Creator': 'ICA2027 Figure 5 structure candidates'} if ext == 'pdf' else None)
    p = OUT / f'{stem}.svg'
    p.write_text(p.read_text().replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', 1))
    record = {'stem': stem, 'size_mm': [round(v * 25.4, 2) for v in fig.get_size_inches()],
              'trial_only': True, 'paired_seeds': 10, 'source_rows': 100,
              'source_csv_sha256': sha(OUT / 'source_data/ablation_seed10_metrics.csv'),
              'script_sha256': sha(script), 'common_style_sha256': sha(Path(__file__)),
              'outside_canvas': outside, 'statistics': statistics,
              'outputs': {ext: sha(OUT / f'{stem}.{ext}') for ext in ('svg', 'pdf', 'png')}}
    (OUT / 'qa' / f'{stem}.build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(f'Saved {stem}: SVG/PDF/PNG')
