"""从完整所选制度分析周表绘制单seed观察图；不读取或启动运行中的引擎。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


ARMS = ('random', 'chronological', 'interest')
WEEKS = tuple(f'2026-W{week:02d}' for week in range(12, 23))
LATE = set(WEEKS[-4:])
# 沿用项目已有三臂图的颜色，避免与原对照含义不一致。
COLORS = {'random': '#737373', 'chronological': '#0F4D92', 'interest': '#B64342'}
LABELS = {'random': 'Random', 'chronological': 'Chronological', 'interest': 'Interest'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(value):
    return None if value == '' else float(value)


def close(left, right):
    return (left is None and right is None) or (
        left is not None and right is not None and math.isclose(left, right, rel_tol=0, abs_tol=1e-12))


def verified_rows(summary, rows, selection=None):
    """绘图前核对所选制度完整周单元，明确排除中止制度。"""
    arms = ARMS
    expected_scope = 'three-arms-seed0-exploratory-only'
    if selection is not None:
        if selection['selected_algorithms'] != ['random', 'interest'] or selection['excluded_algorithms'] != ['chronological']:
            raise ValueError('绘图selection必须明确只含随机/兴趣')
        arms = ('random', 'interest')
        expected_scope = 'selected-arms-seed0-exploratory-only'
        if summary.get('selected_algorithms') != list(arms) or summary.get('excluded_algorithms') != ['chronological']:
            raise ValueError('绘图selection与已完成分析范围不一致')
    if summary.get('status') != 'complete' or summary.get('scope') != expected_scope:
        raise ValueError('绘图要求所选制度已完整通过分析门禁，并显式传入相同selection')
    if set(summary.get('late_weeks', [])) != LATE:
        raise ValueError('主要窗口不是已冻结W19–W22')
    if len(rows) != len(arms) * 11 or {row['algorithm'] for row in rows} != set(arms):
        raise ValueError('周表不是所选制度×11周')
    metrics = {row['algorithm']: row for row in summary['runs']}
    if set(metrics) != set(arms):
        raise ValueError('汇总没有精确覆盖所选制度')
    grouped = {}
    for arm in arms:
        selected = sorted((row for row in rows if row['algorithm'] == arm), key=lambda row: row['week'])
        if tuple(row['week'] for row in selected) != WEEKS or any(int(row['seed']) != 0 for row in selected):
            raise ValueError('周表存在重复/缺失周或不同seed')
        for row in selected:
            total, meme = int(row['posted_total']), int(row['posted_meme_authors'])
            feed, meme_feed = int(row['feed_total']), int(row['feed_meme_tag'])
            if not (0 <= meme <= total and 0 <= meme_feed <= feed):
                raise ValueError('发帖/曝光计数或分母无效')
            expected_supply = meme / total if total else None
            expected_exposure = meme_feed / feed if feed else None
            if not close(fraction(row['meme_author_share']), expected_supply):
                raise ValueError('玩梗作者供给份额与实际分母不一致')
            if not close(fraction(row['feed_meme_tag_share']), expected_exposure):
                raise ValueError('玩梗标签曝光份额与实际分母不一致')
        late = [row for row in selected if row['week'] in LATE]
        metric = metrics[arm]
        if sum(int(row['posted_total']) for row in selected) != metric['total_posts']:
            raise ValueError('全窗周表与通过门禁的汇总不一致')
        if sum(int(row['posted_meme_authors']) for row in late) != metric['late_meme_posts']:
            raise ValueError('晚期玩梗发帖量与汇总不一致')
        if sum(int(row['posted_total']) for row in late) != metric['late_total_posts']:
            raise ValueError('晚期发帖分母与汇总不一致')
        if sum(int(row['feed_total']) for row in late) != metric['late_exposures']['feed_total']:
            raise ValueError('晚期实际曝光分母与汇总不一致')
        if sum(int(row['feed_meme_tag']) for row in late) != metric['late_exposures']['feed_meme_tag']:
            raise ValueError('晚期玩梗标签曝光量与汇总不一致')
        grouped[arm] = selected
    return grouped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis-dir', type=Path, default=Path(__file__).parent / 'analysis')
    parser.add_argument('--selection', type=Path, help='与分析时相同的显式制度选择修订')
    args = parser.parse_args()
    directory = args.analysis_dir.resolve()
    summary_path, weekly_path = directory / 'summary.json', directory / 'weekly.csv'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    selection_path = args.selection.resolve() if args.selection else None
    selection = json.loads(selection_path.read_text(encoding='utf-8')) if selection_path else None
    if selection_path is not None and summary['source_sha256'].get(str(selection_path)) != digest(selection_path):
        raise ValueError('绘图selection字节与分析冻结来源不同')
    with weekly_path.open(encoding='utf-8', newline='') as stream:
        grouped = verified_rows(summary, list(csv.DictReader(stream)), selection)
    paths = [directory / f'weekly_comparison.{extension}' for extension in ('png', 'svg')]
    manifest_path = directory / 'plot_manifest.json'
    if any(path.exists() for path in [*paths, manifest_path]):
        raise ValueError('不覆盖已有观察图或绘图证据')

    # 只有真实分析文件通过门禁后才加载绘图库，不安装依赖或下载字体。
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
        'font.size': 10, 'axes.titlesize': 11, 'axes.spines.top': False,
        'axes.spines.right': False, 'axes.linewidth': 1, 'legend.frameon': False,
        'svg.fonttype': 'none', 'svg.hashsalt': 'hourly-return-pilot-seed0',
    })
    figure, axes = plt.subplots(1, 3, figsize=(14.2, 4.5))
    panels = [
        ('posted_meme_authors', '(a) Meme-author posts', 'Posts per week', 1),
        ('meme_author_share', '(b) Meme share of generated supply', 'Percent of all Agent posts', 100),
        ('feed_meme_tag_share', '(c) Meme-tag feed exposure', 'Percent of observed feed slots', 100),
    ]
    x = list(range(12, 23))
    for axis, (field, title, ylabel, scale) in zip(axes, panels):
        axis.axvspan(18.5, 22.3, color='#F4EEE4', zorder=0)
        for arm in grouped:
            values = [fraction(row[field]) for row in grouped[arm]]
            y = [math.nan if value is None else value * scale for value in values]
            axis.plot(x, y, color=COLORS[arm], marker='o', markersize=3.5, linewidth=1.8)
        axis.set(title=title, xlabel='ISO week in 2026', ylabel=ylabel,
                 xlim=(11.7, 22.3), xticks=[12, 13, 15, 17, 19, 20, 21, 22])
        axis.set_ylim(0, 19 if field == 'posted_meme_authors' else 100)
        axis.grid(axis='y', alpha=.18, linewidth=.7)
    handles = [Line2D([0], [0], color=COLORS[arm], lw=2, marker='o', ms=4, label=LABELS[arm])
               for arm in grouped]
    figure.suptitle(f'Hourly recirculation: {len(grouped)}-arm pilot, seed 0', x=.065, ha='left', fontsize=13)
    figure.legend(handles=handles, loc='lower center', ncol=3, bbox_to_anchor=(.5, .055))
    figure.text(.5, .015,
                'One run per arm; no uncertainty bands. Shading: W19–W22. Empty denominators remain gaps.\n'
                'Supply uses fixed author types; exposure uses feed pool labels. These are not independent semantic classifications.',
                ha='center', fontsize=8.5, linespacing=1.4)
    figure.tight_layout(rect=(0, .19, 1, .93))
    figure.savefig(paths[0], dpi=200, bbox_inches='tight', metadata={'Software': 'plot_pilot.py'})
    figure.savefig(paths[1], bbox_inches='tight', metadata={'Date': None, 'Creator': 'plot_pilot.py'})
    plt.close(figure)
    contract = dict(
        scope='single-seed descriptive pilot; not a manuscript figure',
        selected_algorithms=list(grouped), excluded_algorithms=summary.get('excluded_algorithms', []),
        figure_role='three aligned time trends',
        evidence='complete summary.json and 33 actual weekly.csv rows',
        columns=[panel[0] for panel in panels], late_weeks=sorted(LATE),
        missing_values='empty denominators shown as gaps, never filled with zero',
        uncertainty='none; one run per arm, no confidence intervals or significance test',
        source_sha256={path.name: digest(path) for path in (summary_path, weekly_path)},
        script_sha256=digest(Path(__file__)), matplotlib_version=matplotlib.__version__,
        output_sha256={path.name: digest(path) for path in paths},
    )
    if selection_path is not None:
        contract['source_sha256'][str(selection_path)] = digest(selection_path)
    manifest_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='written', files=[str(path) for path in [*paths, manifest_path]]), ensure_ascii=False))


if __name__ == '__main__':
    main()
