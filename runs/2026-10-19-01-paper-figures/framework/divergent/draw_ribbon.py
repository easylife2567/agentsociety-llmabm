from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent
W, H = 2400, 850
INK = '#17232D'
MUTED = '#45545E'
GREEN = '#009E73'
BLUE = '#0072B2'
CORAL = '#D55E00'
PURPLE = '#CC79A7'
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="63.75mm" viewBox="0 0 {W} {H}">
<title>Complementary empirical and simulation research as a flowing stream map</title>
<desc>Native editable vector diagram. The empirical stream occupies approximately 37 percent and simulation 63 percent of the research field. Ribbon widths and glyph counts are symbolic, not quantities. Green denotes empirical inquiry; blue denotes visibility configuration; vermillion selective expression; reddish purple content recirculation. Candle and white flower mark the mourning research context and do not classify all posts as mourning. Labels, arrows and spatial order carry the same semantics without relying on color. Temporal patterns and platform comparisons motivate mechanism questions; simulation supplies a complementary explanation, not an estimate of platform-specific algorithms. Frozen simulation inputs are represented separately from the empirical corpus. A prior-exposure branch is independent of publication. Exact formula and eligibility timings match the supplied manuscript.</desc>
<defs>''']
for name, col in [('green',GREEN),('blue',BLUE),('coral',CORAL),('purple',PURPLE),('ink',INK),('muted',MUTED)]:
    parts.append(f'<marker id="{name}" markerUnits="userSpaceOnUse" markerWidth="38" markerHeight="42" refX="33" refY="21" orient="auto"><path d="M1,2 L36,21 L1,40 L10,21 Z" fill="{col}"/></marker>')
parts.append('''</defs><style>
text { font-family: Arial, Helvetica, sans-serif; fill: #17232D; }
.title { font-size: 43px; font-weight: 700; }
.study { font-size: 36px; font-weight: 700; }
.head { font-size: 34px; font-weight: 700; letter-spacing: .2px; }
.body { font-size: 32px; }
.small { font-size: 29px; }
.num { font-size: 30px; font-weight: 700; }
.math { font-family: Georgia, 'Times New Roman', serif; font-size: 35px; font-style: italic; }
</style><rect width="2400" height="850" fill="white"/>''')

def text(x,y,s,cls='body',anchor='start',color=INK):
    parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" style="fill:{color}">{escape(s)}</text>')
def lines(x,y,ss,cls='body',step=39,anchor='start',color=INK):
    for k,s in enumerate(ss): text(x,y+k*step,s,cls,anchor,color)
def path(d,col,sw=3,dash=None,arrow=False):
    end = f' marker-end="url(#{arrow})"' if arrow else ''
    dash = f' stroke-dasharray="{dash}"' if dash else ''
    parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{dash}{end}/>')
def circle(cx,cy,r,fill='white',stroke=None,sw=3):
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def paper(x,y,s=1,flower=False):
    parts.append(f'<g transform="translate({x} {y}) scale({s})" fill="white" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round">')
    parts.append('<path d="M-36,-44 H18 L36,-26 V44 H-36 Z"/><path d="M18,-44 V-26 H36" fill="none"/>')
    if flower:
        parts.append(f'<g transform="translate(0 -2)" stroke="{INK}" stroke-width="2.8">')
        for angle in (0,60,120,180,240,300):
            parts.append(f'<ellipse cx="0" cy="-12" rx="7" ry="12" transform="rotate({angle})" fill="white"/>')
        parts.append(f'<circle r="5" fill="#D7B969"/><path d="M0,5 V30 M0,21 Q-15,8 -15,22 Q-4,30 0,27" fill="none"/></g>')
    else:
        parts.append('<path d="M-21,-13 H18 M-21,0 H21 M-21,13 H21 M-21,26 H8" fill="none"/>')
    parts.append('</g>')
def stack(x,y,s=1):
    paper(x-14*s,y-12*s,s)
    paper(x+14*s,y+12*s,s)
def candle(x,y,s=1):
    parts.append(f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="3.3" stroke-linejoin="round"><path d="M-12,-10 H12 V33 H-12 Z" fill="white"/><path d="M0,-13 C-15,-26 -3,-34 0,-43 C13,-29 14,-24 0,-13" fill="#F2AC42"/><path d="M-23,36 H23" fill="none"/></g>')
def person(x,y,s=1):
    parts.append(f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="4" fill="white"><circle cy="-24" r="21"/><path d="M-37,40 V18 C-37,-7 37,-7 37,18 V40 Z"/><path d="M-20,18 V40 M20,18 V40" fill="none"/></g>')
def analysis_icon(x,y):
    parts.append(f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="4" fill="white"><path d="M-54,-35 V46 H55" fill="none"/><path d="M-43,15 L-18,-7 L8,6 L42,-23" fill="none"/><circle cx="-18" cy="-7" r="5" fill="{GREEN}"/><circle cx="42" cy="-23" r="5" fill="{GREEN}"/><path d="M-40,34 H-12 M1,34 H31" stroke="{GREEN}" stroke-width="9"/></g>')
def coding_icon(x,y):
    parts.append(f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="3.5" fill="white"><path d="M-48,-40 H-14 V-6 H-48 Z M12,-40 H46 V-6 H12 Z M-48,15 H-14 V49 H-48 Z M12,15 H46 V49 H12 Z"/><path d="M-40,-24 L-33,-15 L-22,-31 M19,31 L26,40 L38,23" fill="none" stroke="{GREEN}" stroke-width="5"/></g>')

# The empirical study is one continuous organic stream, not a framed side panel.
text(48,58,'Public representation through two complementary lenses','title')
text(54,132,'01  Platform data analysis','study',color=INK)
text(961,132,'02  Simulation modeling','study',color=INK)
path('M150,305 C150,340 226,314 279,344',GREEN,14,arrow='green')
path('M339,475 C339,515 150,471 150,487',GREEN,14,arrow='green')
circle(150,231,74)
paper(135,230,.95,True)
candle(184,253,.64)
lines(253,202,['Platform corpus','49,930 posts','Douyin · Xiaohongshu'],cls='body')
circle(339,400,74)
coding_icon(339,400)
lines(446,384,['Content coding','Expression types'],cls='body')
circle(150,569,74)
analysis_icon(150,569)
lines(253,529,['Temporal + platform patterns','Mourning peak → later meme growth','Shared sequence; divergent trajectories'],cls='body',step=40)

# An unweighted bridge expresses complementarity rather than pooled data ingestion.
path('M880,576 C903,576 895,329 986,330',GREEN,9,arrow='green')
lines(790,453,['Mechanism','questions'],cls='small',step=34,anchor='middle',color=INK)

# A separate frozen-input entry guards the manuscript's data-source boundary.
lines(1080,242,['Frozen inputs'],cls='small',anchor='middle',color=MUTED)
path('M1080,253 V288',MUTED,3,arrow='muted')
# Ribbons are equal-width, symbolic continuous streams with generous curved geometry.
for x,c in [(972,BLUE),(1470,CORAL),(2000,PURPLE)]: circle(x,169,5,c)
path('M1168,354 C1298,294 1354,433 1496,377',BLUE,18,arrow='blue')
path('M1673,362 C1803,294 1873,307 2020,362',CORAL,18,arrow='coral')
path('M2205,390 C2358,390 2370,570 2264,640 C2100,740 1380,735 1060,679 C900,651 898,510 993,428',PURPLE,18,arrow='purple')
# White islands reveal icon silhouettes without turning into colored boxes.
for x in (1080,1590,2110): circle(x,370,89)
stack(1080,367,.93)
person(1590,356,1.05)
stack(2110,370,.98)

lines(1080,181,['VISIBILITY','CONFIGURATION'],cls='head',step=39,anchor='middle',color=INK)
lines(1590,181,['SELECTIVE','EXPRESSION'],cls='head',step=39,anchor='middle',color=INK)
lines(2110,181,['CONTENT','RECIRCULATION'],cls='head',step=39,anchor='middle',color=INK)

lines(1160,494,['Random · Chronological','Interest-based','Feed ≤10 posts'],cls='body',step=38,anchor='middle')
text(1590,458,'100 agents · fixed types','small',anchor='middle')
# Exact OMML formula from the manuscript, using editable tspans.
parts.append('''<text x="1590" y="505" class="math" text-anchor="middle">U<tspan baseline-shift="sub" font-size="23">it</tspan><tspan baseline-shift="baseline"> = B</tspan><tspan baseline-shift="sub" font-size="23">i</tspan><tspan baseline-shift="baseline"> + R</tspan><tspan baseline-shift="sub" font-size="23">it</tspan><tspan baseline-shift="baseline">(D</tspan><tspan baseline-shift="sub" font-size="23">it</tspan><tspan baseline-shift="baseline"> − B</tspan><tspan baseline-shift="sub" font-size="23">i</tspan><tspan baseline-shift="baseline">)</tspan></text>''')
text(1590,550,'U ≥ fixed threshold → LLM','body',anchor='middle')
text(1590,590,'U < fixed threshold: no post','small',anchor='middle')
text(2080,494,'Published posts return','body',anchor='middle')
lines(2080,536,['Chronological: later batches','Random / interest: next week'],cls='small',step=37,anchor='middle')
# Independent history branch is positioned inside the outer recirculation loop.
path('M1150,302 C1245,279 1426,277 1510,317',MUTED,4,dash='10 10',arrow='muted')
text(1340,267,'Exposure history → later R','small',anchor='middle',color=MUTED)
text(1910,672,'Re-exposure','small',anchor='middle',color=INK)

# Two explanatory contributions converge, without implying empirical validation of algorithms.
path('M410,659 C410,713 568,742 748,759',GREEN,4,arrow='green')
path('M1715,715 V759',PURPLE,4,arrow='purple')
text(940,805,'Observed patterns  +  mechanism explanation  →  Representation reorganization','study',anchor='middle')
text(2307,804,'W12–W22','small',anchor='end',color=MUTED)

parts.append('</svg>')
(OUT / 'ribbon.svg').write_text('\n'.join(parts),encoding='utf-8')
print(OUT / 'ribbon.svg')
