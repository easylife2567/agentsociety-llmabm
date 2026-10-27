"""本轮三种互补研究框架的原生SVG工具；仅使用标准库。"""
from html import escape
from pathlib import Path

W,H=2400,850
INK='#111827'; MUTED='#48515D'; BORDER='#A9AFB8'; WHITE='#FFFFFF'; GRAY='#F3F4F6'
GREEN='#A9D47D'; GD='#4D7A27'; BLUE='#88BFF2'; BD='#2167A5'
RED='#F47D7D'; RD='#A72E3B'; PURPLE='#BE9AE3'; PD='#704097'

class D:
 def __init__(self,title,ratio):
  self.parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="63.75mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">Two complementary studies of postmortem public representation. Empirical and simulation panel areas: {escape(ratio)}. Visibility configuration, selective expression and content recirculation form the proposed mechanism. All authors retain fixed types. Candle and flower icons indicate the mourning context, not a variable or a result.</desc><defs>''']
  for name,c in [('ink',INK),('blue',BD),('red',RD),('purple',PD),('green',GD),('gray',MUTED)]:
   self.parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>')
  self.parts.append(f'''</defs><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK};font-size:32px}}.title{{font-size:42px;font-weight:700}}.h{{font-size:36px;font-weight:700}}.b{{font-size:32px}}.s{{font-size:30px}}.xs{{font-size:27px}}.big{{font-size:50px;font-weight:700}}.math{{font-family:Times New Roman,Times,serif;font-style:italic}}</style><rect width="2400" height="850" fill="white"/>''')
 def box(self,x,y,w,h,fill=WHITE,stroke=BORDER,r=8,sw=2,dash=None,id=None):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' id="{id}"' if id else '')+'/>')
 def text(self,x,y,t,cl='b',anchor='start',fill=None,size=None,weight=None):
  style=';'.join([v for v in [f'fill:{fill}' if fill else '',f'font-size:{size}px' if size else '',f'font-weight:{weight}' if weight else ''] if v])
  self.parts.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}"'+(f' style="{style}"' if style else '')+'>'+escape(t)+'</text>')
 def lines(self,x,y,items,cl='b',step=37,**kw):
  for i,t in enumerate(items):self.text(x,y+i*step,t,cl,**kw)
 def line(self,path,color=BORDER,sw=2,dash=None):
  self.parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def arrow(self,path,color='ink',sw=4,dash=None):
  c={'ink':INK,'blue':BD,'red':RD,'purple':PD,'green':GD,'gray':MUTED}[color]
  self.parts.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#{color})"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def circle(self,x,y,r,fill=WHITE,stroke=INK,sw=2):
  self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def diamond(self,cx,cy,rx,ry,fill=GRAY,stroke=INK):
  self.parts.append(f'<polygon points="{cx},{cy-ry} {cx+rx},{cy} {cx},{cy+ry} {cx-rx},{cy}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
 def formula(self,x,y,size=36,anchor='middle'):
  self.parts.append(f'<text x="{x}" y="{y}" class="math" text-anchor="{anchor}" style="font-size:{size}px">U<tspan baseline-shift="sub" font-size="{size*.68}">it</tspan><tspan> = B</tspan><tspan baseline-shift="sub" font-size="{size*.68}">i</tspan><tspan> + R</tspan><tspan baseline-shift="sub" font-size="{size*.68}">it</tspan><tspan>(D</tspan><tspan baseline-shift="sub" font-size="{size*.68}">it</tspan><tspan> − B</tspan><tspan baseline-shift="sub" font-size="{size*.68}">i</tspan><tspan>)</tspan></text>')
 def memorial(self,x,y,scale=1):
  self.parts.append(f'<g aria-label="Mourning context" transform="translate({x} {y}) scale({scale})"><ellipse cx="0" cy="52" rx="28" ry="5" fill="#D5D8DC"/><rect x="-13" y="-3" width="26" height="52" rx="4" fill="white" stroke="{INK}" stroke-width="2"/><path d="M-5 0 V42" stroke="#D5D8DC" stroke-width="5"/><path d="M0 -3 V-10" stroke="{INK}" stroke-width="2"/><path d="M0 -12 C-18 -23 -4 -36 0 -41 C13 -27 15 -19 0 -12 Z" fill="{RED}" stroke="{INK}" stroke-width="1.5"/><path d="M0 -15 C-7 -22 -1 -27 1 -30 C7 -23 7 -19 0 -15 Z" fill="white"/>')
  for fx,fy in [(-36,17),(37,19)]:
   self.parts.append(f'<g transform="translate({fx} {fy})"><path d="M0 4 L4 36 M2 25 L-9 17 M2 21 L13 13" fill="none" stroke="{MUTED}" stroke-width="2"/>')
   for a in range(0,360,60):self.parts.append(f'<ellipse cx="0" cy="-8" rx="5" ry="10" transform="rotate({a})" fill="white" stroke="{MUTED}" stroke-width="1.2"/>')
   self.parts.append(f'<circle r="4" fill="{INK}"/></g>')
  self.parts.append('</g>')
 def docs(self,x,y,scale=1):
  self.parts.append(f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 0 H45 L62 17 V78 H0 Z" fill="{WHITE}" stroke="{INK}" stroke-width="2"/><path d="M45 0 V17 H62 M11 34 H48 M11 48 H48 M11 62 H39" fill="none" stroke="{MUTED}" stroke-width="2"/></g>')
 def person(self,x,y,scale=1):
  self.parts.append(f'<g transform="translate({x} {y}) scale({scale})"><circle r="13" fill="white" stroke="{INK}" stroke-width="2"/><path d="M-23 45 V30 Q-23 14 0 14 Q23 14 23 30 V45 Z" fill="{GRAY}" stroke="{INK}" stroke-width="2"/></g>')
 def label(self,x,y,w,t,fill,stroke):
  self.box(x,y,w,52,fill,stroke,r=0,sw=1.8);self.text(x+16,y+36,t,'h')
 def splitbar(self,x,y,w,h,share,fill=PURPLE):
  # share 必须是论文中可核对的观测比例；不绘制伪造的时序曲线。
  self.box(x,y,w,h,GRAY,BORDER,r=0,sw=1)
  self.box(x,y,w*share,h,fill,fill,r=0,sw=0)
 def save(self,path):Path(path).write_text('\n'.join(self.parts+['</svg>']))
