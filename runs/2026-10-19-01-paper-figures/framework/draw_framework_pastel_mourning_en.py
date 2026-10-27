"""在四阶段英文图中增加可编辑的悼念情境插画；计算机制、数字及箭头保持。"""
from pathlib import Path
from html import escape
P = Path(__file__).parent
s = ['''<svg xmlns="http://www.w3.org/2000/svg" width="2520" height="1510" viewBox="0 0 2520 1510" role="img" aria-labelledby="title desc">
<title id="title">Curation, selective expression and post recirculation: research framework</title>
<desc id="desc">A four-stage research framework grounded in ICA2027v1. Empirical characterization is distinct from separately frozen simulation inputs. A fixed population of 100 agents receives regime-specific feeds, evaluates expression utility from B, D and prior-exposure weight R, and generates posts only after reaching an individual threshold. Successful posts recirculate under regime-specific eligibility rules. Current exposure updates history for later actions. Candle and white-flower illustrations indicate the digital-mourning context only, not additional model variables or findings.</desc>
<defs>
 <marker id="arrow" viewBox="0 0 10 10" refX="8.8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#171717"/></marker>
 <marker id="state" viewBox="0 0 10 10" refX="8.8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#557B64"/></marker>
</defs>
<style>
 text {font-family:Arial,Helvetica,sans-serif;fill:#171717;font-size:26px}
 .column{font-size:37px;font-weight:700}.head{font-size:30px;font-weight:600}
 .top{font-size:31px}.small{font-size:24px}.tiny{font-size:22px}.muted{fill:#4C5557}
 .math{font-family:"Times New Roman",Times,serif;font-style:italic;font-size:38px}
</style>
<rect width="2520" height="1510" fill="white"/>
''']
def box(id,x,y,w,h,fill,stroke='#D4D4D4',r=0,dash=None,sw=2.4):
 s.append(f'<rect id="{id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def text(x,y,t,cl='',anchor='start',fill=None):
 s.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+escape(t)+'</text>')
def lines(x,y,ts,cl='',step=36,anchor='start'):
 for i,t in enumerate(ts):text(x,y+i*step,t,cl,anchor)
def path(d,kind='arrow',dash=None,sw=4):
 s.append(f'<path d="{d}" fill="none" stroke="'+('#557B64' if kind=='state' else '#171717')+f'" stroke-width="{sw}" stroke-linejoin="round" marker-end="url(#{kind})"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def rule(d,stroke='#9BA4A7',sw=2):
 s.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
def avatar(x,y,color,scale=1):
 s.append(f'<g transform="translate({x} {y}) scale({scale})"><circle cx="0" cy="0" r="18" fill="#FFE0BD" stroke="#555" stroke-width="2"/><path d="M-18 -2 Q-18 -25 0 -23 Q18 -23 18 -2 L10 -11 L-9 -11 Z" fill="#596B7A"/><path d="M-29 60 V37 Q-29 19 0 19 Q29 19 29 37 V60 Z" fill="{color}" stroke="#555" stroke-width="2"/><path d="M-12 33 V60 M12 33 V60" stroke="white" stroke-width="2.3"/></g>')
def document(x,y,color='#DCEAF4',scale=1):
 s.append(f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 0 H48 L66 18 V84 H0 Z" fill="{color}" stroke="#566673" stroke-width="2"/><path d="M48 0 V18 H66 M12 34 H52 M12 48 H52 M12 62 H43" fill="none" stroke="#566673" stroke-width="2"/></g>')
def formula(x,y):
 s.append(f'<text x="{x}" y="{y}" class="math" text-anchor="middle">U<tspan baseline-shift="sub" font-size="24">it</tspan><tspan> = B</tspan><tspan baseline-shift="sub" font-size="24">i</tspan><tspan> + R</tspan><tspan baseline-shift="sub" font-size="24">it</tspan><tspan>(D</tspan><tspan baseline-shift="sub" font-size="24">it</tspan><tspan> − B</tspan><tspan baseline-shift="sub" font-size="24">i</tspan><tspan>)</tspan></text>')
# 新增图标仅提示研究情境，不作为模型变量或结果。
def candle(x,y,scale=1):
 s.append(f'<g class="mourning-decoration" transform="translate({x} {y}) scale({scale})" aria-label="Memorial candle illustration"><ellipse cx="0" cy="82" rx="29" ry="6" fill="#D8DCE0"/><rect x="-16" y="4" width="32" height="72" rx="5" fill="#FFFCF1" stroke="#7A8289" stroke-width="2.5"/><path d="M-8 6 V66 Q-8 73 1 73" fill="none" stroke="#E8DED0" stroke-width="7"/><path d="M-15 10 Q-5 17 1 10 Q9 5 15 11" fill="none" stroke="#B5B7B0" stroke-width="2"/><path d="M0 4 V-6" stroke="#5F5B55" stroke-width="2.5"/><path d="M0 -7 C-23 -19 -6 -35 -1 -43 C12 -29 20 -15 0 -7 Z" fill="#F4B86B" stroke="#D99A56" stroke-width="1.8"/><path d="M0 -10 C-8 -17 -1 -25 1 -28 C8 -20 8 -14 0 -10 Z" fill="#FFE4A0"/></g>')
def white_flower(x,y,scale=1,tilt=0):
 s.append(f'<g class="mourning-decoration" transform="translate({x} {y}) rotate({tilt}) scale({scale})" aria-label="White memorial flower illustration"><path d="M0 0 Q-8 27 4 63" fill="none" stroke="#86A194" stroke-width="3"/><path d="M0 35 Q-28 16 -19 43 Q-8 48 0 41 M1 48 Q23 27 24 46 Q15 58 1 53" fill="#B7CBBD" stroke="#86A194" stroke-width="1.5"/>')
 for angle in range(0,360,45):
  s.append(f'<ellipse cx="0" cy="-12" rx="7" ry="14" transform="rotate({angle})" fill="#FFFEF8" stroke="#A4ACA6" stroke-width="1.5"/>')
 s.append('<circle r="7" fill="#E5CF94" stroke="#AB9B74" stroke-width="1.5"/></g>')

# 顶部：经验研究与仿真输入分开呈现；作者类型固定。
box('empirical-and-inputs',120,30,1260,230,'#FADDE2','#EFB6C1',26,'15 10',3)
text(750,78,'Empirical Grounding & Simulation Inputs','top','middle')
# 独立小插画与Digital mourning标签只标记研究主题，不添加输入箭头。
candle(233,135,0.80)
white_flower(185,157,0.64,-19)
white_flower(281,159,0.62,17)
text(232,237,'Digital mourning','tiny','middle')
box('empirical-corpus',350,105,450,130,'#FFF7F8','#ECC7CD',9)
text(371,138,'Empirical content analysis','head')
lines(371,175,['49,930 posts · Douyin & Xiaohongshu','Temporal and platform patterns'],'tiny',34)
box('frozen-inputs',825,105,530,130,'#FFF7F8','#ECC7CD',9)
text(846,138,'Frozen simulation inputs','head')
lines(846,173,['Separately frozen external samples','Time-stamped; shared across regimes','within each seed'],'tiny',27)
box('fixed-profile',1420,30,1050,230,'#FFE9D0','#C6A575',26,'15 10',3)
text(1945,78,'Fixed Agent Population & Individual Profiles','top','middle')
profiles=[(1535,'Marketing','23','#EBA96B'),(1740,'Mourning','22','#91B4D6'),(1945,'Other discussion','21','#A9B6B1'),(2150,'Meme-oriented','19','#B9A4D1'),(2355,'Educational','15','#88B7A4')]
for x,label,n,c in profiles:
 avatar(x,112,c,0.60)
 if label == 'Mourning':
  candle(x+39,118,0.28)
 text(x,180,label,'tiny','middle')
 text(x,210,f'{n} agents','tiny','middle')
text(1945,244,'100 agents · fixed types and counts · fixed individual thresholds','small','middle')
# 主体四列，直接取自正文机制，不复制参考图的心理状态更新。
cols=[('curation',50,475,'#DDEAF8','#92A3B1','Curation & Exposure'),('components',565,600,'#E5F2DB','#A5B99B','Expression Components'),('decision',1205,545,'#FFF4CB','#E2C65A','Threshold Decision'),('generation',1790,680,'#FFE7D7','#F0B58E','Post Generation')]
for id,x,w,fill,stroke,title in cols:
 box('panel-'+id,x,300,w,820,fill,stroke,0,sw=3.5)
 text(x+w/2,350,title,'column','middle')
# 输入线指向模块边界，不穿过标题或误指作者类型。
path('M1020 260 V280 H287 V296')
path('M1477 260 V296')
path('M2130 260 V296')
# 一、候选池和个人接触。
box('candidate-pool',75,385,425,175,'#FFFFFF','#92A3B1',17)
text(287,424,'Regime-specific','head','middle')
text(287,459,'candidate pool','head','middle')
document(101,483,'#D5E4F5',0.63);document(133,491,'#F5E4CB',0.57)
lines(192,501,['Eligible external posts','and generated posts'],'tiny',30)
path('M287 560 V636')
box('personal-feed',75,640,425,210,'#FFFFFF','#92A3B1',17)
text(287,682,'Personal information feed','head','middle')
# 文件小图标只示意内容槽位，不暗示样本数量或真实结果。
for x,c in [(119,'#D6E6F5'),(191,'#E6EFD9'),(263,'#F5E0CB'),(335,'#ECE1F1')]:document(x,710,c,0.80)
# 仅一张示意帖带悼念标记，其余帖子保留异质性。
s.append('<rect x="198" y="729" width="39" height="40" fill="#E6EFD9"/>')
candle(217,741,0.30)
text(287,807,'Up to 10 posts per action','small','middle')
box('curation-regimes',75,905,425,180,'#FFFFFF','#92A3B1',12)
text(287,945,'Curation regimes','head','middle')
lines(287,986,['Random · Chronological','Interest-based'],'small',34,'middle')
text(287,1060,'Selection, retention and recirculation','tiny muted','middle')
# 二、B/D/R是操作化的表达组件。
box('baseline',590,385,550,150,'#FFFFFF','#A5B99B',0)
text(615,425,'B · Baseline expression utility','head')
lines(615,468,['Usual expression level calibrated','from pre-event content supply.'],'small',33)
box('climate',590,565,550,180,'#FFFFFF','#A5B99B',0)
text(615,607,'D · Opinion-climate response','head')
lines(615,650,['Current same-type content share','relative to the type’s population share.'],'small',34)
text(615,718,'Bounded nonlinear response','tiny muted')
box('prior-history-weight',590,775,550,210,'#FFFFFF','#A5B99B',0)
text(615,818,'R · Exposure-dependent weight','head')
lines(615,862,['Based on prior cumulative contact','with same-type content.'],'small',34)
text(615,950,'Declines as cumulative exposure increases.','tiny muted')
# 当前接触进入D；历史更新独立于是否发帖，供未来行动使用。
path('M500 655 H586')
path('M500 830 H545 V1094 H1120 V989','state','10 7',3)
lines(590,1042,['Store current same-type exposure','for subsequent turns'],'small',33)
# 组件汇集到公式，细线区别于主流程。
rule('M1140 460 H1152 V885 H1140','#65785F',2.5)
rule('M1140 655 H1152','#65785F',2.5)
path('M1152 655 H1185 V495 H1226')
# 三、明确效用插值与阈值分支。
box('utility',1230,385,495,205,'#FFFFFF','#E2C65A',20)
text(1477,430,'Compute expression utility','head','middle')
formula(1477,494)
text(1477,548,'R → 0 ⇒ U → B','math','middle')
path('M1477 590 V636')
s.append('<polygon id="threshold-diamond" points="1477,640 1705,735 1477,830 1250,735" fill="#FFFFFF" stroke="#E2C65A" stroke-width="3.5"/>')
lines(1477,726,['Utility ≥ individual','threshold?'],'head',36,'middle')
path('M1705 735 H1811')
text(1746,716,'Yes','small','middle')
path('M1477 830 V925')
text(1496,890,'No','small')
box('no-post',1310,930,335,115,'#FFFFFF','#E2C65A',15)
text(1477,976,'No post this turn','head','middle')
text(1477,1015,'Next scheduled opportunity','tiny muted','middle')
text(1477,1092,'W12–W22 · one opportunity per agent/week','tiny','middle')
# 四、LLM只负责触发后的文本生成，不添加行动候选优化。
box('generation-context',1815,385,630,170,'#FFFFFF','#F0B58E',0)
text(2130,429,'Generation context','head','middle')
lines(2130,477,['Fixed persona + actual feed excerpts','Up to 5 excerpts; ≤120 characters each'],'small',36,'middle')
path('M2130 555 V611')
box('llm-generation',1815,615,630,180,'#FFFFFF','#F0B58E',0)
# 简单的生成器图标为自绘矢量，不代表具体模型品牌。
box('generator-icon',1841,653,87,91,'#FFF0E0','#DDA16F',15)
text(1884,708,'LLM','small','middle')
text(2160,674,'LLM text generation','head','middle')
lines(2160,720,['Generate text only after','the expression threshold is reached.'],'small',33,'middle')
path('M2130 795 V856')
box('new-post',1815,860,630,225,'#FFFFFF','#F0B58E',0)
avatar(1871,925,'#82B5C4',0.82)
document(1930,920,'#F8E1CC',0.75)
text(2180,912,'Successful publication','head','middle')
lines(2180,954,['New post enters the','regime-specific return process.'],'small',34,'middle')
rule('M1837 1017 H2423','#F0B58E',2)
text(2130,1056,'Track supply by fixed author type and later exposure','tiny','middle')
# 底部粉色回流带闭合内容循环，直指候选池，避开人设。
box('recirculation',565,1155,1185,160,'#FADDE2','#EFB6C1',27,'15 10',3)
text(1157,1198,'Content Re-circulation','top','middle')
text(1157,1243,'Chronological: after batch completion; visible to subsequent batches','small','middle')
text(1157,1281,'Random / Interest-based: eligible next week','small','middle')
path('M2130 1085 V1240 H1755')
text(1940,1215,'Published posts','head','middle')
path('M565 1240 H25 V475 H71')
text(275,1282,'Feedback to later feeds','head','middle')
# 研究比较与观测结果放在机制之外，避免混同心理或行为更新。
box('experiment-strip',50,1350,2420,100,'#F9FAF8','#C9CEC9',8)
rule('M855 1365 V1435','#C9CEC9',2);rule('M1650 1365 V1435','#C9CEC9',2)
text(75,1387,'Main experiment','head')
text(75,1425,'3 regimes × 3 seeds = 9 runs','small')
text(880,1387,'Interest-based ablations','head')
text(880,1425,'B = 0 · D = 1 · R = 1; 3 paired repeats each','small')
text(1675,1387,'Observed outcomes','head')
text(1675,1425,'Exposure · participation · supply · re-exposure','small')
text(1260,1487,'Ablations reuse the full-model reference; separate batches used different generation-service configurations.','tiny muted','middle')
s.append('</svg>')
(P/'framework_pastel_mourning_en_v1.svg').write_text('\n'.join(s))
print(P/'framework_pastel_mourning_en_v1.svg')
