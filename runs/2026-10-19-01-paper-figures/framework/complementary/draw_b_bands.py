"""方案 B：两条等宽研究带；正文分析与机制仿真占 40:60。"""
from pathlib import Path
from vivid_lib import *

ROOT=Path(__file__).resolve().parent
d=D('Complementary evidence for the reorganization of public representation','40:60 (2350×270 versus 2350×405)')
d.text(25,37,'Complementary studies of public representation', 'title',size=40)
# 两个研究模块的实际外框面积严格为 40:60；底部为共同解释，不归属某一研究。
d.box(25,55,2350,270,WHITE,GD,r=0,sw=3,id='empirical-panel')
d.box(25,340,2350,405,WHITE,PD,r=0,sw=3,id='simulation-panel')
d.text(48,96,'A  Platform data analysis','h',fill=GD)
d.text(2345,95,'EMPIRICAL PATTERNS','s',anchor='end',fill=GD,weight=700)

# 平台分析：真实语料、分类、比较以及可核验的实际观测量。
d.box(50,116,495,163,GREEN,GD,r=0,sw=2)
d.text(68,153,'49,930 posts','h')
d.lines(68,190,['Douyin + Xiaohongshu','Jan–May 2026','Time-stamped posts'],'s',step=35)
d.memorial(487,205,.65)
d.arrow('M550 200 H583')
d.box(590,116,470,163,WHITE,INK,r=0,sw=2,dash='9 6')
d.text(608,153,'Content coding','h')
d.lines(608,194,['Education · mourning · meme','Other · marketing','Noise identified separately'],'s',step=35)
d.arrow('M1067 200 H1100')
d.box(1107,116,555,163,WHITE,INK,r=0,sw=2,dash='9 6')
d.text(1125,153,'Temporal × platform analysis','h',size=33)
d.lines(1125,194,['Mourning peak: W13','Meme growth: W19–W20','Compare weekly composition'],'s',step=35)
d.arrow('M1669 200 H1702')
d.box(1709,116,640,163,WHITE,GD,r=0,sw=2)
d.text(1727,153,'Mechanism questions','h')
d.lines(1727,194,['Which content becomes visible?','Who chooses to speak?','What returns to circulation?'],'s',step=35)
d.text(48,309,'Observed patterns + parameter references','s',fill=GD)
d.arrow('M1000 301 H1200 V339','green',sw=3.5)
d.text(1250,309,'Mechanism questions for simulation','s',fill=GD)

# 仿真三联机制：颜色仅标识阶段，不承担“好/坏”或“是/否”的含义。
d.text(48,380,'B  Simulation modeling','h',fill=PD)
d.text(2348,379,'100 fixed-type agents · W12–W22','s',anchor='end')
for x,w,fill,stroke,title in [(50,660,BLUE,BD,'1  Visibility configuration'),(755,920,RED,RD,'2  Selective expression'),(1720,630,PURPLE,PD,'3  Content recirculation')]:
 d.box(x,400,w,258,WHITE,stroke,r=0,sw=2.5)
 d.box(x,400,w,57,fill,stroke,r=0,sw=2.5)
 d.text(x+17,440,title,'h',size=35)

# 制度特定候选池与决策信息流，外部冻结输入不与整个实证语料画成同一对象。
d.text(70,497,'Frozen external samples → candidate pools','s',size=29)
d.docs(83,528,.78)
d.docs(143,538,.78)
d.arrow('M208 570 H284','blue')
d.box(293,535,394,69,BLUE,BD,r=0,sw=2)
d.text(490,579,'Feed ≤10 eligible posts','s',anchor='middle')
d.text(70,635,'Random · Chronological · Interest-based','s',size=29)
d.arrow('M715 491 H750','ink')

# 表达决策先于 LLM；历史接触的影响仅通过下一轮 R。
d.formula(1215,502,size=38)
d.text(1215,541,'B baseline · D current climate · R exposure weight','s',anchor='middle',size=29)
d.box(781,550,436,58,WHITE,RD,r=0,sw=2)
d.text(999,589,'U ≥ fixed threshold?','b',anchor='middle')
d.arrow('M999 610 V623','gray',sw=2.5)
d.text(999,650,'no: no post','xs',anchor='middle')
d.arrow('M1220 578 H1256')
d.box(1263,550,387,58,RED,RD,r=0,sw=2)
d.text(1457,589,'If yes: LLM → publish','b',anchor='middle',size=30)
d.text(1457,628,'Persona + ≤5 feed excerpts','xs',anchor='middle')
d.text(1457,654,'≤120 characters each','xs',anchor='middle')
d.arrow('M1653 579 H1715','ink')

# 仅成功发布的帖子进入回流；不同制度具有不同生效时点。
d.docs(1741,478,.66)
d.lines(1810,506,['Successfully published','posts'],'s',step=35)
d.lines(1740,583,['Chronological: later batches','Random / interest: next week'],'s',step=42)

# 独立历史分支：来自阅读接触，绝不依赖是否发布。
d.box(755,665,920,48,GRAY,MUTED,r=0,sw=1.8,dash='8 5')
d.text(1215,699,'Same-type contacts → prior history → later R','s',anchor='middle')
d.arrow('M690 575 H720 V689 H749','gray',sw=3,dash='8 5')
d.arrow('M755 681 H737 V525 H766','gray',sw=3,dash='8 5')
# 回流环单独沿最下沿返回候选池，避免形成“作者类型变化”的读法。
d.arrow('M2115 660 V729 H38 V499 H62','purple',sw=4)
d.box(165,710,490,34,WHITE,WHITE,r=0,sw=0)
d.text(410,734,'Published content returns to pools','xs',anchor='middle',fill=PD)

# 两条研究共同用于解释表征重组；仿真不是对平台数据的验证替代。
d.line('M25 770 H2375',INK,2)
d.text(1200,808,'Empirical patterns + regime contrasts → interpretation of representation reorganization','h',anchor='middle',size=33)
d.text(1200,842,'3 regimes × 3 seeds · Interest-based ablations: B=0 / D=1 / R=1 · Author types remain fixed','xs',anchor='middle')
d.save(ROOT/'b_bands.svg')
