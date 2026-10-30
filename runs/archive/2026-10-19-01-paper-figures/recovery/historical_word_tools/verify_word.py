"""验证修订回退、原格式保留、SVG媒体关系与接受视图的十组数字。"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import hashlib,json,re,zipfile
from lxml import etree as E
from build_tracked_word import HERE,RUN,SOURCE,TARGET,FIGS,NS,W,q,materialize

sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:E.tostring(x,method='c14n',exclusive=True) if x is not None else b''
def pprops(p):
 pr=deepcopy(p.find(q('pPr')))
 if pr is not None and not len(pr) and not pr.attrib:return b''
 return canon(pr)
def charformats(p):
 out=[]
 for t in p.xpath('.//w:t',namespaces=NS):
  parent=t.getparent();pr=parent.find(q('rPr'));key=canon(pr)
  out.extend((c,key) for c in (t.text or ''))
 return out

def main():
 with zipfile.ZipFile(SOURCE) as z:old={n:z.read(n) for n in z.namelist()}
 with zipfile.ZipFile(TARGET) as z:
  assert z.testzip() is None
  new={n:z.read(n) for n in z.namelist()}
 changed=[n for n in old if old[n]!=new[n]]
 assert set(changed)=={'word/document.xml','word/settings.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
 original=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml'])
 accepted=materialize(doc,True);rejected=materialize(doc,False)
 op=original.find(q('body')).findall(q('p'));rp=rejected.find(q('body')).findall(q('p'))
 assert len(op)==len(rp)==120
 assert all(pprops(a)==pprops(b) for a,b in zip(op,rp))
 assert all(charformats(a)==charformats(b) for a,b in zip(op,rp))
 assert all(''.join(a.itertext())==''.join(b.itertext()) for a,b in zip(original.findall('.//m:oMath',NS),rejected.findall('.//m:oMath',NS)))
 assert len(accepted.findall('.//m:oMath',NS))==1
 assert canon(op[62].find('.//m:oMath',NS))==canon(accepted.find('.//m:oMath',NS))
 assert [canon(t) for t in original.findall('.//w:tbl',NS)]==[canon(t) for t in accepted.findall('.//w:tbl',NS)]
 biblio_original=[canon(p) for p in op[97:]]
 ap=accepted.find(q('body')).findall(q('p'));start=next(i for i,p in enumerate(ap) if ''.join(p.xpath('.//w:t/text()',namespaces=NS))=='参考文献')
 assert biblio_original==[canon(p) for p in ap[start:]]
 text='\n'.join(''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in ap)
 for s in ['每种制度采用10个随机种子','30次完整运行','10.8%、75.0%和68.5%','43.6%和26.3%','59.7%和49.7%','24.9%和7.4%','46,602','2026年3月24日']:
  assert s in text,s
 for s in ['图5','图 5','三次配对','九次运行','42.0%','56.6%','47.8%','65.6%','B=0','R=1','D=1']:
  assert s not in text,s
 changes=doc.xpath('.//w:ins|.//w:del',namespaces=NS);ids=[x.get(q('id')) for x in changes]
 assert len(ids)==len(set(ids))==121
 settings=E.fromstring(new['word/settings.xml']);assert settings.find(q('trackRevisions')) is not None
 rels=E.fromstring(new['word/_rels/document.xml.rels']);rm={r.get('Id'):r.get('Target') for r in rels}
 drawings=accepted.findall('.//w:drawing',NS);assert len(drawings)==4
 images=[]
 for i,drawing in enumerate(drawings,1):
  svg=drawing.find('.//asvg:svgBlip',NS);assert svg is not None
  target='word/'+rm[svg.get('{'+NS['r']+'}embed')]
  stem=['figure_01_observed_pooled','figure_02_observed_platforms','figure_03_simulated_trajectories','figure_04_feedback_exposure'][i-1]
  assert new[target]==(FIGS/f'{stem}.svg').read_bytes()
  root=E.fromstring(new[target]);_,_,vw,vh=map(float,root.get('viewBox').split())
  extent=drawing.find('.//wp:extent',NS);cx,cy=int(extent.get('cx')),int(extent.get('cy'))
  assert abs(cy-cx*vh/vw)<1
  images.append({'figure':i,'svg_part':target,'svg_sha256':sha(new[target]),'aspect_ratio_preserved':True})
 # ISO核心结构对比：原稿含MS/WPS扩展，记录所有差异，不声称全包ISO无错误。
 xsd=Path('/Users/easylife/Project/AgentSociety/.claude/skills/docx/scripts/office/schemas/ISO-IEC29500-4_2016/wml.xsd')
 schema=E.XMLSchema(E.parse(str(xsd)));diff={}
 for part in ['word/document.xml','word/settings.xml']:
  errors=[]
  for data in [old[part],new[part]]:
   schema.validate(E.fromstring(data));errors.append(Counter(e.message for e in schema.error_log))
  delta=dict(errors[1]-errors[0]);diff[part]=delta
  assert all('word/2010/wordml}paraId' in message for message in delta),delta
 manifest=json.loads((RUN/'inputs/ICA2027-V5.manifest.json').read_text())
 assert sha(Path(manifest['source']).read_bytes())==sha(SOURCE.read_bytes())==manifest['sha256']
 report={'date':'2026-10-24','file':TARGET.name,'source_original_unchanged':True,
  'source_sha256':sha(SOURCE.read_bytes()),'output_sha256':sha(TARGET.read_bytes()),
  'changed_package_parts':changed,'preserved_package_parts':len(old)-len(changed),
  'new_media_parts':sorted(set(new)-set(old)),
  'track_revisions_enabled':True,'tracked_insertions':len(doc.findall('.//w:ins',NS)),
  'tracked_deletions':len(doc.findall('.//w:del',NS)),'unique_revision_ids':True,
  'reject_all_restores_original_text_and_character_formats':True,
  'original_paragraph_formats_preserved':120,'main_formula_preserved':True,
  'tables_and_bibliography_preserved':True,'current_figures':[1,2,3,4],'figure5_tracked_deleted':True,
  'images':images,'iso_schema_difference':diff,
  'schema_note':'原稿自带MS/WPS扩展不受纯ISO模式识别；新差异仅四个新增图注段的MS paraId，无新增核心元素顺序错误。通用office验证CLI因bundled环境缺defusedxml未运行，使用bundled lxml直接校验并比较。',
  'readme':'PNG视觉核验记录在README；未以位图替代SVG主媒体，PNG只用于旧版Office兼容。'}
 (HERE/'qa/structural_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'pass':True,'revisions':len(changes),'svg_figures':4,'original_paragraph_formats_preserved':120,'original_unchanged':True},ensure_ascii=False))

if __name__=='__main__':main()
