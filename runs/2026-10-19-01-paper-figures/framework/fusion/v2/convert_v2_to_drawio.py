"""把已核查融合SVG重建为draw.io原生文本、基础图形、连线及矢量形状。

不导入整图图片；环形弧线使用draw.io内嵌stencil，文字使用原生标签。
只针对本图中实际存在的SVG命令，遇到不支持元素立即报错。
"""
from pathlib import Path
import xml.etree.ElementTree as E
import math,re,zlib,base64,urllib.parse,html,json,hashlib

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'framework_fusion_en_v2.svg'
TARGET=HERE/'framework_fusion_en_v2.drawio'
SVG='{http://www.w3.org/2000/svg}'
model=E.Element('mxGraphModel',dict(dx='2800',dy='1100',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth='2800',pageHeight='1100',math='0',shadow='0',background='#FFFFFF'))
root=E.SubElement(model,'root')
E.SubElement(root,'mxCell',id='0')
E.SubElement(root,'mxCell',id='1',parent='0')
serial=0;counts={};text_check=[];anchors=[]
def fmt(v):return f'{v:.5f}'.rstrip('0').rstrip('.') if v else '0'
def cell(style,**attrs):
 global serial
 serial+=1
 return E.SubElement(root,'mxCell',dict(id=f'obj-{serial}',parent='1',style=style,**attrs))
def geom(c,x,y,w,h,relative=False):
 return E.SubElement(c,'mxGeometry',dict(x=fmt(x),y=fmt(y),width=fmt(w),height=fmt(h),**({'relative':'1'} if relative else {}),**{'as':'geometry'}))
def count(k):counts[k]=counts.get(k,0)+1
def props(s):
 return {k.strip():v.strip() for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',s)}
doc=E.parse(SOURCE).getroot()
css={}
for selector,body in re.findall(r'([^{}]+)\{([^{}]+)\}',doc.find(SVG+'style').text):css[selector.strip()]=props(body)
def matmul(a,b):
 return (a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5])
IDENT=(1,0,0,1,0,0)
def tf(s):
 m=IDENT
 for name,args in re.findall(r'(translate|scale|rotate)\(([^)]+)\)',s):
  v=[float(n) for n in re.findall(r'-?\d*\.?\d+(?:[eE][+-]?\d+)?',args)]
  if name=='translate':n=(1,0,0,1,v[0],v[1] if len(v)>1 else 0)
  elif name=='scale':n=(v[0],0,0,v[1] if len(v)>1 else v[0],0,0)
  else:
   t=math.radians(v[0]);n=(math.cos(t),math.sin(t),-math.sin(t),math.cos(t),0,0)
  m=matmul(m,n)
 return m
def xy(m,x,y):return (m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5])
def parsepath(data):
 ts=re.findall(r'[MLHVQCAZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',data)
 commands=[];i=0;cx=cy=0;start=None
 arity={'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6,'A':7,'Z':0}
 while i<len(ts):
  op=ts[i];i+=1
  if op not in arity:raise ValueError(f'Unexpected path token {op}: {data}')
  n=arity[op];v=list(map(float,ts[i:i+n]));i+=n
  if op=='H':op,v='L',[v[0],cy]
  if op=='V':op,v='L',[cx,v[0]]
  if op=='M':start=tuple(v)
  if op=='Z':cx,cy=start
  else:cx,cy=v[-2:]
  commands.append((op,v))
 return commands
def sample(cmds):
 pts=[];cur=(0,0);start=None
 for op,v in cmds:
  if op in ('M','L'):
   cur=tuple(v);pts.append(cur)
   if op=='M':start=cur
  elif op=='Z':cur=start;pts.append(cur)
  elif op in ('Q','C'):
   p0=cur
   for j in range(1,41):
    t=j/40;u=1-t
    if op=='Q':p=(u*u*p0[0]+2*u*t*v[0]+t*t*v[2],u*u*p0[1]+2*u*t*v[1]+t*t*v[3])
    else:p=(u**3*p0[0]+3*u*u*t*v[0]+3*u*t*t*v[2]+t**3*v[4],u**3*p0[1]+3*u*u*t*v[1]+3*u*t*t*v[3]+t**3*v[5])
    pts.append(p)
   cur=tuple(v[-2:])
  elif op=='A':
   # 当前图的弧线为无旋转圆弧；取SVG端点形式的真实中心。
   rx,ry,rot,large,sweep,x2,y2=v
   assert abs(rx-ry)<1e-6 and rot==0 and large==0
   x1,y1=cur;mx=(x1+x2)/2;my=(y1+y2)/2;dx=x2-x1;dy=y2-y1;length=math.hypot(dx,dy)
   height=math.sqrt(max(0,rx*rx-length*length/4));sgn=1 if sweep else -1
   center=(mx-sgn*height*dy/length,my+sgn*height*dx/length)
   t1=math.atan2(y1-center[1],x1-center[0]);t2=math.atan2(y2-center[1],x2-center[0])
   if sweep and t2<t1:t2+=2*math.pi
   if not sweep and t2>t1:t2-=2*math.pi
   for j in range(1,81):
    t=t1+(t2-t1)*j/80;pts.append((center[0]+rx*math.cos(t),center[1]+ry*math.sin(t)))
   cur=(x2,y2)
 return pts
def compressed_stencil(shape):
 xml=E.tostring(shape,encoding='unicode',short_empty_elements=True)
 quoted=urllib.parse.quote(xml,safe="~()*!.'-").encode()
 c=zlib.compressobj(wbits=-15)
 return base64.b64encode(c.compress(quoted)+c.flush()).decode()
def stencil(cmds,sty,m=IDENT,label='Vector shape'):
 pts=[xy(m,*p) for p in sample(cmds)];xs,ys=zip(*pts)
 x0,y0=min(xs),min(ys);w=max(max(xs)-x0,1);h=max(max(ys)-y0,1)
 sh=E.Element('shape',dict(name=label,w=fmt(w),h=fmt(h),aspect='variable',strokewidth='inherit'))
 E.SubElement(sh,'connections');E.SubElement(sh,'background');fg=E.SubElement(sh,'foreground')
 E.SubElement(fg,'linecap',cap='round');E.SubElement(fg,'linejoin',join='round')
 p=E.SubElement(fg,'path')
 for op,v in cmds:
  if op=='Z':E.SubElement(p,'close');continue
  if op=='A':
   assert m==IDENT
   rx,ry,rot,large,sweep,x,y=v
   E.SubElement(p,'arc',dict(rx=fmt(rx),ry=fmt(ry),**{'x-axis-rotation':fmt(rot),'large-arc-flag':str(int(large)),'sweep-flag':str(int(sweep))},x=fmt(x-x0),y=fmt(y-y0)))
  else:
   vals=[]
   for i in range(0,len(v),2):
    xx,yy=xy(m,v[i],v[i+1]);vals.extend([xx-x0,yy-y0])
   names={'M':('move',['x','y']),'L':('line',['x','y']),'Q':('quad',['x1','y1','x2','y2']),'C':('curve',['x1','y1','x2','y2','x3','y3'])}
   tag,keys=names[op];E.SubElement(p,tag,{k:fmt(val) for k,val in zip(keys,vals)})
 fill=sty.get('fill','none');stroke=sty.get('stroke','none')
 E.SubElement(fg,'fillstroke' if fill!='none' and stroke!='none' else 'fill' if fill!='none' else 'stroke')
 c=cell(f'shape=stencil({compressed_stencil(sh)});'+paint(sty)+'pointerEvents=1;',vertex='1',value='',**{'data-kind':'native-vector','data-name':label})
 geom(c,x0,y0,w,h);count('native_vector_shapes');return c
def paint(sty):
 scale=sty.get('_scale',1)
 s=f"fillColor={sty.get('fill','none')};strokeColor={sty.get('stroke','none')};strokeWidth={float(sty.get('stroke-width','1'))*scale};"
 if sty.get('stroke-dasharray'):
  sw=float(sty.get('stroke-width','1'))
  vals=[float(v) for v in re.findall(r'\d+(?:\.\d+)?',sty['stroke-dasharray'])]
  s+='dashed=1;fixDash=0;dashPattern='+ ' '.join(fmt(v/sw) for v in vals)+';'
 return s
def marker(cmds,sty,m):
 pts=[xy(m,*p) for p in sample(cmds)];p2=pts[-1];p1=next(p for p in reversed(pts[:-1]) if math.dist(p,p2)>1e-5)
 dx=p2[0]-p1[0];dy=p2[1]-p1[1];length=math.hypot(dx,dy);dx/=length;dy/=length
 sw=float(sty.get('stroke-width','1'));size=6.5*sw
 base=(p2[0]-dx*.88*size,p2[1]-dy*.88*size);tip=(p2[0]+dx*.12*size,p2[1]+dy*.12*size)
 left=(base[0]-dy*size/2,base[1]+dx*size/2);right=(base[0]+dy*size/2,base[1]-dx*size/2)
 stencil([('M',list(tip)),('L',list(left)),('L',list(right)),('Z',[])],{'fill':sty.get('stroke'),'stroke':'none'},label='Arrowhead')
def native_edge(cmds,sty):
 ps=[tuple(v) for op,v in cmds]
 c=cell('edgeStyle=none;noEdgeStyle=1;rounded=0;orthogonalLoop=0;jettySize=0;html=1;'+paint(sty)+('endArrow=block;endFill=1;endSize=12;' if sty.get('marker-end') else 'endArrow=none;')+'startArrow=none;',edge='1',value='',**{'data-kind':'native-connector'})
 g=E.SubElement(c,'mxGeometry',{'relative':'1','as':'geometry'})
 for name,p in [('sourcePoint',ps[0]),('targetPoint',ps[-1])]:E.SubElement(g,'mxPoint',{'x':fmt(p[0]),'y':fmt(p[1]),'as':name})
 if len(ps)>2:
  ar=E.SubElement(g,'Array',{'as':'points'})
  for x,y in ps[1:-1]:E.SubElement(ar,'mxPoint',x=fmt(x),y=fmt(y))
 # 流程线端点附着到原生矩形，拖动模块后端点跟随。
 style=c.get('style')
 for which,p in [('source',ps[0]),('target',ps[-1])]:
  match=[]
  for rid,x,y,w,h in anchors:
   if x-1<=p[0]<=x+w+1 and y-1<=p[1]<=y+h+1:
    dist=min(abs(p[0]-x),abs(p[0]-x-w),abs(p[1]-y),abs(p[1]-y-h))
    if dist<=1:match.append((w*h,rid,x,y,w,h))
  if match:
   _,rid,x,y,w,h=min(match);c.set(which,rid);prefix='exit' if which=='source' else 'entry'
   style+=f'{prefix}X={fmt((p[0]-x)/w)};{prefix}Y={fmt((p[1]-y)/h)};{prefix}Perimeter=0;'
 c.set('style',style);count('native_connectors')
def label(v,sty,m):
 size=float(str(sty.get('font-size',34)).removesuffix('px'));x,y=xy(m,float(v.get('x',0)),float(v.get('y',0)))
 content=''.join(v.itertext());text_check.append(content)
 value=html.escape(v.text or '')
 for t in v:
  if t.get('baseline-shift')=='sub':value+='<sub>'+html.escape(t.text or '')+'</sub>'
  else:value+=html.escape(t.text or '')
  value+=html.escape(t.tail or '')
 anchor=v.get('text-anchor','start');align={'start':'left','middle':'center','end':'right'}[anchor]
 # 不自动换行；宽度为宽松编辑区，原有对齐锚点决定最终位置。
 w=max(45,len(content)*size*.62+20);h=size*1.20
 x=x-w/2 if anchor=='middle' else x-w if anchor=='end' else x
 if anchor=='start':w=min(w,2800-x-12)
 font='Times New Roman' if sty.get('font-family','').startswith('Times') else 'Arial'
 bold=int(sty.get('font-weight','400')=='700');italic=2 if sty.get('font-style')=='italic' else 0
 c=cell(f'text;html=1;whiteSpace=nowrap;overflow=visible;align={align};verticalAlign=top;spacing=0;spacingTop=0;spacingBottom=0;spacingLeft=0;spacingRight=0;resizable=1;autosize=0;fontFamily={font};fontSize={size};fontStyle={bold+italic};fontColor={sty.get("fill","#17212B")};strokeColor=none;fillColor=none;',vertex='1',value=value,**{'data-kind':'editable-text'})
 # draw.io的HTML标签含行高内边距，补偿后基线与SVG接近，且末行不触发第二页。
 geom(c,x,y-size*1.035,w,h);count('editable_text_labels')
def walk(v,m=IDENT,inherit=None,inside=False):
 tag=v.tag.split('}')[-1]
 if tag in ('title','desc','defs','style'):return
 m=matmul(m,tf(v.get('transform','')))
 sty=dict(inherit or {})
 if tag=='text':sty.update(css.get('text',{}));sty.update(css.get('.'+v.get('class',''),{}))
 sty.update({k:val for k,val in v.attrib.items() if k in ('fill','stroke','stroke-width','stroke-dasharray','marker-end','font-family','font-size','font-style','font-weight')})
 sty.update(props(v.get('style','')))
 sty['_scale']=math.hypot(m[0],m[1])
 if tag in ('svg','g'):
  for child in v:walk(child,m,sty,inside or tag=='g')
 elif tag=='text':label(v,sty,m)
 elif tag=='rect':
  x,y=xy(m,float(v.get('x',0)),float(v.get('y',0)));w=float(v.get('width'))*sty['_scale'];h=float(v.get('height'))*sty['_scale']
  if x==0 and y==0 and w==2800 and h==1100:return
  rx=float(v.get('rx',0))*sty['_scale'];rounding=f'rounded=1;absoluteArcSize=1;arcSize={2*rx};' if rx else 'rounded=0;'
  c=cell('shape=rectangle;'+rounding+paint(sty),vertex='1',value='',**{'data-kind':'native-module'})
  geom(c,x,y,w,h)
  if not inside:anchors.append((c.get('id'),x,y,w,h))
  count('native_rectangles')
 elif tag in ('ellipse','circle'):
  cx,cy=xy(m,float(v.get('cx',0)),float(v.get('cy',0)));rx=float(v.get('rx',v.get('r',0)))*sty['_scale'];ry=float(v.get('ry',v.get('r',0)))*sty['_scale']
  angle=math.degrees(math.atan2(m[1],m[0]));c=cell(f'ellipse;rotation={angle};'+paint(sty),vertex='1',value='',**{'data-kind':'native-ellipse'})
  geom(c,cx-rx,cy-ry,2*rx,2*ry);count('native_ellipses')
 elif tag=='polygon':
  pts=[float(t) for t in re.findall(r'-?\d+(?:\.\d+)?',v.get('points'))]
  cmds=[('M',pts[:2])]+[('L',pts[i:i+2]) for i in range(2,len(pts),2)]+[('Z',[])]
  # 门槛判断用原生菱形，支持常规连接点。
  xs=pts[::2];ys=pts[1::2]
  c=cell('rhombus;'+paint(sty),vertex='1',value='',**{'data-kind':'native-decision'})
  geom(c,min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys));count('native_decisions')
 elif tag=='path':
  cmds=parsepath(v.get('d'))
  if not inside and all(op in ('M','L') for op,val in cmds) and sum(op=='M' for op,val in cmds)==1:
   native_edge(cmds,sty)
  else:
   stencil(cmds,sty,m,'Circular mechanism arc' if any(op=='A' for op,_ in cmds) else 'Vector path')
   if sty.get('marker-end'):marker(cmds,sty,m)
 else:raise ValueError('Unsupported SVG element: '+tag)

walk(doc)
mx=E.Element('mxfile',dict(host='Electron',agent='Editable local SVG reconstruction',version='32.5.5',type='device',compressed='false'))
diagram=E.SubElement(mx,'diagram',id='ica-framework-fusion',name='Research framework')
diagram.append(model)
E.indent(mx,space='  ')
TARGET.write_bytes(E.tostring(mx,encoding='utf-8',xml_declaration=True))
counts['total_cells']=serial
manifest=dict(source=SOURCE.name,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),output=TARGET.name,canvas=[2800,1100],counts=counts,source_text_labels=text_check,embedded_images=0)
(HERE/'conversion_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(counts,ensure_ascii=False))
