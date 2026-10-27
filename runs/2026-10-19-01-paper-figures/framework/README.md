# 整体研究框架图

| 文件 | 用途 |
|---|---|
| [fusion/](fusion/README.md) | 当前融合第二版：ProAgent机制细节×环形设计，约三七开互补研究、独立圆环端口与外侧回流、增强局部配色及白菊花束/缎带/蜡烛；英文长横SVG/PNG/源码/灰度与本地draw.io可编辑版；第一版保留 |
| [divergent/](divergent/README.md) | 前轮三种不同视觉语言：报刊地图、圆环机制、流动带状；用户已明确偏好圆环，重点收敛为白底、黑灰字和少量蓝/朱红线条，含SVG/PNG/源码/灰度校样 |
| [complementary/](complementary/README.md) | 前轮三种互补研究长横版：30:70左右联动、40:60双研究带、35:65机制闭环；鲜明配色，不展示两平台各自比例，含SVG/PNG/源码/校样 |
| [alternatives/](alternatives/README.md) | 前轮四种跨双栏长横版候选：A紧凑流程/B横向回路/C泳道/D黑白研究地图；180×63.75mm、SVG/PNG、拼版及源码 |
| [framework_pastel_mourning_en_v1.svg](framework_pastel_mourning_en_v1.svg) | 此前英文候选：四阶段浅色版增加蜡烛、白花与悼念徽记，保留机制与数字；2520×1510，原生可编辑 |
| [framework_pastel_mourning_en_v1.png](framework_pastel_mourning_en_v1.png) | 悼念元素版预览 |
| [draw_framework_pastel_mourning_en.py](draw_framework_pastel_mourning_en.py) | 悼念元素版独立生成脚本，不覆盖无装饰版本 |
| [framework_pastel_en_v1.svg](framework_pastel_en_v1.svg) | 四阶段浅色英文候选，2520×1510；顶部输入/人设、四阶段浅色分区、底部回流带；原生可编辑 |
| [framework_pastel_en_v1.png](framework_pastel_en_v1.png) | 新风格预览 |
| [draw_framework_pastel_en.py](draw_framework_pastel_en.py) | 新风格独立生成脚本，不覆盖既有版本 |
| [framework_proagent_en_v2.svg](framework_proagent_en_v2.svg) | ProAgent风格英文第二版，2100×1250；数据入口分离，含效用公式、回流资格、生成上下文及消融限制 |
| [framework_proagent_en_v2.png](framework_proagent_en_v2.png) | 第二版预览 |
| [draw_framework_en_v2.py](draw_framework_en_v2.py) | 第二版独立生成脚本，保留第一版不覆盖 |
| [framework_proagent_en_v1.svg](framework_proagent_en_v1.svg) | 用户指定ProAgent风格的英文版，2100×1120；原生可编辑矢量与英文文字 |
| [framework_proagent_en_v1.png](framework_proagent_en_v1.png) | 英文版预览 |
| [draw_framework_en.py](draw_framework_en.py) | 英文版独立标准库生成脚本，无额外依赖 |
| [framework_v1.svg](framework_v1.svg) | 中文可编辑初版，1800×1060；原生文字、矩形、路径与箭头，无嵌入位图 |
| [framework_v1.png](framework_v1.png) | 同尺寸预览 |
| [draw_framework.py](draw_framework.py) | 标准库SVG生成脚本；在本目录输出上述SVG |

依据：用户确认的ICA2027v1.docx冻结副本及正文提取文本。采用现实经验识别、仿真反馈循环、实验与观测三分区；框架覆盖原图1—5所支撑的研究分工，不提前改变正文图号。

版式参考及论文来源见[参考图索引](../references/README.md)。仅借鉴布局规律，所有框架内容按当前正文重新组织。

内容边界：现实数据两平台49930条；模型100人、W12—W22、固定类型；主实验3制度×3seed；兴趣制度内B=0、D=1、R=1分别3次配对。候选池为各制度内部，不表示三制度有相同候选池；只共用外部输入。初版中R采用累计接触衰减的简写，未写出效用公式；第二版已直接读取原Word数学对象，按原式补入公式。仿真结果按固定作者类型解释，不画成态度转变。

验证：SVG经XML解析；未含image元素或外部资源；PNG通过sharp渲染并人工查看整体布局。字体使用系统中文字体栈，跨机器打开时字体可能替换；为保持文字可编辑，没有转为轮廓。初版尚待作者审阅，未作为投稿终稿验收，未写入正式paper或Word。

## ProAgent风格英文第一版

2026-10-19用户指定proagent.jpg为主要风格模板，新增英文候选而非直译旧三栏版。采用左侧紧凑总览、虚线放大连接、右侧浅灰圆角机制框、Times New Roman衬线字体、灰蓝输入块、橙色表达判定、绿色文本生成器及黄色接触历史。红色内容回流箭头将生成帖连接回各制度候选池，再进入个人信息流。角色图标和帖文示意均为自绘矢量，无上游图片或品牌标志嵌入。

英文B/D/R分别为Baseline expression utility、Opinion-climate response、Exposure-dependent decay。R箭头从累计同类接触历史进入表达规则；文本生成只在达到固定门槛之后发生。未添加真实数据或实验中不存在的轨迹线。未在左侧添加“发帖判定→B/D/R”独立反馈路径。机制语义经只读辅助核对；固定类型为独立人设输入，信息流不指向作者类型；历史条标为Prior exposure history，当前接触存入后续回合。未修改论文或实验。

可选图注：**Research framework for curation–expression feedback in postmortem representation.** (a) Empirical content analysis informs a model with a fixed population of 100 agents. (b) Regime-specific curation shapes personal exposure; expression is activated when utility reaches the individual threshold. The LLM then generates a post from the agent persona and current feed. Eligible posts re-enter the candidate pool under each regime’s return rules, while cumulative same-type exposure updates the history used by R. Controlled comparisons track exposure, participation, re-exposure, and supply by fixed author type.

验证：XML有效、ID唯一、无嵌入位图；PNG渲染并查看。冻结Word指纹未变。源文件保留可编辑文本，换机如缺Times New Roman会替代字体；SVG仍为待作者审阅候选。

## 英文第二版与正文逐项复核

用户接受事实核查后的修改方案，本版保留第一版、ProAgent版式及正式Word。只新增第二版SVG、PNG及独立生成脚本，不更改原论文、实验或数据。

| 第二版内容 | 原Word依据与检查结论 |
|---|---|
| 两平台49,930条现实语料，与Frozen simulation inputs分开；左侧过渡为Mechanism investigation | 二（二）给出现实语料范围。四（一）称仿真来自两平台，但五（四）称另行冻结三平台输入，正文存在未统一口径。本图不指定仿真平台数或声称全量49,930条进入仿真；不把图示修订当作正文冲突已解决 |
| U_it = B_i + R_it(D_it − B_i)，Utility ≥ individual threshold | 直接解析Word数学对象，核对所有下标与运算符；保留先判定后生成的顺序 |
| R为Exposure-dependent weight；R → 0 ⇒ U → B | 对应四（一）的累计同类接触衰减及原公式；不声称接触增加时效用必然下降，不把R写成纯日历时间衰减 |
| 时序：批次完成后、后续批次可见；随机/兴趣：次周取得资格 | 按表1写明资格与时机，不画作所有制度都立即回流 |
| 个人feed最多10条；文本生成仅取最多5条摘录、每条最多120字符 | 对应四（一），将表达判定的信息流与文本生成上下文分开 |
| 3制度×3种子；消融各3次，复用兴趣完整模型作参照；分批、生成配置不同 | 对应四（一）与五（四）；未新增论文未明确说明的严格配对维度或同期同服务承诺 |
| 固定作者类型的供给与展示 | 不把固定作者类型供给等同于生成文本独立语义分类或个人态度变化 |

验证结果：当前原Word与run冻结副本SHA256一致；SVG XML有效、ID唯一、71个原生文字对象、无嵌入位图；已用sharp渲染并查看PNG，移开R箭头避免穿过No post框。只读辅助复核了原Word数学、表1与局限，未发现第二版与所核对正文的事实冲突或修订遗漏；未执行实验或重新核实原始研究结果。源SVG保留字体、文字、图形和箭头可编辑性。

建议英文图注：**Research framework for curation–expression feedback in postmortem representation.** (a) Empirical characterization motivates mechanism investigation with a fixed population of 100 agents. (b) Separately frozen, time-stamped external samples enter regime-specific candidate pools. Personal exposure and prior same-type exposure history shape threshold-based expression utility, U_it = B_i + R_it(D_it − B_i). When the threshold is reached, the LLM generates a post using the agent persona and up to five feed excerpts of at most 120 characters each. Successfully published posts become eligible for subsequent display according to the regime-specific rules. The main experiment compares three regimes across three seeds. Each interest-based ablation has three paired repeats and reuses the existing full model as its reference. Full-model and ablation runs were conducted in separate batches with different generation-service configurations.

## 用户附件风格的四阶段英文候选

按用户新指定附件制作独立候选，保留ProAgent各版本。新参考见[用户浅色模板](../references/user_pastel_template.png)：采用粉色/米色虚线顶栏、蓝/绿/黄/橙四个机制区、白色子卡片、黑色主流程与粉色底部回流带。自绘人物与帖文图标为可编辑矢量，不添加参考图的心理更新或行动优化机制。

事实内容与正文对应：

- 顶部将现实内容分析与另行冻结的仿真输入分框；不写正文尚有两平台/三平台冲突的仿真平台数。现实49,930条两平台口径保持。
- 固定作者类型和人数：营销23、悼念22、其他21、玩梗19、教育15，总计100人；固定个体阈值。
- Curation & Exposure：各制度候选池形成每次最多10条个人feed；三种制度包含内容选择、保留和回流安排。
- Expression Components：B为事件前常态表达效用，D为当次同类内容份额相对人口份额的响应，R取此前累计同类接触形成的衰减权重。绿色虚线单独从当次feed更新历史，标为后续回合使用，与是否发帖无关。
- Threshold Decision：完整保留U_it = B_i + R_it(D_it − B_i)，及R → 0 ⇒ U → B；达到个体门槛才进入文本生成，未达则本次不发帖。
- Post Generation：人设加实际feed最多5条摘录、每条最多120字符；成功发布后按制度回流。没有虚构的真实帖例句、生成结果或统计曲线。
- 内容回流底带按表1区分时序的同批结束后入池、后续批次可见，以及随机/兴趣次周取得资格；主反馈回到候选池，不回到作者类型。
- 主实验3制度×3种子，三组件干预各3次配对；复用完整模型参照以及分批、生成服务配置差异仍在图中保留。

核查：直接读取当前原Word（含数学对象），指纹与run冻结副本一致；公式与SVG相符；XML解析、唯一ID检查通过，79个原生文字对象，无嵌入图片。PNG已渲染并查看；只读辅助审查未发现与正文、公式或表1的实质事实冲突。未运行实验、未改正式论文与研究资产、未提交Git。字体采用Arial/Helvetica，异机若缺字体可能替换；该候选仍待作者审阅。

英文图注候选：**Research framework for curation, selective expression, and post recirculation.** Separately frozen inputs enter regime-specific candidate pools and form personal feeds. Baseline expression utility (B), opinion-climate response (D), and prior-exposure weight (R) determine expression utility. Posts are generated only when utility reaches the fixed individual threshold, using the agent persona and at most five feed excerpts. Successful posts return under regime-specific eligibility rules. Current exposure updates the history used in subsequent actions. Agent types and population counts remain fixed throughout. The main experiment compares three curation regimes across three seeds; interest-based component ablations reuse the existing full-model reference. Full-model and ablation batches used different generation-service configurations.

## 悼念情境元素版

按用户要求，在四阶段浅色英文图上增加三处原生矢量插画：顶部Digital mourning小情境中为蜡烛与白花，Mourning作者旁为小蜡烛徽记，个人feed中的一张示意帖为蜡烛标记；其他作者与帖文保留异质性，全部生成帖未被统一标作悼念。图标不作为新增变量、额外情绪机制或实验结果，也不表示所有悼念型作者每次都会发帖。

为容纳顶部情境插画，现实语料与仿真输入两张卡片重新排版；49,930条两平台口径和“另行冻结、同seed内制度共用”的语义保持。主图数字、公式、B/D/R说明、生成上下文、资格时机、实验安排及生成配置差异均保持。

检查：机制箭头的全部marker-end路径与上一浅色版逐项一致；旧版文字仅顶部三条文案重排，其余全部保留；SVG XML有效、ID唯一、无嵌入位图；已渲染PNG并查看，文字及图标未见遮挡。当前原Word与冻结副本SHA256一致。仅新增run候选和所属索引，未修改正式论文、原始数据或已有图件版本，未commit。

英文图注可在上版末尾加：**Candle and flower icons indicate the digital-mourning context; schematic post icons do not represent observed samples or category proportions.**

## 前轮：四种跨双栏长横版

按用户此前五项要求及“长而矮、跨双栏”约束，新增[alternatives/](alternatives/README.md)四个英文候选；保留所有此前图件。四版统一180×63.75mm，蓝/橙职责配色与黑白背景，独立的内容/历史反馈，含蜡烛白花情境插画，短标签替代重复段落。图内文字较指定ProAgent第二版减少约36%—41%。尺寸、构图、配色依据、实际检查与共用英文图注均在子目录README，不在本级重复维护。

## 前轮：两项互补研究的三种新构图

新增[complementary/](complementary/README.md)，按用户最新配色、两模块面积与机制主线要求制作A/B/C三版；后续明确不突出两平台各自比例，三版均已去除平台分别的数量、占比与条形，仅将名称保留为来源。当前平台分析占30%、40%、35%，仿真相应占70%、60%、65%；共同解释独立汇合。原生SVG、长横PNG、实际比例、共用图注和事实检查见子目录。旧图件完整保留，未采用到正式论文。

## 前轮：差异化视觉语言与圆环配色收敛

新增[divergent/](divergent/README.md)三种不同视觉语言，保留双研究互补、约三七开、机制主线、悼念元素、英文长横版及无平台分别比例等约束。用户明确喜欢圆环形式，当前重点为白底圆环版：全部文字黑灰，蓝/朱红只用于少量路径，已完成灰度校样；报刊与带状作为并列探索保留。事实核查、共用图注及文件清单见子目录，正式论文仍未修改。

## 当前：ProAgent与圆环融合版

按用户要求新增[fusion/](fusion/README.md)，把ProAgent第二版的显式微流程、效用/阈值和生成限额纳入圆环主机制，保留约三七开的两项互补研究。增加局部配色模块与白菊花束、缎带、蜡烛情境图标；两平台不展示各自数量或比例。已完成彩色/灰度检查和正文定向复核，来源旧版均保留，尚未写入正式论文。

2026-10-23融合目录新增第二版，针对遮挡重排开口与回流通道，并增强局部标题和路径的对比。当前交付包含原生SVG及217对象的draw.io文件，已查看两种实际渲染；详情见所属目录，不覆盖第一版。
