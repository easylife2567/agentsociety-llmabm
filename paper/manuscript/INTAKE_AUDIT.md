# 正文接入审计（2026-09-15）

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
