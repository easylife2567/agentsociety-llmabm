"""报刊式研究地图：开放排版、衬线大字、细线与单一朱红机制回路。"""
from pathlib import Path
from html import escape

OUT=Path(__file__).resolve().parent
INK='#171717'; PAPER='#FFFFFF'; RED='#D55E00'; BLUE='#0072B2'; GRAY='#60605C'
p=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="63.75mm" viewBox="0 0 2400 850" role="img" aria-labelledby="title desc"><title id="title">Postmortem public representation: an editorial research map</title><desc id="desc">An open editorial layout joins empirical characterization and generative explanation. Approximate empirical/simulation visual area is 35:65. The same scientific mechanism is represented without framed cards. All types are fixed. Candle and white flowers indicate context only; no source-platform proportions are shown.</desc><defs>''']
for name,c in [('ink',INK),('red',RED),('blue',BLUE),('gray',GRAY)]:
 p.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>')
p.append(f'</defs><rect width="2400" height="850" fill="{PAPER}"/>')
def text(x,y,t,size=32,font='Arial',weight=400,fill=INK,anchor='start',italic=False):
 p.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-family:{font};font-size:{size}px;font-weight:{weight};fill:{fill};font-style:{"italic" if italic else "normal"}">{escape(t)}</text>')
def line(d,c=INK,sw=2,dash=None,arrow=None):
 p.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' marker-end="url(#{arrow})"' if arrow else '')+'/>')
def circle(x,y,r,c,sw=2,fill='none'):
 p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')

# 报刊式页眉与两个开放栏；无填色阶段卡片、无面板外框。
text(48,65,'Postmortem public representation',60,'Georgia',700)
text(2352,64,'TWO COMPLEMENTARY STUDIES',29,weight=700,anchor='end')
line('M48 93 H2352',INK,4)
text(48,217,'01',128,'Georgia',700,BLUE)
text(232,174,'Observe',64,'Georgia',700)
text(232,218,'Platform content analysis',31)
text(917,217,'02',128,'Georgia',700,RED)
text(1102,174,'Explain',64,'Georgia',700)
text(1102,218,'Controlled agent-based simulation',31)

text(48,318,'49,930',86,'Georgia',700)
text(440,317,'posts',37,'Georgia',italic=True)
text(48,361,'Douyin + Xiaohongshu',34)
text(48,401,'Jan–May 2026',30,fill=GRAY)
line('M48 424 H780',INK,1.5)
# 原生矢量悼念符号，不作为模型变量。
p.append(f'<g aria-label="Mourning context" transform="translate(663 331) scale(1.1)"><ellipse cx="0" cy="48" rx="35" ry="5" fill="#D9D6CD"/><rect x="-12" y="-5" width="24" height="50" rx="3" fill="white" stroke="{INK}" stroke-width="2"/><path d="M0 -5 V-13" stroke="{INK}" stroke-width="2"/><path d="M0 -14 C-16 -26 -2 -40 0 -44 C13 -29 16 -24 0 -14Z" fill="{RED}"/>')
for fx,fy in [(-35,16),(35,18)]:
 p.append(f'<g transform="translate({fx} {fy})"><path d="M0 0 L3 31 M2 21 L-9 14 M2 15 L12 8" fill="none" stroke="{GRAY}" stroke-width="2"/>')
 for angle in range(0,360,60):p.append(f'<ellipse cx="0" cy="-7" rx="5" ry="9" transform="rotate({angle})" fill="white" stroke="{GRAY}" stroke-width="1.2"/>')
 p.append(f'<circle r="3.5" fill="{INK}"/></g>')
p.append('</g>')

line('M84 450 V678',BLUE,4)
for cy,heading,sub in [(467,'Code expressions','Post-level content categories'),(558,'Trace temporal change','Weekly counts + composition'),(649,'Compare platforms','Expression trajectories')]:
 circle(84,cy-11,9,BLUE,2,PAPER)
 text(118,cy,heading,35,weight=700)
 text(118,cy+37,sub,29,fill=GRAY)
text(48,741,'Empirical patterns & model grounding',30,'Georgia',italic=True)

# 标定桥只指向模型规格；外部帖子在下一行独立标注。
line('M750 650 H850 V275 H1000',BLUE,2.8,arrow='blue')
text(1020,284,'Case-grounded author mix + B / D / R',30,fill=BLUE)
text(2352,284,'100 fixed-type agents · W12–W22',30,anchor='end')

# 开放式三站机制；衬线大标号与连续细线，避免卡片排布。
for cx,n,labels in [(1070,'1',['Visibility','configuration']),(1630,'2',['Selective','expression']),(2190,'3',['Content','recirculation'])]:
 circle(cx,442,60,RED,2,RED)
 text(cx,463,n,68,'Georgia',700,PAPER,'middle')
 text(cx,553,labels[0],40,'Georgia',700,anchor='middle')
 text(cx,597,labels[1],40,'Georgia',700,anchor='middle')
line('M1136 442 H1564',INK,3,arrow='ink')
line('M1696 442 H2124',INK,3,arrow='ink')
text(1346,428,'Feed ≤10 posts',29,anchor='middle')
text(1910,428,'Threshold → LLM',29,anchor='middle')

text(1070,641,'Random · Chronological',28,anchor='middle')
text(1070,678,'Interest-based',28,anchor='middle')
p.append(f'<text x="1630" y="644" text-anchor="middle" style="font-family:Times New Roman;font-style:italic;font-size:36px;fill:{INK}">U<tspan baseline-shift="sub" font-size="23">it</tspan> = B<tspan baseline-shift="sub" font-size="23">i</tspan> + R<tspan baseline-shift="sub" font-size="23">it</tspan>(D<tspan baseline-shift="sub" font-size="23">it</tspan> − B<tspan baseline-shift="sub" font-size="23">i</tspan>)</text>')
text(1630,680,'Fixed threshold; otherwise no post',27,anchor='middle',fill=GRAY)
text(2190,641,'Published posts only',29,weight=700,anchor='middle')
text(2190,678,'Regime-specific eligibility',27,anchor='middle',fill=GRAY)

# 两条不同含义的反馈线；灰虚线来自接触，与成功发布无关。
line('M1070 382 V319 H1630 V382',GRAY,2.7,dash='8 7',arrow='gray')
text(1365,309,'Feed → history → later R',27,fill=GRAY,anchor='middle')
line('M2255 442 H2335 Q2346 442 2346 462 V716 Q2346 730 2328 730 H906 Q890 730 890 712 V460 Q890 442 906 442 H1005',RED,4,arrow='red')
text(1630,761,'Content returns to later feeds',29,'Georgia',fill=GRAY,anchor='middle',italic=True)

# 共同解释占独立底栏，两部分互补，不把经验语料等同于模拟输入。
line('M48 781 H2352',INK,3)
text(48,828,'Observed patterns + generative explanation',34,'Georgia')
line('M879 814 H1000',INK,2.5,arrow='ink')
text(1041,828,'Public representation reorganization',41,'Georgia',700)
(OUT/'editorial.svg').write_text('\n'.join(p+['</svg>']))
