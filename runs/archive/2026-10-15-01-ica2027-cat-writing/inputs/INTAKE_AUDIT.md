# 正文接入与版本审计

## 2026-10-12作者修订稿对齐

本轮只落实研究背景、文献综述、第二章第一节理论框架及相关项目研究文档；原始文件未覆盖。PDF初稿全文20页已提取阅读，并核对第6、8、11页的机制图、公式与实验表。两份Word按接受插入、排除删除的当前正文读取，同时读取全部批注与脚注。

| 作者来源（根目录） | 身份与处理 |
|---|---|
| `悼念退潮之后：基于多智能体仿真的逝者数字形象塑造机制研究.pdf` | 全稿初稿；章节、模型说明与历史结果参照，不能覆盖既有编码诚信修订 |
| `【1009批注版】ICA-研究背景和文献综述.docx` | 新研究背景、第一章三节综述和三个研究问题；7处插入、0处删除、7条批注、14项尾注（Markdown转换为脚注） |
| `【修订1】1008 理论框架.docx` | 最新总体理论；24处插入、11处删除、8条批注、4项脚注；来源独立标题在合稿中放入第二章（一） |

Word正文已同步到[manuscript.accepted.md](manuscript.accepted.md)，清理转换器的高亮/上标包装，不改作者论点；新脚注分别使用bg1–bg14、tf1–tf4避免与旧稿冲突。引用信息沿用作者来源，尚未进行独立文献真实性审计。批注作为理解语境：未把“正面形象六成”等建议当作数据事实，未将玩梗直接等同恶意或负面。

研究分工按用户明确要求落实：问题（1）主要由原始数据挖掘与分析回答，问题（2）（3）主要由LLM ABM回答。理论以传播反馈回路视角与策展流框架解释整体循环，B、D、R是表达环节的操作化，而非文献直接提出的一套变量。原先精准遏制恶意玩梗的治理问题不再是当前问题（3），治理意义保留为讨论方向。

作者理论正文中“B由事件前供给数据校准”的概括按原文保留；项目方法文档同时明确W13参与共同尺度、低频映射零人数和初始化限制，具体解释留待第二章后续重写。制度差异包含候选池及回流，不能缩写为同候选池下仅改变排序。仿真类别份额用于观察表征构成，不直接测量情绪或恶意。

摘要、关键词、第二章（二）及以后、第三至五章保持此前文本与编码诚信修订；本轮没有重写或更新实验数字。当前timestamp_v1九配置已离线验收、未启动LLM；anchored_v1结果、数值代理和敏感性分开解释。第二章第二部分与第三、四章后续在当前run中讨论后重写。

来源SHA256、本轮前文件副本、逐文件差异与范围核验保存在[本轮对齐证据](../../runs/archive/2026-10-09-01-activation-calibration/manuscript_alignment/README.md)。下文为历史接入审计，版本与“当前”表述只对应当时。

---

## 历史接入审计（2026-09-15）

## 接入结论

作者提供的三个版本均已作为原始稿件留档。当前版本为 `v3_20260915_2306_*`：PDF 共 20 页、A4、未加密，20 页均成功渲染；DOCX 可正常解包和转换，包含 5 个嵌入图像，没有修订标记和批注。

v1 DOCX 保留 146 个插入、117 个删除和 4 条批注；v2 已经收束这些修订；v3 进一步统一数据口径和图号并删除重复段落。当前版本关系如下：

- `source/v3_20260915_2306_*.docx` 是当前可编辑来源；
- `source/v3_20260915_2306_*.pdf` 是当前版面快照；
- `source/v1_*`、`source/v2_*`、`media_v1/` 与 `media_v2/` 仅作版本追溯；
- `manuscript.accepted.md` 是从 v3 导出的当前可检索文本，不代替 DOCX。

## 已与最新正式实验对齐的内容

- 正式批次写为 `anchored_v1`。
- 实验设计写为 3 种策展制度 × 3 个 seed，共 9 个正式 AgentSociety/LLM run。
- 9 个 run 均完成 W12—W22，共 11 周；时序制度保留 693 个非空小时批次并统一按周聚合。
- 表 2 的终态帖池数量与完成性总览一致：随机 443/443/430，时序 462/469/468，兴趣 500/478/478。
- 正式 run 合计 1904 条 Agent 帖，形成 99 个周级 run 观测点。
- 表达效用使用最新版 `U=B+R(D-B)`，没有沿用已废弃的 `U=D·R` 主公式。
- DTW 均值与 `arm_dtw_fit_summary.csv` 一致：兴趣约 22.0、随机约 23.7、时序约 27.0；正文同时注明 3-seed 范围重叠时不作统计显著性判断。
- B、D、R 消融被标注为 100 个配对 seed 的数值仿真/推演，与 9 次正式 AgentSociety/LLM run 分开陈述。

## 提交前需要处理

1. 统计措辞仍有冲突：结果段明确说明 9-run 比较“不构成统计显著性判断”，结论仍使用“显著差异”“显著提升”。作者于 2026-09-15 决定不再调整，当前版本按原文保留。
2. 因果与治理措辞宜继续保持边界：描述性“策展差值”不能写成算法净放大效应；数值消融不能写成额外的正式 LLM/AgentSociety 消融 run。

## v3 已解决事项

- 数据口径已统一为：原始 52736 条，剔除 20 条存疑记录后分析样本 52716 条；引言不再出现 52737 条。
- 正文引用与图注均已统一为“图 3a”。
- B、D、R 消融结果中的重复说明段已经删除。
- DOCX 继续保持零修订标记、零批注。

## 权威证据路径

```text
hypothesis_4/experiment_1/runs/anchored_v1/_derived/monitor/overview.json
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_dtw_fit_summary.csv
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_fit_summary.csv
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_platform_user_chain.csv
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_weekly_by_type.csv
hypothesis_4/experiment_1/runs/anchored_v1/_derived/data/arm/arm_weekly_summary.csv
```

官方单-run 兼容入口：

```text
hypothesis_4/experiment_1/run -> runs/anchored_v1/anchored_v1_interest_s0
```

该入口只服务官方工具兼容；论文的跨制度结论必须回到 `runs/anchored_v1/_derived/data/arm/`。

## 原件校验值与版本

```text
v1 PDF  SHA-256 f6da13ae920a02d7f0701b21a5f64ef5712ce2416c214dc95ac7c91cdd8ff9fb
v1 DOCX SHA-256 233c9377d2bf813cc9bf384686d7448c04099ef6df3f5bd9c198e298cc76d280
v2 PDF  SHA-256 b6c9a598ad550fb4ed8120e6d4e93cee5876d190148df43a5537293c91ebce5e
v2 DOCX SHA-256 d390d47fc6e5a79016f71303f042b6b6dda5079a230335adb97c4883b73eed98
v3 PDF  SHA-256 48a4111f22b7b8952d591e2e61721a1382b73e7c4579e4f0da25558cd2aa7340
v3 DOCX SHA-256 6e86118cf48ea983fd2198c089befdc0813e593f8dd382641ee94720d2675b0f
```
