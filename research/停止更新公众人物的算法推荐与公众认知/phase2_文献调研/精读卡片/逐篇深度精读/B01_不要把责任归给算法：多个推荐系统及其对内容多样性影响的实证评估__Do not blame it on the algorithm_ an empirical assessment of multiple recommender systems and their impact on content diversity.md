# B01｜不要把责任归给算法：多个推荐系统及其对内容多样性影响的实证评估

> 英文原题：*Do not blame it on the algorithm: an empirical assessment of multiple recommender systems and their impact on content diversity*  
> DOI：10.1080/1369118X.2018.1444076  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level III；学科适配综合评级 A。

## 一、文献一句话定位

core。要求本项目将“单一化”作为待测结果，而非推荐系统的必然后果。

## 二、研究背景

公共讨论常把个性化推荐与内容多样性下降直接联系，但不同推荐逻辑、多样性指标和内容库可能导致相反结果。

## 三、核心问题

多种新闻推荐系统相对编辑策展如何影响推荐集的内容多样性？个性化是否必然造成收窄？

## 四、理论基础与核心概念

以选择性曝光、过滤气泡与新闻多样性为理论背景，并将多样性拆分为多个可计算维度。

## 五、研究方法

使用荷兰大报实际内容（N=21,973）和用户（N=500）模拟多种推荐逻辑，与编辑策展比较多个多样性维度。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

对22,000余篇文章和500位用户的模拟显示，被测试的推荐逻辑并未必然降低多样性，基于用户历史甚至可提高推荐集内的主题多样性。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

在同一真实新闻库和用户数据上并列模拟多种推荐逻辑，直接反驳‘算法必然降低多样性’的过度概括。

## 八、局限性

设计能对“算法必然造成单一化”构成强反证；但新闻推荐模拟不等同于抖音的实际曝光反馈循环。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

本研究必须把‘单一化’设为待测结果，不能当作推荐必然后果。ABM应在同一内容供给上做因子消融，并同时报告标签、来源、语义和观点多样性，而非一个总指标。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

In the debate about filter bubbles caused by algorithmic news
recommendation, the conceptualization of the two core concepts
in this debate, diversity and algorithms, has received little
attention in social scientific research. This paper examines the
effect of multiple recommender systems on different diversity
dimensions. To this end, it maps different values that diversity can
serve, and a respective set of criteria that characterizes a diverse
information offer in this particular conception of diversity. We
make use of a data set of simulated article recommendations
based on actual content of one of the major Dutch broadsheet
newspapers and its users (N=21,973 articles, N=500 users). We find
that all of the recommendation logics under study proved to lead
to a rather diverse set of recommendations that are on par with
human
editors
and
that
basing
recommendations
on
user
histories
can
substantially
increase
topic
diversity
within
a
recommendation set.
ARTICLE HISTORY
Received 30 October 2017
Accepted 20 February 2018

### 方法

We present a first attempt of an empirical assessment of recommender diversity based on
the considerations outlined above. It should be noted that we are explicitly not researching
viewpoint diversity. As we are using a most similar experimental design, we rely on a set of
articles and recommendations from one newspaper, which limits the possibilities to study
ideological diversity or diversity in style. The focus of this study is, as outlined above,
topics (both in general, as the ‘politicalness’ of the topics). Taking these as examples,
we show how to construct a multi-dimensional feature space that allows us to assess
the diversity of recommendation sets. We then evaluate how different recommender sys-
tems perform on these criteria.
3.1. Research design
To study the influence of algorithmic design on diversity, we carry out a data-scientific
experiment. Specifically, we compare the output of different algorithmic news recommen-
dation for the same articles of the same news source (de Volkskrant, a Dutch progressive
high-quality newspaper, that is oriented towards the political center, see Figure 1). Our
dataset also includes recommendation sets for each of the articles that have been picked
by human editors. This provides us with a unique benchmark to evaluate the performance
of the recommender systems.
For N=1000 articles that were published between 19–9–2016 and 26–9–2016, we simu-
lated which three articles out of the pool of N=21,973 articles would be recommended if
one of the following logics were used:
(1) The choice of human editors
(2) The overall popularity
Figure 1. Recommendation box on the newspaper website. The recommendation box is displayed in
the top right corner (‘Aanbevolen artikelen’).
INFORMATION, COMMUNICATION & SOCIETY
965

(3) Collaborative filtering (item-to-item)
(4) Semantic filtering (item-to-item)
(5) Collaborative filtering (taking into account user histories)
(6) Semantic filtering (taking into account user histories)
(7) A random baseline, in which each article is equally likely to be recommended.
For the two algorithms that are based on user histories, we used the tracking history of
500 randomly selected news users.
3.2. Feature engineering
As the dataset contained rich information on each article (e.g. not only the full text, but
also a category label and topic tags), we could create multiple sets of features.
3.2.1. Topic distance
We used the package Gensim (Řehůřek & Sojka, 2010) to estimate a topic model. After
evaluating different models based on their perplexity and interpretability, we chose an
LDA model (Blei et al., 2003) with 50 topics based on tf · idf representations of the docu-
ments, with additional filtering of extremely common and extremely uncommon words.
We used pyLDAvis (see Sievert & Shirley, 2014) to perform multidimensional scaling
on the resulting topics. As a result, each topic can be represented by its coordinates
(x,y) in a two-dimensional space. As the Euclidian distance between two points is

(x2 −x1)2 + (y2 −y1)2

, and as each document D is represented by a vector ⃗
wD of 50
topic weights wD,1 · · · wD,50, we can calculate the topic distance between two documents.2
3.2.2. Category and tag distance
Another more recent approach is the use of word embeddings to capture the aggregate
inter-document difference, basically by considering the Wasserstein metric describing
the minimum effort to make two documents similar. This is called the word mover dis-
tance (WMD).

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

Given that for each document in the dataset we simulated three recommendations (see
also Figure 1), the diversity of a recommender system can be conceptualized in different
ways:
(1) on the level of the recommendation set, as the mean of the distances of each article
towards the original article;
INFORMATION, COMMUNICATION & SOCIETY
967

(2) on the level of the recommendation set, as the mean of the distances within the rec-
ommendation set;
(3) on the user level, as the diversity of the sets of all articles a user has ever been
recommended;
(4) on the level of the individual recommendation.
While all of these conceptualizations can offer valuable insights, we chose to present the
results of the last conceptualization, because it avoids averaging and aggregating. As we
have N=1000 origin articles ×3 recommendations, all following calculations are therefore
based on N=3000 ‘origin article’—‘recommended article’ pairs.
We start by looking at the descriptive statistics of the performance of the different
recommender systems. As Table 1 shows, first and foremost, differences between all sys-
tems seem to be rather limited in size. Across different operationalizations and analyses, all
of the recommendation logics under study proved to lead to a rather diverse set of
recommendations.
We can identify some notable tendencies, though. First of all, as one would expect,
the random recommender produces one of the most diverse recommendation sets. We
also see that the recommendations produced by the editors are not particularly diverse.
Especially if we look at the category, we see that editors tend to recommend articles
from the same or very similar categories. The results with regard to topic diversity
in the output of collaborative filtering are particularly interesting. If data on past
user preferences are not taken into account, collaborative filtering produces the least
amount of diversity. That means if the decision which articles to show is based on
the selection of other readers of the same article, it is likely that articles of the same
topic are presented. Yet, if users are matched on all articles they have read, we find col-
laborative recommendation systems are least likely to recommend a related topic. We
can conclude that in terms of topic diversity, tailoring can support diverse exposure, at
least in the short run.
However, the descriptive statistics in Table 1 might hide more subtle differences. For
instance, it might be the case that a recommender sometimes outputs very diverse rec-
ommendations, and sometimes recommendations that are not diverse at all, which
might cancel each other out. To get a better understanding of the differences, we therefore
plotted the distribution of our metrics.
As Figure 2 shows, the higher average diversity for the random baseline recommender,
but also the user-collaborative recommender, is mainly due to a much flatter distribution
with a fatter tail: Even though the peaks of all recommenders are very close to each other,
Table 1. Means and standard deviations distances between topics, tone, category, tags, and from the
word ‘politiek’.
Topic
Tone
Category
Tag
Politics
Collab. (item)
90.0 (55.1)
0.14 (0.15)
0.21 (0.23)
0.45 (0.11)
0.79 (0.02)
Semantic (item)
94.4 (56.9)
0.14 (0.14)
0.29 (0.24)
0.46 (0.10)
0.79 (0.02)
Popularity
95.6 (63.8)
0.13 (0.13)
0.00 (0.00)
0.45 (0.10)
0.80 (0.02)
Editors
91.3 (56.6)
0.14 (0.14)
0.10 (0.19)
0.43 (0.10)
0.80 (0.02)
Random
114.6 (68.1)
0.15 (0.15)
0.40 (0.18)
0.52 (0.08)
0.80 (0.02)
Collab.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

[未自动定位；不代表原文无此部分]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Möller, J., Trilling, D., Helberger, N., & van Es, B. (2018). Do not blame it on the algorithm: an empirical assessment of multiple recommender systems and their impact on content diversity. Information, Communication & Society, 21(7), 959–977. https://doi.org/10.1080/1369118x.2018.1444076
- 本地正文：`文献全文/正文/B01_2018_不要把责任归给算法：多个推荐系统及其对内容多样性影响的实证评…__Do not blame it on the algorithm an empirical assessment of multiple recommender systems and their impact….pdf`
- 源URL：https://pure.uva.nl/ws/files/23265204/Do_not_blame_it_on_the_algorithm.pdf
- 原文抽取：`../原文结构化抽取/B01_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
