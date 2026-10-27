"""复用chart3b样式展示四格内容修复的固定供给数值预期。

只读取已验收的作者周表和内容摘要，不导入Agent、不跑环境或LLM；
四格共享0–80尺度，汇总图不能解释为新闭环实验结果。
"""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
os.environ['MPLCONFIGDIR'] = str(TASK/'tmp/matplotlib')
SOURCE = OUT/'2026-10-07-02-content-weekly.csv'
SUMMARY = OUT/'2026-10-07-03-content-summary.json'
TEMPLATE = ROOT/'hypothesis_4/experiment_1/plot_run_charts.py'
TEMPLATE_IMAGE = ROOT/'hypothesis_4/experiment_1/runs/anchored_v1/_derived/charts/anchored_v1_chronological_s0__chart3b_agent_supply_stacked_area.png'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # 样式直接取项目模板；数据完全取本任务四格，不借用chronological数值。
    spec = importlib.util.spec_from_file_location('content_overview_style', TEMPLATE)
    style = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(style)
    rows = list(csv.DictReader(SOURCE.open()))
    summary = json.loads(SUMMARY.read_text())['conditions']
    kinds = [k for k in style.TYPE_ORDER if k != 'noise']
    conditions = ['preload-interest', 'timestamp-interest', 'preload-random', 'timestamp-random']
    weeks = [f'2026-W{w}' for w in range(12,23)]
    fig, axes = style.plt.subplots(2, 2, figsize=(15, 9), sharey=True)
    totals = {}
    for ax, condition in zip(axes.flat, conditions):
        group = [r for r in rows if r['condition'] == condition]
        assert [r['week'] for r in group] == weeks
        assert all(sum(int(r[k]) for k in kinds) == int(r['total']) == int(r['archived_total']) for r in group)
        totals[condition] = sum(int(r['total']) for r in group)
        assert totals[condition] == summary[condition]['preserved_posts'] == summary[condition]['archived_published']
        x = list(range(11))
        style._death_line(ax, weeks)
        ax.stackplot(x, *[[int(r[k]) for r in group] for k in kinds],
                     colors=[style.TYPE_COLOR[k] for k in kinds], labels=[style.TYPE_LABEL_EN[k] for k in kinds],
                     alpha=.92, edgecolor='white', linewidth=.6, zorder=2)
        for i, r in enumerate(group):
            ax.text(i, int(r['total'])+1.5, r['total'], ha='center', fontsize=9)
        ax.set_title(f'{condition} · 保留 {totals[condition]} 条', fontsize=13)
        ax.set_ylim(0,80)
        ax.set_yticks(range(0,81,10))
        ax.set_xticks(x, weeks, rotation=45, fontsize=9)
        style._tidy(ax)
    for ax in axes[:,0]:
        ax.set_ylabel('Agent 发布数（条 / 周）')
    # 分类对象与条件边界写入图注；类型不等于重新判类后的正文语义。
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5,.942), ncol=5, frameon=False)
    fig.suptitle('内容修复的固定供给数值预期（仅 Agent 产出）', y=.992, fontsize=18)
    fig.text(.055,.015, '每格100人 · seed 0 · 只修细节，发言不减量 · 原归档供给固定，四格合计794条\n'
             '颜色表示作者类型；不是正文语义分类。无LLM、非新闭环预测，timestamp方案仍暂停。', fontsize=10, color='#555555')
    fig.tight_layout(rect=(0,.075,1,.91))
    stem = OUT/'2026-10-07-09-content-overview'
    fig.savefig(stem.with_suffix('.png'),dpi=240)
    svg = stem.with_suffix('.svg')
    fig.savefig(svg)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    style.plt.close(fig)
    assert sum(totals.values()) == 794
    evidence = {'totals':totals, 'classification':'fixed author type', 'scope':'fixed archived supply; not closed-loop prediction',
                'model_calls':0, 'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in [SOURCE,SUMMARY,TEMPLATE,TEMPLATE_IMAGE,Path(__file__)]}}
    (OUT/'2026-10-07-10-content-overview-provenance.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(totals,ensure_ascii=False))


if __name__ == '__main__':
    main()
