# B19｜Twitter上的政治内容算法放大

> 英文原题：*Algorithmic Amplification of Politics on Twitter*  
> DOI：10.1073/pnas.2025334119  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level II；学科适配综合评级 A。

## 一、文献一句话定位

supporting。证明算法放大差异可在强对照下被观测，同时警告不要把“放大了谁”与“为什么放大”混为一谈。

## 二、研究背景

对算法政治偏向的外部研究往往缺少可观测对照，Twitter平台内部实验则能将排名流与倒时序流长期比较。

## 三、核心问题

个性化排名时间线相对倒时序时间线，如何放大七个国家主流政治人物与美国媒体内容？

## 四、理论基础与核心概念

以算法放大和政治偏向为框架，关键识别来自随机分配的排名/倒时序对照。

## 五、研究方法

Twitter平台内部大规模随机实验，对照组使用无个性化的倒时序流，并分析政治人物和美国媒体来源。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

在近200万日活账号的长期随机对照中，排名时间线在7国中的6国更放大主流右翼政党；但未支持算法更放大极端政治的通俗假设。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

在近200万日活账号上进行长期平台随机实验，对‘排序的额外放大’给出远强于外部抓取的识别。

## 八、局限性

随机分组为排名流与倒时序流的对照提供强识别；但作者明确说明网络干扰违反SUTVA、处理随时间变动，因而不能给出无偏的平均处理效应；精确驱动机制未识别，政治Twitter场景向死后名人的迁移也需谨慎。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

为本课题提供最清晰的反事实逻辑：同一供给下，个性化组相对倒时序组的额外集中才可归于排序。但原文明确承认网络干扰、处理变动与未识别驱动机制；也不可从政治Twitter直接外推抖音名人。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

Content on Twitter’s home timeline is selected and ordered by personalization algorithms. By consistently ranking certain content higher, these algorithms may amplify some messages while reducing the visibility of others. There’s been intense public and scholarly debate about the possibility that some political groups benefit more from algorithmic amplification than others. We provide quantitative evidence from a long-running, massive-scale randomized experiment on the Twitter platform that committed a randomized control group including nearly 2 million daily active accounts to a reverse-chronological content feed free of algorithmic personalization. We present two sets of findings. First, we studied tweets by elected legislators from major political parties in seven countries. Our results reveal a remarkably consistent trend: In six out of seven countries studied, the mainstream political right enjoys higher algorithmic amplification than the mainstream political left. Consistent with this overall trend, our second set of findings studying the US media landscape revealed that algorithmic amplification favors right-leaning news sources. We further looked at whether algorithms amplify far-left and far-right political groups more than moderate ones; contrary to prevailing public belief, we did not find evidence to support this hypothesis. We hope our findings will contribute to an evidence-based debate on the role personalization algorithms play in shaping political content consumption.

Political content is a major part of the public conversation on Twitter. Politicians, political organizations, and news outlets engage large audiences on Twitter. At the same time, Twitter employs algorithms that learn from data to sort content on the platform. This interplay of algorithmic content curation and political discourse has been the subject of intense scholarly debate and public scrutiny (1–15). When first established as a service, Twitter used to present individuals with content from accounts they followed, arranged in a reverse chronological feed. In 2016, Twitter introduced machine learning algorithms to render tweets on this feed called Home timeline based on a personalized relevance model (16). Individuals would now see older tweets deemed relevant to them, as well as some tweets from accounts they did not directly follow.
Personalized ranking prioritizes some tweets over others on the basis of content features, social connectivity, and user activity. There is evidence that different political groups use Twitter differently to achieve political goals (17–20). What has remained a matter of debate, however, is whether or not any ranking advantage falls along established political contours, such as the left or right (2, 7), the center or the extremes (1, 3), specific parties (2, 7), or news sources of a certain political inclination (21). In this work, we provide systematic quantitative insights into this question based on a massive-scale randomized experiment on the Twitter platform.
Experimental Setup
Below, we outline this experimental setup and its inherent limitations. We then introduce a measure of algorithmic amplification in order to quantify the degree to which different political groups benefit from algorithmic personalization.
When Twitter introduced machine learning to personalize the Home timeline in 2016, it excluded a randomly chosen control group of 1% of all global Twitter users from the new personalized Home timeline. Individuals in this control group have never experienced personalized ranked timelines.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 方法

The Timelines Quality Holdback Experiment.
Twitter has maintained the randomized experiment described in Experimental Setup since June 2016. Accounts were randomly assigned to treatment or control either at the experiment’s onset or at the time the account was created. As of 5 June 2020, the experiment included 58 million unique Twitter user IDs (58,087,969, 5% of all accounts globally), of which 20% (11,617,373) are assigned to control, and 80% (46,470,596) are assigned to the treatment group. About 12% of studied accounts (∼ 7 million) logged in within a single day of the study, and about 20% (∼ 12 million) logged in within a single week. More information about the tweet selection, presentation, and ranking in either group, as well as the services and machine learning models influencing the content that users are exposed to through their Home Timeline, is provided in SI Appendix, section 1.A.
Ethical and Data Protection Reviews.
The control group assessed was not created for the purpose of research but rather for the business purpose of improving the algorithm and providing a baseline to which it could be compared to monitor the ongoing performance of the algorithm. As such, this work was reviewed by Twitter’s legal and privacy teams as part of its ordinary business operations (and not an IRB). As part of this review, a data protection impact assessment was conducted, and it was determined that additional notice and consent mechanisms were not required.
Obtaining Legislators’ Twitter Details.
We identified countries to include in our analysis based on the following criteria: 1) availability of data on politicians’ Twitter accounts and 2) sufficient Twitter user base in the country. Screening for these criteria, we identified the following list of countries: United States, Japan, United Kingdom, France, Spain, Canada, Germany, and Turkey. Turkey was then excluded, due to limited availability of legislators’ accounts for the current, 27th term (only about 18% of current legislators had a valid Twitter account). To identify members of the current legislative term in each country, we relied on Wikidata, public Twitter lists, and official government websites. While, in most countries, we were able to identify Twitter details of over 70% of all representatives following automated methods, our goal was to ensure that potentially missing accounts would not result in poor representation of certain minority groups in our dataset. We, therefore, focused manual annotation efforts on ensuring that accounts of legislators who belong to certain underrepresented groups are included in our dataset. In most countries, we were able to retrieve gender labels from Wikidata to aid with this process.
To test various hypotheses about the types of political parties algorithms might amplify more, we make some direct comparisons between parties in each country. We rely on the 2019 Chapel Hill Expert Survey (29) and Wikidata annotations to determine the ideological position of each party. More information on the data collection process from the aforementioned resources and groupings of parties is provided in SI Appendix, section 1.B.
Media Bias Ratings.
We obtained media bias ratings for news sources from AllSides (33) and Ad Fontes Media (34). While the former includes news sources with a global audience, it focuses primarily on the US media landscape, and the media bias ratings relate to how the media bias of these sources is perceived in the United States.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

We divide our findings into two parts. First, we study tweets by elected politicians from major political parties in seven countries which were highly represented on the platform. In the second analysis, which is specific to the United States, we study whether algorithmic amplification of content from major media outlets is associated with political leaning.
We first report how personalization algorithms amplify content from elected officials from various political parties and parliamentary groups. We identified Twitter account details and party affiliation for currently serving legislators in seven countries from public data (25–28) (SI Appendix, section 1.B). The countries in our analysis were chosen on the basis of data availability: These countries have a large enough active Twitter user base for our analysis, and it was possible to obtain details of legislators from high-quality public sources. In cases where a legislator has multiple accounts—for example, an official and a personal account—we included all of them in the analysis. In total, we identified 3,634 accounts belonging to legislators across the seven countries (the combined size of legislatures is 3,724 representatives). We then selected original tweets authored by the legislators, including any replies and quote tweets (where they retweet a tweet while also adding original commentary). We excluded retweets without comment, as attribution is ambiguous when multiple legislators retweet the same content. When calculating amplification relating to legislators, we considered their reach only within their respective country.
To compare the amplification of political groups, we can either calculate the amplification of all tweets from the group (group amplification; Fig. 1 A and B) or calculate amplification of each individual in the group separately (individual amplification; Fig. 1C). The latter yields a distribution of individual amplification values for each group, thus revealing individual differences of amplifying effects within a group.
Fig. 1.
￼
Open in a new tab
Amplification of tweets from major political groups and politicians in seven countries with an active Twitter user base. (A) Group amplification of each political party or group. Within each country, parties are ordered from left to right according to their ideological position based on the 2019 Chapel Hill Expert Survey (29). A value of 0% indicates that tweets by the group reach the same number of users on ranked timelines as they do on chronological timelines. A value of 100% means double the reach. Error bars show SE estimated from bootstrap. Bootstrap resampling was performed over daily intervals as well as membership of each political group. (B) Pairwise comparison between the largest mainstream left- and right-wing parties in each country: Democrats vs. Republicans in the United States, Constitutional Democratic Party of Japan (CDP) vs. Liberal Democratic Party (LDP) in Japan, Labor vs. Conservatives in the United Kingdom, Socialists vs. Republicans in France, Spanish Socialist Worker’s Party (PSOE) vs. People’s Party (Partido Popular) in Spain, Liberals vs. Conservatives in Canada, and Social Democratic Party (SPD) vs. alliance of Christian Democratic Union and Christian Social Union (CDU/CSU) in Germany. In six out of seven countries, these comparisons yield a statistically significant difference, with right being amplified more, after adjusting for multiple comparisons. In Germany, the difference is not statistically significant.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 讨论与结论

We presented a comprehensive audit of algorithmic amplification of political content by the recommender system in Twitter’s home timeline. Across the seven countries we studied, we found that mainstream right-wing parties benefit at least as much, and often substantially more, from algorithmic personalization than their left-wing counterparts. In agreement with this, we found that content from US media outlets with a strong right-leaning bias are amplified marginally more than content from left-leaning sources. However, when making comparisons based on the amplification of individual politician’s accounts, rather than parties in aggregate, we found no association between amplification and party membership.
Our analysis of far-left and far-right parties in various countries does not support the hypothesis that algorithmic personalization amplifies extreme ideologies more than mainstream political voices. However, some findings point at the possibility that strong partisan bias in news reporting is associated with higher amplification. We note that strong partisan bias here means a consistent tendency to report news in a way favoring one party or another, and does not imply the promotion of extreme political ideology.
Recent arguments that different political parties pursue different strategies on Twitter (14, 15) may provide an explanation as to why these disparities exist. However, understanding the precise causal mechanism that drives amplification invites further study that we hope our work initiates.
Although it is the largest systematic study contrasting ranked timelines with chronological ones on Twitter, our work fits into a broader context of research on the effects of content personalization on political content (2, 3, 9, 21) and polarization (35–38). There are several avenues for future work. Apart from the Home timeline, Twitter users are exposed to several other forms of algorithmic content curation on the platform that merit study through similar experiments. Political amplification is only one concern with online recommendations. A similar methodology may provide insights into domains such as misinformation (39, 40), manipulation (41, 42), hate speech, and abusive content.
Materials and Methods
The Timelines Quality Holdback Experiment.
Twitter has maintained the randomized experiment described in Experimental Setup since June 2016. Accounts were randomly assigned to treatment or control either at the experiment’s onset or at the time the account was created. As of 5 June 2020, the experiment included 58 million unique Twitter user IDs (58,087,969, 5% of all accounts globally), of which 20% (11,617,373) are assigned to control, and 80% (46,470,596) are assigned to the treatment group. About 12% of studied accounts (∼ 7 million) logged in within a single day of the study, and about 20% (∼ 12 million) logged in within a single week. More information about the tweet selection, presentation, and ranking in either group, as well as the services and machine learning models influencing the content that users are exposed to through their Home Timeline, is provided in SI Appendix, section 1.A.
Ethical and Data Protection Reviews.
The control group assessed was not created for the purpose of research but rather for the business purpose of improving the algorithm and providing a baseline to which it could be compared to monitor the ongoing performance of the algorithm. As such, this work was reviewed by Twitter’s legal and privacy teams as part of its ordinary business operations (and not an IRB).

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

We then introduce a measure of algorithmic amplification in order to quantify the degree to which different political groups benefit from algorithmic personalization.
When Twitter introduced machine learning to personalize the Home timeline in 2016, it excluded a randomly chosen control group of 1% of all global Twitter users from the new personalized Home timeline. Individuals in this control group have never experienced personalized ranked timelines. Instead, their Home timeline continues to display tweets and retweets from accounts they follow in reverse chronological order. The treatment group corresponds to a sample of 4% of all other accounts who experience the personalized Home timeline. However, even individuals in the treatment group do have the option to opt-out of personalization (SI Appendix, section 1.A).
The experimental setup has some inherent limitations. A first limitation stems from interaction effects between individuals in the analysis (22). In social networks, the control group can never be isolated from indirect effects of personalization, as individuals in the control group encounter content shared by users in the treatment group. Therefore, although a randomized controlled experiment, our experiment does not satisfy the well-known Stable Unit Treatment Value Assumption from causal inference (23). As a consequence, it cannot provide unbiased estimates of causal quantities of interest, such as the average treatment effect. In this study, we chose to not employ intricate causal inference machinery that is often used to approximate causal quantities (24), as this would not guarantee unbiased estimates in the complex setting of Twitter’s home timeline algorithm. Building an elaborate causal diagram of this complex system is well beyond the scope of our observational study. Instead, we present findings based on simple comparison of measurements between the treatment and control groups. Intuitively, we expect peer effects to decrease observable differences between the control and treatment groups; thus, our reported statistics likely underestimate the true causal effects of personalization.
A second limitation pertains to the fact that differences between treatment and control groups were previously used by Twitter to improve the personalized ranking experience.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

## 十一、题录与证据指针

- APA 7：Huszár, F., Ktena, S. I., O’Brien, C., Belli, L., Schlaikjer, A., & Hardt, M. (2022). Algorithmic amplification of politics on Twitter. Proceedings of the National Academy of Sciences, 119(1), e2025334119. https://doi.org/10.1073/pnas.2025334119
- 本地正文：`文献全文/正文/B19_2022_Twitter上的政治内容算法放大__Algorithmic Amplification of Politics on Twitter.html`
- 源URL：https://pmc.ncbi.nlm.nih.gov/articles/PMC8740571/
- 原文抽取：`../原文结构化抽取/B19_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
