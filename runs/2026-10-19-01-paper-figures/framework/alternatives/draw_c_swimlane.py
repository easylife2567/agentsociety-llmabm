"""双栏时间泳道构图：本次表达、后续展示与历史更新各自成线。"""
from pathlib import Path
from diagram_lib import *

d = Diagram('Curation–Expression Feedback',
            'C · Temporal swimlanes in a digital-mourning environment')

# 三种输入分别排布，不把现实语料全量画成仿真输入。
d.box(48,108,720,95,GRAY)
d.memorial(95,155,.65)
d.text(151,143,'EMPIRICAL CONTEXT','xs',fill=MUTED)
d.text(151,183,'49,930 posts · Douyin + Xiaohongshu','s')
d.box(780,108,720,95,BT,BLUE)
d.text(802,143,'SEPARATELY FROZEN SIMULATION INPUTS','xs',fill=BLUE)
d.text(802,183,'Time-stamped posts · shared within seed','s')
d.box(1512,108,840,95,GRAY)
d.text(1534,143,'100 agents · 5 fixed author types','b')
d.text(1534,183,'W12–W22 · 1 opportunity / week','s')

# 三条横向责任泳道；最右表示后续展示与后续行动，不改变作者类型。
rows = [(228,118,'PLATFORM'), (357,129,'AGENT'), (497,118,'LLM')]
for y,h,label in rows:
    d.box(48,y,2304,h,WHITE,BORDER,8)
    d.box(48,y,185,h,GRAY,BORDER,8)
    d.text(141,y+h/2+11,label,'s',anchor='middle')
d.line('M2048 228 V486',BORDER,2,'7 5')
d.text(1907,259,'LATER','xs',anchor='middle',fill=MUTED)
d.text(1907,300,'ELIGIBILITY','xs',anchor='middle',fill=MUTED)

# 外部输入先进入各制度池，制度策展再生成个人feed。
d.arrow('M1140 203 V218 H445 V253','blue',sw=3.5)
d.box(270,253,350,69,BT,BLUE,8)
d.text(445,281,'Regime-specific','s',anchor='middle')
d.text(445,313,'candidate pool','s',anchor='middle')
d.arrow('M620 287 H700','blue',sw=4)
d.box(700,253,1080,69,BT,BLUE,8)
d.text(1240,281,'CURATION','xs',anchor='middle',fill=BLUE)
d.text(1240,313,'Random  |  Chronological  |  Interest-based','s',anchor='middle')
d.arrow('M850 322 V377','blue',sw=4)

# 先前累计接触决定本次R；本次接触只更新后续历史。
d.box(270,380,350,83,GRAY,MUTED,8,dash='7 5')
d.lines(445,414,['Prior same-type','exposure history'],'s',step=34,anchor='middle')
d.box(700,380,330,83,BT,BLUE,8)
d.docs(717,397,.61,mourning=True)
d.text(793,413,'Personal feed','s')
d.text(793,448,'≤10 posts','s')
d.box(1110,370,560,108,OT,ORANGE,9)
d.text(1390,402,'B · baseline   D · climate   R · weight','xs',anchor='middle')
d.formula(1390,438,38)
d.text(1390,470,'R → 0  ⇒  U → B','xs',anchor='middle',fill=MUTED)
d.arrow('M1030 421 H1110','blue',sw=4)
d.text(1069,404,'D','xs',anchor='middle',fill=BLUE)
d.arrow('M620 408 H653 V357 H1240 V370','gray',dash='7 5',sw=3)
d.text(671,393,'R','xs',fill=MUTED)


# 门槛先于生成；未达门槛则本回合不发帖。
d.arrow('M1670 421 H1693','orange',sw=3.5)
d.diamond(1805,421,112,48)
d.text(1805,432,'U ≥ threshold','xs',anchor='middle')
d.box(1940,388,100,68,GRAY,BORDER,8)
d.lines(1990,415,['No','post'],'s',step=31,anchor='middle')
d.arrow('M1917 421 H1940','ink')
d.text(1928,399,'no','xs',anchor='middle')
d.arrow('M1805 469 V516','orange',sw=3.5)
d.text(1822,504,'yes','xs',fill=ORANGE)

# 生成人设与最多5条实际feed摘录；成功发布之后才进入回流资格路径。
d.box(270,516,350,88,GRAY,BORDER,8)
d.person(313,546,.68)
d.text(365,565,'Agent persona','s')
d.box(700,516,550,88,BT,BLUE,8)
d.text(975,550,'≤5 feed excerpts','s',anchor='middle')
d.text(975,587,'≤120 characters / excerpt','s',anchor='middle')
d.arrow('M805 463 V516','blue',sw=3.5)
d.arrow('M620 560 H655 V610 H1464 V560 H1490','ink',sw=3)
d.arrow('M1250 560 H1490','blue',sw=3.5)
d.box(1490,516,430,88,OT,ORANGE,9)
d.text(1705,552,'LLM post','b',anchor='middle')
d.text(1705,590,'generation','b',anchor='middle')
d.arrow('M1920 560 H1960','orange',sw=4)
d.docs(1965,523,.68)
d.text(2060,601,'Published post','s',anchor='middle')
d.arrow('M2007 560 H2336 V287 H2322','blue',sw=4)
d.box(2080,253,242,69,BT,BLUE,8)
d.lines(2201,281,['Eligible for','later display'],'s',step=32,anchor='middle')
d.arrow('M2200 253 V237 H650 V272 H620','blue',sw=3.5)

# 当前接触记录与发帖是否成功无关，灰虚线路径回到下一回合的先前历史。
d.box(2080,380,242,83,GRAY,MUTED,8,dash='7 5')
d.lines(2201,414,['Updated','contact history'],'s',step=34,anchor='middle')
d.arrow('M865 463 V490 H2064 V422 H2080','gray',dash='7 5',sw=3)
d.arrow('M2200 463 V639 H250 V422 H270','gray',dash='7 5',sw=3)
d.box(700,617,1030,39,WHITE,WHITE,0)
d.text(1215,647,'Contact stored for later R · independent of posting','s',anchor='middle',fill=MUTED)

# 所有未展开限制用短句补足，不画不存在的结果轨迹。
d.footer()
d.text(48,833,'Return: Chronological—after batch, later batches; Random / Interest-based—eligible next week.','xs',fill=MUTED)
d.save(Path(__file__).with_name('c_swimlane.svg'))
