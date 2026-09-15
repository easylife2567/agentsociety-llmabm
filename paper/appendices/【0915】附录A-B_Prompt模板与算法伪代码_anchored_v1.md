# 附录A—B　Prompt模板与算法伪代码

*对应 anchored_v1 三臂仿真实现｜版本冻结日：2026-09-15*

本文件为论文《公众人物去世后，算法策展如何塑造舆论场对其的数字表征》的独立附录稿。文本对应当前 anchored_v1 实现；其中花括号表示运行时替换变量，方括号标签用于在伪代码中定位相应提示或公式。

> **方法说明：**当前版本不使用大语言模型决定“是否发言”。发言决策采用数值模拟方法，大语言模型负责在规则判定为发言后生成帖子正文。

| **项目** | **冻结设定** |
|:---|:---|
| 实验窗口 | 2026-W12 至 2026-W22，共11周；W13为去世事件周 |
| 群体 | 100个固定类型智能体：玩梗19、悼念22、借势营销23、教育观点15、其他21 |
| 实验臂 | random、chronological、interest；每臂3个seed（0、1、2） |
| 信息流 | 每次行动10个槽位；内容生成读取排序在前的5条作为上下文 |
| 正文模型 | 仅在数值规则判定发言后调用1次LLM；中文帖子，提示上限300字 |
| 实现版本 | anchored_v1；Uᵢₜ = Bᵢ + Rᵢₜ(Dᵢₜ − Bᵢ) |

---

## 附录A　Prompt模板

本附录依次给出人设的生成规则、实际发送给大语言模型的system消息和user消息、环境工具调用模板，以及替代decision prompt的数值决策规则。除运行时变量外，以下模板按源代码逐字转录。

### A.1　运行时变量与消息结构

| **变量** | **含义与来源** |
|:---|:---|
| {persona} | 初始化时固定生成的完整个体人设，包含姓名、年龄、职业、常用平台、类型强度与三条行为特征。 |
| {agent_type} | 固定内容类型：meme、mourning、marketing、education或other。整个运行期间不改变。 |
| {content_guide} | 与固定类型一一对应的正文写作指引，见A.2.3。 |
| {week} | 当前ISO周标签，例如2026-W13。 |
| {stock}/{flow} | 当前舆论场存量与新增量；在prompt中仅作为语境，不进入发言判定。 |
| {share_own} | 本智能体10槽信息流中与自身固定类型相同的内容份额，显示为整数百分比。 |
| {feed_lines} | 当前信息流前5条；每条含官方标记（如有）、作者、周次和最长120字正文摘录。 |
| {type_vocab} | 初始化时分配给该智能体的类型词表；非空时要求自然选用1—3词。 |

### A.2　System prompt（逐字模板）

**[Prompt A-1] System消息**

> 你在扮演一个中文社交媒体用户，人设如下：
>
> {persona}
>
> 你的固定内容类型是：{agent_type}。{content_guide}

其中，{persona}并非再次由LLM生成，而是在初始化时由固定程序拼接。其逐字组装模板如下。

**[Prompt A-1a] persona插值模板**

> 你叫{name}，{age} 岁，是一名{occupation}，平时主要刷{platform}。{intensity}。
>
> {style}
>
> 行为特征：
>
> \- {spiral_text}
>
> \- {decay_text}
>
> \- {activity_text}

#### A.2.1　五类人设文本的固定部分

**（1）玩梗型（meme）**

表达风格：你是玩梗/抽象文化爱好者，表达方式以谐音、变体称呼、emoji、反讽和圈内梗为主，追求新颖的表达形式，讨厌一本正经。

**（2）悼念型（mourning）**

表达风格：你是被其离世触动的关注者，表达真诚克制，主要是追思、缅怀，以及由事件引发的健康、工作与生活感慨。

**（3）借势营销型（marketing）**

表达风格：你在教育/升学赛道做课程、资料或咨询服务的推广，惯于借热点引流，话术圆滑，擅长把产品植入任何讨论。

**（4）教育观点型（education）**

表达风格：你长期关注升学、专业选择、就业与教育公平议题，习惯理性讨论、输出观点，对相关人物的教育观点有自己明确的评价。

**（5）其他型（other）**

表达风格：你是普通路人用户，偶尔刷到相关讨论，发表一般性看法、转述消息或随口感慨，没有固定立场与议题。

#### A.2.2　个体人口学变量的抽样范围

| **类型** | **年龄** | **职业池（逐字）** | **平台池；强度取值（逐字）** |
|:---|:---|:---|:---|
| meme | 16—29 | 大学生、高中生、刚入职的打工人、自由职业者、研究生、待业青年 | 抖音×2、微博、小红书、B站；“重度玩梗选手，梗是你上网的主要语言”(0.4)／“轻度玩梗用户，看到好笑的梗会跟一下”(0.6) |
| mourning | 22—45 | 考研二战的学生、大学生、年轻家长、中学老师、打工人、公务员 | 微博、小红书、抖音；“真情实感的长期关注者，看过他很多直播和讲座”(0.5)／“被事件触动的普通关注者”(0.5) |
| marketing | 25—45 | 考研机构课程顾问、教育类自媒体运营、资料贩卖店主、升学规划咨询师、带货主播 | 抖音、小红书、微博；“职业推广号，流量就是饭碗”(1.0) |
| education | 24—50 | 高中生家长、大学生、中学老师、考研学生、教育行业从业者、公务员 | 微博、小红书、抖音；“对其教育观点深有认同”(0.5)／“对其教育观点持保留态度、常参与争论”(0.5) |
| other | 18—50 | 上班族、大学生、全职妈妈、个体户、退休职工、程序员 | 抖音、微博、小红书；“只刷不说的潜水用户”(0.6)／“偶尔评论两句的普通用户”(0.4) |

年龄不低于32岁时，从职业池中排除大学生、高中生、考研学生、考研二战的学生和研究生，以保持年龄—职业一致性。

显示名格式为“{类型前缀}\_{10—99随机整数}”。前缀池依次为：meme={抽象、整活、乐子、冲浪、躺平、摸鱼}；mourning={追思、点蜡、感怀、纪念、深思、静心}；marketing={升学规划、资料库、考研助手、志愿指导、提分、上岸直通车}；education={谈教育、聊升学、看专业、志愿观察、教育思考、择校}；other={路人、围观、随便看看、普通、吃瓜、路过}。

#### A.2.3　{content_guide}的五种逐字取值

| **固定类型** | **逐字写作指引** |
|:---|:---|
| meme | 写一条玩梗/抽象风格的帖子：用谐音、变体称呼、emoji、反讽或圈内梗表达，短小轻快，不解释梗。 |
| mourning | 写一条悼念/缅怀风格的帖子：真诚追思、表达哀悼或由其离世引发的生命/健康感慨，语气克制严肃，可用 🕯️ 等符号。 |
| marketing | 写一条借势营销帖子：借当前讨论热点引流你的课程/资料/咨询/服务，含明确行动号召（链接/私信/领取/限时等），话术圆滑。 |
| education | 写一条教育观点讨论帖子：围绕专业选择、升学规划、就业、教育公平或相关人物的教育观点展开理性讨论，有自己的明确立场，不做商业推广。 |
| other | 写一条普通路人讨论帖：转述事件、表达一般性看法或闲聊式感慨，不属于玩梗/悼念/营销/教育讨论中的任何一类，口吻日常。 |

#### A.2.4　System消息完整实例

以下为seed 0中agent_id=1（借势营销型）的完整实例。类型词表不放入system消息，而是在user消息末尾按条件追加。

> 你在扮演一个中文社交媒体用户，人设如下：
>
> 你叫上岸直通车_73，31 岁，是一名带货主播，平时主要刷微博。职业推广号，流量就是饭碗。
>
> 你在教育/升学赛道做课程、资料或咨询服务的推广，惯于借热点引流，话术圆滑，擅长把产品植入任何讨论。
>
> 你的固定内容类型是：marketing。写一条借势营销帖子：借当前讨论热点引流你的课程/资料/咨询/服务，含明确行动号召（链接/私信/领取/限时等），话术圆滑。

### A.3　发言决策：无LLM decision prompt

> **方法说明：**每个智能体先读取信息流快照，再由下列公式确定是否发言。给定配置、信息流和累计曝光，决策结果唯一；该步骤不调用LLM，也没有可披露的自然语言decision prompt。

**[Formula F-1] 感知意见气候**

设智能体i的固定类型为c，qᵢₜ为其当期信息流中类型c的份额，πc为该类型在人口中的基准份额，sᵢ为个体沉默螺旋敏感度，αD=0.4296954755626446，k=1.5，则：

**Dᵢₜ = 1 + (sᵢ·αD)·tanh[k·(qᵢₜ − πc)/πc]**

**[Formula F-2] 注意力衰减**

设Cᵢₜ为截至当期之前智能体i累计看到的本类型内容数，λᵢ为个体疲劳系数，尺度固定为15，则：

**Rᵢₜ = exp(−λᵢ·Cᵢₜ/15)**

**[Formula F-3] 锚定式表达效用与阈值**

Bᵢ是由W05—W12事件前常态盘固定的表达效用锚点，aᵢ是个体表达门槛。

**Uᵢₜ = Bᵢ + Rᵢₜ(Dᵢₜ − Bᵢ)；当且仅当 Uᵢₜ ≥ aᵢ 时发言。**

| **类型c** | **πc** | **Bᵢ（类型常数）** | **sᵢ抽样中心** | **λᵢ类型内标定均值** |
|:---|:---|:---|:---|:---|
| meme | 0.19 | 0.7755 | 1.2 | 1.2430377762 |
| mourning | 0.22 | 0.7678 | 0.8 | 2.2820352014 |
| marketing | 0.23 | 0.82515 | 0.2 | 1.0192411150 |
| education | 0.15 | 0.7412 | 0.5 | 2.4936143468 |
| other | 0.21 | 0.7686 | 1.5 | 4.4294577101 |

aᵢ与sᵢ以类型中心乘U[0.8,1.2]生成并截断到预设区间；λᵢ保留个体相对异质性后，在类型内同比缩放至表中均值。所有个体值均写入每个seed的冻结配置文件。环境中的“丰沛度Bₜ、空旷度Sₜ与涌现增益Gₜ”只记录用于描述和审计，不进入F-1—F-3。

### A.4　内容生成User prompt（逐字模板）

**[Prompt A-2] 信息流非空时的User消息**

> 现在是 {week}。你决定公开发言。
>
> 本周舆论场存量 {stock} 帖、新增 {flow} 帖，你的 feed 里同类内容占比约 {share_own:.0%}。
>
> 你本周刷到的前几条帖子：
>
> \- {official_badge}@\{author_handle_1\}（{post_week_1}）：{content_1[:120]}
>
> \- {official_badge}@\{author_handle_2\}（{post_week_2}）：{content_2[:120]}
>
> …（最多5条）
>
> 你的发言必须建立在你看到的内容之上：可以回应、补充、反驳、二创、玩其中的梗、或接话跟帖式地引用讨论；若其中某条与你高度相关，优先围绕它展开。
>
> 请写一条不超过 {max_chars} 字的帖子正文，只输出正文本身，不要解释、不要引号。可以带 emoji 或话题标签，风格必须符合你的人设与类型。
>
> {vocab_note}

{official_badge}在帖子为官方来源时取“【官方】”，否则为空。每条正文先去除首尾空白并将换行替换为空格，再截取前120字。{max_chars}默认取300。

**[Prompt A-2a] 信息流为空时的替代段落**

> 本周信息流为空，你可就当前话题自由发言。

**[Prompt A-2b] 类型词表非空时追加的逐字文本**

> 组织语言时，从你的常用词库里自然选用 1-3 个词融入正文（贴合语境、不要堆砌、不要逐字罗列）：{type_vocab以“、”连接}

### A.5　环境工具调用模板

以下两段是框架template_mode中的工具路由指令，用于读取快照与发布帖子；它们不是行为决策prompt。

**[Prompt A-3] 读取信息流**

> Please call get_feed() using agent_id from ctx['variables'] to get my current weekly feed snapshot.

**[Prompt A-4] 发布帖子**

> Please call create_post() using agent_id and content from ctx['variables'] to publish my post.

### A.6　输出后处理与类型约束

- LLM返回值去除首尾空白，并去除首尾的英文或中文双引号。
- 提示要求正文不超过300字；实现另设max_chars+100字符的容错截断保护。空输出视为本期未成功发帖。
- 帖子进入内容池时的pool_type恒等于作者的固定智能体类型；词表判类器另行给出assigned_type与type_mismatch，仅作质量审计，不改变pool_type。
- 每个行动批次每个智能体至多发布一帖。

---

## 附录B　算法伪代码

本附录以F-1—F-3和Prompt A-1—A-4为索引，给出三臂仿真的可执行逻辑。random与interest以周为行动批次；chronological采用小时级同步微批次，但三臂均保证每个智能体每周恰有一次决策机会。

### B.1　词表倾向、生命周期与兴趣推荐公式

**[Formula F-4] 词表倾向分**

对帖子p和类型c∈{meme,mourning,marketing,education}，令Hpc为对应词表的命中数，\|xp\|为原始正文字符数，则：

**Tpc = Hpc / max(1, \|xp\|/50)**

匹配同时在原文小写层和“去emoji、去非单词字符、转小写”的规范化层进行。meme倾向由linkage命中数与strong命中数相加；计算strong命中前，用占位符替换死因事实词，避免仅提及死亡事实就被判作玩梗。各倾向分保留4位小数。other没有专用倾向维度，兴趣臂对other智能体的类型倾向项取0。

**[Formula F-5] interest臂帖子生命力**

帖龄冷却半衰期为1.5周；累计曝光饱和尺度为20。设Lpt为帖子时间生命，Ept为累计曝光次数，则：

**Lpt ← Lp,t−1·0.5^(1/1.5)；Vpt = Lpt·0.5^(Ept/20)**

当Lpt<0.35时帖子退出interest候选池。退场只看时间生命，不看曝光饱和项。random与chronological不读取Lpt或Vpt。

**[Formula F-6] interest臂打分与比例抽样**

对于类型为cᵢ的智能体i与候选帖p：

**scoreip = (α·Tp,cᵢ + γ)·Vpt + εip**

正式配置中α=1、γ=0.5、εip∼U[−0.05,0.05]。候选帖的无放回顺序抽样权重为exp(scoreip/τ)，τ=4。该打分不含互动量或帖子级热度。

### B.2　算法1：初始化

> 算法1 InitializeSimulation(arm, seed)
>
> 输入：arm ∈ {random, chronological, interest}；seed ∈ {0,1,2}
>
> 输出：冻结的智能体群体、环境状态与随机数流
>
> 1 读取真实帖子注入样本 injection_sample_s{seed}.json
>
> 2 读取五类词表 vocabs.json
>
> 3 按19/22/23/15/21生成meme/mourning/marketing/education/other共100个固定类型智能体
>
> 4 对每个智能体i：
>
> 5 抽样姓名、年龄、职业、平台与强度，按[Prompt A-1a]拼接persona
>
> 6 冻结(a_i, s_i, λ_i, B_i, α_D)与type_vocab
>
> 7 若arm=chronological：冻结每周行动小时h_i（来自事件前真实“星期×小时”分布）
>
> 8 初始化互相独立的RNG：注入、random feed、interest噪声、interest比例抽样
>
> 9 设置窗口W12…W22、feed_size=10、feed_context_n=5、event_week=W13
>
> 10 若arm=interest：设置半衰期1.5、饱和尺度20、退场线0.35、τ=4、W13悼念保底5槽
>
> 11 打开首个行动批次，并建立W12基线景观快照
>
> 12 返回状态

### B.3　算法2：random／interest周级主循环

> 算法2 WeeklyMainLoop(arm, seed) // arm ∈ {random, interest}
>
> 1 state ← InitializeSimulation(arm, seed) [算法1]
>
> 2 for week = W12,…,W22 do
>
> 3 对已有帖子更新时间生命L_pt [F-5；random忽略]
>
> 4 注入该week的冻结真实帖子样本；保留数据标签并计算倾向T_pc [F-4]
>
> 5 计算(B_t,S_t,G_t)并记入审计状态 [仅观测，不进决策]
>
> 6 if arm = interest then
>
> 7 pinned ← 本周官方帖（延伸周数=0）
>
> 8 floor ← 若week=W13，取非噪音、非置顶活帖中悼念倾向最高的5帖；否则∅
>
> 9 else
>
> 10 pinned ← ∅；floor ← ∅
>
> 11 end if
>
> 12 for agent i 按agent_id升序 do
>
> 13 feed_i ← AssembleFeed(i, week, arm, pinned, floor) [算法3]
>
> 14 立即登记feed_i的曝光；更新帖子E_pt与智能体本周气候q_it
>
> 15 end for
>
> 16 并行执行所有智能体的一次行动 [算法4]
>
> 17 将本周成功生成的pending帖子统一并入帖子池 [同周互不可见]
>
> 18 更新每个智能体累计本类型曝光C_it、累计发帖数与全局景观
>
> 19 写入周级环境表、智能体表和decision_log
>
> 20 end for
>
> 21 close；返回replay与帖子池

### B.4　算法3：三种策展制度的信息流装配

> **批注（王锭云，2026-09-15）：**随机推送和时序推送不知道算不算策展。

> 算法3 AssembleFeed(i, t, arm, pinned, floor)
>
> 1 if arm = random then
>
> 2 C ← 截至当周已经进入环境的全部历史帖子
>
> 3 return 从C中等概率、无放回抽取min(10, |C|)帖
>
> 4 // 不读时间、生命力、类型、兴趣、热度或累计曝光；无置顶、无W13保底
>
> 5 else if arm = chronological then
>
> 6 C ← 行动时刻之前（含该时刻已注入）已经发布的全部帖子
>
> 7 按(event_time, post_id)倒序排列C
>
> 8 return C的最新10帖
>
> 9 // 不读生命周期、兴趣、热度或累计曝光；无置顶、无W13保底
>
> 10 else if arm = interest then
>
> 11 feed ← pinned中最多10帖
>
> 12 依次追加floor中尚未加入的帖子，直至10槽
>
> 13 C ← 时间生命L_pt≥0.35的活帖，并去除pinned与floor [F-5]
>
> 14 对每个p∈C：计算T_p,c_i、V_pt与score_ip [F-4,F-5,F-6]
>
> 15 按权重exp(score_ip/4)无放回顺序抽样，补足剩余槽位
>
> 16 return feed
>
> 17 end if

interest臂在按agent_id升序装配信息流时立即累计帖子曝光，因此较早被抽中的帖子会因F-5的曝光饱和项降低其对后续智能体的边际权重。此顺序在配置与seed固定后可完全复现。

### B.5　算法4：单个智能体的行动

> 算法4 AgentAction(i, t)
>
> 1 若arm=chronological且当前小时≠h_i：return inactive
>
> 2 snap_i ← get_feed(agent_id=i) [Prompt A-3]
>
> 3 若snap_i不可用：记录feed_unavailable；return silent
>
> 4 q_it ← snap_i.feed_type_distribution[c_i]
>
> 5 D_it ← 1+(s_i·α_D)·tanh(1.5·(q_it−π_c_i)/π_c_i) [F-1]
>
> 6 R_it ← exp(−λ_i·C_it/15) [F-2]
>
> 7 U_it ← B_i+R_it·(D_it−B_i) [F-3]
>
> 8 把q_it、D_it、R_it、B_i、U_it、a_i及观测量(B_t,S_t,G_t)写入decision_log
>
> 9 if U_it < a_i then return silent
>
> 10 messages ← [System: Prompt A-1, User: Prompt A-2]
>
> 11 content ← LLM(messages) [每次发言最多1次调用]
>
> 12 content ← 去首尾空白与包裹引号，并执行长度保护
>
> 13 若content为空：记录content_empty；return silent
>
> 14 result ← create_post(agent_id=i, content=content) [Prompt A-4]
>
> 15 pool_type ← c_i；assigned_type ← VocabClassifier(content) [F-4]
>
> 16 记录type_mismatch；return posted

### B.6　算法5：chronological小时级同步微批次

> 算法5 ChronologicalMainLoop(seed)
>
> 1 state ← InitializeSimulation(chronological, seed) [算法1]
>
> 2 for week = W12,…,W22 do
>
> 3 清空本周聚合器；预计算本周(B_t,S_t,G_t) [仅观测]
>
> 4 for event_time = 本周所有“至少一人行动”的小时，按时间升序 do
>
> 5 将published_at≤event_time且尚未注入的真实帖子并入池
>
> 6 A ← {i | h_i = event_time在一周中的小时序号}
>
> 7 在任何A中智能体发言前，为所有i∈A冻结最新10帖feed_i [算法3]
>
> 8 并行执行i∈A的AgentAction(i,event_time) [算法4]
>
> 9 批次结束后统一把pending帖子并入池
>
> 10 // 同小时智能体互不可见；更晚小时可见更早小时生成的帖子
>
> 11 更新A中智能体的累计曝光C_it
>
> 12 end for
>
> 13 注入截至周日23:59:59仍未注入的本周真实帖子
>
> 14 将各小时结果聚合为一行周级环境记录与每智能体一行周级记录
>
> 15 end for
>
> 16 return replay与帖子池

### B.7　同步性、可见性与可复现性约束

- random／interest：本周所有智能体的信息流在发言前预先装配；本周生成帖在周末统一入池，最早于下一周可见。
- chronological：同小时内先冻结全部信息流、后统一行动；同小时互不可见，较晚小时可见较早小时生成帖。
- 所有臂中每个智能体每周只有一次发言判定；每次成功发言只调用一次正文生成LLM。
- 固定seed同时决定群体抽样、真实注入样本与各随机数流；每个随机来源使用独立RNG，减少机制间的随机耦合。
- 决策日志保存F-1—F-3的全部输入、分量、效用与门槛，可在不调用LLM的情况下事后重算“是否发言”。

### B.8　实现来源映射（复现核对用）

| **内容** | **工作区相对路径** |
|:---|:---|
| 智能体、Prompt与行动逻辑 | custom/agents/curation_discourse_agent.py |
| 五类人设与个体参数生成 | custom/agents/curation_personas.py |
| F-1—F-6共享纯函数 | custom/envs/curation_mechanisms.py |
| 三臂信息流、环境工具与主循环 | custom/envs/curation_dynamics_space.py |
| 三臂冻结配置 | hypothesis_4/experiment_1/init/configs/anchored_v1_*.json |
| 周级/小时级步进计划 | hypothesis_4/experiment_1/init/steps.yaml；steps_chronological_hourly.yaml |
| 词表资产 | custom/envs/curation_assets/vocabs.json |

*注：上述路径用于本地复现核对。投稿时若匿名审稿要求隐藏代码位置，可保留算法与提示全文，并将本节路径替换为匿名仓库中的对应文件。*
