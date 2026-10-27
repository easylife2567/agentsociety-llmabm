"""原口径的10seed主实验稳定性图；只读派生表，不读取或修改消融。"""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'data'
CHARTS = BASE / 'charts'
COLORS = {'random': '#737373', 'chronological': '#0F4D92', 'interest': '#B64342'}
LABELS = {'random': 'Random', 'chronological': 'Chronological', 'interest': 'Interest'}
COHORTS = [('old3', 'Old 3 (request 260910)'), ('new7', 'New 7 (response 261017)'), ('all10', 'All 10 (primary analysis)')]
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
    'svg.fonttype': 'none', 'pdf.fonttype': 42, 'font.size': 10, 'axes.titlesize': 11,
    'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False, 'axes.linewidth': 1.1})


def save(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(CHARTS / f'{name}.{ext}', dpi=240, bbox_inches='tight')
    plt.close(fig)


def main():
    rows = pd.read_csv(DATA / 'seed10_runs.csv')
    means = pd.read_csv(DATA / 'seed10_arm_summary.csv')
    weekly = pd.read_csv(DATA / 'seed10_weekly_summary.csv')
    handles = [Line2D([0], [0], color=c, lw=2, label=LABELS[a]) for a, c in COLORS.items()]
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.3), sharey=True)
    for index, (ax, (cohort, title)) in enumerate(zip(axes, COHORTS)):
        ax.set_title(f'{chr(97 + index)}  {title}', loc='left')
        ax.axvspan(19, 22, color='#F4EEE4', zorder=0)
        ax.axvline(13, color='#A5655B', ls=':', lw=1)
        for arm, color in COLORS.items():
            part = weekly[(weekly.cohort == cohort) & (weekly.arm == arm)].sort_values('week')
            x = part.week.str[-2:].astype(int).to_numpy()
            ax.fill_between(x, part.agent_supply_meme_min.to_numpy(), part.agent_supply_meme_max.to_numpy(),
                            color=color, alpha=.12, linewidth=0)
            ax.plot(x, part.agent_supply_meme_mean, color=color, lw=2, marker='o', ms=3)
        ax.set(xlabel='ISO week in 2026', xlim=(12, 22), ylim=(0, 20), xticks=[12, 13, 15, 17, 19, 22], yticks=[0, 5, 10, 15, 20])
        ax.grid(axis='y', alpha=.18)
    axes[0].set_ylabel('Weekly posts by meme-type authors')
    fig.legend(handles=handles, loc='lower center', ncol=3, bbox_to_anchor=(.5, -.01))
    fig.text(.5, -.06, 'Lines: seed means; bands: observed seed ranges (not confidence intervals). All 10 includes Old 3 and New 7.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .07, 1, 1)); save(fig, 'chart_01_seed10_trajectories')

    metrics = [('late_meme_posts', 'Late meme-author posts', 1, 'Posts per run'),
               ('late_meme_share', 'Meme share of author supply', 100, 'Percent'),
               ('own_share', 'Meme users: meme feed slots', 100, 'Percent of 760 slots'),
               ('meme_post_rate', 'Meme users: posting rate', 100, 'Percent of 76 opportunities'),
               ('cross_generated_share', 'Other users: generated meme slots', 100, 'Percent of 3240 slots')]
    fig, axes = plt.subplots(2, 3, figsize=(14.2, 8.3))
    for index, (ax, (metric, title, scale, ylabel)) in enumerate(zip(axes.flat, metrics)):
        ax.set_title(f'{chr(97 + index)}  {title}', loc='left')
        for j, (cohort, _) in enumerate(COHORTS):
            selected = rows if cohort == 'all10' else rows[rows.cohort == cohort]
            for k, (arm, color) in enumerate(COLORS.items()):
                x = j + (k - 1) * .22
                part = selected[selected.arm == arm].sort_values('seed')
                offsets = np.linspace(-.045, .045, len(part))
                ax.scatter(x + offsets, part[metric] * scale, s=18, facecolors='none', edgecolors=color, linewidth=.8, alpha=.65, zorder=2)
                mean = means[(means.cohort == cohort) & (means.arm == arm) & (means.metric == metric)].iloc[0]
                ax.errorbar(x, mean['mean'] * scale, yerr=np.array([[mean['mean'] - mean.ci_low], [mean.ci_high - mean['mean']]]) * scale,
                            fmt='o', color=color, capsize=3, ms=5, lw=1.3, zorder=3)
        ax.set(xticks=[0, 1, 2], xticklabels=['Old 3', 'New 7', 'All 10'], ylabel=ylabel, ylim=(0, None))
        ax.grid(axis='y', alpha=.18)
    axes.flat[-1].axis('off')
    axes.flat[-1].legend(handles=handles, loc='upper left', fontsize=12)
    axes.flat[-1].text(0, .60, 'W19-W22, original denominators\n\nOpen dots: individual seeds\nSolid dots: arithmetic seed means\nWhiskers: approximate 95% t intervals\n\nAll 10 reuses the same 3 + 7 seeds.\nVersions treated as equivalent for this study.', transform=axes.flat[-1].transAxes, fontsize=10, linespacing=1.4, va='top')
    fig.tight_layout(); save(fig, 'chart_02_seed10_model_cohorts')

    fig, axes = plt.subplots(1, 2, figsize=(12.7, 4.7))
    pairs = [('interest', 'random', COLORS['interest']), ('chronological', 'random', COLORS['chronological']), ('chronological', 'interest', '#80558C')]
    for index, (ax, metric, scale, title) in enumerate(zip(axes, ['late_meme_posts', 'late_meme_share'], [1, 100], ['Late meme-author post difference', 'Late meme-share difference (pp)'])):
        ax.set_title(f'{chr(97 + index)}  {title}', loc='left')
        ax.axhline(0, color='#333333', lw=1)
        ax.axvspan(-.5, 2.5, color='#ECECEC', zorder=0)
        ax.axvline(2.5, color='#999999', ls=':', lw=1)
        wide = rows.pivot(index='seed', columns='arm', values=metric).sort_index()
        for a, b, color in pairs:
            ax.plot(wide.index, (wide[a] - wide[b]) * scale, color=color, marker='o', lw=1.4, ms=4,
                    label=f'{LABELS[a]} - {LABELS[b]}')
        ax.set(xlabel='Paired seed index', xticks=range(10), xlim=(-.5, 9.5))
        ax.grid(axis='y', alpha=.18)
    axes[0].set_ylabel('Posts'); axes[1].set_ylabel('Percentage points')
    fig.legend(*axes[0].get_legend_handles_labels(), loc='lower center', ncol=3, bbox_to_anchor=(.5, -.01))
    fig.text(.5, -.06, 'Grey block: Old 3; white block: New 7. Lines connect seed indices, not time. Each contrast uses the same seed and model cohort.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .07, 1, 1)); save(fig, 'chart_03_seed10_paired_seeds')
    print(json.dumps({'charts': 3, 'exports': 6, 'backend': matplotlib.get_backend()}))


if __name__ == '__main__':
    main()
