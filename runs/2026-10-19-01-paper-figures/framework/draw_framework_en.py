"""英文论文框架图：参照ProAgent的总览—放大布局，输出原生可编辑SVG。"""
from pathlib import Path
from html import escape
P = Path(__file__).parent
s = ['''<svg xmlns="http://www.w3.org/2000/svg" width="2100" height="1120" viewBox="0 0 2100 1120" role="img" aria-labelledby="title desc">
<title id="title">Curation–Expression Feedback in Postmortem Representation</title>
<desc id="desc">Empirical posts inform a fixed-type agent model. Curated exposure affects threshold-based expression; generated posts return to regime-specific candidate pools. An overview is expanded into a detailed feedback mechanism.</desc>
<defs>
 <marker id="gray" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9" fill="none" stroke="#8C8C8C" stroke-width="1.8"/></marker>
 <marker id="red" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#DA3434"/></marker>
 <marker id="blue" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9" fill="none" stroke="#5392BD" stroke-width="1.8"/></marker>
 <marker id="peach" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#D5A479"/></marker>
</defs>
<style>
 text{font-family:"Times New Roman",Times,serif;fill:#202020;font-size:25px}
 .title{font-size:36px;font-weight:bold}.head{font-size:29px}.small{font-size:22px}.tiny{font-size:20px}.white{fill:white}.muted{fill:#555}.italic{font-style:italic}
</style>
<rect width="2100" height="1120" fill="white"/>
''']
def box(id,x,y,w,h,fill,stroke='none',r=5,dash=None,sw=2):
 s.append(f'<rect id="{id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def txt(x,y,t,cl='',anchor='start',fill=None):
 s.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+escape(t)+'</text>')
def lines(x,y,ts,cl='',step=30):
 for i,t in enumerate(ts):txt(x,y+i*step,t,cl)
def path(d,c='gray',width=3,dash=None,arrow=True):
 colors={'gray':'#969696','red':'#DA3434','blue':'#5392BD','peach':'#D5A479'}
 s.append(f'<path d="{d}" fill="none" stroke="{colors.get(c,c)}" stroke-width="{width}" stroke-linejoin="round"'+(f' marker-end="url(#{c})"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def person(x,y,scale=1,color='#76A9C8'):
 s.append(f'<g transform="translate({x} {y}) scale({scale})"><circle cx="0" cy="0" r="16" fill="{color}" stroke="#56758B" stroke-width="1.5"/><path d="M-26 53 V37 Q-26 17 0 17 Q26 17 26 37 V53 Z" fill="{color}" stroke="#56758B" stroke-width="1.5"/><path d="M-11 33 V53 M11 33 V53" stroke="white" stroke-width="2"/></g>')
# 放大框先画，虚线连接在框外。
box('expanded-mechanism',550,38,1510,1020,'#FFFFFF','#D6D6D6',36,sw=5)
path('M438 278 L550 68','#D6D6D6',4,'12 8',False)
path('M438 886 L550 1024','#D6D6D6',4,'12 8',False)
txt(72,47,'(a) Research overview','head')
txt(585,87,'(b) Expanded agent–environment loop','head')
txt(2025,134,'Curation–Expression Feedback','title','end')
# 左侧：现实材料与总体循环
box('empirical-data',60,77,400,141,'#F3F3F1','#D3D3D0',8)
txt(260,113,'Empirical content analysis','head','middle')
txt(260,148,'49,930 posts · Douyin & Xiaohongshu','small','middle')
txt(260,183,'Temporal patterns & platform differences','small','middle')
path('M260 218 V258')
txt(280,246,'inputs & calibration','tiny')
box('overview-boundary',92,275,345,611,'#FFFFFF','#D7D7D7',0,'10 7',4)
box('overview-feed',137,296,192,58,'#48A5C4')
txt(233,333,'personal feed','','middle','white')
box('overview-agent-type',122,377,227,55,'#ECEBE4')
txt(235,412,'fixed author type','small','middle')
person(233,474,0.75)
box('overview-response',142,542,181,54,'#DFEBF4')
txt(232,577,'B · D · R','','middle')
box('overview-decision',125,620,215,58,'#E8873C',r=8)
txt(232,658,'expression decision','small','middle','white')
box('overview-generation',125,704,215,57,'#78A84A')
txt(232,741,'LLM generation','small','middle','white')
box('overview-action',146,814,174,54,'#D9D9D9')
txt(233,850,'new post','','middle')
box('overview-history',361,379,45,391,'#FFDA82','#F0C966',9)
s.append('<text x="384" y="575" text-anchor="middle" transform="rotate(-90 384 575)" class="small">exposure history</text>')
box('overview-pool',458,443,56,229,'#4C79B4')
s.append('<text x="487" y="558" text-anchor="middle" transform="rotate(90 487 558)" class="white">content pool</text>')
for a,b in [(432,450),(514,542),(596,620),(678,704),(761,814)]:path(f'M233 {a} V{b}')
path('M137 325 H109 V568 H138','blue',2.5)
path('M320 842 H487 V676','blue',3)
path('M487 443 V325 H333','blue',3)
# 左侧不添加决策返回B/D/R的箭头：模型没有这一独立反馈路径。
path('M329 325 H383 V377','peach',2)
path('M361 571 H327','peach',2)
txt(257,925,'100 agents · fixed types','small','middle')
txt(257,956,'W12–W22 · weekly opportunities','small','middle')
# 右侧：输入上下文，模仿模板的三个浅色信息块
box('external-input',615,177,420,110,'#F1F1F1')
box('external-tab',615,177,186,34,'#DCDCDC')
txt(628,202,'External posts','small')
lines(634,243,['Released by publication time;','same external sample across regimes.'],'small',29)
box('persona',615,310,420,108,'#EEEDE5')
box('persona-tab',615,310,186,34,'#DAD8CD')
txt(628,335,'Agent persona','small')
lines(634,375,['Fixed author type and threshold;','100 agents in five expression groups.'],'small',29)
box('feed',615,454,420,134,'#DFEAF3')
box('feed-tab',615,454,186,34,'#BDD3E7')
txt(628,479,'Personal feed','small')
lines(634,523,['Up to 10 eligible posts selected','by the assigned curation regime.'],'small',30)
# External posts直接进入各制度内容池，路径走顶部细通道。
path('M1035 233 H1060 V161 H1880 V191','gray',2.7)
txt(1110,183,'time-stamped input','tiny muted')
# 候选池与回流，两条红箭头把发布接回个人信息流。
box('candidate-pool',1740,195,270,133,'#E5EBF4','#A5B9D0',7)
txt(1875,233,'Regime-specific','head','middle')
txt(1875,264,'candidate pool','head','middle')
txt(1875,303,'external + generated posts','tiny','middle')
path('M1740 261 H1095 V513 H1041','red',4)
box('feedback-label',1146,232,256,46,'#FFFFFF')
txt(1274,264,'Re-circulation loop','head','middle','#D52D2D')
txt(1445,309,'selection · retention · return timing','tiny muted')
# 选择性表达机制
box('response-model',1140,362,367,285,'#E8873C',r=10)
txt(1323,403,'Expression activation','head white','middle')
box('response-details',1158,423,331,130,'#F6CFAB',r=8)
lines(1175,457,['B  Baseline expression utility','D  Opinion-climate response','R  Exposure-dependent decay'],'small',34)
box('threshold',1158,569,331,58,'#F4B57D',r=8)
txt(1323,607,'Utility ≥ individual threshold?','','middle')
# 外部池->feed已画；persona->决策；feed->决策。
path('M1035 369 H1115 V387 H1136','gray',2.7)
path('M1035 548 H1080 V598 H1136','gray',2.7)
txt(1077,576,'D','small italic')
# 达阈值才生成：清晰的独立绿色模块，原生节点图标。
path('M1507 598 H1550','gray',3)
txt(1533,580,'yes','small','middle')
box('llm-generator',1554,498,155,148,'#78A84A',r=7)
txt(1631,544,'LLM','head white','middle')
txt(1631,579,'post','head white','middle')
txt(1631,614,'generation','small white','middle')
path('M1709 572 H1760','gray',3)
box('generated-post',1766,413,246,253,'#F8F8F6','#B8B8B3',8)
# 帖文示意对象，不含虚构案例语句。
person(1800,449,0.55)
txt(1832,457,'New post','head')
path('M1788 494 H1988','#B8B8B3',2,None,False)
for yy,ww in [(519,189),(542,172),(565,194)]:path(f'M1788 {yy} h{ww}','#C9C9C6',3,None,False)
lines(1786,610,['Persona + current feed','guide text generation.'],'tiny muted',26)
path('M1890 413 V332','red',4)
txt(2019,393,'return','tiny',anchor='end',fill='#D52D2D')
path('M1323 647 V700 H1436','gray',2.5)
txt(1340,682,'no','small')
box('no-post',1440,678,195,45,'#E7E7E7')
txt(1537,709,'No post this turn','small','middle')
# 暴露历史：由接触更新，并进入R；不错误地把发帖本身计为接触。
box('history',615,809,1397,65,'#FFDA82','#F0C966',10)
txt(1313,849,'Prior exposure history: cumulative contact with same-type content','','middle')
path('M741 588 V804','peach',2.7)
txt(754,733,'store for subsequent turns','small',fill='#A47850')
path('M1260 809 V653','peach',2.7)
txt(1276,759,'R','small italic',fill='#A47850')
# 输入给文本生成器的上下文路径：沿底部灰线，绕开判定。
# 文本上下文在生成帖框中说明，避免跨越D/R路径的冗余连线。
# 实验安排下置，作为同一框架的研究设计而非反馈节点。
box('experiment-band',615,913,1397,108,'#F7F7F5','#DEDED9',6)
txt(637,945,'Controlled comparisons','head')
txt(637,980,'Random · Chronological · Interest-based','small')
txt(637,1007,'3 regimes × 3 seeds = 9 main runs','tiny muted')
path('M1121 932 V1002','#C7C7C2',1.4,None,False)
txt(1150,950,'Interest-based ablations','small')
txt(1150,984,'B = 0   |   D = 1   |   R = 1','small')
txt(1150,1008,'3 paired repeats per intervention','tiny muted')
path('M1508 932 V1002','#C7C7C2',1.4,None,False)
txt(1538,950,'Observed outcomes','small')
txt(1538,982,'Exposure → participation → re-exposure','tiny')
txt(1538,1008,'Supply trajectories by fixed author type','tiny muted')
# 图例与底线解释，模板同款色线说明。
for xx,label,cc in [(70,'process','gray'),(239,'curation / return','blue'),(548,'content feedback','red'),(843,'history update','peach')]:
 path(f'M{xx} 1088 h42',cc,2.8);txt(xx+51,1095,label,'tiny')
txt(2025,1095,'Changing public representation through participation, not changing author types.','tiny italic','end')
s.append('</svg>')
(P/'framework_proagent_en_v1.svg').write_text('\n'.join(s))
print(P/'framework_proagent_en_v1.svg')
