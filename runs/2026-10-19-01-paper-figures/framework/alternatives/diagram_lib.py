"""四种英文构图共用的最小SVG绘图工具；颜色、线型与科学内容保持一致。"""
from html import escape
from pathlib import Path
W,H=2400,850
INK='#17212B'; MUTED='#46515C'; BORDER='#ACB6BE'
BLUE='#0072B2'; BT='#E8F2F8'; ORANGE='#D55E00'; OT='#FFF0E4'; GRAY='#F1F3F5'; WHITE='#FFFFFF'
class Diagram:
 def __init__(self,title,subtitle=''):
  self.title=title
  self.parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="63.75mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">Research framework consistent with ICA2027v1: fixed author types, threshold-based expression, and regime-specific post recirculation. Candle and white-flower illustrations indicate thematic context only.</desc><defs>''']
  for name,c in [('ink',INK),('blue',BLUE),('orange',ORANGE),('gray',MUTED)]:
   self.parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>')
  self.parts.append(f'''</defs><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK};font-size:34px}}.title{{font-size:42px;font-weight:700}}.h{{font-size:36px;font-weight:700}}.b{{font-size:34px}}.s{{font-size:33px}}.xs{{font-size:28px}}.muted{{fill:{MUTED}}}.math{{font-family:"Times New Roman",Times,serif;font-style:italic;font-size:36px}}</style><rect width="{W}" height="{H}" fill="white"/>''')
  self.text(48,55,title,'title')
  if subtitle:self.text(48,88,subtitle,'s',fill=MUTED)
 def box(self,x,y,w,h,fill=WHITE,stroke=BORDER,r=12,dash=None,sw=2,id=None):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' id="{id}"' if id else '')+'/>')
 def text(self,x,y,t,cl='b',anchor='start',fill=None):
  if fill == ORANGE: fill = '#9C4300'  # 同一橙色语义，文字使用更深色保证对比。
  self.parts.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+escape(t)+'</text>')
 def lines(self,x,y,ts,cl='b',step=39,anchor='start',fill=None):
  for i,t in enumerate(ts):self.text(x,y+i*step,t,cl,anchor,fill)
 def arrow(self,d,color='ink',dash=None,sw=3.5):
  c={'ink':INK,'blue':BLUE,'orange':ORANGE,'gray':MUTED}.get(color,color)
  self.parts.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{color})"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def line(self,d,color=BORDER,sw=2,dash=None):
  self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def diamond(self,cx,cy,rx,ry,fill=OT,stroke=ORANGE):
  self.parts.append(f'<polygon points="{cx},{cy-ry} {cx+rx},{cy} {cx},{cy+ry} {cx-rx},{cy}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
 def formula(self,x,y,size=31,anchor='middle'):
  self.parts.append(f'<text x="{x}" y="{y}" class="math" text-anchor="{anchor}" style="font-size:{size}px">U<tspan baseline-shift="sub" font-size="22">it</tspan><tspan> = B</tspan><tspan baseline-shift="sub" font-size="22">i</tspan><tspan> + R</tspan><tspan baseline-shift="sub" font-size="22">it</tspan><tspan>(D</tspan><tspan baseline-shift="sub" font-size="22">it</tspan><tspan> − B</tspan><tspan baseline-shift="sub" font-size="22">i</tspan><tspan>)</tspan></text>')
 def docs(self,x,y,scale=1,mourning=False):
  self.parts.append(f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 0 H45 L62 17 V78 H0 Z" fill="{WHITE}" stroke="{INK}" stroke-width="2"/><path d="M45 0 V17 H62 M11 34 H48 M11 48 H48 M11 62 H39" fill="none" stroke="{MUTED}" stroke-width="2"/></g>')
  if mourning:self.memorial(x+scale*31,y+scale*43,scale*.29,flowers=False)
 def person(self,x,y,scale=1):
  self.parts.append(f'<g transform="translate({x} {y}) scale({scale})"><circle cy="0" r="13" fill="{WHITE}" stroke="{INK}" stroke-width="2"/><path d="M-23 45 V30 Q-23 14 0 14 Q23 14 23 30 V45 Z" fill="{GRAY}" stroke="{INK}" stroke-width="2"/></g>')
 def memorial(self,x,y,scale=1,flowers=True):
  self.parts.append(f'<g aria-label="Digital mourning illustration" transform="translate({x} {y}) scale({scale})"><ellipse cx="0" cy="52" rx="26" ry="5" fill="#D7DDE1"/><rect x="-13" y="-3" width="26" height="52" rx="4" fill="white" stroke="{INK}" stroke-width="2"/><path d="M-5 0 V42" stroke="#CBD3D8" stroke-width="5"/><path d="M0 -3 V-10" stroke="{INK}" stroke-width="2"/><path d="M0 -12 C-18 -23 -4 -36 0 -41 C13 -27 15 -19 0 -12 Z" fill="{ORANGE}"/><path d="M0 -15 C-7 -22 -1 -27 1 -30 C7 -23 7 -19 0 -15 Z" fill="white"/>')
  if flowers:
   for fx,fy in [(-36,17),(37,19)]:
    self.parts.append(f'<g transform="translate({fx} {fy})"><path d="M0 4 L4 36 M2 25 L-9 17 M2 21 L13 13" fill="none" stroke="{MUTED}" stroke-width="2"/>')
    for a in range(0,360,60):self.parts.append(f'<ellipse cx="0" cy="-8" rx="5" ry="10" transform="rotate({a})" fill="white" stroke="{MUTED}" stroke-width="1.2"/>')
    self.parts.append(f'<circle r="4" fill="{INK}"/></g>')
  self.parts.append('</g>')
 def footer(self,y=664):
  self.box(48,y,2304,88,GRAY,BORDER,10)
  self.text(69,y+34,'COMPARE','xs',fill=MUTED)
  self.text(257,y+34,'Random · Chronological · Interest-based   ×   3 seeds = 9 main runs','s')
  self.text(69,y+72,'INTERVENE','xs',fill=MUTED)
  self.text(257,y+72,'Interest-based: B=0 / D=1 / R=1   ×   3 paired repeats','s')
  self.text(48,y+128,'Full-model reference reused; generation configurations differ between batches.','xs',fill=MUTED)
 def save(self,path):
  Path(path).write_text('\n'.join(self.parts+['</svg>']))
