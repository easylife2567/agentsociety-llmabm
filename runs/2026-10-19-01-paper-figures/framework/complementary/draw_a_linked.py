"""A：30:70双研究模块；经验结果与标定桥连接三阶段机制。"""
from pathlib import Path
from vivid_lib import *

out=Path(__file__).parent
d=D('Two complementary studies of postmortem representation','30:70')
# 两等高面板的净面积为684:1596=30:70；共同解释不计入任一研究。
d.box(30,30,684,680,WHITE,GD,r=0,sw=3,id='empirical-panel')
d.box(774,30,1596,680,WHITE,INK,r=0,sw=3,id='simulation-panel')
d.box(30,30,684,64,GREEN,GD,r=0,sw=2)
d.text(54,75,'I  Platform data analysis','h')
d.text(798,75,'II  Agent-based simulation','h')
d.text(2345,75,'Proposed mechanism','s',anchor='end')

# 经验部分：语料、五类实质内容与噪音过滤、两个互补的分析维度。
d.docs(65,126,.9);d.memorial(634,168,.8)
d.text(150,142,'49,930 posts','big')
d.text(150,180,'Douyin · Xiaohongshu','b')
d.text(150,218,'Jan–May 2026','s')
d.arrow('M372 226 V250','green')
d.box(54,252,636,112,WHITE,GD,r=0,dash='9 6')
d.text(76,287,'Content coding','h')
d.text(76,323,'Education · Mourning · Meme','s')
d.text(76,352,'Other · Marketing · Noise','xs')
d.arrow('M372 364 V391','green')
d.box(54,394,636,274,WHITE,GD,r=0)
d.text(76,434,'Empirical characterization','h')
d.box(76,454,282,156,GREEN,GD,r=0)
d.box(386,454,282,156,WHITE,GD,r=0,dash='8 5')
d.lines(94,493,['Temporal','evolution'],'b',step=36,weight=700)
d.lines(94,568,['Weekly counts','Content composition'],'xs',step=31)
d.lines(404,493,['Platform','differences'],'b',step=36,weight=700)
d.lines(404,568,['Compare trajectories','across platforms'],'xs',step=31)
d.arrow('M217 610 V627','green',sw=2.5)
d.arrow('M527 610 V627','green',sw=2.5)
d.text(372,653,'Patterns → mechanism questions','s',anchor='middle')

# 单独冻结的模拟输入；经验联动只指向作者构成和表达参数标定。
d.box(798,111,1548,92,WHITE,BORDER,r=0,dash='9 6')
d.text(820,148,'Frozen external posts','b',weight=700)
d.text(820,185,'Shared across regimes within seed','xs')
d.line('M1263 124 V190',BORDER)
d.text(1290,148,'100 fixed-type agents · W12–W22','b',weight=700)
d.text(1290,185,'Case-grounded author mix + B / D / R','s')
d.arrow('M714 683 H750 V236 H1560 V204','green',sw=3.5)
d.arrow('M1020 203 V275','blue')
d.text(1110,266,'Case-grounded specification','xs',fill=GD)
d.arrow('M1690 203 V275','gray',dash='8 7',sw=2.8)

stages=[(804,430,BLUE,BD,'Visibility','configuration'),
        (1280,570,RED,RD,'Selective','expression'),
        (1902,430,PURPLE,PD,'Content','recirculation')]
for x,w,c,cd,a,b in stages:
 d.box(x,275,w,305,WHITE,cd,r=0,sw=2.4)
 d.box(x,275,w,88,c,cd,r=0,sw=2.4)
 d.text(x+18,313,a,'h');d.text(x+18,351,b,'h')

d.lines(824,407,['Random / Chronological','/ Interest-based'],'s',step=38)
d.line('M824 464 H1214',BD)
d.text(824,510,'Eligible pool → Feed ≤10','s')
d.text(824,551,'posts per opportunity','s')
d.arrow('M1234 502 H1280','ink')

d.formula(1565,405,size=36)
d.text(1300,445,'B baseline · D feed response','s')
d.text(1300,483,'R prior-exposure weight','s')
d.text(1565,526,'U ≥ fixed individual threshold?','s',anchor='middle',weight=700)
d.text(1565,564,'Yes: LLM → publish   |   No: skip','s',anchor='middle')
d.arrow('M1850 550 H1902','ink')

d.text(1922,407,'Successfully published posts','xs',weight=700)
d.lines(1922,453,['Chronological:','later action batches'],'s',step=36)
d.lines(1922,535,['Random / Interest-based:','eligible next week'],'xs',step=36)

# 与发帖判定无关的接触历史更新，以及清楚回到候选池的内容回路。
d.box(1268,610,582,50,GRAY,MUTED,r=0,dash='8 6')
d.text(1559,645,'Feed → later exposure history → R','xs',anchor='middle')
d.arrow('M1020 580 V635 H1268','gray',dash='8 7',sw=2.7)
d.arrow('M1850 635 H1874 V481 H1850','gray',dash='8 7',sw=2.7)
d.arrow('M2117 580 V690 H790 V505 H804','purple',sw=4.6)
d.box(928,672,272,34,WHITE,WHITE,r=0,sw=0)
d.text(1064,697,'Recirculation loop','xs',anchor='middle',fill=PD)

# 两种证据汇合为共同解释；不宣称用仿真验证平台的真实因果效应。
d.arrow('M372 710 V750','ink',sw=3)
d.arrow('M1572 710 V750','ink',sw=3)
d.box(30,750,2340,64,GRAY,INK,r=0,sw=2)
d.text(1200,792,'Complementary evidence → public representation reorganization','h',anchor='middle')
d.text(30,842,'3 regimes × 3 seeds  |  Interest-based interventions: B=0 / D=1 / R=1','xs')
d.text(2370,842,'Fixed types; changing participation and supply.','xs',anchor='end')
d.save(out/'a_linked.svg')
