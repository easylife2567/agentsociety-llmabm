# 第四章章首与（一）定稿及写作依据

作者于2026-10-16确认采用已讨论版本，授权将第四章章首与（一）“模型与实验设计”保存到[正式主稿](../../../paper/manuscript/manuscript.accepted.md)，同时保存逐句链和写法说明。本文件保存该范围的中英文定稿及论证依据。表1仅留占位，完整拟定内容保存在本文件；（二）及后续小节继续在聊天中讨论，尚未采用。

## 整章论证链与小节安排

第三章识别共同的表达顺序和不同的平台轨迹 → 在固定人口、行为参数与配对外部输入下连接可见性、表达和回流 → 比较三种策展制度下的供给轨迹 → 追踪个人接触、群体参与与生成帖再流通 → 用B、D、R消融检验表达机制各组成项的作用 → 综合制度与表达机制如何共同形成表征变化。

中文章名为“四、传播反馈机制与策展制度比较”。全章计划共12段，正文约1,800—2,100英文词，按论证需要调整。以下结构是后续写作安排，除本文件明确采用的章首及（一）外，不表示其他小节已经定稿。

| 位置 | 段落与职责 | 图表安排 |
|---|---|---|
| 章首 | 1段，从第三章的内容构成与时序进入传播过程 | 无 |
| （一）模型与实验设计 | 3段，交代用户与环境、表达规则及来源、制度与消融比较 | 表1，制度规则 |
| （二）不同策展制度下的表征演化 | 2段，先比较轨迹，再比较晚期数量与份额 | 图3，占位 |
| （三）可见性配置、表达参与与内容回流 | 3段，沿个人接触、表达选择和生成帖再流通展开 | 图4，占位 |
| （四）表达机制的消融检验 | 2段，凝练B、D、R的不同作用及闭环边界 | 图5，占位 |
| 章末 | 1段，综合制度与表达机制，交接讨论 | 无 |

## 章首总述

### 逐句链

1. **承接研究对象**：从第三章观察的内容构成，转向表达在后续传播中的延续和变化。
2. **引入模型任务**：将个人接触、表达参与与内容回流连接起来，考察共同外部输入在不同制度下的传播过程。

### English draft

How the deceased is represented involves both the composition of content at a given time and the continuation and transformation of expression through subsequent communication. Building on the temporal patterns identified in Chapter 3, the simulation links individual exposure, participation, and content recirculation to examine how shared external inputs develop through different curation regimes.

### 中文对照

逝者被如何呈现，既涉及某一时点的内容构成，也涉及表达如何在后续传播中延续和变化。在第三章所识别的时序特征基础上，仿真将个人接触、表达参与和内容回流连接起来，考察共同外部信息在不同策展制度下展开的传播过程。

### 写法说明

首句延续第三章的研究对象，第二句说明本章具体考察的传播过程，不另写“为何结合现实分析与仿真”的说明段，也不在章首预告制度比较结论。个人接触、表达参与和内容回流沿用第二章的理论链条，随后由（一）落实为可运行的模型。

## （一）模型与实验设计

## 第一段：用户类型与模拟环境

### 逐句链

1. **划分理由与人口构成**：以内容分析识别的表达活动为依据，设置五种作者类型，表现不同表达活动之间的传播竞争。
2. **人数依据**：按W12—W22单一类别作者的构成，换算为100人规模。
3. **固定类型的作用**：观察既有群体参与程度的变化，不将模型条件解释为真实用户永久不变的身份。
4. **时间与机会**：交代11周窗口及每人每周一次表达机会。
5. **外部输入规模**：250条为整个窗口每次重复使用的总量。
6. **输入来源**：如实说明最新冻结仿真输入中的三个来源。
7. **信息时钟与接触**：帖文按时间戳取得资格，在个人行动时点形成最多10条的信息流。

### English draft

To represent competition among the forms of expression identified in the content analysis, the model comprised 100 agents across five fixed author types, with 23 marketing, 22 mourning, 21 other-discussion, 19 memetic, and 15 education agents. Their numbers were scaled from the proportions of authors whose observed posts fell within a single category during W12–W22. Types remained fixed to examine changes in participation among established groups. The simulation covered W12–W22, with one expression opportunity per agent each week. Each replicate used 250 external posts across the entire window. These frozen inputs included material from Douyin, Xiaohongshu, and Weibo. External posts became eligible according to their timestamps, and each agent received a feed of up to ten eligible posts at its scheduled opportunity.

### 中文对照

为表现内容分析中不同表达活动之间的传播竞争，模型设置100名智能体，分属五种固定作者类型，包括营销型23人、悼念型22人、其他讨论型21人、玩梗型19人和教育型15人。各类型人数参照W12—W22期间所发帖文均属于单一类别的作者构成，换算至100人规模。模拟期间类型保持固定，以考察既有群体的表达参与如何变化。仿真覆盖W12—W22，每名智能体每周获得一次表达机会。每次重复使用整个窗口内250条外部帖文。这些冻结输入包含抖音、小红书和微博的材料。外部帖子依据时间戳取得展示资格，每名智能体在预定行动时点获得最多10条可用帖文的信息流。

### 写法说明

前两句补上类型划分与人数构成的依据，把第二章的内容分类转为参与群体设定。固定类型用于识别群体参与的变化，不能据此声称真实用户不会转换表达方式。数量依据来自完整观察窗口，不称为仅凭事件前资料初始化。

按作者批注删除正文中“17条历史帖初始化内容池”的具体数量。该输入仍属于实际配置，没有删除或改动；来源、类型构成与对初始条件的影响留待补充材料交代。250条指整个窗口，不是每周250条。真实分析采用两平台；本段如实记录已运行timestamp冻结输入仍含微博的事实，二者来源范围不同，不能把此差别隐去或据此重新解释第三章。

## 第二段：表达规则、公式来源与正文生成

### 逐句链

1. **核心规则**：以表达效用公式说明每次行动是否发帖。
2. **变量意义**：分别解释常态效用、信息流响应与累计同类接触衰减。
3. **表达门槛**：说明效用达到固定个人门槛才发帖。
4. **D的公式来源**：借鉴计算表达模型的有界非线性响应形式，改为对个人信息流相对人口份额偏离的响应。
5. **R的公式来源**：借鉴注意力衰减模型，采用累计同类接触的单指数函数。
6. **标定时段**：区分B的W05—W12供给及W13换算尺度，与响应和衰减的W13—W18调整。
7. **共同参数**：三种主制度共用行为参数。
8. **正文生成**：决定发帖后，DeepseekV4.1依据人设与实际可见摘录生成文本。
9. **回到循环**：成功发帖进入后续制度化流通。

### English draft

At each opportunity, the decision to post was governed by expression utility,

\[
U_{it}=B_i+R_{it}(D_{it}-B_i).
\]

Here, \(B_i\) represented baseline expression utility, \(D_{it}\) the response to the proportion of same-type content in the personal feed, and \(R_{it}\) a weight that declined with prior cumulative same-type exposure. An agent posted when utility reached its fixed individual threshold. D adapted bounded nonlinear response forms from computational models of opinion expression to the deviation of same-type feed share from population share ([Sohn & Geidner, 2016](https://doi.org/10.1093/ijpor/edv005); [Cabrera et al., 2021](https://link.springer.com/article/10.1007/s11573-021-01064-7)). R drew on attention-decay models and used a single-exponential function of cumulative same-type exposure ([Wu & Huberman, 2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC2077036/); [Candia et al., 2019](https://www.nature.com/articles/s41562-018-0474-5)). Baseline utility was calibrated from W05–W12 supply using a W13 scaling reference, while response and decay parameters were adjusted using W13–W18 patterns. These parameters were shared across the three main curation regimes. After a decision to post, DeepseekV4.1 generated text from the persona and excerpts from up to five posts in the actual feed. Published text then entered subsequent circulation under the relevant regime.

### 中文对照

每次行动是否发帖由表达效用决定：

\[
U_{it}=B_i+R_{it}(D_{it}-B_i).
\]

其中，\(B_i\)表示常态表达效用，\(D_{it}\)表示个人信息流中同类内容比例引起的响应，\(R_{it}\)则是随此前累计同类接触增加而降低的权重。效用达到固定的个人门槛时，智能体发帖。D参照既有计算表达模型中的有界非线性响应形式，将个人信息流中同类内容比例相对该类型人口份额的偏离映射为表达响应（Sohn与Geidner，2016；Cabrera等，2021）。R借鉴注意力衰减模型，以累计同类接触为自变量，采用单指数形式描述衰减（Wu与Huberman，2007；Candia等，2019）。常态表达效用依据W05—W12的供给、结合W13的共同尺度换算，响应与衰减参数则依据W13—W18的变化调整。三种主策展制度共用这些参数。决定发帖后，DeepseekV4.1依据人设及实际信息流中最多五条帖文的摘录生成正文。成功发布的内容随后按相应制度进入后续流通。

### 写法说明

正文只保留组合公式U及各项的传播含义，同时用两句交代函数来源与适配，避免将经典理论文献直接写成当前公式的出处。D借鉴有界响应形式，当前实现采用tanh，输入是个人同类份额相对人口份额的偏离，不能称为原文公式的直接复用。R借鉴注意力衰减函数，但Wu与Huberman的伸展指数、Candia等的双指数与本模型基于累计同类曝光的单指数并非相同方程。完整函数、变量映射、系数及参数标定过程留补充材料。Sohn与Geidner采用卷期正式年份2016，PARAMETERS中的2015为线上发表年份口径。

标定措辞明确B还使用W13尺度，不将其包装为独立事件前估计；当前timestamp沿用既有行为参数，没有为本轮新结果重新标定。文献链接已在前一轮讨论中按原始论文核对，正式稿使用md1、md2两项新增脚注，并复用已有26、27两项。

按作者要求，正文以DeepseekV4.1称呼生成模型；实际冻结模型标识为`deepseek-v4-1-flash-260910`，精确标识、服务参数、提示与修复路径须保留在补充材料。LLM在达到表达门槛后生成正文，不决定U或是否发帖。

## 第三段：制度比较、消融与测量安排

### 逐句链

1. **制度比较**：引入随机、时序与兴趣制度，具体规则交给表1。
2. **配对设计**：固定人口、行动表和行为参数，同一seed共用外部样本，形成九次运行。
3. **消融设计**：在兴趣制度内分别设B=0、D=1、R=1，各三次配对重复，复用完整模型参照。
4. **测量对象**：区分固定作者类型的发帖供给、表达参与和后续接触。
5. **时间窗口**：主结果晚期W19—W22，R检验采用W14—W18退潮窗口。
6. **汇总口径**：先在run内计算，再汇总三次重复。

### English draft

The main experiment compared random, chronological, and interest-based curation, with content selection, retention, and recirculation rules specified in Table 1. The population, action schedule, and behavioral parameters were held fixed, and each of three seeds paired the same external sample across regimes, yielding nine runs. Component tests under interest-based curation additionally set \(B=0\), \(D=1\), or \(R=1\), with three paired replicates per condition and the existing full-model interest runs serving as references. Analyses tracked publication counts and shares by fixed author type, participation rates, and subsequent exposure. The main late-period comparison used W19–W22, while the R test assessed post-event decline over W14–W18. Metrics were calculated within each run before being summarized across the three replicates.

### 中文对照

主实验比较随机、时序和兴趣三种策展制度，其内容选择、保留与回流规则见表1。人口、行动表和行为参数保持固定，每个随机种子下三种制度使用相同外部样本，三个种子共形成九次运行。兴趣制度内另分别设置\(B=0\)、\(D=1\)或\(R=1\)，每个条件进行三次配对重复，并复用已有的兴趣制度完整模型作为参照。分析追踪按固定作者类型统计的发帖数量与份额、表达参与率及后续接触情况。主结果的晚期比较采用W19—W22，R的检验则考察W14—W18的事件后退潮。各项指标先在每次运行内计算，再汇总三次重复。

### 写法说明

本段把主制度比较和表达机制消融放进同一设计，只说明如何比较，结果留到后文。三个seed配对外部抽样与行动表，不等于三个人口独立抽样。B=0与D=1、R=1分别采用实际消融设定，不能笼统写成所有因子都设为零。

指标明确按固定作者类型统计供给，不将其等同于生成正文的独立语义分类；曝光、回流与供给另有各自分母。三种制度同时保留候选池、旧帖处理、保底和回流差异，比较的是完整制度。正文不将制度分别对应到实际商业平台。消融在不同批次执行的API差异、n=3及闭环总效应边界在（四）和补充材料说明。

### 表1占位与拟定内容

> 【表1表位预留，待统一制作】

**表1　三种策展制度的内容组织规则**

| 制度 | 内容选择与旧帖处理 | 生成帖再次展示 |
|---|---|---|
| 随机 | 从已到达的全部历史内容中等概率抽取，旧帖持续保有展示机会 | 次周取得资格 |
| 时序 | 选择行动时点之前最新发布的内容，旧帖可能被新帖挤出展示位置 | 同批结束入池，后续行动批次可见 |
| 兴趣 | 结合类型匹配、内容老化与曝光饱和进行比例抽样，过旧内容退出候选池 | 次周取得资格 |

注：兴趣制度在事件周为其他悼念相关内容保留最多五条优先展示位置；官方讣告按普通推荐处理，不置顶、不参与保底。制度比较包含旧帖处理和回流安排，不分别对应具体商业平台。正式主稿仅保留表位与表题，本表为后续统一制作依据。

## 来源、引用与采用边界

- 模型及冻结设计见[experiment_2设计](../../../hypothesis_4/experiment_2/EXPERIMENT.md)、[配置入口](../../../hypothesis_4/experiment_2/init/README.md)及[PARAMETERS](../../../PARAMETERS.md)的U与行为参数部分。PARAMETERS中旧时钟、旧状态及旧实验结果不作为timestamp结果。
- 正式LLM消融见[experiment_3](../../../hypothesis_4/experiment_3/README.md)；不沿用旧100-seed数值代理结果充当本章证据。
- D的计算参考为Sohn与Geidner（2016），DOI `10.1093/ijpor/edv005`；Cabrera等（2021），DOI `10.1007/s11573-021-01064-7`。R参考为Wu与Huberman（2007），DOI `10.1073/pnas.0704916104`；Candia等（2019），DOI `10.1038/s41562-018-0474-5`。具体借鉴与适配范围已在第二段说明。
- 本次采用前完整主稿保存在[快照](inputs/manuscript.before_chapter_4_1.md)，SHA256为`e8dbe836d0e18d8036bd54d29b28857a4475b01d306090aa9888821dfe2bc516`，保留旧章首、旧（一）、旧图3及旧结果，不改写历史证据。
- 正式稿仅替换第四章章名、章首和（一），增添表1占位及必要引用、版本说明。旧（二）（三）和第五章保持待重写身份。图3拟由下一节讨论确定，本次不绘制或复用旧图。
- 本次为文稿采用，没有运行仿真、调用分类、修改配置、更新研究阶段、commit、push或归档。
