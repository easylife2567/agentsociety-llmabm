# 二（二）数据来源与预处理：作者确认定稿

作者于2026-10-15明确采用本次批注选中的版本，并要求同时保存逐句链和写法说明。本文件保留该版本的中英文正文、论证链和写作说明；没有换用随后以省略“本研究”起句为主要调整的润色版本。选中来源为聊天消息`msg_0033e0b94a77e4de016ad089570fe48191a91225d843fe9f54`中的两段。

正式中文正文对应[主稿二（二）](../../../paper/manuscript/manuscript.accepted.md)。状态和交接统一见[本run README](README.md)。正文仅包含下面两个“中文对照”段落；论证链、逐句链与写法说明作为写作依据保留在本文件。

## 完整论证链

全文后续叙述顺序：数据采集与预处理 → 现实分析回答研究问题（1）并提出机制问题 → 仿真回答研究问题（2）（3） → 综合结论 → 理论与现实意义扩展。

本节论证链：确定观察范围与分析单位 → 用内容分类观察逝者被如何呈现 → 通过人工抽检评估分类一致性 → 比较表达的数量、构成与演化轨迹。

| 段落 | 回答的问题 | 段落职责与承接 |
|---|---|---|
| 第一段 | 研究依据什么材料观察表征变化？ | 交代爬虫采集、两平台、关键词、时间范围、规模及分析单位，为内容分析建立资料基础 |
| 第二段 | 怎样从这些材料形成有意义、可检验的观察？ | 说明分类方式及其传播含义，报告人工抽检结果，最后引出时序与平台比较 |

## 第一段：数据采集与观察单位

### 逐句链

1. **数据来源**：交代网络爬虫、检索关键词与两个平台。
2. **观察范围**：说明帖文时间窗口、记录总量及平台构成。
3. **分析单位**：明确以单条帖文进行观察，并依据发布时间和平台来源组织后续比较。

### English draft

Using web crawlers, we retrieved posts from Douyin and Xiaohongshu with the keyword “张雪峰.” The collected corpus covers posts published from January to May 2026 and contains 49,930 records, comprising 16,602 from Douyin and 33,328 from Xiaohongshu. Individual posts constitute the unit of analysis, with publication time and platform source providing the basis for examining temporal patterns and differences between the two platforms.

### 中文对照

本研究通过网络爬虫，以“张雪峰”为关键词，从抖音和小红书获取帖文。所收集的语料覆盖2026年1月至5月发布的帖文，共49,930条记录，其中抖音16,602条、小红书33,328条。研究以单条帖文为分析单位，依据发布时间和平台来源，考察表达的时序特征及两个平台之间的差异。

### 写法说明

这一段把前文讨论的数字表征落实到具体材料：研究观察的是帖文中呈现出来的表达，时间与平台则构成比较维度。

第三句同时为后文的时序分析和平台比较建立依据，避免数据介绍停留在数量罗列。这里不预告变化方向，也不引入仿真。

“2026年1月至5月”明确指帖文发布范围。实际抓取日期、采集工具名称及检索覆盖方式，有确切记录后再补入对应方法说明。

## 第二段：分类的传播含义与人工抽检

### 逐句链

1. **分类方式**：交代由大语言模型辅助编码，并列出内容类别。
2. **传播含义**：解释教育、悼念和玩梗分别突出人物的哪些面向。
3. **连接研究对象**：说明分类比较怎样帮助观察“逝者被如何呈现”。
4. **检验设计**：交代将400条样本的人工标注与对应模型标签比较。
5. **检验结果**：报告一致率和Cohen κ。
6. **分析安排**：以数量、比例、时间和平台比较交接下一章。

### English draft

Posts were classified through LLM-assisted content coding into education-related discussion, mourning, memetic expression, other discussion, opportunistic marketing, and crawling noise. Education-related discussion foregrounds professional identity and educational issues, mourning foregrounds remembrance and emotional attachment, and memetic expression captures the reuse and adaptation of material associated with the figure. These distinctions allow changes in how Zhang Xuefeng is represented in public expression to be examined through content composition. To assess coding consistency, human annotations of a 400-post subsample were compared with the corresponding LLM labels. The comparison yielded 84.0% agreement and a Cohen κ of 0.799. Using these labels, the analysis examines changes in the quantities and proportions of different forms of expression over time and compares their trajectories between Douyin and Xiaohongshu.

### 中文对照

本研究通过大语言模型辅助内容编码，将帖文划分为教育观点讨论、事件悼念讨论、梗文化讨论、其他讨论、借势营销和爬取噪音。教育观点讨论突出人物的职业身份与教育议题，悼念表达突出纪念与情感联结，玩梗表达则体现对人物相关素材的重复使用与改编。这些区分使研究能够通过内容构成，考察公共表达中张雪峰被如何呈现及其变化。为检验编码一致性，研究将400条抽样帖文的人工标注与对应的模型标签进行比较。一致率为84.0%，Cohen κ为0.799。依据这些标签，研究考察不同表达形式的数量与比例如何随时间变化，并比较其在抖音和小红书上的演化轨迹。

### 写法说明

这一段增加的篇幅主要用于解释分类与传播问题的关系。第二、三句将“教育—悼念—玩梗”连接到职业身份、情感纪念和符号改编，使后文的类别曲线能够用于讨论人物表征的变化。它们说明的是分类的观察意义，没有提前认定这三类必然依次替代。

第四、五句报告已经完成的人工抽检，为模型分类提供具体的一致性证据。当前仅写已经明确的400条样本及比较结果，不补入尚未确认的抽样方式、人工标注人数或独立编码程序。

末句从“如何观察”转向“接下来观察什么”，自然进入第三章。两段至此完成数据基础、测量含义和质量检验的交代。

## 依据与版本边界

- 两平台范围、网络爬虫采集方式及已完成400条人工抽检由作者在本轮对话明确提供；49,930条及平台数量沿用本轮确认文本。用户明确删除的存疑记录处理及比例分母说明未重新加入。
- 人工与模型一致性结果来自作者提供的[结果截图](human_label_agreement.png)：样本400条、一致率84.0%、Cohen κ为0.799。截图是本轮收到的结果证据，不代表本run重新执行了人工编码或全量数据分析。
- 本轮只采用二（二）。旧稿的三平台汇总、人工复编码“尚未执行”表述及旧版模型结果仍属于后续章节待修订内容，不能覆盖本节作者最新确认；本轮不批量改写其他章节、模型或原始记录。
- 主稿修改前的完整文本保留在[初始化快照](inputs/manuscript.accepted.md)，可恢复被替换的旧二（二）方法文字；该快照与本次修改前主稿逐字节一致。原始DOCX、PDF、图件及冻结输入未覆盖。
