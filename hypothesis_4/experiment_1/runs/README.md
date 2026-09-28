# H4-E1 实验批次索引

AgentSociety 官方目录约定使用 `hypothesis_{id}/experiment_{id}/run` 保存一个 run。本研究需要多算法、多 seed，因此保留官方 `run` 兼容入口，并用 `runs/<batch_id>/<run_id>` 扩展多 run 批次。历史原始结果按证据用途转入工作区根目录 `archive/`。

| 批次或位置 | 分类 | 状态 | 分析资格 |
|---|---|---|---|
| `anchored_v1/_derived/` | 当前正式批的派生结果兼容副本 | 9/9 完成 | 当前主分析输入 |
| `archive/hypothesis_4_experiment_1_batches/formal_current/anchored_v1/` | 当前正式批的原始 run、自包含配置与冻结派生结果 | 9/9 完整 | 是 |
| `weekly_lag1/` | 已归档敏感性批的派生结果兼容副本 | 6/6 曾完整完成 | 仅作敏感性分析 |
| `archive/hypothesis_4_experiment_1_batches/formal_superseded/weekly_lag1/` | 严格一期滞后原始 run、配置、工具与派生结果 | 6/6 完整 | 否，不进入主比较 |
| `archive/hypothesis_4_experiment_1_batches/design_superseded/weekly_lag1_event_v2/` | 未运行的后续设计 | 已撤回 | 否 |

当前周级刺激—响应顺序是：本周真实帖先进入环境并冻结全部 Agent 的 feed；本周 Agent 生成帖在全部 Agent 行动结束后统一提交，从下一周起才影响其他 Agent。`../run` 指向当前 `anchored_v1_interest_s0`，只承担 AgentSociety 单 run 工具兼容作用；三臂结论读取 9 个完整 run。

归档总索引见工作区根目录 `ARCHIVE_MANIFEST_H4E1.md`。任何历史结果都不得被自动并入 anchored_v1 的主结果。
