# H4-E1 实验归档总索引

日期：2026-09-27。

AgentSociety官方工作区约定提供`hypothesis_{id}/experiment_{id}/run`单run目录，没有规定多批次历史归档结构。本项目保留该兼容入口，并按实验的证据地位组织本地`archive/`。

## A. 已完成但被取代的正式批

路径：`archive/hypothesis_4_experiment_1_batches/formal_superseded/anchored_v1/`

- 设计：random / chronological / interest × 3 seeds。
- 完成性：9/9完整；周级臂11/11步，chronological 693/693批次。
- replay：每run 1100行Agent状态、11行环境状态。
- 被取代原因：interest/random原先让整周真实帖在当周决策前进入，2026-09-27改为普通真实帖一期滞后。
- 内容：`raw/`原始run、`_derived/`冻结派生结果、`config/`自包含配置、`inventory.json`和`checksums.sha256`。
- 用途：旧结论复核、新旧配对比较；不得作为最新正式结果。

为保持既有论文与审阅链接可读，Git跟踪的派生结果兼容副本仍位于`hypothesis_4/experiment_1/runs/anchored_v1/_derived/`，其中不再保留raw run。

## B. 更早的历史实验

路径：`archive/hypothesis_4_experiment_1_history_20260915/`

| 子目录 | 分类 |
|---|---|
| `hypothesis_4/experiment_1/runs/` | 旧公式历史正式批 |
| `runs_retired_pre_batch/` | 探针、烟测和正式批前残留 |
| `runs_retired_writer_bug/` | replay writer事故样本，无效 |
| `runs_stopped_partial/` | 中断、混跑或不完整run，无效 |
| `init/`、`charts/`、`data/`、`monitor/` | 对应历史配置与派生产物 |

细目见[`ARCHIVE_MANIFEST_H4E1_history_20260915.md`](ARCHIVE_MANIFEST_H4E1_history_20260915.md)。

## C. 当前活动批

路径：`hypothesis_4/experiment_1/runs/weekly_lag1/`

当前活动批不属于归档。配置清单为`init/configs/weekly_lag1_manifest.json`，计划运行interest/random×3 seeds。运行完成并通过完整性检查前，不得替换论文中的正式数值结论。
