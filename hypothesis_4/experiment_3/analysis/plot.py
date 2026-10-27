"""已采纳配对数据的正式派生图；复用指定chart3b配色、事件线和0–80坐标，不调用模型。"""
from pathlib import Path
import os,json,importlib.util
BASE=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(BASE/'checks/mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import pandas as pd
import numpy as np

PRES=BASE.parents[1]/'presentation/hypothesis_4/timestamp_bdr_v1';DATA=PRES/'data';OUT=PRES/'charts'
spec=importlib.util.spec_from_file_location('template',BASE/'analysis/chart3b_template.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
plt.rcParams.update({'svg.fonttype':'none','pdf.fonttype':42,'font.family':['Hiragino Sans GB','DejaVu Sans'],'figure.facecolor':'white','savefig.facecolor':'white','font.size':11})
COL={'full':'#4C72B0','no_b':'#9467BD','no_d':'#DD8452','no_r':'#55A868'}
LABEL={'full':'Full','no_b':'No B','no_d':'No D','no_r':'No R'}
CN={'full':'完整模型 Full','no_b':'去B','no_d':'去D响应（D=1）','no_r':'去R衰减（R=1）'}
CONDS=list(COL);TYPES=['meme','mourning','education','marketing','other'];WEEKS=[f'2026-W{x}' for x in range(12,23)]
w=pd.read_csv(DATA/'weekly_by_type.csv');met=pd.read_csv(DATA/'run_metrics.csv');paired=pd.read_csv(DATA/'paired_summary.csv')
outputs=[]
def export(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=240,bbox_inches='tight')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight')
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight')
    outputs.extend([name+'.'+e for e in ('png','svg','pdf')]);plt.close(fig)
def wide(cond,seed=None):
    sub=w[w.condition==cond]
    if seed is not None:sub=sub[sub.seed==seed]
    pt=sub.groupby(['week','agent_type']).posted.mean().unstack().reindex(WEEKS).fillna(0)
    return [dict(week=wk,**{'agent_supply_'+k:float(pt.loc[wk,k]) for k in TYPES}) for wk in WEEKS]
def stack(ax,rows,title):
    x=np.arange(11);ax.stackplot(x,*[[r['agent_supply_'+k] for r in rows] for k in TYPES],colors=[t.TYPE_COLOR[k] for k in TYPES],alpha=.92,edgecolor='white',linewidth=.6)
    ax.axvline(1,color='#D62728',ls='--',lw=1.3,zorder=5)
    ax.text(1.1,77,'去世 3-24 (W13)',color='#D62728',va='top',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.86,'pad':2})
    ax.set_ylim(0,80);ax.set_yticks(range(0,81,10));ax.set_xticks(x,[x.replace('2026-','') for x in WEEKS]);ax.set_title(title,fontweight='bold',fontsize=14);ax.set_ylabel('Agent 成功发帖数（帖/周）');ax.set_axisbelow(True)

contracts=[dict(contract_id='supply',claim_id='C0',core_finding='固定同一尺度与作者类型口径，Full及三个单因素消融在供给轨迹上分叉。',scope='single faceted chart',evidence='weekly_by_type.csv, grouped by condition/week/type, arithmetic mean over three seeds',outputs=['chart_03_supply_mean_comparison.png'],template='exact chart3b palette/order, W13 marker, 0–80 scale; individual charts use frozen template function',caveat='mean is not a single realized run; see all twelve per-seed charts; author type is not semantic gold'),dict(contract_id='primary',claim_id='CB,CD,CR',core_finding='三项预设窗口指标分别显示B供给维持、D晚期选择性表达和R整体衰减。',scope='single faceted paired comparison',evidence='run_metrics.csv and paired_summary.csv; no pooling opportunities as independent replicates',outputs=['chart_04_primary_paired_effects.png'],caveat='three paired runs only; different metric units separated across facets'),dict(contract_id='trajectories',claim_id='CD,CR',core_finding='总体持续表达与玩梗型作者晚期优势并不同时提高，去D使表达前移。',scope='single two-facet trend chart',evidence='weekly_by_type.csv; exact speak/opportunities, mean and actual range by seed',outputs=['chart_05_speaking_trajectories.png'],caveat='min-max band is not CI; author types and post meaning differ')]
(BASE/'payloads/figure_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2)+'\n')

for seed in range(3):
    for cond in CONDS:
        name=f'chart_01_{cond}_s{seed}_agent_supply'
        for suffix in ('png','svg'):
            t.chart3b_agent_supply_stacked_area(wide(cond,seed),f'{LABEL[cond]} · seed {seed}',OUT/(name+'.'+suffix));outputs.append(name+'.'+suffix)
for cond in CONDS:
    name=f'chart_02_{cond}_mean_agent_supply'
    for suffix in ('png','svg'):
        t.chart3b_agent_supply_stacked_area(wide(cond),f'{LABEL[cond]} · 3 seeds mean',OUT/(name+'.'+suffix));outputs.append(name+'.'+suffix)

fig,axes=plt.subplots(2,2,figsize=(16.8,10.4),sharex=True,sharey=True)
for i,(cond,ax) in enumerate(zip(CONDS,axes.flat)):
    stack(ax,wide(cond),f'({chr(97+i)}) {CN[cond]}')
handles=[plt.Rectangle((0,0),1,1,color=t.TYPE_COLOR[k],alpha=.92) for k in TYPES]
fig.legend(handles,[t.TYPE_LABEL_EN[k] for k in TYPES],loc='upper center',bbox_to_anchor=(.5,.945),ncol=5,frameon=False)
fig.suptitle('单独关闭B、D响应或R衰减，改变了整条Agent供给轨迹',fontsize=19,fontweight='bold',y=.993)
fig.text(.5,.015,'三seed均值；仅Agent成功发布、不含外部输入。统一0–80轴；作者类型不是正文语义金标。逐seed曲线另附。',ha='center',fontsize=10,color='#555555')
fig.subplots_adjust(top=.88,bottom=.07,hspace=.22,wspace=.13);export(fig,'chart_03_supply_mean_comparison')

fig,axes=plt.subplots(1,3,figsize=(15.8,5.5))
settings=[('no_b','late_posts_per_week','去B：晚期供给降低','W19–W22 发帖数（帖/周）',1,(0,19)),('no_d','late_meme_speak_rate','去D：晚期玩梗型作者表达降低','W19–W22 玩梗型作者发言率（%）',100,(0,65)),('no_r','mid_speak_rate','去R衰减：整体表达提高','W14–W18 全体发言率（%）',100,(0,60))]
for ax,(cond,key,title,yl,scale,ylim) in zip(axes,settings):
    for seed,marker in enumerate(('o','s','^')):
        v=met[(met.condition=='full')&(met.seed==seed)][key].iloc[0]*scale;u=met[(met.condition==cond)&(met.seed==seed)][key].iloc[0]*scale;offset=(seed-1)*.035
        ax.plot([0+offset,1+offset],[v,u],color='#A0A0A0',lw=1.3,zorder=1)
        ax.scatter([0+offset,1+offset],[v,u],c=[COL['full'],COL[cond]],marker=marker,s=65,zorder=3,edgecolors='white',linewidth=.8)
    z=paired[(paired.condition==cond)&(paired.metric==key)].iloc[0]
    unit='帖/周' if scale==1 else '个百分点'
    text=f'配对均值差 {z.delta_mean*scale:+.2f} {unit}\n三个seed差值范围 [{z.delta_min*scale:+.2f}, {z.delta_max*scale:+.2f}]'
    ax.set_title(title,fontsize=13,fontweight='bold');ax.set_xticks([0,1],['Full',LABEL[cond]]);ax.set_xlim(-.23,1.23);ax.set_ylim(*ylim);ax.set_ylabel(yl);ax.text(.5,-.16,text,transform=ax.transAxes,ha='center',va='top',fontsize=10);ax.set_axisbelow(True)
fig.legend([Line2D([],[],marker=m,color='#888888',linestyle='none',markersize=7) for m in ('o','s','^')],['seed 0','seed 1','seed 2'],ncol=3,frameon=False,loc='upper center',bbox_to_anchor=(.5,.99))
fig.text(.5,.005,'每条线连接同seed；差值=消融−Full。n=3，展示实际配对点与范围，不画置信区间或显著性星号。',ha='center',fontsize=10,color='#555555')
fig.subplots_adjust(top=.85,bottom=.25,wspace=.31);export(fig,'chart_04_primary_paired_effects')

fig,axes=plt.subplots(1,2,figsize=(16,6))
for ax,scope,title in [(axes[0],'all','(a) 全体发言率：R衰减约束持续表达'),(axes[1],'meme','(b) 玩梗型作者：去D使表达前移，晚期却降低')]:
    z=w if scope=='all' else w[w.agent_type=='meme']
    q=z.groupby(['condition','seed','week'])[['speak','opportunities']].sum().reset_index();q['rate']=q.speak/q.opportunities*100
    for cond in CONDS:
        pivot=q[q.condition==cond].pivot(index='week',columns='seed',values='rate').reindex(WEEKS)
        ax.fill_between(np.arange(11),pivot.min(axis=1),pivot.max(axis=1),color=COL[cond],alpha=.10)
        ax.plot(np.arange(11),pivot.mean(axis=1),color=COL[cond],lw=2.0,marker='o',markersize=3.5,label=LABEL[cond])
    ax.axvline(1,color='#D62728',ls='--',lw=1.2);ax.axvspan(6.5,10.25,color='#AAAAAA',alpha=.08);ax.set_xticks(np.arange(11),[x.replace('2026-','') for x in WEEKS]);ax.set_ylim(0,100 if scope=='meme' else 80);ax.set_ylabel('发言率（%）');ax.set_title(title,fontsize=13,fontweight='bold');ax.set_axisbelow(True)
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.985),ncol=4,frameon=False)
fig.text(.5,.015,'粗线=三seed均值，浅带=实际最小–最大；非置信区间。W13红虚线=去世事件；灰区=W19–W22。',ha='center',fontsize=10,color='#555555')
fig.subplots_adjust(top=.86,bottom=.10,wspace=.2);export(fig,'chart_05_speaking_trajectories')

(DATA/'chart_outputs.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')
print('charts exported:',len(outputs),'files; all template peaks <=80')
