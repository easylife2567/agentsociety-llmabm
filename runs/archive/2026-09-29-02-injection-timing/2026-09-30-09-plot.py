"""从已复算的周指标绘制诊断图，单seed不绘置信区间。

图一比较主曝光与固定作者参与；图二明确词表信号和互斥主标签的差别。
所有曲线复用同一条件配色，导出PNG及可编辑SVG到正式presentation目录。
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'presentation/hypothesis_4/2026-09-30-01-arrival-timing'
plt.rcParams.update({'font.family':'sans-serif', 'font.sans-serif':['Arial','DejaVu Sans'],
                     'svg.fonttype':'none', 'pdf.fonttype':42, 'font.size':10,
                     'axes.spines.top':False, 'axes.spines.right':False, 'legend.frameon':False})
COLORS = {'preload-interest':'#a54212', 'timestamp-interest':'#007e91',
          'preload-random':'#b7a080', 'timestamp-random':'#6a80ae'}


def plot(column, title, ylabel, filename, fraction=False):
    """每张图只比较一个口径；灰色背景标明预登记W19–W22窗口。"""
    data = pd.read_csv(OUT/'weekly.csv')
    fig, ax = plt.subplots(figsize=(9,4.5))
    ax.axvspan(18.75,22.25,color='#f0f2f4',zorder=0)
    for condition, color in COLORS.items():
        d = data[data.condition==condition]
        values = d[column] / d.published * 100 if fraction else d[column]
        ax.plot(d.week.str[-2:].astype(int),values,label=condition,color=color,
                marker='o',markersize=4,linewidth=2,linestyle='--' if condition.startswith('preload') else '-')
    ax.set(title=title,xlabel='Simulation week (Asia/Shanghai)',ylabel=ylabel,xticks=range(12,23),xlim=(11.8,22.3))
    ax.set_ylim(bottom=0)
    ax.grid(axis='y',alpha=.18)
    ax.legend(loc='upper left',ncol=2,fontsize=9)
    fig.text(.11,.015,'One seed per condition. Shaded area: preregistered evaluation window. No inferential intervals.',fontsize=8,color='#555555')
    fig.tight_layout(rect=(0,.04,1,1))
    for extension in ('png','svg'):
        fig.savefig(OUT/f'{filename}.{extension}',dpi=200,bbox_inches='tight')
    # 清理SVG序列化产生的行尾空白，保持版本库差异可读。
    svg = OUT/f'{filename}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)


if __name__ == '__main__':
    plot('Y','Later arrival reduces the interest–random exposure gap',
         'Meme-type exposures per planned action','exposure')
    plot('meme_author_posts','Meme-author production rises later under timestamp arrival',
         'Posts by fixed meme-type authors (19 people)','production')
    plot('meme_signal_posts','Lexicon signals rise; they are not mutually exclusive content labels',
         'Posts with a frozen meme signal (%)','semantic_signal',fraction=True)
