"""图4：统一小时回流三种策展制度的作者供给轨迹。"""
from paper_plot_style import *


def main():
    weekly = pd.read_csv(DATA / 'weekly_supply.csv')
    assert len(weekly) == 330
    assert not weekly.duplicated(['arm', 'seed', 'week']).any()
    assert all(weekly.groupby(['arm', 'seed']).size() == 11)
    fig, grid = plt.subplots(1, 3, figsize=(mm(180), mm(52)), sharey=True)
    fig.subplots_adjust(left=.09, right=.985, top=.96, bottom=.33, wspace=.26)
    axes = list(grid.flat)
    for ax, arm, letter in zip(axes, ARMS, 'abc'):
        part = weekly.loc[weekly.arm.eq(arm)]
        for cat in CATS:
            values = part.pivot(index='seed', columns='week', values=f'agent_supply_{cat}').sort_index()
            assert values.shape == (10, 11) and not values.isna().any().any()
            weeks = values.columns.str[-2:].astype(int).to_numpy()
            for _, row in values.iterrows():
                ax.plot(weeks, row.to_numpy(), color=COLORS[cat], linewidth=.45,
                        alpha=.18, linestyle=STYLES[cat], zorder=2)
            ax.plot(weeks, values.mean().to_numpy(), color=COLORS[cat],
                    linewidth=1.65, linestyle=STYLES[cat], marker=MARKERS[cat],
                    markersize=2.5, markeredgewidth=0, zorder=4)
        ax.set_ylim(0, 25)
        ax.set_yticks([0, 5, 10, 15, 20, 25])
        if letter == 'a':
            ax.set_ylabel('Successful posts\nper week')
        week_axis(ax, 12, 22, simulation=True)
        ax.set_xlabel('')
        sublabel(fig, ax, f'({letter}) {ARM_NAMES[arm]}')

    fig.text(.5375, .145, 'Simulation week (2026)', ha='center', va='center', fontsize=9)
    shared_legend(fig, author=True)
    save_figure(fig, 'figure_04_simulated_trajectories', axes, list('abc'))


if __name__ == '__main__':
    main()
