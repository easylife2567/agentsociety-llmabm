# A09｜情绪的网络传播：名人自杀后社交媒体转发动力研究

> 英文原题：*Online propagation of emotions: A study of resharing dynamics on social media following celebrity suicides*  
> DOI：10.1371/journal.pone.0336134  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level IV；学科适配综合评级 B。

## 一、文献一句话定位

core。为死亡后哪些情绪化片段更容易获得用户再分发提供供给侧机制。

## 二、研究背景

名人自杀会触发大规模社交媒体讨论，但不同离散情绪的内容可能有不同的转发级联速度、规模和寿命。

## 三、核心问题

名人自杀事件后，不同情绪如何影响帖文再分发级联的广度、深度、速度、持续时间与爆发性？

## 四、理论基础与核心概念

文章以情绪传播与信息级联为核心，使用离散情绪而非单一正负价性理解再分发动力。

## 五、研究方法

对超过100万条推文与转发的完整数据集进行BERT情绪识别，用回归分析级联规模、生命期、速度与爆发性。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

四起名人自杀事件后，不同离散情绪表现出不同转发级联特征：厌恶传播快、广且持久，愤怒与惊讶快但短，恐惧较弱。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

在四起名人自杀事件的百万级数据上，将BERT情绪分类与多维级联特征联系，比只比较转发数更细致。

## 八、局限性

大样本计算观察设计；能识别内容情绪与再分发的关联，无法把效应特定归因于推荐算法。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

可用于为张雪峰死后内容建立情绪传播特征，并在ABM中设置不同情绪的转发概率与寿命。但原研究不能区分情绪吸引的用户选择与平台排序，因而不能直接当作推荐效应参数。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

Emotional contagion on social media, particularly following shocking and tragic 
events, often unfolds through widespread resharing, amplifying affective responses 
that are typically intense and negative. This study focuses on the context of celebrity 
suicides, which have the potential to trigger emotional contagion and lead to adverse 
behavioral outcomes, such as copycat suicides. Using an exhaustive Twitter dataset 
covering four celebrity suicides, we theorize the propagation of emotional content 
through a valence-arousal framework, distinguishing emotions based on affective 
valence (positive or negative) and physiological arousal (high or low). We analyze 
how distinct emotions embedded in tweets propagate through retweet cascades, 
treating each tweet and its retweets as a single cascade. Propagation is measured 
across four cascade dimensions: size, lifetime, speed, and burstiness. Emotions are 
extracted from over a million tweets and retweets using a BERT-based language 
model and are used as predictors in regression analyses of the propagation metrics. 
Our results show that emotional messages propagate in distinct ways after tragic 
events. Disgust emerges as the most contagious emotion, spreading quickly, widely, 
and with longevity, while fear, despite its arousal, spreads weakly. Anger and surprise 
generate fast but short-lived cascades marked by high burstiness. Joy, though less 
frequent, endures longer than neutral and negative content, reflecting resilience but 
with lower burstiness. These findings advance research on online emotional propaga­
tion by demonstrating that discrete emotions differ significantly even within the same 
valence–arousal characteristic. They also offer insights for public health strategies to 
mitigate risks linked to emotional amplification in digital environments.

### 方法

[未自动定位；不代表原文无此部分]

### 结果

Cascade size
The average cascade size is 5.36 (SD = 40.2), indicating substantial variation in diffusion patterns. To address the 
over-dispersed nature of the count data, we employed a negative binomial regression model [86] and, for comparison, fit­
ted a Poisson model to the independent variables. As cascades expand and reach wider audiences, the likelihood of addi­
tional reshares increases, suggesting that the dynamics of large cascades differ meaningfully from those of small ones. 
Accordingly, we analyzed two subsets of data: (1) the full sample of 91,868 cascades, where a single retweet corresponds 
to a cascade size of 2 (including the original tweet), and (2) cascades with three or more posts (size ≥ 3), totaling 30,637 
observations. The regression results for cascade size across these subsets are reported in Table 5. We acknowledge that 
sampling on the dependent variable may limit generalizability. The size threshold was set to improve construct validity by 
focusing on cascades that show meaningful network diffusion beyond isolated or incidental reshares. This approach helps 
reduce noise from the large number of trivial cascades that dominate the distribution.
Table 5.  Regression results on the lifetime and size of cascades.
DV: Cascade Size Negative Binomial Model
DV: Log (Lifetime) OLS Model
Size ≥ 2
Size ≥ 3
Size ≥ 2
Size ≥ 3
(1)
(2)
(3)
(4)
(5)
(6)
(7)
(8)
Emotion: Anger
−0.057***
−0.042
−0.155***
−0.200***
Emotion: Fear
−0.099***
−0.103***
−0.075***
−0.100**
Emotion: Sadness
−0.081***
−0.076***
−0.003
−0.052
Emotion: Joy
−0.087***
−0.095***
0.190***
0.252***
Emotion: Disgust
0.622
0.858**
0.215*
0.208***
Emotion: Surprise
−0.038
0.007
−0.174***
−0.223***
# Auth. Followers (Log)
0.332***
0.336***
0.317***
0.325***
0.429***
0.427***
0.399***
0.398***
# Auth. Friends (log)
−0.110***
−0.109***
−0.094***
−0.092***
−0.157***
−0.157***
−0.125***
−0.125***
# Auth. Tweets (log)
−0.123***
−0.125***
−0.126***
−0.130***
−0.343***
−0.339***
−0.366***
−0.361***
# Auth. Likes (log)
0.037***
0.033***
0.043***
0.036***
0.048***
0.047***
0.062***
0.061***
Auth. Verified?
0.820***
0.818***
0.585***
0.571***
0.887***
0.886***
0.507***
0.505***
Wordcount
0.011***
0.009***
0.018***
0.014***
0.012**
0.012**
0.021**
0.020**
Hashtag?
−0.005
0.046
−0.028
0.044
0.127***
0.162***
0.072
0.113**
Celebrity: JS
−0.061***
−0.039**
−0.116***
−0.060**
0.045**
0.048***
−0.004
0.009
Celebrity: LTY
−0.017
0.024***
−0.043**
0.036***
0.366***
0.371***
0.627***
0.643***
Celebrity: TS
−0.278***
−0.243***
−0.369***
−0.297***
0.547***
0.548***
0.501***
0.512***
Intercept
0.437**
0.488***
0.806***
0.832***
3.178***
3.186***
4.048***
4.069***
Observations
91,868
91,868
30,637
30,637
91,868
91,868
30,637
30,637
Adjusted R2
–
–
–
–
0.162
0.164
0.244
0.246
Log Likelihood
−207,590
−206,767
−92,816
−92,346
–
–
–
–
Akaike Inf. Crit
415,202
413,569
185,655
184,726
–
–
–
–
Note: *p < 0.1; **p < 0.05; ***p < 0.01; The standard errors in this linear regression model are clustered on the celebrity suicide event; hence, four clusters 
are created. Negative Binomial regression results are generated using the MASS library in R.
https://doi.org/10.1371/journal.pone.0336134.t005

PLOS One | https://doi.org/10.1371/journal.pone.0336134  December 10, 2025
17 / 27
Emotions demonstrate a variety of effects on cascade size (Table 5, Models 2 & 4). Prior studies have typically exam­
ined emotions as just positive and negative, but we note that there are nuances amongst negative emotions.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

The advent of online social media is unparalleled in that it is a medium by which individuals’ thoughts, emotions, and 
opinions are exposed to the world in real time and on a global scale. A social media platform is a venue where social the­
ory is enacted on a global scale. Therefore, analyzing its content offers important insights into human society, especially 
because it affects the behavior and opinions of those exposed to the media. Of relevance to the current research is how 
messages that carry emotional content spread through this global platform and reach others by being reshared through 
a chain of resharing actions by individual users. The underlying premise is that content diffusion differs depending on its 
emotional content. By analyzing a large dataset of Twitter posts (currently known as X) following tragic and unexpected 
events, i.e., four celebrity suicides, we uncover interesting patterns of content diffusion and link those patterns to the emo­
tion within the posts.
Emotional dynamics on social media are complex, as emotions embedded in online content can propagate and spread 
through resharing across large user populations [10,21]. In the case of celebrity suicides, such propagation is especially 
consequential because it may contribute to behavioral contagion, most notably the “Werther Effect,” where exposure to 
suicide-related content is associated with increased risk of copycat suicides [24,26]. Prior research has established that 
celebrity suicides correlate with rises in suicide rates, and the rapid scale and speed of resharing on social media suggest 
that these risks may be amplified in digital environments [23,25,63]. Our study contributes to this body of work by exam­
ining emotional propagation in the aftermath of celebrity suicides, offering evidence on a potential mediating mechanism 
through which exposure to emotional content may exacerbate vulnerability in audiences. These insights provide a founda­
tion for stakeholders, including public health policymakers, to design more targeted mitigation and prediction strategies in 
the wake of shocking and tragic events.
Supporting information
S1 Appendix. Conceptual clarification and data description. 
(DOCX)
S2 Appendix. Validation of emotion labels. 
(DOCX)
Author contributions
Conceptualization: Ehsan Nouri, Nilesh Saraf.
Data curation: Ehsan Nouri, Jie Mein Goh.

PLOS One | https://doi.org/10.1371/journal.pone.0336134  December 10, 2025
24 / 27
Formal analysis: Ehsan Nouri.
Funding acquisition: Nilesh Saraf, Srabana Dasgupta, Dianne Cyr.
Investigation: Ehsan Nouri, Jie Mein Goh, Srabana Dasgupta.
Methodology: Ehsan Nouri, Jie Mein Goh, Srabana Dasgupta.
Project administration: Nilesh Saraf, Dianne Cyr.
Resources: Nilesh Saraf, Dianne Cyr.
Software: Ehsan Nouri, Nilesh Saraf.
Supervision: Nilesh Saraf, Jie Mein Goh.
Validation: Ehsan Nouri, Nilesh Saraf, Jie Mein Goh, Srabana Dasgupta.
Visualization: Ehsan Nouri.
Writing – original draft: Ehsan Nouri, Nilesh Saraf.
Writing – review & editing: Ehsan Nouri, Nilesh Saraf, Jie Mein Goh, Srabana Dasgupta.

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Ehsan Nouri, Nilesh Saraf, Jie Mein Goh, Srabana Dasgupta, Dianne Cyr (2025). Online propagation of emotions: A study of resharing dynamics on social media following celebrity suicides. PLOS One. https://doi.org/10.1371/journal.pone.0336134
- 本地正文：`文献全文/正文/A09_2025_情绪的网络传播：名人自杀后社交媒体转发动力研究__Online propagation of emotions A study of resharing dynamics on social media following celebrity suicides.pdf`
- 源URL：https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0336134&type=printable
- 原文抽取：`../原文结构化抽取/A09_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
