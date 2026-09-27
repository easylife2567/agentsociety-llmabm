# 待审核运行清单：普通真实帖滞后一周，讣告当周进入

日期：2026-09-27。当前版本v3。执行前必须得到用户审核通过；v1/v2均已退出当前方案。

[当前修改方案](EXPERIMENT_PLAN.md)

| 工作项 | 状态 | 说明 |
|---|---|---|
| 当前源码、原样本及W11可用量核对 | COMPLETE | 只读核对；未抽取初始化样本 |
| 用户审核 | PENDING | 首周W11历史17条、W22结束、帖龄和两臂范围 |
| 实现与初始历史样本/新配置生成 | AWAITING_USER_APPROVAL | 原250条不改；11轮不变 |
| 无LLM规则、重复注入与恢复核验 | AWAITING_USER_APPROVAL | 审核后实施 |

| 拟运行ID | 周窗 | 行动机会 | 状态 |
|---|---|---:|---|
| weekly_lag1_obituary_current_interest_s0 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |
| weekly_lag1_obituary_current_interest_s1 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |
| weekly_lag1_obituary_current_interest_s2 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |
| weekly_lag1_obituary_current_random_s0 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |
| weekly_lag1_obituary_current_random_s1 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |
| weekly_lag1_obituary_current_random_s2 | W12-W22 | 1100 | AWAITING_USER_APPROVAL |

6次完整run，合计最多6,600次行动机会。两臂seed0的前三周先做检查，通过后续跑，作为同一正式run的前缀，不另加实验条件。chronological不改，不重新校准或新增消融。
