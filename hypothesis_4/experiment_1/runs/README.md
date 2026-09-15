# H4-E1 run 批次索引

本文件是 experiment_1 的 run 选择入口。后续状态检查、分析与论文取数必须先按此表
选择批次，不能按目录名模糊发现全部历史数据。

| 位置 | 分类 | 当前权威性 | 是否进入最新分析 |
|---|---|---|---|
| `anchored_v1/anchored_v1_{random,chronological,interest}_s{0,1,2}` | **最新正式批**：锚定式效用，3 算法 × 3 seeds | 当前唯一权威正式实验 | **是，9/9 全部进入** |
| 工作区根目录 `archive/hypothesis_4_experiment_1_history_20260915/` | 旧公式正式批、烟测、事故样本与中断残留 | 本地归档，不随 `hypothesis_4/` 提交 | 否 |

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
`historical`、`smoke/probe` 或 `invalid/partial`。它们已经移出 `hypothesis_4/`，不得被
当前 monitor 自动发现，不得并入 `anchored_v1/_derived/data/arm/`，也不得作为最新正式
实验的完成依据。恢复位置与分类见工作区根目录
`ARCHIVE_MANIFEST_H4E1_history_20260915.md`。
