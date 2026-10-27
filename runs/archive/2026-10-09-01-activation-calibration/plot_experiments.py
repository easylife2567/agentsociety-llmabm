"""离线静态图：绝对供给与份额并列，seed范围不是置信区间。"""
import argparse
import json
import os
from pathlib import Path
from statistics import mean


def main(out):
    os.environ['MPLCONFIGDIR'] = str(out / 'tmp/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = json.loads((out / 'feedback_evidence.json').read_text())['weekly']
    summary = json.loads((out / 'experiment_summary.json').read_text())['aggregate']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none',
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    colors = {'random': '#0072B2', 'chronological': '#D55E00', 'interest': '#009E73'}
    marks = {'random': 'o', 'chronological': 's', 'interest': '^'}
    for arm in colors:
        weekly = [[r['agent_posts'] for r in rows if r['scale_name'] == 'current' and r['arm'] == arm
                   and r['week'] == f'2026-W{w}' and r['type'] == 'meme'] for w in range(12, 23)]
        axes[0].plot(range(12, 23), [mean(x) for x in weekly], color=colors[arm], marker=marks[arm], label=arm)
        axes[0].fill_between(range(12, 23), [min(x) for x in weekly], [max(x) for x in weekly], color=colors[arm], alpha=.1)
        scales = ['half_stress', 'sample_population', 'current', 'unique_authors', 'double_stress']
        values = [100 * next(r['late_supply_share'] for r in summary if r['scale_name'] == s and r['arm'] == arm and r['type'] == 'meme') for s in scales]
        axes[1].plot(range(5), values, color=colors[arm], marker=marks[arm], label=arm)
    axes[0].set(title='Current B: absolute meme supply', xlabel='ISO week, 2026', ylabel='Agent posts / week')
    axes[0].set_xticks(range(12, 23))
    axes[0].set_ylim(0, 20)
    axes[1].set(title='Late meme share across calibration conventions', ylabel='Meme / all Agent posts (%)', ylim=(0, 100))
    axes[1].set_xticks(range(5), ['0.5x\nstress', 'sample\npopulation', 'current', 'unique\nauthors', '2x\nstress'])
    axes[1].axhline(19, color='#777777', linestyle=':', label='fixed meme population: 19%')
    for ax in axes:
        ax.grid(axis='y', alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Closed feedback with frozen content; 3 paired input seeds; no LLM')
    fig.text(.02, .015, 'Left band = observed seed range. Right = mean of seed shares, W19-W22. Sample/author alternatives map to identical B.', fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, .94))
    for ext in ('png', 'svg'):
        fig.savefig(out / f'calibration_results.{ext}', dpi=180, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    main(ap.parse_args().output.resolve())
