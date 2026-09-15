# hypothesis_4 提交说明

本目录只保留当前主假设、正式实验配置、最新 `anchored_v1` 结果，以及与当前模型直接相关的分析材料。比赛提交时可以整体提交本目录。

## 权威内容

- `HYPOTHESIS.md`：主假设与理论机制。
- `SIM_SETTINGS.json`：仿真规模与设置。
- `benchmark_curves.json`：真实数据周级效标。
- `experiment_1/init/`：当前 AgentSociety 配置；`configs/` 中只保留 `anchored_v1_*` 与 `manifest.json`。
- `experiment_1/run`：AgentSociety 官方单-run兼容入口，指向 `anchored_v1_interest_s0`。
- `experiment_1/runs/anchored_v1/`：3 算法 × 3 seeds 的 9 个正式 run。
- `experiment_1/runs/anchored_v1/_derived/`：逐 run CSV、三臂聚合表、图表和完成性快照。
- `experiment_1/results/numerical_ablation_drb/`：明确标注为 numerical proxy 的机制消融，不是正式 ABM/LLM run。

## 正式批次边界

正式批次 ID 为 `anchored_v1`，9/9 runs 均已完成并覆盖 W12–W22。跨算法结论必须读取全部 9 个 replay 或 `_derived/data/arm/`，不能只读取官方单-run入口 `run/`。

旧公式正式批、烟测、失败/中断残留、退役配置、旧图表和旧监视快照已经移出本目录，统一备份在工作区根目录：

```text
archive/hypothesis_4_experiment_1_history_20260915/
```

归档内容不属于比赛提交材料，也不得进入当前 monitor、聚合表或分析数据源。完整索引见工作区根目录 `ARCHIVE_MANIFEST_H4E1_history_20260915.md`。

## 打包提醒

`experiment_1/run` 是相对符号链接。压缩或上传时必须确认链接被保留；如果比赛平台不支持符号链接，应在交付副本中将它实体化为 `anchored_v1_interest_s0` 的真实目录，确保 `run/replay` 可访问。
