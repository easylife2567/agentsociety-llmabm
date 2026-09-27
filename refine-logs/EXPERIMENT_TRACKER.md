# 待运行审核清单：普通真实帖滞后一周，讣告当周进入

日期：2026-09-27。当前实现版本`weekly_lag1`。代码与离线验证已完成；按用户要求，正式运行前再次等待审核。

[当前修改方案](EXPERIMENT_PLAN.md)

| 工作项 | 状态 | 说明 |
|---|---|---|
| 当前源码、原样本及W11可用量核对 | COMPLETE | 只读核对；未抽取初始化样本 |
| 方案审核 | COMPLETE | 首周W11历史17条、W22结束、帖龄和两臂范围已确认 |
| 实现与初始历史样本/新配置生成 | COMPLETE | 原250条不改；11轮不变；6份新配置就绪 |
| 无LLM规则、重复注入与恢复核验 | COMPLETE | 新门禁及旧版25项门禁均通过 |
| 正式运行审核 | PENDING | 用户审核本次代码和配置后才可启动 |

| 拟运行ID | 周窗 | 行动机会 | 状态 |
|---|---|---:|---|
| weekly_lag1_interest_s0 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |
| weekly_lag1_interest_s1 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |
| weekly_lag1_interest_s2 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |
| weekly_lag1_random_s0 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |
| weekly_lag1_random_s1 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |
| weekly_lag1_random_s2 | W12-W22 | 1100 | CONFIG_READY_AWAITING_RUN_APPROVAL |

6次完整run，合计最多6,600次行动机会。chronological不改，不重新校准或新增消融。批跑入口的`--dry-run`显示6个run均为pending，没有启动进程。
