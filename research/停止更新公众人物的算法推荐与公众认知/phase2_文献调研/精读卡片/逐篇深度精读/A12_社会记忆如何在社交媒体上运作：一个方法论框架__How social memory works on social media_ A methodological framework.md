# A12｜社会记忆如何在社交媒体上运作：一个方法论框架

> 英文原题：*How social memory works on social media: A methodological framework*  
> DOI：10.1017/mem.2024.18  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level VI；学科适配综合评级 A。

## 一、文献一句话定位

core。可直接转化为案例编码：谁发起记忆、何时出现峰值、什么平台化语汇变成标签。

## 二、研究背景

社交媒体上的社会记忆既有传统记忆工作的特征，又受平台特有数据结构、交互形式和话语惯例影响，因而需要可跨平台且保留差异的方法框架。

## 三、核心问题

如何用可操作的‘记忆标记’识别社交媒体上的记忆工作，同时兼顾方向性、时间性和平台方言？

## 四、理论基础与核心概念

以社会记忆与记忆工作为理论核心，提出方向性、时间性和平台方言三类记忆标记。

## 五、研究方法

上层数据挖掘加平台特定的自下而上分析；演示数据包含530万条Facebook帖文/评论和500万条Twitter帖文/转发。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

社交媒体记忆工作可以从方向性、时间性和平台方言三类“记忆标记”来测量。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

将大规模自上而下数据挖掘与平台特定的自下而上识别结合，避免用单一关键词套用所有平台。

## 八、局限性

是方法论框架而非针对推荐效应的识别；跨平台演示提升了可迁移性。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

可直接用于张雪峰案例的数据编码：区分谁在记忆谁、何时出现峰值，以及抖音特有的梗、音频、话题和模板。它是方法框架，不识别推荐效应。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

Social media challenge several established concepts of memory research. In particular, the day-to-
day mundane discourse of social media blur the essential distinction between commemorative and
non-commemorative memory. We address these challenges by presenting a methodological frame-
work that explores the dynamics of social memory on various social media. Our method combines
top-down data mining with a bottom-up analysis tailored to each platform. We demonstrate the
application of our approach by studying how the Holocaust is remembered in different corpora,
including a dataset of 5.3 million Facebook posts and comments collected between 2015 and 2017
and a 5 million Tweets and Retweets dataset collected in 2021. We first identify the mnemonic
agents initiating the discussion of the memory of the Holocaust and those responding to it.
Second, we compare the macro-rhythms of Holocaust discourse on the two platforms, identifying
peaks and mundane discussions that extend beyond commemorative occasions. Third, we identify
distinctive language and cultural norms specific to the memorialization of the Holocaust on each
platform. We conceptualize these dynamics as ‘Mnemonic Markers’ and discuss them as potential
pathways for memory researchers who wish to explore the unique memory dynamics afforded by
social media.
Keywords: collective memory; social media; Holocaust; computational methods; cross-platform
analysis

### 方法

Systematic query design
Data mining through search or API
Network analyses
NLP tools
Temporal analysis
Platform
specificity
Platform-agnostic: the same search list can
be used across platforms
Platform-specific: illuminating platform
cultural dynamics
8
Anat Ben‐David et al.
https://doi.org/10.1017/mem.2024.18 Published online by Cambridge University Press

while the bigram ‘Adolf Eichmann’ clearly indicates a reference to the Holocaust, the
bigram ‘Six Million’ may capture other mentions of the number, unrelated to the number
of Jews murdered during the Holocaust. Hence, in that case, we anchored the bigram by
modifying the query to [‘Six Million’ AND ‘Holocaust’].
As previously noted, the process of query design involves a reflexive and iterative
evaluation of the selected starting points for data mining. We therefore sought to identify
the similarities and differences in the English and Hebrew lists, reflecting cultural distinc-
tions despite identical methods. Hence, for instance, terms such as ‘concentration camp’,
Figure 1. A flowchart outlining the steps of the methodological framework.
Memory, Mind & Media
9
https://doi.org/10.1017/mem.2024.18 Published online by Cambridge University Press

or names of perpetrators such as Adolf Eichmann appear in both the English and the
Hebrew lists. In contrast, the bigrams that appear only in the Hebrew list reflect some
of the unique characteristics of Israeli Holocaust commemoration culture: ‘like lambs to
the slaughter’ (a two-word phrase in Hebrew) is a derogatory term that was originally
used during Israel’s first decades to critique the supposed passive compliance of Jewish
victims
during
the
Holocaust.
Correspondingly,
the
English
list
features
American-centered terms and institutions such as the USC-based Shoah Foundation
(see Figure 2).
Mining social media data
Below, we illustrate two instances of utilizing the query lists to mine data from Facebook
and Twitter, conducted before the research API access was deprecated.1
In the first instance, we explored an existing dataset of Facebook posts and comments
initially collected for another purpose. In 2015, a custom server-side tool was developed to
extract data from Facebook’s Graph API (Ben-David and Soffer 2019). This tool enabled
researchers to select a public Facebook page and a time range for analysis. Automated
extraction was performed daily, gathering all posts and comments made by Israeli parlia-
ment members (MKs) who maintained a Facebook page during the period. A total of 47k
posts and 5.3M comments on the posts were collected between March 2015 and March
2017. We employed the Hebrew Holocaust query list to explore the database, obtaining
separate results for posts and comments. Results files were organized by query, and a
metadata file summarizing all queries was created.
In the second instance, we turned to Twitter to establish a real-time data collection
process for Holocaust-related content. The Twitter API was utilized to collect all
Figure 2. Unique and shared bigrams in the English and Hebrew query lists.
1 Social media platforms have recently mounted restrictions on data access for researchers, presenting signifi-
cant risks to the field of social media research. However, we posit that these challenges do not impact the essence
of a methodological approach for identifying memory work on social media. Despite API restrictions, alternative
methods such as web scraping remain viable (Freelon 2018).

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

Given the dataset size differences, our analysis focuses on identifying patterns in each lan-
guage space, highlighting similarities and differences. First, we examined the top query
distributions: both language spaces exhibit long-tail distributions, with the top Hebrew
bigrams being conjugations of ‘The Holocaust’ (14,222, 28.8%), ‘Adolf Hitler’ (12,543,
25.4%), and the Israeli term ‘Holocaust Day’ (8,470, 17.5%). In English, the discrepancy
was far more drastic, with ‘Adolf Hitler’ comprising roughly 51% (2,660,390) and ‘concen-
tration camp’ only 5.7% (see Figure 5).
The shared bigrams across languages indicate iconized commemoration vocabulary.
Several appear in both top rankings, but with considerable proportional variation:
while ‘The Holocaust’ ranks top in Hebrew, it is ranked 16th in English (39,223, 0.75%).
Other differing weights include ‘Six Million’ and ‘Concentration Camp’. Some bigrams
in the English top 20 like Oskar Schindler and Anne Frank do not appear in the
Hebrew top 20 bigrams, while Adolf Eichmann and Heinrich Himmler are frequent in
Hebrew but not English. Such findings require further qualitative, culturally anchored
exploration.
Next, we shifted attention to Twitter hashtags, a platform-specific affordance exem-
plifying mnemonic framing processes: Hashtagging anchors the past within the present
and vice versa, allowing users to present past events as analogies and reasons for
unfolding processes (Edy 1999); it fosters rapid generation of ‘loose’ online memory
communities, constantly reshaping users’ understanding of the past’s interrelations
with the present.
An initial top 10 hashtag exploration in the Hebrew and English datasets reveals strik-
ing differences (Table 3). The English top hashtags are commemorative and somber:
acknowledging remembrance dates (#HolocaustMemorialDay), extermination camps
(#Auschwitz), and moral lessons (#NeverAgain). The only exception to this commemora-
tive tendency is #TigrayGenocide, conjoining Holocaust memory and recent Tigray War
crimes – a non-commemorative mnemonic framing.
Four
leading
Hebrew
hashtags
(#HolocaustDay,
#WeRemember,
#Kristallnach,
#HolocaustRemebranceDay) frame Holocaust remembrance within commemorative con-
texts. In contrast, 6 of the top 10 Hebrew hashtags reflect current Israeli social issues,
such as #GoAway, which ties Holocaust memory to protests demanding the removal of
Prime Minister Benjamin Netanyahu. Critiques within #GoAway tweets highlighted and
mocked Netanyahu’s self-promotion during his 2021 MDHH Yad Vashem speech.
Similarly, #AshkenaziHatred hashtags connect Holocaust memory to tensions between
Israeli Jews of European (Ashkenazi) descent and Israeli Jews of Middle Eastern descent.
14
Anat Ben‐David et al.
https://doi.org/10.1017/mem.2024.18 Published online by Cambridge University Press

The hashtag #Processes reflects complex interactions between Israeli politics and
Holocaust memory, referring to a 2016 speech by Major General Yair Golan. In this speech,
Golan likened troubling trends in Israeli society to historical processes in 20th-century
Europe, sparking intense debate about the appropriateness of such comparisons. Some
tweets under #Processes directly engaged with Golan’s speech, debating its validity; in
another case, the police decision to investigate PM Netanyahu was Retweeted under
the hashtag #Processes with the added comment: ‘looks like the Gestapo has taken control
over the country’.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

This article aims to provide a comprehensive methodological framework to facilitate the
study of memory work across social media platforms. By merging platform-agnostic and
platform-specific elements, this framework can enhance discussions on how collective
memory is constructed on social media. Researchers can utilize a top-down issue mapping
process to create queries for various collective memory events or topics, then employ
bottom-up analyses to explore how these topics are debated, contested, and evolve
over time, along with the unique mnemonic vernacular that arises from user practices
and platform affordances. It is important to note that the bottom-up analyses are not
exhaustive. Once the top-down approach has demarcated a mnemonic space on social
media, various computational, qualitative, and quantitative methods can be employed
to address different research questions.
More generally, the proposed framework aims to locate those overarching high-level
affordances, or mnemonic dynamics that social media afford (Bucher and Helmond
2018), which we find necessary to advance digital memory studies. The scholarly under-
standing of what collective memory is and how collective memory is shaped directs
researchers at several fundamental questions concerning agency (who is socially permit-
ted, or encouraged to speak about the past? Who has the resources to do so?), platform
(how do the characteristics and affordances of venues or platforms influence the ways
in which the past is narrated?) and context (when is the past discussed? Why then?).
The implementation of our methodological framework helps address these fundamental
questions within the realm of social media by illuminating three high-level affordances
Figure 7. The temporal distribution of bigrams in the English Twitter dataset.
18
Anat Ben‐David et al.
https://doi.org/10.1017/mem.2024.18 Published online by Cambridge University Press

of social media memory work, which we term Mnemonic Markers: Directionality, Temporality,
and Vernacular.
Directionality refers to the discursive dynamics unfolding between those who initiate a
mnemonic discourse, and those reacting to it. A key affordance of many social media plat-
forms is the separation between the primary content (e.g. a post, video, article) and the
comments section below it. This architecture creates a dialectic space where content is
distinctly separated from the discourse around it (Ben-David and Soffer 2019). We suggest
that this distinction constitutes a fundamental element in shaping social media memory.
Our findings show institutional mnemonic agents address Holocaust memory on social
media in primary content spaces and directly related contexts. In contrast, ‘lay’ agents
address the Holocaust in varied contexts and for diverse purposes in both primary con-
tent and comment spaces.
The mnemonic discourse within comment spaces distinctly differs from that in main
content areas, where references to the Holocaust often emerge detached from the pri-
mary content. This difference in directionality – who starts the conversation, where,
and in what context, and who responds – helps identify non-commemorative memory
spaces where Holocaust discourse might not be anticipated.
Directionality as a high-level affordance aids researchers in understanding the complex
dynamics of initiation and response, as well as the interactions between different commu-
nicative agents.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Ben-David, A., Meyers, O., & Neiger, M. (2024). How social memory works on social media: A methodological framework. Memory, Mind & Media, 3, e20. https://doi.org/10.1017/mem.2024.18
- 本地正文：`文献全文/正文/A12_2024_社会记忆如何在社交媒体上运作：一个方法论框架__How social memory works on social media A methodological framework.pdf`
- 源URL：https://www.cambridge.org/core/services/aop-cambridge-core/content/view/57CC8FE3831C79B935FD63C6FC25DD44/S2635023824000183a.pdf/div-class-title-how-social-memory-works-on-social-media-a-methodological-framework-div.pdf
- 原文抽取：`../原文结构化抽取/A12_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
