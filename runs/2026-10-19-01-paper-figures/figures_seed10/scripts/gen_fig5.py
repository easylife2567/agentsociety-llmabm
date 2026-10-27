"""图5：兴趣制度内B/D/R干预的十种子配对比较，读取冻结长表。"""
from paper_plot_style import *
import math


def main():
    data = pd.read_csv(DATA / 'ablation_seed10_metrics.csv')
    assert len(data) == 100 and set(data.seed) == set(range(10))
    assert not data.duplicated(['panel', 'condition', 'seed']).any()
    specs = [
        ('a', 'W19–W22', 'Total output\n(posts per week)', 5, 'no_b', 'B = 0'),
        ('b', 'W19–W22', 'Memetic-type\nspeaking rate (%)', 20, 'no_d', 'D = 1'),
        ('c', 'W14–W18', 'Overall\nspeaking rate (%)', 20, 'no_r', 'R = 1'),
        ('d', 'W19–W22', 'Memetic-type\nsupply share (%)', 25, 'no_r', 'R = 1'),
        ('e', 'W19–W22', "Memetic content in\nothers’ feeds (%)", 10, 'no_r', 'R = 1'),
    ]
    fig = plt.figure(figsize=(mm(180), mm(112)))
    # 上排三项预设指标，下排两项R干预后的构成与接触指标；不留空白图例格。
    positions = [
        (.095, .57, .235, .34), (.420, .57, .235, .34),
        (.745, .57, .235, .34), (.095, .065, .3975, .34),
        (.5825, .065, .3975, .34),
    ]
    axes = [fig.add_axes(position) for position in positions]
    offsets = np.linspace(-.15, .15, 10)
    colors = ['#667482', '#0072B2']
    markers = ['o', 'D']
    for ax, (letter, window, ylabel, step, condition, label) in zip(axes, specs):
        part = data.loc[data.panel.eq(letter)]
        assert len(part) == 20 and set(part.condition) == {'full', condition}
        assert all(set(group.seed) == set(range(10)) for _, group in part.groupby('condition'))
        factor = 1 if letter == 'a' else 100
        expected = (14, 18) if letter == 'c' else (19, 22)
        assert set(part.week_start.str[-2:].astype(int)) == {expected[0]}
        assert set(part.week_end.str[-2:].astype(int)) == {expected[1]}
        assert np.allclose(part.value, part.numerator / part.denominator)
        # 只为最高数据点及均值数字预留必要空间，避免百分比面板上方过空。
        upper = math.ceil((part.value.max() * factor + step * .23) / .92 / 5) * 5
        for seed, offset in enumerate(offsets):
            pair = part.loc[part.seed.eq(seed)].set_index('condition')
            values = pair.loc[['full', condition], 'value'].to_numpy(float) * factor
            x = np.array([0, 1]) + offset
            ax.plot(x, values, color='#A8B2BD', lw=.65, alpha=.75, zorder=2)
            for xx, yy, color, marker in zip(x, values, colors, markers):
                ax.scatter(xx, yy, marker=marker, s=20, facecolor=color,
                           edgecolor='white', lw=.35, zorder=4)
        for x, cond in enumerate(['full', condition]):
            values = part.loc[part.condition.eq(cond), 'value'] * factor
            mean = values.mean()
            ax.plot([x - .21, x + .21], [mean, mean], color='#17212B', lw=1.75, zorder=5)
            ax.text(x, values.max() + step * .23,
                    f'{mean:.1f}' + ('' if letter == 'a' else '%'),
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')
        ax.set_xlim(-.38, 1.38)
        ax.set_ylim(0, upper)
        ax.set_yticks(np.arange(0, upper + 1e-9, step))
        ax.set_xticks([0, 1], ['Full', label], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=8.5, labelpad=4)
        panel(ax, 5, letter, window)
    # 种子数、配对关系及均值含义放在配套中文图注，图内只保留必要读图元素。
    save_figure(fig, 'figure_05_bdr_ablation', axes,
                [f'Fig. 5{letter}' for letter in 'abcde'])


if __name__ == '__main__':
    main()
