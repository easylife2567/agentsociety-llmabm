"""图4：10个配对种子的接触、参与及生成帖再展示，读取冻结主实验表。"""
from paper_plot_style import *


def main():
    data = pd.read_csv(DATA / 'seed10_runs.csv')
    assert len(data) == 30
    assert all(set(data.loc[data.arm.eq(arm), 'seed']) == set(range(10)) for arm in ARMS)
    assert data[['arm', 'seed']].duplicated().sum() == 0
    specs = [
        ('own_share', 'Same-type feed items (%)', 55, 10),
        ('meme_post_rate', 'Successful posts /\nopportunities (%)', 80, 20),
        ('cross_generated_share', "Generated memetic posts /\nother authors' feed items (%)", 35, 10),
    ]
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(mm(180), mm(98)))
    fig.subplots_adjust(left=.165, right=.975, bottom=.265, top=.80, wspace=.28)
    for ax, letter, (metric, label, upper, step) in zip(axes, 'abc', specs):
        for y, arm in zip([2, 1, 0], ARMS):
            sample = data.loc[data.arm.eq(arm)].sort_values('seed')
            values = sample[metric].to_numpy() * 100
            assert len(values) == 10 and np.isfinite(values).all()
            # 固定纵向位移保留十个真实种子；不增加虚构的不确定性区间。
            ax.scatter(values, y + np.linspace(-.22, .22, 10), s=17,
                       color=ARM_COLORS[arm], edgecolor='white', linewidth=.35,
                       zorder=3, clip_on=False)
            mean = float(values.mean())
            ax.plot([mean, mean], [y - .23, y + .23], color='#17212B', lw=1.5,
                    solid_capstyle='butt', zorder=4)
            ax.text(mean + upper * .035, y + .31, f'{mean:.1f}%',
                    ha='left', va='bottom', fontsize=8.5, fontweight='bold',
                    color='#17212B')
        ax.set_xlim(-upper * .025, upper)
        ax.set_ylim(-.48, 2.62)
        ax.set_xticks(np.arange(0, upper + .01, step))
        ax.set_yticks([2, 1, 0], [ARM_NAMES[a] for a in ARMS])
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel(label, fontsize=8.5, labelpad=7)
        panel(ax, 4, letter)
        ax.grid(axis='y', visible=False)
        ax.grid(axis='x', color='#DFE4E9', lw=.45)
    axes[0].set_ylabel('Curation regime', labelpad=8)
    fig.text(.975, .93, 'W19–W22 · n = 10 seeds per regime', ha='right',
             va='center', fontsize=9)
    handles = [
        Line2D([], [], marker='o', color='none', markerfacecolor='#667482',
               markeredgecolor='white', markersize=4.5, label='Individual seed'),
        Line2D([], [], marker='|', color='none', markeredgecolor='#17212B',
               markeredgewidth=1.5, markersize=12, label='Arithmetic mean'),
    ]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.57, .035),
               ncol=2, handletextpad=.65, columnspacing=2.0, fontsize=8.5)
    save_figure(fig, 'figure_04_feedback_exposure', list(axes), ['Fig. 4a', 'Fig. 4b', 'Fig. 4c'])


if __name__ == '__main__':
    main()
