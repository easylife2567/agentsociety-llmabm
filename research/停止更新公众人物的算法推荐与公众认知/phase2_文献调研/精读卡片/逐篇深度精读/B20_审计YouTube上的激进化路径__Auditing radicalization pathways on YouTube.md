# B20｜审计YouTube上的激进化路径

> 英文原题：*Auditing radicalization pathways on YouTube*  
> DOI：10.1145/3351095.3372879  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level IV；学科适配综合评级 A。

## 一、文献一句话定位

supporting。强调“推荐可达路径”、“用户实际迁移”和“算法因果”是三个不同层次。

## 二、研究背景

YouTube激进化争论常把可达的推荐路径当作用户被算法推动迁移的证明，但路径、实际迁移和因果需要分开。

## 三、核心问题

YouTube上的用户是否从较温和的社群迁移到更极端社群，推荐网络中又存在哪些可达路径？

## 四、理论基础与核心概念

以在线激进化、社群迁移和推荐路径为框架，结合用户评论轨迹与视频/频道推荐网络。

## 五、研究方法

分析330,925个视频、349个频道、7200万+评论和200万+视频/频道推荐。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

用户会从较温和社群迁移到更极端社群；推荐路径分析显示Alt-lite可从I.D.W.视频达到，Alt-right主要通过频道推荐可达。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

在33万余视频、7200万余评论和200万余推荐边上，同时测量用户纵向迁移与平台可达结构。

## 八、局限性

规模大、用户迁移和推荐路径分析丰富；观察到的时序迁移不能单独证明推荐导致激进化。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

本课题也必须区分：某个梗在推荐链上可达、新用户实际被反复曝光、曝光使其印象改变。三者需要不同数据，推荐网络不能代替受众实验。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

Non-profits, as well as the media, have hypothesized the existence
of a radicalization pipeline on YouTube, claiming that users system-
atically progress towards more extreme content on the platform.
Yet, there is to date no substantial quantitative evidence of this
alleged pipeline. To close this gap, we conduct a large-scale audit of
user radicalization on YouTube. We analyze 330,925 videos posted
on 349 channels, which we broadly classified into four types: Media,
the Alt-lite, the Intellectual Dark Web (I.D.W.), and the Alt-right. Ac-
cording to the aforementioned radicalization hypothesis, channels
in the I.D.W. and the Alt-lite serve as gateways to fringe far-right
ideology, here represented by Alt-right channels. Processing 72M+
comments, we show that the three channel types indeed increas-
ingly share the same user base; that users consistently migrate
from milder to more extreme content; and that a large percentage
of users who consume Alt-right content now consumed Alt-lite
and I.D.W. content in the past. We also probe YouTube’s recom-
mendation algorithm, looking at more than 2M video and channel
recommendations between May/July 2019. We find that Alt-lite con-
tent is easily reachable from I.D.W. channels, while Alt-right videos
are reachable only through channel recommendations. Overall, we
paint a comprehensive picture of user radicalization on YouTube.
CCS CONCEPTS
• Human-centered computing →Empirical studies in collab-
orative and social computing.

### 方法

[未自动定位；不代表原文无此部分]

### 结果

[未自动定位；不代表原文无此部分]

### 讨论与结论

We performed a through analysis of three YouTube communities
— the I.D.W., the Alt-lite, and the Alt-right — inspecting a large
dataset with millions of comments and recommendations from
thousands of videos. In this section, we discuss how the insights of
our analyses shed light into our research questions. We also talk
about the limitations and potential implications of this work.
RQ1. How have these channels grown on YouTube in the last
decade? The three communities studied sky-rocketed in terms of
views, likes, videos published and comments, particularly, since
2015, coinciding with the presidential election of that year, as shown
in Sec. 4. However, this seems to be the case not only for these
communities, but also for the larger channels in the media group.
A key difference between the communities and media channels lies
in the engagement of their users. The number of comments per
view seems to be particularly high for extreme content (Sec. 4), and
users in all three communities are more assiduous commentators
than in the media channels (Sec. 5).
RQ2. To which extent do users systematically gravitate to-
wards more extreme content? We find that the commenting user
bases for the three communities are increasingly similar (Sec. 5), and,
considering Alt-right channels as a proxy for extreme content, that
a significant amount of commenting users systematically migrates
from commenting exclusively on milder content to commenting on
more extreme content (Sec. 7). We argue that this finding provides
significant evidence that there has been, and there continues to be,
user radicalization on YouTube, and our analyses of the activity
of these communities (Sec. 4) is consistent with the theory that
more extreme content “piggybacked” on the surge in popularity
of I.D.W. and Alt-lite content [30]. We show that this migration
phenomenon is not only consistent throughout the years, but also
that it is significant in its absolute quantity. Noticeably, the find-
ings related to this research question make the implicit assumption
that commenting users are a good enough proxy for radicaliza-
tion, and that comments in YouTube channels are supportive of
the videos they are associated with. We established the validity of
these assumptions as follows. First, the sheer number of comments
and high prevalence of comments per views in Alt-right videos
suggest that commenting users are a population worth studying,
especially when in Sec. 4 we found that Alt-right channels have
a very high percentage of comments per view. Secondly, during
the three week annotation period, it was noted that the number of
opposing comments is rather small, as we found by manually check-
ing 900 randomly selected comments (300 for each community of
interest), finding that only 5 could be interpreted as criticisms to
the videos they were associated with. Moreover, we note that the
proportion of likes for the communities of interest is higher for
the communities of interest (> 91% mean, > 96% median) than for
the media channels (85% mean, 93% median), which suggests the
people interacting with the three communities agree with their
videos.
RQ3. Do algorithmic recommendations steer users towards
more extreme content? Our simulations suggest that YouTube’s
recommendation algorithms frequently suggest Alt-lite and I.D.W.
content. From these two communities, it is possible to find Alt-right
content from recommended channels, but not from recommended
videos. Noticeably, our analysis has several shortcomings which
do not allow us to make bold claims about this research question.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Ribeiro, M. H., Ottoni, R., West, R., Almeida, V. A. F., & Meira, W. (2020). Auditing radicalization pathways on YouTube. Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency, 131–141. https://doi.org/10.1145/3351095.3372879
- 本地正文：`文献全文/正文/B20_2020_审计YouTube上的激进化路径__Auditing radicalization pathways on YouTube.pdf`
- 源URL：https://arxiv.org/pdf/1908.08313
- 原文抽取：`../原文结构化抽取/B20_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
