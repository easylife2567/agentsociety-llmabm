"""图5结构候选A：五列共享种子行的配对图谱，底行保留条件均值。"""
from style_rework_common import *


def main():
    data = data_table()
    fig = plt.figure(figsize=(180 / 25.4, 90 / 25.4))
    widths = [.155] * 5
    starts = [.074 + i * .182 for i in range(5)]
    ranges = [(20, [0, 10, 20]), (70, [0, 20, 40, 60]),
              (65, [0, 20, 40, 60]), (90, [0, 25, 50, 75]),
              (30, [0, 10, 20, 30])]
    means = []
    axes = []
    for i, (spec, start, width, scale) in enumerate(zip(SPECS, starts, widths, ranges)):
        letter, condition, window, metric, unit, factor = spec
        pair = paired(data, letter, condition, factor)
        assert list(pair.index) == list(range(10))
        ax = fig.add_axes([start, .205, width, .560])
        axes.append(ax)
        # 相同seed在五列共享一行；线段仅连接该seed的两个条件。
        for seed in range(10):
            y = 10 - seed
            values = pair.loc[seed, ['full', condition]].to_numpy(float)
            ax.axhline(y, color='#E9EDE5', lw=.42, zorder=0)
            ax.plot(values, [y, y], color='#AEB9A7', lw=.85,
                    solid_capstyle='round', zorder=2)
            ax.scatter(values[0], y, marker='o', s=14, color=FOREST,
                       edgecolor='white', linewidth=.30, zorder=4)
            ax.scatter(values[1], y, marker='D', s=14, color=COLORS[condition],
                       edgecolor=CHARCOAL, linewidth=.30, zorder=4)

        # 均值独立成底行，不与种子观测混放，也不添加置信区间。
        mean_y = -.35
        mean_values = pair.mean().to_numpy(float)
        ax.axhline(.28, color='#B9C3B2', lw=.60, zorder=1)
        ax.plot(mean_values, [mean_y, mean_y], color=CHARCOAL, lw=1.10, zorder=3)
        for value, cond, marker in zip(mean_values, ['full', condition], ['o', 'D']):
            ax.scatter(value, mean_y, marker=marker, s=27,
                       color=COLORS[cond], edgecolor=CHARCOAL, linewidth=.40, zorder=5)
            ax.text(value, -.80, f'{value:.1f}', ha='center', va='top',
                    fontsize=8, color=CHARCOAL, fontweight='bold')
            means.append({'panel': letter, 'condition': cond, 'mean': float(value),
                          'unit': unit, 'paired_seeds': len(pair)})
        upper, ticks = scale
        ax.set_xlim(0, upper)
        ax.set_xticks(ticks)
        ax.set_xlabel(unit, fontsize=8, labelpad=3)
        ax.set_ylim(-1.65, 10.60)
        ax.set_yticks(list(range(10, 0, -1)) + [mean_y])
        if i == 0:
            ax.set_yticklabels([str(seed) for seed in range(10)] + ['Mean'])
            ax.tick_params(axis='y', length=0, pad=6)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis='y', length=0)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='x', length=3, width=.6, pad=3)
        # 分图、干预、指标、窗口分层排列，保持横向图谱的统一表头。
        fig.text(start, .963, f'Fig. 5{letter}', ha='left', va='center',
                 fontsize=9.5, fontweight='bold', color=FOREST)
        fig.text(start + width, .963, LABELS[condition], ha='right', va='center',
                 fontsize=8, fontweight='bold', color=CHARCOAL)
        fig.text(start + width / 2, .882, metric, ha='center', va='center',
                 fontsize=8.5, color=CHARCOAL, linespacing=1.1)
        fig.text(start + width / 2, .800, window, ha='center', va='center',
                 fontsize=8, color=FOREST)

    fig.text(.013, .786, 'Seed', fontsize=8, fontweight='bold',
             color=FOREST, ha='left', va='center')
    handles = [
        Line2D([], [], ls='none', marker='o', markersize=3.8,
               markerfacecolor=FOREST, markeredgecolor='white',
               markeredgewidth=.3, label='Full'),
        Line2D([], [], ls='none', marker='D', markersize=3.8,
               markerfacecolor='#A7B89F', markeredgecolor=CHARCOAL,
               markeredgewidth=.3, label='Intervention'),
        Line2D([], [], color='#AEB9A7', lw=.85, label='Same-seed pair'),
    ]
    fig.legend(handles=handles, loc='lower center', ncol=3,
               bbox_to_anchor=(.53, .012), fontsize=8,
               handlelength=1.8, handletextpad=.5, columnspacing=1.4)
    statistics = {'layout': 'five columns with shared seed rows and a separate mean row',
                  'seed_rows': list(range(10)), 'condition_means': means,
                  'axis_limits': {spec[0]: [0, scale[0]] for spec, scale in zip(SPECS, ranges)},
                  'replication_unit': 'same-seed Full/intervention pair'}
    save(fig, 'figure_05_seed_atlas_v1', Path(__file__), statistics)


if __name__ == '__main__':
    main()
