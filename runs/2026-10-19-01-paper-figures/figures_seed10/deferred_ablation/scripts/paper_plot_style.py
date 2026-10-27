"""本轮论文图1—5共享出版样式：原生SVG、明确分图编号与事件图例。"""
from pathlib import Path
import hashlib,json,platform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter,MultipleLocator

OUT=Path(__file__).resolve().parents[1]
DATA=OUT/'source_data'
QA=OUT/'qa'
QA.mkdir(exist_ok=True)
plt.rcParams.update({
 'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
 'font.size':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,
 'legend.fontsize':8,'axes.linewidth':.65,'axes.spines.top':False,
 'axes.spines.right':False,'axes.edgecolor':'#4B5563','text.color':'#17212B',
 'axes.labelcolor':'#17212B','xtick.color':'#344454','ytick.color':'#344454',
 'legend.frameon':False,'figure.facecolor':'white','savefig.facecolor':'white',
 'figure.dpi':150,'savefig.dpi':400,'svg.fonttype':'none','pdf.fonttype':42,
 'text.usetex':False,'mathtext.fontset':'stix','axes.unicode_minus':True,
 'svg.hashsalt':'ica2027-seed10-scientific-20261024',
})
CATS=['education','mourning','meme','other','marketing']
COLORS={'education':'#0072B2','mourning':'#D55E00','meme':'#7A5195',
        'other':'#89939E','marketing':'#C58F00'}
NAMES={'education':'Education','mourning':'Mourning','meme':'Memetic expression',
       'other':'Other discussion','marketing':'Marketing'}
STYLES={'education':'--','mourning':'-','meme':'-','other':':','marketing':'-.'}
ARMS=['random','chronological','interest']
ARM_NAMES={'random':'Random','chronological':'Chronological','interest':'Interest-based'}
ARM_COLORS={'random':'#667482','chronological':'#0072B2','interest':'#7A5195'}
EVENT_LABEL="W13: Zhang Xuefeng's death (24 Mar 2026)"
PERCENT=FuncFormatter(lambda x,_:f'{x:g}%')

def mm(n):return n/25.4

def panel(ax,number,letter,condition=None):
 """分图标识不充当图题；条件标签是读图所需的类别。"""
 ax.text(0,1.055,f'Fig. {number}{letter}',transform=ax.transAxes,
         fontsize=10,fontweight='bold',va='bottom',ha='left')
 if condition:
  ax.text(1,1.055,condition,transform=ax.transAxes,fontsize=9,
          va='bottom',ha='right')
 ax.set_axisbelow(True)
 ax.grid(axis='y',color='#DFE4E9',linewidth=.45)
 return ax

def week_axis(ax,start,stop,simulation=False):
 ticks=sorted(set(list(range(start,stop+1,2))+[13,stop]))
 ax.set_xlim(start,stop)
 ax.set_xticks(ticks,[f'W{w:02d}' for w in ticks])
 ax.set_xlabel(('Simulation' if simulation else 'Publication')+' week (2026)')
 ax.axvline(13,color='#263340',ls=(0,(4,2.4)),lw=.95,zorder=6)

def category_handles(author=False,event=True):
 handles=[Patch(facecolor=COLORS[c],label=('Memetic' if author and c=='meme' else NAMES[c])) for c in CATS]
 if event:handles.append(Line2D([],[],color='#263340',ls='--',lw=.95,label=EVENT_LABEL))
 return handles

def line_handles(author=False,event=True):
 handles=[Line2D([],[],color=COLORS[c],lw=1.8,ls=STYLES[c],
    marker='s' if c=='meme' else None,markersize=3,
    label=('Memetic' if author and c=='meme' else NAMES[c])) for c in CATS]
 if event:handles.append(Line2D([],[],color='#263340',ls='--',lw=.95,label=EVENT_LABEL))
 return handles

def save_figure(fig,stem,axes,expected_panels):
 """不tight裁切固定幅面；记录实际文字边界与SVG/PDF/PNG导出。"""
 fig.canvas.draw();renderer=fig.canvas.get_renderer()
 checks=[]
 for t in fig.findobj(plt.Text):
  if not t.get_visible() or not t.get_text():continue
  # 不包含被坐标轴裁去的内部tick候选。
  b=t.get_window_extent(renderer)
  if b.width and b.height:
   checks.append({'text':t.get_text(),'bbox_px':[round(v,2) for v in b.extents],
                  'outside_canvas':bool(b.x0<-.5 or b.y0<-.5 or b.x1>fig.bbox.width+.5 or b.y1>fig.bbox.height+.5)})
 for fmt in ('svg','pdf','png'):
  fig.savefig(OUT/f'{stem}.{fmt}',format=fmt,dpi=400,
              metadata={'Creator':'ICA2027 scientific figures; frozen existing data'} if fmt=='pdf' else None)
 metadata={'figure':stem,'size_mm':[round(v*25.4,2) for v in fig.get_size_inches()],
  'panels':expected_panels,'font':'Times New Roman','base_font_pt':9,
  'python':platform.python_version(),'matplotlib':matplotlib.__version__,
  'labels':[c for c in checks if c['outside_canvas']],
  'rendered_text_boxes':checks,'axes':[list(ax.get_position().bounds) for ax in axes],
  'outputs':{f:(hashlib.sha256((OUT/f'{stem}.{f}').read_bytes()).hexdigest()) for f in ('svg','pdf','png')}}
 (QA/f'{stem}.build.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 plt.close(fig)
 print(f'Saved {stem}: SVG/PDF/PNG')
