# H4-E1 历史实验本地归档清单（2026-09-15）

## 归档目的

为使可整体提交的 `hypothesis_4/` 只包含最新 `anchored_v1` 正式实验，本次将旧公式正式批、烟测/失败残留、退役配置和旧派生产物按原相对路径移至：

```text
archive/hypothesis_4_experiment_1_history_20260915/
```

该目录是本地备份，受 `.gitignore` 排除，不进入比赛提交或当前分析。原有受 Git 管理的历史文件仍可从本次归档提交之前的版本历史恢复。

归档完成时体积约 **179 MB**，共 **20,620 个文件**；整理后 `hypothesis_4/` 约 **80 MB**。

## 已归档内容

| 原位置 | 分类 | 是否可进入 anchored_v1 分析 |
|---|---|---|
| `experiment_1/runs/{random,chronological,interest}_s{0,1,2}` | 旧公式 `U=D·R` 的历史正式 9-run | 否 |
| `experiment_1/runs_retired_pre_batch/` | 烟测、探针、正式批前残留及鉴权失败样本 | 否 |
| `experiment_1/runs_retired_writer_bug/` | replay 写入器事故样本 | 否 |
| `experiment_1/runs_stopped_partial/` | 中断、混跑或不完整 run | 否 |
| `experiment_1/init/configs_retired_2factor/` | 退役两因子配置 | 否 |
| `experiment_1/init/configs/{random,chronological,interest}_s*.json` | 不带 `anchored_v1` 前缀的旧公式配置 | 否 |
| `experiment_1/charts/` | 旧正式批、烟测和代理预测图 | 否 |
| `experiment_1/data/` 中除 `anchored_utility_prediction.*` 外的旧目录和代理文件 | 旧周表、旧聚合表、烟测与预测数据 | 否 |
| `experiment_1/monitor/` | 旧批次监视快照 | 否 |
| `experiment_1/results/{charts,snapshots,tables}` | 旧冻结结果 | 否 |
| `experiment_1/runtime_logs/` | batch、smoke 与代理运行日志 | 否 |
| `experiment_1/historical_code_and_docs/` | 旧两机制预测文档与历史代理脚本 | 否 |
| `__pycache__/`、`.DS_Store` | 本机缓存与元数据 | 否 |

`experiment_1/results/numerical_ablation_drb/` 未归档：它属于当前锚定式模型的 numerical proxy，并已在文件内部明确标注解释边界。

## 恢复规则

归档保持 `hypothesis_4/experiment_1/` 下的原相对结构。需要审计历史版本时，应在归档目录内只读检查；如确需恢复，先确认目标位置不存在，再按本清单逐项移回。不得把任何历史 replay 并入：

```text
hypothesis_4/experiment_1/runs/anchored_v1/
```

## 后续状态

`anchored_v1`后来完成9/9，但在2026-09-27因真实帖注入时机修订被`weekly_lag1`取代，其raw run也已归档。所有批次的当前分类与位置统一见`ARCHIVE_MANIFEST_H4E1.md`。
