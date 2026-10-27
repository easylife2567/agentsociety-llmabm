# 三种不同视觉语言；当前聚焦圆环机制图

用户认为前轮构图风格仍相近，本轮新增报刊式研究地图、圆环机制图、流动带状图。用户随后要求保留此前要点、避免大面积配色，并明确喜欢“圆环机制图”的形式，要求收敛为科研配色。当前重点候选为B圆环白底版，仍仅保存于本run，尚未写入正式论文。

## 资产

| 候选 | 可编辑SVG | PNG | 绘图源码 | 视觉语言 |
|---|---|---|---|---|
| A 报刊式研究地图 | [editorial.svg](editorial.svg) | [editorial.png](editorial.png) | [draw_editorial.py](draw_editorial.py) | 衬线大字、开放双栏、细线、大号研究序号、单一强调色机制回路 |
| **B 圆环机制图（当前重点）** | [orbit.svg](orbit.svg) | [orbit.png](orbit.png) | [draw_orbit.py](draw_orbit.py) | 开放经验线图与右侧圆形三阶段回路，公式居中，白底黑灰字、少量蓝/朱红色路径 |
| C 流动带状图 | [ribbon.svg](ribbon.svg) | [ribbon.png](ribbon.png) | [draw_ribbon.py](draw_ribbon.py) | 悬浮图标与有机曲线，等宽细带引导流程，取消矩形分区及色块标题 |

[三种构图拼版](comparison.png) / [拼版灰度校样](comparison_grayscale.png) / [圆环单图灰度校样](orbit_grayscale.png) / [完整文件包](three_distinct_styles.zip)。

三版均为英文、180×63.75mm、viewBox 2400×850；PNG为2400×850、339dpi。平台分析与仿真分别占约35%/65%的视觉区域（带状版约37%/63%）；自由构图的比例按内容区域估计，非实测数据比重。圆环扇段、曲线宽度及图标数量均为结构示意，不编码统计结果。未展示两平台分别的样本数量、百分比或对比条形。

## 圆环版配色

- 白底；全部47个文字对象使用深黑`#17212B`或深灰`#48515D`，不以彩色小字承载重要信息。
- 蓝色`#0072B2`强调可见性与经验问题进入机制解释的路径，朱红色`#D55E00`强调阈值表达及成功发布路径，深灰回流；编号、位置、直接标签、实/虚线共同区分机制。
- 蓝/朱红取自Okabe–Ito的[Color Universal Design方案](https://jfly.uni-koeln.de/color/index.html)。采用该方案的冗余编码与直接标注原则；研究图可访问性亦可参阅Wong的[Color blindness, Nature Methods](https://www.nature.com/articles/nmeth.1618)。这些是设计依据，不等同于已完成全部色觉缺陷模拟或期刊终稿验收。
- 没有彩色大底或大面积填色面板。按导出PNG中RGB最大/最小通道差大于30估算，圆环版彩色像素约1.31%；A/C约3.01%/3.02%。该计算仅记录颜色使用克制程度，不用于宣称信息密度或任何科研统计比例。

## 事实与检查

两项研究互补：平台分析刻画内容编码后的时序变化与平台差异，经验模式提出机制问题并提供案例标定参照；仿真展开“Visibility configuration → Selective expression → Content recirculation”，共同解释公共表征重组。不将仿真画成现实平台的严格复制或独立因果验证。

三版均保留100名固定类型智能体、正确公式`U_it = B_i + R_it(D_it − B_i)`、固定门槛先于LLM生成、接触历史独立影响后续R、仅成功发布内容进入回流。圆环和带状版将回流简写为时序制度后续批次、随机/兴趣制度次周；完整时序为发布行动批次完成后入池、后续批次可见，以及次周取得展示资格。蜡烛和白花只表示悼念情境，不是新变量或所有帖文的标签。

框架省略的细节交由图注及正文：生成上下文为人设加最多5条实际信息流摘录，每条最多120字符；个人决策信息流上限为10条，两者不同。主实验3制度×3seed；兴趣制度B=0、D=1、R=1各3次配对，复用已有完整模型参照；完整模型与消融分批、生成服务配置不同。当前feed接触更新后续使用的同类接触历史，无论该次是否发帖。单独冻结外部模拟输入，不声称49,930条全量语料直接入池；正文模拟输入平台数尚有未统一表述，图中不指定。

已对照冻结正文复核科学关系与数学公式；当前原Word与冻结副本SHA256一致。三张SVG XML可解析、ID唯一、无嵌入位图或外部资源。A/B/C分别42/47/34个可编辑文字对象、按空白分词约113/130/105词。全部SVG已从对应脚本再生并导出PNG，已查看彩色拼版与圆环灰度校样；修正了回路线穿字、标定桥贴字和弧线箭头靠近标题的问题。未重跑实验或重新检验研究结果；正式Word、paper及实验资产未修改。

## 英文图注

**Complementary empirical and simulation studies of postmortem public representation.** Platform content analysis identifies temporal patterns and platform differences, motivating questions about how public representation is reorganized. The simulation links visibility configuration, selective expression, and content recirculation among 100 fixed-type agents. Expression utility combines baseline utility (B), current-feed response (D), and prior-exposure weight (R). The LLM generates a post only when utility reaches the fixed individual threshold. Successfully published posts return under regime-specific eligibility rules; feed contact independently updates the history used in later actions. The two studies provide complementary empirical characterization and mechanism explanation. Candle and flower icons indicate the mourning context. Arcs, ribbon widths, and icon counts are schematic rather than quantitative.

必要时追加：**Personal feeds contain up to ten eligible posts; generation uses the persona and at most five feed excerpts of up to 120 characters each. Chronological returns become visible to later batches after the publishing batch completes; random and interest-based returns become eligible the following week. The main comparison uses three regimes across three seeds, sharing external samples within each seed. Interest-based B=0, D=1, and R=1 ablations each have three paired repeats and reuse the existing full-model reference. Full-model and ablation runs used separate batches and different generation-service configurations.**

## 复现与范围

三个独立Python脚本只使用标准库，并只在同目录生成对应SVG。使用项目`.env`的`PYTHON_PATH`运行，随后由[render_all.mjs](render_all.mjs)导出预览与校样；渲染脚本使用本机Codex捆绑Node/sharp路径，换机需适配。字体保留可编辑，Georgia/Arial缺失时可能替换。文件包包含三张SVG、三张PNG、三份Python源码、渲染脚本、本README与三张校样。

本轮只新增当前run图件、独立脚本及维护所属索引；不需要修改既有代码或建立worktree。此前各候选保留。未commit、push或归档。
