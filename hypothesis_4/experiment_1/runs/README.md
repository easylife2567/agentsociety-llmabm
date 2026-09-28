# H4-E1 实验批次索引

AgentSociety官方目录约定使用`hypothesis_{id}/experiment_{id}/run`保存一个run。本研究需要多算法、多seed，因此保留官方`run`兼容入口，并用`runs/<batch_id>/<run_id>`扩展多run批次。官方文档没有规定历史批次归档格式，本项目按证据用途分类归档。

| 批次或位置 | 分类 | 状态 | 最新分析资格 |
|---|---|---|---|
| `weekly_lag1/` | 当前正式批：interest/random × 3 seeds | 6/6完成，回放完整 | 当前正式分析输入 |
| `anchored_v1/_derived/` | 已取代正式批的冻结派生结果兼容副本 | 9/9曾完整完成 | 否，仅用于旧结论复核和新旧比较 |
| `archive/hypothesis_4_experiment_1_batches/formal_superseded/anchored_v1/` | `anchored_v1`原始run、自包含配置和派生结果归档 | 9/9完整，校验通过 | 否 |
| `archive/hypothesis_4_experiment_1_history_20260915/` | 更早旧公式正式批、探针、烟测、事故和中断残留 | 已分类归档 | 否 |

当前批次清单为`../init/configs/weekly_lag1_manifest.json`。`../run`指向`weekly_lag1_interest_s0`，只承担AgentSociety单run工具兼容作用；两臂结论必须读取6个正式run。

归档总索引见工作区根目录[`ARCHIVE_MANIFEST_H4E1.md`](../../../ARCHIVE_MANIFEST_H4E1.md)。任何历史结果都不得被monitor自动并入`weekly_lag1/_derived/`。
