"""绘制无LLM、固定其余供给条件下的Agent拟发布机会。

复用chart3b的配色、字体、周界事件线和比例尺；只汇总离线数值明细。
拟发布机会=重算发言意愿且不是已确认拒答，假设其他生成均成功。
它不是完整闭环预测，作者类别也不是正文语义类别。
"""
import csv
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
OUT = ROOT/'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
SOURCE = OUT/'2026-10-06-01-numerical-decisions.csv'
SUMMARY = OUT/'2026-10-06-03-numerical-summary.json'
TEMPLATE = ROOT/'hypothesis_4/experiment_1/plot_run_charts.py'
# 绘图缓存归本任务管理；只导入无模型依赖的模板样式。
os.environ['MPLCONFIGDIR'] = str(TASK/'tmp/matplotlib')
os.environ['XDG_CACHE_HOME'] = str(TASK/'tmp')
spec = importlib.util.spec_from_file_location('expectation_style', TEMPLATE)
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
KINDS = [k for k in style.TYPE_ORDER if k != 'noise']
WEEKS = [f'2026-W{w}' for w in range(12, 23)]
POPULATION = {'meme': 19, 'mourning': 22, 'education': 15, 'marketing': 23, 'other': 21}


def main():
    # 固定来源和已完成的数值分支，不借用其他任务的参数或曲线。
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (SOURCE, SUMMARY, TEMPLATE, Path(__file__))}
    summary = json.loads(SUMMARY.read_text())
    assert summary['model_calls'] == summary['network_attempts'] == 0
    with SOURCE.open() as file:
        source = list(csv.DictReader(file))
    output, totals = [], {}
    for algorithm in ('interest', 'random'):
        rows = [r for r in source if r['algorithm'] == algorithm and r['mode'] == 'fixed_supply_screen']
        assert len(rows) == len({(r['agent_id'], r['week']) for r in rows}) == 1100
        # 当前唯一确认拒答在interest的agent79/W16，发言意愿保留，拟发布机会排除。
        def known_refusal(r):
            return algorithm == 'interest' and r['agent_id'] == '79' and r['week'] == '2026-W16'
        counts = Counter((r['week'], r['type']) for r in rows
                         if r['recomputed_speak'] == 'True' and not known_refusal(r))
        archived = Counter(r['week'] for r in rows if r['scheduled_publish'] == 'True')
        weekly = []
        for week in WEEKS:
            values = {k: counts[week, k] for k in KINDS}
            assert all(0 <= values[k] <= POPULATION[k] for k in KINDS)
            total = sum(values.values())
            assert total <= 80  # 绝不因模板上限而裁掉真实数值。
            weekly.append(dict(algorithm=algorithm, week=week, **values,
                               total=total, archived_count_excluding_known_refusal=archived[week]))
        assert sum(archived.values()) == summary[algorithm]['fixed_supply_screen']['published']
        totals[algorithm] = sum(w['total'] for w in weekly)
        assert totals[algorithm] == (219 if algorithm == 'interest' else 169)
        output.extend(weekly)

        # 沿用用户模板的五类面积；虚线仅用于与归档有效发布总数比较。
        fig, ax = style.plt.subplots(figsize=(10, 5.4))
        x = list(range(len(WEEKS)))
        style._death_line(ax, WEEKS)
        ax.stackplot(x, *[[w[k] for w in weekly] for k in KINDS],
                     labels=[style.TYPE_LABEL_EN[k] for k in KINDS],
                     colors=[style.TYPE_COLOR[k] for k in KINDS],
                     edgecolor='white', linewidth=0.6, alpha=0.92, zorder=2)
        ax.plot(x, [w['archived_count_excluding_known_refusal'] for w in weekly], color='#444444',
                ls='--', lw=1.1, label='Archived count', zorder=3)
        for i, w in enumerate(weekly):
            ax.text(i, max(w['total'], w['archived_count_excluding_known_refusal'])+1.4,
                    str(w['total']), ha='center', fontsize=9)
        ax.set_xticks(x, WEEKS, rotation=45)
        ax.set_ylim(*style.BASELINE_SUPPLY_YLIM)
        ax.set_yticks(range(0, 81, 10))
        ax.set_ylabel('拟发布机会（次 / 周）')
        ax.set_title(f'Agent 发帖的数值预期（无 LLM · timestamp-{algorithm}）', fontsize=13)
        ax.legend(loc='upper right', frameon=False, fontsize=9)
        style._tidy(ax)
        note = (f'100人 · seed 0 · 合计 {totals[algorithm]} 次拟发布机会 · 类型=固定作者类型\n'
                '固定其他供给，假设其余生成通过；非完整闭环预测；虚线=归档数排除已确认拒答')
        if algorithm == 'random':
            note += '；本臂未移除帖子'
        fig.text(0.07, 0.035, note, fontsize=8, color='#555555')
        fig.tight_layout(rect=(0, 0.10, 1, 1))
        stem = f'2026-10-06-0{4 if algorithm == "interest" else 5}-timestamp-{algorithm}-numerical-expectation'
        fig.savefig(OUT/f'{stem}.png', dpi=300)
        fig.savefig(OUT/f'{stem}.svg')
        style.plt.close(fig)
        print(algorithm, totals[algorithm], weekly)

    # 明细与生成依据一起保存，方便从图追溯条件与整数计数。
    with (OUT/'2026-10-06-06-numerical-expectation-weekly.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(output[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(output)
    evidence = {'metric': 'recomputed_speak excluding one known refusal; all other generations assumed valid',
                'scope': 'fixed_supply_screen; not a full closed-loop prediction',
                'totals': totals, 'source_sha256': hashes}
    (OUT/'2026-10-06-07-numerical-expectation-provenance.json').write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2)+'\n')
    for name, digest in hashes.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest


if __name__ == '__main__':
    main()
