"""融合ProAgent第二版机制细节与环形构图；原生可编辑SVG，标准库实现。"""
from pathlib import Path
from html import escape
from math import sin,cos,radians

OUT=Path(__file__).resolve().parent
W,H=2600,980
INK='#17212B'; MUTED='#48515D'; BORDER='#BAC2CA'; WHITE='#FFFFFF'
BLUE='#0072B2'; ORANGE='#D55E00'; SLATE='#616A73'
BT='#EAF4FA'; OT='#FFF1E6'; GRAY='#F3F5F7'
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="67.8462mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">Complementary research with an expanded circular curation–expression mechanism</title><desc id="desc">Fusion of framework_proagent_en_v2 and the white-background orbit design. Empirical analysis occupies approximately 35 percent and simulation 65 percent of the main research area. The main loop connects visibility configuration, selective expression and content recirculation; current contact independently updates history for later R. Authors retain fixed types. Curves and icon counts are schematic. Memorial bouquet and candle indicate context only. No individual platform quantities or proportions are displayed.</desc><defs>''']
for name,c in [('ink',INK),('blue',BLUE),('orange',ORANGE),('slate',SLATE),('gray',MUTED)]:
 parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="8.8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>')
parts.append(f'''</defs><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK};font-size:34px}}.title{{font-size:43px;font-weight:700}}.head{{font-size:38px;font-weight:700}}.body{{font-size:34px}}.small{{font-size:32px}}.note{{font-size:31px}}.big{{font-size:70px;font-weight:700}}.math{{font-family:Times New Roman,Times,serif;font-size:37px;font-style:italic}}</style><rect width="{W}" height="{H}" fill="white"/>''')
def text(x,y,s,cl='body',anchor='start',color=INK,size=None,weight=None):
 style=[f'fill:{color}']
 if size:style.append(f'font-size:{size}px')
 if weight:style.append(f'font-weight:{weight}')
 parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cl}" style="{";".join(style)}">{escape(s)}</text>')
def lines(x,y,ss,cl='body',step=38,**kw):
 for k,s in enumerate(ss):text(x,y+k*step,s,cl,**kw)
def box(x,y,w,h,fill=WHITE,stroke=BORDER,r=10,sw=2,dash=None):
 parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def path(d,c=INK,sw=2.5,marker=None,dash=None,halo=False):
 if halo:parts.append(f'<path d="{d}" fill="none" stroke="white" stroke-width="{sw+6}" stroke-linejoin="round"/>')
 parts.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{marker})"' if marker else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def circle(x,y,r,fill=WHITE,stroke=INK,sw=2):
 parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def badge(x,y,n,c):
 circle(x,y,25,WHITE,c,2.6);text(x,y+11,str(n),'body',anchor='middle')
def arc(cx,cy,r,start,end,c,marker):
 x1,y1=cx+r*cos(radians(start)),cy+r*sin(radians(start));x2,y2=cx+r*cos(radians(end)),cy+r*sin(radians(end))
 path(f'M{x1:.2f} {y1:.2f} A{r} {r} 0 0 1 {x2:.2f} {y2:.2f}',c,11,marker)
def paper(x,y,s=1):
 parts.append(f'<g transform="translate({x} {y}) scale({s})" fill="white" stroke="{INK}" stroke-width="2.5"><path d="M0 0 H36 L52 16 V66 H0 Z"/><path d="M36 0 V16 H52 M9 29 H42 M9 41 H42 M9 53 H31" fill="none"/></g>')
def flower(x,y,s=1):
 # 白菊：两层细长花瓣，避免图标仅为通用六瓣小花。
 parts.append(f'<g transform="translate({x} {y}) scale({s})">')
 for angle in range(0,360,20):
  parts.append(f'<ellipse cx="0" cy="-18" rx="4.6" ry="20" transform="rotate({angle})" fill="white" stroke="{SLATE}" stroke-width="1.1"/>')
 for angle in range(10,360,30):
  parts.append(f'<ellipse cx="0" cy="-9" rx="3.4" ry="11" transform="rotate({angle})" fill="white" stroke="{SLATE}" stroke-width=".9"/>')
 circle(0,0,5,'#DBD5C6',SLATE,1)
 parts.append('</g>')

# 两项研究等高区域约840:1620，白底与细分隔保持长横版。
text(48,63,'01  Platform data analysis','title')
text(960,63,'02  Simulation modeling','title')
text(2550,62,'100 fixed-type agents · W12–W22','small',anchor='end',color=MUTED)
path('M906 93 V890',BORDER,1.7,dash='7 10')

# 不同样式的纪念花束、缎带与蜡烛，全部仅在语料情境区。
parts.append(f'<g aria-label="Memorial bouquet with chrysanthemum, ribbon and candle"><path d="M104 176 L157 255 M155 151 L157 255 M201 186 L157 255" fill="none" stroke="{SLATE}" stroke-width="3"/><path d="M144 229 Q123 219 115 203 M168 226 Q187 207 199 207" fill="none" stroke="{SLATE}" stroke-width="2"/>')
flower(103,173,.8);flower(155,142,1);flower(204,180,.76)
parts.append(f'<path d="M145 230 L172 239 L163 253 L139 245Z M145 240 L137 274 L151 266 L158 279 L165 247" fill="{SLATE}" stroke="{INK}" stroke-width="1.3"/><rect x="209" y="223" width="25" height="55" rx="3" fill="white" stroke="{INK}" stroke-width="2.2"/><path d="M221 221 V213" stroke="{INK}" stroke-width="2"/><path d="M221 211 C207 199 218 187 221 181 C236 198 234 205 221 211Z" fill="{ORANGE}"/><path d="M196 281 H246" stroke="{SLATE}" stroke-width="2"/></g>')
text(287,166,'49,930','big')
text(287,214,'posts · Jan–May 2026','body')
text(287,260,'Douyin + Xiaohongshu','body')

box(48,308,790,123,GRAY,BORDER)
box(48,308,9,123,BLUE,BLUE,r=0,sw=0)
text(75,348,'Content coding','head')
text(75,385,'Education · Mourning · Meme','small')
text(75,419,'Other · Marketing · Noise','small')
path('M443 431 V449',INK,2.6)
path('M443 449 H233 V470',INK,2.3,'ink')
path('M443 449 H650 V470',INK,2.3,'ink')
for x,w,title,body in [(48,371,'Temporal patterns',['Weekly counts','Content composition']),(457,381,'Platform differences',['Compare expression','trajectories'])]:
 box(x,470,w,154,WHITE,BLUE)
 box(x,470,w,48,BT,BT,r=0,sw=0)
 text(x+18,506,title,'small',weight=700)
 lines(x+18,557,body,'small',step=39)
path('M233 624 V650 H650 V624',INK,2.4)
path('M443 650 V680',INK,2.5,'ink')
text(443,726,'Mourning peak → later meme growth','small',anchor='middle')
text(443,769,'Shared sequence; divergent trajectories','small',anchor='middle')
text(443,834,'Patterns + calibration references','body',anchor='middle',weight=700)

# 另行冻结输入与固定人设分开，不把全量经验语料画成输入池。
box(960,102,700,91,BT,BORDER)
text(981,139,'Frozen, time-stamped posts','small',weight=700)
text(981,176,'Shared across regimes within seed','small')
box(1690,102,860,91,GRAY,BORDER)
text(1712,139,'Fixed author type + individual threshold','small',weight=700)
text(1712,176,'Case-grounded author mix + B / D / R','small')

# 经验模式只向模型提出机制问题；模型设定的细节由右侧人设条说明。
path('M838 815 H916 Q942 815 942 780 V295 H978',BLUE,3.2,'blue')
text(925,862,'Mechanism questions','note',color=MUTED)

# 环形主机制保留，局部模块承接ProAgent版的显式流程。
cx,cy,r=1770,492,248
circle(cx,cy,r-19,WHITE,BORDER,1.5)
arc(cx,cy,r,-154,-39,BLUE,'blue')
arc(cx,cy,r,-23,72,ORANGE,'orange')
arc(cx,cy,r,100,205,SLATE,'slate')
for angle in [-148,-32,90]:
 x=cx+(r-19)*cos(radians(angle));y=cy+(r-19)*sin(radians(angle));circle(x,y,4,INK,INK,1)

# 1 可见性配置：候选池→个人信息流。
badge(1008,248,1,BLUE)
text(1048,243,'Visibility','head')
text(1048,284,'configuration','head')
box(980,327,480,77,BT,BLUE)
text(1220,375,'Regime-specific pool','small',anchor='middle',weight=700)
path('M1510 193 V309 H1220 V327',BLUE,2.8,'blue')
path('M1220 404 V439',BLUE,2.6,'blue')
box(980,439,480,96,WHITE,BLUE)
text(1220,478,'Personal feed ≤10 posts','small',anchor='middle',weight=700)
text(1220,517,'Selected by the assigned regime','note',anchor='middle')
text(1220,578,'Random · Chronological','small',anchor='middle')
text(1220,615,'Interest-based','small',anchor='middle')

# 中央表达激活与精确数学公式，白底环内使用小块暖色。
box(1557,354,426,248,OT,ORANGE)
text(cx,393,'Expression activation','small',anchor='middle',weight=700)
parts.append(f'<text x="{cx}" y="447" class="math" text-anchor="middle">U<tspan baseline-shift="sub" font-size="24">it</tspan> = B<tspan baseline-shift="sub" font-size="24">i</tspan> + R<tspan baseline-shift="sub" font-size="24">it</tspan>(D<tspan baseline-shift="sub" font-size="24">it</tspan> − B<tspan baseline-shift="sub" font-size="24">i</tspan>)</text>')
text(cx,492,'B  Baseline utility','small',anchor='middle')
text(cx,534,'D  Current-feed response','small',anchor='middle')
text(cx,576,'R  Prior-exposure weight','small',anchor='middle')
path('M1460 486 H1503 V534 H1557',INK,2.8,'ink',halo=True)
text(1505,477,'D','note',color=MUTED)

# 独立历史支路来自阅读接触；存储只用于后续行动，不依赖发帖。
box(980,666,480,82,GRAY,MUTED,dash='8 6')
text(1220,699,'Same-type exposure history','small',anchor='middle',weight=700)
text(1220,734,'Store now; use in later actions','note',anchor='middle')
path('M980 490 H963 V706 H980',MUTED,2.7,'gray',dash='7 7')
text(1000,652,'Feed contact','note',color=MUTED)
path('M1460 706 H1512 V576 H1557',MUTED,2.7,'gray',dash='7 7',halo=True)

# 2 选择性表达：先门槛、再生成、再确认成功发表。
badge(2128,248,2,ORANGE)
text(2168,243,'Selective','head')
text(2168,284,'expression','head')
parts.append(f'<polygon points="2315,300 2535,360 2315,420 2095,360" fill="white" stroke="{ORANGE}" stroke-width="2.3"/>')
text(2315,372,'U ≥ fixed threshold?','note',anchor='middle',weight=700)
path('M1983 446 H2050 V360 H2095',INK,2.8,'ink',halo=True)
path('M2315 420 V480',INK,2.7,'ink')
text(2297,461,'Yes','note',anchor='end',color=MUTED)
box(2355,416,205,46,GRAY,BORDER)
text(2458,449,'No post','note',anchor='middle')
path('M2535 360 H2574 V439 H2560',MUTED,2.3,'gray')
text(2542,401,'No','note',color=MUTED)
box(2100,480,450,130,OT,ORANGE)
text(2325,519,'LLM post generation','small',anchor='middle',weight=700)
text(2325,558,'Persona + ≤5 feed excerpts','note',anchor='middle')
text(2325,595,'≤120 characters per excerpt','note',anchor='middle')
path('M2325 610 V654',INK,2.7,'ink')
box(2100,654,450,92,WHITE,BORDER)
paper(2121,669,.86)
text(2190,693,'Published post','small',weight=700)
text(2190,733,'Successful publication','note')

# 3 内容回流：仅成功发表的帖子进入回流资格，而非更新作者类型。
badge(1562,786,3,SLATE)
text(1602,797,'Content recirculation','head')
text(1770,843,'Chronological: after batch; later batches','note',anchor='middle')
text(1770,881,'Random / Interest: eligible next week','note',anchor='middle')
path('M2100 700 H2060 V785 H2030',SLATE,2.8,'slate')
# 内容环接回候选池；下半环的可见灰弧与这段回连保持同一语义。
path('M1546 387 H1490 V366 H1460',SLATE,2.8,'slate',halo=True)
path('M1770 759 V750 H1727 V736',SLATE,2.3,'slate')

# 比较安排简写放在底部，不恢复旧版的长段说明。
text(980,915,'3 regimes × 3 seeds  ·  Interest-based interventions: B=0 / D=1 / R=1','note',color=MUTED)
path('M48 928 H2550',INK,2)
text(1300,956,'Empirical patterns + simulated feedback → Public representation reorganization','body',anchor='middle',weight=700)
(OUT/'framework_fusion_en_v1.svg').write_text('\n'.join(parts+['</svg>']))
