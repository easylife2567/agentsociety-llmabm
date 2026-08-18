# B09｜谁来审计审计者？算法审计生态系统实地扫描的建议

> 英文原题：*Who Audits the Auditors? Recommendations from a field scan of the algorithmic auditing ecosystem*  
> DOI：10.1145/3531146.3533213  
> 精读状态：已根据本地保存正文、结构化原文抽取和已核验题录完成；本文档不代表用户本人已亲读。  
> 证据等级：Level VI；学科适配综合评级 B。

## 一、文献一句话定位

supporting。为抖音黑箱研究的可行性、独立性与透明度局限提供方法治理背景。

## 二、研究背景

算法审计快速扩张，但审计者的独立性、标准、数据权限和问责能力并不统一。

## 三、核心问题

当前算法审计生态由哪些人和组织构成，他们遇到哪些制度障碍，应如何建立更可信的审计机制？

## 四、理论基础与核心概念

主要是算法问责、审计独立性和生态系统治理框架，而非对某个推荐模型的理论检验。

## 五、研究方法

实地扫描438人和189个组织，匿名问卷N=152，并访谈10位行业领导者。

### 方法论解读

- 识别能力只按原设计判定：实验/随机对照可支持相应因果命题；观察、访谈、民族志、网络路径或概念分析不被升格为排序因果证据。
- 与当前课题的外部效度需另行判断：非抖音、非名人死后、非低熟悉度受众的设计，均不直接外推。

## 六、主要发现

算法审计生态尚未标准化；受访审计者常遭遇被审计方不配合、无执法力、保密协议和难以纳入真实伤害等障碍。

### 可支持的命题边界

本文直接支持的是上述特定研究对象、数据与结果变量之间的结论。除非原设计本身包含平台随机对照，否则不将其表述为‘推荐算法导致’；除非结果变量直接测量人物印象，否则不将其表述为‘受众形成了单一化印象’。

## 七、创新点与核心价值

通过大规模实地扫描、问卷与领导者访谈描绘审计产业全景，把‘谁有资格审计’也纳入问责。

## 八、局限性

覆盖面广但对平台推荐不是直接效果证据；调查对象为审计生态参与者。

### 对局限的保守处理

本节只采用作者明言的局限，或可由其样本、平台、时间窗口和设计直接判定的外推边界。未在原文或设计中找到根据的批评不写成作者自述。

## 九、对当前研究的启示

未来对抖音的审计必须披露账号、设备、地点、交互脚本、采集期和失败情形，并承认平台不配合时的可见性边界。它不提供张雪峰案例的直接效果证据。

### 可借鉴之处

- 变量或指标：优先迁移本文已明确操作化的概念，但在中文抖音语境中重新做效度检验。
- 设计：保留原文的对照逻辑、数据层级和时间维度，不只借用结论。
- 边界：始终分开内容供给、推荐曝光、用户选择、再分发与受众印象。

## 十、原文证据摘录（用于回查）

> 以下保留英文原文，是对上述中文转述的核验层，不是额外的中文推论。摘录为定长节选，完整上下文请回到原正文。

### 摘要

[未自动定位；不代表原文无此部分]

### 方法

We first conducted a field scan that yielded a list of 438 individuals from 189 organizations that we identified as involved,
to some degree, in AI auditing. This list included first-, second-, and third-party auditors as well as members of civil
society and advocacy organizations, academic researchers, regulators involved with AI audit legislation and policy, and
others involved in audit-related work. From this list, we identified 10 leaders in the field for semi-structured interviews;
interviewees are described in Table 1.3 Based on our understanding of the field and lessons from our interviews, we
then developed a survey that we shared with contacts at all 189 organizations identified in the field scan. Overall,
we received 152 individual survey responses. Table 2 summarizes our survey respondents: 56 (37%) of respondents
indicated that they had personally participated in an audit of an AI system. Of those, 12 were first parties, 16 were
3All interviewees were offered the option to receive attribution or remain anonymous. Interviewees who wished to receive attribution are identified by
name; interviewees who wished to remain anonymous are identified only as R1, R2, R3, and R4. Interviewees were provided with transcripts after the
interviews to verify that all quotes were accurately recorded; anonymous interviewees were also given the option to redact potentially identifying quotes.
See Appendix A.2 for more information on interview methods.

6
Costanza-Chock, Harvey, Raji, Czernuszenko, and Buolamwini
second parties, and 11 third parties (respondents could select multiple roles). The auditors had collective experience
assessing algorithmic systems in industries including technology and social media, hiring and HR, consumer goods, and
insurance and credit, as well as for state and local governments. The full list of identified individuals and organizations,
the structured interview guide, and the survey questions can be found in the Appendices.
3.1
Limitations
Several factors potentially limit the accuracy and generalizability of our findings. First, our respondents may not be
representative of the entire population of AI auditors. Only 56 survey respondents self-identified as having worked
directly on audits. Additionally, a number of AI audits were published after our survey closed; we were not able to
invite all of the authors of these new audits to participate in our study. Our survey responses came primarily from
respondents in the US (n=90), UK (n=16), and EU (n=18); we only received one response each from auditors in Africa,
Asia, and South America, and no responses from auditors in Australia. Our team is based in the US, our materials and
outreach were all in English, and we did not systematically attempt to identify and include auditors from all regions of
the world. There is a clear need for future research that focuses on algorithmic audits in the Global South.
Since the very meaning of algorithmic audits is up for debate, our decision to focus on professionalized auditors also
influences our findings, as we did not systematically include those working on other approaches to auditing such as
community-based, participatory, or evocative audits. As previously mentioned, there is active discussion and debate
about different approaches to evaluation of AI systems. For example, some argue that AI impact assessments are a more
effective accountability mechanism than audits, or that red teams should be the preferred approach [8, 53].

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 结果

[未自动定位；不代表原文无此部分]

### 讨论与结论

Overall, three major themes emerged from our research. First, we find that the algorithmic audit ecosystem, while
nascent, is growing rapidly. Based on the number of individuals (N = 438) and organizations (N = 189) we identified as
involved in AI audits, we expect that the need to establish standards and regulatory oversight to reduce discrepancies
between auditors’ desired best practices and reality will only become more pressing. Second, there is a consensus among
practitioners that current regulation is lacking, as well as agreement about some areas that require mandates. Auditors and
non-auditors alike overwhelmingly agree that AI audits should be mandated (95%), and that the results of these audits,
in part or in full, should be disclosed (82%). Auditors also near-universally report that their largest barriers are lack
of buy-in from auditees to conduct audits in the first place, and that even when they have buy-in, they have limited
enforcement capabilities. Finally, we find a mismatch between what auditors say is important to conducting audits and
what they actually do. Auditors often want to disclose their results and methods, but are restricted by nondisclosure
agreements. Many express interest in intersectional analysis (65%), but worry that by gathering the demographic data
necessary to demonstrate disparate impacts, they may run afoul of anti-discrimination law. Similarly, although many
auditors consider analysis of real-world harm (65%) and inclusion of stakeholders who may be directly harmed (41%) to
be important in theory, they rarely put this into practice.
5.2
Policy Recommendations
Based on the findings outlined above, we propose six policy recommendations that we believe should be prioritized: 1)
require both owners and operators of AI systems to engage in independent audits against clearly defined standards; 2)
require that individuals be notified when they are subject to algorithmic decision-making; 3) mandate disclosure of
key components of audit findings for peer review; 4) consider real-world harm in the audit process, including through
standardized harm incident reporting and response mechanisms; 5) directly involve the stakeholders most likely to
be harmed by AI systems in the AI audit process; and 6) formalize evaluation and, potentially, accreditation of AI
auditors. The first four have broad support from auditors and non-auditors alike; the last two are more controversial
among audit practitioners. Each recommendation has implications for lawmakers and regulators as they craft bills

Who Audits the Auditors?
13
and regulatory mechanisms to govern AI systems, for private companies as they develop internal policies, and for
standards-setting bodies and professional associations as they organize consensus around standards and best practices.
Our recommendations are intended as core ideas, rooted in lessons from the existing community of practice. Future
work will be required to link these to existing policy, to develop practical recommendations for implementation, and to
develop additional domain-specific standards.
5.2.1
Require audits for AI system owners and operators. AI auditors are in near-universal agreement (95%) that audits
should be a required element of owning and operating AI systems. Across the board, auditors say that their most
important regulatory priority is to establish legislation that requires companies to engage in AI auditing. They also
rank “lack of buy-in from potential auditees to conduct an audit in the first place” as their biggest barrier.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

### 限制

Several factors potentially limit the accuracy and generalizability of our findings. First, our respondents may not be
representative of the entire population of AI auditors. Only 56 survey respondents self-identified as having worked
directly on audits. Additionally, a number of AI audits were published after our survey closed; we were not able to
invite all of the authors of these new audits to participate in our study. Our survey responses came primarily from
respondents in the US (n=90), UK (n=16), and EU (n=18); we only received one response each from auditors in Africa,
Asia, and South America, and no responses from auditors in Australia. Our team is based in the US, our materials and
outreach were all in English, and we did not systematically attempt to identify and include auditors from all regions of
the world. There is a clear need for future research that focuses on algorithmic audits in the Global South.
Since the very meaning of algorithmic audits is up for debate, our decision to focus on professionalized auditors also
influences our findings, as we did not systematically include those working on other approaches to auditing such as
community-based, participatory, or evocative audits. As previously mentioned, there is active discussion and debate
about different approaches to evaluation of AI systems. For example, some argue that AI impact assessments are a more
effective accountability mechanism than audits, or that red teams should be the preferred approach [8, 53]. We sought
to include practitioners who use different language and framing in their work to evaluate AI systems, but may have
inadvertently excluded some who do not agree with the ‘audit’ framing. Finally, although we firmly believe that the
question ‘who audits?’ matters, in this study we did not collect auditors’ demographic information. We believe that
future work to systematically explore the demographics of algorithmic auditors is necessary.
4
KEY FINDINGS
4.1
Methods and Tools Used to Audit AI Systems
4.1.1
Quantitative over qualitative.
“Any good AI audit has to have some sort of measurable, code-based aspect to it.” – Interview with R1,
internal audit lead at a social media company
AI auditors who completed our survey are more likely to report engaging in quantitative audit methods than critical,
structural, or qualitative ones. As depicted in Fig.

[摘录达到长度上限；详见同编号《原文结构化抽取》及正文。]

## 十一、题录与证据指针

- APA 7：Costanza-Chock, S., Raji, I. D., & Buolamwini, J. (2022). Who Audits the Auditors? Recommendations from a field scan of the algorithmic auditing ecosystem. 2022 ACM Conference on Fairness Accountability and Transparency, 1571–1583. https://doi.org/10.1145/3531146.3533213
- 本地正文：`文献全文/正文/B09_2022_谁来审计审计者？算法审计生态系统实地扫描的建议__Who Audits the Auditors Recommendations from a field scan of the algorithmic auditing ecosystem.pdf`
- 源URL：https://arxiv.org/pdf/2310.02521
- 原文抽取：`../原文结构化抽取/B09_原文抽取.md`
- 转述原则：‘作者发现’只指原文直接报告；‘对当前研究的启示’是本项目的二次推论，两者不得混写。
