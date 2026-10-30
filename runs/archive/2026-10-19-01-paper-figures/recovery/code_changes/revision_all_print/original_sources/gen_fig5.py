"""图5：统一小时回流主实验的接触、参与及跨群体再展示。"""
from paper_plot_style import *


def main():
    data = pd.read_csv(DATA / 'feedback_runs.csv')
    assert len(data) == 30 and not data.duplicated(['arm', 'seed']).any()
    assert all(set(data.loc[data.arm.eq(arm), 'seed']) == set(range(10)) for arm in ARMS)
    specs = [
        ('own_share', 'Same-type feed\nitems (%)', 55, 10,
         'own_numerator', 'own_denominator', 760),
        ('meme_post_rate', 'Successful posts /\nopportunities (%)', 80, 20,
         'meme_post_numerator', 'meme_post_denominator', 76),
        ('cross_generated_share', "Generated memetic posts /\nother authors' feed items (%)", 35, 10,
         'cross_generated_numerator', 'cross_generated_denominator', 3240),
    ]
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(mm(180), mm(74)))
    # 编号位于绘图区内，底部只容纳刻度和两行指标名称。
    fig.subplots_adjust(left=.17, right=.975, bottom=.22, top=.97, wspace=.26)
    offsets = np.linspace(-.18, .18, 10)
    for ax, letter, (metric, xlabel, upper, step, numerator, denominator, expected) in zip(axes, 'abc', specs):
        assert data[denominator].eq(expected).all()
        assert np.allclose(data[metric], data[numerator] / data[denominator])
        for y, arm in zip([2, 1, 0], ARMS):
            sample = data.loc[data.arm.eq(arm)].sort_values('seed')
            values = sample[metric].to_numpy() * 100
            assert len(values) == 10 and np.isfinite(values).all()
            assert values.min() >= 0 and values.max() < upper
            ax.scatter(values, y + offsets, s=17, facecolor=ARM_COLORS[arm],
                       edgecolor='white', linewidth=.35, zorder=4, clip_on=False)
            mean = float(values.mean())
            ax.plot([mean, mean], [y - .23, y + .23], color=INK,
                    linewidth=1.7, solid_capstyle='butt', zorder=5)
            label_x = max(mean, upper * .025) if arm == 'random' else mean
            ax.text(label_x, y + .29, f'{mean:.1f}%',
                    ha='left' if arm == 'random' else 'center', va='bottom', fontsize=8.5, color=INK)
        ax.set_xlim(-upper * .025, upper)
        ax.set_ylim(-.45, 2.78)
        ax.set_xticks(np.arange(0, upper + 1e-9, step))
        ax.set_yticks([2, 1, 0], [ARM_NAMES[a] for a in ARMS])
        ax.set_xlabel(xlabel, fontsize=8.5, labelpad=7)
        clean_axis(ax, grid='x')
        ax.tick_params(axis='y', length=0)
        sublabel(fig, ax, f'({letter})', .06)
    axes[0].set_ylabel('Curation regime', labelpad=9)
    save_figure(fig, 'figure_05_feedback_exposure', list(axes), ['a', 'b', 'c'])


if __name__ == '__main__':
    main()
