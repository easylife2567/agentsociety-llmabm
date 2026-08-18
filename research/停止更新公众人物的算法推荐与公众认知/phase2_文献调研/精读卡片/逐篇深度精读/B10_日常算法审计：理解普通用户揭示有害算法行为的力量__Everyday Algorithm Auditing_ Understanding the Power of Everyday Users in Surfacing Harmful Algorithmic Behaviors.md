# B10｜日常算法审计：理解普通用户揭示有害算法行为的力量

> 英文原题：*Everyday Algorithm Auditing: Understanding the Power of Everyday Users in Surfacing Harmful Algorithmic Behaviors*  
> DOI：10.1145/3479577  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level VI；学科适配综合评级 B。

## 一、文献一句话定位

supporting。支持将普通用户的“为什么又看到这个片段”经验作为审计线索，但需与系统采集交叉。

## 二、研究背景

正式审计通常依赖预定义指标，而普通用户可能凭借日常情境经验首先发现不合理或有害的算法行为。

## 三、核心问题

普通用户如何在不掌握算法技术细节的情况下发现、聚合并推动公众审查有害的算法行为？

## 四、理论基础与核心概念

提出everyday algorithm auditing（日常算法审计），重视情境化知识、集体意义建构与自下而上问责。

## 五、研究方法

分析Twitter图像裁剪、平台评分等多个现实世界的日常算法审计案例。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

普通用户能依凭情境化经验发现正式审计容易遗漏的伤害，且这种发现不要求用户了解算法的技术细节。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

把用户经验从‘不可靠抱怨’重新定位为发现审计问题和隐藏伤害的认识资源。

## 八、局限性

案例法适合发现问题与变量，不足以估计算法的一般平均效应。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

可将用户‘为什么总看到这个梗’的叙述用于发现变量和选择审计路径，但不能单独当作排序因果证据。应与数据捐赠、平台抓取和受众实验交叉。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

[未自动定位；不代表原文无此部分]

### 方法

We set out to understand what we can learn from existing everyday algorithm audits in order
to inform the design of platforms and tools that can better support these practices. Thus, we
asked: How can we better understand the characteristics, dynamics, and progression of everyday
auditing practices? How can we support everyday users in detecting, reporting, and theorizing
about problematic machine behaviors during the course of their interactions with algorithmic
systems?
In order to understand the nascent phenomenon of everyday algorithm auditing, we adopted
an exploratory case study approach [69], examining several recent, prominent cases. We began
with a small set of high-profile cases that at least one of the co-authors was already familiar with.
We iteratively reviewed and discussed these known cases to form the initial idea of “everyday
algorithm auditing”. Through this process, we generated related keywords (e.g., “auditing,” “testing,”
“algorithm,” “algorithmic,” “bias,” “harm,” “users,” “collective,” and “community”). Next, we searched
news media (e.g., Google News, Google Search) and social media (e.g., Twitter, Facebook) using
combinations of these keywords to get a rough sense for the scope of this phenomenon. The search
9

yielded 15 cases (see Table 1) that met our definition for everyday algorithm auditing: one or
more everyday users act to detect, understand, and/or interrogate biased and harmful algorithmic
behaviors through their everyday use of a platform. These cases span multiple algorithmic do-
mains, including image captioning, image search, machine translation, online rating/review, image
cropping, credit scoring, and advertising and recommendation systems. We reference these cases
throughout the paper to ground our discussion in concrete examples. However, this set of cases
is by no means comprehensive. Furthermore, as discussed in our Design Implications section, we
expect that these existing cases represent only a thin slice of what is possible for everyday algorithm
audits in the future. At this exploratory stage, our aim is to begin formalizing this concept, to help
guide future empirical and design research in this space.
Case Selection: To support depth as well as breadth in our analysis of everyday algorithm
audits, we chose a small subset of four cases to examine in greater detail. To select these cases, we
iteratively extracted patterns from our initial dataset through a series of discussions among our
research team. We set out to choose a set of cases that a) span multiple domains and vary along the
three dimensions outlined in the Scope and Boundaries section (algorithmic expertise, collectiveness,
organicness) and b) were accessible to us via multiple data sources (e.g., user discussion posts, news
articles, research studies), enabling a rich analysis.
In particular, we chose two different domains that each have each been the target of everyday
algorithm audits in recent years: image cropping algorithms and rating platform algorithms. Within
each domain, we examined two cases that vary across the three dimensions discussed above to
support comparison. Figure 1 summarizes the four cases, visualizing varying degrees along each
dimension. For example, there are highly collaborative, less collaborative, and individual levels of
collectiveness among the four cases. In addition, these cases span multiple levels of algorithmic
expertise and organicness. The cases serve as illustrative examples to better understand how
everyday audits can work, what paths they can take, and what impacts they can have.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

[未自动定位；不代表原文无此部分]

### 讨论与结论

We have taken initial steps to theorize and explore an under-studied phenomenon in which everyday
users detect, interpret, question, and bring attention to problematic machine behaviors in their day-
to-day interactions with algorithms. We argue that such “everyday algorithm auditing” is especially
powerful in detecting harmful behaviors that are challenging for existing auditing approaches
discussed in the academic literature. In this section, we discuss the unique power and contributions
of everyday algorithm auditing and raise a few open questions on how to better support it for
future research.
8.1
The Power of Everyday Algorithm Auditing
Past research has highlighted the limitations and blindspots of existing auditing approaches and
speculated that everyday users might be able to overcome these limitations (e.g., [29, 48]). In this
paper, we take a step further by studying how such user-led audits unfold in the real world and by
exploring how we might better support these processes. Through detailed case studies, we have
shown that everyday users are able to detect harmful algorithmic behaviors that are challenging for
traditional auditing approaches and that users can exercise agency and autonomy in directing their
own auditing process. Below we highlight a number of unique contributions of everyday algorithm
auditing and how it can help overcome some of the limitations presented in existing approaches.
First, everyday algorithm auditing leverages the lived experiences of everyday users. Past literature
suggests that existing approaches often fail to involve auditors with relevant cultural backgrounds
and lived experience that are critical to detect sensitive harms [99]. Everyday algorithm auditing,
with contextually situated users, is especially powerful to appropriately identify the problems at
hand. Although a crowdsourced/collaborative auditing approach [74] also invites users’ partici-
pation, it often relies on crowdworkers, who do not necessarily have lived experiences with the
23

algorithms being audited, do not communicate and work together toward a common goal, and
therefore might not be sensitive to the related harms.
Second, everyday algorithm auditing harnesses the situated knowledge of everyday users. As past
literature suggests, many harmful machine behaviors are challenging to detect outside of situated
contexts of use [17, 33, 48, 60, 78]. Through their day-to-day interactions with an algorithmic
system, everyday users are particularly well positioned to detect these types of behaviors that
emerge in real-world contexts of use, in the presence of complex social dynamics, and in the
changing norms and practices of using algorithmic systems over time.
Third, in an everyday algorithm audit, users are able to form counterpublics via different social
media channels or community forums and participate in their own collective sensemaking and
consensus building. This is especially powerful since only in such collective attempts, will users be
able to build on each others’ contributions, test each others’ hypotheses, and support each other in
different forms (e.g., helping publicize their efforts). In contrast, in a crowdsourced/collaborative
audit [74], users are often working on individualized tasks that have been assigned to them, without
participating in discussion.
Finally, in an everyday algorithm audit, users have control over the auditing process.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

[未自动定位；不代表原文无此部分]

## 十一、题录与证据指针

- APA 7：Shen, H., DeVos, A., Eslami, M., & Holstein, K. (2021). Everyday Algorithm Auditing: Understanding the Power of Everyday Users in Surfacing Harmful Algorithmic Behaviors. Proceedings of the ACM on Human-Computer Interaction, 5(CSCW2), 1–29. https://doi.org/10.1145/3479577
- 本地正文：`文献全文/正文/B10_2021_日常算法审计：理解普通用户揭示有害算法行为的力量__Everyday Algorithm Auditing Understanding the Power of Everyday Users in Surfacing Harmful Algorithmic Be….pdf`
- 源URL：https://arxiv.org/pdf/2105.02980
- 原文抽取：`../原文结构化抽取/B10_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
