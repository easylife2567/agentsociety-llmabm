"""按固定周表画本批三制度Agent实际成功发帖量；离线，不重跑仿真。"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

BASE=Path(__file__).resolve().parent
source=BASE/'data/weekly_metrics.csv'
rows=[r for r in csv.DictReader(source.open()) if r['version']=='new']
arms=['random','chronological','interest']
types=['marketing','mourning','other','meme','education']
selected=[]
expected={'random':176,'chronological':210,'interest':217}
for arm in arms:
    rs=sorted((r for r in rows if r['algorithm']==arm),key=lambda r:r['week'])
    assert len(rs)==11 and [r['week'] for r in rs]==[f'2026-W{w}' for w in range(12,23)]
    for r in rs:
        count=int(r['posted_all'])
        assert count==int(r['agent_supply'])==sum(int(r[f'posted_{t}']) for t in types)
        assert int(r['actions'])==100 and 0<=count<=100
        selected.append({'algorithm':arm,'week':r['week'],'successful_posts':count,**{f'posts_{t}':int(r[f'posted_{t}']) for t in types}})
    assert sum(int(r['posted_all']) for r in rs)==expected[arm]
with (BASE/'data/weekly_agent_posts.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans','Liberation Sans'],'svg.fonttype':'none','pdf.fonttype':42,'font.size':11,'axes.spines.right':False,'axes.spines.top':False,'axes.linewidth':.8,'legend.frameon':False})
fig,ax=plt.subplots(figsize=(11.8,5.8))
colors={'random':'#767676','chronological':'#0F4D92','interest':'#42949E'}
markers={'random':'o','chronological':'s','interest':'D'}
labels={'random':'Random','chronological':'Chronological','interest':'Interest'}
for arm in arms:
    rs=[r for r in selected if r['algorithm']==arm]
    xs=[int(r['week'][-2:]) for r in rs];ys=[r['successful_posts'] for r in rs]
    ax.plot(xs,ys,color=colors[arm],marker=markers[arm],markersize=5.5,lw=2.2,label=f'{labels[arm]} ({sum(ys)} posts)')
    ax.annotate(str(ys[1]),(13,ys[1]),xytext=(-4,10),textcoords='offset points',ha='center',color=colors[arm],fontsize=10,fontweight='bold')
    offset={'random':0,'chronological':-5,'interest':5}[arm]
    ax.annotate(str(ys[-1]),(22,ys[-1]),xytext=(10,offset),textcoords='offset points',va='center',color=colors[arm],fontsize=10,fontweight='bold')
ax.set(xlim=(11.75,22.65),ylim=(0,57),xticks=list(range(12,23)),xlabel='Simulation week (2026)',ylabel='Successful Agent posts / week')
ax.set_xticklabels([f'W{w}' for w in range(12,23)])
ax.yaxis.set_major_locator(MaxNLocator(integer=True,nbins=6))
ax.grid(axis='y',color='#dce2e7',lw=.8,zorder=0)
ax.legend(loc='upper right',fontsize=10)
fig.suptitle('Weekly Agent posting volume',x=.085,y=.97,ha='left',fontsize=18,fontweight='bold')
fig.text(.085,.90,'CUC service | 100 Agents | one run per curation regime',fontsize=11,color='#526474')
fig.text(.085,.02,'Successful Agent publications only; external inputs excluded. One posting opportunity per Agent per week.',fontsize=9,color='#526474')
fig.subplots_adjust(left=.085,right=.975,top=.84,bottom=.14)
assets=BASE/'assets';assets.mkdir(exist_ok=True)
for ext in ['png','svg']:
    fig.savefig(assets/f'chart_02_weekly_agent_posts.{ext}',dpi=200,bbox_inches='tight')
plt.close(fig)
qa={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':len(selected),'weekly_identity_checked':'posted_all == agent_supply == sum(posted_five_types)','totals':expected,'counts':{a:[r['successful_posts'] for r in selected if r['algorithm']==a] for a in arms},'scope':'new runs only, no model calls'}
(BASE/'data/weekly_agent_posts_verification.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
mirror=BASE.parent/'workspace/presentation/hypothesis_4_cuc'
for path in [BASE/'data/weekly_agent_posts.csv',BASE/'data/weekly_agent_posts_verification.json',assets/'chart_02_weekly_agent_posts.png',assets/'chart_02_weekly_agent_posts.svg']:
    target=mirror/path.relative_to(BASE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
print(json.dumps(qa,ensure_ascii=False,indent=2))
