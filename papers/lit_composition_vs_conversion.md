# 文献调研：固定表达倾向的人群，如何通过发言活跃程度的变化产生公共表达的转向

**日期**：2026-09-27
**对应研究问题**：转向在多大程度上来自不同群体发声机会与表达强度的变化，而不必依赖大量个体态度转变
**检索词**：composition effect vs conversion；mobilization vs persuasion；differential turnout；activation / reinforcement / crystallization；spiral of silence / self-censorship
**检索留痕**：工作区 literature-search MCP 网关返回 `429 Too Many Requests`（重试两次均失败），本轮改用 datapro 学术库完成检索。

---

## 一、直接命中（必引）

### 1. Bowler & Donovan (1994) —— 你的命题的原文表述

> Bowler, S., & Donovan, T. (1994). **Information and opinion change on ballot propositions.**
> *Political Behavior*, 16(4), 411–435. DOI: 10.1007/BF01498825（被引 63）

摘要原文：

> "If **mobilization effects** dominate campaigns, individual voters **need not reverse their positions** on propositions for aggregate electorates to display **large-scale shifts in opinion**. This is the case particularly if opinions of different voters are **mobilized at different times**, or by different types of information."

这是本次检索中与你的主张**逐字对应**的一篇：聚合层面的大幅转向，不需要个体立场反转；成立的条件恰恰是**不同群体的激活时点不同**。你仿真里的 D（意见气候反馈）与 R（注意力衰减）做的正是"不同类型在不同时点被激活"这件事。

**用途**：放在引言或理论框架，作为"构成/动员机制可以独立于态度转变产生聚合转向"的直引先例。

### 2. Campbell (1985) —— 分解方法的先例

> Campbell, J. E. (1985). **Sources of the New Deal Realignment: The Contributions of Conversion and Mobilization to Partisan Change.**
> *The Western Political Quarterly*, 38(3), 357–376. DOI: 10.1177/106591298503800304（被引 28）

把聚合党派变化**显式拆成 conversion（改口）与 mobilization（换人）两项贡献**，并逐次选举估计各自份额。这正是我上一条建议你做的份额分解的历史先例。

**用途**：你的"换人项 / 改口项"分解不必自己发明口径，直接引它作为方法出处，能挡掉"分解是你自创的"这类质疑。

---

## 二、理论根源：activation vs conversion

Lazarsfeld / Berelson / Gaudet 在 *The People's Choice* (1944) 提出的四分类——**reinforcement（强化）、activation（激活）、crystallization（结晶）、conversion（转变）**——是你整个论证的原始概念来源。其中 activation 的定义就是"把潜在倾向转化为显性行为"（"transforms the latent political tendency into a manifest vote"），**不涉及态度改变**。

可引的二次文献（原书 1944 年版不易获取，建议引以下之一）：

- **Copeland, G. W. (1983).** Activating voters in congressional elections. *Political Behavior*, 5(4), 391–401. DOI: 10.1007/BF00987563（被引 45）
  —— 直接回到 *The People's Choice* 检验 activation 概念，最适合作为定义出处。
- **Dilliplane, S. (2014).** Activation, conversion, or reinforcement? The impact of partisan news exposure on vote choice. *American Journal of Political Science*. DOI: 10.1111/ajps.12046（被引 152）
  —— 顶刊、较新、被引高；明确批评既有研究"未能区分 activation / conversion / reinforcement"。适合引作"这一区分至今仍是活跃问题"。
- **Lacy, S., & Stamm, M. (2018).** Reassessing *The People's Choice*. In *Routledge* 文集, 16–37. DOI: 10.4324/9781315164441-3
  —— 若需要评述该经典的当代价值。

---

## 三、在线场景（支撑 D 机制）

- **Leong, A. D., & Ho, S. S. (2020).** Perceiving online public opinion: The impact of Facebook opinion cues, opinion climate congruency, and source credibility on speaking out. *New Media & Society*, 23(9), 2495–2515. DOI: 10.1177/1461444820931054（被引 35）
  —— 实验证明**平台的聚合表征（表情反应数）会被当作意见气候**，进而影响发言意愿。直接对应你模型里 `share_own` → D 的那条链路：感知到的气候由平台呈现的聚合信号构成，而非真实分布。
- **Weeks, B. E., Halversen, A., & Neubaum, G. (2023).** Too scared to share? Fear of social sanctions for political expression on social media. *Journal of Computer-Mediated Communication*, 29(1). DOI: 10.1093/jcmc/zmad041（被引 14）
  —— 网络异质性 → 对社交制裁的恐惧 → 表达减少。为 D 的"表达有净成本"提供实证支撑。
- **Chan, M. (2017).** Reluctance to talk about politics in face-to-face and Facebook settings. *Mass Communication and Society*, 21(1), 1–23. DOI: 10.1080/15205436.2017.1358819（被引 59）
  —— 把"恐惧孤立"作为**倾向性变量**与网络同质性交互。对你把 D 参数设为类型常数（不同类型对气候敏感度不同）有直接支撑。

---

## 四、旁支（备查）

- **Norris, P. (2006).** Did the Media Matter? Agenda-Setting, Persuasion and Mobilization Effects in the British General Election Campaign. *British Politics*, 1(2), 195–221. DOI: 10.1057/palgrave.bp.4200022（被引 70）—— 议程设置 / 说服 / 动员三分，可作框架对照。
- **Bastos, M., & Mercea, D. (2018).** The public accountability of social platforms. *Phil. Trans. R. Soc. A*, 376(2128). DOI: 10.1098/rsta.2018.0003（被引 123）—— 在社交平台语境下使用 activation / reinforcement / conversion 三分，说明该框架已进入计算传播学。
- **Slater, M. D. (2014).** Reinforcing Spirals Model. *Media Psychology*, 18(3), 370–395. DOI: 10.1080/15213269.2014.897236（被引 282）—— 选择性曝光与态度强化的内生回路，与你"曝光→发言→曝光"的反馈结构同构，可作机制对照。

---

## 五、与本项目的接口

| 本项目构件 | 对应文献概念 | 可引 |
|---|---|---|
| 固定类型 Agent（表达倾向不随时间变） | 潜在倾向 latent tendency | Lazarsfeld et al. 1944 / Copeland 1983 |
| 发声率变化产生份额转向 | mobilization / activation effect | **Bowler & Donovan 1994** |
| 换人项 vs 改口项分解 | conversion vs mobilization decomposition | **Campbell 1985** |
| D：感知意见气候 | perceived opinion climate | Leong & Ho 2020 |
| D：表达有净成本 | fear of isolation / self-censorship | Weeks et al. 2023 / Chan 2017 |
| 去 D / 去 R 消融 | 区分 activation 与 conversion 的实证策略 | Dilliplane 2014 |

**一句话**：你的机制在政治传播学里有四十年的研究传统，叫 **activation / mobilization 而非 conversion**；你要做的份额分解，Campbell (1985) 已经做过一次。这两篇足以支撑理论定位与方法合法性。

---

## 六、未检索到 / 待补

- 未找到**直接以"推荐算法导致发声构成变化"为因**的实证论文。现有文献的动员来源是竞选接触、社交网络、媒体曝光，不是平台策展。这一块仍是空缺，也正是你项目的贡献空间。
- 若要补，建议下一轮检索方向：`algorithmic curation` + `speaking up` / `differential exposure`；`engagement-based ranking` + `composition of discourse`。
- literature-search 网关恢复后可重跑一次，把结果并入 `papers/literature_index.json`。
