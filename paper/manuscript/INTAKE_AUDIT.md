# 正文接入审计（2026-09-15）

## 接入结论

作者提供的 DOCX 与 PDF 已作为原始稿件留档。PDF 共 20 页、A4、未加密，抽查首页、实验表页和参考文献末页均可正常渲染；20 页均成功生成页面图。DOCX 可正常解包和转换，包含 6 个嵌入图像、146 个插入修订、117 个删除修订和 4 条批注。

DOCX 的修改时间晚于 PDF 约 4 分钟，且保留大量修订，因此：

- `source/*.docx` 是当前可编辑来源；
- `source/*.pdf` 是当前版面快照；
- `manuscript.accepted.md` 仅用于检索、比对和证据核查，不代替 DOCX，也不表示作者已正式接受全部修订。

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

1. 样本量不一致：摘要写“三大平台 5 万余条”并在引言写 52737 条，结论写 52716 条。需确定唯一清洗口径，并在全文、表格和附录中统一。
2. 统计措辞冲突：结果段明确说明 9-run 比较“不构成统计显著性判断”，结论却使用“显著差异”“显著提升”。建议改为“明显差异”“更高”或补充正式检验后再使用“显著”。
3. 图号错误：正文写“图 5a 展示”，紧接的图注为“图 3a”；应统一为最终图号。
4. 重复段落：B、D、R 消融结果段末尾重复了一次“为检验表达效用 U 的内部结构……”段落，需要删除重复文本。
5. 修订状态未收束：DOCX 尚有 263 处修订标记与 4 条批注。提交前应逐项决定接受/拒绝，并生成无修订标记的最终稿。
6. PDF 与 DOCX 版本关系未冻结：最终 DOCX 定稿后需重新导出 PDF，再做逐页渲染检查，避免提交旧 PDF。
7. 图件编号与正文引用需全量交叉检查；当前转换文本中的图 1、图 2、图 3a、图 3b、图 4应与最终排版一一对应。
8. 因果与治理措辞宜继续保持边界：描述性“策展差值”不能写成算法净放大效应；数值消融不能写成额外的正式 LLM/AgentSociety 消融 run。

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

## 原件校验值

```text
PDF  SHA-256 f6da13ae920a02d7f0701b21a5f64ef5712ce2416c214dc95ac7c91cdd8ff9fb
DOCX SHA-256 233c9377d2bf813cc9bf384686d7448c04099ef6df3f5bd9c198e298cc76d280
```
