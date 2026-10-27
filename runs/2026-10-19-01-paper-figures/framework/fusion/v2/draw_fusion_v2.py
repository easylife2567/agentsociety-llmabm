"""融合图V2：明确圆环端口、外侧回流与更有力度的局部语义配色。"""
from pathlib import Path
from html import escape
from math import cos,sin,radians,hypot

OUT=Path(__file__).resolve().parent
W,H=2800,1100
INK='#17212B'; MUTED='#435260'; BORDER='#8C9AA7'; WHITE='#FFFFFF'
BLUE='#0072B2'; ORANGE='#D55E00'; WARM='#AA4600'; RETURN='#283D4F'
BT='#D8EAF6'; OT='#FFE5C7'; GRAY='#EEF2F5'
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="70.7143mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">Research framework: empirical analysis and circular curation–expression feedback, version 2</title><desc id="desc">White background and restrained, stronger blue and vermilion modules. Platform analysis occupies approximately 34 percent and simulation 66 percent of the main research area. The three open circular arcs are a schematic mechanism, not data proportions. The central card lies wholly inside the circle, while D, later R and utility output pass through deliberate gaps. Only successfully published posts return to the regime-specific pool. Reading updates same-type history independently of posting. Fixed author types and separate frozen inputs are retained. Chrysanthemums, memorial ribbon and candle indicate context only. No individual platform proportions are shown.</desc><defs>''']
for name,c in [('ink',INK),('blue',BLUE),('orange',ORANGE),('return',RETURN),('gray',MUTED)]:
 parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="{c}"/></marker>')
parts.append(f'''</defs><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK};font-size:36px}}.title{{font-size:44px;font-weight:700}}.head{{font-size:40px;font-weight:700}}.body{{font-size:36px}}.small{{font-size:34px}}.note{{font-size:32px}}.big{{font-size:84px;font-weight:700}}.math{{font-family:Times New Roman,Times,serif;font-size:37px;font-style:italic}}</style><rect width="{W}" height="{H}" fill="white"/>''')

def text(x,y,s,cl='body',anchor='start',color=INK,weight=None,size=None):
 style=f'fill:{color}'+(f';font-weight:{weight}' if weight else '')+(f';font-size:{size}px' if size else '')
 parts.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}" style="{style}">{escape(s)}</text>')
def lines(x,y,ss,cl='body',step=43,**kw):
 for i,s in enumerate(ss):text(x,y+i*step,s,cl,**kw)
def box(x,y,w,h,fill=WHITE,stroke=BORDER,sw=2.4,r=10,dash=None):
 parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def path(d,c=INK,sw=3,marker=None,dash=None):
 parts.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{marker})"' if marker else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def circle(x,y,r,fill=WHITE,stroke=INK,sw=2.2):
 parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def badge(x,y,n,c):
 circle(x,y,26,c,c,1);text(x,y+12,str(n),'body',anchor='middle',color=WHITE,weight=700)
def arc(cx,cy,r,start,end,c):
 # 弧线与箭头头部分开画，避免线宽连带放大箭头。
 a,b=radians(start),radians(end)
 x1,y1=cx+r*cos(a),cy+r*sin(a);x2,y2=cx+r*cos(b),cy+r*sin(b)
 path(f'M{x1:.3f} {y1:.3f} A{r} {r} 0 0 1 {x2:.3f} {y2:.3f}',c,10)
 dx,dy=-sin(b),cos(b);nx,ny=-dy,dx
 tip=(x2+dx*7,y2+dy*7);base=(x2-dx*23,y2-dy*23)
 left=(base[0]+nx*17,base[1]+ny*17);right=(base[0]-nx*17,base[1]-ny*17)
 # 闭合path而非polygon，draw.io保持原生矢量箭头三角形。
 parts.append(f'<path d="M{tip[0]:.3f} {tip[1]:.3f} L{left[0]:.3f} {left[1]:.3f} L{right[0]:.3f} {right[1]:.3f} Z" fill="{c}" stroke="{c}" stroke-width="1"/>')
def flower(x,y,s=1):
 parts.append(f'<g transform="translate({x} {y}) scale({s})">')
 for angle in range(0,360,20):parts.append(f'<ellipse cx="0" cy="-18" rx="4.6" ry="20" transform="rotate({angle})" fill="white" stroke="{RETURN}" stroke-width="1.3"/>')
 for angle in range(10,360,30):parts.append(f'<ellipse cx="0" cy="-9" rx="3.4" ry="11" transform="rotate({angle})" fill="white" stroke="{RETURN}" stroke-width="1.1"/>')
 circle(0,0,5,'#D3BD86',RETURN,1);parts.append('</g>')
def paper(x,y,s=1):
 parts.append(f'<g transform="translate({x} {y}) scale({s})" fill="white" stroke="{INK}" stroke-width="2.8"><path d="M0 0 H36 L52 16 V66 H0Z"/><path d="M36 0 V16 H52 M9 29 H42 M9 41 H42 M9 53 H31" fill="none"/></g>')

# 01：经验研究保持独立，三七开布局；来源不承担平台比例信息。
text(48,66,'01  Platform data analysis','title')
text(1010,66,'02  Simulation modeling','title')
text(2750,65,'100 fixed-type agents · W12–W22','small',anchor='end',color=MUTED)
path('M950 100 V1015',BORDER,1.8,dash='7 11')
parts.append(f'<g aria-label="Memorial bouquet, ribbon and candle"><path d="M104 189 L159 284 M158 155 L159 284 M210 194 L159 284" fill="none" stroke="{RETURN}" stroke-width="3.5"/><path d="M145 252 Q126 235 117 217 M171 249 Q190 225 204 222" fill="none" stroke="{RETURN}" stroke-width="2.7"/>')
flower(103,184,.9);flower(158,150,1.1);flower(213,194,.82)
parts.append(f'<path d="M144 255 L173 266 L162 282 L137 271Z M144 269 L134 303 L151 293 L160 307 L167 278" fill="{RETURN}" stroke="{INK}" stroke-width="1.5"/><rect x="233" y="233" width="27" height="63" rx="3" fill="white" stroke="{INK}" stroke-width="2.8"/><path d="M247 232 V222" stroke="{INK}" stroke-width="2.4"/><path d="M247 219 C231 206 243 192 247 185 C262 204 262 212 247 219Z" fill="{ORANGE}"/><path d="M219 300 H274" stroke="{RETURN}" stroke-width="2.5"/></g>')
text(316,177,'49,930','big')
text(316,232,'posts · Jan–May 2026','body')
text(316,285,'Douyin + Xiaohongshu','body')

box(48,354,840,146,WHITE,BLUE)
box(48,354,840,51,BLUE,BLUE,r=0,sw=0)
text(73,392,'Content coding','small',color=WHITE,weight=700)
text(73,441,'Education · Mourning · Meme','small')
text(73,479,'Other · Marketing · Noise','small')
path('M468 500 V525 H247 V543',INK,3.2,'ink')
path('M468 525 H686 V543',INK,3.2,'ink')
for x,w,title,body in [(48,400,'Temporal patterns',['Weekly counts','Content composition']),(490,398,'Platform differences',['Compare expression','trajectories'])]:
 box(x,548,w,176,WHITE,BLUE,sw=2.8)
 box(x,548,w,54,BLUE,BLUE,r=0,sw=0)
 text(x+w/2,587,title,'small',anchor='middle',color=WHITE,weight=700)
 lines(x+22,651,body,'small',step=44)
path('M247 724 V755 H686 V724',INK,3)
path('M468 755 V790',INK,3.2,'ink')
text(468,838,'Mourning peak → later meme growth','small',anchor='middle')
text(468,882,'Shared sequence; divergent trajectories','small',anchor='middle')
text(468,945,'Patterns + calibration references','body',anchor='middle',weight=700)

# 模拟初始化条，固定人设为共同模型条件，不连成学习/类型更新路径。
box(1010,110,684,94,BT,BLUE)
box(1010,110,10,94,BLUE,BLUE,r=0,sw=0)
text(1040,149,'Frozen, time-stamped posts','small',weight=700)
text(1040,190,'Shared across regimes within seed','note')
box(1725,110,1025,94,GRAY,BORDER)
box(1725,110,10,94,RETURN,RETURN,r=0,sw=0)
text(1754,149,'Fixed author type + individual threshold','small',weight=700)
text(1754,190,'Case-grounded author mix + B / D / R','small')

# 内容回流采用左侧外通道；与D/R径向输入彻底分开。
path('M1915 980 V986 Q1915 1002 1897 1002 H1010 Q988 1002 988 980 V465 Q988 445 1008 445 H1020',RETURN,3.6,'return')
text(1040,986,'Published posts return to pool','note',color=MUTED)
# 经验分析桥在回流通道外侧，终点高度不同，互不交叉。
path('M888 921 H951 Q968 921 968 904 V322 Q968 306 985 306 H1013',BLUE,3.6,'blue')
text(48,1002,'Empirical patterns → mechanism questions','small',color=MUTED)

# 三个宏观弧段留出左右端口；中央卡片各角与圆弧留出净距。
cx,cy,r=1875,540,252
for start,end in [(200,325),(20,90),(100,145)]:
 a,b=radians(start),radians(end);rr=r-18
 path(f'M{cx+rr*cos(a):.3f} {cy+rr*sin(a):.3f} A{rr} {rr} 0 0 1 {cx+rr*cos(b):.3f} {cy+rr*sin(b):.3f}',BORDER,1.3)
arc(cx,cy,r,200,325,BLUE)
arc(cx,cy,r,20,90,ORANGE)
arc(cx,cy,r,100,145,RETURN)

# 1：可见性配置，制度名称纳入候选池模块，腾出历史线的直通空间。
badge(1046,261,1,BLUE)
text(1091,257,'Visibility','head')
text(1091,303,'configuration','head')
box(1020,350,480,145,BT,BLUE,sw=2.8)
box(1020,350,480,54,BLUE,BLUE,r=0,sw=0)
text(1260,390,'Regime-specific pool','small',anchor='middle',color=WHITE,weight=700)
text(1260,442,'Random · Chronological','small',anchor='middle')
text(1260,482,'Interest-based','small',anchor='middle')
path('M1650 204 V325 H1260 V350',BLUE,3.2,'blue')
path('M1260 495 V545',BLUE,3.5,'blue')
box(1020,545,480,100,BT,BLUE,sw=2.8)
text(1260,584,'Personal feed','body',anchor='middle',weight=700)
text(1260,628,'≤10 eligible posts','small',anchor='middle')

# 环心效用模块：角点半径约224，小于内环半径234。
box(1695,418,360,246,OT,WARM,sw=2.8)
box(1695,418,360,51,WARM,WARM,r=0,sw=0)
text(cx,456,'Expression utility','small',anchor='middle',color=WHITE,weight=700)
parts.append(f'<text x="{cx}" y="518" class="math" text-anchor="middle">U<tspan baseline-shift="sub" font-size="24">it</tspan> = B<tspan baseline-shift="sub" font-size="24">i</tspan> + R<tspan baseline-shift="sub" font-size="24">it</tspan>(D<tspan baseline-shift="sub" font-size="24">it</tspan> − B<tspan baseline-shift="sub" font-size="24">i</tspan>)</text>')
text(cx,566,'B  Baseline utility','note',anchor='middle')
text(cx,607,'D  Feed response','note',anchor='middle')
text(cx,648,'R  Prior-exposure weight','note',anchor='middle')
# D穿过左侧开放端口；无白色遮罩覆盖圆环。
path('M1500 595 H1695',INK,3.4,'ink')
text(1574,577,'D','note',color=MUTED)

# 接触历史独立于是否发布：从feed下方直达历史，无制度文字阻挡。
box(1020,735,480,112,GRAY,MUTED,sw=2.4,dash='9 6')
text(1260,778,'Same-type exposure history','small',anchor='middle',weight=700)
text(1260,823,'For later actions','small',anchor='middle')
path('M1260 645 V735',MUTED,3,'gray',dash='8 7')
text(1281,700,'contact','note',color=MUTED)
path('M1500 795 H1585 V635 H1660 V648 H1695',MUTED,3,'gray',dash='8 7')
text(1565,716,'later R','note',anchor='end',color=MUTED)

# 2：效用输出穿过右侧开放端口，先固定门槛后生成。
badge(2255,261,2,ORANGE)
text(2300,257,'Selective','head')
text(2300,303,'expression','head')
parts.append(f'<polygon points="2485,327 2730,394 2485,461 2240,394" fill="{OT}" stroke="{WARM}" stroke-width="2.8"/>')
text(2485,406,'U ≥ fixed threshold?','small',anchor='middle',weight=700)
path('M2055 518 H2170 V394 H2240',INK,3.4,'ink')
path('M2485 461 V560',INK,3.4,'ink')
text(2468,526,'Yes','note',anchor='end',color=MUTED)
box(2550,484,190,48,GRAY,BORDER)
text(2645,519,'No post','note',anchor='middle')
path('M2730 394 H2770 V508 H2740',MUTED,2.8,'gray')
text(2750,459,'No','note',anchor='end',color=MUTED)
box(2220,560,520,135,OT,WARM,sw=2.8)
box(2220,560,520,50,WARM,WARM,r=0,sw=0)
text(2480,598,'LLM post generation','small',anchor='middle',color=WHITE,weight=700)
text(2480,649,'Persona + ≤5 feed excerpts','small',anchor='middle')
text(2480,686,'≤120 characters each','note',anchor='middle')
path('M2480 695 V748',INK,3.4,'ink')
box(2220,748,520,95,WHITE,RETURN,sw=2.8)
paper(2245,768,.9)
text(2326,788,'Published post','body',weight=700)
text(2326,831,'Successful publication','small')

# 3：回流资格模块有明确节点；仅成功发布的帖子接入。
box(1610,850,610,130,WHITE,RETURN,sw=2.8)
box(1610,850,610,48,RETURN,RETURN,r=0,sw=0)
badge(1641,874,3,RETURN)
text(1681,887,'Content recirculation','small',color=WHITE,weight=700)
text(1915,930,'Chronological: after batch; visible later','note',anchor='middle')
text(1915,966,'Random / Interest: eligible next week','note',anchor='middle')
path('M2480 843 V928 H2220',RETURN,3.6,'return')

# 底部保留比较安排与共同解释；长限定放README图注。
text(1010,1040,'3 regimes × 3 seeds  ·  Interest-based interventions: B=0 / D=1 / R=1','note',color=MUTED)
path('M48 1057 H2750',INK,2.3)
text(1400,1086,'Empirical patterns + simulated feedback → Public representation reorganization','body',anchor='middle',weight=700)

# 几何约束直接反映设计目的，不把“图很漂亮”当作验证。
assert max(hypot(x-cx,y-cy) for x in (1695,2055) for y in (418,664))<r-18
(OUT/'framework_fusion_en_v2.svg').write_text('\n'.join(parts+['</svg>']))
