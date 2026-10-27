"""图2：同周同尺度比较两平台五类内容构成。"""
from paper_plot_style import *


def main():
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    fig, axes = plt.subplots(1, 2, figsize=(mm(180), mm(99)))
    # 每幅图右侧保留W22份额标签的空间，两面板轴宽和尺度完全相同。
    fig.subplots_adjust(left=.105, right=.93, top=.86, bottom=.29, wspace=.46)
    for ax, letter, platform, label in zip(axes, 'ab', ['douyin', 'xiaohongshu'], ['Douyin', 'Xiaohongshu']):
        current = observed.loc[observed.platform.eq(platform)]
        counts = current.pivot(index='week', columns='category', values='count').reindex(columns=CATS)
        assert counts.shape == (18, 5) and not counts.isna().any().any()
        shares = counts.div(counts.sum(axis=1), axis=0) * 100
        original = current.pivot(index='week', columns='category', values='share').reindex(columns=CATS) * 100
        assert np.allclose(shares.values, original.values)
        weeks = shares.index.str[-2:].astype(int).to_numpy()
        ax.stackplot(weeks, *(shares[c].values for c in CATS),
            colors=[COLORS[c] for c in CATS], edgecolor='white', linewidth=.35, zorder=2)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.yaxis.set_major_formatter(PERCENT)
        ax.set_ylabel('Within-week content share (%)')
        week_axis(ax, 5, 22)
        ticks = [5, 7, 9, 11, 13, 15, 17, 19, 22]
        ax.set_xticks(ticks, [f'W{w:02d}' for w in ticks])
        panel(ax, 2, letter, label)
        # 标签只标末周玩梗份额，邻接该色带的终点，而非把所有面积贴满数值。
        last = shares.loc['2026-W22']
        center = last['education'] + last['mourning'] + last['meme'] / 2
        ax.annotate(f"{last['meme']:.1f}%", (22, center), (6, 0),
            textcoords='offset points', color=COLORS['meme'],
            fontsize=8, ha='left', va='center', annotation_clip=False)
    fig.legend(handles=category_handles(event=False), loc='lower center', ncol=5,
        bbox_to_anchor=(.53, .115), columnspacing=1.1, handlelength=1.5)
    fig.legend(handles=[Line2D([], [], color='#263340', ls='--', lw=.95, label=EVENT_LABEL)],
        loc='lower center', bbox_to_anchor=(.53, .034), handlelength=2.2)
    save_figure(fig, 'figure_02_observed_platforms', list(axes), ['2a', '2b'])


if __name__ == '__main__':
    main()
