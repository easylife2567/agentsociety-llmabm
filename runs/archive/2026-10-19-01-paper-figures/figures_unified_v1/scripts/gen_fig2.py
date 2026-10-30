"""图2：五类内容周数量堆积与悼念/玩梗数量。"""
from paper_plot_style import *


def main():
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    counts = observed.loc[observed.platform.eq('pooled')].pivot(index='week', columns='category', values='count').reindex(columns=CATS)
    assert counts.shape == (18, 5) and counts.to_numpy().sum() == 46602
    assert counts.ge(0).all().all()
    weeks = counts.index.str[-2:].astype(int).to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(52)))
    fig.subplots_adjust(left=.105, right=.985, top=.96, bottom=.33, wspace=.22)
    ax = axes[0]
    ax.stackplot(weeks, *(counts[cat].to_numpy() for cat in CATS), colors=[FILL_COLORS[cat] for cat in CATS], alpha=1.0, edgecolor='white', linewidth=.35, zorder=2)
    ax.set_ylabel('Posts per week')
    ax.set_ylim(0, 11000)
    ax.set_yticks([0, 2500, 5000, 7500, 10000])
    ax.yaxis.set_major_formatter(COUNT)
    week_axis(ax)
    ax.set_xlabel('')
    sublabel(fig, ax, '(a)')
    ax = axes[1]
    for cat in ['mourning', 'meme']:
        ax.plot(weeks, counts[cat], color=COLORS[cat], linewidth=1.65, linestyle=STYLES[cat], marker=MARKERS[cat], markersize=3, markeredgewidth=0, zorder=4)
    ax.set_ylim(0, 5500)
    ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000])
    ax.yaxis.set_major_formatter(COUNT)
    week_axis(ax)
    ax.set_xlabel('')
    sublabel(fig, ax, '(b)')
    fig.text(.545, .145, 'Publication week (2026)', ha='center', va='center', fontsize=9)
    shared_legend(fig, area=True)
    save_figure(fig, 'figure_02_observed_trends', list(axes), ['a', 'b'])


if __name__ == '__main__':
    main()
