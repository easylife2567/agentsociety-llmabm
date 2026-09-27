# hypothesis_4 提交说明

本目录保留当前主假设、`weekly_lag1`正式实验配置、旧`anchored_v1`冻结派生结果兼容副本，以及与当前模型直接相关的分析材料。

## 权威内容

- `HYPOTHESIS.md`：主假设与理论机制。
- `SIM_SETTINGS.json`：仿真规模与设置。
- `benchmark_curves.json`：真实数据周级效标。
- `experiment_1/init/`：当前`weekly_lag1`配置与冻结输入。
- `experiment_1/run`：AgentSociety官方单-run兼容入口，指向`weekly_lag1_interest_s0`。
- `experiment_1/runs/weekly_lag1/`：当前interest/random×3 seeds正式批。
- `experiment_1/runs/anchored_v1/_derived/`：已取代批的冻结派生结果兼容副本。
- `experiment_1/results/numerical_ablation_drb/`：明确标注为 numerical proxy 的机制消融，不是正式 ABM/LLM run。

## 正式批次边界

当前正式批次ID为`weekly_lag1`，计划6个run覆盖W12–W22。完成性复核前不得将其写成已完成结果。`anchored_v1`的9个raw run已移入本地归档。

历史实验统一由根目录归档索引管理：

```text
ARCHIVE_MANIFEST_H4E1.md
```

归档内容不得进入当前monitor、聚合表或最新分析数据源。

## 打包提醒

`experiment_1/run`是相对符号链接。压缩或上传时必须确认链接被保留；如果平台不支持符号链接，应在交付副本中将它实体化为当前主run目录。
