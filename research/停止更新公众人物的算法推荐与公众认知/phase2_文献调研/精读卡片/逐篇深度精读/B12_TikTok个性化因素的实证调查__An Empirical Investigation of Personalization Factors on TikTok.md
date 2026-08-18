# B12｜TikTok个性化因素的实证调查

> 英文原题：*An Empirical Investigation of Personalization Factors on TikTok*  
> DOI：10.1145/3485447.3512102  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level III；学科适配综合评级 A。

## 一、文献一句话定位

core。直接支持机制链中“观看和互动会改变后续曝光”；也显示显性选择与隐性行为需分开建模。

## 二、研究背景

TikTok的增长与‘For You’个性化信息流密切相关，但早期公开研究对哪些用户特征与交互会改变推荐缺少受控检验。

## 三、核心问题

语言、位置、关注、点赞和观看时长是否会改变TikTok推荐，在所测因素中哪些影响更强？

## 四、理论基础与核心概念

以个性化、协同过滤和过滤气泡为背景，主要贡献是因素隔离式的木偶审计，而非完整的平台理论。

## 五、研究方法

受控木偶账号审计；每个情景约20次运行，活动账号与控制账号配对，用Jaccard重叠等指标比较信息流。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

语言、位置、关注、点赞和观看时长都会影响TikTok推荐；在所测因素中，关注影响最强，其次为点赞和视频观看率。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

建立成对的活动/对照木偶账号，每次尽量只改变一个个性化因素，并用帖文、标签、创作者和声音的Jaccard重叠测量信息流分化。

## 八、局限性

控制性强，但木偶行为、Web端、实验时段和平台更新限制生态效度。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

它直接支持在ABM中分开建模关注、点赞和观看时长，也为抖音审计提供成对账号范式。但这些是2022年TikTok Web端、特定时段的相对结果，不可直接当作当前抖音权重。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

TikTok currently is the fastest growing social media platform with
over 1 billion active monthly users of which the majority is from
generation Z. Arguably, its most important success driver is its
recommendation system. Despite the importance of TikTok’s algo-
rithm to the platform’s success and content distribution, little work
has been done on the empirical analysis of the algorithm. Our work
lays the foundation to fill this research gap. Using a sock-puppet
audit methodology with a custom algorithm developed by us, we
tested and analysed the effect of the language and location used to
access TikTok, follow- and like-feature, as well as how the recom-
mended content changes as a user watches certain posts longer than
others. We provide evidence that all the tested factors influence
the content recommended to TikTok users. Further, we identified
that the follow-feature has the strongest influence, followed by the
like-feature and video view rate. We also discuss the implications
of our findings in the context of the formation of filter bubbles on
TikTok and the proliferation of problematic content.
CCS CONCEPTS
• Information systems →Personalization; Collaborative fil-
tering; World Wide Web.

### 方法

In this section we outline the general setup of the sock-puppet
auditing experiments we conducted to assess the influence of dif-
ferent personalization factors on TikTok that was applicable to all
experimental setups, regardless of the specific factors analyzed. Dis-
tinct factor-specific characteristics of the experimental setups are
mentioned in the next section separately for each personalization
factor-related experimental group. Same applies to the description
of the analytical strategy.
3.1
Data Collection
In order to empirically test the influence of different factors on
the recommendation algorithm of TikTok, we needed to create
a fully controlled environment so we can isolate all the external
personalization factors except the one we are testing in any given
experimental setup [18]. Virtual agent-based auditing (or "sock-
puppet" auditing [46]) is an appropriate methodology for creating
such an environment while mimicking realistic user behaviour to
assess the effects of different personalization factors [17, 51]. Thus,
we created a custom web-based bot (virtual agent with scripted
actions) that is able to log in to TikTok, scroll through the posts of
its "For You" feed and interact with them, e.g. like a post. Similar
to Hussein and Juneja [25], our program ran the ChromeDriver
in incognito mode to establish a clean environment by removing
any noise resulting from tracked cookies or browsing history that
may originate from the machine on which the bot program was
executed. The source code can be accessed on GitHub 3.
The scripted actions of the bot were executed as follows: first
the program initialized a Selenium Chrome Driver session4 with
browser language set to English per default (depending on the test
scenario, we adjusted the language; see details in Table 1), navigated
to the TikTok website (https://www.tiktok.com), logged in as a
specific user (login verification step was completed manually; we
describe how user accounts were created below), and handled a set
of banners to assure an error-free interaction with the user’s "For
You" feed; then it scrolled through a pre-specified number of posts
and executed actions such as following or liking (as scripted for a
specific experiment and "run" (execution round) of the program);
while scrolling through the "For You" feed, the bot retrieved the
posts’ metadata from the website’s source code and extracted more
data from the request responses. In the testing rounds ahead of the
deployment of the bots we established that every time TikTok’s
website was accessed it automatically preloaded about 30 posts
to be displayed on the "For You" feed. Hereafter we refer to such
groups of 30 posts as batches. As soon as the pre-specified number
3https://github.com/mboeke/TikTok-Personalization-Investigation
4In order to obscure the automated interaction of our bot program we followed the
suggestions of Louis Klimek’s article [29].
of batches5 was scrolled through, the bot paused the last video
and terminated the ChromeDriver session once all requested data
was temporally stored to avoid unintentional interaction with the
TikTok’s feed. Afterwards all the data was stored in a PostgreSQL
database hosted on Heroku. During our experiment we operated
five local machines, four ran Windows 10 Pro and one macOS; as
two users that were compared with each other (see below) always
ran from the same local machine, the between-machine differences
had no potential effect on our results. All machines were connected
to the remote database.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

All machines were connected
to the remote database.
For each run of the bot, we scripted a set of specifications which
defined the characteristics of each run, e.g. web-browser language,
test user, number of batches to scroll through etc. According to Yi,
Raghavan, and Leggetter [56], web services can identify a user’s
location through their IP address. We therefore have assigned a
dedicated proxy with a specific IP address to every test user due
to three reasons: (1) every test shall be performed at a certain
location, (2) to obscure the automated interaction, and (3) to link a
specific IP address to a specific test user. We utilized proxies from
WebShare 6 and acquired phone numbers from Twilio7 to setup
user accounts. We utilized user phone numbers instead of email-
addresses as those would require a completion step on the mobile
application. Similarly to [18, 20, 25], every test user was manually
created using its dedicated proxy and incognito mode to reduce
the influence of any external factors. Every machine executed one
program run at a time which consisted of two bot programs being
executed in parallel.
As noted in the Introduction, we aimed to establish the influence
of several user actions and characteristics on TikTok’s RS and thus
the personalization on the platform’s "For You" feed. We focus
on the influence of the most explicit actions and characteristics
(tested factors): following a content creator, liking a post, watching
a post longer, and the language and location settings. To assess their
influence on TikTok’s RS, we conducted several experiments using
the bot program as outlined above. We describe the experiments
related to each of the tested factors below.
3.2
Experiment Overview
We created one experimental group with different experimental
scenarios for every tested factor. For every scenario we have per-
formed about 20 different runs which mainly consisted of two users
(bots) executing scripted actions on one local machine in parallel.
One of the two was the active and the other the control user. The
active user performed a certain action, e.g. liking a post, while the
control user only scrolled through the same number of batches as
its twin user, looking at each post the same amount of seconds. We
thus followed an approach similar to Hannak et al. [18] and Feuz,
Fuller, and Stalder [16] by creating a second (control) user, that is
identical to the active user except one specific characteristic/action
- one of the tested personalization factors, - in order to measure the
difference of the users’ feeds by comparing the meta-data of the
posts that both saw. If the posts on the feeds vary and do so more
than we would expect due to inherent random noise (see [18]), the
53 by default for all experiments, though for some 5 batches were collected, as noted
below and in Table 1.
6www.webshare.io
7www.twilio.com

Boeker & Urman
difference can be attributed to the personalization of the recommen-
dation algorithm of TikTok triggered by the tested factor. Every test
scenario was executed twice a day, although the execution order
varied, until all 20 test runs were completed.
3.3
Data Analysis
In order to analyse the results of our experiment we used four
different analysis approaches.
First, we analyzed the difference between the feeds of two users
by utilizing the Jaccard Index to measure the overlaps between
posts, hashtags, content creators, and sounds between that each
of the users encountered on their feed.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

In the past decade algorithmic personalization has become ubiqui-
tous on social media platforms, heavily affecting the distribution
of information there. The recommendation algorithm behind Tik-
Tok’s "For You" page is arguably one of the major factors behind
the platform’s success [57]. Given the popularity of the platform
[5, 37], the fact that its largely used by younger users who might
be more vulnerable in the face of problematic content [54], as well
as the central role TikTok’s RS plays in the content distribution, it
is important to assess how user behaviour affects one’s "For You"
page. We took the first step in this direction. In this section we
outline the implications of our findings as well as the directions for
future work.
Our analysis revealed that following action has the largest in-
fluence on the content served to the users among the examined
factors. This is important since following is a conscious action, as
contrasted for example to mere video viewing which could happen
by accident or be affected by unconscious predispositions. One
can watch something without necessarily liking what they see,
especially in the case of disturbing or problematic content. Hence,
according to our results users have some control over their feed
through explicit actions. At the same time, we find that video view
rate has a similar level of importance to the RS as liking action.
This can be problematic: while likes can be easily undone and users
unfollowed, one can not "unwatch" a video, thus the influence of
VVR on the algorithm severely limits the users’ control over their
data and the behaviour of the algorithm. Given the proliferation of
extremist content on the platform and TikTok’s insofar insufficient
measures to limit the spread of problematic content [54] as well as
the high degree of randomization in the videos served to a user as
identified by us, one can be potentially driven into filter bubbles
filled with harmful and radicalizing content by simply lingering
over problematic videos for a little bit too long. To alleviate this, we,
similarly to [54, 57], suggest that TikTok should do more to filter
out problematic content. Additionally, the platform could provide
users with more options to control what appears in their feeds. For
example, TikTok could add a list of inferred user interests avail-
able for control and adjustments to the user itself. TikTok already
enables its users to update their video interests via settings, but
only within few superficial categories. We suggest to provide a con-
sistently updated list of inferred user interests using very detailed
content categories based on which the user can always identify
which interests the TikTok RS inferred from their interaction with
the app. The user should also be able to adjust the list. According
to [36] and [48], such an overview would seriously increase the
degree of transparency and, thus, would benefit not only the user,
but also TikTok.
The impressive accuracy of TikTok’s recommender system (RS)
mentioned by the literature (e.g. [4, 12, 30, 57]), could be used
to effectively communicate important messages such as those on
COVID-19 countermeasures [10], or place appropriate advertise-
ments. However, such tools can also be easily misused for political
manipulation [55], [34], [24] or distributing hate speech [54]. This
can be exacerbated by the closed-loop relationship between users’
addiction to the platform and algorithmic optimization [57] or filter
bubbles.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Boeker, M., & Urman, A. (2022). An Empirical Investigation of Personalization Factors on TikTok. Proceedings of the ACM Web Conference 2022, 2298–2309. https://doi.org/10.1145/3485447.3512102
- 本地正文：`文献全文/正文/B12_2022_TikTok个性化因素的实证调查__An Empirical Investigation of Personalization Factors on TikTok.pdf`
- 源URL：https://arxiv.org/pdf/2201.12271
- 原文抽取：`../原文结构化抽取/B12_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
