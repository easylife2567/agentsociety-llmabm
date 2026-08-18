# B03｜偏差之下：分析YouTube算法推荐中的漂移

> 英文原题：*The bias beneath: analyzing drift in YouTube’s algorithmic recommendations*  
> DOI：10.1007/s13278-024-01343-5  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level IV；学科适配综合评级 B。

## 一、文献一句话定位

core。对本项目最有用的是“随推荐深度的片段漂移”和“可见性不平等”两类可测指标，而不是其因果措辞。

## 二、研究背景

推荐路径不仅可能改变主题，也可能随深度改变情绪、道德语气与毒性，同时造成可见性极度不均。

## 三、核心问题

从地缘政治种子视频出发的多层YouTube推荐网络，是否在语义、情感、道德语气、毒性和可见性分布上出现漂移？

## 四、理论基础与核心概念

以算法偏差、叙事漂移与可见性不平等为概念框架；重点是推荐网络审计，而非一个经过随机识别的理论模型。

## 五、研究方法

每个议题手工选择40个种子视频，在未登录、清除Cookie的会话中用Selenium展开四层推荐；结合情绪/道德/毒性分类、BERTopic、网络与不平等度统计。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

三类地缘政治叙事的四层YouTube推荐网络出现情绪、道德语气、毒性和主题漂移；各层视频的点赞、播放和评论分布高度不均，Atkinson指数随推荐深度接近1。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

在四层推荐路径上同时度量语义、语气和Atkinson不平等度，使‘漂移’和‘少数赢家’成为可观测结果。

## 八、局限性

可观察到推荐路径上的叙事漂移与可见性集中；但种子人工选取、只测三个议题、无随机或倒时序对照，且平台内容库与创作者供给可同时造成漂移；作者的强算法影响表述需降级为关联证据。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

可借用推荐深度和可见性不平等指标，但本文的人工种子、无登录会话与无对照设计使其只能提供关联性证据。张雪峰研究需额外控制内容库和创作者供给。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

In today’s digital world, understanding how YouTube’s recommendation systems guide what we watch is crucial. This study 
dives into these systems, revealing how they influence the content we see over time. We found that YouTube’s algorithms 
tend to push content in certain directions, affecting the variety and type of videos recommended to viewers. To uncover 
these patterns, we used a mixed methods approach to analyze videos recommended by YouTube. We looked at the emotions 
conveyed in videos, the moral messages they might carry, and whether they contained harmful content. Our research also 
involved statistical analysis to detect biases in how these videos are recommended and network analysis to see how certain 
videos become more influential than others. Our findings show that YouTube’s algorithms can lead to a narrowing of the 
content landscape, limiting the diversity of what gets recommended. This has important implications for how information is 
spread and consumed online, suggesting a need for more transparency and fairness in how these algorithms work. In sum-
mary, this paper highlights the need for a more inclusive approach to how digital platforms recommend content. By better 
understanding the impact of YouTube’s algorithms, we can work towards creating a digital space that offers a wider range 
of perspectives and voices, affording fairness, and enriching everyone’s online experience.
Keywords  Algorithmic bias · Recommendation systems · YouTube · Drift · Emotion · Content

### 方法

Section 5 presents 
our findings on narrative drift, supplemented by detailed 
graphical analyses. Finally, Sect. 6 summarizes our study’s 
key insights.
The goal of this research extends beyond merely map-
ping narrative drift; it seeks to delve into the implications 
of algorithmic content curation on content diversity and the 
fair distribution of information across the digital landscape. 
By scrutinizing YouTube’s recommendation algorithm and 
identifying potential biases, this study contributes to the 
ongoing dialogue on digital media consumption, govern-
ance, and its societal impact.
In doing so, we challenge the current state of digital con-
tent recommendation, envisioning a path toward more trans-
parent, equitable, and diverse digital ecosystems. Through 
this exploration of YouTube’s recommendation system, we 
aim to shed light on the nuances of algorithmic governance, 
fostering a richer and more inclusive digital commons for 
all.
2  Background
In this section, we delve into the intricate web of geopo-
litical issues that shape our world, exploring conflicts and 
disputes that not only have regional implications but also 
resonate on the global stage. From the deep-rooted tensions 
in China’s Xinjiang province to the strategic complexities of 
the South China Sea dispute, and the nuanced use of histori-
cal narratives, such as the story of Cheng Ho, in modern-day 
diplomacy, these offer insightful analyses into some of the 
most pressing and contentious geopolitical challenges of our 
times.
2.1  China‑Uyghur conflict
The Xinjiang conflict, deeply rooted in complex historical, 
cultural, and political factors, has emerged as a significant 
issue in global discourse. Central to this conflict is the dif-
ficult situation faced by the Uyghur Muslim minority in Chi-
na’s Xinjiang province, an area filled with ethnic tensions 
and controversial government actions. Research highlights 
the cultural and linguistic aspects of the conflict, focusing 
on the Uyghur identity and language policy, underscoring 
how identity plays a crucial role in the ongoing tensions 
(Dwyer 2005). Another study examines the conflict through 
the lens of majority-minority dynamics within China, pro-
viding insights into the socio-political factors that have 
contributed to the escalation of tensions (Hasmath 2019). 

Social Network Analysis and Mining (2024) 14:171 
Page 3 of 42 
171
Further analysis explores the broader implications of the 
conflict, particularly China’s national policies and their 
impact on the Uyghur population, offering a critical view of 
the government’s approach to handling ethnic diversity and 
disagreement (Israeli 2010). This is complemented by dis-
cussions on the involvement of international organizations 
like Amnesty International in addressing the discrimination 
and conflict faced by Uyghurs, highlighting the period from 
2018 to 2022 and the international community’s response 
(Al-Asad and Zarkachi 2023). Additionally, studies on 
Uyghur Muslim ethnic separatism clarify the complexities 
of ethnic identity and the desire for self-governance within 
Xinjiang, illustrating the intricate relationship between eth-
nic identity, political aspirations, and the broader conflict 
narrative (Davis 2008). These scholarly perspectives paint a 
multifaceted picture of the Xinjiang conflict, demonstrating 
its multi-dimensional nature that includes cultural, political, 
and international elements.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

[未自动定位；不代表原文无此部分]

### 讨论与结论

[未自动定位；不代表原文无此部分]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Cakmak, M. C., Agarwal, N., & Oni, R. (2024). The bias beneath: Analyzing drift in YouTube’s algorithmic recommendations. Social Network Analysis and Mining, 14, Article 171. https://doi.org/10.1007/s13278-024-01343-5
- 本地正文：`文献全文/正文/B03_2024_偏差之下：分析YouTube算法推荐中的漂移__The bias beneath analyzing drift in YouTube’s algorithmic recommendations.pdf`
- 源URL：https://link.springer.com/content/pdf/10.1007/s13278-024-01343-5.pdf
- 原文抽取：`../原文结构化抽取/B03_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
