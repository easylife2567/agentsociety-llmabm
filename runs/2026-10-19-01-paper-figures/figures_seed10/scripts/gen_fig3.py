"""图3：十个配对种子的固定作者供给轨迹及晚期供给份额。"""
from paper_plot_style import *


def main():
    weekly = pd.read_csv(DATA / 'seed10_weekly.csv')
    runs = pd.read_csv(DATA / 'seed10_runs.csv')
    assert len(weekly) == 330 and len(runs) == 30
    assert not runs.duplicated(['arm', 'seed']).any()
    assert set(runs.seed) == set(range(10))
    assert all(runs.groupby('arm').size() == 10)
    assert all(weekly.groupby(['arm', 'seed']).size() == 11)

    fig, grid = plt.subplots(2, 2, figsize=(mm(180), mm(128)))
    fig.subplots_adjust(left=.102, right=.975, top=.93, bottom=.17,
                        wspace=.31, hspace=.64)
    axes = list(grid.flat)
    for ax, arm, letter in zip(axes[:3], ARMS, 'abc'):
        current = weekly.loc[weekly.arm.eq(arm)]
        for category in CATS:
            matrix = current.pivot(index='seed', columns='week',
                                   values=f'agent_supply_{category}').sort_index()
            assert matrix.shape == (10, 11) and not matrix.isna().any().any()
            weeks = matrix.columns.str[-2:].astype(int).to_numpy()
            # 每个实际重复均保留；不把seed变化伪装成置信区间。
            for _, row in matrix.iterrows():
                ax.plot(weeks, row.to_numpy(), color=COLORS[category],
                        linewidth=.50, alpha=.20, linestyle=STYLES[category],
                        zorder=2)
            ax.plot(weeks, matrix.mean(axis=0).to_numpy(),
                    color=COLORS[category], linestyle=STYLES[category],
                    linewidth=1.8 if category in ('mourning', 'meme') else 1.35,
                    marker='s' if category == 'meme' else None,
                    markersize=2.4, markeredgewidth=0, zorder=4)
        ax.set_ylim(0, 25)
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.set_ylabel('Successful posts per week')
        week_axis(ax, 12, 22, simulation=True)
        panel(ax, 3, letter, ARM_NAMES[arm])

    ax = axes[3]
    offsets = np.linspace(-.20, .20, 10)
    for pos, arm in enumerate(ARMS):
        group = runs.loc[runs.arm.eq(arm)].sort_values('seed')
        values = group.late_meme_share.to_numpy() * 100
        # 种子排序固定，横向散开仅用于避免重叠，不改变数值。
        ax.scatter(pos + offsets, values, s=17,
                   facecolor=ARM_COLORS[arm], edgecolor='white',
                   linewidth=.35, zorder=4)
        mean = values.mean()
        ax.plot(pos, mean, marker='_', markersize=20, markeredgewidth=1.7,
                color='#17212B', linestyle='none', zorder=5)
        ax.annotate(f'{mean:.1f}%', (pos, mean), xytext=(0, 11),
                    textcoords='offset points', ha='center', va='bottom',
                    fontsize=9, fontweight='bold', zorder=6)
    ax.set_xlim(-.5, 2.5)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(3), ['Random', 'Chronological', 'Interest-based'])
    ax.yaxis.set_major_locator(MultipleLocator(25))
    ax.yaxis.set_major_formatter(PERCENT)
    ax.set_ylabel('Memetic-type supply share')
    ax.set_xlabel('Curation regime')
    panel(ax, 3, 'd', 'W19–W22')

    # 重复说明由中文图注承载；类别与事件分别占一行，收紧底部留白。
    handles = line_handles(author=True)
    fig.legend(handles=handles[:-1], loc='lower center',
               ncol=5, bbox_to_anchor=(.52, .050), fontsize=8,
               handlelength=1.8, columnspacing=1.35)
    fig.legend(handles=handles[-1:], loc='lower center',
               bbox_to_anchor=(.52, .008), fontsize=8, handlelength=2.2)
    save_figure(fig, 'figure_03_simulated_trajectories', axes,
                ['Fig. 3a', 'Fig. 3b', 'Fig. 3c', 'Fig. 3d'])


if __name__ == '__main__':
    main()
