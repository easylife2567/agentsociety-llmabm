"""A：通栏紧凑主流程，减少重复的机制小总览。"""
from pathlib import Path
from diagram_lib import *
p=Path(__file__).parent
d=Diagram('A  |  Digital mourning: a curation–expression feedback pipeline')
# 顶部三张紧凑条件卡：两套数据分离，人群是固定条件。
d.box(48,105,585,134,GRAY,BORDER)
d.memorial(112,164,.62)
d.text(176,144,'OBSERVE','s',fill=MUTED)
d.text(176,186,'49,930 posts · two platforms','s')
d.text(176,221,'Douyin + Xiaohongshu','xs',fill=MUTED)
d.box(666,105,651,134,BT,BLUE)
d.text(690,145,'FROZEN INPUT','s',fill=BLUE)
d.text(690,186,'Time-stamped external samples','b')
d.text(690,221,'Shared across regimes within each seed','xs',fill=MUTED)
d.box(1350,105,1002,134,GRAY,BORDER)
d.person(1392,159,.7)
d.text(1440,147,'FIXED CONDITIONS','s',fill=MUTED)
d.text(1440,187,'100 agents · 5 types · W12–W22','b')
d.text(1440,221,'One opportunity / agent / week · fixed types and thresholds','xs',fill=MUTED)
# 一条横向主链；上下支路分别承载历史与内容反馈。
items=[(48,328,350,'01  Candidate pool',BLUE,BT),(428,328,350,'02  Personal feed',BLUE,BT),(808,328,610,'03  Expression rule',ORANGE,OT),(1448,328,475,'04  Generate',ORANGE,OT),(1953,328,399,'05  Publish',ORANGE,OT)]
for x,y,w,title,c,fill in items:
 d.box(x,y,w,200,fill,c)
 d.text(x+21,y+42,title,'h',fill=c)
d.lines(70,415,['Eligible external +','generated posts'],'s',39)
d.docs(456,402,.74);d.docs(519,402,.74,True);d.docs(582,402,.74)
d.text(450,507,'≤10 posts per action','s')
d.text(831,417,'B baseline · D climate · R history','s')
d.formula(1113,463,37)
d.text(1113,507,'U ≥ fixed individual threshold?','s','middle')
d.lines(1471,415,['Persona + ≤5 feed excerpts','≤120 characters per excerpt'],'s',40)
d.person(2000,418,.65)
d.lines(2044,423,['Successful','publication'],'s',38)
d.arrow('M398 433 H424','blue');d.arrow('M778 433 H804','blue')
d.arrow('M1418 455 H1444','orange');d.text(1434,433,'Yes','xs','middle')
d.arrow('M1923 433 H1949','orange')
# 前置条件进入所对应的计算层。
d.arrow('M992 239 V275 H223 V324','blue')
d.arrow('M1851 239 V280 H1113 V324','ink')
# 阈值以下分支是结束本次机会，不进入生成。
d.arrow('M1113 528 V552','ink')
d.box(949,554,328,57,GRAY,BORDER,7)
d.text(1113,592,'No → no post this turn','s','middle')
# 当次feed保存到未来历史。灰虚线独立于是否发帖。
d.box(428,554,470,57,WHITE,MUTED,7,'8 6')
d.text(663,592,'Prior same-type exposure','s','middle')
d.arrow('M603 528 V550','gray','7 6',3)
d.text(438,636,'Store for later actions','xs',fill=MUTED)
d.arrow('M898 582 H920 V541 H1352 V532','gray','7 6',3)
d.text(1309,582,'R','s',fill=MUTED)
# 成功发帖才能回流。整条蓝色闭环回到候选池。
d.arrow('M2153 528 V643 H222 V532','blue',sw=4)
d.box(1370,567,981,58,WHITE,BLUE,7)
d.text(1392,605,'Chronological: after batch · random / interest: next week','s',fill=BLUE)
d.text(1201,636,'R → 0 ⇒ U → B','xs','middle',MUTED)
d.footer()
d.save(p/'a_compact.svg')
