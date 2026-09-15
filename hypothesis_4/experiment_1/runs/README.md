# H4-E1 run 批次索引

本文件是 experiment_1 的 run 选择入口。后续状态检查、分析与论文取数必须先按此表
选择批次，不能按目录名模糊发现全部历史数据。

| 位置 | 分类 | 当前权威性 | 是否进入最新分析 |
|---|---|---|---|
| `anchored_v1/anchored_v1_{random,chronological,interest}_s{0,1,2}` | **最新正式批**：锚定式效用，3 算法 × 3 seeds | 当前唯一权威正式实验 | **是，9/9 全部进入** |
| `{random,chronological,interest}_s{0,1,2}` | 历史正式批：旧公式 `U=D·R` | 冻结历史对照 | 否 |
| `../runs_retired_pre_batch/` | 历史烟测、早期探针、正式批前残留 | 仅审计/诊断 | 否 |
| `../runs_retired_writer_bug/` | replay 写入器事故样本 | 无效 run，仅事故审计 | 否 |
| `../runs_stopped_partial/` | 人工停止、并发切换、混跑污染等不完整结果 | 无效/部分 run | 否 |

## 当前批次选择规则

- 批次 ID：`anchored_v1`。
- 配置清单：`../init/configs/manifest.json`。
- 完成性总览：`anchored_v1/_derived/monitor/overview.json`。
- 正式 3-seed 聚合数据：`anchored_v1/_derived/data/arm/`。
- AgentSociety 单-run 兼容入口：`../run` →
  `runs/anchored_v1/anchored_v1_interest_s0`。
- 兼容入口只锚定生成性验证主 run；跨算法结论必须使用 9-run 清单与臂级聚合表，
  不能只读取 `../run/replay`。

## 隔离约束

历史正式批、烟测、预测、失败/中断残留可以用于方法审计或稳健性讨论，但必须显式标为
`historical`、`smoke/probe` 或 `invalid/partial`。它们不得被当前 monitor 自动发现，不得
并入 `anchored_v1/_derived/data/arm/`，也不得作为最新正式实验的完成依据。
