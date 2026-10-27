"""图1：两平台合并的五类周构成与悼念/玩梗周数量。"""
from paper_plot_style import *


def main():
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    pooled = observed.loc[observed.platform.eq('pooled')]
    counts = pooled.pivot(index='week', columns='category', values='count').reindex(columns=CATS)
    assert counts.shape == (18, 5) and not counts.isna().any().any()
    # 合并图先汇总两平台计数，再由当周五类合计计算比例。
    platforms = observed.loc[~observed.platform.eq('pooled')].groupby(['week', 'category'])['count'].sum().unstack().reindex(columns=CATS)
    assert counts.equals(platforms)
    assert int(counts.to_numpy().sum()) == 46602
    shares = counts.div(counts.sum(axis=1), axis=0) * 100
    weeks = counts.index.str[-2:].astype(int).to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(99)))
    fig.subplots_adjust(left=.105, right=.98, top=.86, bottom=.29, wspace=.37)

    axes[0].stackplot(weeks, *(shares[c].values for c in CATS),
        colors=[COLORS[c] for c in CATS], edgecolor='white', linewidth=.35, zorder=2)
    axes[0].set_ylim(0, 100)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    axes[0].yaxis.set_major_formatter(PERCENT)
    axes[0].set_ylabel('Within-week content share (%)')
    panel(axes[0], 1, 'a')

    for category, marker in [('mourning', 'o'), ('meme', 's')]:
        axes[1].plot(weeks, counts[category].values, color=COLORS[category],
            lw=1.7, marker=marker, markersize=3.0, markeredgewidth=0, zorder=4)
    axes[1].set_ylim(0, 5200)
    axes[1].set_yticks([0, 1000, 2000, 3000, 4000, 5000])
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:,.0f}'))
    axes[1].set_ylabel('Posts per week (count)')
    panel(axes[1], 1, 'b')

    for ax in axes:
        week_axis(ax, 5, 22)
        ticks = [5, 7, 9, 11, 13, 15, 17, 19, 22]
        ax.set_xticks(ticks, [f'W{w:02d}' for w in ticks])

    mourning_peak = float(counts.loc['2026-W13', 'mourning'])
    axes[1].annotate(f'{mourning_peak:,.0f}', (13, mourning_peak), (11.8, 4760),
        color=COLORS['mourning'], fontsize=9, ha='right', va='center',
        arrowprops={'arrowstyle':'-', 'color':COLORS['mourning'], 'lw':.75}, zorder=8)
    late_meme = float(counts.loc['2026-W22', 'meme'])
    axes[1].annotate(f'{late_meme:,.0f}', (22, late_meme), (21.6, 3710),
        color=COLORS['meme'], fontsize=9, ha='right', va='center',
        arrowprops={'arrowstyle':'-', 'color':COLORS['meme'], 'lw':.75}, zorder=8)

    handles = category_handles(event=False)
    # 两个焦点类别同时说明右侧曲线的符号，其他类别仅用于堆积构成。
    handles[1] = Line2D([], [], color=COLORS['mourning'], marker='o',
        markersize=3.5, lw=1.6, label=NAMES['mourning'])
    handles[2] = Line2D([], [], color=COLORS['meme'], marker='s',
        markersize=3.5, lw=1.6, label=NAMES['meme'])
    fig.legend(handles=handles, loc='lower center', ncol=5, bbox_to_anchor=(.53, .115),
        columnspacing=1.1, handlelength=1.5)
    fig.legend(handles=[Line2D([], [], color='#263340', ls='--', lw=.95, label=EVENT_LABEL)],
        loc='lower center', bbox_to_anchor=(.53, .034), handlelength=2.2)
    save_figure(fig, 'figure_01_observed_pooled', list(axes), ['1a', '1b'])


if __name__ == '__main__':
    main()
