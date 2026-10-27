# 平台分析与仿真互补：三种长横版框架候选

依据用户最新要求：加强红、蓝、绿、紫配色；把平台数据分析与仿真建模画成有联动的两个主模块；突出“可见性配置—选择性表达—内容回流”；继续采用英文、跨双栏长横版。后续明确要求不突出两平台各自比例，三版均已删除各平台比例、条形图及单独样本数量，只保留总样本量与数据来源名称。

## 图件与构图

| 候选 | 可编辑文件 | 预览 | 两研究模块面积 | 布局用途 |
|---|---|---|---|---|
| A 左右联动 | [a_linked.svg](a_linked.svg) | [a_linked.png](a_linked.png) | 30:70 | 左侧完整分析流程，右侧三阶段横向循环；明确经验标定与独立冻结输入的边界 |
| B 双研究带 | [b_bands.svg](b_bands.svg) | [b_bands.png](b_bands.png) | 40:60 | 参考附件的上下分带；上层产生经验问题，下层展开三个机制阶段，适合强调互补分工 |
| C 机制闭环 | [c_loop.svg](c_loop.svg) | [c_loop.png](c_loop.png) | 35:65 | 左侧两条分析路径，右侧三角闭环；文字最少，适合优先突出提出的机制 |

推荐优先审阅C，其次B。上述比例是两研究面板的实际几何面积比，不是平台数据比例；不计模块间隙和共同解释栏。

- A：经验684×680，仿真1596×680。
- B：经验2350×270，仿真2350×405。
- C：经验812×638，仿真1508×638。

三版均为180×63.75mm，viewBox 2400×850；PNG为2400×850、339dpi。主文字通常30—36px，对应180mm宽排版约6.4—7.7pt，次要说明27px约5.7pt；最终以目标会议版面校样为准。SVG保留文字、路径、图形和箭头编辑性，无嵌入位图；Arial缺失时可能替代字体。

## 配色与图形语义

参考用户最新[双带配色附件](../../references/user_vivid_two_band_template.png)，采用更实的色块和深色文字，白底配少量虚线功能框。绿色`#A9D47D`代表平台分析，蓝色`#88BFF2`代表可见性配置，红色`#F47D7D`代表选择性表达，紫色`#BE9AE3`代表内容回流。黑色为主流程，灰色虚线为后续接触历史影响。深色正文对四色背景的计算对比度分别约10.5、9.1、6.8、7.5。阶段文字、编号和线型提供颜色以外的区分；已查看[灰度校样](comparison_grayscale.png)，未将红绿用作是非判断。蜡烛和白花只提示数字悼念情境，不代表所有帖子均为悼念内容。

[彩色比较拼版](comparison.png)用于挑选构图；投稿使用单张SVG，拼版中的A/B/C构图名称和面积比例不是论文正文内容。信息密度按紧凑流程组织，原有重复段落转入图注。

## 事实核对与省略边界

依据run冻结正文，已直接核对Word数学对象；当前原Word与冻结副本SHA256一致。三版均保留以下科学关系：

- 平台内容分析刻画时序变化与平台差异，仿真提供机制解释。联动为经验问题和案例标定，两条研究路径共同解释表征重组，不声称仿真独立验证真实平台因果效应。
- 经验作者构成参照与B/D/R标定有正文依据；100名智能体在W12—W22保持作者类型不变。六类现实内容编码中的Noise不等于第六类模拟作者，也未添加正文未明确说明的整体噪音剔除操作。
- 冻结模拟输入与49,930条经验语料分开。正文对模拟输入平台数尚有未统一表述，图中不指定该平台数。同一seed内共享外部样本，不表示共享相同候选池。
- 个人信息流最多10条；表达效用为`U_it = B_i + R_it(D_it − B_i)`。达到固定个体门槛后才调用LLM，否则本次不发帖。文本生成采用人设与最多5条实际feed摘录，每条最多120字符；A图的这一上下文限额移入共用图注。
- 当前feed接触独立更新后续使用的历史，R由此前累计同类接触形成；不从成功发帖分支更新作者类型。图中没有态度转变、SVO或额外心理更新机制。
- 仅成功发布的帖子回流。时序制度在行动批次完成后入池、后续批次可见；随机/兴趣制度次周取得资格。“later batches”为此时序的简写，完整边界在图注。
- 主比较为3制度×3seed；兴趣制度B=0、D=1、R=1各3次配对重复，复用已有完整模型参照。完整模型与消融分批运行、生成服务配置不同；这些实验细节以共用图注和正文补足，C图未重复放置实验安排。

检查结果：SVG XML可解析、ID唯一、无外部图片或链接资源；A/B/C分别49/44/38个原生文字对象，可见文本按空白分词约164/190/135词。已查看全部彩色预览及灰度拼版，修正主发布箭头和接触历史线的交叉与文字遮挡。未重跑实验、重核原始数值结果或修改正式论文；仍为待作者选择的候选。

## 英文共用图注

**Complementary studies of postmortem public representation.** Platform content analysis characterizes temporal changes and platform differences in 49,930 posts. Empirical patterns motivate mechanism questions and inform case-grounded model specification. The simulation connects visibility configuration, selective expression, and content recirculation in a population of 100 fixed-type agents over W12–W22. Baseline expression utility (B), current-feed response (D), and prior-exposure weight (R) determine whether utility reaches the fixed individual threshold. Only then does the LLM generate a post from the persona and at most five feed excerpts of up to 120 characters each. Successful posts return under regime-specific eligibility rules, while current exposure updates the history used in later actions. The two studies jointly inform an interpretation of public representation reorganization through changing participation, supply, and re-exposure.

扩展实验说明（按终稿图注长度取舍）：**The main experiment compares random, chronological, and interest-based regimes across three seeds, sharing external samples within each seed. Chronological returns become visible to later action batches after the publishing batch completes; random and interest-based returns become eligible the following week. Each interest-based component ablation (B=0, D=1, or R=1) has three paired repeats and reuses the existing full-model reference. Full-model and ablation runs used separate batches and different generation-service configurations.**

## 源码与复现

本轮新增文件，保留上一轮图件不覆盖；只写当前run。三种生成脚本共享[vivid_lib.py](vivid_lib.py)：[A](draw_a_linked.py)、[B](draw_b_bands.py)、[C](draw_c_loop.py)。使用项目`.env`中的`PYTHON_PATH`运行各脚本，再用Codex捆绑Node运行[render_all.mjs](render_all.mjs)导出PNG与两张校样；渲染脚本当前引用本机捆绑sharp绝对路径，换机需适配该路径。

[完整下载包](three_complementary_layouts.zip)包含三张SVG、三张PNG、四个Python文件、PNG渲染脚本、本README及两张比较校样。未commit、push、归档或写入正式paper资产。
