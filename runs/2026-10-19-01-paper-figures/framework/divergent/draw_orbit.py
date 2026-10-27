"""Native SVG candidate: restrained white orbital map of two complementary studies.
Only schematic geometry: circular arcs do not encode measured proportions.
"""
from pathlib import Path
from html import escape
from math import sin, cos, radians
P=Path(__file__).parent
BG='#FFFFFF'; WHITE='#17212B'; GRAY='#48515D'; LINE='#BAC2CA'
CYAN='#0072B2'; AMBER='#D55E00'; PURPLE='#616A73'
a=[]
a.append('''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="63.75mm" viewBox="0 0 2400 850" role="img" aria-labelledby="title desc"><title id="title">An orbital map of complementary empirical and simulation studies</title><desc id="desc">White-background orbital schematic with restrained semantic accents. Left 35 percent: platform corpus, coding, temporal and platform analyses. Right 65 percent: visibility configuration, selective expression and content recirculation form the proposed mechanism. Curved arcs show process, not data proportions. Mourning icons indicate context only. Types are fixed. Exposure history is updated by contact regardless of posting.</desc><defs>''')
for n,c in [('white',WHITE),('cyan',CYAN),('amber',AMBER),('purple',PURPLE),('gray',GRAY)]:
 a.append(f'<marker id="{n}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 Z" fill="{c}"/></marker>')
a.append('''</defs><style>text{font-family:Arial,Helvetica,sans-serif;fill:#17212B;font-size:32px}.title{font-size:40px;font-weight:700;letter-spacing:.2px}.head{font-size:38px;font-weight:700}.body{font-size:32px}.small{font-size:29px}.num{font-size:80px;font-weight:700}.formula{font-family:Times New Roman,Times,serif;font-size:40px;font-style:italic}</style>''')
a.append(f'<rect width="2400" height="850" fill="{BG}"/>')
def text(x,y,t,cl='body',color=WHITE,anchor='start',extra=''):
 color = GRAY if color == GRAY else WHITE
 a.append(f'<text x="{x}" y="{y}" class="{cl}" fill="{color}" text-anchor="{anchor}" style="fill:{color}" {extra}>{escape(t)}</text>')
def path(d,c=LINE,sw=2,dash=None,marker=None):
 a.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' marker-end="url(#{marker})"' if marker else '')+'/>')
def circle(x,y,r,c,fill=BG,sw=2):
 a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
def dot(x,y,n,c):
 circle(x,y,26,c,sw=2.4);text(x,y+10,str(n),'body',c,'middle')
def arc(cx,cy,r,st,en,color,sw=14):
 x1,y1=cx+r*cos(radians(st)),cy+r*sin(radians(st));x2,y2=cx+r*cos(radians(en)),cy+r*sin(radians(en))
 path(f'M{x1:.2f} {y1:.2f} A{r} {r} 0 {1 if en-st>180 else 0} 1 {x2:.2f} {y2:.2f}',color,sw,marker={CYAN:'cyan',AMBER:'amber',PURPLE:'purple'}[color])
# Titles and empirical open system map.
text(54,63,'01','head',CYAN)
text(124,63,'Platform analysis','title')
text(884,63,'02','head',AMBER)
text(954,63,'Simulation modeling','title')
text(954,108,'100 fixed-type agents · W12–W22','small',GRAY)
path('M830 40 V741',LINE,2,'7 11')
text(56,177,'49,930','num')
text(56,218,'public posts','head',CYAN)
text(56,263,'Douyin + Xiaohongshu','body',GRAY)
# Native paper / mourning context illustration.
a.append('<g transform="translate(679 158)" aria-label="Digital mourning context"><path d="M-34 -49 H16 L39 -26 V50 H-34 Z M16 -49 V-26 H39" fill="none" stroke="#56616B" stroke-width="2.7"/><path d="M-22 21 H24 M-22 34 H8" stroke="#BAC2CA" stroke-width="3"/>')
a.append(f'<rect x="-6" y="-8" width="16" height="26" rx="2" fill="#FFFFFF" stroke="{WHITE}" stroke-width="1.8"/><path d="M2 -12 C-7 -23 1 -29 3 -34 C12 -23 13 -17 2 -12 Z" fill="{AMBER}"/>')
a.append('<g transform="translate(-45 31)"><path d="M0 0 L8 30" stroke="#56616B" stroke-width="2"/>')
for theta in (0,60,120,180,240,300):
 a.append(f'<ellipse cx="0" cy="-7" rx="4" ry="8" transform="rotate({theta})" fill="#FFFFFF" stroke="{GRAY}" stroke-width="1"/>')
a.append(f'<circle r="3" fill="{AMBER}"/></g></g>')
# Coding and two complementary empirical outputs, not separate corpus shares.
path('M78 287 V601',CYAN,2)
for y,n in [(332,'1'),(460,'2'),(578,'3')]:dot(78,y,n,CYAN)
text(124,327,'Content coding','head')
text(124,368,'Education · mourning · meme','body',GRAY)
text(124,405,'Other · marketing · noise','body',GRAY)
text(124,456,'Temporal patterns','head')
text(124,497,'Mourning peak → later meme growth','small',GRAY)
text(124,573,'Platform differences','head')
text(124,614,'Compare expression trajectories','body',GRAY)
# Empirical grounding is a conceptual linkage, not a raw corpus-to-input claim.
path('M126 661 H775 Q875 661 875 177 H1006',CYAN,3.5,marker='cyan')
text(124,704,'Patterns → mechanism questions','small',CYAN)
# Simulation ring: process arcs, without axes, radial data ticks or sectors.
cx,cy,r=1632,377,235
circle(cx,cy,r-22,LINE,sw=1.7)
for ang in (-150,-30,90):
 x,y=cx+(r-22)*cos(radians(ang)),cy+(r-22)*sin(radians(ang));circle(x,y,5,LINE,WHITE,1.5)
arc(cx,cy,r,-150,-37,CYAN,10)
arc(cx,cy,r,-23,76,AMBER,10)
arc(cx,cy,r,100,203,PURPLE,10)
# Closing bridge into the cyan start shows continued recirculation.
path('M1411 457 Q1360 383 1420 267',PURPLE,4,marker='purple')
# Stage labels positioned beyond ring; textual identifiers redundant to color.
dot(939,185,'1',CYAN)
text(983,181,'Visibility','head',CYAN)
text(983,224,'configuration','head',CYAN)
text(939,277,'Regime-specific pool','body')
text(939,315,'Random / chronological /','small',GRAY)
text(939,350,'interest-based curation','small',GRAY)
text(939,395,'Personal feed: ≤10 posts','body')
path('M1317 252 L1433 253',CYAN,2.5)
# Frozen inputs have their own explicitly distinct simulation source.
text(1172,137,'Separately frozen inputs','small',GRAY)
path('M1369 144 V172 H1515',GRAY,2.2,marker='gray')
# Center: exact mathematical expression, fully editable tspan text.
text(cx,313,'Expression utility','body',WHITE,'middle')
a.append(f'<text x="{cx}" y="374" class="formula" text-anchor="middle">U<tspan baseline-shift="sub" font-size="25">it</tspan><tspan> = B</tspan><tspan baseline-shift="sub" font-size="25">i</tspan><tspan> + R</tspan><tspan baseline-shift="sub" font-size="25">it</tspan><tspan>(D</tspan><tspan baseline-shift="sub" font-size="25">it</tspan><tspan> − B</tspan><tspan baseline-shift="sub" font-size="25">i</tspan><tspan>)</tspan></text>')
text(cx,418,'B  Baseline utility','small',GRAY,'middle')
text(cx,456,'D  Opinion-climate response','small',GRAY,'middle')
text(cx,494,'R  Prior-exposure weight','small',GRAY,'middle')
# Selection before generation; do not imply all agents publish.
dot(1970,212,'2',AMBER)
text(2014,208,'Selective','head',AMBER)
text(2014,251,'expression','head',AMBER)
text(1970,310,'U ≥ fixed threshold','body')
path('M1971 334 H1999',AMBER,3,marker='amber')
text(2018,345,'LLM → post','body')
text(1970,394,'U < fixed threshold:','small',GRAY)
text(1970,431,'no post','small',GRAY)
text(1970,481,'Only published posts','small',AMBER)
path('M1922 270 H1955',AMBER,2.5)
path('M2291 490 V573 Q2291 596 2249 596 H2052',AMBER,3.5,marker='amber')
# Independent historical update from the feed, not conditional on posting.
path('M1073 408 V482 Q1073 530 1156 530 H1450',GRAY,2.5,'7 8',marker='gray')
text(939,577,'Feed contact → history → future R','small',GRAY)
# Bottom stage holds regime-specific return timings, after successful publication.
dot(1425,656,'3',PURPLE)
text(1469,652,'Content recirculation','head',PURPLE)
text(1469,698,'Chronological: later batches','small')
text(1469,737,'Random / interest: next week','small')
path('M1643 615 V629',PURPLE,2.5)
path('M2051 596 H1995 V653 H1937',PURPLE,2.5,marker='purple')
# Two studies converge; no causal claim or calibration overstated.
path('M124 725 V763 H1210',CYAN,3,marker='cyan')
path('M2138 730 V763 H1740',PURPLE,3,marker='purple')
path('M54 782 H2346',WHITE,2.2)
text(55,828,'Public representation reorganization','head',WHITE)
text(1184,827,'Observed patterns + mechanism explanation','body',WHITE)
a.append('</svg>')
(P/'orbit.svg').write_text('\n'.join(a),encoding='utf-8')
print(P/'orbit.svg')
