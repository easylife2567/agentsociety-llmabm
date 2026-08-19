# RQ Summary（v0.3）

## 研究问题

在张雪峰去世后，抖音平台的推荐机制如何参与关于他的碎片化叙事传播，并如何影响不了解他的用户对其形成单一化的、标签化的印象？

## 子问题

1. 现有研究如何描述公众人物死亡后，其既有自主表达、第三方再生产内容与平台分发之间的关系？
2. 推荐系统的哪些可观察过程可能影响去语境化片段的选择、重复曝光与可见性集中？
3. 重复接触少数片段与不了解该人物的受众形成单一化、标签化印象之间，已有何种理论与经验证据？
4. 哪些替代解释与研究设计可以区分算法放大、内容供给、用户选择、粉丝组织和新闻周期的作用？
5. 哪些理论、变量与经验规律可为后续基于 AgentSociety 的 LLMABM 提供可校准的机制假设？

## 子问题范围继承

五个子问题默认继承下述人物、平台、时间、地理与受众范围；文献可以跨人物类型和平台，用于提供理论、机制、测量或方法证据，不代表经验结论可以直接迁移至张雪峰案例。

## 初步 FINER 评估

| 维度 | 分数 | 依据与限制 |
|---|---:|---|
| Feasible | 6/10 | 文献调研可执行；但抖音内部排序数据不可直接获得，严格因果识别难度较高 |
| Interesting | 9/10 | 涉及数字死亡、平台治理、公共记忆与受众认知的交叉问题 |
| Novel | 8/10 | 张雪峰案例和中文短视频语境较新；需检索后才能判断理论新颖性 |
| Ethical | 8/10 | 可使用公开内容，但需处理逝者尊严、评论者隐私、误传与平台条款 |
| Relevant | 9/10 | 对平台推荐、数字遗产、公共人物形象和算法影响研究均有潜在意义 |
| **平均** | **8.0/10** | 无单项低于最低门槛；Novel 仍为检索前初评 |

## 检索后 FINER 更新（2026-08-19，基于 79 条 core 精读）

> 依据：CNKI 第一轮 1304 条分级（core 31 + prior core 48 = 79）+ 5 份子问题精读报告（papers/deep_read/rq1–rq5）。检索后判断详见下节「检索后可做性判断」，代表论文见附录 A。

| 维度 | 更新后 | 更新依据 |
|---|---:|---|
| Feasible | **7/10** | LLMABM 路径打通：RQ5 提炼 11 条可校准机制假设与 12 个参数（含取值范围）。但「抖音内部排序数据不可直接获得」未变，严格因果识别仍不可行，定位为机制探索+模拟 |
| Interesting | 9/10 | 维持 |
| Novel | **8.5/10** | 检索后确认：机制链完整整合（死亡×去语境化×重复曝光×低熟悉用户印象）无直接先例；「重复曝光→人物整体印象单一化」从未被直接测量；抖音死亡名人情境零证据 |
| Ethical | 8/10 | 维持 |
| Relevant | 9/10 | 维持 |
| **平均** | **8.3/10** | 单项全部≥7；Novel 由检索前初评转为检索后确认 |

### 检索后可做性判断

**结论：可做，且组合空间独特；但必须定位为「机制探索 + LLMABM 模拟」，而非「证明抖音算法造成单一化」。**

1. **别人已做的（机制链每个环节都有人做过，且质量不低）**：①名人死亡×社交媒体哀悼（**中-强**，多为案例/计算分析）：李文亮微博 134 万条评论计算分析、Jade Goody「天使」标签、袁隆平/金庸记忆书写、墨茶「悲情→道德评价转变」；②数字遗产/账号处置（**弱-中**）：悼念账号、委托人机制、封号治理（C4/C8/C15）；③推荐系统曝光机制（**强**）：TikTok 木偶审计、YouTube 四层推荐漂移、Twitter 放大比（Level II 随机实验）；④重复曝光→认知（**强**）：illusory truth 系列 Level II 实验（对数形重复效应、一致性框架竞争）；⑤去语境化/视觉误导（**中**）：切片判断研究、N=1,404 图文重配实验。
2. **没人做的（精确缺口）**：①完整链条整合无先例（RQ5 的 11 条假设均为「单环节证据+推断」拼接）；②「重复曝光→人物整体印象单一化」从未被直接测量（D 系列实验因变量全部止步于命题真实性）；③死后内容的平台排序曝光分配零直接证据；④中文短视频平台（抖音）死亡名人情境零证据；⑤低熟悉度用户亚群未被区分；⑥张雪峰案例（2026-03 去世）本身。
3. **机制链证据强度**（按 5 环节，评级见上表）：名人死亡×哀悼**中-强**（多为案例/计算分析）；数字遗产/账号处置**弱-中**（全链最弱）；推荐系统曝光机制**强**（Level II/III 齐备）；重复曝光→认知**强但结果变量是命题真实性而非人物印象**——「曝光→印象单一化」链节为[推断]，**中等偏弱**；去语境化/视觉误导**中**（本土直接证据 + Level II 议题依赖性警示）。
4. **两个必须诚实面对的前提**：
   - **算法放大只能是条件性假设**：B01 模拟（21,973 篇×7 种推荐逻辑）反证「算法必然收窄」，「单一化」更可能来自供给集中×排序强化×用户选择收敛的合谋（RQ4 结论），须用反事实对照设计（算法/时序/随机基线三条件）检验；
   - **断点校准需要补数据**：低熟悉用户对张雪峰切片的首印象实验 + 抖音「张雪峰相关」供给池对照抓取（RQ5 §5.2 四项中的 a/b），产出 β0、价性权重、log 系数 a、放大比 A。
5. **结论一句话**：现有文献像一盘散落的珠子（哀悼研究不知算法、审计研究不知死亡、认知实验不知人物印象），本 RQ 是把它们串成一条链的第一项研究——**若追求「证明算法导致单一化」则数据不可得；若检验「在什么条件下死后碎片化叙事让低熟悉用户形成单一化印象」则完全可行且填补空白**。

## 范围

### 纳入范围

- 主要经验案例：张雪峰于2026年3月24日去世后，在抖音上的第三方叙事传播。
- 事件边界：公众人物死亡导致本人第一人称自主内容生产不可逆终止。
- 核心过程：内容截取与去语境化、少数片段重复推荐/曝光集中、受众解释变化、首因印象形成。
- “偏离”比较基准：优先与其生前更大范围的自主表达语料比较，其次与具体片段的原始完整语境比较。
- 核心受众：此前不了解或低熟悉度的用户。
- 平台：抖音为主要场域；TikTok、YouTube、Facebook、X/Twitter、微博、B站等用于理论与比较。
- 文献对象：可包含艺人、网红、主播、知识博主、运动员和政治人物等去世公众人物。

### 排除或限制

- 不把主动停更、退网、被封禁与死亡直接视为同一事件类型。
- 不把算法作用预设为已证实事实。
- 不以受众理解本身单独证明“偏离原意”。
- 不在当前阶段设计或运行 LLMABM 实验。
- 纯线下纪念研究仅在能解释媒介记忆或认知机制时纳入。

### 领域、时间、地理与人群

- Domain：传播学、平台研究、数字死亡研究、社会记忆、媒介心理学、推荐系统审计。
- Timeframe：案例观察自2026-03-24起；文献重点为2005-2026，允许纳入更早的奠基性认知研究。
- Geography：主要案例为中国；文献检索不限国家和地区。
- Population：对张雪峰或相应去世公众人物缺少既有认识的社交媒体用户。

## 暂定机制假设

`内容截取与去语境化 → 少数片段获得重复推荐或曝光集中 → 受众解释向少数框架收敛 → 低熟悉度用户形成单一化、标签化首因印象`

该机制链必须由文献和后续经验材料支持、修正或否定。

## 方法方向

- Methodology type：mixed（暂定，仅为结构化交接所需；当前阶段为文献调研）。
- 后续候选方法：以 AgentSociety 为基础的 LLMABM 机制模拟；是否采用及如何校准，待文献调研后决定。

## 涌现中的理论框架

尚未选定单一理论。检索阶段同时考察：数字来生/身后数字身份、平台化或算法化记忆、去语境化与框架化、推荐放大与重复曝光、首因效应与印象形成。

## 检索关键词

digital afterlife；posthumous digital identity；algorithmic memory；platformed memory；celebrity death and social media；decontextualization；recommender amplification；repeated exposure；impression formation；priming and labeling。

## Socratic Insights

1. 死亡意味着本人自主内容生产的不可逆终止，既有自主表达成为封闭语料。
2. 张雪峰是主要案例，但文献范围应跨人物类型、平台与国家。
3. “先去语境化、后重复推荐”属于待检验假设，而非研究结论。
4. 受众实际理解是结果；判断偏离需要与生前广泛自主表达和原始完整语境比较。
5. LLMABM 是文献调研之后再评估的候选方法。

## 附录 A：机制链各环节代表论文（2026-08-19 v2，按 5 环节展开）

> 选取口径：79 条 core 中证据质量最高者，按**机制链 5 环节**（名人死亡×哀悼 → 数字遗产/账号处置 → 推荐系统曝光 → 重复曝光→认知 → 去语境化/视觉误导）归组；篇数不限。环节级证据等级为检索后判断（下表中-强/弱-中等）；论文级沿用卡片体系：材料层级 A=全文精读卡片、B=CNKI 摘要级、C=题录级（未精读，仅作弱证据）；证据等级 Level II 随机实验＞III 受控审计＞IV 计算观察＞VI/VII 质性/概念。**诚实标注**：L016 为观察设计、L046 效应具议题依赖性、D 系列结果变量是命题真实性而非人物印象——凡此，均直接写入「链条中的角色」。

### 机制链 5 环节总览（检索后判断）

| # | 环节 | 已有研究（代表） | 环节证据等级 |
|---|---|---|---|
| 1 | 名人死亡×社交媒体哀悼 | 李文亮微博 134 万条评论计算分析；Jade Goody「天使」标签；袁隆平/金庸记忆书写；墨茶「悲情→道德评价转变」 | 中-强（多为案例/计算分析） |
| 2 | 数字遗产/账号处置 | 悼念账号、委托人机制、封号治理（C4/C8/C15） | 弱-中 |
| 3 | 推荐系统曝光机制 | TikTok 木偶审计、YouTube 四层推荐漂移、Twitter 放大比（Level II 随机实验） | 强 |
| 4 | 重复曝光→认知 | illusory truth 系列 Level II 实验（对数形重复效应、一致性框架竞争） | 强 |
| 5 | 去语境化/视觉误导 | 切片判断研究、N=1,404 图文重配实验 | 中 |

### A.1 环节 1：名人死亡×社交媒体哀悼（中-强：多为案例/计算分析）

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| L016 | Online propagation of emotions: celebrity suicides | PLOS ONE（2025） | A 卡片 / IV 计算观察 | 四起名人自杀百万级推文：厌恶快、广、持久；愤怒/惊讶快而短；恐惧弱 | 情绪→再分发权重表；**观察设计，无法区分用户选择与平台排序** |
| C24 | 「春天的花开秋天的风」：社交媒体、集体悼念与延展性情感空间（李文亮） | 国际新闻界（2021） | B 摘要级 | 134 万条评论的延展性情感空间 | 本土最大死亡评论语料（标定素材） |
| L015 | Angels not souls: popular religion in the online mourning for Jade Goody | Religion（2011） | A 卡片 / VI-VII | 「天使」标签：生前素材与死后框架的一致性 | 用户点名；生前自主表达→死后再生产的原初案例 |
| C22 | 网络哀悼中的集体记忆与国家认同建构（袁隆平） | 郑州大学学位论文（2022） | B 摘要级 | 悼念规模与意义随道德评价变化 | 名人死亡本土案例 |
| C26 | 追忆逝去的名人：社交媒体上关于金庸的记忆书写研究 | 安徽大学学位论文（2020） | B 摘要级 | 名人死后记忆书写与媒介化记忆 | 名人死亡本土案例 |
| C12 | 社交媒体中悼念普通人行为研究——以「墨茶official事件」为例 | 北京印刷学院学报（2022） | B 摘要级 | 悲情形象→道德评价转变→情感冲突 | 印象可被后续叙事覆盖（首因的可逆性） |
| L011 | #MournHub and @GrieveWatch: Mediating mourners' calls for accountability | Int. Journal of Communication（2024） | A 卡片 / VI-VII | 官方哀悼与娱乐化/批判性叙事并行竞争 | 框架竞争（曝光≠态度，A06 卡片警示） |
| L004 | The Digital Remains: Social Media and Practices of Online Grief | The Information Society（2013） | A 卡片 / VI-VII | 网络悲伤实践本身不统一；平台政策塑造可见性 | 哀悼实践多样性基线 |
| C2 | 短暂的公共情感：网生代青年的赛博悼念 | 新闻与传播评论（2024） | B 摘要级 | 情绪转移、贬值、冲突；公共情感短暂不稳定 | 情绪动力学 |
| C7 | 「逝去的歌」：B 站纪念账号的数字哀悼和媒介记忆建构 | 新闻与写作（2023） | B 摘要级 | 情感从负面悲伤延展至正面鼓励 | 本土平台哀悼仪式 |
| L013 | When a celebrity dies… Social identity, us and them | Celebrity Studies（2014） | C 题录 / VI | 名人死亡与社会身份（我们/他们） | 身份框架（弱证据） |
| L012 | "There Isn't Wifi in Heaven!" Negotiating visibility | Journal of Broadcasting & Electronic Media（2012） | C 题录 / VI-VII | 数字时代的死亡协商 | 场景支撑（弱证据） |

### A.2 环节 2：数字遗产/账号处置（弱-中——全链最弱环节）

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| C4 | 「悬空」的记忆：「无主」社交账号集体管理机制的历史比附 | 新闻与写作（2024） | B 摘要级 | 无主账号集体管理机制（委托人/托管） | 用户点名；账号处置的委托人机制 |
| C8 | 「故园荒芜」：「数字死亡」的记忆与遗忘 | 国际新闻界（2023） | B 摘要级 | 平台存储与遗忘的权力 | 用户点名；封号/治理可切断回路 |
| C15 | 新生活（快手悼念账号功能） | 小康（2021） | B 摘要级 | 悼念账号功能：平台主动参与死后内容 | 用户点名；平台功能层 |
| C1 | 数字记忆视域下纪念账号的记忆建构与维系 | 全媒体探索（2025） | B 摘要级 | 纪念账号的记忆建构与维系 | 供给侧结构 |
| C13 | 国内外互联网平台的数字遗产保护与管理策略研究 | 新媒体研究（2021） | B 摘要级 | 平台数字遗产策略比较 | 治理比较 |
| C14 | 联结、交互和展演：数字遗产的媒介化生存 | 当代传播（2021） | B 摘要级 | 数字遗产的媒介化展演 | 概念支撑 |
| C16 | 作为「数字遗产」的隐私：逝者隐私保护的观念建构与理论想象 | 现代传播（2021） | B 摘要级 | 逝者隐私保护观念 | 伦理边界（RQ5 校准时须处理） |

### A.3 环节 3：推荐系统曝光机制（强）

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| L031 | An Empirical Investigation of Personalization Factors on TikTok | Proc. ACM Web Conf.（2022） | A 卡片 / III 木偶审计 | 因素隔离：关注＞点赞≈观看时长；交互→曝光正反馈 | 用户点名；抖音同平台曝光机制（互动权重 w） |
| L040 | Algorithmic amplification of politics on Twitter | PNAS（2022） | A 卡片 / II 随机实验 | 近 200 万日活随机对照：7 国中 6 国放大主流政党 | 用户点名；排序放大因果基准（放大比 A） |
| L024 | Crowdsourced audit of Twitter's recommender algorithm | Scientific Reports（2023） | A 卡片 / III 众包审计 | 算法时间线相对自选关注放大同社群与情绪化内容 | 放大比指标：曝光份额/可选池份额 |
| L022 | The bias beneath: analyzing drift in YouTube's recommender | Social Network Analysis and Mining（2024） | A 卡片 / IV | 四层推荐网络，Atkinson 不平等指数随深度趋近 1 | 用户点名；深度漂移/少数赢家 |
| L021 | What's "Up Next"? Investigating Algorithmic Recommendations | Media and Communication（2021） | A 卡片 / IV | 六周追踪：视频层多样、来源层稳定赢家 | 双层集中（二创模板/来源） |
| L032 | TikTok and the Art of Personalization | Proc. ACM Web Conf.（2024） | A 卡片 / III | 单用户信息流探索/利用度量（真实用户+机器人+随机基线交叉验证） | 重复曝光强度（探索率 ε） |
| L039 | Echo chamber effects on short video platforms | Scientific Reports（2023） | A 卡片 / IV | 抖音、B 站评论网络回声室显著、TikTok 不显著 | 平台调节：中文场景有支撑；但评论网络≠推荐曝光 |
| L034 | Auditing Algorithmic Explanations of Social Media Feeds | Proc. ICWSM（2024） | A 卡片 / IV | 平台「为何推荐」解释与真实信号不一致 | 用户端不可直接观测机制（方法警示） |

**条件性/替代解释（同环节，RQ4 支撑——「算法放大」须以此为界）**

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| L020 | Do not blame it on the algorithm: an empirical assessment | Information, Communication & Society（2018） | A 卡片 / III 模拟 | 21,973 篇×500 用户×7 种推荐逻辑：推荐未必降多样性 | 「算法放大」非必然——反证基线 |
| L027 | Social Drivers and Algorithmic Mechanisms of Content Selection | Perspectives on Psych. Science（2024） | A 卡片 / VI 综述 | 算法多为条件性放大器，强化既有社会驱动力 | 核心校准结论：放大=供给×排序×选择的合谋 |
| L026 | Challenges in Understanding Human-Algorithm Entanglement | Perspectives on Psych. Science（2024） | A 卡片 / VI 概念 | 人—算法纠缠：不存在干净的「有/无算法」对照；倒时序流亦偏向高频发布者 | 方法警示（反事实设计边界） |
| L025 | Modeling news recommender systems' conditional effects | Journal of Communication（2023） | C 题录 / IV | 推荐对选择性曝光的影响是条件性的 | 条件性支撑 |
| L041 | Exposure to ideologically diverse news and opinion on Facebook | Science（2015） | C 题录 / IV | 曝光同质化主要来自朋友选择而非排序 | 用户选择＞算法（平台：Facebook） |

### A.4 环节 4：重复曝光→认知（强；但结果变量是命题真实性，非人物印象）

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| L058 | Prior exposure increases perceived accuracy of fake news | JEP: General（2018） | A 卡片 / II | 一次先前曝光即有效；延迟一周、争议标签、政治不一致时仍存续 | 感知真实性更新核心实验 |
| L060 | The effects of repetition frequency on the illusory truth effect | Cognitive Research（2021） | A 卡片 / II | **对数形重复效应**：第二次曝光增量最大、之后边际递减（d≈1.00/0.67） | 用户点名；log 形状参数 a |
| L061 | Perceived truth of statements and simulated social media engagement | Cognitive Research（2020） | A 卡片 / II | **一致性框架竞争**：逐字/语义一致重复↑真实感；语义不一致重复↓真实感 | 用户点名；框架竞争胜负（一致性阈值 θ） |
| L062 | The illusory truth effect leads to the spread of misinformation | Cognition（2023） | A 卡片 / II | 重复→感知准确性→分享意愿，中介链成立 | 认知—供给闭环接口 |
| L056 | The Truth About the Truth: A Meta-Analytic Review | Personality and Social Psych. Bulletin（2010） | C 题录 / 元分析 | 真理效应元分析 | 总览性支撑 |
| L057 | Knowledge does not protect against illusory truth | JEP: Applied（2015） | C 题录 / II | 先验知识不防护 | 低熟悉用户尤其易感的间接支撑 |
| L059 | Truth by Repetition: Explanations and Implications | Current Directions in Psych. Science（2019） | C 题录 / 综述 | 机制解释与局限 | 理论 |
| L063 | Judging Truth | Annual Review of Psychology（2020） | C 题录 / 综述 | 真实性判断研究框架 | 理论 |
| C29 | 算法推荐技术下信息茧房倾向：概念化、测量与影响验证 | 中国人力资源开发（2025） | B 摘要级 | 茧房倾向的双理论概念化+量表+影响验证 | 中文概念操作化 |
| C30 | 信息茧房效应下用户群体极化形成机理研究 | 图书与情报（2024） | B 摘要级 | 茧房→群体极化机理 | 中文邻近证据 |

**印象形成子块（同环节，首因印象）**

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| L052 | First Impression Formation Based on Valence of the Text | Frontiers in Psychology（2021） | A 卡片 / II | 微信 N=204 实验：内容价性→可信度→喜爱度（可信度中介、同质性调节） | 首印象机制；**刺激为本人资料，迁移到死后第三方剪辑须重测** |
| L051 | Online first impressions: Person perception | Computers in Human Behavior（2017） | C 题录 / IV-VI | 社交媒体资料→陌生人首印象 | 场景支撑 |
| L053 | Emotional Expressions and First Impressions | Media Psychology（2025） | C 题录 / VI | 情绪表达→首印象形成 | 情绪×首印象 |
| L018 | Algorithmically generated memories | Memory, Mind & Media（2024） | A 卡片 / VI 概念 | 算法记忆=对过去的局部挹取，片段≠人物整体 | 概念警戒（因变量界定：印象≠完整人格） |

### A.5 环节 5：去语境化/视觉误导（中）

| ID | 题名 | 期刊（年份） | 材料/等级 | 关键发现 | 链条中的角色 |
|---|---|---|---|---|---|
| C27 | 从「完整观看」到「切片判断」：短视频传播中的去语境化评价 | 榆林学院学报（2026） | B 摘要级 | 切片观看→评价集中化、稳定化 | 用户点名；去语境化的本土直接证据 |
| L046 | A Picture Paints a Thousand Lies? The Effects of Reshared News | Political Communication（2020） | A 卡片 / II | **N=1,404 图文重配实验**：视觉去语境化可信度效应具**议题依赖性**（校园枪击无稳定差异） | 用户点名；校准警示：效应非普适，须在张雪峰议题重测 |
| L047 | Visual Mis- and Disinformation, Social Media, and the Outrage Machine | Journalism & Mass Communication Quarterly（2021） | A 卡片 / VI-VII | 视觉误导框架：真实素材错置语境同样危险 | 理论框架 |
| L044 | Entextualization and resemiotization as resources | The Language of Social Media（2014） | C 题录 / VI | 文本脱离原语境后被重新嵌入的再语境化机制 | 理论框架 |
| L045 | Disinformation by Design: The Use of Evidence Collages | Political Communication（2020） | C 题录 / VI-VII | 证据拼贴的设计分析 | 理论框架 |
| C28 | 算法偏见与乡土想象：短视频平台受众对乡村形象的认知形塑 | 新闻前哨（2025） | B 摘要级 | 算法×受众认知→乡村形象单一化、标签化 | 链条终点类比：推荐→认知→形象刻板化的中文直接邻近证据 |

### A.6 环节证据强度一览（按 5 环节）

```
〔场域〕环节1 哀悼 中-强(L016/C24/L015) ──►〔供给〕环节5 去语境化 中(C27/L046) ──►〔曝光〕环节3 推荐 强(L031/L040)
                                                      │                          │
                                                      │                        〔认知〕环节4 重复→认知 强(L058/L060)
                                                      └──〔治理〕环节2 账号处置 弱-中(C4/C8/C15) 可切断/重塑回路 ◄─┘
```

- **最强环节**：环节 3（推荐曝光）与环节 4（重复曝光→认知）——Level II/III 证据齐备，可直接参数化；
- **变量错位（本 RQ 的 Novel 点）**：环节 4 全部实验的因变量是「命题真实性/可信度」，**「重复曝光→人物整体印象单一化」无直接测量先例**；
- **最弱环节**：环节 2（数字遗产/账号处置）对曝光回路的量化作用——摘要级/质性为主；首因印象（L052）迁移须以张雪峰切片重测。

## Material Passport

- Origin Skill: academic-research-suite / deep-research
- Origin Mode: socratic → lit-review handoff
- Origin Date: 2026-08-17
- Verification Status: UNVERIFIED
- Version Label: rq_v0.3
- Repro Lock: null
- Experiment Intake Declaration: no_experiments_declared（当前未运行实验；未来设想不等于已声明实验）
- Update 2026-08-19: FINER 检索后更新（Feasible 6→7，Novel 8→8.5，平均 8.0→8.3，依据见「检索后 FINER 更新」节）；新增附录 A 机制链代表论文（依据 papers/deep_read/rq1–rq5 与 literature_index core 79 条，ID 可交叉索引）
- Update 2026-08-19 (2nd): 采纳用户口径，附录 A 重组为**机制链 5 环节**（名人死亡×哀悼 / 数字遗产·账号处置 / 推荐系统曝光 / 重复曝光→认知 / 去语境化·视觉误导），环节证据等级采用用户评级（中-强 / 弱-中 / 强 / 强 / 中），「检索后可做性判断」第 1、3 点同步按 5 环节重述；FINER 分数不变

