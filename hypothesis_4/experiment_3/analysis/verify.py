"""从原始决策独立复算预设主指标，并检查正式图表、链接和零新增调用边界。"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import hashlib,json,re,sys,os
from importlib.metadata import version
import pandas as pd
from PIL import Image
BASE=Path(__file__).resolve().parents[1];RUN=BASE;ROOT=BASE.parents[1];P=ROOT/'presentation/hypothesis_4/timestamp_bdr_v1';D=P/'data'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
source=read(D/'source_index.json');pairs=pd.read_csv(D/'paired_differences.csv');wk=pd.read_csv(D/'weekly_by_type.csv');tot=pd.read_csv(D/'weekly_totals.csv');baseline=read(BASE/'provenance/analysis_baseline.json')
raw={};source_files=0
for run in source['sources']:
 for f in [*run['agents'],*run['replay']]:assert sha(Path(f['path']))==f['sha256'];source_files+=1
 assert sha(Path(run['env_path']))==run['env_sha256']
 rows=[]
 for f in run['agents']:
  agent=read(Path(f['path']));rows.extend((agent['profile']['agent_type'],x) for x in agent['decision_log'])
 assert len(rows)==1100
 raw[(run['condition'],run['seed'])]={'late_posts_per_week':sum(x['posted'] for kind,x in rows if '2026-W19'<=x['week']<='2026-W22')/4,'late_meme_speak_rate':sum(x['speak'] is True for kind,x in rows if kind=='meme' and '2026-W19'<=x['week']<='2026-W22')/76,'mid_speak_rate':sum(x['speak'] is True for kind,x in rows if '2026-W14'<=x['week']<='2026-W18')/500}
 for key in raw[(run['condition'],run['seed'])]:
  if run['condition']=='full':continue
  row=pairs[(pairs.condition==run['condition'])&(pairs.seed==run['seed'])&(pairs.metric==key)].iloc[0]
  assert abs(row.ablation-raw[(run['condition'],run['seed'])][key])<1e-10
for _,row in pairs[pairs.metric.isin(['late_posts_per_week','late_meme_speak_rate','mid_speak_rate'])].iterrows():
 assert abs(row.full-raw[('full',row.seed)][row.metric])<1e-10
 assert abs(row.delta-(raw[(row.condition,row.seed)][row.metric]-raw[('full',row.seed)][row.metric]))<1e-10
assert len(wk)==660 and len(tot)==132 and all(wk.groupby(['condition','seed','week']).opportunities.sum()==100)
assert len(tot[tot.posted==0])>0,'必须确实保留零供给周，而不是删去后作图'
assert tot.posted.max()==63 and tot.posted.max()<=80
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append(a['src']);self.links.append(a['src'])
  elif tag=='a' and 'href' in a:self.links.append(a['href'])
for lang in ['zh','en']:
 f=P/f'report_{lang}.html';q=Links();q.feed(f.read_text());assert len(q.images)==3
 for link in q.links:assert not link.startswith(('http:','https:')) and (f.parent/link).exists(),link
 md=(P/f'report_{lang}.md').read_text();assert len(re.findall(r'!\[',md))==3
 assert all('assets/' in img for img in q.images)
 for text in ['13.83','6.83','47.81','17.11','19.13','49.20','30.70','30.07']:
  assert text in md,(lang,text)
for f in (P/'charts').glob('*.png'):
 with Image.open(f) as im:im.verify()
 assert sha(f)==sha(P/'assets'/f.name)
for f in (P/'charts').glob('*.svg'):
 assert '<text' in f.read_text(),'SVG文字应可编辑'
 assert sha(f)==sha(P/'assets'/f.name)
assert 'Glyph' not in (BASE/'checks/plot.log').read_text()
assert not (BASE/'checks/network_attempts.jsonl').exists() or not (BASE/'checks/network_attempts.jsonl').read_text()
assert sha(ROOT/'.agentsociety/progress.json')==baseline['main_progress_sha256']
assert sha(RUN/'runs/timestamp_bdr_v1_attempt_02/batch_execution.json')==baseline['ablation_execution_sha256']
assert (RUN/'runs/timestamp_bdr_v1_attempt_02/_extra_attempts.count').read_text().strip()==baseline['extra_requests_before']=='5'
summary=read(RUN/'runs/timestamp_bdr_v1_attempt_02/completion_audit.json');assert summary['total_provider_requests']==baseline['model_calls_before']==2657
result=dict(passed=True,units=12,raw_opportunities=13200,independent_primary_pair_checks=27,source_files_sha256_verified=source_files,weekly_type_rows=660,weekly_total_rows=132,zero_output_weeks_preserved=int((tot.posted==0).sum()),peak_weekly_posts=63,template_axis=[0,80],PNG_files=len(list((P/'charts').glob('*.png'))),SVG_files=len(list((P/'charts').glob('*.svg'))),report_image_links='all local and resolved',plot_font_warnings=0,network_attempts=0,additional_LLM_calls=0,main_machine_state_unchanged=True,ablation_results_and_ledger_unchanged=True,scientific_review='user approved adoption; primary-agent consistency review only; no independent model reviewer')
(BASE/'checks/final_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
versions={key:version(key) for key in ['agentsociety2','pandas','numpy','matplotlib','Pillow','duckdb']};versions['python']=sys.version;versions['toolchain']='existing project uv interpreter; no dependency installation or environment rebuild';(BASE/'checks/dependencies.json').write_text(json.dumps(versions,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
