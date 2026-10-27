"""Reproduce the predeclared comparison figure from frozen extracted tables, offline."""
from pathlib import Path
import csv
import json
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans','Liberation Sans'],'svg.fonttype':'none','pdf.fonttype':42,'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'axes.linewidth':0.8})
rows=list(csv.DictReader((BASE/'data/weekly_metrics.csv').open()))
summary=json.loads((BASE/'data/metrics_summary.json').read_text())['summaries']
colors={'random':'#767676','chronological':'#0F4D92','interest':'#42949E'}
fig, axes=plt.subplots(2,3,figsize=(13.4,8.3),layout='constrained')
weekfields=[('exposure_share_mourning','Interest: mourning exposure'),('supply_share_meme','Interest: Agent meme supply'),('exposure_share_meme','Interest: meme exposure')]
for i,(key,title) in enumerate(weekfields):
    ax=axes[0,i]
    for version,style,color in [('old','-','#555555'),('new','--','#42949E')]:
        rs=[r for r in rows if r['version']==version and r['algorithm']=='interest' and r['seed']=='0']
        xs=[int(r['week'].split('W')[1]) for r in rs]
        ys=[100*float(r[key]) for r in rs]
        ax.plot(xs,ys,style,color=color,lw=2,marker='o' if version=='new' else None,markersize=3,label='Old s0' if version=='old' else 'CUC, one run')
    ax.axvspan(18.5,22.5,color='#42949E',alpha=.065)
    ax.set(xlim=(11.7,22.3),ylim=(0,100 if key=='supply_share_meme' else 60),xticks=[12,13,15,17,19,21,22],xlabel='Week',ylabel='Share (%)',title=title)
    ax.grid(axis='y',alpha=.17)
    ax.text(-.10,1.03,chr(97+i),transform=ax.transAxes,fontweight='bold',fontsize=13)
axes[0,0].legend(loc='upper right',fontsize=9)
axes[0,1].text(.03,.94,'Agent posts only; changing denominator',transform=axes[0,1].transAxes,fontsize=8,va='top')
keys=[('late_meme_author_participation','Late meme-author participation','19 authors × 4 weeks = 76 opportunities'),('late_agent_meme_supply_share','Late Agent meme supply','Meme-author posts / all Agent posts'),('late_meme_exposure_share','Late meme exposure','Meme pool slots / 4,000 feed slots')]
for j,(key,title,note) in enumerate(keys):
    ax=axes[1,j]
    for x,arm in enumerate(colors):
        vals=[]
        for version,dx,marker in [('old',-.12,'o'),('new',.12,'D')]:
            rec=next(s for s in summary if s['version']==version and s['algorithm']==arm and s['seed']==0)
            y=100*rec[key]; vals.append(y)
            ax.scatter(x+dx,y,s=55,marker=marker,edgecolors=colors[arm],facecolors='white' if version=='old' else colors[arm],linewidths=1.5,zorder=3)
        label=f'{vals[0]:.2f} → {vals[1]:.2f}' if vals[0]!=vals[1] else f'{vals[1]:.2f}'
        ax.text(x,max(vals)+3,label,ha='center',fontsize=9)
    ax.set(xlim=(-.55,2.55),ylim=(0,82),xticks=[0,1,2],xticklabels=['Random','Chronological','Interest'],ylabel='Share (%)',title=title)
    ax.tick_params(axis='x',labelsize=9)
    ax.text(.5,-.22,note,transform=ax.transAxes,ha='center',fontsize=8)
    ax.grid(axis='y',alpha=.17)
    ax.text(-.10,1.03,chr(100+j),transform=ax.transAxes,fontweight='bold',fontsize=13)
axes[1,0].legend(handles=[Line2D([],[],marker='o',ls='',mfc='white',mec='#555555',label='Old s0'),Line2D([],[],marker='D',ls='',color='#555555',label='CUC, one run')],loc='upper left',fontsize=9)
fig.suptitle('Service switch: interest feedback changes; late-period institution order persists',fontsize=15,fontweight='bold')
assets=BASE/'assets';assets.mkdir(exist_ok=True)
for ext in ['png','svg']:
    fig.savefig(assets/f'figure_01_model_comparison.{ext}',dpi=180,bbox_inches='tight')
plt.close(fig)
workspace=BASE.parent/'workspace/presentation/hypothesis_4_cuc/assets'
workspace.mkdir(parents=True,exist_ok=True)
for path in assets.iterdir():
    shutil.copy2(path,workspace/path.name)
print('Figure PNG and editable SVG written; no model calls.')
