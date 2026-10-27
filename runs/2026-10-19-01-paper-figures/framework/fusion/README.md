# ProAgent机制细节 × 环形构图：英文融合版

用户要求将[ProAgent第二版](../framework_proagent_en_v2.svg)与[白底圆环版](../divergent/orbit.svg)融合，保留此前约束，并增加一些局部配色模块和不同样式的悼念图标。本目录为本轮新候选；两个来源版本均保留，没有覆盖。

## 资产

| 文件 | 用途 |
|---|---|
| [v2/](v2/README.md) | 当前第二版：重排圆环端口与外侧回流、增强局部色彩，含SVG/PNG/灰度及本地draw.io可编辑文件与实际导出验证 |
| [drawio/](drawio/README.md) | 第一版本地draw.io可编辑版、实际导出预览、转换脚本和验证材料，保留作对照 |
| [framework_fusion_en_v1.svg](framework_fusion_en_v1.svg) | 原生可编辑融合版，180×67.85mm、2600×980 |
| [framework_fusion_en_v1.png](framework_fusion_en_v1.png) | 同比例预览，2600×980、367dpi |
| [framework_fusion_en_v1_grayscale.png](framework_fusion_en_v1_grayscale.png) | 已查看的灰度校样 |
| [draw_fusion.py](draw_fusion.py) | 标准库SVG生成脚本，仅输出本目录融合SVG |
| [render_fusion.mjs](render_fusion.mjs) | 使用本机Codex捆绑sharp导出PNG及灰度校样 |
| [framework_fusion_en_v1.zip](framework_fusion_en_v1.zip) | 图件、两份源码及本README的完整包 |

## 融合方式与保留要点

- ProAgent版提供显式的候选池→个人feed→表达效用→固定阈值→LLM→成功发表流程、独立接触历史、冻结输入/固定人设、生成摘录限额及实验比较安排。去掉重复的左侧仿真缩略循环，以节省篇幅。
- 圆环版提供“Visibility configuration—Selective expression—Content recirculation”的三阶段环形骨架；中央表达激活模块与外围微流程共同说明机制。
- 平台分析与仿真在主内容区约三七开（内容宽度约840:1620，约34:66）。左侧展开语料、编码、时序与平台比较；经验模式提供机制问题和标定参照，两部分共同解释公共表征重组。
- 保留英文长横版、白底、黑灰文字和少量蓝/朱红语义色。增加若干局部浅蓝/浅橙模块，分别提示可见性、表达激活与生成；没有恢复大面积彩色分区。编号、标签和实/虚线提供颜色之外的辨识。
- 悼念图标改为双层细瓣白菊花束、灰黑缎带与独立小蜡烛的组合，全为可编辑路径；只放语料情境区，不将所有模拟帖子标作悼念。
- 只显示49,930总样本与来源名称，不展示抖音/小红书各自的样本数、比例或条形。没有新增伪造曲线、真实帖文例句或统计结果。
- 短节点与箭头代替长段说明，约193个英文词。目标为紧凑且清晰的布局；未将用户的信息密度目标解释为着色像素比例。字号31—43px，180mm宽时正文/说明约6—8.4pt；最终仍需结合投稿版面校样。

## 事实核对与验证

依据冻结的ICA2027v1.docx及直接解析的Word数学对象，保留精确公式`U_it = B_i + R_it(D_it − B_i)`。100名智能体保持作者类型不变；W12—W22；效用达到固定个体门槛之后才调用LLM，否则本次不发帖。决策feed最多10条，生成上下文为人设加最多5条实际feed摘录、每条最多120字符。

当前feed接触独立进入同类接触历史，供后续行动的R使用，不取决于是否发帖。只有成功发布的帖子进入回流：时序制度在同批行动完成后入池、后续批次可见；随机/兴趣制度次周取得展示资格。环形箭头与模块宽度是机制示意，不编码数量，也不表示作者类型或态度发生改变。

冻结模拟输入与经验语料分列，同一seed内制度共享外部样本，不表示共用相同候选池。正文对模拟输入平台数仍有未统一口径，图中不指定。主比较3制度×3seed；兴趣B=0、D=1、R=1各3次配对，复用已有完整模型参照。完整模型与干预分批、生成服务配置不同，该限定保留在图注，不挤入图内短标签。

实际检查：SVG XML有效、ID唯一、58个原生文字对象、无嵌入位图或外部资源；源码重新生成与当前SVG内容一致；当前原Word与run冻结副本SHA256一致。已查看彩色与灰度PNG，并完成一次只读内容/箭头复核，修正了门槛标签越界、分支遮字、输入线穿标题及历史线不连续的问题。未发现与所核对正文的事实冲突。未重跑实验、重新核验原始研究结果或修改正式论文。

## 英文图注

**Research framework integrating empirical characterization and a circular curation–expression mechanism.** Platform content analysis characterizes temporal changes and platform differences, supplying empirical patterns and case-grounded references for model specification. The simulation connects visibility configuration, selective expression, and content recirculation among 100 fixed-type agents. Separately frozen external samples enter regime-specific candidate pools and form personal feeds of up to ten eligible posts. Baseline utility (B), current-feed response (D), and prior-exposure weight (R) determine expression utility. When utility reaches the fixed individual threshold, the LLM generates a post from the persona and at most five feed excerpts of up to 120 characters each. Only successfully published posts enter subsequent circulation. Current feed contact independently updates the same-type exposure history used in later actions. Candle and bouquet illustrations indicate the mourning context; arrows and icon counts are schematic.

**Comparison details.** Chronological returns enter the pool after the publishing action batch completes and become visible to later batches; random and interest-based returns become eligible the following week. Three regimes are compared across three seeds, sharing external samples within each seed. Each interest-based component intervention (B=0, D=1, or R=1) has three paired repeats and reuses the existing full-model reference. Full-model and intervention runs used separate batches and different generation-service configurations.

## 复现与边界

以项目`.env`中的`PYTHON_PATH`运行`draw_fusion.py`，再用本机Codex捆绑Node运行`render_fusion.mjs`。渲染脚本中的Node依赖路径换机需适配；Arial/Times New Roman缺失时可能替换字体，SVG文字仍可编辑。

本轮只新增本目录图件/脚本，并维护run和framework索引。没有修改既有代码，不需要代码补丁或worktree；未修改正式paper、Word、数据或实验流水线，未commit、push或归档。候选仍待作者审阅。

## 本地draw.io交付

2026-10-21按用户要求新增[drawio/](drawio/README.md)，以214个可编辑对象保留融合版内容与环形设计；58处文字与SVG完全一致，未将整图嵌入为图片。已通过本机draw.io实际打开、PNG导出和XML往返验证，原SVG保留。主文件与使用说明见子目录。

## 当前第二版

2026-10-23按用户反馈新增[v2/](v2/README.md)：中央卡片与圆弧分离，D、后续R和输出穿过独立开口，内容回流改走外侧；蓝色与深橙标题条增强视觉力度，保持白底与局部语义填充。保留英文长横比例、两项互补研究、悼念图标、无平台分别比例及既有科学边界。当前SVG和原生draw.io均已实际导出并查看，旧版不覆盖；约200字中文研究思路单独回复，不放进图中。
