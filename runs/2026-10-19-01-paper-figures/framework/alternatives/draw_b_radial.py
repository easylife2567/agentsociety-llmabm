"""横向椭圆反馈候选：原生可编辑SVG，保留冻结正文的科学关系。"""
from pathlib import Path
from diagram_lib import *
p=Path(__file__).parent
d=Diagram('B · Curation–expression feedback', 'Digital mourning: exposure, selective participation, and post recirculation')
# 现实经验语料与仿真输入分开；白花和蜡烛仅表达研究情境。
d.box(48,110,530,122,GRAY)
d.memorial(102,176,.82)
d.text(165,147,'EMPIRICAL CONTEXT','xs',fill=MUTED)
d.text(165,184,'49,930 posts','b')
d.text(165,219,'Douyin & Xiaohongshu','xs')
d.box(618,110,722,122,BT,BLUE)
d.text(642,147,'FROZEN SIMULATION INPUTS','xs',fill=BLUE)
d.text(642,184,'Time-stamped external samples','b')
d.text(642,219,'Shared across regimes within each seed','xs')
d.box(1380,110,972,122,GRAY)
d.person(1420,174,.68)
d.text(1462,147,'FIXED POPULATION & INDIVIDUAL THRESHOLDS','xs',fill=MUTED)
d.text(1462,184,'100 agents · 5 fixed author types','b')
d.text(1462,219,'W12–W22 · 1 expression opportunity per week','xs')

def number(cx,cy,t,color):
 d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{"#9C4300" if color == ORANGE else color}"/>')
 d.text(cx,cy+10,t,'xs','middle',WHITE)

# 五站点沿椭圆分布，构成可追踪的内容回路。
d.arrow('M760 232 V245 H250 V335','blue')
d.box(70,335,350,190,BT,BLUE,20)
number(102,371,'1',BLUE)
d.text(136,383,'Candidate pool','h')
d.memorial(122,456,.73)
d.lines(174,430,['Regime-specific','External +','generated posts'],'s',36)
d.arrow('M420 405 C464 405 454 315 500 315','blue')

d.box(500,265,390,150,BT,BLUE,20)
number(532,301,'2',BLUE)
d.text(566,313,'Personal feed','h')
d.docs(527,340,.68,True)
d.text(598,359,'≤10 eligible posts','s',fill=BLUE)
d.text(598,397,'Current exposure','xs')
d.arrow('M890 335 H1010','blue')
d.text(943,312,'D','math',fill=BLUE)

d.box(1010,265,620,230,OT,ORANGE,20)
number(1042,301,'3',ORANGE)
d.text(1076,313,'Expression gate','h')
d.text(1036,352,'B baseline · D climate · R exposure','s')
d.formula(1320,398,36)
d.box(1053,417,534,48,WHITE,ORANGE,8)
d.text(1320,452,'U ≥ individual threshold?','s','middle')
d.text(1320,486,'R → 0 ⇒ U → B','xs','middle',ORANGE)
# 达标分支弯入右侧生成器；未达标分支终止。
d.arrow('M1630 370 C1725 370 1735 423 1830 423','orange')
d.text(1738,389,'yes','s',fill=ORANGE)
d.arrow('M1560 495 V523 H1640','gray')
d.text(1580,512,'no','xs',fill=MUTED)
d.box(1641,500,183,49,GRAY,BORDER,8)
d.text(1732,534,'No post','s','middle')
# 个人门槛是固定输入，不由feed或生成内容更新。
d.arrow('M1700 232 V291 H1630','gray')

d.box(1830,335,522,185,OT,ORANGE,20)
number(1862,371,'4',ORANGE)
d.text(1896,383,'LLM generation','h')
d.text(1856,431,'Persona + ≤5 feed excerpts','s')
d.text(1856,472,'≤120 characters per excerpt','s')
d.text(1856,508,'Only after threshold activation','xs',fill=ORANGE)
d.arrow('M2090 520 C2090 578 1985 580 1880 580','orange')

d.box(1400,550,480,91,BT,BLUE,20)
number(1432,581,'5',BLUE)
d.docs(1462,565,.70)
d.text(1542,585,'Published post','h')
d.text(1542,625,'Successful publication','xs')
# 回到候选池的是成功发布帖；箭头不代表即时再展示。
d.arrow('M1400 593 C1150 655 500 655 95 650 Q48 650 48 606 V430 H70','blue',sw=4.5)
d.text(70,584,'Chronological: after batch','s',fill=BLUE)
d.text(70,625,'Random / Interest: next week','s',fill=BLUE)

# 本次接触无条件记入历史，用于后续R；与是否发帖无关。
d.box(655,505,603,126,GRAY,MUTED,14,'8 6')
d.text(679,544,'Prior exposure history','h')
d.text(679,582,'Cumulative same-type contact','s')
d.text(679,619,'For subsequent actions','xs')
d.arrow('M694 415 V505','gray','8 6',3.2)
d.text(717,458,'store every exposure','xs',fill=MUTED)
d.arrow('M1258 548 H1300 V495','gray','8 6',3.2)
d.text(1320,539,'future R','xs',fill=MUTED)

d.footer()
d.save(p/'b_radial.svg')
