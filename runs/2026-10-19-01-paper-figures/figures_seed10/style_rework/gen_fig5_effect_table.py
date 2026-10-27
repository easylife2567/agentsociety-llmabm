"""图5方案B：五行实际配对差值，右侧并列保留两条件绝对均值。"""
from style_rework_common import *


def main():
    data = data_table()
    fig = plt.figure(figsize=(180 / 25.4, 104 / 25.4))
    ax_a = fig.add_axes((.284, .762, .426, .096))
    ax_rates = fig.add_axes((.284, .130, .426, .580))
    ax_a.set_xlim(-12, 6)
    ax_a.set_ylim(-.5, .5)
    ax_a.set_xticks([-12, -6, 0, 6], ['−12', '−6', '0', '+6'])
    ax_a.xaxis.tick_top()
    ax_a.xaxis.set_label_position('top')
    ax_a.set_xlabel('Change (posts / week)', fontsize=8, labelpad=3)
    ax_rates.set_xlim(-80, 40)
    ax_rates.set_ylim(-.28, 3.28)
    ax_rates.set_xticks([-80, -40, 0, 40], ['−80', '−40', '0', '+40'])
    ax_rates.set_xlabel('Change (percentage points)', fontsize=8.5, labelpad=4)
    for ax in (ax_a, ax_rates):
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.axvline(0, color=FOREST, lw=.85, zorder=1)
        ax.tick_params(axis='x', length=2.5, width=.55)
    ax_a.spines['top'].set_visible(True)
    ax_a.spines['top'].set_linewidth(.5)
    ax_rates.spines['bottom'].set_visible(True)

    # 单位不同的B指标单独给标尺；下四项差值统一为百分点。
    # 两标尺零线对齐，行内实际种子差值与均值分开编码。
    row_y = [.81] + [.130 + (value + .28) / 3.56 * .580 for value in (3, 2, 1, 0)]
    fig.text(.494, .968, 'Intervention − Full', ha='center', va='center',
             color=FOREST, fontsize=9.5, fontweight='bold')
    fig.text(.795, .968, 'Full', ha='center', va='center',
             color=FOREST, fontsize=9, fontweight='bold')
    fig.text(.93, .968, 'Intervention', ha='center', va='center',
             color=FOREST, fontsize=9, fontweight='bold')
    fig.add_artist(Line2D([.264, .979], [.938, .938], transform=fig.transFigure,
                          color=FOREST, lw=.75))
    fig.add_artist(Line2D([.741, .741], [.105, .934], transform=fig.transFigure,
                          color='#C3CCBE', lw=.55))
    statistics = []
    for index, (spec, yy) in enumerate(zip(SPECS, row_y)):
        letter, condition, window, metric, unit, factor = spec
        values = paired(data, letter, condition, factor)
        delta = values[condition] - values['full']
        ax = ax_a if index == 0 else ax_rates
        center = 0 if index == 0 else 4 - index
        offsets = np.linspace(-.20, .20, 10) if index == 0 else np.linspace(-.13, .13, 10)
        ax.hlines(center, *ax.get_xlim(), color='#E2E7DD', lw=.5, zorder=0)
        ax.scatter(delta.to_numpy(), center + offsets, s=19, color=COLORS[condition],
                   edgecolor=CHARCOAL, linewidth=.3, zorder=3)
        ax.scatter(delta.mean(), center, marker='D', s=48, color=CHARCOAL,
                   edgecolor='white', linewidth=.45, zorder=5)
        fig.text(.025, yy + .061, f'Fig. 5{letter}', color=FOREST,
                 fontsize=9, fontweight='bold', ha='left', va='center')
        fig.text(.025, yy - .001, metric, fontsize=8.5, ha='left', va='center',
                 linespacing=1.25)
        window_y = yy - (.04 if index == 0 else .062)
        fig.text(.025, window_y, window, fontsize=8, color='#616A5F',
                 ha='left', va='center')
        for x, cond in ((.795, 'full'), (.93, condition)):
            mean = values[cond].mean()
            display = f'{mean:.1f}' + ('' if index == 0 else '%')
            fig.text(x, yy + .006, display, color=FOREST if cond == 'full' else CHARCOAL,
                     fontsize=10, fontweight='bold', ha='center', va='center')
        fig.text(.93, yy - .029, LABELS[condition], fontsize=8,
                 ha='center', va='center', color=CHARCOAL)
        statistics.append({'panel': letter, 'condition': condition, 'n': 10,
                           'full_mean': float(values['full'].mean()),
                           'intervention_mean': float(values[condition].mean()),
                           'delta_mean': float(delta.mean()), 'delta_values': delta.tolist(),
                           'delta_unit': 'posts per week' if index == 0 else 'percentage points'})
        if index:
            fig.add_artist(Line2D([.024, .979], [yy + .08, yy + .08],
                                  transform=fig.transFigure, color='#E2E7DD', lw=.5))
    handles = [
        Line2D([], [], ls='none', marker='o', color=OLIVE, markeredgecolor=CHARCOAL,
               markeredgewidth=.3, markersize=4, label='Seed-level paired difference'),
        Line2D([], [], ls='none', marker='D', color=CHARCOAL, markersize=4.8,
               label='Mean of 10 pairs'),
    ]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.023, .997),
               ncol=1, fontsize=8, handlelength=1.1, borderaxespad=0, labelspacing=.35)
    save(fig, 'figure_05_effect_table_v1', Path(__file__), statistics)


if __name__ == '__main__':
    main()
