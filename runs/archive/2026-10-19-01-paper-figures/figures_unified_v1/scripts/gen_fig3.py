"""图3：与图2同色的两平台五类比例堆积面积。"""
from paper_plot_style import *


def main():
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(52)), sharey=True)
    fig.subplots_adjust(left=.105, right=.985, top=.96, bottom=.33, wspace=.22)
    for ax, letter, platform, label in zip(axes, 'ab', ['douyin', 'xiaohongshu'], ['Douyin', 'Rednote']):
        data = observed.loc[observed.platform.eq(platform)]
        counts = data.pivot(index='week', columns='category', values='count').reindex(columns=CATS)
        assert counts.shape == (18, 5) and not counts.isna().any().any()
        assert counts.sum(axis=1).gt(0).all()
        shares = counts.div(counts.sum(axis=1), axis=0) * 100
        original = data.pivot(index='week', columns='category', values='share').reindex(columns=CATS) * 100
        assert np.allclose(shares, original) and np.allclose(shares.sum(axis=1), 100)
        weeks = shares.index.str[-2:].astype(int).to_numpy()
        ax.stackplot(weeks, *(shares[cat].to_numpy() for cat in CATS), colors=[FILL_COLORS[cat] for cat in CATS], alpha=1.0, edgecolor='white', linewidth=.35, zorder=2)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.yaxis.set_major_formatter(PERCENT)
        if letter == 'a':
            ax.set_ylabel('Within-week\ncontent share (%)')
        week_axis(ax)
        ax.set_xlabel('')
        sublabel(fig, ax, f'({letter}) {label}')
    fig.text(.545, .145, 'Publication week (2026)', ha='center', va='center', fontsize=9)
    shared_legend(fig, area=True)
    save_figure(fig, 'figure_03_observed_platforms', list(axes), ['a', 'b'])


if __name__ == '__main__':
    main()
