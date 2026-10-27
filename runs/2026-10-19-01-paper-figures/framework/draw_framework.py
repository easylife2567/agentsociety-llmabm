"""绘制可编辑研究框架SVG；全部文字与形状保留为矢量对象。"""
from pathlib import Path
from html import escape
P=Path(__file__).parent
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1060" viewBox="0 0 1800 1060" role="img" aria-labelledby="title desc">', '<title id="title">算法策展与逝者数字表征：整体研究框架</title><desc id="desc">现实数据识别时序与平台差异，并为多智能体模型提供输入和参数参照。模型以可见性配置、选择性表达和内容回流构成反馈循环，通过三种策展制度和三种组件干预比较供给、参与及可见位置。</desc>', '''<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9" fill="none" stroke="#526477" stroke-width="1.6"/></marker></defs><style>text{font-family:"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif;fill:#243447}.h{font-size:24px;font-weight:600}.b{font-size:20px}.small{font-size:17px;fill:#566778}.label{font-size:17px;font-weight:600;letter-spacing:2px}</style>''']
def box(id,x,y,w,h,fill,stroke='#D6DEE7',r=14):
 s.append(f'<rect id="{id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
def text(x,y,t,cl='b',anchor='start',fill=None):
 s.append(f'<text x="{x}" y="{y}" class="{cl}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+escape(t)+'</text>')
def lines(x,y,ts,cl='b',step=31):
 for i,t in enumerate(ts):text(x,y+i*step,t,cl)
def path(d,dash=False):
 s.append(f'<path d="{d}" fill="none" stroke="#526477" stroke-width="2.3" marker-end="url(#arrow)"'+(' stroke-dasharray="7 6"' if dash else '')+'/>')
box('background',0,0,1800,1060,'#FFFFFF','#FFFFFF',0)
text(48,54,'算法策展如何重组逝者的公共表征', 'h')
text(48,87,'现实内容分析与大语言模型多智能体仿真相结合', 'small')
# 三个主分区
box('empirical-panel',40,118,350,805,'#F1F6FB','#CBDCEA')
box('simulation-panel',420,118,890,805,'#FAFBFC','#D6DEE7')
box('evaluation-panel',1340,118,420,805,'#F8F5FA','#DCD2E7')
text(64,157,'01  现实数据与经验识别','label',fill='#336C91')
text(445,157,'02  多智能体传播反馈模型','label',fill='#337B73')
text(1365,157,'03  实验比较与过程观测','label',fill='#785B95')
box('corpus',62,184,306,142,'#FFFFFF')
lines(82,219,['张雪峰相关帖文','抖音 × 小红书'],'h',34)
lines(82,285,['49,930 条｜2026年1—5月'],'small')
box('coding',62,350,306,170,'#FFFFFF')
text(82,386,'内容编码与周度聚合','h')
lines(82,423,['教育 · 悼念 · 玩梗','其他 · 营销；剔除噪音'])
text(82,493,'按平台、发布时间组织','small')
path('M215 326 V347')
box('observation',62,547,306,139,'#E4EEF8','#BDD2E5')
text(82,584,'经验识别  /  RQ1','h')
lines(82,623,['表达数量与构成的时序变化','两平台的共性与差异'],'b',29)
path('M215 520 V544')
box('empirical-inputs',62,716,306,177,'#FFFFFF')
text(82,753,'模型输入与参数参照','h')
lines(82,793,['外部帖文按时间到达','作者类型构成与常态供给','案例变化用于参数标定'],'b',32)
# simulation conditions
box('controls',445,184,840,102,'#EDF2F5')
text(465,218,'共同条件：100名智能体 · W12—W22 · 每周一次表达机会','b')
text(465,251,'固定作者类型与人数；同一种子下共用外部输入、行动表及行为参数','small')
box('pool',710,321,310,112,'#E4F2EF','#AFCFC8')
text(865,358,'制度内候选内容池','h','middle')
text(865,394,'已到达外部帖 ＋ 合资格生成帖','small','middle')
# stages horizontal 3 boxes
for id,x,fill in [('visibility',445,'#E5EFF9'),('expression',735,'#FFF1DC'),('return',1025,'#E5F2ED')]:box(id,x,510,260,235,fill)
text(465,550,'① 可见性配置','h')
lines(465,591,['按策展制度选择内容','形成个人信息流'])
text(465,712,'每次最多10条','small')
text(755,550,'② 选择性表达','h')
lines(755,590,['B  常态表达效用','D  意见气候响应','R  累计接触衰减'],'b',33)
text(755,712,'效用达到个体门槛才发帖','small')
text(1045,550,'③ 内容生成与回流','h')
lines(1045,591,['大模型依据人设与','当次所见内容生成帖文'])
text(1045,712,'按制度规定取得展示资格','small')
path('M705 626 H732');path('M995 626 H1022')
path('M710 377 H575 V506')
path('M1155 507 V377 H1024')
text(1164,454,'后续再分发','small')
path('M690 510 V466 H800 V506',True)
text(816,481,'个体接触历史','small')
# Input path routed bottom
path('M368 799 H430 V772 H720 V448 H741 V436',True)
text(451,816,'经验材料约束模型设定','small')
box('loop-interpretation',710,792,575,101,'#FFFFFF')
text(730,829,'循环生成公开表达的构成与可见位置','h')
text(730,866,'固定作者类型：供给重组不等同于个体态度转变','small')
# evaluation
box('regime-comparison',1362,184,376,205,'#FFFFFF')
text(1382,220,'制度比较  /  RQ2、RQ3','h')
for x,t,c in [(1381,'随机','#E8EEF5'),(1494,'时序','#E5EFF9'),(1607,'兴趣','#E5F2ED')]:
 box('regime-'+t,x,245,110,50,c);text(x+55,277,t,'b','middle')
lines(1382,330,['3种制度 × 3个种子＝9次运行','比较完整内容组织制度'],'small',30)
box('ablation',1362,414,376,205,'#FFFFFF')
text(1382,450,'表达组件干预  /  兴趣制度','h')
for x,t in [(1381,'B = 0'),(1494,'D = 1'),(1607,'R = 1')]:
 box('ablation-'+t,x,475,110,50,'#FFF1DC');text(x+55,507,t,'b','middle')
lines(1382,559,['各3次配对重复；复用完整模型参照','考察参与时机、持续性及闭环变化'],'small',30)
box('measures',1362,645,376,248,'#EEE8F4','#D1C1DF')
text(1382,682,'过程记录与宏观结果','h')
lines(1382,725,['个人：同类接触、表达参与','传播：生成帖的再次展示','群体：按固定作者类型的供给','整体：时序轨迹与晚期构成'],'b',34)
text(1382,871,'联结接触 → 参与 → 后续可见位置','small')
# cross panel output arrow
path('M1285 765 H1323 V769 H1358')
text(1235,787,'记录','small')
# synthesis bottom
box('synthesis',40,950,1720,77,'#243D50','#243D50')
text(900,982,'研究指向：在群体构成固定的条件下，可见性与表达参与的循环如何重组逝者数字表征','b','middle',fill='#FFFFFF')
text(900,1010,'现实分析识别变化格局；仿真提供机制参照与制度比较，不将模拟制度直接对应现实平台','small','middle',fill='#DCE7EF')
s.append('</svg>')
(P/'framework_v1.svg').write_text('\n'.join(s))
print(P/'framework_v1.svg')
