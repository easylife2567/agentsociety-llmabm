"""沿用V5包与格式，生成十组主实验的真实Word修订副本。"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,importlib.util,json,re,sys,uuid,zipfile
from lxml import etree as E

HERE=Path(__file__).resolve().parent
RUN=HERE.parent
SOURCE=RUN/'inputs/ICA2027-V5.docx'
FIGS=RUN/'figures_seed10'
TARGET=HERE/'ICA2027-V5_10组实验_修订版.docx'
SKILL=Path('/Users/easylife/.codex/plugins/cache/openai-primary-runtime/documents/26.1020.11348/skills/documents')
spec=importlib.util.spec_from_file_location('tracked_helper',SKILL/'scripts/add_tracked_replacements.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
ASVG='http://schemas.microsoft.com/office/drawing/2016/SVG/main'
PR='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
NS=dict(w=W,r=R,a=A,wp=WP,m=M,asvg=ASVG)
q=lambda n:f'{{{W}}}{n}'
sha=lambda b:hashlib.sha256(b).hexdigest()
WHEN=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
AUTHOR='Codex'

class Editor:
 def __init__(self,doc):
  self.doc=doc;self.pars=doc.find(q('body')).findall(q('p'))
  self.cid=helper._next_change_id(doc);self.log=[];self.added_paras=[]
 def mark(self,kind):
  node=E.Element(q(kind),{q('id'):str(self.cid),q('author'):AUTHOR,q('date'):WHEN});self.cid+=1;return node
 def text(self,p):
  return ''.join(t.text or '' for t in p.xpath('.//w:t[not(ancestor::w:del)]',namespaces=NS))
 def run(self,s,source=None):
  r=E.Element(q('r'))
  if source is not None:
   r.attrib.update(source.attrib)
   pr=source.find(q('rPr'))
   if pr is not None:r.append(deepcopy(pr))
  t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s
  return r
 def replace(self,i,old,new):
  p=self.pars[i];plain=self.text(p);assert plain.count(old)==1,(i,old,plain)
  start=plain.index(old);end=start+len(old);offset=0;selected=[]
  for t in p.xpath('.//w:t[not(ancestor::w:del)]',namespaces=NS):
   s=t.text or '';a,b=offset,offset+len(s);offset=b
   if b>start and a<end:selected.append((t,max(0,start-a),min(len(s),end-a)))
  assert selected
  inserted=False
  for t,a,b in selected:
   r=t.getparent();assert r.tag==q('r')
   assert all(c.tag in (q('rPr'),q('t')) for c in r),('complex run',i,old)
   parent=r.getparent();pos=parent.index(r);s=t.text or '';nodes=[]
   if a:nodes.append(self.run(s[:a],r))
   deleted=self.mark('del');oldrun=self.run(s[a:b],r)
   oldrun.find(q('t')).tag=q('delText');deleted.append(oldrun);nodes.append(deleted)
   if not inserted and new:
    ins=self.mark('ins');ins.append(self.run(new,r));nodes.append(ins);inserted=True
   if b<len(s):nodes.append(self.run(s[b:],r))
   parent.remove(r)
   for node in reversed(nodes):parent.insert(pos,node)
  self.log.append({'paragraph':i,'old':old,'new':new,'kind':'tracked_text'})
 def insert_before(self,i,needle,new):
  p=self.pars[i];plain=self.text(p);assert plain.count(needle)==1
  pos=plain.index(needle);offset=0
  for t in p.xpath('.//w:t[not(ancestor::w:del)]',namespaces=NS):
   s=t.text or ''
   if offset<=pos<=offset+len(s):
    r=t.getparent();assert all(c.tag in (q('rPr'),q('t')) for c in r)
    parent=r.getparent();index=parent.index(r);cut=pos-offset;nodes=[]
    if cut:nodes.append(self.run(s[:cut],r))
    ins=self.mark('ins');ins.append(self.run(new,r));nodes.append(ins)
    if cut<len(s):nodes.append(self.run(s[cut:],r))
    parent.remove(r)
    for node in reversed(nodes):parent.insert(index,node)
    self.log.append({'paragraph':i,'before':needle,'new':new,'kind':'tracked_insert'});return
   offset+=len(s)
  raise AssertionError((i,needle))
 def delete_children(self,i,start,end):
  p=self.pars[i];children=list(p)[start:end];assert children
  deleted=self.mark('del')
  for child in children:
   p.remove(child)
   for t in child.iter(q('t')):t.tag=q('delText')
   for t in child.iter(q('instrText')):t.tag=q('delInstrText')
   deleted.append(child)
  p.insert(start,deleted)
  self.log.append({'paragraph':i,'kind':'tracked_fragment_delete','children':[start,end]})
 def delete_paragraph(self,i):
  p=self.pars[i];pr=p.find(q('pPr'))
  if pr is None:pr=E.Element(q('pPr'));p.insert(0,pr)
  rp=pr.find(q('rPr'))
  if rp is None:rp=E.SubElement(pr,q('rPr'))
  rp.insert(0,self.mark('del'))
  deleted=self.mark('del')
  for child in list(p):
   if child is pr:continue
   p.remove(child)
   for t in child.iter(q('t')):t.tag=q('delText')
   for t in child.iter(q('instrText')):t.tag=q('delInstrText')
   deleted.append(child)
  if len(deleted):p.append(deleted)
  self.log.append({'paragraph':i,'kind':'tracked_paragraph_delete'})
 def caption_note(self,caption_index,description):
  original=self.pars[caption_index];p=E.Element(q('p'),attrib=dict(original.attrib))
  for key in list(p.attrib):
   if E.QName(key).localname in ('paraId','textId'):p.set(key,f'{uuid.uuid4().int & 0x7FFFFFFF:08X}')
  pr=deepcopy(original.find(q('pPr')));p.append(pr)
  # 新增说明段落沿用原图题字体/字号；仅新段落两端对齐并允许自然分页。
  for name,value in [('jc','both'),('keepNext','0'),('keepLines','0')]:
   el=pr.find(q(name))
   if el is None:el=E.Element(q(name));pr.insert(1,el)
   el.set(q('val'),value)
  rp=pr.find(q('rPr'))
  if rp is None:rp=E.SubElement(pr,q('rPr'))
  rp.insert(0,self.mark('ins'))
  order=['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl',
         'numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens',
         'kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE',
         'autoSpaceDN','bidi','adjustRightInd','snapToGrid','spacing','ind',
         'contextualSpacing','mirrorIndents','suppressOverlap','jc','textDirection',
         'textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle',
         'rPr','sectPr','pPrChange']
  children=list(pr)
  for c in children:pr.remove(c)
  for c in sorted(children,key=lambda e:order.index(E.QName(e).localname)):pr.append(c)
  base=next(r for r in reversed(original.findall(q('r'))) if r.find(q('t')) is not None)
  ins=self.mark('ins');ins.append(self.run('注：'+description,base));p.append(ins)
  original.addnext(p);self.added_paras.append(p)
  self.log.append({'after_paragraph':caption_index,'kind':'tracked_new_caption_note','text':description})

def materialize(root,accept):
 root=deepcopy(root)
 for p in list(root.iter(q('p'))):
  mark=p.find('w:pPr/w:rPr/w:del' if accept else 'w:pPr/w:rPr/w:ins',NS)
  if mark is not None and p.getparent() is not None:p.getparent().remove(p)
 for el in list(root.iter()):
  if el.tag not in (q('ins'),q('del')):continue
  parent=el.getparent()
  if parent is None:continue
  if parent.tag==q('rPr'):
   parent.remove(el)
   if not len(parent) and not parent.attrib:parent.getparent().remove(parent)
   continue
  keep=(el.tag==q('ins'))==accept;index=parent.index(el)
  if keep:
   for child in list(el):
    for t in child.iter(q('delText')):t.tag=q('t')
    for t in child.iter(q('delInstrText')):t.tag=q('instrText')
    el.remove(child);parent.insert(index,child);index+=1
  parent.remove(el)
 return root

def main():
 assert not TARGET.exists(),'不要覆盖已交付版本；新迭代须用明确临时版本后核验。'
 with zipfile.ZipFile(SOURCE) as z:
  infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
 doc=E.fromstring(parts['word/document.xml']);ed=Editor(doc);assert len(ed.pars)==120
 original_par_text=[ed.text(p) for p in ed.pars]
 # 摘要、理论承诺、样本分母及事件周。
 ed.replace(2,'通过设置随机、时序与兴趣三种算法策展制度及表达机制干预','设置随机、时序与兴趣三种算法策展制度，每种制度采用10个随机种子，共形成30次主运行')
 ed.replace(2,'玩梗话语的突出不仅取决于自身表达的激活，也与其他群体的注意力衰减和持续退场密切相关。','不同群体的信息接触与表达参与发生分化，并与后续内容供给及可见位置的变化相互联系。')
 ed.replace(28,'事件注意力权重（R）','同类接触权重（R）')
 ed.replace(28,'B 与 R 分别用来控制用户的常态发帖基线以及事件刺激带来的注意力衰减','B 与 R 分别用来刻画用户的常态发帖基线以及累计同类接触增加时的权重衰减')
 ed.replace(28,'有关表达效用的函数形式、参数标定以及组件消融实验的具体设计','有关表达效用的函数形式、参数标定以及策展制度比较的具体设计')
 ed.insert_before(33,'各类别的操作性编码标准如下表所示：','图1、图2的五类分析剔除3,315条爬取噪音和13条存疑标签，共纳入46,602条。各周比例以当周五类内容合计为分母，合并比例先加总两个平台的类别计数后计算。')
 ed.replace(43,'基于抖音和小红书49,930条真实帖文的内容分析','基于原始49,930条帖文中纳入五类分析的46,602条帖文')
 ed.replace(47,'逝世当周W13','逝世当周W13（2026年3月24日所在周）')
 ed.replace(60,'仿真覆盖W12—W22共11周，','仿真覆盖2026年W12—W22共11周，其中W13为张雪峰逝世周（2026年3月24日）；')
 # 仅修订章号文字，保留原有标题段落样式，不合并不同层级。
 ed.replace(40,'三、逝者公共表征讨论风向的时序演变与平台差异','四、逝者公共表征讨论风向的时序演变与平台差异')
 ed.replace(55,'四、算法策展与用户表达的循环互动：逝后舆论形象的演化机制','五、算法策展与用户表达的循环互动：逝后舆论形象的演化机制')
 ed.replace(56,'第三章实证数据表明','第四章实证数据表明')
 ed.replace(93,'五、讨论与结论','六、讨论与结论')
 # 此片段含三个干预OMML，连同句子完整追踪删除，主公式062不动。
 assert ''.join(ed.pars[64][2].itertext()).startswith('兴趣制度内另分别设置')
 ed.delete_children(64,2,11)
 ed.replace(64,'见表1','见表4')
 ed.replace(64,'通过三个随机种子进行配对重复，共形成九次运行','每种制度采用10个随机种子进行配对重复，共形成30次完整运行')
 ed.insert_before(64,'本节分析','各项指标首先在每次运行内计算，再跨10个种子取算术均值。')
 ed.replace(64,'，以W14—W18为注意力衰减机制的观察窗口。','。')
 ed.replace(65,'表1','表4')
 # 主实验平均轨迹和运行级指标。
 ed.replace(67,'在相同的外部事件与群体构成下，三种算法策展制度分别形成了不同的舆论演化轨迹（图3）。','在相同的外部事件与群体构成下，十次运行的平均轨迹显示，三种算法策展制度分别形成了不同的舆论演化轨迹（图3a—c）。')
 ed.replace(67,'随机制度中的悼念高峰出现得更晚、强度也相对较弱','随机制度的平均悼念高峰位于W14、强度也相对较弱')
 ed.replace(70,'平均发帖数量','每次运行累计发帖数量的均值')
 ed.replace(70,'3.0条、43.0条和36.3条','3.1条、45.4条和37.8条')
 ed.replace(70,'10.3%、73.3%和65.6%','10.8%、75.0%和68.5%')
 ed.replace(70,'三次重复','十次重复')
 ed.replace(70,'时序制度下玩梗型作者的发帖量在W21达到峰值，兴趣制度则持续增长至W22','时序制度下玩梗型作者的平均发帖量在W21达到峰值，兴趣制度的平均发帖量则持续增长至W22')
 ed.insert_before(71,'由此，即使面对','需要注意的是，时序制度还使生成帖在同批行动结束后入池并对后续批次可见，而随机与兴趣制度的生成帖次周才取得展示资格；制度间同时存在候选与保留安排差异。因此，此处比较反映完整策展制度的结果，不能单独归因于排序方式。')
 ed.replace(75,'并通过兴趣制度内的组件干预，','')
 ed.replace(78,'42.0%和25.2%','43.6%和26.3%')
 ed.replace(79,'56.6%和47.8%','59.7%和49.7%')
 ed.replace(79,'3.9%','4.1%')
 ed.replace(80,'22.7%和6.8%','24.9%和7.4%')
 for i in range(83,93):ed.delete_paragraph(i)
 old='更深层的原因在于，不同策展制度改变了各类表达的参与时机与持续条件，使玩梗群体的表达激活与其他群体的逐渐退场共同推动了话语优势的形成。因此，玩梗话语的突出既可能源于自身传播的强化，也可能是其他声音相对沉寂的结果，其演化并非单向、必然的算法放大过程。'
 new='在本模型的设定下，不同策展制度下的信息接触、选择性表达与生成帖再展示存在相互衔接的差异，并与后期供给构成的分化相联系。因此，玩梗型表达的突出不必以用户原有表达倾向的普遍改变为前提，其演化也不宜被解释为单向、必然的算法放大过程。'
 ed.replace(94,old,new)
 ed.insert_before(96,'未来研究可进一步','本研究的主实验由两个执行批次组成，并依据采用的模型版本等价约定合并分析，以分批结果检查方向稳定性。种子范围与执行批次相互绑定，不能由分批差异识别模型版本的独立影响。制度比较同时涉及内容排序、候选资格和回流时机，现有结果不能分解各环节的独立贡献；当前分析也未分别识别B、D、R组件的独立效应。')
 # 复制原有绘图节点与段落，只改变新图媒体、等比高度和替代文字。
 rels=E.fromstring(parts['word/_rels/document.xml.rels']);ct=E.fromstring(parts['[Content_Types].xml'])
 rid=max(int(r.get('Id')[3:]) for r in rels if re.match(r'rId\d+$',r.get('Id','')))+1
 docpr=max(int(x.get('id')) for x in doc.findall('.//wp:docPr',NS))+1
 if not any(x.get('Extension')=='svg' for x in ct):E.SubElement(ct,f'{{{CT}}}Default',Extension='svg',ContentType='image/svg+xml')
 titles=[];descs=[]
 caps=(FIGS/'CAPTIONS_ZH.md').read_text()
 for i in range(1,5):
  section=caps.split(f'## 图{i}\n',1)[1].split('\n## ',1)[0].strip()
  match=re.match(r'\*\*图\d\s+(.*?)\*\*\s*(.*)',section,re.S);assert match
  titles.append(match[1].rstrip('。'));descs.append(match[2].strip())
 stems=['figure_01_observed_pooled','figure_02_observed_platforms','figure_03_simulated_trajectories','figure_04_feedback_exposure']
 image_log=[]
 for i,(pi,ci,stem) in enumerate(zip([44,50,68,76],[45,51,69,77],stems),1):
  p=ed.pars[pi];oldrun=p.find('w:r[w:drawing]',NS);assert oldrun is not None
  newrun=deepcopy(oldrun);drawing=newrun.find(q('drawing'))
  ext=drawing.find('.//wp:extent',NS);cx=int(ext.get('cx'));svg=E.fromstring((FIGS/f'{stem}.svg').read_bytes())
  _,_,vw,vh=map(float,svg.get('viewBox').split());cy=round(cx*vh/vw)
  ext.set('cy',str(cy))
  for ex in drawing.findall('.//a:xfrm/a:ext',NS):ex.set('cx',str(cx));ex.set('cy',str(cy))
  for lock in drawing.findall('.//a:graphicFrameLocks',NS)+drawing.findall('.//a:picLocks',NS):lock.set('noChangeAspect','1')
  prop=drawing.find('.//wp:docPr',NS);prop.set('id',str(docpr));docpr+=1
  prop.set('name',f'Figure {i} SVG');prop.set('descr',titles[i-1])
  for inline in drawing.findall('.//wp:inline',NS):
   for attr in list(inline.attrib):
    if E.QName(attr).localname in ('anchorId','editId'):inline.set(attr,uuid.uuid4().hex[:8].upper())
  pngrid,svgrid=f'rId{rid}',f'rId{rid+1}';rid+=2
  for extname,rname in [('png',pngrid),('svg',svgrid)]:
   media=f'figure_{i:02d}_seed10.{extname}'
   E.SubElement(rels,f'{{{PR}}}Relationship',Id=rname,Type=R+'/image',Target='media/'+media)
   parts['word/media/'+media]=(FIGS/f'{stem}.{extname}').read_bytes()
  blip=drawing.find('.//a:blip',NS);blip.set(f'{{{R}}}embed',pngrid)
  oldext=blip.find('a:extLst',NS)
  if oldext is not None:blip.remove(oldext)
  lst=E.SubElement(blip,f'{{{A}}}extLst');ex=E.SubElement(lst,f'{{{A}}}ext',uri='{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
  E.SubElement(ex,f'{{{ASVG}}}svgBlip',{f'{{{R}}}embed':svgrid},nsmap={'asvg':ASVG})
  pos=p.index(oldrun);p.remove(oldrun);deleted=ed.mark('del');deleted.append(oldrun);inserted=ed.mark('ins');inserted.append(newrun)
  p.insert(pos,deleted);p.insert(pos+1,inserted)
  oldtitle=original_par_text[ci].split(str(i),1)[1].strip()
  ed.replace(ci,oldtitle,titles[i-1]);ed.caption_note(ci,descs[i-1])
  image_log.append({'figure':i,'width_emu':cx,'height_emu':cy,'svg_rid':svgrid,'png_fallback_rid':pngrid,'svg_sha256':sha(parts[f'word/media/figure_{i:02d}_seed10.svg'])})
 settings=E.fromstring(parts['word/settings.xml']);helper._enable_track(settings)
 view=settings.find(q('revisionView'))
 if view is None:view=E.Element(q('revisionView'));settings.insert(0,view)
 for key in ['markup','comments','insDel','formatting']:view.set(q(key),'1')
 updates=settings.find(q('updateFields'))
 if updates is None:updates=E.SubElement(settings,q('updateFields'))
 updates.set(q('val'),'true')
 # CT_Settings有顺序要求，只移动本轮新增的三个设置，不重排旧设置。
 track=settings.find(q('trackRevisions'))
 settings.remove(view);settings.remove(track);settings.remove(updates)
 protection=settings.find(q('documentProtection'))
 if protection is not None:
  pos=settings.index(protection);settings.insert(pos,view);settings.insert(pos+1,track)
 else:settings.insert(0,view);settings.insert(1,track)
 foot=settings.find(q('footnotePr'))
 settings.insert(settings.index(foot) if foot is not None else len(settings),updates)
 parts['word/document.xml']=helper._xml_bytes(doc)
 parts['word/settings.xml']=helper._xml_bytes(settings)
 parts['word/_rels/document.xml.rels']=helper._xml_bytes(rels)
 parts['[Content_Types].xml']=helper._xml_bytes(ct)
 with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED) as out:
  oldnames=set()
  for info in infos:out.writestr(info,parts[info.filename]);oldnames.add(info.filename)
  for name,data in parts.items():
   if name not in oldnames:out.writestr(name,data)
 # 仅供QA的接受/拒绝视图；不另作为用户交付。
 qa=HERE/'qa';qa.mkdir(exist_ok=True)
 for mode in ['accepted','rejected']:
  final=materialize(doc,mode=='accepted')
  with zipfile.ZipFile(qa/f'{mode}_check.docx','w',zipfile.ZIP_DEFLATED) as out:
   for name,data in parts.items():out.writestr(name,helper._xml_bytes(final) if name=='word/document.xml' else data)
  (qa/f'{mode}_check.txt').write_text('\n'.join(''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in final.find(q('body')).findall(q('p')))+'\n')
 rejected=materialize(doc,False)
 rejecttexts=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in rejected.find(q('body')).findall(q('p'))]
 assert rejecttexts==original_par_text,'拒绝全部修订后的原段落文字必须完全恢复'
 (qa/'edit_log.json').write_text(json.dumps({'source_sha256':sha(SOURCE.read_bytes()),'output':TARGET.name,'author':AUTHOR,'date':WHEN,'edits':ed.log,'images':image_log,'reject_all_text_restores_original':True},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'output':str(TARGET),'tracked_changes':len(doc.findall('.//w:ins',NS))+len(doc.findall('.//w:del',NS)),'edit_operations':len(ed.log),'svg_figures':4,'reject_all_restores_text':True},ensure_ascii=False))

if __name__=='__main__':main()
