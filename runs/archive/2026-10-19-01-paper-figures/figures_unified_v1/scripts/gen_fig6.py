"""图6：同批完整模型与B/D/R干预的十种子配对比较。"""
from paper_plot_style import *
import math


def main():
    data = pd.read_csv(DATA / 'ablation_metrics.csv')
    assert len(data) == 100 and set(data.seed) == set(range(10))
    assert not data.duplicated(['panel', 'condition', 'seed']).any()
    specs = [
        ('a', 'W19–W22', 'Total output\n(posts per week)', 5, 'no_b', 'B = 0'),
        ('b', 'W19–W22', 'Memetic-type\nspeaking rate (%)', 20, 'no_d', 'D = 1'),
        ('c', 'W14–W18', 'Overall\nspeaking rate (%)', 20, 'no_r', 'R → 1'),
        ('d', 'W19–W22', 'Memetic-type\nsupply share (%)', 25, 'no_r', 'R → 1'),
        ('e', 'W19–W22', "Memetic content in\nothers’ feeds (%)", 10, 'no_r', 'R → 1'),
    ]
    fig = plt.figure(figsize=(mm(180), mm(84)))
    # 上排三面板各跨两列，下排两面板各跨三列，统一外缘与面板高度。
    grid = fig.add_gridspec(2, 6, left=.095, right=.98, bottom=.10,
                           top=.97, wspace=1.20, hspace=.42)
    axes = [fig.add_subplot(grid[0, 0:2]),
            fig.add_subplot(grid[0, 2:4]),
            fig.add_subplot(grid[0, 4:6]),
            fig.add_subplot(grid[1, 0:3]),
            fig.add_subplot(grid[1, 3:6])]
    offsets = np.linspace(-.15, .15, 10)
    for ax, (letter, window, ylabel, step, condition, label) in zip(axes, specs):
        part = data.loc[data.panel.eq(letter)]
        assert len(part) == 20 and set(part.condition) == {'full', condition}
        assert all(set(group.seed) == set(range(10)) for _, group in part.groupby('condition'))
        factor = 1 if letter == 'a' else 100
        expected = (14, 18) if letter == 'c' else (19, 22)
        assert set(part.week_start.str[-2:].astype(int)) == {expected[0]}
        assert set(part.week_end.str[-2:].astype(int)) == {expected[1]}
        assert np.allclose(part.value, part.numerator / part.denominator)
        maximum = part.value.max() * factor
        upper = math.ceil((maximum + step * .46) / 5) * 5
        segments = []
        for seed, offset in enumerate(offsets):
            pair = part.loc[part.seed.eq(seed)].set_index('condition')
            values = pair.loc[['full', condition], 'value'].to_numpy(float) * factor
            x = np.array([0, 1]) + offset
            segments.append((x, values))
            ax.plot(x, values, color='#A7AFB7', lw=.65, alpha=.8, zorder=2)
            for xx, yy, color, marker in zip(x, values,
                    ['#5595D0', '#F6AF4D'], ['o', 'D']):
                ax.scatter(xx, yy, marker=marker, s=19, facecolor=color,
                           edgecolor='white', linewidth=.35, zorder=4, clip_on=False)
        ax.set_xlim(-.45, 1.38)
        ax.set_ylim(0, upper)
        for x, cond in enumerate(['full', condition]):
            values = part.loc[part.condition.eq(cond), 'value'] * factor
            mean = values.mean()
            ax.plot([x - .21, x + .21], [mean, mean], color=INK, lw=1.75, zorder=5)
            # 用文字实际宽度核对其下方所有配对线，避免斜线穿过数字。
            text = ax.text(x, 0, f'{mean:.1f}' + ('' if letter == 'a' else '%'), ha='center', va='bottom', fontsize=8.5, fontweight='bold')
            fig.canvas.draw()
            half_width = text.get_window_extent(fig.canvas.get_renderer()).width / ax.bbox.width * (ax.get_xlim()[1] - ax.get_xlim()[0]) / 2
            local_top = float(values.max())
            for xx, yy in segments:
                lo, hi = max(xx[0], x - half_width), min(xx[1], x + half_width)
                if lo <= hi:
                    local_top = max(local_top, *(yy[0] + (yy[1] - yy[0]) * (v - xx[0]) / (xx[1] - xx[0]) for v in (lo, hi)))
            text.set_position((x, local_top + step * .22))
        ax.set_yticks(np.arange(0, upper + 1e-9, step))
        ax.set_xticks([0, 1], ['Full', label], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9, labelpad=4)
        clean_axis(ax)
        sublabel(fig, ax, f'({letter})')
    save_figure(fig, 'figure_06_bdr_ablation', axes, list('abcde'))


if __name__ == '__main__':
    main()
