# B05｜Twitter推荐系统的众包审计

> 英文原题：*Crowdsourced audit of Twitter’s recommender systems*  
> DOI：10.1038/s41598-023-43980-4  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level IV；学科适配综合评级 A。

## 一、文献一句话定位

core。提供了“曝光相对用户自选关注的放大比”这一可迁移的算法作用指标。

## 二、研究背景

木偶账号审计可控性强但缺少真实用户历史；众包数据捐赠则可比较算法时间线与用户自选关注所形成的可选帖文池。

## 三、核心问题

Twitter算法时间线相对用户的关注选择，对同社群账号、情绪化/毒性内容及政治立场产生了什么额外曝光？

## 四、理论基础与核心概念

以算法放大、选择性曝光和人—算法反馈为背景，核心可操作化是‘呈现内容/用户可选内容池’的相对放大。

## 五、研究方法

志愿者浏览器扩展采集真实时间线，结合Twitter API重建其可选帖文池，比较算法呈现与关注关系。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

Twitter算法时间线相对用户订阅选择，更强地放大同社群账号、情绪化/毒性帖文，并在政治倾向上不均衡。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

用志愿者浏览器扩展捕捉真实时间线，再用API重建可选池，为排序的边际贡献提供比单看热门帖文更好的参照。

## 八、局限性

真实用户数据弥补了木偶审计的行为真实性；作者明确不声称解开复杂的社会—算法反馈回路。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

本课题最值得迁移的指标是‘曝光相对供给的放大比’。如能通过用户数据捐赠获取抖音推荐流，应同时建立当时张雪峰相关内容供给池；但即便如此，人—算法循环仍不能被完全解开。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

[未自动定位；不代表原文无此部分]

### 方法

Context
Our analysis was conducted prior to the release of the overall architecture and partial source codes of Twitter’s 
recommender systems on March 31, 2023, a preliminary pre-print can be found at hal-04036232v2. The current 
analysis has been re-performed over a more recent timeframe, specifically 07/03/23-06/04/23 for account-level 
features and 14/01/23-07/02/23 for tweet-level features, as explained below. Among the numerous hard-coded 
heuristics and general insights, Twitter engineers have specifically highlighted the significance of community 
detection in the recommendation ­process9. In light of this, we have conducted an additional analysis to examine 
OPEN
1CNRS, Complex Systems Institute of Paris Île-de-France (ISC-PIF), 75013 Paris, France. 2EHESS, Center for Social 
Analysis and Mathematics (CAMS), 75006 Paris, France. *email: paul.bouchaud@iscpif.fr

2
Vol:.(1234567890)
Scientific Reports | (2023) 13:16815 | 
https://doi.org/10.1038/s41598-023-43980-4
www.nature.com/scientificreports/
whether tweets from friends belonging to the same community as the participant are amplified compared to 
those from different communities.
Data collection
We developed a browser-extension called “Horus”, compatible with Chrome and Firefox, that allows us to capture 
various data, including Twitter feeds, displayed on participants’ desktop screens. The participants were self-
selected, they chose to take part in the study after becoming aware of it through newspaper articles and radio 
broadcasts in the fall of 2022. To expand our reach and attract a wider range of individuals, we also employed 
online advertising on Twitter, presenting the initiative and encouraging individuals to participate. In addition 
to contributing to scientific research, the primary incentive for participants to install the extension was receiv-
ing a personalized report on the political diversity of their Twitter friends and their curated feed. This report 
was sent to volunteers once a sufficient amount of data had been collected. Prior to the data collection process, 
participants were fully informed about the study’s objectives, the specific data that would be collected, and their 
informed consent was obtained. Following this, the extension started gathering the participants’ Twitter feed.
Our cohort is not representative of the Twitter audience in terms of devices usages —the data collection, 
performed through a desktop browser extension, is filtering out mobile users— demographics or socioeconomic 
status. We do not claim that our study’s findings can be extrapolated to the entire Twitter population. Neverthe-
less, we argue that the sanity of a platform should be maintained across devices and users’ behavior, justifying 
external audits —even partial ones like ours. We provide in Supplementary Information various statics regarding 
our cohort of participant, both demographics and on their Twitter usages. Furthermore, we present how political-
group-wise, our set of participant does not significantly differ from a random sampling of Twitter French users, 
in terms of their friends political leaning distribution.
Taking the participants having been active on the desktop version of Twitter between March 3, 2023, and 
April 6, 2023 as our only objects of study, the analysis has been performed on N = 463 participants. On aver-
age, our participants followed 682 [22,2712] accounts (5-95 percentiles).

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

Twitter algorithmic curation increases authors’ representation inequality
As a first, high level, illustration of the shaping power of the recommender on what is seen by Twitter users, 
we evaluated the Gini coefficient over the number of tweets published and impressed by participants’ friends. 
We find that despite an already highly unequal situation (Gini coefficient of friends’ publications of .72 [.56,.87] ) 
in which the 10% most active participants’ friends publishes more than half of the entire set of participants’ 

4
Vol:.(1234567890)
Scientific Reports | (2023) 13:16815 | 
https://doi.org/10.1038/s41598-023-43980-4
www.nature.com/scientificreports/
friend tweets, Twitter’s recommender system increases the Gini coefficient by 14% on average (Gini coefficient 
of friends’ impression of .83 [.59,.99] ). The tweets from the 10% most shown friends represent more than 70% of 
participants’ friends impressions in their timelines. We display in the Supplementary Information the associated 
Lorenz curves.
Small and quiet accounts benefit from higher algorithmic amplification
As displayed on Fig.  1, tweets of accounts having less than 576 followers (first decile) are amplified by 
+97.5 [34.7.2,182.7] % . Put differently, the proportion of tweets authored by small accounts is twice larger in the 
timelines than in the overall pool of messages authored by participants’ friends. Conversely, tweets of accounts 
with a number of followers larger than 110k are lessen by −9.8 [−16.9,−2.9] % . Similarly, tweets of accounts hav-
ing published on average less than 1.4 tweets per week since their creation (first decile) are significantly ampli-
fied when they do publish, with an amplification of +162.4 [45.5.2,318.7] % . The tweets of highly active accounts, 
more than 10 tweets per day on average, are lessen by −21.8 [−25.3,−17.9] % . We display in the Supplementary 
Information the number of followers/tweets distributions associated to out-of-networks tweets. For 85.5% of 
the participants, the number of follower distribution of out-of-networks author is stochastically smaller than 
for participants’ set of friends.
Algorithmic curation affects the political landscape
After having estimated the political leaning of participants’ friends by analyzing their retweets of political content, 
we segmented the participants based on their own political orientation; as self-declared through a form crossed 
with their Twitter friends orientation. Our findings reveal that for participants leaning towards the far-left (N=51) 
and left/center-left (N=92), Twitter’s recommender system amplifies ideologically aligned friends, see Fig. 2A,B.
As display on Fig. 2A, for far-left participants, the messages published by far-left friends are ampli-
fied by +21.8 [5.0,42.6] % . The amplification decreases as the opinion difference increases, until it reaches 
−11.2 [−32.8,12.4] % for right leaning accounts’ tweets. Similarly, for left/center-left participants the tweets stem-
ming from further-left or from right-leaning friends are algorithmically lessen, respectively by −10.2 [−27.7,7.4] % 
and −31.4 [−45.7,−19.9] % , while tweets from ideologically aligned friends are amplified +21.1 [10.6,32.6] % , see 
Fig. 2B. Interestingly, for center-right participants (N=33), see Fig. 2C, the opposite effect is noticed, ideologi-
cally aligned accounts tweets are lessened by −23.8 [−43.9,−2.6] % , while far-left and further right tweets are highly 
amplified, respectively by +44.1 [−28.1,145.6] % and +88.0 [31.3,168.0] % .

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

The partial open-sourcing of Twitter’s recommender systems revealed a convoluted blend of deep-learning 
models and hand-crafted ­heuristics21. For example, Twitter incorporates mechanisms such as relevance decay 
based on the age of tweets and the assignment of reputation scores to user based on their number of followers 
and a variant of the PageRank algorithm. Twitter inclination to amplify tweets authored by small or usually quiet 
accounts may then been seen as an attempt to diversify users’ feeds, preventing them from being dominated by 
spam or overly popular content. While this approach gives every user an opportunity to be heard, it also raises 
concerns about potential astroturfing practices, where individuals artificially boost their online presence through 
numerous small, fake accounts.
At the level of individual tweets, it’s reasonable to hypothesize that toxic tweets are favored by the recom-
mender system due to their higher engagement rates in terms of replies and likes, leading to high amplification 
Figure 3.   Amplification of tweets depending of their of engagement rate (B). We display the amplification for 
tweets having no engagement and binned in dodeciles the remainging engagement rates. Error-bars correspond 
to 95% bootstrap confidence interval of the amplification. The bold line corresponds to zero amplification.

7
Vol.:(0123456789)
Scientific Reports | (2023) 13:16815 | 
https://doi.org/10.1038/s41598-023-43980-4
www.nature.com/scientificreports/
of such content. However, it’s noteworthy that, despite the recommender’s focus on engagement, popular tweets 
eventually cease to be recommended. This phenomenon may be attributed to Twitter’s design, which prioritizes 
the promotion of new content and sustains user engagement by favoring recent discussions. This balance between 
promoting popular content and encouraging a diverse range of recent content can result in situations where 
highly popular tweets are no longer recommended.
Additionally, we observe that Twitter’s recommender system tends to favor tweets from accounts within the 
same community as the user. Accounts within these communities often share common ­interests9, a characteristic 
leveraged by Twitter in the recommendation ­process10. It’s important to note that our intention is not to take a 
normative stance on the value of exposure to diverse viewpoints, as an extensive literature has comprehensively 
explored this ­topic22–24. Instead, we highlight that algorithmic amplification may run counter to users’ choices, 
if not by concealing “dissonant” content, by overwhelmingly amplifying consonant one. Similarly, our analysis 
reveals that Twitter’s recommender system presents a political landscape different from the one users actively 
subscribed to. Considering the overall objective function of Twitter’s recommender system, we hypothesize 
that these patterns of amplification are the one found to maximized user engagement. One could argue that the 
observed deviations between user subscriptions and displayed content align with user preferences. However, 
Milli et al’s recent study revealed that users were less likely to prefer the political tweets selected by engagement-
based algorithms compared to reverse chronological ­timelines7, highlighting the disparity between stated and 
revealed preferences.
Our audit underscores the systemic effects of Twitter’s recommender system on the information landscape 
portrayed to users, resulting in more toxic timelines and affecting the mutual representation of political groups.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Bouchaud, P., Chavalarias, D., & Panahi, M. (2023). Crowdsourced audit of Twitter’s recommender systems. Scientific Reports, 13, Article 16815. https://doi.org/10.1038/s41598-023-43980-4
- 本地正文：`文献全文/正文/B05_2023_Twitter推荐系统的众包审计__Crowdsourced audit of Twitter’s recommender systems.pdf`
- 源URL：https://www.nature.com/articles/s41598-023-43980-4.pdf
- 原文抽取：`../原文结构化抽取/B05_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
