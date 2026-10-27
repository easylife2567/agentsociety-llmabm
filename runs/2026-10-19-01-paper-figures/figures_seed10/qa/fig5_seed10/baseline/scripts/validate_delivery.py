"""离线核对最终四图的数据身份、可编辑SVG、PDF字体与文字边界。"""
from pathlib import Path
import argparse,hashlib,json,sys,xml.etree.ElementTree as E
from datetime import date
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parents[1]
DATA=OUT/'source_data'
STEMS=['figure_01_observed_pooled','figure_02_observed_platforms',
       'figure_03_simulated_trajectories','figure_04_feedback_exposure']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--pymupdf-path',type=Path)
 args=parser.parse_args()
 if args.pymupdf_path:sys.path.insert(0,str(args.pymupdf_path))
 import fitz
 source=json.loads((DATA/'seed10_sources.json').read_text())
 for name,digest in source['output_sha256'].items():
  if (DATA/name).exists():assert sha(DATA/name)==digest,name
 r=pd.read_csv(DATA/'seed10_runs.csv');w=pd.read_csv(DATA/'seed10_weekly.csv')
 assert len(r)==30 and len(w)==330
 assert not r.duplicated(['arm','seed']).any()
 assert all(set(g.seed)==set(range(10)) for _,g in r.groupby('arm'))
 assert all(g.week.nunique()==11 for _,g in w.groupby(['arm','seed']))
 cols=[f'agent_supply_{c}' for c in ['education','mourning','meme','other','marketing']]
 assert (w[cols].sum(axis=1)==w.agent_supply).all()
 assert w.agent_supply.sum()==r.total_posts.sum()==6041
 o=pd.read_csv(DATA/'observed_weekly.csv')
 counts=o.pivot(index=['week','category'],columns='platform',values='count')
 assert (counts.pooled==counts.douyin+counts.xiaohongshu).all()
 assert o[o.platform=='pooled']['count'].sum()==46602
 assert np.allclose(o.groupby(['platform','week']).share.sum(),1)
 assert date(2026,3,24).isocalendar().week==13
 summaries=r.groupby('arm')[['late_meme_posts','late_meme_share','own_share','meme_post_rate','cross_generated_share']].mean().to_dict('index')
 records=[]
 for i,stem in enumerate(STEMS,1):
  svg=E.parse(OUT/f'{stem}.svg').getroot()
  texts=[''.join(t.itertext()) for t in svg.findall('.//{http://www.w3.org/2000/svg}text')]
  assert not svg.findall('.//{http://www.w3.org/2000/svg}image')
  assert svg.get('preserveAspectRatio')=='xMidYMid meet'
  expected=2 if i<3 else 4 if i==3 else 3
  assert all(f'Fig. {i}{chr(97+j)}' in texts for j in range(expected))
  assert 'viewBox' in svg.attrib
  if i<4:assert any("W13: Zhang Xuefeng's death (24 Mar 2026)" in t for t in texts)
  if i==3:
   # 图3把重复单位与线/点含义移入配套图注，仍核对解释齐全。
   caption=(OUT/'CAPTIONS_ZH.md').read_text().split('## 图3\n',1)[1].split('\n## ',1)[0]
   assert all(label in caption for label in ('10个种子','共30次主运行','细线','粗线','散点','黑色短横线'))
  if i==4:assert any('n = 10 seeds per regime' in t for t in texts)
  build=json.loads((OUT/'qa'/f'{stem}.build.json').read_text());assert not build['labels']
  for ext,digest in build['outputs'].items():assert sha(OUT/f'{stem}.{ext}')==digest
  pdf=fitz.open(OUT/f'{stem}.pdf');page=pdf[0];assert len(pdf)==1
  assert not page.get_images(full=True)
  spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] if s['text'].strip()]
  assert spans and min(s['size'] for s in spans)>7.8
  clipped=[];overlaps=[]
  for n,a in enumerate(spans):
   ra=fitz.Rect(a['bbox'])
   if ra.x0<-.5 or ra.y0<-.5 or ra.x1>page.rect.width+.5 or ra.y1>page.rect.height+.5:clipped.append(a['text'])
   for b in spans[n+1:]:
    rb=fitz.Rect(b['bbox']);intersection=ra&rb
    if not intersection.is_empty and intersection.get_area()>min(ra.get_area(),rb.get_area())*.10:
     overlaps.append([a['text'],b['text'],round(intersection.get_area(),2)])
  assert not clipped,clipped
  assert not overlaps,overlaps
  records.append({'figure':i,'stem':stem,'panels':expected,'svg_text_objects':len(texts),
    'svg_embedded_images':0,'pdf_raster_images':0,'minimum_font_pt':round(min(s['size'] for s in spans),2),
    'size_mm':[round(page.rect.width*25.4/72,2),round(page.rect.height*25.4/72,2)],
    'clipped_pdf_text':clipped,'overlapping_pdf_text':overlaps,
    'outputs':{ext:sha(OUT/f'{stem}.{ext}') for ext in ['svg','pdf','png']}})
  pdf.close()
 report={'date':'2026-10-24','primary_figures':[1,2,3,4],'deferred_figure':5,
  'main_runs':30,'seeds_per_regime':10,'successful_agent_posts':6041,
  'observed_five_category_posts':46602,'original_observed_records':49930,
  'summary_by_regime':summaries,'figures':records,'pymupdf':fitz.VersionBind,
  'scope':'重新核验冻结作图表、源清单哈希、比例和输出；未重跑仿真，未重新扫描3416项原始输入。',
  'source_csv_sha256':{p.name:sha(p) for p in DATA.glob('*.csv')}}
 (OUT/'qa/delivery_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'pass':True,'figures':len(records),'main_runs':30,'successful_posts':6041},ensure_ascii=False))

if __name__=='__main__':main()
