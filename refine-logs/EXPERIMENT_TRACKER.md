# 待运行审核清单：普通真实帖滞后一周，讣告当周进入

日期：2026-09-27。当前实现版本`weekly_lag1`。代码与离线验证已完成；按用户要求，正式运行前再次等待审核。

[当前修改方案](EXPERIMENT_PLAN.md)

| 工作项 | 状态 | 说明 |
|---|---|---|
| 当前源码、原样本及W11可用量核对 | COMPLETE | 只读核对；未抽取初始化样本 |
| 方案审核 | COMPLETE | 首周W11历史17条、W22结束、帖龄和两臂范围已确认 |
| 实现与初始历史样本/新配置生成 | COMPLETE | 原250条不改；11轮不变；6份新配置就绪 |
| 无LLM规则、重复注入与恢复核验 | COMPLETE | 新门禁及旧版25项门禁均通过 |
| 既有实验分类归档 | COMPLETE | anchored_v1 raw 9-run移入formal_superseded；旧历史继续分为正式/探针/无效中断 |
| 正式运行审核 | APPROVED | 用户要求归档完成后启动正式实验 |

| 拟运行ID | 周窗 | 行动机会 | 状态 |
|---|---|---:|---|
| weekly_lag1_interest_s0 | W12-W22 | 1100 | RUNNING |
| weekly_lag1_interest_s1 | W12-W22 | 1100 | RUNNING |
| weekly_lag1_interest_s2 | W12-W22 | 1100 | QUEUED |
| weekly_lag1_random_s0 | W12-W22 | 1100 | QUEUED |
| weekly_lag1_random_s1 | W12-W22 | 1100 | QUEUED |
| weekly_lag1_random_s2 | W12-W22 | 1100 | QUEUED |

6次完整run，合计最多6,600次行动机会。chronological不改，不重新校准或新增消融。2026-09-27 23:53（Asia/Shanghai）以并发2启动正式批，首批为interest s0/s1，其余由同一调度器自动补位。
